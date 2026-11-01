# Alpha 机制方向库（草案）

**用途：** QuantMind/RD 闭环的 `--direction` 输入；每条必须写清 **钱从谁来**。  
**禁：** 反转/动量/低波/EP/BP/换手裸因子当主方向。  
**宇宙：** 中大盘（csi300/中证500/流通市值 Top1500）；禁小盘主线。  
**本金：** 评测只报 60 万 / 100 万。  
**promotion_approved=false**

## 已写满（≥5）

### D01 连板晋级退潮
- **mechanism_tag：** `consecutive_board`
- **假设：** 晋级率下行时，高位连板拥挤端次 1–5 日相对中大盘偏弱。
- **钱从谁来：** 晋级失败的追板资金与 T+1 被迫隔夜买家；对手方是等待承接的观望盘/做市。
- **结构叶：** `lu_height`, `lu_promote_rate`, `mkt_max_height`
- **失效：** 政策一日游行情下「败晋级仍大涨」；或去掉涨停叶后仍假显著（标签泄漏）。

### D02 情绪退潮（最大高度回落）
- **mechanism_tag：** `limit_up`
- **假设：** 市场最大连板高度从极值回落，短窗指数/中大盘拥挤β超额为负。
- **钱从谁来：** 杠杆短线去杠杆砸给指数成分被动承接。
- **结构叶：** `mkt_max_height`, `lu_promote_rate`, `mkt_lu_breadth`
- **失效：** 高度回落但同时巨量宽基 ETF 净申购对冲。

### D03 题材宽度见顶
- **mechanism_tag：** `theme`
- **假设：** 涨停扩散（宽度）见顶后，主题拥挤股相对冷门中大盘走弱。
- **钱从谁来：** 一日游题材资金与主题 ETF 申购盘；退潮时同一批人卖出。
- **结构叶：** `mkt_lu_breadth`, `theme_lu_density`（待行业/题材映射补全）
- **失效：** 宽度数据仅标题代理且与收益同步造成前视；主题映射缺口。

### D04 T+1 隔夜/日内拆分拥挤
- **mechanism_tag：** `t1`
- **假设：** 涨停次日隔夜收益透支后，日内均值回归由早盘卖方支付。
- **钱从谁来：** 集合竞价抢筹者 vs 开盘后兑现的隔夜仓。
- **结构叶：** `overnight_ret`, `intraday_ret`, `on_minus_id`, `days_since_lu`
- **失效：** 涨停制度或 ST/*ST 规则突变。

### D05 ETF 份额冲击叠加涨停状态
- **mechanism_tag：** `etf_flow`
- **假设：** 宽基/主题 ETF 净赎回日，涨停稀缺股更抗跌或反之（预先注册方向，探索检验）。
- **钱从谁来：** 申赎套利桌与造市商把份额差打到成分股；散户申赎是源头。
- **结构叶：** `etf_major_flow`, `etf_theme_flow`, `etf_flow_x_lu`
- **失效：** available_at 口径误用（份额+净值须按 T+1 日终）。

## 占位（凑满方向库骨架，待补钱从谁来细节）

| ID | 标题 | tag | 状态 |
|---|---|---|---|
| D06 | 解禁供给窗口回避 | lockup | stub |
| D07 | 期指贴水条件多空 | basis | stub |
| D08 | 可转债下修/强赎事件 | cb_event | stub |
| D09 | 公告嵌入×涨停交互 | ann_embed | stub（探索窗 2024-06+ 正文缺口） |
| D10 | 情绪词典/FinBERT 标题 | sentiment | stub |
| D11 | 2→3 板晋级专项 | consecutive_board | stub |
| D12 | 跌停潮密度 β 调节 | limit_up | stub |
| D13 | 题材龙一拥挤度 | theme | stub |
| D14 | 北向+涨停确认（对照） | sentiment | stub |
| D15 | 锁仓筹码×低位（禁小盘表述） | lockup | stub |
| D16–D20 | 预留 | — | stub |

WorkBuddy 技能链接：`docs/v2/workbuddy_skills/`（研究分析师 / 财报采集 / 风险审查 / 策略复盘）。
