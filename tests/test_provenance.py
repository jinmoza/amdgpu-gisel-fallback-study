import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gisel_study.provenance import validate_build_provenance


class ProvenanceTest(unittest.TestCase):
    def test_validates_pinned_source_assertions_and_tool_hashes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            build = root / "build"
            tool = build / "bin/llc"
            source.mkdir()
            tool.parent.mkdir(parents=True)
            tool.write_bytes(b"llc")
            provenance = {
                "schema": 1,
                "llvm_sha": "abc123",
                "llvm_source": str(source.resolve()),
                "llvm_enable_assertions": True,
                "tools": {
                    "llc": hashlib.sha256(tool.read_bytes()).hexdigest(),
                },
            }
            (build / "gisel-study-provenance.json").write_text(
                json.dumps(provenance), encoding="utf-8"
            )

            self.assertEqual(
                validate_build_provenance(
                    build=build,
                    source=source,
                    expected_sha="abc123",
                    tools=(tool,),
                ),
                provenance,
            )

            tool.write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "tool hash mismatch"):
                validate_build_provenance(
                    build=build,
                    source=source,
                    expected_sha="abc123",
                    tools=(tool,),
                )

    def test_requires_provenance_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "missing LLVM build provenance"):
                validate_build_provenance(
                    build=root / "build",
                    source=root / "source",
                    expected_sha="abc123",
                    tools=(),
                )


if __name__ == "__main__":
    unittest.main()
