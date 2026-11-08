import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gisel_study.publish import export_public_results


class PublishResultsTest(unittest.TestCase):
    def test_exports_curated_results_and_sanitizes_workspace_paths(self):
        with TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            run_dir = workspace / "results" / "run-a"
            reproducer = run_dir / "reproducers" / "cluster-a"
            raw_case = run_dir / "cases" / "case-a"
            reproducer.mkdir(parents=True)
            raw_case.mkdir(parents=True)

            (run_dir / "report.md").write_text("report\n", encoding="utf-8")
            (run_dir / "summary.csv").write_text("count\n1\n", encoding="utf-8")
            (run_dir / "run.json").write_text(
                json.dumps({"source": str(workspace / "third_party/llvm-project")}),
                encoding="utf-8",
            )
            (run_dir / "cases.jsonl").write_text(
                json.dumps({"source": str(workspace / "input.ll")}) + "\n",
                encoding="utf-8",
            )
            (run_dir / "fallbacks.jsonl").write_text(
                json.dumps({"case_id": "case-a"}) + "\n", encoding="utf-8"
            )
            (reproducer / "replay.json").write_text(
                json.dumps({"command": [str(workspace / "build/llvm/bin/llc")]}),
                encoding="utf-8",
            )
            (reproducer / "original.ll").write_text(
                f'; source_filename = "{workspace}/input.ll"\n', encoding="utf-8"
            )
            (reproducer / "input.bc").write_bytes(b"\x00binary")
            (raw_case / "stderr.txt").write_text("raw evidence", encoding="utf-8")

            output_dir = workspace / "published-results" / "run-a"
            export_public_results(run_dir, output_dir, workspace=workspace)

            self.assertTrue((output_dir / "report.md").is_file())
            self.assertTrue((output_dir / "reproducers/cluster-a/input.bc").is_file())
            self.assertFalse((output_dir / "cases").exists())
            self.assertIn(
                "<WORKSPACE>/third_party/llvm-project",
                (output_dir / "run.json").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "<WORKSPACE>/build/llvm/bin/llc",
                (output_dir / "reproducers/cluster-a/replay.json").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertNotIn(
                str(workspace),
                "\n".join(
                    path.read_text(encoding="utf-8", errors="ignore")
                    for path in output_dir.rglob("*")
                    if path.is_file()
                ),
            )
            self.assertTrue((output_dir / "SHA256SUMS").is_file())

    def test_refuses_to_overwrite_an_existing_export(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "run"
            output_dir = root / "published"
            run_dir.mkdir()
            output_dir.mkdir()

            with self.assertRaisesRegex(FileExistsError, "already exists"):
                export_public_results(run_dir, output_dir, workspace=root)


if __name__ == "__main__":
    unittest.main()
