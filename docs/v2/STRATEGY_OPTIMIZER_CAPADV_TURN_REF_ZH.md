# capacity_adv 密封窗换手参考（Eng λ_turn）

- **时间**：2026-10-14 08:25:38 ET
- **live / promotion**：false / false
- **JSON**：`output/strategy_optimizer/calib/capadv_sealed_turnover_ref.json`
- **源权重**：`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`（aum_binding=1000000.0；60万/100万共用）
- **节奏**：`month_end_plus_first_last`；密封窗 2018-01-02→2024-05-31
- **重叠再平衡**：6 日（2024-01-02…2024-05-31）；换手观测 n=5（**<20 弱样本**）
- **结果**：median 单边 **18.3%** / 双边 **36.6%**；mean 单边 17.6%；年化单边约 2.20×
- **对照**：Leo 中心双边≈50%→单边≈25%；B4 纸面重叠约 35–42% 单边（更高换手，非优先）
- **Eng 用法**：弱样本 → **λ_turn 主目标用 Leo 单边≈25%**（`turn_target_src=leo_center_fallback`）；本 JSON 仅诊断；勿改纸面 FROZEN
- **缺口**：capadv 日权重仅自 2024-01-02；密封 2018→2024-05 大部无覆盖（全窗月末 77 vs 重叠 6）
