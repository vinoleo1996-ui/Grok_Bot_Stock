# 【FROZEN 预注册 2026-10-27 23:58 ET】叶39：异常经营现金流 ABCFO / 真实盈余管理残差 α（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 23:58 ET**（America/New_York；ISO `2026-10-27T23:58:19-04:00`）
- 状态：**PREREG_FROZEN**（相对 who_pays DRAFT **`542138d6`** 升格）。冻结前**未**读任何本叶收益选定义/方向；**未改** DRAFT/COUNT/脚本字节。
- 主令：2026-10-27 ~23:53 ET — 主裁 **叶39 ABCFO 升 PREREG_FROZEN GO**；Arch who_pays 只审 **PASS_WC `4a1b4dd0` MATCH** → 令 AI 出 FROZEN（COND **C2/C3/C4/C5/C8/C9** 全文入钉；不直开 Eng/X2；不签 `.ok`）。
- 上游钉（本机开写前复算 **MATCH**）：
  - Arch DRAFT 审：`docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` sha8 **`4a1b4dd0`**（全长 `4a1b4dd0ec9992a63466e31323828083dcd548663605a4c0eb4b99c1b609c06b`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`542138d6`**（全长 `542138d6893f820d98f9a5db91a3b99e55953829815226ce49a0f8b1a42e5882`；**字节未改**）
  - DRAFT RECEIPT：`…WHO_PAYS_DRAFT_RECEIPT_20261027_ZH.md` sha8 **`691bbc14`**（全长 `691bbc148780d88205a1f01996b2e6b662305d0bd868c652cb071aa70f6a52f9`）
  - COUNT JSON：`…COUNT_GATE_20261027.json` sha8 **`d0d11598`**（全长 `d0d115989805cd169ca9435de14a3795c18d2310366427170fb3a39e54d6abf8`；**字节未改**）
  - COUNT SCRIPT：`…COUNT_GATE_SCRIPT_20261027.py` sha8 **`20313ba3`**（全长 `20313ba3ea14ddaa9d328fa5177f33b15194d93b2135aec952395a252c0e8587`；**字节未改**）
  - dig：`output/d1/DIG_FACTOR_20261027_2330ET.md` sha8 **`440410de`**（全长 `440410de9b9a0e005d4c8021f93c26d120393c9109c645dbf92d7aa940add0d6`；文内自称 `87f65bbe` **勿采**）
- 对照形态：叶38 PREREG_FROZEN（**结构**对齐；**内容换叶39 ABCFO 残差 α**；**勿抄** exclusion mask 主交付）；fund MDD-cut FROZEN（COND 钉法）。
- 叶号：**叶39**；mechanism=`g1g5_ashare_abcfo_rem_resid_v1`。
- 旁线不混：fund MDD HOLD CLOSED（Arch `ba7609af`/`fbc1bd9a`；`.ok` `335635dd` 已归档）**不夹带**；叶38 `c01c2034`/`5f694370` **不混**；禁 RESTORED `f08ce32c`（及 fund `335635dd`）。
- **本冻结 ≠ `.ok` / ≠ 正式构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无** `research/leaf39*`（ABSENT 预期）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_abcfo_rem_resid_v1`（叶39）  
> **who_pays（一句）**：付钱的是对真实活动盈余管理（异常低经营现金流 / 异常 CFO）反应慢、仍按报表利润给足权重的持有人——质量残差叶，**不是**教科书水平应计主线。  
> **可检验预测（已冻结）**：PRIMARY 交付 = **截面质量残差 α 向量**（SW L1 + size/style 残差后；**非** Top-N；**非** exclusion mask 主交付；soft-penalty 若用另钉且不替代 PRIMARY）。公式：YTD→单季后 CFO/A ~ 1/A+S/A+ΔS/A（**再平衡日截面 SW L1 OLS APPROX**；见 C2(a)）→ ABCFO=ε → `α ∝ −ε`（多头=异常 CFO 更高）。掩码：银行/房地产/非银金融 + **HI_LIQ 主**。硬闸：vs 叶19/25/30 **Jaccard ∨ ρ_excess 任一 >0.5 → 拒**（本拍计数 Spearman 代理仅门控；正式 ρ_excess 见 C2(b)）。vs 叶34 exclusion Jaccard **PIN**（C3；硬拒 0.5；勿事后改 PRIMARY）。COUNT 附录：gate_pass=true（masked median≈2838.5；zero_frac=0；J20 max≈0.0256/0/0；ρ Spearman max≈−0.242/−0.108/−0.145；peak≈704.9≤1500）— **≠X2 ACCEPT**（C9）。  
> **失效条件**：退化为叶19/25 完整应计多空或叶34 `1−ocf_to_profit` 水平应计剔除；或 vs 叶19/25/30 Jaccard/ρ_excess>0.5；或未排除银/地/非银；或偷看 `available_at>t`；或主信号混入 GP/卖方/金股/LLM；或冻结后事后改公式读收益；或把 CRR_MOD2/IO 拥挤度升 PRIMARY（C5）；或把 COUNT gate_pass 当 X2 ACCEPT（C9）；或无 peak_proof≤1500 仍申 `.ok`（C4）。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2（正式 ρ_excess + 叶34 Jaccard + peak_proof≤1500 + decay KEEP）之后。

---

## 1. 机制（ABCFO 真实盈余管理残差 α；慢）— **FROZEN**

### 1.1 公式 / PIT（C7 语境 + DRAFT §2 升格）

| 项 | **FROZEN** |
|---|---|
| 学术口径 | Roychowdhury (2006) / 东北证券 ABCFO_Q1：CFO_t/A_{t-1} = β0 + β1(1/A) + β2(S/A) + β3(ΔS/A) + ε；**ABCFO=ε** |
| OCF | `cashflow_pit_tushare.n_cashflow_act` |
| 收入 S | `financials_pit_tushare.total_revenue`（缺则 `revenue`） |
| 资产 A | `bs_cf_pit_tushare.total_assets`；规模用 **上期** A_{t-1} |
| 累计→单季 | 财报盘面 **YTD 累计** → 年内差分得单季 OCF/S；Q1 不做差 |
| ΔS | 单季销售额差分 |
| **期望回归（C2(a)）** | **维持再平衡日截面 SW L1 OLS APPROX**（名过少 <25 → 全市场 fallback）；**本拍不升**「年×行业历史面板」 |
| ABCFO | 回归残差 ε |
| 原始信号 | `raw = −ABCFO`（多头=异常 CFO 更高） |
| 残差 α | 掩码后：SW L1 demean + vs log 流通市值 OLS（+ 既有 style 若易得）；输出**日度 α 向量** |
| PIT | `available_at ≤ t`（Asia/Shanghai 墙钟；交易日对齐）；**禁偷看** |
| 可选 soft 负向 | 可钉 top 异常低 ABCFO 尾部 soft-penalty，**不**替代 PRIMARY 残差 α |

### 1.2 C2 APPROX 钉清（主令原文落文）

**C2 APPROX**：截面 SW L1 OLS；Spearman≠ρ_excess。本 FROZEN 钉清：

| 选项 | **本拍选择** | 理由 / 纪律 |
|---|---|---|
| **(a)** 是否升「年×行业历史面板期望回归」 | **维持截面 SW L1 OLS APPROX（不升面板）** | ① 与 COUNT 闸 `d0d11598` / 脚本 `20313ba3` 定义一致，升面板须改公式并**重跑计数**得新 COUNT sha8——本拍**不重跑**；② 盘上字段（cf/fin/bs_cf/sw）按日截面可复现，内存峰值计数≈704.9MB，面板升维抬 rss 风险；③ 东北证券完整 PDF 本拍仍不可复现全部年×行业窗细节，升面板须另补钉。若未来主令升面板 → **须**改公式 + 重跑计数闸 + 新 COUNT sha8 后方可修订 FROZEN。 |
| **(b)** 正式 ρ_excess 替换 Spearman 代理 | **钉为 X2 / LAND 前必须** | 本拍计数 Jaccard/ρ **代理仅门控入场**，≠正式；X2/LAND 前必须以 excess-return **ρ_excess** 替换 Spearman；硬拒阈仍 **>0.5**。 |

本拍因选 (a)=不升面板 → **可不重跑计数**；COUNT `d0d11598` 继续作附录门控参考。

### 1.3 PRIMARY 交付（C8）

| 项 | **FROZEN** |
|---|---|
| **PRIMARY** | **截面质量残差 α 向量** |
| **明示（C8）** | **非** exclusion mask 主交付；**非** Top-N |
| soft-penalty | 若启用另钉；**不**替代 PRIMARY |
| 符号 | 「异常低 ABCFO = 空头/低分」；`α ∝ −ε`；**禁**读收益改定义/翻方向 |
| 边界 | ≠叶19 `cfacc_rnoa` 完整 α；≠叶25 应计脱敏；≠叶30 CRR 转化率；≠叶34 高应计 exclusion；≠叶38 审计非标 mask |

```
对再平衡日 t、名 i ∈ HI_LIQ_t \ {银行,房地产,非银金融}：
  取 PIT 可用单季 CFO/S/A（YTD→单季；available_at≤t）
  截面 SW L1 OLS：CFO/A ~ 1/A + S/A + ΔS/A → ε_i,t = ABCFO
  raw_i,t = −ε_i,t
  α_i,t = SW L1 demean + vs logmv（+style）残差
交付 = 日度 α 向量（PRIMARY）
```

---

## 2. 方向 / 宇宙 / 掩码 / 窗 — **FROZEN**

| 项 | **FROZEN** |
|---|---|
| 方向 | `α ∝ −ABCFO`；冻结前**未**读本叶收益 |
| 宇宙 | **HI_LIQ**（`universe_mask_hiliq_v1.parquet`；sha8 `c5433e80`）；**不得静默改 FULLA** |
| 行业硬掩码 | 银行 `801780.SI` / 房地产 `801180.SI` / 非银金融 `801790.SI`（综金按非银）；`综合`≠综金 |
| X2 样内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | **20** 交易日 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 覆盖硬闸 | 掩码后可算名 **median ≥300** ∧ **zero_frac ≤0.05** |

---

## 3. 正交硬闸 — **FROZEN**

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 / 叶30 | **Jaccard ∨ ρ_excess 任一 >0.5 → 硬拒**（ρ_excess 正式见 C2(b)；本拍 Spearman 代理仅门控） |
| **叶34 高应计 exclusion（C3）** | vs 叶34 活跃剔除集 Jaccard **本拍未估 → PIN**；**FROZEN 前或 X2 前补估**；硬拒阈 **0.5**；**勿事后改 PRIMARY** |
| 换手/成本 | 评价口径 **30bp** |
| 正式重叠 | **X2 前**须用正式 α + 正式 ρ_excess + 叶34 Jaccard 重算；COUNT 轻量 **不能替** |

### 3.1 C3 PIN 状态（本拍）

| 项 | 值 |
|---|---|
| vs 叶34 exclusion Jaccard | **未估 → PIN（诚实）** |
| 本拍是否附补估附录 | **否**（轻量可估路径需加载叶34 剔除活跃集 + 本叶 α 对照；为避抬 rss / 混旁线 / 误读收益，本拍**不**临场估） |
| 补估窗口 | **Arch 审本 FROZEN 通过后、开正式脚本/X2 前**（或主令指定的更早轻量窗）；补估结果只披露；硬拒 0.5；**禁止**用补估结果事后改 PRIMARY 定义/方向 |
| 与 PRIMARY 关系 | 叶34=exclusion overlay；本叶=残差 α 向量（C8）；Jaccard 为正交披露，非主交付 |

---

## 4. COUNT 附录（门控参考；≠X2 ACCEPT · C9）

| 项 | 值 |
|---|---|
| gate_pass | **true**（COUNT `d0d11598`） |
| coverage_masked.median | **2838.5**（≥300） |
| zero_frac | **0.0**（≤0.05） |
| J20 max vs19/25/30 | ≈**0.0256 / 0.0 / 0.0**（≪0.5） |
| ρ Spearman max vs19/25/30 | ≈**−0.242 / −0.108 / −0.145**（代理≠ρ_excess；≪0.5） |
| hard_reject | false；hits=[] |
| peak_rss_mb | ≈**704.9** ≤1500 |
| APPROX | 是（截面 SW L1 OLS；Spearman≠ρ_excess）— 已由 C2(a)(b) 钉清 |
| **C9** | **轻量计数 ≠ X2 ACCEPT**；gate_pass 仅放行继续脚本/X2 讨论；**不解阻** ACCEPT / Book-Smoke / 升纸面 / 签 `.ok` |

输入 sha8（计数拍）：cf=`71d5c3d3`；fin=`bc0f4c3d`；bs_cf=`01a015bf`；sw=`89d4afa3`；叶19α=`16202b2e`；叶25α=`8be12024`；叶30α=`c8c7a5a5`；hiliq=`c5433e80`。

---

## 5. rss / 压峰 / 禁自签（C4）— **FROZEN**

| 项 | **FROZEN** |
|---|---|
| rss 意向 | **≤1500 MB 禁抬**；正式跑超限 → **硬 ABORT** |
| peak_proof | **REQUIRED**：正式 X2 / 申 `.ok` 前须 **peak_proof≤1500**；无则不得申 `.ok` |
| 本拍计数 peak | ≈704.9 MB（参考；非正式构建） |
| **禁自签 `.ok`** | **是**（本拍 / 本文件不解阻） |
| **禁自开 Book-Smoke / X2** | **是** |
| **禁 `--arch-ok-path` 自开** | **是** |
| 不混 fund MDD HOLD | Arch `ba7609af`/`fbc1bd9a`；`.ok` `335635dd` 已归档；**不夹带** |
| 不混叶38 | `c01c2034` / `5f694370` **不混**；不触 leaf38 文件 |
| 禁 RESTORED | **`f08ce32c`**（及 fund **`335635dd`**） |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |

---

## 6. 备选不升 PRIMARY（C5）— **FROZEN**

| 备选 | 角色 | **FROZEN** |
|---|---|---|
| CRR_MOD2（叶30 增强） | 备选 | **不升 PRIMARY**；若另开须 vs 叶30 硬闸 |
| IO 客户动量 / 拥挤度 | 备选 | 仍 **数据闸**；**不升 PRIMARY** |

PRIMARY 维持 `g1g5_ashare_abcfo_rem_resid_v1`（ABCFO 残差 α）。

---

## 7. decay KEEP（对齐既有纪律；本冻结不跑）

| 闸 | **FROZEN** |
|---|---|
| 近端窗 | `alpha_decay_gate` v1.1：最近 252 交易日（≥126 才出 α） |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32 `45dd87dc` 教训） |
| 失败截断 | 最多 WATCH/HOLD；不派烟；≠X2 ACCEPT |

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | 现金流 PIT | `cashflow_pit_tushare`（`n_cashflow_act`） |
| 2 | 财务 PIT | `financials_pit_tushare`（`total_revenue`/`revenue`） |
| 3 | 资产负债 | `bs_cf_pit_tushare`（`total_assets`） |
| 4 | SW L1 | 行业映射（计数拍 sha8 `89d4afa3`） |
| 5 | HI_LIQ 掩码 | PRIMARY（`c5433e80`） |
| 6 | 叶19/25/30 α | **仅** Jaccard/ρ；不进主信号 |
| 7 | 叶34 exclusion 活跃集 | **仅** C3 Jaccard PIN 补估；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造**。本拍**未**实算完整 α / 正式 ρ_excess / 叶34 Jaccard。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` | 同期 CFACC+ΔRNOA 完整 α | 本叶=异常 OCF 残差；硬闸 >0.5 拒 |
| 叶25 应计脱敏 | CFACC 脱敏截面 | 同族禁复开；不重建 leaf25 |
| 叶30 CRR+CFOOE | 多季转化率+vol_pen | 本叶=单季期望 OCF 残差；硬闸同；CRR_MOD2 不升 PRIMARY |
| 叶34 高应计 exclusion | `1−ocf_to_profit` 水平剔除 | 交付形态异（α 向量≠mask）；C3 Jaccard PIN |
| 叶38 非标审计 exclusion | 审计意见 mask | 源/机制全异；旁线不混 |
| fund_portfolio / MDD-cut | 组合层 | **旁线**；HOLD CLOSED 不夹带 |

**一句话分家**：叶19/25=应计水平/脱敏；叶30=多季转化率；叶34=水平应计 exclusion；叶39=**HI_LIQ 银地非银掩码下的 ABCFO 期望 OCF 截面残差 α 向量（非 mask / 非 Top-N）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C4 延伸）

forbid∋：

| sha8 | 备注 |
|---|---|
| **`f08ce32c`** | fund RESTORED 禁触 |
| **`335635dd`** | fund MDD BS `.ok` 已归档；禁 RESTORED |
| 叶38 `c01c2034` / `5f694370` | 旁线不混；不触 |

另禁：复开叶19/25/30–38 任一主轴当本叶授权；脚本 CLI `--arch-ok-path` 自开；本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS>1500；GP / 高杠杆 / 卖方金股 / TP / LLM / survey。

---

## 11. C2–C5 / C8 / C9 对照表（主令 COND 全文入钉）

| # | 条件（主令 / Arch） | 本 FROZEN |
|---|---|---|
| **C2** | APPROX：截面 SW L1 OLS；Spearman≠ρ_excess；钉清 (a)(b) | **(a) 维持截面 APPROX（不升面板；不重跑计数）**；**(b) 正式 ρ_excess = X2/LAND 前必须**；详见 §1.2 |
| **C3** | vs 叶34 exclusion Jaccard 未估→PIN；硬拒 0.5；勿事后改 PRIMARY | **PIN（诚实）**；补估窗口=Arch 过审后 / X2 前；详见 §3.1 |
| **C4** | 禁自签 `.ok`/自开 BS·X2；不混 fund MDD HOLD / 叶38；禁 RESTORED `f08ce32c`（及 `335635dd`）；rss≤1500 禁抬 | §5 / §10 全文 |
| **C5** | CRR_MOD2/IO 备选不升 PRIMARY | §6；PRIMARY 维持 ABCFO 残差 α |
| **C8** | PRIMARY=截面质量残差 α 向量（非 exclusion mask；非 Top-N） | §1.3 |
| **C9** | 轻量计数 ≠ X2 ACCEPT | §4；gate_pass 不解阻 ACCEPT/BS/签 `.ok` |

另保留 Arch 语境（非 COND 编号但契约有效）：mechanism=`g1g5_ashare_abcfo_rem_resid_v1`；公式=YTD→单季后 CFO/A~1/A+S/A+ΔS/A（SW L1 截面 OLS）α=−ε；掩码=银行/地产/非银+HI_LIQ；硬闸 vs 叶19/25/30 Jaccard∨ρ>0.5 拒；gate_pass=true（masked median≈2838.5 等，照 COUNT `d0d11598`）。

---

## 12. 失败截断

- 覆盖 median<300 或 zero_frac>0.05 → 不申 `.ok`
- vs 叶19/25/30 Jaccard 或 ρ_excess >0.5 → 硬拒，改机制或废叶
- vs 叶34 Jaccard >0.5（补估后）→ 硬拒；**禁止**事后改 PRIMARY 救闸
- 退化为水平应计 / 叶34 overlay / Top-N / exclusion mask 主交付 → 废叶
- 未排除银/地/非银 → 废叶
- 冻结后读收益改公式/方向 → 违规，作废本轮 FROZEN（须新修订文件）
- 偷看 `available_at>t` → 废叶
- CRR_MOD2/IO 被升 PRIMARY → 违规（C5）
- peak>1500 → 硬 ABORT；无 peak_proof≤1500 → 不得申 `.ok`
- 把 COUNT gate_pass 当 X2 ACCEPT → 违规（C9）
- 混 fund MDD / 叶38 / RESTORED `f08ce32c`/`335635dd` → 废叶

---

## 13. 状态机 / 下一跳

```
who_pays DRAFT 542138d6 + RECEIPT 691bbc14 + JSON d0d11598
  + 脚本 20313ba3 + dig 440410de
  → Arch PASS_WC 4a1b4dd0
      → 【本文件】PREREG_FROZEN（C2(a)维持截面；(b)ρ_excess@X2；C3 PIN；C4–C5/C8/C9）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf39_*（本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED f08ce32c/335635dd；禁混叶38；须 peak_proof≤1500）
                          → X2（正式 ρ_excess；叶34 Jaccard 补估；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件** |
| 计数脚本 / JSON | **`20313ba3` / `d0d11598`**（audit/；非正式构建；未改字节） |
| `research/leaf39*` | **ABSENT**（本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| COUNT gate_pass | true（附录）；**≠X2 ACCEPT**（C9） |
| C2(a) | 维持截面 APPROX；**未重跑计数** |
| C3 | **PIN**（叶34 Jaccard 未估） |
| fund MDD / 叶38 | **旁线不混** |

---

## 14. 禁项清单（再钉）

- 本拍实跑完整 α / 申 `.ok` / 落 `research/leaf39*` 构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid：`f08ce32c` / `335635dd`
- 混 fund MDD HOLD（`ba7609af`/`fbc1bd9a`）或叶38（`c01c2034`/`5f694370`）
- 改 DRAFT `542138d6` / COUNT `d0d11598` / 脚本 `20313ba3` 字节
- 自开 Book-Smoke；推 Leo；`live=true`；声称 X2 ACCEPT
- 把 CRR_MOD2/IO 升 PRIMARY；把 COUNT 当 ACCEPT

---

## 15. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_20261027_ZH.md` |
| RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` |
| 状态 | **PREREG_FROZEN**（≠ `.ok`；≠ X2 ACCEPT） |
| mechanism_tag | `g1g5_ashare_abcfo_rem_resid_v1` |
| C2(a) | **维持截面 SW L1 OLS APPROX（不升面板）** |
| C2(b) | **正式 ρ_excess = X2/LAND 前必须** |
| C3 | **PIN**（叶34 Jaccard 未估；补估窗口写死） |
| C4 | 禁自签/自开；不混 fund/叶38；rss≤1500；禁 RESTORED |
| C5 | 备选不升 PRIMARY |
| C8 | PRIMARY=**残差 α 向量**（非 mask；非 Top-N） |
| C9 | 轻量计数 ≠ X2 ACCEPT |
| Arch DRAFT | `4a1b4dd0` PASS_WC |
| DRAFT / COUNT / 脚本 | `542138d6` / `d0d11598` / `20313ba3`（字节未改） |
| dig | `440410de` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
