# AI FULLA_V1 五腿重生成回执

- 时间：2026-10-14 ~07:46 ET（箱钟）
- 请求方：QuantLab Strategy（FULLA_V1 掩码已冻结）
- 约束：不改 FROZEN_CONFIG / 纸面轨；live=false；promotion=false；不自跑 Book-Smoke
- 变更仅候选池：`research/*_weights_fulla_v1.py`（原脚本未动）+ `research/fulla_v1_universe.py`（sha `ffa79a323d79c48f3e22c16d5df9d6ca2e21c7735d9599151724abd9e02eec63`）
- 叶11 report_rc 事件：`research/g1g5_report_rc_allup_events_fulla.py`（sha `55a0daec6afff69f81fac24bac4c9d132ae444176ba150dd85910634c3e31bf2`）向量化，与慢版定义一致（80 名样本 equal=True）
- 隔夜跳空：bulk tushare daily OHLC（与 load_panel_features_x2 的 open/close 一致），缓存 `_work/gap_panel_fulla_v1.parquet`
- 权重窗口文件内 2024-01-02→2026-10-09；X2 报告切片 2024-06-03→2026-10-09（570 日）
- 掩码 sha：`b5d9f1abd34bc550dd18a3eb2617a7d417cc60d29fbb02dceee02024e19fc7cd`

## 五腿产物

| 腿 | 路径 | sha256 前缀 | rows | X2日均持股 | sum_w |
|---|---|---|---|---|---|
| earnings_event | `output/strategy_fulla/legs/g1g5_earnings_event_fulla_v1_daily_weights_20261014_194511.parquet` | `707c2a126f8b…` | 454908 | 16.50 | 1.0–1.0 OK |
| insider_increase | `output/strategy_fulla/legs/g1g5_insider_increase_fulla_v1_daily_weights_20261014_194511.parquet` | `8bc1828a1f94…` | 387440 | 20.00 | 1.0–1.0 OK |
| equity_incentive | `output/strategy_fulla/legs/g1g5_equity_incentive_fulla_v1_daily_weights_20261014_194511.parquet` | `4ac63f920806…` | 260520 | 20.00 | 1.0–1.0 OK |
| report_rc_allup | `output/strategy_fulla/legs/g1g5_report_rc_allup_fulla_v1_daily_weights_20261014_194511.parquet` | `ec51bd59c00e…` | 177688 | 15.96 | 1.0–1.0 OK |
| insurer_surv | `output/strategy_fulla/legs/g1g5_insurer_surv_fulla_v1_daily_weights_20261014_194511.parquet` | `12fb3e6d7d88…` | 368068 | 19.99 | 1.0–1.0 OK |

各腿均附 `.parquet.check.json`（含 script/mask sha、无负权、sum_w=1）。

## 掩码对比 FULLA_V1 vs research/all_a_universe_mask.py

窗口 2024-06-03→2026-10-09（570 日）：
- 日均在池：FULLA 4958.9 / 我方 all_a 4959.5
- 日差（FULLA−ours）：mean -0.575，min -8，max 0
- Jaccard mean 0.999884（min 0.998384）
- 差异原因：FULLA ADV 门槛 300 万元（NAME_CAP 6%），我方辅助脚本 200 万元（NAME_CAP 4%）；FULLA 为 Strategy 冻结口径，本批腿一律用 FULLA_V1。
- 明细：`output/strategy_fulla/legs/mask_compare_fulla_v1_vs_all_a.csv`

## 备注
- 并行生成时 peak RSS 曾超 1.5GB（report_rc 向量化合并约 3.3GB；其余约 1.6–2.0GB）。weights-only 路径跳过自检/衰减门/ledger，仅交 Strategy 合成用。
- capacity_adv FULLA 腿此前由 Alpha 交付，不在本次五腿内。
