# Arch 运行授权规范 · 轻量自测 .ok（全队适用）

- 版本 v1；生效：2026-10-18 01:59 ET（主 Agent 裁定 E-2）；签发人：QuantLab Arch
- live=false，promotion=false

## 1. 适用范围
任何执行项目代码的测试都算「运行」，须先有 Arch 签的 .ok：pytest、单元测试、合成数据 harness、解析器/门禁测试、python -c 调用项目模块等。只跑 py_compile 和 sha256sum 不算运行。
- 合成数据测试：轻量 .ok（scope=selftest）。
- 读取任何真实数据（raw、cs_panel、output/ 下产物等）的测试：另须 allow_real_data=true，并钉住数据 sha（§6）。

## 2. 必填键
```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=2026-10-18T02:10:00-04:00
scope=selftest
runner_sha256_<测试文件 stem>=<64 hex>
dep_sha256_<模块 key>=<64 hex>
allow_selftest=true
allow_real_data=false
allow_dryrun=false
allow_full=false
allow_smoke=false
allow_diagnostic=false
allow_disclosure_only=false
live=false
promotion=false
out_dir=/tmp/<tag>
expires_et=<带时区 ISO8601>
```
- signed_et、expires_et 为带时区 ISO8601。
- runner_sha256_* 钉测试文件全长 sha；每个被测模块（含其 import 的项目模块）各一条 dep_sha256_*。
- 除 allow_selftest（及按需 allow_real_data）外，该 runner 所认识的全部 allow_* 都须显式写 false。
- out_dir 只能是 mkdtemp 生成的目录（写 out_dir=mkdtemp）或 /tmp/<tag>；不得指向 output/ 或仓库内任何路径。

## 3. 格式规则
- 每行一个 key=value；UTF-8 无 BOM；LF 换行。
- 不得有行内注释（ok_runner_pin 不剥注释，`true # x` 不等于 true，会拒跑）。说明另起以 # 开头的整行。
- 同一键不得重复。sha 一律 64 位小写十六进制，不收前缀。
- 只有 Arch 写 .ok；建议路径 output/<team>/ARCH_RUN_AUTH_SELFTEST_<tag>.ok。

## 4. 代码内门禁
测试文件顶层先调门禁，再 import 被测模块：
```python
import sys; sys.path.insert(0, "<repo>/scripts_eng")
from ok_runner_pin import enforce
_G = enforce(__file__, [OK_PATH], modes=["selftest"], deps={...})
# 自查（ok_runner_pin 当前不检查）：scope==selftest、allow_real_data 与本测试是否读真实数据一致、out_dir 不在 output/ 下
import <被测模块>  # 放行之后才 import
```
- 用 pytest 时把门禁放在 conftest.py 或测试模块顶层，保证收集阶段就执行；不得用 importorskip 等跳过。
- 读真实数据的测试用 modes=["selftest","real_data"]。

## 5. 运行命令
```
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest <测试文件> -q -p no:cacheprovider
```
- 用 qlvenv（系统 python3 没有 pytest）；串行，不与研究进程并发。
- 单进程 RSS ≤1.5GB；超限立即中止并报 Arch。回执记录峰值 RSS（/usr/bin/time -v 的 Maximum resident set size 或 VmHWM）；记不了要写明。

## 6. 真实数据测试
- 须 allow_real_data=true，并为每个读取的数据文件钉 dep_sha256_<key>=<64 hex>（运行时重算比对）。
- 只读；不得写 output/ 或 raw；任何写入只进 out_dir。

## 7. 清理
- 结束后删除 out_dir、临时 .ok 格式样本、harness 和辅助脚本（如 /tmp/<tag>/harness.py、mkok.py）；不得留 __pycache__ 或 .pytest_cache。
- 回执须含：命令行、.ok 路径与 sha、测试文件与依赖全长 sha、通过/失败数、峰值 RSS、清理后 `ls` 证明。

## 8. 违规处理
- 无 .ok 运行测试：首次 P3（记录，不作废产物）；同一 agent 第二次 P2，相关产物须在合规 .ok 下复测后才可引用；第三次 P1，报主 Agent。
- 测试写入 output/ 或读真实数据却没有 allow_real_data：至少 P2。

## 9. 与 ok_runner_pin（c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485）的关系
- mode 名是通用的：enforce(..., modes=["selftest"]) 会要求 allow_selftest=true，现有代码无需修改即可使用 selftest；真实数据用 modes=["selftest","real_data"]（检查 allow_real_data=true）。
- 当前门禁不检查：scope、out_dir 位置、BOM、signed_et 格式、未列出的 allow_* 是否为 false、合成测试中 allow_real_data=false。暂由测试文件自查（§4）；建议 Eng 在下一版 ok_runner_pin 中加入 selftest 专用检查（改动须另经 Arch 审）。
