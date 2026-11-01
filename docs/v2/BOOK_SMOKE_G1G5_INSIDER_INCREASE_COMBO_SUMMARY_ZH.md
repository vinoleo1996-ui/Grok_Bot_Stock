# Book-Smoke：insider_increase 单叶 + capacity_adv 主干组合诊断（X2）

窗口 X2（2024-06-03→2026-10-09），成本开启，sleeves core=0/stock=1，C0=纯 510300。数字全部取自各 book_smoke_summary.json。

| 臂 | AUM | CAGR | vs C0 | MDD | Sharpe | cost/AUM | Alpha门 |
|---|---|---|---|---|---|---|---|
| 单叶 insider_increase | 60万 | 13.14% | +1.87 pp | -16.50% | 0.804 | 2.31% | PASS |
| 单叶 insider_increase | 100万 | 13.14% | +1.87 pp | -17.20% | 0.783 | 2.50% | PASS |
| 主干 capacity_adv | 60万 | 13.82% | +2.56 pp | -10.07% | 1.018 | 1.72% | PASS |
| 主干 capacity_adv | 100万 | 12.23% | +0.97 pp | -11.62% | 0.881 | 1.71% | PASS |
| 组合 70/30 | 60万 | 11.68% | +0.41 pp | -10.68% | 0.928 | 1.91% | FAIL |
| 组合 70/30 | 100万 | 13.18% | +1.91 pp | -12.67% | 0.947 | 1.93% | PASS |
| 组合 80/20 | 60万 | 11.38% | +0.11 pp | -10.46% | 0.916 | 1.92% | FAIL |
| 组合 80/20 | 100万 | 13.30% | +2.04 pp | -11.22% | 0.963 | 1.97% | PASS |

Alpha 门：CAGR∈[12%,18%] ∧ MDD≥−28%。

## 单叶门控
- 单叶 60万：PASS（CAGR=13.14%，MDD=-16.50%）
- 单叶 100万：PASS（CAGR=13.14%，MDD=-17.20%）

## 组合判定（诊断用，非晋级）
共同 session 668；日线性合成后按日归一（Σw=1）；权重 `output/ai_factory/g1g5_combo_capadv_insinc_{70_30,80_20}_daily_weights.parquet`。
- 组合 70/30：未优于主干（600000: CAGR ↓ MDD 深；1000000: CAGR ↑ MDD 深）
- 组合 80/20：未优于主干（600000: CAGR ↓ MDD 深；1000000: CAGR ↑ MDD 浅）

## 旗标
- strategy_promotion_approved=false；所有 promotion 旗标=false
- handoff=NO；live=false；不下单；未修改 capacity_adv 纸面轨
- research_candidate 未自封；禁 GP；未启 uvicorn

## 分年收益（X2 日历年；简单区间收益，非年化）

算法：年末 NAV 链式相除 —— 2024 = NAV(2024-12-31)/NAV(2024-06-03)−1；2025 = NAV(2025-12-31)/NAV(2024-12-31)−1；2026 = NAV(2026-10-09)/NAV(2025-12-31)−1。
2024 / 2026 为残年（X2 窗起止）；2025 为整年。数据一律取自各 out dir 的 `nav.csv`；缺失则标明。

| 臂 | AUM | 2024 partial<br>06-03→12-31 (143d) | 2025 full<br>12-31→12-31 (243d) | 2026 partial<br>12-31→10-09 (183d) | 全窗累计 |
|---|---|---|---|---|---|
| 单叶 insider_increase | 60万 | +9.56% | +19.82% | +1.60% | +33.37% |
| 单叶 insider_increase | 100万 | +9.96% | +19.75% | +1.27% | +33.35% |
| 主干 capacity_adv | 60万 | +15.02% | +17.56% | +0.03% | +35.25% |
| 主干 capacity_adv | 100万 | +12.66% | +17.08% | -0.77% | +30.88% |
| 组合 70/30 | 60万 | +10.91% | +16.00% | +0.55% | +29.37% |
| 组合 70/30 | 100万 | +12.56% | +18.27% | +0.26% | +33.46% |
| 组合 80/20 | 60万 | +11.13% | +15.71% | -0.01% | +28.57% |
| 组合 80/20 | 100万 | +12.43% | +18.27% | +0.63% | +33.81% |
| C0 (510300) | 60万 | +12.15% | +20.82% | -5.34% | +28.27% |
| C0 (510300) | 100万 | +12.15% | +20.83% | -5.34% | +28.27% |

相对 C0 超额（pp，同 AUM）：

| 臂 | AUM | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| 单叶 insider_increase | 60万 | -2.59 | -1.01 | +6.94 |
| 单叶 insider_increase | 100万 | -2.19 | -1.08 | +6.61 |
| 主干 capacity_adv | 60万 | +2.87 | -3.27 | +5.37 |
| 主干 capacity_adv | 100万 | +0.51 | -3.75 | +4.57 |
| 组合 70/30 | 60万 | -1.24 | -4.82 | +5.89 |
| 组合 70/30 | 100万 | +0.40 | -2.56 | +5.60 |
| 组合 80/20 | 60万 | -1.02 | -5.11 | +5.33 |
| 组合 80/20 | 100万 | +0.28 | -2.55 | +5.97 |

## 路径
- 单叶权重：`output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet`
- 组合权重：`output/ai_factory/g1g5_combo_capadv_insinc_70_30_daily_weights.parquet`、`..._80_20_...`
- 单叶烟：`output/v3/book_smoke_g1g5_insider_increase_x2/` · 回执 `docs/v2/BOOK_SMOKE_G1G5_INSIDER_INCREASE_X2_RECEIPT_ZH.md`
- 主干烟（已有）：`output/v3/book_smoke_g1g5_capacity_adv_x2/`
- 70/30：`output/v3/book_smoke_g1g5_combo_capadv_insinc_70_30_x2/` · 回执 `docs/v2/BOOK_SMOKE_G1G5_COMBO_CAPADV_INSINC_70_30_X2_RECEIPT_ZH.md`
- 80/20：`output/v3/book_smoke_g1g5_combo_capadv_insinc_80_20_x2/` · 回执 `docs/v2/BOOK_SMOKE_G1G5_COMBO_CAPADV_INSINC_80_20_X2_RECEIPT_ZH.md`
- 本摘要：`docs/v2/BOOK_SMOKE_G1G5_INSIDER_INCREASE_COMBO_SUMMARY_ZH.md`
- NAV 缺失：无
