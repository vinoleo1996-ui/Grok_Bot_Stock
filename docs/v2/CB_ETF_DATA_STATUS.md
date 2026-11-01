# 可转债 / ETF / V3 数据状态（研究级，promotion_approved=false）
更新 2026-10-11 13:20 ET。队列与逐项状态见 output/d1/CB_ETF_QUEUE.md。

## 接口可用性（datahub 直连；relay 未用于本批）
| 接口 | 状态 |
|---|---|
| cb_basic / cb_daily(含 cb_value,cb_over_rate,bond_value,bond_over_rate 需显式 fields) / cb_share / cb_call / cb_rate | ✅ |
| **cb_price_chg** | **🔴 硬限：datahub "unknown api_name"，relay 返回空** → 下修改由 cb_share 转股价变动推导 |
| 回售专用接口（cb_put 等） | 🔴 不存在；回售只能从 cb_call.call_type 或公告标题提取 |
| **anns_d（公告）** | **🔴 datahub 403 无权限**；只能走 promax（另一任务限速中）|
| fund_basic / fund_daily / fund_adj / fund_div / fund_share / fund_nav | ✅；fund_share 单次 1000 行上限需分段 |
| fut_basic / fut_daily / fut_mapping / index_daily / index_global / shibor / margin | ✅（后台拉取中/已落）|
| 限速 | datahub 并发 4 时偶发 429，已退避；cb_share 按债逐只 ~5s/只 |

## 1. 可转债 data/v2/cb/
- cb_basic.parquet：1171 只（已退市 824）。
- cb_daily.parquet：2015-01-05→2026-10-09，2857 个交易日全覆盖、0 失败；1031 只有行情（含已退市 719 只）；771,832 实行。cb_value/cb_over_rate/bond_value/bond_over_rate 缺失 0.07%（2018 起 0.04%）。close=0 占位行 is_placeholder=True。
- 单位（实测 amount/(close·vol)=0.001）：**vol=手(10张)，amount=万元**。available_at=T 15:00 CST。
- 每年只数：2015:37 2016:24 2017:53 2018:128 2019:237 2020:421 2021:469 2022:538 2023:610 2024:595 2025:550 2026:445。
- 余额/条款事件：拉取中（cb_share→cb_call→cb_rate）。事件 available_at=公告日 18:00 CST（偏保守：多数公告盘后发布）。

## 2. ETF data/v2/etf/
- etf_basic.parquet：1838 只场内 ETF（含退市 127），分类（名称规则 v1，行业关键词优先）：行业 676、宽基 595、跨境 251、主题/其他 221、债券/货币 79、商品 16。
- etf_daily_adj.parquet：2015-01-05→2026-10-09，1,556,347 行、1821 只；含未复权 OHLC、adj_factor、*_hfq 后复权价；adj_factor/close 缺失 0。单位 **vol=手(100份)，amount=千元**。
- 与既有 510300 面板逐日对拍 2857 天，close 最大差 0。
- 511880/511010/518880/159934 2015-01-05→2026-10-09 全；511260 自 2017-08-24 上市起全。

## 3. 可交换债（132xxx.SH / 120xxx.SZ）交易规则
- 2022-08-01 起施行的沪深《可转换公司债券交易实施细则》（上证发〔2022〕117号等）规范对象为**上市公司可转债**，20% 涨跌幅 / 首日 57.3%/-43.3% 仅适用"向不特定对象发行的可转债"，**不覆盖可交换债**。来源：https://www.sse.com.cn/lawandrules/sselawsrules/bond/convertible/trading/c/c_20220729_10776075.shtml ；深交所细则 https://www.crsec.com.cn:9443/files/file/2022/08/01/6080c1ce-b431-4157-8c9b-0328559dc856.pdf
- 可交换债按交易所债券交易规则执行（无 ±20% 日涨跌停，有申报价格范围约束）；实测 2022-08 后 27 只 EB 中仅 1 个交易日 |pct_chg|>20%（31%），与"无 20% 硬限"一致。
- 印花税：证券交易印花税只对股票征收，债券（含可转债/可交换债）交易不征。交易单位：沪深债券 1 手=10 张（面值 1000 元）。
- ⚠ 上述 EB 结论为规则文本推断 + 数据实测，未找到专门针对 EB 涨跌幅的交易所条文，建议合规复核。

## 4. 其它已完成
- 中证调样日历 data/v2/index_members/csi_review_calendar.parquet（17 次，9 次公开报道核实，余规则推断且规则对已核实 9 次全中）；events ann_date 回填 98.2%。
- 费率/保证金核对 docs/v2/FUTURES_FEE_MARGIN_VERIFY.md（2022-07-22 保证金行判错）。
- Shibor 原始 data/v2/rates/shibor.parquet；两融交易所汇总 2014–2017 data/v2/margin/margin_exchange_2014_2017.parquet。
- 中性私募/雪球月度代理：无可靠公开免费源，不做、不编数。
