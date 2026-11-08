from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .analysis import build_fallback_records
from .commands import build_gisel_command, build_sdag_command
from .diagnostics import parse_fallback_functions, parse_remarks_yaml


@dataclass(frozen=True)
class ProcessResult:
    command: tuple[str, ...]
    status: str
    returncode: int | None
    stdout: str
    stderr: str
    elapsed_ms: int


@dataclass(frozen=True)
class ToolPaths:
    llc: Path
    llvm_as: Path
    llvm_nm: Path


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    corpus: str
    input_id: str
    source: Path
    gpu: str
    opt: str
    timeout: float


def collect_codegen_case(
    case: CaseSpec, tools: ToolPaths, artifact_dir: Path
) -> tuple[dict[str, object], list[dict[str, object]]]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    count_source = case.source
    assemble_result: ProcessResult | None = None
    if case.source.suffix == ".ll":
        count_source = artifact_dir / "input.bc"
        assemble_result = run_process(
            [
                str(tools.llvm_as),
                "-disable-verify",
                str(case.source),
                "-o",
                str(count_source),
            ],
            timeout=case.timeout,
        )
        write_process_evidence(artifact_dir, "assemble", assemble_result)

    function_count = 0
    nm_result: ProcessResult | None = None
    if count_source.exists():
        nm_result = run_process(
            [
                str(tools.llvm_nm),
                "--defined-only",
                "--format=posix",
                str(count_source),
            ],
            timeout=case.timeout,
        )
        write_process_evidence(artifact_dir, "nm", nm_result)
        if nm_result.status == "ok":
            function_count = len(parse_defined_functions(nm_result.stdout))

    sdag_result = run_process(
        build_sdag_command(
            llc=tools.llc,
            source=case.source,
            gpu=case.gpu,
            opt=case.opt,
        ),
        timeout=case.timeout,
    )
    write_process_evidence(artifact_dir, "sdag", sdag_result)

    remarks_path = artifact_dir / "remarks.yaml"
    gisel_result: ProcessResult | None = None
    fallback_functions: list[str] = []
    remarks = []
    remarks_parse_status = "not_generated"
    remarks_parse_error = ""
    if sdag_result.status == "ok":
        gisel_result = run_process(
            build_gisel_command(
                llc=tools.llc,
                source=case.source,
                remarks=remarks_path,
                gpu=case.gpu,
                opt=case.opt,
            ),
            timeout=case.timeout,
        )
        write_process_evidence(artifact_dir, "gisel", gisel_result)
        fallback_functions = parse_fallback_functions(gisel_result.stderr)
        if remarks_path.exists():
            try:
                remarks = parse_remarks_yaml(remarks_path.read_text(encoding="utf-8"))
                remarks_parse_status = "ok"
            except Exception as error:  # noqa: BLE001 - diagnostics must not mask codegen
                remarks_parse_status = "failed"
                remarks_parse_error = f"{type(error).__name__}: {error}"

    record: dict[str, object] = {
        "case_id": case.case_id,
        "corpus": case.corpus,
        "input_id": case.input_id,
        "source": str(case.source),
        "input_sha256": hashlib.sha256(case.source.read_bytes()).hexdigest(),
        "gpu": case.gpu,
        "opt": case.opt,
        "function_count": function_count,
        "fallback_functions": fallback_functions,
        "sdag_status": sdag_result.status,
        "sdag_returncode": sdag_result.returncode,
        "sdag_elapsed_ms": sdag_result.elapsed_ms,
        "gisel_status": gisel_result.status if gisel_result else "not_run",
        "gisel_returncode": gisel_result.returncode if gisel_result else None,
        "gisel_elapsed_ms": gisel_result.elapsed_ms if gisel_result else 0,
        "assemble_status": assemble_result.status if assemble_result else "not_needed",
        "nm_status": nm_result.status if nm_result else "not_run",
        "remarks_parse_status": remarks_parse_status,
        "remarks_parse_error": remarks_parse_error,
    }
    record["outcome"] = classify_codegen(
        sdag_status=sdag_result.status,
        gisel_status=gisel_result.status if gisel_result else "not_run",
        fallback_count=len(fallback_functions),
    )
    fallback_records = build_fallback_records(record, remarks)
    (artifact_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (artifact_dir / "fallbacks.json").write_text(
        json.dumps(fallback_records, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record, fallback_records


def write_process_evidence(
    artifact_dir: Path, prefix: str, result: ProcessResult
) -> None:
    (artifact_dir / f"{prefix}.command.json").write_text(
        json.dumps(list(result.command), indent=2) + "\n", encoding="utf-8"
    )
    (artifact_dir / f"{prefix}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (artifact_dir / f"{prefix}.stderr.txt").write_text(result.stderr, encoding="utf-8")


def run_process(
    command: list[str],
    *,
    timeout: float,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> ProcessResult:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=dict(env) if env is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        if process.returncode == 0:
            status = "ok"
        elif process.returncode is not None and process.returncode < 0:
            status = "crash"
        else:
            status = "failed"
        returncode = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        status = "timeout"
        returncode = None
    return ProcessResult(
        command=tuple(command),
        status=status,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        elapsed_ms=int((time.monotonic() - started) * 1000),
    )


def parse_defined_functions(nm_output: str) -> list[str]:
    functions: list[str] = []
    for line in nm_output.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] in {"T", "t", "W", "w"}:
            functions.append(fields[0])
    return list(dict.fromkeys(functions))


def classify_codegen(
    *, sdag_status: str, gisel_status: str, fallback_count: int
) -> str:
    if sdag_status != "ok":
        return "sdag_invalid"
    if fallback_count:
        if gisel_status == "ok":
            return "gisel_fallback_sdag_success"
        return "gisel_fallback_then_failure"
    if gisel_status == "ok":
        return "gisel_success"
    if gisel_status in {"timeout", "crash"}:
        return f"gisel_{gisel_status}"
    return "gisel_hard_failure_without_fallback"
