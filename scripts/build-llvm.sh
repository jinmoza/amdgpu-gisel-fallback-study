#!/usr/bin/env bash
set -euo pipefail

study_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
llvm_source="${study_root}/third_party/llvm-project"
llvm_build="${study_root}/build/llvm"
expected_llvm_sha="4c22a9f755be90fa8ce385f589761033609fe66f"
expected_examples_sha="9f678a8b432d4bb95090c6f32e3d5f18b05b7afe"
sdk_image="rocm/dev-ubuntu-24.04:7.2.4@sha256:bdc8e61026cbb844ede93d44d2c50055f51ebb2041906b60182bf3bee3139054"

actual_llvm_sha="$(git -C "${llvm_source}" rev-parse HEAD)"
actual_examples_sha="$(git -C "${study_root}/third_party/rocm-examples" rev-parse HEAD)"
if [[ "${actual_llvm_sha}" != "${expected_llvm_sha}" ]]; then
  echo "LLVM checkout mismatch: expected ${expected_llvm_sha}, got ${actual_llvm_sha}" >&2
  exit 1
fi
if [[ "${actual_examples_sha}" != "${expected_examples_sha}" ]]; then
  echo "ROCm Examples checkout mismatch: expected ${expected_examples_sha}, got ${actual_examples_sha}" >&2
  exit 1
fi
if [[ -n "$(git -C "${llvm_source}" status --porcelain --untracked-files=all)" ]]; then
  echo "LLVM checkout is dirty; refusing to record a pinned build" >&2
  exit 1
fi
if [[ -n "$(git -C "${study_root}/third_party/rocm-examples" status --porcelain --untracked-files=all)" ]]; then
  echo "ROCm Examples checkout is dirty; refusing to use an unpinned corpus" >&2
  exit 1
fi

docker image inspect "${sdk_image}" >/dev/null

cmake -S "${llvm_source}/llvm" -B "${llvm_build}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_ASSERTIONS=ON \
  -DLLVM_ENABLE_PROJECTS=clang \
  -DCLANG_ENABLE_CIR=OFF \
  -DCLANG_ENABLE_STATIC_ANALYZER=OFF \
  -DLLVM_TARGETS_TO_BUILD=AMDGPU \
  -DLLVM_INCLUDE_TESTS=ON \
  -DLLVM_INCLUDE_BENCHMARKS=OFF \
  -DLLVM_INCLUDE_EXAMPLES=OFF

cmake --build "${llvm_build}" \
  --parallel "${LLVM_BUILD_JOBS:-$(nproc)}" \
  --target clang llc opt llvm-as llvm-dis llvm-nm llvm-reduce

provenance="${llvm_build}/gisel-study-provenance.json"
llvm_source_real="$(realpath "${llvm_source}")"
llc_sha="$(sha256sum "${llvm_build}/bin/llc" | cut -d' ' -f1)"
llvm_as_sha="$(sha256sum "${llvm_build}/bin/llvm-as" | cut -d' ' -f1)"
llvm_nm_sha="$(sha256sum "${llvm_build}/bin/llvm-nm" | cut -d' ' -f1)"
clang_sha="$(sha256sum "${llvm_build}/bin/clang++" | cut -d' ' -f1)"
llvm_reduce_sha="$(sha256sum "${llvm_build}/bin/llvm-reduce" | cut -d' ' -f1)"
printf '{\n  "schema": 1,\n  "llvm_sha": "%s",\n  "llvm_source": "%s",\n  "llvm_enable_assertions": true,\n  "tools": {\n    "clang++": "%s",\n    "llc": "%s",\n    "llvm-as": "%s",\n    "llvm-nm": "%s",\n    "llvm-reduce": "%s"\n  }\n}\n' \
  "${actual_llvm_sha}" "${llvm_source_real}" "${clang_sha}" "${llc_sha}" \
  "${llvm_as_sha}" "${llvm_nm_sha}" "${llvm_reduce_sha}" >"${provenance}"
