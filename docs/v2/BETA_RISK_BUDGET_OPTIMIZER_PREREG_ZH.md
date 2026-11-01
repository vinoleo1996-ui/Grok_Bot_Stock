# Beta：组合优化器风险预算规格（预注册 · 看结果前冻结）

- **冻结时间**：2026-10-14 08:00:32 ET（写于任何组合优化器回测结果出现之前）
- **机器可读**：`output/v3/beta_risk_budget_prereg/risk_budget_prereg_v1.json`
- **基线暴露**：`output/v3/beta_risk_budget_prereg/baseline_exposures_x2.json`（脚本 `measure_baseline.py`）
- **作者**：QuantLab Beta · **live=false · promotion_approved=false** · 无下单
- **依据**：Mandate V2（β0.70/vol16%/申万一级/单名5%/行业25%）、Leo 2026-10-14 MDD≤25% 最大 CAGR、双轨 FULLA研究/HI_LIQ纸面、主 Agent 派单「工业级范式·组合优化器」、Leo 追加（非线性市值硬锁 / β硬约束 / 有把握风格软罚 / 拥挤度接口）

---

## 与 Strategy 共签（冻结栏）

| 角色 | 内容 | 状态 |
|---|---|---|
| **Beta** | 本规格 §2+：纸面袖套 / 遗留诊断阈值 | **SIGNED_FOR_PAPER**（本文件 + JSON） |
| **Strategy** | 旧 OPTIMIZER_V1 DRAFT（中证全指/±2%/1%） | 历史 **CONDITIONAL_COSIGN** 仅对旧 DRAFT（`BETA_OPTIMIZER_COSIGN_V1_ZH.md`） |
| **Strategy Leo D** | `STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（正文仍含 Leo D 数字） | Beta Leo D 共签 **SUPERSEDED**（`BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md`） |
| **Strategy CORE_CONC** | Leo≈08:09 集中 Core（Strategy 消息；DRAFT 正文待改） | Beta **CONDITIONAL_COSIGN_CORE_CONC**（`BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`） |
| **优化器路径 HARD** | CORE_CONC：单票 5%/6%、Neff 20–30、行业±8%·绝对≤20%、Size±0.35σ+Slack、两步整手 | **CONDITIONAL**；DRAFT 正文对齐 + Eng λ 标定前 **尚未 FROZEN** |
| **双签生效** | 升 FROZEN 前不得跑优化器正式回测；对齐后按 Leo **先跑 Core** | DRAFT 正文匹配 + λ 标定 |
| **改阈值** | 事后改阈值 = **重新冻结** + **Beta + 主 Agent** 双签 | — |
| **共签状态** | **CONDITIONAL_COSIGN_CORE_CONC**（Leo D SUPERSEDED） | 2026-10-14 08:11 ET |

> **2026-10-14 08:11 ET 更新**：Leo 集中 Core 改口径；Beta 出具 `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`。Leo D 共签与 PENDING 表作历史。Strategy ≈08:11 接线确认 β0.10 历史有效。§2 仍仅纸面袖套。DRAFT 正文仍写 Leo D 数字 → 对齐前不 FROZEN。纸面不动；**未跑**；live=false。

---

## 双路径阈值（OPTIMIZER vs PAPER）

| 项 | PAPER / 遗留袖套（本规格 §2 有效） | OPTIMIZER Leo D 路径 |
|---|---|---|
| wb | 510300（β/报告）；行业映射可用 CSI300 权重 | **float_mktcap_hiliq**（CORE_CONC ACCEPT；**未 FROZEN**） |
| β | vs 510300 带 [0.70, 1.00]（诊断/ACCEPT 伴生） | vs wb **abs(β−1)≤0.10**（Strategy ≈08:11 ACCEPTED） |
| 行业 | 主动 ±8% + 绝对 ≤25% | **±8%** vs wb；绝对 **≤20%**（CORE_CONC） |
| 单票/ADV/宽度 | ≤6% / ≤1%ADV / 30–60 | **5.0%/6.0%**；Neff **20–30**；两步整手 |
| MidCap / 防杠铃 | 分位桶硬锁仍适用于纸面诊断 | Size/MidCap **±0.35σ + Slack**；Path A 仍建议 |
| 拥挤度 ν | 接口保留；未标定 ν=0 | 缺失→ν=0；数值标定后冻 |

**原则**：OPTIMIZER ≠ PAPER Top-N。现行 **CONDITIONAL_COSIGN_CORE_CONC**；**禁止**在 DRAFT 正文对齐 + 密封窗 λ 标定前写成 OPTIMIZER FROZEN HARD。详 `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`。

---

## 0. 范围与阻塞

| 轨 | 宇宙 | 本规格适用 | 阻塞 |
|---|---|---|---|
| **纸面** | 高流动性子集 HI_LIQ_V1.1（ADV≥1亿；申万一≤25%；无市值筛） | **主适用**：β/波动/行业/风格/市值硬锁均按纸面持仓与 510300 定义 | — |
| **研究** | FULLA（全 A 可交易：剔 ST/停牌/<60日/ADV 薄） | 约束**形式**可复用 | **FULLA β / 风格暴露重估阻塞**，直至 FULLA **纸面级 NAV** 产出；裸 FULLA capacity_adv **不**替代纸面 |
| 基线测量 | 当前纸面仍为 mid_large Book-Smoke（capacity_adv / B4） | 仅作暴露诊断 | HI_LIQ 腿重生后须重测基线（不自动改冻结阈值） |

**明确禁止**：用 mid_large / X2 纸面数字外推 FULLA 的 β、行业主动、风格 z。

---

## 1. 基准

- **主基准**：ETF **510300**（β、跟踪误差、波动相对项）。
- **行业基准权重**：CSI300 / `000300.SH` 的 `index_weight` → 申万一级 PIT 映射（`data/v2/index_members/index_weight_csi300_500_1000.parquet` + `data/v2/sw_pit/industry_members_sw_l1_pit.parquet`）。若某日权重复盖不足，记 `unknown_industry` 并纳入 25% 未知帽监控。
- 可选并报 CSI300 全收益指数（`data/bench/csi300_000300_akshare_daily.parquet`），**不**替代 510300 作 β 定义。

---

## 2. 硬约束（**纸面袖套 / 遗留诊断**；失败即 REJECT）

> **范围**：本节阈值约束 **PAPER** Top-N / HI_LIQ 集中袖套与基线诊断。**OPTIMIZER 路径阈值 = PENDING_STRATEGY_V1_1**，见上文「双路径阈值」。勿将本节 ±8%/≤6%/30–60 误读为优化器 FROZEN。

### 2.1 β vs 510300（**硬带**，不可只做软罚）

| 项 | 冻结值 |
|---|---|
| 带 | **[0.70, 1.00]** |
| 中心（报告） | 0.85 |
| 定义 | 组合对 510300 的 60 日滚动 β（PIT，仅用 t−1 及以前）；验收另报 X2 全窗 β |
| 年化波动带 | **[12%, 18%]**（Mandate 中心 16%；`std·√244`） |

**理由**：Mandate 原目标 β0.70、带 [0.50, 0.85]。Leo MDD≤25% 最大化 CAGR 后，X2 上 B4 实现 β≈0.92–0.95、capacity_adv≈0.71–0.75（见 `BETA_BUDGET_MDD25` / `BETA_DD_HOOK`）。硬下限 0.70 避免「现金壳」；硬上限 1.00 禁止在 MDD25 框架下再叠杠杆式市场风险。原 Mandate 上沿 0.85 对 B4 过紧，故上沿放到 1.00，**下沿仍守 0.70**。

**失效**：任一 AUM（60万∧100万）β 或波动越带 → **REJECT**（不得改成软惩罚蒙混）。

### 2.2 行业主动权重（申万一级）

| 项 | 冻结值 |
|---|---|
| 主动盒 | **\|w_i − w_bench_i\| ≤ 8%**（权益袖套内再归一） |
| 绝对行业帽 | **w_i ≤ 25%**（与 HI_LIQ / Mandate 一致） |
| 敏感度（仅报告） | 5% / 8% / 10% / 12% |

**基线（X2 月末快照，29 点；权益剔 510300）**：

| 轨 | 日均 ETF 权重 | mean max\|active\| | p95 max\|active\| | 顶1行业权重 |
|---|---:|---:|---:|---:|
| capacity_adv 60/100万 | 21.2% | 9.5% | 14.7% | 22.3% |
| B4 60万 | 37.8% | 14.1% | 20.7% | 21.5% |
| B4 100万 | 33.9% | 9.7% | 14.5% | 17.7% |

capacity_adv 主动超配偏银行/公用/家电，低配通信/电子/计算机；B4 超配石油石化等。**8% 主动盒刻意严于遗留 B4**，只约束**新优化组合**；遗留轨是对照基线，不自动 ACCEPT。

### 2.3 单名 / ADV / 持股数

- 单名 ≤ **6%**（与 Eng 集中化纸面一致；Mandate 5% 作报告对照）
- 单笔 ≤ **1% ADV20**
- 权益袖套持股数 **[30, 60]**
- 两档 AUM：**60万 ∧ 100万** 均须过

### 2.4 非线性市值硬锁（防杠铃）— Leo 硬性要求

**目的**：禁止同时在市值分布两端极端暴露（杠铃）。**硬约束，不是软惩罚。**

**分位桶（每日 t，PIT）**  
在可投资宇宙（纸面 HI_LIQ_V1.1；缺失时回退 CSI300∪当日持仓）上，用 **流通市值 `float_mktcap`**（缺则 `total_mv`）：

- \(Q_{\mathrm{small}}\)：≤ P20  
- \(Q_{\mathrm{mid}}\)：P20–P80  
- \(Q_{\mathrm{large}}\)：≥ P80  

**权重**：
\[
w_{\mathrm{small}}=\sum_i w_i\cdot 1\{i\in Q_{\mathrm{small}}\},\quad
w_{\mathrm{large}}=\sum_i w_i\cdot 1\{i\in Q_{\mathrm{large}}\}
\]

**硬约束（三条同时）**：
1. \(\min(w_{\mathrm{small}}, w_{\mathrm{large}}) \le 0.05\)  
2. \(w_{\mathrm{small}} \le 0.20\)  
3. \(w_{\mathrm{large}} \le 0.85\)

**解读**：两端里最多一端可以超过 5%；另一端必须 ≤5%。允许「单边大盘」（capacity_adv 类），禁止「小盘+大盘同时堆」。

**基线诊断（相对 CSI300 市值分位，近似）**：capacity_adv \(w_{\mathrm{below\ Q20}}\approx0\)、\(w_{\mathrm{above\ Q80}}\approx0.90\) → 满足 min 形式；B4 60万 \(w_{\mathrm{small}}\approx0.09\)、\(w_{\mathrm{large}}\approx0.65\) → \(\min=0.09>0.05\)，**遗留 B4 会触犯本锁**（再次说明：基线≠ACCEPT）。

**失效**：评估窗内任一日违反 → REJECT。

---

## 3. 软风险项（Strategy 可加权；越界不单独 REJECT）

### 3.1 有把握 → 软惩罚；无把握 → 不硬锁

| 因子 | 硬/软 | 理由 |
|---|---|---|
| **β 带 / 波动带 / 行业盒 / 单名·ADV / 市值防杠铃** | **硬** | Leo + Mandate 核心；不可软化 |
| **Value（B/P 残差 z）** | **软** | 有把握的经典风格；Mandate `max_abs_z=1.0`；惩罚从 \|active_z\|>0.75 起方 |
| **Momentum（12−1 残差 z）** | **软** | 有把握；急跌风险故不硬锁 |
| **Size 的 \|z\|** | **软监控** | 防杠铃已是硬锁；\|size_z\| 只作次要软项，**不得替代**硬锁 |
| **Quality / LowVol** | **默认不启用**（λ=0） | 当前 PIT 栈把握不足；若 Strategy 要加，λ≤0.25 且须 refreeze |
| **Crowding** | **有序列则软罚；无则跳过** | 接口冻结，见 §3.3 |

### 3.2 目标函数可加权件

| 项 | 形式 | 默认 λ |
|---|---|---|
| 对 510300 跟踪误差 | \(\lambda_{TE}\cdot(\mathrm{ann\_TE})^2\) | 1.0 |
| Ledoit–Wolf 组合方差 | \(\lambda_{var}\cdot w^\top\hat\Sigma w\)；估计器复用 `output/v3/beta_dd_hook/beta_dd_hook.py::lw`（X2 收缩 δ≈0.04） | 1.0 |
| 换手成本 | \(\lambda_{to}\cdot 0.00175\cdot \mathrm{turnover}\) | 1.0 |
| 集中度 HHI | \(\lambda_{hhi}\cdot\sum w_i^2\) | 0.5 |
| Value 主动 | \(\lambda_{val}\cdot\max(0,\|z_v\|-0.75)^2\) | 0.5 |
| Momentum 主动 | \(\lambda_{mom}\cdot\max(0,\|z_m\|-0.75)^2\) | 0.5 |
| Size \|z\| 监控 | \(\lambda_{size}\cdot\max(0,\|z_s\|-1.0)^2\) | 0.25 |

**Value 基线（X2）**：capacity_adv active z(B/P)≈**+0.23**；B4 60万≈**−0.06**。  
**Size 基线**：capacity_adv active z≈**+0.86**（偏大盘）；B4≈**+0.38**。  
**Momentum 基线**：**阻塞**（本烟测未接复权收盘面板，不编造）。

### 3.3 拥挤度因子接口（无序列也冻 schema）

```text
field: crowding_z
symbol: instrument_id（baostock：sh./sz./bj.）
sign: crowding_z 越高 = 多头拥挤越严重
penalty: λ_crd * Σ_i w_i * max(crowding_z_i, 0)   默认 λ_crd=0.5
missing_policy:
  - 当日无 crowding 序列，或覆盖率 < 权益权重的 50%
  → 当日跳过该项（不填补、不因此失败优化）
schema_frozen: true
status: NO_SERIES_YET
```

---

## 4. ACCEPT 门（60万 ∧ 100万）

须**全部**满足：

1. §2 全部硬约束通过（含 β 硬带、波动带、行业、单名/ADV、市值防杠铃）。  
2. **MDD ≤ 25%**；并**报告** MDD≤15% 变体（不作 v1.0 硬门）。  
3. CAGR **高于**同窗同 AUM 的 **capacity_adv**。  
4. Calmar ≥ min(capacity_adv, B4) 的 Calmar，**或**（CAGR > B4.CAGR 且 MDD 不差于 B4.MDD + 2pp）。  
5. 月胜率必报（v1.0 不设硬下限）。  
6. 软项只记账，**单独**不构成 REJECT。  
7. 回撤降β钩子 **默认关闭**（`BETA_DD_HOOK_FOR_COMBO_ZH.md`）。

对照路径：capacity_adv Book-Smoke X2；B4 `book_smoke_conc_v2_B_B4_50_25_25_topN_{60,100}w_x2`。X2 结论须标「样本内」。

---

## 5. 冻结声明

本文件与 `risk_budget_prereg_v1.json` 中的阈值，均在**未见**组合优化器回测结果之前选定。  
阈值事后变更 = 重新冻结 + **Beta + 主 Agent** 双签。  
Strategy 接线共签（文首栏）是优化器启动的前置条件，与改阈值双签分开。

---

## 6. 机器可读 schema（摘要）

完整 JSON 见 `output/v3/beta_risk_budget_prereg/risk_budget_prereg_v1.json`，顶层键：

```json
{
  "meta": { "cosign", "scope", "benchmark", "frozen_at_et", ... },
  "hard_constraints": {
    "beta_vs_510300", "annualized_vol", "industry_active_sw_l1",
    "single_name_and_adv", "size_antobarbell"
  },
  "soft_risk_terms": {
    "tracking_error_vs_510300", "ledoit_wolf_variance", "turnover_cost",
    "concentration_hhi", "style_value_active", "style_momentum_active",
    "style_size_active_z", "style_quality_lowvol", "crowding"
  },
  "accept_gates": { ... },
  "freeze_statement": "..."
}
```

---

## 7. 相关文档

- `BETA_DD_HOOK_FOR_COMBO_ZH.md`（钩子默认关；LW δ≈0.04）  
- `BETA_BUDGET_MDD25_FOR_COMBO_ZH.md`（MDD25 预算；联签附录）  
- `BETA_B1_SURVIVORSHIP_ZH.md` v1.1（纸面持仓路径≈0；非全场）  
- `audit/ARCH_SURVIVORSHIP_AUDIT_20261014_ZH.md`  
- `QuantLab-MANDATE_V2.json` / `GATE_V3_MDD25_PREREG_ZH.md`

live=false；promotion_approved=false；不触碰小盘下单路径。


---

## A. 与 Strategy OPTIMIZER_V1 DRAFT 对齐（2026-10-14 08:05 ET）

共签回批：`docs/v2/BETA_OPTIMIZER_COSIGN_V1_ZH.md`（**CONDITIONAL_COSIGN**）。

| 项 | 本预注册 | Strategy DRAFT | 正式优化器路径 |
|---|---|---|---|
| \(w_b\) | 行业对 CSI300；β 对 510300 | 中证全指（无权重则市值代理） | 优化器跟 Strategy；纸面报告仍 510300 |
| β HARD | vs 510300 ∈[0.70,1.00] | vs \(w_b\) |β−1|≤0.10 | **两套并存** |
| 行业 | ≤8% vs CSI300；绝对≤25% | ≤2% vs \(w_b\)；绝对≤35% | 优化器 ±2%；纸面袖套仍可 25% |
| 防杠铃 | 分位桶 min(w_small,w_large)≤5% | MidCap \|e\|≤0.30 | 路径 A 双启用或路径 B 证明蕴含 |
| 单名/宽度 | 6% / 30–60 | 1–1.5% / 100–400 | 优化器跟 Strategy |
| λ / ν | 未冻 λ；crowding 接口 | λ=1.0；ν=0.25 | 同量纲标定后锁；否则 ν=0、λ 不冻 |

五点裁决：(1) Σ **ACCEPT**；(2) HARD β/Size/MidCap **CONDITIONAL**；(3) 行业±2% **CONDITIONAL**；(4) 软罚/ν **CONDITIONAL**；(5) λ=1.0 **CONDITIONAL**。


---

## B. Leo D 共签指针（2026-10-14 08:06 ET）· **SUPERSEDED**

- 共签正文：`docs/v2/BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` → **SUPERSEDED**
- PENDING 数字表：`docs/v2/BETA_RISK_BUDGET_LEO_D_PENDING_ZH.md` → 历史
- 旧冲突暂停：`docs/v2/BETA_OPTIMIZER_CONFLICT_RESOLVE_ZH.md`（SUPERSEDED）

## C. CORE_CONC 共签指针（2026-10-14 08:11 ET）

- 共签正文：`docs/v2/BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md` → **CONDITIONAL_COSIGN_CORE_CONC**
- Strategy 源：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（**正文仍含 Leo D 数字**；待改 CORE_CONC；仍 DRAFT，非 FROZEN）
- 升 FROZEN：DRAFT 正文对齐 + Eng λ 标定 → 先跑 Core
