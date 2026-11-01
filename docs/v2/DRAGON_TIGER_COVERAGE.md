# 龙虎榜覆盖报告（研究级）

- **区间**: 20150105 → 20261009（X1 已补；原仅 20180102+）
- **交易日对齐**: 2857 / 2857（相对 SSE 交易日历，缺失 0）
- **top_list**: 185,970 行 → `data/v2/dragon_tiger/top_list.parquet`
- **top_inst**: 2,281,288 行 → `data/v2/dragon_tiger/top_inst.parquet`
- **席位标签**: `top_inst_labeled.parquet`（含 `seat_type` / `is_institution`）
  - seat_type: retail_or_hot_money / institution / northbound_channel / broker_prop
- **X1 (2015–2017)**: 732 日；top_list 42,507；top_inst 424,644
- **available_at**: `trade_date` 当日 18:00 Asia/Shanghai（收盘后披露口径）；`available_at_alpha_conservative`≈T+1 15:00
- **不可前移 available_at**：无更早披露时钟源证据
- **promotion_approved**: false（研究级）
- **来源**: Tushare `top_list` + `top_inst`（X1 经 datahub；2018+ 既有）
- 详见：`docs/v2/BETA_X1_EVT_FLOW_COVERAGE.md`
