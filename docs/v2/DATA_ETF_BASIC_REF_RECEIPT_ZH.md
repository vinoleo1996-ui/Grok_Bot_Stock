# 回执：ETF 参考表（只读）
2026-10-14 06:56 ET，Data。promotion_approved=false。
- 文件：`data/v2/ref/etf_basic.parquet`，1,862 行（上市中 1,734，含已退市），sha256 `99cf9b15e242c9e1ab9508f867d807023689ec5e0391c8e30fc201955be40991`，manifest 同名 _manifest.json。
- 来源：datahub `fund_basic market=E`（status=L 与 D 各一次，共 2 次请求；中转未用），筛名称含 ETF。
- 字段：ts_code、name、category、track_index、benchmark、manager、custodian、fund_type、invest_type、found_date、list_date、delist_date、status。
- category 为**规则推断**（名称/基准关键词）：主题 567、行业 386、宽基 340、跨境 295、宽基/策略(红利/价值等) 156、债券 62、货币 30、商品 26。“主题”是兜底类，可能混入少量行业；track_index 由 benchmark 去掉权重尾巴得到，复合基准原样保留。
- 510300.SH：华泰柏瑞沪深300ETF / 宽基 / 沪深300指数 / 华泰柏瑞基金 / 上市 20120528 ✓
- 脚本：`scripts/acquire/ref_tables_20261014.py`
