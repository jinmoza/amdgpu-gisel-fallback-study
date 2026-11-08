import unittest

from gisel_study.report import render_markdown_report


class ReportTest(unittest.TestCase):
    def test_renders_summary_and_root_cause_table(self):
        cases = [
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "input_id": "a.ll",
                "outcome": "gisel_fallback_sdag_success",
                "function_count": 2,
                "fallback_functions": ["kernel"],
            },
            {
                "corpus": "hip",
                "gpu": "gfx900",
                "opt": "O2",
                "input_id": "broken.hip",
                "outcome": "source_compile_failure",
                "function_count": 0,
                "fallback_functions": [],
            },
        ]
        fallbacks = [
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "input_id": "a.ll",
                "function": "kernel",
                "stage": "instruction-select",
                "reason": "cannot select",
                "opcode": "G_FOO",
                "llt": "s32",
                "signature": "sig",
            }
        ]

        report = render_markdown_report(
            cases,
            fallbacks,
            {"run_id": "run-1", "llvm_sha": "deadbeef", "rocm_examples_sha": "cafe"},
        )

        self.assertIn("# AMDGPU GlobalISel 显式回退报告", report)
        self.assertIn("run-1", report)
        self.assertIn("SDAG 有效、已尝试 GlobalISel 的案例：1", report)
        self.assertIn("显式回退案例：1（100.00%）", report)
        self.assertIn("归一化根因簇：1", report)
        self.assertIn("50.00%", report)
        self.assertIn("instruction-select", report)
        self.assertIn("G_FOO", report)
        self.assertIn("source_compile_failure", report)
        self.assertIn("本报告不检测静默错误生成", report)
        self.assertIn("ROCm 设备库函数", report)
        self.assertIn("首个 `GISelFailure`", report)
        self.assertIn("函数分母统计这些案例中定义的函数", report)


if __name__ == "__main__":
    unittest.main()
