# 【DRAFT — NOT FROZEN】叶39 who_pays：异常经营现金流 ABCFO / 真实盈余管理残差 α

- 角色：QuantLab AI（执行器）
- 时点：2026-10-27 23:42 ET（America/New_York）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量覆盖/计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选系数/窗；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑；**禁**自升 FROZEN。
- 叶号意向：**叶39**（叶37 IMAX HOLD CLOSED；叶38 非标审计 exclusion overlay 旁线 `c01c2034` **不混**；叶30–37 **不复开**）。
- dig：盘上 sha8 **`440410de`**（`output/d1/DIG_FACTOR_20261027_2330ET.md`；文内自称 `87f65bbe` **勿采**）。
- 网研：`docs/v2/WEB_RESEARCH_15PCT_PATHS_ZH.md` **第二十四轮**（盘上 WEB sha8 以 `sha256sum` 为准；旁证 BigQuant https://bigquant.com/wiki/doc/fbp6xs9sH3 ：中证800 季度 ABCFO_Q1 多空年化约 14.63%、夏普 1.67）。
- 旁线红线：**禁**碰 fund MDD Eng BS（`.ok` `335635dd` / FROZEN `d489c937` / RESTORED 禁 `f08ce32c`）；**禁**混叶38（`c01c2034` 等）。
- 禁：GP / 高杠杆 / 教科书水平应计主线（水平应计已有叶34 exclusion HOLD）；卖方/金股/TP/LLM 权重；把叶19/25/30 α 当本叶主输入；禁自签 `.ok`；禁自派 X2/Book-Smoke。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（COVER·交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_abcfo_rem_resid_v1`（叶39 意向）  
> **who_pays（一句）**：付钱的是对真实活动盈余管理（异常低经营现金流 / 异常 CFO）反应慢、仍按报表利润给足权重的持有人——质量残差叶，**不是**教科书水平应计主线。  
> **可检验预测**：交付形态 = **截面质量残差 α 向量**（SW L1 + size/style 残差后；**非** Top-N；**非** exclusion mask 主交付；可另钉 soft 负向但不升 PRIMARY）。方向冻结意向：`α ∝ −ABCFO_resid` 的多头=异常 CFO 更高（REM 嫌疑更低）。硬闸：vs 叶19 `cfacc_rnoa` / 叶25 应计 / 叶30 CRR —— **Jaccard 或 ρ_excess 任一 >0.5 → 拒**（ρ_excess 正式在 X2；本拍计数用 rank Spearman 代理并披露）。池：**HI_LIQ 主**；**银行/房地产/非银金融（综金）硬掩码**。本拍轻量计数：**gate_pass=`true`**（masked median≈2838.5；zero_frac=0.0；J20 max vs19/25/30≈0.0256/0.0/0.0；ρ max≈-0.2420/-0.1081/-0.1451；peak_rss≈704.9MB）。  
> **失效条件**：退化为叶19/25 完整应计多空或叶34 `1−ocf_to_profit` 水平应计剔除；或 vs 叶19/25/30 Jaccard/ρ_excess >0.5；或未排除银/地/非银；或偷看 `available_at > t`；或主信号混入 GP/卖方/金股/LLM；或冻结后事后改公式读收益；或把 CRR_MOD2/IO 拥挤度升 PRIMARY。  
> **交 Alpha 时点**：主排号确认→Arch 审 DRAFT→主令升 FROZEN→独立 `.ok` + X2 之后；现在只交 DRAFT + 轻量计数闸。

---

## 1. 选型理由（PRIMARY = ABCFO 真实盈余管理残差 α）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| 叶19 `cfacc_rnoa` | 同期 CFACC + ΔRNOA **完整 α** | 本叶=**异常 OCF 残差**（Roychowdhury/东北证券 ABCFO）；非同期应计水平+ΔRNOA；硬闸 Jaccard/ρ>0.5 拒 |
| 叶25 应计脱敏 | CFACC 脱敏截面全因子 | 同族禁复开；本叶**不**重建 leaf25 α |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF **转化率** + 残差波动惩罚 | 本叶=单期（季）**期望 OCF 模型残差**，非多季转化率；硬闸同左；备选 CRR_MOD2 **不升 PRIMARY** |
| 叶34 高应计 exclusion | `1−ocf_to_profit` **水平**剔除 overlay | 本叶交付=**残差 α 向量**，≠ exclusion；另披露 vs 叶34 活跃剔除集（本叶≠overlay） |
| 叶38 非标审计 exclusion | 审计意见非标 mask | 源/机制全异；旁线不混 |
| accrual_quality | BS WC 应计 TopN | 现金流量表期望模型残差，非 BS 应计 TopN |

**PRIMARY 选定**：`g1g5_ashare_abcfo_rem_resid_v1`（异常经营现金流 / 真实盈余管理残差）。  
**备选（§内写清，不升 PRIMARY）**：CRR_MOD2（叶30 增强；须 vs 叶30 硬闸）；IO 客户动量/拥挤度仍 **数据闸**。

---

## 2. 机制与公式纪律（查证后写死；不读收益选系数）

### 2.1 学术/卖方口径（查证摘要）

- Roychowdhury (2006) / 国内复述（国泰君安等）：分行业截面  
  \(\mathrm{CFO}_t / A_{t-1} = \beta_0 + \beta_1 (1/A_{t-1}) + \beta_2 (S_t/A_{t-1}) + \beta_3 (\Delta S_t/A_{t-1}) + \varepsilon_t\)  
  **ABCFO** \(=\varepsilon\)（实际−期望）。异常**低** OCF → 销售操控等真实盈余管理嫌疑。
- 东北证券《基于异常现金流模型的真实盈余管理因子》（2022-11-04；BigQuant 摘要）：年度 ABCFO_Y1/Y2/Y3、季度 ABCFO_Q1/Q2/Q3；公开摘要未展开全部三模型差异；**本叶 DRAFT 默认钉 Q1=上式 Roychowdhury CFO 模型**（与旁证「ABCFO_Q1」对齐）。完整 PDF 本拍 404，**未**臆造 Y2/Y3 系数。

### 2.2 盘上可复现规格（PRIMARY）

| 项 | 钉死 |
|---|---|
| OCF | `cashflow_pit_tushare.n_cashflow_act` |
| 收入 S | `financials_pit_tushare.total_revenue`（缺则 `revenue`） |
| 资产 A | `bs_cf_pit_tushare.total_assets`（或 balancesheet 同字段）；规模用 **上期** \(A_{t-1}\) |
| 累计→单季 | 财报盘面为 **YTD 累计** → 年内差分得单季 OCF/S；Q1 不做差 |
| ΔS | 单季销售额差分 |
| 期望回归 | 再平衡截面 **按 SW L1** OLS（名过少 <25 → 全市场 fallback）；正式 X2 可升「年×行业」历史窗（须重钉） |
| ABCFO | 回归残差 \(\varepsilon\) |
| 原始信号 | `raw = -ABCFO`（多头=异常 CFO 更高） |
| 残差 α | 掩码后：SW L1 demean + vs log 流通市值 OLS（+ 既有 style 若易得）；输出日度 α 向量 |
| PIT | `available_at ≤ t`（Asia/Shanghai 墙钟；交易日对齐）；禁偷看 |
| 可选 soft 负向 | 可钉 top 异常低 ABCFO 尾部 soft-penalty，**不**替代 PRIMARY 残差 α |

### 2.3 DATA_GAP / APPROX（诚实）

1. **期望回归窗**：东北证券或用年×行业历史样本；本拍计数=**再平衡日截面 SW L1 OLS** → 标 **APPROX**；冻结时可升完整面板，须重跑计数。  
2. **Δ应收/存货/PPE**：balancesheet 有 `accounts_receiv` / `inventories` / `fix_assets` —— **非** ABCFO_Q1 主公式必需；若后续做异常生产成本/酌量费用合成 REM，另开备选叶，**不**夹带本 PRIMARY。  
3. **无独立 income_pit**：收入取 financials_pit，可复现。  
4. **禁**把 `ocf_to_profit_pit_daily` 的 `1−ocf_to_profit` 当本叶主公式（那是叶34）。  
5. 本拍 **ρ_excess 正式未算**（未读收益）；计数披露的是 vs 叶19/25/30 α 的 **rank Spearman** 与 Top-20 Jaccard 代理 → X2 阶段换正式 ρ_excess。

---

## 3. 失败条件（读收益前写死）

1. vs 叶19 / 叶25 / 叶30：**Jaccard 或 ρ_excess 任一 >0.5** → **同构硬拒**（本拍计数阈值同；ρ 现为 Spearman 代理）。  
2. 覆盖：HI_LIQ 再平衡日掩码后可算名 **median <300** 或 zero_frac >0.05 → 不过。  
3. 未排除银行/房地产/非银金融 → 不过。  
4. 退化为水平应计 / 叶34 overlay / Top-N 长端复开 → 不过。  
5. peak RSS 正式跑 >1.5GB → 不过；本拍计数 peak≈704.9MB。  
6. 衰减门非 KEEP / 不可交易 / Gate A·B / GATE_V3 FAIL → 不过（X2）。  
7. 偷看未来 `available_at` 或冻结后改公式读收益 → 作废。

---

## 4. 数据 / 宇宙 / 窗

| 项 | 值 |
|---|---|
| 宇宙 | **HI_LIQ**（`universe_mask_hiliq_v1.parquet`；sha8 `c5433e80`） |
| 行业掩码 | 银行 `801780.SI` / 房地产 `801180.SI` / 非银金融 `801790.SI`（综金按非银）；`综合`≠综金 |
| X2 样内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | DRAFT **20** 交易日 |
| 输入 sha8（计数拍） | cf=`71d5c3d3`；fin=`bc0f4c3d`；bs_cf=`01a015bf`；sw=`89d4afa3`；叶19α=`16202b2e`；叶25α=`8be12024`；叶30α=`c8c7a5a5` |

---

## 5. 本拍计数结论（摘要）

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| gate_cov_pass | `true`（masked median=2838.5；zero_frac=0.0） |
| hard_reject_overlap | `false`（hits=[]） |
| peak_rss_mb | 704.9 |
| APPROX | 是（截面 SW OLS；Spearman≠正式 ρ_excess） |
| 未算 | 收益/IC/CAGR/PnL；未申 `.ok`；未开 X2；未升 FROZEN |

详 COUNT JSON / RECEIPT。

---

## 6. 禁项与下一跳

- 禁自签 `.ok`；禁自派 X2；禁 Book-Smoke；禁碰 fund MDD / 叶38；禁 GP/高杠杆；禁复开叶30–37。  
- 下一跳：**交主 → Arch 只审本 DRAFT**（通过后再由主令升 FROZEN）。本执行器**不自升** FROZEN、**不**申 `.ok`。
