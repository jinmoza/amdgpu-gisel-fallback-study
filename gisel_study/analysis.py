from collections import Counter, defaultdict
from typing import Any

from .diagnostics import Remark


def build_fallback_records(
    case: dict[str, Any], remarks: list[Remark]
) -> list[dict[str, Any]]:
    by_function: dict[str, list[Remark]] = defaultdict(list)
    for remark in remarks:
        by_function[remark.function].append(remark)
    records: list[dict[str, Any]] = []
    for function in case.get("fallback_functions", []):
        matching = by_function.get(function, [])
        remark = next(
            (item for item in matching if item.name.startswith("GISelFailure")),
            matching[0] if matching else None,
        )
        record = {
            key: case.get(key)
            for key in ("case_id", "corpus", "input_id", "gpu", "opt", "outcome")
        }
        record.update(
            {
                "function": function,
                "pass": remark.pass_name if remark else "unknown",
                "stage": remark.stage if remark else "unknown",
                "reason": remark.reason if remark else "unknown",
                "instruction": remark.instruction if remark else "",
                "opcode": remark.opcode if remark else "unknown",
                "llt": remark.llt if remark else "unknown",
                "register_bank": remark.register_bank if remark else "unknown",
                "signature": remark.signature if remark else "unknown",
                "remark_count": len(matching),
            }
        )
        records.append(record)
    return records


def summarize_cases(
    cases: list[dict[str, Any]], fallbacks: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        grouped[(case["corpus"], case["gpu"], case["opt"])].append(case)

    signatures: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for fallback in fallbacks:
        key = (fallback["corpus"], fallback["gpu"], fallback["opt"])
        signatures[key].add(fallback["signature"])

    rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        valid = [case for case in group if str(case["outcome"]).startswith("gisel_")]
        fallback_cases = [case for case in valid if case.get("fallback_functions")]
        valid_functions = sum(int(case.get("function_count", 0)) for case in valid)
        fallback_functions = sum(
            len(case.get("fallback_functions", [])) for case in fallback_cases
        )
        outcome_counts = Counter(case["outcome"] for case in group)
        row: dict[str, Any] = {
            "corpus": key[0],
            "gpu": key[1],
            "opt": key[2],
            "total_cases": len(group),
            "valid_modules": len(valid),
            "valid_functions": valid_functions,
            "fallback_modules": len(fallback_cases),
            "fallback_functions": fallback_functions,
            "module_fallback_rate": (
                len(fallback_cases) / len(valid) if valid else 0.0
            ),
            "function_fallback_rate": (
                fallback_functions / valid_functions if valid_functions else 0.0
            ),
            "unique_signatures": len(signatures[key]),
        }
        for outcome, count in sorted(outcome_counts.items()):
            row[f"outcome_{outcome}"] = count
        rows.append(row)
    return rows
