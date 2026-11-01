# 【DRAFT — 未排号】技术/拥挤/状态复合分 who_pays / 预注册草案

## 修订说明（Alpha 预审补丁 · P1–P8）

- **修订时点**：2026-10-25 ~12:00 ET（America/New_York；箱 `date`）
- **作者**：QuantLab AI（执行器）
- **触发**：Alpha 闸门预审 = **ACCEPT_DRAFT_WITH_PATCHES**（**非**叶级 ACCEPT / **非** FROZEN）
- **旧 DRAFT 全长 sha256**：`655d2a3c447b12fcb741938f4f15659a1da91b98c175d460fcb5ca73d1a32a0f`（sha8=`655d2a3c`）
- **Alpha 预审全长 sha256**：`cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a`（sha8=`cf68d904`；路径 `docs/v2/ALPHA_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_PREREVIEW_20261025_ZH.md`）
- **本修订范围**：同文件修订；升 FROZEN 前必须项 **P1–P6** 全补；建议项 **P7/P8** 顺手补
- **本修订不做**：申 `.ok`；开跑；实跑；git commit；改脚本；升 FROZEN；排号
- **不挡**：叶25 mem_probe / 全叶 X2（另轨）；叶27 已 VOID 不复用

| 补丁 | 级别 | 落点摘要 |
|---|---|---|
| P1 | 必须 | §5 正交硬闸表显式纳入叶25 / 叶26 / capacity_adv / moneyflow_resid（Jaccard≪0.7 ∧ 近等权拒） |
| P2 | 必须 | §3.A 一次写死：方向、状态档数与权重表、β/mom/vol 窗、停牌涨跌停剔除；禁冻结后读收益翻档/翻号 |
| P3 | 必须 | 资金维默认 **OFF**（至主裁相对 moneyflow_resid 裁定启用；启用则强制残差+Jaccard） |
| P4 | 必须 | 筹码 POC **默认关闭**；无 PIT 不得编造；不得静默进主 α |
| P5 | 必须 | OHLC / volume / 复权价 / 指数 available_at·as-of 契约重钉；广度 GAP→状态臂降级并回执披露 |
| P6 | 必须 | 动量维 vs style mom 臂双重计分披露与处理（残差前剔除 / 降权 / 仅披露，FROZEN 三选一写死） |
| P7 | 建议 | 状态指数单一钉（默认 **510300**）；与叶25 共用 `sw_l1_asof_with_gap_carry` 一旦落地禁私造 |
| P8 | 建议 | 正文保留 vs Beta A6：本叶选股 α ≠ Mandate 降仓旋钮 |

---

- 角色：QuantLab AI（后台执行器）
- 时点（初稿）：2026-10-25 ~11:46–11:50 ET；**修订**：~12:00 ET
- **状态=DRAFT**；**未排号**；**待主排号**；NOT FROZEN。
- 来源：Leo（经主 Agent ~11:45 ET）纠正——AlphaLens「技术/拥挤/状态复合分」**开放为研究叶**（非禁区）；吸收计划修订见 `docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md`。
- 对照结构：`docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md`；残差/HI_LIQ/Gate 惯例对齐叶25 accruals DRAFT。
- Alpha 政策钉：`docs/v2/ALPHA_GATE_RESEARCH_TECH_COMPOSITE_LLM_DEBATE_20261025_ZH.md`（残差候选叶+WF/闸门；**禁**页面 TOP 当超额）。
- **禁**：申 `.ok`；自开跑；实跑读盘调参；git commit；把页面 TOP/榜单当超额证明；无残差 Top-N 叙事冒充 α。
- **不挡**：叶25 mem_probe / r6 FROZEN 另轨；叶27 VOID 不复用旧 `.ok`。
- `live=false`；`promotion_approved=false`；`research_only=true`。

---

## 0. Alpha 空位填写（交主排号用·可整段摘抄）

> **mechanism_tag（拟）**：`g1g5_ashare_tech_crowd_state_composite_v1`（**未排号**；正式叶号待主）  
> **who_pays（一句）**：付钱的是在日频价量上忽视「趋势/动量/量能/波动/位置拥挤/多周期共振」经 **SW L1 + style（logmv/β/mom/vol/ADV）截面残差** 后、再按市场状态（进攻↔防守）重加权的复合分所刻画的**拥挤兑现与状态切换错配**——对手盘在高拥挤一侧过度追涨、或在状态已切防守时仍按进攻权重持仓，从而在下一窗支付均值回归与换手成本；**不是**「页面 TOP 好看」叙事对手。（资金维默认 OFF，见 §2/§3.P3；启用后须再钉残差。）  
> **可检验预测（冻结前不读收益选号）**：残差复合 α 对次日/次周特质收益的截面 IC 符号在正式预注册冻结时写死；walk-forward 各折同号且非仅首折有效；活跃集 vs **capacity_adv / moneyflow_resid / 叶18·24·25·26·27** 的 Jaccard ≪0.7 且 frac(J≥0.7)=0；须报残差 ρ。  
> **失效条件**：以 AlphaLens 页面 TOP/评级榜当超额证明；主交付退化为 Top-N 名单无 α 向量；无 SW/style 残差；状态权重事后按收益翻档；把筹码峰/未入库字段静默编造；与 moneyflow_resid / 叶25·26 近等权换皮；冻结后翻方向；广度 GAP 却静默假装有广度臂。  
> **交 Alpha 时点**：主排号 → 正式预注册 FROZEN → Arch 审脚本 → **独立**新窗 `.ok` → X2/密封分签回执之后；现在只交 DRAFT（已吸收预审补丁，仍非 FROZEN）。

---

## 1. 机制与谁付钱（可检验假说）

| # | 假说 | 可检验陈述 |
|---|---|---|
| H1 拥挤兑现 | 高「位置+乖离+涨幅分位」拥挤侧后续特质收益偏低 | 残差后 crowding 分位最高组 vs 最低组，WF 折内 IC/多空差符号事前钉死（DRAFT 倾向：高拥挤→惩罚） |
| H2 状态切换 | 市场由进攻切防守时，未降权的动量暴露支付回撤 | 状态代理（指数趋势+广度+波动，见 §3；广度 GAP 则降级）切档后 T+1..T+k 内，进攻权重组合相对防守权重的超额为负（研究披露；非本 DRAFT 实跑） |
| H3 反转袖 | 震荡/防守态下短期反转贡献上升 | 状态条件 IC：动量维在进攻态 IC>0、震荡态减弱或翻号；反转/低波维相反——须 WF 内事前分层，禁全样本事后挖（资金残差袖默认 OFF，见 P3） |

**允许**：价量公式、截面残差、状态条件权重、α 向量。  
**禁止**：页面 TOP / 强烈看多榜 / 「交易计划」叙事当闸；把 AlphaLens OOS 纸面数字直接当本叶证据。

主交付：**日度 base-α 向量**（`session → instrument → alpha`），**不是** Top-N 名单。

**双轨一句**：判决宇宙 **HI_LIQ**（纸面硬闸）；**FULLA** 仅研究披露 / 覆盖对照，不得以 FULLA 数字代替 HI_LIQ 过门。

**六硬钉（保持）**：

| # | 硬钉 | 本 DRAFT 落点 |
|---|---|---|
| 1 | 截面残差 = SW + style | §3：SW L1 → logmv → 滚动β → mom → vol → logADV20；合成后再 SW+style 一次得 base-α |
| 2 | HI_LIQ 判决 | §1 / §4：判决宇宙 HI_LIQ；FULLA 不得代过门 |
| 3 | walk-forward | §4：密封/X2 分窗；X2 内≥3 折；禁全样本一次拟合状态表 |
| 4 | Gate B / GATE_V3 | §4：CMC v1.2 / `leaf_selfcheck_v3.py`；sha 申 `.ok` 时重钉；本 DRAFT 不跑任一闸 |
| 5 | 机制 who_pays 写清 | §0 / §1：拥挤兑现+状态切换错配；H1/H2/H3；主交付日度 α 向量 |
| 6 | 禁页面 TOP 当超额 | §0 失效 / §1 禁止 / §5 首条；禁 AlphaLens OOS 纸面当本叶证据 |

---

## 2. AlphaLens 8 维 → 可复现子集（只列可用价量/已有库；缺则 GAP）

对照 `docs/v2/refs/alphalens_workbuddy/README.md` §8 维表。本叶**不**移植其页面权重原值当冻结 α；下列仅标「能否用本地价量/已钉库字段复现骨架」。

| # | AlphaLens 维 | 可复现子集（本地） | 状态 |
|---|---|---|---|
| 1 | 趋势结构（MA 排列/斜率/ADX） | MA5/10/20/60/120、MA20 斜率：由 `research/adj_price` 或 Arch 钉的日频 OHLC/复权价计算 | **REPRO** |
| 1b | ADX/DMI | 可由 OHLC 计算；工厂无现成列 → 实现时自算并钉公式 sha | **REPRO（自算）** |
| 2 | 动量（5/20 涨幅、MACD、RSI） | ret5/ret20、MACD、RSI(14)：价序列自算；与 style mom 臂双重计分见 §3.P6 | **REPRO** |
| 3 | 量能（量比、OBV、连阳放量） | 量比/OBV/阴阳×量：需日频 `volume`（与价同 PIT / available_at 契约，见 §3.P5） | **REPRO**（缺 volume PIT 钉 → **GAP**） |
| 4 | 波动可控度（ATR%、年化波动、60 日 MDD、Beta） | ATR/vol20/MDD60/β vs **510300**（P7 单一钉）：价序列自算 | **REPRO** |
| 5 | 位置与拥挤（120 日位置、BIAS20、距 60 高） | 价序列自算；拥挤合成可对照 `refs/.../crowding.py` 思想（位置/涨幅分位/BIAS），**不得**照搬其 ETF 池阈值当冻结闸 | **REPRO** |
| 6 | 资金（主力净流入、超大单） | 候选：`data/v2/moneyflow/moneyflow_stock_daily_pit.parquet`（`net_mf_amount`+`available_at`） | **默认 OFF（P3）**；至主裁相对 moneyflow_resid 裁定启用。启用则：**强制**残差 + Jaccard≪0.7；否则剔除本维，不得静默进主 α |
| 7 | 多周期共振（日×周） | 日频聚合成自然周 OHLC 后再算趋势/动量一致度 | **REPRO** |
| 8 | 形态结构（摆动点、布林 %B、筹码 POC） | 摆动高低、布林 %B：价序列 **REPRO**；**筹码峰 POC / 密集区** | **默认关闭（P4）**；工厂无筹码分布 PIT → **GAP**；**禁止编造**；不得静默进主 α；仅允许标 S-chip 敏感性且默认 OFF |

**状态机输入（非 8 维内，但是复合分的状态臂）**：

| 输入 | 本地可行性 | 契约（P5 / P7） |
|---|---|---|
| 指数趋势 | ETF/指数日频若已 PIT 钉 → REPRO；未钉 → GAP | **单一钉默认 510300**（P7；正式预注册写死 510300 vs 000300，禁双钉混用）；须钉 `available_at` / as-of |
| 市场广度（上涨家数比等） | 全 A 涨跌统计若无现成 PIT 广度表 → **GAP** | 不得用「当日股票池」幸存者样本冒充广度；GAP → 状态臂**降级**为「指数趋势+波动」两因子三～五档，**回执必须披露降级**（P5） |
| 波动（指数 vol） | 指数收益序列自算 → REPRO | 同源依赖指数 PIT / available_at |

缺广度时：状态臂降级为「指数趋势+波动」两因子三～五档，**回执披露降级**；不得静默假装有广度。

---

## 3. 信号草图（DRAFT；窗长/权重在 FROZEN 瞬间一次写死）

1. 对每维可复现子分数做 winsor→截面 rank→正态分（或工厂惯例 z）。  
2. **截面残差**（同日；缺则记 GAP，不得跳过）：  
   1. SW L1 demean / dummies（as-of 与叶25 同族；**P7**：`sw_l1_asof_with_gap_carry` 一旦落地须共用，禁私造）  
   2. vs **logmv**（T−1 流通市值）  
   3. vs **滚动 β**（vs **510300**；窗长见 §3.A）  
   4. vs **mom**（如 t−120→t−20；与动量维双重计分见 §3.P6）  
   5. vs **vol**（如 vol20）  
   6. vs **logADV20**（capacity 惯例）  
   7. 披露 vs capacity_adv / moneyflow_resid / expand / 叶18 / 叶24 / **叶25** / **叶26** / 叶27 α 的 ρ 与 Jaccard（硬闸见 §5）  
3. **状态权重**：五档或降级三档（广度 GAP 时）；进攻偏动量/趋势，震荡偏反转，防守偏低波+反拥挤。**资金维默认不参与状态袖**（P3）。权重表在 FROZEN 瞬间写死；**禁**读本叶收益后改表（P2）。  
4. 合成 `α_raw` → 再经一次 SW+style 残差得 **base-α**。  
5. 拥挤闸（研究级）：高拥挤分位可作**过滤/降权**，默认不单独开第二主叶。**P8**：与 Beta A6「拥挤进 β 预算」分轨——**本叶是选股 α，不是 Mandate 降仓旋钮**。

### 3.A P2 — 方向 / 状态权重 / 窗 · 一次写死（升 FROZEN 时填入终值；本表为 DRAFT 预填草案）

| 项 | DRAFT 预填（FROZEN 瞬间替换为终值并封口） | 翻档禁令 |
|---|---|---|
| 方向 | 高残差复合分（经拥挤惩罚后）做多；拥挤维为惩罚项 | **禁**冻结后读 IC/收益翻多空号 |
| 状态档数 | 默认五档（进攻 / 偏进攻 / 震荡 / 偏防守 / 防守）；广度 GAP 降级为三档并回执披露 | **禁**读收益后增删档 |
| 状态权重表 | 进攻：动量/趋势↑、反转/低波↓；震荡：反转↑、动量中性；防守：低波+反拥挤↑、动量↓。具体数值表 FROZEN 一页钉死 | **禁**冻结后按本叶收益/IC 翻档 |
| β 窗 | DRAFT 倾向 60 交易日 vs 510300（P7）；FROZEN 写死 | **禁**事后择窗 |
| mom 臂窗（style） | DRAFT 倾向 t−120→t−20；与动量维处理见 P6 | **禁**事后择窗 |
| vol 臂窗 | DRAFT 倾向 vol20 | **禁**事后择窗 |
| 停牌 / 涨跌停 | 剔除当日不可交易（停牌）及一字涨跌停不可成交样本，口径与叶25 同族；正式预注册钉细则 | **禁**用可交易池回填冒充历史宇宙 |
| 读收益选号 | **本 DRAFT 与未来 FROZEN 均禁止** | 失效条件 |

### 3.P3 — 资金维默认 OFF

- 维 6（主力净流入等）**默认 OFF**，不进主 α、不进状态袖。  
- 启用条件：主裁相对 **moneyflow_resid** 书面裁定启用 → 强制 SW+style 残差 + §5 Jaccard/ρ 闸通过。  
- 未裁定前：敏感性实验仅允许隔离披露，**不得**混入主 α 向量。

### 3.P4 — 筹码 POC 默认关闭

- 维 8 中筹码峰 / POC / 密集区：**默认关闭**。  
- 无 PIT 筹码分布库 → GAP；**禁止编造**；不得静默进主 α。  
- 仅允许单独 S-chip 敏感性标签且默认 OFF。

### 3.P5 — available_at / as-of 契约与广度降级

| 数据 | 须钉契约 | GAP / 降级 |
|---|---|---|
| OHLC / 复权价 | `available_at` + as-of；与叶25 价源同族优先 | 缺钉 → 不得开跑本叶 |
| volume | 与价同 PIT / available_at | 缺 → 量能维 GAP，复合分剔除量能或降级披露 |
| 指数（状态臂 / β） | **510300**（P7）日频 PIT + available_at | 缺 → 状态臂/β GAP，不得用未钉指数冒充 |
| 市场广度 | 全历史非幸存者 PIT 广度表 | **GAP → 状态臂降级为「指数趋势+波动」**；X2/密封回执**必须**披露降级事实与档数 |

### 3.P6 — 动量双重计分披露

动量维（§2 维2：ret5/ret20/MACD/RSI）与 style 残差 **mom 臂**（§3 步骤 2.4）存在双重计分风险。升 FROZEN 前须三选一写死并在回执披露：

| 选项 | 含义 |
|---|---|
| A 残差前剔除 | 动量维子分在进残差前已正交掉 style mom 臂口径，或动量维不进合成、仅作研究披露 |
| B 降权 | 动量维系数显式降权（数值 FROZEN 钉死），并披露与 mom 臂的 ρ |
| C 仅披露 | 双臂均保留，但 Gate/回执强制披露双重计分风险与 ρ；**不得**静默 |

DRAFT 倾向：**选项 A 或 B**（优先避免静默双计）；终选 FROZEN 写死。

### 3.P7 — 状态指数单一钉 + SW 共用

- 状态趋势臂与滚动 β 的指数锚：**默认单一钉 510300**；若主/Data 改钉 000300，须全文一致替换，禁 510300/000300 混用。  
- SW L1：与叶25 共用 `sw_l1_asof_with_gap_carry`（一旦落地）；**禁**本叶私造 as-of / gap-carry。

### 3.P8 — vs Beta A6（Mandate）

- 本叶交付的是**选股截面 α**。  
- Beta A6「拥挤进 β 预算」是 Mandate **降仓旋钮**，与本叶分轨。  
- 不得以本叶拥挤分直接改组合杠杆/仓位预算冒充 α 闸通过。

**方向（与 §3.A 一致）**：DRAFT 倾向「高残差复合分（非拥挤惩罚后）做多」；拥挤维符号为惩罚项。正式方向以 FROZEN 文为准；本 DRAFT **不读收益选号**。

---

## 4. 宇宙、WF、Gate 入口

| 项 | DRAFT 约定 |
|---|---|
| 判决宇宙 | **HI_LIQ**（与叶23/24/25 同族 ADV 底与单名帽惯例；具体帽在正式预注册钉） |
| 研究披露 | **FULLA** 覆盖/IC 对照一句带过；过门数字以 HI_LIQ 为准 |
| Walk-forward | 密封 / X2 分窗；X2 内再切 ≥3 折（折界冻结时钉）；禁「全样本一次拟合状态权重」 |
| Gate A | ρ vs capacity_adv 等共用闸；残差 α>0 披露 |
| Gate B | CMC v1.2：`research/alpha_combo_marginal_v1_2.py`（现盘 sha 在申 `.ok` 时重钉）；cap80+叶20 等门控组合 |
| GATE_V3 / 衰减 | `research/leaf_selfcheck_v3.py`（现盘 sha 申 `.ok` 时重钉）；衰减 KEEP；换手/MDD 门槛随正式预注册 |
| 成本 | 研究比较默认 30bp/边（与叶25 披露惯例对齐）；对照表可并排 17.5bp |

本 DRAFT **不跑** 任一闸。

---

## 5. 正交硬闸与禁项（P1 强化）

### 5.1 正交硬闸表（升 FROZEN / 申独立 `.ok` 前须过）

活跃集与下列对象两两比较；默认门槛：**Jaccard ≪ 0.7** 且 **frac(日度 J≥0.7)=0**；近等权（权向量 ρ 过高或换皮）**拒**。须同时报残差后 ρ。

| # | 对照对象 | 闸 | 备注 |
|---|---|---|---|
| O1 | **capacity_adv** | Jaccard≪0.7 ∧ 近等权拒；报 ρ | 共用容量叶；Gate A 同族 |
| O2 | **moneyflow_resid** | 同上；资金维若仍 OFF 则本行作「启用前预留对照」 | P3：默认 OFF；启用后本行升硬闸 |
| O3 | **叶25**（accruals / r6 族） | 同上 | P1 显式纳入；禁与财务应计叶换皮 |
| O4 | **叶26** | 同上 | P1 显式纳入 |
| O5 | 叶18 / 叶24 / 叶27（价量快叶族） | 同上 | 近等权拒 |
| O6 | expand / 其他已钉 α | 披露 ρ + Jaccard；近等权拒 | 正式预注册可扩表 |

### 5.2 禁项

- **禁页面 TOP 当证明**：任何 README/API「TOP 预览」「强烈看多」不得写入回执「超额」栏。  
- **禁幸存者池**：不得用「当日可交易池回测」冒充全历史 HI_LIQ；广度同理（P5）。  
- **禁无残差动量换皮**：未 SW+style 的 ret20/60 合成 ≠ 本叶。  
- **禁静默双重计分**：动量维 vs style mom 未按 §3.P6 披露处理。  
- **禁静默资金维 / 筹码 POC**：违反 P3/P4。  
- **禁冻结后翻档/翻号**：违反 P2。  
- **vs AlphaLens 纸面**：禁止把其 OOS 配置表复制为 PASS 证据。  
- **禁复用他叶 `.ok`**：不得复用叶25 step_m1 `.ok` `1c32ab1e` 或叶27 VOID/`8bcd79dc` 等冒充本叶授权。  
- 卖方/金股/一致预期/GP/杠杆：禁。  
- LLM「模型说多就买」：禁进本叶（另轨 P1-(B)，本 DRAFT 不审）。

---

## 6. 待主排号 / 升 FROZEN 清单

| # | 项 | Owner 建议 | 与补丁 |
|---|---|---|---|
| 1 | 正式叶号 / mechanism_tag 终钉 | 主 | — |
| 2 | 日频 OHLC/volume/复权价/指数 PIT·available_at 契约重钉；广度表有无 | Data | P5 / P7 |
| 3 | SW as-of 共用函数落地确认（`sw_l1_asof_with_gap_carry`） | Arch / Strategy | P7 |
| 4 | 资金维：保持 OFF vs 主裁启用（相对 moneyflow_resid） | 主 + Arch | P3 |
| 5 | 筹码 POC：确认 GAP、默认关闭 | Data + AI | P4 |
| 6 | 状态档数与权重表 + 方向 + β/mom/vol 窗一次写死（FROZEN 文） | AI 起草 → Arch 审 | P2 |
| 7 | 动量双重计分选项 A/B/C 写死 | AI → Arch | P6 |
| 8 | §5 正交表对叶25/26/capacity_adv/moneyflow 的阈值进正式预注册 | AI → Alpha 复核 | P1 |
| 9 | Gate B / GATE_V3 脚本 sha 重钉进正式预注册 | Arch | — |
| 10 | 排窗与独立 `.ok`（不与叶25 mem_probe/X2 抢；不复用废窗） | 主 | — |

**无 P1–P6 落地 → 不得升 FROZEN / 不得申本叶独立 `.ok`。**

---

## 7. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF_TECH_CROWD_STATE_COMPOSITE_WHO_PAYS_DRAFT_20261025_ZH.md` |
| 状态 | DRAFT（已吸 Alpha 预审 P1–P8）；未排号；待主排号；**仍非 FROZEN** |
| 旧 sha256 | `655d2a3c447b12fcb741938f4f15659a1da91b98c175d460fcb5ca73d1a32a0f` |
| Alpha 预审 sha256 | `cf68d904103815a6857154a00af09c9deae33294b38444c2f4b76e33bc74079a` |
| live | false |
| promotion_approved | false |
| 本回合动作 | 只修订文档；**未**申 `.ok`；**未**开跑；**未**实跑读盘；**未** git commit |
| 回执 | `docs/v2/audit/AI_LEAF_TECH_CROWD_P1P6_PATCH_RECEIPT_20261025_ZH.md` |

**sha256**（整文件）：落盘后以 `sha256sum` 为准（见回执）。
