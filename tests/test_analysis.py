import unittest

from gisel_study.analysis import build_fallback_records, summarize_cases
from gisel_study.diagnostics import parse_remarks_yaml


class AnalysisTest(unittest.TestCase):
    def test_prefers_the_gisel_failure_over_other_same_function_remarks(self):
        case = {
            "case_id": "case-0",
            "corpus": "llvm",
            "input_id": "foo.ll",
            "gpu": "gfx900",
            "opt": "O2",
            "fallback_functions": ["kernel"],
            "outcome": "gisel_fallback_sdag_success",
        }
        remarks = parse_remarks_yaml(
            """--- !Missed
Pass: gisel-legalize
Name: LostDebugLoc
Function: kernel
Args:
  - String: debug location was lost
...
--- !Missed
Pass: gisel-select
Name: GISelFailure
Function: kernel
Args:
  - String: cannot select
  - Inst: '%1:vgpr(s32) = G_FOO %0:vgpr'
...
"""
        )

        records = build_fallback_records(case, remarks)

        self.assertEqual(records[0]["stage"], "instruction-select")
        self.assertEqual(records[0]["reason"], "cannot select")
        self.assertEqual(records[0]["remark_count"], 2)

    def test_joins_fallback_function_to_same_function_remark(self):
        case = {
            "case_id": "case-1",
            "corpus": "llvm",
            "input_id": "foo.ll",
            "gpu": "gfx900",
            "opt": "O2",
            "fallback_functions": ["kernel"],
            "outcome": "gisel_fallback_sdag_success",
        }
        remarks = parse_remarks_yaml(
            """--- !Missed
Pass: gisel-legalize
Name: 'GISelFailure: '
Function: kernel
Args:
  - String: unable to legalize instruction
  - Inst: '%12:vgpr(s128) = G_FOO %3:vgpr'
...
"""
        )

        records = build_fallback_records(case, remarks)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["function"], "kernel")
        self.assertEqual(records[0]["stage"], "legalizer")
        self.assertEqual(records[0]["opcode"], "G_FOO")
        self.assertEqual(records[0]["signature"], remarks[0].signature)

    def test_preserves_fallback_without_remark_as_unknown(self):
        case = {
            "case_id": "case-2",
            "corpus": "hip",
            "input_id": "bar.hip",
            "gpu": "gfx1100",
            "opt": "O0",
            "fallback_functions": ["kernel"],
            "outcome": "gisel_fallback_sdag_success",
        }

        records = build_fallback_records(case, [])

        self.assertEqual(records[0]["stage"], "unknown")
        self.assertEqual(records[0]["signature"], "unknown")

    def test_summarizes_valid_denominators_and_fallback_rates(self):
        cases = [
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "outcome": "gisel_success",
                "function_count": 3,
                "fallback_functions": [],
            },
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "outcome": "gisel_fallback_sdag_success",
                "function_count": 2,
                "fallback_functions": ["f"],
            },
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "outcome": "sdag_invalid",
                "function_count": 9,
                "fallback_functions": [],
            },
            {
                "corpus": "llvm",
                "gpu": "gfx900",
                "opt": "O2",
                "outcome": "source_compile_failure",
                "function_count": 0,
                "fallback_functions": [],
            },
        ]
        fallbacks = [
            {"corpus": "llvm", "gpu": "gfx900", "opt": "O2", "signature": "sig"}
        ]

        rows = summarize_cases(cases, fallbacks)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["total_cases"], 4)
        self.assertEqual(row["valid_modules"], 2)
        self.assertEqual(row["valid_functions"], 5)
        self.assertEqual(row["fallback_modules"], 1)
        self.assertEqual(row["fallback_functions"], 1)
        self.assertEqual(row["module_fallback_rate"], 0.5)
        self.assertEqual(row["function_fallback_rate"], 0.2)
        self.assertEqual(row["unique_signatures"], 1)


if __name__ == "__main__":
    unittest.main()
