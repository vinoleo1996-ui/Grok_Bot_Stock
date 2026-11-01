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
| §10.6 新 ckpt 目录必须为空，不复用 `_ckpt_v1_3_poolind/` | 输出目录固定为 `core_x2/v1_4/`，ckpt 在 `v1_4/_ckpt_v1_4/`；目录非空就拒跑；不支持续跑 | 25–28, 174–189, 777 |
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

启动命令（只在 .ok 存在、Leo 定了 Core 去留之后）：
```
nohup /workspace/qlvenv/bin/python research/optimizer_core_x2_run_v1_4.py --mode full --auth-sha256 <.ok 的 sha> > output/strategy_optimizer/core_x2/v1_4_run.log 2>&1 &
nohup /workspace/qlvenv/bin/python research/v1_4_snapshot_equiv_check.py --auth-sha256 <.ok 的 sha> > output/strategy_optimizer/core_x2/v1_4_equiv_run.log 2>&1 &
```
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
