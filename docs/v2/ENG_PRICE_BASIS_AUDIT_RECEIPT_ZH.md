# Eng 价格口径审计回执（PRICE_BASIS）——只读核查，未重跑回测

时间：2026-10-13 ET。检查对象：capacity_adv、earnings_event、insider_increase、集中化三腿 B4，含 Book-Smoke 与 X2 主干。未改 STATUS/live/promotion；峰值 RSS 约 515MB。

## 结论
**Book-Smoke 与 X2 主干引擎的 NAV 是含分红/除权的总收益口径，不受未复权问题影响。受影响的是 AI/Alpha 的叶自检脚本（未复权 close 算收益），系统性低估收益。**

## (a) 引擎取价
- 调用链：cli book-smoke → quantlab/portfolio/book_smoke.py → v2_multisleeve_book.run_book（L488）。股票不在 Data.HFQ 中，走 platform/execution.py `load_execution_panels(..., corporate_actions=True)`（L494-495，L1194）。
- 成交与盯市都用**未复权原始 OHLC**（docstring L1214：“All trading/valuation uses RAW prices”）：股票取 merged/asof_extend 面板的 open/close，ETF 取 data/v2/etf/etf_daily_adj.parquet 的 close/open（不用 close_hfq）。fill=next_open（strategy_v1，L343-349）。
- 收益由显式公司行为补回：ExecConfig.corporate_actions=True（L330）。

## (b) 分红与送转
- 数据：股票为 data/v2/corporate_actions/dividend_by_exdate_tushare.parquet（cash_div_tax 税前，stk_div 送转比，L1568-1578）；基金为 etf_daily_adj.adj_factor + etf/raw/fund_div.parquet（L1514）。
- 处理（L825-840）：除权日开盘前，现金分红 = 股数×每股派现×(1−dividend_tax，默认 0)，**计入现金，不自动再投资**，下次调仓再部署，闲置期按 cash_rate 计息；送转按 (1+share_ratio) 增加股数。没有事件数据时，用 adj_factor 跳变比例作为股数乘数兜底（L537-557）；事件与因子偏差 >1% 时以因子为准。
- 实证（capacity_adv 60万 BOOK，比较前一日实际权重算出的收益与 NAV）：

| 事件 | NAV 日收益 | Σw·未复权收益 | Σw·含息收益 |
|---|---|---|---|
| 601088 2024-07-08 派 2.26 | −0.265% | −0.379% | −0.266% |
| 601088 2025-07-07 派 2.26 | −0.324% | −0.498% | −0.373% |
| 000333 2025-06-12 派 3.5 | +0.040% | −0.204% | −0.055% |

  NAV 贴近含息口径，无假跌（剩余差为当日成交/冲击）。送转路径有代码（SR），本次未找到持仓内大送转样本做实证。

## (c) C0（510300）
含分红：C0 在 2025-06-18 与 2026-01-19 除息日的 NAV 收益为 +0.073% / +0.044%，与 close_hfq 一致（未复权 close 为 −2.13% / −2.49%）。X2 全窗口 C0 累计 +28.27%，close_hfq 为 +28.25%，未复权 close 仅 +22.25%。

## (d) 叶自检脚本：**未复权**
- research/g1g5_x2_panel_stitch.py L21-26 `load_panel_features_x2` 只返回 open/close 原价（无 adj_factor）。
- research/g1g5_earnings_event_weights.py L95-99、L216-233，以及 research/g1g5_insider_increase_weights.py L96-100、约 L258：叶收益 = w.shift(1)×close.pct_change()，基准 = `_load_benchmark_closes`。
- research/ai_debate_memory_runner.py L719-743 `_load_benchmark_closes`：510300 读 etf_daily_adj 的**原始 close**，不是 close_hfq。
- research/g1g5_capacity_adv_weights.py L551 与 research/g1g5_wiring.py L149/L685：同样用原价 close（vol20 等信号也是原价）。
- output/alpha/verify_equity_incentive_20261013.py L38-52：Alpha 复核与 AI 同口径（所以“全部吻合”）。
- research/small_aum_concentration_v2.py / small_aum_conc_lib.py L39：原价只用于计算一手金额，这一用途用原价是正确的。

## 偏差方向与量级（基于权重×(含息−未复权)日收益差的算术年化估算）
| 叶 | 合计 pp/年 | 其中个股 | 其中 510300 |
|---|---|---|---|
| capacity_adv | 4.77 | 4.23 | 0.54 |
| earnings_event | 2.56 | 0.75 | 1.82 |
| insider_increase | 2.97 | 2.57 | 0.41 |
| 集中化 B4 60万 | 3.99 | 3.13 | 0.86 |
| 集中化 B4 100万 | 4.05 | 3.23 | 0.82 |
- 方向：未复权口径低估叶毛收益；510300 基准同样低估（约 2.3pp/年 CAGR，X2 上 9.45% 对 11.3%），因此残差 α 的偏差取决于个股股息率减 β×基准股息率。高股息叶（capacity_adv 偏大盘高息）低估最多。
- 原价信号（动量/波动）在除息日会出现假跳，属于选股层面的轻微噪声；权重一经引擎执行，NAV 仍为总收益口径。

## 受影响文档
- **不受影响**：所有 docs/v2/BOOK_SMOKE_*（含 G1G5_*、CONC_V2*、EQUITY_INCENTIVE 等）与 output/strategy_three_leg/compare_table.json 的数字（引擎口径）。
- **受影响（自检毛收益/α/分年 α 偏低）**：docs/v2/AI_G1G5_*_WEIGHT_RECEIPT_ZH.md、AI_G1G5_*_WEIGHT_ACCEPT_ZH.md 中的“close-to-close、无成本、未复权”自报与复核数字（例：AI_G1G5_EQUITY_INCENTIVE_WEIGHT_ACCEPT_ZH.md §3），以及各叶 WHO_PAYS/ATTRIBUTION 文档中基于同一脚本的 β/α 数字。
- 建议：为自检补一个复权取价函数（close×adj_factor 或直接调用引擎的 total_return_factor），本回执不改代码。
