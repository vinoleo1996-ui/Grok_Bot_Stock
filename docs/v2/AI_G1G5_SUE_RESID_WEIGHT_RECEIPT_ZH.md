# 叶20 sue_resid（去敏 SUE 残差，时间序列 SUE，不用一致预期）回执 —— WATCH
- 时间：2026-10-18 00:03 ET（恢复跑；α/闸/评价权重 10-14 22:00 ET 已按冻结预注册建好，本次复用不重建、不改参数）
- 预注册：docs/v2/AI_G1G5_SUE_RESID_WHO_PAYS_PREREG_ZH.md（FROZEN 2026-10-14 09:13:03 ET，sha256 53cbdc9e…，未改）
- 产物：output/ai_factory/leaf20_sue_resid/（alpha_{HILIQ,FULLA}_20261014_220029.parquet = 日度 base-α 主交付；eval_resume_20261018_000034.json；poolew_excess.json）
- live=false；promotion_approved=false；未自封；未跑 Book-Smoke；未起 8787；禁 GP

## 结论：WATCH（不交 Alpha 验收）
HI_LIQ（主）：衰减门 v1.1 DECAY_DOWNGRADE（最新滚动残差 α −8.9%，连降 3 季，H2 净 CAGR ≤510300）→ GATE_V3 FAIL；密封窗两档均负；对池等权超额 X2 +6.2%（t 0.89），统计上不显著。可交易（双边换手 5.6%/日）。

## 数字（复权、T+1 开盘、17.5bp；244 主 / 252 对照）
| 宇宙·窗 | 档 | CAGR244 / 252 | MDD | 残差α(对510300) |
|---|---|---|---|---|
| HI_LIQ 密封 | 60万 | −3.03% / −3.12% | −48.7% | −1.1% |
| HI_LIQ 密封 | 100万 | −2.66% / −2.74% | −46.0% | −1.0% |
| HI_LIQ X2 | 60万 | 8.82% / 9.13% | −36.1% | −1.7% |
| HI_LIQ X2 | 100万 | 14.25% / 14.75% | −25.1% | +3.2% |
| FULLA 密封 | 60万 | −0.37% / −0.38% | −47.5% | +1.6% |
| FULLA 密封 | 100万 | 3.76% / 3.88% | −36.4% | +5.3% |
| FULLA X2 | 60万 | 25.00% / 25.92% | −27.1% | +14.2% |
| FULLA X2 | 100万 | 15.21% / 15.75% | −28.3% | +5.0% |

自检（LC 引擎，X2 20 名书）：HI_LIQ 净 20.24%/MDD −22.4%/残差α +8.0%（2024 +2.2/2025 +18.6/2026 −1.2）；FULLA 净 22.61%/−20.5%/+11.4%。
- 对池等权基准：HI_LIQ 密封 +3.9%（t 0.91）、X2 +6.2%（t 0.89）；FULLA 密封 +2.6%（t 0.68）、X2 +0.1%（t 0.02）。→ 收益基本来自 β/小盘，纯意外部分不显著。
- ρ(去β) vs capacity_adv −0.23 / capacity_adv_hiliq 0.32；vs earnings_event(预注册必报) 0.23，earnings_event_hiliq 0.41，Jaccard max 0.04/0.09；vs 叶19 0.53（HI_LIQ）/0.61（FULLA）→ 与叶19 同用只能作过滤；Jaccard max 0.11，无硬拒。
- 衰减门 v1 与 v1.1 一致：HI_LIQ DOWNGRADE / FULLA KEEP。
- 组合（cap80+叶20，旧 capacity_adv 书）：HI_LIQ 60万 15.02%→15.17%（+0.15pp）、100万 16.24%→16.86%（+0.62pp），MDD 变浅；对 B4 60万 −1.26pp / 100万 +0.26pp。LC Gate A/B：HI_LIQ、FULLA 均 current/A/B ✓；预注册 Gate A ✓、Gate B ✓。
- IC（新池，HAC 仅披露）：HI_LIQ 5d 0.0019（t 0.86 / HAC 1.05），20d 0.0027（0.59/0.75）；FULLA 20d 0.0024（0.77/1.00）。全部不显著。

## 披露
1. 预注册第 4 条「叶19 CFACC rank（若可得）」未进中性化回归（两叶 10-14 并行构建，叶19 当时未落盘）；事后 ρ vs 叶19 0.53–0.61，已按「只作过滤」处理。
2. 10-14 建 α 峰值 RSS 2.39GB，**超 1.5GB 红线**（已发生，未重跑；下游峰值 1.22GB）。
3. 建 α 脚本 summary 的 cap 对照列作废（同叶19 回执第 4 条）。
