# Core v1.4 runner 改动对照（LOTFIX v1.4 + AMEND-1 r2.1）

- 起草：QuantLab Strategy，2026-10-18 ET。live=false，promotion=false。
- **只写了代码，没有执行任何东西。** 唯一跑过的是 `/workspace/qlvenv/bin/python -m py_compile`（两个新文件都通过）。没有 import 检查、smoke、dry-run、pytest 或小样本；没有创建任何 .ok；没有碰 TEAM_STATE、ql_bus、`output/strategy_hiliq/`、并列敏感性脚本、`strategy_hiliq_capadv_b4_x2.py`，也没有碰 v1.3 runner 和 v1.3 产物。
- 本文引用的行号，全部以下列文件 sha 为准（Arch R3）：
  - `research/optimizer_core_x2_run_v1_4.py` = **db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602**（下文写作 R@db8bdb8e）
  - `research/v1_4_snapshot_equiv_check.py` = **3d2e05333df033329b03012d99d939fa2c69736be27820198234dccf7d67a1b3**（下文写作 E@3d2e0533）
- 一起计入 combined sha、但未修改的依赖：`research/optimizer_core_v1_1.py` b500c21b…067e、`research/optimizer_lambda_calib_sealed.py` 875daca9…9c。

## 1. 开工前核对（全部一致）

| 文件 | 期望 sha256 | 实测 |
|---|---|---|
| research/optimizer_core_x2_run.py（v1.3 现行，未改） | b623825457efb2a3ce22c450d12e87624dc8f5642ad310e4ecc869362c64cbb4 | 一致 |
| docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md（LOTFIX v1.4 冻结） | d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425 | 一致 |
| docs/v2/STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md（停跑规则冻结） | 41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b | 一致 |
| docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md（AMEND-1 r2.1） | 0029672aed3d9e6a70409e25b02de16291caf5bafbc5c8d8b93624e16719f009 | 一致（就在原路径） |

三份文档的 sha 写死在 runner 里（R@db8bdb8e 第 33–37 行），启动时复核，并且要与 .ok 里的字段一致（第 159–162 行）。

## 2. 与 v1.3 runner 的关系

- 先把 b6238254 原样复制成 `research/optimizer_core_x2_run_v1_4.py`，再在新文件上改写。v1.3 runner 一个字节都没动。
- 保留并沿用 b6238254 的逻辑：`frozen_lambdas`（R 第 90–96 行，λ_risk 117.21317483995702、λ_turn 0.6/0.6 校验不变）、`sessions` / `rebal_days`（第 105–111 行，`month_end_plus_first_last`）、调仓日 PIT 收盘价（往前看 ≤10 个自然日、取最后一笔，第 790–794 行）、结构化 .ok 解析方式（第 125–145 行）、按日展开的权重文件 schema（第 962–982 行）。
- 删掉了 v0/v1.1/v1.2/v1.3 分支和 smoke 路径：v1.4 没有 smoke 模式，.ok 里 `allow_smoke=true` 也会被拒（第 154–155 行）。
- 求解器：`_solve_support_v14`（第 253–298 行）是 `optimizer_core_v1_1._solve_support` 的拷贝，按 v1.3 的设置写死 POOL_STD=True、IND_POOL=True。**唯一改动是把标量单票上限 `w <= cap` 换成逐票向量 `w <= capv`**（第 278、282 行）。目标函数、λ、行业/Size/MidCap/β 约束、Neff、2% 下限、Clarabel→OSQP 顺序都没变。slack 阶梯 `_solve_with_slack_v14`（第 301–308 行）与 v1.3 相同。
- `optimizer_core_v1_1.py` 和 `optimizer_lambda_calib_sealed.py` 只读引用，没有改（改了会打破 v1.3 的 combined sha）。

## 3. 逐条映射（行号 = R@db8bdb8e）

| 规格条目 | 实现 | 行号 |
|---|---|---|
| §1 常量不变：λ、单票上限 6%/5%、行业 ±8%（+slack ≤1pp）/≤20%、Size/MidCap ±0.35σ（+0.05σ）、β ±0.10、20–30 名、2% 下限、现金 2% | 全部引用 C / V 的原常量；λ 读 calib 文件并校验 | 41–49, 90–96, 253–298 |
| §1 基准不随预筛变化（Beta L2）：wb、bb、Size/MidCap 标准化与 zb/mb、行业 wb 都在完整池上算 | `tier_context` 中 pool = `D["alpha"].index`；`V.style_ctx(D,0,0)` 与 `V.pool_ind_bench(D)` 都用完整池；求解器内基准也用完整池（第 270–276 行）；预筛只改候选集和逐票上限 | 218–249, 270–276 |
| §1 两袖共用一个解、任一袖整手失败两袖同沿用 | 采用条件要求两袖硬约束都过（`hard_both`/`strict_both`）；失败日两袖同时沿用 | 523–525, 562–576, 869–877 |
| §2 L_i（688/689=200）、P_i（PIT）、u_i=L·P/A、ε=1e-6 手 | `C.lot_round_rule`；第 790–794 行取价；`EPS_LOT` | 43, 222–231, 790–794 |
| §3.1 S1：m = floor(c_A·B_s·A/(L·P)+ε)；cap^{s,lot}=m·u；求解器上限 cap^{lot}=min_s cap^{s,lot}/B_s | `lot_cap_lots`；`caps_nav`、`cap_lot`；向量上限进入求解器 | 209–215, 228–232, 278, 282 |
| §3.1 P2-5：候选集内 cap^{lot} > c_A/2 且 ≤ c_A | 不变量检查，不成立就 raise（是 bug，不是数据问题） | 233–235 |
| §3.1 P3-1：ε 版和无 ε 版择一写死 | 保守混合：默认用 +ε；如果 +ε 让 m·u 超过 T 超过相对 1e-9，就对该票改用无 ε 的 m（**待裁定 D1**） | 44, 209–215 |
| §3.2 取整：q = floor(x·A/(L·P)+ε)·L，x = B_s·w | 同式；另加一道不超过 m 手的夹紧，次数计入 `clamp_count` 并披露（**D2**） | 362–370 |
| §3.2 修复/补手的加仓条件 q_i + L_i ≤ m_i·L_i | 风格修复：`okcap`；补手：手数判断 | 421–422, 468 |
| §4.1 整手阶段失败 = LOT_HARD_FAIL（名数 / 行业上下界与绝对值 / Size / MidCap / β，按口径 C，含所用 slack）或 LOT_CASH_GT2 | `hard_eval(…, "C", slack)` 只在终态上判定；现金 >2% 另记 | 340–353, 520 |
| §4.1 P1-1：现金触发会改变持仓，但不改失败日的判定 | `s3_trigger="cash"` 会进 S3；停跑计数只看 INFEASIBLE / LOT_HARD_FAIL | 565, 51, 1008 |
| §4.1(3) 只因现金升 K 的日子：天数、ΔK、两种换手，以 K_sel 那次为对照 | `core_v1_4_s3_cash_days.csv`：k_final−K_sel、one_way_solver / one_way_lot 与 *_ksel 对照，直接取自 attempt，不另做求解 | 922–925, 955 |
| §4.2 步长 +1、只向上、K_max=30、去掉当日求解已证实不可行的 K、最多 (30−K_sel) 个 K、每个 K 走原 slack 阶梯、支撑集取 step-1 \|w\| 降序前 K 名 | `retry` 列表；`bad_K`；`order` 不重做 step-1 | 549–566 |
| §4.3 降级序 1–5 | ①原 K 循环（cap→cap_lot）→ ②K_sel 严格 OK 就采用 → ③S3 采用第一个严格 OK 的 K → ④否则在试过的 K（含 K_sel）里取最小的两袖硬约束都过的 K，记 LOT_CASH_GT2 → ⑤都不过则 LOT_HARD_FAIL，沿用（首日全现金） | 538–576 |
| §4.3(6) β 0.15 不作可行判定，只做影子 | `core_v1_4_beta15_shadow.csv`，只对已有尝试的整手结果判定，不另求解 | 830–835 |
| §4.3(7) 不实现「Full 域预算」和「权益降仓到现金」 | 未实现，如实写明 | — |
| §4.4 S3 救回日分两类计数 | `s3_rescued_from_hard`、`s3_rescued_from_cash` | 878–879 |
| §4.4 救回日在「不救回时的失败段」中的位置（段首/段中/段尾/孤立）；不救回时 k=3 是否触发；现金救回日在 M3「失败或现金>2%」段中的位置 | `rescue_positions` | 1041–1061 |
| §4.4 K_sel/k_final 分布、Neff（求解与整手各一份）、k_trace、k_final、s3_used、s3_trigger、换手与 Neff 变化 | disclosure 列 + `k_neff` 汇总 | 712–717, 870, 900–916, 1074–1083 |
| §4.4 P2-4 失败按阶段拆分（solve / lot），都计入停跑 | `fail_stage`；停跑评估里给出 n_fail_solve / n_fail_lot | 547–548, 560–561, 576, 1025–1026 |
| §5 S5：门槛 T_{A,s}=c_A·B_s·A；共用候选集按 ② 剔除；无价格不剔除、记 no_price | `ex`、`in_cand`、`prefilter` ∈ {none, sleeve2_only, both, no_price} | 222–241 |
| §5 只因 ② 被剔的票单列；P2-3 披露 1–3 项（v1.3 ① 中被持有的票及权重、申万一级分布与 wb 加权 β/Size/MidCap、占全池 wb 比例） | `core_v1_4_prefilter_names.csv`（含 `v13_eq100_weight`，只读 v1.3 ① 产物，sha 记入 summary）；daily_bench 的 `wb_*_prefiltered` | 698–709, 839–867 |
| §6.1 口径 C：求解、修复、补手、终判四处统一 | 求解器在股票簿上约束（取整前即 C）；`lot_round_v14` 的 `excC` 用 E=Σx·v/B_s−v_b；终判 `hard_eval(…,"C")`；行业按 B_s 归一（与 v1.3 代码一致） | 312–353, 384–386, 520 |
| §6.1 口径 A/B 只披露 | `book_exposures` 三种口径都算；style/industry 明细都写 A/B/C | 312–337, 744–768 |
| §6.2 40% 换手只监控 | `turn_solver_gt40` / `turn_lot_gt40`，按 s3_used 分组计数，不设约束 | 48, 918–919, 1084–1088 |
| §7.1 attempt_weights（键、solver_status、slack、instrument、w_solver、cap_lot、lot/price/u、sleeve、q_floor/q_final（手）、x_lot、at_cap_lot、selected、beta_i、size_z_i、midcap_m_i、sw_l1、s3_trigger） | `ATT_SCHEMA` + 逐票行；求解不可行的尝试写一行 sleeve=SOLVER | 580–585, 808–826 |
| §7.2 style_components（solver/post_floor/post_repair/final × A/B/C） | `style_rows` | 718–719, 744–753, 827–829 |
| §7.3 industry_detail（含无入选票的行业） | `ind_rows`，行业集合 = 持有行业 ∪ 全池行业 | 720, 756–768 |
| §7.4 repair_trace.jsonl（每步一行 + 每个 phase 的 stop_reason：excess_zero / no_candidate / cash_le_2pct / iter_cap_300 / cap_lot_block） | `tr(...)`；cap_lot_block = 除上限外其他条件都满足的候选只被上限挡住 | 388–389, 399–400, 411–447, 449–477 |
| §7.5 beta15_shadow | 见上 | 721, 830–835 |
| §7.6 daily_bench（bb、zb、mb、标准化参数、β 窗、pool_n、n_prefilter、n_prefilter_sleeve2_only、wb_share/beta/size_prefiltered、caplot_cut_sum、corr_cut_*） | 字段齐全；另加 `*_support` 一组（Beta L3 用的是支撑集），以及 n_at_cap_lot_support、sum_caplot_support | 722–725, 837–862 |
| §7.6 carry_exposure（沿用日实际持有的那本书 × A/B/C） | `day["carry"]` | 726–727, 888–899 |
| §7.7 lot_fail_reason 多值枚举 + cash_gt2 + fail_stage、k_trace、s3_used、s3_trigger、k_final、两类救回、neff_solver、neff_lot、n_prefilter_sleeve2_only | disclosure 列 | 712–717, 900–920 |
| §8 门槛（X2、口径 C 严格、含耦合；100万 任一袖 <80% 或 X2 上 k=3 触发 → 仍不可行）；同时报 60万；60万 也 <80% 时提示「不能只归因于 5%」 | `post_run_disclosures` 的 `s8`；`n < 29` 时标 `n_days_equals_29=false` | 1089–1101 |
| §10 第 6 条 新 ckpt 目录必须为空，不复用 `_ckpt_v1_3_poolind/` | 输出目录固定为 `core_x2/v1_4/`，ckpt 在 `v1_4/_ckpt_v1_4/`；目录非空就拒跑；不支持续跑 | 25–28, 174–189, 777 |
| 停跑规则 §2（k=3 连续失败、调仓日序列、无数据日跳过不重置；单月 ≥2 失败日并集）、M3、M4（按档同停）、M5（连续 ≥2 无数据日上报）、M6（滚动 6 期 ≥3 只披露） | `stop_rule_eval`：全样本和 X2-only 各算一次。**本次研究运行只评估、不改任何决策**（**D5**） | 985–1038 |
| 运行门禁：ARCH_RUN_AUTH_v1_4.ok，缺失或 sha 不符拒跑 | `parse_run_auth_v14` / `enforce_run_auth_v14` / `preflight`；另要求 `--auth-sha256` 等于 .ok 的 sha | 121–206, 1136, 1141 |
| 统一异常处理（Arch P2-r2-1）：没有 summary 就自动写 VOID.md | `main` 中 try/except BaseException；SIGTERM/SIGHUP/SIGINT 转成异常；summary 先写 tmp 再原子替换 | 1105–1114, 1127–1128, 1131–1181 |
| AMEND-1 内存：分日追加写，单进程 RSS ≤1.5GB | ParquetWriter / CSV 都按日追加；RSS 超限即 raise→VOID（**D16**） | 594–618, 933–950 |

## 4. AMEND-1 r2.1 实现（行号 = R@db8bdb8e）

| 要求 | 实现 | 行号 |
|---|---|---|
| §1 每个调仓日 × 档 × 袖，完整候选池每只票一行；字段 date, tier, sleeve, code, in_candidate, price, lot_size, lots, u_i, beta, size_z, midcap_m, sw_l1, wb_i, q_cont, q_final, selected, stage, K_sel | `SNAP_SCHEMA` 含全部字段，另加 instrument、in_pool、cap_lot、cap_lot_sleeve、m_lots、exposure_filled、k_final、prefilter | 586–591, 628–661 |
| A1 池范围包括 S5 剔除和 cap_lot=0 的票；每天每档校验 Σwb_i=1、Σwb_i·β_i=bb，不过就 raise | 遍历 `ctx["pool"]` 全体；校验容差 1e-9 | 634–647, 663–667 |
| A2 bb/zb/mb 与标准化参数取 daily_bench；z/m/β 计算窗口与求解完全一致 | 快照和 daily_bench 用同一个 `ctx["sty"]`（`V.style_ctx`，与求解器同公式、同 `D`） | 243, 847–849 |
| A3 每天每档每袖各一行 CASH（β=0）和 sh.510300（β=当天实际使用的 bb），记 q_final 与 beta | 第 652–661 行 | 652–661 |
| A3 校验 Σq_final=1，且 Σq_final·β = disclosure 组合 β（1e-6），不过就 raise | 与 disclosure 的 `beta_port`（第 326 行独立算出）比较 | 668–680 |
| A4 β 等暴露缺失写 NaN，不写 0 | β 取原始 `D["betas"]`；ln_mcap 缺失时 size_z/midcap_m 写 NaN，`exposure_filled=true` 标出求解器实际用的是填补值 | 638–644 |
| §2 selected 覆盖所有 q_final>0（含修复阶段新加入的票） | selected = q_final>0；另做两道覆盖检查。注：v1.3/v1.4 的修复只在支撑集内加减手，不会引入支撑集外的票；沿用日持有、但已不在当日池里的票另写一行（in_pool=false） | 646, 647–651, 671–677 |
| 开关、只写盘 | `--pool-snapshot on|off`（第 1134 行）；正式全量必须 on（第 182–183 行），off 只用于等价性检验 | 1134, 182–183, 926–928, 942–943 |
| 逐位一致证明 | `research/v1_4_snapshot_equiv_check.py`（E@3d2e0533），见 §5 | — |

### 4.1 AMEND-1 没有改动任何决策路径（单列说明）

1. **调用位置在决策之后。** `build_pool_snapshot` 只在第 926–928 行调用，此时当天当档的采用 / 沿用、`held`、`prev_w`、disclosure 行都已确定（第 871–921 行）。
2. **只读入参。** 传入的 `hb`、`ad["w"]`、`ctx`、`D`、`e["beta_port"]` 只做读取（`Series.get`、`reindex` 都返回新对象）。函数内部新建字典列表，不写任何共享状态。
3. **返回值只流向快照文件。** 返回的行只追加到 `day["snap"]`，而 `day["snap"]` 只在第 942–943 行交给快照写入器，没有其他任何读取者。
4. **关闭时根本不调用。** `--pool-snapshot off` 时第 926 行和第 942 行的分支都不进入，快照代码完全不执行。所以「开 / 关」的差别，正好就是「执行快照代码 / 不执行」，等价性检验能直接证明它没有副作用。
5. **汇总不含快照信息。** 快照文件、快照 manifest 和 `run_runtime.json` 列在 `EXCLUDED_FROM_EQUIV` 里（第 53 行），不进 summary 的 `outputs_sha256`（第 1117–1124 行）。summary 里也不写开关状态和运行模式（它们写进 run_runtime.json），所以开 / 关两次的 summary.json 应当逐字节相同。
6. **唯一的差异是失败方式。** 快照校验不过会 raise，整次作废。这只会让「开」的那次作废，不会让它产出不同的内容。

## 5. 等价性检验脚本（E@3d2e0533）

- 门禁与 runner 相同：复核三份文档 sha，`enforce_run_auth_v14(..., "equiv", ...)` 要求 `allow_equiv_check=true`，且 `equiv_script_sha256` 等于本脚本的 sha。另外要求 `--auth-sha256`，并要求 `core_x2/v1_4_equiv/` 不存在或为空（E 第 40–51 行）。
- 两次子运行依次进行，不并行：`--mode equiv --pool-snapshot on` 写到 `v1_4_equiv/snap_on/`，`off` 写到 `v1_4_equiv/snap_off/`。子进程环境固定 PYTHONHASHSEED=0、OMP/OPENBLAS/MKL 线程数 1（E 第 25、53–65 行）。
- 比对：两目录除排除项（快照、快照 manifest、run_runtime.json、*.log、*.tmp）之外的全部文件逐个算 sha256，文件集合和 sha 都必须一致。还要求「开」那次有快照、「关」那次没有，且快照 schema 等于 `SNAP_SCHEMA`（E 第 68–91 行；只读 parquet 的元数据 schema，不读数据）。
- 结果写进 `v1_4_equiv/equiv_report.json`，verdict 为 PASS 或 FAIL；FAIL 时退出码为 2。任何一次子运行失败、或没写出报告，都写 `v1_4_equiv/VOID.md`（E 第 94–99、109–139 行）。收到 SIGTERM 时，先把信号转给子进程（子进程会自己写 VOID），然后作废（E 第 102–106 行）。

## 6. ARCH_RUN_AUTH_v1_4.ok 字段规范（供 Arch 写；Strategy 不创建）

路径 `output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_v1_4.ok`。解析规则与 v1.3 相同：只认 `^key=value$` 行，重复键、缺字段或值不合法都拒跑。`RUN_AUTH_FORMAT.md` 目前只写了 v1_3，我没改它；v1.4 的规范暂写在这里，是否并入由 Arch 定。

| key | 值 | 规则 |
|---|---|---|
| format | quantlab_run_auth_v1 | 精确 |
| version | v1_4 | 精确 |
| signed_by | arch | 不区分大小写 |
| signed_et | 例如 2026-10-18 hh:mm ET | 非空 |
| allow_full | true/false | 正式全量需 true |
| allow_smoke | false | v1.4 没有 smoke 模式，为 true 一律拒 |
| allow_equiv_check | true/false | 等价性检验需 true |
| runner_sha256 | 64 位 hex | = sha256(research/optimizer_core_x2_run_v1_4.py) |
| combined_sha256 | 64 位 hex | = sha256("research/optimizer_core_x2_run_v1_4.py=<sha>\nresearch/optimizer_core_v1_1.py=<sha>\nresearch/optimizer_lambda_calib_sealed.py=<sha>\n") |
| equiv_script_sha256 | 64 位 hex | = sha256(research/v1_4_snapshot_equiv_check.py)，mode=equiv 时核对 |
| lotfix_sha256 / stoprule_sha256 / amend_sha256 | d921dd3f… / 41f29825… / 0029672a… | 必须与写死值和当前文件 sha 三方一致 |

按当前文件算，combined_sha256 应为下式的 sha256（由 Arch 独立复算）：
`research/optimizer_core_x2_run_v1_4.py=db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602\nresearch/optimizer_core_v1_1.py=b500c21bca955ea8c8667808f412e734a5c70dae9b20823e5b890d6a5938067e\nresearch/optimizer_lambda_calib_sealed.py=875daca9cfbb861cdf685a9f7ff836f1dc18fa80eccf2cf238baccaaf40d3b9c\n`

启动命令：**r1 的 qlvenv 命令已作废（Arch P2-2 / P3-7）**，现行命令见 §r2.8（`.venv_opt/bin/python` + DETERMINISM_ENV；先 equiv，PASS 后才 full）。字段规范的 r2 增补见 §r2.1。
**日志必须写在输出目录之外**：nohup 会在 Python 启动前先建日志文件，写进 `v1_4/` 会让「目录必须为空」的检查拒跑。

## 7. 产出（v1_4/ 目录内）

summary.json（最后写，含其他产出的 sha）、core_v1_4_disclosure.csv、core_v1_4_disclosure_counts.json（停跑评估、救回位置、K/Neff、换手、§8）、core_v1_4_attempt_weights.parquet、core_v1_4_style_components.csv、core_v1_4_industry_detail.csv、core_v1_4_repair_trace.jsonl、core_v1_4_beta15_shadow.csv、core_v1_4_daily_bench.csv、core_v1_4_carry_exposure.csv、core_v1_4_prefilter_names.csv、core_v1_4_s3_cash_days.csv、core_{equity_100,equity80_etf20_510300}_{60w,100w}.parquet、_ckpt_v1_4/*.pkl；快照开时还有 core_v1_4_pool_snapshot.parquet 和 manifest；另有 run_runtime.json（用时、峰值 RSS、模式，不参与比对）；作废时有 VOID.md。不计算收益。

## 8. 已知风险

1. **代码完全没有执行过。** py_compile 只查语法，不能发现运行时错误（例如字段名、类型、pyarrow 转换）。v1.4 规格不允许 smoke，所以正式运行就是第一次执行：任何运行时错误都会触发统一处理、写 VOID，并消耗那张 .ok。建议 Arch 审查时重点看第 503–576 行（尝试与 S3）、第 776–959 行（主循环）和第 628–681 行（快照校验）。是否另开一个受 .ok 约束的静态单测或 mock 测试通道，由 Arch 决定。
2. **逐位一致依赖确定性。** Clarabel/OSQP 在不同线程数下可能有最后几位的差异。等价性脚本给两次子运行固定了单线程和 PYTHONHASHSEED，正式全量没有固定，所以正式全量和等价性检验那两次之间不保证逐位相同，也不要求相同。pyarrow 版本不同也会改变 parquet 字节。
3. **耗时。** S3 每档每天最多再加 30 次求解，100万 预计 S3 很频繁。等价性检验又要跑两次全样本，总耗时约为一次正式全量的 3 倍。
4. **体积。** industry_detail.csv 是 尝试数 × 2 袖 × 4 阶段 × 3 口径 × 约 31 个行业，预计几十万行以上。已按日追加写，内存不累积，但文件较大。
5. 求解器解出后先 clip 再归一化，权重可能比 cap_lot 高约 1e-9。取整时的 ε 和夹紧（第 368–369 行）能保证不多取一手。
6. 在 `core_x2/` 下新建 `v1_4/` 和 `v1_4_equiv/` 两个目录，不会写入 v1.3 的任何产物。§5 第 1 项只读 v1.3 的 `core_equity_100_{60w,100w}.parquet`，读入时记 sha。

## 9. 待 Arch 裁定点

- **D1 S1 的 ε。** 采用保守混合：默认按 floor(T/u'+ε)；如果这样多取的那一手让 m·u' > T·(1+1e-9)，就对该票退回无 ε 的 m。等于只用 ε 吸收浮点误差，真正落在 [m−ε, m) 区间的票不多取。要不要改成纯 ε 版或纯无 ε 版？
- **D2 取整夹紧。** 取整后的手数再夹到 ≤m，夹紧次数计入 clamp_count。
- **D3 无价格的票。** 沿用 v1.3：不剔除、不取整、上限 c_A。和 v1.3 不同的一点：它们的权重以常数偏移计入修复和补手里的风格、行业、名数和现金（v1.3 修复时忽略它们，只在终判里计入）。
- **D4「完整 HI_LIQ 池」的范围。** 实现为 prepare_day 数据过滤后的求解池 `D["alpha"].index`，wb 正好在这个池上归一到 1，A1 的 Σwb=1 才成立。掩码里有、但因收益数据不足被 prepare_day 剔掉的票，不在快照里。
- **D5 停跑规则。** 在这次 X2/sealed 研究运行里**只评估、不真的停**：照常求解后面的日子，否则 §8 的 29 天可行率没法算。§8 的 k=3 判定用「从 X2 首日开始计数」的序列，全样本序列另报一份。
- **D6 S3 字段口径。** s3_used = 进入了 S3（K_sel 不严格 OK）。s3_rescued_from_cash 要求最终采用的 K > K_sel 且严格 OK。现金触发但没找到严格 OK 的 K 时，回退采用 K_sel，不算救回。
- **D7 A3 的「每种口径」。** 按袖（①/②）理解。组合 β 取 NAV 层：Σx_i·β_i + 0.2·bb + 现金·0。沿用日持有、但已不在当日池的票 β 记 NaN，不计入，这和 v1.3 exposure_drift 的处理一致。
- **D8 510300 的 β。** 取 bb（全池 wb 加权 β），与 v1.3 口径 A 的处理一致。
- **D9 q_cont 的定义。** 采用日为 NAV 层的 B_s·w；沿用日为 NaN（当天没有被采用的连续解，K_sel 的连续解在 attempt_weights 里有）；CASH 行为 NaN；510300 行在 ② 为 0.2、在 ① 为 0。
- **D10 同名字段单位不同。** 快照的 q_final 按 AMEND 是 NAV 权重；attempt_weights 的 q_floor/q_final 按 LOTFIX §7.1 是手数。各按原文实现，这里写明。
- **D11 u_i 列。** AMEND 写的是「u_i(上限)」，有歧义。u_i 按 LOTFIX §2 写 L·P/A，上限另列 cap_lot（求解层）和 cap_lot_sleeve（m·u，NAV 层）。
- **D12 attempt 编号。** step-1 不算 attempt（其状态记在 step1_status）。求解阶段不可行的 K 也编号落盘，写一行 sleeve=SOLVER。
- **D13 caplot_cut_sum 和 corr_cut_* 的样本。** §7.6 的同名字段按候选集算；Beta L3 用的是支撑集，另列 *_support 一组。
- **D14 β 窗口起止。** 按 SSE 日历取 ≤调仓日的最后 L_BETA=60 个交易日推出，不是从 prepare_day 内部的收益行直接取（D 里没有返回日期）。
- **D15 硬约束判定容差。** 逐分量 1e-6，按归一化后的单位。v1.3 的整手标志用的是风格超出量之和 >1e-6，以及 NAV 单位下的行业容差，两者量级相同、略有差别。
- **D16 RSS 超 1.5GB。** 立即 raise，整次作废（保守做法）。
- **D17 新增门禁。** 启动时校验 HI_LIQ 掩码 sha = C.MASK_SHA_EXPECT；`--auth-sha256` 为必填。
- **D18 等价性检验的方式。** 独立跑两次全样本（约 2 倍耗时）。另一种做法是拿正式全量（开）和一次关的运行配对，可以省一次。选哪种？
- **D19 口径 A 的行业项。** 按 v1.3 整手检查的代码口径写（按 B_s 归一，与 C 相同）。v1.3 disclosure 里的 ind_active_max 用的是按股票合计归一，相当于口径 B。
- **D20 LOT_HARD_FAIL 日的 lot_fail_reason。** 取 K_sel 那次两袖原因的并集；每个 K 的原因在 k_trace 里。
- **D21 v1.3 按口径 C 重算（Beta L6）。** 不在这个 runner 里做，需要另行授权。
- **D22 v1.4 .ok 字段规范**（§6）是否并入 RUN_AUTH_FORMAT.md。

---

## r2 修改（按 Arch 审查 ARCH_V1_4_RUNNER_REVIEW_ZH.md db781708、CLARIFY-1 d075a2a6、自测规范 1aa43bdd）

- 起草：QuantLab Strategy，2026-10-18 约 02:01–02:14 ET（r2 快照登记 02:01 ET；提交 246aa99a 于 02:14:15 ET）。原写「约 02:05–02:30 ET」晚于提交时间，r3 按 Arch P3-6 更正。live=false，promotion=false。
- **只写了代码，没有执行任何东西。** 只跑过 `python -m py_compile`（`.venv_opt` 与 qlvenv 各一次，全部通过），以及用 `<python> -c` 读 Python/numpy/pyarrow 等的版本号（不 import 项目代码）、`sha256sum` 读输入文件 sha。没有 pytest、import、smoke、合成数据测试；没有建任何 .ok；没碰 TEAM_STATE、ql_bus、`output/strategy_hiliq/`、v1.3 runner b6238254 和任何冻结文档。
- 修改前快照（sha 全长、只读）：
  - `research/_runner_archive/optimizer_core_x2_run_v1_4.db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602.py`
  - `research/_runner_archive/v1_4_snapshot_equiv_check.3d2e05333df033329b03012d99d939fa2c69736be27820198234dccf7d67a1b3.py`
  - `docs/v2/audit/snapshots/STRATEGY_V1_4_RUNNER_CHANGES_ZH.d9767ef0c77014633fc892793a41232da90a106e7dd524fc718091ae9318c6fc.md`
  - 记录已追加到 `research/_runner_archive/MANIFEST.md`。
- **本节行号以下列 sha 为准：**
  - R = `research/optimizer_core_x2_run_v1_4.py` **3df05b4b85a3caec050810f1e4eac4035935ef6d7704b7a88df56d079e628b10**（下文 R@3df05b4b）
  - E = `research/v1_4_snapshot_equiv_check.py` **1380985102b598f16e111bf0b62cbc04e105aa00ad6cfeb3365bbf7ce711bf7a**（下文 E@13809851）
  - T = `research/tests_v1_4/test_v14_synthetic.py` **7176f97477b5f9aaf6b6aac8a9b53333a455c0f3e9441f65249a8834882195d3**（下文 T@7176f974）
  - combined_sha256（按 §6 公式，R + b500c21b… + 875daca9…）= **9e6d00c7f84c6d7e209de7d48bb577cba5624b21eca9a43e8c305d76b7c6c335**
- §1–§9 是 r1 的记录，行号仍指 R@db8bdb8e / E@3d2e0533，不改写；只把 §3 的「§10.6」改成「§10 第 6 条」（P3-7），§6 的 qlvenv 启动命令换成指向 §r2.8。

### r2.1 .ok 字段增补（Arch §7.1、P1-1、P1-2、P2-2、P3-4、D22）

在 §6 表格之外新增（全部必填，缺一拒跑；R@3df05b4b 第 164–168 行 `AUTH_REQUIRED_V14` / `AUTH_SHA_KEYS_V14`，解析在第 172–197 行）：

| key | 值 | 规则（R@3df05b4b 行号） |
|---|---|---|
| live | false | 必须恰好是小写 `false`（189–191） |
| promotion | false | 同上 |
| python_exe | /workspace/QuantLab/.venv_opt/bin/python | 绝对路径（194–195）；启动时与解释器比对（276–284） |
| out_dir | output/strategy_optimizer/core_x2/v1_4 | 等于代码常量 `OUT_FULL_REL`（33、208–209） |
| equiv_root | output/strategy_optimizer/core_x2/v1_4_equiv | 等于代码常量 `EQUIV_ROOT_REL`（34、210–211） |
| daily_basic_sha256 | 64 hex | 见 r2.2 |
| calendar_sha256 | 64 hex | 见 r2.2 |
| sw_members_sha256 | 64 hex | 见 r2.2 |
| calib_risk_sha256 | 64 hex | 见 r2.2 |
| calib_turn_60w_sha256 | 64 hex | 见 r2.2 |
| calib_turn_100w_sha256 | 64 hex | 见 r2.2 |
| dep_nontextbook_sha256 | 64 hex | 见 r2.2 |

全部 sha 键一律 64 位小写十六进制，不收前缀（196 行循环覆盖 `AUTH_SHA_KEYS_V14`）。是否并入 `core_x2/RUN_AUTH_FORMAT.md` 由 Arch 定（D22），我没改该文件。

### r2.2 七个输入 / 依赖（P1-2、D17 扩展）

路径取自 runner 实际读取的文件：`C.DAILY_BASIC`（prepare_day / load_daily_basic_window）、`C.CAL_PATH`（_open_days / month_ends）、`g1g5_nontextbook_weights.SW_MEMBERS`（C.load_sw_map → `_load_sw_members`）、`frozen_lambdas()` 读的三个 calib json，以及 C.load_sw_map import 的模块本身。代码常量 `DATA_INPUTS`（R@3df05b4b 第 76–84 行）；`check_input_paths()`（251–261）启动时断言它们与 C 里的常量是同一文件。当前 sha（2026-10-18 约 02:05 ET 实测，供 Arch 出 .ok 时参考；Strategy 不写 .ok）：

| .ok key | 路径 | 当前 sha256 |
|---|---|---|
| daily_basic_sha256 | data/v2/valuation/daily_basic_full_tushare.parquet（mtime 01:06:51 ET，快照恢复） | f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948 |
| calendar_sha256 | data/v2/calendar/trade_cal_sse_pit.parquet（mtime 01:13:35 ET） | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 |
| sw_members_sha256 | data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet（mtime 01:08:43 ET） | 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c |
| calib_risk_sha256 | output/strategy_optimizer/calib/calib_lambda_risk.json | 633c21ef0a44c557bb5619206f6086c6fce153bb4be6af8b2b88d24295620591 |
| calib_turn_60w_sha256 | output/strategy_optimizer/calib/calib_lambda_turn_60w.json | 56e75b458cd24b72abc92b6f43447e421773a7cfc90957ece6fba35d6884b0a4 |
| calib_turn_100w_sha256 | output/strategy_optimizer/calib/calib_lambda_turn_100w.json | 6cccfb7a177c7df312ac160edd5d114c4d75e972d211ab8caa00b805aa35e58a |
| dep_nontextbook_sha256 | research/g1g5_nontextbook_weights.py | 8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789 |

（HI_LIQ 掩码 c5433e80… 仍按 `C.MASK_SHA_EXPECT` 校验，不变。）与 Arch 审查 §1 的前缀全部一致。

### r2.3 逐条对应（行号 = R@3df05b4b / E@13809851）

| 审查意见 | 实现 | 行号 |
|---|---|---|
| **P1-1** live / promotion | 必填，恰好 `false`；enforce 再查一次 | R 164–166, 189–191, 206–207 |
| **P1-2** 数据输入与依赖钉 sha | `DATA_INPUTS` 7 键；`input_shas` / `check_inputs` 全长比对，enforce 与 preflight 都调；路径一致性 `check_input_paths`；运行结束、写 summary 之前再算一次，变了就 raise → VOID；summary 写 `inputs_sha256` | R 76–84, 212, 251–273, 356–358, 1394–1396, 1409 |
| P1-2（E 部分） | 两次子运行后复核输入 sha，与运行前和 .ok 都比；变了 → verdict=FAIL，写 `inputs_changed` | E 138–143, 145–149 |
| **P1-3** 前置执行通道 | 主 Agent E-2 已裁定合成单测算运行、走轻量 .ok：新增 T（见 r2.6）。T 不改 R，只 import R 的函数 | T 全文 |
| **P2-1 / E-1** §8 口径 | 按 CLARIFY-1（d075a2a6）改写：每档输出 `sleeve_A_strict_days`、`sleeve_B_strict_days`、`both_strict_same_day_days`、`denominator`=29、`daily` 逐日布尔明细；判定只用「两袖同日」，门槛 24/29（`S8_THRESHOLD`），80%、k=3 不变；分袖计数标 `disclosure_only_no_exemption`；输出不完整（分母≠29 或两袖日期集合不同）时 `judgeable=false`、判定为 null，不判定。旧的分袖块保留为披露。「口径待主 Agent 裁」的标注已删，改为引用 CLARIFY-1 | R 86–87, 1265–1307 |
| **P2-2** 解释器 | `.ok` 键 python_exe；`check_interpreter`：`realpath(sys.executable)==realpath(python_exe)`，另加 `sys.prefix` 与 venv 根一致（见 r2.9 第 2 点）；summary 写 `interpreter`（python + numpy/pandas/pyarrow/cvxpy/clarabel/osqp/scipy 版本） | R 85, 276–301, 355, 1410 |
| **P2-3 / D18** 顺序与环境 | `DETERMINISM_ENV` 唯一来源放在 R，E 直接引用同一对象；R 在任何模式下环境不符都拒跑；full 模式要求 `equiv_report.json` verdict=PASS，且 combined、auth_sha256、`inputs_sha256_after`、python_exe、determinism_env 都与本次相同，并要求 snap_on/summary.json 存在 | R 65–68, 287–291, 304–320, 350, 363；E 34, 55 |
| D18 ③ full 与 snap_on 比对 | full 跑完把 outputs_sha256 与 snap_on 的比对，写入 summary `d18_full_vs_snap_on`，标 `disclosure_only` / `not_a_void_condition` | R 1357–1366, 1419 |
| **P2-4** 防并发锁 | `acquire_lock`：在 `core_x2/` 下 O_CREAT\|O_EXCL 建锁（输出目录之外），内容为 pid、ET 时间、模式、auth sha、argv；代码从不删除；preflight 发现锁已存在即拒跑（须 Arch 归档）。锁名按模式分开：`.v1_4_run_full.lock`、`.v1_4_run_equiv_snap_on.lock`、`.v1_4_run_equiv_snap_off.lock`；E 自己另有 `.v1_4_equiv_check.lock` | R 69–72, 323–341, 362, 1381–1382；E 35, 61–64, 129 |
| **P2-5** FAIL 也用掉 .ok | E 文档字符串写明：FAIL（退出码 2）与 VOID（退出码 1）一样用掉 .ok，都须 Arch 重审、出新 .ok；报告里写 `fail_consumes_ok`；VOID.md 文案同步 | E 13–17, 112, 148 |
| E 子进程解释器 | 子进程命令用 `.ok` 里的 python_exe，不再用 sys.executable；E 自己也要过 `check_interpreter` | E 58, 68–70, 134 |
| **P3-1 / D1** 回退计数与 233 行上界 | `lot_cap_lots_ex` 返回 (m, reverted)；按日、按档、按袖计 `eps_revert_count`（daily_bench 两列、disclosure 一列、disclosure_counts / summary 汇总 `eps_revert_D1`）；r1 第 233 行上界改为 `cA*(1+STRICT_CAP_REL)+1e-12` | R 369–382, 387, 395–396, 402, 897, 1037–1038, 1098, 1311–1312, 1418 |
| **D2** clamp | clamp_count>0 的日子在 disclosure_counts / summary 汇总（`clamp_days_D2`，逐日列出），逐日值仍在 disclosure | R 1309–1310, 1418 |
| **P3-2** S5 与 S1 同一规则 | `ex = {sv: m[sv] == 0}`，即 S5 剔除 ⇔ m=0（同一容差） | R 397 |
| **P3-3** A3 同义反复 | manifest `a3_note` 写明 Σq_final=1 因 CASH 按残差必然成立，有信息的是 Σq·β 与 beta_port 核对 | R 1343–1355, 1398–1401 |
| **P3-4** out_dir 进 .ok | 见 r2.1 | R 33–38, 208–211 |
| **P3-5** 日内 RSS | `rss_guard` 在 step-1、每个 solve_loop / S3 attempt 之后、每日结束各采样一次，超 1536MB 即 raise → VOID；run_runtime 写每日 `rss_peak_intraday_mb`、`rss_samples`、`rss_peak_sampled_mb`（不进 summary，不影响逐位比对） | R 88–96, 714, 725, 740, 1124–1125, 1431 |
| **P3-6 / D4 / D10 / D14** manifest 与 mask_n | daily_bench 新增 `mask_n`（`C.load_pool(d)` 只读，掩码当日 in_universe 且去掉 HARD_EXCLUDE 的票数）、`n_dropped_by_prepare_day`=mask_n−pool_n；manifest 写单位（snapshot.q_final=NAV 权重，attempt_weights.q_*=手）、join 键（snapshot.tier ↔ daily_bench.aum）、pool 计数、β 窗口来源 | R 897, 960, 1035–1036, 1343–1355 |
| **P3-7** 文档引用与命令 | §3 改「§10 第 6 条」（代码注释同步）；§6 命令改指 §r2.8 | R 37, 246；本文 §3、§6 |
| D3 / D5 / D15 | 抄送主 Agent 知悉，无代码改动 | — |
| D21 | 不在本 runner 里做；独立脚本另交（见本文后续 D21 一节） | R 1306 |
| D22 | 字段规范由 Arch 并入 RUN_AUTH_FORMAT.md | — |

### r2.4 summary 新增字段（全部确定性，两次 equiv 应逐字节相同）

`clarify_1_sha256`、`inputs_sha256`（路径 + sha）、`interpreter`、`determinism_env`、`constants` 里加 `S8_DENOM`/`S8_THRESHOLD`/`RSS_LIMIT_MB`、`clamp_days_D2`、`eps_revert_D1`、`equiv_report_sha256`（equiv 模式为 null）、`d18_full_vs_snap_on`（equiv 模式为 null）。模式、锁文件、RSS、耗时只写 run_runtime.json（不参与比对）。R@3df05b4b 第 1405–1420 行。

### r2.5 E 的报告新增字段

`python_exe`、`interpreter`、`inputs_sha256_before`、`inputs_sha256_after`、`inputs_changed`、`fail_consumes_ok`（E@13809851 第 144–149 行）。R 的 full 前置检查读的就是 `inputs_sha256_after`、`python_exe`、`determinism_env`。

### r2.6 合成数据单测 T（E-2；只 py_compile，未运行；Arch 出 .ok 前不得运行）

- 文件 `research/tests_v1_4/test_v14_synthetic.py`（T@7176f974）。文件顶部第 36 行先调用 `ok_runner_pin.enforce(__file__, [OK_PATH], modes=["selftest"], deps=...)`（ok_runner_pin c7805d9a…），再在第 39–75 行做规范 §4/§9 要求的自查（scope=selftest、allow_selftest=true、allow_real_data 及其他所有 allow_* 显式 false、live/promotion=false、signed_et/expires_et 带时区且未过期、无 BOM、LF、out_dir 只能是 `mkdtemp` 或 `/tmp/<tag>` 且不在仓库内），之后第 100–105 行才 import numpy/pandas/pytest 和被测模块 R。
- 隔离：第 81–97 行 audit hook 拒绝打开 `data/`、`output/` 下任何文件和仓库内任何写入；第 114–116 行把 C.prepare_day / load_daily_basic_window / load_pool / load_sw_map / month_ends、R._open_days、R.load_v13_eq100 换成直接 raise 的函数。从不调用 R.main / run_v14 / preflight。所有写入只进 out_dir。
- 覆盖：lot_cap_lots 整除、浮点噪声、ε 回退、过贵 m=0；tier_context 的 S5=m0、cap_lot 上下界、no_price、基准不随预筛变化；build_pool_snapshot 通过与篡改 wb / beta_port / 现金时 raise；solve_tier 结构性断言（含 q ≤ m 手、w ≤ cap_lot、日内 RSS 已采样）；门禁反例（BOM、重复键、行内注释、缺 live、live=true、promotion=False、短 sha、缺 dep 键、相对 python_exe、错 version、文件缺失、allow_smoke=true、sha 不符、out_dir / equiv_root 不符）；确定性环境与解释器检查；out_dir 规则；O_EXCL 锁；Writers 的 parquet（含 None）/ CSV 追加 / jsonl；§8 CLARIFY-1 四种情形（分袖 29/23 → 同日 23 判不可行；两袖坏日错开 → 26/26/23；k=3 在同日 26 天时仍触发；缺一天 → 不判定）；停跑规则（无数据日不重置、M5 上报）；救回位置、clamp 与 eps 汇总；隔离自检；RSS < 1536MB。
- 需要 Arch 写的 .ok（路径建议 `output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_SELFTEST_v1_4.ok`，按规范 §2；Strategy 不创建）：
```
format=quantlab_run_auth_v1
signed_by=arch
signed_et=<带时区 ISO8601>
scope=selftest
runner_sha256_test_v14_synthetic=7176f97477b5f9aaf6b6aac8a9b53333a455c0f3e9441f65249a8834882195d3
dep_sha256_runner_v1_4=3df05b4b85a3caec050810f1e4eac4035935ef6d7704b7a88df56d079e628b10
dep_sha256_core_v1_1=b500c21bca955ea8c8667808f412e734a5c70dae9b20823e5b890d6a5938067e
dep_sha256_calib_sealed=875daca9cfbb861cdf685a9f7ff836f1dc18fa80eccf2cf238baccaaf40d3b9c
dep_sha256_ok_runner_pin=c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485
allow_selftest=true
allow_real_data=false
allow_dryrun=false
allow_full=false
allow_smoke=false
allow_diagnostic=false
allow_disclosure_only=false
allow_equiv_check=false
allow_mocktest=false
live=false
promotion=false
out_dir=mkdtemp
expires_et=<带时区 ISO8601>
```
- 将来的运行命令（规范 §5；串行，不与研究进程并发；.venv_opt 没有 pytest，所以用 qlvenv）：
```
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest research/tests_v1_4/test_v14_synthetic.py -q -p no:cacheprovider
```
  **box 上没有 `/usr/bin/time`（02:10 ET `ls` 实测；上次 tie-sens 作废就是因为套了 `time`），命令里不要套它。** 峰值 RSS 由 T 最后一条 `test_zz_rss_budget` 取本进程 ru_maxrss，写到 `<out_dir>/peak_rss_mb.txt`（超 1536MB 即失败）；清理前把它抄进回执。
- 清理（规范 §7）：`out_dir=mkdtemp` 时目录名为 `/tmp/v14_selftest_*`，跑完 `rm -rf /tmp/v14_selftest_*`；若 Arch 用 `/tmp/<tag>`，则 `rm -rf /tmp/<tag>`。再确认没有 `research/tests_v1_4/__pycache__`、`.pytest_cache`（`ls -a research/tests_v1_4/ /workspace/QuantLab/.pytest_cache 2>&1`），并把清理后的 `ls` 输出写进回执。
- T 的 .ok 在这次之后若 R 再改，dep_sha256_runner_v1_4 要跟着换。

### r2.7 解释器版本（`<python> -c` 只读版本号）

| | .venv_opt（v1.3 正式运行所用，v1.4 采用） | qlvenv（r1 文档误写的） |
|---|---|---|
| 路径 | /workspace/QuantLab/.venv_opt/bin/python → python3 → /usr/bin/python3.13（venv，sys.prefix=/workspace/QuantLab/.venv_opt） | /workspace/qlvenv/bin/python → uv cpython-3.12.14 |
| Python | 3.13.5 | 3.12.14 |
| numpy | 2.5.4 | 2.5.3 |
| pyarrow | 26.0.0 | 25.0.1 |
| pandas | 3.0.6 | 3.0.6 |
| cvxpy / clarabel / osqp / scipy | 1.9.3 / 0.11.1 / 1.1.3 / 1.18.1 | 1.9.3 / 0.11.1 / 1.1.3 / 1.18.1 |
| pytest | 无 | 9.1.1 |

### r2.8 完整启动命令（只在 Leo 定了 Core 继续、D21 回执经 Arch 审过、Arch 签了 v1.4 .ok 之后；CLARIFY-1 §4）

先 equiv，等 `v1_4_equiv/equiv_report.json` verdict=PASS（E 退出码 0）之后才跑 full。环境变量用 bash 的前缀赋值写法，不另套 `env`、`time` 等外部程序；日志写在输出目录之外。
```
cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup /workspace/QuantLab/.venv_opt/bin/python research/v1_4_snapshot_equiv_check.py --auth-sha256 <ARCH_RUN_AUTH_v1_4.ok 的 sha> > output/strategy_optimizer/core_x2/v1_4_equiv_run.log 2>&1 &

# equiv PASS 之后：
cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_x2_run_v1_4.py --mode full --auth-sha256 <同一 .ok 的 sha> > output/strategy_optimizer/core_x2/v1_4_run.log 2>&1 &
```
同一张 .ok 需 `allow_equiv_check=true`、`allow_full=true`。

### r2.9 仍需 Arch 裁定 / 知悉的点

1. **nontextbook 的 import 闭包没钉。** `g1g5_nontextbook_weights.py` 在模块顶层 import `quantlab/intel/debate_ledger.py`（8e388df9…）、`research/ai_debate_memory_runner.py`（e1736d80…，**目前工作区有未提交改动 +21 行，不是 Strategy 改的**）、`research/g1g5_wiring.py`（ff510148…）、`research/g1g5_expand_g6.py`（b2d26c0d…），它们还会再 import 别的。按 Arch 指定只钉了 7 个键；要不要再钉这几个（或改为钉整个闭包的 combined sha），请裁定。
2. **解释器比对。** `.venv_opt/bin/python` 是指向 `/usr/bin/python3` 的软链，所以 `realpath(sys.executable)==realpath(python_exe)` 无法区分 venv 和裸系统解释器（`/usr/bin/python3` 也会通过）。我另加了「python_exe 的上两级目录有 pyvenv.cfg 时，sys.prefix 必须等于该目录」（R 280–284）。请确认这条加严可以接受。
3. **§8 的 NO_DATA 日。** 我把 X2 上的 NO_DATA_CARRY 日留在分母 29 里、记为「不严格」（保守，只会更早触发），并单列 `n_no_data_days`；r1 是把它们剔除在外。另外「100万 任一配置」我按「每档」理解（每档两袖）。请确认。
4. **锁文件命名与归档。** 锁按模式分 4 个（R 69–72、E 35），代码从不删除；equiv 之后跑 full 不受 equiv 锁影响，但任何模式重跑前都要 Arch 先归档对应的锁。
5. **运行中输入变化。** R 在写 summary 前复算 7 个输入 sha，变了就作废（VOID，用掉 .ok）；E 在两次子运行后复算，变了判 FAIL（同样用掉 .ok）。Data 抓数进程在跑，建议签 .ok 时与 Data 协调冻结这几个文件。
6. **mask_n 的读法。** 用 `C.load_pool(d)` 再读一次掩码（只读、掩码 sha 已钉）；HARD_EXCLUDE 的两只票不计入 mask_n。
7. **T 的 .ok 键。** T 自查要求 `allow_equiv_check`、`allow_mocktest` 也显式为 false（它们是 R 认识的 allow_*）。T 的部分断言是在没运行的情况下写的；首次运行若有失败，按「测试发现 bug → 改 R/T → 新 sha → Arch 重审」处理，不构成证据。
8. **D18 耗时。** 等价性两次 + 正式一次，约为一次的 3 倍；单线程环境下 S3 会更慢，耗时未知。

### r2.10 D21（E-3）

D21 是独立脚本，不在 v1.4 runner 里：`research/optimizer_core_v1_3_basisC_recalc_d21.py`（0a7d21835788fb847c88dee13d0b52fdfe65d6de88fdcce1fccfb8b87fd2ef8e），说明与门禁字段见 `docs/v2/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.md`。只 py_compile，未运行。

## r3 修改（按 Arch 复审 ARCH_V1_4_RUNNER_REVIEW_R2_ZH.md f9edf4a3 + 主 Agent CLARIFY-2 改向）

- 起草：QuantLab Strategy，2026-10-18 02:43 EDT（`date` 实测，写本节时）。live=false，promotion=false。**只写代码，没有运行**：只用 .venv_opt 和 qlvenv 跑过 `python -m py_compile`（4 个脚本都通过），没有 import 项目代码，没有建 .ok，没有碰 TEAM_STATE、ql_bus、output/strategy_hiliq/、b6238254、任何冻结文档、research/ai_debate_memory_runner.py。
- 修改前快照（只读，MANIFEST 已登记 02:32 EDT 条）：R 3df05b4b、E 13809851、T 7176f974、D21 0a7d2183（research/_runner_archive/）；本文档 e5b6d02d、D21 文档 8b7a29f0（docs/v2/audit/snapshots/）。
- 新 sha：R **94643e27741835d703440d64d906f4c130f4763a522412a058f5fbd879454ca0**；R combined（R + b500c21b + 875daca9）**7943d83b5740fddadd8e06472731ddbc4f22fadee316f568d034bbdcb197f3f0**；E **09dc431d2f90782e6aaa406bc4ca84e6e332d0db8395bd081a0f8520060b0bed**；T **2ef7277a1d2ae210bc66cfa176c330938f68b4c8023c6c870bda870e4206d966**；D21 **86c6f7bb5a04030a7970e59fa5074fd03c1ef8c2f1285153dc57e87509f2bc3c**；D21 combined（D21 + R + V + C）**497c151b2a281462fa60ae242f74659be53313c1ea92c7ccb0856987aad256d0**。下文行号 = R@94643e27 / E@09dc431d / T@2ef7277a / D@86c6f7bb。
- **T 字节已变**：Arch 已签的 selftest .ok 33ef1df9 钉的是 T 7176f974 和 R 3df05b4b，对新字节自动失效；要跑新 T 须 Arch 重审并签新 selftest .ok。

### r3.0 CLARIFY-2 与审查 P2-1 的关系（重要）
- 审查 f9edf4a3 的 P2-1（§7 裁定 3）要求「无数据日按冻结原文剔除；n_no_data>0 时 judgeable=false、needs_main_agent_ruling」。主 Agent 02:30 ET 改向：已裁定 CLARIFY-2，**推翻该 P2-1**。r3 按 CLARIFY-2 实现，未实现 judgeable=false / needs_main_agent_ruling。
- **CLARIFY-2 文件未找到**：按指示 `rg -l CLARIFY-2 docs/v2`（02:30、02:41 ET 两次）无结果，docs/v2 下没有 CLARIFY-2 文件；LOTFIX 冻结记录 0d47c52f 也没有追加。所以：
  - 本节按主 Agent 改向消息转述的内容实现，**无法引用 CLARIFY-2 的 sha**；
  - R 第 62–63 行 `CLARIFY2_REL`（按 CLARIFY-1 的命名推测为 docs/v2/LOTFIX_V1_4_FREEZE_RECORD_APPENDIX_CLARIFY_2_ZH.md，待确认）、`CLARIFY2_SHA256 = ""`；`check_clarify2`（284–293）在 sha 为空时拒绝启动（v1.4 两种模式、E、D21 都经它）。文件落盘后须改这两行 → R 新 sha → D21 combined 也变 → Arch 重审。
  - .ok 已预留必填键 `clarify2_sha256`。

### r3.1 逐条对应
| 审查项 | 改动 | 位置 |
|---|---|---|
| P2-1 → CLARIFY-2 §8 | 无数据日不剔除：记为「不可证可行」，留在分母 29；另列日期和原因（`not_provably_feasible_days`，NO_DATA_CARRY 或 disclosure 缺行）；门槛绝对：两袖同日严格 <24 → 升级；「有效日 80%」只作对照（`control_80pct_of_valid_days`）；有效日 <29 不阻断，`judgeable` 恒为 true 并披露 `valid_days_lt_29_disclosure`；有效日 <24 直接升级（`valid_days_lt_24_direct_escalation`）；k=3 不变；判定字段引用 CLARIFY-2（`basis`、`clarify_2_sha256`、`verdict_100w_reason`、`verdict_100w_action`）；不输出 judgeable=false / needs_main_agent_ruling | R 1418–1475 |
| P2-2 闭包 | 11 个文件逐个钉键（`dep_nontextbook_sha256` + 10 个 `nt_*`）；`PINNED_INPUTS` = 7 + 10 + 4；启动比对（check_inputs 378–383）；写 summary 前复核（end_of_run_recheck 385–400），并核对本进程实际加载的仓库内模块 ⊆ 代码文件 ∪ 闭包（loaded_project_modules 403–411），否则 VOID；summary 写 `nontextbook_closure.combined_sha256`（nt_closure_combined 372–375）和 `loaded_project_modules` | R 100–125、348–411、1579、1593–1594 |
| P2-2 ai_debate_memory_runner | 钉在工作区当前字节 e1736d80（sha256sum 实测，见 r3.3）；Strategy 未修改、未回退、未 git add | R 112 |
| P2-3 .ok 解析 | `parse_ok_strict`（217–242，R 与 D21 共用）：只接受空行、整行 # 注释、`^[a-z0-9_]+=value`；其他行（含缩进、大写键）拒；未知键拒（白名单 = 必填键集合，211）；BOM、CR、非 UTF-8、重复键、值首尾空白拒；`check_auth_times`（255–262）：signed_et、expires_et 必须带时区 ISO8601，signed_et 不得在未来，expires_et 必须晚于 signed_et，过期即拒；signed_by 必须恰为 arch | R 208–293；D 73–90 |
| P2-4 T 钩子 | Arrow 包装 28 个入口（ARROW_WRAPS 154–176：pq.read_table/read_pandas/ParquetFile/ParquetDataset/read_schema/read_metadata/ParquetWriter/write_table/write_to_dataset，pa.memory_map/create_memory_map/OSFile/input_stream/output_stream，pyarrow.dataset.dataset/write_dataset，feather read_table/read_feather/write_feather，csv read_csv/open_csv/write_csv/CSVWriter，json.read_json，ipc open_file/open_stream/new_file/new_stream），调用前按 realpath 查路径（含路径列表）；审计钩子全部改 realpath（102–110），并拦 os.mkdir/rename（含 os.replace、shutil.move）/remove（含 unlink）/rmdir/link/symlink/truncate/chmod/chown/utime、shutil.copyfile/copymode/copystat/copytree/rmtree/chown/make_archive/unpack_archive（_FS_EVENTS 116–120）；包装装在 import R 之前（195 < 204）；新增测试：入口全部包装 644、逐入口拒绝 652（参数化 28 项，读 data/ 和写仓库都拒）、路径列表 668、符号链接绕不过 realpath 675、仓库内文件系统改动全部拒 692（19 种）、OUT 内允许 709 | T 93–204、644–713 |
| 裁定 2 / P3-5 解释器 | pyvenv.cfg 必须存在（不再是「存在才查」）；sys.prefix 必须是该 venv；PYTHONPATH/PYTHONHOME/PYTHONSTARTUP/PYTHONUSERBASE 任一非空即拒；numpy/pandas/pyarrow/cvxpy 的 `__file__` realpath 必须在 sys.prefix 下；T 新增 fake venv（无 cfg）反例 463 | R 127–128、414–436 |
| 裁定 4 锁 | 不变（4 把 + D21），代码不删；归档按 Arch 的做法：移到 `core_x2/_archive_locks/<ET 时间>/`，记 sha 与内容，VOID/FAIL 后连同输出目录一起归档 | 文档 |
| 裁定 5 / P3-4 | 结束前复核 HI_LIQ 掩码（R end_of_run_recheck 393–394；D21 经同一函数；E 143 也复核） | R 385–400；E 143 |
| 裁定 6 D21 | 见 D21 文档 r3：主结果 = §8 基线（持仓沿口径 A 决策，只按 C 重判标签）；第二披露列 = 按 C 决策；可引用标准写进代码（VALID / VALID_WITH_DISCLOSURE），引用 CLARIFY-2 | D 155–213、242–285、302–357 |
| 裁定 7 首次失败 | 采纳，写进 T 文档串与本节：失败 → 停 → 回执 → 改 R 或 T → 新 sha → Arch 重审 → 新 selftest .ok；相同字节重跑须 Arch 同意 | T 1–28 |
| 裁定 8 / P3-3 | T 运行命令改为 Arch §6 版（加 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`、`--noconftest`）；文档串披露两个解释器版本差异 | T 21–25 |
| P3-1 | v1_1、calib_sealed、ok_runner_pin 不在 git：不归 Strategy 所有，未提交，留给各自所有者 | — |
| P3-2 | summary.json：`write_x_atomic`（先 open('x') 写 .tmp，再 os.link 到正式名，已存在即失败，从不覆盖）；manifest、VOID.md：`write_x`（open('x')）；E 的 equiv_report.json 和 VOID.md、D21 的 summary/VOID/计数 json 同样处理 | R 1488–1512、1582、1606；E 117、154；D 288–300、321–350 |
| P3-6 | r2 节的起草时间改为「约 02:01–02:14 ET（提交 246aa99a 于 02:14:15 ET）」 | 本文第 169 行 |
| P3-7 | D21 PINNED_DOCS 补钉停跑规则 41f29825（.ok 键 stoprule_sha256） | D 48–49 |
| P3-8 | v1.4 读的 v1.3 产物按 D21 做法钉 4 个权重文件键（`v13_w_eq*_sha256`），load_v13_eq100 只读这些文件，缺失即报错 | R 119–124、1022–1027 |
| P3-9 | T 自查加「signed_et 不得在未来」；v2 门禁启用后改用 v2（待 Eng） | T 73 |

另：CLARIFY-1 现在也作为 `clarify_sha256` 钉进 R 的 PINNED_DOCS（R 56），D21 共用。

### r3.2 .ok 键白名单模板（ARCH_RUN_AUTH_v1_4.ok；白名单 = 必填，缺一个或多一个都拒；Arch 写，Strategy 不创建）
```
format=quantlab_run_auth_v1
version=v1_4
signed_by=arch
signed_et=<ISO8601 带时区，不得在未来>
expires_et=<ISO8601 带时区，晚于 signed_et>
allow_full=<true|false>
allow_smoke=false
allow_equiv_check=<true|false>
runner_sha256=94643e27741835d703440d64d906f4c130f4763a522412a058f5fbd879454ca0
combined_sha256=7943d83b5740fddadd8e06472731ddbc4f22fadee316f568d034bbdcb197f3f0
equiv_script_sha256=09dc431d2f90782e6aaa406bc4ca84e6e332d0db8395bd081a0f8520060b0bed
lotfix_sha256=d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425
stoprule_sha256=41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b
amend_sha256=0029672aed3d9e6a70409e25b02de16291caf5bafbc5c8d8b93624e16719f009
clarify_sha256=d075a2a68f2d5c42c750669cdff2dd51f93794e11ea907f08ffc29c39c724d85
clarify2_sha256=<CLARIFY-2 文件 sha；文件尚不存在，代码也未钉>
live=false
promotion=false
python_exe=/workspace/QuantLab/.venv_opt/bin/python
out_dir=output/strategy_optimizer/core_x2/v1_4
equiv_root=output/strategy_optimizer/core_x2/v1_4_equiv
daily_basic_sha256=f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948
calendar_sha256=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41
sw_members_sha256=89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c
calib_risk_sha256=633c21ef0a44c557bb5619206f6086c6fce153bb4be6af8b2b88d24295620591
calib_turn_60w_sha256=56e75b458cd24b72abc92b6f43447e421773a7cfc90957ece6fba35d6884b0a4
calib_turn_100w_sha256=6cccfb7a177c7df312ac160edd5d114c4d75e972d211ab8caa00b805aa35e58a
dep_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
nt_quantlab_init_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
nt_quantlab_intel_init_sha256=750fa5854299df15b04ad0b4ade7cb888d93039f07f744adb84855b6bdd0bee0
nt_asof_window_sha256=593e35882155c2acf143d7c741fef33023345dd41a73a9fc9218ca7c0be400b1
nt_debate_ledger_sha256=8e388df93f1fa63b9a01ec9b2adafaa4e316800aa351804b75ab1edb0615fdcd
nt_embeddings_sha256=d5c52c0e3af901ce2924d59733286ae6697878b64211f2f032b21945b08b9d46
nt_messages_sha256=9354a34c893aa9dccab72215e367235d7f4ea336905016414e71408ad7bdca35
nt_promotion_gate_sha256=514564fd0cbea65a7b148de5c179ddabadc9866fdf89b88b42883f62322d55ac
nt_ai_debate_memory_runner_sha256=e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea
nt_g1g5_wiring_sha256=ff510148a8d0c571680986c8345b5d83e70fd572eca80206b1383f3c35da8c54
nt_g1g5_expand_g6_sha256=b2d26c0d26933778df62af99828dc58e17d37f94432004ca2d2de94ed2ba1a16
v13_w_eq100_60w_sha256=a9b7647c138942ab3648c85b9271ded0cde4f17938841d7f1254a742536949c1
v13_w_eq100_100w_sha256=6ef9c029a3d892f655e34c2a282678d879eb18b26e7c55616208151c4104d6ec
v13_w_eq80_60w_sha256=eab75fe6756fb46beb257324d30c428ba9c51920ddb1cd63622195fd081a24e4
v13_w_eq80_100w_sha256=ef89f20810fde244445b3221a75e214cc5c6026735728938dea9fc642457b4c0
```
- 共 42 个键。允许整行 # 注释和空行；不允许行内注释、缩进、未知键。
- 上面的输入 sha 都是 2026-10-18 02:43 EDT 用 sha256sum 实测的当前值；签发前须当场复算（裁定 5）。闭包 combined（11 个文件，按路径排序拼「path=sha\n」）= d3889fe3112ab8a5a5c403d71dbb28fac8ea11a13bd57ae0e7cf8e863ced13ad，只写进 summary，不是 .ok 键。

### r3.3 nontextbook 顶层闭包 11 个文件（sha256sum 实测）
| 文件 | sha256 |
|---|---|
| research/g1g5_nontextbook_weights.py | 8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789 |
| quantlab/__init__.py（空文件） | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| quantlab/intel/__init__.py | 750fa5854299df15b04ad0b4ade7cb888d93039f07f744adb84855b6bdd0bee0 |
| quantlab/intel/asof_window.py | 593e35882155c2acf143d7c741fef33023345dd41a73a9fc9218ca7c0be400b1 |
| quantlab/intel/debate_ledger.py | 8e388df93f1fa63b9a01ec9b2adafaa4e316800aa351804b75ab1edb0615fdcd |
| quantlab/intel/embeddings.py | d5c52c0e3af901ce2924d59733286ae6697878b64211f2f032b21945b08b9d46 |
| quantlab/intel/messages.py | 9354a34c893aa9dccab72215e367235d7f4ea336905016414e71408ad7bdca35 |
| quantlab/promotion_gate.py | 514564fd0cbea65a7b148de5c179ddabadc9866fdf89b88b42883f62322d55ac |
| research/ai_debate_memory_runner.py（工作区字节，AI 未提交 +21 行；= e1736d80，与审查一致） | e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea |
| research/g1g5_wiring.py | ff510148a8d0c571680986c8345b5d83e70fd572eca80206b1383f3c35da8c54 |
| research/g1g5_expand_g6.py | b2d26c0d26933778df62af99828dc58e17d37f94432004ca2d2de94ed2ba1a16 |

### r3.4 启动命令（不变；只在 CLARIFY-2 钉进代码、Leo 定 Core 继续、D21 回执经 Arch 审过、Arch 签 v1.4 .ok 之后）
- 同 §r2.8（先 equiv，PASS 后再 full）。新增要求：PYTHONPATH/PYTHONHOME/PYTHONSTARTUP/PYTHONUSERBASE 不得设置。

### r3.5 仍需裁定 / 知悉
1. **CLARIFY-2 文件不存在**：r3 按主 Agent 转述实现；文件落盘后须填 R 第 62–63 行（路径 + sha）→ 新 R sha → Arch 复核 §8 实现与文件原文一致。在此之前所有模式都拒绝启动。
2. **「disclosure 缺行」也记为不可证可行**（与 NO_DATA_CARRY 同等对待，原因写明），而不是报错。这是我对 CLARIFY-2「有效日 <29 不阻断」的理解，请确认。缺行在正常运行中不应出现。
3. **加载模块检查**（end_of_run_recheck）：真实运行中只要加载了不在「代码 3 文件 ∪ 闭包 11 文件」里的仓库内模块，就作废。v1.4 路径按 Arch 的 AST 结论只会加载这些；若 nontextbook 的懒加载（g1g5_x2_panel_stitch）意外被触发，会 VOID。请确认这一严格度。
4. **Arrow 包装未覆盖**：`pyarrow.fs.LocalFileSystem` 的方法（cython 类型，不能打补丁）、`pa.ipc.RecordBatchFileWriter/StreamWriter` 直接构造、`pyarrow.orc`。R/C/V 不用这些（rg 只在 C 第 117、123 行有 pq.read_table）。T 的保证仍是「已包装的入口 + 真实数据函数全部替换」。
5. ai_debate_memory_runner.py 须由 AI 原样提交（sha 仍为 e1736d80）后才签 v1.4/D21 .ok；g1g5_x2_panel_stitch.py 同理（不钉）。
6. P3-1 三个未入 git 的文件由各自所有者提交。
7. T 新 sha → 须 Arch 重审并签新 selftest .ok；T 没有跑过（主 Agent 只跑过旧 T 7176f974）。
8. 时间敏感的反例：T 的 .ok 反例以运行当时时间 ±数小时构造，不依赖固定日期。
