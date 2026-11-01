# Arch 文档终签：OPTIMIZER Core 冻规格（DOC_FREEZE_COSIGN）

- **时间**：2026-10-14 ≈08:21 ET（Arch）
- **标的**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（修订 ≈08:20 ET：双口径+月末+stretch 成本+Core 禁 LLM/防守垫）
- **对照**：
  - `ARCH_OPTIMIZER_V1_COSIGN_CORE_CONCENTRATED_ZH.md`（≈08:14 浓缩有条件通过；数值骨架仍有效）
  - Leo ≈08:09 Core-concentrate；挑战补丁（Arch ≈08:18/08:20 拍板）
  - `STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md`（双口径对标句）
- **约束**：本文只新增文档 / TEAM_STATE / ql_bus；**不改** FROZEN_CONFIG / 纸面轨；**不授权开跑**；`live=false`

---

## 0. 终签结论

### **文档终签通过（DOC_FREEZE_COSIGN_PASS）**

**一句话**：PREREG ≈08:20 已对齐浓缩 Core + 挑战双口径补丁，规格层可冻；**FROZEN / 开跑仍须 Eng λ（NEW HARD）密封窗产物 + Leo/主 Agent 过关**——本签**不**把状态机升为 FROZEN，**不**授权优化器回测。

| 层 | 结论 |
|---|---|
| 文档 / 四闸+两步+双口径完整性 | **通过** |
| 状态机 `DRAFT` → `FROZEN` | **仍阻塞**（Eng λ + Leo/主 Agent） |
| 开跑 / book-smoke | **禁止** |
| 纸面 FROZEN_CONFIG / capacity_adv / B4 / S6 | **不动** |

旧 `ARCH_OPTIMIZER_V1_COSIGN_CORE_CONCENTRATED_ZH.md` 的「有条件通过」在**规格完整性**上被本文 **升级为文档终签通过**；其中 G1（Beta 浓缩重签）已由 Beta `CONDITIONAL_COSIGN_CORE_CONC` 覆盖；G3（支撑集主准则）已在 PREREG §3.5 写死 `|w^{(0)}|`。残余阻塞仅剩 **Eng λ + Leo**。

---

## 1. 检查清单（挑战补丁 + 浓缩参数）

### 1.1 挑战补丁（必须）

| # | 要求 | PREREG 落点 | 判定 |
|---|---|---|---|
| C1 | 双口径① **纯股票腿 100%** | §5.1 | ✅ |
| C2 | 双口径② **同挂 20% 510300（80/20）**；**主结论用②** 对标 capacity_adv | §5.1 规则 2；§0 #5 | ✅ |
| C3 | **禁止**满仓 HI_LIQ / 取消 510300 单稿当对标 | §5.1 开篇 + 规则 | ✅ |
| C4 | 再平衡 **写死月末**（不改周频） | §3.8 | ✅ |
| C5 | 成本 ≤1.3%/AUM = **stretch 观察**，非硬门 | §3.8 | ✅ |
| C6 | **Stage1 纸面底仓不动** | §5.1 规则 3；横幅 | ✅ |
| C7 | Core **禁** LLM 权重 / 防守垫 ETF | §3.8；§5 Core 行；§7 | ✅ |
| C8 | Full↔B4 / 事件门卫 **延后**；冻后先只跑 Core | §5；§0 #5 | ✅ |

**本表**：8/8 ✅。

### 1.2 浓缩 Core 参数（Leo ≈08:09）

| # | 要求 | PREREG 落点 | 判定 |
|---|---|---|---|
| P1 | Neff **20–30** | §0 / §3.4 / §3.5 | ✅ |
| P2 | 单票 **100万 5.0% / 60万 6.0%** | §3.4 | ✅ |
| P3 | **两步截断重解** + 整手（科创 200） | §3.5 | ✅ |
| P4 | 行业相对 \(w_b\) **±8%**；绝对 **≤20%** | §3.4 | ✅ |
| P5 | Size/MidCap **±0.35σ** + Slack（≤0.05σ；行业相对 ≤1pp） | §3.4 | ✅ |
| P6 | **L1-only**（无 3/2、无外部双阈） | §3.1 / §3.7 | ✅ |
| P7 | \(w_b\)=池内流通市值加权（非中证全指） | §1.3 | ✅ |
| P8 | 支撑集主准则写死 `|w^{(0)}|`；单票下限暂定 2.0% | §3.5 (b) | ✅ |

**本表**：8/8 ✅。

### 1.3 四闸完整性（摘要）

| 闸 | 判定 | 备注 |
|---|---|---|
| (1) UNIVERSE | ✅ | HI_LIQ_V1.1；双轨；Core 无域预算；MidCap Path A |
| (2) FACTORS | ✅ | 慢残差 α；禁名次当 α；快门卫仅 Full；库正交=V1.1 |
| (3) CONSTRAINTS | ✅ | HARD+Slack 上限写死；Σ=行业+特异；β±0.10 vs \(w_b\)；降级序 |
| (4) EXECUTION | ✅ | 仅 L1；引擎 strategy_v1 终判；月末再平衡；60/100万分标 |
| (5) 两步流程 | ✅ | 初解→支撑集 20–30→重解→整手；失败禁静默扩 Neff |

---

## 2. 与工业支柱意图

| 问 | 答 |
|---|---|
| 删 3/2 + 外部双阈、改 L1-only？ | **不违**支柱④简化意图；完整冲击留 Full/对照臂 |
| Neff20–30 + 两步截断？ | **不违**支柱①（仍全池优化再截断，非 Top-N 裸排） |
| 双口径对标？ | **强化**控制变量；避免 100% 股票 vs 80% 股票回撤假象 |

---

## 3. FROZEN / 开跑前置（仍 BLOCKING）

| ID | 项 | 谁 | 状态 |
|---|---|---|---|
| F1 | Eng \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 密封窗标定（**NEW HARD + 两步**）；产物非 FAILED/null | Eng + Strategy | **BLOCKING** |
| F2 | Leo / 主 Agent 明示过关，状态机升 FROZEN | Leo / 主 Agent | **BLOCKING** |
| F3 | Beta `CONDITIONAL_COSIGN_CORE_CONC` | Beta | 已有（规格层） |
| F4 | 单票下限 2.0% 密封窗后钉单点 | Strategy + Eng | 实现前钉；不阻塞本轮文档终签 |
| F5 | Arch S1 退市清算披露 | Eng + Data | 宽池披露；不阻塞 Core 文档冻 |

**明确**：

1. 本签 = **文档终签通过**（规格可冻）。
2. **不等于** `FROZEN` 状态机翻转。
3. **不等于**授权开跑 / book-smoke / 改纸面。
4. F1+F2 齐备后，由 Strategy 升 FROZEN，再按 RUNBOOK 只跑 Core。

---

## 4. Arch 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **DOC_FREEZE_COSIGN_PASS（文档终签通过）** |
| 规格完整性 | 挑战补丁 8/8 + 浓缩参数 8/8 + 四闸/两步 ✅ |
| FROZEN / 开跑 | **禁止**，直至 **Eng λ + Leo/主 Agent 过关** |
| 旧 CONDITIONAL（≈08:14） | 规格层 **升级为本文**；数值骨架不冲突 |
| Arch 签字 | QuantLab Arch · 2026-10-14 ≈08:21 ET |
| live / promotion | false / false |

---

## 5. 可转发 Strategy 的终签全文

> 【Arch→Strategy｜OPTIMIZER Core 文档终签】
> 标的：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（≈08:20）。
> **结论：文档终签通过（DOC_FREEZE_COSIGN_PASS）。**
> 挑战补丁齐：§5.1 双口径①纯股票100% + ②80/20+510300（主结论用②）；禁满仓 HI_LIQ 单稿对标；月末再平衡；成本≤1.3%=stretch；Stage1 底仓不动；Core 禁 LLM/防守垫。
> 浓缩参数齐：Neff20–30、单票5%/6%、两步+整手、行业±8%/绝对≤20%、Size/MidCap±0.35σ+Slack、L1-only、池内 wb、支撑集主准则 `|w^{(0)}|`。
> 四闸+两步完整性通过；不违工业支柱意图。
> **FROZEN/开跑仍须 Eng λ（NEW HARD）+ Leo/主 Agent 过关。** 本签不升 FROZEN、不授权开跑；纸面不动；live=false。
> 回执：`docs/v2/ARCH_OPTIMIZER_CORE_FREEZE_COSIGN_ZH.md`。

---

## 6. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:21 ET | 初版：文档终签通过；FROZEN 仍卡 Eng λ + Leo。 |
