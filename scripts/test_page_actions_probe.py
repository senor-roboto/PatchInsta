"""Keep the second negative control strict and preserve both phase reports."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree import ElementTree as ET
import check_mounted_controls as probe


class PageActionsProbeTests(unittest.TestCase):
    # Parser fixtures only; production suite/methods are supplied separately.
    fixture_suite = 'app.morphe.extension.instagram.patches.reels.ParserFixtureTest'
    fixture_reds = {'visibilityCase': 'expected:<4> but was:<0>',
                    'positionCase': 'expected:<240.0> but was:<84.0>'}
    fixture_guards = {'guardCase'}

    def setUp(self):
        self.spec = patch.object(probe, 'PAGE_SUITES', {self.fixture_suite: {
            'regressions': self.fixture_reds, 'guards': self.fixture_guards}})
        self.spec.start()
        self.addCleanup(self.spec.stop)

    def xml(self, phase='negative'):
        negative = phase == 'negative'
        suite = ET.Element('testsuite', name=self.fixture_suite, tests='3',
                           failures='2' if negative else '0', errors='0', skipped='0')
        for name in sorted(set(self.fixture_reds) | self.fixture_guards):
            case = ET.SubElement(suite, 'testcase', name=name, classname=self.fixture_suite)
            if negative and name in self.fixture_reds:
                ET.SubElement(case, 'failure', type='java.lang.AssertionError',
                              message=self.fixture_reds[name])
        return suite

    def check(self, suite, phase='negative', code=1):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'report.xml'
            ET.ElementTree(suite).write(report, encoding='utf-8')
            return probe.verify_report(report, phase, code, 'paging')

    def fixture(self, root):
        spec = probe.probe_spec('paging')
        source = root / 'upstream' / probe.CONTROL_PATH
        source.parent.mkdir(parents=True)
        source.write_bytes(b'candidate parser fixture')
        reverse = root / 'diagnostics' / spec['reverse']
        reverse.parent.mkdir()
        reverse.write_bytes(b'reverse parser fixture')
        evidence = root / spec['evidence']
        negative = evidence / 'negative/xml' / ('TEST-' + spec['suite'] + '.xml')
        negative.parent.mkdir(parents=True)
        ET.ElementTree(self.xml()).write(negative, encoding='utf-8')
        positive = root / 'upstream/extensions/instagram/build/test-results/testReleaseUnitTest' / negative.name
        positive.parent.mkdir(parents=True)
        ET.ElementTree(self.xml('positive')).write(positive, encoding='utf-8')
        verdict = {'schema': spec['schema'], 'baseline_ref': spec['baseline_ref'],
                   'baseline_controls_sha256': spec['baseline_sha256'],
                   'candidate_controls_sha256': probe.digest(source.read_bytes()),
                   'reverse_patch_sha256': probe.digest(reverse.read_bytes()),
                   'negative': probe.verify_reports(negative.parent, 'negative', 1, 'paging'),
                   'positive': None, 'negative_files_sha256': probe.report_snapshot(evidence / 'negative')}
        probe.write_once(evidence / 'negative.json', verdict)
        return evidence, negative, source

    def positive(self, root):
        with patch.dict('os.environ', GITHUB_ACTIONS='true'), contextlib.redirect_stdout(io.StringIO()):
            probe.main(root, 'positive', 'paging')

    def test_exact_method_assertions_and_positive_cases_are_accepted(self):
        negative = self.check(self.xml())
        self.assertEqual(negative['failed_methods'], sorted(self.fixture_reds))
        self.assertEqual(negative['passed_methods'], sorted(self.fixture_guards))
        self.assertEqual(self.check(self.xml('positive'), 'positive', 0)['failures'], 0)

    def test_a_visibility_assertion_cannot_substitute_for_the_position_failure(self):
        suite = self.xml()
        for case in suite:
            if case.attrib['name'] == 'positionCase':
                case.find('failure').set('message', self.fixture_reds['visibilityCase'])
        with self.assertRaisesRegex(ValueError, 'visibility regression'):
            self.check(suite)

    def test_old_suite_is_not_the_second_control(self):
        suite = self.xml()
        suite.set('name', probe.SUITE)
        with self.assertRaisesRegex(ValueError, 'suite/counts'):
            self.check(suite)

    def test_all_green_old_run_and_compiler_exits_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'suite/counts'):
            self.check(self.xml('positive'))
        for code in (0, -9, 2):
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, 'exit code'):
                self.check(self.xml(), code=code)

    def test_absent_fresh_xml_cannot_be_a_reproduction(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(FileNotFoundError):
            probe.verify_report(Path(directory) / 'missing.xml', 'negative', 1, 'paging')

    def test_positive_summary_is_created_once_and_negative_bytes_are_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence, negative, _ = self.fixture(root)
            before = (evidence / 'negative.json').read_bytes(), negative.read_bytes()
            self.positive(root)
            summary = json.loads((evidence / 'summary.json').read_text())
            self.assertEqual(summary['positive']['failures'], 0)
            self.assertEqual(before, ((evidence / 'negative.json').read_bytes(), negative.read_bytes()))
            with self.assertRaises(FileExistsError):
                self.positive(root)

    def test_semantically_identical_but_modified_negative_xml_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence, negative, _ = self.fixture(root)
            negative.write_bytes(negative.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'report bytes changed'):
                self.positive(root)
            self.assertFalse((evidence / 'summary.json').exists())

    def test_changed_candidate_cannot_reuse_negative_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, source = self.fixture(root)
            source.write_bytes(b'another candidate')
            with self.assertRaisesRegex(ValueError, 'candidate/identity'):
                self.positive(root)

    def test_compiler_failure_without_fresh_xml_restores_only_candidate_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = probe.probe_spec('paging')
            source = root / 'upstream' / probe.CONTROL_PATH
            source.parent.mkdir(parents=True)
            candidate = b'candidate parser fixture'
            baseline = b'baseline parser fixture'
            source.write_bytes(candidate)
            reverse = root / 'diagnostics' / spec['reverse']
            reverse.parent.mkdir()
            reverse.write_bytes(b'reverse parser fixture')

            def command(arguments, **kwargs):
                if arguments[0] == './gradlew':
                    return SimpleNamespace(returncode=1)  # compiler failure, no XML
                if '--reverse' in arguments and '--check' not in arguments:
                    source.write_bytes(baseline)
                return SimpleNamespace(returncode=0)

            with patch.dict('os.environ', GITHUB_ACTIONS='true'), \
                    patch.object(probe, 'PAGE_BASELINE_SHA256', probe.digest(baseline)), \
                    patch.object(probe.subprocess, 'check_output', return_value='1\t1\t' + probe.CONTROL_PATH), \
                    patch.object(probe.subprocess, 'run', side_effect=command), \
                    self.assertRaisesRegex(ValueError, 'fresh reports'):
                probe.main(root, 'negative', 'paging')
            self.assertEqual(source.read_bytes(), candidate)
            self.assertFalse((root / spec['evidence'] / 'negative.json').exists())
            self.assertFalse((root / spec['evidence'] / 'summary.json').exists())

    def test_both_baselines_are_pinned_and_unconfigured_probe_fails_closed(self):
        self.assertEqual(probe.probe_spec('mounted')['baseline_ref'],
                         '9e849b68b70ce0b3ee5f3221a403a1d431bea6b9')
        self.assertEqual(probe.probe_spec('paging')['baseline_ref'],
                         '3633309194fedc922c6f0aa7494fe064ec484796')
        self.assertEqual(probe.probe_spec('paging')['baseline_sha256'],
                         '53bd2eebce4178ee69219233436decf5ee3a34899ad99d6335c1ddc83d2104a1')
        with patch.object(probe, 'PAGE_SUITES', {}), self.assertRaisesRegex(ValueError, 'distinct suite'):
            probe.probe_spec('paging')


class TwoPageSuitesTests(unittest.TestCase):
    def reports(self, directory, phase):
        directory.mkdir()
        for name, spec in probe.PAGE_SUITES.items():
            failed = spec['regressions'] if phase == 'negative' else {}
            methods = set(spec['regressions']) | spec['guards']
            xml = ET.Element('testsuite', name=name, tests=str(len(methods)),
                             failures=str(len(failed)), errors='0', skipped='0')
            for method in sorted(methods):
                case = ET.SubElement(xml, 'testcase', name=method, classname=name)
                if method in failed:
                    failure = ET.SubElement(case, 'failure', type='java.lang.AssertionError',
                                            message=failed[method] or 'java.lang.AssertionError')
                    failure.text = 'java.lang.AssertionError\n\tat ' + name + '.' + method + '(Test.java:1)'
            ET.ElementTree(xml).write(directory / ('TEST-' + name + '.xml'), encoding='utf-8')

    def test_exact_two_suites_eight_reds_three_guards_and_eleven_positive_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.reports(root / 'negative', 'negative')
            self.reports(root / 'positive', 'positive')
            negative = probe.verify_reports(root / 'negative', 'negative', 1, 'paging')
            positive = probe.verify_reports(root / 'positive', 'positive', 0, 'paging')
            self.assertEqual((negative['tests'], negative['failures'], len(negative['passed_methods'])), (11, 8, 3))
            self.assertEqual((positive['tests'], positive['failures']), (11, 0))
            owned = next(name for name in probe.PAGE_SUITES if name.endswith('OwnedControlsTest'))
            anchor = next(name for name in probe.PAGE_SUITES if name.endswith('CommentAnchorTest'))
            (root / 'negative' / ('TEST-' + owned + '.xml')).write_bytes(
                (root / 'negative' / ('TEST-' + anchor + '.xml')).read_bytes())
            with self.assertRaisesRegex(ValueError, 'filename'):
                probe.verify_reports(root / 'negative', 'negative', 1, 'paging')

    def test_unmessaged_assertion_requires_its_exact_method_stack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.reports(root / 'negative', 'negative')
            owned = next(name for name in probe.PAGE_SUITES if name.endswith('OwnedControlsTest'))
            path = root / 'negative' / ('TEST-' + owned + '.xml')
            xml = ET.parse(path)
            for case in xml.getroot():
                if case.attrib['name'] == 'ownedRailCannotHideNewCommentOrRenewAfterRebind':
                    case.find('failure').text = 'java.lang.AssertionError\n\tat another.Method(Test.java:1)'
            xml.write(path, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'visibility regression'):
                probe.verify_reports(root / 'negative', 'negative', 1, 'paging')


if __name__ == '__main__':
    unittest.main()
