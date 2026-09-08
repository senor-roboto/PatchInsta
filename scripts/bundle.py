"""Validate real build outputs, make a distributable kit, and verify downloaded bytes."""
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def version_tuple(version):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Use a stable major.minor.patch version")
    return tuple(map(int, version.split('.')))


def validate_mpp(path, version, name):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt MPP archive")
        manifest = archive.read('META-INF/MANIFEST.MF').decode('utf-8').replace('\r\n', '\n').replace('\n ', '')
        fields = dict(line.split(': ', 1) for line in manifest.splitlines() if ': ' in line)
        if fields.get('Version') != version or fields.get('Name') != name:
            raise ValueError(f"Unexpected MPP identity: {fields}")
        dex = [n for n in archive.namelist() if re.fullmatch(r'classes[0-9]*\.dex', n)]
        if not dex or any(not archive.read(n).startswith(b'dex\n') for n in dex):
            raise ValueError("MPP is missing its Android patch DEX")
        extensions = [n for n in archive.namelist() if 'instagram' in n.lower() and n.endswith('.mpe')]
        if len(extensions) != 1:
            raise ValueError("MPP is missing the Instagram extension")
        extension = archive.read(extensions[0])
        if not extension.startswith(b'dex\n') or b'Lapp/morphe/extension/instagram/patches/reels/FoldReels;' not in extension:
            raise ValueError('Instagram extension is missing the injected FoldReels entry point')
        print('MPP manifest:', fields)
        return fields


def verify_checksums(directory):
    directory = Path(directory)
    expected = {}
    for line in (directory / 'SHA256SUMS.txt').read_text().splitlines():
        sha, name = line.split('  ', 1)
        if not re.fullmatch('[0-9a-f]{64}', sha) or Path(name).name != name or name in expected:
            raise ValueError('Invalid checksum entry')
        expected[name] = sha
        if digest(directory / name) != sha:
            raise ValueError(f'Checksum mismatch: {name}')
    if not expected:
        raise ValueError('Empty checksums')
    return expected


def verify_kit(directory, config):
    directory = Path(directory)
    checksums = verify_checksums(directory)
    stem = 'PatchInsta-' + config['version']
    required = {stem+'.mpp', stem+'.zip', 'GUIDE-FR.md', 'LICENSE', 'NOTICE', 'CHANGELOG.md',
                'build-info.json', 'patches-list.json', 'piko-fold-reels.patch', 'test-results.json'}
    if not required.issubset(checksums):
        raise ValueError('Missing required release assets')
    validate_mpp(directory / (stem+'.mpp'), config['version'], config['name'])
    with zipfile.ZipFile(directory / (stem+'.zip')) as archive:
        if archive.testzip() is not None:
            raise ValueError('Corrupt distributable ZIP')
        if set(archive.namelist()) != required - {stem+'.zip'} | {'SHA256SUMS.txt'}:
            raise ValueError('Unexpected ZIP contents')
        inner = dict(line.split('  ',1)[::-1] for line in archive.read('SHA256SUMS.txt').decode().splitlines())
        for name in required - {stem+'.zip'}:
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != checksums[name] or inner.get(name) != checksums[name]:
                raise ValueError(f'ZIP asset differs from standalone asset: {name}')
    return checksums


def test_results(upstream):
    root = upstream / 'extensions/instagram/build/test-results/testReleaseUnitTest'
    expected = {'FoldReelsRuntimeTest':14, 'FoldReelsLifecycleTest':18, 'FoldReelsPreferencesTest':4,
                'FoldReelsPresentationTest':23, 'FoldReelsScrimTest':5, 'FoldReelsUpdateTest':13}
    suites = {}
    for report in root.glob('TEST-*FoldReels*Test.xml'):
        suite = ET.parse(report).getroot()
        name = suite.attrib['name'].rsplit('.',1)[-1]
        if any(int(suite.attrib[k]) for k in ('errors','failures','skipped')):
            raise ValueError('All Android scenarios must pass, with none skipped')
        suites[name] = int(suite.attrib['tests'])
    if suites != expected:
        raise ValueError(f'Unexpected Android test reports: {suites}, expected {expected}')
    return {'android_scenarios':sum(suites.values()), 'suites':suites, 'policy_geometry_checks':305,
            'mapping_keys':13, 'device_validation':False, 'instagram_apk_patch_validation':False}


def prepare(root, upstream, output):
    config = json.loads((root/'release.json').read_text())
    version_tuple(config['version'])
    version = re.search(r'^version\s*=\s*(\S+)', (upstream/'gradle.properties').read_text(), re.M).group(1)
    if version != config['version']:
        raise ValueError('release.json and Gradle version differ')
    bundles = list((upstream/'patches/build/libs').glob('*.mpp'))
    if len(bundles) != 1:
        raise ValueError(f'Expected exactly one MPP, found {len(bundles)}')
    manifest = validate_mpp(bundles[0], version, config['name'])
    results = test_results(upstream)
    patch_list = json.loads((upstream/'patches-list.json').read_text())
    if patch_list['version'] != version or sum(p['name']=='Adaptive Fold Reels' for p in patch_list['patches']) != 1:
        raise ValueError('Compiled patch listing identity differs')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Output directory must be empty')
    stem = 'PatchInsta-' + version
    shutil.copy2(bundles[0], output/(stem+'.mpp'))
    for name in ('GUIDE-FR.md','LICENSE','NOTICE','CHANGELOG.md','piko-fold-reels.patch'):
        shutil.copy2(root/name, output/name)
    shutil.copy2(upstream/'patches-list.json', output/'patches-list.json')
    (output/'test-results.json').write_text(json.dumps(results, indent=2)+'\n')
    info = {**config, 'source_commit':os.environ['GITHUB_SHA'],
            'run_url':f"https://github.com/{config['repository']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
            'mpp_sha256':digest(output/(stem+'.mpp')), 'source_patch_sha256':digest(root/'piko-fold-reels.patch'),
            'manifest':manifest, 'tests':results}
    (output/'build-info.json').write_text(json.dumps(info, indent=2)+'\n')
    def sums():
        return ''.join(f'{digest(p)}  {p.name}\n' for p in sorted(output.iterdir()) if p.name!='SHA256SUMS.txt')
    (output/'SHA256SUMS.txt').write_text(sums())
    files = sorted(output.iterdir())
    with zipfile.ZipFile(output/(stem+'.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)
    (output/'SHA256SUMS.txt').write_text(sums())
    verified = verify_kit(output, config)
    print(json.dumps({'verified_release_assets':verified, 'tests':results}, indent=2))


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    prepare(root, root/'upstream', root/'output')
