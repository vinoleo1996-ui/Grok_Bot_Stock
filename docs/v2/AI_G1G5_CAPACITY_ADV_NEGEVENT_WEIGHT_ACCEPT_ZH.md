# 研究级裁定 · g1g5_ashare_capacity_adv_negevent_v1 → **DONE_FAIL**

- 权重：`output/ai_factory/g1g5_capacity_adv_negevent_daily_weights_20261014_010218.parquet`
- 核验（本侧独立）：{"rows": 32732, "dates": 668, "names": 49, "range": "2024-01-02→2026-10-09", "sum_w": "1±1e-15", "neg": 0, "maxw": 0.04, "b600519_002371": 0, "ballast_mean": 0.2158, "ballast_min": 0.2}
- PIT：入场 T2（available_at 后首个交易日确认、次日入场）/信号 d-1→权重 d；脚本抽查未见前视
- Jaccard（逐日，对盘上全部先验包）：{"capacity_adv": {"max": 1.0, "mean": 0.994, "frac_ge_0_7": 1.0}, "combo_capadv_earnevt": {"max": 1.0, "mean": 0.781}, "others_max": 0.577}
- AI 自报（未复算，无成本）：{"cagr": 0.1168, "parent_cagr": 0.1207, "mdd": -0.1389, "alpha": 0.047, "parent_alpha": 0.0506, "turnover_delta": "+6.9%", "pruned_excess_mean": 0.0227, "n_windows": 13}

## 裁定理由
主干剪枝变体：与 capacity_adv 逐日 Jaccard≥0.7 占比 100%（形式上同构硬闸不过）；被剪窗口超额 +2.27%，剪掉的是右尾；CAGR/α/MDD 全劣于主干；预注册 §4.3 派烟条件 3 项仅换手过。不重调参。

## 缺口
- 负事件仅 13 窗口，样本极小
- 高质押无满窗 PIT

Book-Smoke：NOT_DISPATCHED；promotion_approved=false；live=false；handoff=NO；禁 GP / 主书 / Strategy。
