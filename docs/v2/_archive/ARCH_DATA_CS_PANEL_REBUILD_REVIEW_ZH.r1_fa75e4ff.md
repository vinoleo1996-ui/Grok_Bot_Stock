# Arch 审核：Data cs_panel 复牌重建方案（D-1～D-4）

- 审核人：QuantLab Arch｜时间：2026-10-18 01:10 ET｜只读审核，未改任何 Data 代码或面板，未算任何叶收益/IC
- 被审对象（Data 自报）：docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md；诊断 docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md
- 内存：独立抽查按年分块读 universe_mask_hiliq_v1.parquet，峰值 RSS ≈ 494MB（≤1.5GB）

## 0. 结论

**CONDITIONAL（含 P0 阻断）——本轮不发 .ok。**

方向认可：独立证据支持 D-1、D-3、广汇汽车面值退市三项诊断。但被审的方案文档、诊断文档、strategy_hiliq_universe_v1.py、tier1_materialize、构建脚本、现行 cs_panel 在共享盒子上均不存在，无法核 sha、核第 148 行、核 125 行，也无脚本 sha 可钉。按规则，构建脚本不存在则不写 .ok。

## 1. 盒子现状（事实）

在 /workspace 全盘 find/rg 均未找到：
- docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md、docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md
- strategy_hiliq_universe_v1.py（任何路径）；任何引用 HI_LIQ/hiliq 的 .py
- tier1_materialize；任何含 is_resume_day / hiliq_carry / resumefix 的文件
- cs_panel*（任何路径）；output/data/ 目录不存在；全盘无任何 .ok 文件
- 另：docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md（SD1，2e428f39）与 MILP 预注册规格也不在；scripts_eng/ 不存在；output/loop/TEAM_STATE_latest.md 只剩 1 行。docs/v2 与 output 下文件 mtime 均为 2026-10-18 01:06–01:08 ET，像是盒子被恢复成了较早快照。需要主 Agent 确认工作区是否被重置。

存在且可用于抽查的：output/strategy_hiliq/universe_mask_hiliq_v1.parquet（11,748,583 行；列 date/instrument/in_universe/st/suspended/young/adv_fail/adv20_yuan；本快照覆盖到 2026-10-14）；data/v2/tushare_raw/{suspend_d（2024-07-25～2026-10-09，168 个有事件日文件）, daily, namechange, stock_basic}。

## 2. 独立抽查

| 项 | 结果 |
|---|---|
| 第 148 行逻辑 | **无法核**：文件不存在。行为层面见下行，与「复牌首日必被剔除」一致 |
| 复牌日 vs 掩码（2024-07-25 起） | suspend_d 中 R 记录 1,353 条；能在掩码中匹配的 1,321 条**全部** suspended=True、in_universe=False（2024：318；2025：561；2026：442）；32 条掩码无行。1,353 条中 1,322 条当日 vol>0，即确有成交却被判停牌 |
| 4971 / 2865 / 734 | **无法复算**：本盒 suspend_d 只从 2024-07-25 起，无 2018 起全量；cs_panel 不在。我数到的 1,353 是「2024-07-25 起所有 R 记录」口径，与 Data「2024 起应补 734」口径不同（后者应是还须满足 HI_LIQ 其余条件：非 ST、非次新、ADV 达标）。差额 4971−2865=2106 的解释须由 Data 在 manifest 里按原因分解（见 P1-3） |
| 复牌日收益分布 | 1,322 个有成交复牌日 close/pre_close−1：均值 −1.74%，中位 −0.29%，最小 −96.4%，最大 +30%。剔除复牌日确会抹掉大幅负跳空 → 收益向上偏 |
| 4 例抽样 | 000639.SZ 2026-04-30（−5.14%）；688521.SH 2025-09-12（+20.0%）；300205.SZ 2025-04-30（+5.34%）；300506.SZ 2025-05-20（+2.03%）。四例均当日有成交、掩码 suspended=True / in_universe=False |
| 002445 2026-08-24 | suspend_d 记为 **R**（复牌），daily vol=47,973.94 手，close 3.37（pre 3.06）；掩码 suspended=True。即「有成交却标停牌」属实，根因是 R 被当停牌，与 D-2 描述一致（2026-03-09 同股同样情况） |
| D-2 125 行 | **无法核**：tier1_materialize 及其产物不在盒子上 |
| D-3「退市XX」61 只 | namechange 中以「退市」开头的名称 68 行、**61 个代码**，与 61 吻合。抽样 600200.SH 退市苏吴 2025-12-09、600896.SH 退市海医 2022-06-28、600781.SH 退市辅仁 2023-05-30、600193.SH 退市创兴 2026-06-08、600647.SH 退市同达 2024-06-05，change_reason 均为「退市整理期」。另有「XX退」写法 90 个代码，Data 规则须两种写法都覆盖 |
| 广汇汽车 600297.SH | stock_basic(D)：delist_date 2024-08-28，名称「广汇汽车(退)」。daily：2024-06-20 起连续 **20** 个交易日收盘 <1 元，最后交易日 2024-07-17（close 0.78），namechange 无「退市」改名、无整理期交易。**面值退市属实**；不应走整理期强卖路径 |

## 3. 设计审核（对照业界做法）

1. **PIT**：「当日无成交」收盘后才知道，只可用于当日收益记账/掩码事后标注，不可用于当日选股。业界做法（Barra/CRSP 类回测）：T 日成分与入选只用 T−1 及以前信息；持仓穿越停牌保持权重、复牌日按真实价格入账；不可交易日不得新建仓。
2. **hiliq_carry 的 PIT 性**：方案文档不在，无法确认其定义。Arch 规定其**必须**满足：hiliq_carry[T] = 「T−1 收盘时在 HI_LIQ 内且已持有/可持有」的延续标志，只依赖 ≤T−1 信息，停牌期间保持 True，直到复牌日（含）收益入账完毕；不得用 T 日成交量决定。若 Data 的定义用了 T 日 vol，则判 P0 不合规。
3. **is_resume_day**：可用当日信息（事后标注），仅作披露与入场闸门，不得进入因子或选股。
4. **掩码不改 → 纸面轨不受影响**：方向正确；但须由 Data 给出 universe_mask_hiliq_v1.parquet 重建前后 sha256 一致的证明（当前快照 sha 由 Data 在 manifest 记录）。
5. **入账口径与 SD1 一致**：停牌拒买卖、冻结持仓；复牌跳空按真实价入账；开盘触板拒单；整理期开盘强卖受跌停约束；强制退市默认 0 回收（30%/70% 敏感性）；策略层不读退市日期。

## 4. 列裁定

- **叶评价收益记账**：用 **hiliq_carry**（持有延续，含停牌期 0 收益与复牌日真实跳空），不得因停牌/复牌删除样本行。
- **is_resume_day**：仅披露 + 入场闸门（当日不可交易/复牌日不新建仓，除非开盘未触板且引擎 SD1 允许成交）；不入因子、不入选股、不作为剔除条件。
- **AI 叶 23 及以后**：信号/入选用 T−1 截面（现行掩码 in_universe[T−1]），收益记账用 hiliq_carry，与上同。
- 上述裁定待 Data 方案文档上盒、我核实两列定义后生效；若定义与此不符，以本节为准修改定义。

## 5. P 清单

- **P0-1 审核对象缺失**：将方案文档、诊断文档、strategy_hiliq_universe_v1.py、tier1_materialize 及**构建脚本**放回 /workspace/QuantLab 并报 sha256；构建脚本须为独立文件，可钉 sha。缺则不发 .ok。
- **P0-2 hiliq_carry PIT 定义**：按 §3.2 写成精确公式并附单测（停牌中段、复牌日、复牌日开盘触板、整理期、面值退市各一例）。
- **P0-3 位级回归**：构建脚本须有修复开关；全部开关关闭时输出与现行 cs_panel **逐位一致**（报两边 sha256），并报 universe_mask_hiliq_v1.parquet 前后 sha256 一致。
- **P1-1 版本化**：新面板落新目录 cs_panel_v2_resumefix，附 manifest（脚本 sha、输入快照 sha、交易日历 PIT 版本、生成时间、各列定义）；旧面板不覆盖、不删除。
- **P1-2 变更计数**：manifest 按年列出新增行、改动行（按 D-1/D-2/D-3/D-4 分列），以及受影响代码数。
- **P1-3 4971 vs 2865 分解**：按原因列出未补的 2106 次（不在 HI_LIQ：ST/次新/ADV 不足/复牌当日即再停/无行情等），合计须闭合。
- **P1-4 D-2/D-3/D-4 下游**：tradestatus 修正（R 与盘中停牌不置 0）、整理期两种写法（「退市XX」「XX退」）、面值退市分类必须作为 SD1 引擎输入（exec_SD1 / wb_SD1）的同一份数据源，引擎侧不得另写一套判定；SD0 开关仍须与现行结果逐位一致。
- **P1-5 面值退市路径**：面值退市无整理期，SD1 按最后可成交价/跌停约束处理，强制退市回收 0%（30%/70% 敏感性）；不得套用整理期强卖逻辑。
- **P2-1 叶 15–22 可按需重算**：保留旧面板与新面板并存，叶 15–22 的构建脚本能以面板版本参数切换重跑；是否重算由 Arch 另行评估，仅披露。
- **P2-2 内存**：重建按年分块读写，单进程 RSS ≤1.5GB，日志记录峰值。
- **P3-1 抽查附录**：manifest 附 002445 2026-08-24、600297 广汇汽车、本审 4 例的前后行对照。

## 6. 运行授权

未写 output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok。阻断项：P0-1（构建脚本不存在，无 sha 可钉）、P0-2、P0-3。P0 清零后 Data 回报脚本 sha，Arch 再发结构化 .ok（allow_full / allow_smoke 显式给值）。
