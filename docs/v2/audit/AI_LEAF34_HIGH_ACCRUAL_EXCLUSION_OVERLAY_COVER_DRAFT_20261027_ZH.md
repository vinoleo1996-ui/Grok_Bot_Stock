# 叶34 HI_LIQ 高应计剔除 overlay · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T09:42:00-04:00（America/New_York；墙钟 2026-10-27 09:42 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED_full_alpha=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑全窗** · 轻量计数已做 · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案 + 轻量计数闸**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶30–33 RESTORED）
- **主令**：2026-10-27 ~09:34 ET dig `cfd83e85`；叶33 HOLD CLOSED → 续挖叶34（优先高应计剔除 overlay；避 25/27/30–33 同构）

## 一句话

叶33 `SHARE_UNLOCK_PRESSURE_RESID` **HOLD CLOSED**（Arch `30efc8ed`；coverage 稀疏 ratio med=0.3365）。本票提案 **叶34 PRIMARY = HI_LIQ 高应计剔除 overlay**（`g1g5_ashare_high_accrual_exclusion_overlay_v1`）：`accrual_cf=1−ocf_to_profit` → 池内 top 20% 高应计 **mask=0 / soft-penalty** → 叠主干；**不是**重开 accrual_quality / 叶19 / 叶25 完整应计 α。轻量计数 **gate_pass=true**（median=2431；J20_max vs 19/25≈0.053；APPROX）。请主**排号→Arch 只审不签**。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **34**（28/29 FROZEN；26 GAP 不交审；33 CLOSED） |
| mechanism_tag | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| who_pays | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| dig | `cfd83e85`（`DIG_FACTOR_20261027_0934ET.md`） |
| 叶33 CLOSED | Arch `30efc8ed` · `.ok` `81521fb5` · lift `ee5235e6` · 正式 `afbbe7e7` UNCHANGED |
| 叶32 / 31 / 30 HOLD | `45dd87dc` / `7ef5aa11` / `f00536b9`（不回撤） |
| 正交硬拒 | vs 叶19/25 Jaccard≥0.7；披露 27/30/31/32/33 |
| q / rebal | DRAFT top **20%** / **20** 交易日 |
| 交付 | 形态 A：exclusion mask / soft-penalty；非完整多空 α |
| 计数闸 | **gate_pass=true**（APPROX；见 COUNT RECEIPT） |
| rss 意向 | **1500** 禁抬 |
| forbid | `245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74` |
| `0087c928` | 另队不夹带 |
| EXECUTED_full_alpha | **false** |

## 提案摘要（mechanism / 数据 / 公式）

| 项 | 内容 |
|---|---|
| mechanism | HI_LIQ 高应计剔除 overlay：忽视应计恶化仍满仓者付钱 |
| 数据路径 | `ocf_to_profit_pit_daily_tushare.parquet`（计数）；financials_pit cashflow/BS 冻结可选；HI_LIQ mask 同叶31/32 |
| 公式 | `accrual_cf=1−ocf_to_profit`；`H_t=top 20%`；`mask=0` on H_t |
| 与 19/25 差 | 19/25=完整 CFACC α；本叶=尾部剔除 overlay |
| 宇宙 | HI_LIQ 主判决 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300 |
| 判定 | 主干级或 ρ_excess vs capacity_adv<0.5 且 60万/100万叠加优于主干 |

## 禁止清单（forbid）

- 申 `.ok` / 全窗 X2 / Book-Smoke / selfcheck / 升纸面 / 挂 QUIET
- 重开 accrual_quality / 叶19 / 叶25 主叶；碰 RESTORED `245df63f+c5ed13df+5774bb6e` + 二十票
- 禁改叶33 `afbbe7e7`；夹带 `0087c928`；叶28/29 升 PRIMARY
- 卖方/金股/ETF份额/问询函当本叶主信号；GP/杠杆；moneyflow/hk_hold/margin/Amihud/解禁换皮
- git commit；报 Leo

## 请主 / Arch

1. **主**：确认叶号（默认 **34**）→ 收 who_pays+COVER+COUNT → hand Arch **只审不签**；通过后再谈预注册冻结/脚本窗。
2. **Arch**：只审文档契约与正交/禁项/PIT/APPROX；**不签** `.ok`；不代跑。
3. 备选 (2)(3) 不升；仅当 PRIMARY 后续硬拒时由主改派。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` |
| dig | `output/d1/DIG_FACTOR_20261027_0934ET.md`（`cfd83e85`） |

live=false · ≠X2 · ok_requested=false · EXECUTED_full_alpha=false · QUIET 未挂 · leo_notify=false
