# Alpha 复检 · D1 估值残差（ACCEPT_FULL）

**日期**：2026-10-12 · America/New_York（复检落盘约 17:00 ET）  
**角色**：QuantLab Alpha  
**依据**：Data `output/d1/db2014_merge_receipt.json`；前次 `ALPHA_DATA_D1_RESIDUAL_RECHECK_ZH.md`（CONTINUE_STAGE）；`ALPHA_DATA_D1_VALUATION_ACCEPT_ZH.md`  
**门锁**：`promotion_approved=false` · **未跑 GP** · **未自建 moneyflow/IOPV** · **未代跑工厂**

---

## 裁决

**ACCEPT_FULL** — 前次空窗 **2014-04-08→2014-12-31** 已关；SSE 开市日对照 `missing_from_gap=0`；full 表可作研究级 asof join 源。  
**不**晋级密封 / Strategy / promotion（`promotion_approved=false` 保持）。

另见全量验收单：`ALPHA_DATA_D1_VALUATION_FULL_ACCEPT_ZH.md`

---

## 三项残差对照（终态）

| # | 项 | 前次 CONTINUE | 今次 |
|---|---|---|---|
| 1 | full `trade_date_semantics` | 有 | **有**（manifest 保留） |
| 2 | 估值/full date_max | 2026-10-12 | **2026-10-12**（不变） |
| 3 | 2014-04-08→12-31 SSE 开市日 | 缺 183 | **0 缺**（gap_closed；cal_gap=183 / full_gap=183） |

full 表现况（盘面核验，非口述）：**12,289,609** 行 / **5,913** 标的（`ts_code`）/ **2014-01-02→2026-10-12**；2014 全年开市日 **245** = SSE 日历 **245**。

---

## 空窗核验（相对 trade_cal SSE is_open=1）

| 指标 | 值 |
|---|---:|
| SSE 2014 开市日 | 245 |
| full 2014 交易日 | 245 |
| missing_2014_vs_cal | 0 |
| 原空窗日历日数 | 183 |
| full 原空窗日数 | 183 |
| **missing_from_gap** | **0** |

---

## available_at / asof（轻量）

- `available_at` null = **0**；时刻全部 **18:00 Asia/Shanghai**（hour≠18 或 minute≠0 = 0）
- 抽检 session：

| session | same_day_rows | @open09 | @eod18 | future_leak |
|---|---:|---:|---:|---:|
| 2020-06-30 | 3836 | 0 | 3836 | 0 |
| 2024-06-28 | 5338 | 0 | 5338 | 0 |

---

## 路径

- `data/v2/valuation/daily_basic_full_tushare.parquet`
- `data/v2/valuation/daily_basic_full_tushare_manifest.json`（含 `available_at_rule`、`trade_date_semantics`、`known_gap.status=closed`）
- Data 合并回执：`output/d1/db2014_merge_receipt.json`
- Alpha 机读：`output/alpha/d1_valuation_full_accept_20261012.json`

---

## 明确未做 / 边界

- **D2 moneyflow 未 ACCEPT** — 勿当满样本；拉数中，另单交付后再验  
- 未跑 GP；工厂归真实 QuantLab AI  
- `promotion_approved=false`
