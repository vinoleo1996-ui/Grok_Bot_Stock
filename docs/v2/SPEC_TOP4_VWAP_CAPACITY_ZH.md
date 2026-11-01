# 规格 Top4：VWAP 撮合敏感性 + 60万/100万分档容量检查（2026-10-14）

来源：ARCH_REVIEW_20261014_ZH.md 第 4 项。约束：live=false；禁 GP、禁小盘；**不改引擎默认，不改主干 capacity_adv**；只新增脚本和输出；不虚构数据。

## 1. 目标
1. 量化 B4、S6、capacity_adv 三条轨道在不同成交价假设下的指标敏感性：close（现行）、日内 VWAP 代理、对开盘价不利滑点。
2. 按 60万/100万两档检查每笔成交占当日成交额的比例，标出容量风险。

## 2. 输入（仓库真实路径）
- 行情：`data/v2/bars/daily_ohlcv_raw_pit.parquet`（字段含 open/high/low/close/volume/amount/adj_factor/limit_up/limit_down/tradestatus）。日 VWAP 代理 = amount/volume，单位换算以 `volume_unit`/`amount_unit` 为准，须先核对。
- 复权：`data/v2/adj/adj_factor_2023h2plus.parquet`；日历：`data/v2/calendar/trade_cal_sse_pit.parquet`
- 成本模型（只读引用）：`quantlab/portfolio/v2_execution_costs.py`（佣金/印花/滑点 bps）
- 权重：`output/strategy_paper_b4/FROZEN_CONFIG.json` 指向的 B4 60w/100w parquet；capacity_adv 见 `output/loop/capacity_adv_FROZEN_CONFIG.json`；S6 shadow 权重来源按 `quantlab/portfolio/scorecard.py` 中的路径表读取
- 基线指标：`output/loop/scorecard_latest.{md,json}`

## 3. 接口/CLI 草案（新增文件，不改现有 cli 子命令行为）
新增 `research/top4_exec_sensitivity.py`，独立运行：
```
PYTHONPATH=. /workspace/qlvenv/bin/python research/top4_exec_sensitivity.py \
  --tracks capacity_adv,b4,s6 --aum 600000,1000000 \
  --fill close,vwap_proxy,open_adverse --slip-bps 0,10,20 \
  --part-cap 0.01,0.05 --out output/top4_exec/<YYYYMMDD>
```
- `fill_price` 只在本脚本内重算 NAV（参考 vnpy 4.5 的 fill_price/vwap 撮合）；不写回引擎，也不改 Mandate 默认值。
- 容量：participation = |Δw|·AUM / amount_当日。超过 part-cap 的部分按「当日未成交、顺延到下一日」处理；涨跌停或停牌（limit_up/limit_down/tradestatus）当日不可成交。

## 4. 实验矩阵
3 条轨道 × 2 档 AUM × 3 种成交价 × 3 档滑点（0/10/20 bps）× 2 档参与率上限（1%/5%）= 108 组，只跑 X2 段。基线格 close+0bps+无上限须与记分卡对得上，作为一致性校验。

## 5. 产物
- `output/top4_exec/<date>/metrics.parquet`：每格 CAGR/MDD/Calmar/月胜率/日胜率/成本占 AUM
- `output/top4_exec/<date>/capacity_flags.parquet`：逐笔参与率、被顺延的成交、涨跌停阻塞
- `output/top4_exec/<date>/REPORT_ZH.md` + `run_manifest.json`（输入 sha256、参数、RSS、耗时）

## 6. 验收标准
1. **一致性**：基线格（close、0 bps、无上限）与 scorecard_latest 的 X2 值偏差 ≤0.05pp，两档都要满足。参照值：capacity_adv 60万 13.82/−10.07/1.37/月胜 52，100万 12.23/−11.62/1.05/59；B4 60万 15.11/−13.85/1.09/62，100万 14.24/−13.17/1.08/55；S6 60万 17.15/−11.95/1.43/62，100万 16.37/−12.66/1.29/59。
2. **稳健判定**（只给结论，不晋级）：vwap_proxy+10bps 加 5% 参与率上限下，某轨道 CAGR 降幅 ≤1.5pp、MDD 恶化 ≤1pp、Calmar 仍 ≥ 同档 capacity_adv 基线，记为「执行稳健」；否则记为「执行敏感」。
3. **容量**：100万档参与率超过 1% 的成交笔数占比，以及被顺延成交占比，必须如实列出。
4. 进程单进程，RSS ≤2GB；live=false、promotion_approved=false 写入 manifest。

## 7. 分工与工作量（共约 3–4 人日）
- Eng（2 人日）：脚本、撮合与容量逻辑、一致性校验
- Strategy（1 人日）：解读矩阵，写 REPORT_ZH 结论
- Web（0.5 人日）：看板读取 metrics.parquet 展示
- AI（0.5 人日）：复核 S6/B4 权重来源和价格口径

## 8. 风险
- 日 VWAP 只是 amount/volume 的代理，不是真实日内撮合（无盘中数据，见 Eng 回执缺口 3），只能当作上界或下界的参考。
- amount/volume 单位必须先核对，否则 VWAP 会差一个量级。
- 若基线一致性校验不过，说明权重或成本口径没对齐，须先停下排查。
- 结论只用于研究，不得据此改主干或改引擎默认。
