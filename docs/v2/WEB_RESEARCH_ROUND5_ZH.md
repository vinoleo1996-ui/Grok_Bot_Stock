# 网研第五轮（2026-10-13 ~20:30 ET，研究级）
红线同前。已否方向不再开：重大合同、行业 ETF 申赎反转、问询回函、分拆上市、锁价定增、指数纳入、战略合作、放量事件簇；及叶1–8、已灭各包。

## A. 盘上可做 → 已开叶9
**中期分红首次/大幅提升预案**（dividend_tushare.parquet，ann_date 满窗至 2026-10-10，PIT=预案公告日）。
- 来源：Michaely, Thaler & Womack (1995, JF) 分红首发漂移；A 股 2002–2004 样本 https://www.1mishu.com/lunwen/jjgl/jjbylw/201004/684152.html （首次发放超常收益最高）；反面 http://www.abslw.com/29/abs1627529.html （年报同日披露，信号难识别）、https://www.lunwendata.com/thesis/2015/48337.html （长期漂移不显著）。
- 与 V33（分红实施日短窗，reject）不同构：用预案的派息**变化**信号，不用实施日。
- 结果：见 AI_G1G5_INTERIM_DIV_INIT_WEIGHT_RECEIPT_ZH.md → WATCH。

## B. 盘上无数据 → 等 Data
| 方向 | 依据 | 所需数据 | 状态 |
|---|---|---|---|
| 公募季报持仓拥挤/减配 | 开源金工 https://finance.sina.com.cn/roll/2024-08-31/doc-incmpyvx9111123.shtml | fund_portfolio（含 ann_date） | 等 Data（已排队） |
| 分析师全部上调 | 国信金工 https://bigquant.com/wiki/doc/mXJ6ppnrEd | report_rc | 等 Data（拉取中） |
| 机构调研密集 | 华泰金工 https://finance.sina.com.cn/stock/stockzmt/2021-03-29/doc-ikknscsk3540018.shtml | stk_surv + 披露滞后 | 等 Data |
| 股权激励强度分层 | 第二轮 | EM RPT_EQUITY_INCENTIVE 规模/考核门槛 | 等 Data（属叶6 加强，非新叶） |

## C. 盘上有数据但不开
- 分红**实施**/股息率排序：V33 已 reject / 教科书因子。
- 问询函、分拆、锁价定增：第四轮已否。
