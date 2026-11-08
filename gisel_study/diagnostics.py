from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import yaml

_FALLBACK_RE = re.compile(
    r"^warning: Instruction selection used fallback path for (.+?)\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Remark:
    pass_name: str
    name: str
    function: str
    stage: str
    reason: str
    instruction: str
    opcode: str
    llt: str
    register_bank: str
    signature: str


class _RemarkLoader(yaml.SafeLoader):
    pass


def _construct_tagged_mapping(
    loader: _RemarkLoader, node: yaml.MappingNode
) -> dict[str, Any]:
    return loader.construct_mapping(node, deep=True)


_RemarkLoader.add_multi_constructor(
    "!", lambda loader, _suffix, node: _construct_tagged_mapping(loader, node)
)


def parse_fallback_functions(stderr: str) -> list[str]:
    return list(dict.fromkeys(_FALLBACK_RE.findall(stderr)))


def _stage_for(pass_name: str) -> str:
    return {
        "gisel-ir-translator": "ir-translator",
        "gisel-legalize": "legalizer",
        "gisel-regbankselect": "regbank-select",
        "amdgpu-reg-bank-legalize": "regbank-legalize",
        "gisel-select": "instruction-select",
    }.get(pass_name, "unknown")


def _arg_value(args: list[dict[str, Any]], key: str) -> str:
    for arg in args:
        if key in arg:
            return str(arg[key])
    return ""


def _normalize_reason(args: list[dict[str, Any]]) -> str:
    for arg in args:
        value = str(arg.get("String", "")).strip()
        if value and value not in {":", "("} and not value.startswith("(in function:"):
            return value.removesuffix(":").strip()
    return "unknown"


def _instruction_shape(instruction: str) -> tuple[str, str, str]:
    opcode_match = re.search(r"\b(G_[A-Z0-9_]+)\b", instruction)
    opcode = opcode_match.group(1) if opcode_match else "unknown"
    typed_bank_match = re.search(r":([a-z_][\w-]*)\(([^)]+)\)", instruction)
    if typed_bank_match:
        bank = typed_bank_match.group(1)
        return opcode, typed_bank_match.group(2), "unassigned" if bank == "_" else bank
    bank_match = re.search(r":([a-z][\w-]*)\b", instruction)
    return opcode, "unknown", bank_match.group(1) if bank_match else "unknown"


def parse_remarks_yaml(yaml_text: str) -> list[Remark]:
    remarks: list[Remark] = []
    for document in yaml.load_all(yaml_text, Loader=_RemarkLoader):
        if not isinstance(document, dict):
            continue
        pass_name = str(document.get("Pass", "unknown"))
        args = document.get("Args", [])
        if not isinstance(args, list):
            args = []
        instruction = _arg_value(args, "Inst")
        reason = _normalize_reason(args)
        opcode, llt, bank = _instruction_shape(instruction)
        signature = f"{pass_name}|{reason}|{opcode}|{llt}|{bank}"
        remarks.append(
            Remark(
                pass_name=pass_name,
                name=str(document.get("Name", "")),
                function=str(document.get("Function", "")),
                stage=_stage_for(pass_name),
                reason=reason,
                instruction=instruction,
                opcode=opcode,
                llt=llt,
                register_bank=bank,
                signature=signature,
            )
        )
    return remarks
