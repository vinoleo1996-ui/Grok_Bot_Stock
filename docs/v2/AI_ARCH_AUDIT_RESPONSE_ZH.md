# QuantLab AI 对 Arch 内部审计（ARCH_INTERNAL_AUDIT_20261014_ZH）的回应

日期：2026-10-14（ET）。live=false，promotion_approved=false，没有改任何权重文件，没有跑 Book-Smoke 和 8787。

## A. 已在本方非冻结代码中修复（#4、#5）
- `research/leaf_selfcheck_common.py`
  - 组合闸门（current/A/B）改为**净收益 + T+1**：T 日的权重在 T+1 开盘成交，与 Eng 的 fill=next_open 对齐。日收益 = (1+Σ旧仓×隔夜)(1+Σ新仓×日内)−1−0.00175×Σ|ΔH|。
  - 复权开盘价 = 原始开盘价 × (复权收盘价 / 原始收盘价)；ETF 用 open_hfq/close_hfq。停牌日没有开盘价时，按前一日收盘价成交。
  - 仍是近似：没有涨跌停拦截，没有参与率上限，终判以 Eng X2 为准。
  - 收益计算从 `pct_change().fillna(0)` 改为 `quantlab.platform.strategy_feed.close_to_close_returns`，停牌期间的涨跌在复牌日兑现。
  - A 臂 β 改为滚动 120 日（最少 60 日），只用 t−1 及以前的数据（PIT）。
  - 成本段保留 alpha_decay_gate 的冻结数值，另增 `net_cagr_t1`。
- 下游同步：`leaf_selfcheck_v3.py`（marginal/GATE_V3 走新的 `_ret`；v2 每次都现算，不再读 meta 缓存）和 `alpha_combo_marginal.py`（CMC 的净值走新的 `_ret`）。
- 年化仍用 252 天（#1 等 Eng 的 `quantlab/metrics.py` 统一后再迁移）。

## B. 冻结代码的问题：只提补丁，不改（都需要新预注册或 Eng FROZEN_CONFIG 重新哈希）
| # | 位置 | 核实 | 补丁建议 | 前置条件 |
|---|---|---|---|---|
| 6 | research/g1g5_earnings_event_weights.py:183 | 已用 ast 核实：断言被解析成 IfExp `X.max() if any else (0.0 <= 0)`，硬排除守卫实际不起作用 | `assert weights.loc[weights.instrument == b, "target_weight"].sum() <= 1e-12, f"hard-exclude {b}"` | 改脚本会改变 sha，需要 Eng 更新 FROZEN_CONFIG 和 leg check.json 里的 frozen_script_sha256，并重新算权重做历史一致性核对（预期逐行一致） |
| 6 | research/g1g5_insider_increase_weights.py:190 | 同上，已用 ast 核实 | 同上 | 同上 |
| 6 | 现有权重 | 已核实：earnings_event 005430/111825、insider_increase 011841/111825、capacity_adv 111219/paper/paper_r2 里 600519、002371 的权重合计都是 **0** | — | — |
| 7 | g1g5_insider_increase_weights.py:2-7 | docstring 写的是"回购注销 / 业绩预告快报"，但代码 :73-76 过滤的是 event_type=insider_increase、标题含"增持"、且主体是控股股东/董监高 | 把 docstring 改为"控股股东/实控人/董监高增持公告（PIT available_at），排除减持/更正/终止等标题"，其余照旧 | 只改注释也会改变 sha，需要 Eng 重新哈希；建议和 #6 一起打包 |
| 18 | g1g5_capacity_adv_weights.py:174-195 | 已核实：adv_yuan = 当日 float_mktcap × turnover_rate / 100，是单日值；AUM_BINDING=100万（:78），60万档共用这一约束 | 改成近 20 个已披露交易日（available_at ≤ session）的均值，最少 10 日；文档写明 60万档沿用 100万档的约束 | 会改变权重和策略，属于新变体：需要新预注册（Leo 批准）、Eng FROZEN_CONFIG 重新哈希、重跑 X2，并重新核对 B4/S6 纸面历史 |
| 5 | research/alpha_decay_gate.py:45（Alpha 冻结） | 已核实：`pct_change(fill_method=None)` 再整体 `.fillna(0)`，停牌期间的涨跌被丢掉 | 改为 `close_to_close_returns(pd.DataFrame({...}))`，只对上市前和退市后的 NaN 填 0 | 需要 Alpha 发新预注册（衰减闸门 v1.1）并重新冻结；影响幅度可参考 capacity_adv 累计 53.80% → 54.07% |

## C. 修复前后对比（叶11–14）
见 output/ai_factory/leaf_reports/<leaf>/：修复前在 `selfcheck_v2_pre_audit.json` / `selfcheck_v3_pre_audit.json`，修复后在 `selfcheck_v2.json` / `selfcheck_v3.json` / `selfcheck_common_after_audit.json`。

| 叶 | GATE_V3 前→后 | cagr>cap 60万/100万 前→后 | +20% 于 cap ΔCAGR 60万/100万（pp）前→后 | CMC ΔCAGR 净 vs B4 60万/100万（pp）前→后 | CMC 负年数 前→后 | 组合闸门 current/A/B 前→后 |
|---|---|---|---|---|---|---|
| report_rc_allup | 过→过 | ✓✓→✓✓ | +0.45/+1.55 → +0.16/+1.23 | −0.18/+0.56 → −0.20/+0.49 | 2,0→2,0 | ✗✗✗→✗✗✗ |
| analyst_recoverage | 不过→不过 | ✗✓→✗✗ | −2.22/+0.77 → −8.13/−6.20 | −10.39/−7.18 → −9.39/−7.25 | 3,3→3,3 | ✗✗✗→✗✗✗ |
| stk_surv | 不过→不过 | ✓✓→✗✓ | +0.20/+0.40 → −0.02/+0.11 | −0.73/−0.62 → −0.80/−0.80 | 3,3→2,3 | ✗✗✗→✗✗✗ |
| insurer_surv | 不过→不过 | ✓✓→✓✓ | +0.57/+1.23 → +0.24/+0.79 | −0.67/−0.06 → −0.70/−0.27 | 2,2→2,2 | ✗✗✗→✗✗✗ |
（CMC 里的 ΔIC 和 ΔICIR 不受收益引擎影响，数值不变。）
