# QuantMind P0 落地回执

**日期**：2026-10-12 · America/New_York  
**触发**：Leo 批推进（New Bot 转达）  
**门锁**：`promotion_approved=false`；无 GP 进程；无 vendor

---

## 1. 改动文件

| 文件 | 变更 |
|---|---|
| `quantlab/agents/factor_evolve/schemas.py` | FactorCandidate 增双读/冲击/tags；GateResult.tags；`COLUMN_CONTRACT_VERSION`；EvolveRunMeta 扩展 |
| `quantlab/agents/factor_evolve/hard_gates.py` | `HARD_GATE_VERSION=factor_evolve_v2_qm_p0_20261012`；双读 ICIR；冲击@60∧100≥10%；overnight 精神禁；who_pays 仍强制 |
| `quantlab/agents/factor_evolve/weights_from_scores.py` | alias ingest；权威列写出；`build_weight_meta`（stub_window WARN） |
| `quantlab/agents/factor_evolve/run_stub.py` | 合成样例覆盖 pass×2 + fail(who_pays/impact/overnight/textbook) |
| `docs/v2/QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md` | 闸门字段表 + 权重消费约定 |
| `docs/v2/QUANTMIND_P0_LANDING_RECEIPT_ZH.md` | 本回执 |

---

## 2. Smoke 结果

（跑完后填一行；见下文命令输出）

```
cd /workspace/QuantLab && python3 -m quantlab.agents.factor_evolve --smoke --capital 600000 --top-k 5
```

| 项 | 值 |
|---|---|
| hard_gate_version | `factor_evolve_v2_qm_p0_20261012` |
| n_passed | **2** |
| n_failed | **4** |
| n_weight_rows | **50** |
| promotion | false |
| run_id | `fe_20261012_104400_3a7c6ae6` |

预期：2 pass（etf_flow + nb_hold；后者带 `EDGE_WARN_ICIR_DUAL_GAP`）；4 fail（no_who / impact / overnight / textbook）。

---

## 3. 给 AI 的消费约定（三句）

1. 日更请交 `date,instrument,target_weight` → 内部 `session,instrument_id,weight`。  
2. 必须带 `mechanism_tag`（及 who_pays / 双读 / 冲击两档）；缺 tag 拒进辩论。  
3. 完整日更 ≠ 10 日 stub；短窗非 smoke 只 WARN，不算生产 KPI。

---

## 4. 自检

- [x] 无 `gp_reopen` / dense_micro 进程  
- [x] `strategy_promotion_approved=false`  
- [x] 未 clone / vendor QuantMind  
