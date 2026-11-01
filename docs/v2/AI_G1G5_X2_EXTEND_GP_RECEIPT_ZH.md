# AI G1G5 X2 日历延伸 + GP 接管回执

- **时间：** 2026-10-12 ~11:16 ET
- **Leo 确认卡：** 「延伸X2+接管GP」
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；禁 v27 同构空转

## 1) 日历延伸结果

| 包 | 角色 | 路径 | 行数 | sessions | 标的 | 日期跨度 | 达 ≥2026-10-09 |
|---|---|---|---|---|---|---|---|
| **nontextbook** | **主攻** | `output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet` | 33400 | 668 | 50 | 2024-01-02→2026-10-09 | **是** |
| expand | 备选/对照 | `output/intel/g1g5_expand_daily_weights_20261012_111354.parquet` | 33400 | 668 | 50 | 2024-01-02→2026-10-09 | **是** |

- 主攻机制：`g1g5_ashare_inst_friction_v1`（ETF份额流/解禁残差/T+1/涨跌停）；who_pays **无「动量」**
- 对照机制：截面 excess_20d vs 510300（教科书动量）；角色=备选，非主线
- 列契约：`weight_long_v1_20261012`；别名 `session,instrument_id,weight`；`mechanism_tag` 行级
- universe：`g1g5_mid_large_liquid_top50`（复用）
- stub_window=false；stub_forward_fill=false
- 面板拼接：D0 `data/local_market/.../panels` ∪ `data/v2/asof_extend_tushare_202610/panels`（50/50 达 2026-10-09）
- 月频再平衡 sessions：nontextbook=35；日权重合计=1
- 抽样 vs expand 权重 corr@2025-06-30≈-1.4583242021378345e-17（非换皮预期）
- meta sidecar：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet.meta.json` · `output/intel/g1g5_expand_daily_weights_20261012_111354.parquet.meta.json`
- run meta：`output/intel/g1g5_nontextbook_run_meta_20261012_111316.json` · `output/intel/g1g5_expand_run_meta_20261012_111354.json`
- G6：两包 proof pass

### peak MEM

| 包 | peak_rss_kb | ≈MB | 相对 2GB |
|---|---|---|---|
| nontextbook | 2111016 | 2061.5 | **WARN 略超**（目标≤2048MB） |
| expand | 2022356 | 1975.0 | **WARN 略超** / 边界 |

诚实记录：未杀跑；后续 X2 重生可再砍辩论轮次/清缓存压到 ≤2GB。

## 2) GP/工厂接管

- 交接已读：`output/alpha/AI_FACTORY_HANDOFF_TO_QUANTLAB_AI_ZH.md`、`AI_PARTICIPATION_STATUS_ZH.md`、`docs/v2/PROMOTION_ACCEPTANCE.md`、`output/factor_evolve/latest_meta.json`
- 接管盘点落盘：`output/ai_factor/GP_TAKEOVER_BY_QUANTLAB_AI_ZH.md`
- **ACTIVE：** 无（FE latest 仅为 smoke；strategy_promotion_approved=false）
- **硬闸版本指针：** `factor_evolve_v2_qm_p0_20261012`（权重契约侧）；GP 适应度硬闸见交接页 §Alpha 硬闸
- **GP 现状：** v23–v26 均已停；v26 GATE_OK=0；**本批未新开 GP**（禁 v27 同构）
- promotion_approved=false；不晋级；不交 Strategy

## 3) 请 New Bot

派 Beta Book-Smoke @60万/100万 vs 510300，主测：

`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`

可选对照：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`（动量备选，不作主线）。

## 4) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不启 v27；不把过闸数字当晋级
