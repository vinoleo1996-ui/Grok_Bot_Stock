# 【DRAFT — 未冻结】叶26 预注册 r1：宽基 ETF 资金流→个股 who_pays（g1g5_ashare_broad_etf_flow_stock_v1）

- **起草时刻**：2026-10-25 07:09:00 ET（America/New_York；箱 `TZ=America/New_York date`）
- **角色**：QuantLab Arch（执行器起草；研究级 DRAFT，非 AI 冻结）
- **状态**：**DRAFT（未冻结；正式 FROZEN 另候主令）**
  - 本文件写死研究边界、池、`pit_basis`、宇宙双轨与正交闸口径；**不**写死主规格 α 符号（r2 明示「不读收益选号」；符号在正式 FROZEN 瞬间落盘，冻结后禁翻号）。
- **声明**：起草前**未读**本叶任何收益 / IC / X2 / 密封读数以选方向或窗长；主规格口径摘自 who_pays DRAFT r2 + Data 缺口回执 + Arch 契约预告。
- **MATCH 三件**（落盘前 `sha256sum` 核盘；全长）：
  | 输入 | 路径 | sha256 |
  |---|---|---|
  | who_pays DRAFT r2 | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` | `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` |
  | Data 缺口回执 | `docs/v2/audit/DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` | `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` |
  | Arch 契约预告 | `docs/v2/ARCH_AI_LEAF26_CONTRACT_PREVIEW_20261025_ZH.md` | `5c44944c2a496a5cc461459d9b9f232116bfa152a41f1b26f8e21427a9a42f36` |
- **旁证（非闸；不覆写）**：
  - Strategy 袖套：`docs/v2/STRATEGY_ETF_FLOW_SLEEVE_PLAN_20261025_ZH.md` sha256 `7722efec9f750ec89b2047d5890a39a119771eb86c8fb35bc265217b82286091`
  - 旧 Data 盘点：`docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md` sha256 `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305`
  - Alpha 骨架（候选1 ETF 资金流空位）：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md` 钉 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605`
- **锁**：`live=false` · `promotion_approved=false` · 研究级 · **不申 `.ok`** · **不** git commit · **不挡**叶25 10:00–10:45 ET（钉 `7b279d47` / R5c_v3 `be7f5e5a`）· 叶27 `.ok` 另窗（≥10:50 ET）正交 · 禁 GP / 卖方 / 金股 / 一致预期 · 禁个股 moneyflow 主轴 · 禁 etf_core 双计 · **禁扩池**（默认池不得 silent 纳入 `512100`/`000852`）· **禁静默称严格 PIT**

---

## 0. mechanism_tag 与 who_pays（一句）

> **mechanism_tag**：`g1g5_ashare_broad_etf_flow_stock_v1`（叶26；与 r2 / Arch 预告一致；**不用**未钉的 `…_who_pays_v1` 别名）  
> **who_pays**：付钱的是在宽基 ETF 大额申赎日、忽视「ETF 产品层份额流→篮子权重」传导而承接 AP 机械买卖冲击的个股定价对手——**不是**个股 `net_mf_amount` / moneyflow_resid 对手盘，也不是直接持有 ETF-core 的配置差对手盘，也不是行业 ETF 流（叶4/8a）或 idx_rebal 事件对手。

**可检验预测**（正式 FROZEN 时写死符号；本 DRAFT 不选号）：经残差化后的 ETF 流量暴露 α，对次日特质收益的截面 IC 符号以冻结瞬间主规格为准；活跃集 vs moneyflow_resid / etf_core / resid_etf / idx_rebal_flow / capacity_adv / 叶25 / 叶27 的 Jaccard ≪0.7 且 frac(J≥0.7)=0；须报残差 ρ。

**失效条件**：主信号混入个股 D2 moneyflow；或退化成持有 ETF≈0.70 / etf_core 换皮；或与 moneyflow_resid 近等权（Jaccard≥0.7）；或无 PIT/未披露 `pit_basis`；或默认池擅自纳入 512100/000852 而未与 Strategy+Data+Arch 共签并 bump 预注册；或正式冻结后事后翻号。

---

## 1. 主规格 ETF 池（禁扩池）

| 项 | DRAFT 钉 |
|---|---|
| **主规格池** | **仅** `510300.SH → 000300.SH` 与 `510500.SH → 000905.SH` |
| **默认剔除** | `512100.SH` / `000852.SH`（与 Strategy 袖套默认池、r2、Arch 预告对齐） |
| 映射契约 | 研究级**硬编码**上两对；无 Arch 官方映射表；`fund_basic` 仅旁证 |
| 联接去重 | 无名契约；major 名单事实未纳入联接（非契约保证）；主规格不依赖联接 |
| 扩池 / 敏感性 | 000852/512100 / premium / hk_hold / 美 ETF：**另签**；须 Strategy 书面改默认池 + Data 映射/PIT 共签 + **预注册 bump（新文件名）**；**不得 silent** |

**硬规则**：本 DRAFT / 未来 FROZEN 正文默认池一律不得 silent 写入 512100/000852。

---

## 2. 双宇宙（看结果前同时写死；α 向量非 Top-N）

| 口径 | 掩码 | 角色 | 行业帽 |
|---|---|---|---|
| **FULLA_V1**（研究主报） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | 研究级主报密封重叠段 + X2 对照 | SW L1 ≤28% |
| **HI_LIQ_V1.1**（纸面候选） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | 纸面候选路径；密封满窗 + X2 并报 | SW L1 ≤25% |

掩码列沿用既有契约（含 `date, instrument, in_universe, st, suspended, young, adv_fail, adv20_yuan` 等）。本叶不新开宇宙。

**主交付**：**日度 instrument→alpha 向量**（base-α）；**不是** Top-N 名单当闸。评价簿（60万/100万）仅作自检/并报表构造，不得把「取前 N 名」倒灌为 α 定义。

---

## 3. `pit_basis`（硬写专节；对齐 Data `aaf84d66…` / Arch `5c44944c…`）

本叶研究级主规格**允许**推进，但**不得**静默称严格 PIT。凡消费权重表或旁路拼装，回执与脚本首页必须披露本节。

### 3.1 主规格可用代理（研究级）

| # | 输入 | 研究级路径 / 规则 | `pit_basis` / asof | 状态 |
|---|---|---|---|---|
| A | 宽基份额流（**主输入**） | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（含 510300/510500；`available_at` 至 20261009） | 份额次日 09:00 规则见 manifest；消费侧以文件 `available_at` 为准 | **OK**（研究级；签 `.ok` 前重钉表 sha） |
| B | 指数权重 asof（**主映射**） | `data/v2/index_members/index_weight_csi300_500_1000.parquet`（列：`index_code,con_code,trade_date,weight`；至 20260930；**无** `available_at`） | **`pit_basis=month_end_snapshot_no_available_at`**：`trade_date≤session` 最近月末点；**不得**把月末 `trade_date` 当作披露可得时点静默前视 | **GAP**（严格 PIT）；研究级可绕 |
| C | ETF↔指数映射 | 硬编码两对（§1） | 映射静态；扩池另签 | **PARTIAL**（无 Arch 钉表；主规格可绕） |
| D | SW L1 / log 流通市值 | 与叶25/27 同族契约；市值 **T−1** | 缺市值不得静默用 T | 沿用族契约；实现 sha 另窗重钉 |
| E | capacity_adv / moneyflow_resid（残差对照） | 既有暴露/活跃指示 | 仅残差/正交，不进主信号合成 | 缺则记 GAP |

### 3.2 GAP（主规格不硬阻塞 vs 硬阻塞「严格 PIT / `.ok`」）

| # | GAP | 阻塞叶26 r2 主规格？ | DRAFT 处置 |
|---|---|---|---|
| 1 | `index_weight` 无 `available_at` | **软阻塞**严格 PIT；研究级可绕 | 首页+回执硬披露 `pit_basis=month_end_snapshot_no_available_at`；正式 FROZEN / `.ok` 前须 Arch 明示接受本披露或落列 |
| 2 | 宽基映射无 Arch 钉表 | **否**（研究级两对硬编码） | 主规格不扩池；扩池硬阻塞 |
| 3 | 000852 / 202610 空 | **否** | 主规格剔除；敏感性另签 |
| 4 | `hk_hold` 密窗（密→20240816；后稀疏） | **否**（非主轴） | 禁作主信号；2024-08-16 后勿当日频；Intel `nb_hold_*` 另裁 |
| 5 | premium PIT 无现成表 | **否**（非主轴） | 可研究拼装 `etf_daily_adj` ⋈ share `unit_nav`（asof=两表 `available_at` max）；**本 DRAFT 不落地**；另签 |
| 6 | 美 ETF PIT 无 | **否** | 非主轴；另签时区规则后落表 |
| 7 | `hsgt_top10` manifest 漂移 | **否** | 消费以文件为准；catalog 校准不阻塞 |

**r2 主规格不硬阻塞声明（摘 Data）**：主输入（`etf_share_flow_pit_major` 含 510300/510500 + 权重表 000300/000905）本地可读；真正挡「正式预注册 / 严格 PIT / `.ok`」的是**权重 PIT 契约**（及日后扩池映射）。本 DRAFT 接受研究级绕行并硬披露 `pit_basis`；**不**因此申请 `.ok`。

### 3.3 禁读作主轴

- 个股 `moneyflow_stock_daily_pit` / `net_mf_amount` / moneyflow_resid（仅可作残差/正交对照）
- etf_core 持仓差（禁双计）
- 行业 ETF 流（叶4/8a）；idx_rebal 事件流
- 叶25 应计 / financials；叶27 `on_minus_id` 价量拆分
- 卖方 / 金股 / 一致预期；补跑 `.ok` sha8 `9e4359f9`（Arch CONSUME_SUSPEND）
- 未披露 `pit_basis` 的权重「伪 PIT」

---

## 4. 机制与残差化清单（研究级；缺任一步 → GAP，不得静默跳过）

### 4.1 主轴构造（产品层→篮子→个股）

1. 取主规格池 ETF 的产品层份额净变动（来自 §3.1-A；PIT/`available_at` 规则见 manifest）。  
2. 经 §1 硬编码映射到指数；用 §3.1-B 权重 asof（`pit_basis` 披露）把 ETF 流量映射为个股截面**流量暴露**（flow×weight 族；实现细节在 Arch 审脚本窗钉，本 DRAFT 不选实现变体）。  
3. 同日截面残差（顺序写死）：  
   1. SW L1 demean  
   2. vs log 流通市值 OLS 残差（市值 T−1）  
   3. （披露）vs capacity_adv 暴露/活跃指示  
   4. （披露）vs moneyflow_resid（正交，不进合成）  
4. 得 **base-α**（日度向量；分域 rank→[-1,1] 等实现细节正式 FROZEN / 脚本审时钉；**本 DRAFT 不读收益选变体**）。

### 4.2 方向（DRAFT：未冻结）

| 项 | 本 DRAFT | 正式 FROZEN 时 |
|---|---|---|
| 主规格符号 | **未选号**（对齐 r2「不读收益选号」） | 落盘瞬间写死 `α_raw` 符号；冻结后**禁翻号** |
| 敏感性 | 对侧符号仅可事前标为敏感性，不得升格 | 同左 |

### 4.3 评价权重（研究级默认叙述；不挡本 DRAFT）

- 再平衡：每 **5** 个交易日按当日 base-α 重算评价权重（与叶18/27 同类；正式跑前 Arch 审脚本确认，**不得**借此改池/`pit_basis`/符号）  
- 簿：AUM **60万** / **100万**；年化 **244** 主 / **252** 对照  
- 成本：30bp 单边作判定主口径；17.5bp 与 30bp 并列披露（对齐叶23/24/25/27 惯例）  
- 行业帽见 §2；余额 510300；硬排除惯例名（600519/002371 等）从族惯例；只在 gate=1 的票中按 α 构造评价权重  
- **α 定义 ≠ Top-N 闸**

---

## 5. 密封窗 / X2 / 自检口径（团队惯例；本文件不跑）

| 项 | 口径 |
|---|---|
| 密封窗 | **2018-01-02 → 2024-05-31**（HI_LIQ 满窗；FULLA 重叠段） |
| X2 | **2024-06-03 →**（结束日在独立 `.ok` / 正式 FROZEN 窗硬钉字面日期，不在本 DRAFT 读「最新日」） |
| 密封读取规则 | **仅**在 X2 过全部硬闸后、另窗 Arch `.ok` 下读一次；两档相对 HI_LIQ wb 净超额同号且 >0，否则 WATCH 封顶 |
| 自检 | `research/leaf_selfcheck_v3.py`（族惯例；实现 sha 在独立 `.ok` 窗重钉） |
| AUM | 60万 / 100万 并报 |
| 本文件 | **不跑**实数据、不读生产收益、不申请自检 `.ok` |

覆盖闸（读收益前写死；阈值不因结果调；正式 FROZEN 可微调数字但须 bump）：

- FULLA（研究主报）：X2 median 日可算 α 名数 **≥500** 且 **≥80%** 交易日 ≥500  
- HI_LIQ（纸面候选）：密封与 X2 各自 median **≥200** 且 **≥80%** 日 ≥200  

---

## 6. 正交硬闸（读收益前写死）

共用：活跃集 Jaccard 均 ≪0.7 且 frac(Jaccard≥0.7)=0；≥0.7∧近等权 → 换皮硬拒；须报残差 ρ；伪耦合（ρ 高且叠加≈加权和）→ CMC 不得 PASS。

| 对照 | 硬规则 |
|---|---|
| moneyflow_resid / 个股 D2 moneyflow | **不得**进主信号；残差清单可披露对照；**禁** moneyflow×capacity_adv 80/20 叠仓续挖 |
| etf_core / resid_etf | 禁双计 / 持仓差换皮；Jaccard/ρ 硬闸 |
| idx_rebal_flow | 禁事件换皮；构造分家 |
| capacity_adv | 残差步强制（披露）；ρ 与 Jaccard 按共用闸 |
| 叶4 / 8a 行业 ETF 流 | 本叶=宽基产品层；禁行业流主轴 |
| 叶25 cfacc_desens | 会计慢 vs 本叶产品层流；**禁复用**叶25 `.ok`；窗冲突让路叶25 |
| 叶27 on_minus_id ivol | 价量快拆分 vs 本叶份额流；禁混主信号；Jaccard/ρ 硬闸 |
| 扩池 512100/000852 | 主规格禁；另签+bump |

---

## 7. 验收门（研究级叙述；本文件不跑）

- **A / A′**：流量暴露残差 α 的 IC/ICIR + 特质 α  
- **B**：中性后相对 capacity_adv（含 cap80 等族对照）  
- **C**：与 moneyflow 慢袖 / etf_core 错配检查必做  
- **CMC / GATE_V3**：过门后才可议 Book-Smoke；衰减 KEEP；换手≤20%/日；两档 MDD≤25% 且净 CAGR>capacity_adv（族惯例；正式 FROZEN 可钉细项）  
- **门B 并报**：Calmar 两档胜主干且 MDD≤15%（族惯例）

研究级至少 A+A′；进 GATE_V3 / 派 Eng 须 A+A′+B+C。  
本文件 **不**申请 `.ok`、**不**跑自检、**不**读生产收益。

---

## 8. 与 Arch GAP 对齐摘要（首页可摘）

摘 Arch 预告 `5c44944c…` §1 / §1.1 + Data `aaf84d66…` §6：

1. **GAP×4（契约表）**：index_weight PIT；hk_hold 密窗；premium PIT；美 ETF PIT。  
2. **PARTIAL×3**：000852（主规格剔除）；映射无钉表（两对硬编码可绕）；hsgt_top10 catalog 漂移。  
3. **主规格研究级可推进**：份额流 OK + 权重 asof 披露 `pit_basis` + 硬编码两对；**不**授权跑 / 不授权 IMPL / 不授权 `.ok`。  
4. **正式 PIT / 扩池映射另裁**：本 DRAFT ≠ Arch 接受 `pit_basis` 的终裁；正式 FROZEN 前须 Arch 明示接受披露或落 `available_at`。  
5. **禁消费**补跑 `.ok` `9e4359f9`；禁复用叶25/叶27 `.ok` 钉签本叶。

---

## 9. 交闸时点与非动作

| 里程碑 | 条件 |
|---|---|
| 本 r1 **DRAFT** | 本文件落盘（未冻结） |
| 正式 **FROZEN** | **另候主令**；须再度 MATCH 现盘 Data/Arch sha；写死 α 符号；首页重钉 `pit_basis` |
| 申请本叶独立 `.ok` | Arch 审脚本 + Data 确认份额流/权重/`pit_basis`（或落列）之后；**另窗**；不复用叶25/叶27 钉 |
| 叶25 窗 | **10:00–10:45 ET 优先**；冲突时本叶排队 |
| 叶27 | ≥10:50 ET 另窗签路径 sha；与本叶正交 |
| X2 / Alpha 闸 | 独立回执后；WATCH/FAIL 不交 ACCEPT |

**非动作**：不申 `.ok`；不改脚本 / 不交 DIFF/IMPL；不跑实数据；不读生产收益选参；不改 `alpha_labels`；不派 Eng/Book-Smoke；不碰纸面；不 git commit；不拉外网/中转；不消费 `9e4359f9`；**不挡叶25**。

**优先级（主裁）**：叶25@10:00 > 叶27 路径清单/10:50 `.ok` > 本起草。

---

## 10. 失败条件（摘要）

覆盖闸失败；同构硬拒（§6）；ρ_excess>0.5 对兄弟主叶；不可交易；衰减非 KEEP；Gate A/B/GATE_V3 不过；跑不赢主干；who_pays 退化为 moneyflow/etf_core；未披露 `pit_basis` 却声称严格 PIT；默认池 silent 扩至 512100/000852；正式冻结后翻号 → WATCH/DONE_FAIL，不派 Book-Smoke。

---

## 11. DRAFT 钉（未冻结）

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_PREREG_DRAFT_r1.md` |
| 状态 | **DRAFT（未冻结；正式 FROZEN 另候主令）** |
| 起草时刻 | 2026-10-25 07:09:00 ET America/New_York |
| mechanism_tag | `g1g5_ashare_broad_etf_flow_stock_v1` |
| 主规格池 | 仅 510300→000300、510500→000905；剔 512100/000852 |
| `pit_basis`（权重） | `month_end_snapshot_no_available_at` |
| 宇宙 | FULLA 研究主报 + HI_LIQ 纸面候选；α 向量非 Top-N |
| 方向 | **未冻结**（FROZEN 另候主令） |
| MATCH r2 | `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` |
| MATCH Data | `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` |
| MATCH Arch | `5c44944c2a496a5cc461459d9b9f232116bfa152a41f1b26f8e21427a9a42f36` |
| live | false |
| promotion_approved | false |

**sha256**（整文件）：以本文件落盘后 `sha256sum` 为准。
