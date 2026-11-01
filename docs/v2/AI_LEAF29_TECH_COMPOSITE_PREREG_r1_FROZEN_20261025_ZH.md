# 【FROZEN 戳记】叶29 tech/crowd/state 复合预注册 r1

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 戳记落盘 | 2026-10-25T12:16:10-0400（America/New_York；墙钟 `2026-10-25 12:16:10 EDT`） |
| **主令 FROZEN 时刻** | **2026-10-25 12:14 ET**（America/New_York）；令文 `docs/v2/audit/MAIN_LEAF29_PREREG_r1_FROZEN_ORDER_20261025_ZH.md` sha256 `a2f5f62afb9ddf2d4edf8651d6097e11d342d3c05350e987d247f90e7ebac13f`（sha8 **a2f5f62a**） |
| 状态 | **FROZEN（戳记）** — 冻结正文 = 下方基盘 DRAFT 全长 sha；开项钉见 §2；**本戳记不改基盘 DRAFT 文件** |
| live | **false** |
| promotion_approved | **false** |
| research_only | true |

---

## 1. 冻结正文指针（权威）

| 项 | 值 |
|---|---|
| 基盘路径 | `docs/v2/AI_LEAF29_TECH_COMPOSITE_PREREG_r1_DRAFT_20261025_ZH.md` |
| 基盘状态行（落盘时） | **正式预注册 DRAFT r1 / NOT FROZEN**（文件头不改；以本戳记宣布主令 FROZEN） |
| **基盘 DRAFT 全长 sha256** | `574e0740c4703371326480a318278055fd1401a969ec699a8a3dcd58be67bdb2` |
| 基盘 sha8 | **574e0740** |
| 校验 | 落戳记前 `sha256sum` **MATCH**；**基盘文件本回合未改写** |
| DRAFT 回执 | `docs/v2/audit/AI_LEAF29_PREREG_r1_DRAFT_RECEIPT_20261025_ZH.md` sha8 `cb1fa7d1` |
| who_pays / Alpha | `cea0dc60` / `15e6b00c` MATCH |

> **语义**：主令宣布叶29 预注册 r1 **FROZEN**；机制 / 残差 / 闸门以基盘 DRAFT 正文为准（sha 上表）。本文件是 **状态戳记 + 主裁开项钉 + 闸口清单**，不是第二份可改钉的预注册正文。

---

## 2. 主裁开项钉死（写入戳记；不改基盘）

| 开项 | 主裁钉（令文 `a2f5f62a`） |
|---|---|
| §3.P6 动量双重计分 | **A**（残差前剔除 / 动量维不进合成或正交掉 style mom） |
| §3.A β / mom / vol 窗 | **β：60 交易日 vs 510300**；**mom：t−120→t−20**；**vol：vol20** |
| §3.A 状态权重表 | 冻结基盘**定性规则**（进攻偏动量/趋势、震荡偏反转、防守偏低波+反拥挤）；**数值表**待 Arch 契约审前由 AI 一页附录钉死并交主裁并入；**禁**读本叶收益后改 |
| 资金维 / POC | **默认 OFF**（维持） |
| 页面 TOP | **禁**当超额证明（维持） |

---

## 3. 主令已钉摘要（只复述；细节以基盘为准）

| 钉 | 值 |
|---|---|
| 叶号 / 主题 | **29** · 技术/拥挤/状态复合分（残差候选叶） |
| 六硬钉 | 截面残差(SW+style) · HI_LIQ 判决 · walk-forward · Gate B/GATE_V3 · who_pays 机制句 · 禁页面 TOP |
| P1–P8 | Alpha **PATCHES_CLOSED** `15e6b00c` |
| 密封 / X2 窗占位 | 可对齐叶25 r6 日期占位；**本叶独立 `.ok`**；**本戳记不构成任何 `.ok`** |
| 排号令 | `docs/v2/audit/MAIN_LEAF28_29_WHO_PAYS_QUEUE_20261025_ZH.md` |
| 流程开闸 | `docs/v2/audit/MAIN_LEAF29_PREREG_FROZEN_PROCESS_ORDER_20261025_ZH.md` sha8 `5f13e01f` |

---

## 4. 硬闸（戳记瞬间仍成立）

- **仍禁申 `.ok`** / **禁自开跑** / **禁实跑读盘** / **禁 git commit** / **禁升纸面**
- 独立密封/X2 `.ok` 仅在 FROZEN+Arch 契约审后另排；**禁**复用叶25/27 任何 `.ok`
- **不挡**叶25 mem_probe r2（Arch 另审另签实峰 probe `.ok`）
- 数值权重附录：**未**并入本戳记；后续一页须交主裁后再并
- live=false

---

## 5. 前置未齐（不得假装已过）

| # | 前置 | 状态 |
|---|---|---|
| A | Arch 契约审（禁字段/runner/sha 清单） | **未排** |
| B | 状态权重**数值表**附录 | **待 AI 一页 → 主裁 → 并入戳记附录** |
| C | 本叶独立密封 / X2 `.ok` | **未申请**；禁自开跑 |
| D | 实现脚本 / 因子落盘 | **未写**（FROZEN 仅锁预注册口径） |

---

## 6. 状态机指针

```
PREREG_r1_DRAFT (574e0740…)
  → 【本戳记】r1 FROZEN（主令 12:14 ET；正文仍指向 574e0740…；开项钉 §2）
      →（可选）状态权重数值附录 → 主裁并入
          → Arch 契约审
              → 主/Arch 另排独立 .ok（禁复用叶25/27）
                  → 窗内研究跑（仍非纸面）
```

**当前**：**叶29 预注册 r1 FROZEN（戳记）**；**仍禁申 `.ok` / 禁自开跑**。P0 仍是叶25 mem_probe r2 等 Arch 另签。

live=false.
