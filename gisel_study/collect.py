import hashlib
import json
import os
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .commands import build_hip_compile_command
from .manifest import Manifest, discover_inputs
from .provenance import validate_build_provenance
from .report import write_reports
from .runner import (
    CaseSpec,
    ToolPaths,
    collect_codegen_case,
    run_process,
    write_process_evidence,
)


@dataclass(frozen=True)
class SourceCase:
    case_id: str
    corpus: str
    input_id: str
    source: Path
    gpu: str
    opt: str
    timeout: int


def enumerate_source_cases(
    manifest: Manifest, llvm_inputs: list[Path], hip_inputs: list[Path]
) -> list[SourceCase]:
    cases: list[SourceCase] = []
    llvm_corpus_root = manifest.llvm_source / "llvm/test/CodeGen/AMDGPU"
    for source in sorted(llvm_inputs):
        input_id = source.relative_to(llvm_corpus_root).as_posix()
        for gpu in manifest.targets:
            opt = "O2"
            cases.append(
                SourceCase(
                    case_id=stable_case_id("llvm", input_id, gpu, opt),
                    corpus="llvm",
                    input_id=input_id,
                    source=source,
                    gpu=gpu,
                    opt=opt,
                    timeout=manifest.llvm_timeout,
                )
            )
    for source in sorted(hip_inputs):
        input_id = source.relative_to(manifest.rocm_examples_source).as_posix()
        for gpu in manifest.targets:
            for opt in manifest.hip_optimization_levels:
                cases.append(
                    SourceCase(
                        case_id=stable_case_id("hip", input_id, gpu, opt),
                        corpus="hip",
                        input_id=input_id,
                        source=source,
                        gpu=gpu,
                        opt=opt,
                        timeout=manifest.hip_timeout,
                    )
                )
    return cases


def collect_experiment(
    manifest: Manifest,
    *,
    run_id: str,
    corpora: set[str],
    limit: int | None = None,
) -> Path:
    tools = ToolPaths(
        llc=manifest.llvm_build / "bin/llc",
        llvm_as=manifest.llvm_build / "bin/llvm-as",
        llvm_nm=manifest.llvm_build / "bin/llvm-nm",
    )
    for tool in (tools.llc, tools.llvm_as, tools.llvm_nm):
        if not tool.is_file():
            raise FileNotFoundError(f"required LLVM tool is missing: {tool}")

    actual_llvm_sha = _git_checkout_state(manifest.llvm_source, "LLVM")
    actual_examples_sha = _git_checkout_state(
        manifest.rocm_examples_source, "ROCm Examples"
    )
    _validate_revision(actual_llvm_sha, manifest.llvm_sha, "LLVM")
    _validate_revision(actual_examples_sha, manifest.rocm_examples_sha, "ROCm Examples")
    provenance_tools = [tools.llc, tools.llvm_as, tools.llvm_nm]
    if "hip" in corpora:
        provenance_tools.append(manifest.llvm_build / "bin/clang++")
    build_provenance = validate_build_provenance(
        build=manifest.llvm_build,
        source=manifest.llvm_source,
        expected_sha=manifest.llvm_sha,
        tools=tuple(provenance_tools),
    )

    run_dir = manifest.root / "results" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    cases_root = run_dir / "cases"
    cases_root.mkdir()

    llvm_root = manifest.llvm_source / "llvm/test/CodeGen/AMDGPU"
    llvm_inputs, hip_inputs = discover_inputs(llvm_root, manifest.rocm_examples_source)
    if "llvm" not in corpora:
        llvm_inputs = []
    if "hip" not in corpora:
        hip_inputs = []
    source_cases = enumerate_source_cases(manifest, llvm_inputs, hip_inputs)
    if limit is not None:
        source_cases = source_cases[:limit]

    metadata: dict[str, Any] = {
        "run_id": run_id,
        "started_at": _utc_now(),
        "llvm_sha": manifest.llvm_sha,
        "llvm_actual_sha": actual_llvm_sha,
        "rocm_examples_sha": manifest.rocm_examples_sha,
        "rocm_examples_actual_sha": actual_examples_sha,
        "docker_image": manifest.docker_image,
        "targets": list(manifest.targets),
        "hip_optimization_levels": list(manifest.hip_optimization_levels),
        "workers": manifest.workers,
        "llvm_build_provenance": build_provenance,
        "llvm_input_count": len(llvm_inputs),
        "hip_input_count": len(hip_inputs),
        "case_count": len(source_cases),
    }
    _write_json(run_dir / "run.json", metadata)

    case_records: list[dict[str, Any]] = []
    fallback_records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=manifest.workers) as executor:
        futures = {
            executor.submit(
                _collect_source_case_safe,
                manifest,
                source_case,
                tools,
                cases_root / source_case.case_id,
            ): source_case
            for source_case in source_cases
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            record, fallbacks = future.result()
            case_records.append(record)
            fallback_records.extend(fallbacks)
            if completed == len(futures) or completed % 100 == 0:
                print(f"collected {completed}/{len(futures)} cases", flush=True)

    case_records.sort(key=lambda row: str(row["case_id"]))
    fallback_records.sort(
        key=lambda row: (
            str(row["case_id"]),
            str(row["function"]),
            str(row["signature"]),
        )
    )
    metadata["finished_at"] = _utc_now()
    metadata["outcomes"] = dict(
        sorted(Counter(str(row["outcome"]) for row in case_records).items())
    )
    metadata["fallback_function_instances"] = len(fallback_records)
    _write_json(run_dir / "run.json", metadata)
    write_reports(run_dir, case_records, fallback_records, metadata)
    return run_dir


def _collect_source_case(
    manifest: Manifest,
    source_case: SourceCase,
    tools: ToolPaths,
    artifact_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if source_case.corpus == "llvm":
        return collect_codegen_case(
            CaseSpec(
                case_id=source_case.case_id,
                corpus=source_case.corpus,
                input_id=source_case.input_id,
                source=source_case.source,
                gpu=source_case.gpu,
                opt=source_case.opt,
                timeout=source_case.timeout,
            ),
            tools,
            artifact_dir,
        )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    bitcode = artifact_dir / "input.bc"
    compile_result = run_process(
        build_docker_hip_command(
            manifest,
            source=source_case.source,
            output=bitcode,
            gpu=source_case.gpu,
            opt=source_case.opt,
        ),
        timeout=source_case.timeout,
    )
    write_process_evidence(artifact_dir, "compile", compile_result)
    if compile_result.status != "ok" or not bitcode.is_file():
        compile_status = (
            compile_result.status if compile_result.status != "ok" else "missing_output"
        )
        record: dict[str, Any] = {
            "case_id": source_case.case_id,
            "corpus": source_case.corpus,
            "input_id": source_case.input_id,
            "source": str(source_case.source),
            "source_input_sha256": _sha256_file(source_case.source),
            "gpu": source_case.gpu,
            "opt": source_case.opt,
            "function_count": 0,
            "fallback_functions": [],
            "compile_status": compile_status,
            "compile_returncode": compile_result.returncode,
            "compile_elapsed_ms": compile_result.elapsed_ms,
            "sdag_status": "not_run",
            "gisel_status": "not_run",
            "outcome": "source_compile_failure",
        }
        _write_json(artifact_dir / "record.json", record)
        _write_json(artifact_dir / "fallbacks.json", [])
        return record, []

    record, fallbacks = collect_codegen_case(
        CaseSpec(
            case_id=source_case.case_id,
            corpus=source_case.corpus,
            input_id=source_case.input_id,
            source=bitcode,
            gpu=source_case.gpu,
            opt=source_case.opt,
            timeout=source_case.timeout,
        ),
        tools,
        artifact_dir,
    )
    record["source_input"] = str(source_case.source)
    record["source_input_sha256"] = _sha256_file(source_case.source)
    record["compile_status"] = compile_result.status
    record["compile_returncode"] = compile_result.returncode
    record["compile_elapsed_ms"] = compile_result.elapsed_ms
    _write_json(artifact_dir / "record.json", record)
    return record, fallbacks


def _collect_source_case_safe(
    manifest: Manifest,
    source_case: SourceCase,
    tools: ToolPaths,
    artifact_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        return _collect_source_case(manifest, source_case, tools, artifact_dir)
    except Exception:  # noqa: BLE001 - one bad input must not abort the corpus run
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "infrastructure.stderr.txt").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        record: dict[str, Any] = {
            "case_id": source_case.case_id,
            "corpus": source_case.corpus,
            "input_id": source_case.input_id,
            "source": str(source_case.source),
            "source_input_sha256": (
                _sha256_file(source_case.source)
                if source_case.source.is_file()
                else None
            ),
            "gpu": source_case.gpu,
            "opt": source_case.opt,
            "function_count": 0,
            "fallback_functions": [],
            "sdag_status": "not_run",
            "gisel_status": "not_run",
            "outcome": "infrastructure_error",
        }
        _write_json(artifact_dir / "record.json", record)
        _write_json(artifact_dir / "fallbacks.json", [])
        return record, []


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_checkout_state(source: Path, label: str) -> str:
    try:
        head = run_process(
            ["git", "-C", str(source), "rev-parse", "HEAD"], timeout=10
        )
        status = run_process(
            [
                "git",
                "-C",
                str(source),
                "status",
                "--porcelain",
                "--untracked-files=all",
            ],
            timeout=10,
        )
    except OSError as error:
        raise ValueError(f"cannot verify {label} checkout: {error}") from error
    if head.status != "ok" or not head.stdout.strip():
        raise ValueError(f"cannot verify {label} checkout at {source}")
    if status.status != "ok":
        raise ValueError(f"cannot inspect {label} checkout at {source}")
    if status.stdout.strip():
        raise ValueError(f"{label} checkout is dirty: {source}")
    return head.stdout.strip()


def _validate_revision(actual: str | None, expected: str, label: str) -> None:
    if actual is None:
        raise ValueError(f"cannot verify {label} checkout revision")
    if actual != expected:
        raise ValueError(
            f"{label} checkout mismatch: expected {expected}, got {actual}"
        )


def stable_case_id(corpus: str, input_id: str, gpu: str, opt: str) -> str:
    value = f"{corpus}\0{input_id}\0{gpu}\0{opt}".encode()
    return hashlib.sha256(value).hexdigest()[:16]


def build_docker_hip_command(
    manifest: Manifest, *, source: Path, output: Path, gpu: str, opt: str
) -> list[str]:
    root = manifest.root.resolve()

    def container_path(host_path: Path) -> Path:
        relative = host_path.resolve().relative_to(root)
        return Path("/study") / relative

    inner = build_hip_compile_command(
        clang=container_path(manifest.llvm_build / "bin/clang++"),
        source=container_path(source),
        output=container_path(output),
        gpu=gpu,
        opt=opt,
        include_dirs=(
            container_path(manifest.rocm_examples_source / "Common"),
            container_path(manifest.rocm_examples_source / "External"),
        ),
    )
    return [
        "docker",
        "run",
        "--rm",
        "--network=none",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--env",
        "HOME=/tmp",
        "--volume",
        f"{root}:/study",
        "--workdir",
        "/study",
        manifest.docker_image,
        *inner,
    ]
