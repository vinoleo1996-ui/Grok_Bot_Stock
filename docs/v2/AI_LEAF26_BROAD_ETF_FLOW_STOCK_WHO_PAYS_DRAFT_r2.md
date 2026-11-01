# 【DRAFT r2 — NOT FROZEN】叶26 who_pays：ETF 资金流（宽基→成分暴露）

- 角色：QuantLab AI
- 时点：2026-10-25 约 04:53 ET（`date`）
- **权威草稿链**：r1（盘面）sha256 `34c1540f50452b7fbc60dcbf2c7cdfeb0820b09ddf5a8b1342833ca200f88926` → **本 r2 取代其主规格口径**（r1 文件保留不覆写）
- 对齐：
  - Alpha：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md` sha256 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605`（叶候选 1 ETF 资金流空位）
  - Data 缺数盘点：`docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md` sha256 `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305`
  - Strategy 袖套：`docs/v2/STRATEGY_ETF_FLOW_SLEEVE_PLAN_20261025_ZH.md` sha256 `7722efec9f750ec89b2047d5890a39a119771eb86c8fb35bc265217b82286091`（路径1 池**默认不含 512100/中证1000**）
- 禁：卖方/金股/一致预期；禁 GP；**禁个股 moneyflow 主轴**；禁 etf_core 双计；禁无 PIT 静默当严格 PIT。
- live=false；promotion_approved=false。叶25 10:00 窗优先，本文件不申请 `.ok`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_broad_etf_flow_stock_v1`（叶26）  
> **who_pays（一句）**：付钱的是在宽基 ETF 大额申赎日、忽视「ETF 产品层份额流→篮子权重」传导而承接 AP 机械买卖冲击的个股定价对手——**不是**个股 `net_mf_amount` / moneyflow_resid 对手盘，也不是直接持有 ETF-core 的配置差对手盘。  
> **主规格 ETF 池（r2）**：默认仅 `510300.SH→000300.SH` 与 `510500.SH→000905.SH`；**默认不含** `512100.SH` / `000852.SH`（与 Strategy 袖套默认池对齐）。000852 权重虽在合并表至 20260930，接线须另与 Strategy/Data 共签后再开敏感性支路。  
> **可检验预测**：经残差化后的 ETF 流量暴露 α，对次日特质收益的截面 IC 符号在预注册冻结时写死（本 DRAFT 不读收益选号）；活跃集 vs moneyflow_resid / etf_core / resid_etf / idx_rebal_flow / capacity_adv 的 Jaccard ≪0.7 且 frac(J≥0.7)=0。  
> **失效条件**：主信号混入个股 D2 moneyflow；或退化成持有 ETF≈0.70；或与 moneyflow_resid 近等权（Jaccard≥0.7）；或无 PIT/未披露 `pit_basis`；或默认池擅自纳入 512100 而未与 Strategy 对齐。  
> **交 Alpha 时点**：正式预注册冻结 + Arch 审脚本 + 本叶新窗 `.ok` + X2 回执之后；现在只交 DRAFT。

---

## 1. 机制（不变，收紧池）

宽基 ETF **产品层**份额净申购/净赎回 → 经指数权重映射为个股截面 α。  
**不是**行业 ETF 流（叶4/8a）；不是 etf_core 持仓；不是 idx_rebal 事件；不是个股 moneyflow_resid；不是叶25 应计。

残差：SW L1 + log(流通市值) +（披露）vs capacity_adv / moneyflow_resid；主交付 **α 向量**。

---

## 2. Data 缺数回执落点（预注册必须披露）

| # | 缺口 | Data 结论（c03a9f0e…） | 预注册默认处置 |
|---|---|---|---|
| 1 | `index_weight_*` 无 `available_at` | 合并表有 `trade_date/weight`，无 PIT 列；研究惯例 `trade_date≤session` 最近月末 | 冻结前披露 `pit_basis=month_end_snapshot_no_available_at`；**不得**静默称严格 PIT；正式 `available_at` 规则待 Arch+Data 契约 |
| 2 | 中证1000 / 000852 | 合并表内 **有** 000852 至 20260930；202610 空片 | **主规格仍剔除 512100/000852**（Strategy 默认）；敏感性支路另签 |
| 3 | ETF↔指数映射 | 无 Arch 钉表；仅有 fund_basic benchmark 旁证；联接去重无契约 | 主规格硬编码两对映射（510300↔000300、510500↔000905）；扩池/联接须 Arch 映射表 |

短期研究绕行允许，但须在预注册与 X2 回执首页披露 `pit_basis`。

---

## 3. Strategy 接线

- Strategy 路径1 默认池 **禁 512100** → 叶26 主规格同步，避免因子叶与袖套池不一致。  
- 若未来要纳入 000852/512100：须 Strategy 书面改默认池 + Data 映射/PIT 共签 + 预注册 bump（新文件名），不得 silent。

---

## 4. 草稿钉说明（给 Data）

| 项 | sha256 |
|---|---|
| 已作废任务钉（勿再用） | `5fd1a4a78c4024013baecc1abcd23f8c5dda111fa00e5a54766d930e87c1f3bc` |
| r1 盘面（Alpha 空位填写版） | `34c1540f50452b7fbc60dcbf2c7cdfeb0820b09ddf5a8b1342833ca200f88926` |
| **本 r2（现行主规格口径）** | （本文件写出后打印） |

路径：`docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md`

---

## 5. 交 Alpha / 时点

| 里程碑 | 时点 |
|---|---|
| 本 r2 交主/Data/Strategy/Alpha | 已完成（本文件） |
| 预注册 r1 | Arch 权重 PIT 规则或明示接受 `pit_basis` 披露 + 映射钉后 +1 工作窗 |
| X2 / 交 Alpha 闸 | 本叶独立 `.ok` 窗；**不**复用叶25；与叶25 冲突让路 |

live=false。
