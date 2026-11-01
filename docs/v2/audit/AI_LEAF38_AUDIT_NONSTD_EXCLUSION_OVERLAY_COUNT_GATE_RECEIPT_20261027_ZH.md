# 叶38 非标审计意见剔除 overlay HI_LIQ 轻量计数闸短回执（2026-10-27）

- 角色：QuantLab AI（执行器）
- 时点：2026-10-27 20:42 ET（America/New_York）
- 状态：轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**挂 QUIET；**未**改叶37 产物。
- `live=false`；`promotion=false`；`EXECUTED_full_alpha=false`；`leo_notify=false`
- mechanism_tag：`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`
- PRIMARY：**非标审计意见剔除 overlay**（负向；挂 capacity_adv / HI_LIQ）
- dig：sha8 **`fa973826`** / 全长 `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 规则 | `daily_excl_median>=30.0 AND frac(daily>=10)>=0.6 AND zero_frac<=0.5 AND jaccard_max_vs_negevent<=0.5 AND jaccard_max_vs_leaf36<=0.5 (hard reject if either >0.5; metric=max on leaf38-hit days)` |
| gate_cov_pass | **`true`**（median=48.0；frac_ge10=1.0；zero_frac=0.0） |
| hard_reject_jaccard | **`false`**（jmax_neg≈0.056180；jmax_l36≈0.064935） |
| peak_rss_mb | **1584.4**（>1500 → **WATCH**；rss 意向 1500 禁抬；本拍未抬限） |
| MemAvailable 起/止 Gi | 12.275 / 11.325 |
| X2/selfcheck/Book-Smoke | **未开** |
| 未算 | 收益/IC/CAGR/PnL |

## 覆盖（X2 样内 HI_LIQ；PIT 最新意见非标）

窗：2024-06-03 → 2026-10-09；n_cal=570。  
口径：HI_LIQ ∩「最新可用审计意见 is_non_standard=True」（T1=available_at 次一交易日生效）。

| 口径 | median | p25 | p75 | mean | 零覆盖日占比 |
|---|---:|---:|---:|---:|---:|
| **触窗剔除名（全日）** | **48.0** | 41.0 | 58.0 | 47.4789 | **0.0** |
| 有剔除日（hit） | 48.0 | 41.0 | 58.0 | 47.4789 | — |
| HI_LIQ 宇宙规模 | 3171.5 | — | — | — | — |

有剔除日占比：**1.0**；frac(日剔除≥10)=**1.0**；frac(≥30)=**0.8579**。

**阈值论证（醒目）**：叶36 问询函短窗 median=6 FAIL；**勿盲抄**叶34/35 `median≥300`。本叶写死 **median≥30 且 ≥60% 交易日剔除名≥10**。审计非标为年报级 PIT 状态，厚度天然高于问询函短窗；实测 median=**48.0** → 覆盖闸 **PASS**。

## 事件源

| 项 | 值 |
|---|---|
| 源 | `data/v2/audit/audit_opinion_pit_tushare.parquet` |
| 非标行 / 只 | 2621 / 895 |
| 非标结果分布 | {'带强调事项段的无保留意见': 1130, '保留意见': 913, '无法表示意见': 570, '否定意见': 7, '无保留带持续经营重大不确定性': 1} |
| 按年（available_at） | 见 JSON `nonstd_by_year` |
| X2 内 state-true name-days | 27063 |

## 同构

| 对照 | max（触窗日） | 硬拒>0.5 |
|---|---:|---|
| vs negevent（held-cut∪E2/E3/E4） | 0.056180 | 否 |
| vs 叶36（FIN 问询 WIN=20 重建） | 0.064935 | 否 |

negevent 先验：**FAIL**（CAGR/MDD 未优于主干；meta sha8 `4ab30657`）。

## APPROX / GAP

**APPROX**：negevent 对照无 E1；叶36 为同漏斗重建；instrument=`ts_code`。  
**GAP**：未算 vs 叶34/35/37 Jaccard；无完整 overlay 落盘；软惩罚未做。

输入 sha8：{'audit': '7d0af2e4', 'hiliq': 'c5433e80', 'capacity_adv': '4348877e', 'negevent_w': 'e19e1dc4', 'negevent_meta': '4ab30657', 'ann_main': 'aab46c56', 'ann_post': '549a28c3'}

## 产物钉（sha8 + 全长）

| 文件 | sha8 | 全长 |
|---|---|---|
| who_pays | `16c1f70b` | `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c` |
| COVER | `7c3b8691` | `7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea` |
| 计数脚本 | `ba34da2a` | `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296` |
| JSON | `2b3babb5` | `2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750` |
| 本 RECEIPT | `7cc317d9` | `7cc317d96d770985cccbe326683935220e2112718da1e84866c75793e1989803` |

下一跳：priority 回主 → Arch 审 DRAFT / 是否升 FROZEN；**不**申 `.ok`；**不**挂 QUIET；**不**跑 X2/Book-Smoke；fund_portfolio 仍待 Data 补 fund_basic；不推 Leo；≠X2 ACCEPT。
