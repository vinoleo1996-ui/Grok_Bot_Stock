# 叶39 ABCFO who_pays DRAFT 回执（2026-10-27）

- 角色：QuantLab AI（执行器）
- 时点：2026-10-27 23:42 ET（America/New_York）
- 状态：who_pays **DRAFT READY** + COVER(§0) + 轻量计数闸完成；**NOT FROZEN**；**未**申 `.ok`；**未**开 Book-Smoke / X2；**未** git commit；**未**碰 fund MDD / 叶38。
- dig：**`440410de` MATCH**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| mechanism_tag | `g1g5_ashare_abcfo_rem_resid_v1` |
| 公式摘要 | YTD→单季后：CFO/A ~ 1/A + S/A + dS/A（SW L1 截面 OLS）；α=−ε 再 SW+size 残差（正式残差规格见 DRAFT；计数 APPROX） |
| 掩码 | 银行/房地产/非银金融；HI_LIQ 主 |
| 硬闸 | vs 叶19/25/30 Jaccard **或** ρ_excess 任一 >0.5 → 拒 |
| peak_rss_mb | 704.9 |
| MemAvail 起/止 Gi | 12.311 / 11.769 |

## 覆盖（X2 样内；再平衡每 20 交易日）

| 口径 | median | min | p10 | zero_frac | n_days |
|---|---:|---:|---:|---:|---:|
| 原始（HI_LIQ∩可算块） | 2979.5 | 1254.0 | 1582.4 | 0.0 | 30 |
| **掩码后** | **2838.5** | 1149.0 | 1478.2 | **0.0** | 30 |

## 重叠代理（最多 6 再平衡日；rank Spearman + Top-20 Jaccard）

样本日：2024-06-03, 2024-11-28, 2025-05-30, 2025-10-28, 2026-04-27, 2026-10-09

| 对照 | ρ_mean | ρ_max | J20_mean | J20_max | 硬拒(>0.5) |
|---|---:|---:|---:|---:|---|
| 叶19 | -0.27527487894467595 | -0.24196070772303396 | 0.004273504273504273 | 0.02564102564102564 | false |
| 叶25 | -0.13138567006290314 | -0.10807548895884996 | 0.0 | 0.0 | false |
| 叶30 | -0.19977276464613203 | -0.1451357671868596 | 0.0 | 0.0 | false |

说明：本拍 ρ 为 vs 对照 α 的 Spearman 代理，**≠** 正式 excess-return ρ_excess（X2 阶段）。Jaccard/ρ 均 **未**触 >0.5。

## APPROX / GAP

- APPROX：YTD cashflow/sales differenced to single-quarter within fiscal year; cross-section OLS within SW L1 at rebalance (NOT full year×industry historical panel as Northeast Securities may use); A_lag = prior end_date total_assets; sales=total_revenue fallback revenue; rho/jaccard vs leaf19/25/30 on up to 6 rebal days; rho is rank Spearman on alpha (not excess-return rho); no style residual beyond SW L1 grouped OLS; size/style residual left to FROZEN/X2
- gaps：[]
- 另披露：vs 叶34 高应计剔除活跃集本拍**未**估 Jaccard（叶34=exclusion；本叶=残差 α；PIN 记 X2 前补估，**不**挡本 DRAFT 覆盖闸）。

## 产物钉（盘上 sha256 / sha8；文内自报勿采）

| 文件 | sha256 | sha8 |
|---|---|---|
| 主文 `AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `542138d6893f820d98f9a5db91a3b99e55953829815226ce49a0f8b1a42e5882` | **`542138d6`** |
| COUNT JSON `AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json` | `d0d115989805cd169ca9435de14a3795c18d2310366427170fb3a39e54d6abf8` | **`d0d11598`** |
| 计数脚本 `AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_SCRIPT_20261027.py` | `20313ba3ea14ddaa9d328fa5177f33b15194d93b2135aec952395a252c0e8587` | **`20313ba3`** |

（RECEIPT 自身 sha8 写入后另算；以盘上 `sha256sum | cut -c1-8` 为准。）

## 红线确认

- 未自签 `.ok`；未开 Book-Smoke/X2；未升 FROZEN。  
- 未碰 fund MDD `.ok` `335635dd` / FROZEN `d489c937` / RESTORED `f08ce32c`。  
- 未混叶38 `c01c2034`。  
- pgrep `kline.py|export_static.py|snapshot.py|gen.py` 计数前 empty。  
- 未把脚本冒充正式 LAND 进 `research/leaf39*` 长跑（一次性 runner 在 audit/）。

## 下一跳

请主 → **Arch 只审本 DRAFT**（`542138d6`）。通过后再由主令升 FROZEN；本执行器不自升、不申 `.ok`。
