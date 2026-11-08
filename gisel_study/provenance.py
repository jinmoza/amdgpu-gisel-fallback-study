from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_build_provenance(
    *, build: Path, source: Path, expected_sha: str, tools: tuple[Path, ...]
) -> dict[str, Any]:
    path = build / "gisel-study-provenance.json"
    if not path.is_file():
        raise ValueError(f"missing LLVM build provenance: {path}")
    try:
        provenance = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid LLVM build provenance: {path}: {error}") from error
    if provenance.get("schema") != 1:
        raise ValueError("unsupported LLVM build provenance schema")
    if provenance.get("llvm_sha") != expected_sha:
        raise ValueError(
            "LLVM build provenance revision mismatch: "
            f"expected {expected_sha}, got {provenance.get('llvm_sha')}"
        )
    if Path(str(provenance.get("llvm_source", ""))).resolve() != source.resolve():
        raise ValueError("LLVM build provenance source path mismatch")
    if provenance.get("llvm_enable_assertions") is not True:
        raise ValueError("LLVM build provenance does not enable assertions")
    recorded_tools = provenance.get("tools")
    if not isinstance(recorded_tools, dict):
        raise TypeError("LLVM build provenance has no tool hashes")
    for tool in tools:
        if not tool.is_file():
            raise ValueError(f"provenance tool is missing: {tool}")
        actual = sha256_file(tool)
        expected = recorded_tools.get(tool.name)
        if actual != expected:
            raise ValueError(
                f"LLVM tool hash mismatch for {tool.name}: expected {expected}, got {actual}"
            )
    return provenance
