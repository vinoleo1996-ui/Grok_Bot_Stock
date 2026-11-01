# 业绩预告重叠段差异报告（Arch P3-1，研究级，promotion_approved=false）
生成：2026-10-18T01:03:18-04:00（ET）

- 重叠段：公告日 **20251016 → 20251116**（自然日 32 天）。datahub `forecast` 按公告日逐日独立重拉（limit=1000，不复用旧缓存），失败 0 天。
- 对比对象：`data/v2/events/forecast_1y.parquet` 同区间（sha256 `043bdecc569d2a780c98e2fc80410b25983452ff4570b5516fda7593111f89d7`）；重拉表 `data/v2/events/forecast_overlap_20251016_20251116.parquet`（sha256 `69a82305b2e75e995a0b4fcfebba184f04c041cd19704972447e9210e855fc2f`）。
- 键：['ts_code', 'ann_date', 'end_date', 'update_flag']；比较字段：type, p_change_min, p_change_max, net_profit_min, net_profit_max, last_parent_net, first_ann_date, summary, change_reason。
- 行数：重拉 52，forecast_1y 48；键：重拉 52，forecast_1y 48，**两边都有 48**，仅重拉 4，仅 forecast_1y 0；键一致率 **92.31%**。
- 两边都有的键中，全部字段一致 48 / 48（**100.00%**）。
- 各字段不一致条数：type=0, p_change_min=0, p_change_max=0, net_profit_min=0, net_profit_max=0, last_parent_net=0, first_ann_date=0, summary=0, change_reason=0。
- 说明：两次都是「现在回拉」的数据商当前版本，一致只能说明两次拉取口径稳定，不能证明是首发快照。

## 不一致样例（最多 10 条）
| ts_code | ann_date | end_date | update_flag | 差异 |
|---|---|---|---|---|
| — | — | — | — | 无 |
