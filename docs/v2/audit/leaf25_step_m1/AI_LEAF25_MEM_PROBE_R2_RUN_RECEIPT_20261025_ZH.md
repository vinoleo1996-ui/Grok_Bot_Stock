# 叶25 mem_probe r2 开跑回执（FAIL / rc=1）

- written_et: 2026-10-25 12:29:36 ET
- by: QuantLab AI（主令短窗 12:25–13:05 ET · 令文 sha8 `d7fb2580`）
- live: **false**
- promotion_approved: **false**
- result: **FAIL**（非 RSS 破帽；`C4=PASS`）
- retry: **none**（`ai_no_retry=true` · **禁自重跑** · **禁抬帽** · **禁申 X2.ok**）

## 钉核验（开跑前）

| 项 | 值 | 状态 |
|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.ok` | 现盘仍在（待 Arch 消费/VOID） |
| `.ok` sha256 | `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279` | MATCH `cd230f9c…` |
| script | `research/leaf25_full_factor_mem_probe_r2.py` | MATCH `9dfe173a…` |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | MATCH `4240ce82…` |
| 主令确认 | `docs/v2/audit/MAIN_LEAF25_MEM_PROBE_R2_WINDOW_CONFIRM_20261025_ZH.md` | MATCH `d7fb2580…` |
| 窗 | 12:25–13:05 ET / expires 13:07 | 开跑 @12:27:04 ET 窗内 |
| C4/stop/hard | 1331200 / 1484800 / 1536000 | 未抬帽 |
| 宇宙/块 | HI_LIQ · month 2024-06-03→2024-06-28 · chunk0 | 与 `.ok` 一致 |

## Prelaunch

| 检项 | 结果 |
|---|---|
| `RESEARCH_QUIET.lock` | 已挂（跑后仍在；**未自 lift**） |
| healthz quiet | true（12:26:07 → wait≥15s → 12:26:33 / 12:27:04 再检） |
| gen/snapshot/kline | false |
| pgrep `kline\|export_static\|snapshot\|gen` | 空 |
| MemAvailable | ≈11.9 GiB ≥ 2.5 GiB |
| 禁复用 | 未触 `1c32ab1e` / dry.ok / X2.ok |

## 执行

- ET_TS: `20261025_122704`
- WPID / child: `789424` / `789505`（已退出）
- out_dir: `output/ai_factory/_leaf25_mem_probe_r2/20261025_122704/`（**无** part / meta 产物）
- log_dir: `output/ai_factory/_leaf25_mem_probe_r2/20261025_122704_logs/`
- sampler: `/tmp/quantlab_leaf25_mem_probe_r2_20261025_122704/leaf25_mem_probe_r2_sampler.txt`（`/tmp/quantlab_*` 合规）
- wrapper stdout: `WRAPPER_DONE tag=leaf25_mem_probe_r2 rc=1 stopped=0 peak_kb=208312 C4=PASS`
- exit.txt: `PGREP_G_EMPTY 789505
exit=1 stopped=0 launched=1
peak_kb=208312 sampler=208312 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss=207944 meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)`
- wrapper peak_kb: **208312**（≈203 MB）≪ C4；`C4=PASS`；`stopped=0`
- stage log 末：`hiliq_members_loaded` `ru_maxrss=207944` 后崩溃

## 披露（强制）

| 键 | 值 |
|---|---|
| dry_run | **false**（已 `--allow-real-data`；未写完 real_peak） |
| float32 | n/a（未到 part 写出） |
| densify | **false**（未 densify） |
| claims_full_cfacc | **false** |
| alpha_kind | n/a（未产出 α） |
| peak_kb | **208312**（wrapper sampler） |
| chunk_bounds | 拟 2024-06-03→2024-06-28 · chunk_id=0（未完成） |

## 根因（只读核）

- 异常：`pyarrow.lib.ArrowNotImplementedError: Function 'greater_equal' has no kernel matching input types (timestamp[us], string)`
- 位点：`_read_pit_projected` 对 `end_date` 使用字符串滤子 `YYYYMMDD`，而盘上 PIT 表 `end_date` 类型为 **`timestamp[us]`**
  - 首触：`data/v2/financials_pit/financials_pit_tushare.parquet`（income / `n_income`）
  - 同型：`cashflow_pit_tushare.parquet` / `balancesheet_pit_tushare.parquet` 亦为 `timestamp[us]`
- 脚本注释误写「end_date stored as YYYYMMDD string」与现盘 schema **不符**
- **非** RSS / C4 / QUIET / 窗超时问题；**未**触发 exit 94/95

## 产物

| 路径 | 状态 |
|---|---|
| `output/ai_factory/_leaf25_mem_probe_r2/20261025_122704/` | 空（无 `run_meta.json` / `alpha_parts/`） |
| `output/ai_factory/_leaf25_mem_probe_r2/20261025_122704_logs/leaf25_mem_probe_r2.log` | Traceback 全文 |
| sampler | 仅至 VmHWM≈208312 kB |

## QUIET

- 预检已挂；跑后 **仍挂**；AI **未**自 lift（主/Arch 收尾）

## 请 Arch / 主

1. 消费或 VOID 现盘 `.ok` `cd230f9c…`（`single_use`；本票 FAIL，**禁**再消费同票重跑）
2. 裁定 r3：滤子改为 `timestamp`/`pd.Timestamp`（或先投影后 pandas 滤）——须新 DIFF + 新 `.ok` + 主另排窗；**AI 本票停**
3. 叶27 分块包 `262f9bf6…` 继续排队，不抢本窗（本窗已结束）
4. **勿**把本 FAIL 当 real_peak PASS；X2 仍 blocked

live=false。
