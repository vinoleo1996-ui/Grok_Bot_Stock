# 叶36 问询函/复合排雷剔除 overlay HI_LIQ 轻量计数闸短回执（2026-10-27）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 16:35 ET（America/New_York；ISO `2026-10-27T16:35:00-04:00`）
- 状态：轻量计数完成；**非** X2 / selfcheck / Book-Smoke；**未**申 `.ok`；**未**挂/抬 QUIET；**未**改叶33 正式 `afbbe7e7`；**未**改叶35 正式脚本；`research/leaf36*` **ABSENT**。
- 预检：`pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` → **EMPTY_OK**。
- `live=false`；`promotion_approved=false`；`EXECUTED_full_alpha=false`。
- mechanism_tag：`g1g5_ashare_inquiry_letter_exclusion_overlay_v1`
- PRIMARY：**问询函/复合排雷剔除 overlay**；备选 **不自开**
- dig：文内 `116a5454` / 磁盘现算 **`74234fca`** MATCH

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`false`** |
| 规则 | `daily_excl_median>=30 AND zero_frac<=0.50 AND jaccard_max_vs_negevent<=0.5`（硬指标=触窗日 max） |
| gate_cov_pass | **false**（median=6.0 < 30） |
| hard_reject_jaccard | **false**（max≈0.057143 ≪ 0.5） |
| APPROX | **是**（醒目；见下） |
| 峰 RSS | **1421.0 MB**（rss 意向 1500 禁抬；本拍未抬限） |
| MemAvailable 起/止 Gi | 12.336 / 11.254 |
| X2/selfcheck/Book-Smoke | **未开** |
| 建议改升备选 | **是**（PRIMARY 覆盖闸 FAIL；见文末备选文案；**勿自开**） |

## 覆盖（X2 样内 HI_LIQ；全日触窗剔除名）

窗：2024-06-03 → 2026-10-09；n_cal=570；exclusion WIN=20 交易日。  
口径：HI_LIQ ∩ PRIMARY 事件窗内名（财务问询/关注函过滤后）。

| 口径 | median | p25 | p75 | mean | 零覆盖日占比 |
|---|---:|---:|---:|---:|---:|
| **触窗剔除名（全日）** | **6.0** | 4.0 | 12.0 | 8.1140 | **0.0**（0/570） |
| 有剔除日（hit）上剔除名 | 6.0 | 4.0 | 12.0 | 8.1140 | — |
| 每 20 日抽样披露 | 5.0 | 4.25 | 12.5 | — | — |
| HI_LIQ 宇宙规模 | 3171.5 | — | — | — | — |

有剔除日占比：**1.0000**（570/570）；日均剔除名数≈**8.114**。

**阈值论证（醒目）**：财务问询/关注函天然稀疏，**勿盲抄**叶34/35 `median≥300`。本拍写死 **全日触窗剔除名 median≥30** 作为「独立 overlay 叶最小厚度」。实测 median=**6.0** → **覆盖闸 FAIL**（即便放宽到「无 FIN 关键词」敏感性中位仍≈9，仍≪30）。同构闸单独**通过**。

## 事件过滤漏斗

| 步 | 条数 |
|---|---:|
| inquiry_letter 行 | 9666 |
| +标题含问询函/关注函 | 7839 |
| +FIN 关键词 | 2827 |
| −重组类 | 2627 |
| −异常波动/可转债 | 2526 |
| −纯回函噪声（PRIMARY） | 2490 |
| PRIMARY 唯一 inst×d（≥2023-10） | **362** |
| 其中 X2 available_at | **311** |
| HI_LIQ 窗应用次数 | 345 |

披露：base∧FIN 中异常波动=0；可转债=101；重组切出=200。  
按年 PRIMARY inst×d：{"2023": 15, "2024": 105, "2025": 120, "2026": 122}。

FIN 关键词表（写死）：`年报|半年报|季报|财务|会计|审计|业绩|应收|存货|商誉|收入|利润|信息披露|监管工作函`  
重组剔除：`重组|重大资产重组|吸收合并|借壳`

## 同构 vs negevent（已 FAIL 对照）

negevent run_meta：CAGR_cap≈**0.1206702675422644** / CAGR_neg≈**0.11683043590904685**；MDD_cap≈**-0.13679790509278622** / MDD_neg≈**-0.13887855429317553** → **未优于主干**（诚实 FAIL）。  
Jaccard 方法：APPROX = held-cut(capacity_adv vs negevent 权重) ∪ 同表重建 E2/E3/E4 窗；**未**重建 E1 share_float。

| 口径 | n | mean | max | median |
|---|---:|---:|---:|---:|
| 双侧非空日 | 570 | 0.004186 | 0.057143 | 0.000000 |
| **叶36 触窗日（硬指标用 max）** | 570 | **0.004186** | **0.057143** | 0.000000 |

硬拒阈值 >0.5：**未触**。held-cut name-days=55；E2/E3/E4 重建 pairs≈46235；approx_neg_pairs=46256。

**未算**收益/IC/CAGR/PnL。

## APPROX / GAP

**APPROX（醒目）**
- 公告 = 主表 + post202406 同伴（主表 `inquiry_letter` 截断 2024-05-31；对齐 negevent `EVENTS`）
- 回函噪声过滤为标题启发式（issuer-ish）
- negevent 对照 = held-cut ∪ E2/E3/E4；**无 E1**
- WIN=20 为 DRAFT 冻结意向，**未**读收益选窗
- 无完整 overlay 向量落盘；无 `--allow-real-data` 长跑

**GAP**
- 未算 vs 叶34/35/33/32 Jaccard（X2 阶段补）
- E1 share_float 未重建进 negevent 对照
- 连续 soft-penalty + SW+style 未构建

输入 sha8：ann_main=`aab46c56`；ann_post=`549a28c3`；hiliq=`c5433e80`；capacity_adv=`4348877e`；negevent_w=`e19e1dc4`；negevent_meta=`4ab30657`。

## 备选建议（勿自开）

> PRIMARY 计数/同构闸未过：建议主改派备选——**(A) IMAX/隔夜彩票剔除**（须 vs 叶18/27 overnight-idio 同构闸）；或 **(B) 行业级客户动量**（先 IO 表 PIT 可得性）。本拍**勿自开**备选 who_pays。

## 产物钉

| 文件 | 备注 |
|---|---|
| who_pays | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| 计数脚本 | `/tmp/quantlab_leaf36_inquiry_exclusion_count_gate.py` + audit 副本 `…COUNT_GATE_SCRIPT_20261027.py` |
| JSON | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` |
| dig | 文内 `116a5454` / 磁盘 `74234fca` |

下一跳：priority 回主 → **改派备选或另议**；不申 `.ok`；不挂 QUIET；不跑 X2/Book-Smoke；叶35/33/32 HOLD 不回撤；不推 Leo；≠X2 ACCEPT。
