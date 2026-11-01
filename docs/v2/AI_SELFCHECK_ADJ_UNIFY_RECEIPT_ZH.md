# 自检收益统一接复权 回执（2026-10-13）

红线：未跑 Book-Smoke，未起 8787/uvicorn，未碰封存窗口，未改任何已落盘权重文件，未改信号层，live/promotion=false。

## 改动（全部为新增或仅改自检段）
1. `research/g1g5_x2_panel_stitch.py`：**新增** `load_adj_close_x2(inst)` = X2 原始 close × adj_factor（research/adj_price.py）。`load_panel_features_x2` **未改**，原因：它返回的 open/close/amount 直接喂信号（隔夜跳空、大宗成交额占比等）。
2. `research/ai_debate_memory_runner.py`：**新增** `_load_benchmark_closes_hfq()`，读 etf_daily_adj 的 close_hfq。原 `_load_benchmark_closes` **未改**，原因：它被 27 个文件引用，用于交易日历、`compute_ashare_horizon_returns`（G5 结算）以及部分信号（如 industry_etf_rotation 的 rb），改了就会动信号层。
3. 9 个带自检的 `research/g1g5_*_weights.py`，只改 `def leaf_ret` 及其之后的自检段：block_trade、buyback_cancel、earnings_event、equity_incentive、idx_rebal_predict、industry_etf_rotation、insider_increase、interim_div_init、unlock_rebound。
   - 压舱 `c = bench` → `BENCH_HFQ`（close_hfq）。
   - 个股 `cl[inst]…/load_panel_features_x2(inst)["close"]` → `load_adj_close_x2(inst)`。
   - 回归基准 `bench.pct_change()` → `BENCH_HFQ.pct_change()`。
   - 自检段内残余原始价调用数为 0（脚本统计）。其余 14 个 g1g5_*_weights.py 没有 leaf_ret 自检，未动。

## 未改处（收益同时喂信号层）
- `industry_etf_rotation` 第 42 行用原始 bench 收益算信号（rb），保留；它的 ETF 价格 P 本来就用 close_hfq。
- 各脚本信号段里的 `cl`/`op` 原始面板（跳空、事件窗口）保留。
- `_load_benchmark_closes`、`load_panel_features_x2` 本体保留，理由见上。

## 核对
- 23 个 weights 脚本加 stitch、runner 全部通过 py_compile。
- 冒烟：`_load_benchmark_closes_hfq` 覆盖 2015-01-05→2026-10-09，2024-01→2026-10 年化 12.32%（原始 9.43%）；002594 在 2025-07-29 除权日，复权收益 +0.37%（原始 −66.94%）；`load_panel_features_x2` 输出列不变。
- 未整脚本重跑：整脚本会落新权重并跑全流程，超出本次范围。自检逻辑与 adj_diag_leaves.py 同口径，可交叉印证（叶 1/5/6 结果见 AI_ADJ_PRICE_RECEIPT_ZH.md）。
- 备份：/tmp/stitch.bak、/tmp/runner.bak。
