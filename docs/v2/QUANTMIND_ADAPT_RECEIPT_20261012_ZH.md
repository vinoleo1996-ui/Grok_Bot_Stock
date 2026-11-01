# QuantMind 适配 + TA 融合 · 回执（2026-10-12）

**角色**：Grok Bot（executor）· 研究级  
**`strategy_promotion_approved`**：`false`（全程）  
**不下单 · 不开密封 · 不联系用户**

---

## 1. 交付清单

| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | QuantMind 适配计划 | `docs/v2/QUANTMIND_ADAPT_PLAN_ZH.md` | ✅ |
| 2 | TA×QuantMind 融合蓝图 | `docs/v2/TA_QUANTMIND_FUSION_ZH.md` | ✅ |
| 3 | 因子演化→权重 stub | `quantlab/agents/factor_evolve/` | ✅ |
| 4 | 本回执 | `docs/v2/QUANTMIND_ADAPT_RECEIPT_20261012_ZH.md` | ✅ |

### stub 文件

- `__init__.py` / `__main__.py`
- `schemas.py` — Candidate / Gate / RunMeta
- `hard_gates.py` — 教科书·小盘·who_pays·本金·无分数
- `weights_from_scores.py` — 截面分 → `session,instrument_id,weight`
- `run_stub.py` — `--smoke` CLI

**未做**：vendor QuantMind/RD-Agent 源码；Docker；Yahoo/Reddit；实盘桥；密封 Book-Smoke 重跑（需另批）。

---

## 2. Smoke 结果（合成面板）

```text
python3 -m quantlab.agents.factor_evolve --smoke --capital 600000 --top-k 5
```

| 字段 | 值 |
|---|---|
| run_id | `fe_20261012_101924_10514de4` |
| capital_cny | 600000 |
| n_candidates | 5 |
| n_passed / n_failed | **2 / 3** |
| **KPI n_weight_rows** | **50** |
| weight_path | `output/factor_evolve/fe_20261012_101924_10514de4_weights.parquet` |
| promotion | false |

硬闸抽样：

| candidate_id | verdict | reasons |
|---|---|---|
| stub_etf_flow_resid_v1 | pass | — |
| stub_nb_hold_delta_v1 | pass | — |
| stub_momentum_fail | fail | textbook |
| stub_smallcap_fail | fail | smallcap_main_banned |
| stub_no_scores_fail | fail | no_score_rows |

权重列契约：`session | instrument_id | weight`（与 `WeightLongTableSleeve` 一致）。

---

## 3. 与既有层关系（防空转）

- **不取代** `quantlab/factors/ai_factory/quantmind_loop.py`（五段式 expr/ledger）  
- **本包 KPI** = 可消费权重行数，专门喂 Book-Smoke  
- **融合口径**见 `TA_QUANTMIND_FUSION_ZH.md` §5：辩论 settle ∧ `n_weight_rows>0` ∧ sleeve 可解析  

---

## 4. 下一步（未授权不跑）

1. Data 真实中大盘/ETF score panel 替换 `_synth_candidates`  
2. Book-Smoke：`--alpha-event-path` + sleeves 拨 `alpha_event` 预算（探索窗）  
3. 辩论 `approve_research` → evolve 队列自动准入  

---

## 5. 跑法（一行）

```bash
cd /workspace/QuantLab && python3 -m quantlab.agents.factor_evolve --smoke
```

产物指针：`output/factor_evolve/latest_meta.json` · `latest_weights.path`
