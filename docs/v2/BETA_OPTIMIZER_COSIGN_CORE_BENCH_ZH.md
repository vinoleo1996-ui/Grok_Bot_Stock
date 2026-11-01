# Beta 共签 · Core 对标补丁 v1.1（双口径 / Sharpe·MDD·IR）

- **时间**：2026-10-14 ≈08:21 ET
- **对象**：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` §5.1–§5.3（≈08:21 主 Agent 采纳 Arch 补丁）
- **上游 HARD**：`BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`（浓缩 Core：单票 5%/6%、Neff 20–30、行业±8%/绝对≤20%、Size/MidCap±0.35σ+Slack、两步整手、β|β−1|≤0.10、L1-only、wb=float_mktcap_hiliq）——**本补丁不改 HARD**
- **状态**：**CONDITIONAL_COSIGN_CORE_CONC_V1_1**（bench patch；结构 ACCEPT；**仍非** FULL_COSIGN / **仍非** FROZEN）
- **升 FROZEN 剩余闸**：Eng 密封窗 λ（NEW HARD，双口径报告层）+ Leo/主 Agent 过关
- **live / promotion**：false / false；**不跑**优化器；**不改** FROZEN 纸面

---

## 总裁决

| # | Strategy §5 提案 | Beta 裁决 | 一句话 |
|---|---|---|---|
| (1) | Core **只对标** capacity_adv；主指标 **Sharpe / MDD / IR**（CAGR/Calmar/胜率仍报、非主排序） | **ACCEPT** | B4 主对决不进 Core |
| (2) | 双口径必报：①纯股票 100%；②80% 股票 + 20% 510300；**主表=②**；**禁止**用①绝对 MDD/Sharpe 比 capadv 总账 | **ACCEPT** | ①仅分解；公平对标在② |
| (3) | α 表述 = **抬 Sharpe / 压 MDD**（相对同口径 capadv 目标带）；**不作**「α≥8%+」设计输入 | **ACCEPT** | 目标区间非硬门槛 |
| (4) | Stage1 冻+只跑 Core、纸面底仓不动；Stage2 Full↔B4；Stage3 才议换垫仓 | **ACCEPT** | 本共签范围 = Stage1 |

**整体共签栏**：**CONDITIONAL_COSIGN_CORE_CONC_V1_1**。HARD 沿用 CORE_CONC；本文件只锁对标/记分/阶段。不升 FULL / 不 FROZEN，直至 Eng λ 落盘（可接受单点）+ Leo 过关。之后按 Leo：**先跑 Core**（双口径报告）。

---

## (1) 对标对象与主指标 — **ACCEPT**

| 项 | 写死 |
|---|---|
| 对标 | Core **仅** vs **capacity_adv**（Top-25 书结构）；**不做** vs B4 主对决（B4→Full） |
| 主指标 | **Sharpe、MDD、IR**（IR = 相对同口径基准的信息比率） |
| 次报 | CAGR、Calmar、日/月胜率、换手、成本、填单、Neff |
| 年化 | **244** 交易日；公式须在 Core 报告标注；若记分卡缺字段 → Eng **补算** |

**ACCEPT 理由**：主排序用风险调整收益 + 回撤，避免 CAGR 单点诱导；与 Mandate MDD 预算一致。

---

## (2) 双口径报告 — **ACCEPT**

| 口径 | 构造 | 用途 |
|---|---|---|
| **① 纯股票 100%** | 优化器股票权重 renormalize→100%（无 510300） | 分解选股/约束；**非**主结论 |
| **② 80/20 + 510300** | 股票袖 80% + **510300 固定 20%**（与 capadv 书同形） | **主对标表**；与 capacity_adv 并排 |

**强制规则（共签）**：
1. ①② 均报 **60万 ∧ 100万** ×（密封窗披露 + X2 样本内）。
2. **主结论表 = ②**；①不得单独宣称「跑赢 capadv」。
3. **禁止**用①的绝对 MDD / Sharpe **直接**对比含 20% 510300 的 capacity_adv 总账。
4. 510300 **只在报告层套袖**；**不进**优化器 HARD；求解仍在 HI_LIQ、\(w_b\)=池内流通市值加权。

---

## (3) α 表述 — **ACCEPT**

- 设计/沟通用语：**抬 Sharpe / 压 MDD**（相对 **同口径** capacity_adv 的目标带）。
- **禁止**把「α≥8%+」或固定超额点写成优化器输入、HARD、或晋级门槛。
- 过门比较在 **口径②** 上相对 capadv；数值带见 `BETA_CORE_ACCEPT_GATES_PENDING_ZH.md`（PENDING，冻后才量）。

---

## (4) Stage1–3 — **ACCEPT**

| 阶段 | 内容 | 本共签 |
|---|---|---|
| **Stage1** | 纸面底仓（FROZEN_CONFIG / capacity_adv / B4 / S6）**不动**；浓缩 Core 冻后只跑；双口径对标 capadv；禁 LLM / 禁换垫仓 | **本范围** |
| **Stage2** | Full ↔ B4（事件/门卫）；不回贴 Core 选参 | 后置 |
| **Stage3** | 才考虑替换 20% 510300 垫仓 | 后置；须独立预注册 |

---

## HARD 继承（不变）

自 `CONDITIONAL_COSIGN_CORE_CONC`：**单票 100万 5% / 60万 6%**；**Neff 20–30**；**行业 ±8% / 绝对≤20%**；**Size/MidCap ±0.35σ + Slack**（Size/Mid≤0.05σ；行业≤1pp；绝对20%/单票/Neff/β = 0 Slack）；**两步截断 + 科创 200 整手**；**β |β−1|≤0.10 vs \(w_b\)**；纸面仍报 vs 510300 **[0.70, 1.00]**；**仅 L1**；INFEASIBLE **不松** HARD；Path A 桶锁建议保留。

---

## Eng λ 与阻塞（披露，非本补丁改 HARD）

| 项 | 状态（≈08:21 ET 核） |
|---|---|
| 交接 | `docs/v2/STRATEGY_OPTIMIZER_LAMBDA_CALIB_HANDOFF_ZH.md` |
| 目录 | `output/strategy_optimizer/calib/` |
| 文件 | `calib_meta.json` + `calib_lambda_risk.json` + `calib_lambda_turn_60w.json` + `calib_lambda_turn_100w.json` **已落盘** |
| 可用 λ | **否**：`lambda_risk` / `lambda_turn_*` = **null**；risk/turn JSON `status=FAILED` |
| 原因摘要 | Neff `quad_over_lin` **非 DCP**；采样日 n=3≪20；系统 INFEASIBLE rate=1.0；无 `ENG_OPTIMIZER_LAMBDA_CALIB_RECEIPT_ZH.md` |
| hard_spec | `leo_core_concentrated_0809`（NEW HARD 指纹对齐；产物失败 ≠ 可冻） |

**Beta 不发明 λ 数值。** FROZEN 前须 Eng 重标出可接受单点（或 dated 停报 + Leo 裁决）。

---

## 与旧共签关系

| 文件 | 关系 |
|---|---|
| `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md` | HARD 底座；**仍有效**；本文件 = **v1.1 bench 补丁**叠加上去 |
| `BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` | **SUPERSEDED**（宽度数字） |
| `BETA_CORE_ACCEPT_GATES_PENDING_ZH.md` | 冻后过门（PENDING）；与本共签一致 |

---

## 升 FULL / FROZEN 清单

1. Eng 密封窗 λ 产物可用（非 null；≥20 再平衡烟测或 dated 豁免）
2. Leo / 主 Agent 过关 → FROZEN
3. 仅 Stage1：**只跑 Core**；双口径报告；纸面底仓不动
4. live=false；promotion=false

**本轮裁决给 Strategy**：**CONDITIONAL_COSIGN_CORE_CONC_V1_1 — ACCEPT §5.1–5.3 四项；HARD 沿用 CORE_CONC；仍等 Eng λ + Leo。**
