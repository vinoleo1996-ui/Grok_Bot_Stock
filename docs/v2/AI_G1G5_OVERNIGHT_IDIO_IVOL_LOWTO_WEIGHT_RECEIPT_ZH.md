# 叶18v overnight_idio_ivol_lowto（VARIANT：20 日再平衡 + 前 40 名不交易缓冲 + 快门只管新开仓）回执 —— WATCH
- 时间：2026-10-18 00:16 ET（恢复跑；α/闸/评价权重已于 10-14 21:13–21:58 ET 按冻结变体预注册建好，本次复用、不重建、不调参。按预注册，只跑这一个变体）
- 预注册：docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_LOWTO_VARIANT_PREREG_ZH.md（FROZEN 2026-10-14 09:13:03 ET，sha256 fc1b9e53…，未改）。原叶18 结论不变（WATCH）。
- 产物：output/ai_factory/leaf18v_overnight_idio_ivol_lowto/（alpha_* = 日度 base-α；eval_resume_20261018_001319.json；poolew_excess.json）
- live=false；promotion=false；未自封；未跑 Book-Smoke；未起 8787；禁 GP

## 结论：WATCH（VARIANT；不交 Alpha）
换手问题解决了：HI_LIQ 双边换手从 20.9%/日降到 7.3%/日，变为可交易。但衰减门 v1.1 为 DECAY_DOWNGRADE（最新滚动残差 α −1.1%，H2 净 CAGR ≤510300）；GATE_V3 FAIL（两档都没跑赢 capacity_adv）；预注册 Gate B FAIL；密封窗为负。

## 数字（复权、T+1 开盘、17.5bp；244 主 / 252 对照）
| 宇宙·窗 | 档 | CAGR244 / 252 | MDD | 残差α |
|---|---|---|---|---|
| HI_LIQ 密封 | 60万 | −1.21% / −1.25% | −40.6% | +0.4% |
| HI_LIQ 密封 | 100万 | −2.32% / −2.39% | −42.9% | −0.8% |
| HI_LIQ X2 | 60万 | 9.91% / 10.26% | −20.5% | −0.2% |
| HI_LIQ X2 | 100万 | 7.39% / 7.64% | −19.8% | −2.8% |
| FULLA X2 | 60万 | 14.74% / 15.25% | −21.2% | +4.4% |
| FULLA X2 | 100万 | 20.06% / 20.78% | −20.1% | +8.7% |
| FULLA 密封 | — | N/A：FULLA 掩码在密封窗只覆盖 2023-09-21→2024-05-31（164 日），其余日子为空仓/ETF，数字无效 | | |

- 自检（LC 引擎，X2 20 名）：HI_LIQ 净 14.14%/MDD −18.7%/残差α +3.3%（2024 +11.3/2025 −2.6/2026 +4.9）；FULLA 净 13.40%，成本拖累超过毛超额一半 → FULLA 不可交易。
- 对池等权基准：HI_LIQ 密封 +5.3%（t 1.60），X2 +3.0%（t 0.56）；FULLA X2 −7.3%（t −1.36）。
- ρ(去β)：vs capacity_adv −0.27，vs cap_hiliq 0.37；vs 原叶18 0.85（同一 α 的变体，Jaccard max 1.0 出现在起始调仓日，不按硬拒处理）；vs insurer_surv/equity_incentive/insider_increase_hiliq 0.58–0.65。
- 组合（cap80+叶20）：HI_LIQ 60万 12.60%→12.59%，100万 13.79%→13.45%（均输）；对 B4 −0.79/−1.24pp。LC Gate：current ✓、A ✗、B ✓。
- IC（新池，HAC 仅披露）：HI_LIQ 5d 0.0017（t 1.09 / HAC 1.32），20d 0.0018（0.58/0.90），60d −0.0017；全部不显著。
- 披露：建 HI_LIQ 密封 α 时峰值 RSS 1.83GB，FULLA X2 1.69GB，**超 1.5GB 红线**（10-14 已发生）；下游评估峰值 1.26GB。评价 top-N 按建模时的行序取（缓冲规则下行序未必等于 α 排序）。
