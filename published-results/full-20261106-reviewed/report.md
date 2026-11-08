# AMDGPU GlobalISel 显式回退报告

- Run ID：`full-20261106-reviewed`
- LLVM：`4c22a9f755be90fa8ce385f589761033609fe66f`
- ROCm Examples：`9f678a8b432d4bb95090c6f32e3d5f18b05b7afe`
- 案例数：11322
- SDAG 有效、已尝试 GlobalISel 的案例：7041
- 显式回退案例：885（12.57%）
- 显式回退函数实例：6111
- 归一化根因簇：107

## 结果分类

| 结果 | 案例数 |
|---|---:|
| `gisel_crash` | 61 |
| `gisel_fallback_sdag_success` | 885 |
| `gisel_success` | 6095 |
| `sdag_invalid` | 4191 |
| `source_compile_failure` | 90 |

## 汇总

| 语料 | GPU | 优化 | 案例 | 已尝试 GISel 模块 | 模块内函数 | 回退模块 | 回退函数 | 模块回退率 | 函数回退率 | 根因簇 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hip | gfx1030 | O0 | 92 | 77 | 1025 | 77 | 263 | 100.00% | 25.66% | 1 |
| hip | gfx1030 | O2 | 92 | 77 | 100 | 13 | 16 | 16.88% | 16.00% | 1 |
| hip | gfx1100 | O0 | 92 | 77 | 1025 | 77 | 263 | 100.00% | 25.66% | 1 |
| hip | gfx1100 | O2 | 92 | 77 | 100 | 13 | 16 | 16.88% | 16.00% | 1 |
| hip | gfx900 | O0 | 92 | 77 | 1018 | 77 | 265 | 100.00% | 26.03% | 2 |
| hip | gfx900 | O2 | 92 | 77 | 100 | 13 | 15 | 16.88% | 15.00% | 1 |
| llvm | gfx1030 | O2 | 3590 | 2199 | 44749 | 200 | 1697 | 9.10% | 3.79% | 99 |
| llvm | gfx1100 | O2 | 3590 | 2192 | 44688 | 203 | 1676 | 9.26% | 3.75% | 104 |
| llvm | gfx900 | O2 | 3590 | 2188 | 44498 | 212 | 1900 | 9.69% | 4.27% | 98 |

## 根因簇

| 次数 | 阶段 | 原因 | Opcode | LLT | 受影响配置 | 代表输入 |
|---:|---|---|---|---|---|---|
| 2811 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_INTRINSIC_W_SIDE_EFFECTS | i32 | gfx1030/O0, gfx1030/O2, gfx1100/O0, gfx1100/O2 | `lcssa-optnone.ll` |
| 1617 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_INTRINSIC_W_SIDE_EFFECTS | i64 | gfx900/O0, gfx900/O2 | `HIP-Doc/Programming-Guide/HIP-C++-Language-Extensions/extern_shared_memory/main.hip` |
| 560 | ir-translator | unable to translate instruction | unknown | unknown | gfx1030/O2, gfx1100/O2, gfx900/O2 | `float-to-arbitrary-fp.ll` |
| 221 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_PTRMASK | p0 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `GlobalISel/irtranslator-ptrmask.ll` |
| 48 | legalizer | unable to legalize instruction | G_GET_FPMODE | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `llvm.get.fpmode.ll` |
| 39 | legalizer | unable to legalize instruction | G_FDIV | bf16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fdiv.bf16.ll` |
| 30 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 30 | legalizer | unable to legalize instruction | G_INTRINSIC | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `llvm.amdgcn.cluster.workgroup.max.id.ll` |
| 25 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_TRUNC | i16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `packed-op-sel.ll` |
| 24 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_ADD | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-unsupported.ll` |
| 24 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `attributor-flatscratchinit-globalisel.ll` |
| 24 | legalizer | unable to legalize instruction | G_FNEARBYINT | f32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `combine-ftrunc.ll` |
| 18 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_BUILD_VECTOR | <7 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 18 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <4 x i32> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 18 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <9 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `tuple-allocation-failure.ll` |
| 15 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_BUILD_VECTOR | <7 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <10 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.640bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <10 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.640bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <11 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.704bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <11 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.704bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <12 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.768bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <12 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.768bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <13 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.832bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <13 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.832bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <14 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.896bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <14 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.896bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <15 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.960bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <15 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.960bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_IMPLICIT_DEF | <9 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.576bit.ll` |
| 15 | legalizer | unable to legalize instruction | G_STORE | <3 x i15> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgpu-codegenprepare-idiv.ll` |
| 15 | legalizer | unable to legalize instruction | G_ZEXT | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `atomic_optimizations_global_pointer.ll` |
| 12 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_IMPLICIT_DEF | <7 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 12 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_IMPLICIT_DEF | <7 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 12 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_INTRINSIC_W_SIDE_EFFECTS | unknown | gfx1030/O2, gfx1100/O2, gfx900/O2 | `llvm.amdgcn.s.dcache.inv.ll` |
| 12 | legalizer | unable to legalize instruction | G_ATOMICRMW_XCHG | p0 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `flat_atomics_i64.ll` |
| 12 | legalizer | unable to legalize instruction | G_CLMUL | i64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `clmul.ll` |
| 12 | legalizer | unable to legalize instruction | G_CTLZ_ZERO_POISON | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgpu-simplify-libcall-pow.ll` |
| 11 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_SEXTLOAD | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 11 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ZEXTLOAD | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 10 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_AMDGPU_BUFFER_ATOMIC_SUB_CLAMP_U32 | i32 | gfx1030/O2, gfx1100/O2 | `buffer-fat-pointer-atomicrmw-usub_sat.ll` |
| 9 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <4 x f16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 9 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | i64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 9 | legalizer | unable to legalize instruction | G_FCOS | bf16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `llvm.cos.bf16.ll` |
| 9 | legalizer | unable to legalize instruction | G_FNEARBYINT | f64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fnearbyint.ll` |
| 9 | legalizer | unable to legalize instruction | G_FSIN | bf16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `llvm.sin.bf16.ll` |
| 8 | legalizer | unable to legalize instruction | G_FREEZE | <9 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `vector-alloca-limits.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <2 x f16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <2 x i32> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <3 x i32> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <4 x bf16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | p1 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | p2 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | p3 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 6 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_INTRINSIC | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `cttz-elts.ll` |
| 6 | legalizer | unable to legalize instruction | G_CLMUL | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `clmul.ll` |
| 6 | legalizer | unable to legalize instruction | G_FFREXP | bf16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `frexp-inf-nan-combine.ll` |
| 6 | legalizer | unable to legalize instruction | G_UBSANTRAP | unknown | gfx1030/O2, gfx1100/O2, gfx900/O2 | `hsa-metadata-queue-ptr-v4.ll` |
| 4 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_INTRINSIC | f16 | gfx1030/O2, gfx900/O2 | `fneg-combines.legal.f16.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: missing fast rule ('Div' or 'Uni') for | G_SELECT | p8 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `lower-buffer-fat-pointers-control-flow.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_AND | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_MAX | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_MIN | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_OR | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_SUB | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_UMAX | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_UMIN | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_XCHG | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_ATOMICRMW_XOR | i32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-atomic.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_BUILD_VECTOR | <7 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_BUILD_VECTOR | <7 x i64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgcn.bitcast.448bit.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <2 x bf16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | <2 x i16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | f32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | f64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `gds-load-store.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | i16 | gfx1100/O2 | `gds-load-store.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | <2 x f16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | <2 x f32> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | <2 x f64> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | <2 x i16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | <2 x i32> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | f32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | f64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | i64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `store-to-constant.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_TRUNC | <4 x i1> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `cttz-elts.ll` |
| 3 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_TRUNC | i8 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `cttz-elts.ll` |
| 3 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_INTRINSIC | f32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `copysign-to-disjoint-or-combine.ll` |
| 3 | regbank-legalize | No AMDGPU RegBankLegalize rules defined for opcode | G_STACKRESTORE | p5 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `promote-alloca-unhandled-intrinsic.ll` |
| 3 | legalizer | unable to legalize instruction | G_FLOG | bf16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `amdgpu-codegenprepare-log.ll` |
| 3 | legalizer | unable to legalize instruction | G_FNEARBYINT | f16 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fnearbyint.ll` |
| 3 | legalizer | unable to legalize instruction | G_FPTRUNCSTORE | s32 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `slp-int-to-fp.ll` |
| 3 | legalizer | unable to legalize instruction | G_INSERT_SUBVECTOR | <16 x i16> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `undef-build-vector.ll` |
| 3 | legalizer | unable to legalize instruction | G_INSERT_VECTOR_ELT | <2 x i128> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `lower-buffer-fat-pointers-pointer-ops.ll` |
| 3 | legalizer | unable to legalize instruction | G_LOAD | <7 x i9> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `promote-alloca-non-byte-sizes.ll` |
| 3 | legalizer | unable to legalize instruction | G_STORE | <16 x i63> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `splitkit-getsubrangeformask-phi-extend.ll` |
| 3 | legalizer | unable to legalize instruction | G_STORE | <2 x i65> | gfx1030/O2, gfx1100/O2, gfx900/O2 | `GlobalISel/irtranslator-function-args.v2i65.ll` |
| 3 | legalizer | unable to legalize instruction | G_UREM | i127 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fshl-illegal-types.ll` |
| 3 | legalizer | unable to legalize instruction | G_UREM | i65 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fshl-illegal-types.ll` |
| 3 | legalizer | unable to legalize instruction | G_UREM | i66 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fshl-illegal-types.ll` |
| 3 | legalizer | unable to legalize instruction | G_UREM | i67 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fshl-illegal-types.ll` |
| 3 | legalizer | unable to legalize instruction | G_UREM | i68 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `fshl-illegal-types.ll` |
| 3 | instruction-select | instruction is not legal | G_ADD | i64 | gfx1030/O2, gfx1100/O2, gfx900/O2 | `GlobalISel/irtranslator-sat.ll` |
| 2 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | i16 | gfx1100/O2 | `store-to-constant.ll` |
| 2 | instruction-select | cannot select | G_INTRINSIC_CONVERGENT | i32 | gfx900/O0 | `HIP-Doc/Programming-Guide/Using-HIP-Runtime-API/Memory-Management/Device-Memory/kernel_memory_allocation/main.hip` |
| 1 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | bf16 | gfx1100/O2 | `gds-load-store.ll` |
| 1 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_LOAD | f16 | gfx1100/O2 | `gds-load-store.ll` |
| 1 | regbank-legalize | AMDGPU RegBankLegalize: none of the rules defined with 'Any' for MI's opcode matched MI | G_STORE | f16 | gfx1100/O2 | `store-to-constant.ll` |
| 1 | instruction-select | cannot select | G_TRUNC | i16 | gfx1100/O2 | `ctpop16.ll` |

## 解释边界

本报告不检测静默错误生成，也不验证生成代码在真实 GPU 上的运行结果。它只统计 LLVM 明确发出的 GlobalISel fallback 诊断；因此零回退不等于后端完整正确。

HIP device bitcode 可能同时包含样例 kernel 和 ROCm 设备库函数。模块触发回退并不表示样例自身的 kernel 必然回退；应结合 fallbacks.jsonl 中的函数名区分二者。

根因聚类为每个 fallback 函数选取首个 `GISelFailure` remark，避免同一函数被重复计数；每个 case 的原始 remarks 仍完整保留。

函数分母统计这些案例中定义的函数，包括随后 GlobalISel 崩溃的模块；它不是实际执行到某个 GlobalISel 阶段的函数数。
