# Beta 对 Strategy OPTIMIZER_V1 DRAFT 共签回批

- **时间**：2026-10-14 08:05 ET  
- **对象**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` + `docs/v2/STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md`  
- **配套**：`docs/v2/BETA_RISK_BUDGET_OPTIMIZER_PREREG_ZH.md` · `output/v3/beta_risk_budget_prereg/risk_budget_prereg_v1.json`  
- **状态**：**CONDITIONAL_COSIGN**（非 FULL_COSIGN）· live=false · promotion_approved=false  
- **原则**：看优化器回测结果之前共签；阈值窥视后改动须 refreeze + Beta+主 Agent 双签  

---

## 总裁决

| # | Strategy 提案 | Beta 裁决 | 一句话 |
|---|---|---|---|
| (1) | Σ V1 = LW + 行业哑元起步 | **ACCEPT** | N≈3000、L=120 纯股票 LW 病态；行业因子+特异风险正确 |
| (2) | HARD：\|β−1\|≤0.10（相对 wb）、线性 Size≤0.30、MidCap/非线性≤0.30 | **CONDITIONAL** | 形式同意硬约束；须双口径 β + 单位定义 + 与 Leo 防杠铃桶锁对齐 + 求解失败降级序 |
| (3) | 申万一相对中证全指 ±2% | **CONDITIONAL** | 方向同意；**无 000985 成分权重**→须市值代理并打标；±2% 相对遗留纸面主动（p95≈15–21% vs CSI300）极紧，可行性风险高 |
| (4) | 软罚 + 拥挤度 ν=0.25 | **CONDITIONAL** | 有把握风格软罚 ACCEPT；ν=0.25 仅在与 α 同量纲标定后；缺失跳过 |
| (5) | λ=1.0 单点 | **CONDITIONAL** | 仅 α 与 \(\lambda(w-w_b)'\Sigma(w-w_b)\) 同量纲标定文档化后可冻；否则不得写死 1.0 |

**整体共签栏**：**CONDITIONAL_COSIGN**。Strategy 确认文末「待确认项」并补齐标定/数据代理后，可升 **FULL_COSIGN**（仍须 Leo/主 Agent 改 DRAFT→FROZEN）。

---

## 双口径 β（强制写清，避免混用）

| 用途 | 基准 | 约束/报告 |
|---|---|---|
| **优化器硬约束** | \(w_b\) = **中证全指**（可交易池内 renormalize；权重缺失时用流通市值代理并打标） | \(\lvert\beta(w,w_b)-1\rvert\le 0.10\) **HARD** |
| **纸面轨对照 / Mandate 报告** | **510300** | 仍报 vs 510300 的 β、跟踪误差、波动；Beta 风险预算预注册带 **[0.70, 1.00]** 继续作纸面 ACCEPT/对照门（见差异表） |
| **禁止** | 用相对 \(w_b\) 的 β 替代 Mandate/纸面 vs 510300 报告，或反过来用 510300 β 充当优化器硬约束而不声明 | — |

依据：Mandate / 既有 `BETA_DD_HOOK` / `BETA_BUDGET_MDD25` 全部相对 510300；Strategy DRAFT §3.2 选定中证全指为 \(w_b\)——两套口径并存，共签承认，不合并成一套。

---

## (1) Σ V1：LW + 行业哑元 — **ACCEPT**

**可实现性**
- 仓库已有 `quantlab/strategy/portfolio.py::ledoit_wolf_cov` 与 `output/v3/beta_dd_hook/beta_dd_hook.py::lw`（袖套级 δ≈0.04）。
- N≈3000、L=120 时，**纯个股样本协方差秩亏且噪声主导**：V1 改为 **申万一级行业因子 + 对角特异风险**（特异 = LW 对角或 60 日波动）是正确起步；与 DRAFT §3.3 一致。

**必须写入实现的风险注记**
1. **行业 PIT**：成员用 `data/v2/sw_pit/industry_members_sw_l1_pit.parquet` asof；未知行业单独因子或并入「其他」，权重进 35% 绝对兜底监控。  
2. **停牌/缺失填 0**（DRAFT §3.3）：会压低相关与特异波动、低估同停牌簇的共同冲击 → 报告须披露「填 0 偏差」；**不得**用未来 K 线回填。  
3. 演进真实 Barra 前，不把 Σ 精度当晋级证据。

**失败条件**：若实现退回「全池个股稠密 LW 无行业结构」→ 本条共签 **作废**，须重签。

---

## (2) HARD：β / 线性 Size / MidCap — **CONDITIONAL**

### 2.1 β：\(\lvert\beta_{w,w_b}-1\rvert\le 0.10\) — 形式 **ACCEPT**，口径 **CONDITIONAL**

- 优化器内：**同意 HARD**（相对 \(w_b\)）。实现建议：60 日滚动、PIT、对 \(r_b=\sum_i w_{b,i} r_i\)（代理基准组合收益）。  
- 纸面对照：仍报 vs **510300**；与 Leo/Mandate 带 [0.70, 1.00] **并行不替代**。  
- **数据**：中证全指 **日线有**（`index_daily/000985_CSI.parquet`），**成分权重无**（`index_weight` 仅 000300/000905/000852）。V1 必须用「可交易池流通市值加权」作 \(w_b\) 并打标 `wb_proxy=float_mktcap`；正式成分权到位后 dated 修订，不静默切换。

### 2.2 线性 Size \(\lvert e_{\mathrm{size}}\rvert\le 0.30\) — **CONDITIONAL**

- 同意 **HARD**。  
- **待确认单位**：须写死 \(e_{\mathrm{size}}=(w-w_b)'z_{\ln\mathrm{mcap}}\)（截面 z）还是回归因子载荷。Beta 建议：**活跃暴露 = 组合加权 z − 基准加权 z**，单位为截面标准差；0.30 ≈ 0.3σ，与纸面 capacity_adv active size z≈**+0.86**（vs CSI300，X2 基线）相比偏紧——优化器相对全指 \(w_b\) 后预期更小，但仍可能绑死 α。  
- 失败：单位未定义就开跑 → 本条视为未共签。

### 2.3 MidCap / 非线性 Size \(\lvert e_{\mathrm{mid}}\rvert\le 0.30\) — **CONDITIONAL**（对齐 Leo 防杠铃）

- 同意作为 **HARD 防杠铃**，满足 Leo 07:58「非线性市值硬锁」。  
- Strategy 用 \((\ln\mathrm{mcap}-\mu)^2\) 暴露；Beta 预注册另有 **分位桶硬锁** \(\min(w_{\mathrm{small}},w_{\mathrm{large}})\le 0.05\)（P20/P80）。  
- **共签要求（二者任一正式路径须满足）**：  
  - **路径 A（推荐）**：同时启用 MidCap 暴露硬盒 **与** 分位桶 `min(w_small,w_large)≤0.05`（桶锁防「两端堆、中间空」更直观）；或  
  - **路径 B**：仅 MidCap 暴露，但须在预注册证明 \(\lvert e_{\mathrm{mid}}\rvert\le 0.30\) **蕴含** 不允许 \(w_{\mathrm{small}},w_{\mathrm{large}}\) 同时 >5%（用 X2 可交易池做可行域烟测，**看优化器收益之前**）。  
- 未选路径不得 FROZEN。

### 2.4 联合可行性与求解失败降级序（**不得松硬约束当正式**）

Size + MidCap + 行业 ±2% + β 带 **同时 HARD** 时，可行域可能为空（尤其 α 强行业偏斜时）。

**降级顺序（写死；每步打标；正式 NAV 禁止松 HARD）**：

1. 软罚 λ / μ / ν → **临时置 0**（仅当步求解；日志 `degrade=soft_zero`）。  
2. 域预算偏离 ±3pp → **压回 0**（贴 \(w_b\) 域份额）。  
3. 权益总仓按比例降仓 → 现金（保持相对权重形状），直到 β/行业/Size 可行。  
4. 放宽成交死区（增大 \(\tau_{\mathrm{lo}}\)）降低换手压力；**不**改 HARD 盒。  
5. 仍不可行 → 该再平衡日 **沿用上期权重** 或 **全现金**，标记 `optimize_status=INFEASIBLE`；**禁止**把「临时把行业改为 ±5% / Size 改为 0.50」的解记入正式臂。  
6. 若日历月内 INFEASIBLE ≥2 次 → 停跑升级主 Agent；阈值修订须 dated + 双签，**另计试验**。

---

## (3) 申万一级相对中证全指 ±2% — **CONDITIONAL**

**方向**：同意相对 \(w_b\) 主动盒为主约束（替代 HI_LIQ absolute 25% 主路径）；absolute ≤35% 兜底可接受。

**数据阻塞**：无 000985 成分权重 → V1 行业基准 = 可交易池内按流通市值加权的申万一权重，标签 `industry_wb_proxy=float_mktcap_hiliq`。Data 补全指权重前不得宣称「相对中证全指官方权重」。

**可行性（用既有基线，非优化器窥视）**  
纸面 capacity_adv / B4 相对 **CSI300** 的 max\|active\|：mean≈9.5–14%、**p95≈14.7–20.7%**（`baseline_exposures_x2.json`）。±2% 比遗留暴露紧约一个数量级——对优化器是强中性约束，**可接受为范式选择**，但预期：  
- 求解更易走降级序 §2.4；  
- 慢 α 的行业溢价会被大幅削掉。  

**共签条件**
1. 代理基准打标；官方权重到位后修订。  
2. 敏感度仅报告：±2%（正式）/ ±3% / ±5%（**不得**用 ±5% 结果当正式 ACCEPT）。  
3. 与 Beta 预注册旧值「相对 CSI300 ≤8%」的关系：见差异表——优化器路径以 Strategy ±2% vs \(w_b\) 为准；纸面遗留对照仍可报 vs CSI300/510300。

**失败条件**：静默用 CSI300 行业权冒充全指、或松到 ±5% 仍标正式 → 共签作废。

---

## (4) 软罚与拥挤度 ν=0.25 — **CONDITIONAL**

| 项 | 裁决 |
|---|---|
| 自信风格（价值/质量等）走 **软罚**，β/Size/行业走 **HARD** | **ACCEPT**（对齐 Leo：有把握软、核心硬） |
| Quality/LowVol 把握不足 | 默认 μ=0；启用须 dated（与 Beta 预注册一致） |
| 拥挤度接口 + 缺失跳过 | **ACCEPT** schema；代理 \(c_i\) 可审计（成交额分位×重叠） |
| \(\nu=0.25\) | **CONDITIONAL**：须与 α 同量纲标定（见 §5）；未标定前 \(\nu=0\) 并打标「拥挤度未启用」——DRAFT 已允许，共签确认 |

---

## (5) λ=1.0 单点 — **CONDITIONAL**

- **仅当**存在书面标定：例如先把 \(\alpha_{\mathrm{res}}\) 缩放到「预期日超额同量级」，再使典型 \(\lvert w-w_b\rvert\) 下 \(\lambda(w-w_b)'\Sigma(w-w_b)\) 与 \(w'\alpha\) 同数量级，然后锁 λ=1.0。  
- 标定产物建议：`output/strategy_optimizer/calib_lambda_scale.json`（**首跑结果前**落盘，可与 TC 标定同批）。  
- **未标定就冻 λ=1.0** → Beta 对本条 **REJECT**（避免无量纲单点变成隐性网格自由度）。  
- 不做 {0.5,1,2} 网格：同意（省试验数）。

---

## 与 Leo 07:58 四项对齐检查

| Leo 要求 | Strategy DRAFT | Beta 共签 |
|---|---|---|
| 非线性市值硬锁（防杠铃） | MidCap HARD ≤0.30 | **CONDITIONAL**：须路径 A/B 与分位桶锁对齐 |
| β 硬约束 | \|β−1\|≤0.10 vs wb | **ACCEPT** 优化器侧；纸面仍报 510300 |
| 有把握风格软罚 | Pen_soft | **ACCEPT** |
| 拥挤度接口 | crowd_penalty / ν | **ACCEPT** 接口；ν 标定后 |

---

## 与 `BETA_RISK_BUDGET_OPTIMIZER_PREREG` 差异表

| 项 | Beta 预注册 v1（08:00） | Strategy OPTIMIZER_V1 DRAFT | 共签后以谁为准 |
|---|---|---|---|
| 优化基准 \(w_b\) | 行业对 CSI300；β 对 510300 | 中证全指（代理市值） | **优化器：Strategy \(w_b\)**；**纸面报告：510300** |
| β HARD | vs 510300 ∈[0.70,1.00] | vs \(w_b\) \|β−1\|≤0.10 | **两套都保留**（用途不同） |
| 波动带 | [12%,18%] HARD | 未单列 HARD（软/风险项） | Beta 带作纸面/验收并报；优化器可不另加硬波动盒 |
| 行业主动 | ≤8% vs CSI300；绝对≤25% | ≤2% vs \(w_b\)；绝对≤35% | **优化器正式：±2% vs \(w_b\)**；绝对兜底 35%；纸面 HI_LIQ 25% 仍约束纸面袖套 |
| 单名 / 宽度 | ≤6%；30–60 名 | 1.0%/1.5%；100–400 名 | **优化器：Strategy**（范式已变）；纸面遗留轨不变 |
| 防杠铃 | 分位桶 min≤5% | MidCap 暴露 ≤0.30 | **CONDITIONAL 双路径**（上文） |
| ADV 参与 | ≤1% ADV20 | ≤0.6% ADV20 | **优化器：0.6%**（更严） |
| λ / ν | 未冻优化器 λ；crowding λ_crd=0.5 | λ=1.0；ν=0.25 | **标定后** Strategy 单点；未标定则 ν=0、λ 不冻 |
| DD 钩子 | 默认关 | 未启用为硬闸 | 保持默认关 |

Beta 预注册文末已改为指向本共签；JSON `meta.cosign.strategy_wiring` → `CONDITIONAL_COSIGN`。

---

## 待 Strategy 确认（升 FULL_COSIGN 前）

1. 接受 **双口径 β**（优化器 vs \(w_b\)；纸面/Mandate vs 510300）。  
2. 确认 \(w_b\) / 行业基准 V1 = **流通市值代理**并打标；Data 全指权重为后续修订。  
3. 选定防杠铃 **路径 A 或 B**，并在 FROZEN 前做可行域烟测（**不看收益**）。  
4. 落盘 **α–风险同量纲标定** 后再锁 λ=1.0、ν=0.25。  
5. 写入求解失败 **降级序 §2.4**（正式结果不松 HARD）。  
6. Arch 对四闸/拥挤度代理可审计性并行共签（Beta 不替代 Arch）。

---

## Beta 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **CONDITIONAL_COSIGN** |
| Beta 签字 | QuantLab Beta · 2026-10-14 08:05 ET |
| Strategy 接线确认 | **PENDING** |
| 升 FULL 条件 | 上文 1–5 项书面确认 + 标定文件路径写入 DRAFT 修订记录 |
| live / promotion | false / false |

