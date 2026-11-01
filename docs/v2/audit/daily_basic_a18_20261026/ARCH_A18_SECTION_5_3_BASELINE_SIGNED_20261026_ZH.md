# Arch SIGNED：A18 §5.3 引导基线 `.ok`

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T15:13:35-04:00`（墙钟 2026-10-26 15:13 ET） |
| **状态** | **SIGNED** |
| `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.ok` |
| `.ok` sha8 / 全长 | **`a158f17a`** / `a158f17a1be1c89c8475f6712294a21cc0cf9dc2907809118415b8704b39a2ff` |
| 审稿 | `ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md` sha8 **`232a2295`** / 全长 `232a229583ae602520861e2bcad72c3a08aca3d8ce4f103a8636f561cb486dbb` |
| 签窗 | **2026-10-26 15:00–16:00 ET**（not_before=15:00；expires=16:00） |
| QUIET | **未挂**（默认不挂；主令/例程钉不挂 QUIET） |
| live / promotion | false / false |
| ≠ | seed / allow_run / 物化 / enable `4377eb59` / X2 / 叶25 selfcheck / §5.2 盘点 |

## 签前门禁（本签）

| 项 | 结果 |
|---|---|
| 墙钟 ≥15:00 且 <16:00 | **PASS**（2026-10-26 15:13 ET） |
| 审稿 sha 仍 `232a2295` | **PASS** |
| dest pin `f6bbf9e5` / manifest `8c2c978b` | **PASS**（审稿钉；本签未改生产） |
| §5.2 `.ok` `dc51a0b3` / Data 回执 `b21066a1` | **PASS**（prereq） |
| baseline ABSENT | **PASS**（prereq_baseline_absent） |
| 无真实数据进程 | **PASS** |
| 无 `RESEARCH_QUIET.lock` | **PASS**（本签未新建） |
| 勿复用 enable `4377eb59` | **PASS**（forbid_reuse；本票 allow_run/enable=false） |
| 勿动叶25 CONSUMED `3c297052`/`d37a157e` | **未触碰** |
| 错开叶25 16:15–17:45 | **钉入** forbid_overlap_window_et |

## 授权边界（复述）

- allow_ref_build=**true**（真实 raw；输出 `/tmp`；单进程逐年；years=2014..2026；end=20261016）
- allow_write_baseline=**true**（**仅**对账一致时原子写 `build_baseline.json`）
- allow_write_baseline_on_mismatch=**false**（A9）
- allow_read_dest_for_reconcile=**true**
- allow_write_production_parquet / allow_write_manifest / allow_seed_manifest_build / allow_materialize / allow_run / allow_backfill / allow_enable / allow_quarantine_move = **false**
- 命令清单：审稿 §3 / §3.1（钉审稿 sha `232a2295`）
- A13 VmHWM ≤ 1,000,000 kB；超线不得签后续
- 下一手：主 MATCH → 令 Eng 开跑 ref_build（须避开叶25 16:15–17:45；不足则 **17:45 后**）

## 禁区

未挂 QUIET；未盲 seed；未代码 bootstrap；未复用 enable `4377eb59`；未 seed/allow_run/物化；未改 parquet/manifest；未触叶25 CONSUMED；未代跑 ref_build（仅签授权）。≠X2；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 SIGNED）
