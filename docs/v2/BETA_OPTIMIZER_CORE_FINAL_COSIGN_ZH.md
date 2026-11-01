# Beta 终签 · OPTIMIZER Core（PASS_PENDING_ENG_LAMBDA）

- **时间**：2026-10-14 ≈08:22 ET
- **对象**：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（≈08:22 Leo 频率+换手终签已写入 §3.8 / §4 / §5.1–5.3）
- **频率/换手 ACK**：`docs/v2/BETA_OPTIMIZER_CORE_FREQ_ACK_ZH.md`（≈08:24；三项均 ACCEPT）——本终签与之**一致、不矛盾**；ACK 管频率/换手确认，本文件为规格总终签栏位
- **状态**：**PASS_PENDING_ENG_LAMBDA**（= **CONDITIONAL_PASS_FINAL**：规格全文共签通过；**唯一**剩余阻塞 = Eng 密封窗 λ 可用产物）
- **授权声明**：一旦 **Eng λ 交付可用** 且 **Leo/主 Agent 将状态翻为 FROZEN**，Beta **授权 Stage1 只跑 Core**（双口径报告；纸面底仓不动）。本文件**不**自行开跑。
- **live / promotion**：false / false
- **HARD**：沿用 `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`（不变）
- **对标补丁**：沿用 `BETA_OPTIMIZER_COSIGN_CORE_BENCH_ZH.md` §5.1–5.3（V1.1）

---

## 总裁决（给 Strategy 一行）

**PASS_PENDING_ENG_LAMBDA** — DRAFT 正文已对齐（含 `month_end_plus_first_last` + λ_turn 标定中心）；HARD + 双口径/主指标已共签；**仅等 Eng λ**；λ 齐 + FROZEN 翻牌后 Beta 授权开跑 Core（Stage1）。

---

## 本轮新增共签（Leo ≈08:20 · DRAFT ≈08:22）

| # | 提案 | DRAFT 核对 | Beta 裁决 |
|---|---|---|---|
| (1) | 再平衡 cadence = `month_end_plus_first_last`（与 capacity_adv 一致）；**禁止**密封窗双试周频 vs 月末 | §3.8 **已写** | **ACCEPT** |
| (2) | λ_turn 标定中心 = 月双边 ≈50% **或** 年化单边 4–6×；**优先**对齐同窗同 AUM capacity_adv ±20%；成本/实际换手在 X2 = **观测非硬闸** | §3.8 / §4 **已写** | **ACCEPT** |
| (3) | 双口径①/② + 主指标 Sharpe/MDD/IR | §5.1–5.2 **已写** | **ACCEPT**（承 V1.1） |

**DRAFT sync**：`month_end_plus_first_last` 与 λ_turn 中心目标 **均已落笔** → **不**因缺字停留在 CONDITIONAL；升栏为 **PASS_PENDING_ENG_LAMBDA**。

---

## 继承共签（仍有效）

### A. HARD（CORE_CONC · 不变）

| 项 | 值 |
|---|---|
| \(w_b\) | HI_LIQ 池内 `float_mktcap` |
| 单票 | 100万 **5.0%** / 60万 **6.0%** |
| Neff | **20–30**（两步截断；支撑集 \|w⁰\|；下限暂定 2.0%） |
| 行业 | 相对 \(w_b\) **±8%**；绝对 **≤20%** |
| Size / MidCap | **±0.35σ** + Path A；Slack Size/Mid ≤0.05σ；行业 ≤1pp；绝对20%/单票/Neff/β = **0 Slack** |
| β vs \(w_b\) | \|β−1\|≤**0.10**（系统性 INFEASIBLE 可提案 ±0.15，停并回报） |
| 纸面 β vs 510300 | 报告带 **[0.70, 1.00]**（非优化器 HARD） |
| TC | **仅 L1**；禁 3/2、双阈 |
| 两步+整手 | 全池→支撑集→重解→科创 **200**；`LOT_HARD_FAIL` 不得静默 |
| INFEASIBLE | **不松**行业/单票/Neff/β |

### B. 对标 / 阶段（CORE_BENCH V1.1）

| 项 | 值 |
|---|---|
| 对标 | Core **只对** capacity_adv；B4→Full |
| 主指标 | **Sharpe / MDD / IR**；CAGR/Calmar/胜率次报 |
| 双口径 | ①纯股票 100%；② **80/20+510300** = **主表**；禁①绝对 MDD/Sharpe 比 capadv 总账 |
| α 表述 | 抬 Sharpe / 压 MDD（同口径目标带）；**非**「α≥8%+」输入 |
| Stage1 | 冻+只跑 Core；纸面底仓不动 |
| Stage2 | Full↔B4 |
| Stage3 | 换垫仓（后置预注册） |

---

## Eng λ 阻塞（唯一）

| 项 | 现状（核盘，不发明数值） |
|---|---|
| 交接 | `docs/v2/STRATEGY_OPTIMIZER_LAMBDA_CALIB_HANDOFF_ZH.md` |
| 目录 | `output/strategy_optimizer/calib/` |
| 落盘 | `calib_meta.json`、`calib_lambda_risk.json`、`calib_lambda_turn_60w.json`、`calib_lambda_turn_100w.json` **存在** |
| 可用 | **否**：`lambda_*` = **null**；`status=FAILED`（Neff `quad_over_lin` 非 DCP；n=3≪20；INFEASIBLE rate=1.0） |
| RECEIPT | **无** `ENG_OPTIMIZER_LAMBDA_CALIB_RECEIPT_ZH.md` |
| hard_spec | `leo_core_concentrated_0809`（指纹对齐 NEW HARD；失败 ≠ 可冻） |

**交付定义（Beta 接受才算齐）**：非 null 的 `λ_risk` / `λ_turn_60w` / `λ_turn_100w` 单点 + `calib_meta.json` 记录方法与密封窗约束；标定遵守月末 cadence 与 λ_turn 中心目标；**未**用 X2 收益选参。

---

## FROZEN → 开跑授权链

1. Eng λ 交付满足上表 → Strategy 写入 DRAFT 修订记录  
2. Leo / 主 Agent：**DRAFT → FROZEN**  
3. **Beta 本文件授权**：Stage1 **只跑 Core**；双口径①②全套；主对比在②；纸面 FROZEN_CONFIG / capacity_adv / B4 / S6 **不动**  
4. 过门见 `docs/v2/BETA_CORE_ACCEPT_GATES_PENDING_ZH.md`（PENDING → 跑后填）  
5. live=false；promotion=false；Beta **本人不跑**

---

## 关系

| 文件 | 关系 |
|---|---|
| `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md` | HARD 底座 |
| `BETA_OPTIMIZER_COSIGN_CORE_BENCH_ZH.md` | §5.1–5.3 V1.1；本终签吸收 |
| `BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` | SUPERSEDED |
| 本文件 | **规格终签**；栏位 = PASS_PENDING_ENG_LAMBDA |

**Strategy 回执栏**：**PASS_PENDING_ENG_LAMBDA**（DRAFT synced；Eng λ only）。
