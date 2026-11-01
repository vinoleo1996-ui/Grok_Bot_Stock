# Arch 最终共签：OPTIMIZER Core（FINAL_COSIGN）

- **时间**：2026-10-14 ≈08:23 ET（Arch）
- **标的**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（修订 ≈08:22 ET：§3.8 / §4 / §5 含 Leo ≈08:20 频率+换手终签）
- **对照**：
  - `ARCH_OPTIMIZER_CORE_FREEZE_COSIGN_ZH.md`（≈08:21 文档终签；规格层仍有效，本文升级频率/换手条款）
  - `audit/AUDIT_20261014_0817_ET_ZH.md` **N2**：Eng λ `prepared_days_3_lt_20` / 换手弱样本 → **不得当 HARD 完成**
  - Leo ≈08:09 Core-concentrate；Leo ≈08:20 频率+换手；挑战双口径补丁
- **约束**：本文只新增文档 / TEAM_STATE / ql_bus；**不改** FROZEN_CONFIG / 纸面轨；**不自行升 FROZEN**；`live=false`

---

## 0. 终签结论

### **文档最终共签通过（FINAL_COSIGN_PASS）**

**一句话**：PREREG ≈08:22 已对齐浓缩 Core + 双口径 + Leo ≈08:20 调仓/换手终签，**规格层最终共签通过**；**FROZEN / 开跑仍唯一卡 Eng 合格 λ（密封窗有效调仓日 ≥20 + 换手目标样本合格）**——λ 齐后 Strategy 可立即升 FROZEN 并只跑 Core 双口径；本签**不**代为翻转状态机、**不**授权在不合格 λ 下开跑。

| 层 | 结论 |
|---|---|
| 文档 / 四闸+两步+双口径+频率/换手完整性 | **通过** |
| Leo ≈08:20 开跑指令 | **已收**（条件 = Eng 合格 λ） |
| 状态机 `DRAFT` → `FROZEN` | **仍阻塞**（**仅** Eng λ） |
| 开跑 / book-smoke | **禁止**，直至 Eng λ HARD 完成 |
| 纸面 FROZEN_CONFIG / capacity_adv / B4 / S6 | **不动** |

相对 `ARCH_OPTIMIZER_CORE_FREEZE_COSIGN_ZH.md`：规格完整性继承；**F2（Leo/主 Agent 过关）因 Leo ≈08:20 终签拍板关闭**；残余阻塞收敛为 **F1 = Eng λ（N2 未清）**。

---

## 1. Leo ≈08:20 条款核对（必须）

| # | Leo 要求 | PREREG 落点 | 判定 |
|---|---|---|---|
| L1 | 调仓写死 `month_end_plus_first_last`（与 capacity_adv 一致） | §3.8 | ✅ |
| L2 | **禁止**密封窗内双试周频/月末 | §3.8 | ✅ |
| L3 | \(\lambda_{\mathrm{turn}}\) 标定中心 = 月双边 ≈50% / 年化单边 4–6× | §3.8；§4 | ✅ |
| L4 | **优先**对齐同窗同 AUM capacity_adv 引擎换手中位数 ±20%（B4 仅对照） | §3.8；§4 | ✅ |
| L5 | 成本 / 实际换手 = X2 观测；**非硬保**；≤1.3% = stretch | §3.8；§4 | ✅ |
| L6 | 双口径①②保留；主结论用②对标 capacity_adv | §5.1 | ✅ |
| L7 | Core 禁 LLM / 防守垫；Stage1 底仓不动 | §3.8；§5 | ✅ |

**本表**：7/7 ✅。

---

## 2. 继承检查清单（挑战补丁 + 浓缩参数）

### 2.1 挑战补丁（仍必须）

| # | 要求 | 判定 |
|---|---|---|
| C1 | 双口径① 纯股票腿 100% | ✅ |
| C2 | 双口径② 80/20+510300；**主结论用②** | ✅ |
| C3 | 禁止满仓 HI_LIQ / 取消 510300 单稿对标 | ✅ |
| C4 | 再平衡写死（现为 `month_end_plus_first_last`，非笼统「月末」） | ✅（已升级 L1） |
| C5 | 成本 ≤1.3% = stretch，非硬门 | ✅ |
| C6 | Stage1 纸面底仓不动 | ✅ |
| C7 | Core 禁 LLM / 防守垫 | ✅ |
| C8 | Full↔B4 延后；先只跑 Core | ✅ |

### 2.2 浓缩 Core 参数（Leo ≈08:09）

| # | 要求 | 判定 |
|---|---|---|
| P1 | Neff 20–30 | ✅ |
| P2 | 单票 100万 5.0% / 60万 6.0% | ✅ |
| P3 | 两步截断重解 + 整手（科创 200） | ✅ |
| P4 | 行业 ±8% / 绝对 ≤20% | ✅ |
| P5 | Size/MidCap ±0.35σ + Slack | ✅ |
| P6 | L1-only | ✅ |
| P7 | \(w_b\)=池内流通市值加权 | ✅ |
| P8 | 支撑集主准则 `|w^{(0)}|`；单票下限暂定 2.0% | ✅ |

### 2.3 四闸 + 两步

| 闸 | 判定 |
|---|---|
| (1) UNIVERSE | ✅ HI_LIQ；双轨；Core 无域预算；MidCap Path A |
| (2) FACTORS | ✅ 慢残差 α；禁名次；快门卫仅 Full |
| (3) CONSTRAINTS | ✅ HARD+Slack；Σ=行业+特异；β±0.10 vs \(w_b\) |
| (4) EXECUTION | ✅ 仅 L1；`month_end_plus_first_last`；引擎终判 |
| (5) 两步流程 | ✅ 初解→支撑集→重解→整手 |

---

## 3. FROZEN / 开跑前置（更新后）

| ID | 项 | 谁 | 状态 |
|---|---|---|---|
| **F1** | Eng \(\lambda_{\mathrm{risk}},\lambda_{\mathrm{turn}}\) 密封窗标定（**NEW HARD + 两步 + 月末 cadence**）；**有效调仓日 ≥20**；换手目标样本合格；产物非 FAILED/null；**禁用** 3 日弱样本 | Eng + Strategy | **BLOCKING**（AUDIT N2；当前 calib 目录无合格 JSON 交付物） |
| F2 | Leo / 主 Agent 明示过关 | Leo ≈08:20 | **CLOSED**（条件开跑：λ 齐 → Strategy 立即 FROZEN 开跑 Core） |
| F3 | Beta 浓缩共签 | Beta | 规格层已有 `CONDITIONAL_COSIGN_CORE_CONC`；频率/换手条款请 Beta 一行确认（不阻塞 Arch 本签） |
| F4 | 单票下限 2.0% 密封窗后钉点 | Strategy + Eng | 实现前钉；不阻塞文档终签 |
| F5 | 退市清算披露 | Eng + Data | 宽池披露；不阻塞 Core 冻 |

**明确**：

1. 本签 = **FINAL_COSIGN_PASS**（规格可冻）。
2. **不等于**状态机已 FROZEN。
3. **不等于**授权在 Eng λ 不合格时开跑。
4. **F1 一旦合格**（≥20 调仓日 + 换手样本 + RECEIPT）：Strategy **立即**升 FROZEN，并按 RUNBOOK **只跑 Core 双口径**（禁 Full/LLM/换垫）。
5. 旧 `ARCH_OPTIMIZER_CORE_FREEZE_COSIGN_ZH.md` 在频率/换手细节上由本文 **supersede**；浓缩参数与双口径不冲突。

---

## 4. Arch 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **FINAL_COSIGN_PASS（最终共签通过）** |
| 规格完整性 | Leo≈08:20 7/7 + 挑战补丁 8/8 + 浓缩 8/8 + 四闸/两步 ✅ |
| FROZEN / 开跑 | **仍须 Eng 合格 λ（≥20 调仓日）**；λ 齐后 Strategy 可立即 FROZEN 开跑 |
| 弱样本 λ | **禁止**当作 HARD 完成（AUDIT N2） |
| Arch 签字 | QuantLab Arch · 2026-10-14 ≈08:23 ET |
| live / promotion | false / false |

---

## 5. 可转发 Strategy 的终签全文

> 【Arch→Strategy｜OPTIMIZER Core 最终共签】
> 标的：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（≈08:22，§3.8/§4/§5）。
> **结论：最终共签通过（FINAL_COSIGN_PASS）。**
> Leo≈08:20 齐：调仓写死 `month_end_plus_first_last`（与 capacity_adv 一致；禁双试频率）；λ_turn 密封标定中心=月双边≈50%/年化单边4–6×（优先对齐 capadv ±20%）；成本非硬保（≤1.3%=stretch）；双口径①②保留（主结论用②）。
> 继承仍齐：Neff20–30、单票5%/6%、两步+整手、行业±8%/绝对≤20%、Size/MidCap±0.35σ+Slack、L1-only、池内 wb、Core 禁 LLM/防守垫、Stage1 底仓不动。
> **FROZEN/开跑仍唯一依赖 Eng 合格 λ**（密封窗有效调仓日 ≥20 + 换手目标样本合格；AUDIT N2：3 日弱样本禁止当 HARD）。λ 齐后你可立即升 FROZEN 并只跑 Core 双口径报数。本签不代升 FROZEN；纸面不动；live=false。
> 回执：`docs/v2/ARCH_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md`。

---

## 6. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:23 ET | 初版：FINAL_COSIGN_PASS；F2 关闭；F1=Eng λ≥20 仍 BLOCKING。 |
