# 叶15 tp_rerate（卖方目标价集中上调）X2 回执（2026-10-14 06:36 ET）
派单：主 Agent 2026-10-14 06:32 ET。预注册 docs/v2/AI_G1G5_TP_RERATE_WHO_PAYS_PREREG_ZH.md（FROZEN 2026-10-14 06:33:06 ET，冻结前未读收益）。研究级；promotion_approved=false；live=false；未跑 Book-Smoke；未动冻结脚本。

## 结论：WATCH（不送 ACCEPT 作新叶）
- 硬闸（同源）：ρ_excess（去β残差）vs report_rc_allup 0.323、earnings_event 0.167、analyst_recoverage 0.187，均 <0.5 → 不属强度过滤，可作独立叶；逐日 Jaccard max 0.25（report_rc_allup），无同构。
- 判定 (a) 主干级：不满足。单叶净 CAGR 11.14%（毛 11.98%）< capacity_adv 单独，且低于 510300 基准 12.34%；MDD −16.95%。
- 判定 (b)：ρ_excess vs capacity_adv 0.016 <0.5 ✓；但 cap80+leaf20 净 CAGR 60万 14.34% vs 14.42%（−0.08pp），100万 17.82% vs 18.41%（−0.58pp），两档都不赢 → 不满足。
- Gate A（ρ<0.5 且残差 α>0）：形式上过（α +0.04%/年，接近 0，分年 2024 −2.00%/2025 +3.18%/2026 −2.18%）。Gate B（两档组合赢主干）：FAIL。
- GATE_V3：MDD≤25% 两档 ✓、≤15% 两档 ✓；CAGR 高于 capacity_adv 两档 ✗；衰减门 v1.1 DECAY_DOWNGRADE ✗；可交易 ✓ → FAIL。
- CMC vs B4：ΔIC −0.0007、ΔICIR −0.025、ρ vs B0 −0.017；ΔCAGR 净 60万 −0.81pp、100万 −1.70pp → 不过。

## 关键数字
- 事件：全样本 515 条/197 只；窗口候选 157 条，反转过滤剔除 81 条（52%），入场 76 条（2024:37/2025:20/2026:19）。日均 6.6 名，压舱 73.5%。
- 换手双边 1.72%/日；成本 17.5bp → 拖累 0.76%/年；毛超额 −0.37% → 不判不可交易（成本未超 1%/年），但无超额。
- 因子（20 日）：IC 0.014，RankIC −0.018，ICIR −0.114，Q5−Q1 −0.57%。lookahead 三截点 PASS。
- 年化天数：主报 252；244 口径对照：单叶净 10.76%，capacity_adv 60万 13.93%/100万 17.77%。结论不变。
- 【07:3x ET 更正】按 Eng quantlab/metrics.py，主报改为 244（即上行的 244 数字），252 只作对照；见 AI_ANNUALIZATION_244_NOTE_ZH.md。结论不变（WATCH）。
- 峰值 RSS 958MB（≤1.5GB）。

## 口径更正与已知问题
- report_rc 的 tp 字段是利润总额而不是目标价，因此目标价改用 max_price/min_price 的均值。冻结前已写入预注册，需要主 Agent 和 Alpha 知悉。
- 反转过滤剔除了一半事件，说明目标价上调大多跟在上涨之后；保留事件的 α≈0。
- 机构名未归一，“家数”可能被同一券商的不同名称虚增。

## 产物
- 事件脚本 research/g1g5_tp_rerate_events.py sha bdefa2d7…34ca8（冻结时登记）
- 权重脚本 research/g1g5_tp_rerate_weights.py sha 103633e4…e1b5
- 权重 output/ai_factory/g1g5_tp_rerate_daily_weights_20261014_183329.parquet sha e80d5b27…ff1d；meta g1g5_tp_rerate_run_meta_20261014_183329.json
- output/ai_factory/leaf_reports/tp_rerate/{selfcheck_v2.json,selfcheck_v3.json,decay_v1_1.json,lookahead_check.json,hypothesis_critique.md}
- output/top5_factor_report/20261014/summary.json 已追加 tp_rerate

## 补记：机构名归一后计数复核（2026-10-14 06:52 ET，仅计数，不改权重/结论/定义，未读收益）
- 归一：去空格、全半角括号统一，去后缀「证券股份有限公司/有限公司/研究所/证券/公司」，别名（中金公司=中金、申万宏源研究=申万宏源、财富证券=财信证券、东亚前海证券研究所=东亚前海、高盛两种写法合一）；机构 162→154。
- 原事件存活：全样本 515/515、窗口 157/157、入场 76/76 全部仍 ≥3 家不同机构 → 「≥3 家」未被同名虚增。归一重跑多出 1 条（516/158，2026 年 +1；因别名合并后上一条目标价链变化），不采用。
- 敏感性（再把合并券商视为一家：国泰君安+海通→国泰海通、国联+民生→国联民生）：存活 510/515、154/157、74/76。
- 结论维持 WATCH。脚本 research/g1g5_tp_rerate_org_recount.py（sha 481f71d6…43f2）；结果 output/ai_factory/leaf_reports/tp_rerate/org_norm_recount.json（sha fcf6f706…f3ca）；峰值 RSS 631MB。
