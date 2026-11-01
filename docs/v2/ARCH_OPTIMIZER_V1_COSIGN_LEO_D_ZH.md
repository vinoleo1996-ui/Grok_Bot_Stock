# Arch 终签：OPTIMIZER_V1 预注册草稿（Leo D 口径）

- **时间**：2026-10-14 ≈08:10 ET（Arch）
- **标的**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（≈08:08 ET 按 Leo D 改写，**DRAFT 非 FROZEN**）
- **附录已读**：`docs/v2/STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md`
- **对照**：Leo **选项 D**（≈08:03 ET，主 Agent 转发）；`ARCH_INDUSTRIAL_PILLARS_SPEC_ZH.md`；`BETA_OPTIMIZER_COSIGN_V1_ZH.md`（旧数值）；`BETA_OPTIMIZER_CONFLICT_RESOLVE_ZH.md`（PAUSE/SUPERSEDED）
- **作废**：`ARCH_OPTIMIZER_V1_COSIGN_ZH.md`（≈08:03）全部旧数值与 EXECUTION「双阈+3/2」打勾——**以本文为准**
- **约束**：本文只新增文档；**不改** FROZEN_CONFIG / 纸面轨；**禁开跑**优化器回测 / book-smoke；`live=false`

---

## 0. 终签结论

### **有条件通过（conditional pass · Leo D）**

四闸按 **Leo D** 改写后**完整性通过**；删除 3/2 冲击与外部双阈**不违背**工业支柱意图（见 §2）。  
**不得**就此改标 **FROZEN**，**不得**开跑优化器回测，直至 §4 残余缺口关闭（首要：Beta 按 D 重签 + 密封窗 λ 标定产物）。

**一句话**：Gateway 已对齐 Leo D（HI_LIQ 池内 \(w_b\)、仅 L1、Core/Full、V1=单慢α+域壳）；旧 Arch/Beta 数值共签作废；FROZEN 仍阻塞于 Beta 重签与 λ 标定。

---

## 1. Leo D 强制口径打勾

| # | Leo D | DRAFT | 判定 |
|---|---|---|---|
| 1 | 池=HI_LIQ；**不用**中证全指作 \(w_b\) | §1.3：`wb_proxy=float_mktcap_hiliq`；明确不用 000985/CSI300 官方权 | ✅ |
| 1b | Size/MidCap vs \(w_b\) ≤ ±0.25σ | §3.4 HARD；Path A（连续 MidCap + 分位桶） | ✅ |
| 2 | 单票约 2.5–3%；持股约 40–70；行业 ±5% | 100万 2.5% / 60万 3.0%；\(N_{\mathrm{eff}}\) 40–70；行业 ±5%；绝对兜底 35% | ✅ |
| 3 | **取消** 3/2 与外部双阈；仅 L1 | §3.1 / §3.6：\(\mathrm{TC}=\lambda_{\mathrm{turn}}\|w-w_0\|_1\)；引擎 strategy_v1 终判 | ✅ |
| 4 | λ 样本内标定后再进 X2；Core vs Full | §4 BLOCKING；§5 Core/Full 写死 | ✅ |
| 另 | V1=单慢α+域预算壳；库正交→V1.1；双轨=HI_LIQ 求解 / FULLA 仅诊断 | §1.4 / §2.2 / 文首双轨句 | ✅ |

---

## 2. 「删 3/2 / 双阈」是否违背工业支柱意图

### **明确判断：不违背。**

| 层 | 说明 |
|---|---|
| **支柱④意图** | 控换手、控冲击、避免「掉名即卖」与大单砸盘——见 `ARCH_INDUSTRIAL_PILLARS_SPEC_ZH.md` §1④。 |
| **Leo D 简化** | 优化器内仅保留 L1（\(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)），数学上即一阶无交易死区的凸代理；冲击与按手/涨跌停/participation 仍由 **引擎 strategy_v1** 终判（含既有 sqrt 冲击）。 |
| **3/2 + 外部双阈** | **不是** V1 硬前提；标为 **V1.1+ / Full 消融对照**（或 Eng 侧敏感性臂），用于度量「相对纯 L1」的边际，**不得**回贴进 Core 选参。 |
| **旧共签** | 旧 Arch COSIGN 把双阈+3/2 当 EXECUTION 必选项——**作废**；以 Leo D + 本判断为准。 |

因此：删优化器规格层的 3/2 与外部双阈 = **V1 简化代理**，不构成对工业支柱的否决。

---

## 3. 四闸打勾（Leo D）

### (1) UNIVERSE：HI_LIQ + 分域壳 + MidCap 硬锁

| 子项 | 判定 |
|---|---|
| HI_LIQ_V1.1 方案 A；不改冻掩码；ADV≥1亿；无市值剔除 | ✅ |
| \(w_b\)=池内流通市值加权（非中证全指） | ✅ |
| 分域 D1/D2/D3 + 域预算 ±3pp（仅 Full）；V1=单慢α+域壳，真分域独立α=V1.1 | ✅（已知相对「分域独立建模」降级，已写死） |
| MidCap Path A（连续暴露 ±0.25σ + 分位桶） | ✅ |
| 双轨：求解=HI_LIQ；FULLA 仅诊断；裸 FULLA 不进纸面 | ✅ |

**本项总评**：通过。

### (2) FACTORS：慢底仓 / 快门卫

| 子项 | 判定 |
|---|---|
| 慢残差 α 进主目标；快因子仅门卫（V1 默认） | ✅ |
| V1：行业+Size+MidCap 截面残差；禁止名次当 α | ✅ |
| 对已有因子库施密特正交 = **V1.1**（非 V1） | ✅（按 Leo/Strategy 约定延期） |

**本项总评**：通过。

### (3) CONSTRAINTS：HARD / SOFT + 拥挤度

| 子项 | 判定 |
|---|---|
| HARD：Size/MidCap ±0.25σ、行业 ±5%、单票 2.5%/3.0%、宽度 40–70、杠杆/禁空 | ✅ |
| SOFT：自信风格二次罚；拥挤度接口；缺失 ν=0 打标 | ✅ |
| Σ V1=申万一级行业因子+对角特异；禁稠密 LW | ✅ |
| 双口径 β：优化器 vs \(w_b\)；纸面报 vs 510300 | ✅ 结构 |
| 优化器 β 带宽（提案 ±0.15 vs 新 \(w_b\)） | ⚠️ **待 Beta 按 D 重签**（旧 ±0.10 vs 全指作废） |
| INFEASIBLE 降级序（正式永不松 HARD） | ✅ |

**本项总评**：闸门通过；**β 带宽数值**为 Beta 重签项（不阻塞本轮四闸完整性终签，阻塞 FROZEN）。

### (4) EXECUTION：仅 L1 · 60/100万分标

| 子项 | 判定 |
|---|---|
| 优化内 TC = 仅 L1；已删 3/2、外部双阈、staged builds（优化器层） | ✅（对齐 Leo D） |
| 引擎 strategy_v1 终判成本/参与率/按手/涨跌停 | ✅ |
| \(\lambda_{\mathrm{turn}}\) 60万/100万分别密封窗标定（对齐 B4 换手量级） | ✅ 闸门写死；**数值 BLOCKING** |
| 单边换手硬帽 ≤40% NAV / 再平衡 | ✅ |

**本项总评**：通过（简化代理已确认不违支柱）。

---

## 4. 与 Beta 旧共签关系

| 来源 | 状态 | 说明 |
|---|---|---|
| `BETA_OPTIMIZER_COSIGN_V1_ZH.md`（08:05） | **数值作废** | 中证全指 \(w_b\)、行业 ±2%、单票 1.0%/1.5%、宽度 100–400、ν=0.25、λ=1.0 盲冻条件 —— **全部被 Leo D 覆盖** |
| `BETA_OPTIMIZER_CONFLICT_RESOLVE_ZH.md`（08:04） | **PAUSE/SUPERSEDED** | 与本终签一致：等 Strategy 按 D 落笔后再重签 |
| 结构仍可复用 | 保留 | Σ=行业+特异；Path A；降级序；双口径纸面 β vs 510300；crowd missing→0；HI_LIQ 双轨 |

**Arch 不替代 Beta 重签。** Strategy 已按 D 改写后，请 Beta 对新表（\(w_b\)、±0.25σ、±5%、单票/宽度、L1-only、β 带宽提案）出 **Leo D 共签文**。

---

## 5. 残余缺口（FROZEN / 开跑前置）

| ID | 缺口 | 谁 | 阻塞 |
|---|---|---|---|
| G1 | Beta 按 Leo D **重签**（含 β 带宽 vs 新 \(w_b\)） | Beta | FROZEN |
| G2 | \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 密封窗标定文件落盘（不看 X2 收益选参） | Eng 初值 + Strategy 写死 | FROZEN |
| G3 | ν 同量纲标定或保持 0 + `crowd=off` | Beta + Strategy | Full 臂 |
| G4 | Eng 退市 terminal（Arch S1）落地前报告持续打标；不宣称无幸存者问题 | Eng + Data | 宽池披露 |
| G5 | 真分域独立慢 α、因子库正交 | Alpha → V1.1 dated | 非 V1 阻塞 |
| G6 | 3/2 / 外部双阈若做消融 | Strategy + Eng → V1.1+/对照臂 | 非 V1 阻塞 |

**明确**：本终签 **不授权** FROZEN、**不授权**开跑。

---

## 6. Arch 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **CONDITIONAL_PASS（Leo D 四闸完整性）** |
| 删 3/2·双阈 | **不违工业支柱意图**（L1=简化代理；3/2/双阈→V1.1+/Full 对照） |
| 旧 `ARCH_OPTIMIZER_V1_COSIGN_ZH.md` | **作废** |
| Arch 签字 | QuantLab Arch · 2026-10-14 ≈08:10 ET |
| FROZEN / 开跑 | **禁止**（直至 G1–G2 关闭 + Leo/主 Agent 确认） |
| live / promotion | false / false |

---

## 7. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:10 ET | Leo D 终签初稿：有条件通过；四闸打勾；3/2/双阈删除判决；Beta 旧数值覆盖说明。 |
