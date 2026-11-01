# Eng 指标口径统一回执（架构审计 P1#1）2026-10-14
live=false；未重跑任何回测，只用现有 NAV 重算；冻结权重、FROZEN_CONFIG 和 pin 哈希均未改动（被 pin 的脚本没有一个被修改）。

## 新增 quantlab/metrics.py（唯一口径来源）
- 年化 PERIODS=244（A 股）。CAGR=(末/初)^(244/日收益数)-1；Sharpe/vol 取 rf=0、ddof=1、×√244；MDD 在 NAV 路径上计算；Calmar=CAGR/|MDD|。
- 提供日胜率；月胜率按 SSE 日历剔除首尾不完整月，输出里带 `monthly_note` 说明剔除了哪些月。X2 窗口剔除 2026-10，共 28 个月；2024-06 的首日 06-03 是当月第一个交易日，算完整月。

## 已切换的模块（改前备份和 sha：output/loop/_metrics_unify/）
- Eng 侧：quantlab/portfolio/b4_paper.py（`_stats`、换手年化）、v2_multisleeve_book.py（`metrics`，原本就是 244，结果不变）、scorecard.py（原先 CAGR 按自然日/365.25 计，月胜率含不完整月；现全部改走 metrics，meta 和 md 中注明口径）、v2_strategy_paper.py（252→244）、quantlab/research_statistics.py（252→244；win_rates 剔除不完整月，并新增 monthly_note）。
- **研究侧脚本（请 Alpha/AI 知悉）**：
  - research/leaf_selfcheck_common.py：`_m`、成本段的 CAGR 和成本拖累年化由 252 改为 244，叶自检数字会小幅下降，约 0.6pt。
  - research/alpha_decay_gate.py：仅 net_cagr/b_cagr 的年化改为 244。预注册锁定的 WIN=252 日窗口和 α=截距×252 **未改**，改动需要 Alpha/Leo 另行批准。PREREG_SHA 未变。
  - 两份冻结门的预注册写的是「按 leaf_selfcheck_common 定义」。AI 那一节写的是「252 主报/244 对照」，现在主报已变为 244，请 AI 核对。
- 未改：research/*_v1_1.py、leaf_selfcheck_v3.py 等变体，以及 output/alpha 下的一次性脚本（列入待办）。v2_strategy_paper 在盒子上因为缺 scipy 无法 import（这是既有问题），本次只做了 py_compile 校验。

## 记分卡新旧对比（主要轨道 X2；CAGR/MDD/Calmar 取自引擎 summary，原本就是 244，所以不变）
| 轨道 | AUM | 段 | CAGR% | MDD% | Calmar | 月胜率% 旧→新 | 月胜 C0% 旧→新 |
|---|---|---|---|---|---|---|---|
| capacity_adv | 60万 | X2 | 13.82 | -10.07 | 1.37 | 51.72→50.00 | 48.28→46.43 |
| capacity_adv | 100万 | X2 | 12.23 | -11.62 | 1.05 | 58.62→57.14 | 48.28→46.43 |
| B4 | 60万 | X2 | 15.11 | -13.85 | 1.09 | 62.07→64.29 | 58.62→57.14 |
| B4 | 100万 | X2 | 14.24 | -13.17 | 1.08 | 55.17→57.14 | 58.62→57.14 |
| S6 | 60万 | X2 | 17.15 | -11.95 | 1.43 | 62.07→64.29 | 58.62→57.14 |
| S6 | 100万 | X2 | 16.37 | -12.66 | 1.29 | 58.62→60.71 | 62.07→60.71 |
| leaf11 cap80+rc20 | 60万 / 100万 | X2 | 13.54 / 14.73 | -13.02 / -11.90 | 1.04 / 1.24 | 58.62→60.71 / 51.72→53.57 | 48.28→46.43 |
| conc_v2 CORE | 60万 / 100万 | X2 | 13.69 / 13.83 | -12.57 / -11.66 | 1.09 / 1.19 | 58.62→60.71 / 48.28→50.00 | 51.72→50.00 / 48.28→46.43 |

完整对比见 output/loop/_metrics_unify/old_vs_new.md。X2H 段太短，CAGR 和 Calmar 仍记 missing（不足 5 个收益日），总收益和 MDD 不变。

## 待办（P2，本次未做）
- #5 停牌收益置 0（leaf_selfcheck、alpha_decay_gate）→ 改用 close_to_close_returns（AI）
- #6 硬排除 assert 优先级 bug（AI）
- #7 insider docstring（AI）
- #8 静态股票池（Data/AI）
- #9 参与率用当日全天成交量（Eng）
- #10 冲击成本缺失 fail-open（Eng）
- #11 可交易性面板缺数据即放行（Eng/Data）
- #12 个股退市价（Data/Eng）
- #13 N 字段改名（Strategy）
- #14 冻结后改动的治理（Strategy/Beta）
- #15 截止时间常量：Eng 已统一为 CUTOFF_ET，Data 侧仍是 20:00 上海
- #16 本次已顺带完成
- #17 日历驱动的扩展加 WAITING 告警
- #18 单日 ADV
- 研究侧变体脚本（*_v1_1、leaf_selfcheck_v3、output/alpha/*.py）迁移到 metrics
