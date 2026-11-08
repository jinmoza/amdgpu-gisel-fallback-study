import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gisel_study.manifest import discover_inputs, load_manifest


class ManifestTest(unittest.TestCase):
    def test_loads_paths_relative_to_manifest_and_builds_matrix(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "experiment.yaml"
            manifest_path.write_text(
                """
llvm:
  source: third_party/llvm-project
  build: build/llvm
  sha: deadbeef
rocm_examples:
  source: third_party/rocm-examples
  sha: cafe1234
docker_image: rocm/example@sha256:1234
targets: [gfx900, gfx1030, gfx1100]
hip_optimization_levels: [O0, O2]
workers: 16
timeouts:
  llvm: 60
  hip: 180
""",
                encoding="utf-8",
            )

            manifest = load_manifest(manifest_path)

            self.assertEqual(manifest.llvm_source, root / "third_party/llvm-project")
            self.assertEqual(manifest.llvm_build, root / "build/llvm")
            self.assertEqual(manifest.targets, ("gfx900", "gfx1030", "gfx1100"))
            self.assertEqual(manifest.hip_optimization_levels, ("O0", "O2"))
            self.assertEqual(manifest.workers, 16)

    def test_discovers_only_expected_ir_and_hip_inputs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            llvm_root = root / "llvm"
            hip_root = root / "rocm"
            (llvm_root / "nested").mkdir(parents=True)
            (hip_root / "HIP-Basic" / "a").mkdir(parents=True)
            (hip_root / "HIP-Doc" / "b").mkdir(parents=True)
            (hip_root / "Applications" / "c").mkdir(parents=True)
            (llvm_root / "a.ll").touch()
            (llvm_root / "nested" / "b.ll").touch()
            (llvm_root / "ignored.mir").touch()
            (hip_root / "HIP-Basic" / "a" / "one.hip").touch()
            (hip_root / "HIP-Doc" / "b" / "two.hip").touch()
            (hip_root / "Applications" / "c" / "three.hip").touch()
            (hip_root / "Applications" / "c" / "host.cpp").touch()

            llvm_inputs, hip_inputs = discover_inputs(llvm_root, hip_root)

            self.assertEqual(
                [path.name for path in llvm_inputs],
                ["a.ll", "b.ll"],
            )
            self.assertEqual(
                [path.name for path in hip_inputs],
                ["three.hip", "one.hip", "two.hip"],
            )


if __name__ == "__main__":
    unittest.main()
