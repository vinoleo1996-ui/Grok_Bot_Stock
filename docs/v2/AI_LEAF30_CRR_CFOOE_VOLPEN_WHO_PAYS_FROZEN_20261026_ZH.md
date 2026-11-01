# 【FROZEN 2026-10-26 17:37 ET】叶30 who_pays：CRR 增强（现金流实现率 + CFOOE 残差波动惩罚）

- 角色：QuantLab AI
- 冻结时点：**2026-10-26 17:37 ET**（America/New_York；箱墙钟 `2026-10-26 17:37:52 EDT`）
- 状态：**FROZEN**。冻结前**未**读任何本叶收益选 λ/方向。
- 主令：2026-10-26 ~17:37 ET FREEZE（who_pays DRAFT sha8 `e00ba1b7` / 计数回执 `24d1bcfd` / JSON `b0e7b1d0` / 脚本 `ad524f9e` MATCH；gate_pass=true APPROX 收下）。
- 基盘 DRAFT：`docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_DRAFT_20261026_ZH.md` 全长 sha256 `e00ba1b7171cd5621c3250881d731d331e1da33f7a80154c2cc0d1979e6c6c00`（sha8 **`e00ba1b7`**）——本 FROZEN 在基盘上写死 λ/IC 方向并钉 APPROX/GAP；**不**把计数 APPROX 当 X2 交付。
- 对齐：网研 `docs/v2/WEB_RESEARCH_15PCT_PATHS_ZH.md` §第十七轮；叶19 `docs/v2/AI_G1G5_CFACC_RNOA_WHO_PAYS_PREREG_ZH.md`；叶25 r6 + alpha sha8 `8be12024`。
- 叶号：**叶30**（叶28/29 仍 FROZEN；叶26 GAP **不交审**）。
- **本冻结 ≠ `.ok` / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**禁**动 A18（`.ok` sha8 `6de02e74`）。
- `live=false`；`promotion_approved=false`；禁 GP/高杠杆/教科书主线。

---

## ⚠ APPROX / GAP（醒目钉；冻结时仍成立）

| # | 钉 | 含义 |
|---|---|---|
| A1 | **计数闸 APPROX** | `docs/v2/audit/AI_LEAF30_CRR_COUNT_GATE_RECEIPT_20261026_ZH.md` sha8 **`24d1bcfd`**；JSON sha8 **`b0e7b1d0`**；脚本 sha8 **`ad524f9e`**。覆盖统计用 `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（YTD OCF/净利润代理），**不是**完整 16 季营业利润 CRR，**未**算 `vol_pen`。 |
| A2 | **X2 / 正式构建禁止用 APPROX 冒充** | 正式 α 构建与另窗 X2 **必须**用 `financials_pit_tushare`（`operate_profit`）+ `cashflow_pit_tushare`（`n_cashflow_act`）做 YTD→单季→L≈16 季 CRR，并实现 CFOOE 残差 `vol_pen`。 |
| A3 | **GAP** | 日频 ocf 表无 `operate_profit` 列；完整 CRR 不得静默用净利润替换营业利润。缺季/分母≤0 → 该票该日无效，记覆盖缺口。 |
| A4 | **计数过闸 ≠ 晋级** | gate_pass=true（APPROX）只授权进入本 FROZEN→Arch 审→另窗 X2 队列；**≠X2 ACCEPT**。 |

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_crr_cfooe_volpen_v1`（叶30）  
> **who_pays（一句）**：付钱的是按同期报表利润/EPS 定价、忽视「过去约 16 个季报窗口内营业利润→经营现金流转化效率（CRR）及其跨期稳定性（CFOOE 对截面回归残差的滚动波动）」的交易者；高 CRR 且转化稳定者被低估持续性。  
> **可检验预测（已冻结）**：`α_raw = rank(CRR) − 1.0·rank(vol_pen)` 对**次期特质收益**的截面 IC **期望为正**（高 α → 更高次期特质收益）；活跃集 vs 叶19 / 叶25 / `accrual_quality` 的 Jaccard≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；HI_LIQ 再平衡日可算 α 名数 median≥300。  
> **失效条件**：与叶19 近等权（Jaccard≥0.7）；或退化为无时序窗/无 vol_pen 的单点 OCF÷利润；或未排除银行/房地产/非银金融；或冻结后事后翻转 IC 符号/改 λ；或把计数 APPROX 当 X2 主交付；或主信号混入卖方/金股/一致预期/GP。  
> **交 Alpha 时点**：Arch 审构建脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（会计慢叶；时序转化，非同期应计）

**CRR（现金流实现率）**：在 PIT 可用的连续季报上，取过去 L=**16** 个单季（至少 **12** 个有效季才算）：

$$
\mathrm{CRR}_{raw} = \frac{\sum_{q\in L}\mathrm{OCF}_q}{\sum_{q\in L}\mathrm{OP}_q}
$$

- 分母 ≤0、有效季 <12、或关键字段缺 → 该票该再平衡日**无效**（记覆盖缺口，勿静默填 0）。
- YTD→单季：对齐叶19（连续季报差分；同一 `(ts_code,end_date)` 取**最早** `available_at`；次一交易日起可用）。
- OCF = `n_cashflow_act`；OP = **`operate_profit`（营业利润）**——正式构建**禁止**用净利润永久替代（计数 APPROX 已披露，不得升格）。

**CFOOE / 残差波动惩罚（冻结）**：

1. 截面输入：最近可用单季 `OCF_q/OP_q`（分母≤0 无效）。
2. 对 HI_LIQ 池内截面 OLS：**SW L1 dummy + log 流通市值（T−1）** → 残差 ε。
3. `vol_pen = rolling_std(ε)`，窗长 **8** 个季报点；最少有效点 **≥6** 季，否则该票该日无效。

**合成（冻结）**：

$$
\alpha_{raw} = \mathrm{rank}(\mathrm{CRR}) - \lambda\cdot\mathrm{rank}(\mathrm{vol\_pen}),\quad \lambda^{\mathrm{FROZEN}}=1.0
$$

池内百分位 rank → §3 残差中性 → 日度 base-α 向量（**非 Top-N**）。

---

## 2. 相对叶19 / 叶25 的分家

| 包 | 要点 | 叶30 必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` | 同期 CFACC+(Δ)RNOA | **多季时序 CRR** + **CFOOE 残差波动惩罚** |
| 叶25 `cfacc_desens` | 应计脱敏/质量应计全叶 | 同族硬闸；禁复用叶25 `.ok`/alpha 当本叶交付 |
| 库内 `accrual_quality` | BS WC 应计 | 现金流量表时序转化 |
| 教科书单点 OCF/利润 | 单期比率 | 必须 L=16 + vol_pen；单点仅曾作计数 APPROX |

**一句话分家**：叶19=同期 CFACC+(Δ)RNOA；叶25=应计脱敏全叶；叶30=**多季营业利润→OCF 转化效率 + 残差波动惩罚**。

---

## 3. 残差化清单（冻结最低集）

1. 原始：`CRR_raw` 与构建 `vol_pen` 的 ε 序列。  
2. **行业硬掩码**（§5）信号前排除。  
3. **SW L1 demean**（掩码后）。  
4. vs **log 流通市值** OLS 残差（T−1 PIT）。  
5. **本冻结不强制**再正交 mom20/mom60/vol20/log ADV20（若 X2 前 Arch 要求加正交，须补丁文件，不得静默改本钉）。  
6. 披露 vs 叶19 / 叶25 / `accrual_quality` 的 Jaccard 与 ρ_excess；家族多重检验 n ≥4（上述三项 + 本叶）。

---

## 4. 方向与 λ（已冻结；禁事后切换）

| 项 | **FROZEN** |
|---|---|
| 主规格 | `α_raw = rank(CRR) − λ·rank(vol_pen)`，高 CRR、低 vol_pen 优先 |
| **λ** | **1.0** |
| **IC 符号** | 对**次期特质收益**的截面 IC **期望为正**（事先机制：高现金实现且稳定 → 正超额；**冻结前未读本叶收益**） |
| 禁事后翻 | 不得因 X2/密封读数改 λ、改符号、或改为奖励高 `vol_pen` |
| 敏感性 | 非主规格支路若将来要报 λ∈{0.5,1.5}，须另文件且不得升格主规格 |

---

## 5. 行业掩码（硬排除）

申万一级（`data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`）：

| sw_name | sw_code | 处理 |
|---|---|---|
| 银行 | `801780.SI` | **硬排除** |
| 房地产 | `801180.SI` | **硬排除** |
| 非银金融 | `801790.SI` | **硬排除**（「综金」按非银金融） |

注：`综合`=`801230.SI` **不**在本掩码内。PIT：`in_date`/`out_date`/`available_at` as-of 再平衡日。

---

## 6. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| 叶19 `cfacc_rnoa` | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **只算强度过滤**（披露） |
| 叶25 | 同上 |
| `accrual_quality` | 同上；计入家族 n |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300** |
| 换手/成本 | 评价口径 **30bp**；>20%/日或成本>毛超额一半 → 不可交易 |
| 衰减 / Gate A·B / GATE_V3 | 另窗独立 `.ok`+X2 后再跑；**本冻结不跑** |

计数闸抽样（APPROX，已收）：ρ_mean vs 叶19≈0.365 / 叶25≈0.371；J20_max≈0.026 / 0.053 —— **仅入口参考**，正式 X2 须用完整 CRR α 重算。

---

## 7. 宇宙 / 窗 / 交付

| 项 | **FROZEN** |
|---|---|
| 宇宙 | **HI_LIQ 主**（`output/strategy_hiliq/universe_mask_hiliq_v1.parquet`，HI_LIQ_V1.1） |
| X2 样本内窗 | **2024-06-03 → 2026-10-09** |
| 再平衡 | 每 **20** 交易日（慢 α） |
| 成本口径 | **30bp** |
| 主交付 | **日度 base-α 向量**；非 Top-N |
| live / promotion | `false` / `false` |

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 角色 |
|---|---|---|
| 1 | `data/v2/financials_pit/financials_pit_tushare.parquet`（`operate_profit`） | **完整 CRR 必用** |
| 2 | `data/v2/financials_pit/cashflow_pit_tushare.parquet`（`n_cashflow_act`） | **完整 CRR 必用** |
| 3 | `ocf_to_profit_pit_daily_tushare.parquet` | **仅**计数 APPROX；**禁止**作 X2 主交付 |
| 4 | SW L1 PIT | 银/地/非银硬排除 |
| 5 | HI_LIQ 掩码 | 上表 |
| 6 | log 流通市值 T−1 | 残差 |
| 7 | 叶19 / 叶25 α | 仅 Jaccard/ρ；不进主信号 |

---

## 9. 状态机 / 下一跳

```
who_pays DRAFT e00ba1b7 + count gate_pass APPROX
  → 【本文件】who_pays FROZEN
      → 主排 Arch 审（构建脚本待写/待审）
          → 另窗独立 .ok（禁复用叶25；避 A18）
              → X2（完整 16 季 OP CRR + vol_pen；≠APPROX）
```

| 项 | 状态 |
|---|---|
| 本 FROZEN | **本文件** |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |
| A18 | **勿动** `6de02e74` |

---

## 10. 禁项清单（再钉）

- 把计数 APPROX（ocf_to_profit）当作 X2/正式 α 交付  
- 自申 `.ok`；自开 X2/selfcheck/Book-Smoke；动 A18；挂/抬 QUIET；抬 RSS  
- 复跑叶25 alpha；改叶25 build  
- GP / 高杠杆 / 教科书单点比率当主规格  
- 冻结后改 λ 或 IC 符号  
- 未掩码银行/房地产/非银金融  
- 与叶19/25 Jaccard≥0.7 仍宣称新叶  
- `live=true` 或 `promotion_approved=true`

---

## 11. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` |
| 基盘 DRAFT sha8 | `e00ba1b7` |
| 状态 | **FROZEN** |
| λ | **1.0** |
| IC 符号（次期特质收益） | **期望为正** |
| mechanism_tag | `g1g5_ashare_crr_cfooe_volpen_v1` |
| live | false |
| promotion_approved | false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
