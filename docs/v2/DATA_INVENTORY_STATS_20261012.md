# QuantLab data/v2 数据库存统计

- **生成**：2026-10-12（ET，America/New_York）
- **范围**：`/workspace/QuantLab/data/v2/` 权威 PIT/面板 + docs 晋级指针；主日线另含 `data/local_market/1c85…/panels`（平台默认喂价来源）
- **方法**：pyarrow 元数据 + 单列 min/max；大文件未全量载入内存。**不虚构**；缺口如实标注
- **总开关**：`promotion_approved_overall=true`（平台数据门，见 `docs/v2/ACCEPTED_DEFAULTS.md` / `PROMOTION_ACCEPTANCE.*`）。下表「研究级」= 该数据集 `promotion_approved=false` 或未进 acceptance PASS
- **磁盘**：`data/v2` ≈ 8.4G；1c85 panels ≈ 1.4G

---

## 最近补数亮点（2026-10-12）

| 项 | 状态 | 覆盖 |
|---|---|---|
| 北向持股 `hk_hold_ashare` | **已完成** | 2018-01-02 → **2025-06-30**（日频 A 股约至 2024-08-16；其后多为季末点） |
| 沪深港通 `hsgt_top10` | **未达目标** | 现 parquet **2018-01-02 → 2024-07-10**；目标 ≥2025-06；窗口续拉曾跑过，当前无活跃 runner |
| 两融个股 `margin_detail` | **已完成** | 2018-01-02 → **2026-10-09** |
| 解禁 `share_float` X1 | **已完成** | float_date **2015-01-05 → 2026-10-30**；X1(2015–17) ≈ 42,486 行 |
| 龙虎榜 X1 | **已完成** | top_list / top_inst_labeled **2015-01-05 → 2026-10-09** |
| 北向 moneyflow X1 | **已完成** | **2014-11-17 → 2026-10-09**（深股通自 2016-12-05） |
| ETF 份额流 `available_at` | **已有** | share 下一交易日 09:00 与 nav 日末取晚；信号须 asof，勿用当日 `trade_date` |
| 行业 ETF `trade_date` 类型 | **已对齐** | YYYYMMDD 字符串；权威 `ind_etf_share_flow_pit.parquet` |

---

## 1. 日线 / 面板

| 权威 path | date_min → date_max | nrows（约） | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/local_market/1c85fd9aceaa03c3c4863bec/panels/{ex.code}.parquet` | available_at **2014-01-02 → 2026-06-30**（抽样） | **≈11,905,370** / **6026** 标的 | 平台主面板（历史） | OHLCV、涨跌停、复权因子等；按标的分文件 |
| `data/v2/asof_extend_tushare_202610/panels/` | **2026-07-01 → 2026-10-09** | 5578 文件 × ~67 行 | **acceptance PASS**（默认 asof 扩展） | Tushare 扩展段；含 limit_up/down、tradestatus、adj_factor |
| `data/v2/asof_extend_202610/panels/` | 同窗口（约） | 5201 文件 | 回退/对照 | 旧 1c85 风格扩展；日历/d0 仍可能从此取 |
| `data/v2/etf_510300/panels/sh.510300.parquet` | available_at **2012-05-28 → 2026-10-09** | 3,490 | 研究/基准 | 沪深300ETF 单品种面板 |
| `data/v2/tushare_raw/daily/` | 按日文件 **20180102 → 20261009** | 2125 日文件 | raw | 日线 raw 分区 |
| `data/v2/delisted/delisted_daily_from2015_tushare.parquet` | **2015-01-05 → 2026-07-29** | 426,473 | 研究 | 退市股日线补全 |
| `data/v2/delisted/delisted_master_tushare.parquet` | list/delist 至 **2026-07-30** | 339 | 研究 | 退市主表 |

---

## 2. 市值

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet` | **2018-01-02 → 2026-10-09** | 9,756,821 | **PASS**（默认） | 流通市值日频；`promotion_approved` 列有 |
| `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` | **2015-01-05 → 2026-10-09** | 11,711,361 | 研究扩展 | 含 X1 早窗 |
| `data/v2/float_mktcap/float_mktcap_asof.parquet` | asof **2026-10-09** | 987 | 研究快照 | 日频稀疏后的 asof 点 |
| `data/v2/valuation/daily_basic_valuation_tushare.parquet` | **2018-01-02 → 2026-10-09** | 9,754,991 | 研究 | PE/PB 等 daily_basic 估值 |

---

## 3. 申万 SW_L1 PIT

| 权威 path | in_date_min → max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | **1984-05-09 → 2026-09-24** | 7,920 / 31 L1 / 5914 标的 | **PASS（晋级首选）** | 成分进出 + available_at |
| `data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet` | 1990-01-01 → 2026-09-24 | 12,925 | **研究、非晋级** | XLS 前缀映射；见 `NOT_PROMOTION_GRADE.md` |
| `data/v2/sw_l1_pit/industry_members_sw_l1.parquet` | 同上 | 7,115 | 研究 legacy | 当前成员投票法 |

---

## 4. 财务 PIT

| 权威 path | 日期列范围 | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/financials_pit/financials_pit_tushare.parquet` | end_date **1990-12-31 → 2026-09-30**；available_at → **2026-10-10** | 422,129 / 5910 标的 | **PASS** | 利润/指标 PIT；`available_at`=f_ann\|\|ann @18:00 SH |
| `data/v2/financials_pit/financials_available_at_tushare.parquet` | available_at **1995-01-05 → 2026-10-10** | 422,129 | 时机表（已被 numeric PIT 取代为默认） | 仅时机 |
| `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet` | **2018-01-02 → 2026-10-09** | 9,754,991 | 研究 | OCF/利润 日频 |

---

## 5. EP

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/ep/ep_pit_daily_tushare.parquet` | **2018-01-02 → 2026-10-09** | 9,754,901 | 研究（覆盖≈99.97%） | 日频 EP PIT；验收见同目录 acceptance.json |
| `data/v2/financials_pit/ep_tushare_asof_20260630.parquet` 等 | asof 点 | — | 研究快照 | 截面 EP |

---

## 6. 分红 / 除权

| 权威 path | 日期范围 | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/corporate_actions/dividend_tushare.parquet` | ex 相关 **1991-02-26 → 2026-10-23** | 268,204 | **PASS**（默认 `load_dividends`） | 分红全量 |
| `data/v2/corporate_actions/dividend_by_exdate_tushare.parquet` | **2024-01-02 → 2026-10-09** | 15,278 | 研究/对账窗 | 按除权日切片 |
| 同目录 reconcile / eastmoney 交叉 | 2024+ | — | 研究 | 除权缺口对账产物 |

---

## 7. 涨跌停 / 停牌

| 权威 path | 覆盖 | 规模 | 晋级/研究 | 备注 |
|---|---|---|---|---|
| 1c85 panels 内 `upper_limit`/`lower_limit`/`tradestatus` | 随面板 **2014→2026-06** | 见上 | 主路径 | 覆盖率见 `docs/v2/LIMIT_COVERAGE_2018.md` |
| asof_extend_tushare panels `limit_up`/`limit_down` | **2026-07→2026-10** | 5578 标的 | PASS 扩展 | |
| `data/v2/tushare_raw/stk_limit/` | 按日 **20180102→20261009** | **2125** 日文件 | raw | |
| `data/v2/tushare_raw/suspend_d/` | 同上 | **2125** 日文件 | raw | |

---

## 8. ST

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/st_flags/is_st_daily_2018_2026.parquet` | **2018-01-02 → 2026-10-09** | 320,476 | 研究 | 日频 is_st |
| `data/v2/st_flags/st_intervals_tushare.parquet` | **2000-02-21 → 2026-09-30** | 2,716 | 研究 | ST 区间 |
| `data/v2/st_events/st_events_from_namechange.parquet` | — | 3,763 | 研究 | 更名推导 ST 事件 |
| `data/v2/delisted/delisted_is_st_daily_from2015.parquet` | **2015-01-05 → 2026-04-30** | 134,312 | 研究 | 退市股 ST 日旗 |

---

## 9. 龙虎榜

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/dragon_tiger/top_list.parquet` | **2015-01-05 → 2026-10-09** | 185,970 | 研究 | X1 已补；available_at=T日 18:00 SH |
| `data/v2/dragon_tiger/top_inst_labeled.parquet` | 同上 | 2,281,288 | 研究 | 含 seat_type / is_institution |
| `data/v2/dragon_tiger/exalter_institution_map.parquet` | — | 19,674 席位 | 研究 | 席位类型映射 |
| 文档 | — | — | — | `docs/v2/DRAGON_TIGER_COVERAGE.md`、`BETA_X1_EVT_FLOW_COVERAGE.md` |

---

## 10. 北向

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/northbound/moneyflow_hsgt_daily_2018plus.parquet`（同内容 `…_2014plus`） | **2014-11-17 → 2026-10-09** | 2,800 | 研究 | 沪 20141117 起；深 sgt **20161205** 起；available_at=T 18:00 |
| `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet` | **2018-01-02 → 2025-06-30** | 3,715,734 | 研究 | **已补至 20250630**；日频 A 约至 20240816，其后季末点 |
| `data/v2/northbound/hsgt_top10_daily_2018plus.parquet` | **2018-01-02 → 2024-07-10** | 22,480 | 研究 | **未达 ≥2025-06**；raw `tushare_raw/hsgt_top10/` 同步至 20240710 |

---

## 11. 两融

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/margin/margin_detail_daily_2018plus.parquet` | **2018-01-02 → 2026-10-09** | 5,786,686 | 研究 | 个股明细；available_at=**T+1 09:00**；max available_at≈2026-10-12 09:00 |
| `data/v2/margin/rzrq_daily_tushare.parquet` | 同上 | 5,786,686 | 研究 | 与 detail 同源重建 |
| `data/v2/margin/margin_exchange_daily_merged.parquet` | **2014-01-02 → 2026-10-09** | 7,088 | 研究 | 交易所汇总 = 2014–17 ∪ 2018+ |
| `data/v2/margin/margin_exchange_2014_2017.parquet` | **2014-01-02 → 2018-01-05** | 1,962 | 研究 | Beta X1 MARGIN 臂 |

---

## 12. 解禁 share_float

| 权威 path | float_date 范围 | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/share_float/share_float_pit.parquet` | **2015-01-05 → 2026-10-30** | 6,449,659 | 研究 | **权威全量**；X1≈42,486；available_at=ann_date 18:00；5361 代码 |
| `…/share_float_2015_2017.parquet` | 2015–17 | 42,486 | 研究 sidecar | |
| `…/share_float_2018plus.parquet` | 2018+ | 6,407,173 | legacy | 请改读全量 PIT |

---

## 13. ETF 份额流

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet` | **2014-01-02 → 2026-10-09** | 1,578,335 | 研究 | 全 ETF；**有 available_at**（share T+1 09:00 vs nav 日末取晚） |
| `…/etf_share_flow_pit_industry_theme.parquet` | 同上 | 223,545 | 研究 | SW L1 映射主题 ETF |
| `…/ind_etf_share_flow_pit.parquet` | 同上 | 223,286 | 研究 | 行业 ETF 预 join；`trade_date`=YYYYMMDD str |
| `…/ind_etf_share_flow_by_sw_l1.parquet` | 同上 | 51,728 | 研究 | 按申万一级汇总 |
| `…/etf_share_flow_pit_major.parquet` | 2018-01-02 → 2026-10-09 | 14,258 | 研究 | 主要宽基等 |

---

## 14. 可转债事件

| 权威 path | 日期范围 | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/cb/events/cb_forced_redemption_pit.parquet` | exclude_from_ann **2004-04-14 → 2026-09-23** | 630 | 研究 | 强赎排除日 |
| `data/v2/cb/events/cb_remain_size_pit.parquet` | **2000-07-04 → 2026-10-10** | 108,034 | 研究 | 余额 PIT |
| `data/v2/cb/events/cb_call_trigger_hist.parquet` | **2004-04-14 → 2026-10-09** | 894 | 研究 | 赎回触发史 |
| `data/v2/cb/raw/` | — | — | raw | cb_daily / cb_call / cb_share / cb_rate |

---

## 15. 国债期货 / 利率

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/futures/bond_fut_daily.parquet` | **2013-09-06 → 2026-10-09** | 26,388 | 研究 | 国债期货日线 |
| `data/v2/futures/bond_fut_main_map_pit.parquet` | **2013-09-06 → 2026-10-12** | 8,800 | 研究 | 主力映射 PIT |
| `data/v2/futures/bond_fut_contracts.parquet` | — | 155 | 研究 | 合约静态 |
| `data/v2/futures/bond_fut_margin_*.parquet` / fee | — | — | 研究 | 保证金/手续费 |
| `data/v2/rates/lpr.parquet` | **2013-10-25 → 2026-08-20** | 1,532 | 研究 | LPR 1y/5y |
| `data/v2/rates/shibor.parquet` | **2014-01-02 → 2026-10-10** | 3,162 | 研究 | Shibor 各期限 |

---

## 16. 公告文本语料 / 分类事件

| 权威 path | date_min → date_max | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/events/announcements_classified_pit.parquet` | ann **2018-01-01 → 2024-05-31** | 1,440,145 | 研究 | 规则分类事件叶 |
| `data/v2/events/announcements_classified_pit_post202406.parquet` | **2024-06-01 → 2026-10-11** | 701,817 | 研究 | 后段；合计 ≈ **2.14M** |
| `data/v2/text/ann_embedding_corpus_pit.parquet` | available_at **2018-01-01 → 2026-10-11** | 2,306,969 | 研究 | 嵌入语料（无正文） |
| `…/ann_embedding_corpus_pit_with_body.parquet` | → **2026-10-10** | 1,651,413 | 研究 | 含正文子集 |
| `data/v2/announcements/{eastmoney,cninfo}/by_stock*` | 按股分文件 | 东财≈327+2189；巨潮≈1319+1402 | raw/研究 | 标题+URL；正文不全 |
| `data/v2/text/em_heat/*` | 快照 | 极少行 | 研究试点 | 股吧热度等 |
| `data/v2/text/xueqiu/` | — | — | **BLOCKED** | 见目录 BLOCKED.md |

---

## 17. 其它重要表

| 权威 path | 日期范围 | nrows | 晋级/研究 | 备注 |
|---|---|---|---|---|
| `data/v2/index_members/index_member_events.parquet` | available_at **2018-05-25 → 2026-05-29** | 5,840 | 研究 | 指数成分进出事件 |
| `data/v2/index_members/index_weight_csi300_500_1000.parquet` | **2018-01-31 → 2026-09-30** | 189,000 | 研究 | 中证 300/500/1000 权重 |
| `data/v2/index_members/csi_review_calendar.parquet` | **2018-05-25 → 2026-05-29** | 17 | 研究 | 调样日历 |
| `data/v2/index_global/index_global_raw.parquet` | **2014-01-02 → 2026-10-09** | 9,567 | 研究 | 全球指数 raw |
| `data/v2/tushare_raw/daily_basic/` | **20150105 → 20261009** | 2857 日文件 | raw | 含较早基本面日频 |
| `data/v2/tushare_raw/adj_factor_hist/` | **20140102 → 20260630** | 3035 日文件 | raw | 复权因子史 |
| `data/v2/d1_masks/prototype_*` | 单日原型 | — | 原型 | D1 成员掩码脚手架 |

---

## 晋级数据集速查（acceptance PASS，平台默认）

来源：`docs/v2/PROMOTION_ACCEPTANCE.json` + `ACCEPTED_DEFAULTS.md`（overall=true）：

- SW_L1：`sw_l1_pit/industry_members_sw_l1_tushare.parquet`
- 流通市值日频：`float_mktcap/float_mktcap_daily_tushare.parquet`
- 日线 asof 扩展：`asof_extend_tushare_202610/panels`
- 财务 PIT：`financials_pit/financials_pit_tushare.parquet`
- 分红：`corporate_actions/dividend_tushare.parquet`

其余事件/资金流/北向/两融明细/解禁/ETF 份额等均为 **研究级**（`promotion_approved=false`），可喂 Alpha/Beta 冒烟，不视为策略晋级依据。

---

## 已知缺口（审计时点）

1. **hsgt_top10**：权威表仅到 **2024-07-10**，目标 ≥2025-06 未完成；续拉需重启 runner。
2. **hk_hold**：2024-08 后官方日频 A 股披露变稀，仅季末等点有完整 A 行——勿当全日频。
3. **分类公告** 主表前段止于 2024-05；后段另文件；anns 高峰日可能截断。
4. **雪球文本**：blocked。
5. **1c85 主面板** available_at 抽样止于 **2026-06-30**；2026-07+ 靠 asof_extend_tushare。

原始抽样 JSON：`docs/v2/_inventory_raw_stats.json`（机器可读，可删可留）。
