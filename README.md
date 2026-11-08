# AMDGPU GlobalISel fallback study

这个实验统计 AMDGPU 后端中显式触发 SelectionDAG fallback 的 GlobalISel 编译实例，并保留可复查的原始证据。它不要求 AMD GPU：只运行前端和后端编译，不执行生成的程序。

完整的研究背景、SelectionDAG 与 GlobalISel 的关系以及实验结果解读，见博客文章：[从宽操作数修复到 AMDGPU GlobalISel fallback：双指令选择流水线研究与实测](https://jinmoza.github.io/posts/llvm-amdgpu-globalisel-fallback-study/)。

实验固定以下输入：

- LLVM `4c22a9f755be90fa8ce385f589761033609fe66f`
- ROCm Examples `rocm-7.2.4` 对应提交 `9f678a8b432d4bb95090c6f32e3d5f18b05b7afe`
- ROCm SDK 镜像 `rocm/dev-ubuntu-24.04:7.2.4@sha256:bdc8e61026cbb844ede93d44d2c50055f51ebb2041906b60182bf3bee3139054`
- GPU：`gfx900`、`gfx1030`、`gfx1100`
- HIP 优化级别：`-O0`、`-O2`

## 准备环境

需要 Git、Python 3.10+、CMake、Ninja、C/C++ 编译器和 Docker。首次准备仓库与镜像：

```bash
mkdir -p third_party
git clone --filter=blob:none https://github.com/llvm/llvm-project.git third_party/llvm-project
git -C third_party/llvm-project checkout --detach 4c22a9f755be90fa8ce385f589761033609fe66f
git clone --filter=blob:none --branch rocm-7.2.4 https://github.com/ROCm/rocm-examples.git third_party/rocm-examples
git -C third_party/rocm-examples checkout --detach 9f678a8b432d4bb95090c6f32e3d5f18b05b7afe
docker pull rocm/dev-ubuntu-24.04:7.2.4@sha256:bdc8e61026cbb844ede93d44d2c50055f51ebb2041906b60182bf3bee3139054
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
./scripts/build-llvm.sh
```

`build-llvm.sh` 会先核对两个源码提交、工作区清洁状态以及 SDK 镜像，再构建仅含 AMDGPU 后端且启用 assertions 的 LLVM/Clang 工具。构建结束后会记录各工具的 SHA-256；采集和约简都会复核这份 provenance，避免把别的编译器误报成固定提交的结果。

## 运行

先做小规模端到端验证：

```bash
gisel-study collect --manifest experiment.yaml --run-id smoke-llvm --corpus llvm --limit 12
gisel-study collect --manifest experiment.yaml --run-id smoke-hip --corpus hip --limit 12
```

运行完整矩阵：

```bash
gisel-study collect --manifest experiment.yaml --corpus all
```

在当前固定提交上，工具会发现 3,590 个 LLVM AMDGPU `.ll` 输入和 92 个 HIP 输入；乘以 GPU 与优化级别后，完整矩阵共 11,322 个 case。

每个 case 先用 SelectionDAG 编译，排除本身就无法由当前后端处理的输入；随后用 `-global-isel -global-isel-abort=2` 编译并记录 YAML optimization remarks。结果位于 `results/<run-id>/`：

- `report.md`：总体结果和按 GPU、语料、优化级别、失败阶段的统计；
- `summary.csv`：机器可读汇总；
- `cases.jsonl`：每个编译 case 的状态、耗时和输入 SHA-256；
- `fallbacks.jsonl`：每个 fallback 函数以及归一化原因签名；
- `cases/<case-id>/`：命令、stdout、stderr、remarks 和逐 case JSON 原始证据。

对每种原因签名选择最小样本并尝试约简：

```bash
gisel-study reduce --manifest experiment.yaml --run results/<run-id>
```

约简脚本会先复核 run 元数据、工具链 provenance 和原始输入 SHA-256，再同时要求 SelectionDAG 成功且 GlobalISel 仍产生相同归一化签名。最终约简产物还会再次 replay，产物放在 `reproducers/`；重复运行会替换其中同一根因簇的旧生成物。

## 已发布的 baseline

仓库中的 [`published-results/full-20261106-reviewed`](published-results/full-20261106-reviewed) 是固定版本实验的公开结果包：

- 11,322 个计划 case；
- 7,041 个 SelectionDAG 基线有效并尝试 GlobalISel 的 case；
- 885 个 fallback case，包含 6,111 个函数级 fallback 事件；
- 107 个归一化候选签名；
- 104 个通过最终重放的 reduced artifact。

公开结果保留汇总数据、逐 case/逐函数索引和每个候选签名的代表 reproducer，但不把约 1.7 GB 的逐 case stdout、stderr 和 YAML remarks 放入 Git 历史。所有原工作区绝对路径都替换为 `<WORKSPACE>`，文件校验值记录在 `SHA256SUMS`。

从一个本地完整 run 重新生成公开结果：

```bash
gisel-study publish-results \
  --run results/full-20261106-reviewed \
  --output published-results/full-20261106-reviewed \
  --workspace .
```

## 统计口径

这里的“fallback”严格指 LLVM 打印的 `Instruction selection used fallback path`。没有出现该诊断但 GlobalISel 失败、崩溃或超时的情况会分别记录，不能算作 fallback。HIP 源码若无法在固定 SDK 中编译，也单独计为 source compile failure，不进入“SDAG 有效、已尝试 GlobalISel”的模块分母。函数分母是这些模块中定义的函数数，不表示每个函数都执行到了同一个 GlobalISel 阶段。

HIP device bitcode 可能同时包含样例 kernel 和 ROCm 设备库函数，因此模块 fallback 不等于样例自身的 kernel 必然 fallback；可通过 `fallbacks.jsonl` 中的函数名继续拆分。若 YAML remarks 损坏，编译结果仍按进程状态和显式 fallback 警告分类，并单独记录 remarks 解析错误。

LLVM 自带 AMDGPU `.ll` 测试只用 `-O2`，HIP 样例使用 `-O0/-O2`。完整实验是编译覆盖研究，不证明生成代码在真实硬件上的运行正确性或性能。

## 验证工具本身

```bash
python -m unittest discover -v
python -m compileall -q gisel_study
bash -n scripts/build-llvm.sh
```

## 许可证

本项目代码使用 Apache License v2.0 with LLVM Exceptions，见 [`LICENSE.TXT`](LICENSE.TXT)。公开 reproducer 可能包含或派生自 LLVM 和 ROCm Examples 的测试输入，详细归属见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
