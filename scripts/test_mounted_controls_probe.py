"""Reject false negative-control evidence before accepting a candidate build."""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from check_mounted_controls import GUARDS, REGRESSIONS, SUITE, verify_report


class MountedControlsProbeTests(unittest.TestCase):
    def suite(self, failed=()):
        suite = ET.Element('testsuite', name=SUITE, tests='5', failures=str(len(failed)), errors='0', skipped='0')
        for name in sorted(REGRESSIONS | GUARDS):
            case = ET.SubElement(suite, 'testcase', name=name, classname=SUITE)
            if name in failed:
                ET.SubElement(case, 'failure', type='java.lang.AssertionError', message='expected:<4> but was:<0>')
        return suite

    def check(self, suite, phase='negative', exit_code=1):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'report.xml'
            ET.ElementTree(suite).write(report, encoding='utf-8')
            return verify_report(report, phase, exit_code)

    def test_accepts_exactly_three_old_regressions_and_two_passing_guards(self):
        result = self.check(self.suite(REGRESSIONS))
        self.assertEqual(result['failed_methods'], sorted(REGRESSIONS))
        self.assertEqual(result['passed_methods'], sorted(GUARDS))

    def test_accepts_all_five_candidate_tests_passing(self):
        result = self.check(self.suite(), 'positive', 0)
        self.assertEqual(result['tests'], 5)
        self.assertEqual(result['failures'], 0)

    def test_exit_status_must_match_the_expected_phase(self):
        for phase, failed, code in [('negative', REGRESSIONS, 0), ('negative', REGRESSIONS, -9), ('positive', (), 1)]:
            with self.subTest(phase=phase, code=code), self.assertRaisesRegex(ValueError, 'exit code'):
                self.check(self.suite(failed), phase, code)

    def test_runtime_exception_or_wrong_assertion_is_not_a_reproduction(self):
        for change in [{'type': 'java.lang.RuntimeException'}, {'message': 'expected:<1> but was:<0>'}]:
            suite = self.suite(REGRESSIONS); suite.find('testcase/failure').attrib.update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'visibility regression'):
                self.check(suite)

    def test_same_failure_count_on_the_wrong_methods_is_rejected(self):
        failed = set(GUARDS) | {sorted(REGRESSIONS)[0]}
        with self.assertRaisesRegex(ValueError, 'failing methods'):
            self.check(self.suite(failed))

    def test_missing_or_duplicate_methods_are_rejected(self):
        for duplicate in (False, True):
            suite = self.suite(REGRESSIONS)
            if duplicate:
                suite[-1].set('name', suite[0].attrib['name'])
            else:
                suite.remove(suite[-1])
            with self.subTest(duplicate=duplicate), self.assertRaisesRegex(ValueError, 'test cases'):
                self.check(suite)

    def test_errors_skips_and_wrong_suite_counts_are_rejected(self):
        for change in [{'errors': '1'}, {'skipped': '1'}, {'tests': '4'}, {'failures': '2'}, {'name': SUITE + 'Other'}]:
            suite = self.suite(REGRESSIONS); suite.attrib.update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'suite/counts'):
                self.check(suite)

    def test_case_errors_or_skips_cannot_hide_behind_suite_totals(self):
        for tag in ('error', 'skipped'):
            suite = self.suite(REGRESSIONS); ET.SubElement(suite[0], tag)
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, 'non-test failure'):
                self.check(suite)

    def test_nonzero_build_exit_without_xml_is_not_a_reproduction(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(FileNotFoundError):
            verify_report(Path(directory) / 'missing.xml', 'negative', 1)

    def test_all_green_old_run_is_rejected_even_if_exit_code_is_nonzero(self):
        with self.assertRaisesRegex(ValueError, 'suite/counts'):
            self.check(self.suite())


if __name__ == '__main__':
    unittest.main()
