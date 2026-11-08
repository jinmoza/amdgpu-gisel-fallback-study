import sys
import unittest

from gisel_study.runner import (
    classify_codegen,
    parse_defined_functions,
    run_process,
)


class RunnerTest(unittest.TestCase):
    def test_runs_process_and_captures_output(self):
        result = run_process(
            [
                sys.executable,
                "-c",
                "import sys; print('out'); print('err', file=sys.stderr)",
            ],
            timeout=5,
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "out")
        self.assertEqual(result.stderr.strip(), "err")
        self.assertGreaterEqual(result.elapsed_ms, 0)

    def test_marks_timed_out_process(self):
        result = run_process(
            [sys.executable, "-c", "import time; time.sleep(1)"],
            timeout=0.01,
        )

        self.assertEqual(result.status, "timeout")
        self.assertIsNone(result.returncode)

    def test_parses_only_defined_function_symbols(self):
        nm_output = """
kernel_a T ---------------- 0
helper t ---------------- 0
weak_fn W ---------------- 0
global_data D 00000000 4
undefined U
kernel_a T ---------------- 0
"""

        self.assertEqual(
            parse_defined_functions(nm_output),
            ["kernel_a", "helper", "weak_fn"],
        )

    def test_excludes_selectiondag_failure(self):
        self.assertEqual(
            classify_codegen(sdag_status="failed", gisel_status="ok", fallback_count=0),
            "sdag_invalid",
        )

    def test_classifies_gisel_success(self):
        self.assertEqual(
            classify_codegen(sdag_status="ok", gisel_status="ok", fallback_count=0),
            "gisel_success",
        )

    def test_classifies_successful_fallback(self):
        self.assertEqual(
            classify_codegen(sdag_status="ok", gisel_status="ok", fallback_count=2),
            "gisel_fallback_sdag_success",
        )

    def test_classifies_fallback_followed_by_failure(self):
        self.assertEqual(
            classify_codegen(sdag_status="ok", gisel_status="failed", fallback_count=1),
            "gisel_fallback_then_failure",
        )

    def test_classifies_hard_gisel_failure(self):
        self.assertEqual(
            classify_codegen(sdag_status="ok", gisel_status="failed", fallback_count=0),
            "gisel_hard_failure_without_fallback",
        )


if __name__ == "__main__":
    unittest.main()
