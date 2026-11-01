# 预注册：申万行业 as-of（PIT）修复，改前/改后对照（r3e，Arch 已审：r3d 审查 PASS_WITH_CONDITIONS c08065f3；r3e 依据 Arch 2026-10-18 12:09 ET 裁定）

- 日期：2026-10-18（美东）；提出：QuantLab Strategy；状态：r3e，Arch 已审；对照运行未授权、未运行（需 Arch 签 run .ok）
- 代码提案（完整链 B r2 → r3d → r3e；B r2 与 r3d 于 2026-10-18 11:47 ET 连续落地，r3e 于 12:21 ET 增量落地）：B r2 `docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018_r2.diff`（sha256 d0fb1d3faa6962d19e8405280975e8818766ef406b00f390edcc9b02f81ee250；取代 r1 98633d9b；按 Arch 审查 3f195231 修改）→ r3d 完整 diff `docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3d.diff`（sha256 090e9c2a4ebbd40cd056f6438e2216a1292b00b172d8be99675c778ab5eceaa8；Arch 审查 c08065f3）→ r3e 增量 `docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3e_incremental.diff`（sha256 4f1952ef0e278613ec6283ef071ccde6ae2471a35cfb9f65f641c01fd907f670），r3e 完整 `docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3e.diff`（sha256 db151957a9bf17e90284e915edfd3b936c1083545a855b4b9b4171063eab533d）；r3e 自测回执 `docs/v2/audit/strategy_r3e/SELFTEST_R3E_RECEIPT_20261018.md`（sha256 ec10c0569813b16c2d9a7fb6317856afb8a182cfd00a371e5558e5691037ce91，85 passed）
- live=false，promotion=false。纸面（FROZEN_CONFIG、capadv/B4/S6 纸面轨、10-19 17:40 ET 纸面运行）和已封存产物都不动，也不读本结果。

## 1. 要回答的问题
hx2 合成 B4 时，行业 25% 上限用的是“每只股票最后一次出现的 l1_name”的静态映射，带前视偏差。改成按调仓日 as-of 归属后，结果变化多大。只做披露，不调参。

## 2. 口径（固定，不得改动）
- **as-of 规则**：调仓日 d 的有效行需满足 in_date < d，且 out_date 为空或 ≥ d。in_date 当天 18:00（上海时间）才发布，所以从下一交易日起生效。行过滤与 Intel sw_members_asof（a5b0b633/0e968759）逐行一致。
- **取重**：同一代码有多条有效行时，取 in_date 最新的一条；in_date 相同时，is_new=Y 优先，其次 out_date 为空的，再其次按文件行序。Arch 3f195231 已裁定采纳。Intel 现有的 keep="last"/keep="first" 与此不同，已转 Intel 对齐。
- **改分类空档日例外（主 Agent 2026-10-18 约 05:45 ET 裁定，有约束力）**：d 日某代码没有有效行、而它有一条旧行的 out_date == d−1（自然日）时，当天沿用该旧行的 l1_name，最多 1 个交易日。其余没有有效行的情况一律归入“未知行业”（_UNK_）。实现为公共函数 research/sw_members_asof.py::sw_l1_asof_with_gap_carry，只依赖 stdlib/numpy/pandas，以及 sw_pit_freshness 的错误类型；Intel 下一轮直接调用。只用于新代码；before 组不用。
- **完整性**：out_date 原值非空、却解析失败的，只要有 1 行就 raise SwPitIntegrityError，不会被当成“仍在成分”。in_date 解析失败的行计数并披露，这些行永不命中。
- **数据**：只用 data/v2/sw_pit/industry_members_sw_l1_pit.parquet，sha256 = 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6（manifest built 2026-10-14T04:00:19，美东时间）。check_sw_l1_pin 显式 raise，不用 assert。as-of 加载时，sha 与解析用的是同一份字节，两次读取的 sha 都写进 summary。
- **改前组**：改前（before_static）原样保留旧的 load_industry_map 实现：pd.to_datetime(coerce) 后 sort_values("in_date").groupby("ts_code").tail(1)，与 7dd5bea5 的逻辑逐字一致。改后（after_asof）用 as-of 加空档沿用。两组之间唯一的差别是行业映射。
- **窗口**：X2 = 2024-06-03 至 2026-10-09（hx2 常量 X2，book-smoke --windows X2）。
- **组合**：B4_50_25_25 = capacity_adv 0.5 / earnings_event 0.25 / insider_increase 0.25（HI_LIQ_V1.1 腿，hx2 中的 P 路径不变）；每条腿取 topN，60万 N=6，100万 N=10；单票上限 6%，超出部分转 510300.SH；股票袖套内申万一级行业上限 25%，迭代按比例缩放，超出部分转 510300.SH。
- **调仓频率**：照现有实现。合成按腿文件每个 session 的权重逐日生成 target weight（共同 session 取交集），没有另设调仓日。session 就是决策日，book-smoke 次日开盘成交。
- **成本与执行**：ExecConfig.strategy_v1（execution.py 373fed30）：次日开盘成交；佣金 0.00025，最低 5 元；印花税 2023-08-28 后卖出 0.0005；平方根冲击 k=1.0；参与率上限 10%；未成交部分顺延；按手取整；遵守涨跌停；按 tick 取整；处理公司行为。sleeves 为 {"core":0,"stock":1,"alpha_event":0}，arms 为 BOOK,C0。

## 3. 运行
- **暂停（主 Agent 2026-10-18 06:49 ET 裁定）**：自然日 pitfix 比对暂停，等 sw_l1_pit_v2 审完后改用 v2 sha 并重签 .ok；当前表 0b1d3432 已知 349 只在市无行业、12 代码双开（9-24 至 10-16）。下列运行比对计划本身不变。
- **授权**：在同一份 Arch 签的 run .ok 下只跑一次，不准重跑。不自行创建 .ok。
- **命令**：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/strategy_hiliq_capadv_b4_x2.py --pitfix-compare output/strategy_hiliq/pitfix_compare_20261018`
- **out_dir 保护**：out_dir 必须解析到 output/strategy_hiliq/ 之下，而且事先不存在；拒绝 b4、capadv_x2、legs，以及任何路径中带 paper 或 frozen 的目录。所有检查都先做完，然后才 mkdir(exist_ok=False)。
- **成败判定**：每个 arm 要同时满足 returncode == 0、book_smoke_summary.json 是本次运行生成的（mtime 晚于子进程启动），并且 extract 没有报错、cagr 和 mdd 都不为空。任何一个 arm 失败：summary 写 all_ok=false，写 VOID.md，退出码 1，整轮数值不得引用。没有 summary.json 的运行同样记为 VOID，手写 VOID.md。
- summary 记录父进程和子进程的峰值 RSS（上限 1.5GB）。跑完用 `find -newermt T0` 确认只有 out_dir 下的文件被写过。

## 4. 报告（60万、100万两档，改前和改后）
- **指标**：CAGR、MDD、Calmar、胜率（日、月）、行业上限触发次数（n_ind_cap_sessions_x2，指 X2 内 apply_ind_cap 实际削减权重的 session 数），以及 ind_cut_mean 和 max_ind_sleeve_share_after。
- **只作披露**：
  - 受改分类影响的持仓日占比：X2 内 (session, 持仓股票) 行中，as-of l1_name 与旧静态映射不同的占比，按行数和按权重各报一个（reclass_share_x2）；
  - 未知行业单独报：n_rows_asof_missing、n_rows_static_missing、n_rows_asof_missing_static_known（Arch 实测 X2 约 477 个代码日，约 1.4%），以及 n_unk_over_cap_sessions_x2（_UNK_ 桶单独超过 25% 的 session 数）；
  - 空档沿用：n_rows_gap_carry、share_rows_gap_carry（占 X2 持仓行的比例），n_rows_unknown，以及全表 n_reclass_gap_rows（以 summary.json 中代码算出的值为准；Arch c72f0856 按 prep_sw 口径预期为 1088。原写的“1545 次变更中有 1109 次 new in_date = old out_date + 1”是 r1 审查口径，仅供参考）；
  - 重叠：n_rows_multi_match、n_codes_overlap_on_d；
  - before 组与现有 output/strategy_hiliq/b4/B4_50_25_25_topN_{60w,100w}.parquet（ca77bc8c… / f75ace33…）对比 sha 和最大权重差。不作门槛。

## 5. 披露与限制
- sw_pit 表 built 是 10-14，按 R4 口径已 stale（落后 3 个交易日）。summary 带 industry_cap_on_stale_sw_pit=true 和 disclosure_zh，凡引用这次结果的报告，标题行都要带 disclosure_zh。
- **滞后阈值（Arch 2026-10-18 11:11 ET 裁定①，r3c 起；常量在 research/sw_members_asof.py）**：
  - legacy sw_pit 表（0b1d3432）：沿用 research/sw_pit_freshness.py 的 STALE_LAG_TDAYS = 3，lag_tdays ≥ 3 即 stale。
  - CLEAN 表（89d4afa3）：CLEAN_STALE_LAG_TDAYS = 10（Arch 11:11 ①，以及 11:13 / 11:20 两条补充裁定的合并理解，Arch 2026-10-18 11:28 ET 确认）：
    - lag_tdays ≤ 10：stale=False，stale_lag_only=False，滞后天数只写进 lag_notes；
    - lag_tdays > 10 且没有 coverage_gap：stale=True，stale_lag_only=True（summary 字段 sw_l1_stale_lag_only），写 disclosure_zh；
    - 有 coverage_gap：一律 stale=True，stale_lag_only=False。
  - 按 Data §14②（docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt，sha256 0a5a5197…77d2b），当前 lag = 5 个交易日（收盘覆盖日 20261009，截至 20261016），因此不算 stale，也不算 stale_lag_only。
  - 没有 manifest 描述的表一律置 stale=True。
  - stale 只影响披露（industry_cap_on_stale_sw_pit、disclosure_zh），不阻断运行。阈值改动须重新预注册。
- 结果只作披露：不调参，不据此改 B4 规则，不进纸面。如果要改规则，按 B4 规则流程走：主 Agent 裁定、Leo 决定、新的预注册，从 2026-11-02 起在 FWD 上测试。
- 导入 hx2 的脚本：
  - optimizer_core_x2_run.py 只 import run_smoke，而且那一行是死代码。run_smoke 现在会检查 returncode 和 summary 是否新鲜，判定更严，但不影响它。
  - strategy_capadv_topn_tie_sensitivity.py 和 strategy_b4_hiliq_leg_review.py 仍走 load_industry_map()（原样保留）加 apply_ind_cap(dict)，签名和行为都不变，所以仍带前视偏差。两份结果文档已加“行业映射存在前视，待修”的提示行，修复单独出 diff，等本次 B 对照有结果后再交。
  - tie-sens 如果要重跑，需要重新做预注册（dep_hx2_sha256 已过期）；凡钉过 hx2 sha 的 .ok 都要重签。
- hx2 main() 默认改用 as-of 映射，但本次不授权重跑 hx2 main。
