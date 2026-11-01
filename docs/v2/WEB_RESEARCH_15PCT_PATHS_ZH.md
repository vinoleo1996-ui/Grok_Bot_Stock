# 网络调研：A股+ETF 账户 15% 净年化的可行路径（机制优先）
日期：2026-10-13 ｜ 范围：60万–100万，偏多头，不做小盘、不用 GP、不加高杠杆，可转债/黄金不做主仓 ｜ 只做研究，不改代码，live=false

> 规则：下面的数字都是原文给出的口径（大多是研报样本内回测或事件均值，没扣成本）。没查到的标「未知」。所有数字都要在我们自己的 X2/PIT 框架里复现，复现前不能采信。
> 判断背景：capacity_adv 是按容量加权的中大盘个股组合。之前 13 叶失败，主要是同质的量价/资金流信号（moneyflow_resid、margin_delta 和主干超额相关约 0.95）。之前组合 0/6，是因为「低相关」其实来自 β 差异。所以下面优先选**事件和制度驱动、时点离散、有明确对手方**的收益来源。

## 候选清单

### C1 指数定期调样：预测调入 + 公告到实施窗口
- 机制：中证/上证指数每年 6 月和 12 月调样，深证每年 1 月和 7 月。被动资金要在实施日前被动买入调入股、卖出调出股。规则公开，名单可以提前预测。
- 谁付钱：跟踪指数的被动基金和 ETF。它们必须在实施日附近按收盘价成交，付出冲击成本，相当于为「确定性」付流动性溢价。
- 证据：
  - 华创 2025-12：沪深300 调入股公告前 10 日平均超额 +2.48%，公告后 10 日 +3.20%；调出股公告前、后 10 日分别 −4.03% 和 −4.04%。中证500 调入股公告后 10 日是 −1.40%，效应已经前移。https://www.fxbaogao.com/detail/5410272
  - 回顾报告：2012 年以来沪深300 调入组合在 R2（公告后 10 日）胜率 67%，次均超额 1.26%；中证500 胜率 71%，次均 0.57%，2017-06 以后胜率 80%。https://www.hangyan.co/reports/3500707111195641816
  - 中信系（格隆汇转载）：2023 年以后，沪深300 公告后 10 日超额升到 4.64%，上证50 升到 6.77%。高冲击系数的样本更强。https://m.gelonghui.com/p/2142036
- 独立性：**中高**。一年只在约 2–4 个离散窗口持仓，收益来自被动资金流，不是截面因子。注意：我们已有的 idx_rebal_flow 叶失败了，必须先查清它是怎么做的（是不是做成了常驻因子、有没有用预测名单、窗口是否对），确认这次是不同的实现再立项。
- 数据：成分股历史在 tushare index_weight 和 akshare 都有；按规则预测需要日均市值、成交额，免费数据可以覆盖。冲击系数需要被动 AUM，可以用 ETF 份额乘净值来近似。
- 容量：60–100万完全没问题。
- 拥挤：**高且在上升**，公告前就被抢跑。可靠的做法是「预测 → 公告前布局」，并且只做高冲击系数的票。

### C2 业绩预告/快报「相对一致预期的惊喜」+ PEAD
- 机制：A 股对盈利信息反应不足，预告超预期之后价格持续漂移约 3 周到 60 日。
- 谁付钱：反应慢、注意力有限的投资者，以及有报告期约束的机构。他们滞后调仓。
- 证据：
  - SSRN 4589824（Lan 等）：用隔夜收益度量惊喜（ORJ），每季度超额市场平均 6.78%，只做多几十只票，FF3 解释不了。https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4589824
  - RMIT 2000–2008 样本：多空（最高减最低惊喜十分位）60 日 7.92%。https://scholarpublishing.org/journals/index.php/ABR/article/download/526/544/693
  - 中邮 2026：只有「预增+超预期」「略增+符合/超预期」「首亏/预减+超预期」胜率和赔率都好；高增速本身不给超额。https://cnpsec.com/plat_files/upload/png_upload/20260212/202602121770876800078.pdf
- 独立性：**中**。事件型，按季集中在 1、4、7、10 月，和主干的容量加权有交集，但信号来源不同。
- 数据：我们已经有 forecast_1y 和 express_1y 的 PIT（东财）。一致预期是付费数据（Wind/朝阳永续），免费替代是用「隔夜跳空 + 预告增速相对上年同期」来代理惊喜，SSRN 那篇用的正是隔夜收益口径。
- 容量：足够。拥挤：中（PEAD 是公开因子），但「预告 + 隔夜」的组合口径不算教科书版本。

### C3 分析师一致上调 / 研报超预期事件
- 机制：财报后多家分析师同时上调盈利预测，是信息扩散的信号。
- 谁付钱：反应慢的资金。
- 证据：国信金工：财报后 5 日内至少 3 家覆盖且全部上调，事件后 60 日平均超额 6.5%；研报标题「超预期」平均 6.2%；超预期精选组合年化 35.09%（相对中证500 超额 31.73%，样本内）。https://bigquant.com/wiki/doc/mXJ6ppnrEd
- 独立性：中，和 C2 高度相关，应合并成一个「盈利信息事件」叶。
- 数据：**免费数据不足**。研报标题和预测明细需要付费，东财研报页可以爬标题和评级，但 PIT 难保证。
- 容量：足够。拥挤：中高。

### C4 定增/首发解禁「负面清单」
- 机制：解禁前供给冲击和抢跑卖出。作为**剔除过滤器**，在主干持仓里避开解禁窗口。
- 谁付钱：被迫或主动减持的锁定股东（尤其定增基金，减持动机最强），以及不看日历的持有人。
- 证据：
  - 中金 2018：定增解禁前后 60 日都跑输基准，解禁前 5 日负超额最明显，解禁比例越高越差；首发原股东解禁后 60 日有反弹。https://bigquant.com/wiki/doc/9TrkvC0hV5
  - 2009 年以来统计：[T−10, T] 累计超额 −1.66%，[T, T+40] +0.44%。https://business.sohu.com/20181211/n557925721.shtml
- 独立性：**高（作为 overlay）**。不是新叶，是对 capacity_adv 持仓的规避规则，直接减少主干的左尾。
- 数据：tushare share_float 和 akshare 解禁日历都免费，可以做 PIT（日历事先公告）。
- 容量：无限制，只是少买。拥挤：低到中。
- 价值：如果主干持仓常碰到大比例定增解禁，每年可能省下零点几个百分点。具体要用主干的持仓实测，**数字未知**。

### C5 重大负面事件 overlay（减持预告、质押高位、业绩预减）合并过滤
- 机制和谁付钱同 C4：知情内部人卖出，持有人承担损失。
- 证据：中金同一报告建议把解禁、业绩预减、高管减持做成负面清单来增强选股。增强的具体数值在摘要里看不到，**未知**。https://bigquant.com/wiki/doc/9TrkvC0hV5
- 数据：我们已有 holder_trade_1y 和 pledge_latest 的 PIT。**成本最低、复用现有数据**。
- 独立性：高（overlay）。拥挤：低。

### C6 回购/实控人增持事件（只做多）
- 机制：管理层用真钱表达信号，回购本身也形成持续的买盘。
- 谁付钱：误定价时的卖方，以及回购期间卖给公司的流动性提供者。
- 证据（东财转载的策略报告）：预案公告后 30 日和 90 日相对收益均值约 1.17% 和 1.94%；完成公告后 1 年和 2 年约 6.42% 和 11.32%。回购比例超过 1%、注销式、低 PB 的更优。公告日脉冲约 1.70%，随后回落，不宜追。https://pdf.dfcfw.com/pdf/H3_AP202503271648248814_1.pdf?1743104408000.pdf= ；开源量化评论 118（股权激励+回购）https://fxbaogao.com/detail/5266115
- 独立性：中高。数据：tushare repurchase、东财免费。容量：足够。拥挤：中，2024 年以后回购数量大增，效应可能被稀释。

### C7 行业 ETF 轮动（景气度 + 趋势 + 拥挤度 / ETF 资金流反转）
- 机制：行业景气的趋势延续，加上过热时回避（拥挤度）；ETF 资金极端流入后反转。
- 谁付钱：追涨的散户和 ETF 申购资金，即在拥挤处买入的人。华泰原文明确写了这种「非信息性大额交易」造成的价格扭曲。
- 证据：
  - 国盛 2026 年度专题：多头年化 26%、超额 16%、最大超额回撤 4%（样本内）；ETF 配置直接法 2016 年以来相对中证800 年化超额 15%，夏普 1.7。2025 年实盘跟踪超额 21.4%。http://fxbaogao.com/detail/5691751 ，https://www.sgpjbg.com/bgdown/1036354.html
  - 华泰 ETF 资金流反转：周频多头年化超过 20%，超额超过 26%（2018-01 到 2024-07 样本内）。https://finance.sina.com.cn/roll/2024-10-17/doc-incswhzt9440591.shtml
  - 华泰 2026 年 3 月反思：行业轮动是「崎岖之路」，残差动量和拥挤度经受住了检验，北向因子已经拿不到数据。https://finance.sina.com.cn/wm/2026-03-27/doc-inhskrvx9631921.shtml
- 独立性：**中**。行业暴露会和主干重叠，必须用「超额相关 + 行业残差」来验收，不能看总收益相关。注意我们的 etf_core_sleeve 失败过。
- 数据：ETF 日行情和份额（tushare fund_daily / fund_share、akshare）免费；景气度需要财报和一致预期，可以只用财报部分。
- 容量：足够。拥挤：中高，各家券商都在发。

### C8 股指期货贴水 carry（用期货多头替代部分现货 β）
- 机制：中性产品和雪球对冲导致长期贴水；分红季（4–8 月）IF/IH 有可预期的分红贴水。持有期货多头加现金，就能赚到贴水收敛。
- 谁付钱：对冲需求方（中性私募、雪球发行商的套保盘），他们为空头保护付溢价。
- 证据：2024-06 主力年化基差 IF −14.72%、IC −18.95%、IM −24.53%（证券时报）https://stcn.com/article/detail/1916544.html ；建信期货的分红季跨期价差策略约年化 2%，胜率 85% 以上 https://www.ccbfutures.com/main/a/20230628/61674.shtml ；国联期货：中性规模与贴水正相关 https://www.glqh.com/u/cms/www/202403/03215811exnl.pdf
- 独立性：**高**，收益来自衍生品对冲需求，和选股无关。
- **硬约束**：股指期货开户要 50万 资金和适当性测试；IF 一手名义值约 4000×300 ≈ 120万，IC/IM 一手名义值也在百万以上。**60万 账户做不了 1 手且不加杠杆**，100万 也只能勉强 1 手。中证1000 股指期权和 MO 合成也有门槛。结论：**当前 AUM 不可行**，作为扩容后（≥150–200万）的储备。
- 数据：tushare fut_daily 免费。

### C9 510300 单资产波动率目标 / 回撤控制
- 证据（反面）：2018–2026 年沪深300 用 20 日已实现波动率做管理，年化从 2.4% 降到 0.6%，夏普从 0.22 降到 0.12，最大回撤仍约 46%。原因是 V 型反弹时滞后信号卖在了底部。https://taolike.net/reports/vol-managed-ashare ；理论条件见北大文 https://math.pku.edu.cn/finance/docs/20200729123502538771.pdf
- 谁付钱：不清楚，**没有明确的对手方**。
- 结论：**不建议**把它当作提高 CAGR 的手段。主干 MDD 只有约 −10% 到 −12%，离 25% 还有空间，真要用的话，反过来**加仓位的风险预算**（比如把现金闲置降到 0）更有用。

### C10 公募报告期 / 季末窗口与「年末效应」（日历类）
- 机制：公募基金季末粉饰，季初重仓股回落。
- 证据：本轮没找到可靠的量化数字，**未知**，需要专门检索。
- 独立性：中。只建议作为 C1/C2 的时点修正，不单独立项。

### C11 注册制新股上市初期 / ST 摘帽
- 不合规：新股多是小盘高波，ST 也基本是小盘，和「不做小盘」冲突。**排除**。只记录在案，不展开。

## Top 5（按「能加真正残差收益」的可信度排序）
1. **C1 指数调样（预测名单、公告前布局、只做高冲击系数）**：被动基金付冲击成本。2023 年后沪深300 公告后 10 日超额 4.64%。先排查 idx_rebal_flow 的失败原因。
2. **C2+C3 合并「盈利信息事件」叶（预告/快报惊喜 + 隔夜跳空口径）**：反应慢的资金付钱。SSRN 4589824 报告每季超额 6.78%。我们已有 forecast/express PIT。
3. **C4+C5 负面事件 overlay（解禁、减持、质押、预减）**叠在 capacity_adv 上：减持方和不看日历的持有人付钱。不新增叶，只削左尾，成本最低。
4. **C6 回购（注销式、比例超过 1%、低 PB）/ 实控人增持**：知情的买方赚、卖给公司的人付钱。完成后 1 年超额约 6.42%。
5. **C7 行业 ETF 轮动（景气 + 拥挤度 / ETF 资金流反转）**：追涨申购资金付钱。国盛超额 16%（样本内），2025 年跟踪 21.4%。要用行业残差验收。

储备：C8 期货贴水 carry，独立性最高，但 60–100万 做不了。
排除：C9 波动率目标（A 股实证负面）、C11（小盘）。

## 现实测算提醒
从 13.8%/12.2% 到 15%，需要净增约 1.2–2.8pp。事件 overlay（C4/C5）可能贡献零点几 pp。真正有可能补到 1pp 以上的是 C1 和 C2 这类离散事件叶，按约 20–30% 的卫星权重叠加。前提是它们相对主干的**超额相关**低（建议预注册上限 ρ_excess < 0.5），而且两档 AUM 都要成立。所有研报数字都是样本内、没扣成本，按经验打对折估计。

## 追加（2026-10-13 15:30 ET，持续深挖例行）：原队列已做完，转第二轮网研
- 原队列 earnings_event → negevent 剔除 → 注销回购 → 行业 ETF 残差轮动 → 指数调仓 均已走完；盘上正交候选穷尽，见 docs/v2/AI_LEAF_CANDIDATES_EXHAUSTED_ZH.md。
- 第二轮网研全文：docs/v2/WEB_RESEARCH_ROUND2_ORTHOGONAL_ZH.md（R1 大宗交易机构承接、R2 分析师全部上调、R3 机构调研密集、R4 ETF 申赎下沉、R5 公募持仓拥挤；R6 股东户数不立项）。
- 新队列顺序：R1 block_trade（预注册 DRAFT：docs/v2/AI_G1G5_BLOCK_TRADE_WHO_PAYS_PREREG_DRAFT_ZH.md，等 Data 满窗回执后冻结）→ R2 report_rc（须报与 earnings_event 的 ρ_excess，>0.5 只算强度过滤）→ R3 stk_surv（Data 队列尚未排入，需补）→ R5 → R4。
- 判定口径不变：叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干（13.82%/−10.07%、12.23%/−11.62%）。

## 追加（2026-10-13 19:28 ET，持续深挖例行）
- 叶7 `block_trade`：FROZEN→X2 完成，自检毛 CAGR **10.12%** / MDD **−17.63%**，残差 α **+0.80%/年**（2024 +4.17%｜2025 −0.20%｜2026 −1.36%），ρ_excess vs capacity_adv **0.07**，压舱均值 **79.6%** → **WATCH**，不送 ACCEPT/Book-Smoke（见 `AI_G1G5_BLOCK_TRADE_WEIGHT_RECEIPT_ZH.md`）。
- 空窗叶8 尝试 `major_contract`（重大合同/中标）：池内事件 190 条但**不同股票仅 30–31 只**、建筑/电力设备扎堆、央企高频重复 → 计数闸失败，**不冻结不跑 X2**（`AI_G1G5_MAJOR_CONTRACT_WHO_PAYS_PREREG_DRAFT_ZH.md`）。
- R2 `report_rc`：Data 仍在拉（~19:28 ET dh 日文件约 525，已到 20190609；满窗仍约数小时）；R3 `stk_surv` 继续 waiting。
- **下一正交叶（盘上可立即开）**：R4 **行业 ETF 申赎流反转**（`data/v2/etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet` 满窗 2014→2026-10，含 available_at）。机制：极端净申购后非信息性买压推高价格，随后均值回归；谁付钱=追涨申购的 ETF 投资者。须与已 FAIL 的 `industry_etf_rotation` 区隔（本叶只做**份额流极值反转**，不用景气/动量合成）。ρ_excess vs capacity_adv 与 vs 已灭行业叶均须 <0.5。
- **备选（盘上）**：解禁后「利空出尽」反弹长腿（`share_float_window_m30_p90` research_grade）——与 negevent/V30「解禁前规避」方向相反（解禁日之后做多、只做大比例解禁）；须写清与 negevent 正交，否则拒。网研旁证：邢不行解禁日后 20 日均值上行；光大减持公告首日负超额后修复节奏。
- 判定口径不变：叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干（13.82%/−10.07%、12.23%/−11.62%）。禁 GP；live/promotion=false。

## 追加（2026-10-13 21:30 ET，持续深挖例行 · 网研第七轮）
- 现状：QuantLab AI 21:15 ET 交付自检统一复权 + 叶1/5/6 复权诊断（结论不变：earnings_event 复权毛 CAGR 16.95%/−19.81%、insider_increase 15.71%/−17.70%、equity_incentive 22.07%/−16.49%，残差 α 与 ρ 方向一致；自检口径不替代 Smoke）。原队列与第2–6轮候选均已走完；AI 当前空闲是在等 Data 的 report_rc 满窗（巡检估 ~23:00–23:30 ET），属正常等待，非卡死。
- 第七轮候选（计数只看条数/只数，未读收益；池 = mid_large 2024-06-28 锚定 float_mktcap_basis 前 300，事件 2023-10→2026-10）：
  1. **减持计划提前终止**（公告标题检索 announcements_classified_pit*）：机制=原减持抛压预期解除，付钱的是按减持冲击定价、提前卖出的资金；文献仅有减持预披露首日 AR −1.42% 的反面旁证（https://www.oajrc.org/FileUpload/PdfFile/e5b40182480941f8bb169c76c1df6008.pdf）。全市场 178 条，**池内 15 条/13 只** → 计数闸失败，不开。
  2. **商誉减值预告/公告**（负事件 overlay 候选）：池内 10 条/7 只 → 计数闸失败，不开。
  3. **分析师逆市重新覆盖**（与 report_rc 同源数据、不同事件）：中信金工 2020《寻找分析师前瞻观点中的Alpha》：近 1 年无覆盖后重新覆盖，120 日相对中证500 超额 4.6%，买入评级 + 前期涨幅低的组更强，组合年化超额 11.8%、IR 1.4（https://m.hibor.com.cn/wap_detail.aspx?id=59d8032fecc420696329babdaf66b38a ）；海外「同一分析师中断≥6个月后重新覆盖」3 个月月均超额 0.55%（https://bigquant.com/wiki/doc/xEQtiaBuS5 ）。机制=长期无人关注的票被重新覆盖预示拐点，付钱的是忽略冷门票的资金。**风险**：中大盘前 300 很少整年无覆盖，计数闸大概率卡；可改用「同一机构中断≥6 个月后重新覆盖」口径。**待 report_rc 满窗后先只数计数**，与 report_rc_allup 一起看与 earnings_event 的同源判定。
  4. 业绩说明会：召开本身无稳定方向，信息在问答语调（上财学报 2016 https://cdxb.shufe.edu.cn/mv_html/j00001/201607/55d59dcd-3adb-405d-8f72-552a844e3acf_WEB.htm ），需全文文本 + NLP，盘上无问答文本 → 不开。
- 结论：本轮无可立即开的新叶；下一叶仍是 report_rc_allup（满窗后冻结 → X2），重新覆盖作为同数据的第二候选排在其后。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干 13.82%/−10.07%、12.23%/−11.62%）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-13 22:25 ET，持续深挖例行 · 网研第八轮）
- 现状：叶7 block_trade、叶9 interim_div_init 均已由 Alpha 正式 **WATCH**（复权毛 13.12%/−17.54% 与 12.91%/−14.94%；70/30、80/20 组合两档均劣于 capacity_adv 复权单跑 17.66%/−13.18%），不派 Book-Smoke。叶1–9 与第2–7 轮盘上可做候选均已关。QuantLab AI 空闲属等 Data `report_rc` 满窗（dh 日文件约 2284、最新约 20240402；当前拉取约 15 文件/分，粗估满窗 **~23:30 ET**），非卡死。
- 本轮外部依据（中金《A股事件影响解析之十问十答》2025-07-31 https://finance.sina.cn/2025-08-05/detail-infiwtcf1202776.d.html ；兴业公告 Alpha 2025-06 http://og.microbell.com/data/8e88375c7001e48a0115024e9033f517.html ；源达股权激励/ESOP https://finance.sina.com.cn/stock/report/2025-04-09/doc-inesqkxs6613240.shtml）：
  1. **增持计划 + 公告前弱势过滤**（中金七问）：与叶5 `insider_increase` 标题/日期键几乎全重合（547 条计划中 546 与 insider_increase 同日同票）→ **同构，不开**。
  2. **员工持股计划单独成叶**：已并入叶6 equity_incentive 规则；池内草案约 48 只，拆开仍同源 → **不开**。
  3. **定增预案 / 不含机构认购**（中金三问、九问）：池内「向特定对象发行.*预案」约 32 只，计数偏薄；标题无法可靠识别「发行对象不含机构」；定增实施偏负 → **计数/可识别性闸失败**。
  4. **股份冻结 / 立案 / 高质押**：池内冻结 6 只、立案 8 只 → 计数闸失败；且与已 FAIL 的 negevent 负向 overlay 同族。
  5. **兴业目标导向公告关键词库**：需新分类器与正文规则，盘上 rules_v2 仅 10 类 event_type，多数落 other → 本轮不立项，记为 Data/文本工程候选项。
- 结论：本轮**无可立即开的新叶**。下一叶仍是 **report_rc_allup**（DRAFT：`AI_G1G5_REPORT_RC_WHO_PAYS_PREREG_DRAFT_ZH.md`）：满窗回执后只数计数→冻结→X2；须报 vs earnings_event 的 ρ_excess/Jaccard，>0.5 只算强度过滤。其后：分析师「中断后重新覆盖」（同 report_rc 数据）、stk_surv、fund_portfolio（均等 Data）。
- 判定口径不变：叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干（纸面 Smoke 口径 13.82%/−10.07%、12.23%/−11.62%）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 00:30 ET，持续深挖例行）
- 叶11 `report_rc_allup`：Alpha 00:25 ET 裁定 **RESEARCH_ACCEPT → WATCH，不派 Book-Smoke**。叶自身复权毛 CAGR 16.65% / MDD −17.50%，残差 α +3.76%（2024 −0.43｜2025 +4.29｜2026 +6.35），ρ_excess vs capacity_adv 0.038，与 earnings_event 事件窗重合仅 6.1%（独立）。但组合门不过：AI conc v2 口径 80/20 60万 15.41%/−14.12%、100万 20.40%/−12.41%，主干 14.96%/−13.63%、18.85%/−12.25%——CAGR 两档更高、MDD 两档更深；本侧简单混合连 CAGR 也略低（17.56% vs 17.66%）。见 `AI_G1G5_REPORT_RC_ALLUP_WEIGHT_ACCEPT_ZH.md`。
- 下一叶（盘上可立即开）：**分析师「中断后重新覆盖」**（同 report_rc 满窗数据，Q3_report_rc 已 done 1,917,334 行）。先只数计数（池 = mid_large 前 300；口径「同一机构中断≥6 个月后重新覆盖」），过计数闸再写 who_pays 预注册→冻结→X2；须报与 report_rc_allup、earnings_event 的 Jaccard / ρ_excess。stk_surv 仍在拉取（`stk_surv_after_report_rc.py` 运行中），fund_portfolio 排其后。
- 判定口径不变；禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 01:25 ET，持续深挖例行 · 网研第九轮）
- 现状：叶12 `analyst_recoverage` 已由 Alpha 00:40 ET 裁定 **RESEARCH_ACCEPT → WATCH，不派 Book-Smoke**（复权毛 13.80%/−15.17%；残差 α +1.64%，2024 +14.05｜2025 −5.79｜2026 −5.70；ρ vs capacity_adv 0.043；组合门两档不过：AI 60万 80/20 12.74%/−15.63% vs 主干 14.96%/−13.63%，100万 19.62%/−12.70% vs 18.85%/−12.25%；弱 OOS）。QuantLab AI 空闲是在等 Data `stk_surv` 满窗（relay 1175 日文件、最新 20221104，约 12 文件/分，粗估满窗 ~02:45 ET），属正常等待，非卡死。
- 本轮只做公告标题计数（池 = mid_large 2024-06-28 锚定前 300，2023-10→2026-10，未读收益）：
  1. **估值提升计划**（证监会《上市公司监管指引第10号——市值管理》2024-11-15 起，长期破净公司须披露，https://www.21jingji.com/article/20241115/herald/ddedb7719c42a9db7df91c668ffa123f.html ）：池内 45 条/34 只，且只有 2025–2026（2024 年 X2 段为 0）；样本集中在银行/地产/建筑的低 PB 票，本质是低估值暴露（教科书价值），外部也无直接事件效应研究（新华网 2025-04 报道 100 家发布，专家认为短期提振有限 http://www.news.cn/finance/20250402/0ca26038927148c38c22d5914dc2ef18/c.html ）→ **计数+机制闸失败，不开**。「市值管理制度」63 条/58 只，属指数成份股的合规性披露、无方向信息 → 不开。
  2. **减持计划实施完毕 / 期限届满**（抛压解除）：实施完毕 32 条/21 只，期限届满 53 条/34 只，合计约 51 只。与 negevent（显式剔除「完毕/届满」标题）方向相反、可区隔，但外部证据偏反面：大股东减持研究发现减持期间存在正超额、**减持完成后正超额立即消失**（http://abslw.com/98/abs1187598.html ），找不到「完毕后反弹」的付钱方 → **who_pays 不成立，不开**；记为备查。
  3. 其余标题计数（仅备查）：董事长/总经理辞职 144 条/85 只（方向不定，且属已 FAIL 的负事件 overlay 族）；回购上限上调 78 条/48 只（与 buyback_cancel/C6 同族）；董监高增持 70 条/28 只（与 insider_increase 同源）；限制性股票授予登记完成 45 条/29 只（equity_incentive 同族）；重大资产重组预案/报告书 62 条/18 只、可转债预案 16 条/10 只、政府补助 29 条/14 只、药品获批 129 条/9 只 → 计数闸或同构闸失败。
- 结论：本轮**无可立即开的新叶**。下一叶仍是 **stk_surv（机构调研密集）**：满窗 + Data 披露滞后回执后→只数计数→who_pays 预注册冻结→X2；其后 fund_portfolio。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干）。禁 GP；禁小盘；live/promotion=false。


## 追加（2026-10-14 02:32 ET，持续深挖例行 · 网研第十轮）
- 现状：叶11 `report_rc_allup`、叶12 `analyst_recoverage` 均已 Alpha **WATCH**（不派 Book-Smoke）。叶6 `equity_incentive` 已 RESEARCH_ACCEPT 并进入 **S6 影子纸面**（50/25/25 capacity_adv/earnings_event/equity_incentive；前向自 2026-11-02；不替换 B4；live/promotion=false）。QuantLab AI 02:10 ET 交付 B4/S6/capacity_adv 扩展脚本 + check 字段后，正确等待 Data `stk_surv` 满窗（relay **~1690** 日文件、最新 **20241218**，近 10 分钟约 1.4 文件/分，工作日剩余粗估 ~470，ETA 仍偏 **~04:00–06:00 ET** 视限速），**非卡死，本轮不派新叶**。
- 本轮外部依据：中金《A股事件影响解析之十问十答》2025-07（https://finance.sina.cn/2025-08-05/detail-infiwtcf1202776.d.html ）机构调研间隔一年再调研 / 财报后 5 日内调研；中银金工公募重仓黑白马（https://t.baogaoting.com/info/710253 ）；ESG 评级变动月度多空约 1.80%（https://ideas.repec.org/a/eee/glofin/v67y2025ics1044028325001073.html ）；绿色债券发行正 CAR（学术综述）。计数口径同前：mid_large 2024-06-28 锚定前 300（去 600519/002371），事件 2023-10→2026-10，只数条数/只数，未读收益。
  1. **分红回报规划 / 未来三年股东回报规划**：池内 **319 条/158 只**（2024–2026 均有）。计数过闸，但多数为大盘股例行合规披露，**信息增量弱**；与已 WATCH 的 `interim_div_init` / 分红族同暴露；中金证据针对「高股息预案日」而非规划文本身 → **who_pays 不清晰，不开**。收窄「提升分红比例承诺」仅 **1 只** → 计数闸失败。
  2. **特别分红 / 特别派息**：27 条/10 只 → 计数闸失败；且与 interim/分红族同构。
  3. **绿色债券 / 碳中和债发行完毕**：窄口径 5 条/4 只，宽口径 23–76 条但有效发行人 ≤24 只且偏银行金融债 → 计数闸失败；正股事件效应文献不足。
  4. **控股股东增持计划实施完毕**：47 条/36 只 → 计数偏薄；与叶5 `insider_increase` 同源 → **同构，不开**。
  5. **转债强赎实施 / 科创板做市商**：18 只 / 16 只 → 计数闸失败（同 Round6）。
  6. **ESG 评级上调/下调事件**：外部有短窗 α，但盘上**无免费 ESG 评级 PIT**（仅有社会责任/ESG 报告标题，291 只属例行披露、无方向）→ 数据闸，不开。
  7. **公募重仓黑白马 / 高频持仓共振**：机制独立（谁付钱=拥挤端与滞后调仓资金），排在 **fund_portfolio** 满窗之后（Q7 remaining 候命），本轮不抢跑。
  8. **机构调研（间隔≥1 年再调研 / 财报后 5 日内）**：仍是下一叶主线，依赖 `stk_surv` 满窗 + 披露滞后回执；与中金六问一致。
- 结论：本轮**无可立即开的新叶**。下一叶仍是 **stk_surv（机构调研密集，优先「间隔一年再调研」与「财报后 5 日」子口径）**→只数计数→who_pays→X2→Alpha→Eng；其后 **fund_portfolio**。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 03:35 ET，持续深挖例行 · 网研第十一轮）
- 现状：自 02:32 ET 无新产物（AI 最新交付仍为 02:10 ET 的 B4/S6/capacity_adv 扩展 check；Alpha/Eng 无新裁定）。QuantLab AI 空闲是在等 Data `stk_surv` 满窗：relay **1914** 日文件、最新 **20251121**，近 10 分钟约 4.3 文件/分，剩余约 220 个交易日，粗估满窗 **~04:20–05:00 ET**（队列日志有「mem<2GB pause」，可能拖慢），**非卡死，本轮不派新叶**。其后 Q7（report_rc 机构名归一 + fund_portfolio）。
- 本轮新机制候选（盘上无数据，未读收益）：
  1. **券商月度金股「新进」事件（R7 broker_gold_new）**：机制=各券商每月 1–3 日公布十大金股，**12 个月内首次/相对上月新进**的票带来卖方新增覆盖观点 + 公募跟随调仓的买压；谁付钱=月初之后才跟随买入的公募/散户（注意力与资金滞后方），以及忽略卖方增量观点的卖出方。外部证据：源达 2025-06《掘金券商金股》2018-01→2025-06 首次推荐组累计 **142.38%** vs 非首次 **57.40%**，1–3 家推荐更稳、大券商更优（https://finance.sina.com.cn/roll/2025-06-13/doc-inezxpez7136338.shtml ）；开源金工全部金股年化 **10.8%**、新进优于重复，「新进+SUE 前 30」优选年化约 **21%**（https://finance.sina.com.cn/roll/2025-02-05/doc-ineimqqc5120663.shtml ），但 2026 年以来优选仅 **−0.2%**（https://www.diaifu.net/post/31244.html ）；反面证据：2026-08/09 「≥3 家共识」组相对独推组无统计分离（http://ludegao.com/research/reports/yanbao_quanshangjinguyizhixingfenxi_20260918/ ）→ **只做「新进 + 1–3 家」口径，不做共识追涨**。
     - 数据：Tushare `broker_recommend`（month=YYYYMM，6000 积分，官方文档 https://tushare.pro/document/2?doc_id=267 ）；盘上 `data/v2/tushare_raw/` **无此表**，Data 队列（Q5 stk_surv → Q7 remaining）也**未排入** → 需 Data 追加拉取 2018-01→2026-10，PIT `available_at` 保守取当月第 4 个交易日 09:00。
     - 同源风险：与叶11 `report_rc_allup`、叶12 `analyst_recoverage` 同为卖方观点；与叶1 earnings_event 若叠 SUE 会同构。立项前须报 vs report_rc_allup / analyst_recoverage / earnings_event 的 Jaccard 与 ρ_excess，>0.5 只算强度过滤；**不叠 SUE**（避免与 earnings_event 同构）。池 = mid_large 前 300，过计数闸（≥80 只、各年均有）才写 who_pays 预注册。
     - 衰减风险：2026 年金股优选近乎零收益，预注册须把 2026 段 OOS 单列，2026 残差 α 为负即 WATCH。
- 结论：本轮**无可立即开的新叶**；下一叶仍是 **stk_surv（间隔一年再调研 / 财报后 5 日内）**，其后 fund_portfolio，再其后 **broker_gold_new（待 Data 拉取）**。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 04:35 ET，持续深挖例行 · 网研第十二轮）
- 现状：自 03:35 ET 无新产物（docs/v2 与 output/ai_factory 最新仍为 02:10–02:13 ET 的 B4/S6/capacity_adv 扩展 check 与 X2H 回执；Alpha/Eng 无新裁定）。QuantLab AI 空闲是在等 Data `stk_surv` 满窗：relay **2009** 日文件、最新 **20260416**，近 10 分钟 12 个文件（约 1.2 文件/分；队列有「mem<2GB pause」），剩余约 110 个交易日，ETA 由上轮 ~04:20–05:00 ET **顺延到约 06:00–06:30 ET**。拉取进程 `stk_surv_after_report_rc.py` 与 `remaining_after_stk_surv.py` 都在运行，**非卡死，本轮不派新叶**。
- 本轮网研（未读收益，只记机制）：
  1. **公募「黑马」边际加仓**（中银金工多因子十一，https://t.baogaoting.com/info/710253 ）：低持仓占比 + 本期公募边际加仓，捕捉机构刚开始关注的票；谁付钱=未跟上机构增量建仓的卖出方。与已排队的 **fund_portfolio** 同数据，**并入 fund_portfolio 预注册当子口径**，不单独开叶；须与「白马抱团」口径分开报、各自过计数闸。
  2. **公募行业仓位 × 20 日动量共振**（东吴金工《共识的力量》，https://wap.hibor.com.cn/data/b31bfa762e65cc5cf58dc40e88cd422a.html ，多头超额年化 7.86%、IR 0.94）：本质是行业轮动，与叶4 industry_etf_rotation（FAIL）、8a ind_etf_flow_rev（同构 FAIL）同族，且主线只做个股/ETF、行业层残差此前为负 → **不开**，仅备查。
  3. 新发基金建仓买压：未找到可核实的 A 股事件研究数字 → 不立项。
- 结论：本轮**无可立即开的新叶**；下一叶顺序不变：**stk_surv（间隔一年再调研 / 财报后 5 日内）** → **fund_portfolio（含黑马边际加仓子口径）** → **broker_gold_new（待 Data 追加拉 broker_recommend）**。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万、100万两档都优于主干）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 05:28 ET，持续深挖例行 · 网研第十三轮）
- 现状：叶13 `stk_surv`（gap1y 主变体）已于 ~05:23 ET 交付 X2+自检并登记台账 → **WATCH**（毛 CAGR 12.05%/MDD −17.47%；残差 α +0.51%/年，2024 −3.09｜2025 +0.08｜2026 +0.41；ρ vs capacity_adv 0.396；组合层 80/20 两档 CAGR 略好、**MDD 两档更深**不过；压舱 77%）。不送 ACCEPT/Book-Smoke。QuantLab AI 交付后空闲。Q7 `remaining_after_stk_surv.py` **进程已不在**（`remaining_queue_status` 仍停在 waiting_stk_surv，未见 orgnorm/fund_portfolio 进度更新）；dmesg 有 17:25 CST（≈05:25 ET）内核异常帧，疑与并行 Gate A/B 重判抢内存有关。MemAvailable≈5.5–6GB。
- 本轮外部依据（未读收益）：
  1. **国盛金工 2026《量价事件驱动信号的绝对收益策略》**（https://www.fxbaogao.com/detail/5673109 ）：低位放量做多 / 高位放量做空，个股 CTA 通道框架，报年化约 17–18%、回撤约 10% 内，与截面选股相关极低；但对成本极敏感（单边千一可砍 ~5pp），年化换手四五十倍。与现有 capacity_adv/事件叶正交潜力高，但高换手+绝对收益通道框架偏离「主线个股/ETF 组合门」、且近教科书量价 → **本轮不开**；记为备查，若要立项须先 Eng 成本闸与 Leo 明示。
  2. **国信金工券商金股业绩增强**（https://finance.sina.com.cn/roll/2025-09-23/doc-infrmtuw9380786.shtml ；月报 https://finance.sina.com.cn/roll/2025-10-09/doc-infthnhn2292055.shtml ）：金股池跟踪偏股混基，可在池内优化；与已排队 **broker_gold_new**（待 Data 拉 `broker_recommend`）同族，**并入该叶预注册**，不新开。
  3. 东吴「公募高频持仓×动量」行业轮动：与叶4/8a 同族 FAIL → 仍不开（第十二轮已记）。
- 结论：本轮**无可立即开的新叶**（下一叶 **fund_portfolio** 缺数据）。顺序不变：**fund_portfolio（含黑马边际加仓子口径）** → **broker_gold_new**。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干；并行记录 Gate A/B 预注册结果，不改现行门）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 06:30 ET，持续深挖例行 · 网研第十四轮）
- 现状：叶13 `stk_surv`、叶14 `insurer_surv` 均已登记 **WATCH**（叶14：毛 CAGR 17.21%/MDD −16.98%；残差 α +3.78%，2024 −3.95｜2025 +15.16｜2026 −2.86；ρ vs capacity_adv −0.342、vs stk_surv 0.072；衰减门 DECAY_DOWNGRADE；现行/A/B 组合门均不过；不送 ACCEPT/Book-Smoke）。AI 06:28 ET 交付 Arch 审计回应（自检净收益+T+1/滚动β）后空闲。Data `fund_portfolio`（Q7a）仍在拉：盘上仅 20180331–20181231 四季，进程 `remaining_after_stk_surv.py` 在跑，**未满窗**；`broker_recommend` 仍未排入。
- 盘上可立即开的下一叶：**tp_rerate**（见 `AI_NEXT_LEAF_CANDIDATES_ZH.md` #1）。机制=10 日内 ≥3 家机构把目标价较各自上一条上调 ≥20%（不看 np），事件后 60 日冷却；谁付钱=按旧估值锚定价、对卖方估值重定反应慢的资金。粗计数：全窗 969 条/271 只｜X2 477/220（2024–2026 各年均有）。外部旁证：财通「星火」十三（2020-05-12）目标价上调短期冲击最强于评级/盈利上调（https://n2nquant.com/wiki/doc/alpha-20200512-vV4XHPDfFX ）；国信超预期全攻略把「盈余后分析师调升目标价」并入超预期簇（https://bigquant.com/wiki/doc/mXJ6ppnrEd ）。**同构风险中高**：与叶11 `report_rc_allup` 同源（卖方）；须读收益前写死 vs report_rc_allup / earnings_event / analyst_recoverage 的 Jaccard/ρ_excess 硬闸（>0.5 只算强度过滤），并加反转过滤（事件前 20 日涨幅过高则剔除追涨）。流程：who_pays 草稿→计数闸→冻结→X2→自检 v2→Alpha；不自跑 Book-Smoke。
- 本轮网研新机制（未读收益，只记队列）：
  1. **公募持仓占比「预期」/高频修正**（华泰/BigQuant 高频系列，https://bigquant.com/wiki/doc/2QK6YNuhs9 ）：用高频数据把季报持仓外推为日频预期持仓，正交后仍有多头效应。盘上无日频持仓推断管线 → **数据闸**；并入 `fund_portfolio` 满窗后的增强子口径（不单开），且须先有可复现的 PIT 外推规则。
  2. **券商金股业绩增强**（国信月报，https://www.diaifu.net/post/31239.html ）：金股池跟踪偏股混基；与已排队 **broker_gold_new** 同族，等 Data 拉 `broker_recommend` 后开，不新开。
  3. 事件驱动+传统因子双层过滤（安信事件多因子架构，https://qiniu-images.datayes.com/uqer/anxin04.pdf ）：属组合方法而非新收益源 → 不单立叶，记为 Eng/Strategy 叠层备查。
- 结论：本轮派 **tp_rerate**（盘上可立即开）；其后顺序不变：**fund_portfolio（含 dark_horse_add）** → **broker_gold_new**。判定口径：叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干；并行报 Gate A/B 与 GATE_V3（MDD≤25% 最大化 CAGR，另报 ≤15%）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 07:26 ET，持续深挖例行 · 网研第十五轮）
- 现状：叶15 `tp_rerate` 已登记 **WATCH/FAIL**（毛/净 CAGR 11.98%/11.14%，MDD −16.95%；残差 α +0.04%；衰减门 DECAY_DOWNGRADE；GATE_V3 两档不过）。Alpha 07:22 ET 新口径重判叶11–15 **全部 FAIL、无翻转**。QuantLab AI 空闲属等 Data `fund_portfolio`：盘上已有 **6/35** 季（至 20190630），`remaining_after_stk_surv.py` 在跑，ETA 仍偏 **数小时**，**非卡死**。
- **解阻**：`broker_recommend` 盘上已满窗 **201801→202610（106 月、缺 0）**，`broker_gold_new` 预注册仍标 PENDING_DATA → **本轮派 AI 只做计数附录（不改冻结条款、不读收益）**；满计数闸后再 X2。`fund_portfolio` 继续拉，满窗后再补该叶计数。
- 本轮网研新机制（未读收益，只记队列）：
  1. **分析师净利润预期修正动量**（CJL 口径；[taolike 2019–2026](https://taolike.net/reports/analyst-revision)）：近 90 日预期净利润均值 / 前 90–270 日 −1，月度十分位，上调组年化超额约 **14%**、多空约 **21pp**、规模中性后更强。数据=盘上 `report_rc`。**同构风险高**：与叶11 `report_rc_allup`、叶15 `tp_rerate`、叶1 earnings_event 同源卖方；且偏截面教科书修正因子 → **不单开主叶**；若立项须先报 vs report_rc_allup/tp_rerate 的 ρ_excess/Jaccard，>0.5 只算强度过滤，并过「禁教科书主线」红线复核。
  2. **破折价定增**（国盛「专业投资者行为」[BigQuant 转载](https://bigquant.com/square/paper/c780e783-e712-4e71-9379-4a5c62c6410f)）：定向增发破发/折价认购事件。盘上需定增发行价与市价 PIT；**数据闸**待 Data 确认表源后再计数，不抢跑。
  3. **「市值管理」目的回购**（CGS-NDI 2026-09，[新浪](https://finance.sina.com.cn/stock/stockzmt/2026-09-10/doc-inirhvxa5373601.shtml)）：维护价值/市值管理类回购公告提振强于激励/补偿类。与已 WATCH 的 `buyback_cancel` 同族 → **并入回购族增强子口径备查**，不新开；若重开须换「目的字段」过滤并过同构闸。
  4. **国盛个股异动雷达/量价事件簇绝对收益**（[fxbaogao](https://fxbaogao.com/detail/5667195)、[sembr](https://sembr.live/digests/quant-ideas-20260920/)）：高换手通道框架 + 近教科书量价 → **维持不开**（第十三轮已记；须 Eng 成本闸 + Leo 明示）。
- 结论：本轮派 **broker_gold_new 计数**（数据已齐）；`fund_portfolio` 继续等满窗；其后顺序不变。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干；并行 Gate A/B 与 GATE_V3 MDD≤25% 最大 CAGR，另报 ≤15%）。禁 GP；禁小盘；live/promotion=false。

## 追加（2026-10-14 08:28 ET，持续深挖例行 · 网研第十六轮）
- 现状：叶16 `broker_gold_new`、叶17 `major_contract_growth` 均已 **WATCH/DONE_FAIL**（不派 Book-Smoke）。原 `tech_qual_cert` 草稿按主 Agent HARD PIVOT（禁卖方/合同）已 **ABORTED**。叶18 改选 **`overnight_idio_ivol`**（低特质隔夜波动慢α + 1–3 日隔夜左尾快门；`AI_G1G5_OVERNIGHT_IDIO_IVOL_WHO_PAYS_PREREG_ZH.md` 已 FROZEN）。覆盖闸 **PASS**（`overnight_idio_ivol_coverage_20261014.json`）：HI_LIQ 密封 median_valid=1754、≥200 日占比 98.5%；HI_LIQ X2 median=3075、96.7%；FULLA X2 median=4954、≥500 日占比 96.7%。覆盖脚本已结束，**AI 空闲 → 本轮派 α 向量 + 自检/X2**（不自跑 Book-Smoke）。`fund_portfolio_dh` 续拉至约 **10/35** 季（→20200630），满窗后再计数；live/promotion=false。
- 本轮网研（未读收益，只记机制；对齐 Leo 08:23 转向：质量/应计残差、隔夜-日内/特质波、脱敏 SUE）：
  1. **隔夜特质波动「昼伏夜出」旁证**（北大/人大复印资料 https://nsd.pku.edu.cn/docs/20250910141126209248.pdf ）：IVOL 负相关主要在隔夜、日内为正；与本叶「α=−隔夜特质波动」同向。东北证券 2025「显著上行特质波动」重构多头超额约 7.63%（https://www.baogaobox.com/insights/250908000020103.html ）→ **叶18 跑完后再议子口径**（上行跳跃 IVOL / 大单日子集），不并行开第二波叶。
  2. **高应计剔除 overlay（非重开 accrual_quality）**（taolike 现金 vs 应计 https://taolike.net/reports/cash-profitability ；应计异象 https://taolike.net/reports/accruals ）：稳健信号是「去掉高应计」而非现金利润率水平；`accrual_quality` 已 Book-Smoke WATCH/DONE_FAIL → **只作主干负向过滤器候选**，须与旧叶 Jaccard/ρ 硬闸，过闸才写 who_pays；不单开主叶。
  3. **换手率分布均匀度 UTD**（东吴 2014–2025-10 多空年化约 20%、IR≈2.71 https://www.sgpjbg.com.cn/baogao/960604.html ）：需分钟成交量 → 盘上分钟历史不足（见 INTRADAY_DATA_FEASIBILITY）→ **数据闸，不开**。
  4. **逐笔流动性冲击羊群**（国盛 2026 https://finance.sina.com.cn/stock/stockzmt/2025-11-14/doc-infximrk3274904.shtml ）：需逐笔委托/成交 → **数据闸，不开**。
  5. **脱敏 SUE**：仍缺分析师一致预期 PIT；与 earnings_event 同族 → **维持不开**（扫描已否）。
- 结论：本轮派 QuantLab AI 继续叶18 **overnight_idio_ivol**：覆盖 PASS → 建 α/gate/eval_weights（HI_LIQ 主 + FULLA 对照）→ leaf_selfcheck_v2 → 台账；过 Gate A/B + GATE_V3 + 衰减 KEEP 才交 Alpha；不自跑 Book-Smoke。其后队列：**fund_portfolio（含黑马边际加仓）** → **高应计剔除 overlay（计数后）** → 叶18 子口径（上行 IVOL）视主叶结果。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干；并行 Gate A/B 与 GATE_V3 MDD≤25% 最大 CAGR，另报 ≤15%）。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 追加（2026-10-14 09:31 ET，持续深挖例行 · 网研第十七轮）
- 现状：叶18 `overnight_idio_ivol` 已台账 **WATCH**（HI_LIQ 净 CAGR 4.85% α −5.26%；不可交易/衰减 DOWNGRADE/Gate A/B 不过/GATE_V3 FAIL；不交 Alpha）。QuantLab AI **非空闲**：盘上并行 (1) 叶18 变体 `overnight_idio_ivol_lowto`（20 日再平衡+缓冲，HILIQ/x2 建 α 中）；(2) 叶19 `cfacc_rnoa`（FROZEN 预注册后刚起跑）；(3) 叶20 `sue_resid` 曾写完 HILIQ alpha/gate 后 **SIGKILL/OOM**，串行循环将在 19 后重试。MemAvailable≈2.3GB（巡检已令 AI/Alpha 勿再开新全窗）；本轮**不派新叶**。原 WEB 队列（earnings→negevent→回购→行业ETF→调仓）已穷尽；现行队列对齐 Leo 08:23 转向：质量/应计残差、隔夜-日内/特质波、脱敏 SUE。
- 本轮网研新机制（未读收益，只记队列；live=false）：
  1. **现金流实现率 CRR + 残差波动惩罚**（天风「现金流实现率因子」；播客摘要 https://castro.fm/episode/Nx2X0r ；慧博 https://www.hibor.com.cn/repinfodetail_5045180.html ）：过去 16 季营业利润→经营现金流转化效率，再以 CFOOE 对全市场回归残差波动率过滤不稳定回收。报改进版 RankIC≈2.82%/ICIR≈2.08，沪深300 RankIC≈3.85%。与叶19 `cfacc_rnoa`（同期 CFACC+ΔRNOA）**同族但口径不同**（时序转化 vs 同期应计）→ **并入叶19 后增强子口径 / 下一叶候选**，须 vs 叶19 Jaccard/ρ 硬闸；银行/地产/综金失效须行业掩码。
  2. **高应计剔除 overlay**（taolike 现金 vs 应计 https://taolike.net/reports/cash-profitability ）：稳健信号是「去掉高应计」而非现金利润率水平；与第十六轮备查一致 → **主干负向过滤器**，计数后过 Jaccard/ρ 才写 who_pays，不单开主叶。
  3. **隔夜-日内细分因子簇**（中信建投 2025-11「逐鹿」Alpha https://finance.sina.com.cn/wm/2025-11-26/doc-infystcp1980904.shtml ）：32 个隔夜/日内动量·波动·量价背离细分 + d-LE-SC 领先滞后；旁证「昼伏夜出」IVOL。与叶18/18v 同微观结构族 → **叶18v 出结果后再议子口径**（上行跳跃 IVOL / 隔夜动量切割），不并行开第二波；d-LE-SC 网络策略偏组合方法、记 Eng/Strategy 备查。
  4. **东吴「日与夜殊途同归」量价动量**（月报至 2025-10，多空年化约 18% 量级）：偏教科书动量切割 → **禁教科书主线复核后默认不开**，仅作叶18 族旁证。
- 结论：本轮**不派叶**（AI 忙 + 内存紧）。下一交付顺序：叶18v → 叶19 → 叶20（OOM 后串行重试，等 MemAvailable≥4GB）→ 过 Gate A/B+GATE_V3+衰减 KEEP 才交 Alpha；其后队列 **CRR 增强（vs 叶19）** / **高应计剔除 overlay** / **fund_portfolio（Data 满窗后）**。判定口径不变。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 第十八轮网研（2026-10-18 00:25 ET，主 Agent 持续深挖例程）
- 背景：叶18v/19/20 于 10-18 00:00–00:16 ET 全部 WATCH（HI_LIQ 衰减 v1.1 DOWNGRADE、GATE_V3 FAIL）；AI 已开叶21 biz_climate（00:18:58 FROZEN），本轮**不派新叶**，候选仅入队。
  1. **ETF 申赎→成分股被动资金压力**（招商金工「综合资金流视角的选股策略」https://wap.hibor.com.cn/repinfodetail_4589122.html ：18 个资金流指标含公募/ETF/两融/境外/高频订单，与风格相关 <0.2，仅对残差波动率负暴露）。who_pays=被动申赎被迫按权重交易的 ETF 份额持有人；与已 WATCH 的 moneyflow_resid 不同源（用 ETF 份额变化×成分权重，非逐笔大单）。须先确认 Data 有 ETF 份额日度+成分权重 PIT；对 capacity_adv、叶18v ρ/Jaccard 硬闸；HI_LIQ 主。**排在叶21 之后**。
  2. **机构持仓拥挤度（持仓市值/流通市值）负向过滤**（海通「因子拥挤度的扩展」解读 http://mp.weixin.qq.com/s/UazyfI5mCi6XVhrsWFVobw ：正交后市值比与未来收益相关 −0.41，优于金额比；但中证800 内敏感度高）。只作 capacity_adv/Core 的**负向过滤 overlay**，不单开主叶；依赖 Data fund_portfolio 满窗（季报滞后按公告日 PIT）。并入既有「fund_portfolio（Data 满窗后）」队列项。
  3. 旁证（不开）：国信金工 10-11 周报 HS300/ZZ500 内低波/低换手占优、动量反转弱（https://finance.sina.com.cn/roll/2026-10-11/doc-iniuvtkp8925022.shtml ）；中金 2026「集中度平台期」框架可作 regime 披露，非因子。均属教科书风格，禁作主线。
- 队列更新：叶21 biz_climate（在跑）→ CRR 增强（vs 叶19）→ ETF 申赎压力（待 Data 核数）→ 高应计剔除 overlay / 拥挤度过滤 overlay（fund_portfolio 满窗后）。判定口径不变。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 第十九轮网研（2026-10-18 01:33 ET，主 Agent 持续深挖例程）
- 候选 A：**IMAX（三因子残差下的最大日收益）作为剔除过滤器**。Hu/Jiang/Zhu, Applied Economics 2025-11-20（https://www.tandfonline.com/doi/abs/10.1080/00036846.2025.2584716）：用中国三因子估计时，IVOL 与 IMAX 都显著负向预测收益。who_pays：赌博偏好散户为彩票型股票支付溢价。用法建议：capacity_adv/HI_LIQ 池内剔除 IMAX 顶部分位（只作剔除，不作主线因子，避免教科书因子当主线）。
- 候选 B：**彩票型异象主要在隔夜分量**。Gu/Hu/Xiong, Accounting & Finance 2025（https://ideas.repec.org/a/bla/acctfi/v65y2025i1p883-911.html）：负的隔夜收益集中在彩票型股票，且在高赌博偏好、高套利限制股票中更强 → 可做「隔夜异常 × IMAX」交互剔除。
- 反证：Cheema/Chiah/Man, PBFJ 2022（https://ideas.repec.org/a/eee/pacfin/v74y2022ics0927538x22001044.html）：美股「拔河」强度在 A 股无预测力（隔夜正、日内反转互相抵消）→ **不要照搬 Akbas 拔河因子**，只用分量做剔除/交互。
- 排队：与第三方评审要求的「隔夜-日内/特质波动」方向一致；须先对 capacity_adv 与叶18 lowto 正交（预期与低换手/低波高度相关），HI_LIQ、X2 样本内、30bp。未开叶、未看收益。

## 第二十轮网研（2026-10-18 02:33 ET，主 Agent 持续深挖例程）
- 背景：AI 非空闲——叶23 r2.3（f011b277）/叶24 r2（6f57c82d）已按 Arch 129d67c5 第二轮修复（未跑），等 Arch 复审 .ok + Data cs_panel 重建（D3D4 计数断言 P2-1）；本轮**不派新叶**，候选仅入队，未看收益。
- 候选 A：**交易所财务类问询函（剔除重组类）收函事件 → capacity_adv/Core 负向剔除**。证据：陈运森等 2018《金融研究》（https://file-lianxh.oss-cn-shenzhen.aliyuncs.com/Lectures/2021-3-Text/%E9%99%88%E8%BF%90%E6%A3%AE-2018-%E9%87%91%E8%9E%8D%E7%A0%94%E7%A9%B6.pdf ）收函 CAR 显著为负、回函为正；深交所研究（http://docs.static.szse.cn/www/aboutus/research/secuities/daily/W020180727381262164950.pdf ）年报问询负反应有延迟、收入问题集中度越高越负；于孝建等（https://www.zhangqiaokeyan.com/academic-journal-cn_financial-regulation-research_thesis/0201286809774.html ）定期报告类问询负、重组类为正。who_pays：对监管揭示的未披露风险反应迟缓的持有人。
- 候选 B：**复合排雷信号（≥3 个：问询/关注函/延期回函/非标审计/业绩预告下修/存贷双高/应收-营收偏离）→ 剔除**。天风 2019《量化排雷指南》（http://pdf.dfcfw.com/pdf/H3_AP201906261336467942_1.pdf ）：财务问询后半年/一年跑输二级行业 5.25%/9.02%，复合预警组合 2017 起年化跑输中证全指 23.33%。
- 风险/闸：与已 FAIL 的 negevent overlay 同族（第十轮商誉/立案在 HI_LIQ 计数闸失败）→ 立项前须 (1) Data 确认公告标题表能 PIT 区分「问询函/回函/重组类」；(2) HI_LIQ 池内计数闸（年均事件只数）；(3) 对 negevent 剔除集 Jaccard 硬闸 >0.5 即拒；(4) 只作剔除 overlay，不作主线因子；判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干）。
- 队列更新：叶23 → 叶24（串行，等 .ok）→ CRR 增强（vs 叶19）→ ETF 申赎压力（待 Data 核数）→ IMAX/隔夜彩票剔除（第十九轮）→ 问询函/复合排雷剔除（本轮，先计数）→ 高应计/拥挤度 overlay（fund_portfolio 满窗后）。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 第二十一轮网研（2026-10-18 10:30 ET，主 Agent 持续深挖例程）
- 背景：AI **非空闲**——叶25 应计预注册 DRAFT r2（10:22，按 Arch AUDIT_20261018_1018 修订，已补 vs 叶19 硬闸、家族 n=4）待 Arch 再审→主 Agent 裁冻结；叶24 CMC v1.2 memtest PASS 但 Alpha 维持 WATCH（dCAGR +3.28/+3.15pp，B1 跑输池内等权≈7.9pp）。本轮**不派新叶**，候选仅入队，未看收益。
- 候选 A：**供应链（客户）动量溢出**。招商定量「蓝海启航」之五（2022-05，https://www.hibor.com.cn/repinfodetail_1617408.html ；全文摘录 http://yanbao.us/wechatreport/228111.html ）：按供应链关联度加权客户过去 80 日动量，双层客户动量季度调仓，2018 起沪深300/中证800/中证1000 池超额 9.65%/10.54%/5.97%（夏普 0.38/0.40/0.12），与传统动量相关约 20%、与其他大类因子 <5%。兴业「产业链视角下的 Alpha 传导」（https://www.sdyanbao.com/detail/374239 ）：产业链传导动量 ICIR 0.46，复合 Top 组合年化超额 3.4%。who_pays：有限关注、未及时把客户端冲击传导到供应商定价的持有人（Cohen-Frazzini 2008）。
  - **数据闸**：个股级关联度依赖秩鼎等商业数据，盘上无 → 个股版不开。可行降级：**行业级客户动量**（投入产出表下游行业加权的 SW 行业滞后收益，Shahrur 等 2010 口径）→ 与已排队「行业 ETF 残差轮动」同族，须先对叶4/8a 行业轮动 FAIL 记录与 capacity_adv 做 ρ/Jaccard 硬闸，投入产出表须按发布日 PIT。
- 候选 B（旁证，不新开）：**研发费用 TTM/市值**（源达信息 2026-01，http://m.hibor.org/data/35c53a820ebc2f1645e4f4d6e7cbf50c.html ：IC 0.04、中性化 ICIR 0.39、多空年化 9.71%、MDD 7.5%）。与叶22 `rd_innov`（WATCH，RD/平均总资产口径）同族，且 RD/市值偏价值暴露 → 只作叶22 子口径备查，家族 n 须 +1；学界对创新溢价是错误定价（王志强等）还是风险补偿（尹力博、辛宇 2025《金融研究》http://www.jryj.org.cn/CN/Y2025/V541/I7/168 ）有分歧，后者意味着回撤风险高。
- 队列更新：叶25 应计（预注册审中）→ CRR 增强（vs 叶19/25 同族，n 计入）→ ETF 申赎压力（待 Data 核数）→ IMAX/隔夜彩票剔除 → 问询函/复合排雷剔除（先计数）→ 行业级客户动量（新，先 IO 表 PIT 可得性）→ 高应计/拥挤度 overlay（fund_portfolio 满窗后）。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干）。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 第二十二轮网研（2026-10-27 20:26 ET，主 Agent 持续深挖例程）
- 背景：叶37 `imax_lottery_exclusion_overlay` X2 selfcheck **HOLD CLOSED**（ρ≈0.9589≫0.5；Gate 全 false；KEEP≠ACCEPT；≠X2 ACCEPT）。叶34–36 exclusion overlay 亦均 HOLD CLOSED。AI **空闲**；原 WEB 首队列与 exclusion 短队列已走完 → 本轮**派下一叶**并追加机制候选（未读收益）。
- 候选 A（优先解锁）：**fund_portfolio 公募季报持仓边际 / dark_horse_add**。预注册已 FROZEN（`AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md`）；盘上 `fund_portfolio_dh` 现 **34** 季（20180331→20260630）。本拍只做 **PIT 计数附录**（不改冻结条款、不读收益）；过计数闸后再排 X2。who_pays=季报滞后跟随/忽视冷门票的资金。
- 候选 B（叶38）：**非标审计意见剔除 overlay**。盘上 `data/v2/audit/audit_opinion_pit_tushare.parquet`（`is_non_standard`；约 2621 非标行 / 895 只；`available_at` PIT）。旁证：天风《量化排雷指南》非标后半年/一年相对二级行业约 −7.06%/−8.83%（http://pdf.dfcfw.com/pdf/H3_AP201906261336467942_1.pdf ）；国盛基础排雷把非标当硬闸（https://finance.sina.com.cn/stock/stockzmt/2020-09-15/doc-iivhvpwy6808339.shtml ）。只作 capacity_adv/HI_LIQ 负向剔除；须 vs negevent/叶36 Jaccard>0.5 拒；覆盖闸参考叶36（median=6 FAIL）写死合理厚度，勿盲抄。
- 候选 C（数据闸，不开）：**行业级客户动量**（招商供应链动量 https://www.hibor.com.cn/repinfodetail_1617408.html / http://yanbao.us/wechatreport/228111.html ）。个股版需秩鼎；盘上无投入产出表 PIT；`sw_l1_pit` 仅成员映射且 NOT_PROMOTION_GRADE → 待 Data。
- 旁证不开：公开价量+ML 严格 OOS 近零（https://github.com/wangpage/quant-ashare ）；残差动量属教科书切割 → 禁作主线。
- 队列更新：fund_portfolio 计数附录（优先）→ 叶38 非标审计剔除（计数后）→ 行业级客户动量（IO PIT 后）→ 拥挤度过滤（fund_portfolio 满计数后子口径）。判定口径不变。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。

## 第二十三轮网研（2026-10-27 22:34 ET，主 Agent 持续深挖例程）
- 现状：叶38 `audit_nonstd_exclusion_overlay` B1_PUSHDOWN X2 **DONE**（RECEIPT `5e68af78`；rc=0；peak≈967.7≤1500；thickness median=48 PASS；hard_jaccard=false；mask-only PRIMARY；≠X2 ACCEPT；等 Arch CONSUME→Alpha）。fund_portfolio who_pays **FROZEN→Book-Smoke `.ok` `f08ce32c` SIGNED**（主 MATCH→Eng GO；窗 expires 00:05 ET）。AI **交接中非卡死** → **本轮不派新叶**。原 WEB 首队列与 exclusion 短队列已穷尽；现行队列对齐 Leo 质量/应计/微观结构转向。
- 候选备查（未读收益；不开本拍）：
  1. **CRR_MOD2 现金流实现率+残差波动惩罚**（天风 https://www.hibor.cn/repinfodetail_5045180.html ；播客 https://castro.fm/episode/Nx2X0r ）：RankIC≈2.82%/ICIR≈2.08；沪深300 RankIC≈3.85%。与叶19/25/30 CRR 同族 → **仅作叶30 后增强子口径**，须 vs 叶30 Jaccard/ρ 硬闸；银行/地产/综金行业掩码。
  2. **机构–散户筹码成本差**（申万宏源 2026-03《投资者分层视角下的信息增量》摘要 https://www.baogaobox.com/insights/260319000026364.html ）：成本差 RankIC≈1.58%、合成 IC≈4.35%；**中小盘更强、沪深300 IC 为负** → 与 moneyflow/叶32 同族风险 + 小盘偏置 → **备查不开主叶**（若立项须 HI_LIQ 残差+ρ 硬闸）。
  3. **解禁冲击比率残差剔除 overlay**（解禁市值/近30日 ADV；正交市值·流动性后作负向闸）：旁证解禁前月均溢价约 −0.70%（https://www.sohu.com/a/243236400_683085 ）。与叶33 `share_unlock` 同族 → **并入解禁族增强**，不新开；须确认 Data 解禁 PIT 与叶33 ABORT/补丁状态后再计数。
- 旁证不开：港股解禁评分卡（华泰 2026-06）非 A 股主线；公开价量+ML 严格 OOS 近零仍禁教科书主线。
- 队列更新：Eng fund Book-Smoke（本拍 GO）→ 叶38 Arch CONSUME→Alpha → 行业级客户动量（IO PIT 后）→ 拥挤度过滤（fund 满闸后）→ CRR_MOD2 增强（vs 叶30）。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干）。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。


## 第二十四轮网研（2026-10-27 23:30 ET，主 Agent 持续深挖例程）
- 现状：fund who_pays 首跑 BS **HOLD**（MDD>25%）；**MDD-cut V_BALLAST_MIX** `.ok` **`335635dd` SIGNED** → 等主 MATCH→Eng GO（3 臂）。叶38 B1_PUSHDOWN **CONSUMED_PASS `c01c2034`**（≠X2 ACCEPT；等 Alpha 审闸）。AI **空闲**（FROZEN 已交）→ **本轮派下一叶**。原 WEB 首队列与 exclusion 短队列已穷尽。
- 候选 A（优先解锁）：**异常经营现金流 ABCFO / 真实盈余管理残差**（东北证券《基于异常现金流模型的真实盈余管理因子》https://bigquant.com/wiki/doc/fbp6xs9sH3 ：中证800 季度 ABCFO_Q1 多空年化约 14.63%、夏普 1.67）。who_pays=对真实活动盈余管理（异常低 OCF）反应慢的持有人。盘上可用 `data/v2/financials_pit` + `cashflow_pit_tushare`。**同构闸**：须 vs 叶19 `cfacc_rnoa` / 叶25 应计 / 叶30 CRR Jaccard/ρ_excess >0.5 拒；银行地产综金行业掩码；HI_LIQ 主；只作质量残差，禁教科书水平应计当主线（水平应计已有叶34 exclusion HOLD）。
- 候选 B（备查增强）：**CRR_MOD2**（天风现金流实现率+残差波动惩罚 https://www.hibor.com.cn/repinfodetail_5045180.html ；RankIC≈2.82%/ICIR≈2.08；沪深300 RankIC≈3.85%）。与叶30 同族 → **仅作叶30 后增强子口径**，硬闸同 A。
- 候选 C（旁证，不新开主叶）：taolike 应计异象 2015–2026 Q1−Q5≈+4.6pp（https://taolike.net/reports/accruals ）→ 已覆盖为叶34 高应计剔除 HOLD CLOSED；只作排雷旁证。2025–26 公开复盘偏小盘/成长（果仁/汇安）→ **禁把小盘风格当主线超额证明**；纸面仍 HI_LIQ 约束。
- 数据闸维持：行业级客户动量（无 IO PIT）；拥挤度过滤等 fund MDD-cut BS 交卷后再开。
- 队列更新：Eng fund MDD-cut Book-Smoke（本拍 MATCH→GO）→ Alpha 审叶38 `c01c2034` → **叶39 ABCFO who_pays+覆盖闸**（优先）→ CRR_MOD2 增强（备选）→ 拥挤度过滤（fund 后）→ 行业客户动量（IO 后）。判定口径不变（叶自身主干级，或 ρ_excess vs capacity_adv <0.5 且叠加后 60万/100万两档都优于主干）。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。


## 追加（2026-10-28 00:25 ET，持续深挖例行 · 叶39 LAND→X2）
- 现状：叶39 ABCFO LAND_SCRIPT Arch **PASS_WC `edc32c9f`**（脚本 `e99376dd` / RECEIPT `04f6c7bb` / FROZEN `150d1a28` / ArchFROZEN `b51a59a0`）。AI **非空闲**（等独立 X2 签窗）→ **本轮不派新叶**；主裁 **GO 签窗**（钉 `e99376dd`；须 peak_proof + 正式 ρ_excess + 叶34 Jaccard）。fund MDD / 叶38 HOLD CLOSED 旁线不混。dig `bc8a9652`。
- 本轮网研（未读收益，只记队列）：
  1. **CRR_MOD2**（天风 https://www.hibor.com.cn/repinfodetail_5045180.html）：维持叶30/39 后增强备选；硬闸 Jaccard/ρ；银地综金掩码。
  2. **REM 合成**（旁证东北/国君）：叶39 闭合后再议；不并行。
  3. **隔夜/日内**（中信建投逐鹿 2025-11）：叶18 族旁证；不重开。
- 队列更新：叶39 X2 签窗（本拍）→ 真跑/CONSUME/Alpha → CRR_MOD2 增强 → 拥挤度过滤 → 行业客户动量（IO 后）。判定口径不变。禁 GP；禁高杠杆；小盘可买（仅剔不可交易）；live/promotion=false。
