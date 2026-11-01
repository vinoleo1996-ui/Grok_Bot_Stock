# AI 年化口径更正说明（2026-10-14 ~07:10 ET）
依据 docs/v2/ENG_METRICS_UNIFY_RECEIPT_ZH.md（quantlab/metrics.py，PERIODS=244）：
- 自即日起 AI 报告中，**CAGR/Sharpe 年化主报 244，252 仅作对照**。
- 以下已冻结预注册写的是“主报 252 / 244 对照”。为避免改变冻结 sha，原文不动，以本说明为准：AI_G1G5_TP_RERATE_WHO_PAYS_PREREG_ZH.md（§4）、AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md（7.）、AI_G1G5_BROKER_GOLD_NEW_WHO_PAYS_PREREG_ZH.md（7.），以及非冻结回执 AI_G1G5_TP_RERATE_WEIGHT_RECEIPT_ZH.md（已加更正行）。“两口径结论不一致记 WATCH”这条规则保留。叶15 的结论在两种口径下相同（WATCH）。
- 非冻结脚本已改为 244：research/alpha_combo_marginal.py（CAGR）、research/leaf_selfcheck_v3.py（CAGR、Sharpe）。改前备份在 output/loop/_metrics_unify/*.bak_pre_metrics_ai。衰减门的 252 日窗口和 α×252 按预注册保持不变。IC 的 rolling-252 窗口不属于年化，也不改。
- 07:3x ET 补充：全 A 补充预注册（AI_G1G5_FUND_PORTFOLIO/BROKER_GOLD_NEW_ALLA_SUPPLEMENT_PREREG_ZH.md）直接写明主报 244、252 对照。
