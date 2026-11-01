# AI 辩论结算批次回执（非 null alpha）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI 后台执行器  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`**  
**未做**：下单 · NAV/冒烟 · 交 Strategy · 启 v27 · 事件臂 · Yahoo/Reddit/StockTwits

---

## 1. 交付

| 项 | 路径 |
|---|---|
| Runner（含真价 helper + `--settle-batch`） | `research/ai_debate_memory_runner.py` |
| Eng 契约 | `quantlab/intel/debate_ledger.py` |
| 账本 | `output/intel/debate_ledger.jsonl` |
| 本回执 | `docs/v2/AI_DEBATE_SETTLE_BATCH_RECEIPT_ZH.md` |

**预注册持有窗**：`horizon_days=5`（与 runner `DEFAULT_HORIZON_DAYS` / ROLES 一致；**未**事后改窗刷分）。  
**基准**：`benchmark=510300`（Eng 字段 `alpha_vs_benchmark`）。  
**收益来源**：D0 `data/local_market/1c85…/panels/{sh\|sz}.*.parquet` 的 `feature_close` + `data/v2/etf/etf_daily_adj.parquet` 中 `510300.SH` close。  
**入场/出场**：session 当日或之后首根 bar → +5 个交易日 bar（ex-post 结算；决策本身仍用 session asof 证据）。

---

## 2. ① 非 null settlement（7 条，≥3）

| instrument | session | entry→exit | raw_return | alpha_vs_510300 | decision_id |
|---|---|---|---:|---:|---|
| 600519.SH | 2024-06-28 | 2024-06-28→2024-07-05 | −0.9807% | −0.1490% | `dec_2024-06-28_600519SH_3ace7a25` |
| 601318.SH | 2024-06-28 | 2024-06-28→2024-07-05 | −0.5865% | **+0.2452%** | `dec_2024-06-28_601318SH_6cda5824` |
| 000858.SZ | 2024-06-28 | 2024-06-28→2024-07-05 | +0.7108% | **+1.5425%** | `dec_2024-06-28_000858SZ_f0036532` |
| 600036.SH | 2024-09-30 | 2024-09-30→2024-10-14 | +4.5736% | **+9.1330%** | `dec_2024-09-30_600036SH_808b748f` |
| 000333.SZ | 2024-09-30 | 2024-09-30→2024-10-14 | +3.8655% | **+8.4250%** | `dec_2024-09-30_000333SZ_0b354baa` |
| 601166.SH | 2024-11-29 | 2024-11-29→2024-12-06 | +2.4385% | **+1.0389%** | `dec_2024-11-29_601166SH_3c2e3fe9` |
| 002415.SZ | 2025-01-15 | 2025-01-15→2025-01-22 | +1.2815% | **+1.2042%** | `dec_2025-01-15_002415SZ_27f72b58` |

样例一行（父代理摘要用）：**601318.SH，alpha_vs_benchmark=+0.2452%**（相对 510300，horizon=5）。

全部为仓内真价计算；**未**使用 `--allow-synthetic-returns`。

---

## 3. ② 并行扩辩论样例（本批 +7 轮）

每轮写入 5×`DebateTurn`（`analyst_news` / `analyst_market` / `bull` / `bear` / `research_manager`）+ 1×`DecisionEntry`（pending→settled）。

| # | (session, instrument) | decision_id | rating |
|---|---|---|---|
| 1 | 2024-06-28 × 600519.SH | `dec_2024-06-28_600519SH_3ace7a25` | Abstain |
| 2 | 2024-06-28 × 601318.SH | `dec_2024-06-28_601318SH_6cda5824` | Abstain |
| 3 | 2024-06-28 × 000858.SZ | `dec_2024-06-28_000858SZ_f0036532` | Abstain |
| 4 | 2024-09-30 × 600036.SH | `dec_2024-09-30_600036SH_808b748f` | Abstain |
| 5 | 2024-09-30 × 000333.SZ | `dec_2024-09-30_000333SZ_0b354baa` | Abstain |
| 6 | 2024-11-29 × 601166.SH | `dec_2024-11-29_601166SH_3c2e3fe9` | Abstain |
| 7 | 2025-01-15 × 002415.SZ | `dec_2025-01-15_002415SZ_27f72b58` | Abstain |

**evidence_refs**：优先 `intel.messages` 真实 PIT `event_id`；缺窗则标 `coverage_gap:*`。市场角仍诚实标 D0 panel 路径用于结算、分析师侧不编造动量叙事。  
**未**标 `synthetic_demo`（本批未开 `--synthetic-demo`）。

与①重叠：同批 7 轮既扩样例又完成结算（≥5 轮且 ≥3 非 null）。

---

## 4. decision_id 列表（本批）

```
dec_2024-06-28_600519SH_3ace7a25
dec_2024-06-28_601318SH_6cda5824
dec_2024-06-28_000858SZ_f0036532
dec_2024-09-30_600036SH_808b748f
dec_2024-09-30_000333SZ_0b354baa
dec_2024-11-29_601166SH_3c2e3fe9
dec_2025-01-15_002415SZ_27f72b58
```

---

## 5. 跳过 / coverage_gap

| 项 | 说明 |
|---|---|
| 本批 skipped | **无**（7/7 均有 D0 panel + 510300 覆盖且持有窗已走完） |
| 评级 Abstain | 7/7：`intel.messages` 对应标的窗内无可见公告 → 规则模板不硬编多空 → Abstain；**结算仍用真价**做记忆评分 |
| 市场角 coverage_gap | 分析师侧仍标「个股 OHLCV PIT 统一 reader 未接线」；结算单独走 D0 panel `feature_close`（研究观察，非 PIT 偷看） |
| 历史 null 结算 | 保留 `dec_2024-05-31_600519SH_6d5bcd01`（接线 dry-run 时无价 helper；**未改写**刷分） |
| 未尝试标的 | 无；候选中大盘均命中 panel |

---

## 6. 账本现状（批后）

| kind | 行数 |
|---|---:|
| debate_turn | 40 |
| decision | 8 |
| settlement | 8（其中非 null raw/alpha = **7**） |
| **合计** | **56** |

全行 `promotion_approved=false`。

---

## 7. 禁项核对

| 禁项 | 状态 |
|---|---|
| 下单 / 券商路由 | 未做 |
| NAV / 冒烟 | 未做 |
| 交 Strategy / 晋级权重 | 未做 |
| 启 v27 / 事件臂 | 未做 |
| Yahoo / Reddit | 未接 |
| 伪造收益 | 未做（真价或留 null） |
| 事后改 horizon 刷分 | 未做（固定 5） |

---

## 8. 复跑命令

```bash
cd /workspace/QuantLab
python3 research/ai_debate_memory_runner.py --settle-batch --horizon-days 5
```

*研究级决策质量记忆闭环；非下单系统。*
