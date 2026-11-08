import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gisel_study.collect import (
    SourceCase,
    _collect_source_case_safe,
    _git_checkout_state,
    _validate_revision,
    build_docker_hip_command,
    collect_experiment,
    enumerate_source_cases,
    stable_case_id,
)
from gisel_study.manifest import Manifest
from gisel_study.runner import ToolPaths


class CollectTest(unittest.TestCase):
    def test_rejects_a_checkout_at_the_wrong_revision(self):
        with self.assertRaisesRegex(ValueError, "LLVM checkout mismatch"):
            _validate_revision("actual", "expected", "LLVM")

        with self.assertRaisesRegex(ValueError, "cannot verify source archive"):
            _validate_revision(None, "expected", "source archive")

    def test_requires_a_clean_git_checkout(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            tracked = root / "tracked.txt"
            tracked.write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "commit",
                    "-qm",
                    "initial",
                ],
                check=True,
            )

            head = _git_checkout_state(root, "test checkout")
            self.assertEqual(len(head), 40)

            tracked.write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dirty"):
                _git_checkout_state(root, "test checkout")

    def test_missing_tool_does_not_leave_an_unusable_run_directory(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=root / "third_party/llvm-project",
                llvm_build=root / "build/llvm",
                llvm_sha="llvm-sha",
                rocm_examples_source=root / "third_party/rocm-examples",
                rocm_examples_sha="rocm-sha",
                docker_image="unused",
                targets=("gfx900",),
                hip_optimization_levels=("O2",),
                workers=1,
                llvm_timeout=5,
                hip_timeout=5,
            )

            with self.assertRaises(FileNotFoundError):
                collect_experiment(manifest, run_id="failed-setup", corpora={"llvm"})

            self.assertFalse((root / "results/failed-setup").exists())

    def test_records_unexpected_case_error_without_aborting_run(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "broken.ll"
            source.write_text("broken", encoding="utf-8")
            artifact_dir = root / "artifacts"
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=root,
                llvm_build=root / "build",
                llvm_sha="llvm-sha",
                rocm_examples_source=root,
                rocm_examples_sha="rocm-sha",
                docker_image="unused",
                targets=("gfx900",),
                hip_optimization_levels=("O2",),
                workers=1,
                llvm_timeout=5,
                hip_timeout=5,
            )
            case = SourceCase("case", "llvm", "broken.ll", source, "gfx900", "O2", 5)
            tools = ToolPaths(root / "llc", root / "llvm-as", root / "llvm-nm")

            with patch(
                "gisel_study.collect._collect_source_case",
                side_effect=RuntimeError("unexpected parser failure"),
            ):
                record, fallbacks = _collect_source_case_safe(
                    manifest, case, tools, artifact_dir
                )

            self.assertEqual(record["outcome"], "infrastructure_error")
            self.assertEqual(fallbacks, [])
            self.assertIn(
                "unexpected parser failure",
                (artifact_dir / "infrastructure.stderr.txt").read_text(),
            )

    def test_collect_experiment_writes_aggregated_outputs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            llvm_source = root / "third_party/llvm-project"
            llvm_input = llvm_source / "llvm/test/CodeGen/AMDGPU/a.ll"
            llvm_input.parent.mkdir(parents=True)
            llvm_input.write_text(
                "define void @kernel() { ret void }\n", encoding="utf-8"
            )
            build_bin = root / "build/llvm/bin"
            build_bin.mkdir(parents=True)

            def executable(name: str, body: str) -> None:
                path = build_bin / name
                path.write_text(
                    "#!/usr/bin/env python3\n" + textwrap.dedent(body), encoding="utf-8"
                )
                path.chmod(0o755)

            executable(
                "llvm-as",
                """
                import shutil, sys
                shutil.copyfile(sys.argv[1], sys.argv[sys.argv.index('-o') + 1])
                """,
            )
            executable("llvm-nm", "print('kernel T ---------------- 0')\n")
            executable("llc", "pass\n")
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=llvm_source,
                llvm_build=root / "build/llvm",
                llvm_sha="llvm-sha",
                rocm_examples_source=root / "third_party/rocm-examples",
                rocm_examples_sha="rocm-sha",
                docker_image="unused",
                targets=("gfx900",),
                hip_optimization_levels=("O0", "O2"),
                workers=1,
                llvm_timeout=5,
                hip_timeout=5,
            )

            with (
                patch(
                    "gisel_study.collect._git_checkout_state",
                    side_effect=["llvm-sha", "rocm-sha"],
                ),
                patch(
                    "gisel_study.collect.validate_build_provenance",
                    return_value={"schema": 1},
                ),
            ):
                run_dir = collect_experiment(
                    manifest, run_id="test-run", corpora={"llvm"}
                )

            self.assertEqual(run_dir, root / "results/test-run")
            self.assertTrue((run_dir / "cases.jsonl").exists())
            self.assertTrue((run_dir / "fallbacks.jsonl").exists())
            self.assertTrue((run_dir / "summary.csv").exists())
            self.assertTrue((run_dir / "report.md").exists())
            self.assertIn("gisel_success", (run_dir / "cases.jsonl").read_text())

    def test_enumerates_llvm_and_hip_matrices(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            llvm_source = root / "third_party/llvm-project"
            llvm_input = llvm_source / "llvm/test/CodeGen/AMDGPU/a.ll"
            rocm_source = root / "third_party/rocm-examples"
            hip_input = rocm_source / "HIP-Basic/saxpy/main.hip"
            llvm_input.parent.mkdir(parents=True)
            hip_input.parent.mkdir(parents=True)
            llvm_input.touch()
            hip_input.touch()
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=llvm_source,
                llvm_build=root / "build/llvm",
                llvm_sha="llvm-sha",
                rocm_examples_source=rocm_source,
                rocm_examples_sha="rocm-sha",
                docker_image="image",
                targets=("gfx900", "gfx1100"),
                hip_optimization_levels=("O0", "O2"),
                workers=1,
                llvm_timeout=60,
                hip_timeout=180,
            )

            cases = enumerate_source_cases(manifest, [llvm_input], [hip_input])

            self.assertEqual(len(cases), 6)
            llvm_cases = [case for case in cases if case.corpus == "llvm"]
            hip_cases = [case for case in cases if case.corpus == "hip"]
            self.assertEqual({case.opt for case in llvm_cases}, {"O2"})
            self.assertEqual({case.opt for case in hip_cases}, {"O0", "O2"})
            self.assertEqual({case.gpu for case in cases}, {"gfx900", "gfx1100"})
            self.assertEqual(llvm_cases[0].input_id, "a.ll")
            self.assertEqual(hip_cases[0].input_id, "HIP-Basic/saxpy/main.hip")

    def test_case_id_is_stable_and_configuration_specific(self):
        first = stable_case_id("hip", "HIP-Basic/saxpy/main.hip", "gfx900", "O2")
        second = stable_case_id("hip", "HIP-Basic/saxpy/main.hip", "gfx900", "O2")
        other = stable_case_id("hip", "HIP-Basic/saxpy/main.hip", "gfx1100", "O2")

        self.assertEqual(first, second)
        self.assertNotEqual(first, other)
        self.assertEqual(len(first), 16)

    def test_builds_networkless_unprivileged_docker_compile(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "third_party/rocm-examples/HIP-Basic/saxpy/main.hip"
            output = root / "results/run/cases/id/input.bc"
            source.parent.mkdir(parents=True)
            output.parent.mkdir(parents=True)
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=root / "third_party/llvm-project",
                llvm_build=root / "build/llvm",
                llvm_sha="llvm-sha",
                rocm_examples_source=root / "third_party/rocm-examples",
                rocm_examples_sha="rocm-sha",
                docker_image="rocm/image@sha256:1234",
                targets=("gfx900",),
                hip_optimization_levels=("O2",),
                workers=1,
                llvm_timeout=60,
                hip_timeout=180,
            )

            command = build_docker_hip_command(
                manifest, source=source, output=output, gpu="gfx900", opt="O2"
            )

            self.assertEqual(command[:3], ["docker", "run", "--rm"])
            self.assertIn("--network=none", command)
            self.assertIn("--user", command)
            self.assertIn("rocm/image@sha256:1234", command)
            self.assertIn("/study/build/llvm/bin/clang++", command)
            self.assertIn("-I/study/third_party/rocm-examples/Common", command)
            self.assertIn("-I/study/third_party/rocm-examples/External", command)
            self.assertIn(
                "/study/third_party/rocm-examples/HIP-Basic/saxpy/main.hip", command
            )
            self.assertIn("/study/results/run/cases/id/input.bc", command)


if __name__ == "__main__":
    unittest.main()
