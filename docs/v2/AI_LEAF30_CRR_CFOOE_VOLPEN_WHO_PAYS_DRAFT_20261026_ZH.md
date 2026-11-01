# 【DRAFT — NOT FROZEN】叶30 who_pays：CRR 增强（现金流实现率 + CFOOE 残差波动惩罚）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-26 约 17:32 ET（America/New_York；箱 `date`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays 草稿 + HI_LIQ 轻量计数闸；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**不**动 A18（`.ok` sha8 `6de02e74`；Eng ≥17:45）。
- 对齐网研：`docs/v2/WEB_RESEARCH_15PCT_PATHS_ZH.md` §第十七轮 CRR；叶19 `docs/v2/AI_G1G5_CFACC_RNOA_WHO_PAYS_PREREG_ZH.md`（FROZEN）；叶25 r6 `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` + alpha `output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet`（期望 sha8 `8be12024`）。
- 叶号：**叶30**（叶28/29 仍 FROZEN；叶25/27 已收口；叶26 GAP **不交审**）。
- 禁：GP / 高杠杆 / 教科书主线当主轴；卖方/金股/一致预期；复跑叶25 alpha；改 build；申 `.ok`；挂/抬 QUIET；抬 RSS。
- `live=false`；`promotion_approved=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_crr_cfooe_volpen_v1`（叶30）  
> **who_pays（一句）**：付钱的是按同期报表利润/EPS 定价、忽视「过去约 16 个季报窗口内营业利润→经营现金流转化效率（CRR）及其跨期稳定性（CFOOE 对截面回归残差的滚动波动）」的交易者；高 CRR 且转化稳定者被低估持续性。  
> **可检验预测**：残差化后的 `α_raw = rank(CRR) − λ·rank(vol_pen)`（λ 冻结时写死；DRAFT 建议 1.0）对次期特质收益的截面 IC 符号在预注册**冻结时**写死（本 DRAFT **不**读收益选 λ）；活跃集 vs 叶19 `cfacc_rnoa` / 叶25 / 库内 `accrual_quality` 的 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**（披露，不单独当 ACCEPT）；覆盖 HI_LIQ 再平衡日可算 α 名数 median≥300。  
> **失效条件**：与叶19 同期 CFACC+ΔRNOA 近等权（Jaccard≥0.7）；或退化为单季/TTM OCF÷利润且无时序窗与无波动惩罚；或未排除银行/房地产/非银金融；或冻结后事后翻转方向/改 λ；或主信号混入卖方/金股/一致预期/GP。  
> **交 Alpha 时点**：正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 计数闸。

---

## 1. 机制（会计慢叶；时序转化，非同期应计）

**CRR（现金流实现率）**：在 PIT 可用的连续季报上，取过去 L≈16 个单季（至少 12 个有效季才算）：

\[
\mathrm{CRR}_{raw} = \frac{\sum_{q\in L}\mathrm{OCF}_q}{\sum_{q\in L}\mathrm{OP}_q}
\]

- 分母 ≤0、有效季 <12、或关键字段缺 → 该票该再平衡日**无效**（记覆盖缺口，勿静默填 0）。
- YTD→单季：对齐叶19 规则（连续季报差分；同一 `(ts_code,end_date)` 取**最早** `available_at`；次一交易日起可用）。
- OCF = `n_cashflow_act`；OP = `operate_profit`（营业利润）。若盘面仅有净利润代理，**计数阶段可 APPROX**，正文规格仍以营业利润为准（缺则 GAP，勿编造）。

**CFOOE / 残差波动惩罚**：

1. 取 CFOOE 截面版本：可用单期 `OCF/OP`，或与 CRR 同日的截面可算值（冻结时写死其一；DRAFT 默认用最近可用单季 `OCF_q/OP_q`，分母≤0 无效）。
2. 对全市场（或 HI_LIQ 池内）截面 OLS：**SW L1 dummy + log 流通市值（T−1）** → 残差 ε。
3. `vol_pen = rolling_std(ε)`：DRAFT 建议 **8 个季报点**（或等价约 20 个再平衡日的日频近似）；最少有效点冻结时写死（建议 ≥6 季）。
4. **本拍计数**可用季频/日频代理并醒目标 APPROX；**不算收益选窗长**。

**合成（DRAFT）**：

\[
\alpha_{raw} = \mathrm{rank}(\mathrm{CRR}) - \lambda\cdot\mathrm{rank}(\mathrm{vol\_pen}),\quad \lambda^{\mathrm{DRAFT}}=1.0
\]

池内百分位 rank；再按残差清单中性 → 日度 base-α 向量（**非 Top-N**）。

---

## 2. 相对叶19 / 叶25 的分家（禁止同构重开）

| 包 | 要点 | 叶30 必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` | 同期 CFACC=(NI−OCF)/资产 + ΔRNOA；α=rank(−CFACC)+rank(ΔRNOA) | **多季时序转化率 CRR** + **CFOOE 残差波动惩罚**；非同期应计水平+ΔRNOA |
| 叶25 `cfacc_desens` | 应计脱敏/质量应计全叶；同族 | 同族须硬闸；不得复用叶25 `.ok`/alpha 当本叶交付 |
| 库内 `accrual_quality` | BS WC 应计 | 现金流量表时序转化，非 BS 应计 |
| 教科书「经营现金流/净利润」单点 | 单期比率 | 必须 L≈16 季汇总 + vol_pen；单点仅可作计数 APPROX |

**一句话分家**：叶19=同期 CFACC+(Δ)RNOA；叶25=应计脱敏全叶；叶30=**多季营业利润→OCF 转化效率 + 残差波动惩罚**。

---

## 3. 残差化清单（同日截面；缺则记 GAP，不得静默跳过）

1. 原始：`CRR_raw`（及构建 `vol_pen` 的 ε 序列）。  
2. **行业硬掩码**（信号前排除，见 §5）。  
3. **SW L1 demean**（掩码后池内；名过少时仅 demean，回执披露）。  
4. vs **log 流通市值** OLS 残差（市值 T−1 PIT）。  
5. 可选再正交：mom20 / mom60 / vol20 / log ADV20（capacity_adv 代理）——与叶19 对齐与否在冻结时写死；DRAFT 建议至少 SW L1 + log 市值。  
6. 披露 vs 叶19 / 叶25 / `accrual_quality` 的 Jaccard 与 ρ_excess（家族多重检验 n 至少含这三项 + 本叶）。

---

## 4. 方向与 λ（不可事后切换）

| 项 | DRAFT 约定 |
|---|---|
| 主规格 | `α_raw = rank(CRR) − λ·rank(vol_pen)`，高 CRR、低 vol_pen 优先 |
| λ | DRAFT 建议 **1.0**；**冻结时写死**；本拍**不算收益选 λ** |
| 禁事后翻 | 冻结后不得因 X2/密封读数把主规格改为奖励高波动或改符号 |
| 本 DRAFT | 不读本叶生产收益；不声称方向/λ 已 FROZEN |

---

## 5. 行业掩码（硬排除）

申万一级（盘面 `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` 实际名称/代码）：

| sw_name | sw_code | 处理 |
|---|---|---|
| 银行 | `801780.SI` | **硬排除** |
| 房地产 | `801180.SI` | **硬排除** |
| 非银金融 | `801790.SI` | **硬排除**（「综金」按非银金融） |

注：`综合`=`801230.SI` **不**在本掩码内（≠综金）。PIT：`in_date`/`out_date`/`available_at` as-of 再平衡日。

---

## 6. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| 叶19 `cfacc_rnoa` | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **只算强度过滤**（披露） |
| 叶25 全因子/应计脱敏 | 同上 |
| `accrual_quality` | 同上；计入家族多重检验 n |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300**（对齐叶19） |
| 换手/成本 | 评价口径成本 **30bp**（DRAFT 披露；本拍不算 PnL）；>20%/日或成本>毛超额一半 → 不可交易（冻结后评价） |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

---

## 7. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙 | **HI_LIQ 主**（掩码 `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`，HI_LIQ_V1.1） |
| X2 样本内窗 | **2024-06-03 → 2026-10-09** |
| 再平衡 | DRAFT 建议每 **20** 交易日（与叶19 慢 α 对齐）；计数闸与此一致 |
| 成本口径 | **30bp**（本拍不算 PnL） |
| 主交付 | **日度 base-α 向量**（instrument→alpha）；非 Top-N 当闸 |
| live / promotion | `false` / `false` |

---

## 8. PIT 输入与缺数（只列契约；计数可 APPROX）

| # | 候选输入 | 备注 / 缺数 |
|---|---|---|
| 1 | `financials_pit_tushare`（`operate_profit` 等） | 完整 CRR 单季差分用；`operate_profit` 空率低但仍须 PIT 对齐 |
| 2 | `cashflow_pit_tushare`（`n_cashflow_act`） | 与利润 `(ts_code,end_date)` 最早 `available_at` |
| 3 | `ocf_to_profit_pit_daily_tushare.parquet` | **计数 APPROX 代理**（现盘 `period_basis≈YTD_cumulative`；分母偏净利润非营业利润）→ 回执须醒目 APPROX |
| 4 | SW L1 PIT（上表路径） | 银/地/非银硬排除 |
| 5 | HI_LIQ 掩码 | 上表路径 |
| 6 | log 流通市值 T−1 | 残差用；缺则记 GAP |
| 7 | 叶19 / 叶25 α parquet | 仅供 Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造** 16 季营业利润序列。

---

## 9. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 DRAFT + HI_LIQ 计数闸 | 本文件 + `research/leaf30_crr_hiliq_count_gate.py` + JSON + 短回执 |
| 预注册 FROZEN | 主排期；方向/λ/窗长写死；Arch 可审脚本 |
| 申请 `.ok` / X2 | **另窗**；禁复用叶25 `.ok`；避 A18 Eng 内存窗 |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |

---

## 10. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）  
- 复跑叶25 alpha；改 build；申 `.ok`；挂/抬 QUIET；抬 RSS；动 A18  
- GP / 高杠杆 / 教科书单点比率当主规格  
- 冻结前读本叶收益选 λ/方向  
- 未掩码银行/房地产/非银金融  
- 与叶19/25 Jaccard≥0.7 仍宣称新叶  
- 推 Leo（本拍无新 ACCEPT）  
- `live=true` 或 `promotion_approved=true`

---

## 11. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_DRAFT_20261026_ZH.md` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_crr_cfooe_volpen_v1` |
| live | false |
| promotion_approved | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
