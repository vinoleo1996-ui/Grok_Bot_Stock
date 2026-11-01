# Alpha 验收 · D1 估值/日频基础 PIT（全量 ACCEPT）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab Alpha  
**对应需求**：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md` §D1  
**触发**：Data 【D1 CONTINUE 完成】db2014 raw→full 合并  
**门锁**：`promotion_approved=false` · **未跑 GP** · **未触 moneyflow/IOPV 构建** · **未代跑工厂**

---

## 裁决

**ACCEPT（全量 / ACCEPT_FULL）**

可用作估值、换手、市值等日频基础的 **研究级 asof join 源**。  
**明确不是**：promotion / 密封包 / Strategy 交接 / 晋级权重短清单的自动放行。本单只验收数据可消费性。

前次：`ACCEPT_STAGE`（`ALPHA_DATA_D1_VALUATION_ACCEPT_ZH.md`）→ `CONTINUE_STAGE`（空窗 183 日）→ **本单升全量 ACCEPT**。

---

## 核验路径（盘面，非口述）

| 资产 | 路径 | 结果 |
|---|---|---|
| full 日频基础 | `data/v2/valuation/daily_basic_full_tushare.parquet` | 统计对齐 Data 声明与 receipt |
| full manifest | `data/v2/valuation/daily_basic_full_tushare_manifest.json` | 有 `available_at_rule` + `trade_date_semantics`；`known_gap.status=closed` |
| Data 合并回执 | `output/d1/db2014_merge_receipt.json` | `gap_closed=true`，`missing_from_full=0`，`days_2014=245` |
| 交易日历 | `data/v2/tushare_raw/trade_cal.parquet`（SSE `is_open=1`） | 2014 开市 245；原空窗 183 日全在 full |

机读回执：`output/alpha/d1_valuation_full_accept_20261012.json`

---

## 统计（Alpha 复算 vs Data 声明）

| 指标 | Data 声明 | Alpha 盘面 | 对齐 |
|---|---:|---:|:---:|
| rows | 12,289,609 | 12,289,609 | ✓ |
| instruments（ts_code） | 5,913 | 5,913 | ✓ |
| date_min | 2014-01-02 | 2014-01-02 | ✓ |
| date_max | 2026-10-12 | 2026-10-12 | ✓ |
| days_2014 | 245 | 245（= SSE 开市 245） | ✓ |
| available_at null | （规则：18:00 ASH） | **0** | ✓ |
| 非 18:00 Asia/Shanghai | — | **0** | ✓ |
| 原空窗 missing_from_gap | 0 | **0** | ✓ |

相对前次 CONTINUE 基线（11,865,655 行 / 5,911 标的）：+**424,000−ish** 行量级、+2 标的，与 183 日回填一致。

---

## available_at 规则（manifest 摘录）

> `available_at = trade_date 18:00 Asia/Shanghai. Tushare daily_basic updates same trade day ~15:00–17:00; 18:00 conservative. asof on available_at; NOT naked trade_date for open signals.`

**trade_date_semantics**：

> `trade_date/session = the A-share trading calendar day the pe/pb/mv/turnover metrics refer to (close-of-day). Same-day row is NOT available at 09:00; join with asof on available_at.`

同日 basic **禁止**在 09:00 开盘信号裸用 `trade_date`。

---

## asof 无未来泄漏（Alpha 轻量 2 session）

| session | same_day_rows | @open09 | @eod18 | future_leak |
|---|---:|---:|---:|---:|
| 2020-06-30 | 3836 | 0 | 3836 | 0 |
| 2024-06-28 | 5338 | 0 | 5338 | 0 |

---

## 2014 空窗（已关闭）

| 项 | 值 |
|---|---:|
| 原缺口区间 | 2014-04-08 → 2014-12-31 |
| SSE 开市日（该窗） | 183 |
| full 覆盖日（该窗） | 183 |
| **missing_from_gap** | **0** |
| 2014 全年 full vs SSE | 245 / 245；missing=0 |

---

## schema 要点（full）

含：`ts_code` / `instrument_id` / `trade_date` / `available_at`（tz=Asia/Shanghai）/ `pe,pe_ttm,pb,ps,ps_ttm,dv_ttm` / `total_mv,float_mktcap` / `turnover_rate,turnover_rate_f,volume_ratio` / `total_share,float_share,free_share` / `close` / `source,quality_status,promotion_approved`。

列上 `promotion_approved` 布尔字段存在；**Alpha 门锁仍为 false**（研究级，不晋级）。

---

## 明确未做 / 边界

1. **D2 个股 moneyflow** — **未 ACCEPT**；拉数中，勿当满样本，另单交付后再验  
2. 未跑 GP；工厂归真实 QuantLab AI  
3. 未密封、未 Strategy 交接、未自动进短清单权重  
4. `promotion_approved=false` 保持  
5. 估值窄表（`daily_basic_valuation_tushare*.parquet`）非本单重验对象；full 已升全量 ACCEPT

---

## 对 Data / 工厂

- D1 full：**可消费**（研究 asof）  
- D2：继续拉至正式交付句后再 ping Alpha  
- 禁止用本 ACCEPT 当作 GP 重启或 promotion 授权
