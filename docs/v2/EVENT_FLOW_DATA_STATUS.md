# 事件驱动 + 资金结构数据状态（研究级，promotion_approved=false）
更新：2026-10-11 08:4x ET。总开关 promotion_approved_overall 仍为 true。字段对齐 output/alpha/DATA_SCHEMA_EVENT_CAPITAL_ZH.md。

## 1. 分类公告  data/v2/events/announcements_classified_pit.parquet  【进行中】
- 来源：Tushare anns_d（仅 pcd relay 可用；datahub 403「无 token 权限」；`anns` 接口两边都不存在）。
- 列：instrument,event_type,available_at,polarity,event_id,ann_title,source,promotion_approved,classifier_version,meta_json(url/ann_type),ann_date,available_at_rule,url。
- 分类：规则 rules_v1（回购/增持/减持/业绩预增/预减/问询函/问询回复/处罚立案/other），版本哈希写在 classifier_version。
- available_at：有 ann_time 时钟则用时钟；无时钟（绝大多数）记 ann_date 23:59 Asia/Shanghai，即最早 T+1 开盘可交易。
- 正文：anns_d 只给标题+原文 URL（东财/巨潮 PDF），未落正文。
- **限额/缺口**：relay 速度约 2 天/分钟，并偶发 upstream_pool_exhausted；全量 3204 天估计 20–26 小时。**单日硬上限 5000 条、offset 翻页无效、不能按 ts_code/类型过滤**，公告高峰日（如 20240628）会截断；日期格式有时只认 YYYYMMDD、有时只认 YYYY-MM-DD，已做双格式重试。截断天数在 output/d1/event_alpha_build_summary.json 的 days_truncated_5000 里，后续需东财/巨潮按代码补。

## 2. 龙虎榜  data/v2/dragon_tiger/  【完成】
- top_list 157,092 行 / top_inst 1,950,371 行，2018-01-02→2026-10-09，交易日 2125/2125 无缺。
- 席位映射 exalter_institution_map.parquet（19,674 个席位）：institution(机构专用)/northbound_channel(沪深股通)/broker_prop(自营)/retail_or_hot_money；top_inst_labeled.parquet 已带 seat_type、is_institution。
- available_at = T 日 18:00（交易所当晚披露）；另给 available_at_alpha_conservative = T+1 15:00，符合 Alpha 的 T+2 开盘约定。
- “游资”目前只是“非机构营业部”，没有知名游资名单。

## 3. 两融  data/v2/margin/  【明细进行中，汇总完成】
- rzrq_daily_tushare.parquet：margin_detail 走 datahub，并强制带 fields= 回源，避开只给沪市的缓存；已逐日核对每天都有深市。目前到 2022-09，约 1 小时后到 2026-10-09。
- margin_exchange_daily_2018plus.parquet：交易所汇总 2125 天完成。
- available_at = T+1 09:00（交易所 T+1 早间公布）。两融标的生效日尚未单独落表（可从明细首次出现日近似）。

- **merged 2026-10-12**：`margin_exchange_daily_merged.parquet` = `margin_exchange_2014_2017`（available_at **backfill** = 下一交易日 09:00 Asia/Shanghai；`promotion_approved=false`）∪ `margin_exchange_daily_2018plus`（as-filed；重叠日取 2018+）。meta：`margin_exchange_merged_meta.json`。

## 4. 北向  按 Alpha 意见暂停（CS2 搁置）
- 副产品：moneyflow_hsgt 日度汇总 2018+ 已落在 data/v2/northbound/。hsgt_top10/hk_hold 已停拉；hk_hold 2024-08 后官方停披露。

## 后台
nohup：event_flow_pull.py anns / margin_detail；event_rebuild_loop.sh 每 30 分钟重建，日志 logs/event_*.log、logs/event_rebuild.log。

## rzrq_daily update 2026-10-11 10:15 ET
- path `data/v2/margin/rzrq_daily_tushare.parquet` range 20180102–20261009 rows=5786686 days=2125 sha16=7be089e2fe0cf952
- SZ complete through 20261008; 20261009 upstream SSE-only (margin + margin_detail).
- promotion_approved=false; overall promotion untouched.

## ortho_evt_ind2 覆盖快照（2026-10-12 06:50 ET）
- `etf_share_flow_pit_all`：2014-01-02→2026-10-09；X1 行业 ETF 日均≈32.4；NAV 有效≈31.5/日。
- SW L1 bars：1999-12-30→2026-09-30。
- 龙虎/北向/公告：仍 2018+ → 本批未开 DT/NB/ANN。
- 三臂均 research_observe_near_relative vs IND-RATE（同构 510300↔GOLD 削仓）；无交接。

## ind_etf_share_flow trade_date 对齐（2026-10-12 ~07:00 ET）
- **根因**：`etf_share_flow_pit_industry_theme` 与 `sw_l1_etf_map_pit_daily` 落盘 `trade_date` 均为 **YYYYMMDD str**；AI v16 仅对 map 侧 `pd.to_datetime` → merge `str` vs `datetime64` 失败。
- **约定**：ETF share PIT / theme×SW map 的 `trade_date` = **YYYYMMDD str**；`available_at` = datetime64。两侧 join 前必须用同一 cast（`quantlab.data.v2_readers.as_trade_date_ymd`）。
- **权威预 join（研究级，promotion_approved=false）**：
  - ETF×日：`data/v2/etf/share_pit/ind_etf_share_flow_pit.parquet` — 223286 行 / 178 ETF / 27 SW；`20140102`→`20261009`；列 `ts_code,trade_date,sw_l1_code,flow_est_wan_yuan,d_share_wan,available_at,…`
  - SW×日汇总：`data/v2/etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet` — 51728 行；X1 日均 SW≈7.2
  - meta：`data/v2/etf/share_pit/ind_etf_share_flow_pit_meta.json`
- **源表**：theme=`…/etf_share_flow_pit_industry_theme.parquet`；map=`data/v2/etf/sw_l1_etf_candidates.parquet`（静态 ts_code→sw_l1 + list/delist 窗）；日代表旗标来自 `sw_l1_etf_map_pit_daily`。
- **Reader**：`load_ind_etf_share_flow()` / `join_theme_share_flow_to_sw()` / `as_trade_date_ymd()`。
- 未改 `promotion_approved_overall`。

## Beta X1 rerun note (2026-10-12 ~19:15 ET)
Data 已补龙虎/北向 X1（见 `BETA_X1_EVT_FLOW_COVERAGE.md`）。Beta 重跑：**DT-INST-BREADTH**=fail_explore（X2 CAGR≈3.4%）；**NB-MARGIN-DIV**=fail_precheck（X1 Sharpe≤0）。无交接。`promotion_approved=false`。
