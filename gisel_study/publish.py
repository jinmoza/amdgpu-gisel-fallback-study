from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

_ROOT_FILES = (
    "report.md",
    "summary.csv",
    "run.json",
    "cases.jsonl",
    "fallbacks.jsonl",
)
_TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".ll",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}


def export_public_results(run_dir: Path, output_dir: Path, *, workspace: Path) -> Path:
    run_dir = run_dir.resolve()
    output_dir = output_dir.resolve()
    workspace_text = str(workspace.resolve())

    if output_dir.exists():
        raise FileExistsError(f"public result export already exists: {output_dir}")

    required = tuple(run_dir / name for name in _ROOT_FILES) + (
        run_dir / "reproducers",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing public result inputs: {', '.join(missing)}")

    output_dir.mkdir(parents=True)
    for source in required:
        destination = output_dir / source.name
        if source.is_dir():
            _copy_tree(source, destination, workspace_text)
        else:
            _copy_file(source, destination, workspace_text)

    (output_dir / "README.md").write_text(
        "# Curated experiment results\n\n"
        "This directory contains the aggregate records and one representative "
        "reproducer directory per normalized fallback signature. Per-case raw "
        "logs are intentionally excluded from Git history. Paths rooted in the "
        "original checkout are written as `<WORKSPACE>`.\n",
        encoding="utf-8",
    )
    _write_checksums(output_dir)
    return output_dir


def _copy_tree(source: Path, destination: Path, workspace_text: str) -> None:
    destination.mkdir()
    for child in sorted(source.iterdir()):
        output = destination / child.name
        if child.is_dir():
            _copy_tree(child, output, workspace_text)
        else:
            _copy_file(child, output, workspace_text)


def _copy_file(source: Path, destination: Path, workspace_text: str) -> None:
    if source.suffix.lower() in _TEXT_SUFFIXES:
        text = source.read_text(encoding="utf-8", errors="surrogateescape")
        destination.write_text(
            text.replace(workspace_text, "<WORKSPACE>"),
            encoding="utf-8",
            errors="surrogateescape",
        )
    else:
        shutil.copy2(source, destination)


def _write_checksums(output_dir: Path) -> None:
    lines = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.relative_to(output_dir)}")
    (output_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
