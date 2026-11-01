# 叶25 mem_probe r3b 开跑回执（PASS / rc=0）

- written_et: 2026-10-25 15:17:42 ET
- by: QuantLab AI（主令 prelaunch；Arch `.ok` 已签；窗 15:00–15:45 expires 15:47）
- live: **false** · promotion_approved: **false**
- result: **PASS**（`rc=0`；`C4=PASS`；`C5=PASS`/无命中；`stopped=0`；real_peak 完成）
- retry: **none**（本票 PASS；`ai_no_retry` 不适用抬帽/重跑；**禁抬帽** · **禁申 X2.ok** · **禁擅 lift QUIET**）
- ≠X2 · 未触 leaf27

## 钉核验

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok` | 开跑时 SIGNED |
| `.ok` sha256 | `6054b3bfc44977614d299976da28e72d757885cf6a59fa26b361d4112060692b` | MATCH `6054b3bf…` |
| wrapper PIN | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` | MATCH `b1208d3c…` |
| probe | `research/leaf25_full_factor_mem_probe_r3.py` | MATCH `8da4f2e6…` |
| 帽 | c4=1331200 / stop=1484800 / hard=1536000 | **未抬** |
| `--c5-ignore` | **未用** | — |
| 禁路径 | `.draft.sh` / `e03a61b6` | **未触** |
| 禁复用 VOID | `c5e54085` / `cd230f9c` / `1c32ab1e` | **未触** |
| 窗 | 15:00–15:45 / expires 15:47 | 开跑 @15:12:24 ET 窗内；结束 @≈15:16:34 ET |

## 执行

- ET_TS: `20261025_151224`
- WPID: `1156368`（wrapper；已退出）
- PPID/child: python `1156406`（已退出）
- OUT: `output/ai_factory/_leaf25_mem_probe_r3b/20261025_151224/`
- LOGDIR: `output/ai_factory/_leaf25_mem_probe_r3b/20261025_151224_logs/`
- SAMP: `/tmp/quantlab_leaf25_mem_probe_r3b_20261025_151224`
- universe/mode: **HI_LIQ** · **month** · chunk_id=0 · 2024-06-03→2024-06-28（n_open_days=19）
- wrapper_stdout: `WRAPPER_DONE tag=leaf25_mem_probe_r3b rc=0 stopped=0 peak_kb=323784 C4=PASS`
- exit.txt: `PGREP_G_EMPTY 1156406` / `exit=0 stopped=0 launched=1` / `peak_kb=323784 sampler=323784 … C4=PASS(limit=1331200)`
- **peak_kb: 323784**（sampler 权威；≈316 MB）≪ C4=1331200
- meta `rss.peak_kb`: 323008（ru_maxrss / after_gc）
- **C4=PASS** · **C5=PASS**（无 `*_c5.txt` 命中；`rc≠96`）
- abort_reason: **none**

## 产物

| 文件 | sha256 前 8 |
|---|---|
| `run_meta.json` | `bebfcada…` |
| `chunk_plan_used.json` | `684cb143…` |
| `alpha_parts/chunk_0000.parquet` | `4c18ffe7…` |
| log（`/tmp/quantlab_wrapper_logs/leaf25_mem_probe_r3b.log`） | `f30cbb8b…` |
| sampler | `dfeccb76…` |
| exit.txt | `4ba2d1d1…` |

## 阶段进展（完整 real_peak）

1. `hiliq_members_loaded` → `pit_income/cashflow/balance_loaded`（timestamp 滤生效）
2. `cs_day_20240607` / `20240617` / `20240624` RSS_CHECK
3. `cs_alpha_done` → `real_after_gc` → `after_chunk`
4. probe OK：`dry=False universe=HI_LIQ chunk_id=0 peak_kb=323008`

log 摘要：
```
STAGE start ru_maxrss=102636
RSS_CHECK start peak_kb=103168 split=1131520 c4=1331200 hard=1536000
STAGE real_begin ru_maxrss=130580
STAGE hiliq_members_loaded ru_maxrss=206172
STAGE pit_income_loaded ru_maxrss=254436
STAGE pit_cashflow_loaded ru_maxrss=295208
STAGE pit_balance_loaded ru_maxrss=321924
RSS_CHECK cs_day_20240607 peak_kb=323008
RSS_CHECK cs_day_20240617 peak_kb=323008
RSS_CHECK cs_day_20240624 peak_kb=323008
STAGE cs_alpha_done ru_maxrss=323008
STAGE real_after_gc ru_maxrss=323008
RSS_CHECK after_chunk peak_kb=323008
OK mem_probe_r3 dry=False universe=HI_LIQ chunk_id=0 peak_kb=323008
```

## 强制披露

| 键 | 值 |
|---|---|
| dry_run | **false**（`--allow-real-data`） |
| float32 | **true** |
| densify | **false** |
| claims_full_cfacc | **false** |
| alpha_kind | `crude_accrual_cs_zscore_probe_only` |
| n_names / n_days / n_rows | 2245 / 19 / 34261 |
| peak_kb（sampler） | **323784** |
| peak_kb（meta/after_gc） | **323008** |
| C4 / C5 | **PASS** / **PASS** |
| wrapper_rc / probe | **0** / **0**（exit=0） |
| chunk_bounds | 2024-06-03→2024-06-28 · chunk0 · **完成** |

## QUIET

- 跑后 **仍挂**（healthz `quiet=true`；`output/loop/RESEARCH_QUIET.lock`）
- AI **未**自 lift（等主/Arch 收尾）

## 请 Arch / 主

1. 收本 PASS 回执；裁定是否消费 `.ok` `6054b3bf…`（single_use）
2. 是否 lift QUIET（AI **不**擅动）
3. **AI 本票停等主令**；≠X2；不解阻 X2；叶27 month DRAFT 仍 HOLD 勿撞
4. 本票非 full CFACC；勿把 probe PASS 当 X2 ACCEPT

live=false。
