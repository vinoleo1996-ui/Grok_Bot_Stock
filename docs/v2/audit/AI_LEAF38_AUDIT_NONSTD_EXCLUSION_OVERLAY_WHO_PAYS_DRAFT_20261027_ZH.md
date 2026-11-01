# 【DRAFT — NOT FROZEN】叶38 who_pays：非标审计意见剔除 overlay（主干负向过滤）

- 角色：QuantLab AI（执行器）
- 时点：2026-10-27 20:42 ET（America/New_York）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选窗；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑。
- 叶号意向：**叶38**（叶37 IMAX/隔夜彩票剔除 HOLD CLOSED：Alpha `384fb9db` / Arch `4afd5ae1`；禁复跑 `015e6f06`/`32605aca`/`108aba8f`/`57ab9096`）。
- dig：盘上 sha8 **`fa973826`**（全长 `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`；文内自称 `a6ddc4ef` **勿采**）。
- 旁线：fund_portfolio 计数附录 **gate_pass=false**（口径未齐；缺主动权益 fund_basic）；本叶 = dig 备选「非标审计意见剔除 overlay」。
- 禁：GP / 高杠杆 / 教科书量价主线；卖方/金股/TP/LLM；把本叶做成完整多空 α 主叶；复跑叶18/24/25/27/30–37；禁自签 `.ok`；禁自派 X2；禁 Book-Smoke；禁改叶37 产物。
- `live=false`；`promotion=false`；`leo_notify=false`；**≠X2 ACCEPT**。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`（叶38 意向）  
> **who_pays（一句）**：付钱的是忽视非标审计意见（保留/无法表示/否定/带强调事项段等）仍给涉事名足额权重的持仓者——剔除后主干少踩财务鉴证雷。  
> **可检验预测**：交付形态 **A** = 日度 exclusion mask（最新可用审计意见为非标 → HI_LIQ 名 `mask=0`）；**不是**完整多空 α 主叶。判定：ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干；活跃剔除集 vs negevent **与** 叶36 Jaccard **任一 >0.5 硬拒**。厚度闸写死：触窗日剔除名全日 **median≥30** 且 **≥60% 交易日剔除名≥10** 且 zero_frac≤0.50（**勿盲抄** median≥300；叶36 median=6 FAIL 教训）。本拍轻量计数：**gate_pass=`true`**（median=48.0；frac_ge10=1.0；jmax_neg≈0.0562；jmax_l36≈0.0649；peak_rss≈1584.4MB）。  
> **失效条件**：退化为完整事件多空 α；或 vs negevent/叶36 Jaccard>0.5；或用标准无保留意见当剔除；或偷看 `available_at > t`；或把 ETF/应计/问询函/IMAX 换皮当本叶主输入；或冻结后事后改定义读收益。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 轻量计数闸。

---

## 1. 选型理由（PRIMARY = 非标审计意见剔除 overlay）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| **negevent** | E1–E4 剪枝（已 FAIL） | 本叶事件=审计意见非标 PIT 状态；Jaccard>0.5 硬拒 |
| 叶36 问询函剔除 | 财务问询/关注函短窗 | 源不同（audit_opinion vs inquiry_letter）；Jaccard>0.5 硬拒；叶36 覆盖 FAIL 不回撤 |
| 叶37 IMAX/彩票剔除 | 隔夜 idio 波动 | 本叶**不**读收益/波动；叶37 HOLD CLOSED 不回撤 |
| 叶34 高应计 / 叶35 ETF 压力 / 叶33 解禁 / 叶32 两融 / 叶31 Amihud / 叶30 CRR / 叶27 on−id / 叶25 / 叶24 / 叶18 | 各已占 | 本叶主轴=审计鉴证非标剔除；零应计/ETF/解禁/两融/冲击/CRR/隔夜/量价主线 |
| fund_portfolio | 主动权益持仓边际 | **口径未齐 FAIL**（本拍附录）；不夹带 |

**PRIMARY 选定**：`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`（只作负向剔除 overlay，挂 capacity_adv / HI_LIQ；**非主线因子**）。

---

## 2. 机制与 PIT

**源**：`data/v2/audit/audit_opinion_pit_tushare.parquet`  
字段：`ts_code` / `instrument_id` / `available_at`（Asia/Shanghai）/ `audit_result` / `is_non_standard` / …  
盘上：总行≈56144；**非标 2621** 行 / **895** 只；`is_non_standard=True` ∈ {带强调事项段的无保留意见, 保留意见, 无法表示意见, 否定意见, …}。

**PIT 状态定义（DRAFT 写死；不读收益选窗）**：

1. 将 `available_at` 归一日 D；**T1** = 日历上严格 >D 的第一个交易日（与叶36 同构 T1 规则）。  
2. 对每个 HI_LIQ 名、每个交易日 t：取全部 `T1 ≤ t` 的审计意见中**最新**一条；若该条 `is_non_standard=True` → **剔除**（mask=0）。  
3. 下一份意见（无论标准/非标）的 T1 起改判。  
4. 映射键：`ts_code`（如 `600829.SH`）对齐 HI_LIQ `instrument`；**不用** `instrument_id`（`sh.600829`）硬拼。

**交付形态 A**：日度 exclusion mask 叠主干；**不是** TopN 慢再平衡主叶；可选 soft-penalty=`-1`（本拍不做）。

---

## 3. 失败条件（读收益前写死）

1. 逐日 Jaccard vs negevent 剔除集 **或** 叶36 问询函剔除集，硬指标=触窗日 **max >0.5** → **同构硬拒**。  
2. 厚度闸 FAIL：全日触窗剔除名 **median <30** 或 **frac(日剔除名≥10) <0.60** 或 zero_frac>0.50 → 不过（**禁止**事后改成 median≥300 或放宽到 median≥6）。  
3. ρ_excess vs capacity_adv ≥0.5 → 不过（X2 阶段）。  
4. 残差 α≤0 或组合门不过 → 不过（X2）。  
5. peak RSS >1.5GB（正式跑）→ 不过；本拍计数 peak≈1584.4MB → **WATCH**（须压峰后再申 `.ok`）。  
6. 衰减门非 KEEP / 不可交易 → 不过。

---

## 4. 数据 / 宇宙 / 窗

| 项 | 值 |
|---|---|
| 宇宙 | **HI_LIQ**（`universe_mask_hiliq_v1.parquet`） |
| X2 样内窗意向 | **2024-06-03 → 2026-10-09**（与叶36 同；本拍只计数） |
| 密封窗 | 若用 2018→2024-05：**只计数、不读收益** |
| 输入 sha8（计数拍） | audit=`7d0af2e4`；hiliq=`c5433e80`；cap=`4348877e`；neg_w=`e19e1dc4` |

---

## 5. 本拍计数结论（摘要）

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| gate_cov_pass | `true`（median=48.0；frac_ge10=1.0；zero_frac=0.0） |
| hard_reject_jaccard | `false`（jmax_neg≈0.056180；jmax_l36≈0.064935） |
| peak_rss_mb | 1584.4（>1500 → WATCH；计数拍未抬限） |
| 未算 | 收益/IC/CAGR/PnL；未申 `.ok`；未开 X2 |

详 COUNT RECEIPT / JSON。

---

## 6. 禁项与下一跳

- 禁自签 `.ok`；禁自派 X2；禁 Book-Smoke；禁改叶37；禁 GP/高杠杆。  
- 下一跳：请主裁 — **(A)** Data 另补 fund_basic 主动权益；**(B)** Arch 审叶38 DRAFT→是否升 FROZEN/排脚本；**(C)** HOLD。本执行器**不自升** FROZEN、**不**申 `.ok`。
