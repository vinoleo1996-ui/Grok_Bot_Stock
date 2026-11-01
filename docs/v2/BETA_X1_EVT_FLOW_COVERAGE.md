# Beta X1 (2015–2017) 事件/资金流覆盖审计 + 补拉回执

更新：2026-10-12 ~19:05 ET。研究级，**promotion_approved=false**（未改 overall promotion）。  
用途：`smoke_evtflow_indetf` X1 窗口。另有执行器在补 2018→2024+ 的 hk_hold/hsgt_top10/margin_detail——本单错峰，未抢同一 relay 高峰 bulk。

## 总表（可直接转 Beta）

| 数据集 | 权威 path | date_min | date_max | nrows | 关键列 | X1(2015-01-01..2017-12-31) | available_at | 可前移? | 缺口/补数 |
|---|---|---|---|---|---|---|---|---|---|
| 龙虎 top_list | `data/v2/dragon_tiger/top_list.parquet` | 20150105 | 20261009 | 185,970 | trade_date,ts_code,net_amount,reason,available_at | **有** 42,507 行 / 732 日（20150105–20171229） | trade_date 18:00 SH | **否** | 已用 datahub 补齐 X1；raw 按日 `tushare_raw/top_list/YYYYMMDD.parquet` |
| 龙虎 top_inst / labeled | `data/v2/dragon_tiger/top_inst.parquet` + `top_inst_labeled.parquet` | 20150105 | 20261009 | 2,281,288 | trade_date,ts_code,exalter,net_buy,side,reason,**seat_type**,is_institution,available_at,available_at_alpha_conservative | **有** 424,644 行 / 同 732 日 | 同上；conservative≈T+1 15:00 | **否** | seat_type 来自 `exalter_institution_map`（未命中则 regex 回填）；**不可**因“想用 X1”而前移 available_at |
| 北向 moneyflow_hsgt | `data/v2/northbound/moneyflow_hsgt_daily_2018plus.parquet`（同内容副本 `..._2014plus.parquet`） | 20141117 | 20261009 | 2,800 | trade_date,hgt,sgt,north_money,south_money,ggt_ss,ggt_sz,available_at | **有** 710 行（20150105–20171229）；沪股通自 20141117；**深股通 sgt 自 20161205** | trade_date 18:00 SH | **否** | datahub **403 未开**该 API；经 relay 年块补 y2014q4–y2017；研究级 |
| 行业 ETF 份额 all | `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet` | 20140102 | 20261009 | 1,578,335 | ts_code,trade_date,fd_share,share_wan,d_share_wan,share_available_at,nav_available_at,available_at | **有** 93,773 行 / 179 codes（本地 raw `fund_share` 并入，**无新 API**） | share: 下一交易日 09:00；nav: max(ann,trade) 23:59；available_at=max | **否** | 2018+ 与 bak 逐行 fd_share 一致；bak=`..._all.parquet.bak_2018plus` |
| 行业 ETF 份额 SW 映射 | `data/v2/etf/share_pit/etf_share_flow_pit_industry_theme.parquet` | 20140102 | 20261009 | 223,545 | 同上（仅 SW L1 映射 ETF） | **有** 13,030 行 / 30 codes；日均 SW L1≈**7.2**（2015≈5.6 / 2016≈7.1 / 2017≈8.9） | 同上 | **否** | 类别宽表备份：`..._industry_theme_by_category.parquet` |
| 两融交易所汇总（已有） | `data/v2/margin/margin_exchange_2014_2017.parquet` | 20140102 | 20180105 | 1,962 | trade_date,exchange_id,rzye,… | **有**（Beta 自用，本单未重做） | （既有） | — | 个股明细仍见他执行器 2018+ 任务 |

---

## 1) 龙虎榜 `top_inst_labeled` / `seat_type`

### 审计结论（补前）
- 旧覆盖：**仅 20180102→20261009**（2125 日），X1 **无**。
- 文档：`docs/v2/DRAGON_TIGER_COVERAGE.md`、`EVENT_FLOW_DATA_STATUS.md`。

### 补后
- 权威：`data/v2/dragon_tiger/top_inst_labeled.parquet`（及 top_list / top_inst）。
- 全区间：20150105→20261009，2857 日，相对 SSE 日历 **missing=0**。
- X1：732/732 交易日；top_list 42,507；top_inst 424,644。
- 关键列：`seat_type` ∈ {institution, northbound_channel, broker_prop, retail_or_hot_money}；`is_institution`；`available_at`；`available_at_alpha_conservative`。
- 来源：Tushare `top_list`/`top_inst`，**datahub** 按日拉取（避让 relay 上 hk_hold 高峰）；脚本 `scripts/acquire/x1_dragon_pull.py`。

### available_at / 能否前移
- 规则（现有列 + 文档）：**trade_date 当日 18:00 Asia/Shanghai**（收盘后披露口径）；Alpha 保守时钟 **T+1 15:00** → 交易上按 T+2 开盘用。
- **可否前移：否**。无独立“更早披露时钟”源证据；不可为填 X1 而把 available_at 改早于披露口径。

---

## 2) 北向 `moneyflow_hsgt` / 日度汇总

### 审计结论（补前）
- 旧文件仅 **20180102→20261009**（2059 日）。X1 **无覆盖**（与 `V3_NB_MARGIN_DIV_PREREG` 记载一致）。

### 补后
- 权威（兼容旧路径）：`data/v2/northbound/moneyflow_hsgt_daily_2018plus.parquet`  
  另存：`moneyflow_hsgt_daily_2014plus.parquet`（同内容）。
- 全区间：20141117→20261009，2800 日。
- X1：710 日，20150105–20171229；`north_money` 无空。
- **沪股通 hgt**：自 **20141117**。
- **深股通 sgt**：自 **20161205**（此前 sgt 为空；仅沪股通阶段属正常）。
- datahub：**api_not_enabled (403)**；经 **relay** 年块 `y2014q4`–`y2017` 补齐。研究级。

### available_at
- `trade_date 18:00 Asia/Shanghai`。**不可前移**（无更早时钟证据）。

---

## 3) 行业 ETF `etf_share_flow_pit_all` / industry_theme

### 审计结论（补前）
- share_pit 物化脚本曾硬过滤 `trade_date>="20180101"`，故 PIT 表仅 2018+。
- 但 raw `data/v2/etf/raw/fund_share/*.parquet` **已有 2014+**（含 X1 行业 ETF）。

### 补后（本地并入，无 API）
- `etf_share_flow_pit_all.parquet`：20140102→20261009；X1 93,773 行 / 179 ETF。
- `etf_share_flow_pit_industry_theme.parquet`：按 **SW L1 映射** 子集（与 `V3_IND_SHARE_REV` 池一致）；X1 13,030 行 / 30 ETF。
- 2018+ `fd_share` 与 bak **100% 一致**。

### 「日均可交易行业约 3–4」是否属实？
- **上市日证据**（`sw_l1_etf_first_date`）：2015 末仅 **7** 个一级行业有代表 ETF；2016 末 8；2017 末 **11**。上市家数稀少是正常历史事实，不是数据坏了。
- 有份额行的日均 SW L1 行业数：整体 X1 ≈ **7.2**（未加流动性过滤）。
- Beta prereg 过滤（上市满 60 日、近 20 日均额≥2000 万等）后，**日均 3–4 完全合理**；稀疏属机制约束，不是可“发明映射”解决的。
- **上市前映射**：不应伪造；无 ETF 的行业在 X1 只能空仓/压舱（如 511880）。更早份额：raw 已覆盖到 2014，已并入 PIT。

### available_at
- share：保守 **下一交易日 09:00**；nav：max(ann_date, trade_date) 23:59；`available_at=max(share,nav)`。不可前移。

---

## 接口可补性 / 难度（若仍有缺口）

| 项 | 免费/Tushare | 难度 | 备注 |
|---|---|---|---|
| 龙虎 2015–17 | Tushare top_list/top_inst；datahub 可用 | 已完成 | ~1464 日次，workers=2，~25–40 min |
| moneyflow_hsgt 2014–17 | Tushare；**仅 relay**（datahub 403） | 已完成 | 与 hk_hold 争 relay 时需长退避 |
| ETF 份额 X1 | 本地 fund_share 已有 | 已完成 | 无需拉取 |
| 行业 ETF 扩容到 30+ 行业 | 受上市日限制 | **不可补** | 2017 前多数一级行业无对应 ETF |
| hk_hold / hsgt_top10 / margin_detail 2018+ | 他执行器进行中 | — | 本单未抢限速 |

---

## 文件与脚本

- 报告：`docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`（本文件）
- 龙虎拉取/物化：`scripts/acquire/x1_dragon_pull.py`、`x1_dragon_materialize.py`；日志 `logs/x1_dragon_pull.log`
- 北向：`scripts/acquire/x1_moneyflow_pull.py`；摘要 `data/v2/northbound/moneyflow_x1_extend_summary.json`
- ETF：`data/v2/etf/share_pit/share_pit_x1_extend_summary.json`、`industry_theme_sw_summary.json`
- promotion：**全部 false**；未触碰 `promotion_approved_overall`
