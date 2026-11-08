from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Manifest:
    path: Path
    root: Path
    llvm_source: Path
    llvm_build: Path
    llvm_sha: str
    rocm_examples_source: Path
    rocm_examples_sha: str
    docker_image: str
    targets: tuple[str, ...]
    hip_optimization_levels: tuple[str, ...]
    workers: int
    llvm_timeout: int
    hip_timeout: int


def load_manifest(path: Path) -> Manifest:
    path = path.resolve()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("manifest must contain a YAML mapping")
    root = path.parent
    llvm = data["llvm"]
    rocm = data["rocm_examples"]
    timeouts = data.get("timeouts", {})
    return Manifest(
        path=path,
        root=root,
        llvm_source=(root / llvm["source"]).resolve(),
        llvm_build=(root / llvm["build"]).resolve(),
        llvm_sha=str(llvm["sha"]),
        rocm_examples_source=(root / rocm["source"]).resolve(),
        rocm_examples_sha=str(rocm["sha"]),
        docker_image=str(data["docker_image"]),
        targets=tuple(str(target) for target in data["targets"]),
        hip_optimization_levels=tuple(
            str(level) for level in data["hip_optimization_levels"]
        ),
        workers=int(data.get("workers", 1)),
        llvm_timeout=int(timeouts.get("llvm", 60)),
        hip_timeout=int(timeouts.get("hip", 180)),
    )


def discover_inputs(
    llvm_root: Path, rocm_examples_root: Path
) -> tuple[list[Path], list[Path]]:
    llvm_inputs = sorted(llvm_root.rglob("*.ll"))
    hip_inputs: list[Path] = []
    for relative_root in ("HIP-Basic", "HIP-Doc", "Applications"):
        source_root = rocm_examples_root / relative_root
        if source_root.is_dir():
            hip_inputs.extend(source_root.rglob("*.hip"))
    return llvm_inputs, sorted(hip_inputs)
