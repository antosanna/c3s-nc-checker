from c3schecker.cmd import run_checks


class TestCheckRunner:
    def test_run_checks_ok(self, input_file, spec, good_check):
        self._run(input_file, spec, good_check, 1)

    def test_run_checks_ko(self, input_file, spec, bad_check):
        self._run(input_file, spec, bad_check, 0)

    @staticmethod
    def _run(input_file, spec, check, expected_status):
        status, outcome = run_checks([input_file], [check], spec)
        assert status == expected_status
        assert isinstance(outcome, dict)
        assert check in outcome
        check_outcome = outcome[check]
        assert "status" in check_outcome
        assert check_outcome["status"] == expected_status
