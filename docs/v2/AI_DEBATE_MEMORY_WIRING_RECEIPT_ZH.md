# AI 辩论 + 记忆结算接线回执

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI 后台执行器  
**状态**：研究级桩已接线 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`**  
**未做**：下单 · NAV/冒烟 · 交 Strategy · 启 v27 · 克隆 TradingAgents 整仓 · Yahoo/Reddit/StockTwits

---

## 1. 交付路径

| 项 | 路径 |
|---|---|
| Runner | `research/ai_debate_memory_runner.py` |
| Eng 契约（唯一 schema） | `quantlab/intel/debate_ledger.py` |
| 账本 JSONL | `output/intel/debate_ledger.jsonl` |
| 角色/总览/PIT 规格 | `docs/v2/TRADINGAGENTS_ADAPT_{ROLES,OVERVIEW,PIT}_ZH.md` |
| 本回执 | `docs/v2/AI_DEBATE_MEMORY_WIRING_RECEIPT_ZH.md` |

选择 `research/` 而非 `quantlab/intel/`：与既有 `research/ai_factor_*.py` 惯例一致；intel 包保持 Eng 契约，AI 消费侧放 research。

---

## 2. 与 New Bot `trading_loop` 骨架冲突时的裁决

| 点 | New Bot `quantlab/agents/trading_loop/` | **本接线（胜出）** |
|---|---|---|
| 决策/结算 schema | `DecisionLogEntry`、`alpha_vs_510300` | Eng `DecisionEntry` / `SettlementRecord`、**`alpha_vs_benchmark` + `benchmark`** |
| 默认日志路径 | `output/trading_loop/decision_log.jsonl` | **`output/intel/debate_ledger.jsonl`** |
| 角色枚举 | `AnalystBrief` / `side=bull\|bear` | Eng `DebateRole`（`analyst_news` / `analyst_market` / `bull` / `bear` / `research_manager`） |

**裁决**：与 New Bot 骨架冲突时以 `quantlab/intel/debate_ledger.py` 为准（父代理转向 + AI 规格明示）。  
**相对基准**：结算必须相对 **510300**；写入 Eng 字段为 `benchmark="510300"`（或 `510300.SH` 前缀族）与 `alpha_vs_benchmark`，**不**另写 `alpha_vs_510300` 平行字段。  
New Bot `TRADINGAGENTS_MEMORY_SETTLE_SPEC_ZH.md` / `settle.py` 仍可作收益算法参考，但本桩 **不双写** 其 decision_log，避免两套账本。

---

## 3. Runner 行为（最小可运行）

1. **读** `prior settlements`（同标的，截断最近 K 条）注入分析师上下文。  
2. **写** 一轮 `DebateTurn`：`analyst_news` + `analyst_market` + `bull` + `bear` + `research_manager`（规则/模板中文可证伪论点；**不调外部 LLM**）。  
3. `make_pending_decision` → `JsonlDebateLedger.append_turns` / `append_decision`。  
4. `settle_pending` 桩：默认 **dry_run 不伪造收益**；无价格 helper → `raw_return=null`、`alpha_vs_benchmark=null` + `reflection_zh` 说明 `coverage_gap`；接口接受调用方注入的真实/研究收益；`--allow-synthetic-returns` 才写 demo 零收益并标明 `synthetic_demo`。  
5. 可选上下文：若存在 `output/strategy_mbook_v2_smoke/X2/BOOK/target_weights.parquet`，仅作 **weight_ctx 路径引用**（不下单、不改权重、不作晋级产出）。

### Dry-run 命令

```bash
cd /workspace/QuantLab
python3 research/ai_debate_memory_runner.py --dry-run \
  --instrument 600519.SH --session 2024-05-31
```

成功标志：stdout 打印 `decision_id`；`output/intel/debate_ledger.jsonl` 增行（turns + decision + settlement）；所有行 `promotion_approved=false`。

---

## 4. 本次 dry-run 结果

| 字段 | 值 |
|---|---|
| `decision_id` | `dec_2024-05-31_600519SH_6d5bcd01` |
| 标的 | `600519.SH`（沪深300 成分 · 中大盘样例） |
| session | `2024-05-31`（asof 默认 18:00） |
| rating | `Hold` |
| ledger 行 | 5×`debate_turn` + 1×`decision` + 1×`settlement` |
| settlement.benchmark | `510300` |
| raw_return / alpha_vs_benchmark | `null` / `null`（coverage_gap，未伪造） |
| promotion_approved | **false**（全行） |

### coverage_gap（诚实标注）

- `intel.messages`：窗内有 PIT 可见公告（已引用 `event_id`）；reader attrs 另提示 lookback 前缘服务范围说明（非「无新闻」）。  
- **个股 OHLCV PIT 统一 reader 未接线**（仓内可见 `data/v2/etf/etf_daily_adj.parquet`，不足支撑个股持有窗收益）→ settlement 收益留空。  
- 未启用 `--synthetic-demo` / `--allow-synthetic-returns`（本次为实盘公告证据 + 空收益结算桩）。

API 仍可调用：`build_rule_debate`、`append_round`、`settle_pending(..., raw_return=, alpha_vs_benchmark=)` 供后续接 Eng/Data 收盘 helper。

---

## 5. 禁项核对

| 禁项 | 状态 |
|---|---|
| 下单 / 券商路由 | 未做 |
| NAV / 冒烟证明辩论 | 未做 |
| 交 Strategy / 写晋级权重长表 | 未做（仅只读引用既有 smoke 权重路径作上下文） |
| 启 v27 / 垃圾事件臂空转 | 未做 |
| Yahoo / Reddit / StockTwits | 未接 |
| vendor TradingAgents 整仓 | 未克隆 |
| 抬升 promotion | 恒 false |

---

## 6. 下一步（另批，非本回执范围）

- Eng/Data：个股 PIT 收盘统一 helper 后，将 `settle_pending` 从 null 升级为真实 raw/alpha（仍研究级）。  
- WorkBuddy：把规则模板换成只读 PIT 的提示词技能（仍写同一 ledger）。  
- 与 `trading_loop`：若需收敛，由 Eng 定迁移/双写策略；在此之前 AI 只写 `debate_ledger.jsonl`。

*研究级。辩论与记忆是决策质量闭环，不是下单系统。*
