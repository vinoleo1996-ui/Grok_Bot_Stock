# Beta · OPTIMIZER Core v1.3 门控审查（X2 入场券口径）

- 时间：2026-10-18 02:24 ET 起草，落盘见文末（`date` 实测，ET = UTC−4）
- 审查人：Beta（β / 风险预算 / 风格）
- 性质：**纯只读**。没有执行任何项目代码、脚本、pytest 或 harness，也没有申请 .ok。只用了 Read、rg、ls、sha256sum、jq、awk，读的是 CSV/JSON/MD 和 nav.csv。§4.2 里组合对 510300 的 β 是 Beta 用 awk 对两份 nav.csv 做的协方差粗算，**不是项目代码，只作披露**；同一算法复算出的 vol 与 summary.json 一致，到小数点后 3 位。
- 判定依据（事前登记，早于任何 v1.3 收益）：`docs/v2/BETA_CORE_ACCEPT_GATES_PENDING_ZH.md`（2b72d099…，10-14 ≈08:22 ET）§2–§4；`STRATEGY_OPTIMIZER_PREREG_FROZEN_ZH.md`（c7b4b799…）§3.4/§3.7/§3.8/§5.1/§5.2；AMEND_v1_3（278bc401…）；`ARCH_RESIGN_A_v1_3.ok`（f27c7e97…）。
- **live=false；promotion_approved=false。** 冻结纸面轨 capacity_adv / B4 / S6 没有碰过（B 列只读记分卡里的数字）。不做 Strategy 交接。

---

## 0. 结论

**Beta 门控 = FAIL（Core v1.3 在 X2 未通过事前登记的 ACCEPT 门；60万、100万两档都 FAIL）。**

- 主指标三门 G-S（Sharpe）、G-M（MDD）、G-IR（IR）在口径②上，两档相对 B（现行 capacity_adv）**全部不过**，差距远大于容差（Sharpe 差 −0.60 / −0.47，容差 0.05；MDD 深 9.5pp / 7.9pp，容差 2pp）。
- 结构硬闸 G-Lot（「LOT_HARD_FAIL = 0 才可 ACCEPT」）两档都失败：X2 中 60万 4/29 天，100万 12/29 天。
- 按 ACCEPT 汇总规则 §4，「任一 HARD 结构闸失败 → FAIL，不得靠放宽 HARD 补救」。主指标也不是「容差边缘」，所以没有 CONDITIONAL 的余地。
- 不出 PASS_WITH_AMENDMENTS。下面 §6 列的 D1–D8 是披露和后续条件，**不能把 FAIL 改成通过**。
- 正面结果（只作描述）：A 在同池对照中明显好于 C（Sharpe 0.42 对 0.09，MDD −19.6% 对 −29.9%，60万②），但 C 的执行层不可比（成交率 0.547，闲置现金 23.8%），见 §3.3。
- 与 Strategy 00:56 ET、Arch 00:59 ET 的诚实结论一致：**Core 输 B 赢 C**。不进 FWD，不调参。

**失败条件（写死）**：
1. v1.3 的 X2 数字不得用于晋级、FWD 入轨或纸面替换。
2. 如果 Leo 决定保留 Core，下一版（v1.4 / D21）必须**在口径 C 下**重新完整走一遍本文 §2–§4 的所有门。G-S、G-M、G-IR 用同样的容差，G-Lot 仍要求 LOT_HARD_FAIL=0（或者先由 Leo/主 Agent 书面改门，并且改门必须在看收益之前）。任何一项不过就是 FAIL。
3. 即使 X2 通过，那也只是入场券。晋级只看 2026-11-02 起的 FWD。

---

## 1. 输入清单与磁盘 sha256（R3，02:2x ET 实测）

| 文件 | sha256 |
|---|---|
| output/strategy_optimizer/core_x2/ARCH_RESIGN_A_v1_3.ok | f27c7e97da146e52c4db5d20520581b05e5780c46db06cc841d61461100bae7e |
| output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_v1_3.ok | 94ecf1738173859e6915d268b9d9e752655d6c9bc579e180ca14729240faeeba |
| output/strategy_optimizer/core_x2/ARCH_S2_3_RELEASE.ok | 11a693927d64431b1526acea833bb7a4fdcb58ca0a1bb591dcc217086849704d |
| output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok | 623c038af325336134cc9e04988e8bf1f90594bedb12e905c00958cdbe2be8f3 |
| docs/v2/ARCH_OPTIMIZER_CORE_v1_3_RESIGN_ZH.md | bd8b23f66ec9e65eed89c4a48d9529ecdb1fc687a6cf1ce4f4348ab5f7e83dff |
| docs/v2/ARCH_V1_3_SCORECARD_AUDIT_ZH.md（Arch 00:59 审计） | eab8ff78a386474fc9e6a2b8cb5803949727a9969f0ddf17159cf384c4187eff |
| docs/v2/ARCH_ENG_RECOVERY_SCORECARD_OK_REVIEW_ZH.md | 54074cbc1b69f7a415b48aa2b762687cecb975e114eabdb14c4de2f353ffcb29 |
| docs/v2/ENG_V1_3_AUDIT_FIX_RECEIPT_ZH.md | 3e07f17fb18753346e8c17a03ae668df8e40363b3d52930073c3b8981f177d7e |
| core_x2/scorecard_three_col_auditfix_20261018_2aa03a8f.md（= .md.gen，**本文主读源**） | aca6059ea4408cf95e1d1aed36b2ab099f7900f4a971c2c6ad8079c9882c89d7 |
| core_x2/scorecard_three_col.md（00:5x 原版） | 5b9250d2ae26e9108e122c02f86043b0c9da0ca9dcecab101055444c4458d3f5 |
| core_x2/scorecard_three_col.csv | 7622242b98b45dca2f5882086bcbdfb0a01157516a51e29c365109bcf28e9fe9 |
| core_x2/overcap_recount_v1_3_auditfix_20261018_ff4ac3f0.json | 5b5d4a95c4317352c49cbef60b34006758a775fcb83f7d0205af76e7e90ca310 |
| core_x2/core_v1_3_stats.json | 576539648e424a6c1b744da01e68a14124f33f54f98bfe691ede6e62337ff224 |
| core_x2/core_v1_3_disclosure.csv | 9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b |
| core_x2/core_v1_3_infeasible_days.csv | 42c5dd8a5fb000dfbb7792f82de2dccf6554f518bf5f053ef3dae00b1a83c288 |
| core_x2/v1_3_RUN_MANIFEST.json | 8824a87ee4aa9660279811a96d4f57e542faa0acda9f48e90100f0c92a58f94e |
| core_x2/v1_3_RUN_MANIFEST_ADDENDUM_20261018_ENG.json | fc58fa084812ad5e8980360a535beaa17ab48e808c4583ac5a27821c8cd85fe2 |
| book_smoke_v1_3_equity80_etf20_510300_60w/book_smoke_summary.json | 1008b6e054d6c777c2db3ab53eb0447fc6bd347d55044f3cca5bcfc03a69e78d |
| book_smoke_v1_3_equity80_etf20_510300_100w/book_smoke_summary.json | 7886d52950586c58d103c9d2a5f483b2895aa2f9822522fd53cf9a4b8d1e2322 |
| book_smoke_v1_3_equity_100_60w/book_smoke_summary.json | 39f8e6d5c5c47db9332fd4d2de7db2ffc47ad6834d4ea9ca452c81e03d18412d |
| book_smoke_v1_3_equity_100_100w/book_smoke_summary.json | bfedf131d5bc8b45a06a5b3f10ecc126124e0009709c48e6d76926d746505402 |
| …eq80_60w/aum_600000/X2/BOOK/summary.json · nav.csv | 75f5502d… · b2c0432bba27f3a8d5931b293bd07aace65f76840b9d07b7db038c75687467bf |
| …eq80_100w/aum_1000000/X2/BOOK/summary.json · nav.csv | b6b96831… · 3153f7adb6b8dc270f9aa8eda1e47bf71c1efacddf158f05c866f320cde5d1fa |
| …eq100_60w/aum_600000/X2/BOOK/summary.json · nav.csv | 071282e7… · a788e4019c6c9ebc1ff84616b53051649efab86f84d0233968e0ce382514a036 |
| …eq100_100w/aum_1000000/X2/BOOK/summary.json · nav.csv | 11fb3f0b… · 730877e70fb6cb1d14ddf227b2514f55b866f982ff28649aad0626e494eb7d80 |
| X2/C0（510300）nav.csv：60万 · 100万（同档两口径逐位相同） | 06c4c41a859c5ba5fe6c1be4a6d44b6214ce3d1280be201854c9335934454a5f · f8fdb368887b409a633a49a5f9e219482b261fa0b093709b9b36c5e874fabd34 |
| docs/v2/STRATEGY_OPTIMIZER_PREREG_FROZEN_ZH.md | c7b4b799a16a46cf9fb83957b44156c3d7d3b8425e70befef56a51e48e349b6d |
| docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_v1_3_ZH.md | 278bc4019041fc5d52e5060667500a14b46063ed977e126a5c78a8dd1a4f3502 |
| docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md（LOTFIX v1.4 冻结体） | d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425 |
| docs/v2/LOTFIX_V1_4_FREEZE_RECORD_ZH.md | 0d47c52f8be402d02e369d0a92c4ba05d868038f4b3c41870b2bdb8234c52641 |
| docs/v2/LOTFIX_V1_4_FREEZE_RECORD_APPENDIX_CLARIFY_1_ZH.md | d075a2a68f2d5c42c750669cdff2dd51f93794e11ea907f08ffc29c39c724d85 |
| docs/v2/S2_3_FREEZE_RECORD_ZH.md | a8e67a71ca774a396e606cc9a44ad5764f48ab7054e2f59befd6c8c06bb30757 |
| docs/v2/STOPRULE_CONSEC_FREEZE_RECORD_ZH.md · STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md | 13c6ad5872d8c86e1d43169952ee5d4b93dd767db28dbb427b12f4a6727e76f4 · 41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b |
| docs/v2/BETA_CORE_ACCEPT_GATES_PENDING_ZH.md（**事前门**） | 2b72d099f8ddea28fd28ce672dfd88460c34617da0f1b3c7e8dbaa0eb9d978dd |
| docs/v2/BETA_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md | 3baf84ac1c0faa5bed22cb34df0cc319dac3eb60204ed23582946ff50e3f05b5 |
| docs/v2/BETA_LOTFIX_V1_4_COSIGN_ZH.md | 0ad588a3fb725b5bbc4f4b9f04b1dbade5f13b14bedf5ae5ea698045dcb4fa6f |
| docs/v2/BETA_STOPRULE_CONSEC_COSIGN_ZH.md | 56512b8d1dbe412298be00fc479129e572d0116910a2150907516d33d3f1c9ae |
| docs/v2/BETA_OPTIMIZER_STAGE2_S2_3_COSIGN_ZH.md | 78d1a0114fe5a11732f7d0090629eafc4f72c5a7addc80255437465a120ecb66 |
| docs/v2/BETA_LOTFIX_AMEND1_POOL_SNAPSHOT_COSIGN_ZH.md | 45b7f4156e99a95012aa058e2d708884de7b0f0348105c2843b7cb27029fa463 |
| docs/v2/MANDATE_DRAFT_STOCK_ETF_MAINLINE_ZH.md | d861e77a9a959db893e7f55e527b1fcbf53264e26f6d48418670a746afd4835d |
| docs/v2/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.md | 8b7a29f0775de8e325a3105001d309cf40624221eb60b576d409536e75382753 |
| docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md | 1aa43bdd01935f55fd81f4ef0e1ddf92ef585d7ba6571e7078cd28ee86239a03 |
| output/beta/lotfix_v14_check/basisC_recheck_v1_3.csv（Beta 01:00 前产物） | 4f9f994d509179c173e312ad2f2bfdcfd69f95df78b4d4ed98ea64bae6c2df77 |

一致性：RESIGN .ok 里的 resign_doc_sha / amend_sha 与磁盘一致。复签文档 §7 列出的 disclosure/infeasible/stats/RUN_AUTH 的 sha 与磁盘一致。Arch 审计 §1 引用的两份 .ok（f27c7e97…、11a69392…）与磁盘一致。复算 json 的 source_sha256 = disclosure.csv 的 sha。权重 4 份的 sha 以 .ok 第 8–11 行为准（本审查没有读 parquet）。

---

## 2. 三列齐备性与口径一致性

| 项 | 结果 | 出处 |
|---|---|---|
| 三列齐全 | ✅ A=Core v1.3(HI_LIQ)、B=现行 capacity_adv mid_large、C=capadv Top-25@HI_LIQ_V1.1，两档 × ①② 都有 | auditfix 记分卡 L30–39、L148–198 |
| 同窗口 | ✅ X2 2024-06-03→2026-10-09，569 个日收益，年化 244 | Arch 审计 §4 L45；BOOK summary window_dates |
| 同引擎 | ⚠ 都是 strategy_v1/execution.py，但 B（10-13 11:14）、C（10-14 20:03）的引擎 sha **没有钉** | 记分卡 L78（P2-7） |
| 同成本口径 | ✅ 优化器内只有 L1（λ_turn‖w−w0‖₁），引擎 strategy_v1 作终判成本 | FROZEN §2 第 3 行、§3.7 |
| λ 一致 | ✅ λ_risk=117.21317483995702，λ_turn=0.6/0.6（calib json 与 meta 都一致） | RESIGN §1(b) L34 |
| 调仓节奏 | ⚠ A 是 `month_end_plus_first_last`（X2 29 个调仓日：2024-06-28…2026-09-30 + 2026-10-09）；B、C 每天都有目标权重（570 个信号日）。FROZEN §3.8「调仓时点须与 capacity_adv 100% 同步」这条控制变量**没有达成**，只披露 | disclosure.csv X2 日期；Arch 审计 §5 L75 |
| 池 | B 用 top300 静态锚，A、C 用 HI_LIQ。这是设计本意，但 B 和 A/C 之间的差距里混有池子效应 | Arch 审计 §5 L77 |
| 510300 套袖 | A 固定 80/20；B 平均 0.212；C 平均 0.200 | 记分卡 L166–167 |

---

## 3. Core ACCEPT 双基准（主指标 Sharpe / MDD / IR；按档分别判）

### 3.1 口径②（80/20 510300，主表）

| 档 | 列 | Sharpe | MDD | IR vs wb | IR vs 510300 | CAGR | Calmar | 日胜率 | 月胜率 28月 / 29月* | vol |
|---|---|---|---|---|---|---|---|---|---|---|
| 60万 | A | 0.42 | −19.6% | −0.07 | −0.38 | 6.6% | 0.34 | 51.7% | 53.6% / 51.7% | 19.9% |
| 60万 | B | 1.02 | −10.1% | 0.41 | 0.13 | 13.8% | 1.37 | 52.7% | 50.0% / 51.7% | 13.6% |
| 60万 | C | 0.09 | −29.9% | −0.59 | −0.75 | −0.6% | −0.02 | 49.7% | 53.6% / 51.7% | 23.2% |
| 100万† | A | 0.41 | −19.5% | −0.11 | −0.42 | 6.3% | 0.32 | 51.8% | 53.6% / 51.7% | 19.6% |
| 100万† | B | 0.88 | −11.6% | 0.30 | 0.00 | 12.2% | 1.05 | 53.6% | 57.1% / 58.6% | 14.3% |
| 100万† | C | 0.20 | −33.0% | −0.27 | −0.46 | 1.7% | 0.05 | 50.1% | 50.0% / 48.3% | 26.9% |
| 参照 | 510300（C0） | 0.65 | −16.2% | — | — | 11.3% | 0.69 | — | — | 19.2% |

出处：auditfix 记分卡 L34–39、L165–167、L190–192；vol 取自 scorecard_three_col.csv 的 vol 列；C0 取自 BOOK/C0 summary.json；月胜率 29 个月口径取自 Arch 审计 §4 表 L50–55。
*主 Agent 00:59 裁定以 29 个月口径为准，记分卡仍用 28 个月（见 §5 C-2）。†100万列标「可行性不足，收益仅供参考」。

### 3.2 事前门判定（BETA_CORE_ACCEPT_GATES_PENDING §2；A 对 B，口径②）

| 门 | 定义 | 60万 | 100万 |
|---|---|---|---|
| G-S | Sharpe_A ≥ Sharpe_B − 0.05 | 0.42 对 0.97 → **FAIL**（差 −0.60） | 0.41 对 0.83 → **FAIL**（差 −0.47） |
| G-M | MDD_A 比 MDD_B 深不超过 2pp | 深 9.5pp → **FAIL** | 深 7.9pp → **FAIL** |
| G-IR | IR_A ≥ IR_B − 0.05（主基准 HI_LIQ wb，次基准 510300） | wb：−0.07 对 0.36 → **FAIL**；510300：−0.38 对 0.08 → **FAIL** | wb：−0.11 对 0.25 → **FAIL**；510300：−0.42 对 −0.05 → **FAIL** |
| G-M25 | MDD ≤25% | −19.6% ✅（破 15%） | −19.5% ✅（破 15%） |
| G-C / G-Cal | CAGR、Calmar、胜率只报不判 | CAGR 低 7.3pp，Calmar 0.34 对 1.37 | CAGR 低 5.9pp，Calmar 0.32 对 1.05 |

对 C（同池控制变量，只描述）：两档 A 的 Sharpe、MDD、IR 都好于 C（60万 Sharpe +0.33、MDD 浅 10.3pp；100万 Sharpe +0.21、MDD 浅 13.5pp）。

### 3.3 口径①（纯股票，只作分解；不得拿 A① 的绝对值去比 B 的总账）
60万：A 3.9% / −24.1% / Sharpe 0.28 / IR_wb −0.26；B 12.9% / −10.4% / 0.96 / 0.29；C −2.4% / −34.9% / 0.04 / −0.51。
100万：A 5.2% / −22.9% / 0.35 / −0.16；B 12.1% / −10.7% / 0.88 / 0.25；C −1.3% / −37.4% / 0.11 / −0.30（记分卡 L169–171、L194–196）。
A① 60万 MDD −24.07%，离 25% 线不到 1pp（Arch 审计 L59）。
C 的执行层：成交率 0.547 / 0.614，闲置现金 23.8% / 13.5%，平均敞口 0.76 / 0.86（记分卡 L64–69）。所以「A 赢 C」里有一部分是 C 的执行折损，c_col_exec_diagnostic.md 还没出，**不作归因结论**。
A 自身的执行层（Beta 补读 BOOK summary.json）：② 60万成交率 0.974、闲置现金均值 7.9%、平均敞口 0.92、公司行为现金 32,778 元；100万成交率 0.973、闲置现金 6.1%、平均敞口 0.94。优化器层现金 ≤2%，但账簿层平均闲置 6–8%，主要是月度调仓之间分红留成现金，加上整手残余，**会摊薄 A 的 β 和收益**。只披露。

---

## 4. Beta 职责项核查

口径说明：v1.3 判定口径是 **A（代码口径，510300 记为基准暴露）**，按主 Agent 00:46 ET 裁定、.ok 第 14 行。disclosure.csv 里的 β/Size/MidCap 漂移是 A 口径；行业列是「股票部分归一」（B 口径），依据是 RESIGN §1 L42「B 口径行业越界 18/18/34/38 行、最大 1.34pp」与本列 max 21.34% 相符。C 口径的数字取自 RESIGN §3 和 Beta 自己的 basisC_recheck_v1_3.csv。

### 4.1 β vs wb：|β−1| ≤ 0.10（G-βw）
可行调仓日整手后的 beta_drift（disclosure.csv 第 17 列，awk 统计；X2 ‖ 全样本）：

| 档·口径 | n | 均值 | max\|·\| | >0.10 天数 |
|---|---|---|---|---|
| 60万 ② | 25 ‖ 96 | −0.024 ‖ +0.017 | 0.0999 ‖ 0.0999 | 0 ‖ 0 |
| 60万 ① | 25 ‖ 96 | −0.023 ‖ +0.027 | 0.0994 ‖ 0.0998 | 0 ‖ 0 |
| 100万 ② | 17 ‖ 81 | −0.015 ‖ +0.016 | 0.0904 ‖ 0.0904 | 0 ‖ 0 |
| 100万 ① | 17 ‖ 81 | −0.012 ‖ +0.029 | 0.0974 ‖ 0.0993 | 0 ‖ 0 |

- 口径 A 下 **违约 0 天**（与 RESIGN §1(c) |β|≤0.0999 一致）。约束在顶：60万② 2026-03-31、08-31、09-30、10-09 的 β 漂移在 −0.099 到 −0.0999 之间，**下界 binding**，X2 末段系统性低 β。
- **沿用日（不可行、沿用上期）不受约束**：60万① X2 沿用日 β 最大越界 0.0727（\|β\|=0.173）；100万① 沿用日 β 越界 5/12 天，最大 0.1079（\|β\|=0.208）；100万② 3/12 天，最大 0.0826（stats.json X2 carry_day_drift）。实际持有组合的 β 在这些天**越过** 0.10。
- 口径 C（股票袖按预算）：口径② β 越界 6–11 行，最大 0.025（RESIGN §3 L116）。Beta 复核表中 X2 60万② 有 β 越界日，例如 2024-07-31 E_beta=0.1088。
- **判：口径 A 下通过；按实际持仓（含沿用日）和口径 C 不通过。** 只作披露，v1.4 口径 C 必须重判。

### 4.2 Mandate 组合层：vol≈16%、β≈0.70（G-βp 报告带 [0.70, 1.00]）
- 组合对 510300 的 β（Beta 用 awk 对 BOOK/C0 nav.csv 做日收益 OLS，n=569，非项目代码）：② 60万 **0.871**（相关 0.842，TE 11.0%）、100万 **0.863**（0.846，10.8%）；① 60万 0.854、100万 0.842。**在报告带 [0.70, 1.00] 内** ✅，但高于 Mandate 草案的「β≈0.70」目标 0.16–0.17。
- 年化 vol：A② 19.9% / 19.6%，A① 21.2% / 20.9%。510300 是 19.2%，B 是 13.6% / 14.3%。**A 高于 Mandate 的 16% 目标 3.6–3.9pp，甚至高于 510300 本身。** MANDATE_DRAFT L37 写的是「约 16% vol · β≈0.70（仍可随试配微调，须预注册）」，是目标而不是 HARD，所以只披露。也就是说，Core 没有达到 Leo 的风险预算意图：它比被动基准更波动，同时收益更低。
- B、C 对 510300 的 β：**无数据，不能判**（本审查没读 B、C 的 nav.csv，记分卡也没给这一列）。

### 4.3 单票 5%（100万）/ 6%（60万）
- 整手前和整手后（口径 A），单票 ≤ cap×预算，越界 0（RESIGN §1(c) L35–36）。
- 整手后低于 2%×预算下限的有 76 行、共 100 只，最小 0.47%（RESIGN §1 L37，P2-1）。冻结规格没有规定整手后的下限，只披露。
- 账簿层实际单票峰值（价格漂移后）：**无数据，不能判**（记分卡没有给）。

### 4.4 Neff 20–30（G-N）
- X2 可行日 neff_opt：60万 min 19.99995 / 均值 20.08 / max 20.80；100万 20.00 / 20.62 / 21.56。全样本 60万 max 20.80、100万 max 23.53。
- 60万有 17 行（X2 4 行）是 19.99995–19.99999，属于求解器数值容差，不算违约。
- **判：通过，但贴着下界**：60万中位数 = 20.0，下界 binding。整手后持仓 20–22 只（X2），中位 21（RESIGN §2⑤）。
- Neff 贴底，说明「集中度越高越好」的 α 方向被 20 只的下限截住，与 6% 单票上限、整手一起构成 60万档的结构性约束。

### 4.5 行业 ±8%（相对全池 wb）且绝对 ≤20%（G-I）
- 口径 A（判定）：整手前和整手后越界都是 0，含零持仓行业，零持仓行业的 wb 最大 8.64%，在 box + slack 内（RESIGN §1(c) L35–36）。
- B 口径（disclosure 列）：X2 可行日 ind_active_max 60万 8.94%、100万 8.64%（都在 8% + 1pp slack 内）；ind_abs_max 60万 20.21–20.26%（X2 1 天 >20%），100万 20.58–20.78%（X2 3–4 天 >20%）。全样本 >20% 的行数 60万 11、100万 27–32，最大 21.34%（+1.34pp）。
- 冻结 slack 规定「绝对行业 slack = 0」。所以在 B 口径下，绝对 20% 有真实越界；A 口径下没有。
- **判：口径 A 下通过；B 口径下绝对上限有越界（≤1.34pp）**，只披露。

### 4.6 Size / MidCap ±0.35σ（含 slack ≤0.05σ）（G-Sz）
- 口径 A，X2 可行日：|Size| max 60万 0.336、100万 0.329；|MidCap| max 60万 0.3996、100万 0.395。超过 0.35 的部分都落在 slack 内，越界 0（stats.json X2 postlot_drift；RESIGN L36）。
- slack 使用：X2 60万 5/29 天（17.2%），100万 3/29 天（10.3%）；顶格 60万、100万各 1 天（3.4%）。全样本：60万 13.5%，100万 9.9%（RESIGN §2⑤）。
- 沿用日越界：100万① X2 MidCap 5/12 天，超出 >0.05，最大 0.294（\|MidCap\|=0.644）；60万全样本沿用日 MidCap 最大越界 0.306。
- 口径 C：口径② MidCap 越界 12–17 行（最大 0.087σ）。口径 A 在口径②上相当于把界放宽到 0.4375σ（RESIGN §3 L116）。
- **判：口径 A 下通过；按实际持仓（沿用日）和口径 C 不通过**，只披露。

### 4.7 换手、L1 成本、再平衡
- 再平衡 `month_end_plus_first_last`：✅。全样本 107 个调仓日（含 2018-01-02 首日、2026-10-09 末日），X2 29 天（disclosure.csv）。
- 求解单边换手中位：X2 60万 0.386、100万 0.395（全样本 0.323 / 0.311）。超过 40% 帽（只作监控，P1-R2 裁定）：60万 28/96（X2 11/25），100万 18/81（X2 7/17）；分母 95/80 的口径差见复算 json（5b5d4a95…）。
- 年化单边（日度实际权重差 ×244，含漂移，与 λ 标定口径不可比）：A② 6.10 / 5.13，B 4.57 / 4.70，C 7.49 / 8.54。60万 A 超出「年化单边 4–6×」中心带和「capadv ±20%」带（4.57×1.2=5.49）；100万在带内。
- 成本 / 初始 AUM：A② 2.73% / 2.31%，B 1.72% / 1.71%。**两档都远超 1.3% 的 stretch。**
- S2-3（只作描述，VALID_WITH_DISCLOSURE）：无带 TO_d 中位 ② 0.3776 / 0.3969、① 0.3936 / 0.4263，都 >0.30，FAIL（事前预期）。与 Beta S2-3 会签结论一致。

### 4.8 可行性（INFEASIBLE / LOT_HARD_FAIL；口径 A 对 C；两袖同日严格）
- 求解阶段 INFEASIBLE = 0。全部失败都是整手阶段的 LOT_HARD_FAIL：60万 10 天（X2 4 天：2024-09-30、2025-08-29、2025-11-28、2026-02-27），100万 25 天（X2 12 天）（RESIGN §1(d)；stats.json infeasible_list）。

| X2（29 天） | 只看硬约束（A） | 严格（A） | 两袖同日严格（A，CLARIFY-1 口径） | 两袖同日严格（C，Beta 复核） | v1.4 §8 门 24/29 |
|---|---|---|---|---|---|
| 60万 | 25/29 = 86.2% | ② 25 · ① 24 | **24/29 = 82.8%** | **15/29 = 51.7%**（② 15、① 24） | A 恰好到线；C 不到 |
| 100万 | 17/29 = 58.6% | ② 11 · ① 5 | **5/29 = 17.2%** | **5/29 = 17.2%**（② 7、① 5） | 两种口径都远不到 |

- 口径 C 下翻成不可行的 X2 档日：60万 10 天，100万 5 天（RESIGN §3 表）。
- 这再次确认了 Beta L1 警告：v1.4 的 80% 参照是口径 A、判定用口径 C，**§8 很可能触发**。原因不只是 5% 上限，β/MidCap 收紧也是一个原因（100万 X2 的 12 个失败日中有 9 天涉及 style）。

### 4.9 停跑规则 r3（k=3，按档；v1.4 起生效，**不追溯**）
- 假想套用到 v1.3：**100万会触发**，第一次在 2026-05-29（2026-03-31、04-30、05-29 连续 3 天 LOT_HARD_FAIL），之后 2026-08-31、09-30、10-09 再次连续 3 天。2025-06→07 只连 2 天，不触发。全样本里 X2 以前没有连续 3 天的情况。
- 60万不触发：X2 内最多连续 1 天，全样本最多连续 2 天（2020-12-31→2021-01-29）。
- 与 Beta 停跑会签 M1–M6 和置顶披露「100万两段」一致。只作描述。按主 Agent 00:31 裁定，本轮按原规则继续、不追溯。

### 4.10 小结（职责项）
| 项 | 口径 A（判定） | 实际持仓 / 口径 C |
|---|---|---|
| β vs wb | ✅ 0 违约（顶格 0.0999） | ❌ 沿用日最大 0.208；C 口径 6–11 行 |
| vol 16% / β 0.70 | β 0.86–0.87 在 [0.70, 1.00] 内 ✅；vol 19.6–19.9% ❌ 高于目标 | — |
| 单票 5% / 6% | ✅ | 账簿层峰值无数据 |
| Neff 20–30 | ✅（贴下界） | — |
| 行业 ±8% / ≤20% | ✅ | B 口径绝对上限越界 ≤1.34pp |
| Size/MidCap ±0.35σ | ✅（slack 顶格 1 天/档） | ❌ 沿用日 MidCap 最大 0.644；C 口径 12–17 行 |
| 换手 / 成本 | 40% 帽只作监控；成本 2.3–2.7% ❌ 超 stretch | — |
| 再平衡 | ✅ | B/C 节奏不同步 ⚠ |
| 可行性 / LOT | ❌ G-Lot（4 天 / 12 天） | C 口径更差 |
| 停跑 r3 | 不追溯 | 100万假想会触发 |

---

## 5. Arch 00:59 审计条件与 RESIGN 条件现状

| # | 条件 | 现状 | 依据 |
|---|---|---|---|
| P1-1 | S2-3 runner 放行后被改、未钉 sha → 补审 diff | ✅ 已关：主 Agent 01:37 裁定 VALID_WITH_DISCLOSURE（结论只作描述）；以后的 .ok 要钉 runner sha | 记分卡 L43；TEAM_STATE Arch 01:38 |
| P1-2 | 披露 C 列的成交率、闲置现金、换手、不可比性 | ✅ 已写入 auditfix 记分卡；C 列归因诊断 `c_col_exec_diagnostic.md` **不存在**（待 .ok） | 记分卡 L60–72；ls |
| P2-1 | 引擎偏乐观标注改写 | ✅ | 记分卡 L5–6 |
| P2-2 / **C-2** | 月胜率统一为 29 个月（主 Agent 00:59 定稿） | ❌ **未满足**：auditfix 记分卡 L74 仍写「本表取 28 个月口径」 | 审计 L100；记分卡 L74 |
| P2-3 | 超帽分母 96/81 | ✅ 两种分母都输出 | 记分卡 L26；复算 json |
| P2-4 | v1.2 可行性表标「已取代」 | ✅ | 记分卡 L121–123 |
| P2-5 | 2025-06→07 失败段确认 | ✅ | 记分卡 L11 |
| P2-6 | 100万 sh.511880 的来源 | ✅（book 层现金停泊） | 记分卡 L76 |
| P2-7 | B、C 引擎 sha 没有钉 | ❌ 已知缺口，只能在重跑时钉 | 记分卡 L78 |
| P3-1 / P3-2 | 00:35 调试运行不可核；599 对 111 | 不可核 / 未单独核对 | — |
| **C-A** | Arch 复核 auditfix 产出（aca6059e / 5b5d4a95） | ⏳ 只找到 .ok 签发（附录 D5）和 Eng 02:00「已报 Arch」，**没有找到 Arch 对输出的复核文档** | rg 结果 |
| RESIGN-1 | 按 A 通过只算入场券，晋级讨论前必须在 v1.4 用口径 C 复现 | ⏳ 未满足：v1.4 和 D21 都没跑，等 Leo 定 Core 去留。本文判 FAIL，入场券本身也没拿到 | .ok 第 15 行 |
| RESIGN-2 | 40% 只作监控，披露规格与代码不一致 | ✅ | 记分卡 L26 |
| RESIGN-3 | 100万可行性置顶；VOID smoke 不得引用 | ✅（本文没有引用 00:32 / 00:30–00:44 的 VOID 数字） | 记分卡 L8–13、L27 |

---

## 6. 前视 / 幸存者 / 口径漂移 / 窗口表述

- **前视**：λ 由密封窗标定，`x2_returns_used_for_selection=false`（FROZEN L3）。P1-R1/R2 的裁定 00:46:19 早于 book_smoke START 00:47:44（Arch 审计 §2）。权重 mtime 00:27:01 早于 .ok，allow_rerun_weights=false 没有被违反（审计 §1）。✅ 没有发现前视。
- **幸存者**：book_smoke 引擎停牌日禁止成交、复牌时一次性实现涨跌，没有股票退市终值。X2 内持有退市票的事件 = 0（审计 §3）。HI_LIQ_V1.1 池是否按时点构建，Beta 没有独立核实：**无数据，不能判**。Arch 10-14 的结论是「机制存在，Beta B1『约 0』只对 mid_large 成立」。
- **口径漂移**：
  - (a) 判定口径 A 在口径②上把风格/β 界放宽到 1/0.8 倍。这是事前裁定，但它意味着「A 通过」不等于「股票袖通过」。
  - (b) 月胜率 28 对 29 个月（C-2 未关）。
  - (c) 年化换手含漂移，与 λ 标定口径不可比（记分卡 L145）。
  - (d) v1.2→v1.3 行业基准从入选名单 wb 改成全池 wb，属于 AMEND 事前修订，不是漂移。
  - (e) B 是日度目标，A 是月度。
- **窗口表述**：记分卡第 1 行「X2 漂亮数不得晋级」、L30「X2 只作入场门槛」、L141「晋级看 2026-11-02 起 FWD」都写明了 ✅。本文同样写明：**X2 只作入场券，FWD 自 2026-11-02 起才是晋级检验。**

---

## 7. 披露与后续条件（D1–D8，不改变 FAIL）

- **D1**：v1.3 X2 的 FAIL 原样记录。不调参，不换口径重判，不改 λ。
- **D2**：如果 Leo 保留 Core，v1.4 / D21 必须在口径 C、两袖同日严格的口径下重跑本文 §3–§4 全部门。G-Lot 未经书面改门仍然是 0 容忍。§8 的 24/29 预计会触发（60万 C 只有 15/29）。
- **D3**：Eng 把记分卡月胜率改为 29 个月口径，写到带 sha 后缀的新路径，不覆盖（C-2）。
- **D4**：Arch 补写对 auditfix 输出（aca6059e / 5b5d4a95）的复核结论（C-A）。
- **D5**：B、C 重跑时用 ok_runner_pin 钉引擎 sha（P2-7）。在那之前，A 对 B 的差距按「方向确定、精度待钉」来读。
- **D6**：组合层风险预算缺口要写进 Leo 简报：A 的 vol 19.6–19.9% 高于 16% 目标和 510300（19.2%），对 510300 的 β 是 0.86–0.87，高于 0.70 目标。Core 在 X2 没有实现「抬 Sharpe / 压 MDD」的设计意图。
- **D7**：沿用日的 β/MidCap 越界要在 v1.4 记分卡里单列（实际持仓口径），不能只报可行日。
- **D8**：A 账簿层闲置现金 6–8%（分红留现 + 整手残余）要单列；C 列执行诊断等 .ok 后再出。

---

live=false · promotion_approved=false · 冻结纸面轨（capacity_adv / B4 / S6）没有碰过 · 没有执行任何项目代码 · 没有 Strategy 交接 · 本文是新文件，写前已确认路径不存在。
