# Third-party notices

The curated experiment results contain representative LLVM IR inputs and reduced derivatives selected from two pinned source corpora.

## LLVM

Inputs originating from `llvm/test/CodeGen/AMDGPU` are from LLVM commit `4c22a9f755be90fa8ce385f589761033609fe66f`.

LLVM is distributed under the Apache License v2.0 with LLVM Exceptions. The complete license text is included in [`LICENSE.TXT`](LICENSE.TXT).

Upstream project: <https://github.com/llvm/llvm-project>

## ROCm Examples

Some LLVM IR inputs were generated from ROCm Examples at commit `9f678a8b432d4bb95090c6f32e3d5f18b05b7afe` using the pinned ROCm SDK image recorded in the experiment metadata.

ROCm Examples is distributed under the MIT License. Its license text is included in [`LICENSES/ROCm-Examples-MIT.txt`](LICENSES/ROCm-Examples-MIT.txt).

Upstream project: <https://github.com/ROCm/rocm-examples>

The `input_id`, source commit, input SHA-256, commands, and normalized failure signature retained in the public result set provide provenance for each representative artifact.
