from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .collect import collect_experiment
from .manifest import load_manifest
from .report import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gisel-study", description="Measure AMDGPU GlobalISel fallbacks"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="collect a new experiment run")
    collect.add_argument("--manifest", required=True)
    collect.add_argument("--run-id")
    collect.add_argument("--corpus", choices=("all", "llvm", "hip"), default="all")
    collect.add_argument("--limit", type=int)

    for command in ("analyze", "report"):
        subparser = subparsers.add_parser(command, help=f"{command} an existing run")
        subparser.add_argument("--run", required=True)

    reduce_parser = subparsers.add_parser(
        "reduce", help="reduce one representative per root-cause signature"
    )
    reduce_parser.add_argument("--run", required=True)
    reduce_parser.add_argument("--manifest", default="experiment.yaml")
    reduce_parser.add_argument("--timeout", type=int, default=900)

    publish_parser = subparsers.add_parser(
        "publish-results", help="export a sanitized, curated result set"
    )
    publish_parser.add_argument("--run", required=True)
    publish_parser.add_argument("--output", required=True)
    publish_parser.add_argument("--workspace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "collect":
        manifest = load_manifest(Path(args.manifest))
        run_id = args.run_id or _default_run_id(manifest.llvm_sha)
        corpora = {"llvm", "hip"} if args.corpus == "all" else {args.corpus}
        run_dir = collect_experiment(
            manifest, run_id=run_id, corpora=corpora, limit=args.limit
        )
        print(run_dir)
        return 0
    if args.command in {"analyze", "report"}:
        run_dir = Path(args.run).resolve()
        cases, fallbacks, metadata = _load_run(run_dir)
        write_reports(run_dir, cases, fallbacks, metadata)
        print(run_dir / "report.md")
        return 0
    if args.command == "reduce":
        from .reduce import reduce_run

        reduce_run(
            Path(args.run).resolve(),
            load_manifest(Path(args.manifest)),
            timeout=args.timeout,
        )
        return 0
    if args.command == "publish-results":
        from .publish import export_public_results

        output_dir = export_public_results(
            Path(args.run),
            Path(args.output),
            workspace=Path(args.workspace),
        )
        print(output_dir)
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def _load_run(
    run_dir: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    cases = _read_jsonl(run_dir / "cases.jsonl")
    fallbacks = _read_jsonl(run_dir / "fallbacks.jsonl")
    metadata = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    return cases, fallbacks, metadata


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _default_run_id(llvm_sha: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{llvm_sha[:12]}"
