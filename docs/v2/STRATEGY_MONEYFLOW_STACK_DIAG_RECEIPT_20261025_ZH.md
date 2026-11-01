# Strategy 回执：moneyflow 剥舱+80/20 组合诊断（VOID）

- 角色：QuantLab Strategy
- 时刻（America/New_York）：2026-10-25T05:02:30-04:00
- live=false；promotion=false；paper 未动；未 commit；未改代码；**.ok 未移动**（Arch 归档）

## 结论

**VOID**。外挂 RSS 监控在 book-smoke 启动后立刻观测到主进程 `VmHWM=4511.5MB > rss_cap_mb=1536`，按 .ok / 任务要求终止进程树，**不采信任何门控数字**。

## 授权与开跑前核验（均通过）

| 项 | 结果 |
|---|---|
| .ok | `output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.ok` |
| .ok sha256 | `68c04741cbabd8cd3821146168ed262bf22672f327646a8ab7139c37bd411514` |
| allow_run | true；未进 `_consumed` |
| 时刻 | 05:01:29 ET（不在 10:00–10:45） |
| `output/loop/RESEARCH_QUIET.lock` | 不存在 |
| pgrep kline/export_static/snapshot/gen | 空 |
| script sha | `c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63` MATCH |
| trunk/sat/两档 nav sha | 与 .ok 逐字 MATCH |
| out_dir 事先 | 不存在 |
| MemAvailable | ≈11.66 GiB ≥ 2.5 |
| python | `/workspace/qlvenv/bin/python` 3.12.14 |

## 命令

```bash
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 timeout -k 30 1800 nice -n 10 \
  /workspace/qlvenv/bin/python research/strategy_moneyflow_stack_diag_v1.py \
  --arch-ok output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.ok \
  > output/strategy_hiliq/moneyflow_stack_8020_20261025_run.log 2>&1
```

- 开始：2026-10-25T05:01:41-04:00
- 终止：2026-10-25T05:01:53-04:00（用时 ≈11.8s）
- 主 PID：214222（外层 timeout 214221）
- **EXIT**：进程被 SIGTERM 终止；包装 shell 随后因 `; echo EXIT=$?` 解析报错以 exit 2 结束。**以 VOID 为准，不报成功 EXIT=0。**
- 外层日志：`moneyflow_stack_8020_20261025_run.log` 为空（0 字节，stdout 缓冲未刷）
- book-smoke 侧日志：`out_dir/book_smoke/run.log` 显示已启动 `quantlab.cli book-smoke --run-nav … --capitals 600000,1000000`，未完成

## 内存

| 观测 | 值 |
|---|---|
| rss_cap_mb（.ok） | 1536 |
| 终止时 VmRSS | 289.7 MB（296672 kB） |
| **VmHWM（breach）** | **4511.5 MB（4619744 kB）** |
| 动作 | SIGTERM → 确认无残留 strategy_moneyflow / book_smoke 进程 |

## 门控 / 指标（均无）

| 项 | 值 |
|---|---|
| 门B | **null**（VOID，无 summary） |
| GATE_V3 | **null**（VOID；即便跑完也会因钉死的 `decay_outcome=REJECT` 预期不过） |
| 60万 CAGR/MDD/Calmar | 无 |
| 100万 CAGR/MDD/Calmar | 无 |
| 与 capacity_adv 对照 | 未完成 |

## 披露（仍适用）

- 混合策略：剥卫星表内 510300 后 80/20；**无 topN / 无单名 6% 帽**（与 CMC 相反）
- `decay_outcome=REJECT`（Alpha DECAY_DOWNGRADE 映射）→ GATE_V3 即使跑完也预期不过
- 结果即使将来重跑也只是研究级，禁升 paper/live

## 产物（不完整）

`out_dir=output/strategy_hiliq/moneyflow_stack_8020_20261025`

| 文件 | sha256（前 16） | 说明 |
|---|---|---|
| meta.json | 9d17df4f19412125… | 钉与覆盖率已写完 |
| blended_weights_8020.parquet | 3f8a2b33a995f381… | 混合权重已写出 |
| book_smoke/run.log | f3214693e7fb6638… | book-smoke 未完成 |
| VOID.json | （见下方全长） | 本 VOID 标记 |
| ARTIFACT_MANIFEST.txt | （见下方全长） | 标注 VOID/不完整 |
| summary.json | **缺失** | 脚本未写到 |

**.ok 仍在原位** sha `68c04741…`；single_use 未由本方归档。是否作废/重签由 Arch 决定。

## 建议（不擅自执行）

1. Arch：本 .ok 建议 VOID/作废；若重签，需先查 book-smoke 为何 VmHWM≈4.5GB（是否一次加载双档 X2 行情），或加外挂 runguard / 降内存路径后再签。
2. 勿把本 out_dir 当成功诊断；重跑前应换新 out_dir 或清空并获新 .ok。
3. 叶25 窗 10:00–10:45 ET 仍避开。

live=false。

## 产物 sha（回执落盘时；回执自身 sha 见文末一行）

- `output/strategy_hiliq/moneyflow_stack_8020_20261025/ARTIFACT_MANIFEST.txt`：`bf98abec1b8e112c8df816251baf661e05cea43c787e7e4e961c1389ea9ad726`
- `output/strategy_hiliq/moneyflow_stack_8020_20261025/VOID.json`：`5a586007722b36605de04753525abc90c901c1d3bd7d8caeb02a7d335c59d5ed`
- `output/strategy_hiliq/moneyflow_stack_8020_20261025/meta.json`：`9d17df4f194121259bf50e611ad9ee3ca3d04d798a2114bc489dd1db9caecb40`
- `output/strategy_hiliq/moneyflow_stack_8020_20261025/blended_weights_8020.parquet`：`3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`
- `output/strategy_hiliq/moneyflow_stack_8020_20261025/book_smoke/run.log`：`f3214693e7fb6638a82ecd89bab47e136211ffb55397f64bbb28b9a036b59f47`
- `output/strategy_hiliq/moneyflow_stack_8020_20261025_run.log`：`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

（本回执全文 sha256 不含下一行）
- 本回执全文：`737c436708f3a2c48ac6c1993019f7970ceb220151ff47043a86202fd13d883f`
