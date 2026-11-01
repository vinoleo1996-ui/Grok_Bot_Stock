# 业界日频多因子股票池惯例核查

- 日期：2026-10-14（ET）
- 问题：市面上主流股票多因子，是否普遍「每个交易日对全市场（或全可交易股票）统一算因子、截面排序，再按规则选 TopN/分位数建仓」，而不是先锁死小池（如仅市值前 300）再在池内选？
- 范围：开源平台、国内投研平台、Barra/公募表述；**不改代码**，仅作业界对照。

---

## 结论（一句话）

**是：主流日频多因子的主流程是「宽可交易宇宙（全 A / 流动性过滤全市场）上的截面打分与排序 → TopN 或分位数组仓」；「仅在市值前 300 内选」不是主动多因子选股的默认范式，而是指数增强或演示基准的特例。**

更精确的表述：宇宙通常是「可交易全市场」（剔 ST、停牌、次新、极低流动性），不是字面意义上的每一只垃圾股；但相对「先锁死 CSI300/市值 top300 再池内选」，业界默认是**先宽池截面，再建仓规则**。

---

## 与「仅在 top300 内选」的对比

| 维度 | 仅 top300 / CSI300 池内选 | 主流主动多因子 |
| --- | --- | --- |
| 因子截面 | 只在约 300 只里 rank | 在全 A 或 TOP2000–TOP3000 级宽池里 rank |
| 选股自由度 | 受成分约束，易变成「指增味道」 | TopN/分位数由分数决定，行业/市值可内生暴露 |
| 典型用途 | 沪深300增强、教学 demo、跟踪误差硬约束 | 全市场量化选股、「空气指增」、对冲基金截面 alpha |
| 二次过滤 | 池已很小，再滤流动性 | 宽池算完后可按 ADV/涨跌停做可成交过滤（容量约束） |

---

## 证据列表（带 URL）

### 1) 开源与平台

1. **microsoft/qlib**：基础市场名为 `all`（`D.instruments(market='all')`）；CSI300 是可选预定义池，不是唯一范式；默认用动态股票池。  
   - https://qlib.readthedocs.io/en/stable/start/getdata.html  
   - https://github.com/microsoft/qlib/blob/main/examples/tutorial/detailed_workflow.ipynb  

2. **Quantopian / alphalens**：工作流第 1 步是宽 universe 筛选；第 2 步是「对 universe 内股票做截面排序」；设计假设是「传统股票 alpha 对大宇宙做 cross-sectional rank」。  
   - https://quantopian-archive.netlify.app/forum/threads/alphalens-a-new-tool-for-analyzing-alpha-factors.html  
   - https://github.com/quantopian/alphalens/  

3. **WorldQuant BRAIN**：`rank`/`zscore`/`scale` 为截面算子，在所选 universe 当日全体股票上运算；公开 universe 为流动性分档 **TOP3000 / TOP2000 / … / TOP200**（宽流动性池），不是「先锁 300 再选」。  
   - https://roger2389.github.io/WorldQuant-Introduction/  
   - （社群复述）https://wiki.untymen.com/en/%E7%BB%8F%E6%B5%8E%E5%AD%A6/WorldQuant/0%EF%B8%8F%E2%83%A3Data%20and%20its%20operations/  

4. **RiceQuant / RQFactor**：横截面算子 `RANK`/`CS_ZSCORE`/`QUANTILE` 在「当日股票池」上计算；`execute_factor(..., universe=None)` **默认 None = 全市场**；文档明确横截面因子值依赖整个股票池。  
   - https://www.ricequant.com/doc/rqfactor/api/factor-calculation  
   - https://www.ricequant.com/doc/rqfactor/manual/quick-start  
   - https://www.ricequant.com/doc/rqfactor/api/built-in-operators  

5. **JoinQuant 聚宽（社区/教程惯例）**：典型流程 `get_all_securities` → 剔 ST/停牌/退市/次新 → `get_factor_values` 截面打分 → 按总分排序取前 N 或前分位。也有用指数成分做简化 demo 的例子，但漏斗起点仍是「全市场再过滤」。  
   - 示例综述：https://blog.csdn.net/weixin_30904593/article/details/98088174  
   - https://easyquant.ai/e/joinquant/joinquant-layered-breakout-stock-selection-score  

6. **BigQuant**：明确「股票池：全 A，剔除停牌和 ST」→ `c_rank` 截面因子 → `score_to_position` 按分取前 30。  
   - https://bigquant.com/wiki/doc/GImenVoJyx  

7. **vnpy alpha**：框架支持任意成分/`AlphaLab` 股票池；官方示例常下沪深300作 demo，但 API 可换全 A 成分（非强制 top300）。  
   - https://github.com/vnpy/vnpy/blob/master/examples/alpha_research/download_data_rq.ipynb  
   - https://github.com/vnpy/vnpy/blob/master/vnpy/alpha/lab.py  

### 2) 业界 / 教材 / 公募表述

8. **MSCI Barra GEMTR**：估计宇宙为 **MSCI ACWI IMI（可投资市场宽指数）**，每日截面回归估计因子收益；覆盖数万只股票，而非窄基准成分。  
   - https://cdn2.hubspot.net/hubfs/2174119/Return%20Downloads/Datasheet%20-%20Barra%20Global%20Total%20Market%20Equity%20Trading%20Model.pdf  

9. **A 股公募量化常见表述**：全 A / 中证全指覆盖数千只、剔除 ST 等后多因子打分；「空气指增」类产品以全市场选股对标全指，行业与风格由模型内生（相对成分内增强）。  
   - 例：兴全全指指增相关报道 https://finance.sina.com.cn/money/fund/jjgsgd/2026-05-11/doc-inhxpxxc8848481.shtml  
   - 质量股票池构造（券商研报类）：先宽池再过滤再打分 http://www.hibor.com.cn/repinfodetail_1637344.html  

---

## 明确例外（不推翻主结论）

| 例外 | 说明 |
| --- | --- |
| **指数增强** | 常限成分内（沪深300 / 中证500 / 1000）或「成分 + 少量卫星」，主目标是控跟踪误差，不是自由全市场选股。 |
| **教学 / 开源 demo** | qlib、聚宽、vnpy 示例大量用 CSI300，多为数据量与可复现，不等于业界默认。 |
| **行业轮动 / 主题** | 先定行业再在行业内排序，但仍是该层宇宙的截面，不是「永久锁死市值 top300」。 |
| **容量二次过滤** | 宽池打分后按 ADV、涨跌停、可成交量过滤小盘——这是**建仓约束**，不是把因子截面缩成 top300。 |
| **两段漏斗** | 先用市值/流动性粗筛（如 ADV>阈值、非 ST）再打分：粗筛后仍是数千只级宽池，≠ 仅 300 只。 |

---

## 对我们「全 A」决策的含义（不改代码）

1. **Leo 拍板「全 A 可交易掩码统一算因子再排序」与业界主动多因子主流程一致**；相对旧「仅在前 300 里挑」，是纠正产品形态（主动截面选股 vs 伪指增）。  
2. 业界「全市场」几乎总带可交易过滤（ST/停牌/次新/流动性），QuantLab 的 FULLA 掩码（剔 ST、停牌、上市不足、ADV）方向正确。  
3. 若某条腿要对标沪深300增强，应**显式标成指增约束**，不要与全 A 主动腿共用同一套「池内选」叙事。  
4. 容量仍可用 ADV/分档做**建仓后过滤**，不必为了容量把截面宇宙缩回 top300。  
5. 本文仅业界对照；内部是否每条路径已切全 A，见另文审计，不在此改代码。

---

## 五条最硬证据（摘要）

1. RiceQuant：`universe=None` = 全市场；横截面 RANK 依赖整个股票池。  
2. BigQuant 全 A 策略：全 A 剔 ST/停牌 → 截面 `c_rank` → Top30。  
3. Alphalens/Quantopian：alpha = 对宽 universe 的截面排序。  
4. WorldQuant BRAIN：截面算子作用在 TOP3000 级宽流动性宇宙（非 top300 锁死）。  
5. Barra GEMTR：估计宇宙 = ACWI IMI 宽市场，截面回归。

