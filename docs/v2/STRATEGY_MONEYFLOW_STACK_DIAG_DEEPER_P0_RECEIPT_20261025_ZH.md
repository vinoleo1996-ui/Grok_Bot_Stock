# Strategy 回执：moneyflow deeper P0 reuse-blended 诊断（COMPLETE）

- 角色：QuantLab Strategy
- 时刻（America/New_York）：2026-10-25T05:52:42-04:00
- live=false；promotion=false；paper 未动；未 commit；**未改 research/**（allow_write_code=false）；**.ok 仍留原位**（未归档/未 VOID）

## 结论

**COMPLETE**。按 Arch run.ok `b5425d53…` 一次开跑成功：外挂 VmHWM 帽 2048 未触发；峰值 **VmHWM=753.8MB**；dst blended sha **MATCH** `3f8a2b33…`（hardlink）；写出 `summary.json` + `ARTIFACT_MANIFEST.txt`。门 B / GATE_V3 均 **fail**（`decay_outcome=REJECT` 钉死，预期失败；非 VOID）。禁抬帽；禁复用废签 `42a16384` / `68c04741`。

## 授权与开跑前核验（均通过）

| 项 | 结果 |
|---|---|
| .ok | `output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_RUN.ok` |
| .ok sha256 | `b5425d53498ff81bf7e94beda31547619290b5414ec9f8eec1d815fc468d4abf` MATCH |
| allow_run | true；allow_write_code=false；未进 `_consumed` |
| script sha | `f7a6a77595eef52120f7619eff9a8b8656b8534d10b76afa4d18ea5d9bd3150c` MATCH |
| trunk/sat/两档 nav / reuse_blended sha | 与 .ok 逐字 MATCH |
| reuse_blended_path | `output/strategy_hiliq/_recovery/strategy/20261025T0502ET_moneyflow_stack_void/blended_weights_8020.parquet` |
| expected_blended_sha256 | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103` |
| out_dir 事先 | 不存在 → `moneyflow_stack_8020_reuse_blended_20261025` |
| rss_cap_mb | 2048（外挂 `/tmp/mf_lowmem_vmhwm_guard.py`；禁抬 4.5GB） |
| `output/loop/RESEARCH_QUIET.lock` / 根锁 | 不存在 |
| healthz | ok；quiet=false；snapshot_pending=false |
| pgrep kline/export_static/snapshot/gen | 空 |
| leftover strategy_moneyflow / mf_lowmem / book-smoke | 空 |
| MemAvailable | ≈12.21 GiB ≥ 2.5 |
| 叶25 窗 10:00–10:45 ET | 未落入（开跑 05:51 ET） |

## 命令（含显式 --out-dir）

```bash
cd /workspace/QuantLab
OK=output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_DEEPER_P0_REUSE_BLENDED_RUN.ok
OKSHA=b5425d53498ff81bf7e94beda31547619290b5414ec9f8eec1d815fc468d4abf
OUT=output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025
LOG=output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025_run.log
MON=output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025_vmhwm_monitor.log

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

- 开始：2026-10-25T05:51:16.104666-04:00
- 结束：2026-10-25T05:51:35.965376-04:00（elapsed ≈19.9s；脚本内 elapsed_sec≈19.613）
- **EXIT=0**（外挂 JSON：`void=false`；无 `VOID.json`）

## 内存

| 观测 | 值 |
|---|---|
| rss_cap_mb（.ok / 外挂） | 2048 |
| **peak VmHWM** | **753.8 MB**（< 2048，未杀） |
| peak VmRSS | 702.1 MB |
| 监控日志 | `output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025_vmhwm_monitor.log` |

## blended

| 项 | 值 |
|---|---|
| dst | `output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025/blended_weights_8020.parquet` |
| sha256 | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103` **MATCH** |
| 复用方式 | hardlink（nlink=2）；skip_trunk_sat_read=true；未重算混合 |

## 门控（研究披露；decay=REJECT → GATE_V3 预期 fail）

| 门 | pass | 备注 |
|---|---|---|
| 门 B | **false** | 两档 calmar>trunk=true；mdd_le_15=false（60万 mdd≈−25.6%；100万≈−28.2%） |
| GATE_V3 | **false** | `decay_outcome=REJECT`（.ok pin）→ decay_keep=false；tradable_to_le_20pct=true（turnover_2s_mean≈0.0442）；两档 mdd_le_25=false |

### combo（X2/BOOK book-smoke）摘要

| AUM | CAGR | MDD | Calmar | Sharpe |
|---|---|---|---|---|
| 600000 | 0.0256 | −0.2563 | 0.0997 | 0.2270 |
| 1000000 | 0.0352 | −0.2822 | 0.1247 | 0.2678 |

trunk_ref：60万 cagr≈−0.0058 / mdd≈−0.2993；100万 cagr≈0.0171 / mdd≈−0.3299。

## 产物

- out_dir：`output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025/`
- `summary.json` sha256 `5718de4cea59ff8e76af76eb2733051a0e9c425b48c645f2ad08b0c917cafd5e`（sha8 `5718de4c`）
- `meta.json` / `ARTIFACT_MANIFEST.txt` / `blended_weights_8020.parquet`
- `book_smoke/`：分档串行 60万→100万；`--arms BOOK`；`book_smoke_summary_agg.json`
- 运行日志：`…_run.log`；VmHWM 监控：`…_vmhwm_monitor.log`
- run.ok：仍在原位（Arch 归档）

## 约束遵守

- 未抬 RSS 帽；未复用废签 `42a16384` / `68c04741`
- 未改 research/；未 commit；未碰 paper / 叶25
- live=false；promotion=false；decay=REJECT 已披露

## 回执自身

- 回执自身 sha256：`f9817a3ff9808af5ddd943a0b7251a0d3e769bb6beab956bb961bf8d15db554a`（sha8 `f9817a3f`；含 summary sha 补丁后）
