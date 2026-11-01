# 回执：月度 PIT 股票池锚点（给 Arch，审计 #8）
2026-10-14 06:56 ET，Data。promotion_approved=false。源：`data/v2/universe/mid_large_members_pit.parquet`（本地，0 请求）。
| 文件 | 内容 | 行数 | sha256 |
|---|---|---|---|
| `data/v2/universe/mid_large_month_end_anchor_pit.parquet` | 每月最后一个 session 的全部 mid_large 成员 + rank_mcap + in_top300 | 277,460（142 个月，2015-01→2026-10） | 9e322736c35b3c651fdbf46627fc6fcbeb6539dc786562c7ea2331f4c5bfb4f2 |
| `data/v2/universe/mid_large_top300_monthly_pit.parquet` | 按月重算的 top300 | 42,600（142×300） | 05a2f8f7d9b2dd278bfee267cf6967bad7d4d9f9c00c0c28854b352a93fcd533 |
- 规则：复刻 `research/g1g5_d1_val_resid_weights.py::select_mid_large_topn_light(anchor=2024-06-28)`——mid_large 成员按 `float_mktcap_basis`（前一交易日流通市值）降序取前 300，但每月月末重算。available_at=锚点 session 09:00 上海，无同日前视。
- 差异：原函数还会跳过没有 D0 panel 的票再补位；这依赖研究侧 panel 目录，本表未做，使用端需按同样规则补位。2024-06-28 那期可用来对账原静态池。
- **注意**：2026-10 那期锚点是 2026-10-14（月份未完），用 `month_complete=False` 标记，回测请剔除。
