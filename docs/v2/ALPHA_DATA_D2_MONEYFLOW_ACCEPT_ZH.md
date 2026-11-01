# Alpha 验收 · D2 个股资金流 PIT（ACCEPT_FULL）

**日期**：2026-10-13 · America/New_York  
**角色**：QuantLab Alpha  
**对应需求**：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md` §D2  
**触发**：Data 【D2 正式交付 · 请 ACCEPT】  
**门锁**：`promotion_approved=false` · **未跑 GP** · **未升 live** · **未代跑工厂** · **非 FactorCandidate 解锁**

---

## 裁决

**ACCEPT_FULL（研究级满样本）**

可用作闸门 / 短清单叶子所需的 **个股资金流研究级 asof 源**（`net_mf_*` / 大小单买卖额量）。  
**明确不是**：promotion / 密封包 / Strategy 实盘交接 / live handoff。本单只验收数据可消费性。

前次状态：`ALPHA_DATA_D1D4_STATUS_ACCEPT_ZH.md` 记 D2「进行中 · 不 ACCEPT」→ **本单升 ACCEPT_FULL**。

---

## 核验路径（盘面，非口述）

| 资产 | 路径 | 结果 |
|---|---|---|
| moneyflow PIT | `data/v2/moneyflow/moneyflow_stock_daily_pit.parquet` | 可读；schema 含 trade_date / instrument_id / 资金流字段 / **available_at** |
| Data 交付回执 | `docs/v2/ALPHA_DATA_D2_MONEYFLOW_DELIVERY_ZH.md` | DELIVERED_FOR_ACCEPT |
| Data 机读 | `output/alpha/d2_moneyflow_delivery_20261013.json` | 声明对齐 |
| 交易日历 | `data/v2/tushare_raw/trade_cal.parquet`（SSE `is_open=1`） | 20180102→20261012 开市 **2126** 日；moneyflow **0 缺日** |
| 中大盘 PIT | `data/v2/universe/mid_large_members_pit.parquet` | 抽样 session 重叠 ≈99.9%+，可 join |

机读回执：`output/alpha/AI_D2_MONEYFLOW_ACCEPT_20261013.json`

---

## 统计（Alpha 复算 vs Data 声明）

| 指标 | Data 声明 | Alpha 盘面 | 对齐 |
|---|---:|---:|:---:|
| rows | 9,498,309 | 9,498,309 | ✓ |
| n_instruments | ≈5465 | 5465 | ✓ |
| trade_date_min | 20180102 | 20180102 | ✓ |
| trade_date_max | 20261012 | 20261012 | ✓ |
| n_trade_dates | — | 2126（= SSE 开市） | ✓ |
| size | ≈750MB / 786.1MB | 786.1 MB（786,115,514 B） | ✓ |
| available_at null | — | **0** | ✓ |
| (trade_date, instrument_id) 重复 | — | **0** | ✓ |
| 20261013 行 | 0（空日） | 无该日（有效末日 20261012） | ✓ |

---

## Schema（盘面）

`session, trade_date, instrument_id, ts_code, buy_elg_amount, sell_elg_amount, buy_lg_amount, sell_lg_amount, buy_md_amount, sell_md_amount, buy_sm_amount, sell_sm_amount, buy_elg_vol, sell_elg_vol, buy_lg_vol, sell_lg_vol, buy_md_vol, sell_md_vol, buy_sm_vol, sell_sm_vol, net_mf_amount, net_mf_vol, available_at`

满足 D2 需求最小字段（含 `net_mf_amount` 与大小单额量）+ **PIT `available_at`**。

---

## PIT / 无未来泄漏（抽检）

| 检查 | 结果 |
|---|---|
| available_at 早于 trade_date（日历日） | **0** |
| available_at 同日 | **0** |
| available_at 在 trade_date 之后 | **全部 9,498,309** |
| 抽样 lag 中位数 | **1 个日历日**（周末/长假拉长至 3–11 日，符合下一开市 09:00 语义） |
| available_at 时刻（抽样） | 一律 **09:00 Asia/Shanghai** |

**用法**：开盘信号必须 **asof on `available_at`**，禁止裸用同日 `trade_date` 资金流。

---

## 覆盖连续性

- SSE 开市日 20180102→20261012：**2126 / 2126**，缺日 **0**。
- 日历间隔 >3 日共 56 段，均为春节/国庆等休市（最大 11 日），**非数据空洞**。
- `20261013` 空日 0 行：已文档化；有效末日 **20261012** OK。
- 近端日行数稳定（如 20261012 ≈5224 标的）。

---

## 中大盘可联结性

| session | mid_large | moneyflow | overlap | ml∈mf % |
|---|---:|---:|---:|---:|
| 2024-01-02 | 2488 | 5089 | 2487 | 99.96 |
| 2024-06-28 | 2481 | 5088 | 2480 | 99.96 |
| 2025-06-30 | 2486 | 5138 | 2484 | 99.92 |
| 2026-10-09 | 2507 | 5224 | 2507 | 100.00 |

全历史中大盘标的 4410 中，**4403** 曾出现在 moneyflow（仅 7 从未命中，可忽略）。  
软注：`mid_large` 在 **2026-10-12** 尚无 session 行（宇宙表未跟到该日），属 D3 宇宙侧滞后，**非** moneyflow 缺口；moneyflow 当日有 5224 行。

---

## 已知软缺口（不挡 ACCEPT_FULL）

1. 无独立 `manifest.json`（交付 JSON/回执已承载规则；建议 Data 后续补 `available_at_rule` 一文）。
2. `mid_large` 末日可能滞后于 moneyflow 1 日——join 时以双方交集为准。
3. 研究级 only：`promotion_approved=false`；不得据此解锁 live / GP / 晋级密封。

---

## 允许用途 / 禁止

**允许**：闸门残差、短清单叶子（需个股资金流者）、与 mid_large asof join、研究回测。  
**禁止**：把本 ACCEPT 当 GP 授权、升主书 live、交 Strategy 实盘权重、FactorCandidate 自动晋级。

---

## 对 Data

D2 正式 ACCEPT_FULL。无需返工。可选：补 `moneyflow_stock_daily_pit_manifest.json`（`available_at_rule` = 下一开市日 09:00 Asia/Shanghai）。日常增量保持与 SSE 日历对齐即可。

验收时刻：2026-10-13T02:52:35.510845-04:00 ET
