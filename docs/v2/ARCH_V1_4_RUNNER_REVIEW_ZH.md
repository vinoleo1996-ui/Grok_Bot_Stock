# Arch 审查：Core v1.4 runner（LOTFIX v1.4 + AMEND-1 r2.1）静态审查

- 审查：QuantLab Arch，2026-10-18 约 02:00 ET。**纯静态**：读代码、复算 sha、核对版本，没有运行 runner 或等价性脚本，也没有 import 它们。live=false，promotion=false。
- 对象（行号以下列 sha 为准）：
  - R = `research/optimizer_core_x2_run_v1_4.py` db8bdb8e63da01b3e759a19e317a870c7bbd356fb02724e5df4501eb753ba602
  - E = `research/v1_4_snapshot_equiv_check.py` 3d2e05333df033329b03012d99d939fa2c69736be27820198234dccf7d67a1b3
  - 改动对照 `docs/v2/STRATEGY_V1_4_RUNNER_CHANGES_ZH.md` d9767ef0c77014633fc892793a41232da90a106e7dd524fc718091ae9318c6fc
- **结论：有条件通过（P0=0，P1=3，P2=5，P3=7）。** 规格实现基本忠实，门禁结构正确，输出隔离、不碰纸面。**本轮不出 v1.4 .ok**：要等 Leo 对 Core 去留拍板，P1 也要先修。**mock 通道的 .ok 也不出**：runner 和测试里都没有 allow_mocktest 门禁，而且 LOTFIX §10 / 冻结记录对「任何形式的运行」有禁令，需要主 Agent 先裁定（见 §6）。

## 1. sha 与依赖核对（全部实测）
| 文件 | 期望 | 实测 |
|---|---|---|
| R | db8bdb8e… | ✅ |
| E | 3d2e0533… | ✅ |
| 改动对照 | d9767ef0… | ✅ |
| LOTFIX v1.4（FROZEN） | d921dd3f… | ✅；冻结记录 0d47c52f… ✅ |
| 停跑规则 | 41f29825… | ✅（冻结记录 13c6ad58…） |
| AMEND-1 r2.1 | 0029672a…f009 | ✅ |
| optimizer_core_v1_1.py / optimizer_lambda_calib_sealed.py | b500c21b… / 875daca9… | ✅ |
| combined_sha256（Arch 独立复算） | — | **04ffdd55e7a205944ec33193c796ad13a240f2ccf106b73da3a4177a28ec6243** |
| HI_LIQ 掩码（C.MASK_SHA_EXPECT） | c5433e80… | ✅ |
| 未纳入 combined 的代码依赖 | research/g1g5_nontextbook_weights.py（C.load_sw_map 会 import） | 8a56d136…，**属于纸面闭包**（与 Eng 闭包记录一致），v1.4 只读不写 |
| 未钉的数据输入 | daily_basic_full_tushare.parquet f6bbf9e5…（mtime 01:06:51，快照恢复）；trade_cal_sse_pit fa4260b8…；industry_members_sw_l1_tushare 89d4afa3…；calib λ 三个 json：633c21ef / 56e75b45 / 6cccfb7a | 只有 λ 按数值校验，其余**不校验** → P1-2 |

## 2. 规格符合性
| 规格 | 实现（R 行号） | 判定 |
|---|---|---|
| S1 整手上限 m=floor(c_A·B_s·A/(L·P)+ε)，cap_lot=min_s m·u/B_s | 209–215、228–232；求解器向量上限 278、282 | ✅。ε 用「保守混合」（D1，见 §4） |
| S1 不变量 c_A/2 ≤ cap_lot ≤ c_A | 233–235 raise | ✅。上界容差 1e-12 与 STRICT_CAP_REL=1e-9 不一致，理论上可能误 raise（P3-1） |
| S3：整手失败 → K+1…30，排除已证实不可行的 K，支撑集取 step-1 降序前 K，每个 K 走原 slack 阶梯，降级序 ①–⑤ | 538–576 | ✅。retry 末尾的切片是多余的，无害；④ 取 K≥K_sel 中最小的 hard_both；⑤ fail_stage=lot → 沿用 |
| S5 分袖预筛 L·P > c_A·B_s·A；共用候选集按 ② 剔除；无价格不剔除 | 229–241 | ✅。严格 `>` 在浮点相等时与「S5 剔除 = m=0」可能不一致（P3-2） |
| 基准不随预筛变化（Beta L2） | pool = D["alpha"].index；style_ctx 和 pool_ind_bench 在全池上算；求解器内基准 268–276 | ✅ |
| 口径 C 四处统一：求解、修复、补手、终判 | 求解器 w 和为 1（即股票袖按预算归一）；excC 384–386 是 E/B_s−b；终判 hard_eval(…,"C") 520；行业 den=B_s 333–334 | ✅。**硬约束分母 = B_s，现金留在分母里，510300 不进 HARD**，与 §6.1 一致 |
| 两袖耦合（任一袖失败两袖同沿用） | 523–525、871–877 | ✅ |
| §4.1 现金触发不改失败判定；停跑只计 INFEASIBLE / LOT_HARD_FAIL | 51、565、1008 | ✅ |
| §4.4 救回日分类、位置、反事实 k=3 | 878–879、1041–1061 | ✅ |
| §8 门槛（X2、口径 C、严格、80%、k=3）+ 60万 同报 | 1087–1101 | ⚠ 「含两袖耦合」的口径有歧义（P2-1，上报） |
| 停跑规则 §2 / M3–M6 | 985–1038 | ✅（只评估，D5） |
| AMEND-1 快照：全池加 S5 剔除、加 cap_lot=0、加沿用的池外票、加 CASH 和 510300；A1 / A3 / 覆盖性校验 raise | 628–681 | ✅。β 在 prepare_day 里永不为 NaN（stock_betas 缺省为 1.0），所以 673 行实际不会触发；A3 的 Σq_final=1 因为 CASH 按残差定义，几乎是同义反复（P3-3，披露即可） |
| AMEND-1 只写盘、不改决策 | 926–928、942–943 只在决策之后调用；EXCLUDED_FROM_EQUIV 53 | ✅ |
| 统一异常处理 → VOID；SIGTERM / SIGHUP / SIGINT | 1105–1181 | ✅ |
| v1.4 无 smoke 模式 | 153–154 | ✅ |

## 3. 门禁、隔离、纸面、内存
**门禁（parse / enforce，121–206）**
- 已做到：
  - 只认 `^[a-z0-9_]+=value$`；重复键拒跑；缺字段或空值拒跑。
  - format / version 精确匹配；signed_by=arch。
  - allow_full / allow_smoke / allow_equiv_check 只接受小写 true/false，没有默认值；allow_smoke=true 一律拒跑。
  - 只接受 64 位 hex sha；运行时重算 runner、combined、三份文档、等价性脚本和掩码；`--auth-sha256` 必填，并须等于 .ok 实测 sha。
  - 带 BOM 时 format 行失配，会拒跑；行内注释会让值失配，也会拒跑（两者都是安全失败）。
- 缺口：
  - **不要求、不校验 live=false 和 promotion=false**（P1-1）。
  - 数据输入和 nontextbook 依赖没有钉（P1-2）。
  - out_dir 写死在代码里、没有进 .ok（P3-4）。
  - 没有防并发锁（P2-4）。

**输出隔离**
- check_out_dir（179–189）要求输出目录精确等于 `core_x2/v1_4/` 或 `v1_4_equiv/snap_{on,off}/`，非空就拒跑，不在 strategy_hiliq 之下。ckpt 写到 `v1_4/_ckpt_v1_4/`，exist_ok=False。
- v1.3 产物只读（load_v13_eq100 会记 sha）。冻结目录和 v1.3 产物都不会被写。✅

**纸面**
- R、C、V 都不 import quantlab.platform、execution.py 或 v2_multisleeve_book，也不计算收益。唯一碰到纸面闭包的是只读 import research/g1g5_nontextbook_weights.py。✅

**SD1**
- v1.4 runner 只产权重，**既不用 SD1，也不用 execution.py 373fed30**。
- SD1 规格（2e428f39）§207 写明「SD1 只改会计层，不改求解」。
- v1.4 权重以后若进 book-smoke，属于另一个步骤，另批 .ok：引擎按 373fed30（SD0）出主列，以便与 v1.3 记分卡同引擎对照；SD1 通过 SD0 逐位证明之后再并列（规格 §204–206）。

**内存**
- 按日追加写，disc 和 v1.3 字典都很小，每日结束检查 RSS，超过 1536MB 即 raise → VOID（D16）。
- 不足：一天之内的峰值没有监控（S3 每档最多 30 次求解）（P3-5）。
- v1.3 正式运行约 7 分钟（00:20–00:27），日志里没有 RSS 记录。

**解释器**
- v1.3 用 `.venv_opt/bin/python`：Python 3.13.5、numpy 2.5.4、pyarrow 26.0.0。
- 改动对照 §6 的命令用 `/workspace/qlvenv/bin/python`：3.12.14、numpy 2.5.3、pyarrow 25.0.1。
- cvxpy 1.9.3、clarabel 0.11.1、osqp 1.1.3 两边相同（P2-2）。

## 4. D1–D22 逐条裁定
| # | 裁定 | 说明 |
|---|---|---|
| D1 | **采纳保守混合** | 效果等于「无 ε 版，加一个浮点噪声容差」：两位小数的价格让 T/(L·P) 实际上不可能落在 [m−1e-6, m) 而又不等于 m，所以对经济含义没有可见影响，又满足 §3.1「cap ≤ c_A·B_s + ε·u」的更严形式。要求加回退计数（P3-1），并把 233 行的上界容差改为 c_A·(1+STRICT_CAP_REL)。不上报 |
| D2 | 采纳 | 理论上不应触发；clamp_count>0 的日子须在 summary 汇总并逐日披露 |
| D3 | 采纳（规格内）**，抄送主 Agent** | §6.1「四处统一」要求修复和补手与终判同口径。v1.3 修复时忽略无价格票，与终判不一致；v1.4 计入常数偏移才符合规格。修复路径会因此与 v1.3 略有不同，属轻微经济影响，须披露 n_no_price |
| D4 | 采纳**，抄送 Beta** | 「完整池」= prepare_day 之后的求解池，wb 在这个池上归一，与 v1.3 基准一致，A1 才成立。要求 daily_bench 增加 mask_n（掩码当日在池的票数），披露被 prepare_day 剔除的数量（P3-6） |
| D5 | **采纳：只评估、不停跑**，抄送主 Agent | 停跑规则 §21 规定的是前瞻 / 纸面的停跑处置；§8 必须算满 29 天。summary 已标注 mode=evaluate_only_no_decision_change。§8 的 k=3 用 X2 首日起算的序列，全样本另报 |
| D6 | 采纳 | 与 §4.4 两类计数一致；现金触发但没找到严格 OK 的 K 时回退到 K_sel，不算救回 |
| D7 | 采纳 | AMEND A3 里的「口径②」指袖②，按袖理解正确；组合 β 取 NAV 层（Σx·β + 0.2·bb）；池外沿用票的 β 记 NaN 不计入，与 disclosure 一致 |
| D8 | 采纳 | 510300 的 β 取 bb，与 v1.3 口径 A 一致；口径 C 下 510300 不进 HARD，不影响判定 |
| D9 | 采纳 | — |
| D10 | 采纳 | 快照 manifest 须写明 q_final 的单位是 NAV 权重，attempt_weights 的 q_* 单位是手（P3-6） |
| D11 | 采纳 | u_i = L·P/A；上限另列 cap_lot 和 cap_lot_sleeve |
| D12 | 采纳 | — |
| D13 | 采纳 | §7.6 同名字段按候选集算，*_support 按支撑集另列 |
| D14 | 采纳 | beta_window_source 已标明是推算值；manifest 注明「SSE 日历推算，非直接取自收益行」 |
| D15 | 采纳**，抄送主 Agent** | 逐分量 1e-6（归一化单位）。会影响 §8 边际可行天数的计数，所以 v1.3 按口径 C 重算（D21）时必须用同一容差 |
| D16 | 采纳 | 另加日内采样（P3-5） |
| D17 | 采纳并**扩展** | 见 P1-2：数据输入和 nontextbook 依赖一并钉住 |
| D18 | **方案：独立跑两次（snap on / off，都在 equiv 模式、同一确定性环境）** | **否决**「正式全量与 off 配对」：正式全量没有固定确定性环境，逐位比对可能假失败并拖累正式结果。另要求：① 正式全量也在同一解释器、同一 DETERMINISM_ENV 下运行（runner 自查 env，不符拒跑）；② 顺序是先 equiv，PASS 之后再 full（full 模式检查 equiv_report.json：verdict=PASS，且 code_sha、auth_sha 相同）；③ full 跑完把它与 snap_on 的 outputs_sha256 比对，结果只作披露，不是作废条件。耗时约为一次的 3 倍（v1.3 一次约 7 分钟，v1.4 因为 S3 会更长） |
| D19 | 采纳 | 只披露 |
| D20 | 采纳 | — |
| D21 | 采纳：不在本 runner 里做**，上报主 Agent** | §8 报 Leo 时需要「v1.3 按口径 C」的同口径对照（Beta L6），须另立脚本、另批 .ok，并在 v1.4 之前排期，用与 D15 相同的容差 |
| D22 | 采纳 | 由 Arch 在出 v1.4 .ok 时并入 `core_x2/RUN_AUTH_FORMAT.md`，同时加入 live、promotion、数据 sha、python_exe 等新字段 |

**会改变经济含义或需要另行上报的（单列）**
- E-1（主 Agent / Beta）：§8「严格可行，含两袖耦合」的计数口径。代码按每袖记录的状态计数：通过 ④ 采用时（两袖硬约束都过、但只有一袖现金 >2%），另一袖记 OK、计入严格可行。Beta 的 v1.3 复算两袖都是 15/29，看起来用的是「两袖同日都严格」。请主 Agent 裁定判定用哪种，两种都报（P2-1）。
- E-2（主 Agent）：mock 通道是否算 LOTFIX §10 和冻结记录所说的「运行」（§6）。
- E-3（主 Agent）：D21「v1.3 按口径 C 重算」要另批，并在 v1.4 前排期。
- 抄送知悉（规格内，不需要裁定）：D3（修复路径计入无价格票）、D5（只评估）、D15（容差影响边际计数）。
- Leo：本轮没有新增 P0 或 mandate 事项。v1.4 正式运行和等价性证明仍然只等 Leo 对 Core 去留拍板。

## 5. P 清单
- **P0**：无。
- **P1-1 门禁缺 live / promotion。** AUTH_REQUIRED_V14 加 `live`、`promotion`，值必须恰好是 `false`，否则拒跑。这是全队 .ok 的统一要求，Eng 的 ok_runner_pin c7805d9a 已经执行这一条。
- **P1-2 数据输入和依赖没有钉。** Data 的抓数进程正在运行（nightly_update tier3 等），daily_basic 在 01:06 由快照恢复。两次 equiv 之间、或 equiv 与 full 之间，输入一旦变化，就会出现假 FAIL / VOID 并烧掉 .ok，C 对 C 的比较也会失去意义。要求：
  - 新增 .ok 键 `daily_basic_sha256`、`calendar_sha256`、`sw_members_sha256`、`calib_risk_sha256`、`calib_turn_60w_sha256`、`calib_turn_100w_sha256`、`dep_nontextbook_sha256`，preflight 时全长比对，并写入 summary。
  - E 在两次子运行之后再复核一遍这些 sha。
- **P1-3 第一次执行就是正式运行。** 依赖数据的 raise 点有：S1 不变量 233–235、A1 / A3 / 覆盖性 666–680、状态集合 953、λ 校验 94。任何运行时错误（字段名、pyarrow 类型、pandas 3 行为）都会让正式运行作废并耗掉 .ok，而 runner 没有任何前置执行通道。→ 须先有一个受门禁约束的合成数据测试通道（§6），并由主 Agent 裁定 E-2。在此之前不出 v1.4 .ok。
- **P2-1** §8 耦合口径：增加 `n_strict_coupled`（两袖同日都是 OK）和对应的比率，与每袖口径并列；判定口径等 E-1 裁定。
- **P2-2** 解释器：正式全量和 equiv 都用 `.venv_opt/bin/python`（与 v1.3 相同）。新增 .ok 键 `python_exe`，runner 核对 sys.executable；把 python、numpy、pandas、pyarrow、cvxpy、clarabel、osqp、scipy 的版本写进 summary（两次 equiv 用同一解释器，不会破坏逐位比对）。改动对照 §6 的命令也要同步改。
- **P2-3** D18 的执行顺序和环境自查按 §4 实现：full 前置检查 equiv PASS，runner 不在 DETERMINISM_ENV 下就拒跑。
- **P2-4** 防并发：在输出目录之外用 O_EXCL 建锁文件（例如 `core_x2/.v1_4_run.lock`，记录 pid），避免两次启动同时通过空目录检查；正常结束或作废后保留锁文件作为记录，下次运行必须由 Arch 归档。
- **P2-5** E 的 FAIL（退出码 2）同样须视为「本 .ok 已用尽」：E 的文档字符串要写明，FAIL 也要求 Arch 重审并出新 .ok。
- P3-1 加 D1 回退计数 `eps_revert_count`（按日、按档）；233 行的上界改为 `cA*(1+STRICT_CAP_REL)+1e-12`。
- P3-2 S5 的 ex 改为由 `lot_cap_lots(...)==0` 判定（或者两处共用同一容差），保证「S5 剔除 = m=0」在浮点上也成立。
- P3-3 manifest 注明：A3 的 Σq_final=1 因为 CASH 按残差定义而必然成立，真正有信息的是 Σq·β 与 disclosure 的交叉核对。
- P3-4 .ok 增加 `out_dir=output/strategy_optimizer/core_x2/v1_4`（以及 equiv_root），与代码常量比对。
- P3-5 在 solve_tier 每个 attempt 之后采样 RSS，超限即 raise；把日内峰值写进 run_runtime。
- P3-6 快照 manifest 写明：q_final 的单位（D10），join 键 snapshot.tier ↔ daily_bench.aum（A2），以及 mask_n / pool_n（D4）。
- P3-7 改动对照 §3 的「§10.6」引用与正文一致；§6 命令里的解释器同步修改（P2-2）。

## 6. mock / 单测通道：建议与规格（本轮不出 .ok）
- **有必要设。** 理由见 P1-3。v1.3 的 smoke 隔离原则是：独立 .ok、独立输出目录、不留 ckpt、不消耗正式 .ok、产物不能当证据。mock 通道沿用同样的原则。
- **但现在不能放：**
  1. 没有门禁：R、E 里都没有 allow_mocktest，也没有测试文件，按规则不能出 .ok。
  2. LOTFIX §10 写明「全部满足前不得运行，包括 smoke 和单日测试」，冻结记录写明「两者都满足之前，禁止任何形式的运行」。**真实数据的 3 天 X2 切片在 Leo 拍板之前一律禁止**；而且 runner 目前没有限天数的参数，加了就要改代码、换 sha、重审。
  3. 只用合成数据、不读任何 data/ 或 output/ 输入的单元测试，是否算上述「运行」，由主 Agent 裁定（E-2）。Arch 倾向：不算，可以放。
- **规格（供 Strategy 实现，Arch 审过后签）：**
  - 新文件 `research/tests_v1_4/test_v14_synthetic.py`，只 import R 的函数，**不调用 main**，不改 R（R 的 sha 不变）。
  - 合成数据：约 120 只票、5 个行业、随机 α / β / ln_mcap，人为构造高价票，触发 S5、S1 截断、S3 升 K、现金 >2%、求解不可行、NO_DATA 日。
  - 覆盖：
    - lot_cap_lots 的整除价格、浮点边界和回退；tier_context 的不变量
    - solve_tier 走完 ①–⑤ 各分支；lot_round_v14 的 clamp 和 cap_lot_block
    - build_pool_snapshot 正常通过，并在篡改 wb / β / q 时正确 raise
    - Writers：ATT / SNAP 两个 schema 含 None 的 round-trip，以及 CSV 追加
    - stop_rule_eval、rescue_positions、post_run_disclosures（含 NO_DATA）
    - 用合成 pkl 测 write_daily_weights
    - 门禁的反例：BOM、重复键、行内注释、缺 live、allow_smoke=true、sha 不符、目录非空
  - 隔离：
    - 用 `sys.addaudithook` 拦截 open()：路径落在 `data/`、`output/strategy_hiliq`、`output/strategy_optimizer/core_x2/v1_4*` 或任何纸面产物下就立即中止。
    - 用 monkeypatch 让 C.prepare_day、load_daily_basic_window、_open_days 一被调用就 raise。
    - 只写 `output/strategy_optimizer/core_x2/_mock_v1_4_VOID_NOT_EVIDENCE/`（必须为空），先写 `VOID_NOT_EVIDENCE.md`。RSS < 500MB。
  - 门禁：`core_x2/ARCH_RUN_AUTH_v1_4_MOCK.ok`，字段：
    - format=quantlab_run_auth_v1、version=v1_4_mock、signed_by、signed_et
    - allow_mocktest=true、allow_full=false、allow_smoke=false、allow_equiv_check=false、live=false、promotion=false
    - test_sha256、runner_sha256、combined_sha256、out_dir
    - 测试文件自己解析这份 .ok，规则与 R 相同，**不读也不改**正式的 ARCH_RUN_AUTH_v1_4.ok。
  - 测试发现 bug → 改 R → 新 sha → Arch 重审。测试通过不构成任何证据，不改变正式 .ok 的前提。
- **真实数据切片（Leo 拍板之后才可能）**：要另立规格，另批 .ok（allow_slice=true），输出到 `core_x2/_slice_v1_4_VOID/`，不放在 v1_4/ 下面，也不消耗正式 .ok。

## 7. 给 Strategy 的确切修改清单（改完重报 R、E 的 sha 和改动对照）
1. `AUTH_REQUIRED_V14` 加入 `live`、`promotion`、`python_exe`、`out_dir`，以及 P1-2 的 7 个 sha 键（如果实现 P2-3，再加上 `equiv_root`）。`parse_run_auth_v14` 要求 live、promotion 恰好等于 `false`，全部 sha 键为 64 位 hex。
2. `preflight` 增加：
   - 比对 7 个输入 / 依赖 sha
   - `os.path.realpath(sys.executable) == realpath(kv["python_exe"])`
   - DETERMINISM_ENV 四个变量与 E 完全相同，否则拒跑
   - out_dir 键等于代码常量
   - mode=full 时，`v1_4_equiv/equiv_report.json` 存在、verdict=PASS、code_sha256.combined 与 auth_sha256 都与本次相同
3. summary 增加 `inputs_sha256`、`interpreter`（版本表）；manifest 按 P3-3 / P3-6 补充说明。
4. `post_run_disclosures.s8` 每档增加 `n_strict_coupled` 和 `strict_rate_coupled`；summary 两种口径并列，判定字段先保留现状，并标注「口径待主 Agent 裁定（E-1）」。
5. 在 R 的输出目录之外实现 O_EXCL 锁（P2-4）。
6. 实现 P3-1、P3-2、P3-5（回退计数、233 行上界、S5 判定共用 m=0、日内 RSS 采样）。
7. E：两次子运行之后复核输入 sha；文档字符串写明 FAIL 同样用尽 .ok；子进程解释器使用 `.ok` 里的 python_exe。
8. 改动对照 §6 的命令改为 `.venv_opt/bin/python`，并在前面加 DETERMINISM_ENV。
9. 如果主 Agent 裁定合成测试可以放，再按 §6 交测试文件和它的 sha。
