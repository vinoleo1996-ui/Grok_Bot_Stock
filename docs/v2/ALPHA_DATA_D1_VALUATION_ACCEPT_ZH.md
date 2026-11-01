# Alpha 验收 · D1 估值/日频基础 PIT（阶段 ACCEPT）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab Alpha  
**对应需求**：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md` §D1  
**门锁**：`promotion_approved=false` · **未跑 GP** · **未触 moneyflow/IOPV 构建**

---

## 裁决

**ACCEPT_STAGE（阶段 ACCEPT）** — 有残差缺口，见下。

可用作估值/换手等日频基础的 **asof join 源**；进因子短清单 / 密封 / Strategy **仍须另审**，本单不晋级。

---

## 核验路径

| 资产 | 路径 | 结果 |
|---|---|---|
| full 日频基础 | `data/v2/valuation/daily_basic_full_tushare.parquet` | schema 含 `available_at`；统计对齐 manifest |
| full manifest | `data/v2/valuation/daily_basic_full_tushare_manifest.json` | 有 `available_at_rule` |
| 估值窄表 | `data/v2/valuation/daily_basic_valuation_tushare.parquet` | 含 `available_at` + `session` |
| 估值 manifest | `data/v2/valuation/manifest.json` | 语义 + 规则 + 3 日 asof |
| 估值 acceptance | `data/v2/valuation/daily_basic_valuation_available_at_acceptance.json` | `ok=true`，`future_leak_rows=0` |

可选机读回执：`output/alpha/d1_valuation_accept_20261012.json`

---

## available_at 规则（摘录）

> `available_at = trade_date 18:00 Asia/Shanghai. Tushare daily_basic updates same trade day ~15:00–17:00; 18:00 conservative. asof on available_at; NOT naked trade_date for open signals.`

**trade_date / session 语义（估值表 manifest）**：

> `trade_date/session = the A-share trading calendar day the pe/pb/mv metrics refer to (close-of-day).`

同日 basic **不可**在 09:00 开盘信号裸用 `trade_date`；必须 `asof(available_at)`。

---

## 统计（与 manifest 一致）

| 表 | rows | instruments | date_min | date_max | available_at null |
|---|---:|---:|---|---|---:|
| **full** | 11,865,655 | 5,911 | 2014-01-02 | 2026-10-12 | 0 |
| **valuation** | 9,754,991 | 5,899 | 2018-01-02 | 2026-10-09 | 0 |

- full：`available_at` 时刻全部为 18:00 Asia/Shanghai（hour≠18 / minute≠0 = 0）
- full 关键列含：`pe/pe_ttm/pb/ps/ps_ttm/dv_ttm`、`total_mv/float_mktcap`、`turnover_rate(_f)`、`volume_ratio` 等
- valuation 含：`pe_ttm/pb/ps_ttm/dv_ttm`、`total_mv/float_mktcap`、`session`

---

## asof 无未来泄漏

**估值窄表（Data 已做 3 日）**：2020-06-30 / 2024-06-28 / 2026-06-30 — 同日在开盘 09:00 可用 = 0；`future_leak_rows=0`。

**full 轻量抽检（Alpha，2 session）**：

| session | same_day_rows | @open09 | @eod18 | future_leak |
|---|---:|---:|---:|---:|
| 2020-06-30 | 3836 | 0 | 3836 | 0 |
| 2024-06-28 | 5338 | 0 | 5338 | 0 |

---

## 残差缺口

1. **2014-04→12 近整段空窗（硬缺口）**  
   对照 `data/v2/tushare_raw/trade_cal.parquet`（SSE `is_open=1`）：2014-04..12 应有 **187** 个开市日，full 表仅有 **2014-04-01..04 共 4 日**；**缺失 183 日**（2014-04-08→2014-12-31）。2014-01..03 的 58 日齐全。Data 口述「部分未齐」偏轻 — 实为 4 月中起整段未补。
2. **full manifest** 缺显式 `trade_date_semantics` 一行（`available_at_rule` 已覆盖 join 禁令；估值表已有完整语义）。建议 Data 补一行对齐。
3. **估值窄表** `date_max=2026-10-09` 落后 full 的 `2026-10-12` 两日 — 可后续对齐，非阻塞。
4. **D2–D4**：moneyflow / IOPV 仍 P0 排队。FYI：`data/v2/universe/mid_large_members_pit.parquet` 已存在（约 555 万行）— **本单不重开 D3**，是否算 D3 完成另单确认。

---

## 明确未做

- 未跑 GP / 未晋级 / 未密封  
- 未触 moneyflow、IOPV 构建  
- `promotion_approved=false` 保持

---

## 对 Data 下一拍（提醒）

D1 阶段可接。请继续 **D2 个股 moneyflow PIT** 与 **D4 ETF IOPV**（P0）；2014-04→12 full 空窗有空再回填。D3 文件或已在盘，请在回传里对 `mid_large_members_pit` 给正式状态句，Alpha 不在本单重验。

---

## 残差复检（2026-10-12 12:17 ET · Data 回传后）

**裁决：CONTINUE_STAGE**（阶段 ACCEPT 维持；空窗未关，不升全量 ACCEPT）

| 残差项（前次） | 复检结果 |
|---|---|
| full `trade_date_semantics` | **已补**（`daily_basic_full_tushare_manifest.json`） |
| 估值 `date_max`→2026-10-12 | **已对齐**（主表至 10-09 + `daily_basic_valuation_tushare_ext_20261012.parquet` 5561 行；manifest `rows=9,760,552`） |
| 2014-04-08→12-31 空窗 | **仍开**：SSE 开市 **183** 日，full 表该窗 **0** 日；与前次相同 |

**raw 侧**：`tushare_raw/daily_basic` 已见 `20140408`–`20140411`（Data 口述 raw 过 20140411 属实），但 **尚未并入 full parquet**。full `known_gap.status=backfill_in_progress`。

**不变**：`available_at`=trade_date 18:00 Asia/Shanghai；开盘裸 `trade_date` 仍禁；`promotion_approved=false`；本侧未跑 GP、未触 moneyflow/IOPV 构建。

另见：`docs/v2/ALPHA_DATA_D1_RESIDUAL_RECHECK_ZH.md`
