# report_rc 满窗回执（研究级，promotion_approved=false）

- 表：`data/v2/events/report_rc_2018plus.parquet`
- 行数：1917334；日期窗：['20180101', '20261013']；n_fails=0
- available_at：report_date 后首个交易日 09:00
- SHA256：`2d3a37a79be15bdc3fe795b498deb3541b7ee6b412b1df3f64078a33a4567019`

## 机构名归一（2026-10-14 17:33 ET）
- 规则：全角括号→半角、去空格，逐层去后缀（股份有限公司/有限责任公司/有限公司/集团/证券研究所/研究所/研究院/研究中心/研究部/研究），标准名=该组内行数最多的原始写法。原表不改，映射另存。
- 映射表：`data/v2/events/report_rc_org_name_map.parquet`（及 .csv），列 org_name_raw/org_name_std/n_rows/merged
- 原始写法 162 个 → 标准名 161 个；被合并写法 1 个，涉及 1167 行
- 多写法机构 Top20（标准名 | 写法数 | 行数）：
  - 高盛集团（GoldmanSachs） | 2 | 3771
- 注意：规则归一可能有误合/漏合，研究使用前建议抽查映射表。

## 更正与归一 v2（2026-10-14 06:56 ET）
- **字段更正**：`tp` = 预测**利润总额**（万元），不是目标价；目标价是 `max_price`/`min_price`。以前任何把 tp 当目标价的说法作废。字典见 `docs/v2/DATA_DICT_REPORT_RC_ZH.md`。
- **机构归一 v2**：NFKC 全半角统一、去空格、去「股份有限公司/有限责任公司/有限公司/分公司/证券/研究所…」后缀，加别名表（更名=同法人才合并：安信→国投证券、财富→财信证券、国联→国联民生；中金/中金公司、中信建投/中信建投证券、申万宏源研究/证券、高盛两种写法等）。
- 机构数：**归并前 162 → 归并后 151**（合并 11 组；旧 v1 是 162→161）。
- 刻意**不合并**：国泰君安/海通证券/国泰海通（合并前为不同法人；国泰海通与国泰海通证券已合并）、民生证券 vs 国联民生、摩根大通证券(境内) vs JPMorgan、高华 vs 高盛、各「香港/国际」子公司 vs 母公司。需要按集团口径时在使用端再映射。
- 文件：`data/v2/events/report_rc_2018plus_orgid.parquet`（1,917,334 行，原列全保留 + org_name_norm + org_id），sha256 见同名 _manifest.json；映射表 `report_rc_org_id_map.parquet/.csv`；脚本 `scripts/acquire/report_rc_org_id.py`。
