# MILP 整手抛光对照：预注册规格（DRAFT r2）

- **状态：DRAFT r2**。未冻结，未经 Beta 会签、主 Agent 批准。live=false，promotion=false。
- **重建说明**：
  - 本文**重建**于 2026-10-18 01:05 ET box 重启时丢失的 r1（DRAFT，sha256 前缀 `f78f93aa306864f9`，见 `docs/v2/RECOVERY_INVENTORY_20261018_ZH.md` 第 23 行）。r1 在全盘、tgz、git blob 中都没有副本。
  - r2 按 Arch 对 r1 内容的记录逐条重写，所有探针数字重新取自现存的探针脚本和三个结果 json（§9）。
  - **r2 与 r1 不是逐字节一致的文件，sha 不同**。r2 的 sha 不写在本文内（文件不能包含自身的 sha），以 TEAM_STATE 的 Arch 行和后续 RECOVERY_INVENTORY 更新为准。r1 的 sha f78f93aa 作废，任何授权、会签都不得引用它。
  - r2 相对 r1 的已知变化：输入源改为 AMEND-1 r2.1 的全池快照（§1.3）；另有几处 r1 未写明、r2 补写的细节，统一列在 §10「待定事项」，冻结前须逐条定稿。
- **性质**：Arch 单独提议的对照原型（v1.4 §4.4「MILP 抛光原型（Arch P3-2）」，§9 中的 S4）。**只比较整手层可行率与偏离，不计算任何收益**，不替换 v1.4，不改 v1.4 的任何规则或结论。
- 起草：QuantLab Arch，2026-10-18 ET。写作时没有运行任何优化器、回测或求解器（探针是 r1 时期已运行完的合成数据测试，本次只读其结果）。

## 0. 钉住的文件（运行时逐个重算 sha256，任一不符即 raise SystemExit）

| 文件 | sha256 | 关系 |
|---|---|---|
| `docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md`（LOTFIX v1.4 FROZEN 正文） | d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425 | 常量、口径 C、S1/S3/S5、slack 阶梯、落盘字段。本规格只引用，不修改 |
| `docs/v2/LOTFIX_V1_4_FREEZE_RECORD_ZH.md`（v1.4 冻结记录） | 0d47c52f8be402d02e369d0a92c4ba05d868038f4b3c41870b2bdb8234c52641 | 冻结依据 |
| `docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md`（AMEND-1 r2.1，主 Agent 01:09 ET 批准，Beta 会签 45b7f415） | 0029672aed3d9e6a70409e25b02de16291caf5bafbc5c8d8b93624e16719f009 | 提供全池快照 `core_v1_4_pool_snapshot.parquet`，是本对照的输入源 |
| `docs/v2/audit/arch_milp_probe_v1.py`（探针） | 51a6df602b039c45ff33604796700551e0cf63fdcc7a6f15bc2b93dec89735ec | §9 的数字来源 |
| `docs/v2/audit/arch_milp_probe_v1_result_base.json` | b3a41edb06f35b87dc135bb609a62d9985d7065f7de4470cdfbb0355386c181e | 同上 |
| `docs/v2/audit/arch_milp_probe_v1_result_stress.json` | 14e3f6d784a55d0a6ebb7cb7abd19f9c5c6b114bc6d9bc89d645d3782c4024c1 | 同上 |
| `docs/v2/audit/arch_milp_probe_v1_result_tight.json` | 04cd5a0b8e07d796ac8c5bfef8c4d9104ebcf0db4f6994c7647ce9550895fa9b | 同上 |

运行时另须钉住（运行前由 Arch 写入 .ok，§8 前提 ③）：v1.4 正式输出目录内的快照及 §7 落盘文件 sha、MILP runner 和 checker 脚本 sha、κ 的来源文件 sha。

## 1. 对照设计

### 1.1 问题
v1.4 用「连续求解 → 整手取整 → 修复 → 补手」（round-and-repair）。本对照回答：在同样的约束下，**直接以整数手数求解**能多救回多少个严格可行日。差值界定 round-and-repair 相对整数最优损失的可行率。

### 1.2 一日一解、无跨日传递
- 对每个**调仓日 × 档位（60万 / 100万）× 口径（① / ②）**，各解一个独立的 MILP。
- 每个 MILP 的输入全部取自 **v1.4 当天的状态**：候选集、价格、每手股数、逐票 β/Size/MidCap、行业、全池 wb 与基准值、目标 w\*、上期持仓。
- MILP 的结果**不传到下一天**：下一天的上期持仓仍是 v1.4 的实际持仓。因此两者的差异只来自整手层，**不存在 MILP 权重路径**，也就无从计算 MILP 的收益或 NAV。

### 1.3 输入源（r2 新增）
- 全池逐票数据取自 AMEND-1 r2.1 的 `core_v1_4_pool_snapshot.parquet`（每调仓日 × 档 × 袖，完整 HI_LIQ 池每票一行，含 in_candidate、price、lot_size、u_i、beta、size_z、midcap_m、sw_l1、wb_i、q_cont、q_final、selected、stage、K_sel，另有 CASH 和 sh.510300 行）。
- **MILP runner 读快照，不重跑 prepare_day，不重读行情**。快照的 A1（Σwb_i=1、Σwb_i·beta_i=bb）和 A3（Σq_final=1、Σq_final·beta=组合 β）校验在 runner 读入时再做一次，不通过即 raise SystemExit。
- 基准值 bb/zb/mb 与 v1.4 记录状态分别取自 v1.4 的 `core_v1_4_daily_bench.csv`（§7.6）和 disclosure；目标 w\* 的来源见 §2.2 和 §10 O1。
- 快照中缺失值为 NaN（AMEND-1 A4）。候选票的 β/Size/MidCap/价格任一为 NaN 时，该 档×口径×日 记为 INPUT_NAN，raise SystemExit，不填补。

## 2. 模型

### 2.1 记号与变量
沿用 v1.4 §2 记号：A、c_A、B_s（① 1.0 / ② 0.8）、L_i、P_i、u_i = L_i·P_i/A、ε = 1e-6（手）。候选集 = 快照中 in_candidate=true 的票（即 v1.4 S5 按 ② 门槛筛后的集合）。
- n_i ∈ ℤ≥0：票 i 的持有手数；整手后 NAV 权重 x_i = u_i·n_i。
- z_i ∈ {0,1}：是否持有票 i。
- t_i ≥ 0：跟踪辅助变量，t_i ≥ |x_i − x_i\*|（两条线性不等式）。
- d_i ≥ 0：交易辅助变量，d_i ≥ |x_i − x_i^prev|（两条线性不等式）。
- 口径 ② 的 510300 固定 0.20、不取整，不是变量，与 v1.4 相同。

### 2.2 目标 w\*
- **w\* = v1.4 当日在 K_sel 上第一次成功的连续求解**（在 S3 升 K 之前；状态 optimal 或 optimal_inaccurate，取该 K 的 slack 阶梯中第一个成功的那次）。x_i\* = B_s·w_i\*。
- 若 v1.4 当日所有求解都失败（求解阶段 INFEASIBLE），则**没有 w\***：
  - 主口径：该 档×日 记为 MILP 失败，**分母不变**（与 v1.4 同一分母）；
  - 另做一个**只披露**的「只判可满足性」变体（同一约束 H1–H10、同一 slack 阶梯，目标函数为 0），不进入 §5.4 的任何门槛。
- x^prev = v1.4 当日调仓前实际持有的股票簿 NAV 权重（与 v1.4 计算换手所用的 w_cur 同源，见 §10 O2）。

### 2.3 目标函数
min (1/B_s)·[ Σ_i t_i + μ·Σ_i d_i ]，**μ = 0.1**。
- μ 只是并列打破项（tie-breaker）：把某票偏离 w\* δ 来省换手，最多省 μ·δ，却至少多付 δ 的跟踪偏离；因为 μ < 1，**为省换手而偏离永远不划算**。
- 1/B_s 只是把两口径归一到股票簿尺度，不改变每个 MILP 的最优解（探针中未乘 1/B_s，见 §9.4）。

### 2.4 硬约束 H1–H10（全部按口径 C，全池基准，线性化）
记 G_g = Σ_{i∈g} x_i，f ∈ {Size z, MidCap m, β}，f_b 为完整 HI_LIQ 池 wb 加权基准（bb/zb/mb，含 S5 剔除和 cap_lot=0 的票）。

| 编号 | 约束 | 线性形式 |
|---|---|---|
| H1 | 名数 20–30 | 20 ≤ Σ z_i ≤ 30 |
| H2 | 单票上限（最紧 big-M） | n_i ≤ M_i·z_i，**M_i = m_i^s = floor(c_A·B_s·A/(L_i·P_i) + ε)**，与 v1.4 S1 公式完全相同 |
| H3 | 整手后单票下限 2% | n_i ≥ F_i·z_i，F_i = ceil(0.02·B_s/u_i − ε)，即 x_i ≥ 0.02·B_s（股票簿 2%）。若 F_i > M_i 则固定 n_i = z_i = 0 |
| H4 | 含成本预算（现金 0–2%） | B_s − 0.02 ≤ Σ u_i·n_i + κ·Σ d_i ≤ B_s |
| H5 | 行业相对上界 | G_g/B_s − wb_g ≤ 0.08 + s_ind |
| H6 | 行业相对下界 | wb_g − G_g/B_s ≤ 0.08 + s_ind |
| H7 | 行业绝对上限 | G_g/B_s ≤ 0.20（无 slack） |
| H8 | Size | \|Σ x_i·size_z_i/B_s − zb\| ≤ 0.35 + s_sty |
| H9 | MidCap | \|Σ x_i·midcap_m_i/B_s − mb\| ≤ 0.35 + s_sty |
| H10 | β | \|Σ x_i·β_i/B_s − bb\| ≤ 0.10（无 slack） |

- 行业 g 遍历**所有申万一级行业，包括当日没有候选票的行业**：此时 G_g ≡ 0，若 wb_g − 0.08 − s_ind > 1e-6 则该档位在该 slack 级上平凡不可行（INFEASIBLE_TRIVIAL），不调求解器。
- 现金 = B_s − Σx_i − κ·Σd_i，留在分母里、暴露为 0（口径 C）。
- κ：Eng 提供的 book_smoke 线性单边成本率（见 §7.4）。

### 2.5 slack 阶梯
与 v1.4 相同：(s_sty, s_ind) = (0, 0) → (0.05σ, 0.5pp) → (0.05σ, 1pp)，**采用第一个严格可行的级**（§3.1）。β、行业绝对上限、名数、单票上下限、现金**都不享受 slack**。

### 2.6 MILP 比 v1.4 更严（写死，不另设变体）
- MILP 额外要求：**整手后**每只持有票 ≥2%（H3；v1.4 只在求解阶段要求 2%），以及**交易成本计入预算**（H4）。
- 因此「MILP 严格可行日 − v1.4 严格可行日」是 round-and-repair 损失的**保守下界**。
- **不做去掉这两条的变体**，避免看结果后挑模型。

## 3. 严格可行判定与求解器

### 3.1 严格可行
一个 档×口径×日×slack 级 的 MILP 严格可行，须**同时**满足：
1. 求解器状态为 Optimal；**或**到时限时有可行解，且相对 gap ≤ 1%（或绝对 gap ≤ 1e-6，按 §2.3 归一后的目标）；
2. **独立 checker** 从整数手数 n_i 重算（不信任求解器的行活动值），H1–H10 全部满足，容差 1e-6。

一个 档×日 严格可行，当且仅当**两个口径都严格可行**（与 v1.4 两袖耦合一致）。

### 3.2 求解器设置（写死，不得通过 CLI 或环境变量修改）
- HiGHS（highspy），**每个 MILP 时限 60 s，单线程（threads=1），random_seed=0**，output_flag=False。
- 求解器内部收敛设置沿用探针：mip_rel_gap = 1e-4，mip_abs_gap = 1e-7（见 §10 O4）。
- 串行执行，一次只解一个 MILP。

## 4. VOID 条件（任一触发即整次作废，写 VOID.md，不得重试，须新 .ok）
1. **checker 自检不一致**：checker 按 **v1.4 规则**复核 v1.4 的整手结果（快照 q_final），与 v1.4 自己记录的状态在**任一天**不一致。
2. **模型错误**：v1.4 的整手解满足本规格 H1–H10（在某个 slack 级上），而 MILP 在同一级报告 infeasible。
3. **checker 失败率 > 5%**：求解器报可行、但 checker 不通过的 MILP 占比超过 5%。
4. **内存**：进程峰值 RSS > 1400 MB。
5. **总时长**：全量运行总时长 > 4 h。
6. 任何钉住文件 sha 不符、highspy/HiGHS 版本不符、Highs.run() 返回错误（§7.3）。

## 5. 产出与读数

### 5.1 严格可行率表
2 档 × {①、②、两袖合并} × {X2、全样本、SEALED}，每格给 v1.4 与 MILP 的严格可行天数、分母、比率和差值（天）。
- 窗口沿用 v1.4 §1：SEALED 2018-01-02→2024-05-31，X2 2024-06-03→2026-10-09（29 个调仓日），全样本 = 两者之和；分母为 v1.4 记录的调仓日（排除无数据日），与 v1.4 相同。
- 两袖合并 = 档×日 两口径都严格可行（§3.1）。

### 5.2 2×2 一致矩阵
每档 × 口径 × 窗口：v1.4 严格（是/否）× MILP 严格（是/否）四格天数。

### 5.3 偏离指标（两者都严格可行的日子）
- Σ|Δw| = Σ_i |x_i^{MILP} − x_i^{v1.4,lot}|；
- 名字差异：只在一边持有的票数，以及两边名数；
- 换手差：MILP 单边换手 − v1.4 整手后单边换手（0.5·Σ|x − x^prev|）。
逐日落盘，汇总给中位数、均值、最大值。

### 5.4 失败归因（按约束族）
对 MILP 在最后一级 slack 仍不严格可行的 档×口径×日，做一次**弹性重解**：给 H1、H4–H10 各族加非负弹性变量，最小化「违反量 / 该约束带宽」之和（H1 按名数、H4 按 2% 现金带、H5/H6 按 8%+slack、H7 按 20%、H8/H9 按 0.35σ+slack、H10 按 0.10）。按归一后违反量最大的族归因，并列出所有非零族。弹性重解只用于归因，不改变可行判定。

## 6. 输出 schema（固定输出目录，见 §7.2）

| 文件 | 键 | 字段 |
|---|---|---|
| `milp_solve_rows.parquet` | date, tier, caliber, slack_level, solve_rep | has_wstar, variant（main / satisfiability_only）, status, run_status, wall_s, n_cols, n_rows, nodes, mip_gap, obj, n_names, track_l1, turn_l1, cash, check_pass, viol（多值）, strict, rss_mb |
| `milp_positions.parquet` | date, tier, caliber, slack_level, code | n_lots, x_milp, x_v14_lot, x_star, x_prev |
| `milp_day_status.csv` | date, tier, caliber | window, v14_strict（记录状态）, v14_strict_checker, milp_strict, milp_slack_level, no_wstar, tierday_v14_strict, tierday_milp_strict |
| `milp_feasibility_table.csv` | tier, caliber∈{①,②,both}, window | n_days, v14_strict_days, milp_strict_days, diff_days, v14_rate, milp_rate |
| `milp_agreement_matrix.csv` | tier, caliber, window | both_yes, v14_only, milp_only, both_no |
| `milp_deviation.csv` | date, tier, caliber | sum_abs_dw, n_names_milp, n_names_v14, n_names_diff, turn_milp, turn_v14, turn_diff |
| `milp_failure_attribution.csv` | date, tier, caliber | top_family, families_nonzero, 各族归一违反量 |
| `run_meta.json` | — | 所有钉住 sha 的实测值、highspy/HiGHS 版本、python/numpy/scipy 版本、κ 及来源、.ok 路径与 sha、mode、开始/结束时间（ET）、峰值 RSS、MILP 总数、checker 失败率、VOID 检查结果 |
| `VOID.md` | — | 仅在失败时写：触发条件、时间、已产出文件清单 |

## 7. 工程要求

### 7.1 授权（.ok）
- 结构化 .ok，含三个字段 `allow_dev`、`allow_smoke`、`allow_full`，**都必须显式写出，不设默认值**；**恰好一个为 true**，且与 CLI 的 mode 一致，否则 raise SystemExit。
- dev、smoke、full **各自需要一份 Arch 出的 .ok**。Strategy 或其他 agent 不得创建 Arch 的 .ok。本规格不创建任何 .ok。

### 7.2 运行纪律
- 启动时重算 §0 和 .ok 中全部钉住文件的 sha256；检查 highspy 与 HiGHS 核心版本 = 1.15.1（探针所用版本，§9.1）。
- 只用 `raise SystemExit(...)` 报错，不用 assert。固定输出目录，启动时必须为空。串行执行。任何失败都写 VOID.md。

### 7.3 Highs.run() 返回状态（写死）
- runner 必须检查每次 `Highs.run()` 的返回状态，kError 即 raise SystemExit；模型状态为 "Not Set" 也 raise。
- **threads 必须在进程内第一个 Highs 实例上设置**，否则后续 run() 会返回错误、模型状态为 "Not Set"，且**不抛异常**。runner 在启动时先建一个 Highs 实例并设 threads=1（探针在 `h_ver()` 中即如此），之后每个实例再设一次。

### 7.4 成本率 κ
- κ 取 Eng 提供的 book_smoke **线性单边成本率**，须附来源文件路径和 sha，经 Arch 核对后写入 .ok。
- 探针中的 **0.0015 只是占位值**，不得用于正式运行。

### 7.5 smoke
- 100万、口径 ②、5 个调仓日；日期规则事先写死：**X2 窗口内按日期升序的前 5 个 v1.4 调仓日**（见 §10 O5）。
- 每个 MILP 解**两次**，两次的状态、整数手数向量、目标值必须逐位相同，否则 raise SystemExit。

## 8. 运行前提、解读门槛与禁止事项

### 8.1 运行前提（按顺序，全部满足前不得运行任何模式）
1. Leo 决定 Core 的去留；
2. v1.4 正式运行完成，并经 Arch 审过（含 AMEND-1 快照的逐位一致证明）；
3. 按 v1.4 实际产物重新钉 sha（快照、§7 落盘文件、runner、checker、κ 来源）；
4. Beta 会签；
5. 主 Agent 批准。

### 8.2 解读门槛（写死，事前给定）
- **建议主 Agent 考虑在 v1.5 采用 MILP**，须三条同时成立：
  1. 某一档（以 100万 为主）全样本「两袖合并」严格可行**多 ≥6 天**，**且** X2 多 ≥3 天（约 10.3pp；X2 1 天 = 1/29 = 3.45pp）；全样本 6 天折合约 5.6pp（按 v1.3 日历 107 个调仓日，见 §10 O3），以天数为准；
  2. 没有任何 档 × 口径 × 窗口 退步 ≥2 天（MILP − v1.4 ≤ −2）；
  3. 全部一致性检查通过（§4 未触发）。
- 若两档全样本都只多 ≤2 天，且 X2 都只多 ≤1 天：结论为「**round-and-repair 已接近整数最优，剩余不可行来自约束本身**」。
- 其余情况：**不确定，不作建议**。

### 8.3 禁止
- 不得据此修订 v1.3/v1.4 的任何结论或 v1.4 §8 的判定。
- 看到结果后不得调整任何参数（μ、时限、gap、slack、容差、κ、门槛等）。
- MILP 结果不得进入停跑规则或记分卡，不得据此计算任何收益。

## 9. 探针结果（合成数据，r1 时期已运行；数字逐项取自三个结果 json）

`docs/v2/audit/arch_milp_probe_v1.py`：只用合成数据，不读行情、不加载 QuantLab 模块、不算收益。N = 300 只、G = 28 个行业，10 个 seed × 2 档 × 2 口径（eq100 B=1.0、eq80 B=0.8），每组按 slack 阶梯解到第一个 checker 通过的级为止。κ = 0.0015（占位）、μ = 0.1、时限 60 s、threads = 1、random_seed = 0、mip_rel_gap = 1e-4、mip_abs_gap = 1e-7、checker 容差 1e-6。

### 9.1 环境
highspy 1.15.1，HiGHS core 1.15.1，Python 3.13.5，numpy 2.5.4，scipy 1.18.1，Linux-6.12.94+-x86_64-with-glibc2.41，threads=1。

### 9.2 三种模式
- base：价格中位数 18，目标在风格/β 带宽的 80% 以内（margin 0.8）。
- stress：价格中位数 60（手更粗），目标贴在带边（margin 1.0）。
- tight：stress 数据，但 MILP 带宽收紧到 β ±0.01、风格 ±0.05σ（目标仍按正常带宽生成），用于测难解分支定界的耗时。只测时间，不是模型变体。

### 9.3 规模与耗时

| 模式 | MILP 数 | 状态 | checker 通过 | 所用 slack 级 | 列数 | 行数 | 候选数 | 节点数 | 中位 s | p90 s | 最长 s | 合计 s | 峰值 RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 40 | 40 Optimal | 40/40 | 全部第 0 级 | 1196–1200 | 1827–1833 | 299–300 | 1–34 | 0.161 | 0.331 | 0.657 | 7.66 | 58.8 |
| stress | 40 | 40 Optimal | 40/40 | 全部第 0 级 | 1128–1200 | 1725–1833 | 282–300 | 1–19 | 0.241 | 0.443 | 0.598 | 11.51 | 60.4 |
| tight | 40 | 40 Optimal | 40/40 | 全部第 0 级 | 1128–1200 | 1725–1833 | 282–300 | 1–1555 | 0.488 | 0.983 | 1.294 | 24.04 | 60.1 |

- 合计 **120/120 Optimal**，checker 全部通过（违反 0），所有 MILP 的 gap ≤ 9.99e-5，名数 21–26。
- 单个 MILP 最长 1.294 s（tight，60万 eq80）；三种模式峰值 RSS 58.8–60.4 MB。

### 9.4 局限（如实写明）
- 120 个 MILP 都可行，且都在 slack 第 0 级就通过：**证明不可行（infeasibility proof）的耗时没有测到**，slack 第 1、2 级也没有被实际走到。正式运行中不可行的 档×日 可能明显更慢，最坏可到 60 s 时限。
- 探针目标函数未乘 1/B_s（§2.3），不影响最优解，但绝对 gap 的数值尺度与正式规格不同。
- 合成数据不构成关于 Core 的任何证据。

### 9.5 全量耗时估计
- 按 107 个调仓日（v1.3 日历）× 2 档 × 2 口径 × 最多 3 级 slack = 至多 1284 个主 MILP，以探针最长 1.294 s 计约 27.7 分钟；按 tight 中位数 0.488 s、每组一级计约 3.5 分钟。**预计 30 分钟内完成**（不含弹性重解和可满足性变体，二者只覆盖失败日）。
- 风险：若大量 MILP 跑满 60 s 时限，约 240 个即达到 4 h 上限（§4 第 5 条）而整次 VOID。这一风险只能在 smoke 中初步观察，不得据此调参（§8.3）。

## 10. 待定事项（冻结前须定稿；r1 中未见明确记录或 r2 新引入）
- **O1 w\* 的取数位置**：AMEND-1 r2.1 快照的 q_cont 写作「连续解权重」，没有写明是 K_sel 那次尝试还是 S3 之后 k_final 的解。r2 规定 w\* 取 v1.4 `core_v1_4_attempt_weights.parquet`（§7.1）中 K=K_sel、第一个 solver_status 成功的 attempt 的 w_solver，并在 stage 显示快照即为 K_sel 尝试时与 q_cont 交叉核对（差 >1e-9 即 raise）。若须改由快照直接提供，需 AMEND-1 r3。
- **O2 x^prev 的来源**：快照 schema 没有显式的「调仓前持仓 w_cur」列。r2 规定取 v1.4 计算换手时实际使用的 w_cur；若 v1.4 产物中没有可直接读取的字段，须先补落盘（AMEND-1 r3），不得由 runner 重读行情推算。
- **O3 全样本分母**：r1 记录「6 天 ≈ 5.7pp」，对应约 105–106 个调仓日；v1.3 日历为 107 个调仓日（6/107 = 5.6pp）。门槛以天数为准，pp 只作参考；正式分母取 v1.4 记录的调仓日。
- **O4 求解器内部 gap**：mip_rel_gap = 1e-4、mip_abs_gap = 1e-7 取自探针，r1 的设置清单只列了时限、线程和 seed。r2 将其写死，以免运行时依赖 HiGHS 默认值。
- **O5 smoke 日期规则**：r2 写为「X2 内前 5 个 v1.4 调仓日」；r1 的具体规则未保留。
- **O6 VOID 第 2 条的口径**：因 MILP 比 v1.4 更严（§2.6），r2 写明只在 v1.4 的整手解**满足本规格 H1–H10** 时才判模型错误，避免把「v1.4 可行但不满足整手后 2% 或含成本预算」的正常情况误判为 bug。
- **O7 510300 的成本**：口径 ② 的 510300 固定 0.20，不进入 d_i 与 H4 的成本项（与探针一致）。

## 11. 声明
本文只是文字：没有运行任何优化器、回测或求解器，没有计算收益，没有创建 .ok，没有修改 v1.3/v1.4 的任何产物、预注册、冻结文档或停跑规则。
