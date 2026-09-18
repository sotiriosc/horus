"""Release checks must reject silent simulation failures and missing evidence."""
import unittest
from scripts.run_checks import validate_output


class PublicRunnerTests(unittest.TestCase):
    def test_zero_failures_is_accepted(self):
        validate_output('PASS: 7   FAIL: 0\nALL TESTS PASSED', ('ALL TESTS PASSED',), True)

    def test_zero_exit_style_failure_is_rejected(self):
        for output in ('FAIL\n', 'FAIL: 1', 'PASS summary\nfails=2', 'FATAL: simulation stopped'):
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                validate_output(output, (), True)

    def test_missing_measurement_is_rejected(self):
        with self.assertRaises(RuntimeError):
            validate_output('command completed', ('PREDICTIONS EXACT',))

    def test_negative_scientific_result_can_be_expected(self):
        validate_output('E0M6 K1 FAIL; E0M9 K1 PASS', ('E0M6 K1 FAIL', 'E0M9 K1 PASS'))
