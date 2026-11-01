# Eng 回执：Arch P1-K5 归档 + v1.3 book_smoke 入口加固 + 宽/严可行率（2026-10-18 ET）

- **归档**：4 个 v1.2 `book_smoke_{equity_100,equity80_etf20_510300}_{60,100}w/` 已原样 mv 至 `core_x2/_archive_v1_2/`，`MANIFEST.json` 记 52 个文件 sha256/字节数。
- **入口**：`scripts_eng/core_x2_book_smoke.py` 无显式 `--out`/`--version` 拒跑；`--version` 缺省 v1_3 → `core_x2/book_smoke_{version}_{sleeve}_{aum}w/`；非空目录无 `--overwrite` 拒写；`run_meta.json` 记权重 sha256/行数/日期区间。**v1.3 未跑**，ARCH_RESIGN_A_v1_3.ok **未建**。
- **记分卡**：v1.2【HARD 违约账本】改读 `_archive_v1_2/`；A_v1_3 读 `book_smoke_v1_3_*`，门控 ARCH_RESIGN_A_v1_3.ok，现为 PENDING。v1.2 业绩数值未变。
- **可行率（v1.3，按档去重，分母含 2018-01-02 NO_DATA）**：宽口径（现金>2%仅预警）SEALED 60万 87.2%/100万 89.7%，X2 两档 89.7%；严格口径（现金>2%=不可行）SEALED 47.4%/29.5%，X2 17.2%/13.8%。旧回执 87.0%/89.6% 为 77 日分母笔误。Arch「36–53%」为逐行不去重 status==OK 占比，按档去重的严格值更低。脚本 `scripts_eng/core_c5_rereport.py`→`c5_feasibility_v1_3.csv`、`c5_rereport_v1_3_loose_strict.txt`。
- **Web**：`apis.py` 的 `book_smoke_*/nav.csv` glob 现匹配 0 个（v1.2 已归档）；v1.3 跑后匹配 `book_smoke_v1_3_*`，键名带 `v1_3_` 前缀；`core_v1_2_disclosure.csv` 已在 `_archive_v1_2/`，Web 需改读该路径或 `core_v1_3_disclosure.csv`。
- **持仓导出**：`scripts_eng/export_holdings_by_track_aum.py` → `output/loop/paper_daily_20261014/bridge_X2H/holdings_by_track_aum.parquet`（只读纸面文件；BOOK nav 与纸面 NAV 逐档一致）。shares 无法从桥接产物推出，置空。
- 纸面/FROZEN/STATUS 未动；live/promotion=false。

## 补记：K2/K6 记分卡口径（2026-10-18 00:08 ET）

- **K2**：`scripts_eng/core_c5_rereport.py` / `core_x2_scorecard.py` 现同时报 HARD-only（官方：仅风格/β/行业/整手 HARD 失败；现金>2%只披露）与严格口径（现金>2%=失败）、整手后现金分布（p5/p50/p95/max、>2%占比）、现金拖累（年化 pp；无 `ARCH_RESIGN_A_v1_3.ok` 时为 PENDING，Eng 未建该标记）。
- **K6**：预 K6 权重 sha256 写入 `core_x2/_void_pre_K6_sha.json`；命中则记分卡标注「作废版本（K6 前），待 Strategy 重跑」。Strategy 已将当前批次移至 `_archive_v1_3_pre_ruling/`；C5/记分卡回退读取该目录做作废版证明跑。
- **作废版 HARD-only 参考**：SEALED 60万 87.2% / 100万 89.7%；X2 两档 89.7%。严格口径仍为 SEALED 47.4%/29.5%、X2 17.2%/13.8%。未跑 book_smoke；纸面未动；live=false。
