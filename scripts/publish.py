"""Publish only verified durable assets, then fast-forward the stable Morphe feed.

Uses the workflow's GITHUB_TOKEN through gh. No PAT, admin action, private URL token,
or token forwarding to asset storage is required.
"""
import json
import os
import subprocess
import tempfile
import time
import hashlib
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote
from bundle import verify_kit, version_tuple


def gh(*args, input=None):
    result = subprocess.run(['gh', *args], input=input, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'gh {args[0]} failed: {result.stderr}')
    return result.stdout


def api(path, data=None, method=None):
    args = ['api', path]
    if method:
        args += ['--method', method]
    if data is not None:
        args += ['--input','-']
    return json.loads(gh(*args, input=json.dumps(data) if data is not None else None) or '{}')


def find_release(base, tag, request=api, delay=time.sleep):
    # A newly created public draft may not immediately appear in the collection.
    # Existing drafts are retried; a missing result never creates a duplicate draft.
    for attempt in range(6):
        result = next((r for r in request(base+'/releases?per_page=100') if r['tag_name']==tag), None)
        if result is not None:
            return result
        if attempt < 5:
            delay(2 * (attempt + 1))
    raise ValueError('Known release is not yet visible in the REST collection')


def select_release(releases, tag, name):
    exact = [r for r in releases if r['tag_name'] == tag]
    if len(exact) > 1:
        raise ValueError('Ambiguous versioned releases')
    if exact:
        return exact[0]
    # Recover the empty Actions draft left by a failed retarget operation. GitHub
    # can replace a draft's tag with untagged-* if an update omits tag_name.
    pending = [r for r in releases if r['draft'] and not r['assets'] and r['name'] == name
               and r['author']['login'] == 'github-actions[bot]' and r['tag_name'].startswith('untagged-')]
    if len(pending) > 1:
        raise ValueError('Ambiguous empty release drafts')
    return pending[0] if pending else None


def upload_assets(base, release, directory):
    if not release['draft']:
        raise ValueError('Published assets are immutable')
    result=[]
    for path in sorted(directory.iterdir()):
        old=next((a for a in release['assets'] if a['name']==path.name),None)
        if old:
            api(base+'/releases/assets/'+str(old['id']), method='DELETE')
        endpoint='https://uploads.github.com/'+base+'/releases/'+str(release['id'])+'/assets?name='+quote(path.name,safe='')
        result.append(json.loads(gh('api',endpoint,'--method','POST','--header','Content-Type: application/octet-stream','--input',str(path))))
    return result


def download_assets(base, assets, directory):
    for asset in assets:
        name=asset['name']
        if Path(name).name != name:
            raise ValueError('Unsafe release asset name')
        with (Path(directory)/name).open('wb') as output:
            result=subprocess.run(['gh','api',base+'/releases/assets/'+str(asset['id']),
                                   '--header','Accept: application/octet-stream'],stdout=output,stderr=subprocess.PIPE)
        if result.returncode:
            raise RuntimeError('Asset download failed: '+result.stderr.decode('utf-8',errors='replace'))


def metadata(config, release):
    version_tuple(config['version'])
    # Manager's DTO uses kotlinx.datetime.LocalDateTime, without a timezone suffix.
    created = datetime.fromisoformat(release['published_at'].replace('Z','+00:00')).astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')
    return {'created_at':created, 'description':'Instagram 439 : chemin normal RoundedCornerFrameLayout vérifié même avec handlers R8 ; garde bytecode conservé.',
            'download_url':f"https://github.com/{config['repository']}/releases/download/v{config['version']}/PatchInsta-{config['version']}.mpp",
            'signature_download_url':None, 'page_url':release['html_url'], 'version':config['version']}


def verify_public(url, feed, checksum, opener=urlopen, delay=time.sleep):
    # GitHub raw may serve the previous feed briefly after the ref advances. Verify
    # the SAME stable URL as Manager, not a cache-busted URL that would mask this.
    for attempt in range(7):
        try:
            with opener(url, timeout=40) as response:
                remote = json.load(response)
        except HTTPError as error:
            if error.code not in (404, 502, 503, 504) or attempt == 6:
                raise
        else:
            if remote == feed:
                with opener(remote['download_url'], timeout=40) as response:
                    if hashlib.sha256(response.read()).hexdigest() != checksum:
                        raise ValueError('Anonymous MPP download checksum differs')
                return
            if attempt == 6:
                raise ValueError('Stable anonymous source still differs after bounded CDN retries')
        delay(min(5 * (attempt + 1), 30))


def load_device_evidence(path, config, candidate_run_id, source_commit, mpp_sha256):
    evidence = json.loads(Path(path).read_text())
    if evidence.get('schema') != 'patchinsta-device-validation/v1':
        raise ValueError('Unsupported physical validation evidence schema')
    expected = {
        'version': config['version'],
        'candidate_run_id': str(candidate_run_id),
        'source_commit': source_commit,
        'mpp_sha256': mpp_sha256,
    }
    for key, value in expected.items():
        if evidence.get(key) != value:
            raise ValueError(f'Physical validation evidence {key} does not match candidate')
    if config['version'] != '4.1.9':
        raise ValueError('This promotion gate is reserved for the 4.1.9 release')
    for key in ('attested_by', 'tested_at'):
        if not isinstance(evidence.get(key), str) or not evidence[key].strip():
            raise ValueError(f'Physical validation evidence requires {key}')
    if not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('Candidate source commit is invalid')
    device = evidence.get('device', {})
    for key in ('model', 'android_version', 'one_ui_version'):
        if not isinstance(device.get(key), str) or not device[key].strip():
            raise ValueError(f'Physical validation evidence requires device.{key}')
    app = evidence.get('instagram', {})
    if not isinstance(app.get('version'), str) or not app['version'].strip():
        raise ValueError('Physical validation evidence requires instagram.version')
    checks = evidence.get('checks', {})
    required_checks = ('external_screen_visual_pass', 'internal_screen_native_pass',
                       'no_media_border', 'gradient_full_width_bottom', 'author_and_caption_readable',
                       'comments_work', 'scrubber_seeks_correctly', 'no_crashes')
    if any(checks.get(key) is not True for key in required_checks):
        raise ValueError('Physical validation evidence is missing a required passing check')
    runs = evidence.get('scenarios', {})
    if runs.get('cold_starts', 0) < 10 or runs.get('swipes', 0) < 30 or runs.get('fold_cycles', 0) < 5:
        raise ValueError('Physical validation evidence does not meet the required device scenario counts')
    screenshots = evidence.get('screenshot_sha256', [])
    if not isinstance(screenshots, list) or not screenshots or any(
        not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
        for digest in screenshots
    ):
        raise ValueError('Physical validation evidence requires local screenshot SHA-256 digests')
    return evidence


def verify_candidate(root, config, candidate_run_id, requested_sha, evidence_path):
    if config['version'] != '4.1.9':
        raise ValueError('This promotion workflow is reserved for the 4.1.9 release')
    expected = verify_kit(root/'output', config)
    stem = 'PatchInsta-'+config['version']
    mpp_sha256 = expected[stem+'.mpp']
    requested_sha = requested_sha.strip().lower()
    if not re.fullmatch(r'[0-9a-f]{64}', requested_sha) or requested_sha != mpp_sha256:
        raise ValueError('Downloaded MPP SHA-256 differs from the explicitly approved digest')
    run_id = str(candidate_run_id)
    if not run_id.isdigit():
        raise ValueError('Candidate Actions run ID must be numeric')
    info = json.loads((root/'output'/'build-info.json').read_text())
    source_commit = info.get('source_commit', '')
    expected_run_url = f"https://github.com/{config['repository']}/actions/runs/{run_id}"
    if info.get('run_url') != expected_run_url:
        raise ValueError('Candidate build metadata does not match the selected Actions run')
    if info.get('mpp_sha256') != mpp_sha256:
        raise ValueError('Candidate build metadata MPP digest differs from the downloaded MPP')
    load_device_evidence(evidence_path, config, run_id, source_commit, mpp_sha256)
    return expected, source_commit


def publish(root, evidence_path):
    config = json.loads((root/'release.json').read_text())
    repo = config['repository']; base = 'repos/'+repo; main_head = os.environ['GITHUB_SHA']; tag = 'v'+config['version']
    if os.environ['GITHUB_REPOSITORY'] != repo:
        raise ValueError('Repository identity mismatch')
    current = api(base+'/git/ref/heads/main')['object']['sha']
    if current != main_head:
        raise ValueError('main advanced during promotion; retry from the current main revision')
    run_id = os.environ['CANDIDATE_RUN_ID']
    expected, source_commit = verify_candidate(
        root, config, run_id, os.environ['EXPECTED_MPP_SHA256'], evidence_path)
    comparison = api(base+f'/compare/{source_commit}...{main_head}')
    if comparison.get('status') not in ('ahead', 'identical'):
        raise ValueError('Candidate source is not an ancestor of current main')
    old_feed = json.loads((root/'patches-bundle.json').read_text()) if (root/'patches-bundle.json').exists() else None
    if old_feed and version_tuple(config['version']) <= version_tuple(old_feed['version']):
        raise ValueError('Increment release.json and the bundle version before publishing a new source')
    release = select_release(api(base+'/releases?per_page=100'),tag,'PatchInsta '+config['version'])
    if release is None:
        listed = json.loads(gh('release','list','--repo',repo,'--limit','100','--json','tagName,isDraft'))
        if any(r['tagName'] == tag for r in listed):
            release = find_release(base,tag) # Known to exist: wait for REST, never create a duplicate.
    if release is None:
        # Use the POST response's numeric ID rather than trying to rediscover a new
        # draft through a public, potentially stale collection or /tags endpoint.
        release = api(base+'/releases', {'tag_name':tag,'target_commitish':source_commit,
                      'name':'PatchInsta '+config['version'],'draft':True,
                      'body':(root/'RELEASE-NOTES.md').read_text()+f"\n\nPhysical Samsung Fold validation passed. Candidate: https://github.com/{repo}/actions/runs/{run_id}. MPP SHA-256: {expected['PatchInsta-'+config['version']+'.mpp']}"})
    # Published releases are immutable here. A retry may finish publishing the feed but never
    # silently replace the already-distributed binary, which contains a build timestamp.
    if release['draft']:
        if release['target_commitish'] != source_commit or release['tag_name'] != tag:
            if release['assets'] or release['name'] != 'PatchInsta '+config['version'] or release['author']['login'] != 'github-actions[bot]':
                raise ValueError('Nonempty or foreign draft belongs to a different source commit')
            release = api(base+'/releases/'+str(release['id']),
                          {'tag_name':tag,'target_commitish':source_commit,'body':(root/'RELEASE-NOTES.md').read_text()+f"\n\nPhysical Samsung Fold validation passed. Candidate: https://github.com/{repo}/actions/runs/{run_id}. MPP SHA-256: {expected['PatchInsta-'+config['version']+'.mpp']}"}, 'PATCH')
        release['assets'] = upload_assets(base,release,root/'output')
    with tempfile.TemporaryDirectory() as temp:
        download_assets(base,release['assets'],temp)
        actual = verify_kit(temp, config)
        info = json.loads((Path(temp)/'build-info.json').read_text())
        if info['source_commit'] != source_commit:
            raise ValueError('Release was built from a different commit')
        if actual != expected:
            raise ValueError('Downloaded release differs from the explicitly validated candidate assets')
        print('Authenticated release download verified:',json.dumps(actual,sort_keys=True))
    if release['draft']:
        release = api(base+'/releases/'+str(release['id']),
                      {'tag_name':tag,'target_commitish':source_commit,'draft':False,'make_latest':'true'}, 'PATCH')
        if release['draft'] or release['tag_name'] != tag:
            raise ValueError('GitHub did not publish the requested versioned release')
    feed = metadata(config, release)
    commit = api(base+'/git/commits/'+main_head)
    tree = api(base+'/git/trees', {'base_tree':commit['tree']['sha'], 'tree':[
        {'path':'patches-bundle.json','mode':'100644','type':'blob','content':json.dumps(feed,indent=2)+'\n'}]})
    feed_commit = api(base+'/git/commits', {'message':f"chore(release): publish Morphe source {config['version']} [skip ci]", 'tree':tree['sha'],'parents':[main_head]})
    api(base+'/git/refs/heads/main', {'sha':feed_commit['sha'],'force':False}, 'PATCH')
    print('Published release:',release['html_url']); print('Morphe feed commit:',feed_commit['sha'])
    status = {'release':release['html_url'], 'feed_commit':feed_commit['sha'], 'anonymous_access':False,
              'candidate_run_id':run_id, 'source_commit':source_commit,
              'mpp_sha256':expected['PatchInsta-'+config['version']+'.mpp'],
              'physical_device_validation':'passed'}
    private = api(base)['private']
    # Never present authenticated access as a working remote source in Manager.
    url = f'https://raw.githubusercontent.com/{repo}/main/patches-bundle.json'
    try:
        verify_public(url, feed, actual['PatchInsta-'+config['version']+'.mpp'])
        status['anonymous_access'] = True
    except HTTPError as error:
        if not private or error.code not in (403,404):
            raise
        status['blocked_reason'] = 'Private repository: anonymous Morphe HTTP access unavailable'
        print('::warning::Release is verified, but the repository must be public before Morphe can access its remote source.')
    (root/'publication-result.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Promote a physically validated PatchInsta candidate')
    parser.add_argument('--promote', action='store_true', help='require physical-device evidence and an approved MPP digest')
    parser.add_argument('--evidence', default='validation-evidence.json', help='physical validation JSON file')
    args = parser.parse_args()
    if not args.promote:
        parser.error('Direct publication is disabled; use the 4.1.9 promotion workflow')
    publish(Path(__file__).resolve().parents[1], Path(args.evidence))

