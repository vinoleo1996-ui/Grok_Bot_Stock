# 中美股信息面专家 v2 · AlphaLens

实时行情 + 多智能体信息面研判 + 多指标技术分析 + 可执行交易计划。

- 后端:FastAPI + 常驻快照中枢(hub),端口 **8722**
- 前端:React 18 + Vite + ECharts,构建产物由后端托管
- 数据:NeoData MCP(主)→ 东财 → 腾讯 → Tushare(RDS/Promax)四级降级

---

## 1. 为什么现在不慢了(架构说明)

**旧问题**:每次开页面都现拉数据;NeoData 一批 10 只、20 次串行请求 → `/api/recommendations` 43 秒,
首屏白屏、切页重算、智能体要等几分钟。

**现在的做法**(`app/dataflows/hub.py`):

| 层 | 做法 | 效果 |
|---|---|---|
| 并发 | MCP 批量调用 8 并发 + 连接池 32 | 69 只 K 线 3.4s(原 7s+),行情 10 只 0.28s |
| 快照 | 后台常驻刷新,结果放内存 | 读接口全部 10–30ms |
| 推送 | `/api/live` SSE 行情流(1s),替换前端 15s 轮询 | 端到端 15–21s → **3–4s** |
| 分层预热 | 先重点池(4 板块)→ 量化可算 → 再全市场补全 | 首屏 3–5s 内可用 |
| 计算解耦 | 量化只用内存行情+K线重算,零网络 | 重算 0.05–0.2s,45s 一轮 |
| 分频轮询 | 热集(指数/ETF/TOP)6s,全量 90s,日线 180s | 真"实时"且不浪费配额 |
| 不装实时 | 响应带 `updated_at / age_s / stale` | 前端显示"X 秒前",不假直播 |

实测(2026-10-24,全池 327 只):

```
/api/overview        26ms      /api/recommendations  15ms
/api/allocation      23ms      /api/etf-board        21ms
/api/stock           83ms      /api/analyze          14ms(缓存命中)
/api/paper           25ms      智能体全链路            23s
```

刷新节奏:行情 6s/90s、量化 45s、板块资金 60s、日线 180s、ETF 120s、配置 180s。
非交易时段自动降速 4 倍。

**实时推送**:前端 `useLiveQuotes` 订阅 `/api/live`(SSE),后端按 3s 推增量;
Dashboard 与个股抽屉实时更新,轮询降级为 60s 兜底。断线自动指数退避重连。

**CPU 密集任务不占事件循环**:量化打分与回测跑在独立线程池(`run_in_executor`),
实测 1.29s 的回测重算期间 `/api/health` 最慢 14ms(修复前会冻结 1252ms)。

**首屏可用时间约 18–20 秒**(冷启动):先拉重点池 K 线→量化→首屏;全市场补全、
活力指标、宏观、资金流全部后台跑,不阻塞首屏。

---

## 2. 任意标的深度研判

顶部「个股深度研判」页,或直接 `GET /api/analyze?q=...`。

**输入什么都能认**(`app/dataflows/symbols.py`,约 1 万条:5500 A 股 + 3000 ETF + 2800 港股 + 260 美股):

```
600519 / sh600519 / 600519.SH / 1.600519   → 贵州茅台
贵州茅台 / 茅台 / gzmt / GZMT / maotai      → 贵州茅台
中芯 / zxgj / 688981                        → 中芯国际(A/H 都列)
00700 / 腾讯 / tx                            → 腾讯控股
NVDA / 英伟达                                → 英伟达
```

**8 维打分**(`app/quant/analysis.py`,不是单指标):

| 维度 | 权重 | 依据 |
|---|---|---|
| 趋势结构 | 20 | MA5/10/20/60/120 排列、MA20 斜率、ADX/DMI |
| 动量 | 15 | 5/20 日涨幅、MACD(含顶/底背离)、RSI |
| 量能 | 12 | 量比、OBV 20 日变化、连阳放量/缩量连阳扣分 |
| 波动可控度 | 10 | ATR%、年化波动、60 日最大回撤、Beta |
| 位置与拥挤 | 12 | 120 日位置、BIAS20、距 60 日高 |
| 资金 | 15 | 主力净流入、超大单同向 |
| 多周期共振 | 10 | 日线 × 周线(按自然周聚合)一致度 |
| 形态结构 | 6 | 摆动高低点、布林 %B、筹码峰 POC / 密集区 |

输出:评级(强烈看多…看空)、行动(可以买/持有不追/小仓试/等右侧/不碰)、
**三类买入窗口**(回踩承接 / 右侧确认 / 突破确认,各带触发条件与失效条件)、
**卖出窗口**(吊灯止损 / 趋势止盈 / 分批止盈 / 情绪止盈)、
交易计划(分档建仓、结构性止损、1.2R→2.5R→4R 阶梯、仓位、时间止损、动量衰减、轮动退出)、
**持仓诊断**(填成本价/股数 → 盈亏、R 倍数、加/减/走建议)、
**反面证据**(主动列出与结论相反的信号)。

---

## 3. 量化:市场状态 + 25 行业配置 + 灵活退出

### 3.1 状态识别(`app/quant/engine.py`)

指数趋势(60%)+ 市场广度(25%)+ 波动(15%)→ 五档:进攻/中性偏多/震荡/防守/危机。
权重随状态切换(进攻偏动量,震荡偏反转与资金,防守偏低波),
阴跌缩量只判"防守",只有急跌放量才判"危机"。

### 3.2 反人性条款

- **反拥挤**:60 日涨幅分位 + 120 日位置 + BIAS → 拥挤度 >78% 直接降级为"持有不追"
- **恐慌反转**:RSI<32 + 位置<25% + 缩量止跌 + MACD 底背离 → 左侧试仓(只用 1/3 仓)
- **不追情绪顶**:RSI≥78 或(拥挤>0.85 且乖离>12%)→ "不追/兑现"
- **不在暴跌当天砍**:单日跌 >3% 但未破 MA60 → 当天不卖

### 3.3 资产配置(`app/quant/allocation.py`)

30 个行业/宽基 ETF → 评分(20/60 日动量 + 趋势 + 反拥挤 + 资金 + 超跌修复)
→ 核心(宽基)+ 卫星(TOP 2–8 个行业)+ 现金三层;单板块 ≤12%,按状态决定权益上限。
输出目标权重表 + 每板块动作 + 再平衡规则。

### 3.4 退出状态机(`app/quant/exits.py`)

硬止损(结构位 / 2.5ATR)、吊灯止损(高点 − k·ATR)、均线破位、分批止盈、
时间止损(20 日未达 1R)、动量衰减、板块轮动退出。卖出不看买入评分。

### 3.5 样本外回测(`app/quant/backtest2.py`)

**只认 walk-forward**:训练 252 日 → 测试 126 日 → 前移 126 日,参数只在训练段挑。
打分、拥挤闸门、状态识别与实盘 `engine.py` **完全同一套**(2026-10-24 审计后统一)。

- 标的:35 只行业+宽基 ETF(用 ETF 而非个股,避免"正好选到翻倍股"的幸存者偏差)
- 区间:2021-01 ~ 2026-10(跨 2021 结构市 / 2022 熊市 / 2023 阴跌 / 2024 反转 / 2025 主线 / 2026 调整)
- 成本:单边 0.13%(佣金 0.03% + 滑点 0.10%),ETF 免印花税

当前结果(2026-10-24 实测):

```
全样本:     +7.28%  年化 1.55%  Sharpe 0.19  MDD -23.3%  429 笔  胜率 39.6%  盈亏比 2.09
样本外拼接: -15.95% vs 沪深300 -6.37%  →  超额 -9.58pp
IS Sharpe 0.41 → OOS -0.64
```

**诚实结论(重要)**:这套模型**没有通过样本外检验**。全样本 24 组参数配置的中位数 +17.4%
(全部跑赢基准 -11.1%),但同一框架下最差 -7.5%、最好 +31.8%(标准差 13pp),
再叠加 walk-forward 的负超额,结论是:**框架有相对优势,但绝对收益不可预测,不能照着买。**

详见 `reports/量化策略审计-20261024.md`。审计可复现:

```bash
.venv/bin/python scripts/audit_quant.py     # 9 项不变量审计
.venv/bin/python scripts/sensitivity.py     # 24 组配置敏感性
```

### 3.6 纸面跟踪(`app/quant/paper.py`)

回测终归有假设。每个交易日首次刷新时,把当日 TOP10(含止损/目标)写进
`data/paper.jsonl`(只写一次,不可回改);结算时用**次一交易日开盘价**建仓、
按最新收盘算收益,并对比沪深300。只统计满 5 个交易日的批次。
`GET /api/paper` 或「样本外回测」页底部查看。

---

## 4. 启动

```bash
cd cnus-info-expert-v2
.venv/bin/python -m uvicorn app.main:app --port 8722
# 前端开发热更新(可选)
cd web && npm run dev        # 5173,代理到 8722
# 生产构建
cd web && npm run build
```

首次启动 30–60 秒完成快照预热(期间接口返回 503 + 提示,不会白屏卡死)。
`GET /api/health` 看 `ready` 与各数据集 `age_s`。

配置:`config/mcp.json`(NeoData 端点)、`config/cloud.json`(免密钥 LLM)、
`.env`(`TUSHARE_RDS_KEY` / `TUSHARE_PROMAX_KEY` / `LLM_PROVIDER` / `LLM_API_KEY`)。

---

## 5. API

| 接口 | 说明 |
|---|---|
| `GET /api/health` `/api/hub` | 服务与快照状态(含每个数据集的 age/stale/error) |
| `GET /api/overview` | 首屏:指数 + 板块 ETF + 状态 + TOP 预览 |
| `GET /api/quotes?secids=` | 轻量行情轮询(读快照) |
| `GET /api/search?q=` | 名称/代码/拼音/英文代码搜索 |
| `GET /api/analyze?q=&cost=&shares=` | 任意标的深度研判 + 持仓诊断 |
| `GET /api/analyze/{secid}` | 同上,按 secid |
| `GET /api/recommendations` | 量化 TOP20 + 卖出清单(读快照,15ms) |
| `GET /api/allocation` | 25 行业资产配置 |
| `GET /api/regime` | 市场状态 |
| `GET /api/etf-board` | 30 行业 + 7 宽基 ETF 全景 |
| `GET /api/fundflow` | 板块资金流排行 |
| `GET /api/top-movers?period=day\|week\|month` | 涨跌幅榜 |
| `GET /api/stock?secid=` | 单标的聚合(行情/K线/指标/资金/新闻/量化行) |
| `GET /api/walkforward` | 样本外回测(首次约 20s,缓存 6h) |
| `GET /api/paper` | 纸面跟踪账本 |
| `GET /api/live?secids=&interval=3` | **实时行情推送(SSE)**:quotes 增量 + signal 事件 + 心跳 |
| `GET /api/vitality` | 市场活力:涨跌停/连板/龙虎榜/两融/期指基差 |
| `GET /api/etf-board` | 30 行业 + 7 宽基 ETF 全景 + **宽基ETF资金面**(主力净买/份额申赎/托底申购识别) |
| `GET /api/agent/stream?subject=&budget=90` | 智能体 SSE 轨迹与报告 |
| `GET /api/maskboard` | 口罩哥同款看板(存储双雄/美光/SOX/光模块) |

---

## 6. 目录

```
app/
  dataflows/
    hub.py          快照中枢(本项目的性能核心)
    mcp_source.py   NeoData MCP 封装(并发批量)
    symbols.py      标的全集与模糊搜索
    quotes.py kline.py sectors.py tsboard.py etf_board.py news.py macro.py
  quant/
    indicators.py   纯 Python 指标库(MA/MACD/RSI/KDJ/BOLL/ATR/ADX/OBV/筹码)
    engine.py       状态识别 + 因子打分 + 交易计划
    analysis.py     单标的 8 维研判 + 买卖时机
    allocation.py   25 行业资产配置
    exits.py        退出状态机
    backtest2.py    walk-forward 样本外回测
    paper.py        纸面跟踪账本
    rotation.py     broad_universe(市值前 N + 行业)
    backtest.py     旧版个股回测(保留,脚本在用)
  agents/           多智能体图(5 侦察→辩论→研判→风控→主编→记忆)+ SSE
  api/routes.py     HTTP 层(全部读快照)
web/src/pages/      Dashboard / Analysis / Recommendations / Allocation / EtfBoard / Backtest ...
```

---

## 7. 已知边界

- NeoData 的 `limit` 实际返回约请求量的 65%,`nd_kline` 已超量请求并截尾
- 东财 `clist` 单页上限 100,IP 限流时会返回空 → 走 RDS 聚合兜底
- datahubco 的 `moneyflow_ind_dc` / `moneyflow_ths` 无权限(403)→ 板块资金流自行聚合
- Promax 通道 Key 失效时整体 401,换 Key 即恢复(不改代码)
- 美股无"主力资金"口径 → 资金维度取中性 0.5,不硬编
- GDELT 免费额度不稳定:失败不再写 600s 缓存(改为 30s),且按类目词表做相关性过滤
- KOL 观点库是**人工策展的静态文案**,不是实时抓取,只作情绪参考
- 回测不含分红与极端流动性,纸面账本不含无法成交的情况

---

*本项目为研究与决策辅助工具,所有信号不构成投资建议;止损位必须执行,否则概率会失效。*
