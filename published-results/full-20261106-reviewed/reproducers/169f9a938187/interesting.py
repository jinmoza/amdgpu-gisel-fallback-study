#!/usr/bin/env python3
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, '<WORKSPACE>')
from gisel_study.commands import build_gisel_command, build_sdag_command
from gisel_study.diagnostics import parse_fallback_functions, parse_remarks_yaml

candidate = pathlib.Path(sys.argv[-1]).resolve()
llc = pathlib.Path('<WORKSPACE>/build/llvm/bin/llc')
gpu = 'gfx1030'
opt = 'O2'
expected = "amdgpu-reg-bank-legalize|AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI|G_LOAD|<4 x f16>|vgpr"

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
