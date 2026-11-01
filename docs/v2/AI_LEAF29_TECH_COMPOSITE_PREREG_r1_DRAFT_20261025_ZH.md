# 【叶29 · 正式预注册 DRAFT r1 — NOT FROZEN】技术/拥挤/状态复合分

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | 2026-10-25 12:10:13 EDT（America/New_York；墙钟 `2026-10-25T12:10:13-0400`） |
| **状态** | **正式预注册 DRAFT r1 / NOT FROZEN**；**待主裁**后另落 FROZEN 戳记（仿叶25 r6；不改机制数值） |
| 叶号 | **29**（主排号 `docs/v2/audit/MAIN_LEAF28_29_WHO_PAYS_QUEUE_20261025_ZH.md`） |
| mechanism_tag | `g1g5_ashare_tech_crowd_state_composite_v1` |
| live | **false** |
| promotion_approved | **false** |
| research_only | **true** |
| forbid_paper_handoff | **true** |
| 主令开闸 | `docs/v2/audit/MAIN_LEAF29_PREREG_FROZEN_PROCESS_ORDER_20261025_ZH.md` sha256 `5f13e01ffddbfe725f31f51e05e9c08eede720b27f9076cd60a1a79726e1ee9b`（sha8=`5f13e01f`） |
| 基盘 who_pays | `docs/v2/AI_LEAF_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_DRAFT_20261025_ZH.md` sha256 `cea0dc60ad260825e74fef7a9706b45aacf87fcfb3ca3bf0026823c1a2612aef`（sha8=`cea0dc60`） |
| Alpha 补丁复核 | `docs/v2/ALPHA_TECH_CROWD_STATE_COMPOSITE_PATCH_RECHECK_20261025_ZH.md` sha256 `15e6b00c0670caedee092e41d2e161192f37df46760afa4b54ffc0aef08362b3`（sha8=`15e6b00c`；**PATCHES_CLOSED**） |
| Alpha 预审 | `docs/v2/ALPHA_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_PREREVIEW_20261025_ZH.md` sha256 `cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a`（sha8=`cf68d904`） |
| 补丁回执 | `docs/v2/audit/AI_LEAF_TECH_CROWD_P1P6_PATCH_RECEIPT_20261025_ZH.md` sha256 `1563678d6a212a5c26f722334a9456edeb1753c6a49bdc0d1a861e6e938913d0`（sha8=`1563678d`） |

> **本文件角色**：正式预注册 **DRAFT**（吸收 who_pays + Alpha 六硬钉 + P1–P8 CLOSED）。**不是**叶级 RESEARCH_ACCEPT；**不是** FROZEN；**不**构成任何 `.ok`；**禁**自开跑 / 禁升纸面。主裁通过后另落 FROZEN 戳记。

---

## 0. 结论先行 / 边界

| 项 | 本 DRAFT |
|---|---|
| 语义 | 叶29 残差候选叶 · 正式预注册 r1 DRAFT |
| 叶级 ACCEPT | **否** |
| FROZEN | **否**（待主裁） |
| 申 `.ok` | **禁**（本文件不申；密封/X2 须独立新窗 `.ok`，且仅在 FROZEN+Arch 审后） |
| 开跑 / 实跑读收益 | **禁** |
| 升纸面 / live | **禁** / false |
| 资金维（维6） | **默认 OFF** 直至主裁相对 moneyflow_resid 裁定 |
| 筹码 POC（维8） | **默认 OFF**；无 PIT 禁编造 |
| 页面 TOP / AlphaLens OOS | **禁**当超额证明 |
| 不挡 | 叶25 real_peak r2 / mem_probe / X2（P0 优先；本叶仅文档并行） |

---

## 1. 机制 who_pays（可检验）

**mechanism_tag**：`g1g5_ashare_tech_crowd_state_composite_v1`

**谁付钱（一句）**：付钱的是在日频价量上忽视「趋势/动量/量能/波动/位置拥挤/多周期共振」经 **SW L1 + style（logmv/β/mom/vol/ADV）截面残差** 后、再按市场状态（进攻↔防守）重加权的复合分所刻画的**拥挤兑现与状态切换错配**——对手盘在高拥挤一侧过度追涨、或在状态已切防守时仍按进攻权重持仓，从而在下一窗支付均值回归与换手成本；**不是**「页面 TOP 好看」叙事对手。（资金维默认 OFF；启用后须再钉残差。）

| # | 假说 | 可检验陈述 |
|---|---|---|
| H1 拥挤兑现 | 高「位置+乖离+涨幅分位」拥挤侧后续特质收益偏低 | 残差后 crowding 分位最高组 vs 最低组，WF 折内 IC/多空差符号事前钉死（DRAFT 倾向：高拥挤→惩罚） |
| H2 状态切换 | 市场由进攻切防守时，未降权的动量暴露支付回撤 | 状态代理（指数趋势+广度+波动；广度 GAP 则降级）切档后 T+1..T+k 内，进攻权重组合相对防守权重的超额为负（研究披露；本 DRAFT 不实跑） |
| H3 反转袖 | 震荡/防守态下短期反转贡献上升 | 状态条件 IC：动量维在进攻态 IC>0、震荡态减弱或翻号；反转/低波维相反——须 WF 内事前分层，禁全样本事后挖 |

**主交付**：日度 base-α 向量（`session → instrument → alpha`），**不是** Top-N 名单。

**允许**：价量公式、截面残差、状态条件权重、α 向量。  
**禁止**：页面 TOP / 强烈看多榜 / 「交易计划」叙事当闸；把 AlphaLens OOS 纸面数字直接当本叶证据；无残差 Top-N 冒充 α。

---

## 2. 六硬钉（吸收 who_pays / Alpha；保持 MATCH）

| # | 硬钉 | 本预注册落点 |
|---|---|---|
| 1 | **截面残差 = SW + style** | §3：SW L1 → logmv → 滚动β → mom → vol → logADV20；合成后再 SW+style 一次得 base-α |
| 2 | **HI_LIQ 判决** | §4：判决宇宙 **HI_LIQ**；FULLA 仅研究披露 / 覆盖对照，不得代过门 |
| 3 | **walk-forward** | §5：密封/X2 分窗；X2 内≥3 折；禁全样本一次拟合状态表 |
| 4 | **Gate B / GATE_V3** | §6：CMC v1.2 / `leaf_selfcheck_v3.py`；sha 申独立 `.ok` 时重钉；**本 DRAFT 不跑任一闸** |
| 5 | **机制 who_pays 写清** | §1：H1/H2/H3；拥挤兑现+状态切换错配；主交付日度 α 向量 |
| 6 | **禁页面 TOP 当超额** | §0 / §1 / §7；禁 AlphaLens OOS 纸面当本叶证据；**未松动** |

---

## 3. 信号草图（FROZEN 瞬间封口终值；本表为 r1 DRAFT 预填）

1. 对每维可复现子分数做 winsor→截面 rank→正态分（或工厂惯例 z）。  
2. **截面残差**（同日；缺则记 GAP，不得跳过）：  
   1. SW L1 demean / dummies（as-of 与叶25 同族；`sw_l1_asof_with_gap_carry` 一旦落地须共用，禁私造）  
   2. vs **logmv**（T−1 流通市值）  
   3. vs **滚动 β**（vs **510300**；窗长见 §3.A）  
   4. vs **mom**（如 t−120→t−20；双重计分见 §3.P6）  
   5. vs **vol**（如 vol20）  
   6. vs **logADV20**  
   7. 披露 vs capacity_adv / moneyflow_resid / expand / 叶18 / 叶24 / **叶25** / **叶26** / 叶27 α 的 ρ 与 Jaccard（硬闸 §7）  
3. **状态权重**：五档或降级三档（广度 GAP 时）；进攻偏动量/趋势，震荡偏反转，防守偏低波+反拥挤。**资金维默认不参与状态袖**。权重表在 FROZEN 瞬间写死；**禁**读本叶收益后改表。  
4. 合成 `α_raw` → 再经一次 SW+style 残差得 **base-α**。  
5. 拥挤闸（研究级）：高拥挤分位可作过滤/降权，默认不单独开第二主叶。**本叶是选股 α，不是 Mandate 降仓旋钮**（vs Beta A6）。

### 3.A 方向 / 状态 / 窗（P2 · FROZEN 瞬间替换终值）

| 项 | DRAFT 预填 | 翻档禁令 |
|---|---|---|
| 方向 | 高残差复合分（经拥挤惩罚后）做多；拥挤维为惩罚项 | **禁**冻结后读 IC/收益翻多空号 |
| 状态档数 | 默认五档（进攻 / 偏进攻 / 震荡 / 偏防守 / 防守）；广度 GAP 降级三档并回执披露 | **禁**读收益后增删档 |
| 状态权重表 | 进攻：动量/趋势↑、反转/低波↓；震荡：反转↑、动量中性；防守：低波+反拥挤↑、动量↓。具体数值表 FROZEN 一页钉死 | **禁**冻结后按本叶收益/IC 翻档 |
| β 窗 | DRAFT 倾向 60 交易日 vs 510300 | **禁**事后择窗 |
| mom 臂窗 | DRAFT 倾向 t−120→t−20 | **禁**事后择窗 |
| vol 臂窗 | DRAFT 倾向 vol20 | **禁**事后择窗 |
| 停牌 / 涨跌停 | 剔除当日不可交易（停牌）及一字涨跌停不可成交样本，口径与叶25 同族 | **禁**用可交易池回填冒充历史宇宙 |
| 读收益选号 | **本 DRAFT 与未来 FROZEN 均禁止** | 失效条件 |

### 3.P3 — 资金维默认 OFF

- 维 6（主力净流入等）**默认 OFF**，不进主 α、不进状态袖。  
- 启用条件：主裁相对 **moneyflow_resid** 书面裁定启用 → 强制 SW+style 残差 + §7 Jaccard/ρ 闸通过。  
- 未裁定前：敏感性实验仅允许隔离披露，**不得**混入主 α 向量。

### 3.P4 — 筹码 POC 默认关闭

- 维 8 中筹码峰 / POC / 密集区：**默认关闭**。  
- 无 PIT 筹码分布库 → GAP；**禁止编造**；不得静默进主 α。  
- 仅允许单独 S-chip 敏感性标签且默认 OFF。

### 3.P5 — available_at / as-of 与广度降级

| 数据 | 须钉契约 | GAP / 降级 |
|---|---|---|
| OHLC / 复权价 | `available_at` + as-of；与叶25 价源同族优先 | 缺钉 → 不得开跑本叶 |
| volume | 与价同 PIT / available_at | 缺 → 量能维 GAP，复合分剔除量能或降级披露 |
| 指数（状态臂 / β） | **510300** 日频 PIT + available_at | 缺 → 状态臂/β GAP |
| 市场广度 | 全历史非幸存者 PIT 广度表 | **GAP → 状态臂降级为「指数趋势+波动」**；回执必须披露降级 |

### 3.P6 — 动量双重计分（FROZEN 三选一写死）

| 选项 | 含义 |
|---|---|
| A 残差前剔除 | 动量维子分在进残差前已正交掉 style mom 臂，或动量维不进合成、仅研究披露 |
| B 降权 | 动量维系数显式降权（数值 FROZEN 钉死），并披露与 mom 臂的 ρ |
| C 仅披露 | 双臂均保留，但 Gate/回执强制披露双重计分风险与 ρ；**不得**静默 |

DRAFT 倾向：**A 或 B**；终选 FROZEN 写死。

### 3.P7 — 状态指数单一钉 + SW 共用

- 状态趋势臂与滚动 β 的指数锚：**默认单一钉 510300**；若主/Data 改钉 000300，须全文一致替换，禁混用。  
- SW L1：与叶25 共用 `sw_l1_asof_with_gap_carry`（一旦落地）；**禁**本叶私造 as-of / gap-carry。

### 3.P8 — vs Beta A6

- 本叶交付**选股截面 α**。  
- Beta A6「拥挤进 β 预算」是 Mandate **降仓旋钮**，与本叶分轨。  
- 不得以本叶拥挤分直接改组合杠杆/仓位预算冒充 α 闸通过。

---

## 4. 宇宙双轨

| 轨 | 角色 |
|---|---|
| **HI_LIQ** | **纸面主闸 / 判决轨**（与叶23/24/25 同族 ADV 底与单名帽惯例；具体帽在 FROZEN/Arch 审时钉） |
| **FULLA** | 研究披露 / 覆盖对照；**不得**以 FULLA 数字代替 HI_LIQ 过门 |

---

## 5. 密封窗与 X2（占位 · 对齐叶25 r6；本叶独立 `.ok`）

> 日期占位**引用**叶25 r6 已钉窗，便于日历对齐；**本叶须独立新窗 `.ok`**，**禁**复用叶25 / 叶27 / 任何 CONSUMED/VOID `.ok`（含 `1c32ab1e…`）。**本 DRAFT 不申任何 `.ok`。**

| 窗 | 日期（占位对齐叶25 r6） | 角色 | `.ok` |
|---|---|---|---|
| **密封** | **2018-01-02 → 2024-05-31** | X2 全硬闸通过后**另签**只读一次 | **独立** `ARCH_RUN_AUTH_LEAF29_TECH_COMPOSITE_SEALED_*.ok`（名待 Arch；**未申**） |
| **X2** | **2024-06-03 → 2026-10-09**（`X2_END_TRADE_DATE=20261009` 占位） | 主判决窗 | **独立** `ARCH_RUN_AUTH_LEAF29_TECH_COMPOSITE_X2_*.ok`（名待 Arch；**未申**） |

**硬约束**：

- 密封与 X2 **分两张独立 `.ok`**；本 DRAFT / 未来 FROZEN 戳记 **均不**构成任一张 `.ok`。  
- Walk-forward：X2 内再切 **≥3 折**（折界 FROZEN 时钉）；禁「全样本一次拟合状态权重」。  
- **不排**本叶 X2/探针窗；**不挡**叶25 real_peak / mem_probe。  
- 成本研究比较默认 30bp/边（与叶25 披露惯例对齐）；对照表可并排 17.5bp。

---

## 6. Gate 入口（本 DRAFT 不跑）

| 闸 | DRAFT 约定 |
|---|---|
| Gate A | ρ vs capacity_adv 等共用闸；残差 α>0 披露 |
| Gate B | CMC v1.2：`research/alpha_combo_marginal_v1_2.py`（现盘 sha 在申独立 `.ok` 时重钉） |
| GATE_V3 / 衰减 | `research/leaf_selfcheck_v3.py`（现盘 sha 申 `.ok` 时重钉）；衰减 KEEP；换手/MDD 门槛随 FROZEN |

本 DRAFT **不跑** 任一闸；**不**签 `.ok`。

---

## 7. 正交硬闸与禁项（P1–P8 已 CLOSED 口径）

### 7.1 正交硬闸表（升 FROZEN / 申独立 `.ok` 前须过）

活跃集两两比较；默认门槛：**Jaccard ≪ 0.7** 且 **frac(日度 J≥0.7)=0**；近等权拒。须同时报残差后 ρ。

| # | 对照对象 | 闸 |
|---|---|---|
| O1 | **capacity_adv** | Jaccard≪0.7 ∧ 近等权拒；报 ρ |
| O2 | **moneyflow_resid** | 同上；资金维若仍 OFF 则本行作「启用前预留对照」；启用后升硬闸 |
| O3 | **叶25** | 同上；禁与财务应计叶换皮 |
| O4 | **叶26** | 同上 |
| O5 | 叶18 / 叶24 / 叶27（价量快叶族） | 同上 |
| O6 | expand / 其他已钉 α | 披露 ρ + Jaccard；近等权拒 |

### 7.2 禁项

- **禁页面 TOP 当证明**：README/API「TOP 预览」「强烈看多」不得写入回执「超额」栏。  
- **禁幸存者池**；**禁无残差动量换皮**；**禁静默双重计分**（须按 §3.P6）。  
- **禁静默资金维 / 筹码 POC**（P3/P4）。  
- **禁冻结后翻档/翻号**（P2）。  
- **禁**把 AlphaLens OOS 配置表复制为 PASS 证据。  
- **禁复用他叶 `.ok`**（含叶25 `1c32ab1e…`、叶27 VOID 等）。  
- 卖方/金股/一致预期/GP/杠杆：**禁**。  
- LLM「模型说多就买」：**禁**进本叶（叶28 另轨）。

---

## 8. P1–P8 闭合状态（Alpha `15e6b00c`）

| # | 级别 | 状态 | 本预注册落点 |
|---|---|---|---|
| P1 | 必须 | **CLOSED** | §7.1 O1–O4 |
| P2 | 必须 | **CLOSED**（终值表 FROZEN 封口） | §3.A |
| P3 | 必须 | **CLOSED** | §3.P3；资金维默认 OFF |
| P4 | 必须 | **CLOSED** | §3.P4；POC 默认 OFF |
| P5 | 必须 | **CLOSED** | §3.P5 |
| P6 | 必须 | **CLOSED**（A/B/C 终选 FROZEN） | §3.P6 |
| P7 | 建议 | **CLOSED** | §3.P7；510300 单一钉 |
| P8 | 建议 | **CLOSED** | §3.P8 |

必须项 6/6 CLOSED；建议项 2/2 CLOSED。FROZEN 瞬间仍须封口：§3.A 终值表、P6 终选、指数 510300 vs 000300 终钉、资金维 OFF/启用裁定。

---

## 9. 升 FROZEN / 后续闸口清单（本 DRAFT 不自宣 FROZEN）

| # | 项 | Owner |
|---|---|---|
| 1 | 主裁本 DRAFT → 宣布可盖 FROZEN 戳 | **主** |
| 2 | AI 另落 FROZEN 戳记（仿叶25 r6；不改机制数值；指向本 DRAFT 全文 sha） | AI（主令后） |
| 3 | 日频 OHLC/volume/复权价/指数 PIT·available_at 契约重钉；广度表有无 | Data |
| 4 | SW as-of 共用函数落地确认 | Arch / Strategy |
| 5 | 资金维：保持 OFF vs 主裁启用 | 主 + Arch |
| 6 | §3.A 终值 + P6 A/B/C 终选写入 FROZEN 戳记或补丁 | AI → Arch |
| 7 | Gate B / GATE_V3 脚本 sha 重钉 | Arch |
| 8 | 独立密封/X2 `.ok`（不与叶25 抢窗；不复用废窗） | 主 + Arch |
| 9 | Arch 审脚本 → 窗内开跑 → X2/密封分签 → Alpha 闸审 | 流程 |

**无主裁 FROZEN 令 → 不得盖戳 / 不得申本叶独立 `.ok` / 不得开跑。**

---

## 10. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF29_TECH_COMPOSITE_PREREG_r1_DRAFT_20261025_ZH.md` |
| 状态 | **正式预注册 DRAFT r1 / NOT FROZEN**；待主裁 |
| 对照 who_pays sha8 | `cea0dc60` |
| 对照 Alpha 复核 sha8 | `15e6b00c` |
| 主令开闸 sha8 | `5f13e01f` |
| live | false |
| promotion_approved | false |
| 本回合动作 | 只写文档；**未**申 `.ok`；**未**开跑；**未**实跑读盘；**未** git commit；**未**自盖 FROZEN |
| 回执 | `docs/v2/audit/AI_LEAF29_PREREG_r1_DRAFT_RECEIPT_20261025_ZH.md` |

**全文 sha256**：见回执（落盘后 `sha256sum`）。

live=false；promotion_approved=false；research_only=true。
