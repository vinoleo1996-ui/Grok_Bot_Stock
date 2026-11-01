# g1g5_ashare_insider_increase_v1 — 研究级 ACCEPT（2026-10-13 ET）

**裁定：ACCEPT（研究级）**；Book-Smoke=PENDING（New Bot→Eng，510300，60万/100万）。
promotion_approved=false · live=false · handoff=NO · 禁 GP · 非主书。

## 1. 文件
预注册 `docs/v2/AI_G1G5_INSIDER_INCREASE_WHO_PAYS_PREREG_ZH.md`；回执 `docs/v2/AI_G1G5_INSIDER_INCREASE_WEIGHT_RECEIPT_ZH.md`；
脚本 `research/g1g5_insider_increase_weights.py`；权重 `output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet`（文件戳为机时 CST）。
探针：预注册称"跑前仅事件计数"。但盘上有 2026-10-12 的 ann_insider 因子 WF 研究（`output/alpha/AI_FACTOR_L1c_ANN_INSIDER_WF_STABILITY_ZH.md`、`AI_FACTOR_L1d_ANN_INSIDER_DEC_DEEPEN_ZH.md`），同一数据族收益已被看过 → 样本外独立性打折（软）。

## 2. 权重独立核验
74,816 行 / 668 日 / 112 名；2024-01-02→2026-10-09；日 Σw≡1；无负权；非 stub；600519/002371=0；
单名 max 0.04；申万一级 max 24%（≤28%）；510300 均 21.0%（20%–44%），全压舱日 0；日均持股 19.75（max 20）。与 AI 声明一致。

## 3. PIT
available_at 为 Asia/Shanghai（如 23:59+08）→ 本地日 D；T1=严格晚于 D 的首个交易日（不吃），T2 入场持 60 日；收益 w(t-1)×r(t)。**无前视，PASS。**

## 4. 逐日 Jaccard（活跃股，全部重叠日，22 包）
≥0.7 占比全 0，无同构硬拒。Top5：
| 包 | max | mean | 日数 |
|---|---|---|---|
| g1g5_nontextbook_daily_weights_20261012_110220.parquet | 0.1765 | 0.0672 | 242 |
| g1g5_nontextbook_daily_weights_20261012_111309.parquet | 0.1765 | 0.0462 | 668 |
| g1g5_nontextbook_daily_weights_20261012_111316.parquet | 0.1765 | 0.0462 | 668 |
| g1g5_accrual_quality_daily_weights_20261013_022400.parquet | 0.1538 | 0.0482 | 668 |
| g1g5_resid_etf_daily_weights_20261013_002418.parquet | 0.1429 | 0.04 | 668 |

capacity_adv max 0.098；moneyflow_resid 0.125；margin_delta 0.125；northbound 0.111；etf_core 0.130；idx_rebal 0.023。
差异：AI 报 max 0.154（accrual），本侧多覆盖 nontextbook 得 0.1765，不影响结论。

## 5. 与 earnings_event 重叠
Jaccard max 0.12 / 均 0.022；260 日有共持，单日最多 3 名，共同名 31 个，日均共同权重 3.1%。两事件叶基本独立。

## 6. 分年（AI 自检，未复权、无成本）
| 年 | α | β | 叶 CAGR | 510300 |
|---|---|---|---|---|
| 2024 | −2.07% | 0.95 | 13.72% | 17.29% |
| 2025 | +2.91% | 0.84 | 18.97% | 18.91% |
| 2026 | +9.52% | 0.70 | 1.76% | −10.50% |
α 高度集中于 2026 下跌段防守，牛市段跑输/持平。预注册未见改动 → 软缺口（偏高）。

## 7. 缺口
- SOFT-HIGH 体制集中（2026 防守贡献主要α）
- SOFT 预注册前有同族 ann_insider 收益研究
- SOFT 政策性增持潮/央国企周期拥挤
- SOFT 未复权价；池锚 2024-06-28 前视；无金额强度；毛 CAGR 12.13% 仅在门下沿、未扣费

## 8. Book-Smoke
PENDING：请 New Bot 派 Eng 跑单叶（60万/100万）+ capacity_adv 主干卫星诊断；门锁仍按现行 CAGR 12%–18%、MDD≤28%。

## 9. Book-Smoke 标注（2026-10-13 Alpha 核验）→ **ACCEPT→BOOK_SMOKE_PASS / RESEARCH_CANDIDATE**
来源：`output/v3/book_smoke_g1g5_insider_increase_x2/`（run `book_smoke_20261014_013316`），同权重文件，成本开，X2 2024-06-03→2026-10-09，C0=510300，sleeve stock=1。Alpha 从 nav.csv 复算一致（CAGR 日历约定差 ≤0.1pp）。

| AUM | CAGR | vsC0 | MDD | Sharpe | cost/AUM | fill | 门 |
|---|---|---|---|---|---|---|---|
| 60万 | 13.14% | +1.87pp | −16.50% | 0.804 | 2.31% | 0.918 | PASS |
| 100万 | 13.14% | +1.87pp | −17.20% | 0.783 | 2.50% | 0.978 | PASS |
any_pass=true；both_aum_pass=true（门：CAGR∈[12%,18%] ∧ MDD≥−28%，两档）。

对比：capacity_adv 60万 13.82%/−10.07%/1.018、100万 12.23%/−11.62%/0.881；earnings_event 13.64%/−18.29%、13.87%/−19.08%、Sharpe≈0.73。本叶 Sharpe 介于两者间，回撤比 capacity_adv 深 ~6pp。
分年（区间收益，vs 510300）：2024残年 +9.56% vs +12.15%（−2.6pp）；2025 +19.82% vs +20.82%（−1.0pp）；2026残年 +1.60% vs −5.34%（+6.9pp）。**超额全部来自 2026 防守**，牛市段跑输——SOFT-HIGH 体制集中缺口确认。
组合 70/30、80/20：均未优于 capacity_adv 主干（60万两档跌出门，MDD 均更深），仅诊断。
注：X2 起点 2024-06-03，消费 570/668 日（权重 2024-01-02 起）。
旗标：promotion_path=null；promotion_approved=false；handoff=NO；live=false；禁 GP；不入主书。
