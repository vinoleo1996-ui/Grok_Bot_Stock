# AI 辩论 · QuantMind 权重上下文 + 记忆回灌 回执

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI 后台执行器  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`**  
**未做**：下单 · NAV/冒烟 · 交 Strategy · 启 v27 · 事件臂 · Yahoo/Reddit/StockTwits · 改写权重长表

**对齐**：`docs/v2/TA_QUANTMIND_FUSION_ZH.md` · Eng `quantlab/intel/debate_ledger.py` · `WeightLongTableSleeve` 列契约（仅文档/解析对齐，**不**跑 Book-Smoke）

---

## 1. 目标与交付

把 QuantMind `factor_evolve` **可消费权重长表**注入辩论输入，并继续同标的非 null settlement 记忆回灌；相对 510300 事后结算。

| 项 | 路径 / 说明 |
|---|---|
| Runner（已升级） | `research/ai_debate_memory_runner.py`（`--weight-context` / `--memory-loop`） |
| 融合蓝图 | `docs/v2/TA_QUANTMIND_FUSION_ZH.md` |
| Eng 契约（权威） | `quantlab/intel/debate_ledger.py` |
| 账本 | `output/intel/debate_ledger.jsonl` |
| 本回执 | `docs/v2/AI_DEBATE_WEIGHT_CONTEXT_RECEIPT_ZH.md` |
| 前批记忆回灌回执 | `docs/v2/AI_DEBATE_MEMORY_LOOP_RECEIPT_ZH.md`（要点并入下文 §7） |
| 前批结算回执 | `docs/v2/AI_DEBATE_SETTLE_BATCH_RECEIPT_ZH.md` |

---

## 2. 权重长表（只读）

| 项 | 值 |
|---|---|
| **路径** | `output/factor_evolve/fe_20261012_101924_10514de4_weights.parquet` |
| **指针** | `output/factor_evolve/latest_meta.json` → `weight_path`；`latest_weights.path` |
| **run_id** | `fe_20261012_101924_10514de4` |
| **行数** | **50**（`n_weight_rows=50`） |
| **列契约** | `session, instrument_id, weight` |
| **Sleeve 解析** | `WeightLongTableSleeve._load()` → **`book_consumable`**，`n_rows=50`（仅验证可解析；**未**挂主书、**未**下单） |
| **窗口（stub）** | 2024-06-03 … 2024-06-14（meta: `X2_stub_2024-06..2024-07`） |
| **标的样例** | `sh.600519` / `sh.601318` / `sz.000858` / `sh.600036` / `sh.601166` / ETF 等 |

加载逻辑：`resolve_factor_evolve_weight_path()` → `load_weight_long_table()` → `lookup_instrument_weight(asof≤session)`。  
**禁止**：把 weight 当成交价；写 Strategy；改 parquet。

---

## 3. 回灌 + 权重上下文是否生效

### 3.1 记忆回灌：**是**

1. `load_prior_settlements(..., non_null_only=True)`  
2. `format_memory_block` → `【记忆回灌·最近K条非null结算】` + reflection 摘录  
3. 注入 `bull` / `bear` / `research_manager` 的 `thesis_zh`；`evidence_refs` 含 `memory:<prior_decision_id>`

本批：`memory_injected_rounds=5` / `memory_injection_ok=true`（5/5）。

### 3.2 权重上下文：**是**

1. 读 `latest_meta.json` 指向的 factor_evolve 权重长表  
2. `format_weight_context_block` → `【权重上下文·QuantMind factor_evolve】session=… weight=…`  
3. 注入 `analyst_market` + `bull` / `bear` / `research_manager`；`evidence_refs` 含 `weight:<id>@<session>=<w>`  
4. 无该标的行时明示 `coverage_gap:weight_ctx`（本批 5 标的均命中）

本批：`weight_injected_rounds=5` / `weight_injection_ok=true`（5/5）。

### 3.3 单条证据（ledger）

对 `dec_2024-11-15_600519SH_58ed1d1b`：bull/bear/RM thesis 同时含 `【记忆回灌` 与 `【权重上下文`；refs 含先验 `memory:dec_*` 与 `weight:sh.600519@2024-06-14=0.200000`。

---

## 4. 本批（≥3；优先有权重 ∪ 有历史 settlement）

预注册 `horizon_days=5`；基准 **510300**；收益 = D0 panel `feature_close` + `etf_daily_adj` 中 `510300.SH`（**非 Yahoo**）。

| instrument | session | 先验非null | mem→B/B/RM | wt→Mkt/B/B/RM | weight hit | entry→exit | raw | alpha_vs_510300 | decision_id |
|---|---|---:|---|---|---|---|---:|---:|---|
| 600519.SH | 2024-11-15 | ≥1 | 是 | 是 | sh.600519@06-14=0.2 | 11-15→11-22 | −3.2829% | **−0.7675%** | `dec_2024-11-15_600519SH_58ed1d1b` |
| 601318.SH | 2024-11-15 | ≥1 | 是 | 是 | sh.601318@06-13=0.2 | 11-15→11-22 | −4.9590% | **−2.4436%** | `dec_2024-11-15_601318SH_0c31f400` |
| 000858.SZ | 2024-11-15 | ≥1 | 是 | 是 | sz.000858@06-11=0.2 | 11-15→11-22 | −4.2302% | **−1.7148%** | `dec_2024-11-15_000858SZ_2be0c760` |
| 600036.SH | 2024-12-20 | ≥1 | 是 | 是 | sh.600036@06-12=0.2 | 12-20→12-27 | +3.7755% | **+2.5560%** | `dec_2024-12-20_600036SH_8352c0e6` |
| 601166.SH | 2024-12-06 | ≥1 | 是 | 是 | sh.601166@06-10=0.2 | 12-06→12-13 | −1.8404% | **−0.9284%** | `dec_2024-12-06_601166SH_ddf68035` |

- 辩论轮次：**5**（≥3）  
- 非 null settlement：**5**（skipped=0）  
- 评级：5/5 Abstain（窗内无 PIT 公告 → 不硬编；**记忆+权重仍注入**；结算仍用真价）

### decision_id 列表

```
dec_2024-11-15_600519SH_58ed1d1b
dec_2024-11-15_601318SH_0c31f400
dec_2024-11-15_000858SZ_2be0c760
dec_2024-12-20_600036SH_8352c0e6
dec_2024-12-06_601166SH_ddf68035
```

---

## 5. Book-Smoke / WeightLongTableSleeve（仅文档对齐）

| 项 | 状态 |
|---|---|
| 列契约与 Sleeve 一致 | 是（`session,instrument_id,weight`） |
| Sleeve 解析本路径 | `book_consumable` / 50 行 |
| 挂 `--alpha-event-path` / `--stock-path` 跑主书 | **未做**（等 Leo 允探索窗；本批不下单） |
| 辩论 approve → evolve 队列自动入 | 仍二期（蓝图 §3.3） |

融合验收口令对照（蓝图 §5）：

1. 近窗有非 null α settlement — **是**（本批 5）  
2. `latest_meta.json` 的 `n_weight_rows>0` — **是**（50）  
3. Sleeve 可解析 — **是**  
→ 管线「活着」；**仍非密封晋级**。

---

## 6. 账本现状（本批后）

| kind | 行数 |
|---|---:|
| debate_turn | 85 |
| decision | 17 |
| settlement | 17（非 null raw/alpha 累计 **16**；含早期 dry-run 1 条 null） |
| **合计** | **119** |

全行 `promotion_approved=false`。

---

## 7. 自 `AI_DEBATE_MEMORY_LOOP_RECEIPT_ZH.md` 合并要点（勿丢）

- 记忆回灌机制已通：非 null only → 中文块 → bull/bear/RM；无历史则 `coverage_gap`。  
- 前批 memory-loop 4 轮（2024-10-31 / 12-13）均已注入并结算出非 null α。  
- 旧 `OPTIONAL_WEIGHT_TABLE` 曾指向 BOOK `target_weights.parquet`（研究引用）；**本批主路径改挂 factor_evolve**（融合蓝图 KPI），BOOK 路径仅作缺失时兜底引用。  
- New Bot `trading_loop` 并行 TypedDict；本 runner **只写** Eng `JsonlDebateLedger`（`alpha_vs_benchmark`）。  
- 禁项：不下单、不 NAV、不交 Strategy、不启 v27、不接 Yahoo、不伪造收益、不事后改 horizon。

---

## 8. 禁项核对

| 禁项 | 状态 |
|---|---|
| 下单 / 券商路由 | **未做** |
| NAV / Book-Smoke 冒烟 | **未做** |
| 交 Strategy / 晋级权重 | **未做** |
| 启 v27 / 事件臂 | **未做** |
| Yahoo / Reddit | **未接** |
| 伪造收益 / 改 horizon 刷分 | **未做**（固定 5） |
| 改写 factor_evolve 权重 | **未做**（只读） |
| 把 weight 当成交价 | **未做**（仅 thesis/refs 上下文） |

---

## 9. 复跑命令

```bash
cd /workspace/QuantLab
python3 research/ai_debate_memory_runner.py --weight-context --horizon-days 5 --prior-limit 3
# 等价：--memory-loop（现已含权重注入）
```

*研究级：辩论上下文消费 QuantMind 权重长表 + 记忆结算闭环；非下单系统；promotion=false。*
