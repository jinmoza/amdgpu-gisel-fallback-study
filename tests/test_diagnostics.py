import unittest

from gisel_study.diagnostics import (
    parse_fallback_functions,
    parse_remarks_yaml,
)


class DiagnosticsTest(unittest.TestCase):
    def test_classifies_amdgpu_register_bank_legalization(self):
        remarks = parse_remarks_yaml(
            """--- !Missed
Pass: amdgpu-reg-bank-legalize
Name: GISelFailure
Function: kernel
Args:
  - String: no rule matched
  - Inst: '%1:vgpr(i32) = G_FOO %0:vgpr'
...
"""
        )

        self.assertEqual(remarks[0].stage, "regbank-legalize")

    def test_parses_fallback_warning_once_per_function(self):
        stderr = """
remark: unable to lower arguments (in function: kernel_a)
warning: Instruction selection used fallback path for kernel_a
warning: Instruction selection used fallback path for kernel_a
warning: Instruction selection used fallback path for _Z8kernel_bPi
"""

        self.assertEqual(
            parse_fallback_functions(stderr),
            ["kernel_a", "_Z8kernel_bPi"],
        )

    def test_parses_and_normalizes_gisel_remark(self):
        yaml_text = """--- !Missed
Pass:            gisel-select
Name:            'GISelFailure: '
Function:        s_add_v2s16
Args:
  - String:          cannot select
  - String:          ': '
  - Inst:            '%2:sgpr(<2 x s16>) = G_ADD %0:sgpr, %1:sgpr'
  - String:          ' (in function: s_add_v2s16)'
...
"""

        remarks = parse_remarks_yaml(yaml_text)

        self.assertEqual(len(remarks), 1)
        remark = remarks[0]
        self.assertEqual(remark.function, "s_add_v2s16")
        self.assertEqual(remark.stage, "instruction-select")
        self.assertEqual(remark.reason, "cannot select")
        self.assertEqual(remark.opcode, "G_ADD")
        self.assertEqual(remark.llt, "<2 x s16>")
        self.assertEqual(
            remark.signature,
            "gisel-select|cannot select|G_ADD|<2 x s16>|sgpr",
        )

    def test_preserves_llt_before_register_bank_assignment(self):
        remarks = parse_remarks_yaml(
            """--- !Missed
Pass: gisel-legalize
Name: 'GISelFailure: '
Function: kernel
Args:
  - String: unable to legalize instruction
  - Inst: '%12:_(<4 x s32>) = G_FOO %3:_(p1)'
...
"""
        )

        self.assertEqual(remarks[0].opcode, "G_FOO")
        self.assertEqual(remarks[0].llt, "<4 x s32>")
        self.assertEqual(remarks[0].register_bank, "unassigned")
        self.assertEqual(
            remarks[0].signature,
            "gisel-legalize|unable to legalize instruction|G_FOO|<4 x s32>|unassigned",
        )


if __name__ == "__main__":
    unittest.main()
