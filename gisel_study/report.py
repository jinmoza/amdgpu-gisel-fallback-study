import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .analysis import summarize_cases


def render_markdown_report(
    cases: list[dict[str, Any]],
    fallbacks: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> str:
    summary = summarize_cases(cases, fallbacks)
    valid_cases = [
        case for case in cases if str(case.get("outcome", "")).startswith("gisel_")
    ]
    fallback_cases = [case for case in valid_cases if case.get("fallback_functions")]
    fallback_rate = len(fallback_cases) / len(valid_cases) if valid_cases else 0.0
    root_causes = {str(item.get("signature", "unknown")) for item in fallbacks}
    lines = [
        "# AMDGPU GlobalISel 显式回退报告",
        "",
        f"- Run ID：`{metadata.get('run_id', 'unknown')}`",
        f"- LLVM：`{metadata.get('llvm_sha', 'unknown')}`",
        f"- ROCm Examples：`{metadata.get('rocm_examples_sha', 'unknown')}`",
        f"- 案例数：{len(cases)}",
        f"- SDAG 有效、已尝试 GlobalISel 的案例：{len(valid_cases)}",
        f"- 显式回退案例：{len(fallback_cases)}（{fallback_rate:.2%}）",
        f"- 显式回退函数实例：{len(fallbacks)}",
        f"- 归一化根因簇：{len(root_causes)}",
        "",
        "## 结果分类",
        "",
        "| 结果 | 案例数 |",
        "|---|---:|",
    ]
    outcomes = Counter(str(case.get("outcome", "unknown")) for case in cases)
    for outcome, count in sorted(outcomes.items()):
        lines.append(f"| `{outcome}` | {count} |")

    lines.extend(
        [
            "",
            "## 汇总",
            "",
            "| 语料 | GPU | 优化 | 案例 | 已尝试 GISel 模块 | 模块内函数 | 回退模块 | 回退函数 | 模块回退率 | 函数回退率 | 根因簇 |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summary:
        lines.append(
            "| {corpus} | {gpu} | {opt} | {total_cases} | {valid_modules} | "
            "{valid_functions} | {fallback_modules} | {fallback_functions} | "
            "{module_rate:.2%} | {function_rate:.2%} | {unique_signatures} |".format(
                **row,
                module_rate=row["module_fallback_rate"],
                function_rate=row["function_fallback_rate"],
            )
        )

    lines.extend(["", "## 根因簇", ""])
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fallback in fallbacks:
        clusters[str(fallback.get("signature", "unknown"))].append(fallback)
    if not clusters:
        lines.append("本次运行没有发现显式 fallback。")
    else:
        lines.extend(
            [
                "| 次数 | 阶段 | 原因 | Opcode | LLT | 受影响配置 | 代表输入 |",
                "|---:|---|---|---|---|---|---|",
            ]
        )
        ordered = sorted(
            clusters.values(), key=lambda group: (-len(group), group[0]["signature"])
        )
        for group in ordered:
            first = group[0]
            configs = sorted({f"{item['gpu']}/{item['opt']}" for item in group})
            lines.append(
                "| {count} | {stage} | {reason} | {opcode} | {llt} | {configs} | `{input_id}` |".format(
                    count=len(group),
                    stage=_md(first.get("stage", "unknown")),
                    reason=_md(first.get("reason", "unknown")),
                    opcode=_md(first.get("opcode", "unknown")),
                    llt=_md(first.get("llt", "unknown")),
                    configs=_md(", ".join(configs)),
                    input_id=first.get("input_id", "unknown"),
                )
            )

    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            (
                "本报告不检测静默错误生成，也不验证生成代码在真实 GPU 上的运行结果。"
                "它只统计 LLVM 明确发出的 GlobalISel fallback 诊断；因此零回退不等于后端完整正确。"
            ),
            "",
            (
                "HIP device bitcode 可能同时包含样例 kernel 和 ROCm 设备库函数。"
                "模块触发回退并不表示样例自身的 kernel 必然回退；应结合 fallbacks.jsonl "
                "中的函数名区分二者。"
            ),
            "",
            (
                "根因聚类为每个 fallback 函数选取首个 `GISelFailure` remark，避免同一函数"
                "被重复计数；每个 case 的原始 remarks 仍完整保留。"
            ),
            "",
            (
                "函数分母统计这些案例中定义的函数，包括随后 GlobalISel 崩溃的模块；"
                "它不是实际执行到某个 GlobalISel 阶段的函数数。"
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(
    run_dir: Path,
    cases: list[dict[str, Any]],
    fallbacks: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.md").write_text(
        render_markdown_report(cases, fallbacks, metadata), encoding="utf-8"
    )
    _write_csv(run_dir / "summary.csv", summarize_cases(cases, fallbacks))
    _write_jsonl(run_dir / "cases.jsonl", cases)
    _write_jsonl(run_dir / "fallbacks.jsonl", fallbacks)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    buffer = io.StringIO()
    if fieldnames:
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
