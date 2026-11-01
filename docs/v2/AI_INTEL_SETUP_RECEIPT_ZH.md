# AI 情报师 搭建回执

研究级，live=false，promotion_approved=false。不下单、不改任何权重、禁 GP；没跑 Book-Smoke，没起 8787；封存窗口没碰；峰值内存 RSS ≤0.8GB。生成：2026-10-13 22:57 ET。

## 路径
| 用途 | 路径 |
|---|---|
| 公共模块（数据源、规则表、个股映射） | `research/intel/intel_common.py` |
| 主脚本 | `research/intel/intel_run.py` |
| 事件研究 | `research/intel/intel_event_study.py` |
| 最新预警 | `output/intel/ALERTS_latest.md`、`output/intel/ALERTS_latest.json` |
| 历史 | `output/intel/history/ALERTS_YYYYMMDD_HHMM.{md,json}`（时间为 ET，用 zoneinfo America/New_York 换算，不依赖盒子时钟 CST） |
| intraday 状态 | `output/intel/intraday_state.json` |
| 事件研究结果 | `output/intel/event_study_full.csv`、`output/intel/event_study_hitrate.json`（intel_run 读取它来降级） |
| 事件研究报告 | `docs/v2/AI_INTEL_EVENT_STUDY_ZH.md` |

## 数据源可用性（2026-10-13 本机实测）
| 源 | 状态 |
|---|---|
| Yahoo chart v8（query1.finance.yahoo.com，curl/urllib 直连） | **可用**：^IXIC ^SOX KWEB ^TNX DX-Y.NYB ^N225 ^KS11 均有 10 年日线 |
| Yahoo ^HXC（纳斯达克中国金龙） | 实时报价可用，**无历史日线**，因此快照里取不到涨跌；中概改用 KWEB |
| yfinance 库 | 未安装（直接调 chart 接口，不依赖它） |
| stooq CSV | **不可用**（JS 浏览器校验页） |
| FRED CSV（fredgraph） | **不可用**（连接超时）；美债改用 ^TNX |
| Google News 搜索 RSS（337/出口管制/关税/实体清单） | 可用 |
| CNBC RSS | 可用 |
| USTR RSS（ustr.gov/rss.xml） | 可用 |
| BIS RSS（bis.gov/rss.xml） | 404，**不可用** |
| Reuters feeds | 无法解析，**不可用** |

## 运行命令
```bash
cd /workspace/QuantLab
python3 research/intel/intel_run.py --mode preopen     # A 股开盘前，建议 21:00 ET（=09:00 北京时间）
python3 research/intel/intel_run.py --mode intraday    # 盘中，建议每 10–15 分钟一次；无重大变化时不写文件
python3 research/intel/intel_event_study.py            # 刷新命中率（约 20 秒）
```
**持续运行尚未接入定时任务**（盒子上没装 cron 条目，也没起常驻进程），需要 Eng 或调度方按上面的频率调用。intraday 只拉新闻 12 小时窗口，preopen 拉 36 小时窗口。

### intraday 重大变化阈值（任一满足才写新文件）
- A：任一市场强度升级为「强」（指数单日 |涨跌| ≥2%，美债 ≥10bp，美元 ≥0.8%）；
- B：任一市场涨跌相对上次落盘再变动 ≥1.0pp（美债 ≥5bp，美元 ≥0.5%）；
- C：出现上次落盘没见过的、严重度 ≥2 的政策/贸易新闻。

### 判定规则
- 市场强度：「中」= |涨跌| ≥1%（美债 ≥5bp，美元 ≥0.5%）；「强」= ≥2%（10bp、0.8%）；「弱」不出冲击。
- 行业得分 = Σ 方向 × 强度（中=1，强=2；同一新闻主题对同一行业只计一次）。得分 ≤−2 判偏空，≥+2 判偏多，其余为观察。
- 降级：对应规则的历史命中率 <55% 或 n<10 → 观察；只由新闻驱动（未回测）→ 观察。
- 个股：每个行业取 mid_large 最新 session 流通市值前 5（small_cap=false），另附池外流通市值最大的 1 只（剔除 ST 和退市），标 small_cap=true（小盘）。

## JSON 字段（schema `quantlab.intel.alerts.v1`）
- `mode`：preopen / intraday；`generated_et`：生成时间 ET；`live`、`promotion_approved` 恒为 false；`pool_session`：mid_large 池日期。
- `markets.{key}`：`name`、`symbol`、`date`（该市场最后交易日）、`last`、`change`、`unit`（% 或 bp）、`grade`（弱/中/强）、`adverse`（对 A 股是否利空：指数跌，或美债、美元升）。
- `shocks[]`：`type`=market 时有 `key`、`change`、`grade`、`direction`；`type`=news 时有 `theme`、`title`、`source`、`published_et`、`link`、`severity`(1–3)。
- `alerts[]`：`industry`（申万一级）、`score`、`call`（偏多/偏空/观察）、`note`（降级原因）、`strength`、`reasons[]`、`invalidation[]`（失效条件）、`hist_support[]`（rule、n、hit_rate、rel_hit_rate、mean_ret_pct）、`stocks[]`（code、name、small_cap）。
- `source_status`：各数据源 ok 或 fail；`trigger`（只在 intraday 出现）：触发写入的阈值。

## 局限
- 新闻是英文标题关键词匹配，会误报（例如出口管制规避报道、非中美关税）；没有中文政策源；337 和实体清单查询当前都是 0 条。
- 规则表是人工先验；事件研究显示日韩规则和美债规则无效（会自动降级），纳指和费半对科技链有效，但样本小。
- 日经/KOSPI 在美东夜间就是亚洲盘中，快照取的是实时价，不是收盘价。
- ^HXC 没有涨跌数据；美债用 ^TNX（CBOE 收益率指数），不是 FRED 官方 DGS10。
- 不是交易信号，没接权重，也没接下单。
