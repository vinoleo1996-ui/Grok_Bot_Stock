# 【FROZEN 2026-10-14 07:25:11 ET】全 A 口径补充预注册：g1g5_ashare_broker_gold_new_v1_allA
原冻结预注册：docs/v2/AI_G1G5_BROKER_GOLD_NEW_WHO_PAYS_PREREG_ZH.md（冻结于 2026-10-14 06:51:36 ET，sha256 b880813b2da22db6cd07ff3ed7ead38bd1ad03dfc923566189681f5918675a68，即追加计数附录之前的版本）。本文只换股票池，不改原文。

## 全 A 股票池（Leo 2026-10-14 07:24 ET 指令；PIT）
- 实现：research/all_a_universe_mask.py（非冻结辅助，冻结时 sha256 6ab6a305cb91db9a89c17a8db005d967679cfe4585a7fecad361e902a3daa114）；判定日 S 开盘决策，只用 S 之前的数据（停牌公告除外，开盘前已披露）。
- 基础：沪深 A 股（SSE+SZSE），按 tushare_raw/daily 逐日文件构造（含后来退市的票，无幸存者偏差）。北交所剔除，与 MID_LARGE_RULE.md 一致（另需投资者权限、涨跌幅 30%）。
- 剔除 ST/*ST：S 落在 data/v2/st_events/st_events_from_namechange.parquet 中名称含 ST 的区间内。
- 剔除停牌：tushare_raw/suspend_d 在 S 日 suspend_type=S，或 S−1 无成交。
- 剔除次新：list_date（stock_basic L/D/P）到 S−1 不足 60 个交易日。
- ADV（100万档可交易）：ADV20 = S−20…S−1 共 20 个交易日成交额均值（停牌/缺失记 0，偏保守；单位元）。条件与 capacity_adv 一致：NAME_CAP 4% × AUM 100万 ≤ k × ADV20，k=0.02（ADV_PARTICIPATION_K）→ ADV20 ≥ 200 万元。
- 名单规模（示例）：2024-01-04 4945 只、2025-06-04 4917 只、2026-10-14 4993 只。ADV 门几乎不约束（≤2 只被剔），实际上本池 ≈ 全部非 ST 沪深 A 股，**包含小盘**——这与“禁小盘”红线存在冲突，已报主 Agent 定夺；在其拍板前，本补充只做计数，不读收益。
- 数据缺口：st_flags/is_st_daily 只到 10-09，所以 ST 用 namechange 区间；namechange 的更新延迟没有单独校验。stock_basic 是当前快照，list_date 不随时间变化，影响可以忽略。suspend_d 覆盖 2018-01-02→2026-10-14。
- 其余全部不变：沿用原冻结预注册的机制、事件定义、阈值、计数闸、硬闸 1–6/8、仓位（每名 4%、≤20 名、SW L1 ≤28%、余额 510300、排除 600519/002371）。只把“池：mid_large PIT top300”换成上面的全 A 池。
- 年化：主报 244（quantlab/metrics.py），252 对照；两种口径结论不一致记 WATCH（取代原文第 7 条的 252 主报）。
- promotion=false；live=false；禁 GP/高杠杆；不自跑 Book-Smoke；冻结前未读任何价格或收益。

## 计数口径（两版共用，计数前写死；属对原文的解释，不改原文）
- 券商名归一：去首尾空格、全角转半角；不做并购合并。
- 新进 = 该券商本月名单有、上月名单无；若该券商上月**没有任何名单**，本月不计新进（保守）。
- 事件月 M 的 T2 = M 月第 3 个交易日；X2 相关期 = T2 落在 2024-01-02→2026-10-09 的月份。
- 池：事件票在 T2 时须在池内（mid_large = available_at≤T2 09:00 的最新 top300 月度名单；全 A = universe_mask(T2)），且不是 600519/002371。
- 计数闸按原文：不同股票 ≥50 只，且月均事件 ≥5。

## 冻结
FROZEN 2026-10-14 07:25:11 ET（box 2026-10-14 19:25:11 +08）。冻结之后只追加计数附录。

## 计数附录
- 2026-10-14 07:25:27 ET（AI）：只计数，未读价格或收益。数据 tushare_raw/broker_recommend 201801–202610（Data prefill ok=58）；口径见 AI_G1G5_BROKER_GOLD_NEW_ALLA_SUPPLEMENT_PREREG_ZH.md「计数口径」。脚本 research/broker_gold_new_count.py（sha 5c48e27334ed），结果 output/ai_factory/broker_gold_new_count_20261014.json（sha 784fc457acc4）。
- X2 相关期 33 个月（202401–202609）；入池前原始事件 315 个。
- 全 A 池：事件 314 个，不同股票 183 只，月均 9.52 个；分年 2024=136、2025=80、2026(1–9 月)=98；2 个月为 0 事件。每月池规模 4910–4992 只。
- 计数闸（不同股票 ≥50 且月均 ≥5）：**PASS**。提示：事件集中在 7 月和 12 月等月份，月度分布不均。

## 追加说明（2026-10-14 07:27 ET，AI；不改上文冻结条款）
- Leo 07:24 ET 取消“禁小盘”：好股票即使是小盘也可买；股票池为全 A，只剔除不可交易票（ST、停牌、上市不满 60 日、100万档 ADV 不可交易）。GP、高杠杆仍禁止。
- 因此上文“包含小盘——与禁小盘红线冲突、拍板前只计数”的提示已解除：**全 A 池（research/all_a_universe_mask.py）为主口径**，mid_large top300 为对照口径；小盘贡献仅披露，不作判定。其余条款（定义、阈值、计数闸、硬闸、仓位）不变。
- 主 Agent 07:27 ET 批准进入 X2。
