# AI G1–G5 接线回执（本地 PIT 辩论 + 满窗结算 + 全日更权重）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI（后台执行器）  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`** · **不下单** · **不交 Strategy** · **未改 Alpha 工厂**  
**对照**：`docs/v2/TRADINGAGENTS_DEEP_READ_ZH.md` G1–G5；`docs/v2/QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md`（`factor_evolve_v2_qm_p0_20261012`）

---

## 1. 产物路径

| 产物 | 路径 |
|---|---|
| 辩论账本 | `output/intel/debate_ledger_g1g5_20261012_104627.jsonl` |
| 全日更权重 | `output/intel/g1g5_daily_weights_20261012_104627.parquet` |
| 运行 meta | `output/intel/g1g5_run_meta_20261012_104627.json` |
| 实现模块 | `research/g1g5_wiring.py`（由 `research/ai_debate_memory_runner.py --g1g5` 可调） |
| G5 修补 | `research/ai_debate_memory_runner.py`：`settle_pending` **未满窗不再写 settlement** |

---

## 2. Alpha 消费约定对齐（必须写清）

### 2.1 列名最终口径

| 侧 | 列 | 本批 |
|---|---|---|
| **AI 日更（入口）** | `date`, `instrument`, `target_weight` | ✅ 已写 |
| **权威别名（出口 / Book-Smoke / 辩论 ingest）** | `session`, `instrument_id`, `weight` | ✅ 同行附带（`instrument_id`=panel 形 `sh./sz.`） |
| 契约版本 | `column_contract_version=weight_long_v1_qm_p0_20261012` | ✅ meta 已标 |
| 闸门版 | `hard_gate_version=factor_evolve_v2_qm_p0_20261012` | ✅ meta 已标 |

**禁止**：把 Alpha `factor_evolve` 的 10 日 stub（`n_weight_rows=50`）前推冒充生产日更。本批日历来自 **510300** `etf_daily_adj` 交易日，覆盖 **2024-01-02 → 2024-12-31**（**242** 个 distinct session，**非 stub**）。

### 2.2 `mechanism_tag`（强制）

| 字段 | 值 |
|---|---|
| **`mechanism_tag`** | **`g1g5_pit_debate_rule_v1`** |
| `who_pays_zh` | 辩论规则模板相对 510300 的持有窗 alpha 由错误定价修正对手盘支付；非事件臂、非隔夜因子。 |
| 权重行 | 每行非空 `mechanism_tag` + `who_pays_zh` |
| 辩论 evidence | thesis/refs 含 `mechanism:g1g5_pit_debate_rule_v1`；缺 tag 包拒消费（与 P0 一致） |

**闸门候选专用字段**（`icir_eps_gate` / `icir_eps_posthoc` / `impact_flat25_pct_60万` / `impact_flat25_pct_100万`）：属 `FactorCandidate` 硬闸路径，**本批未冒充因子候选交闸**；G1G5 权重是**辩论规则袖套**对照导出。若 Alpha 要将本表当 evolve 候选 ingest，需另补双读 ICIR + 冲击两档——**不在本回执范围、不替 Alpha 改工厂**。

### 2.3 `universe_id`

| 字段 | 值 |
|---|---|
| **`universe_id`** | **`g1g5_mid_large_liquid`** |
| `universe_kind` | `mid_large_stock` |
| 标的 | `600519.SH`, `601318.SH`, `000858.SZ`（D0 panel 覆盖充足） |

说明：既有 `factor_evolve/latest_meta.json` **无** `universe_id` 字段；本批自研导出显式写入，便于 Alpha 拒接裸表。

### 2.4 promotion

- `promotion_approved=false`（权重行 / ledger / meta 恒 false）  
- `strategy_promotion_approved=false`  
- 不下单、不交 Strategy、不启 v27、不跑事件臂空转  

---

## 3. 权重表摘要

| 项 | 值 |
|---|---|
| 行数 | **726**（242 日 × 3 标的） |
| 日期跨度 | **2024-01-02 → 2024-12-31** |
| `n_distinct_sessions` | **242**（>10 → **非 stub_window**） |
| `stub_window` | `false` |
| 列 | `date,instrument,target_weight,mechanism_tag,who_pays_zh,universe_id,session,instrument_id,weight` |
| 权重映射 | Buy0.08 / OW0.05 / Hold0.02 / UW0.01 / Sell·Abstain·REVIEW=0；决策日前 =0（非 stub 前推） |

---

## 4. G1–G5 逐条验收

| ID | 结果 | 证据 |
|---|---|---|
| **G1** | **pass** | 四报：`analyst_news`（messages PIT）+ `analyst_market`（D0 panel 量价）+ `analyst_sentiment` + `other`（财报 `ann_date≤asof`）；缺窗 `coverage_gap`；账本扫描 **零** yfinance/stocktwits/via-yahoo 引用 |
| **G2** | **pass** | 情绪角色显式 `sentiment:coverage_gap`（S1 未齐）；禁 Reddit/StockTwits |
| **G3** | **pass** | `max_debate_rounds=2` → bull/bear 各 2（`bull_bear_count=4`）+ `research_manager` 入 ledger |
| **G4** | **pass** | `risk`×3（Aggressive/Conservative/Neutral）→ `portfolio_manager` 终评；Abstain/REVIEW **不**记成 Hold（本批样本为 Hold/Underweight） |
| **G5** | **pass** | `horizon_days=5` 可配；`2026-06-25` **仍 pending**（未写 settlement）；满窗 9 笔相对 **510300** 非 null α |

---

## 5. Ledger 摘要

| kind | 条数 |
|---|---|
| `debate_turn` | 130（10 轮 × 13 turns：四报+4辩论+RM+3风险+PM） |
| `decision` | 10（pending→9 settled + 1 仍 pending） |
| `settlement` | 9（均 `benchmark=510300`，`alpha_vs_benchmark` 非 null） |

评级分布：Hold×6，Underweight×4。

---

## 6. 与 Alpha 对齐说明（不替 Alpha 改工厂）

1. 列 alias 与 P0 契约一致：AI 入口 `date,instrument,target_weight` ↔ 权威 `session,instrument_id,weight`。  
2. **必带** `mechanism_tag=g1g5_pit_debate_rule_v1`；辩论 evidence 已注入 `mechanism:<tag>`。  
3. 既有 `output/factor_evolve/fe_*_weights.parquet` 仍为短窗 stub（50 行）；**本批未消费/前推该 stub**；G1G5 自建 242 日全日更。  
4. `factor_evolve` 包级缺 `mechanism_tag` 时，辩论仅 WARN 作研究引用，**不**当 Alpha 生产输入。  
5. **未**修改 `quantlab/agents/factor_evolve/*` 硬闸/工厂代码。  

---

## 7. 资源 / 禁项

| 项 | 值 |
|---|---|
| 峰 RSS（本跑） | ≈2051480 KB（~2.0 GiB 贴边；后续可缓存 panel/财报过滤） |
| 结算基准 | **510300**（`etf_daily_adj`） |
| 行情 | 本地 D0 panels（`feature_close`） |
| 禁 | Yahoo / Reddit / StockTwits；vendor TradingAgents 整仓；v27；事件臂空转；下单 |

---

## 8. 复跑

```bash
cd /workspace/QuantLab
python research/g1g5_wiring.py --horizon-days 5 --max-debate-rounds 2 \
  --weight-start 2024-01-02 --weight-end 2024-12-31
# 或
python research/ai_debate_memory_runner.py --g1g5 --horizon-days 5
```

*End. promotion_approved=false. No orders. No Strategy submit. No Alpha factory edits.*


---

## 9. Alpha ACCEPT（2026-10-12 ~10:48 ET）

- 裁决文：`docs/v2/AI_G1G5_WEIGHT_ACCEPT_ZH.md` → **ACCEPT（辩论权重袖套）**
- meta sidecar 已补：`promotion_approved=false`；`column_contract_version=weight_long_v1_20261012`（Eng 权威）+ `column_contract_version_qm_alias=weight_long_v1_qm_p0_20261012`
- 非阻断缺口保留：窄 3 标的；无双读 ICIR/冲击（勿进 hard_gates）；宇宙待 Data D3
- 不扩 ACTIVE；不交 Strategy；不启 GP
