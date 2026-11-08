import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gisel_study.manifest import Manifest
from gisel_study.reduce import (
    _reduced_output_path,
    _validate_run_metadata,
    _verify_case_source,
    select_representatives,
)


class ReduceTest(unittest.TestCase):
    def test_reduced_output_keeps_input_suffix(self):
        root = Path("/tmp/reproducer")
        self.assertEqual(_reduced_output_path(root / "original.ll"), root / "reduced.ll")
        self.assertEqual(_reduced_output_path(root / "original.bc"), root / "reduced.bc")

    def test_rejects_source_that_changed_after_collection(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.ll"
            source.write_text("original", encoding="utf-8")
            case = {
                "case_id": "case",
                "source": str(source),
                "input_sha256": "not-the-current-hash",
            }

            with self.assertRaisesRegex(ValueError, "input hash mismatch"):
                _verify_case_source(case)

    def test_rejects_run_from_another_manifest_or_toolchain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = Manifest(
                path=root / "experiment.yaml",
                root=root,
                llvm_source=root / "llvm",
                llvm_build=root / "build",
                llvm_sha="llvm-sha",
                rocm_examples_source=root / "examples",
                rocm_examples_sha="examples-sha",
                docker_image="image@sha256:digest",
                targets=("gfx900",),
                hip_optimization_levels=("O2",),
                workers=1,
                llvm_timeout=1,
                hip_timeout=1,
            )
            metadata = {
                "llvm_sha": "llvm-sha",
                "rocm_examples_sha": "examples-sha",
                "docker_image": "image@sha256:digest",
                "llvm_build_provenance": {"tools": {"llc": "old"}},
            }

            with self.assertRaisesRegex(ValueError, "toolchain provenance mismatch"):
                _validate_run_metadata(
                    metadata, manifest, {"tools": {"llc": "new"}}
                )

    def test_selects_smallest_input_per_signature(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            large = root / "large.ll"
            small = root / "small.ll"
            other = root / "other.ll"
            large.write_text("x" * 100, encoding="utf-8")
            small.write_text("x" * 10, encoding="utf-8")
            other.write_text("x" * 20, encoding="utf-8")
            cases = [
                {
                    "case_id": "large",
                    "source": str(large),
                    "gpu": "gfx900",
                    "opt": "O2",
                },
                {
                    "case_id": "small",
                    "source": str(small),
                    "gpu": "gfx900",
                    "opt": "O2",
                },
                {
                    "case_id": "other",
                    "source": str(other),
                    "gpu": "gfx1100",
                    "opt": "O2",
                },
            ]
            fallbacks = [
                {"case_id": "large", "signature": "sig-a", "function": "f"},
                {"case_id": "small", "signature": "sig-a", "function": "f"},
                {"case_id": "other", "signature": "sig-b", "function": "g"},
            ]

            selected = select_representatives(cases, fallbacks)

            self.assertEqual(len(selected), 2)
            self.assertEqual(selected["sig-a"]["case"]["case_id"], "small")
            self.assertEqual(selected["sig-b"]["case"]["case_id"], "other")


if __name__ == "__main__":
    unittest.main()
