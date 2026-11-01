# TradingAgents ↔ QuantLab 时点（PIT）对照

**角色**：AI / Eng 对照 · 研究级 · `promotion_approved=false`  
**日期**：2026-10-12 · America/New_York  
**代码**：`quantlab/intel/asof_window.py`、`quantlab/data_os/pit.py`、`quantlab/intel/messages.py`

---

## 1. 概念对齐

| TradingAgents 概念 | QuantLab 概念 | 适配规则 |
|---|---|---|
| `as_of` / trade date 钳制工具 end | `trade_session` + `asof_decision_ts` | 工具/reader 结束日不得晚于决策 session |
| `in_window` | `filter_frame_asof` / `visible` | 只保留 `available_at` ≤ 决策时刻的行 |
| `coverage_gap` | attrs / meta `coverage_gap` | 未观测 ≠ 无新闻；必须显式字符串 |
| withhold live-only | 历史回放拒绝无时间戳文本 | 无 `available_at` 的文本在历史 run 直接拒绝 |
| 记忆 settlement 持有窗 | `SettlementRecord.horizon_days` | 窗长预注册；禁止事后改窗 |

---

## 2. 时钟与默认 cutoff

| 项 | QuantLab 约定 |
|---|---|
| 市场 | A 股 · `Asia/Shanghai` |
| 会话决策默认 | **当日 18:00** 墙钟（`asof_window._DEFAULT_SESSION_CUTOFF`） |
| 收盘可知（行情） | `data_os.pit.session_available`：CN 约 **15:00** 转 UTC（行情类） |
| 公告粗糙精度 | 仅有公布日时可用当日 **23:59:59** 本地，并标记精度（`publication_available`） |
| 舆情 S1 | 建议 `available_at` ≥ T 18:00 或次日开盘前；信号最早 T+1（见 `S1_SENTIMENT_INTERFACE.md`） |

辩论层统一用 **`asof_decision_ts`**（建议 18:00），与消息 reader 的 `trade_session=` 接线一致；不要混用「收盘 15:00 当文本已全部可知」。

---

## 3. 对照表示例

```
决策 session = 2024-03-15
asof_decision_ts = 2024-03-15 18:00 Asia/Shanghai（墙钟）

可用：available_at ≤ 2024-03-15 18:00 的公告/嵌入/舆情行
丢弃：available_at > 该时刻（前瞻）
strict_asof=True：前瞻行 → ValueError(pit_lookahead)
coverage_gap：该源在窗内无采集 → 元数据声明，禁止写「无利空」
```

---

## 4. 与晋级的关系

- PIT 通过 **只** 说明「没有偷看未来」，**不** 等于 `dataset_promotion_approved` 或 `strategy_promotion_approved`。  
- 辩论 settlement 的 alpha **不是** Strategy 密封证据。  
- 本适配文档阶段：`strategy_promotion_approved=false`；不开 NAV/冒烟。

---

## 5. 待 Eng 定（勿捏造）

- 外部 `.SS`/`.SZ` → 内部 instrument 映射表模块名  
- settlement 收益/复权统一 helper 路径  
- `output/intel/` 是否另增按日分区（当前默认单文件 JSONL）

*研究级。时点纪律优先于故事完整性。*
