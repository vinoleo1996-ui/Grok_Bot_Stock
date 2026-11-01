# 【FROZEN 预注册 2026-10-27 10:03 ET】叶34：HI_LIQ 高应计剔除 overlay（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 10:03 ET**（America/New_York；ISO `2026-10-27T10:03:09-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER/COUNT **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 λ/q/方向。
- 主令：2026-10-27 09:56 ET — Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`9d8a2f9e`** → 令 AI 出 FROZEN 预注册（C1–C13 入钉；不 HOLD）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`9d8a2f9e`**（全长 `9d8a2f9edde9f00ae230b9914025fc95db2fba35dc102f83c2a38c26d8247ecd`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`fa6aa2e3`**（全长 `fa6aa2e3ffb084cc01f6a4d20575e528f1c095262c10a00e70dadb4c15cc473b`）
  - COVER DRAFT：`docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` sha8 **`76b37ca3`**（全长 `76b37ca33be72f5311ded30693493ab431b5ac0820730c2f4d0081cfe9b5aa8c`）
  - COUNT RECEIPT：`docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` sha8 **`806e1758`**（全长 `806e17589697c48c0078cc43f42c01736a80b1995a71947484358cc4c2c4aae9`）
  - COUNT JSON：`output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` sha8 **`9730d432`**（全长 `9730d432735f48892eaceb0c3c8d73f3a104d4cf32a73dd0863cc9a23f546731`）
  - PIN（C3）：`docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` sha8 **`bb418e6a`**（全长 `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b`）
- 对照形态：叶33 PREREG_FROZEN `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md`（结构对齐；内容换叶34）。
- 叶号：**叶34**；mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；叶28/29 仍 FROZEN 另队；叶26 GAP **不交审**；叶33 正式 `afbbe7e7` UNCHANGED；叶32 HOLD `45dd87dc` / 叶31 `7ef5aa11` / 叶30 `f00536b9` **不回撤**（只读对照）。
- **本冻结 ≠ `.ok` / ≠ 构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无脚本**（`research/leaf34*` ABSENT 预期）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_high_accrual_exclusion_overlay_v1`（叶34）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内忽视应计质量恶化、仍给高应计名足额权重的持仓者——高应计剔除后，主干少踩应计反转与质量踩雷。  
> **可检验预测（已冻结）**：PRIMARY 交付 = **mask-only** 日度 exclusion mask（池内 `accrual_cf` top_q=**0.20** 高应计名 `mask=0`，其余可算名 `mask=1`；不可算名不进有效集、不填假 0）；**不是**完整 CFACC/accrual_quality TopN 多空主 α。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃集 vs 叶19/25 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另须完整重叠 vs 叶27/30/31/32/33；HI_LIQ 再平衡日可算 overlay 有效名 median≥300；FULLA 研究对照 median≥800。  
> **失效条件**：退化为叶19/25 完整 CFACC 多空主叶或 accrual_quality TopN 长端复开；或与叶19/25 Jaccard≥0.7；或主信号混入卖方/金股/TP/LLM/ETF份额/问询函；或冻结后事后改 top_q / 翻转剔除方向读收益；或用 `e_available_at > t` 偷看；或把本 overlay 伪称「全新会计 α」掩盖与应计族相关；或 PRIMARY 静默改 FULLA；或把 COUNT APPROX gate_pass 当 X2 ACCEPT。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（高应计剔除 overlay；慢）— **FROZEN**

在 PRIMARY 池（HI_LIQ）财务 PIT 上定义 CF-accrual 代理并做截面高应计剔除。

对每个再平衡日 \(t\)，取 as-of 有效的 OCF/净利润（PIN C3）：

$$
\mathrm{accrual\_cf}_{i,t} = 1 - \mathrm{ocf\_to\_profit}_{i,t}
\quad\text{（仅 NP>0 有效行；等价 }(\mathrm{NP}-\mathrm{OCF})/\mathrm{NP}\text{）}
$$

### 1.1 C3 数据 / PIT / NP / period_basis（PIN 入钉）

PIN 决议 **`bb418e6a`** 写死：

| 项 | **FROZEN** |
|---|---|
| 日表路径 | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（9,754,991 行；sha8 `f9faf7e7`） |
| PIT | `e_available_at ≤ t`；禁偷看 |
| 有效行 | `ocf_to_profit` 有限 ∧ `denom_small=false` ∧ `net_profit>0` ∧ `np_negative=false`；**NP≤0 一律剔除** |
| `period_basis` | **接受**日表 YTD-ish / `YTD_cumulative` 为 PRIMARY（与 COUNT APPROX 同口径）；改季表/TTM 须补丁+重计数，不得静默改 |
| PRIMARY 不用 | BS `WC_ACC/TA`（可选对照默认 OFF；启用须另补丁+重计数） |

### 1.2 剔除规则 / 交付（C4 / C5 / C11 — **mask-only PRIMARY**）

$$
\mathcal{H}_t = \{i\in\mathrm{PRIMARY}_t:\; \mathrm{accrual\_cf}_{i,t} \ge Q_{1-q}(\mathrm{accrual\_cf}_{\cdot,t})\}
\quad q=0.20
$$

| 项 | **FROZEN** |
|---|---|
| **PRIMARY 交付** | **mask-only**：可算名 \(i\in\mathcal{H}_t\) → `mask=0`；其余可算名 → `mask=1`；不可算名 **不进有效集、不填假 0** |
| 明示（C4） | **mask-only PRIMARY**；截面分位阈值剔除，**可不**做全残差（mask 已是池内相对） |
| soft-penalty | **非 PRIMARY**；若另窗启用连续 soft-penalty，须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP |
| 符号（C5） | 「高应计=剔除」；`q=0.20`；**禁**读收益改阈值/翻方向 |
| C11 | **禁**输出完整 CFACC/accrual_quality TopN 多空当本叶主 α；**禁**叶19/25 α 当主输入 |
| 再平衡 | 每 **20** 交易日（慢；对齐叶19/30–33） |
| 边界 | ≠叶19/25 完整应计主叶；≠accrual_quality TopN；≠叶30 CRR 主轴；≠两融/Amihud/解禁/hk_hold/moneyflow/ETF/问询函 |

---

## 2. 方向 / 符号（已冻结；禁事后切换）— **C1 / C5**

| 项 | **FROZEN** |
|---|---|
| 主规格 | 高应计尾部剔除（top_q=0.20 → mask=0） |
| 符号 | 「高应计=剔除」；冻结前**未**读本叶收益 |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改 q、改符号、改再平衡，或改为奖励高应计 |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选 q/方向 |

---

## 3. soft-penalty / 残差（C4 — 非 PRIMARY；启用另窗）

1. **PRIMARY = mask-only**（§1.2）：不做 SW+style 全残差。
2. **若另窗启用连续 soft-penalty**：同日 PRIMARY 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP；后加正交项须**补丁文件**。
3. 披露 vs 叶19 / 25 / 27 / 30 / 31 / 32 / 33 的 **Jaccard** 与 **ρ_excess**（C7）。
4. **禁**把叶19/25 α、叶30 CRR 主轴、两融/Amihud/解禁/hk_hold/moneyflow/ETF份额/问询函当本叶主输入（C11）。

---

## 4. 正交硬闸（C7 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **强度过滤**（披露） |
| 叶27 | 同上；禁 `on_minus_id` 主输入 |
| 叶30 CRR | 同上；禁多季 CRR 主轴当本叶主信号（允许同族数据源，交付必须是剔除 overlay） |
| 叶31 Amihud | 同上；禁冲击主输入 |
| 叶32 两融 | 同上；禁两融主输入 |
| 叶33 解禁 | 同上；禁 float_share 解禁主输入 |
| 叶25 尾窗 | COUNT 已披露样本日 2026-04-27 / 2026-10-09 的 `n_common=0`（ρ/J null）；**X2 前须解释**尾窗空交 |
| ρ_max vs25 | COUNT 披露单日 ρ_max≈0.5117>0.5；冻结/X2 **须披露**；规则为 ρ_mean 强度过滤 |
| 覆盖 | HI_LIQ 再平衡日可算 overlay 有效名 **median≥300**；FULLA 研究 **median≥800** |
| 换手/成本 | 评价口径 **30bp** |
| 正式重叠 | **X2 前须用完整 overlay 重算** vs 叶19/25/**27/30/31/32/33**；COUNT 轻量（仅 19/25）**不能替**正式重叠证明 |

COUNT 轻量摘要（APPROX，≠X2）：masked_median=**2431**；zero_frac=**0**；J20_max≈**0.053**≪0.7；ρ_mean≈**0.37**；peak≈**900**MB。

---

## 5. 宇宙双钉（C6 — HI_LIQ 主判决 + FULLA 研究）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | median≥**300** |
| **FULLA_V1** | **研究对照**（仅披露；不得静默改 PRIMARY） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | median≥**800** |

- **PRIMARY 不得静默改 FULLA**；FULLA 读数仅研究披露，不单独解阻 X2 ACCEPT。
- 两池规格**同时冻结**。

---

## 6. 窗 / 再平衡 / 交付 / rss（C9）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗 | **2024-06-03 → 2026-10-09**（与叶25/30–33 对齐） |
| 再平衡 | **20** 交易日 |
| top_q / 符号 | **0.20** / 高应计=剔除 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 exclusion mask**（HI_LIQ 主 + FULLA 研究）；非 Top-N 主叶；soft-penalty 非 PRIMARY |
| 判定路径 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED** |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C13 — 对齐 `alpha_decay_gate` v1.1 + 叶32 HOLD 教训）

叶32 HOLD `45dd87dc`：**decay=KEEP 仍不解阻** X2 ACCEPT。本叶把 KEEP 三闸合取写死：

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `alpha_decay_gate` v1.1 **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1：对 510300 去 β 后截距×252；若以叠加超额评价则同口径披露） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **`H2_net_cagr > 510300`** |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**；任一条不满足 → **最多 WATCH / HOLD** |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc`）；组合闸仅意图，冻结后另验 |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改 q/符号救闸 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | OCF/利润 PIT 日表 | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（PRIMARY；PIN `bb418e6a`） |
| 2 | HI_LIQ 掩码 | PRIMARY（§5） |
| 3 | FULLA 掩码 | 研究对照（§5） |
| 4 | SW L1 / style / 市值 | **仅** soft-penalty 另窗强制；mask-only PRIMARY 可后钉 |
| 5 | 叶19 / 25 / 27 / 30 / 31 / 32 / 33 α parquet | **仅** Jaccard/ρ；不进主信号 |
| 6 | （可选 OFF）BS WC_ACC/TA | 对照默认 OFF；启用须补丁+重计数 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造**。本拍**未**实算完整 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 完整 α 排序 | 本叶=**剔除 overlay**；不输出完整多空 α |
| accrual_quality | BS WC TopN 长端 | **不是**重开该主叶；无 TopN EW |
| 叶30 CRR+CFOOE | 多季转化率主 α | 本叶用单期 CF-accrual **水平**做剔除阈值 |
| 叶27 overnight−intraday | `on_minus_id` | 零隔夜−日内 |
| 叶31 Amihud | 冲击残差 | 不读冲击 |
| 叶32 两融 | 净流入残差 | 不读两融 |
| 叶33 解禁 | float_share 压力 | 不读解禁；正式 `afbbe7e7` UNCHANGED |
| 叶28/29 / `0087c928` | 另队 | **不夹带**（C10） |

**一句话分家**：叶19/25=应计完整 α；叶30=CRR；叶34=**HI_LIQ 高应计 top20% mask-only 剔除 overlay（非主 α）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C8）

forbid∋ 下列 sha8（**`245df63f`+`c5ed13df`+`5774bb6e` + 二十票 + 叶33 探针 `81521fb5`**）：

| sha8 | 备注 |
|---|---|
| `245df63f` | 主令点名 RESTORED |
| `c5ed13df` | 主令点名 RESTORED |
| `5774bb6e` | 叶32 selfcheck CONSUMED |
| `02426b73` | 二十票 |
| `4bb141c9` | 叶31 X2 selfcheck `.ok`（已 CONSUMED） |
| `fdbaa512` | 叶31 X2 构建 `.ok`（已 CONSUMED） |
| `aa25e989` | 叶30 X2 selfcheck `.ok`（已 CONSUMED） |
| `7e239487` | 禁复用旧窗 |
| `5af20222` | 禁复用旧窗 |
| `5ae077fa` | 禁复用旧窗 |
| `3c297052` | 二十票 |
| `e107383f` | 二十票 |
| `2be59acd` | 二十票 |
| `a7d98ac9` | 二十票 |
| `8e51de63` | 二十票 |
| `3a6caa4f` | 二十票 |
| `8bcd79dc` | 二十票 |
| `725be3e0` | 二十票 |
| `0f50daf7` | 二十票 |
| `3c19dd7d` | 二十票 |
| `1c32ab1e` | 二十票 |
| `6054b3bf` | 二十票 |
| `6de02e74` | 二十票 |
| **`81521fb5`** | 叶33 探针窗（已 CONSUMED；禁复用） |

合取串：`245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74` + **`81521fb5`**

另禁：
- 复用叶25 / 叶27 / 叶30 / 叶31 / 叶32 / 叶33 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS

---

## 11. 叶30 KEEP 修复 / 叶28/29 另队（C10）

- 叶30 衰减 KEEP 修复 DRAFT sha8 **`0087c928`**：**另队**；**不并入**本 FROZEN。
- 本拍**未打开/未审** `0087c928`。
- 叶28/29 仍 **FROZEN**；**不夹带、不升**本叶 PRIMARY。
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤。

---

## 12. C1–C13 对照表

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册 | **本文件**全文（符号/q/再平衡/失效/交付写死） |
| C2 | 正式脚本另窗 | `research/leaf34*` **ABSENT**（本拍禁落） |
| C3 | ocf/PIT/NP/period_basis | PIN **`bb418e6a`** 入钉；日表 YTD-ish；NP≤0 剔；PRIMARY 不用 BS WC |
| C4 | soft-penalty / mask-only | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW+style |
| C5 | top_q=0.20 符号冻结 | q=0.20；高应计=剔除；禁读收益改阈值/翻方向 |
| C6 | FULLA 双钉 | HI_LIQ PRIMARY median≥300 + FULLA 研究 median≥800；PRIMARY 不得静默改 FULLA |
| C7 | X2 前完整重叠 | vs 19/25/**27/30–33**；解释叶25 尾窗 n_common=0；披露 ρ_max vs25；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤 |
| C8 | forbid | §10 完整列表含 `81521fb5`；禁复用叶25/27/30–33 `.ok`；禁 `--arch-ok-path` |
| C9 | rss+peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | 另队 | `0087c928`/叶28/29 不夹带 |
| C11 | overlay≠应计主叶 | 交付=mask-only overlay；禁 CFACC/accrual_quality TopN 主 α；禁叶19/25 α 主输入 |
| C12 | APPROX≠X2 ACCEPT | COUNT gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke |
| C13 | decay KEEP | 近端=252d；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`） |

---

## 13. 失败截断

- 覆盖闸 HI_LIQ median<300 或 FULLA median<800 → 不申 `.ok` / 不宣称可交易
- Jaccard≥0.7 vs 叶19/25/27/30/31/32/33 → 硬拒，改机制或废叶
- 冻结后读收益改方向/q/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT；**KEEP 亦不解阻** X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT；无 peak_proof → 回执不完整
- 误读叶19/25 α 当主输入 / 偷看 `e_available_at>t` / 复开 accrual_quality 主叶 / 静默改 period_basis → 废叶
- 把 COUNT APPROX 当 X2 ACCEPT → 违规（C12）

---

## 14. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT fa6aa2e3 + COVER 76b37ca3 + COUNT 806e1758 / JSON 9730d432
  → Arch PASS_WITH_CONDITIONS 9d8a2f9e
      → 【本文件】PREREG_FROZEN（C1；mask-only PRIMARY；PIN C3 入钉）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf34_*（C2：本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED 245df63f+c5ed13df+5774bb6e+二十票+81521fb5）
                          → X2（完整重叠含 19/25/27/30–33；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| PIN C3 | **`bb418e6a`** |
| `research/leaf34*` 构建脚本 | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| COUNT APPROX | gate_pass=true；**≠X2 ACCEPT**（C12） |
| 叶30 KEEP `0087c928` | **另队不并入**（C10） |
| 叶28/29 | **仍 FROZEN**（不夹带） |
| 叶33 正式 `afbbe7e7` / 叶32 HOLD `45dd87dc` | **不回撤** |

---

## 15. 禁项清单（再钉）

- 本拍实跑 / 申 `.ok` / 落构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid（见 §10）含 `81521fb5`
- 冻结后改 q / 符号 / 再平衡；读收益翻号
- 卖方/金股/survey/TP/LLM 权重当 α；GP/高杠杆；moneyflow 80/20
- 重开 accrual_quality / 叶19 / 叶25 应计主叶；叶19/25 α 当主输入
- ETF 份额 / 问询函当本叶主信号（备选另节不升）
- PRIMARY 静默改 FULLA；COUNT APPROX 当 X2 ACCEPT
- 并入 `0087c928`；夹带叶28/29；改叶33 正式 `afbbe7e7`
- `live=true` / `promotion_approved=true` / 声称 X2 ACCEPT / 报 Leo

---

## 16. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` |
| 状态 | **FROZEN**（PREREG_FROZEN） |
| mechanism_tag | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| PRIMARY 交付 | **mask-only**；top_q=**0.20**；高应计=剔除 |
| soft-penalty | 非 PRIMARY（启用须 SW+style） |
| 再平衡 / X2 窗 / 成本 | **20** / **2024-06-03→2026-10-09** / **30bp** |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| C3 PIN | `bb418e6a`（日表 YTD-ish；NP≤0 剔） |
| decay KEEP | latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端=252d；**KEEP 不解阻** X2 ACCEPT |
| forbid | §10 含 `81521fb5` |
| rss / peak_proof | 1500 / REQUIRED |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| Arch / WHO / COVER / COUNT / JSON | `9d8a2f9e` / `fa6aa2e3` / `76b37ca3` / `806e1758` / `9730d432` |
| 上下文 | 叶33 `afbbe7e7` UNCHANGED；叶32 HOLD `45dd87dc`（不回撤） |
| ok_requested / EXECUTED / 脚本本拍 | false / false / 无 |
| live / promotion / ≠X2 ACCEPT / leo_notify | false / false / true / false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
