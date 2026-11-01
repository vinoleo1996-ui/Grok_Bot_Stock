# 【FROZEN 预注册 2026-10-27 13:03 ET】叶35：ETF 申赎→成分股被动资金压力 overlay（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 13:03 ET**（America/New_York；ISO `2026-10-27T13:03:36-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER/COUNT **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 λ/q/方向。
- 主令：2026-10-27 ~12:57 ET — Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`ee7ec307`** → 令 AI 出 FROZEN 预注册（C1–C13 入钉；不 HOLD）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`ee7ec307`**（全长 `ee7ec307e22bb5e6b98b6521d76e5f62a04311ffc9917efafde24524861a6f93`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`05942769`**（全长 `0594276917a88969456ed3b7103d7f51ca26d4b2923125295507f1a8f2802997`）
  - COVER DRAFT：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` sha8 **`f41d7db8`**（全长 `f41d7db8f0632a8433972def18bd92b6f76f625fdabd9603b5fe18be74ca92a1`）
  - COUNT RECEIPT：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` sha8 **`cbca88e7`**（全长 `cbca88e797c4c423e082d8db189ef1e0265747e90990817bbfd823f09798b431`）
  - COUNT JSON：`output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` sha8 **`a17b75fb`**（全长 `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6`）
  - 计数脚本（迁仓）：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` sha8 **`4e964d40`**（全长 `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538`；自 `/tmp/quantlab_leaf35_etf_passive_flow_pressure_count_gate.py` 字节复制，内容不变）
  - PIN（C3）：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` sha8 **`dd17044a`**（全长 `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36`）
- 路径说明：主令亦写 `docs/v2/AI_LEAF35_…_PREREG_*_FROZEN_*_ZH.md` 惯例；**本拍优先落 `docs/v2/audit/`（与叶34 同目录）**；不另写双份冲突副本。
- 对照形态：叶34 PREREG_FROZEN `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md`（`8be1099e`；结构对齐；内容换叶35）。
- 叶号：**叶35**；mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；叶28/29 仍 FROZEN 另队；叶26 BROAD_ETF_FLOW **DRAFT 另队勿重开同构**；叶25/27/30–34 已占轴只读对照。
- 叶34 HOLD CLOSED（`.ok` `178e90e9` / lift `3fce510e` / 回执 `a37257b9`）**不回撤**；叶33 正式 `afbbe7e7` UNCHANGED；叶32 HOLD `45dd87dc` **不回撤**。
- **本冻结 ≠ `.ok` / ≠ 正式构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无** `research/leaf35*`（ABSENT 预期）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`（叶35）  
> **who_pays（一句）**：付钱的是在宽基 ETF 大额申赎日、忽视「产品层份额变化→篮子权重」机械冲击、仍给高被动压力名足额权重的持仓者——压力 overlay 剔除后，主干少踩 AP 篮子冲击。  
> **可检验预测（已冻结）**：PRIMARY 交付 = **mask-only** 日度 exclusion mask（池内 `|pressure_raw|` top_q=**0.20** 高绝对被动压力名 `mask=0`，其余可算名 `mask=1`；不可算/不可映射名不进有效集、不填假 0）；**叠主干**；**不是**叶26 `g1g5_ashare_broad_etf_flow_stock_v1` 完整多层残差 α 主叶；**不是**交易 ETF。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃集 vs moneyflow_resid Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；vs 叶26 残差 α（若落盘）同硬拒精神；另须完整重叠 vs 叶8a（若有）/25/27/30–34；HI_LIQ 再平衡日可映射压力名 median≥300；FULLA 研究对照 median≥800。  
> **失效条件**：退化为叶26 完整多层残差 α 主叶；或与 moneyflow_resid Jaccard≥0.7；或主信号混入个股 moneyflow / 行业 ETF 持仓 / 卖方/金股/TP/LLM；或冻结后事后改 top_q / 翻转剔除方向读收益；或用 `weight_available_at > t` / `available_at > t` 偷看；或把本 overlay 伪称「全新 ETF α」掩盖与叶26 raw 同幅；或 PRIMARY 静默改 FULLA；或把 COUNT APPROX gate_pass 当 X2 ACCEPT；或 KEEP 被误读为解阻 ACCEPT。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（ETF 被动压力 overlay；慢）— **FROZEN**

在 PRIMARY 池（HI_LIQ）上，用宽基 ETF 份额 PIT × 指数权重方案 A PIT 定义个股被动资金压力，并做截面高 `|pressure|` 剔除。

对每个再平衡日 \(t\)：

$$
\mathrm{pressure\_raw}_{i,t} = \sum_{e\in\mathcal{E}} w\big(i,\mathrm{index}(e),\mathrm{asof\_PIT}(t)\big) \times \mathrm{flow\_est\_proxy}(e,t)
$$

其中 \(\mathcal{E}=\{510300.\mathrm{SH},510500.\mathrm{SH},512100.\mathrm{SH}\}\)；`flow_est_proxy` = 有限 `flow_est_wan_yuan`，否则 `d_share_wan`；权重/份额 PIT 见 PIN C3。

### 1.1 C3 数据 / 权重方案 A / 份额 PIT（PIN 入钉）

PIN 决议 **`dd17044a`** 写死：

| 项 | **FROZEN** |
|---|---|
| 权重路径 | `data/v2/index_members/index_weight_csi300_500_1000.parquet`（189,000 行；sha8 `d543a485`；列无 `available_at`） |
| **方案 A** | 月末 `trade_date` 点 → **次月首个交易日 09:00 Asia/Shanghai** 为 `weight_available_at`（**交易日历** `trade_cal_sse_pit`，非纯日历日）；再平衡仅用 `weight_available_at ≤ t_ts` |
| 份额路径 | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（sha8 `a3eac35b`） |
| 份额 PIT | `available_at ≤ t_ts` 写死；禁偷看 |
| 映射 | 510300↔000300；510500↔000905；512100↔000852 |
| 权重单位 | percent_div100（与 COUNT JSON 对齐） |
| **禁** | 静默沿用月末向后 asof 当 PIT 完备；行业 ETF 主轴 |

### 1.2 剔除规则 / 交付（C4 / C5 / C11 — **mask-only PRIMARY**）

$$
\mathcal{H}_t = \{i\in\mathrm{PRIMARY}_t\cap\mathrm{mappable}_t:\; |\mathrm{pressure\_raw}_{i,t}| \ge Q_{1-q}(|\mathrm{pressure\_raw}|_{\cdot,t})\}
\quad q=0.20
$$

| 项 | **FROZEN** |
|---|---|
| **PRIMARY 交付** | **mask-only**：可算名 \(i\in\mathcal{H}_t\) → `mask=0`；其余可算名 → `mask=1`；不可算/不可映射名 **不进有效集、不填假 0**；**叠主干** |
| 明示（C4） | **mask-only PRIMARY**（与 COUNT 剔除路径一致）；截面 `|pressure|` 分位阈值剔除 |
| soft-penalty | **非 PRIMARY**；若另窗启用连续 soft-penalty，须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP |
| 符号（C5） | 「高 `|pressure|`=剔除」；`q=0.20`；**禁**读收益改阈值/翻方向；行业 ETF 禁主轴 |
| C11 | 交付=形态 A **mask-only overlay 叠主干**；**禁**输出叶26 `g1g5_ashare_broad_etf_flow_stock_v1` 完整多层残差 α 当本叶主 α；**禁** moneyflow / 行业 ETF 持仓主输入；raw 同幅须持续披露 |
| 再平衡 | 每 **20** 交易日（慢；对齐近叶） |
| 边界 | ≠叶26 完整残差 α 主叶；≠叶8a/叶4 交易 ETF；≠moneyflow 主轴；≠叶25/27/30–34 各自主轴换皮 |

---

## 2. 方向 / 符号（已冻结；禁事后切换）— **C1 / C5**

| 项 | **FROZEN** |
|---|---|
| 主规格 | 高绝对被动压力尾部剔除（top_q=0.20 → mask=0） |
| 符号 | 「高 `|pressure|`=剔除」；冻结前**未**读本叶收益 |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改 q、改符号、改再平衡，或改为奖励高压力 |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选 q/方向 |

---

## 3. soft-penalty / 残差（C4 — 非 PRIMARY；启用另窗）

1. **PRIMARY = mask-only**（§1.2）：不做 SW+style 全残差。
2. **若另窗启用连续 soft-penalty**：同日 PRIMARY 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP；后加正交项须**补丁文件**。
3. 披露 vs moneyflow_resid / 叶26 残差 α（若有）/ 叶8a（若有）/ 叶25/27/30–34 的 **Jaccard** 与 **ρ_excess**（C7）。
4. **禁**把个股 moneyflow、叶26 完整残差 α、行业 ETF 持仓、两融/Amihud/解禁/应计/hk_hold 当本叶主输入（C11）。

---

## 4. 正交硬闸（C7 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| moneyflow_resid | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **强度过滤**（披露）；禁个股 moneyflow 主输入 |
| 叶26 残差 α（若落盘） | Jaccard≥0.7 → **硬拒**；**禁**重开完整残差 α 主叶同构 |
| 叶26-like raw 诊断 | COUNT 已披露 J 可=1.0（by construction）；**不得**当硬拒，也**不得**当正交已证；raw 同幅持续披露 |
| 叶8a | 禁交易行业 ETF；股票 Jaccard 若有则同硬拒精神；本拍 GAP 未伪造 |
| 叶25 / 27 / 30 / 31 / 32 / 33 / 34 | X2 前完整重叠 Jaccard/ρ；禁各自主轴换皮；叶34 HOLD CLOSED / 叶33/32 HOLD **不回撤** |
| 覆盖 | HI_LIQ 再平衡日可映射压力名 **median≥300**；FULLA 研究 **median≥800** |
| 换手/成本 | 评价口径 **30bp** |
| 正式重叠 | **X2 前须用完整 overlay 重算** vs moneyflow / 叶26 残差（若有）/ 8a（若有）/ **25/27/30–34**；COUNT 轻量 **不能替**正式重叠证明 |

COUNT 轻量摘要（APPROX，≠X2）：masked_median=**1552.5**；zero_frac=**0**；J20_max vs moneyflow=**0.25**≪0.7；ρ_mean≈**−0.080**；peak≈**566**MB；叶26 残差 α / 叶8a **GAP**。

---

## 5. 宇宙双钉（C6 — HI_LIQ 主判决 + FULLA 研究）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（sha8 `c5433e80`） | median≥**300** |
| **FULLA_V1** | **研究对照**（仅披露；不得静默改 PRIMARY） | `output/strategy_fulla/universe_mask_fulla_v1.parquet`（sha8 `b5d9f1ab`） | median≥**800** |

- **PRIMARY 不得静默改 FULLA**；FULLA 读数仅研究披露，不单独解阻 X2 ACCEPT。
- 两池规格**同时冻结**。

---

## 6. 窗 / 再平衡 / 交付 / rss（C9）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗 | **2024-06-03 → 2026-10-09**（与叶25/30–34 对齐） |
| 再平衡 | **20** 交易日 |
| top_q / 符号 | **0.20** / 高 `|pressure|`=剔除 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 exclusion mask**（HI_LIQ 主 + FULLA 研究）；形态 A overlay 叠主干；非叶26 完整 α；soft-penalty 非 PRIMARY |
| 判定路径 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED** |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C13 — 对齐 `alpha_decay_gate` v1.1 + 叶32/34 教训）

叶32 HOLD `45dd87dc` / 叶34 HOLD CLOSED `178e90e9`：**decay=KEEP 仍不解阻** X2 ACCEPT。本叶把 KEEP 三闸合取写死：

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `alpha_decay_gate` v1.1 **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1：对 510300 去 β 后截距×252；若以叠加超额评价则同口径披露） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **`H2_net_cagr > 510300`** |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**；任一条不满足 → **最多 WATCH / HOLD** |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32 `45dd87dc` / 叶34 `178e90e9`）；组合闸仅意图，冻结后另验 |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改 q/符号救闸 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | 宽基份额流 | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（PRIMARY；`available_at≤t`） |
| 2 | 指数权重 | `data/v2/index_members/index_weight_csi300_500_1000.parquet`（方案 A synthetic `weight_available_at`；PIN `dd17044a`） |
| 3 | 交易日历 | `data/v2/calendar/trade_cal_sse_pit.parquet`（方案 A） |
| 4 | HI_LIQ 掩码 | PRIMARY（§5） |
| 5 | FULLA 掩码 | 研究对照（§5） |
| 6 | SW L1 / style / 市值 | **仅** soft-penalty 另窗强制；mask-only PRIMARY 可后钉 |
| 7 | moneyflow_resid / 叶26 残差α / 8a / 25/27/30–34 α | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造**。叶26 残差 α / 叶8a 本拍 **GAP**（COUNT 已诚实）。本拍**未**实算完整 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| **叶26** BROAD_ETF_FLOW | 宽基流量→完整多层残差 α 主叶 | 本叶=**mask-only overlay 叠主干**；不输出完整残差 α |
| 叶8a / 叶4 | 交易行业 ETF | 本叶评分对象=**股票暴露 overlay**；不交易 ETF |
| moneyflow_resid | 个股主力净流入残差 | 本叶主轴=ETF **产品层**份额×权重；moneyflow 禁主输入 |
| 叶34 高应计剔除 | OCF/NP 尾部剔除 | 不读财务应计；叶34 HOLD CLOSED 不回撤 |
| 叶33 解禁 | float unlock | 不读解禁；正式 `afbbe7e7` UNCHANGED |
| 叶32 两融 / 叶31 Amihud / 叶30 CRR / 叶27 on−id / 叶25 cfacc | 各已占 | 零两融/冲击/CRR/隔夜/应计 |
| 叶28/29 / `0087c928` | 另队 | **不夹带**（C10） |

**一句话分家**：叶26=宽基流量完整残差 α；叶35=**HI_LIQ 高 `|pressure|` top20% mask-only 被动压力 overlay（非主 α）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C8）

forbid∋ 下列 sha8（**`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5` + 二十票**）：

| sha8 | 备注 |
|---|---|
| **`178e90e9`** | 叶34 X2 selfcheck `.ok`（HOLD CLOSED CONSUMED；禁 RESTORED） |
| **`c1b71e64`** | 主令点名 RESTORED |
| `245df63f` | 主令点名 RESTORED |
| `c5ed13df` | 主令点名 RESTORED |
| `5774bb6e` | 叶32 selfcheck CONSUMED |
| **`81521fb5`** | 叶33 探针窗（已 CONSUMED；禁复用） |
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

合取串：`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`

另禁：
- 复用叶25 / 叶27 / 叶30 / 叶31 / 叶32 / 叶33 / 叶34 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS；RESTORED 上列任一票

---

## 11. 叶30 KEEP 修复 / 叶28/29 另队（C10）

- 叶30 衰减 KEEP 修复 DRAFT sha8 **`0087c928`**：**另队**；**不并入**本 FROZEN。
- 本拍**未打开/未审** `0087c928`。
- 叶28/29 仍 **FROZEN**；**不夹带、不升**本叶 PRIMARY。
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 叶34 HOLD CLOSED（`178e90e9`/`3fce510e`/`a37257b9`）不回撤。
- 叶26 BROAD_ETF_FLOW **另队 DRAFT**；本叶只反同构 overlay，**不**代跑叶26。

---

## 12. C1–C13 对照表（Arch `ee7ec307` §3 全文入钉）

| # | 条件（Arch §3） | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册（mechanism/公式/窗/再平衡/交付/判定） | **本文件**全文 |
| C2 | 正式脚本另窗；/tmp 计数迁仓或重钉 | `research/leaf35*` **ABSENT**（本拍禁落构建脚本）；计数脚本已迁仓 **`4e964d40`** → `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` |
| C3 | 权重 asof APPROX→方案 A；份额 `available_at≤t` | PIN **`dd17044a`**：次月首个**交易日** 09:00 Asia/Shanghai synthetic `weight_available_at`；份额 PIT 写死；禁静默 APPROX |
| C4 | soft-penalty 须 SW+style；或明示 mask-only | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW L1+log 市值+mom20/vol20/logADV20 |
| C5 | top_q=0.20 符号冻结；行业 ETF 禁主轴 | q=0.20；高 `|pressure|`=剔除；禁读收益改阈值/翻方向；宽基三件套冻结 |
| C6 | HI_LIQ PRIMARY + FULLA 研究双钉 | HI_LIQ mask hiliq_v1 median≥300 + FULLA mask fulla_v1 median≥800；PRIMARY 不得静默改 FULLA |
| C7 | X2 前完整重叠；轻量不替；leaf26-like J=1.0 不得当硬拒或正交已证 | vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–34；COUNT 轻量不替；诊断 J=1.0 纪律入钉 |
| C8 | forbid 全集；禁复用叶25/27/30–34 `.ok`；禁 `--arch-ok-path`；禁 RESTORED | §10 完整列表含 `178e90e9+c1b71e64+…+6de02e74` |
| C9 | rss=1500 + peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | `0087c928`/叶28/29 另队不夹带 | §11 |
| C11 | overlay≠叶26 完整残差 α；禁 moneyflow/行业 ETF 持仓主输入；raw 同幅持续披露 | 交付=形态 A mask-only overlay 叠主干；§1.2/§9 |
| C12 | APPROX 计数 ≠ X2 ACCEPT / Book-Smoke / 升纸面 | gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** ACCEPT |
| C13 | decay KEEP 口径；KEEP 不解阻 ACCEPT | 近端=252d（≥126 才出 α）；KEEP=`latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；KEEP 不解阻（叶32/34 教训） |

---

## 13. 失败截断

- 覆盖闸 HI_LIQ median<300 或 FULLA median<800 → 不申 `.ok` / 不宣称可交易
- Jaccard≥0.7 vs moneyflow / 叶26 残差 α（若有）/ 相关叶 → 硬拒，改机制或废叶
- 退化为叶26 完整残差 α 主叶 → 废叶
- 冻结后读收益改方向/q/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT；**KEEP 亦不解阻** X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT；无 peak_proof → 回执不完整
- 误读 moneyflow / 行业 ETF 持仓当主输入 / 偷看 future 权重或份额 / 静默沿用 APPROX 权重 asof → 废叶
- 把 COUNT APPROX 当 X2 ACCEPT → 违规（C12）

---

## 14. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT 05942769 + COVER f41d7db8 + COUNT cbca88e7 / JSON a17b75fb / 脚本 4e964d40
  → Arch PASS_WITH_CONDITIONS ee7ec307
      → 【本文件】PREREG_FROZEN（C1；mask-only PRIMARY；PIN C3 方案 A 入钉）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf35_*（C2：本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED 178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票）
                          → X2（完整重叠含 moneyflow/叶26残差/8a/25/27/30–34；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| PIN C3 | **`dd17044a`**（方案 A） |
| 计数脚本迁仓 | **`4e964d40`**（audit/；非正式构建） |
| `research/leaf35*` 构建脚本 | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| COUNT APPROX | gate_pass=true；**≠X2 ACCEPT**（C12） |
| 叶30 KEEP `0087c928` | **另队不并入**（C10） |
| 叶28/29 | **仍 FROZEN**（不夹带） |
| 叶33 正式 `afbbe7e7` / 叶32 HOLD `45dd87dc` / 叶34 HOLD CLOSED | **不回撤** |

---

## 15. 禁项清单（再钉）

- 本拍实跑完整 α / 申 `.ok` / 落 `research/leaf35*` 构建脚本 / 挂 QUIET / 抬 RSS / git commit / 改 TEAM_STATE
- RESTORED forbid（见 §10）含 `178e90e9`+`c1b71e64`
- 冻结后改 q / 符号 / 再平衡；读收益翻号
- 卖方/金股/survey/TP/LLM 权重当 α；GP/高杠杆；moneyflow 80/20
- 重开叶26 完整残差 α 主叶；交易行业 ETF；moneyflow / 行业 ETF 持仓主输入
- 静默沿用权重 APPROX asof 当 PIT 完备
- PRIMARY 静默改 FULLA；COUNT APPROX 当 X2 ACCEPT；KEEP 当 ACCEPT
- 并入 `0087c928`；夹带叶28/29；改叶33 正式 `afbbe7e7`
- `live=true` / `promotion_approved=true` / 声称 X2 ACCEPT / 报 Leo

---

## 16. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` |
| 状态 | **FROZEN**（PREREG_FROZEN） |
| mechanism_tag | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1` |
| PRIMARY 交付 | **mask-only**；top_q=**0.20**；高 `|pressure|`=剔除；叠主干 |
| soft-penalty | 非 PRIMARY（启用须 SW+style） |
| 再平衡 / X2 窗 / 成本 | **20** / **2024-06-03→2026-10-09** / **30bp** |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| C3 PIN | `dd17044a`（方案 A：次月首个交易日 09:00 Asia/Shanghai） |
| 计数脚本迁仓 | `4e964d40` |
| decay KEEP | latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端=252d；**KEEP 不解阻** X2 ACCEPT |
| forbid | §10 含 `178e90e9+c1b71e64+…` |
| rss / peak_proof | 1500 / REQUIRED |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| Arch / WHO / COVER / COUNT / JSON | `ee7ec307` / `05942769` / `f41d7db8` / `cbca88e7` / `a17b75fb` |
| 上下文 | 叶33 `afbbe7e7` UNCHANGED；叶32 HOLD `45dd87dc`；叶34 HOLD CLOSED `178e90e9`（不回撤） |
| ok_requested / EXECUTED / 正式脚本本拍 | false / false / 无（ABSENT） |
| live / promotion / ≠X2 ACCEPT / leo_notify | false / false / true / false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
