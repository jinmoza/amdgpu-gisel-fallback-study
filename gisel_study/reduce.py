import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .commands import build_gisel_command, build_sdag_command
from .manifest import Manifest
from .provenance import sha256_file, validate_build_provenance
from .runner import run_process, write_process_evidence


def select_representatives(
    cases: list[dict[str, Any]], fallbacks: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    cases_by_id = {str(case["case_id"]): case for case in cases}
    selected: dict[str, dict[str, Any]] = {}
    for fallback in fallbacks:
        signature = str(fallback["signature"])
        case = cases_by_id.get(str(fallback["case_id"]))
        if case is None:
            continue
        source = Path(str(case["source"]))
        if not source.is_file():
            continue
        candidate = {
            "case": case,
            "fallback": fallback,
            "size": source.stat().st_size,
        }
        current = selected.get(signature)
        if current is None or (candidate["size"], str(case["case_id"])) < (
            current["size"],
            str(current["case"]["case_id"]),
        ):
            selected[signature] = candidate
    return selected


def reduce_run(run_dir: Path, manifest: Manifest, *, timeout: int = 900) -> Path:
    cases = _read_jsonl(run_dir / "cases.jsonl")
    fallbacks = _read_jsonl(run_dir / "fallbacks.jsonl")
    metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    current_provenance = validate_build_provenance(
        build=manifest.llvm_build,
        source=manifest.llvm_source,
        expected_sha=manifest.llvm_sha,
        tools=(
            manifest.llvm_build / "bin/llc",
            manifest.llvm_build / "bin/llvm-reduce",
        ),
    )
    _validate_run_metadata(metadata, manifest, current_provenance)
    selected = select_representatives(cases, fallbacks)
    output_root = run_dir / "reproducers"
    output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    llvm_reduce = manifest.llvm_build / "bin/llvm-reduce"

    for signature, representative in sorted(selected.items()):
        cluster_id = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:12]
        cluster_dir = output_root / cluster_id
        if cluster_dir.exists():
            shutil.rmtree(cluster_dir)
        cluster_dir.mkdir(exist_ok=True)
        case = representative["case"]
        fallback = representative["fallback"]
        source = _verify_case_source(case)
        original = cluster_dir / f"original{source.suffix or '.bc'}"
        shutil.copy2(source, original)
        replay = {
            "signature": signature,
            "case_id": case["case_id"],
            "input_id": case.get("input_id"),
            "function": fallback.get("function"),
            "gpu": case["gpu"],
            "opt": case["opt"],
            "sdag_command": build_sdag_command(
                llc=manifest.llvm_build / "bin/llc",
                source=original,
                gpu=str(case["gpu"]),
                opt=str(case["opt"]),
            ),
            "gisel_command": build_gisel_command(
                llc=manifest.llvm_build / "bin/llc",
                source=original,
                remarks=cluster_dir / "replay-remarks.yaml",
                gpu=str(case["gpu"]),
                opt=str(case["opt"]),
            ),
        }
        (cluster_dir / "replay.json").write_text(
            json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        result_record: dict[str, Any] = {
            "cluster_id": cluster_id,
            "signature": signature,
            "case_id": case["case_id"],
            "original": str(original),
        }
        if signature == "unknown" or not llvm_reduce.is_file():
            result_record["status"] = (
                "unknown_signature" if signature == "unknown" else "missing_llvm_reduce"
            )
            results.append(result_record)
            continue

        interesting = cluster_dir / "interesting.py"
        interesting.write_text(
            _interestingness_script(manifest, case, signature), encoding="utf-8"
        )
        interesting.chmod(0o755)
        initial = run_process([str(interesting), str(original)], timeout=60)
        write_process_evidence(cluster_dir, "initial-check", initial)
        if initial.status != "ok":
            result_record["status"] = "initial_check_failed"
            results.append(result_record)
            continue

        reduction = run_process(
            [
                str(llvm_reduce),
                "--abort-on-invalid-reduction",
                "-j",
                "2",
                f"--test={interesting}",
                str(original),
            ],
            timeout=timeout,
            cwd=cluster_dir,
        )
        write_process_evidence(cluster_dir, "reduce", reduction)
        result_record["status"] = reduction.status
        reduced = _reduced_output_path(original)
        if reduced.is_file():
            final_check = run_process([str(interesting), str(reduced)], timeout=60)
            write_process_evidence(cluster_dir, "final-check", final_check)
            result_record["final_check_status"] = final_check.status
            if final_check.status == "ok":
                result_record["reduced"] = str(reduced)
            else:
                result_record["status"] = "final_check_failed"
        results.append(result_record)

    (output_root / "reproducers.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output_root


def _validate_run_metadata(
    metadata: dict[str, Any],
    manifest: Manifest,
    current_provenance: dict[str, Any],
) -> None:
    expected = {
        "llvm_sha": manifest.llvm_sha,
        "rocm_examples_sha": manifest.rocm_examples_sha,
        "docker_image": manifest.docker_image,
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(
                f"run metadata mismatch for {key}: expected {value}, "
                f"got {metadata.get(key)}"
            )
    if metadata.get("llvm_build_provenance") != current_provenance:
        raise ValueError("run toolchain provenance mismatch")


def _verify_case_source(case: dict[str, Any]) -> Path:
    source = Path(str(case["source"]))
    if not source.is_file():
        raise ValueError(f"collected input is missing for case {case['case_id']}: {source}")
    expected = case.get("input_sha256")
    actual = sha256_file(source)
    if not expected or actual != expected:
        raise ValueError(
            f"input hash mismatch for case {case['case_id']}: "
            f"expected {expected}, got {actual}"
        )
    return source


def _reduced_output_path(original: Path) -> Path:
    return original.with_name(f"reduced{original.suffix}")


def _interestingness_script(
    manifest: Manifest, case: dict[str, Any], signature: str
) -> str:
    return f"""#!/usr/bin/env python3
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, {str(manifest.root)!r})
from gisel_study.commands import build_gisel_command, build_sdag_command
from gisel_study.diagnostics import parse_fallback_functions, parse_remarks_yaml

candidate = pathlib.Path(sys.argv[-1]).resolve()
llc = pathlib.Path({str(manifest.llvm_build / "bin/llc")!r})
gpu = {str(case["gpu"])!r}
opt = {str(case["opt"])!r}
expected = {signature!r}

try:
    sdag = subprocess.run(build_sdag_command(llc=llc, source=candidate, gpu=gpu, opt=opt), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    if sdag.returncode != 0:
        raise SystemExit(1)
    with tempfile.TemporaryDirectory() as directory:
        remarks_path = pathlib.Path(directory) / "remarks.yaml"
        gisel = subprocess.run(build_gisel_command(llc=llc, source=candidate, remarks=remarks_path, gpu=gpu, opt=opt), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=30)
        fallbacks = set(parse_fallback_functions(gisel.stderr))
        remarks = parse_remarks_yaml(remarks_path.read_text()) if remarks_path.exists() else []
        interesting = any(remark.signature == expected and remark.function in fallbacks for remark in remarks)
        raise SystemExit(0 if interesting else 1)
except (subprocess.TimeoutExpired, OSError):
    raise SystemExit(1)
"""


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
