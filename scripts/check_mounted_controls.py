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

PAGE_BASELINE_REF = '3633309194fedc922c6f0aa7494fe064ec484796'
PAGE_BASELINE_SHA256 = '53bd2eebce4178ee69219233436decf5ee3a34899ad99d6335c1ddc83d2104a1'
PAGE_SUITES = {
    'app.morphe.extension.instagram.patches.reels.FoldReelsOwnedControlsTest': {
        'regressions': {
            'partialOwnerHidesAnonymousImageTextAndNamedRepostWhilePreservingComment': 'expected:<4> but was:<0>',
            'lateCommentAndCountReleaseHiddenAncestorWithoutRediscovery': 'expected:<4> but was:<0>',
            'laterMountedMediaAndBudgetAbortWholeOwner': 'expected:<4> but was:<0>',
            'reboundAndDetachedOwnersReleaseAllLeases': 'expected:<4> but was:<0>',
            'ownedRailCannotHideNewCommentOrRenewAfterRebind': None,
        },
        'guards': {'foreignAndAmbiguousOwnersCannotHideUnknowns', 'mediaAndIncompleteOwnersDoNotHideAnyBranch'},
    },
    'app.morphe.extension.instagram.patches.reels.FoldReelsCommentAnchorTest': {
        'regressions': {
            'changingNativeColumnAndCommentCountCannotMoveTheCommentAnchor': 'expected:<700.0> but was:<430.0>',
            'paginationResizeAndRebindUseTheCurrentInteractivePageCentre': 'expected:<800.0> but was:<430.0>',
            'ownerThatIsAlsoTheRailAnchorsOnceAndYieldsToSheetsAndCancellation': 'expected:<700.0> but was:<430.0>',
        },
        'guards': {'identicalRediscoveryPreservesNativeCommentTouchAndVerticalTransfer'},
    },
}


def probe_spec(probe):
    if probe == 'mounted':
        return {'suite': SUITE, 'regressions': {name: 'expected:<4> but was:<0>' for name in REGRESSIONS},
                'guards': GUARDS, 'baseline_ref': BASELINE_REF, 'baseline_sha256': BASELINE_SHA256,
                'evidence': 'controls-evidence', 'reverse': 'mounted-controls-9e849b68.patch',
                'schema': 'patchinsta-mounted-controls-probe/v1'}
    if probe == 'paging':
        if not PAGE_SUITES or any(not spec['regressions'] for spec in PAGE_SUITES.values()):
            raise ValueError('Paging probe requires its distinct suite and exact failing methods')
        seen = set(REGRESSIONS) | GUARDS
        for name, spec in PAGE_SUITES.items():
            methods = set(spec['regressions']) | spec['guards']
            if name == SUITE or methods & seen or set(spec['regressions']) & spec['guards']:
                raise ValueError('Paging methods and suite must be distinct from the original probe')
            if any(message is not None and (not isinstance(message, str) or not message)
                   for message in spec['regressions'].values()):
                raise ValueError('Paging failures require an exact assertion for every method')
            seen.update(methods)
        return {'suite': next(iter(PAGE_SUITES)), 'suites': PAGE_SUITES,
                'baseline_ref': PAGE_BASELINE_REF, 'baseline_sha256': PAGE_BASELINE_SHA256,
                'evidence': 'page-actions-evidence', 'reverse': 'page-actions-36333091.patch',
                'schema': 'patchinsta-page-actions-probe/v1'}
    raise ValueError('Unknown probe')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_report(report, phase, exit_code, probe='mounted', expected_suite=None):
    spec = probe_spec(probe)
    if phase not in ('negative', 'positive'):
        raise ValueError('Unknown probe phase')
    if exit_code != (1 if phase == 'negative' else 0):
        raise ValueError(f'{phase}: unexpected Gradle exit code {exit_code}')
    suite = ET.parse(report).getroot()
    if probe == 'paging':
        name = suite.attrib.get('name')
        if name not in spec['suites']:
            raise ValueError(f'{phase}: unexpected suite/counts {suite.attrib}')
        spec = {'suite': name, **spec['suites'][name]}
    if expected_suite is not None and suite.attrib.get('name') != expected_suite:
        raise ValueError(f'{phase}: XML suite does not match its filename')
    expected_failures = set(spec['regressions']) if phase == 'negative' else set()
    expected_methods = set(spec['regressions']) | spec['guards']
    expected_counts = {'tests': len(expected_methods), 'failures': len(expected_failures), 'errors': 0, 'skipped': 0}
    counts = {key: int(suite.attrib[key]) for key in expected_counts}
    if suite.tag != 'testsuite' or suite.attrib['name'] != spec['suite'] or counts != expected_counts:
        raise ValueError(f'{phase}: unexpected suite/counts {suite.attrib}')
    cases = suite.findall('testcase')
    names = [case.attrib['name'] for case in cases]
    if len(names) != len(expected_methods) or set(names) != expected_methods:
        raise ValueError(f'{phase}: missing, duplicate or unexpected test cases {names}')
    failed = set()
    for case in cases:
        if case.attrib['classname'] != spec['suite'] or case.find('error') is not None or case.find('skipped') is not None:
            raise ValueError(f'{phase}: non-test failure or skipped case')
        failures = case.findall('failure')
        if failures:
            if case.attrib['name'] not in spec['regressions']:
                raise ValueError(f"{phase}: unexpected failing methods {case.attrib['name']}")
            expected_message = spec['regressions'][case.attrib['name']]
            message = failures[0].attrib.get('message', '')
            matches = expected_message in message if expected_message is not None else (
                message in ('', 'java.lang.AssertionError')
                and spec['suite'] + '.' + case.attrib['name'] + '(' in (failures[0].text or ''))
            if len(failures) != 1 or failures[0].attrib.get('type') != 'java.lang.AssertionError' \
                    or not matches:
                raise ValueError(f'{phase}: expected visibility regression, got {ET.tostring(case, encoding="unicode")}')
            failed.add(case.attrib['name'])
    if failed != expected_failures:
        raise ValueError(f'{phase}: unexpected failing methods {failed}')
    return {'phase': phase, 'gradle_exit_code': exit_code, **counts,
            'failed_methods': sorted(failed), 'passed_methods': sorted(set(names) - failed)}


def verify_reports(directory, phase, exit_code, probe='mounted'):
    spec = probe_spec(probe)
    suites = list(spec['suites']) if probe == 'paging' else [SUITE]
    expected = {'TEST-' + name + '.xml' for name in suites}
    reports = {path.name for path in directory.glob('TEST-*.xml')}
    if not expected <= reports or (phase == 'negative' and reports != expected):
        raise ValueError(f'{phase}: missing or unexpected fresh reports {sorted(reports)}')
    results = {name: verify_report(directory / ('TEST-' + name + '.xml'), phase, exit_code, probe, name)
               for name in suites}
    if probe == 'mounted':
        return results[SUITE]
    return {'phase': phase, 'gradle_exit_code': exit_code,
            **{key: sum(result[key] for result in results.values()) for key in ('tests','failures','errors','skipped')},
            'failed_methods': sorted(method for result in results.values() for method in result['failed_methods']),
            'passed_methods': sorted(method for result in results.values() for method in result['passed_methods']),
            'suites': results}


def run_negative(upstream, evidence, probe='mounted'):
    spec = probe_spec(probe)
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
    suites = list(spec['suites']) if probe == 'paging' else [SUITE]
    command = ['./gradlew', ':extensions:instagram:testReleaseUnitTest']
    for name in suites:
        command.extend(['--tests', name])
    command.extend(['--init-script', str(init), '--rerun-tasks', '--no-daemon', '--console=plain'])
    result = subprocess.run(command, cwd=upstream, check=False)
    return verify_reports(directory / 'xml', 'negative', result.returncode, probe)


def report_snapshot(directory):
    return {path.relative_to(directory).as_posix(): digest(path.read_bytes())
            for path in sorted(directory.rglob('*')) if path.is_file()}


def write_once(path, verdict):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(verdict, indent=2) + '\n')


def main(root, phase, probe='mounted'):
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise ValueError('This Gradle probe is CI-only; run its parser unit tests locally')
    spec = probe_spec(probe)
    upstream = root / 'upstream'
    source = upstream / CONTROL_PATH
    reverse = root / 'diagnostics' / spec['reverse']
    candidate = source.read_bytes()
    if digest(candidate) == spec['baseline_sha256']:
        raise ValueError('The candidate still contains the old controls')
    evidence = root / spec['evidence']
    summary = evidence / 'summary.json'
    identity = {'schema': spec['schema'], 'baseline_ref': spec['baseline_ref'],
                'baseline_controls_sha256': spec['baseline_sha256'], 'candidate_controls_sha256': digest(candidate),
                'reverse_patch_sha256': digest(reverse.read_bytes())}
    if phase == 'positive':
        verdict = json.loads((evidence / 'negative.json').read_text(encoding='utf-8'))
        if any(verdict.get(key) != value for key, value in identity.items()):
            raise ValueError('Positive controls do not match the negative-control candidate/identity')
        if verdict.get('negative_files_sha256') != report_snapshot(evidence / 'negative'):
            raise ValueError('Negative-control report bytes changed before the full suite')
        if verdict.get('negative') != verify_reports(evidence / 'negative/xml', 'negative', 1, probe):
            raise ValueError('Negative-control evidence changed before the full suite')
        # The workflow reaches this command only after the full Gradle suite returned 0.
        reports = upstream / 'extensions/instagram/build/test-results/testReleaseUnitTest'
        verdict['positive'] = verify_reports(reports, 'positive', 0, probe)
        write_once(summary, verdict)
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
        if digest(source.read_bytes()) != spec['baseline_sha256']:
            raise ValueError(f"The negative production file is not the exact {spec['baseline_ref'][:8]} blob")
        negative = run_negative(upstream, evidence, probe)
    finally:
        source.write_bytes(candidate)
        if source.read_bytes() != candidate:
            raise ValueError('Candidate controls were not restored')
    verdict = {**identity, 'negative': negative, 'positive': None,
               'negative_files_sha256': report_snapshot(evidence / 'negative')}
    write_once(evidence / 'negative.json', verdict)
    print(json.dumps(verdict, indent=2))


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        raise SystemExit('Usage: check_mounted_controls.py negative|positive [mounted|paging]')
    main(Path(__file__).resolve().parents[1], sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else 'mounted')
