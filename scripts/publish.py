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
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
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


def metadata(config, release):
    version_tuple(config['version'])
    # Manager's DTO uses kotlinx.datetime.LocalDateTime, without a timezone suffix.
    created = datetime.fromisoformat(release['published_at'].replace('Z','+00:00')).astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')
    return {'created_at':created, 'description':'Instagram : rattrapage au premier dessin, bandeau fixe, contour et calques de métadonnées corrigés.',
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


def publish(root):
    config = json.loads((root/'release.json').read_text())
    repo = config['repository']; base = 'repos/'+repo; head = os.environ['GITHUB_SHA']; tag = 'v'+config['version']
    if os.environ['GITHUB_REPOSITORY'] != repo:
        raise ValueError('Repository identity mismatch')
    current = api(base+'/git/ref/heads/main')['object']['sha']
    if current != head:
        raise ValueError('main advanced during the build; refusing to publish a stale source')
    old_feed = json.loads((root/'patches-bundle.json').read_text()) if (root/'patches-bundle.json').exists() else None
    if old_feed and version_tuple(config['version']) <= version_tuple(old_feed['version']):
        raise ValueError('Increment release.json and the bundle version before publishing a new source')
    expected = verify_kit(root/'output', config)
    releases = json.loads(gh('release','list','--repo',repo,'--limit','100','--json','tagName,isDraft'))
    existing = next((r for r in releases if r['tagName']==tag), None)
    if not existing:
        gh('release','create',tag,'--repo',repo,'--draft','--target',head,'--title','PatchInsta '+config['version'],
           '--notes-file',str(root/'RELEASE-NOTES.md'))
    # The REST lookup by tag does not return an unpublished draft. The authenticated
    # releases collection does; use its numeric ID for subsequent reads.
    release = next(r for r in api(base+'/releases?per_page=100') if r['tag_name']==tag)
    # Published releases are immutable here. A retry may finish publishing the feed but never
    # silently replace the already-distributed binary, which contains a build timestamp.
    if release['draft']:
        if release['target_commitish'] != head:
            if release['assets'] or release['name'] != 'PatchInsta '+config['version'] or release['author']['login'] != 'github-actions[bot]':
                raise ValueError('Nonempty or foreign draft belongs to a different source commit')
            gh('release','edit',tag,'--repo',repo,'--target',head,'--notes-file',str(root/'RELEASE-NOTES.md'))
        gh('release','upload',tag,'--repo',repo,'--clobber',*[str(p) for p in sorted((root/'output').iterdir())])
    with tempfile.TemporaryDirectory() as temp:
        gh('release','download',tag,'--repo',repo,'--dir',temp)
        actual = verify_kit(temp, config)
        info = json.loads((Path(temp)/'build-info.json').read_text())
        if info['source_commit'] != head:
            raise ValueError('Release was built from a different commit')
        if release['draft'] and actual != expected:
            raise ValueError('Downloaded release differs from prepared assets')
        print('Authenticated release download verified:',json.dumps(actual,sort_keys=True))
    if release['draft']:
        gh('release','edit',tag,'--repo',repo,'--draft=false','--latest')
        release = api(base+'/releases/'+str(release['id']))
    feed = metadata(config, release)
    commit = api(base+'/git/commits/'+head)
    tree = api(base+'/git/trees', {'base_tree':commit['tree']['sha'], 'tree':[
        {'path':'patches-bundle.json','mode':'100644','type':'blob','content':json.dumps(feed,indent=2)+'\n'}]})
    feed_commit = api(base+'/git/commits', {'message':f"chore(release): publish Morphe source {config['version']} [skip ci]", 'tree':tree['sha'],'parents':[head]})
    api(base+'/git/refs/heads/main', {'sha':feed_commit['sha'],'force':False}, 'PATCH')
    print('Published release:',release['html_url']); print('Morphe feed commit:',feed_commit['sha'])
    status = {'release':release['html_url'], 'feed_commit':feed_commit['sha'], 'anonymous_access':False}
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
    publish(Path(__file__).resolve().parents[1])
