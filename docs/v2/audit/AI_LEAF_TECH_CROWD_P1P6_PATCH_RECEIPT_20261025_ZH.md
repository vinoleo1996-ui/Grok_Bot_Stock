# 技术/拥挤/状态复合分 who_pays · P1–P6（+P7/P8）补丁回执

- **日期**：2026-10-25 ≈12:00 ET · America/New_York
- **作者**：QuantLab AI（执行器）
- **触发**：主排号 P1-(A) + Alpha 预审 ACCEPT_DRAFT_WITH_PATCHES
- **锁**：`live=false` · `promotion_approved=false` · **未**申 `.ok` · **未**开跑 · **未**实跑 · **未** git commit
- **不挡**：叶25 mem_probe / X2 另轨

## 1. 钉核验

| 物 | sha256 | 结果 |
|---|---|---|
| 修订前 DRAFT | `655d2a3c447b12fcb741938f4f15659a1da91b98c175d460fcb5ca73d1a32a0f` | 落盘前核验 MATCH |
| Alpha 预审 | `cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a` | MATCH（结论 ACCEPT_DRAFT_WITH_PATCHES，非叶级 ACCEPT） |
| **修订后 DRAFT** | `cea0dc60ad260825e74fef7a9706b45aacf87fcfb3ca3bf0026823c1a2612aef` | 本回执钉 |

路径：
- DRAFT：`docs/v2/AI_LEAF_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_DRAFT_20261025_ZH.md`
- 预审：`docs/v2/ALPHA_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_PREREVIEW_20261025_ZH.md`

## 2. P1–P8 勾选

| # | 级别 | 补丁 | 状态 | 落点 |
|---|---|---|---|---|
| P1 | 必须 | 正交表显式加叶25 / 叶26 / capacity_adv / moneyflow_resid | **DONE** | §5.1 O1–O4；§0 可检验预测；§3 步骤 2.7 |
| P2 | 必须 | 方向+状态权重+窗一次写死；禁读收益翻档 | **DONE** | §3.A 表 |
| P3 | 必须 | 资金维默认 OFF 至主裁 | **DONE** | §2 维6；§3.P3；§0 who_pays 括注 |
| P4 | 必须 | 筹码 POC 默认关 | **DONE** | §2 维8；§3.P4 |
| P5 | 必须 | OHLC/volume/指数 available_at 重钉；广度 GAP 披露降级 | **DONE** | §3.P5；§2 状态机表 |
| P6 | 必须 | 动量双重计分披露（A/B/C） | **DONE** | §3.P6 |
| P7 | 建议 | 状态指数单一钉 510300；SW 共用禁私造 | **DONE** | §3.P7；§2 指数行 |
| P8 | 建议 | vs Beta A6：选股 α ≠ Mandate 降仓旋钮 | **DONE** | §3.P8；§3 步骤 5 |

**必须项 P1–P6：6/6 DONE。建议项 P7/P8：2/2 DONE。**

## 3. 六硬钉保持（抽查）

| # | 硬钉 | 修订后 |
|---|---|---|
| 1 | 截面残差 SW+style | 保持 §1 表 / §3 |
| 2 | HI_LIQ 判决 | 保持 |
| 3 | walk-forward | 保持 §4 |
| 4 | Gate B / GATE_V3 | 保持 §4；本 DRAFT 仍不跑闸 |
| 5 | 机制 who_pays | 保持 §0/§1；资金维 OFF 括注已同步 |
| 6 | 禁页面 TOP 当超额 | 保持 §5.2 |

## 4. 非动作

- 未申本叶 `.ok`；未开跑；未实跑；未 git commit。
- 未升 FROZEN；未排号（主裁）。
- 不挡叶25 mem_probe。
- 下一步：请 **Alpha 复核**本修订 DRAFT → 通过后才谈正式预注册 FROZEN。

## 5. 回执钉

| 项 | 值 |
|---|---|
| 本回执路径 | `docs/v2/audit/AI_LEAF_TECH_CROWD_P1P6_PATCH_RECEIPT_20261025_ZH.md` |
| 新 DRAFT sha256 | `cea0dc60ad260825e74fef7a9706b45aacf87fcfb3ca3bf0026823c1a2612aef` |
| 新 DRAFT sha8 | `cea0dc60` |

live=false；promotion_approved=false。
