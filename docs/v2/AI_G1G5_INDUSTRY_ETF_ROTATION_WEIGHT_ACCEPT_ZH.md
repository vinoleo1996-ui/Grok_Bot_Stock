# 研究级裁定 · g1g5_ashare_industry_etf_rotation_v1 → **REJECT**

- 权重：`output/ai_factory/g1g5_industry_etf_rotation_daily_weights_20261014_011706.parquet`
- 核验（本侧独立）：{"rows": 26052, "dates": 668, "names": 39, "range": "2024-01-02→2026-10-09", "sum_w": 1.0, "neg": 0, "max_single_etf": 0.2, "b600519_002371": 0, "ballast_mean": 0.554, "ballast_min": 0.4}
- PIT：入场 T2（available_at 后首个交易日确认、次日入场）/信号 d-1→权重 d；脚本抽查未见前视
- Jaccard（逐日，对盘上全部先验包）：{"max": 0.143, "vs": "etf_core_sleeve", "frac_ge_0_7": 0.0}
- AI 自报（未复算，无成本）：{"cagr": 0.0825, "c0_cagr": 0.0945, "mdd": -0.2062, "c0_mdd": -0.1625, "alpha": -0.0064, "beta": 0.999, "alpha_by_year": {"2024": -0.1168, "2025": 0.1216, "2026": -0.0442}, "annual_turnover_x": 14.6}

## 裁定理由
硬闸过，但扣费前即跑输 510300（CAGR −1.2pp，MDD 深 4.4pp），残差α<0、β≈1，分年极不稳；年化单边换手≈14.6 倍，扣费后更差。无烟价值，REJECT（非 WATCH：经济上无可观察的正面）。

## 缺口
- 代表 ETF 关键词映射
- 510300 基准可能未计分红（偏向叶）
- 无折溢价/冲击模型

Book-Smoke：NOT_DISPATCHED；promotion_approved=false；live=false；handoff=NO；禁 GP / 主书 / Strategy。
