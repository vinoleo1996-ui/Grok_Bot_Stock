# Eng 回执：v1.3 记分卡审计修复（docs/v2/ARCH_V1_3_SCORECARD_AUDIT_ZH.md，sha eab8ff78…）

- 编写：QuantLab Eng，2026-10-18 01:3x ET。**只改了生成器代码和披露文字，没有渲染**（Arch 规则：无 .ok 不执行）。现存 `scorecard_three_col.md`（5b9250d2…）仍是 00:51 ET 版本，**修复要等 Arch 给 .ok 后跑 `--disclosure-only` 才会体现在 md 里**。收益数字不重算。
- 生成器：`scripts_eng/core_x2_scorecard.py` a401107c… → **14167702…**（改前副本 `_recovery/eng/scripts_eng/core_x2_scorecard.pre_auditfix_a401107c.py`）。py_compile 通过。
- 重启前死掉的 worker（sand-subagent-1c16771e…）**没有落盘任何 P1-2 / P2 修复**（生成器里查不到 P2 文字），所以全部是这次新改，不是复核。它落盘的只有：runner-pin 接入（4 个 runner + ok_runner_pin.py）、S2-3 diff 和改前重建件、各 S2-3 目录的 VOID_PENDING_DIFF.md、c_col_exec_diagnostic.py（未运行，无产物）。

| 项 | 改法 | 依据 / 核对 |
|---|---|---|
| P1-1 | S2-3 节加 ⛔ VOID_PENDING_DIFF 标注和实际运行代码 sha 3d4b08e3…；diff 交 `docs/v2/eng_s2_3/`；ok_runner_pin 改严格模式（未钉 sha 也拒跑） | patch 打到改前重建件上逐位得到 3d4b08e3…（= MANIFEST code sha） |
| P1-2 | 新节「审计补充披露」：B/C 两档成交率、闲置现金、总敞口、交易只数（渲染时从各 book summary.json 读）；列出三列不可比之处（A 月度 vs B/C 日度目标；B top300 静态锚 vs A/C HI_LIQ；B/C 引擎 sha 未钉；C 执行层差）；原因拆解指向 c_col_exec_diagnostic.md（待 .ok） | 读数核对：C 60万 0.547 / 23.8% / 0.76 / 233；B 60万 0.970 / 9.3% / 0.91 / 43，与 Arch 一致；另 C 100万 0.614 / 13.5% / 0.86，B 100万 0.969 / 5.3% / 0.95 |
| P2-1 | 置顶引擎标注改写为 Arch 核实的机制（停牌禁止成交、卖单顺延、复牌一次性实现涨跌、无退市终值；停牌事件 A 15/10、B 10、C 13 名·日，退市 0；偏差可忽略），并注明 00:49 原标注已被取代 | Arch P2-1 原文 |
| P2-2 | 写明月胜率 = 完整自然月，X2 28 个月（2024-06 以首个交易日为基点算完整；2026-10 只到 10-09 剔除）；Arch 29 个月口径并列说明 | quantlab/metrics.py monthly_returns(complete_only=True) |
| P2-3 | 超帽分母改为可行行：28/96、18/81（代码同步：不再 dropna 首日行） | 读 core_v1_3_disclosure.csv 复核：60万 28/96、100万 18/81 |
| P2-4 | v1.2 可行性节标题加「【已被 v1.3 取代】」，并注明「100万 X2 全部可行」只属 v1.2 | — |
| P2-5 | 2025-06→07 段：改为「已确认，长度 2 <k=3，不进置顶」，保留长度 2 失败段那一行 | Strategy 10-18 裁定 |
| P2-6 | sh.511880 = book 层现金停泊：`quantlab/portfolio/v2_multisleeve_book.py` 第 34 行 CASH_ETF、第 459–460 行把未投资预算停到 511880；行情取自 etf_daily_adj（第 76 行），不走股票读取器 | 文件 sha 6adefbeb…；A 100万 ② 174 个名·日持有，权重中位 3.3%，最大 4.5% |
| P2-7 | B run_id book_smoke_20261013_111418，C run_id book_smoke_20261014_200345（run.log 首行 20:03:46 ET）；两次都没记录引擎 sha，事后钉不住，标为已知缺口 | summary.json engine = run_weight_schedule + ExecConfig.strategy_v1 |

- 手工备注 sidecar `scorecard_notes_manual.md`（b84a705c…）未改；Strategy「行业偏离相对全池 wb」那行仍在。
- 清单补记：`core_x2/v1_3_RUN_MANIFEST.json` 是冻结件，没有改；新增附录 `core_x2/v1_3_RUN_MANIFEST_ADDENDUM_20261018_ENG.json`。
- live=false · promotion=false · 纸面未动。

## 追加 r2（2026-10-18 01:4x ET；按 Arch 审查 4698a2c1…）
- **κ（SD0 引擎 quantlab/platform/execution.py 373fed30…）**：线性部分买 2.5bp、卖 7.5bp，按单边均摊 κ≈5bp/边；510300 为 2.5bp/边。行号见 _recovery/eng/RECOVERY_REPORT_ZH.md §6，Arch 已逐行核实。
  - 另有两项约束**不计入 κ**：
    1. 参与率上限 `participation_cap=0.10`：execution.py L347（`strategy_v1` 的 kw）。成交量不足时订单顺延，不是成本。
    2. book 层最小成交额 `min_trade_value=2000`：`quantlab/portfolio/v2_multisleeve_book.py`（6adefbeb4e66bdd8856c748180b09fa0fbf071d8fe20f6ccdd70ff37a4a603b4）L477 `exec_cfg`。名义额低于 2000 元的订单直接跳过。
  - 冲击按 sqrt 计（k=1），也不属线性 κ。
- **更正（Arch P3）**：Origin `leo-vino/QuantLab` main 最新提交 7197939d（2026-10-15 10:25:33 ET）的作者/提交人是 **Leo vino**（合并 PR #2；被合并的 ff5cddc5 由 Cursor Agent 提交），不是 QuantLab Frontend。只有 `leo-vino/QuantLab-data`（2f4f77a9，10-15 22:36:59 ET）是 Frontend (agiuser) 推的。
- **S2-3**：主 Agent 已解除 VOID_PENDING_DIFF，并要求披露 00:48 前版本是重建件、只做过循环验证。说明文件在 `docs/v2/eng_s2_3/VOID_LIFTED_20261018_*.md`。运行目录被 manifest 记录，所以没往里写；目录里的 VOID_PENDING_DIFF.md 保持原样。生成器的 S2-3 标注已改为「已解除 VOID（第 00:48 前版本为重建件，仅循环验证）」，门槛 FAIL 不变。仍未渲染。
- **生成器 r2**：`scripts_eng/core_x2_scorecard.py` 14167702… → **a85444eea3686c4933a584a6fa71f178d0d216032777588d6a6608e06c7cd5de**。
  - 新增 `--out-tag`（必填），输出 `scorecard_three_col_<tag>.md/.md.gen`。
  - 受保护文件（md、md.gen、csv、notes_manual）一律不写；`scorecard_notes_manual.md` 只读，手改行不再追加。
  - 门控 = RESIGN + S2_3_RELEASE + ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok，mode=disclosure_only，dep 钉 metrics、trade_calendar、ok_runner_pin。
  - 前一版副本：`_recovery/eng/scripts_eng/core_x2_scorecard.auditfix_14167702.py`。
- **ok_runner_pin** b302911b… → **c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485**：只认 64 位全长；每份 .ok 都须 live=false、promotion=false；缺 .ok 拒跑；执行 allow_* 检查；校验 dep；未知键忽略。
- **新增** `scripts_eng/overcap_recount_v1_3.py`（4dd66271f5bd38853568cf653477e10bc0518a3f3e3e5bee33750f7846eadeee）：独立复算 28/96、18/81，不 import pandas 或 quantlab，未运行。
- **c5** d61f50f2…：不带 `--tag` 拒跑。**c_col** e9e42f14…：暂缓，门控通过后才 import execution。
- 申请：`_recovery/eng/OK_REQUEST_ENG.md`（r2）。

## 追加 r3（2026-10-18 01:5x ET；Arch 附录 C 8b50f6c0…）
- **记分卡** a85444ee… → **2aa03a8f99477073950f33ff366acbb7aec876e9025a3994ca0a407e0ad089ae**，out-tag = `auditfix_20261018_2aa03a8f`。
  - P1-3：tag 须带本脚本 sha8 后缀。
  - P2-5：输出用 open(path,"x") 独占新建。
  - P2-6：quantlab.metrics 在门控通过后才 import。
  - P2-7：dep pin 增加 11 项（portfolio/__init__ 的全部传递导入）。
  - P3：披露节说明 95/80 与 96/81 的差异。
- **复算脚本** 4dd66271… → **ff4ac3f0251d04c34408f12092d75c00c79b5353e84c1f0359e5c3b3c046794d**，out-tag = `auditfix_20261018_ff4ac3f0`。分子和两种分母原样输出，附 rows_without_turnover 和差异说明。
- **超帽分母差异**：首个 HARD 可行行 2018-01-31（两档）无前一期权重，one_way_opt 为空。不计这一行得 95/80（冻结 RESIGN .ok 第 16 行），计入得 96/81（Arch P2-3）。2018-01-02 是 NO_DATA_CARRY，两种口径都不计。
- **sd0_parity_runner** → 4b9c30a4…：门控加了 modes=parity_<suite> 和 10 项 dep；新增 unit/pytest 套件。SD1_SHAS.txt → a8b9df45…。
- 申请见 `_recovery/eng/OK_REQUEST_ENG.md` r3。
