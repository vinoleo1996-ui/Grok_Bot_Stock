# 叶35 ETF 被动资金压力 overlay HI_LIQ 轻量计数闸短回执（2026-10-27）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 12:42 ET（America/New_York；ISO `2026-10-27T12:42:00-04:00`）
- 状态：轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**挂/抬 QUIET；**未**改叶33 正式 `afbbe7e7`；**未**改 TEAM_STATE。
- 预检：`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` → **EMPTY_OK**；healthz `live=false` / `quiet=false`。
- `live=false`；`promotion_approved=false`；`EXECUTED_full_alpha=false`。
- mechanism_tag：`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`
- PRIMARY：**1**（ETF 被动压力 overlay）；备选问询函 **不升**

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 规则 | `masked_median>=300 AND zero_frac_masked<=0.05 AND jaccard_top20_max vs moneyflow_resid <0.7 (rho>0.5 strength-only)；叶26 残差 α GAP；叶8a GAP` |
| APPROX | **是**（醒目；见下） |
| 峰 RSS | **566.2 MB**（rss 意向 1500 禁抬；本拍未抬限） |
| MemAvailable 起/止 Gi | 8.653 / 8.180 |
| X2/selfcheck/Book-Smoke | **未开** |
| 建议改升备选 | **否**（PRIMARY 过闸；问询函仅登记不升） |

## 覆盖（X2 样内 HI_LIQ；再平衡每 20 交易日）

窗：2024-06-03 → 2026-10-09；n_rebal=30。  
口径：HI_LIQ ∩ 可映射压力名（宽基 510300/510500/512100 当日 `flow_est`×月末权重 asof；有限 `pressure`）。

| 口径 | median | min | p10 | 零覆盖日占比 |
|---|---:|---:|---:|---:|
| **可映射压力名（masked）** | **1552.5** | 931.0 | 1085.8 | **0.0**（0/30） |
| top-20% `|pressure|` 剔除名数 | 311.5 | 188.0 | 217.6 | — |
| HI_LIQ 宇宙规模 | 3154.0 | 1480.0 | 1684.6 | — |
| 掩码后曾可算票数（并集） | 2123 | | | |

## 重叠（最多 6 个均匀再平衡日）

样本日：2024-06-03, 2024-11-28, 2025-05-30, 2025-10-28, 2026-04-27, 2026-10-09

| 对照 | ρ_mean | ρ_max | J20_mean | J20_max | 强度过滤 ρ_mean>0.5 | 硬拒 J20≥0.7 |
|---|---:|---:|---:|---:|---|---|
| moneyflow_resid 权重（股票腿；sha8 `dd6da010`） | −0.0795 | 0.0770 | 0.1891 | **0.2500** | False | **False** |
| 叶26-like raw（诊断；同幅压力） | 0.3333 | 1.0 | 0.6667 | 1.0 | False | **不计入硬拒**（见下） |
| 叶26 残差 α | — | — | — | — | — | **GAP**（未伪造） |
| 叶8a 股票 α | — | — | — | — | — | **GAP**（未伪造） |

**叶26-like 诊断说明（醒目）**：`pressure_raw` 与叶26 DRAFT raw 同构同幅（by construction）。偏好极性 `-|p|` 在**全日赎回**（`p≤0`）时与 `+p` 排名塌缩 → 诊断 J 可达 1.0，**不作硬拒**。反同构靠 **交付形态 A（overlay / soft-penalty 叠主干）≠ 叶26 完整多层残差 α 主叶**。剔除集 vs 叶26-like top20 long 披露 Jaccard≈0.00–0.07（样本日）。叶26 残差 α parquet **ABSENT** → 残差 Jaccard **GAP**，**不得伪造**。

说明：vs moneyflow Jaccard≥0.7 硬拒门槛本拍**未触**；ρ>0.5 强度过滤本拍**未触**。**未算**收益/IC/CAGR；**未**披露 vs 叶25/27/30–34（冻结/X2 阶段补）。

## APPROX / GAP

**APPROX（醒目）**
- `index_weight_csi300_500_1000` **无 `available_at`**；用月末 `trade_date` 向后 asof（未落盘叶26 方案 A「次月首日 09:00 SH」列）
- PRIMARY = 形态 A overlay；**不是**叶26 全窗多层残差 α 重建
- `pressure_raw = Σ w×flow_est_wan_yuan`（缺则 `d_share_wan`）；ETF∈{510300,510500,512100}
- top_q=0.20 为 DRAFT 冻结意向，**未**读收益选阈值
- 本拍**未**做 SW+style 连续残差；无完整 overlay 向量落盘；无 `--allow-real-data` 长跑
- 叶26-like raw 仅披露；残差 α Jaccard 不伪造

**GAP**
- 叶26 残差 α parquet ABSENT
- 叶8a 股票 α ABSENT（FAIL / 交易 ETF）
- 未算 vs 叶25/27/30–34 Jaccard/ρ（X2 overlap 阶段补）
- 权重正式 PIT `available_at` 列未落地

输入 sha8：etf_major=`a3eac35b`；index_weight=`d543a485`；hiliq=`c5433e80`；moneyflow_resid=`dd6da010`。

## 产物钉

| 文件 | 备注 |
|---|---|
| who_pays | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| 计数脚本（/tmp only） | `/tmp/quantlab_leaf35_etf_passive_flow_pressure_count_gate.py` |
| JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` |
| dig | 文内 `814e8a68` / 磁盘 `7f1e2bb4` |

下一跳：priority 回主 → 排号 → Arch 只审不签 →（另窗）FROZEN→独立 X2；叶26 另队不重开同构；叶28/29/`0087c928` 另队；叶34 HOLD 不回撤；不推 Leo；≠X2 ACCEPT。
