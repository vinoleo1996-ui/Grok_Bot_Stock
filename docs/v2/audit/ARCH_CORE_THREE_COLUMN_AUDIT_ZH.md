# Arch 审计：OPTIMIZER Core 三列 / 双口径 / λ / v0 / N1（只读）
时间：2026-10-14 ≈08:45 ET · Arch · 未改代码 · live=false · 纸面 FROZEN 未动

## 结论
**无 P0；P1×3；P2×5。** 三列定义与 C 列同池/同频/同引擎/同 20% 510300 落实；双口径在 A/C 均有接线，但 **A 列 smoke 输出路径与记分卡读取路径不一致**（不修则 A 永远 PENDING）；**C/B 无密封窗**，三列仅能在 X2 并表。λ 回执中 “INFEASIBLE=0” 被 v0 回退逻辑虚高。v0 **未产生任何业绩数字**（无 NAV/smoke，NOTE 明示 UNSCORED）——无“看结果改规则”证据。N1 五腿 ind_cap_ok_book 全 True。

## 1) 三列落实
| 列 | 产物 | 核查 |
|---|---|---|
| A Core@HI_LIQ | v1.1 权重未全量（`research/optimizer_core_x2_run.py:164` 有意 SystemExit 等 Arch 复签） | PENDING，正确 |
| B capadv mid_large | `output/v3/book_smoke_g1g5_capacity_adv_x2/aum_*/X2/BOOK` | engine=run_weight_schedule+ExecConfig.strategy_v1；510300 均值 0.212 |
| C Top-25@HI_LIQ_V1.1 | 权重 `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_pos_weights.parquet`（脚本 `research/g1g5_capacity_adv_weights_hiliq.py`）；NAV `output/strategy_hiliq/capadv_x2/aum_*/X2/BOOK` | **同池** mask=`universe_mask_hiliq_v1.parquet` sha c5433e80…f1b9af（与 calib/Core 一致，现场 sha256 复核通过），PIT 取 ≤session（:116）；**同频** cadence=month_end_plus_first_last（:819，实测换仓日=月末+首日）；**同引擎成本** ExecConfig.strategy_v1（summary.json）；**同 80/20** 每日 25 只+510300=0.200、Σw=1（实测 668 日恒定） |
差异（设计内，需披露）：C 单票≤4%、行业≤25% 袖；A 单票 5/6%、行业 ±8% vs wb——属"Top-N vs 优化器"构造差，不是池差。

## 2) 双口径
记分卡 `scripts_eng/core_x2_scorecard.py`：② B/C 用原生 BOOK NAV（510300≈20%）；① B/C 为 **派生** ex-510300（:88 `(r−sh·bb)/(1−sh)`），A ① 将是原生 equity_100 跑。15% 补丁 **结构闭合**，但①在 A 与 B/C 间口径不同源（P2）。

## 问题清单
| 级 | ID | 位置 | 问题 | 负责 |
|---|---|---|---|---|
| P1 | T1 | `research/optimizer_core_x2_run.py:171` vs `scripts_eng/core_x2_scorecard.py:70` | A smoke 写 `smoke_{sleeve}_{60w}`，记分卡读 `book_smoke_{sleeve}_{60w}/nav.csv` → A 列永远 PENDING；须统一路径（且 v1.1 产物文件名须明确，避免误读根目录旧 core_*.parquet） | Strategy+Eng |
| P1 | T2 | `scorecard_three_col.md` sealed 行；C 权重仅 2024-01→ | B/C 无密封窗（sealed_refused_by_book_module），三列只能在 X2 并表；而 X2 按纪律"不得晋级"→ Core Stage1 唯一可比证据只剩 X2+FWD。须预注册明示：三列主判定窗=X2(披露)+FWD 2026-11-02；或补 C 密封窗重跑 | Strategy（主 Agent 裁定） |
| P1 | T3 | `research/optimizer_lambda_calib_sealed.py:548-549` | `two_step_polish` step-2 失败 `return r1`（回退 step-1 大篮子）且状态仍 OK → calib "INFEASIBLE=0/24" 被虚高；v0 全量实测 n>30 回退 100万 12 日、20–30 越界过半。λ 数值本身可保留（未用 X2），但"可行率"结论作废，v1.1 须按真实 INFEASIBLE 重报可行率 | Eng |
| P2 | T4 | `core_x2/WEIGHTS_README.md` | 根目录 README 仍描述 v0（Σw 0.715、INFEASIBLE 0、"FROZEN target weights"），与归档 NOTE 冲突；改为 v1.1 或标 SUPERSEDED | Strategy |
| P2 | T5 | `research/strategy_hiliq_capadv_b4_x2.py:38-42` | B4@HI_LIQ 合成仍指向已隔离到 `_rejected_ind_cap/` 的旧腿（195336/195433/195554…），重跑会失败或用错腿；改指 N1 新腿 | Strategy |
| P2 | T6 | `scripts_eng/core_x2_scorecard.py:88` | ① B/C 为派生口径、A 为原生；在报告中标注，或 B/C 另跑原生 100% 股票 | Eng |
| P2 | T7 | ENG λ 回执 §2 | turn 目标回退 monthly_two_way_50pct（capadv 密封 n_obs=5 不足）——合理且符合 Leo 08:20；v0 密封单边中位 0.234≈0.25 吻合。X2 单边 0.31–0.33 仅披露 | Eng（仅披露） |
| P2 | T8 | `scorecard_three_col.md` | B/C X2 数（C ②60万 −0.6%/MDD −29.9%）已在 A 出数前可见；规则已 FROZEN 于此前，v1.1 仅实现修正不改策略/λ——可接受，但 v1.1 复签须确认未据此改任何参数 | Strategy/Arch |

## 3) Eng λ
prepared=24（密封 2018-01→2024-05 均匀取样）✅；x2_returns_used_for_selection=false，calib 窗止于 2024-05-31 ✅；λ_risk=117.213 由 α/风险项比例定标 ✅；turn fallback 合理（T7）；INFEASIBLE=0 不可信（T3）。

## 4) v0
缺陷确认：Σw 中位 0.72–0.95（未满仓）、step-2 失败回退大篮子、20–30 越界。业绩：`_archive_v0` 只有权重/log（log 只含 neff/n/Σw/换手），无 smoke 目录、无 NAV，scorecard A 列 PENDING，docs/TEAM_STATE 无 v0 收益数 → **未被看过**。

## 5) AI N1
五腿 check.json `ind_cap_ok_book=true`：earnings_event 202822、insider_increase 202928、equity_incentive 202436、report_rc_allup 203201、insurer_surv 203108；旧 195554（false）已隔离 ✅。注意 T5 下游仍引用旧腿。
