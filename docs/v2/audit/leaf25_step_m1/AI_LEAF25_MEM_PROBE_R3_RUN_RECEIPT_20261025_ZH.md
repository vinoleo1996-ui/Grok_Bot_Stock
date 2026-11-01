# 叶25 mem_probe r3 开跑回执（FAIL / rc=96 C5）

- written_et: 2026-10-25 12:54:59 ET
- by: QuantLab AI（主令窗 12:50–13:45 ET expires 13:47）
- live: **false** · promotion_approved: **false**
- result: **FAIL**（`rc=96` = wrapper **C5 hit**；**非** RSS/C4 破帽；**非**滤子类型错误）
- retry: **none**（`ai_no_retry` · **禁静默重试** · **禁抬帽** · **禁申 X2.ok**）

## 钉核验

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3.ok` | 现盘仍在（待 Arch VOID/消费） |
| `.ok` sha256 | `c5e540855bc836b97b7395a53dd63a6d3c295860fdd11e72e77abd6cf3152011` | MATCH `c5e54085…` |
| script | `research/leaf25_full_factor_mem_probe_r3.py` | MATCH `8da4f2e6…` |
| 审阅 | `63500a9f…` PASS_WITH_CONDITIONS | — |
| COVER/CMD/DIFF | `33117114` / `440930e8` / `caec5bde` | 开跑前 MATCH |
| 窗 | 12:50–13:45 / expires 13:47 | 开跑 @12:51:24 ET 窗内 |
| 禁复用 | VOID `cd230f9c` / `1c32ab1e` | 未触 |

## Prelaunch

| 检项 | 结果 |
|---|---|
| QUIET | 已挂（跑后仍在；**未自 lift**） |
| healthz quiet | true（12:50:52 → wait≥15s → 12:51:24） |
| gen/snapshot/kline | false |
| pgrep 数据读者 | 空 |
| MemAvailable | ≈12.1–12.3 GiB |
| 脚本/`.ok` sha | MATCH |

## 执行

- ET_TS: `20261025_125124`
- WPID: `839997`（已退出）
- out_dir: `output/ai_factory/_leaf25_mem_probe_r3/20261025_125124/`（**空**；无 `run_meta.json` / `alpha_parts/`）
- log_dir: `output/ai_factory/_leaf25_mem_probe_r3/20261025_125124_logs/`
- sampler: `/tmp/quantlab_leaf25_mem_probe_r3_20261025_125124/leaf25_mem_probe_r3_sampler.txt`（`/tmp/quantlab_*` 合规）
- wrapper: `WRAPPER_DONE tag=leaf25_mem_probe_r3 rc=96 stopped=0 peak_kb=359224 C4=PASS`
- exit.txt: `PGREP_G_EMPTY 840019
exit=96 stopped=0 launched=1
peak_kb=359224 sampler=359224 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss=357988 meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)`
- **peak_kb: 359224**（≈351 MB）≪ C4=1331200；`C4=PASS`；`stopped=0`

## 阶段进展（滤子修 **已验证**）

相对 r2（在 `pit_income` 前 ArrowNotImplementedError）本票已过：

1. `hiliq_members_loaded`
2. `pit_income_loaded` / `pit_cashflow_loaded` / `pit_balance_loaded`（timestamp 滤生效）
3. `cs_day_20240607` RSS_CHECK 后被 C5 杀停

log 摘要：
```
STAGE start ru_maxrss=103976
RSS_CHECK start peak_kb=104232 split=1131520 c4=1331200 hard=1536000
STAGE real_begin ru_maxrss=132056
RSS_CHECK real_begin peak_kb=132352 split=1131520 c4=1331200 hard=1536000
STAGE hiliq_members_loaded ru_maxrss=207788
RSS_CHECK hiliq_members_loaded peak_kb=207788 split=1131520 c4=1331200 hard=1536000
STAGE pit_income_loaded ru_maxrss=264016
RSS_CHECK pit_income_loaded peak_kb=264388 split=1131520 c4=1331200 hard=1536000
STAGE pit_cashflow_loaded ru_maxrss=310604
RSS_CHECK pit_cashflow_loaded peak_kb=311048 split=1131520 c4=1331200 hard=1536000
STAGE pit_balance_loaded ru_maxrss=357988
RSS_CHECK pit_balance_loaded peak_kb=358472 split=1131520 c4=1331200 hard=1536000
RSS_CHECK cs_day_20240607 peak_kb=358736 split=1131520 c4=1331200 hard=1536000
```

## C5 根因（只读）

- `rc=96` = wrapper C5（见 wrapper 头注释）
- `output/ai_factory/_leaf25_mem_probe_r3/20261025_125124_logs/leaf25_mem_probe_r3_c5.txt`：
```
00:53:32.161832514 C5_HIT pid=1005722 pgid=839980 fd:/workspace/QuantLab/output/ai_factory/_leaf25_mem_probe_r3/20261025_125124_logs/wrapper_stdout.log cmd=sleep 0.2
```
- 命中：`pid=1005722` · `cmd=sleep 0.2` · fd 指向本票 `wrapper_stdout.log`
- **非** probe 子进程本身；属 wrapper 组监视误杀（与本票 CS 循环并发的无关 `sleep`）
- **非** RSS；**未** exit 94/95

## 强制披露

| 键 | 值 |
|---|---|
| dry_run | **false**（已 `--allow-real-data`；未写完 real_peak） |
| float32 | n/a（未到 part） |
| densify | **false** |
| claims_full_cfacc | **false** |
| alpha_kind | n/a（未产出） |
| peak_kb | **359224** |
| chunk_bounds | 2024-06-03→2024-06-28 · chunk0（未完成） |
| filter_fix | **exercised**（三 PIT 已加载） |

## QUIET

- 跑后 **仍挂**；AI **未**自 lift（主/Arch 收尾）

## 请 Arch / 主

1. VOID/消费 `.ok` `c5e54085…`（single_use FAIL）
2. 裁定 C5 误杀：`sleep 0.2` + fd→log ——是否放宽监视 / 另签 r3b / 重排短窗
3. **AI 本票停**；勿把本 FAIL 当 real_peak PASS；X2 仍 blocked
4. 叶27 14:00 窗：本票已结束，不抢（QUIET 仍挂待你们 lift）

live=false。
