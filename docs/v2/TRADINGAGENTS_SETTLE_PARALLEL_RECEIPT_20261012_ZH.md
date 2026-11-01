# TradingAgents 辩论扩样 × 结算并行回执

**日期**：2026-10-12（America/New_York）  
**状态**：研究级 · **`strategy_promotion_approved=false`** · **不下单** · **不交 Strategy**  
**约束**：`--no-mock` / `allow_mock=false`；来源仅仓内 `etf_daily_adj`；禁 Yahoo；禁事件臂空转；不伪造收益。

---

## 1. 结论（一句话）

在行情覆盖充足的中大盘/宽基 ETF 上，**辩论扩样与相对 510300 结算已并行跑通**：8 会话×标的 → trading_loop **8/8 settled（非 null）** + debate_ledger **8/8 settled（非 null）**，合计 **16** 条真实 alpha；`settle_source=etf_daily_adj`（非 mock）。

---

## 2. 命令

```bash
cd /workspace/QuantLab

# A) trading_loop：扩 stub 决策 → 真行情结算
python3 -m quantlab.agents.trading_loop.run_stub \
  --session 2024-03-01 --instrument 510500.SH \
  --log output/trading_loop/decision_log_parallel_20261012.jsonl
# …（同批其余 7 条，见下表 session×instrument）
python3 -m quantlab.agents.trading_loop.settle_pending \
  --log output/trading_loop/decision_log_parallel_20261012.jsonl \
  --no-mock

# B) Eng debate_ledger：规则辩论扩样 → ETF 桥接结算
python3 research/ai_debate_memory_runner.py --dry-run --no-settle \
  --instrument 510500.SH --session 2024-03-01 \
  --ledger output/intel/debate_ledger_parallel_20261012.jsonl
# …（同批其余）
python3 research/settle_debate_ledger_vs_510300.py \
  --ledger output/intel/debate_ledger_parallel_20261012.jsonl
# （默认 allow_mock=false；内部调用 trading_loop.settle.compute_horizon_returns）
```

本次回执由一次性并行脚本写出 summary（等价于上列命令批跑）。

---

## 3. 标的与窗

| session | instrument | 覆盖（etf_daily_adj） |
|---|---|---|
| 2024-03-01 | 510500.SH | 2015-01→2026-10 |
| 2024-03-01 | 159915.SZ | 2015-01→2026-10 |
| 2024-04-15 | 510050.SH | 2015-01→2026-10 |
| 2024-04-15 | 512100.SH | 2016-11→2026-10 |
| 2024-06-03 | 510500.SH | 同上 |
| 2024-06-03 | 159919.SZ | 2015-01→2026-10 |
| 2024-09-02 | 588000.SH | 2020-11→2026-10 |
| 2024-09-02 | 510050.SH | 同上 |

- 基准：`510300.SH`  
- 持有窗：`horizon_trading_days=5`（交易日）  
- 未用个股（如 600519）：仓内统一个股 OHLCV reader 仍缺 → 刻意避开，避免 null/造假。

---

## 4. Settle 数字（非 null）

### 4.1 trading_loop（`allow_mock=false`）

| instrument | session | entry→exit | raw | bench | **alpha_vs_510300** |
|---|---|---|---:|---:|---:|
| 510500.SH | 2024-03-01 | 2024-03-01→03-08 | −0.6036% | +0.0850% | **−0.6886%** |
| 159915.SZ | 2024-03-01 | 2024-03-01→03-08 | −1.0704% | +0.0850% | **−1.1554%** |
| 510050.SH | 2024-04-15 | 2024-04-15→04-22 | +0.0814% | −0.4238% | **+0.5052%** |
| 512100.SH | 2024-04-15 | 2024-04-15→04-22 | −0.7529% | −0.4238% | **−0.3291%** |
| 510500.SH | 2024-06-03 | 2024-06-03→06-11 | −0.7178% | −1.0036% | **+0.2858%** |
| 159919.SZ | 2024-06-03 | 2024-06-03→06-11 | −0.9654% | −1.0036% | **+0.0382%** |
| 588000.SH | 2024-09-02 | 2024-09-02→09-09 | −2.2760% | −2.1309% | **−0.1451%** |
| 510050.SH | 2024-09-02 | 2024-09-02→09-09 | −2.9289% | −2.1309% | **−0.7980%** |

汇总：`settled_n=8` · `pending_n=0` · `unavailable_n=0` · 正 alpha 3/8。

### 4.2 debate_ledger（同批、同公式）

与上表数值一致（桥接同一 `compute_horizon_returns`）；Eng 字段名为 `alpha_vs_benchmark`（值=相对 510300）。  
辩论侧评级多为 **Abstain**（消息窗 coverage_gap，规则模板不硬编方向）——结算仍记多头持有窗 raw/alpha，作记忆质量分，非晋级信号。

---

## 5. 产出路径

| 产物 | path |
|---|---|
| trading_loop 决策+结算 JSONL | `output/trading_loop/decision_log_parallel_20261012.jsonl` |
| Eng 辩论账本 JSONL | `output/intel/debate_ledger_parallel_20261012.jsonl` |
| 并行汇总 JSON | `output/trading_loop/settle_parallel_summary_20261012.json` |
| ETF→ledger 结算桥 | `research/settle_debate_ledger_vs_510300.py` |
| 本回执 | `docs/v2/TRADINGAGENTS_SETTLE_PARALLEL_RECEIPT_20261012_ZH.md` |

行情源：`data/v2/etf/etf_daily_adj.parquet`。

---

## 6. 边界（未做 / 不做）

- **不下单、不改主书权重、不交 Strategy、不开 X2、promotion=false**  
- 不把 settled alpha 回填同一 session 的分析师输入  
- 不启用 mock；个股路径仍 coverage_gap，待 PIT 日线 reader  
- 旧 ledger 中 600519 的 null settlement **未改写、不造假**；本批用独立 `*_parallel_20261012` 路径

---

## 7. 备注

并行含义：同批 session×instrument 上 **A 扩 stub / B 扩辩论** 与 **settle** 同一公式、同一 ETF 表；辩论扩样不阻塞结算，结算不依赖 LLM。
