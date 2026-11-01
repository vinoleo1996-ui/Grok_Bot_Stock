# 技术/拥挤/状态复合分 who_pays · P1–P8 补丁复核

- **日期**：2026-10-25 ≈12:03 ET · America/New_York
- **作者**：QuantLab Alpha（补丁复核；**非**叶级 ACCEPT / **非** FROZEN / 非纸面）
- **对象**：主 Agent（正式预注册排号）、AI、Arch（知会）
- **锁**：`live=false` · `promotion_approved=false` · `forbid_paper_handoff=true` · **不签 .ok** · **不开跑** · **勿升纸面** · Alpha **不**自行宣布 FROZEN
- **不挡**：叶25 mem_probe / 全叶 X2；叶27 LOWMEM 另窗

## 结论先行

| 项 | Alpha 裁定 |
|---|---|
| **裁决** | **PATCHES_CLOSED** |
| 语义 | 必须项 P1–P6 全 CLOSED；建议项 P7/P8 亦 CLOSED；六硬钉仍 MATCH。可**报主**谈正式预注册 / FROZEN **流程**——Alpha **不**自行宣布 FROZEN |
| 相对预审 | 预审 `ACCEPT_DRAFT_WITH_PATCHES`（`cf68d904…`）之补丁点已闭合；本复核 **≠** 叶级 RESEARCH_ACCEPT |
| 叶25 | 全叶仍等 X2 / mem_probe；本复核不抢窗、不复用 `1c32ab1e` |
| 晋级/纸面/live | **全部 false** |

## 1. 钉核验表（独立 sha256sum）

| 物 | 声称 sha8 / 全长 | 盘面 sha256 | 结果 |
|---|---|---|---|
| 修订后 DRAFT | `cea0dc60` / `cea0dc60ad260825e74fef7a9706b45aacf87fcfb3ca3bf0026823c1a2612aef` | `cea0dc60ad260825e74fef7a9706b45aacf87fcfb3ca3bf0026823c1a2612aef` | **MATCH** |
| AI 补丁回执 | `1563678d` / `1563678d6a212a5c26f722334a9456edeb1753c6a49bdc0d1a861e6e938913d0` | `1563678d6a212a5c26f722334a9456edeb1753c6a49bdc0d1a861e6e938913d0` | **MATCH** |
| Alpha 原预审 | `cf68d904` / `cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a` | `cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a` | **MATCH** |
| 政策钉（Leo） | `e671dee6` / `e671dee6660f159669ad6589b346822ec714c8b83d3c41c97a8d48f2f0670c26` | `e671dee6660f159669ad6589b346822ec714c8b83d3c41c97a8d48f2f0670c26` | **MATCH** |
| 旧 DRAFT（对照） | `655d2a3c…` | 已由修订稿取代；修订说明与回执均钉旧 sha | 历史钉 |

路径：
- DRAFT：`docs/v2/AI_LEAF_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_DRAFT_20261025_ZH.md`
- 回执：`docs/v2/audit/AI_LEAF_TECH_CROWD_P1P6_PATCH_RECEIPT_20261025_ZH.md`
- 预审：`docs/v2/ALPHA_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_PREREVIEW_20261025_ZH.md`
- 政策：`docs/v2/ALPHA_GATE_RESEARCH_TECH_COMPOSITE_LLM_DEBATE_20261025_ZH.md`

## 2. P1–P8 勾选表

| # | 级别 | 要求（摘自预审 `cf68d904…` §4） | 状态 | 修订稿落点 |
|---|---|---|---|---|
| P1 | 必须 | 正交硬闸表显式加叶25 / 叶26 / capacity_adv / moneyflow_resid（Jaccard≪0.7 ∧ 近等权拒） | **CLOSED** | §5.1 O1–O4；§0 可检验预测；§3 步骤 2.7 |
| P2 | 必须 | 方向+状态权重+窗一次写死；禁读收益翻档/翻号 | **CLOSED** | §3.A 表（方向/档数/权重/β·mom·vol 窗/停牌涨跌停 + 翻档禁令） |
| P3 | 必须 | 资金维默认 OFF 至主裁相对 moneyflow_resid | **CLOSED** | §2 维6；§3.P3；§0 who_pays 括注 |
| P4 | 必须 | 筹码 POC 默认关；无 PIT 禁编造；不得静默进主 α | **CLOSED** | §2 维8；§3.P4；§5.2 禁静默 |
| P5 | 必须 | OHLC/volume/复权价/指数 available_at 重钉；广度 GAP→状态臂降级并回执披露 | **CLOSED** | §3.P5；§2 状态机表；§1 H2 括注 |
| P6 | 必须 | 动量维 vs style mom 双重计分披露与处理（三选一框架） | **CLOSED** | §3.P6（A/B/C；DRAFT 倾向 A/B；终选 FROZEN 写死） |
| P7 | 建议 | 状态指数单一钉 510300；SW 共用禁私造 | **CLOSED** | §3.P7；§2 指数行；§3 步骤 2.1/2.3 |
| P8 | 建议 | vs Beta A6：选股 α ≠ Mandate 降仓旋钮 | **CLOSED** | §3.P8；§3 步骤 5 |

**必须项 P1–P6：6/6 CLOSED。建议项 P7/P8：2/2 CLOSED。未闭项：无。**

注：P2 数值表与 P6 终选（A/B/C）属 **FROZEN 瞬间封口**项——DRAFT 已给预填/选项框架与禁令，满足预审「升 FROZEN 前须补」之文档闭合标准；终值仍走主令正式预注册，Alpha 不代封。

## 3. 六硬钉（修订后抽查）

| # | 硬钉 | 修订后落点 | Alpha |
|---|---|---|---|
| 1 | 截面残差 = SW + style | §1 六硬钉表 / §3 步骤 2+4 | **MATCH** |
| 2 | HI_LIQ 判决 | §1 / §4；FULLA 不得代过门 | **MATCH** |
| 3 | walk-forward | §4：密封/X2 分窗；X2≥3 折；禁全样本一次拟合状态表 | **MATCH** |
| 4 | Gate B / GATE_V3 | §4：CMC v1.2 / `leaf_selfcheck_v3.py`；本 DRAFT 仍不跑闸 | **MATCH** |
| 5 | 机制 who_pays 写清 | §0 / §1 H1–H3；资金维 OFF 括注已同步 | **MATCH** |
| 6 | 禁页面 TOP 当超额 | §0 失效 / §1 禁止 / §5.2 首条；未松动 | **MATCH** |

六硬钉 **全 MATCH**；禁页面 TOP **未松动** → 排除 `PATCHES_FAIL`。

## 4. 政策对齐（Leo）

- 技术复合分按**残差候选叶**审：正交 / WF / Gate B·GATE_V3 —— DRAFT 路径保持。
- **硬拒**页面 TOP / 演示榜当超额 —— §5.2 维持。
- 本复核只审 (A) tech who_pays；不审 (B) LLM 辩论稿。

## 5. 下一步 / 非动作

1. **报主**：可启动正式预注册 / FROZEN **流程**（排号 → FROZEN 文 → Arch 审脚本 → 独立新窗 `.ok` → X2/密封分签 → Alpha 闸审）。Alpha **不**自行宣布 FROZEN。
2. **不**签 `.ok`；**不**开跑；**不**跑实数据；**不**改脚本 / `alpha_labels` / FROZEN_CONFIG；**勿升纸面**。
3. **不挡**叶25 mem_probe / 全叶 X2；**不挡**叶27 LOWMEM@另窗。
4. FROZEN 瞬间仍须封口：§3.A 终值表、P6 A/B/C 终选、指数 510300 vs 000300 终钉、资金维 OFF/启用裁定。

## 6. 状态动作

- 落盘本文；`TEAM ### Alpha` 覆盖本复核结论 + 叶25/27 等待态。
- `ql_bus` type=`gate` verdict=`PATCHES_CLOSED`；refs=本文。
- blocker：无（相对本补丁复核）；全叶仍等叶25 X2（既有优先，非本裁决 blocker）。

live=false；promotion_approved=false；forbid_paper_handoff=true。
