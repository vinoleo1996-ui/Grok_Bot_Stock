# AI 辩论记忆回灌闭环回执

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI 后台执行器  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`**  
**未做**：下单 · NAV/冒烟 · 交 Strategy · 启 v27 · 事件臂 · Yahoo/Reddit/StockTwits

---

## 1. 目标与交付

强化「记忆结算 → 下次辩论可读」闭环（为日后拼 Book-Smoke 准备；本批仍研究级）。

| 项 | 路径 / 说明 |
|---|---|
| Runner（已升级） | `research/ai_debate_memory_runner.py`（`--memory-loop`） |
| Eng 契约（权威） | `quantlab/intel/debate_ledger.py` |
| New Bot 骨架 | `quantlab/agents/trading_loop/` — **仅对齐接口**；冲突以 Eng `debate_ledger` 为准 |
| 账本 | `output/intel/debate_ledger.jsonl` |
| 本回执 | `docs/v2/AI_DEBATE_MEMORY_LOOP_RECEIPT_ZH.md` |
| 前批结算回执 | `docs/v2/AI_DEBATE_SETTLE_BATCH_RECEIPT_ZH.md` |

---

## 2. 回灌机制（是 / 否 + 证据）

**回灌是否生效：是。**

### 机制

1. `load_prior_settlements(..., non_null_only=True)`：只取同标的 **raw_return 与 alpha_vs_benchmark 均非 null** 的 settlement。
2. `format_memory_block(priors, k=prior_limit)`：拼中文块，含每条 `session` / `decision_id` / `raw%` / `alpha_vs_510300%` / `reflection_zh` 摘录。
3. 无历史时：block 明示 `coverage_gap`，并写入 `coverage_gaps`；`evidence_refs` 含 `coverage_gap:memory_non_null`。
4. **注入目标角色**：`bull` / `bear` / `research_manager` 的 `thesis_zh` 追加完整记忆块；`evidence_refs` 追加 `memory:<prior_decision_id>`。新闻角仍保留压缩版 prior_note（兼容）。
5. 结果对象 stash：`_memory_injected` / `_memory_prior_n` / `_memory_block` 供批跑证据。

### 本批证据（ledger 真写）

对 `dec_2024-10-31_600519SH_9425b185`：

| 角色 | thesis 含 `【记忆回灌` | evidence_refs 含 `memory:dec_2024-06-28_600519SH_3ace7a25` |
|---|---|---|
| bull | 是 | 是 |
| bear | 是 | 是 |
| research_manager | 是 | 是 |

rationale 含「已注入同标的非 null 记忆回灌」。  
批汇总：`memory_injected_rounds=4` / `memory_injection_ok=true`（4/4）。

---

## 3. 本批（新 session，≥3 只有先验非 null 的标的）

预注册 `horizon_days=5`；基准 `510300`；收益来源仍为 D0 panel `feature_close` + `etf_daily_adj` 中 `510300.SH`（**非 Yahoo**）。

| instrument | 新 session | 先验非 null | memory→B/B/RM | entry→exit | raw | alpha_vs_510300 | decision_id |
|---|---|---:|---|---|---:|---:|---|
| 600519.SH | 2024-10-31 | 1 | 是 | 2024-10-31→2024-11-07 | +7.9429% | **+0.9673%** | `dec_2024-10-31_600519SH_9425b185` |
| 601318.SH | 2024-10-31 | 1 | 是 | 2024-10-31→2024-11-07 | +8.7984% | **+1.8228%** | `dec_2024-10-31_601318SH_a0d3f5b7` |
| 000858.SZ | 2024-10-31 | 1 | 是 | 2024-10-31→2024-11-07 | +10.4950% | **+3.5195%** | `dec_2024-10-31_000858SZ_08b578be` |
| 600036.SH | 2024-12-13 | 1 | 是 | 2024-12-13→2024-12-20 | +1.6331% | **+1.6829%** | `dec_2024-12-13_600036SH_28cc24d5` |

- 辩论轮次：**4**（≥3）  
- 新 session 非 null settlement：**4**（窗均已满；skipped=0）  
- 评级：4/4 Abstain（窗内无 PIT 公告证据 → 不硬编；**记忆仍回灌**；结算仍用真价）

### decision_id 列表

```
dec_2024-10-31_600519SH_9425b185
dec_2024-10-31_601318SH_a0d3f5b7
dec_2024-10-31_000858SZ_08b578be
dec_2024-12-13_600036SH_28cc24d5
```

---

## 4. 可消费权重长表扫描

**找到：是（只读引用，未改、未交 Strategy）。**

| 候选 | 说明 |
|---|---|
| **主引用** | `output/strategy_mbook_v2_smoke/X2/BOOK/target_weights.parquet`（长表：`session, instrument_id, weight`；shape≈13110×3） |
| 同族 | `…/BOOK/actual_weights.parquet`、`sleeve_weights.csv`；`…/SA_xd/*` |
| 其它 smoke | `output/strategy_paper_costs/**/target_weights.parquet`、`output/strategy_mbook_ind_mom/**`、`output/strategy_s2/smoke/**`、`output/strategy_mbook_noic_diag/**` |

Runner `OPTIONAL_WEIGHT_TABLE` 指向 BOOK `target_weights.parquet`；市场角可在 `evidence_refs` 标 `weight_ctx:…`（研究上下文，非晋级产出）。本批 meta：`weight_table_cited=output/strategy_mbook_v2_smoke/X2/BOOK/target_weights.parquet`。

---

## 5. 账本现状（本批后）

| kind | 行数 |
|---|---:|
| debate_turn | 60 |
| decision | 12 |
| settlement | 12（非 null raw/alpha 累计 **11**；含早期 dry-run 1 条 null） |
| **合计** | **84** |

全行 `promotion_approved=false`。

---

## 6. 与 trading_loop 对齐说明

- New Bot `quantlab/agents/trading_loop/schemas.py` 使用并行 TypedDict（`DecisionLogEntry` / `alpha_vs_510300` 等）。
- 本 runner **只写** Eng `JsonlDebateLedger`（`kind=debate_turn|decision|settlement`，字段 `alpha_vs_benchmark`）。
- 未改 trading_loop；未把决策写入 Strategy Book。冲突以 Eng 模块为准（本批无 schema 冲突）。

---

## 7. 禁项核对

| 禁项 | 状态 |
|---|---|
| 下单 / 券商路由 | 未做 |
| NAV / 冒烟 | 未做 |
| 交 Strategy / 晋级权重 | 未做 |
| 启 v27 / 事件臂 | 未做 |
| Yahoo / Reddit | 未接 |
| 伪造收益 | 未做 |
| 事后改 horizon 刷分 | 未做（固定 5） |
| 改写权重长表 | 未做（只读路径引用） |

---

## 8. 复跑命令

```bash
cd /workspace/QuantLab
python3 research/ai_debate_memory_runner.py --memory-loop --horizon-days 5 --prior-limit 3
```

*研究级决策质量记忆闭环；非下单系统。QuantMind 融合由 New Bot 另开，本任务未抢。*
