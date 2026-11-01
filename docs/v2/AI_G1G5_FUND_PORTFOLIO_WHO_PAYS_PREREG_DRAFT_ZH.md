# 【指针 · 2026-10-27 ~21:59 ET】who_pays 全票草稿已迁至 audit

- **现行全票 DRAFT**：`docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`7cfbb3e5`**
- 冻结全文（勿改前缀条款）：`docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` **`547b246e`**；ALLA **`724e1df5`**
- Arch C1+C2：**`5f7ff5a6` PASS**；C2 RECEIPT **`cb48e5d9`** / JSON **`d6024472`** / events **`81afda13`**
- 主变体 **`dark_horse_add`**；池 **ALLA**；gate_pass=`true`；EXECUTED=false；≠X2 ACCEPT
- 下文保留 2026-10-14 早期 DRAFT 原文（历史对照；池口径已由 ALLA 补充 supersede mid_large 主口径）

---

# 【DRAFT · 未冻结】G1G5 预注册：公募季报持仓边际变化（g1g5_ashare_fund_portfolio_v1，含子变体 dark_horse_add）
起草：2026-10-14 05:57 ET。状态：DRAFT。Data 的 fund_portfolio（tushare_raw/fund_portfolio_dh）未满窗，未读任何收益、也未读持仓计数。研究级；promotion=false；live=false；禁 GP；不碰小盘；不自跑 Book-Smoke。

## 机制与谁付钱
- 主变体 crowd_add：多家主动权益基金同季集中加仓某票，后续同风格基金跟随买入、季报公布后被动跟踪资金补仓。付钱的是季报披露前卖出、且对持仓信息反应慢的资金。
- 子变体 dark_horse_add（黑马边际加仓）：非一致持仓票（上季持有基金数少/持仓市值占流通比低）被少数基金显著加仓。信息含量来自基金经理的独立研究；付钱的是只盯热门抱团票、忽视冷门名字的资金。

## 可检验预测
事件后 T2 起 60 交易日，组合相对 510300 的去 β 残差 α > 0；与 capacity_adv、earnings_event、report_rc_allup、insider_increase 的去 β 残差相关均 <0.5。dark_horse_add 的残差 α 应高于 crowd_add（若相反，说明只是动量/抱团）。

## 数据与 PIT（关键）
- 源：fund_portfolio（ts_code=基金，symbol=股票，end_date、ann_date、mkv、amount、stk_mkv_ratio、stk_float_ratio）。仅主动权益类基金（按 fund_basic 类型过滤；剔除指数/ETF/联接）。
- 季报（Q1/Q3）只披露前十大重仓，约在季末后 15 个交易日内披露；中报/年报披露全部持仓，晚至季末后约 2–3 个月。
- **available_at = 该基金该期 ann_date 次一交易日 09:00**；以基金层逐只 ann_date 为准，不用季末日。截面统计（「多家基金」）只用 available_at ≤ 判定日的基金；判定日固定为季末后第 16 个交易日（Q1/Q3 用前十大口径）。中报/年报全持仓不与前十大混算：只用前十大口径保持各季一致。
- 加仓 = 同基金对同票本期持股数 amount 较上期增加 ≥20%，或新进入前十大。

## 事件定义（冻结前可按计数分布确认阈值，不看收益）
- crowd_add：判定日上，满足「加仓」的不同主动权益基金数 ≥ K（默认 K=10）。
- dark_horse_add：上季持有该票的基金数 ≤ 5（非一致），本季加仓/新进基金数 ≥ 2，且加仓基金合计增持市值 ≥ 该票流通市值 0.1%。
- 入场：判定日 T1，T2 入场，持 60 交易日；同票新事件截断旧窗。
- 池：mid_large PIT top300，排除 600519/002371；每名 4%、≤20 名、SW L1 ≤28%，余额 510300。
- X2 窗口：2024-01-02→2026-10-09（与叶 8–13 同）；封存窗口 2018→2024-05 内只计数、不读价格/收益。

## 计数闸
X2 相关期不同股票 ≥50 只，且 2024–2026 各年事件 ≥25；每季事件高度集中（一季一批），另报每季批次数与「全压舱日」占比；全压舱日 >40% 记为稀疏风险。

## 失败条件（写于读收益前）
1. 任一日 Jaccard vs 任一旧包 ≥0.7 → 同构硬拒（重点核对 capacity_adv、northbound_flow、moneyflow_resid）。
2. 去 β ρ vs capacity_adv / earnings_event / report_rc_allup ≥0.5 → 不过。
3. 残差 α ≤0 → 不过；≥2 个年份残差 α 为负 → WATCH。
4. 组合门（现行）：cap80+叶20，60万/100万两档 CAGR 更高且 MDD 不更深，否则 WATCH；同时报 A/B 门（docs/v2/AI_LEAF_SELFCHECK_V2_RECEIPT_ZH.md）。
5. 成本门：自检 v2 判不可交易 → 不过；衰减门 DECAY_DOWNGRADE → 不过。
6. peak RSS >1.5GB 或 G6 不过 → 不过。
主/子变体只选一个送 ACCEPT：按「先 dark_horse_add、后 crowd_add」的优先级，第一个过计数闸者为主变体（写于计数前）。

## 冻结前待办
Data 满窗回执（基金类型过滤口径、ann_date 完整率、前十大/全持仓标记）；计数分年；冻结。
