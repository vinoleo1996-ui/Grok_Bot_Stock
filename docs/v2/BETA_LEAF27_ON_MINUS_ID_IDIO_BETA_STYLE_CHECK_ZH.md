# Beta · 叶27 `on_minus_id`/idio vol · β / 风格暴露与 Mandate 冲突检查（研究级一页）

- 时间：2026-10-25 ≈06:20 ET（America/New_York；盒机 `TZ=America/New_York date`）
- 角色：QuantLab Beta（β / 风险预算 / 风格；**不**重写 who_pays、**不**挖 Alpha、**不**声称实证数字）
- 触发：主 Agent【主→Beta P1】Supervise 06:14 ET — 叶27 β/风格一页；禁跑、禁申 .ok；不挡叶25@10:00–10:45 ET
- 性质：**机制 + 冲突矩阵 + 草稿接线规则**。全程只读（Read / rg / sha256sum / ls）。**未**跑 python / pytest / 读 parquet 算收益。未申请 Arch .ok。
- **live=false；promotion_approved=false。** 不改线上、不改 Mandate JSON、不碰冻结纸面轨（capacity_adv / B4 / S6）。研究开关**默认关**。

### 对齐输入（写前磁盘 sha256，R3）

| 文件 | sha256 |
|---|---|
| `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md` | `4a0eec1a4d1694be7a91b8cd291b8d1547e68ff41f8b9121e90dd7f44967282b` |
| `docs/v2/ALPHA_LEAF27_WHO_PAYS_SLOT_FILL_REVIEW_20261025_ZH.md` | `01ab6bf39ca276c459c9febb1178f1d1afa9e5b8170a167b4a16a904a297f801` |
| `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md`（**FROZEN** 06:11 ET） | `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` |
| `docs/v2/QuantLab-MANDATE_V2.json` | `04afacc45778bfcdcfbcc7b8ff73098f2ec843cd49fea6ef406d297e05e68f0f` |
| `docs/v2/BETA_VOL_TARGET_HANDOFF.md` | `3872d1a449b8704ae398f79881194aa7ab6b49cfe7e9fc2689893b62f0ddedfa` |
| `docs/v2/BETA_CORE_V1_3_GATE_REVIEW_ZH.md` | `8bff82f1b30c92898fb5cc8c681dd8c3440925a71eef1bdd72918db72990a4fa` |
| `docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_WHO_PAYS_PREREG_ZH.md`（叶18） | `b00a1f9ea5e50cf928c001e4caa48483fac1951019cb62d02beb4c3df53aa00e` |
| 板式对照 `docs/v2/BETA_ETF_FLOW_PREMIUM_BETA_SIGNAL_DRAFT_ZH.md` | `0fa22cd818bdd2c348a9e71842babd4cdab4caed0d47f1d722b01c98797e9efd` |

冻结钉（prereg r1）：`α_raw=−ivol`；β 基准=**510300**·60 会话/最少 40；W=20/最少 15；残差序 **SW L1 demean + log 流通市值(T−1) + 滚动β + capacity_adv**；停牌无效；涨跌停不进截面且 gate=0。

---

## §0 结论三句

1. **主规格 `α=−ivol` 与 Mandate vol16% / `style_budget.low_vol`（optional, max_abs_z 0.75）呈软兼容倾向**：信号层已对 510300 滚动β残差，意图截面 β 中性；方向惩罚高拆分特质波动，与「压组合特质波动贡献」同向——**但不能**把本叶当 ETF β 预算旋钮，也**不**自动把 Core 已超标的组合 vol（≈19.6–19.9%）拧回 16%。
2. **硬冲突倾向只有一类：用 `+ivol`（或精神叙事）冲年化 / 抬组合 vol·β。** 主规格已 FROZEN 为 −ivol；`+ivol` 仅可事前敏感性且不得升格。Core 现状 β≈0.86–0.87、vol 已高于 16%，再叠高 idio 波动卫星 = 与 Leo 风险预算意图相反。
3. **软冲突须披露、不挡预注册**：隔夜跳空 → 开盘-to-开盘 β 与 Mandate 收盘-to-收盘 β 口径错配；与叶18 同族低波方向叠仓的伪耦合（组合风险预算含义，Jaccard/ρ 仍是 Alpha 硬闸）；行业 SW L1 demean ≠ 持仓行业中性自动成立；Size 已 vs log 市值残差但仍须盯 Core Size/MidCap ±0.35σ。本页**零实证**；研究开关默认关；不挡叶25；Core FAIL 去留仍等 Leo。

---

## §1 叶27 从 Beta 视角的暴露机制

### 1.1 信号层 vs 组合层（分清两层）

| 层 | 叶27 已写死的意图 | Beta 仍须盯的 |
|---|---|---|
| **信号层** | 对 `on_minus_id` 做 SW L1 demean → vs log 市值 → vs **滚动β(510300,60/40)** → vs capacity_adv → `ivol=std(ε,20)` → `α=−ivol` | 截面 β 中性是**残差意图**，不是持仓 β≈0.70 的保证 |
| **组合层** | 评价权重：≤4%/名、≤20 名、行业帽 HI_LIQ≤25% / FULLA≤28%、余额 510300、5 日再平衡 | 叠仓/权重/再平衡节奏 → 组合 realized β / vol / Size / 行业偏离仍由持仓加权决定 |

**含义**：残差掉滚动β，只说明 α 向量与 510300 暴露在截面上正交意图；一旦按 α 取前 20、叠 80/20 或与其他叶加权，**组合对 510300 的 β 与年化 vol 仍可能偏离 Mandate**。本页只给冲突与接线规则，不报任何回测 β/vol。

### 1.2 `α=−ivol` 与 Mandate `style_budget.low_vol`

Mandate（`QuantLab-MANDATE_V2.json`）：

- `style_budget.low_vol`：**optional=true**，`max_abs_z_exposure=0.75`
- `risk.target_annual_vol=0.16`（范围 [0.14, 0.18]）；`target_beta_vs_benchmark=0.70`；`target_beta_band=[0.5, 0.85]`
- `signal_construction.industry_neutral_residual_book=true`；`optional_mktcap_neutral=true`
- `style_budget.size`：允许小盘倾斜但非主 α；`microcap_hard_cap_weight=0.0`（与宇宙剔除底 30% 一致）

叶27 主规格惩罚高拆分特质波动 → 持仓倾向**低 idio vol**一侧，与 optional low_vol 袖套**方向同族**。Beta 解读：

- 若未来叠仓后 holdings-weighted low_vol z 落在 \|z\|≤0.75 → **风格预算无硬越界**（仍须实测披露，本页未测）。
- 若 \|z\|>0.75 → 软冲突：要么缩本叶卫星权重，要么 Leo 书面放宽 low_vol 带——**不得**借「低波因子」叙事抬仓冲年化。
- **禁止**把本叶解释成「可以放松 vol_targeting / DD L1–L4」；handoff 契约不变（`BETA_VOL_TARGET_HANDOFF`）。

### 1.3 Size（已 vs log 市值残差）与 Core Size/MidCap ±0.35σ

- 信号：强制 vs **log 流通市值(T−1)** OLS 残差 → 意图去掉纯 Size 暴露。
- Core v1.3 门控（只读披露）：可行日 \|Size\| max≈0.33、\|MidCap\| max≈0.40（slack 内）；沿用日 MidCap 曾见更大偏离。G-Sz 在判定口径 A 上「过（顶格）」，但组合层 Size 带仍是 Beta 长期盯梢项。
- **风险**：分域 rank（P70/P90）+ 评价取前 20，仍可能在**中小盘带内**形成隐式倾斜；微盘硬顶 0 / 宇宙底 30% 剔除不得被本叶「复活」。
- 接线：叠仓前必须报 Size / MidCap holdings-z；越 ±0.35σ（含 slack 规则与 Core 同口径）→ 本叶卫星降权或不开。

### 1.4 行业：SW L1 demean + 评价帽 ≤25% vs Mandate / Core

| 口径 | 叶27 | Mandate / Core |
|---|---|---|
| 信号 | SW L1 **demean**（残差书） | `industry_neutral_residual_book=true` |
| 评价持仓 | HI_LIQ 行业帽 **≤25%**（与 `max_industry_weight=0.25` 对齐） | Core G-I：相对全池 wb **±8%** 且绝对 ≤20%（判定口径细节见 Core 审查） |

**关键句（Beta）**：残差 demean **≠** 持仓行业中性自动成立。demean 去掉行业截面均值对 α 的贡献；取 Top 权重后仍可能在少数 SW L1 上堆仓。叠仓诊断必须同时报：

1. 信号侧：行业 demean 是否完整（缺 SW L1 PIT → GAP，见 §4）；
2. 持仓侧：相对 wb 的行业偏离与绝对行业权重（对标 Core ±8% / ≤20% 与 Mandate 25% 帽）。

---

## §2 冲突矩阵（硬 / 软 / 无）

Mandate 锚点：`vol★=0.16`（[0.14,0.18]）；`β★=0.70`（带 [0.5,0.85]）；`low_vol` max_abs_z=0.75；行业残差书 + 持仓帽；微盘硬顶 0。Core 现状（只读）：组合 vol≈**19.6–19.9%**，对 510300 β≈**0.86–0.87**；Size/MidCap 带见上。

| # | 情景 | 冲突级 | 理由（Beta） |
|---|---|---|---|
| 1 | 用 **`+ivol` / 追高 idio 波动** 当主规格或卫星「冲年化」 | **硬冲突** | 与 FROZEN `α=−ivol` 相反；抬特质波动贡献 → 推高组合 vol/MDD；Core 已超 16%。须 Leo 书面改 Mandate **且**改门在看收益前——本页拒绝默认 |
| 2 | 主规格 **`−ivol` 降特质波动** 作研究卫星（默认关） | **无硬冲突 / 软兼容倾向** | 与 vol 预算、optional low_vol 同向；**不承诺**把 Core vol 压回 16%；不得借此抬 `max_etf` 或关 DD |
| 3 | 在 Core 已超 vol 时，仍把本叶当 **抬 β / 加权益风险** 旋钮 | **硬冲突（现状叠加）** | 本叶不是 ETF β 预算工具（那是份额流一页的旋钮族）；混用 = 加剧已超标风险 |
| 4 | 隔夜跳空成分 → **开盘-to-开盘** 隐含 β 与 Mandate **收盘-to-收盘** β 口径 | **软冲突（披露）** | `r_on`/`on_minus_id` 含隔夜；滚动β用日收益(510300)近似收盘口径。叠仓回执须并列报 close-close 组合 β 与（若有）open-open 敏感；不得静默混口径宣称「已 β 中性」 |
| 5 | 与 **叶18 / 18v** 同族低波方向叠仓 | **软冲突（伪耦合·组合预算）** | 叶18=WATCH/Gate A·B/GATE_V3 FAIL（不可交易/衰减/跑不赢主干）；叶27 主轴不同但方向同为 −ivol。Alpha 硬闸：Jaccard/ρ；**Beta 追加**：即使过 Jaccard，叠加权重对组合 low_vol z / 特质 vol 的边际若≈加权和 → 风险预算双计，CMC/组合层不得当两个独立 vol 缓冲 |
| 6 | 与 **叶26 ETF 流** 或 **moneyflow×capadv 80/20**（已 STOP）混信号/叠仓 | **硬冲突（路径关闭）** | prereg 禁 ETF 份额/个股 moneyflow 进主信号；Strategy 05:57 已停 80/20。Beta 不复活混袖 |
| 7 | **Size/小盘倾斜复活**（绕过 log 市值残差或宇宙底 30%） | **硬冲突** | Mandate `microcap_as_universe_banned` / hard_cap=0；Core Size/MidCap 带。缺市值 PIT 不得静默用 T |
| 8 | 仅靠 SW L1 demean 宣称 **持仓行业中性**，不报持仓偏离 | **软冲突** | demean ≠ 持仓中性；对标 Core 行业 ±8%/≤20% 与 Mandate 25% 帽必须持仓侧另报 |
| 9 | who_pays / 接线以 **精神/情绪/叙事** 解释隔夜 | **硬冲突** | Alpha/AI 已硬禁；与 v23 REJECT 同构；Beta 不接受叙事作为风险预算理由 |
| 10 | 拥挤后用本叶 **降特质波动卫星**（vol 已高时优先） | **无冲突** | 与 §2.1 行 2 一致；前提：独立 `.ok`+实证后、且不抬 β★ |

**一行摘要（给主 / Leo）**：硬 = `+ivol` 冲年化、当 β 旋钮、混叶26/moneyflow、复活微盘、精神叙事；软 = 隔夜β口径、叶18 伪耦合预算、行业 demean≠持仓中性、low_vol z 顶格；无/软兼容 = 主规格 −ivol 作降特质波动卫星（默认关，未实证）。

---

## §3 草稿接线规则（研究开关，默认关；不改 Mandate）

开关名建议（研究草稿，**非** Mandate 字段）：`leaf27_idio_vol_satellite=false`（默认）。

只动「是否把叶27 base-α 向量纳入研究级卫星诊断/未来叠仓候选」；**不**改 `target_beta` / `target_vol` / `max_etf` / DD L1–L4；**不**写实盘权重。

### 3.1 叠仓前必报（缺一则不开）

1. 组合 realized **年化 vol** 与对 **510300** 的 close-close β（及是否另报 open-open 敏感）；
2. holdings-weighted **Size / MidCap z**（对标 ±0.35σ + 既有 slack 口径）；
3. **行业**绝对权重与相对 wb 偏离（对标 Mandate 25% 与 Core ±8%/≤20%）；
4. vs 叶18/18v/叶24/capacity_adv 的 **Jaccard 与 ρ_excess**（Alpha 硬闸原文；Beta 只消费，不改阈值）；
5. holdings-weighted **low_vol z**（对标 max_abs_z 0.75）。

### 3.2 动作规则（草稿）

| 条件 | 动作 |
|---|---|
| 组合 vol **>16%**（现状 Core 即是） | 本叶若开，**只**允许作**降特质波动**卫星（权重上限研究自定且须事前写死）；**禁止**借本叶抬 β★ / 加权益 |
| 组合 vol 已 ≤16% 且 β 在带内 | 仍默认关；若开，卫星权重以不把 low_vol \|z\| 顶穿 0.75、不把 vol 推回 >18% 为软闸 |
| Jaccard≥0.7∧近等权 对叶18 | **硬拒**叠仓（Alpha）；Beta 不同时给「第二份 low_vol 预算」 |
| 有人提议主规格改 `+ivol` | **拒绝**；冻结后禁翻号 |
| 有人提议本叶调 `β_eff`/`vol_eff`（ETF 流旋钮族） | **拒绝**；本叶 ≠ ETF β 预算旋钮（见 `BETA_ETF_FLOW_PREMIUM_BETA_SIGNAL_DRAFT_ZH`） |

### 3.3 明确禁止

- 精神/情绪/叙事主轴或风险预算理由；
- 无残差 Top-N 等权当闸；
- 绕过 Arch `.ok` 读生产收益「先看年化再接线」；
- 改 Mandate JSON / 碰纸面轨 / `live=true`；
- 挡叶25 10:00–10:45 ET 窗或复用叶25 `.ok`。

---

## §4 缺数 / GAP（只列，不读生产收益）

| # | GAP | 影响 | 谁 |
|---|---|---|---|
| 1 | SW L1 PIT 完整 as-of（既有 `sw_pit` 缺票教训） | 行业 demean 不完整 → 信号「假中性」 | Data |
| 2 | OHLC / `adj_price` 实现 sha 重钉；`open`/`pre_close` 停牌涨跌停旗名 | 无效票规则与 β/ivol 窗覆盖 | Data / Arch |
| 3 | 叶18 / 18v / 叶24 **α 向量**是否仍在盘面可对齐 | 正交 Jaccard/ρ；伪耦合预算诊断 | AI / Arch |
| 4 | capacity_adv 暴露/活跃指示 PIT | 残差第 5 步；缺则 GAP 不得静默跳过 | Data |
| 5 | 本叶独立研究/selftest `.ok` | 无 .ok **不**回测、不报 IC/年化 | Arch（叶25 窗后另窗） |
| 6 | 盒机实数据跑 | 仍须 Arch .ok；本页遵守禁跑 | Arch / 主 |

---

## §5 非动作与下一步

**非动作（本页）**

- 不申 Arch `.ok`；不跑脚本/自检/读收益；不改 Mandate；不碰纸面；不改 α 标签；不派 Eng/Book-Smoke；
- 不挡叶25@10:00–10:45 ET；不复用叶25 钉（`7b279d47` / `be7f5e5a`）；
- 不重写 who_pays；不假装有实证 β/vol/IC；
- Core v1.3 门控 **FAIL 两档不变**，去留**仍等 Leo**；本页不复活 Core。

**下一步**

1. 叶25 窗结束后，本叶若进实证：Arch 另窗签独立 `.ok` + Data 契约确认（§4）→ AI/Eng 跑覆盖与自检（非本角色）；
2. 叠仓诊断按 §3.1 五元组；伪耦合按 §2 行 5；
3. 研究开关保持 `leaf27_idio_vol_satellite=false` 直至有独立回执且 Leo/主书面点开；
4. Beta 下一拍：仅在主 Agent 点名时更新冲突矩阵（例如 Core 去留裁定后）。

---

## §6 引用钉（盘内 sha，写时实测）

| 文件 | sha256 |
|---|---|
| AI who_pays DRAFT | `4a0eec1a4d1694be7a91b8cd291b8d1547e68ff41f8b9121e90dd7f44967282b` |
| Alpha 空位填审 | `01ab6bf39ca276c459c9febb1178f1d1afa9e5b8170a167b4a16a904a297f801` |
| AI 预注册 r1 FROZEN | `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` |
| Mandate V2 JSON | `04afacc45778bfcdcfbcc7b8ff73098f2ec843cd49fea6ef406d297e05e68f0f` |
| BETA_VOL_TARGET_HANDOFF | `3872d1a449b8704ae398f79881194aa7ab6b49cfe7e9fc2689893b62f0ddedfa` |
| BETA_CORE_V1_3_GATE_REVIEW_ZH | `8bff82f1b30c92898fb5cc8c681dd8c3440925a71eef1bdd72918db72990a4fa` |
| 叶18 who_pays 预注册 | `b00a1f9ea5e50cf928c001e4caa48483fac1951019cb62d02beb4c3df53aa00e` |
| 板式：ETF 流 β 信号草稿 | `0fa22cd818bdd2c348a9e71842babd4cdab4caed0d47f1d722b01c98797e9efd` |

叶18 结局（对照教训，非本页实证）：WEIGHT 回执 **WATCH**（Gate A/B 不过、GATE_V3 FAIL、不可交易/衰减）；18v 换手改善仍 WATCH。叶27 不得 silent 复跑 `std(ε_on)`。

---

## §7 落盘与门锁

- 路径：`docs/v2/BETA_LEAF27_ON_MINUS_ID_IDIO_BETA_STYLE_CHECK_ZH.md`（写前确认不存在；未覆盖任何旧文）
- `leaf27_idio_vol_satellite=false`；`live=false`；`promotion_approved=false`
- 最终 sha256：见落盘后 `sha256sum` 实测（R3；正文至此结束，避免自指改哈希）

- 落盘 R3 实测 sha256：`321e2c5db32bf1d4f18eb9a8d0cb6d330f34caf7c5b231a22787c6da6977e096`（2026-10-25；America/New_York）
