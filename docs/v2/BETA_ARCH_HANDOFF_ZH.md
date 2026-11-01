# Beta 架构交接：风险预算、容量与 Alpha 接口

研究级，**promotion_approved=false**（未经 Leo 明示不得晋级）。  
日期：2026-10-11 23:30 ET。依据：`QuantLab-AI_FACTOR_MINING_PLAN_ZH.md`、`docs/v2/QuantLab-MANDATE_V2*.md/json`、V3 各预注册（B1/B2/CB/MA/FUT-RP/CIB 等）。

---

## 0. 一句话

**Alpha 挖边，Beta 管风险与容量。**  
主 alpha 路径是 AI 因子挖掘（中大盘、日/周频、严格 PIT/多重检验）。Beta 线只提供：结构 β / carry 袖套、风险预算、成交容量闸门、以及把 Alpha 分数装进 Strategy 多袖套账本的接口。**禁止**用公开 ETF 轮动叠 CAGR，**禁止**小盘主线，默认 **L≤1.5**，高杠杆凑数一律否决。

---

## 1. 袖套角色

| 角色 | 谁负责 | 例子 | 钱从哪里来 |
|---|---|---|---|
| **结构 β / carry** | Beta | 510300 敞口、IC 贴水半仓、国债/黄金压舱、全规则 CB 双低/低溢价 | 股权溢价、对冲需求贴水、期限溢价、转债凸性 |
| **Alpha overlay** | Alpha → Beta 接入 | AI/GP/LGBM 中大盘分数 → 超配/低配 | 截面预测边（扣成本后） |
| **风险预算层** | Beta | 波动目标、β 锚、行业/单票上限、回撤刹车 | 不创造收益；约束组合形状 |
| **现金 / 融资** | Beta + Eng | 511880 计息；MarginConfig 仅在预注册且 L≤1.5 | 货币利率；融资利差是成本 |

既有试探（B1、B2/B2LL、MA-RP、FUT-RP L3、CIB-*）一律 **research-only**；通过探索 + 前向模拟盘后，才以 `promotion_approved` 闸门进入实盘候选。

---

## 2. 风险预算（Beta 硬约束）

对齐 Mandate V2 默认，Beta 组合层再收一层：

| 维度 | 默认 | 说明 |
|---|---|---|
| 年化波动 | 目标 ≤16%（Mandate）；结构试探可声明 8–14% | 用 60 日实现波动估计；超标降杠杆或加压舱 |
| 组合 β | 锚 ~0.70 vs 沪深300（Mandate） | 结构 β 袖套可偏离，须在预注册写明 |
| 行业 | 申万一级单行业 ≤25% | Alpha overlay 计入同一上限 |
| 单票 | ≤5%；持股数约 30–60（股票账本） | CB 袖套按转债只数规则，不与股票混用同一 5% |
| 回撤 | 组合 −18%→权益敞口≤0.5；−22%→≤0.3（V3 刹车，优先于加仓） | Mandate 门禁 −28% 可恢复缩放 |
| 杠杆 | **默认 L≤1.5**（名义/NAV）；FUT-RP 等特例须 Leo 点名 | 拒「软禁止亏损高杠杆」违规 |
| 换手 | 月单边 ≤35%（Mandate） | Alpha 适应度函数须含换手惩罚 |

风险预算输出物：每日/调仓日的 `risk_budget.parquet`（见 §6）。

---

## 3. 容量（Capacity）

| 规则 | 默认 |
|---|---|
| 宇宙 | 流通市值前 1500 **或** 沪深300/中证500 历史成分（PIT）；**禁小盘主线** |
| 流动性 | 近 20 日 ADV；参与率硬顶（建议单票单日 ≤5–10% ADV，预注册写死） |
| ETF/期货 | ETF 用份额与成交额；期货用持仓限额与滚动流动性（季月） |
| 冲击 | 引擎 `impact_k` + Mandate 成本（佣金/滑点/印花税历史） |
| 容量报告 | 每个晋级候选必须有：在目标 AUM 下的参与率分布、换手、成本占比 |

容量与 Alpha 联动：Alpha 分数只在 `universe_mask=1` 且 ADV 达标的票上生效；否则权重归 0，余额进压舱/现金。

---

## 4. Beta **不做**的事

1. **不再堆公开 ETF 行业/宽基轮动凑 CAGR**（E1/E2 已试且探索失败；与 AI 挖因子主路径冲突）。
2. **不做小盘主线**（对照臂须标注，不得进主账本）。
3. **不做高杠杆凑 12%**（L>1.5 须 Leo 书面例外；FUT-RP L3 是已批准的前向对照上限，不是开放加杠杆许可证）。
4. **不代替 Alpha 挖边**：结构 carry（贴水、双低）可保留为低相关袖套，但主超额期望在 AI 因子。
5. **不把密封窗当调参器**：部分见过的窗只描述/弱确认。

---

## 5. 与 Alpha 的交接接口

### 5.1 Alpha → Beta（只读契约）

路径建议（落地时可微调，字段稳定）：

```
output/alpha/handoff/<factor_id>/
  scores_pit.parquet      # 必需
  meta.json               # 必需
  universe_mask.parquet   # 必需（可与 scores 同表）
  ic_stats.json           # 必需：探索窗 IC/ICIR/换手/尝试次数 N
  prereg_path.txt         # 指向 docs/prereg/...
```

**`scores_pit.parquet` 字段：**

| 字段 | 类型 | 含义 |
|---|---|---|
| `trade_date` | date | 信号日（收盘后可知） |
| `code` | str | `sh.600000` / `sz.000001` |
| `score` | float | 截面分数（已按 Alpha 预注册中性化与否处理） |
| `available_at` | datetime | PIT 可用时间；Beta 只用 `available_at ≤ T 15:00` |
| `universe_ok` | bool | 中大盘 ∩ 非ST ∩ 上市≥120 日 ∩ ADV 闸门 |
| `adv_20` | float | 20 日成交额（元），供参与率 |
| `industry_sw1` | str | 申万一级，供行业预算 |

**`meta.json`：** `factor_id`, `family`, `horizon_days`, `long_only`, `cost_assumption_bp`, `n_trials_explore`, `sealed_status`, `promotion_approved`（必须为 false 除非 Leo 翻转）。

**`ic_stats.json`：** 探索窗 IC 均值、ICIR、扣成本多头超额、换手、相对 510300；密封若已跑则单独键且标 `descriptive|weak|official`。

### 5.2 Beta → Strategy 账本

- 权重日程：`output/v3/handoff_strategy/<sleeve_id>/targets_{window}.csv`  
  字段：`date, instrument, target_weight`（期货为名义/NAV；现货为资金权重）。
- 风险附注：`README.md`（展期、保证金源、L 上限、现金、窗口）。
- Strategy 多袖套：`quantlab/portfolio/v2_multisleeve_book.py` 只消费已交接、且探索通过的袖套；**双引擎对账仅探索窗**。

### 5.3 Beta 合成伪代码

```
w_alpha = map_scores_to_weights(scores, mask, cap_single=0.05, cap_ind=0.25, particip_adv=0.08)
w_struct = structural_sleeves(...)          # CB/IC05/ballast/β 等，gross 受 L≤1.5
w = risk_budget_merge(w_alpha, w_struct, vol_target, beta_anchor, dd_brake)
w = capacity_scale(w, adv, aum)
assert sum(abs(w)) <= L_max  # default 1.5
```

---

## 6. 文件级接口草图（汇总）

| 文件 | 方向 | 用途 |
|---|---|---|
| `output/alpha/handoff/<id>/scores_pit.parquet` | A→B | 因子分数 PIT |
| `output/alpha/handoff/<id>/ic_stats.json` | A→B | IC/ICIR/闸门摘要 |
| `output/beta/risk_budget/daily.parquet` | B 内部 | date, vol_exante, beta_exante, gross, dd, brake_level |
| `output/beta/capacity/participation.parquet` | B 内部 | date, code, weight, adv_20, particip |
| `output/v3/handoff_strategy/<sleeve>/` | B→S | 权重日程 + README |
| `docs/trial_ledger.csv` | 全体 | 臂级诚实记账 |
| `docs/v2/*_PREREG.md` | 全体 | 跑前冻结 |

---

## 7. 与当前 Beta 试探的关系

| 状态 | 臂 | 含义 |
|---|---|---|
| 前向对照 | FUT-RP L3 | Leo 指定 L_max=3 仅该臂；非默认 |
| 结构零件 | B2LL-IC05、全规则 CB1/CB2、MA-RP、压舱 | 可组合，但不得无假设重洗失败件 |
| 已否决路径 | 公开行业 ETF 轮动主线（**E1/E0 parked**，见 §10.2 / `ETF_ROTATION_PREREG.md`）、小盘主线、无风险预算的高杠杆 RP、教科书动量主线 | 不再叠 CAGR；Leo §10 |
| 等待 Alpha | 中大盘容量感知 β 袖套骨架 | 分数未到则只建接口与宇宙/ADV 掩码，不假装有边 |

---

## 8. 晋级闸门（重申）

1. 预注册 → 探索通过（含成本、容量）→ 密封规则按该臂文档（多见过则弱确认）→ 2026-11 起前向模拟盘 ≥6 个月。  
2. **`promotion_approved=false` 直到 Leo 明示。**  
3. 主期望超额来自 Alpha AI 因子；Beta 负责别爆回撤、别超容量、别用错杠杆。

## 9. 2026-10-11 23:35 ET 更新
- 架构文：本文件。
- 下一结构臂 **CIB2-EW 探索通过**（全规则 CB2+IC05+压舱等权）；见 docs/v2/V3_CIB2_PREREG.md 与 output/v3/handoff_strategy/cib2/。

---

## 10. Leo 规则：拒绝传统因子踩踏（2026-10-11 23:40 ET）

**来源**：Leo 经 New Bot 传达（同步至本文件）。研究级，`promotion_approved=false`。

### 10.1 硬规则

1. **Beta 同样拒绝传统因子踩踏。** 不得以教科书动量、行业/风格轮动、公开可复制的截面因子堆叠作为主线去凑 CAGR。
2. **结构性收益来源可以。** 贴水/展期 carry、转债条款与定价错配、期限溢价、对冲需求补偿、明确声明的压舱等，只要收益机制可写清、可证伪，允许作为结构袖套。
3. **教科书动量/轮动不得当主线。** 对照臂可以保留，但不得进主账本、不得再叠 CAGR。
4. **新臂开跑前必须写清独特收益来源。** 预注册 §「钱从哪里来 / 独特收益来源」为空或只能写「动量惯性 / 轮动」→ **禁止开跑**。

### 10.2 与 E1/E0 的交叉引用（已停放）

| 臂 | 文档 | 状态 | 停放原因 |
|---|---|---|---|
| **E1 行业动量** | `docs/v2/ETF_ROTATION_PREREG.md` §1/§11/§14；映射 `data/v2/etf/sw_l1_etf_map_pit*.parquet` | **parked** | 教科书行业动量主线；X2 探索未过（0.90%/−32.1%），且违反本条 Leo 规则，不再作为主线推进 |
| **E0 行业等权** | 同上 | **parked**（对照） | 无独特超额来源，仅 β+行业分散；密封窗覆盖不足未跑；不作主线 |

本条强化 §4.1「不再堆公开 ETF 行业/宽基轮动凑 CAGR」与 §7「已否决路径」。后续若只作风险预算对照，须在预注册标明 `role=control`，且不得晋升。

### 10.3 CIB2-EW 是否满足本规则（文档核对，无回测）

臂：`CIB2-EW`（全规则 CB2 + IC≤0.5 + 国债/黄金压舱，三袖套等权）。预注册：`docs/v2/V3_CIB2_PREREG.md`（承 `V3_CB_IC05_BALLAST_PREREG.md`、`CB_PREREG.md`）。

| 袖套 | 文档写明的独特收益来源 | 是否教科书动量/轮动 |
|---|---|---|
| **CB2 低溢价** | 转换期权/股性暴露 + 转债相对正股的低估/折价回归（`CB_PREREG` CB2：正股 β + 凸性；低溢价挑选） | 否 |
| **IC 半仓贴水** | 对冲需求贴水/展期 carry（`V3_CB_IC05_BALLAST` / B2LL：hedging-demand discount） | 否 |
| **压舱 511010/518880** | 国债期限溢价 + 黄金低相关压舱（吸收权益/转债回撤，非收益主引擎） | 否 |

**结论：满足。** CIB2-EW 的三条收益来源均为结构性机制，预注册已写清且非动量/轮动主线；可继续作为结构臂交接 Strategy 对账，仍受 `promotion_approved=false` 约束。E1/E0 因本规则停放，与 CIB2-EW 路径分离。

