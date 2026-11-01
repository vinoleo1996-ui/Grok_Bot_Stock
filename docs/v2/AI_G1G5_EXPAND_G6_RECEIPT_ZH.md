# AI G1G5 扩池 + G6 回执（中大盘可交易池全日更）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI（后台执行器）  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`** · **不下单** · **不交 Strategy** · **不进 hard_gates 晋级**  
**对照**：`TRADINGAGENTS_DEEP_READ_ZH.md` G6；`AI_G1G5_WIRING_RECEIPT_ZH.md`；`AI_G1G5_WEIGHT_ACCEPT_ZH.md`；`QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md`  
**触发**：Leo 确认卡「启动扩池+G6」；New Bot 授权并行；Book-Smoke 反馈旧 3 标的包 any_pass=false → 扩池为主修复路径

---

## 1. 产物路径

| 产物 | 路径 |
|---|---|
| 全日更权重 | `output/intel/g1g5_expand_daily_weights_20261012_105459.parquet` |
| 运行 meta | `output/intel/g1g5_expand_run_meta_20261012_105459.json` |
| 辩论账本 | `output/intel/debate_ledger_g1g5_expand_20261012_105459.jsonl` |
| G6 证明账本 | `output/intel/debate_ledger_g1g5_expand_20261012_105459_g6_proof.jsonl` |
| 实现 | `research/g1g5_expand_g6.py`；G6 过滤：`research/ai_debate_memory_runner.py`（`load_prior_settlements(as_of=…)` / `settlement_resolved_date`）；`quantlab/intel/debate_ledger.py` 增 `resolution_date` |
| 旧包（对照） | `output/intel/g1g5_daily_weights_20261012_104627.parquet`（3 标的 / 726 行） |

---

## 2. 扩池宇宙定义

| 项 | 值 |
|---|---|
| **`universe_id`** | **`g1g5_mid_large_liquid_top50`** |
| `universe_kind` | `mid_large_stock` |
| 源 | **Data** `data/v2/universe/mid_large_members_pit.parquet`（`universe_id=mid_large`，≠ CSI300） |
| 锚点日 | `2024-06-28` |
| 筛选 | 按 `float_mktcap_basis` 降序；保留有 **D0 panel** 的前 **50**；再平衡日再做 PIT 成员交叉 |
| 再平衡 | 窗首 `2024-01-02` + 各月末（510300 日历），共 13 次 |
| 持仓规则 | 截面 excess_20d vs 510300 排序；**top 20 等权**（日毛敞口=1.0）；非活跃=0 |
| 诚实标注 | **已接 Data mid_large PIT**；top50 可交易子集仍可再做 D3 成员交叉审计（非阻断） |

标的数：**50**（远超旧包 3：600519/601318/000858）。示例：`600519.SH`, `601857.SH`, `601398.SH`, `300750.SZ`, `000858.SZ`, …

---

## 3. 权重表摘要（完整日更 · 非 stub）

| 项 | 值 |
|---|---|
| 行数 | **12100**（242 × 50） |
| 日期跨度 | **2024-01-02 → 2024-12-31** |
| `n_distinct_sessions` | **242**（>10 → **非 stub_window**） |
| `stub_window` | `false` |
| 日毛敞口 | mean=min=max=**1.0**（窗首再平衡后无整月零仓） |
| 活跃名/日 | **20** |
| 列 | `date,instrument,target_weight` + 权威别名 `session,instrument_id,weight` + `mechanism_tag,who_pays_zh,universe_id` |
| **`mechanism_tag`** | **`g1g5_pit_debate_rule_v2_expand`**（行级非空） |
| `who_pays_zh` | 扩池辩论规则模板相对 510300…（行级非空） |
| 契约 | `column_contract_version=weight_long_v1_20261012`（Eng）；alias `weight_long_v1_qm_p0_20261012` |
| `promotion_approved` | **false**（meta + 行语义） |

**禁止**：把本包当 FactorCandidate 进 hard_gates；无双读 ICIR/冲击字段（与袖套定位一致）。

---

## 4. G6 验收（记忆 as_of / resolution_date）

| 项 | 结果 |
|---|---|
| **G6** | **pass** |
| 行为 | `load_prior_settlements(..., as_of=session)` 仅保留 `resolution_date`（否则 exit_date / settled_at 日）**≤ asof** 的 settlement |
| 写入 | `settle_pending` / `settle_pending_g5` 满窗结算写 `resolution_date=exit_date`（本批 18/18） |
| 注入点 | `build_g1g5_debate` / `build_rule_debate` 传 `as_of=sess_d` |
| 证明 | 证明账本植入 past(`2024-03-22`) + future(`2024-07-05`)；asof=`2024-06-28` 时 **future 被挡**、past 保留 |

---

## 5. Ledger / 稀疏辩论（证据，非全宇宙逐日辩论）

| kind | 条数 |
|---|---|
| `debate_turn` | 247 |
| `decision` | 19（6 标的 × 3 会话 + 1 条 2026-06-25 pending 探针） |
| `settlement` | 18（均 `benchmark=510300`，非 null α；均含 `resolution_date`） |
| still pending | 1（`2026-06-25` 未满窗） |

权重曲线由 **截面 PIT 规则再平衡** 生成全日更；稀疏全量 G1–G5 辩论用于机制/记忆回灌证据，避免 50×全日历辩论撑爆 2GB。

---

## 6. 与旧包差异

| | 旧 G1G5 | 本批 expand |
|---|---|---|
| 标的数 | 3 | **50** |
| 行数 | 726 | **12100** |
| sessions | 242 | 242（同日历） |
| mechanism_tag | `g1g5_pit_debate_rule_v1` | `g1g5_pit_debate_rule_v2_expand` |
| universe_id | `g1g5_mid_large_liquid` | `g1g5_mid_large_liquid_top50` |
| 日毛敞口 | 窄截面累加 | **等权 top20 → 1.0** |
| G6 | 弱/未滤 | **pass**（resolution≤asof） |
| Data PIT | 未接 | **已接 mid_large_members_pit** |

Book-Smoke：旧 3 标的 any_pass=false（略逊 510300）。请 New Bot → Beta 用本 parquet 重测。

---

## 7. 资源 / 禁项

| 项 | 值 |
|---|---|
| 峰 RSS | ≈2056012 KB（~2.0 GiB 贴边；已 panel 缓存 + PIT 单次过滤） |
| 结算基准 | **510300** |
| 禁 | Yahoo / Reddit / StockTwits；vendor TradingAgents；v27/事件臂空转；下单；Strategy 交接；hard_gates 晋级 |

---

## 8. 复跑

```bash
cd /workspace/QuantLab
python research/g1g5_expand_g6.py --top-n 50 --active-n 20 \
  --horizon-days 5 --weight-start 2024-01-02 --weight-end 2024-12-31
```

*End. promotion_approved=false. No orders. No Strategy submit. Not a hard_gates candidate.*
