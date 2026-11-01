# Strategy 回执：moneyflow lowmem v1.1 诊断（VOID）

- 角色：QuantLab Strategy
- 时刻（America/New_York）：2026-10-25T05:27:41-04:00
- live=false；promotion=false；paper 未动；未 commit；**未改 research/**（allow_write_code=false）；**.ok 未移动**（Arch 归档）

## 结论

**VOID**。显式对齐 `--out-dir` 后开跑；外挂 VmHWM 帽 `2048` 在约 3s 内观测到主进程树峰值 **VmHWM=2320.9MB > 2048**，按 .ok / 任务要求 SIGTERM，**不采信任何门控数字、不抬帽、不开第二份**。

## 先前秒退（out_dir 未对齐）

| 项 | 值 |
|---|---|
| 时刻 | 2026-10-25T05:23:42-04:00 |
| 原因 | 未传 `--out-dir`；脚本挡：`.ok` 要求 `moneyflow_stack_8020_lowmem_20261025` ≠ CLI/default `moneyflow_stack_8020_20261025` |
| EXIT | 1 |
| peak VmHWM | 6.4 MB（**非**内存杀） |
| 日志去向 | `output/strategy_hiliq/_recovery/strategy/20261025T0523ET_lowmem_outdir_mismatch/` |
| 处置 | 不废 run.ok `42a16384…`；改传显式 `--out-dir` 重跑一次 |

## 授权与开跑前核验（重跑前均通过）

| 项 | 结果 |
|---|---|
| .ok | `output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RUN.ok` |
| .ok sha256 | `42a163840cf4023d2ddb39471acd7368550025e7db49a1519bf68e1c91faa262` MATCH |
| allow_run | true；未进 `_consumed` |
| script sha | `2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616` MATCH |
| trunk/sat/两档 nav sha | 与 .ok 逐字 MATCH |
| expected_blended_sha256 | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`（本轮未写出 blended） |
| out_dir 事先 | 不存在 |
| rss_cap_mb | 2048（外挂 `/tmp/mf_lowmem_vmhwm_guard.py`；禁抬 4.5GB） |
| `output/loop/RESEARCH_QUIET.lock` / 根锁 | 不存在 |
| healthz | ok；quiet=false；snapshot_pending=false |
| pgrep kline/export_static/snapshot/gen | 空 |
| MemAvailable | ≈11.55 GiB ≥ 2.5 |
| 叶25 窗 10:00–10:45 ET | 未落入（开跑 05:26 ET） |
| 并发副本 | 无 |

## 命令（含 --out-dir）

```bash
cd /workspace/QuantLab
OK=output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_LOWMEM_V11_RUN.ok
OKSHA=42a163840cf4023d2ddb39471acd7368550025e7db49a1519bf68e1c91faa262
OUT=output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025
LOG=output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025_run.log
MON=output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025_vmhwm_monitor.log

PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 nice -n 10 \
  python3 -u /tmp/mf_lowmem_vmhwm_guard.py \
    --cap-mb 2048 --interval 0.2 \
    --void-dir "$OUT" \
    --arch-ok-sha256 "$OKSHA" \
    --monitor-log "$MON" \
    -- /workspace/qlvenv/bin/python -u research/strategy_moneyflow_stack_diag_v1.py \
         --arch-ok "$OK" \
         --out-dir "$OUT" \
  > "$LOG" 2>&1
```

- 开始：2026-10-25T05:26:31-04:00
- 终止：2026-10-25T05:26:34-04:00（elapsed ≈3.0s）
- 根 PID（被杀）：255631
- **EXIT=2**（外挂 VmHWM 违约 → 约定 exit 2）
- 杀信号：SIGTERM

## 内存

| 观测 | 值 |
|---|---|
| rss_cap_mb（.ok / 外挂） | 2048 |
| **peak VmHWM（breach）** | **2320.9 MB** |
| 终止时 VmRSS | 2320.9 MB |
| 监控样例（约 0.2s 间隔） | 7.3 → 81.7 → 531.5 → 1225.7 → 1775.7 → **2320.9** |
| 动作 | SIGTERM → 确认无残留 strategy_moneyflow / mf_lowmem_vmhwm_guard |

## 门控 / 指标（均无）

| 项 | 值 |
|---|---|
| 门B / gate_B | **null**（VOID，无 summary） |
| GATE_V3 / gate_v3 | **null**（VOID） |
| blended sha vs `3f8a2b33…` | **未写出** → 无 MATCH；不发明数字 |
| summary.json | **缺失** |
| ARTIFACT_MANIFEST.txt | **缺失**（仅 VOID.json） |
| 60万/100万 CAGR/MDD/Calmar | 无 |

## 产物（不完整）

`out_dir=output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025`

| 文件 | sha256 | 说明 |
|---|---|---|
| VOID.json | `d90a837a251ed8853e1917eca5c8b201c509d5c7df893e7ae93a9d56ff17a1b4` | 外挂写出 |
| `…_run.log` | `813374dea3769a710c60c61ea6be645f76c94b248b3915563152f120afeeab24` | 一行 JSON VOID |
| `…_vmhwm_monitor.log` | `8f004116413526e87a4f1a0b1166a097eab028070cddc3d8843fb6a4551ba677` | 爬升样例 + BREACH |
| summary.json / ARTIFACT_MANIFEST / blended | **缺失** | 未跑到写出 |

**.ok 仍在原位** sha `42a16384…`；single_use 未由本方归档。是否作废/重签由 Arch 决定。

## 披露（仍适用）

- lowmem v1.1：分档串行 + `--arms BOOK`；rss 目标 2048；**禁抬帽**
- `decay_outcome=REJECT` 钉死 → 即便跑完 GATE_V3 亦预期不过
- 结果即使将来重跑也只是研究级，禁升 paper/live
- 叶25 窗 10:00–10:45 ET 仍避开

## 建议（不擅自执行）

1. Arch：本 run.ok 建议按 VOID 归档；若再签需更深降内存（book-smoke 仍在启动瞬间冲过 2GB），**Strategy 不自行抬帽硬跑**。
2. 勿把本 out_dir 当成功诊断；重跑前换新 out_dir 或清空并获新 .ok。
3. 先前 out_dir 未对齐秒退与本次 VmHWM VOID 分开记账；后者才是内存违约。

live=false。

## 产物 sha（回执落盘时；回执自身 sha 见文末一行）

- `output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025/VOID.json`：`d90a837a251ed8853e1917eca5c8b201c509d5c7df893e7ae93a9d56ff17a1b4`
- `output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025_run.log`：`813374dea3769a710c60c61ea6be645f76c94b248b3915563152f120afeeab24`
- `output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025_vmhwm_monitor.log`：`8f004116413526e87a4f1a0b1166a097eab028070cddc3d8843fb6a4551ba677`

（本回执全文 sha256 不含下一行）
- 本回执全文：`c21d3f68849703d6b10c73e4062bbefd7d831d0d7a72becd107475775e6c5774`
