# V35 Data 轻量规划：回购 / 预告·快报 / 质押（PIT + X1）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab Data |
| 范围 | **仅规划**；**不开**新重型拉数（当前 acquire：moneyflow + db2014 + 4×bs_shard + anns 等） |
| 窗 | X1 = **2015-06-01 → 2017-12-31**（与 AI V35 阻断备忘一致） |
| promotion_approved | **false**（数据层口径不变；不触策略层） |
| 依据 | `docs/v2/AI_NEXT_ARM_COVERAGE_BLOCKED_MEMO_V35_ZH.md` |

## 1. 现状（盘内）

| 维 | 现状 | X1 |
|---|---|---|
| 回购 | `events/announcements_classified_pit` 有 buyback 子类，但 ann 自 **2018**；无独立 `repurchase` PIT | **0** |
| 预告/快报 | 无 `smallcap_events`；em_yjbb seed≈2024+；disclosure_date raw 自 2018Q1 | **0** |
| 质押 | 无 `pledge*` raw/PIT | **0** |

## 2. 目标契约（解阻后 AI 可提案）

共用要求：`instrument_id`/`ts_code` 可 join 中大盘；**`available_at` 可证伪**；覆盖完整 X1；**≠** 解禁窗 / V34 披露日历 / V31 调样同构。

### 2.1 回购 `events/repurchase_pit.parquet`（优先）
- 源：Tushare `repurchase`（首选）或 cninfo 标题回补 2015-06→2017-12
- 键：`ts_code`, `ann_date`, `end_date`/`proc` 进度字段（以接口实有列为准）
- `available_at`：公告日 **Asia/Shanghai 18:00**（若仅有 ann_date）
- 验收：X1 事件数>0；∩ float top800 密度可报；不复用 `share_float.float_date`

### 2.2 业绩预告/快报 `events/forecast_express_pit.parquet`
- 源：Tushare `forecast` + `express`（优于仅 BaoStock）
- 锚点：预告/快报 **自身 ann_date**，须证明 **≠** `financials_available_at` 首次披露同构（V34 硬禁）
- `available_at`：ann_date 当日 18:00 Asia/Shanghai
- 验收：X1>0；与 V34 披露日重叠率报告；极性字段若缺则标 research

### 2.3 股权质押 `events/pledge_events_pit.parquet`（或日频+事件差分）
- 源：Tushare `pledge_stat`（日频率）+ 若有 `pledge_detail`/解质押事件接口则事件表
- 事件定义优先：**解质押**、**质押率跳变**（阈值后定），非裸持仓快照当 Alpha 叶
- `available_at`：stat 日 T+1 09:00 或公告日 18:00（按源语义写清）
- 验收：X1 覆盖；中大盘密度；无表则保持 GAP 不伪造

## 3. 执行队列（等现有重型降载后）

**现在禁止开拉。** 建议顺序（控峰后单路）：

1. **回购**（V35 机制匹配最高）— 探活 `repurchase` → raw by ann → PIT
2. **forecast/express** — 探活 → X1 窗 raw → PIT + 与 V34 重叠审计
3. **pledge** — 探活 → 定事件定义 → PIT

并行约束：与 moneyflow / db2014 / BS 并存时 **不加第四类**；anns 现有 loop 不扩到回购全量。

## 4. 非目标（本规划不做）
- 不跑 V35 冒烟 / GP / 回测
- 不动 Strategy / Beta / `promotion_approved`
- 不把解禁 `share_float`、披露日历、指数调样包装成「新叶」

## 5. 回执句（完成后给 AI/New Bot）
- 有：`path` + X1 事件数/只 + available_at 规则 + promotion=false
- 无源：`GAP` + 已探接口 HTTP/字段证据，不虚构

下一动作：重型（MF/db2014/BS）降到 ≤2 路后再按 §3 开第一路回购探活。
