# 【FROZEN 2026-10-14 06:51:36 ET · 计数待数据】G1G5 预注册：券商月度金股新进（g1g5_ashare_broker_gold_new_v1）
起草：2026-10-14 05:57 ET。状态：FROZEN（2026-10-14 06:51:36 ET，草稿 05:57 ET）。盘上**无**券商金股数据（需 Data 拉 tushare broker_recommend 满窗，月度）；未读任何收益。研究级；promotion=false；live=false；禁 GP；不碰小盘；不自跑 Book-Smoke。

## 机制与谁付钱
券商每月发布金股组合；新进入（上月不在该券商金股中）的名字代表卖方新增推荐，经销售渠道传导给客户与机构，月初形成集中买盘。付钱的是不跟踪卖方月度推荐、月初被动卖出的资金。多家券商同月新进 = 共识新推荐，强度更高。

## 可检验预测
新进金股（≥2 家券商同月新进）在 T2 起持有至当月末（约 20 交易日）相对 510300 的去 β 残差 α > 0；与 report_rc_allup（卖方上调）、analyst_recoverage、earnings_event 的去 β 残差相关 <0.5。

## 数据与 PIT
- 源：broker_recommend（month、broker、ts_code、name）。
- 金股一般在月末最后几个交易日至次月第一个交易日发布；接口按月份给出，无精确发布时刻。**保守：available_at = 该月第 1 个交易日收盘后（即 T1 = 第 2 个交易日开盘）**，入场 T2 = 第 3 个交易日。
- 新进 = 该券商本月有、上月无；券商名需归一（同一券商简称/全称）。

## 事件定义
- 事件：同月 ≥2 家券商新进该票（阈值已冻结）。
- 持有至当月最后一个交易日（约 18–20 日）；下月若再被新进，视为新事件。
- 池：mid_large PIT top300，排除 600519/002371；每名 4%、≤20 名、SW L1 ≤28%，余额 510300。
- X2：2024-01-02→2026-10-09；封存窗口内只计数。

## 同构风险（事前写死）
与 report_rc_allup 同为卖方信号：逐日 Jaccard 任一日 ≥0.7 → 硬拒；ρ vs report_rc_allup ≥0.5 → 只登记为其变体，不算新叶。

## 计数闸
X2 相关期不同股票 ≥50 只，月均事件 ≥5（年 ≥60）。

## 失败条件
同 fund_portfolio 草稿第 1–6 条（Jaccard 硬拒、ρ<0.5、α>0 且负年 ≤1、组合门现行两档 CAGR∧MDD、成本门/衰减门、RSS/G6）。月度全换仓，换手偏高，须特别看成本门。

## 数据待办（冻结后，仅计数）
Data 拉 broker_recommend 满窗并回执（券商名归一、发布日分布）；计数分年；冻结。

## 冻结补充（2026-10-14 06:51:36 ET 冻结；冻结前未读任何价格/收益；盘上无该数据，计数待数据，未伪造）
- 状态：FROZEN（定义/阈值/计数闸/硬闸已写死）。事件计数 = **PENDING_DATA**：Data 满窗回执后只做 PIT 计数并追加到本文件末尾「计数附录」，不得改动以上任何条款；计数闸不过即停，不读收益。
- 草稿里「阈值冻结前可按计数分布确认」一句作废：阈值即为本文默认值，计数后不调。
- 硬闸（读收益前写死）：
  1. 逐日 Jaccard vs capacity_adv、B4、report_rc_allup、earnings_event、insider_increase、analyst_recoverage、tp_rerate 任一日 ≥0.7 → 同构硬拒。
  2. ρ_excess（去行业/市值/β 残差）vs 上述任一 >0.5 → 只作强度过滤，不开主叶。
  3. 自检 v2：扣成本净收益（0.00175/单位换手）+ T+1 开盘成交 + 滚动 β；双边换手 >20%/日或成本拖累 > 毛超额一半（无超额时 >1%/年）→ 不可交易。
  4. 衰减门 v1.1（Alpha，停牌修复版）非 KEEP → 不过。
  5. Gate A（ρ<0.5 且残差 α>0）、Gate B（cap80+叶20 在 60万/100万两档净 CAGR 均高于 capacity_adv 单独）并行报。
  6. GATE_V3：MDD≤25% 下最大化 CAGR，两档 CAGR 高于 capacity_adv 单独 + 衰减门 KEEP + 可交易；另报 MDD≤15% 变体。终判以 Eng Book-Smoke X2 为准（AI 不自跑）。
  7. 年化天数：主报 252，并列 244 对照；两口径结论不一致记 WATCH。
  8. 峰值 RSS ≤1.5GB；promotion=false；live=false；禁 GP/小盘/高杠杆。

## 计数附录
- 2026-10-14 07:25:27 ET（AI）：只计数，未读价格或收益。数据 tushare_raw/broker_recommend 201801–202610（Data prefill ok=58）；口径见 AI_G1G5_BROKER_GOLD_NEW_ALLA_SUPPLEMENT_PREREG_ZH.md「计数口径」。脚本 research/broker_gold_new_count.py（sha 5c48e27334ed），结果 output/ai_factory/broker_gold_new_count_20261014.json（sha 784fc457acc4）。
- X2 相关期 33 个月（202401–202609）；入池前原始事件 315 个。
- mid_large top300：事件 221 个，不同股票 108 只，月均 6.70 个；分年 2024=95、2025=58、2026(1–9 月)=68；3 个月为 0 事件。
- 计数闸（不同股票 ≥50 且月均 ≥5）：**PASS**。提示：事件集中在 7 月和 12 月等月份，月度分布不均。
