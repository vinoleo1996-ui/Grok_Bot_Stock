# 【FROZEN 2026-10-13 20:24:32 ET】G1G5 叶9：中期分红首次实施/大幅提升预案（g1g5_ashare_interim_div_init_v1）
研究级；promotion_approved=false；live=false；禁 GP；不自跑 Book-Smoke。授权：Leo 12:51 ET 连续开叶。冻结时间由盒子 CST 时钟减 12 小时得到；冻结前只做了事件计数，未读任何收益。

## 来源
- Michaely, Thaler & Womack (1995, Journal of Finance)「Price reactions to dividend initiations and omissions」：美股分红首发后存在正向漂移（海外经典，A 股需复现）。
- A 股 2002–2004 样本（https://www.1mishu.com/lunwen/jjgl/jjbylw/201004/684152.html ）：股利增加组 CAR 显著为正，首次发放组超常收益最高。
- 反面：http://www.abslw.com/29/abs1627529.html 指出年报与分红预案同日披露，信号效应难以干净识别；创业板研究（https://www.lunwendata.com/thesis/2015/48337.html ）长期漂移不显著。
- 制度背景：2024-04 新国九条推动一年多次分红；2025 年中期 810 家、300 余家首次（证券时报统计）。

## 谁付钱
公司首次推出中期现金分红（或较上年同期大幅提高）是管理层对现金流可持续性的承诺信号，并吸引险资等红利型配置资金在其后逐步买入；付钱的是对这一信号反应迟缓、按旧派息预期定价的卖方。

## 可检验预测
预案公告后 T2 起 60 个交易日，入选股相对 510300 的去 β 残差为正；与 capacity_adv、earnings_event 的去 β 残差相关均 <0.5。

## 数据与 PIT
data/v2/corporate_actions/dividend_tushare.parquet（ann_date 1991→2026-10-10，满窗）。只用 div_proc=「预案」行，available_at = ann_date 当日盘后 → T2 入场。

## 规则（冻结，不调）
- 事件：end_date 非 12-31（中期/季度分红）的「预案」，cash_div_tax>0，且（上年同期无现金分红，或本次每股派现 ≥ 上年同期 ×1.3）。同票同 end_date 取最早预案。
- 入场 T2，持有 60 个交易日；同票新事件重置窗口。
- 池：mid_large PIT top300，T2 当日须在 PIT 成员内；硬排除 600519/002371。每名 4%，≤20 名，SW L1 ≤28%，余额 510300。
- 窗口 2024-01-02→2026-10-09；事件读取从 2023-10 起。

## 计数（只看计数，冻结前）
池内 255 条 / 178 只（2023Q4:4 / 2024:110 / 2025:99 / 2026:42），其中首次中期分红 212 条。

## 失败条件（看收益前写定）
1) 不同股票 <40 或压舱均值 >85% → 计数闸失败；2) 逐日 Jaccard 任一日 max≥0.7 → 同构硬拒；3) 去 β 残差相关 vs capacity_adv ≥0.5 或 vs earnings_event ≥0.5 → 不正交；4) 残差 α ≤0 → FAIL；5) 分年残差 α 两年以上为负 → 最多 WATCH；6) peak RSS >1.5GB 或 G6 不过 → 不交。

## 与已有/已灭各包的区别
| 包 | 区别 |
|---|---|
| V33 STOCK-DIV-IMP（reject） | V33 是分红**实施公告**入日后 10 日短窗的机械性公司行动；本叶是**预案**里「首次/大幅提升中期分红」的信号，入场早于实施，持有 60 日，且只看中期分红变化，不看实施 |
| earnings_event | 不用业绩预告/快报和隔夜跳空；须报残差相关，≥0.5 即失败 |
| insider_increase / buyback / equity_incentive | 不是内部人或公司买股，是现金分配承诺 |
| 常驻股息率因子（教科书） | 不按股息率高低排序，只用派息**变化**事件 |
| 其余（capacity/margin/northbound/OCF/accrual/negevent/moneyflow/idx_rebal/block_trade/unlock_rebound/已否方向） | 无共同输入 |
