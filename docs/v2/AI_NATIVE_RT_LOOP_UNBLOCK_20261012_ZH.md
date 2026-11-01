# AI-Native 研究级实时闭环（不下单）· 打通清单

**角色**：Grok Bot（executor）· 研究级  
**时间**：2026-10-12 ~22:56 ET（America/New_York）  
**门锁**：`promotion_approved=false` · `strategy_promotion_approved=false` · **不下单** · **不启 GP** · **不叠新 uvicorn**（8787 由 Data/Leo 管）  
**AUM 报告口径**：60万 ∧ 100万  
**成功标准**：可执行打通清单 + 至少一条端到端 dry-run 证据（本页已满足）

---

## 0. 一句话

研究链 **G1–G5 → 全日更权重 → Alpha 短裁 → Book-Smoke（可 skip-run）** 在契约层已通；  
「实时闭环」缺的是：**日更入口/健康检查 glue（本批已补）**、**D2 moneyflow ACCEPT（Data）**、**辩论 approve→evolve 自动入队（Eng/AI 二期）**、**工厂主循环解冻出新正交叶（AI，已另派）**。  
数字闸（满窗 ≥12%）与密封/晋级 **不在本页范围**。

---

## 1. 已通 / 未通清单（每条 1 行 + 证据）

| 状态 | 项 | 证据路径 |
|---|---|---|
| **已通** | 权重长表契约 `session\|instrument_id\|weight` + AI 别名 | `quantlab/platform/weight_long_table.py` · `docs/v2/QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md` |
| **已通** | TradingAgents 状态机 stub + settle α@510300（无 LLM/不下单） | `quantlab/agents/trading_loop/` · `docs/v2/TRADINGAGENTS_ADAPT_RECEIPT_20261012_ZH.md` |
| **已通** | QuantMind 风格硬闸→权重 stub（`--smoke`） | `quantlab/agents/factor_evolve/` · `docs/v2/QUANTMIND_ADAPT_RECEIPT_20261012_ZH.md` |
| **已通** | 骨架一键：`trading_loop→factor_evolve→weight→book_smoke --skip-run` | `docs/v2/SKELETON_ONECLICK_ZH.md` · `output/v3/skeleton_smoke/skeleton_smoke_summary.json` |
| **已通** | G1–G5 本地 PIT 辩论接线 + 全日更权重导出 | `research/g1g5_wiring.py` · `docs/v2/AI_G1G5_WIRING_RECEIPT_ZH.md` |
| **已通** | 机制包日更样例（idx_rebal_flow，668 日，stub=false） | `output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet` |
| **已通** | Alpha 研究级 ACCEPT（idx_rebal；不交 Strategy） | `docs/v2/AI_G1G5_IDX_REBAL_FLOW_WEIGHT_ACCEPT_ZH.md` |
| **已通** | Local Data API 8787 health（v1.2.0，oom_safe） | `curl http://127.0.0.1:8787/health` · `services/local_data_api/` |
| **已通** | D1 valuation / D3 mid_large ACCEPT；D4 IOPV GAP ACCEPT | `docs/v2/ALPHA_DATA_D1D4_STATUS_ACCEPT_ZH.md` |
| **已通（本批 glue）** | RT 健康检查 + dry-run 入口（到可消费权重为止） | `scripts/rt_loop_health_dryrun.py` · `output/v3/rt_loop_dryrun/rt_loop_health_dryrun_summary.json` |
| **未通** | **D2 moneyflow 全量 ACCEPT**（仍在拉，缺约 325/2127 日） | `logs/moneyflow_stock_loop.log` · `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet`（末 RG max≈20250610） |
| **未通** | 辩论 `approve_research` → `factor_evolve` **自动入队** | `docs/v2/TA_QUANTMIND_FUSION_ZH.md` §3.3「二期」 |
| **未通** | 真 QuantLab AI 工厂主循环持续产新正交叶（交接冻点 ~02:03） | `output/alpha/AI_FACTORY_HANDOFF_TO_QUANTLAB_AI_ZH.md`（两叶已另派 AI） |
| **未通** | trading_loop **真 LLM** 填分析师/辩论节点 | `docs/v2/TRADINGAGENTS_ADAPT_RECEIPT_20261012_ZH.md` §4 |
| **未通** | Embedding 日级 store / 消息→嵌入产品化日更 | `docs/v2/SYSTEM_ARCH_V3_AI_NATIVE_ZH.md` §3 |
| **未通** | WorkBuddy 四角色正式采纳（仍 DRAFT） | `docs/v2/ALPHA_WORKBUDDY_PIPELINE_ZH.md` |
| **未通（故意）** | 实盘下单 / promotion=true / 密封窗自动过 | 全仓门锁；本闭环 **永不**自动打开 |
| **未通（数字闸）** | 满窗 Book-Smoke 过 12% 门锁进主书 | 七包已烟均未过闸；属研究结论，非 glue |

---

## 2. 本批已做（glue）

1. **入口脚本** `scripts/rt_loop_health_dryrun.py`  
   - 探测 Data API `/health`（**不**启服）  
   - 权重契约 `schema_handshake`  
   - 校验生产级全日更 parquet（默认 idx_rebal_flow）  
   - 可选跑 `skeleton-smoke`（trading_loop→factor_evolve→book_smoke skip-run）  
   - 只读提示 D2 moneyflow 进度（不加载全表）  
2. **端到端证据**（2026-10-12 22:56 ET）：`ok=true`，耗时 ≈1.3s  
   - Data API v1.2.0 ok  
   - 生产权重：3243 行 / **668** sessions / stub=false / promotion=false  
   - skeleton：`n_weight_rows=50`（smoke stub，契约可消费）  
   - 摘要：`output/v3/rt_loop_dryrun/rt_loop_health_dryrun_summary.json`

### 可执行命令

```bash
cd /workspace/QuantLab

# 研究级实时闭环 health + dry-run（推荐日检）
PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py

# 只验 API + 契约 + 既有生产权重（更轻）
PYTHONPATH=. /workspace/qlvenv/bin/python scripts/rt_loop_health_dryrun.py --skip-skeleton

# Eng 骨架一键（与上者共用）
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli skeleton-smoke

# 分项
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli factor-evolve --smoke
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli book-smoke --skip-run

# Data API（只读；勿叠新进程）
curl -sS --max-time 3 http://127.0.0.1:8787/health
```

**日更权重生产入口（机制包，非 stub）**：各 `research/g1g5_*_weights.py`（由 QuantLab AI 跑；本批不重跑重型 peak≈2GB 包）。  
消费侧：Alpha `validate` / ACCEPT 文档 → Beta Book-Smoke（需 Leo 确认才派满窗烟）。

---

## 3. 卡点（仍未通 Top3）

| # | 卡点 | Owner | 下一步 |
|---|---|---|---|
| 1 | **D2 moneyflow 未 ACCEPT**（pull missing≈325/2127；盘上 max≈2025-06-10） | **Data** → Alpha 全量 ACCEPT | 拉完至最新后给正式交付句；未 ACCEPT 前资金流叶勿当满样本 |
| 2 | **辩论 approve → evolve 自动入队** 未接线 | **Eng / AI**（二期） | 一期继续手工 mechanism 白名单；自动入队需契约 PR（勿 force-push） |
| 3 | **工厂主循环冻点** / 下一正交叶 | **QuantLab AI**（已派两叶） | 解冻产新 X2 权重；禁 GP/resid同构/etf_core/摩擦换皮；promotion=false |

**不卡本闭环 glue 的项**：8787 已由 Leo「现在重启」拉起；人工登录/券商桥 **不在** 研究级不下单闭环内。

---

## 4. 下一步需谁做

| Who | 做什么 | 不做 |
|---|---|---|
| **Data** | 完成 moneyflow 缺口 → 交付句 → 等 Alpha D2 ACCEPT；保持 8787；OOM 仍停服等 Leo | 不自启第二 API；不宣称 D2 已 ACCEPT |
| **QuantLab AI** | 两叶正交机制 → 全日更 `date,instrument,target_weight` + who_pays；G6；禁同构 | 不启 GP；不交 Strategy；不升主书 |
| **Alpha** | 权重短裁；D2 拉完后 ACCEPT；禁把 stub≤10 日当生产 | 不启 GP；promotion=false |
| **Beta** | Leo 确认后 Book-Smoke @60∧100万 vs 510300 | 不满窗烟除非确认；不改门锁数字 |
| **Eng** | （可选）approve→evolve 队列接线 PR；保持 weight 契约 | 不改 promotion_gate；不大改未经批 force-push |
| **Strategy** | 无 | 本闭环不交可执行仓 |
| **Leo** | 确认开烟 / 点选工厂叶 / 再令重启 API | — |

---

## 5. 与「全部打通」的边界（诚实）

| 含义 | 本页是否覆盖 |
|---|---|
| 契约层：辩论 stub → 权重 → Book skip-run 可日检 | ✅ 已打通（glue + 证据） |
| 数据层：moneyflow 满样本可进资金流叶 | ❌ 仍卡 Data D2 |
| 产叶层：工厂持续出新过正交包 | ❌ 仍卡 AI 主循环（已派） |
| 数字层：满窗 expand≥12% 进主书 | ❌ 研究闸，非 glue |
| 交易层：实盘/模拟下单闭环 | ❌ **明确不做**（本页 locks） |

---

## 6. 相关文档

- 架构：`SYSTEM_ARCH_V3_AI_NATIVE_ZH.md` · `TA_QUANTMIND_FUSION_ZH.md` · `SKELETON_ONECLICK_ZH.md`
- 适配回执：`TRADINGAGENTS_ADAPT_RECEIPT_20261012_ZH.md` · `QUANTMIND_ADAPT_RECEIPT_20261012_ZH.md`
- 数据：`ALPHA_DATA_D1D4_STATUS_ACCEPT_ZH.md`
- 融合验收口令：近 24h settle 非空 α **且** `factor_evolve` `n_weight_rows>0` **且** 权重可被 `WeightLongTableSleeve` 解析（见 Fusion §5）

**全文研究级 · 未晋级 · 不下单。**
