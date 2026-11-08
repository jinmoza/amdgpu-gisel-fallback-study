import hashlib
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gisel_study.runner import CaseSpec, ToolPaths, collect_codegen_case


def _write_executable(path: Path, body: str) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n" + textwrap.dedent(body), encoding="utf-8"
    )
    path.chmod(0o755)


class CollectCaseTest(unittest.TestCase):
    def test_collects_successful_fallback_with_raw_evidence(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.ll"
            source.write_text("define void @kernel() { ret void }\n", encoding="utf-8")
            llvm_as = root / "llvm-as"
            llvm_nm = root / "llvm-nm"
            llc = root / "llc"
            _write_executable(
                llvm_as,
                """
                import pathlib, shutil, sys
                assert '-disable-verify' in sys.argv
                source = next(arg for arg in sys.argv[1:] if arg.endswith('.ll'))
                shutil.copyfile(source, pathlib.Path(sys.argv[sys.argv.index('-o') + 1]))
                """,
            )
            _write_executable(
                llvm_nm,
                """
                print('kernel T ---------------- 0')
                """,
            )
            _write_executable(
                llc,
                """
                import pathlib, sys
                if '-global-isel=1' in sys.argv:
                    output = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('-pass-remarks-output='))
                    yaml_text = "--- !Missed\\nPass: gisel-select\\nName: 'GISelFailure: '\\nFunction: kernel\\nArgs:\\n  - String: cannot select\\n  - Inst: '%2:vgpr(s32) = G_FOO %0:vgpr'\\n...\\n"
                    pathlib.Path(output).write_text(yaml_text)
                    print('warning: Instruction selection used fallback path for kernel', file=sys.stderr)
                """,
            )
            artifact_dir = root / "artifacts"
            case = CaseSpec(
                case_id="abc123",
                corpus="llvm",
                input_id="input.ll",
                source=source,
                gpu="gfx900",
                opt="O2",
                timeout=5,
            )

            record, fallbacks = collect_codegen_case(
                case,
                ToolPaths(llc=llc, llvm_as=llvm_as, llvm_nm=llvm_nm),
                artifact_dir,
            )

            self.assertEqual(record["function_count"], 1)
            self.assertEqual(
                record["input_sha256"], hashlib.sha256(source.read_bytes()).hexdigest()
            )
            self.assertEqual(record["fallback_functions"], ["kernel"])
            self.assertEqual(record["outcome"], "gisel_fallback_sdag_success")
            self.assertEqual(
                fallbacks[0]["signature"], "gisel-select|cannot select|G_FOO|s32|vgpr"
            )
            self.assertTrue((artifact_dir / "sdag.stderr.txt").exists())
            self.assertTrue((artifact_dir / "gisel.stderr.txt").exists())
            self.assertTrue((artifact_dir / "remarks.yaml").exists())
            self.assertTrue((artifact_dir / "record.json").exists())

    def test_malformed_remarks_do_not_replace_codegen_classification(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.ll"
            source.write_text("define void @kernel() { ret void }\n", encoding="utf-8")
            llvm_as = root / "llvm-as"
            llvm_nm = root / "llvm-nm"
            llc = root / "llc"
            _write_executable(
                llvm_as,
                """
                import pathlib, shutil, sys
                source = next(arg for arg in sys.argv[1:] if arg.endswith('.ll'))
                shutil.copyfile(source, pathlib.Path(sys.argv[sys.argv.index('-o') + 1]))
                """,
            )
            _write_executable(llvm_nm, "print('kernel T ---------------- 0')\n")
            _write_executable(
                llc,
                """
                import pathlib, sys
                if '-global-isel=1' in sys.argv:
                    output = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('-pass-remarks-output='))
                    pathlib.Path(output).write_text('--- !Missed\\nArgs: [unterminated')
                    print('warning: Instruction selection used fallback path for kernel', file=sys.stderr)
                """,
            )

            record, fallbacks = collect_codegen_case(
                CaseSpec("case", "llvm", "input.ll", source, "gfx900", "O2", 5),
                ToolPaths(llc=llc, llvm_as=llvm_as, llvm_nm=llvm_nm),
                root / "artifacts",
            )

            self.assertEqual(record["outcome"], "gisel_fallback_sdag_success")
            self.assertEqual(record["remarks_parse_status"], "failed")
            self.assertIn("ParserError", record["remarks_parse_error"])
            self.assertEqual(len(fallbacks), 1)
            self.assertEqual(fallbacks[0]["signature"], "unknown")


if __name__ == "__main__":
    unittest.main()
