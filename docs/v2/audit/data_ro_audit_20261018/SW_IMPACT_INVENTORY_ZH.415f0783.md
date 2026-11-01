# 申万一级（SW L1）影响面盘点 + 来源追溯（只读）
- 作者：QuantLab Data；时间：2026-10-18 06:48–07:05 ET。只读：rg/读源码文本，未 import 或运行项目代码，未读价格/因子数据，未改任何数据/代码/已有文档。唯一的数据读取是 pyarrow 只读 parquet 元数据 num_rows（sw_pit 两个文件）。
- BAD = data/v2/sw_pit/industry_members_sw_l1_pit.parquet（sha 0b1d3432，7573 行）；CLEAN = data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet（sha 89d4afa3）。

## 0. 证据归档
06:48:48 ET：cp -p /tmp/data_ro_audit_20261018/* 到本目录，sha256sum -c SHA256SUMS.txt：13/13 OK。

## 1. 命令
- rg -n -S "industry_members_sw_l1_pit|sw_pit|sw_l1_pit|industry_members_sw_l1_tushare|industry_members|sw_l1" -g *.py -g *.sh -g *.cmd -g *.yaml -g *.yml -g *.toml scripts scripts_eng research quantlab qlab_b services tests rev *.py *.sh
- rg -n "sw_pit/industry_members_sw_l1_pit|industry_members_sw_l1_pit" -g *.py -g *.sh -g *.cmd -g *.yaml -g *.json -g *.ok（排除 _review docs logs output/ai_factor）
- rg -l -S <同上> output -g *.ok -g *.cmd：只有 output/alpha/_consumed/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1...ok（第 2 行仅是并发禁令里提到 sw_pit_refresh，不读 SW）
- 共享加载函数：research/g1g5_nontextbook_weights.py:74 SW_MEMBERS=CLEAN；:121 _load_sw_members；:168 sw_code_on（无命中返回 None，:174-176）。quantlab/data/v2_readers.py load_sw_l1_members 默认 CLEAN（:5,:630），回退 prefix/vote，不涉及 BAD。

## 2. 影响面表
| 消费方 | 文件 | 读哪个 | 用途 | 缺行业的处理 |
|---|---|---|---|---|
| 纸面轨 capacity_adv | research/capacity_adv_paper_extend.py:35 -> research/g1g5_capacity_adv_weights.py:56-57,76,222-224,296,333 | CLEAN（经 _load_sw_members） | 行业去均值打分 + 行业硬上限 28% | sw_code_on 为 None -> 不打分（剔出候选，:223-224）；后续上限用 "_UNK" 桶 |
| 纸面轨 B4 | research/b4_paper_extend.py:38-43 -> capacity_adv + g1g5_earnings_event/insider_increase/equity_incentive_weights.py | CLEAN | 行业相对跳空确认 + SW L1 <=28% | earnings_event:121-122 无行业则无同业；:194 上限检查用 "_UNK" |
| 纸面轨 S6 | research/s6_paper_extend.py:22,35-36（复用 B4 及同一组腿脚本） | CLEAN | 同上 | 同上 |
| 叶23 | research/g1g5_sue_desens_cs_alpha.py:20,85,115 | cs_panel_v2_resumefix -> scripts/fix_sd1/sd1_common.py:29 sw_l1_sha256=CLEAN；build_cs_panel_v2_resumefix.py:44-46 | 行业 <=25% 上限 | panel 内 out_date fillna(2100)；不读 BAD |
| 叶24 | research/g1g5_imax_intraday_alpha.py:35,65,96 | 同上（CLEAN 经 cs_panel） | 行业 <=25% | 同上 |
| Strategy hiliq/capadv/B4 X2 | research/strategy_hiliq_capadv_b4_x2.py:33,76,158,316,502 | BAD | :76 load_industry_map -> :158 apply_ind_cap 行业硬上限（合成书）；:316 行业权重披露 | 取每个 ts_code 按 in_date 最后一行（不看 out_date），所以 349 只仍取到最后已知行业，不丢；12 只双开 tail(1) 只留一条，不重复计；查不到 -> "_UNK_"（:101）|
| Strategy fulla B4 X2 | research/strategy_fulla_b4_x2.py:25,255-285 | BAD | 仅披露（行业权重时间占比） | 同上，最后已知行业；notna 过滤 |
| 优化器 OPTIMIZER_V1 Core | research/optimizer_core_x2_run_v1_4.py:93-98（钉 sw_members_sha256=CLEAN，经 C.load_sw_map/_load_sw_members） | CLEAN | 行业基准/约束 | sw_code_on 语义 |
| Beta | quantlab/beta/smallcap_sleeve.py:101,306,721 / smallcap_history_selector.py:84（cfg data.sw_l1 = CLEAN）；quantlab/beta/sleeve.py:1076 = prefix | CLEAN / prefix | 行业上限 12、行业结构 | sw_l1_unknown_names 计数披露 |
| Intel | research/intel/intel_common.py:170-171、intel_event_study.py:39、intel_c1_gap_split.py:25 | BAD | 披露/事件研究（相关个股、行业事件） | r3 有新鲜度+完整性检查；缺行业的股票不会列为相关个股 |
| Alpha CMC | 无读取（.ok 只提到并发禁令） | 无 | 不用 | - |
| 其他 | scripts/nightly_update.py:54 与 scripts/acquire/sw_pit_refresh.py（BAD 的写入方/打包）；output/v3/beta_risk_budget_prereg/measure_baseline.py:48（BAD，预注册基线）；research/attrib_v2/common.py:24（CLEAN）；quantlab/portfolio/v2_s2_book.py:64,165（CLEAN）；quantlab/portfolio/research_loop.py:246,331（sw_l1_pit/industry_members_sw_l1.parquet vote 版）；scripts/acquire/promotion_acceptance.py、data_progress_dashboard.py（CLEAN，元数据） | | | |

## 3. 结论：10-19 纸面轨
不会因为 BAD 的 349 个缺失 / 12 个双开产生错误持仓。capacity_adv、B4、S6 的纸面 runner 只经 g1g5_nontextbook_weights.py:74 读 CLEAN（每只股票恰好一个当前行业，5914 只，无缺失无双开），不读 BAD。BAD 只被 Strategy X2 合成脚本（窗口止于 2026-10-09，非纸面 runner）、Intel 和一个 v3 预注册基线脚本读。剩余风险：CLEAN 中真正没有行业的股票会被 capacity_adv 从打分中剔除（g1g5_capacity_adv_weights.py:222-224），这是既有冻结规则，与 BAD 无关。

## 4. 叶23/24 X2 窗口
- 叶23 .ok output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_10_X2.ok:5-7：scope=X2，window 2024-06-03..2026-10-09；脚本 g1g5_sue_desens_cs_alpha.py:115 X2E=2026-10-09。叶24 g1g5_imax_intraday_alpha.py:96 同样 2026-10-09。
- 两者都通过 cs_panel_v2_resumefix 使用 CLEAN（sd1_common.py:29），不读 BAD。即使读 BAD，窗口终点 10-09 早于 BAD 缺失区间的大部分；但 BAD 缺失始于 09-24，所以 09-24..10-09 这 10 个交易日会受影响——实际未读，故无影响。

## 5. 来源追溯
### 5.1 10-14 删掉 254 个代码（7743 -> 7573）
- 不是文档描述的那次修补。docs/v2/ALPHA_DATA_D5D6_FIX_ZH.md:3,G4 行（作者 Data）写的是 L1 7743 -> 7735（删同代码同 in_date 的已关闭重复，加 is_primary，197 只无现行行业不补）。bak_pre_fix_20261014 实测 7743 行（sha 59734014），与之对应。
- 现在的 0b1d3432（7573 行）来自 10-14 03:50:24–04:00:20 ET 的自动重拉：scripts/acquire/queue_chain_20261014.py:139-142 nightly() 调 scripts/nightly_update.py --steps hsgt,sw --date 20261013 -> scripts/nightly_update.py:39 sw_pit_refresh.py 全量重建。logs/queue_chain_20261014.log:5（04:00:20 ok）；logs/nightly/verify_20261014.log:39-41（sw ok 596s）；logs/nightly/20261013_sw.log:2-6：members Y 5914 / N 2006，union rows 11028，instruments 5600，L1 rows 7573，current_members 5566——与 manifest built 2026-10-14T04:00:19.99 一致。
- 依据：无人工依据，是 relay 截断后的重拉直接覆盖了已修补的表。sw_pit_refresh.py 只有 instruments>5000 的断言（:33 附近），5600 通过，所以截断没被拦下；分 L1 补拉循环（l1 fail 0 次）也没能补齐。修补文档描述的 7735 行版本已被覆盖、现已不存在。
- git：git log --all -- data/v2/sw_pit data/v2/sw_l1_pit docs/v2/ALPHA_DATA_D5D6_FIX_ZH.md 无输出（数据不入 git，仓库共 26 个提交）。
- 注：sw_pit 下所有文件 mtime 为 10-18 01:13:13–01:13:16，是 01:13 整体回写的结果，不是新的写入。

### 5.2 10-18 01:08 的 CLEAN 与 index_member_all
- 是恢复，不是拉取。box 01:05 重启（TEAM_STATE_latest.md:47）；01:05:55–01:11:59 ET 间 data/v2 下 104,071 个文件被整体回写，sw_l1_pit 全目录 01:08:19–01:08:43 写成。
- CLEAN 的 sha 89d4afa3 与 output/data_v2_bundle/sw_l1_pit/ 及 output/data_v2_bundle.tar 内 data_v2_bundle/sw_l1_pit/industry_members_sw_l1_tushare.parquet（tar 内时间 2026-10-10 14:42，107038 字节）逐字节一致；sw_l1_pit/manifest.json 与 bundle 中的 cmp 一致，fetch_time 2026-10-10T10:01:23-04:00，rows 7115，in_date_max 2026-09-24。即内容是 10-10 那次 tushare_relay_pull（scripts/acquire/tushare_relay_pull.py:140-151,223-230 写这两个路径）的结果。
- tushare_raw/index_member_all/*（62 个文件，mtime 01:08:43）不在 bundle tar 内，但落在同一整体回写窗口；没有任何 01:00–01:15 的拉取日志（logs/ 中这一区间的文件都是回写的旧日志），/home/box/.bash_history 01:05:59 重建、仅 9 字节，/root 不可读。
- _recovery/ai/RECOVERY_MANIFEST_ZH.md:3 记录 01:13:24–01:14:51 第二次整体回写，只列 AI 文件，未列 sw_l1_pit；其他 _recovery/*/RECOVERY_MANIFEST 中也无 sw_l1_pit / index_member_all 条目。
- /cursor/stores 下只看到本 bot 的 store 与 user，未发现其他 agent 记录。
