# Alpha 裁定：g1g5_ashare_stk_surv_gap1y_v1（叶13，机构调研断档 ≥1 年后再调研）
**结论：RESEARCH_ACCEPT（硬闸过）→ WATCH；book_smoke = NOT_DISPATCHED。** promotion_approved=false；live=false；handoff=NO；禁 GP。日期 2026-10-14。

- 权重：output/ai_factory/g1g5_stk_surv_daily_weights_20261014_172311.parquet，sha256 bfdf369b…a499（已核一致）；42,084 行 / 668 日 / 63 名。
- 预注册：AI_G1G5_STK_SURV_WHO_PAYS_PREREG_ZH.md，FROZEN 05:22:55 ET；权重落盘 05:23:20 ET → 预注册先于权重。如实记录：主变体选取规则写于看过计数之后、读收益之前（AI 已自报）；原草稿事件为 V3「滚动10日≥20家」，冻结时按指令优先级改为 V1。
- 复核口径：复权价（research/adj_price.py；510300 close_hfq）；毛收益 + 净收益（17.5bp/单位双边换手）。脚本 output/alpha/verify_stk_surv_20261014.py，输出 verify_stk_surv_20261014_raw.json。窗口 2024-01-03→2026-10-09（667 日）。

## 1. 硬闸（全过）
Σw≡1；无负权/重复/NaN/缺日；单名 max 4%；600519/002371 恒 0；510300 压舱均 77.0%（20%–96%，无全压舱日）。逐日 Jaccard vs 38 个前包 max 0.30（block_trade），vs earnings_event 0.083、capacity_adv 0.077。PIT：68 次入场全部有前置事件，最近事件可得日距入场最少 2 个交易日，0 违规（available_at = surv_date+25 交易日，T2 入场）。G6 pass、peak RSS 999MB 为 AI 自报。

## 2. 自报数复核（一致）
| 口径 | CAGR | MDD | 备注 |
|---|---|---|---|
| 叶13 毛 | 12.05% | −17.47% | β 0.94，Sharpe 0.71 |
| 叶13 净（17.5bp） | 11.30% | −17.68% | 双边换手 1.5%/日 |
| 510300 | 12.34% | −16.25% | |
| capacity_adv 毛 / 净 | 17.66% / 16.37% | −13.18% / −13.55% | |
残差 α +0.51%/年（2024 **−3.09**｜2025 +0.08｜2026 +0.41）。**扣成本后跑输 510300。**

## 3. 相关与重叠
去 β 残差 ρ：capacity_adv 0.396、insider 0.354、equity_incentive 0.357、analyst_recoverage 0.251、report_rc_allup 0.117、earnings_event −0.028（均 <0.5）。但 2026 年 vs capacity_adv 升到 **0.617**，vs equity_incentive 0.503。入场落在 earnings_event 40 日窗内 1/68；被 report_rc_allup 持有 1/68。

## 4. 组合门（现行/门A/门B 均不过）
本地简单混合（毛）：cap 17.66%/−13.18%；90/10 17.13%/−13.61%；80/20 16.58%/−14.04%；70/30 16.04%/−14.47% → CAGR 与 MDD 都劣于主干。净口径同向。AI conc v2 读数（60万 80/20 15.16%/−13.84% vs 14.96%/−13.63%；100万 19.25%/−12.47% vs 18.85%/−12.25%）CAGR 略好但 MDD 两档都更深 → 不过。门A/门B 见 ALPHA_GATE_AB_REJUDGE_20261014_ZH.md（三门均不过）。

## 5. 弱样本外
盘上未发现冻结前对 stk_surv 做过收益研究；但 V1 口径取自中金 2025-07 公开研究，其样本与 X2 窗口重叠 → 弱样本外。池锚 2024-06-28 静态 top300，2024H1 有轻微前视。

## 6. 裁定
硬闸、PIT、预注册时序都过，研究级 ACCEPT；但残差 α 近零且 2024 为负、扣费后跑输 510300、压舱 77%、组合门不过 → **WATCH，不派 Book-Smoke**。
