# 规格 Top5：旧叶统一复权重算 + 标准因子分析报告 + trusted 开关（2026-10-14）

来源：ARCH_REVIEW_20261014_ZH.md 第 5 项。约束：live=false；禁 GP、禁小盘；不改主干 capacity_adv；**不改既有叶的裁定**（重算结果只作为附表）；不虚构数据。

## 1. 目标
1. 把 AI_LEAF_LEDGER_ZH.md 中标为「未复权」或「两者都有」的叶，统一用复权口径重算自检指标：叶 2 capacity_adv_negevent、3 buyback_cancel、4 industry_etf_rotation、idx_rebal_predict、1/5/6、7 block_trade、8 unlock_rebound、9 interim_div_init。
2. 为每个叶输出标准因子分析：IC/RankIC、分层收益、换手、逐年残差 α、压舱率。
3. 新增研究 artifact 加载的 trusted 开关（参考 qlib 0.9.8）。

## 2. 输入（仓库真实路径）
- 叶脚本：`research/g1g5_*_weights.py`（例如 g1g5_buyback_cancel_weights.py、g1g5_block_trade_weights.py、g1g5_unlock_rebound_weights.py、g1g5_interim_div_init_weights.py、g1g5_industry_etf_rotation_weights.py、g1g5_idx_rebal_predict_weights.py、g1g5_capacity_adv_negevent_weights.py、g1g5_earnings_event_weights.py、g1g5_insider_increase_weights.py、g1g5_equity_incentive_weights.py）
- 复权：`research/adj_price.py`、`data/v2/adj/adj_factor_2023h2plus.parquet`；行情：`data/v2/bars/daily_ohlcv_raw_pit.parquet`
- 既有复权诊断：`research/adj_diag_leaves.py`、`docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md`、`docs/v2/AI_SELFCHECK_ADJ_UNIFY_RECEIPT_ZH.md`
- 台账与标签：`docs/v2/AI_LEAF_LEDGER_ZH.md`、`output/loop/leaf_status_index.parquet`、`output/loop/alpha_labels.json`

## 3. 接口/CLI 草案（全部新增）
```
PYTHONPATH=. /workspace/qlvenv/bin/python research/top5_adj_recompute.py --leaves all_legacy --out output/top5_adj/<date>
PYTHONPATH=. /workspace/qlvenv/bin/python research/top5_factor_report.py --leaves <list|all> --horizons 1,5,20 --quantiles 5 --out output/top5_factor_report/<date>
```
- 因子报告用自研实现（polars/pandas），避免 alphalens 在 Python 3.12 下的兼容问题；alphalens-reloaded 可选，只读比对。
- trusted 开关：新增 `research/artifact_guard.py`，提供 `load_artifact(path, trusted=False)`。只有 trusted=True 且文件 sha256 在 `output/loop/trusted_artifacts.json` 白名单里，才允许 pickle/可执行加载；parquet/json 数据读取不受影响。先在 top5 脚本里使用，不回改主干。

## 4. 实验矩阵
约 10 个叶 × 口径（未复权、复权）× 指标（毛 CAGR/MDD、残差 α 及逐年值、压舱率、ρ vs capacity_adv）；因子报告为叶 × 持有期 1/5/20 日 × 5 分位。组合层只对 research ACCEPT 的叶（1/5/6），在 60万/100万两档用 Book-Smoke 复核。

## 5. 产物
- `output/top5_adj/<date>/leaf_adj_recompute.parquet` + `LEAF_ADJ_APPENDIX_ZH.md`（新旧口径对照，作为台账附表）
- `output/top5_factor_report/<date>/<leaf>/{ic.parquet, quantile_ret.parquet, turnover.parquet, REPORT_ZH.md}`
- `output/loop/trusted_artifacts.json`、`run_manifest.json`

## 6. 验收标准
1. **可复现**：AI_ADJ_PRICE_RECEIPT_ZH.md 里已有复权诊断的叶（3/7/8/9、1/5/6），重算值与回执偏差 ≤0.05pp；例如叶 9 复权毛 CAGR 12.91%/MDD −14.94%、残差 α +1.60%。
2. **组合层 Smoke 一致**（60万/100万）：earnings_event 13.64/−18.29、13.87/−19.08；insider_increase 13.14/−16.50、13.14/−17.20；equity_incentive 14.31/−14.80、15.18/−15.58（CAGR/MDD），Calmar 和月胜率与 scorecard_latest 一致（例如 earnings_event 0.75/55、0.73/52）。偏差 ≤0.05pp，否则须说明原因。
3. **裁定不变**：重算后结论如有变化，只在附表标「口径变化待 Alpha 复核」，不改原表。
4. **trusted 测试**：未在白名单的 pickle 被拒绝（单测），数据读取通过。
5. 单进程 RSS ≤2GB；live=false。

## 7. 分工与工作量（共约 2–4 人日）
- AI（1.5 人日）：复权重算与附表
- Eng（1 人日）：因子报告模块、artifact_guard、单测
- Web（0.5 人日）：看板展示 IC/分层图
- Strategy（0.5 人日）：组合层 Smoke 复核

## 8. 风险
- `adj_factor_2023h2plus` 只覆盖 2023 下半年以后，更早样本无法复权，须在附表中标明覆盖区间。
- 重算可能改变 WATCH/FAIL 叶的观感，引发重开旧叶；此项须经 Alpha 和 Leo 批准，不得自动晋级。
- 叶脚本里的路径/口径参数各不相同，不能一刀切。
- trusted 白名单如果维护不当，会阻塞既有流程，所以只在新脚本中启用。
