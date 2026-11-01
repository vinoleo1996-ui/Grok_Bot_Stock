# Alpha → Data 需求单（QuantMind 深读衍生）

**日期**：2026-10-12 · America/New_York  
**来源**：`docs/v2/QUANTMIND_DEEP_READ_ZH.md`（HEAD `7d8019c`）  
**角色**：QuantLab Alpha 提需求；**QuantLab Data 专责交付**  
**门锁**：`promotion_approved=false`；不下单；不开密封；**不 vendor QuantMind/QuantDB**  
**主线**：个股残差 + ETF；中大盘；禁小盘主仓；资本档 60万∧100万  

> 说明：下列只列 **数据缺口**。闸门双读 / 冲击 / 族 ρ / who_pays 属 Alpha/AI 契约，不进本单。

---

## 已有（本单不重复催）

| 资产 | 路径（摘要） | 备注 |
|---|---|---|
| 估值日频 pe/pb/ps/mv | `data/v2/valuation/daily_basic_valuation_tushare.parquet` | 有 pe_ttm/pb；**缺 available_at 契约确认**（见 D1） |
| EP PIT | `data/v2/ep/ep_pit_daily_tushare.parquet` | 接受单已写无未来泄漏 |
| 流通市值 | `data/v2/float_mktcap/*` | 日频+asof；Z 用 log float mcap |
| 申万一级成分史 | `data/v2/sw_l1_pit/*` | 中性化行业维 |
| 两融 | `data/v2/margin/rzrq_daily_tushare.parquet` 等 | 已有 |
| 北向汇总/持股 | `data/v2/northbound/*` | **≠** 个股 moneyflow |
| ETF 份额/NAV PIT | `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet` | **IOPV 仍缺** |
| 指数成分月度快照 | `data/v2/index_members/index_weight_csi300_500_1000.parquet` | 调样公告日仍弱 |

---

## 新需求（按优先级）

### D1 · P0 · 估值/日频基础表 PIT 契约补全

**要什么**：对 `daily_basic_valuation_tushare`（及同类日频基础）明确并落盘：

- `available_at`（或等价：可在开盘前用于决策的最早本地时间）
- `session` / `trade_date` 语义文档一行
- 若日频基本面实际是 T+1 09:00 才可用，请写进 manifest，并保证 join 用 `available_at` 而非裸 `trade_date`

**为何（QuantMind 对照）**：上游把 `$pe/$bp/$float_mv` 直接灌进 `daily_pv.h5` 给当日 eval；无 PIT 会在我们闸门下被 Data 专责 FAIL。

**验收**：manifest 含 `available_at` 规则；抽样 3 日 asof join 无未来泄漏（仿 EP 接受单）。

---

### D2 · P0 · 个股资金流（moneyflow / netflow）PIT

**要什么**：A 股个股日频资金流长表，至少：

- `session, instrument_id, buy_elg_amount, sell_elg_amount, net_mf_amount`（或 Tushare `moneyflow` 同口径字段）
- 可选分档：超大单/大单/中单/小单净流入
- **`available_at`**（通常下一交易日开盘前）
- 覆盖目标：2018-01-02 → 最新；沪深主宇宙（北交所可后置）

**路径建议**：`data/v2/moneyflow/moneyflow_stock_daily_pit.parquet` + `manifest.json`

**为何**：QuantMind `_ENRICH_FEATURES_DAILY` 白名单含 `netflow_*`；仓内目前只有 **HSGT** moneyflow，**没有个股 moneyflow**。

**验收**：行数/标的数/日期范围写入 manifest；与 deep read 对照「禁止无 as_of 的 QuantDB 富化列」。

---

### D3 · P0 · 中大盘可交易宇宙成员 PIT

**要什么**：研究级 `universe_id=mid_large` 成员史：

- 列：`session`（或 `in_date/out_date`）, `instrument_id`, `universe_id`, `available_at`
- 规则文档：市值分位/指数成分/流动性门槛（Data 定可复现规则；Alpha 不绑 CSI300 默认）
- **显式声明**：此宇宙 ≠ CSI300；小盘/微盘/北交所默认排除出主仓宇宙

**路径建议**：`data/v2/universe/mid_large_members_pit.parquet`

**为何**：QuantMind `AShareAdapter` 硬绑 `market=csi300`；我们短清单/冲击闸要求中大盘 ∩ 可交易池。现仅有 `announcements/.../universe_top1500_yearend.csv` 等非 PIT 成品。

**验收**：任选 5 个 session，成员数稳定、可复现；与 float_mktcap 交叉无大量微盘误入。

---

### D4 · P0 · ETF IOPV（盘中估值）PIT

**要什么**：ETF IOPV 时序（至少日终或分钟采样可研究级），带 `available_at`；覆盖主线行业/宽基 ETF（与 `etf_share_flow_pit_all` 交集优先）。

**为何**：份额/NAV PIT 已到；A2 臂与定价机制仍缺 IOPV（既有记忆/A2 报告已记 missing）。

**验收**：与 NAV 同标的可对齐；文档写清频率与延迟。

---

### D5 · P1 · 指数调样「公告日」补强

**要什么**：沪深300/中证500/中证1000 调样事件补 `ann_date`（或证监会/中证官网公告日），使 `index_member_events` 不只依赖相邻月度快照夹逼。

**为何**：QuantMind/事件臂与 V31 指数再平衡研究需要「可知日」；现状 Tushare 无公告日（见 `ALPHA_DATA_REQUESTS_STATUS` #3）。

**验收**：2018+ 主要 6/12 月调样批次有 ann_date；未知则显式 `ann_date` 空并标 `quality_status`。

---

### D6 · P1 · 配股（rights issue）PIT

**要什么**：配股实施表（公告日/除权日/配股价/比例），用于解释 `exrights_unexplained` 中「当日无分红」类缺口。

**为何**：既有 Data 状态单 (c) 已指出配股不在 dividend 表。

**验收**：与未解释除权子集交叉，命中率写入短回执。

---

### D7 · P2 · 中性化即用宽表（可选）

**要什么**：可选交付 `session × instrument` 宽表：`log_float_mcap` + `sw_l1`（已映射）+ 一阶行业 dummy 或 sw_code，全部 asof 可join。  
**非必须**：Alpha/Eng 也可现场 join；若 Data 已有统一 reader，给路径即可。

---

## 明确不要

- QuantDB Key / 默认 300+ 维特征包整包搬家  
- Yahoo/Reddit/美股默认链作主数据  
- 把 CSI300 成分直接标成 `mid_large`  
- AGPL 上游数据文件 vendor 进专有树  

---

## 回传格式（请 Data 回复）

每条 D1–D6：`状态(有/做/拒)` · 路径 · 日期范围 · `available_at` 规则一句话 · 已知缺口。  
`promotion_approved=false` 保持不变。
