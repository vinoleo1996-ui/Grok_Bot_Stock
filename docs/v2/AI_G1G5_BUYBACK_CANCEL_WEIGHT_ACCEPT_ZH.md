# 研究级裁定 · g1g5_ashare_buyback_cancel_v1 → **WATCH**

- 权重：`output/ai_factory/g1g5_buyback_cancel_daily_weights_20261014_010405.parquet`
- 核验（本侧独立）：{"rows": 28724, "dates": 668, "names": 43, "range": "2024-01-02→2026-10-09", "sum_w": 1.0, "neg": 0, "maxw": 0.04, "b600519_002371": 0, "ballast_mean": 0.8205, "ballast_min": 0.6}
- PIT：入场 T2（available_at 后首个交易日确认、次日入场）/信号 d-1→权重 d；脚本抽查未见前视
- Jaccard（逐日，对盘上全部先验包）：{"max": 0.2, "vs": "earnings_event", "frac_ge_0_7": 0.0}
- AI 自报（未复算，无成本）：{"cagr": 0.0967, "c0_cagr": 0.0945, "excess": 0.001, "mdd": -0.1518, "alpha": 0.0058, "beta": 0.956, "alpha_by_year": {"2024": 0.0316, "2025": -0.0068, "2026": -0.027}, "rho_excess_vs_capacity_adv": 0.213}

## 裁定理由
硬闸过、PIT T2 入场；但 82% 压舱的 510300 克隆，α +0.58% 且 2025/2026 转负（衰减），扣费前超额仅 +0.10%/年，扣费后大概率 ≤0。不派烟，留 WATCH（事件机制本身合理，待有回购金额字段/更长样本再议）。

## 缺口
- 无回购金额
- 池锚定 2024-06-28（2024H1 前视）
- 未复权价
- 脚本 docstring 残留 earnings_event 模板描述（代码逻辑为回购事件，文档需修）

Book-Smoke：NOT_DISPATCHED；promotion_approved=false；live=false；handoff=NO；禁 GP / 主书 / Strategy。
