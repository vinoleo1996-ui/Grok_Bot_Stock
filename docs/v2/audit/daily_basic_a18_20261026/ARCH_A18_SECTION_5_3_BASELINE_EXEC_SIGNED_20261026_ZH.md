# Arch SIGNED：A18 §5.3 引导基线 **EXEC** `.ok`

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T15:18:59-04:00`（墙钟 2026-10-26 15:18 ET） |
| **状态** | **SIGNED**（执行授权；not_before=17:45） |
| `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` |
| `.ok` sha8 / 全长 | **`6de02e74`** / `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca` |
| 审稿 | `ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md` sha8 **`232a2295`** / 全长 `232a229583ae602520861e2bcad72c3a08aca3d8ce4f103a8636f561cb486dbb` |
| 废止旧票 | sha8 **`a158f17a`** → `output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.a158f17a.SUPERSEDED.20261026T151859ET.ok`；SUPERSEDED 回执 sha8 **`6c5abfec`** |
| 签窗 | **2026-10-26 17:45–23:00 ET**（not_before=17:45；expires=23:00） |
| QUIET | **未挂**（默认不挂） |
| live / promotion | false / false |
| ≠ | seed / allow_run / 物化 / enable `4377eb59` / X2 / 叶25 CONSUMED / 盲 seed / 代码 bootstrap |

## 签前门禁（本签）

| 项 | 结果 |
|---|---|
| 审稿 sha 仍 `232a2295` | **PASS** |
| dest pin `f6bbf9e5`（size=745129744；审稿/§5.2 钉） / manifest `8c2c978b` | **PASS**（manifest 复算 MATCH；has_build=false；本签未改生产） |
| §5.2 `.ok` `dc51a0b3` / Data 回执 `b21066a1` | **PASS**（prereq） |
| baseline ABSENT | **PASS** |
| 无真实数据进程 | **PASS**（pgrep 空） |
| 无 `RESEARCH_QUIET.lock` | **PASS**（本签未新建） |
| 旧票 `a158f17a` SUPERSEDED | **PASS**（live 路径 gone） |
| 勿复用 enable `4377eb59` | **PASS** |
| 勿动叶25 CONSUMED `3c297052`/`d37a157e` | **未触碰** |
| 错开叶25 16:15–17:45 | **钉入** forbid_overlap；执行窗自 **17:45** 起 |

## 授权边界（复述；同审稿 §3）

- allow_ref_build=**true**（真实 raw；输出 `/tmp`；单进程逐年；years=2014..2026；end=20261016）
- allow_write_baseline=**true**（**仅**对账一致时原子写 `build_baseline.json`）
- allow_write_baseline_on_mismatch=**false**（A9）
- allow_read_dest_for_reconcile=**true**
- allow_write_production_parquet / allow_write_manifest / allow_seed_manifest_build / allow_materialize / allow_run / allow_backfill / allow_enable / allow_quarantine_move = **false**
- forbid_reuse_ok_sha8=`4377eb59`；supersedes_ok_sha256=`a158f17a…`
- 命令清单：审稿 §3 / §3.1（钉审稿 sha `232a2295`）
- A13 VmHWM ≤ 1,000,000 kB
- **未代跑** ref_build；**未挂 QUIET**

## 请主

1. MATCH 本 EXEC `.ok` sha8 **`6de02e74`** + 本回执
2. 令 Eng ≥**17:45 ET** 开跑（仍避 16:15–17:45；本窗至 23:00）
3. Eng 仍 HOLD 至 MATCH

≠X2；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 EXEC SIGNED）
