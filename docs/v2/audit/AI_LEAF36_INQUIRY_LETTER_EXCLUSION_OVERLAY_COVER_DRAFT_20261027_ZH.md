# 叶36 问询函/复合排雷剔除 overlay · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T16:35:00-04:00（America/New_York；墙钟 2026-10-27 16:35 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED_full_alpha=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑全窗** · 轻量计数已做 · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案 + 轻量计数闸**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶35 RESTORED）
- **主令**：2026-10-27 ~16:25 ET dig 文内 `116a5454` / 磁盘 **`74234fca`**；叶35 B1 HOLD CLOSED → 续挖叶36（优先问询函排雷剔除；避 negevent/34/35 同构）

## 一句话

叶35 ETF 被动压力 overlay **B1 HOLD CLOSED**（`.ok` `eb70eef4` CONSUMED；≠X2 ACCEPT）。本票提案 **叶36 PRIMARY = 问询函/复合排雷剔除 overlay**（`g1g5_ashare_inquiry_letter_exclusion_overlay_v1`）：财务问询/关注函 → T1 起 20 日 HI_LIQ `mask=0` → 叠主干；**不是** negevent 复刻、**不是**完整 α。轻量计数 **gate_pass=false**（触窗剔除名 median=**6.0**≪30；vs negevent jaccard_max≈**0.0571**≪0.5 同构过）。请主**收 COUNT → 改派备选或另议**；**勿本拍升 FROZEN / 申 `.ok`**。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **36**（28/29 FROZEN；35 B1 HOLD CLOSED） |
| mechanism_tag | `g1g5_ashare_inquiry_letter_exclusion_overlay_v1` |
| who_pays | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| dig | 文内 `116a5454` / 磁盘 **`74234fca`**（`DIG_FACTOR_20261027_1625ET.md`） |
| 叶35 B1 CLOSED | 脚本 `434ff42c` · SIGNED `65d89851` · `.ok` `eb70eef4` · lift `52a3bc4b` · RUN `e75c090b` · mask `576ca398` · overlap `54933299` · run_meta `2bb21a76` · CONSUMED `63af61e1`；≠X2 ACCEPT |
| 叶33 / 32 HOLD | `afbbe7e7` / `45dd87dc`（不回撤） |
| 正交硬拒 | vs negevent Jaccard **>0.5** |
| WIN / 交付 | DRAFT **20** 交易日 / 形态 A exclusion mask |
| 计数闸 | **gate_pass=false**（覆盖 FAIL；见 COUNT RECEIPT） |
| rss 意向 | **1500** 禁抬（本拍 peak≈1421.0 MB） |
| forbid | `eb70eef4+00eec671+10927bd9+25ae4572+…`（who_pays §11） |
| EXECUTED_full_alpha | **false** |

## 提案摘要（mechanism / 数据 / 公式）

| 项 | 内容 |
|---|---|
| mechanism | 财务问询/关注函监管排雷剔除：忽视信号仍满仓者付钱 |
| 数据路径 | `announcements_classified_pit.parquet` + post202406 同伴；HI_LIQ mask |
| 公式 | `inquiry_letter` ∧ (问询函\|关注函) ∧ FIN_KW ∧ ¬重组 ∧ ¬异常波动/可转债 ∧ ¬纯回函噪声 → T1..T1+19 mask=0 |
| 与 negevent 差 | negevent=E1–E4（已 FAIL）；本叶=财务问询/关注函 only |
| 宇宙 | HI_LIQ 主判决 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300 |
| 判定 | 主干级或 ρ_excess vs capacity_adv<0.5 且 60万/100万叠加优于主干 |

## 禁止清单（forbid）

- 申 `.ok` / 全窗 X2 / Book-Smoke / selfcheck / 升纸面 / 挂 QUIET
- 复刻 negevent；碰 RESTORED `eb70eef4+00eec671+10927bd9+25ae4572` + 旧票
- 禁改叶33 `afbbe7e7` / 叶35 正式脚本；自开备选 who_pays
- 卖方/金股/应计/ETF/两融换皮；GP/杠杆
- git commit；报 Leo

## 请主 / Arch

1. **主**：确认叶号（默认 **36**）→ 收 who_pays+COVER+COUNT；**因 gate_pass=false**，建议改派 §12 备选（IMAX/隔夜彩票剔除，或行业级客户动量先 IO 表 PIT），**或**另议扩源——**勿令 AI 自开备选**。
2. **Arch**：若主仍交审，只审文档契约与正交/禁项/PIT/APPROX；**不签** `.ok`；不代跑；**不建议本拍 FROZEN**。
3. 备选不升 PRIMARY 正文。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| SCRIPT | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py`（/tmp 同源） |
| JSON | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` |
| dig | `output/d1/DIG_FACTOR_20261027_1625ET.md`（磁盘 `74234fca`） |

live=false · ≠X2 · ok_requested=false · EXECUTED_full_alpha=false · QUIET 未挂 · leo_notify=false
