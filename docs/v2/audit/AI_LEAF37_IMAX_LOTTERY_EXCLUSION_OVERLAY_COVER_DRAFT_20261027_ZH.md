# 叶37 IMAX/隔夜彩票剔除 overlay · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T16:45:00-04:00（America/New_York；墙钟 2026-10-27 16:45 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED_full_alpha=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑全窗** · 轻量计数已做 · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案 + 轻量计数闸**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶36 RESTORED）
- **主令**：叶36 inquiry **HOLD CLOSED**（WHO `feaa5dbb`）→ 改派备选 **(A)** IMAX/隔夜彩票剔除；dig `74234fca`

## 一句话

叶36 财务问询剔除 **HOLD CLOSED**（覆盖不足；禁放宽阈）。本票提案 **叶37 PRIMARY = IMAX/隔夜彩票剔除 overlay**（`g1g5_ashare_imax_lottery_exclusion_overlay_v1`）：`IMAX_proxy`（raw r_id 20 日 top-5 均）→ 池内 top 20% **mask=0** → 叠主干；**不是**叶24 完整 −IMAX 主叶，**不是**叶18/27 波动主 α。轻量计数 **gate_pass=true**（computable median=**2816.5**；excl median=**564.0**；J18_max≈**0.311**；J27_max≈**0.443**≪0.7；APPROX）。请主**排号→Arch 只审不签**。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **37**（叶36 inquiry HOLD CLOSED → 改派 A；亦可主裁挂 36-altA） |
| mechanism_tag | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| who_pays | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| dig | 磁盘 **`74234fca`** |
| 叶36 CLOSED | WHO `feaa5dbb`；禁放宽覆盖阈；不复开 inquiry |
| 叶35 B1 / 叶33 / 叶32 | `.ok` `eb70eef4` / `afbbe7e7` / `45dd87dc`（不回撤） |
| 正交硬拒 | vs 叶18/18v/27 Jaccard≥0.7；披露叶24 |
| q / rebal | DRAFT top **20%** / **20** 交易日 |
| 交付 | 形态 A：exclusion mask / soft-penalty；非叶24 完整 α |
| 计数闸 | **gate_pass=true**（APPROX；见 COUNT） |
| rss 意向 | **1500** 禁抬（本拍 peak≈1030.1 MB） |
| forbid | `eb70eef4+00eec671+10927bd9+25ae4572+…`（who_pays §11） |
| EXECUTED_full_alpha | **false** |

## 提案摘要（mechanism / 数据 / 公式）

| 项 | 内容 |
|---|---|
| mechanism | 高 IMAX 彩票右尾剔除：忽视日内追高彩票仍满仓者付钱 |
| 数据路径 | `cs_panel_v2_resumefix` ret/ret_on；HI_LIQ mask；叶18/18v/27/24 α 仅正交 |
| 公式 | `r_id=(1+ret)/(1+ret_on)−1`；`IMAX_proxy=mean(top5 r_id,20d)`；`H_t=top 20%`；`mask=0` |
| 与 18/24/27 差 | 18/27=波动主 α；24=−IMAX 完整排序；本叶=高 IMAX 剔除 overlay |
| 宇宙 | HI_LIQ 主判决 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300 |
| 判定 | 主干级或 ρ_excess vs capacity_adv<0.5 且 60万/100万叠加优于主干 |

## 禁止清单（forbid）

- 申 `.ok` / 全窗 X2 / Book-Smoke / selfcheck / 升纸面 / 挂 QUIET
- 重开叶24 完整主叶；复开叶36 inquiry；放宽叶36 覆盖阈
- 碰 RESTORED `eb70eef4+00eec671+10927bd9+25ae4572` + 旧票
- 禁改叶33 `afbbe7e7` / 叶35 `434ff42c`；自开备选 B；`research/leaf37*` 正式构建
- git commit；报 Leo

## 请主 / Arch

1. **主**：确认叶号（默认 **37**）→ 收 who_pays+COVER+COUNT → hand Arch **只审不签**；通过后再谈预注册冻结/脚本窗。
2. **Arch**：只审文档契约与正交/禁项/PIT/APPROX；**不签** `.ok`；不代跑。
3. 备选 B 不升；仅当 PRIMARY 后续硬拒时由主改派。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| SCRIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` |
| JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` |
| dig | `output/d1/DIG_FACTOR_20261027_1625ET.md`（`74234fca`） |

live=false · ≠X2 · ok_requested=false · EXECUTED_full_alpha=false · QUIET 未挂 · leo_notify=false
