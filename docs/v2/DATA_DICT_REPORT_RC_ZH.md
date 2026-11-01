# 数据字典：report_rc（卖方盈利预测明细）
更新：2026-10-14 06:56 ET（Data）。promotion_approved=false。表：`data/v2/events/report_rc_2018plus.parquet`（原表不动）；带 org_id 版：`data/v2/events/report_rc_2018plus_orgid.parquet`。

依据：Tushare 官方文档 doc_id=292（https://tushare.pro/document/2?doc_id=292，2026-10-14 核对）。

| 字段 | 含义（官方） | 单位 | 备注 |
|---|---|---|---|
| op_rt | 预测营业收入 | 万元 | |
| op_pr | 预测营业利润 | 万元 | |
| **tp** | **预测利润总额** | 万元 | **不是目标价**（更正）。本地分布佐证：tp 中位 13.3 万万元，与 np 中位 10.75 万同量级，tp/np≈1.2 |
| np | 预测净利润 | 万元 | |
| eps / pe / rd / roe / ev_ebitda | 每股收益 / 市盈率 / 股息率 / ROE / EV/EBITDA | 元 / 倍 / % / % / 倍 | |
| rating | 卖方评级 | | |
| **max_price** | **预测最高目标价** | 元 | 非空仅 30,936 行 |
| **min_price** | **预测最低目标价** | 元 | 非空 574,092 行；两者都非空 30,705 行；max<min 有 3 行。只给一个目标价时多填在 min_price，建议目标价取两者中 >0 的均值（与 AI 叶15 预注册口径一致） |
| org_name | 机构名（原始） | | 保留不改 |
| org_name_norm / org_id | 归一后机构名 / 稳定 ID（ORG+sha1 前 8 位） | | 新增，仅在 _orgid 表；映射 `report_rc_org_id_map.parquet/.csv` |
| available_at | 研报日后第一个交易日 09:00 上海 | | |
