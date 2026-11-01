# Eng｜Core X2 脚手架回执（研究级；live=false；strategy_promotion=false；X2 漂亮数不得晋级）

范围：只做脚手架；Core 权重由 Strategy 生成（`core_{sleeve}_{60,100}w.parquet`），Eng 未生成权重、未写 core_* 文件、未启动求解器。纸面轨未动。

## 1) 三列记分卡
- 脚本：`scripts_eng/core_x2_scorecard.py` → `output/strategy_optimizer/core_x2/scorecard_three_col.{csv,md}`
- A=`core_x2/book_smoke_<sleeve>_<60|100>w/nav.csv`（缺则 PENDING）；B=`output/v3/book_smoke_g1g5_capacity_adv_x2`；C=`output/strategy_hiliq/capadv_x2`（只读）
- 口径：主=equity80_etf20_510300；B/C 原生 NAV 已含约 20% 510300（B 均值 21.2%，C 20.0%），标为 native；equity_100 由原生 NAV 按每日 510300 实际占比剥离推得（标 derived，近似，含现金）。基准=同引擎 C0（510300 买入持有）。quantlab.metrics 244；MDD 对 25%/15% 双线标记。
- 密封窗：B/C 无密封 book-smoke（book 模块按 PREREG 拒跑 SEALED），标 N/A。
- 验证（X2，主口径②）：

| AUM | 列 | CAGR | MDD | Calmar | Sharpe | IR | 日胜 | 月胜 | >25% | >15% |
|---|---|---|---|---|---|---|---|---|---|---|
| 60万 | B | 13.8% | -10.1% | 1.37 | 1.02 | 0.13 | 52.7% | 50.0% | 否 | 否 |
| 60万 | C | -0.6% | -29.9% | -0.02 | 0.09 | -0.75 | 49.7% | 53.6% | 是 | 是 |
| 100万 | B | 12.2% | -11.6% | 1.05 | 0.88 | 0.00 | 53.6% | 57.1% | 否 | 否 |
| 100万 | C | 1.7% | -33.0% | 0.05 | 0.20 | -0.46 | 50.1% | 50.0% | 是 | 是 |

峰值 RSS 158MB。

## 2) Book-Smoke strategy_v1 入口
- `scripts_eng/core_x2_book_smoke.py`（包 `quantlab.portfolio.book_smoke`：next_open、sqrt 冲击 k=1、参与率 10%、整手含科创 200、涨跌停、未成交结转）；仅 X2。
```
python3 scripts_eng/core_x2_book_smoke.py --weights output/strategy_optimizer/core_x2/core_equity80_etf20_510300_60w.parquet --aum 600000 --sleeve equity80_etf20_510300
python3 scripts_eng/core_x2_book_smoke.py --weights output/strategy_optimizer/core_x2/core_equity80_etf20_510300_100w.parquet --aum 1000000 --sleeve equity80_etf20_510300
```
（equity_100 同理换 `--sleeve equity_100` 与文件名。）输出 `core_x2/book_smoke_<sleeve>_<60|100>w/nav.csv`。
- 试跑：C 的 HI_LIQ 权重 @60万 → `core_x2/_dryrun_capadv_hiliq_60w/`，CAGR -0.58% / MDD -29.93%，与 C 原产物一致；12s；峰值 RSS 655MB。
