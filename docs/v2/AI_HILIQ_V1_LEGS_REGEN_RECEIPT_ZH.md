# AI HI_LIQ Arch N1 行业超限修复回执

- 时间：2026-10-14 ≈08:33 ET（箱钟 CST≈20:33）
- 请求：Arch N1 P1 + 主 Agent（全超限事件腿重生）+ Alpha 硬断言
- 约束：未动 FROZEN_CONFIG / 纸面轨 / FULLA 腿；live=false；不自跑 Book-Smoke

## 根因与修复

1. **根因**：事件腿用事件日粘性行业（sticky）做 `maxn`，持仓日 PIT 申万一重映射后账面可到 0.28（equity_incentive 21 日）。
2. **修复**：`research/hiliq_ind_cap.py` — 持仓日 PIT 行业；袖预算口径 book_cap=`min(0.25, 0.25×0.80)=0.20`（maxn=5）；超限按比例缩放并把溢出按信号序再分配到未触顶行业（预注册 §2）。
3. **硬断言**：构造后 `assert_ind_caps`；`finalize_all.py` 要求 `ind_cap_ok_book`∧`ind_cap_ok_sleeve`，否则 RuntimeError。
4. **capacity_adv**：仅改 docstring（≤28%/k=2%→袖≤25%/k=0.6%）并标注 FULLA_* 实为 HI_LIQ（Arch N4/N5）；未改逻辑、未重生该腿。

## 五腿新戳（旧 195* 已迁 `_rejected_ind_cap/`，含 equity 195554 REJECT）

| 腿 | 戳 | sha前缀 | max_book | max_sleeve_budget | ok_book | ok_sleeve | X2均持股 |
|---|---|---|---|---|---|---|---|
| earnings_event | `20261014_202822` | `6bb3b3f3160e` | 0.2 | 0.25 | True | True | 16.25 |
| insider_increase | `20261014_202928` | `c4b93255b694` | 0.2 | 0.25 | True | True | 20.0 |
| equity_incentive | `20261014_202436` | `df9fa57c754d` | 0.2 | 0.25 | True | True | 20.0 |
| insurer_surv | `20261014_203108` | `057f02eaa78b` | 0.2 | 0.25 | True | True | 19.99 |
| report_rc_allup | `20261014_203201` | `16db6b15d4a4` | 0.2 | 0.25 | True | True | 15.28 |

## X2 申万一袖份额（电子/计算机/通信/医药生物）

| 腿 | 电子 | 计算机 | 通信 | 医药生物 |
|---|---|---|---|---|
| earnings_event | 23.9% | 4.6% | 7.9% | 4.2% |
| insider_increase | 6.5% | 4.4% | 0.8% | 10.2% |
| equity_incentive | 18.8% | 8.1% | 3.4% | 9.8% |
| insurer_surv | 17.0% | 7.3% | 4.4% | 8.5% |
| report_rc_allup | 13.4% | 8.2% | 2.9% | 8.3% |

## 说明

- `max_sleeve_frac` = 行业账面 / 股票袖预算 0.80（与 capacity_adv `IND_CAP_STOCK_SLEEVE` 同口径）；`max_sleeve_frac_among_held` 为当日实际持仓内份额（稀疏日可为 1.0，不作硬闸）。
- peak RSS：equity≈1320MB；earnings≈1562；insider≈1702；insurer≈1311；report_rc≈3409（向量化合并，超 1.5GB 软顶，weights-only）。
- 交 **Alpha** 按 `ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md` §2.1 重验；通过后通知 Strategy 合成。不派 Book-Smoke。
- 叶18 由其他 worker 处理，本回执不涉及。
