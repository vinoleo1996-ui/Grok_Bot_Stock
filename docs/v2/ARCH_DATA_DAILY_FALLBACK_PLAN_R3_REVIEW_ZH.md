# Arch 审查：Data 日线降级备用方案 r3（影子披露轨，静态审）

- 审查对象：docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3.md，sha256 f7cacfb1…（审前核对一致，286 行）。
- 回应对象：Arch r2 审 docs/v2/ARCH_DATA_DAILY_FALLBACK_PLAN_REVIEW_ZH.md（5072ec5c，审前核对一致）。
- 审查人：QuantLab Arch；签署时间：2026-10-18T10:16:59-04:00（ET）。
- 方式：只做静态审。只用 Read / rg / sed / ls / find 读源码文本与目录元数据；没读 parquet，没运行项目代码，没联网，没提交。
- promotion_approved=false；live=false。

## 结论：PASS with conditions（有条件通过）
- 5072ec5c 的 P2-1、P2-2、P3-1…P3-5、Q1-Q4 与 §4 条件 4 都已在 r3 §13.2（L271-286）逐条回应，并落到正文。
- 须补 2 个 P2（data_freshness 路径、前后 sha 清单范围），按下文裁定 §12 Q2，然后可签 code-change .ok。run .ok 仍须附主 Agent 书面转达的「Leo 选 B」。

## 逐项核对
| 项 | r3 位置 | 核对 | 结论 |
|---|---|---|---|
| P2-1 写入黑名单 6 项 | L38-44 | 含 asof_extend_202610/、asof_extend_tushare_202610/、float_mktcap/、data_freshness / daily_update_status、Tushare 表、events | 通过，第 4 项路径须改（P2-1） |
| 禁止 enrich_asof_extend_em* | L46、L243 | 不调用、不 import | 通过 |
| 运行前后 sha 清单 | L50、L197、L249 | 逐文件 path、size、mtime、sha256 + 汇总 sha | 通过，范围须扩大（P2-2） |
| P2-2 events 间接读取 | L108-116 | b4_paper_extend.py：run_legs L160-166（capacity_adv L163），run_event_leg L169-179（WEIGHT_END L173，subprocess L174）；s6_paper_extend.py L42 调 B.run_event_leg("equity_incentive")，L36 列出冻结 weights 脚本；三个 weights 脚本 L51-52 都读 announcements_classified_pit*.parquet | 属实（run_event_leg 止于 L179，见 P3-1） |
| Q2 书本引擎 | L61 | b4_paper.py L93-96 _run_smoke → book_smoke.run（L94）；forward 在 L108 import v2_multisleeve_book | 属实 |
| Q3 NAV | L199-203 | 只以区间出现，SHADOW_NOT_NAV + PROVISIONAL，不进任何 ledger / nav / FWD / Leo NAV 报告 | 通过 |
| Q4 七类 unavailable | L151-158 | ST/*ST、退市整理、新股前 5 日、长停复牌首日、北交所、ST 冲突、除权可疑 | 通过 |
| code .ok 与 run .ok 分开 | L238-249 | 分开签；run .ok 限两个域名、附「Leo 选 B」 | 通过 |
| v2_readers 回退入口 | L32-35 | L90、L149、L1625、L1678-1680、L1778-1782 逐行复核正确；ST 前向填充在 L1851-1853 | 属实 |
| tier1_materialize | L92、L101-102 | L62-71 为 suspend 块、L114-115 写主目录、L124 is_st_at_open=False | 属实 |

## 发现

### P1
- 无。

### P2
- **P2-1 黑名单第 4 项路径不对（即 §12 Q3）**。data/v2/acquire_status 不存在。data_freshness_status.json 的确切路径是 **output/data_freshness_status.json**：写入方 scripts/acquire/data_freshness_status.py L9（OUT 常量），nightly_update.py L43；读取方 quantlab/portfolio/research_loop.py L654（可被环境变量 QL_FRESH_PATH 覆盖）与 L665。要求：
  - 黑名单第 4 项改为确切路径 output/data_freshness_status.json 与 output/daily_update_status.json；
  - 影子脚本不得设置或导出 QL_FRESH_PATH；
  - run .ok 签发前由 Arch 再核一次该路径与当时 sha，写进 .ok。
- **P2-2 前后 sha 清单只覆盖黑名单第 1-3 项**（L50、L249）。要证明「纸面能读到的东西没变」，范围须扩大为：
  - 黑名单第 1-3 项目录（全量）；
  - output/data_freshness_status.json、output/daily_update_status.json；
  - data/v2/events 下两个 announcements_classified_pit*.parquet；
  - data/v2/tushare_raw/trade_cal.parquet；
  - paper_import_closure.json 所钉的全部文件。
  写入白名单（只许 data/v2/_shadow_public/20261019/）仍是第一道防线；sha 清单是证据，两者都要。

### P3
- **P3-1** run_event_leg 实际是 L169-179（return 在 L179），r3 写 L169-178；不影响结论。
- **P3-2** 标「据 Arch」的行号（§12 Q4）本次已逐行复核，全部属实（见上表与 capacity_adv_paper_extend.py L75 读 tushare_raw/trade_cal、L84-85 读 D1 估值；b4_paper.py L99-118 为 backfill / forward）。Data 实施前自己再跑一次同样的 rg，结果附回执后可去掉「据 Arch」标注。
- **P3-3** §12 Q1（10-19 是否执行 extend）仍待 Strategy / Eng 按运行手册确认；不阻塞 B，但决定 A/C 是否需要 10-19 的 events。
- **P3-4** 清单逐文件字段加 st_ctime_ns 与 inode。ctime 不能用 utime 改回，能抓到「写后改回 mtime」的情形。

## §12 开放问题裁定
- **Q2 黑名单目录的 sha 清单：全量 sha，不抽样。**
  - 本次 find / du 实测（只读元数据）：asof_extend_202610 共 10404 个文件、185M；asof_extend_tushare_202610 共 11161 个文件、175M；float_mktcap 9 个文件、360M。合计约 720M，全量 sha 只需几秒到几十秒的顺序读，占的是页缓存不是 RSS。
  - 我原先倾向「回退目录 size + mtime 全量 + 抽样 sha；冻结 closure 文件和其他黑名单目录全量 sha」。按实测体量，抽样省下的 IO 很少，却会留下未抽中文件被改而查不出的缺口，所以定为：**所有清单范围（P2-2）一律全量 sha**，同时记录 size、mtime_ns、ctime_ns、inode。
  - 运行前清单与运行后清单要在同一 run .ok 内完成；只做哈希，不解析内容；遵守一次只跑一个真实数据进程，并与 Arch 对齐 94322 停到 T。任何一项不一致：影子轨整体 FAIL，立即报 Arch。
- **Q3 data_freshness_status.json 路径**：已核实，见 P2-1。签 run .ok 前 Arch 再核一次。
- **Q4 「据 Arch」行号**：已复核，见 P3-2。

## Data 下一步
1. 出 r3.1（增量）：P2-1 改路径与 QL_FRESH_PATH 禁令；P2-2 扩大 sha 清单范围，按 Q2 裁定改为全量 sha + ctime / inode；P3 一并修订。
2. 交 code-change .ok 申请：脚本 scripts/acquire/daily_shadow_public.py 与 selftest 的完整文本（含白名单、黑名单、P2-2 清单范围的写死常量）。
3. 只有在 10-19 14:30 ET 中转仍不通、且主 Agent 书面转达「Leo 选 B」之后，才申请 run .ok；避开 10-19 16:40-18:40 ET。
