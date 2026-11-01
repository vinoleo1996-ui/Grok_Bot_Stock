# 【FROZEN 2026-10-14 05:58:36 ET】G1G5 预注册：保险机构集中调研（g1g5_ashare_insurer_surv_v1）
写于读任何收益之前；写完即冻结（盒子 CST −12h）。研究级；promotion=false；live=false；禁 GP；不碰小盘；不自跑 Book-Smoke。授权：主 Agent 批准开叶 14（来源 docs/v2/AI_NEXT_LEAF_CANDIDATES_ZH.md）。
**如实说明**：候选筛选时已看过粗计数（旧口径仅 保险资管+寿险：全窗 280 条/85 只，X2 156 条/66 只）；未看任何收益。本预注册的分类口径略宽（见下），计数会有差异。

## 机制与谁付钱
保险资金负债久期长、配置型、换手低。同日多家保险机构集中调研，预示其后续配置型建仓（保险建仓慢、持续数月）。付钱的是建仓窗口内的短线卖方与对保险配置需求反应迟缓的资金。

## 可检验预测
事件后 T2 起 60 交易日，组合相对 510300 的去 β 残差 α > 0；在中和红利与大盘风格后（见下）残差 α 仍 > 0；与 stk_surv、capacity_adv、earnings_event、report_rc_allup 的去 β 残差相关 < 0.5。

## 数据与 PIT
- 源：data/v2/events/stk_surv_2018plus.parquet（395,691 行）。池内记录实际自 2021 起。
- **available_at = surv_date + 25 个交易日 09:00**（Data p95 披露滞后 L=25）；T1 = available_at 当日，T2 入场。

## 机构类型分类规则（写死）
org_type ∈ {寿险公司, 保险资产管理公司, 综合保险公司, 再保险公司, 保险集团控股公司} 计为保险机构；保险经纪公司、保险代理公司不计（中介、非资金方）；org_type 缺失或「--」不计（不用机构名猜测）。同日同票按 rece_org 去重计数。

## 事件
- 同一 surv_date 同一票，保险机构不同 rece_org 数 ≥3。
- 持有 60 交易日；同票新事件截断旧窗。
- 池 mid_large PIT top300（锚 2024-06-28），排除 600519/002371；每名 4%、≤20 名、SW L1 ≤28%，余额 510300。信号不用价格。
- X2 权重 2024-01-02→2026-10-09，事件读取自 2023-10。

## 与 stk_surv（叶13）去重（写死）
- 若本叶事件的 surv_date 与同票任一 stk_surv V1（断档≥1年再调研）事件的 surv_date 相差 ≤30 自然日，**剔除该事件**；回执报告剔除数与占比。
- 硬规则：去 β 残差 ρ vs stk_surv ≥0.5 → 直接 WATCH。

## 红利/大盘暴露中和（写死，自检层）
- 叶日收益对 [510300, 510880−510300, 510050−510300]（均 close_hfq）做 OLS（全窗），报截距年化 α_style。
- **α_style ≤ 0 → WATCH**（说明收益来自红利/大盘风格）。权重层不做中和（保持信号不用价格）。

## 失败条件（读收益前写死）
1. 任一日 Jaccard vs 任一旧包 ≥0.7 → 同构硬拒。
2. ρ vs stk_surv ≥0.5 → WATCH；ρ vs capacity_adv / earnings_event / report_rc_allup ≥0.5 → 不过。
3. 去 β 残差 α ≤0 → 不过；α_style ≤0 → WATCH；≥2 个年份残差 α 为负 → WATCH。
4. 组合门：现行（cap80+叶20，60万/100万两档 CAGR 更高且 MDD 不更深）不过 → WATCH；同时报 A（去 β 后叠加，两档 CAGR∧MDD）、B（原样叠加，两档 Calmar 更高且 MDD ≥−15%），按 docs/v2/AI_LEAF_SELFCHECK_V2_RECEIPT_ZH.md 口径。
5. 自检 v2：衰减门 DECAY_DOWNGRADE → 不过；成本门判不可交易 → 不过。
6. peak RSS >1.5GB 或 G6 不过 → 不过。
送 Alpha ACCEPT 的条件：1–6 全部不触发。
