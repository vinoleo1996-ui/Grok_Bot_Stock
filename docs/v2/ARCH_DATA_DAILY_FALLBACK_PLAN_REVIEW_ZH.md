# Arch 审阅：Data 日线降级备用方案 r2（影子披露轨）

- 审阅对象：docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r2.md，sha256 3985730628e3c3d86678e817cfafc1b4f43eabf32da172c344dc74402a94b174（取代 r1 92ceae2d）
- 审阅人：QuantLab Arch；时间：2026-10-18T09:42:03-04:00；基线 HEAD 0ec38296
- 方式：只做静态审阅，用 rg 和 Read 读源码。execution.py 373fed30、v2_readers.py 84f07b1f、b4_paper.py ffe195e6、paper_track.py 4b4b63da 与冻结清单一致。
- **结论：PASS with conditions（有条件通过）**。r2 已经把 B 改为纯影子轨，r1 的 P1-a、P1-b、P1-c 都已关闭。还剩 2 个 P2 和若干 P3，需要在实施 .ok 之前补进方案。
- promotion_approved=false；live=false

## 1. 引用行号核对

| 方案引用 | 实际 | 结论 |
|---|---|---|
| execution.py:1197-1352 load_exec_panels | 函数签名约在 L1194，docstring 从 L1197 开始，L1226 是 fields，L1271–1294 是成交量单位优先级（volume_shares，然后 volume_unit，然后比值推断），L1300 是 open_status 停牌，L1349–1352 return | 正确 |
| v2_readers.py:17, :89 | L17 注释写的是 asof_extend_tushare_202610；L89 是 DEFAULT_ASOF_EXTEND_TUSHARE_DIR | 正确 |
| eng_daily_panels.py:71-98 | 行号范围对，L94 volume=float(r.vol)，L98 volume_shares=vol×100。但 asof_em 这一步写的是 **data/v2/asof_extend_202610/panels**（docstring L4，代码 L66），不是 tushare 目录。tushare 目录在 asof_ts 步骤（L5、L117）只做校验 | **需更正（P3-1）** |
| tier1_materialize.py:40-132 | L40 是 ×100（手转股），L41 是 ×1000（千元转元），L53–61 stk_limit，L62–71 suspend_d，L115 写 asof_extend_tushare_202610/panels。**L124 把 is_st_at_open 硬写为 False**，不是从 stock_st 来的 | 范围对；ST 来源需更正（P3-2） |
| execution.py:1569-1600 | load_corporate_action_panels 定义在 L1568；L1576 是 dividend_by_exdate_tushare；用的是税前 cash_div_tax 和 stk_div | 正确 |

## 2. 发现

- **P2-1：纸面链上确实存在「回退目录」入口，§2 的说法不准确**。
  - v2_readers.load_merged_panel 在 L1778–1782 处：某只股票的 tushare 面板不存在时，会**逐只回退**读取 data/v2/asof_extend_202610/panels/<iid>.parquet。日历在 L1679–1680 回退到 asof_extend_202610/calendar.parquet，manifest 在 L1625 也会读回退目录。
  - 这个目录同时也是东财增强脚本 scripts/enrich_asof_extend_em_seq.py 的写入目标（L12、L15、L91）。
  - 方案已经把写入限定在 data/v2/_shadow_public/，本身不构成漏洞。但必须在 §2、§7、§11 写明以下三点，并在 run .ok 里列为条件：
    - 影子脚本禁止写 asof_extend_202610（panels、calendar、manifest）、asof_extend_tushare_202610、float_mktcap 和 data_freshness_status.json；
    - 禁止调用 enrich_asof_extend_em*.py；
    - 运行回执要给出上述目录运行前后的 sha 清单，并证明没有变化。
- **P2-2（Q1）：events 会被纸面链间接读到**。见 §3 Q1。B 从不写 events，所以没有污染风险。但 A 和 C 路径要把权重延长到 10-19，就需要 10-19 的 events 是新鲜的。方案 §3.3 应改为「间接读取：是」，并把 events 列进 A/C 所需表的清单。
- **P3-1**：§3.2 表里的「生成处」要拆开写：tushare 目录由 tier1_materialize 写；eng_daily_panels 的 asof_em 写的是回退目录，而且那里的 volume 列单位是手（volume_unit=lot_100sh），另有 volume_shares 列；execution 读取时优先用 volume_shares。
- **P3-2**：tushare 目录面板的 is_st_at_open 恒为 False（tier1_materialize L124）。D0 一侧的 ST 值在 v2_readers L1849–1851 做了前向填充。§3.2 里 ST 一行要更正。§4.5 的影子 ST 判定不受影响，但对照时要知道纸面实际的 ST 口径。
- **P3-3**：§3.1 漏列了纸面实际读取的几张表，见 Q2。
- **P3-4**：影子估值要读冻结纸面的 10-16 持仓输出，这属于读权重，需要 .ok。§11 的 run .ok 要钉住所读输出文件的 sha。
- **P3-5**：影子面板如果将来要和面板口径对照，应显式带上 volume_unit=share 和 volume_shares 两列，避免落到 execution L1286 的比值推断分支。

## 3. §12 开放问题答复

- **Q1：events 是否被间接读取？是，条件是纸面运行包含「延长腿权重」这一步。**
  - research/b4_paper_extend.py 的 run_legs()（L164–168）和 run_event_leg()（L171–176）用 python -c 重跑冻结脚本 research/g1g5_earnings_event_weights.py 和 g1g5_insider_increase_weights.py，只改 WEIGHT_END。这两个脚本在 L51–52 读 data/v2/events/announcements_classified_pit.parquet 和 announcements_classified_pit_post202406.parquet。
  - S6 的 equity_incentive 腿（g1g5_equity_incentive_weights.py L51–52）情况相同。
  - 以上脚本都在 paper_import_closure.json 里（b4_paper_extend 6c927ae6、s6_paper_extend 3b258bbe，以及各 weights 脚本）。
  - b4_paper.py 本身的 backfill 和 forward（L99–118）只读冻结权重文件，不直接读 events。
  - 10-19 的纸面流程是否执行 extend，请 Strategy 和 Eng 按运行手册确认。
- **Q2：书本引擎是否另读其他行情表？是。**
  - 书本引擎不在 scripts_eng，而是 quantlab/portfolio/book_smoke.py 调用 v2_multisleeve_book.py（b4_paper._run_smoke 在 L93–96）。scripts_eng 只在 monitor 里用到 conc_fill_diag，读的是输出文件。
  - v2_multisleeve_book.py 除了 load_execution_panels（L495）以外还读：
    - data/v2/etf/etf_daily_adj.parquet 的 close_hfq 和 amount（L76）；
    - with_ind_etf 时读 sw_l1_etf_map_pit_daily（L67）；
    - with_cb 时读 cb_daily 和 cb_basic_raw（L82–86）；
    - futures/raw/index_daily（L98）和 load_index_futures_panels（L93）；
    - L40–43 的 HASH_FILES 会做哈希。
  - extend 脚本还会读：tushare_raw/trade_cal.parquet（capacity_adv_paper_extend L75）、D1 估值（L84–85）、universe/mid_large_members_pit.parquet 和 daily_update_status（L134–141）、X2 拼接面板（D0 1c85 加 asof_extend_tushare_202610，见 g1g5_x2_panel_stitch L15–16），以及 _load_benchmark_closes（etf_daily_adj 里的 510300）。
  - 这些表 B 都不写，不影响影子轨安全。但 A 和 C 路径的「10-19 所需 Tushare 表清单」应该补全。
- **Q3：影子报告能否出现估算 NAV？可以，但有限制**：
  - 只能以区间或估算值的形式出现，并标注 SHADOW_NOT_NAV 和 PROVISIONAL；
  - 不报收益率和绩效结论，并列出不可用项；
  - 文件名和 manifest 带 shadow 与 not_for_paper=true；
  - **永远不写进**任何 ledger、nav.csv、actual_weights、scorecard、promotion_gate、forward 或 Leo 的 NAV 报告；
  - 如果做不到上述隔离，就改为只列持仓价格变动和不可用项。
- **Q4：特殊情形一律置 unavailable**：风险警示板（ST、*ST）、退市整理期、注册制新股上市前 5 日（主板、创业板、科创板都包括）、长期停牌后复牌首日、北交所（本来就已排除）、ST 状态冲突，以及除权可疑的代码，limit_status 一律为 unavailable。只有状态确定的普通主板、创业板、科创板股票才派生涨跌停价。派生价只用于是否触板的披露。

## 4. 实施 .ok 前需补的条件

1. 把 P2-1 写进方案，包括写入黑名单和运行前后目录 sha 回执。
2. 按 P2-2 和 Q1 更正 events 的结论，并把 events 列入 A/C 所需表。
3. 改正 P3-1、P3-2 的引用，补全 Q2 的表清单。
4. 公开源拉取属于联网读取，code .ok 和 run .ok 分开签；run .ok 需要附上主 Agent 书面转达的「Leo 选 B」。
