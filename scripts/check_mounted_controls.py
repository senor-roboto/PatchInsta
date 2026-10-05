"""Run the five mounted-control tests against exact old and candidate production in CI."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

BASELINE_REF = '9e849b68b70ce0b3ee5f3221a403a1d431bea6b9'
BASELINE_SHA256 = '3f9aa6cd589cc1ca719a92c8fa148444906ac1007a95ef049582ab71f403e059'
CONTROL_PATH = 'extensions/instagram/src/main/java/app/morphe/extension/instagram/patches/reels/FoldReelsControls.java'
SUITE = 'app.morphe.extension.instagram.patches.reels.FoldReelsMountedControlsTest'
REGRESSIONS = {
    'neighbourLikeAndCountHideBeforeACompleteRailIsMounted',
    'laterMountedActionsUseTheKnownOwnerWithoutWaitingForRediscovery',
    'detachedActionAndReboundOwnerCannotCarryAHideLeaseToAnotherPage',
}
GUARDS = {
    'classNameAndResourceNameAloneDoNotQualifyUnknownOwners',
    'mixedNamedWrapperCannotHideItsNativeCommentDescendant',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_report(report, phase, exit_code):
    if phase not in ('negative', 'positive'):
        raise ValueError('Unknown probe phase')
    expected_failures = REGRESSIONS if phase == 'negative' else set()
    if exit_code != (1 if phase == 'negative' else 0):
        raise ValueError(f'{phase}: unexpected Gradle exit code {exit_code}')
    suite = ET.parse(report).getroot()
    expected_counts = {'tests': 5, 'failures': len(expected_failures), 'errors': 0, 'skipped': 0}
    counts = {key: int(suite.attrib[key]) for key in expected_counts}
    if suite.tag != 'testsuite' or suite.attrib['name'] != SUITE or counts != expected_counts:
        raise ValueError(f'{phase}: unexpected suite/counts {suite.attrib}')
    cases = suite.findall('testcase')
    names = [case.attrib['name'] for case in cases]
    if len(names) != 5 or set(names) != REGRESSIONS | GUARDS:
        raise ValueError(f'{phase}: missing, duplicate or unexpected test cases {names}')
    failed = set()
    for case in cases:
        if case.attrib['classname'] != SUITE or case.find('error') is not None or case.find('skipped') is not None:
            raise ValueError(f'{phase}: non-test failure or skipped case')
        failures = case.findall('failure')
        if failures:
            if len(failures) != 1 or failures[0].attrib.get('type') != 'java.lang.AssertionError' \
                    or 'expected:<4> but was:<0>' not in failures[0].attrib.get('message', ''):
                raise ValueError(f'{phase}: expected visibility regression, got {ET.tostring(case, encoding="unicode")}')
            failed.add(case.attrib['name'])
    if failed != expected_failures:
        raise ValueError(f'{phase}: unexpected failing methods {failed}')
    return {'phase': phase, 'gradle_exit_code': exit_code, **counts,
            'failed_methods': sorted(failed), 'passed_methods': sorted(set(names) - failed)}


def run_negative(upstream, evidence):
    directory = evidence / 'negative'
    directory.mkdir()
    def quoted(path):
        return "'" + path.as_posix().replace('\\', '\\\\').replace("'", "\\'") + "'"
    init = directory / 'reports.gradle'
    init.write_text('gradle.projectsEvaluated {\n'
                    '    def target = gradle.rootProject.project(":extensions:instagram").tasks.named("testReleaseUnitTest").get()\n'
                    f'    target.reports.junitXml.outputLocation.set(new File({quoted(directory / "xml")}))\n'
                    f'    target.reports.html.outputLocation.set(new File({quoted(directory / "html")}))\n'
                    f'    target.binaryResultsDirectory.set(new File({quoted(directory / "binary")}))\n'
                    '}\n', encoding='utf-8')
    command = ['./gradlew', ':extensions:instagram:testReleaseUnitTest', '--tests', SUITE,
               '--init-script', str(init), '--rerun-tasks', '--no-daemon', '--console=plain']
    result = subprocess.run(command, cwd=upstream, check=False)
    reports = list((directory / 'xml').glob('TEST-*.xml'))
    expected = directory / 'xml' / ('TEST-' + SUITE + '.xml')
    if reports != [expected]:
        raise ValueError(f'negative: missing or unexpected fresh reports {reports}')
    return verify_report(expected, 'negative', result.returncode)


def main(root, phase):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise ValueError('This Gradle probe is CI-only; run its parser unit tests locally')
    upstream = root / 'upstream'
    source = upstream / CONTROL_PATH
    reverse = root / 'diagnostics/mounted-controls-9e849b68.patch'
    candidate = source.read_bytes()
    if digest(candidate) == BASELINE_SHA256:
        raise ValueError('The candidate still contains the old controls')
    evidence = root / 'controls-evidence'
    summary = evidence / 'summary.json'
    identity = {'schema': 'patchinsta-mounted-controls-probe/v1', 'baseline_ref': BASELINE_REF,
                'baseline_controls_sha256': BASELINE_SHA256, 'candidate_controls_sha256': digest(candidate),
                'reverse_patch_sha256': digest(reverse.read_bytes())}
    if phase == 'positive':
        verdict = json.loads(summary.read_text(encoding='utf-8'))
        if any(verdict.get(key) != value for key, value in identity.items()):
            raise ValueError('Positive controls do not match the negative-control candidate/identity')
        negative_report = evidence / 'negative/xml' / ('TEST-' + SUITE + '.xml')
        if verdict.get('negative') != verify_report(negative_report, 'negative', 1):
            raise ValueError('Negative-control evidence changed before the full suite')
        # The workflow reaches this command only after the full Gradle suite returned 0.
        report = upstream / 'extensions/instagram/build/test-results/testReleaseUnitTest' / ('TEST-' + SUITE + '.xml')
        verdict['positive'] = verify_report(report, 'positive', 0)
        summary.write_text(json.dumps(verdict, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(verdict, indent=2))
        return
    if phase != 'negative':
        raise ValueError('Choose negative or positive')
    evidence.mkdir()  # A retry must not consume reports from an earlier invocation.
    git_apply = ['git', '-c', 'core.autocrlf=false', 'apply']
    stat = subprocess.check_output([*git_apply, '--numstat', '--reverse', str(reverse)],
                                   cwd=upstream, text=True).strip().splitlines()
    if len(stat) != 1 or stat[0].split('\t')[-1] != CONTROL_PATH:
        raise ValueError('The negative control must replace exactly FoldReelsControls.java')
    try:
        subprocess.run([*git_apply, '--check', '--reverse', str(reverse)], cwd=upstream, check=True)
        subprocess.run([*git_apply, '--reverse', str(reverse)], cwd=upstream, check=True)
        if digest(source.read_bytes()) != BASELINE_SHA256:
            raise ValueError('The negative production file is not the exact 9e849b68 blob')
        negative = run_negative(upstream, evidence)
    finally:
        source.write_bytes(candidate)
        if source.read_bytes() != candidate:
            raise ValueError('Candidate controls were not restored')
    verdict = {**identity, 'negative': negative, 'positive': None}
    summary.write_text(json.dumps(verdict, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(verdict, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: check_mounted_controls.py negative|positive')
    main(Path(__file__).resolve().parents[1], sys.argv[1])
