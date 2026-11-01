# 核对 EXECUTION_FUTURES_CASH.md 费率 / 保证金表（中金所公告）

口径：交易所标准（不含期货公司加收）。"结算时起"=当日结算即按新保证金计。

## FEE_TABLE（平今）
| 生效日 | 文档值 | 结论 | 依据 |
|---|---|---|---|
| 2010-04-16 | 0.000025 全部（近似） | ⚠未核实（官方初始标准未找到公开原文；保留近似） | — |
| 2015-09-07 | 平今 0.0023 | ✅ 对（平今=万分之23，开/平 0.23‰ 不变） | 中金所 2015-09-02 通知（经媒体转载） |
| 2017-02-17 | 0.00092 | ✅ 对 | https://www.nbd.com.cn/articles/2019-04-19/1323298.html（回顾历次调整） |
| 2017-09-18 | 0.00069 | ✅ 对 | 同上 |
| 2018-12-03 | 0.00046 | ✅ 对 | 同上；https://finance.caixin.com/2019-04-19/101406381.html |
| 2019-04-22 | 0.000345 | ✅ 对 | http://www.cffex.com.cn/cn/jystz/20190419/23719.html |
| 2023-03-20 | 0.00023 | ✅ 对（中金所发〔2023〕16号，含 IM） | https://www.bocifco.com/newsinfo.aspx?id=47985 ; http://www.cffex.com.cn/zjssf/20230320/23701.html |
| 开/平仓 0.000023 | — | ✅ 对（收费一览表：成交金额万分之零点二三） | http://www.cffex.com.cn/zjssf/20230320/23701.html |

## MARGIN_TABLE（交易所保证金）
| 生效日 | 文档值 | 结论 | 依据 |
|---|---|---|---|
| 2015-09-07 | 40%/40% | ✅ 方向对（非套保 40%；套保 20%）。注：2015-08-26～09-01 间另有 12→15→20→30% 多次上调，文档缺 | 中金所 2015-08/09 通知 |
| 2017-02-17 | IF/IH 20%，IC 30% | ✅ 对（非套保） | nbd 2019-04-19 回顾 |
| 2017-09-18 | IF/IH 15%，IC 30% | ✅ 对 | 同上 |
| 2018-12-03 | IF/IH 10%，IC 15% | ✅ 对 | https://www.xinhu.cn/article/...88662-1.html（转载中金所 2018-12-02 通知） |
| 2019-04-22 | IF/IH 10%，IC 12% | ✅ 对 | https://www.jiemian.com/article/3058082.html |
| 2022-07-22 | IF/IH 12%，IC 14%，IM 15% | ❌ 不可信：当前（2026）交易所标准 IF/IH/IC/IM 均为 12%（期货公司常见 13–14%，"IC 14%" 疑为公司保证金）。IF/IH 何时由 10% 调至 12% 未找到公告原文，需人工到 cffex.com.cn 核对 | https://www.ccbfutures.com/main/a/20260506/77818.shtml ; https://www.guoshengqh.com/storage/file/20260929/dfa9b0fd9cd25cbe8350dd051c2c9ed4.pdf |

建议：2022-07-22 行改为 IM 上市即 12%（待核），并在找到原文前对 2019-04-22 之后的 IF/IH 保证金做 10%/12% 敏感性。cffex.com.cn 在 box 上可达性不稳定，未逐条取原文 PDF。

## 国债期货 T/TF/TS/TL（Eng 假设核对，2026-10-11 16:18 ET）

口径：交易所最低保证金 / 涨跌停板 / 交易所手续费（不含期货公司加收）。Eng 假设：涨跌停 T 2%、TF 1.2%、TS 0.5%、TL 3.5%；保证金=涨跌停；手续费每手 3 元。

### 涨跌停板（vs 上一交易日结算价）
| 品种 | Eng 假设 | 结论 | 依据 |
|---|---|---|---|
| T | ±2% | ✅ 对 | 合约表 http://www.cffex.com.cn/cn/10t.html ；细则 http://www.cffex.com.cn/cn/ssxz/20200612/43096.html（2020-06-12） |
| TF | ±1.2% | ✅ 对 | 合约表 http://www.cffex.com.cn/cn/5tf.html ；细则 http://www.cffex.com.cn/cn/ssxz/20200612/43095.html |
| TS | ±0.5% | ✅ 对 | 合约表 http://www.cffex.com.cn/cn/2ts.html ；细则 PDF http://www.cffex.com.cn/u/cms/www/202601/241747392v9l.pdf |
| TL | ±3.5% | ✅ 对 | 合约表 http://www.cffex.com.cn/cn/30tl.html ；细则 http://www.cffex.com.cn/cn/ssxz/20230414/43097.html ；上市通知 http://www.cffex.com.cn/cn/jystz/20230414/32098.html（2023-04-14，上市当日 ±7%） |

### 最低交易保证金（交易所标准，非交割月）
| 品种 | Eng 假设（=涨跌停） | 结论 | 实际 | 依据 |
|---|---|---|---|---|
| T | 2% | ✅ 对 | 2%（交割月前两交易日起 3%） | 同上 T 合约表/细则 |
| TF | 1.2% | ✅ 对（实际执行） | **实际执行 1.2%**（交割月前两交易日起 2%）。细则/产品页写「最低」1%，但 2015-03-10 通知起新合约执行 1.2%，此后无下调至 1% 的公告；fut_settle 与期货公司「交易所栏」均为 1.2% | http://www.cffex.com.cn/cn/jystz/20150310/18713.html ；沿革表 data/v2/futures/bond_fut_margin_official.csv |
| TS | 0.5% | ✅ 对 | 0.5%（交割月前两交易日起 1%） | 同上 TS；上市通知 http://www.cffex.com.cn/jystz/20180807/22445.html（2018-08-07） |
| TL | 3.5% | ✅ 对 | 3.5%（交割月前两交易日起 5%） | 同上 TL；上市通知 2023-04-14 |

### 手续费（交易所）
| 项 | Eng 假设 | 结论 | 依据 |
|---|---|---|---|
| 开仓 / 平昨 | 每手 3 元 | ✅ 对 | 各品种上市通知均写「暂定每手 3 元」；收费一览表 http://www.cffex.com.cn/cn/zjssf/20260601/47965.html 、http://www.cffex.com.cn/cn/zjssf/20240701/39212.html（明文 3 元/手） |
| 平今 | （futures.py 表按 3 元保守） | ⚠ 偏严 | 官方：**平今仓免收**。交割手续费每手 5 元（TL 上市初期曾减半至 2023-12-31）。建议 BOND_FEE_TABLE close_today 改为 0 |

### 建议改 futures.py
- `BOND_MARGIN_TABLE`：TF 保持 **0.012**（实际执行；勿改成细则字面 0.01）
- `BOND_FEE_TABLE`：close_today 3 → **0**（开/平昨保持 3）
- 涨跌停四档可保留，已核实

