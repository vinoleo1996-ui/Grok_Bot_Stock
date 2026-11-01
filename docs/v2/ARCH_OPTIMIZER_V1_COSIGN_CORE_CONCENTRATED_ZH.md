# Arch 终签：OPTIMIZER_V1 预注册草稿（Leo ≈08:09 浓缩 Core）

- **时间**：2026-10-14 ≈08:14 ET（Arch）
- **标的**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`
  - 文内修订：**≈08:13 ET** Leo Core-concentrate 最终改写（横幅 + §0/§3.4/§3.5/§5）
  - 文件 mtime：审计时已含浓缩条款（早先 ≈08:09 磁盘稿仍为 Leo D → 曾拟拒签；**以本终签重读的 ≈08:13 稿为准**）
- **对照**：Leo ≈08:09 浓缩 Core（主 Agent 转发）；`ARCH_OPTIMIZER_V1_COSIGN_LEO_D_ZH.md`（**数值 SUPERSEDED**）；`ARCH_INDUSTRIAL_PILLARS_SPEC_ZH.md`
- **约束**：本文只新增/覆盖文档；**不改** FROZEN_CONFIG / 纸面轨；**禁开跑**优化器回测 / book-smoke；`live=false`

---

## 0. 终签结论

### **有条件通过（CONDITIONAL_PASS · Leo Core-concentrate）**

**一句话**：四闸 + 两步截断按 Leo ≈08:09 浓缩 Core **完整性通过**；旧 LEO_D 宽度/单票/行业/Size 终签数值 **SUPERSEDED**；**不得 FROZEN / 不得开跑**，直至 Beta 按浓缩重签 + Eng λ（NEW HARD）密封窗产物 + Leo/主 Agent 确认。

---

## 1. Leo ≈08:09 浓缩 Core 强制口径打勾

| # | Leo 浓缩 Core | 当前 DRAFT（≈08:13） | 判定 |
|---|---|---|---|
| 1 | Core \(N_{\mathrm{eff}}\) **20–30** | §0 / §3.4 / §3.5 | ✅ |
| 2 | 单票 **5% / 6%**（100万/60万） | §3.4 | ✅ |
| 3 | **两步截断重解** | §3.5 (a)(b)(c)+失败序 | ✅ |
| 4 | 行业 vs \(w_b\) **±8%**；绝对 ≤**20%** | §3.4 | ✅ |
| 5 | Size/MidCap **±0.35σ + Slack** | §3.4 HARD + Slack 通道（仅 Size/MidCap） | ✅ |
| 6 | Core **对标 capacity_adv**；Full **后对 B4** | §0 #5 / §5 | ✅ |
| 7 | 保留 **L1-only** | §3.1 / §3.7 | ✅ |
| 8 | 保留 **HI_LIQ 池内 \(w_b\)** | §1.3 | ✅ |
| 9 | 旧 LEO_D 宽度/单票/行业数值**作废** | 横幅 + §0 + 附录 A SUPERSEDED | ✅ |

**本表总评**：9/9 ✅。

---

## 2. 「两步截断 + Neff20–30 集中」是否违背工业支柱意图

### **明确判断：不违背。**

| 层 | 说明 |
|---|---|
| **支柱①意图** | 可交易池 + 优化器合成，非 Top-N 裸排——Core 仍是全池优化再截断，不是「直接取名次前 25」。 |
| **支柱③意图** | MidCap/Size 硬盒 + 行业盒 + Slack 防无解；绝对行业 ≤20% 防集中踩踏。 |
| **支柱④意图** | 优化内仍仅 L1；引擎 strategy_v1 终判冲击/按手/涨跌停；两步是**支撑集压缩**，不是恢复 3/2 或外部双阈。 |
| **对标** | Neff20–30 显式对齐 capacity_adv Top-25 + 整手，符合 Leo 浓缩意图。 |

3/2 与外部双阈仍可作 **V1.1+/对照臂**，不得回贴 Core 选参。

---

## 3. 四闸 + 两步流程完整性

### (1) UNIVERSE

| 子项 | 判定 |
|---|---|
| HI_LIQ_V1.1；不改冻掩码；ADV≥1亿；无市值剔除 | ✅ |
| \(w_b\)=池内流通市值加权（非中证全指） | ✅ |
| 分域壳仅 Full；Core=全池优化+两步截断；真分域 α=V1.1 | ✅ |
| MidCap Path A（±0.35σ + 分位桶） | ✅ |
| 双轨：求解=HI_LIQ；FULLA 仅诊断；裸 FULLA 不进纸面 | ✅ |

**本项总评**：通过。

### (2) FACTORS

| 子项 | 判定 |
|---|---|
| 慢残差 α 进主目标；快门卫仅 Full；禁止名次当 α | ✅ |
| V1：行业+Size+MidCap 截面残差；库正交=V1.1 | ✅ |
| 慢 α 主源=capacity_adv 全池向量 | ✅ |

**本项总评**：通过。

### (3) CONSTRAINTS

| 子项 | 判定 |
|---|---|
| HARD：Size/MidCap ±0.35σ、行业 ±8%/绝对≤20%、单票 5%/6%、Neff 20–30、β±0.10、杠杆/禁空 | ✅ |
| Slack：仅 Size/MidCap 可 dated 临时放宽；禁静默松行业/单票/Neff/β | ✅ |
| SOFT：风格二次罚；拥挤度接口；缺失 ν=0 | ✅ |
| Σ=申万一级+对角特异；双口径纸面 β vs 510300 | ✅ |
| INFEASIBLE 降级序 | ✅ |

**本项总评**：通过（β/Slack 数值仍须 **Beta 重签确认**，不阻塞本轮完整性终签，阻塞 FROZEN）。

### (4) EXECUTION

| 子项 | 判定 |
|---|---|
| 优化内 TC=仅 L1；已删 3/2、外部双阈、staged builds | ✅ |
| 引擎 strategy_v1 终判；60/100万 λ_turn 分标 | ✅ 闸门；**数值 BLOCKING** |
| 科创板 lot=200；普通 100 | ✅ |

**本项总评**：通过。

### (5) 两步截断重解

| 子项 | 判定 |
|---|---|
| (a) 全池初解 HARD+SOFT+L1 | ✅ |
| (b) 支撑集前 20–30 且单票 ≥1.5–2.0% | ✅ |
| (c) 支撑集二次重解 + 整手 | ✅ |
| 失败 → Slack/降级；禁偷偷 Neff>30 不打标 | ✅ |

**本项总评**：通过。  
**残余微缺口（不改拒签）**：支撑集排序准则写「\(|w^{(0)}|\) **或** α 贡献」——实现前须 **单点写死** 一种主准则（建议默认 \(|w^{(0)}|\)，α 贡献仅作披露对照）；单票下限 **1.5–2.0%** 建议密封窗后钉死单点。

---

## 4. 与旧终签关系

| 文档 | 状态 |
|---|---|
| `ARCH_OPTIMIZER_V1_COSIGN_LEO_D_ZH.md` | **数值 SUPERSEDED**（L1 / 池内 \(w_b\) / 四闸骨架仍复用） |
| `ARCH_OPTIMIZER_V1_COSIGN_ZH.md` | 仍作废 |
| 本文 | **现行 Arch 终签依据（浓缩 Core）** |

---

## 5. 残余缺口（FROZEN / 开跑前置）

| ID | 缺口 | 谁 | 阻塞 |
|---|---|---|---|
| G1 | Beta 按 Core-concentrate **重签**（Neff/单票/行业/Size+Slack/两步/β） | Beta | FROZEN |
| G2 | Eng \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 密封窗标定（**NEW HARD + 两步**）；旧 HARD 产物作废 | Eng + Strategy | FROZEN |
| G3 | 支撑集主准则与单票下限单点写死（实现前） | Strategy | 实现/烟测 |
| G4 | ν=0 或同量纲标定 | Beta + Strategy | Full |
| G5 | Arch S1 退市清算披露 | Eng + Data | 宽池披露 |
| G6 | Leo/主 Agent 过关 | Leo | FROZEN |

**明确**：本终签 **不授权** FROZEN、**不授权**开跑。

---

## 6. Arch 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **CONDITIONAL_PASS（Leo Core-concentrate 四闸+两步完整性）** |
| 两步截断+Neff20–30 | **不违工业支柱意图** |
| 旧 LEO_D 终签数值 | **SUPERSEDED** |
| Arch 签字 | QuantLab Arch · 2026-10-14 ≈08:14 ET |
| FROZEN / 开跑 | **禁止**（直至 G1–G2 + Leo 确认） |
| live / promotion | false / false |

---

## 7. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:12 ET | 初读磁盘稿仍为 Leo D → 拟拒签「草稿未完成」。 |
| 2026-10-14 ≈08:14 ET | Strategy ≈08:13 改稿到位 → **改为有条件通过**；打勾表 + 残余缺口；禁开跑保留。 |
