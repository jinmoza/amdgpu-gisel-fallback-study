from pathlib import Path


def build_hip_compile_command(
    *,
    clang: Path,
    source: Path,
    output: Path,
    gpu: str,
    opt: str,
    include_dirs: tuple[Path, ...] = (),
) -> list[str]:
    return [
        str(clang),
        "--target=x86_64-unknown-linux-gnu",
        "--offload-device-only",
        "-x",
        "hip",
        f"--offload-arch={gpu}",
        "--rocm-path=/opt/rocm",
        *(f"-I{include_dir}" for include_dir in include_dirs),
        f"-{opt}",
        "-emit-llvm",
        "-c",
        str(source),
        "-o",
        str(output),
    ]


def build_sdag_command(*, llc: Path, source: Path, gpu: str, opt: str) -> list[str]:
    return _base_llc_command(llc, source, gpu, opt) + ["-global-isel=0", str(source)]


def build_gisel_command(
    *, llc: Path, source: Path, remarks: Path, gpu: str, opt: str
) -> list[str]:
    return _base_llc_command(llc, source, gpu, opt) + [
        "-global-isel=1",
        "-global-isel-abort=2",
        "-pass-remarks-missed=gisel.*",
        "-pass-remarks-format=yaml",
        f"-pass-remarks-output={remarks}",
        str(source),
    ]


def _base_llc_command(llc: Path, source: Path, gpu: str, opt: str) -> list[str]:
    return [
        str(llc),
        "-mtriple=amdgcn-amd-amdhsa",
        f"-mcpu={gpu}",
        f"-{opt}",
        "-verify-machineinstrs",
        "-filetype=null",
    ]
