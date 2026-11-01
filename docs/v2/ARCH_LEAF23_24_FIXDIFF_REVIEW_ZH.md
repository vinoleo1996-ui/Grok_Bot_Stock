# Arch 复审附录：叶23 r2.2 / 叶24 r1 修复 diff（对 b997cba8 §8）

- 时间：2026-10-18 02:15 ET，QuantLab Arch。只做静态审：没有运行叶脚本、没有跑测试、没有在仓库内 py_compile、没有读任何叶结果、没有改 AI 的文件。
- 只读计数：在 /tmp 用 `nice -n 10` 读 v1 `panel_cache` 和 `universe_mask_hiliq_v1.parquet`，只读 date/instrument/hiliq/fulla/st/suspended 等列，峰值 RSS 860MB。
- 前审：`docs/v2/ARCH_LEAF23_R2_1_LEAF24_REVIEW_ZH.md`（b997cba8…）。live=false；promotion=false。

## 0. 结论

**不放行，两份 .ok 都不签。** P0=0，P1=3，P2=6，P3=6。

- B1、B2、B4，以及 N1、N2、N3、N4、N7、N8，在代码里核对后都正确。
- **B3 的沿用写法有错（P1-1）。** 在面板里，「无行」不等于停牌。v1 面板和重建面板都只保留 `fulla|hiliq` 为真的行，所以 ST、成交额不足、次新的日子同样没有行。r2.2 把所有无行日都当成停牌，沿用了成员状态和市值。
  - 在 v1 面板上按 r2.2 的写法模拟，X2 窗口内 HI_LIQ 沿用了 20,088 个名·日。其中 16,987 个是 ST 日（68 名），停牌日只有 3,079 个（405 名）。
  - 这个错的根源在 Arch：前审 C1 的措辞「停牌无行」，以及 §4 的伪代码 `Mraw.ffill()`，都没有把停牌和其他无行原因分开。本附录改正 C1 的执行口径，预注册不需要重新冻结。
- N5 和 N6 只修了一部分：敏感性变体不受 .ok 约束（P1-2），进程检查会永久拒跑（P1-3）。

## 1. 核验事实（全部实测）

| 项 | 期望 | 实测 |
|---|---|---|
| 叶23 r2.2 `research/g1g5_sue_desens_cs_alpha.py` | 81c2b4e6… | 81c2b4e6a30e8b2f66773c1fcc163cf58f2eca1bbcf3aa84ddaf16b76aee635d ✓ |
| 叶24 r1 `research/g1g5_imax_intraday_alpha.py` | de87c839… | de87c839ec4e278d798d7789669b5e75dfc8e284399b590d38b9763d99d7ea47 ✓ |
| diff `docs/v2/AI_LEAF23_24_ARCH_FIX_DIFF.patch` | 92ede693… | 92ede6938ec02439d1c81ed5c5c96fff209eb5bd5a2ea96d6235320933e29d9d ✓ |
| 备份 `_recovery/ai/pre_arch_fix_0154/` 两份脚本 | 8bfc8d4b… / 4be361ee… | ✓ / ✓ |
| 备份 + diff → 新文件 | 逐位一致 | 在 /tmp 对备份副本 `patch -p1`，cmp 两份都 IDENTICAL ✓ |
| 叶23 预注册 r2.1 | 8f5d8ac4… | 8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e ✓（未改） |
| 叶24 预注册 | c289e770… | c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8 ✓（未改） |
| `prereg_sha_leaf23.txt` 所列 27 项 | — | 当前项全部一致；两处「不一致」都是已标 superseded 的旧行（8bfc8d4b、0d9bd147），属预期 |
| `prereg_sha_leaf24.txt` 所列 22 项 | — | 当前项全部一致；一处为 superseded 旧行（4be361ee），属预期 |
| sha 清单文件本身 | — | leaf23 2d937d4a3c5fa4624e77d7f02c3faf0e0c4eaa2261a5504fb7a0fe4a5626bd2a；leaf24 697a1a46f50670ac29416c0b14146ee1e8034fb5ff33fb37c2eed92e3e9e11e7 |
| 内联 `ic_tstat_hac` | 与 leaf_selfcheck_v3（ecaa30d8）原函数等价 | 函数体（去掉 docstring 后）逐行文本一致，AST dump 一致，两叶都是 ✓ |
| 两叶守卫段（rss/进程/解析器/授权/meta 链） | — | 逐行相同，只有 is_primary/variant_tag 不同 |

## 2. 逐项复审

| 项 | 结论 | 说明 |
|---|---|---|
| B1 FIN | ✓ | `load_fin(panel)` 是真正的代码，只读面板目录里的 ind_names.csv（verify_panel 已核对它的 sha 等于 manifest）。v1 文件第 1 行是表头 `0`，`read_csv().iloc[:,0]` 的位置与 IND_ID 对齐。断言 `len==2`，但 assert 的问题见 P3-1。 |
| B2 manifest | ✓ | 已与 Data `build_cs_panel_v2_resumefix.py` 第 41–43、177–186 行逐键对照：step、mode、version、fixes、status、years[y].sha256、ind_names_sha256 都存在；RECEIPT 的 step、status、manifest_sha256 也都存在。 |
| **B3 池 EW/wb 沿用** | **✗ P1-1** | 见 §3。 |
| B4 当前记录 | ✓ | 正式报表行只按 eff 去掉缺失（niq 可为 NaN）；预告行 niq 算不出的仍然丢掉，这是前审允许的。`current_records`：先比 end_date，同季正式报表优先，再取最新 eff，按 eff 累计取最大。选出当前记录后，d1 是 NaN 就没有 α，不再退回旧季度。stale 200 天按当前记录的 eff 计。正式报表 niq 为 NaN 的唯一来源是上一期 ytd 缺失，此时同季预告的 niq 也算不出，所以不存在「正式报表 NaN 盖掉可用预告」的情况。旧写法的退回名·日数只作披露（event_table_oldsel），口径正确。 |
| N1 | ✓ | 已内联，不再 import leaf_selfcheck_v3；dep_adg 和 dep_lc 仍钉住。 |
| N2 | ✓ | 读文件之前先用 `repin` 重算 sha。FE 模块只 import 标准库和 numpy/pandas。面板逐年文件只在 authorize 时核对一次，见 P3-6。 |
| N3（叶24） | ✓ | 按叶18/18v 自己的 α 排序；另报持仓中缺 α 的比例。 |
| N4（叶23） | ✓ | 报 Mp&X 每日名数的中位数，以及 wb 权重占比的中位数和均值。注意 Mp 本身受 P1-1 影响。 |
| N5 | 部分 | 严格行格式、BOM、重复键、空值、必填键都已做。没做的：变体不受 sensitivity_specs 约束（P1-2）；未知键静默放过，window 等键不校验（P2-1）。 |
| N6 | 部分 | 首阶段 out_dir 非空就拒跑；meta 链核对脚本、.ok、预注册、manifest、变体，以及每个产出和上游 meta 的 sha，这部分正确。没做的：敏感性不接在主口径之后，叶24 也不接在叶23 之后（P2-2）；写文件不是排他创建（P2-3）。 |
| N7（叶24） | ✓ | ret_on 为 NaN 时 r 就是 NaN，该行丢掉；缺失计数写进 meta。 |
| N8 | ✓ | 不再回退到 v1。 |

### 2.1 叶24 对照主 Agent 01:42 裁定原文（逐字核对）

| 原文 | 预注册 c289e770 | 脚本 de87c839 | 结论 |
|---|---|---|---|
| ① 金融不剔主口径，加「剔金融」敏感性，仅披露 | §0 第 1 行、§4.1 第 48 行 | 只有 `--ex-fin` 时才执行 `~P.ind.isin(FIN)`；is_primary 要求 not ex_fin；持仓里的金融占比 `held_financial_share` 有报 | ✓ |
| ② 低波/彩票家族第 3 次试验，|t|≥2.50 | §0 第 2 行、第 87–89 行（「≥2.50 且为正」） | `T_DECISIVE=2.50`，两档 `t_hac >= 2.50` 才放行。对长仓超额，单侧条件就是 |t| 条件中有意义的那一侧，与第 89 行一致 | ✓ |
| ③ 涨停截断只披露不修正，须报涨停日占 IMAX 样本比例 | §3.4 第 37 行、§6.8 第 67 行 | `imax_window` 对每名算前 k 天里的涨停占比 `lu_share`，不改动 e_id。全池报 `limitup_share_in_imax_sample_pool`（再平衡日），各书持仓报 `held_limitup_share_in_imax_sample`，top-6、top-10、top-20 分别报 | ✓（不记 P1）。识别范围有缺口，见 P2-5；持仓口径见 P3-3 |
| ④ 只做多，已声明，不加空头臂 | §1 第 26 行 | `short_arm=False`；分位多空只作描述（字段名是 `_descriptive_only`） | ✓ |
| 用重建后 cs_panel；HI_LIQ 以 wb 为硬底线 | 第 72 行（出处写的是 00:59，与 01:42 不矛盾） | 只认 panel_cache_v2_resumefix；`floor`：两档 CAGR 都要 > wb，否则 FAIL | ✓（wb 本身受 P1-1 影响） |
| 研究叶、不开 GP、live=false、拿到 .ok 前不得运行 | 文首第 4 行 | research_only=true，live=false，有 .ok 门控 | ✓ |
| 出处 | §0 表头把第 5 行（含行业帽 25%）也归在 01:42 裁定下 | — | 01:42 原文**没有提到行业帽**。25% 的出处是 Arch 审核第 96 行（叶23 由主 Agent 01:52 认可），记 P3-4，在回执里写明即可，不需要重新冻结 |

## 3. P1-1（两叶）B3：「无行」不等于停牌（Arch 自己的 C1 口径错，在此更正）

**事实**
- Data `research/ai_cs_panel_build.py` 第 17–18 行：v1 面板只保留 `fulla|hiliq` 为真的行；fulla 等于 `~st & ~suspended & ~young & adv20>=3e6`。D1b 重建只在复牌日补回行，所以 ST、成交额不足、次新的日子在重建面板里仍然没有行。
- 在 v1 面板上，用 r2.2 的 `pool_benchmarks` 写法模拟 X2 窗口里被沿用的名·日，再用 mask 当天的状态逐日归因：

| 池 | 沿用名·日 | ST | 停牌（非 ST） | adv 不足 | 平均每日被沿用名数 |
|---|---|---|---|---|---|
| HI_LIQ | 20,088 | 16,987（68 名） | 3,079（405 名） | 22（7 名） | 35.2 |
| FULLA | 41,371 | 36,586（152 名） | 4,461（613 名） | 324（26 名） | 72.6 |

- ST 期间最长的连续沿用：300096.SZ 565 天，600165.SH 543 天，000656.SZ 504 天。
- **后果一：基准偏差。** 这些名在 ST 期间被当成 HI_LIQ 成员，收益记 0，权重是 ST 前的流通市值，这会扭曲判定用的 wb 地板和判定 t。断言只核对补回的复牌行，抓不到这个问题。
- **后果二：误停跑。** 摘帽通常要停牌 1 天。复牌那天如果是补回行，Data 的 `hiliq_carry` 取「最后一个有成交且 mask 非停牌的交易日」的状态，那天在 ST 期内，所以是 False。r2.2 沿用的是 ST 之前的 True，两者不一致，会 STOP。

**另外查了 AI 的扩展 3（种子窗口）**
- v1 面板上，窗口首日（2024-05-20）无行、但更早有行的名一共 111 个。其中 79 个能用 2023 年到 2024 年初的行作种子；32 个的最后一行早于 2023-01-01（最后一行 hiliq 为真的 18 个，fulla 为真的 32 个）。
- 用 mask 逐名核对这 32 名：2023-01-01 到 2024-05-20 之间，没有任何一名出现过「停牌且非 ST」的日子。复牌前一天，29 名是「停牌且非 ST」（摘帽停牌 1 天），3 名是正常日。
- 结论：**这 32 名都不是 2023 年以前开始的长期停牌，而是长期 ST 后摘帽。** 按正确口径它们的状态应为 False，与 Data 一致。
- **窗口末尾的问题：** 有 5 名在 10-09 之前停牌、10-09 之后才有行（000582.SZ、000668.SZ、300082.SZ、301139.SZ、603183.SH）。r2.2 按「PX 截到 e 之后的最后一行」判断退市，会把这 5 名误判为退市、不再沿用。

**修法（执行口径，取代前审 §4 伪代码；预注册文字「停牌记 0、不剔分母」不变，不需要重新冻结）**
1. 第 i 名在第 d 日的成员状态 S(i,d)：
   - 面板有行：S = 该行的 col（补回行为 False）。
   - 面板无行，且 mask 当日有行、`suspended=True`：S = 沿用上一个 S（停牌期沿用）。
   - 面板无行，且 mask 当日有行、`suspended=False`：S = False（ST、成交额不足、次新，**不沿用**，并中断沿用链）。
   - mask 当日无行（未上市或已退市）：S = False。
2. 流通市值只在停牌段内沿用该段之前最后一个有行日的 logmv，其余与 S 同步。
3. 然后 `Mp = S.shift(1)`，`wv = MV.shift(1)·Mp`。这正好是 Data `classify_restore` 中 `carry` 的定义（最后一个有成交且 mask 非停牌的交易日的状态），断言 `Mp == hiliq_carry / fulla_carry` 因此有意义。
4. **从数据起点 2018 开始逐年递推状态**（每年只读 date、instrument、col、logmv 和 mask 的 suspended，跨年只带一个状态向量），取消 2023/2024 种子窗口。
   - verify_panel 要核对实际读到的全部年份（2018–2026）的 sha（见 P2-6）。
   - 面板起点之前就在停牌的名，状态为 False，与 Data 的 `unknown_pre_data` 一致。
5. 退市判定改为「mask 此后无行」，不再用 PX 截到 e 之后的最后一行。窗口末尾停牌的名照常沿用。
6. `universe_mask_hiliq_v1.parquet` 钉进 .ok 的 `data_mask_sha256`，取值必须等于 D1b 回执 `pins.mask_sha256`。本审实测值 c5433e80…，但该文件 mtime 是 10-18 01:07，签发时以 D1b 回执为准。
7. 在 summary 的 b3 里加两项：
   - 沿用名·日按 mask 原因归类的计数。必须全部是 `suspended`，否则停跑。
   - 旧写法（不沿用）和 r2.2 写法（无行即沿用）的 EW/wb 年化差，两者都只作披露。
8. 「Mp ≠ carry 列」停跑这一条保留。修正后再出现不一致，就是真缺陷，不是种子窗口造成的。

## 4. P 清单

**P1（必须改，改后报新 sha；不改不签 .ok）**
- **P1-1（两叶）** B3 只在停牌日沿用，按 §3 改。
- **P1-2（两叶）** 敏感性范围没有绑定 .ok。现在只要 `allow_sensitivity=true`，任何组合都能跑，例如叶23 `--signal sue --no-forecast --blackout 40`，叶24 `--src total --k 1 --win 60 --ex-fin`，这些都没有预注册。修法：非主口径的 `variant_tag(a)` 必须**正好等于** `ok["sensitivity_specs"].split(",")` 中的一项，也就是只允许单因素变体，否则拒跑。
- **P1-3（两叶）** 进程检查会永久拒跑（扩展 4）。现在只要命令行含 `python`，并且含 `research/`、`scripts/`、`scripts_eng/` 之一，就判为占用。本审 02:10 ET 的 `ps` 显示以下四个进程都会命中：
  - Data 常驻抓数 94322 `scripts/acquire/remaining_after_stk_surv.py`
  - Data 常驻抓数 94403 `scripts/acquire/relay_outage_backfill.py`
  - 142531 `scripts/nightly_update.py --steps tier3`
  - 142545 `scripts/acquire/tier3_daily_snapshot.py`
  
  修法见 §5-4。

**P2（与 P1 同一个补丁改掉）**
- P2-1（两叶）.ok 白名单：未知键要拒跑。下列键必须核对：`window_start=2024-06-03`、`window_end=2026-10-09`、`mechanism_tag`、`rss_limit_mb=1500`、`serial_order`、`sensitivity_specs`、`data_mask_sha256`、`tool_cmds_path`、`tool_cmds_sha256`、`tool_closure_*`、`issued_at`（带时区的 ISO8601）。
- P2-2（两叶）阶段顺序：
  - 敏感性变体的首阶段（叶23 是 fund，叶24 是 build_HILIQ），必须先核对主口径 `OUT_ROOT/eval_meta.json` 的链（脚本、.ok、manifest 一致），并把它的 sha 写进 upstream。
  - 叶24 首阶段必须核对叶23 主口径和 4 个敏感性的 `eval_meta.json` 都已存在且链完整。依据是 serial_order：叶23 敏感性跑完才轮到叶24。
- P2-3（两叶）排他创建：meta、summary、B3_carry_mismatch、所有 parquet 输出，以及写到 `output/ai_factory/` 根目录的 daily_weights 和 run_meta，都改为 `open(p, "x"/"xb")`，parquet 写入这个文件对象。
- P2-4（两叶）进程检查要排除自己的整条祖先链，不能只排除 ppid；外层 wrapper 的命令行里也有 `research/`。另外：
  - 每个阶段的 meta 记录 `os.nice(0)` 和 ps 快照；
  - niceness 小于 10 就拒跑。
- P2-5（叶24）`limit_up` 漏了创业板 302 开头的代码：v1 面板 2025 年有 243 行，按 10% 处理是错的。改成：深市代码以 `30` 开头，或沪市 `688`/`689`，用 20%，其余用 10%。面板里没有北交所，已实测为 0 行。
- P2-6（两叶）verify_panel 改为核对实际读到的全部年份；P1-1 修好后是 2018–2026。

**P3（披露或顺手修）**
- P3-1 `load_fin` 的长度检查、pick_book 的行业帽检查、单名权重检查都用 assert，`python -O` 下会失效。改为显式 raise，与 leaf_selfcheck_v3 的 P3-1 一致。
- P3-2 FULLA 书的 `held_resume_rows_hiliq_carry` 读的是 hiliq_carry。改为按 carry_col 读，字段名改为 `held_resume_rows_carry`。
- P3-3（叶24）持仓的涨停占比是全部持有日的均值。预注册 §3.4 的口径是「每个再平衡日每名的前 5 天」，要补报再平衡日版本，原版本保留。
- P3-4（叶24）预注册 §0 第 5 行把行业帽 25% 也归在 01:42 裁定下，但原文没有这一项，出处应为 Arch 审核第 96 行。在回执里写明，不需要重新冻结。
- P3-5 面板逐年文件只在 authorize 时核对 sha。eval 和 build 阶段开始读之前，应再按 manifest 核对一次。
- P3-6 叶23 回执要写明：正式报表 niq 为 NaN 的唯一来源是上一期 ytd 缺失，同季预告此时也算不出，所以 B4 不存在「正式报表盖掉可用预告」的情况。

## 5. AI 四项扩展的裁定

1. **工具命令行含空格。**
   - **裁定：命令行改放进单独的 `.cmd` 文件，由 Arch 在签发时写好，.ok 只钉这个文件的路径和 sha。** 文件为 `output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd` 和 `…_LEAF24_X2.cmd`，每行一条完整命令，UTF-8、无 BOM、LF 换行。
   - .ok 加两个键：`tool_cmds_path=…`、`tool_cmds_sha256=…`。脚本 authorize 时核对这个 sha，并写进 meta。
   - 运行者每次运行工具前都要 `sha256sum` 这个 .cmd 文件和全部 `tool_closure_*` 文件，留痕到 `<out_dir>/tool_run_log.txt`（排他创建）。
   - .ok 里不再出现 `tool_*_cmd=` 键。严格解析器拒绝 `#` 行，这一点认可，保持不变。
2. **敏感性变体写到 `<out_dir>_<variant>`、共用同一份 .ok。** 认可，附三个条件：
   - 变体必须在 sensitivity_specs 里，且只能是单因素变体（P1-2）；
   - 变体首阶段要核对主口径 eval_meta 并写进链（P2-2）；
   - 全部输出排他创建（P2-3）。
   
   .ok 里的 `out_dir` 仍然只写主目录；meta 已核对 variant，保持不变。
3. **B3 种子窗口：2023 年以前开始的停牌就停跑。**
   - **裁定：取消种子窗口，改为从 2018 起逐年递推（§3 第 4 条），所以不会因为种子窗口不够而停跑。** 「Mp ≠ carry」停跑保留，因为修正后出现不一致就是真缺陷。不采用「披露加回退」，因为回退会让判定基准静默偏离 Data 的 carry 定义。
   - 实测：v1 中被怀疑的 32 名全是长期 ST 后摘帽，不是长期停牌。
4. **进程检查扩到 scripts/ 和 scripts_eng/。**
   - **裁定：现写法会永久拒跑，不认可（P1-3）。** 改为以下规则：
     - 命中即拒跑：命令行含 `research/`（python），或含 `scripts/fix_sd1/`、`scripts_eng/`、`scripts/nightly_update.py`。nightly 会写 etf、财报等被钉住的输入，开跑后 repin 会让运行中途拒跑，所以要在开跑前拦下。
     - 只记录、不拦：`scripts/acquire/` 下的常驻抓数（94322、94403 及其子进程）。叶的全部输入都钉了 sha，并且读之前重算，抓数改动不了已钉住的输入。这些进程的 RSS 计入开跑前的内存余量检查：系统可用内存不足 2GB 就拒跑。
     - 排除自己的整条祖先链（P2-4），ps 快照写进 meta。

## 6. .ok 草案更新（**仍未签发**）

- 签发前提：P1-1～P1-3、P2-1～P2-6 修完，新 sha 复审通过；Data D1b 重建的 execute 回执经 Arch 审过。
- `cs_panel_manifest_sha256` 和 `data_mask_sha256` 留空，审过 D1b 回执后回填。
- `script_sha256` 填的是当前 sha，修完后要替换。
- 格式：每行 `key=value`，无 BOM、无注释、无空格、每个键只出现一次。

### 6.1 叶23 `output/ai_factory/ARCH_RUN_AUTH_LEAF23_SUE_DESENS_CS_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=23
mechanism_tag=g1g5_ashare_sue_desens_cs_v1
scope=X2
window_start=2024-06-03
window_end=2026-10-09
allow_full=true
allow_smoke=false
allow_sensitivity=true
allow_sealed=false
live=false
promotion=false
promotion_approved=false
script_sha256=81c2b4e6a30e8b2f66773c1fcc163cf58f2eca1bbcf3aa84ddaf16b76aee635d
prereg_sha256=8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054
dep_l19_hiliq_sha256=16202b2e5b4935fc7613b0e6aeefd0573b1dd81c8174917782f118ae8166f9db
dep_l19_fulla_sha256=c761dc3618b813b23cb4c48489bdfd4d67808831a9639c82906e1c205d6bf7e6
dep_l20_hiliq_sha256=4ad2984e278fddad8bbdc2c0b26af8cdf3fc7078492e79ad2a38761bfff3d8ef
dep_l20_fulla_sha256=c572d56b7b32638118592f15bb2d8f2b8fb8509918b36dd1a2f3b1c6595ec403
dep_l20w_hiliq_sha256=a812b5506fcd9f05971088d856ae60344502586098fccbb3eccb46b594f25169
dep_l20w_fulla_sha256=acf9e9c39baa96c57476985eeae98386d5353706bf93510af7f5e65c83d17cdc
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
data_forecast_sha256=f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5
data_financials_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
tool_cmds_path=/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd
tool_cmds_sha256=
tool_closure_adj_price_sha256=93b54ae774651b3bf9c832f8c23d973893e446270eba92423767306c57d37849
tool_closure_panel_stitch_sha256=043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620
tool_closure_moneyflow_sha256=ca04507616030ccc789128bd1650b573ea934014ae6ed5e69dd90088386e943c
tool_closure_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
out_dir=/workspace/QuantLab/output/ai_factory/leaf23_sue_desens_cs
sensitivity_specs=sig-sue,denom-daily,nofc,bo40
serial_order=fund>build_HILIQ>build_FULLA>eval>sensitivities>leaf24
run_niceness=10
rss_limit_mb=1500
issued_at=
```

### 6.2 叶24 `output/ai_factory/ARCH_RUN_AUTH_LEAF24_IMAX_INTRADAY_X2.ok`
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=24
mechanism_tag=g1g5_ashare_imax_intraday_v1
scope=X2
window_start=2024-06-03
window_end=2026-10-09
allow_full=true
allow_smoke=false
allow_sensitivity=true
allow_sealed=false
live=false
promotion=false
promotion_approved=false
research_only=true
script_sha256=de87c839ec4e278d798d7789669b5e75dfc8e284399b590d38b9763d99d7ea47
prereg_sha256=c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8
cs_panel_dir=/workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
cs_panel_manifest_sha256=
cs_panel_build_version=cs_panel_v2_resumefix
data_mask_sha256=
dep_fe_sha256=2b49b10b1e79de49161190fd15aa0d705642aac94e21f5acda5d127b1ade916e
dep_selfcheck_sha256=ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe
dep_combo_sha256=bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c
dep_adg_sha256=a877cec51dbb96c75a6d071e222caf35f62fd14f101741a03be117e0e6076a97
dep_lc_sha256=218b61cfbf2bf0b6bb133ef030aa2d7ff20b3eafda9724aa98c9f3b1fa5cb054
dep_l18_hiliq_sha256=1a42f9e83d2e1c9accc64c01dccff334725a98d70c44692ec3cae5ec2d49e874
dep_l18_fulla_sha256=838c418779d5ecb69095c246928e5351334e183444f1b3308290850a029973c3
dep_l18v_hiliq_sha256=237e760c78abdeda8451486f554466bbc45c230dd3b1800583f7f8f5490d1939
dep_l18v_fulla_sha256=e942de2988dc8ce3864bbc417b8540f17f4f36da2d3e8741d3b20fbd743663d6
dep_l18w_hiliq_sha256=ed4dbf57953d84c0ef0470937fefded319fdd0bf97e87f3ce8ddc0faa68bea2a
dep_l18w_fulla_sha256=d158e41007d9274096810316141cacca1d90f6d34b49c7f2c6b1551609bc263f
dep_l18vw_hiliq_sha256=6002afab2f1214f183fca7f9064301daa272e1cc442a3d8f00bfe122a2fa6e54
dep_l18vw_fulla_sha256=ee68d5eb2d7ff5392eb5312294da6b0b73e4c5b8dbfc37564cc921a8b2cdfaef
dep_capadv600_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv600_nav_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
dep_capadv1000_tw_sha256=b010839dd1d7a0a218a00957a0cf99289bedc4511b0ed058c60e25351a7fb1a3
dep_capadv1000_nav_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
data_etf_daily_adj_sha256=48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
tool_cmds_path=/workspace/QuantLab/output/ai_factory/ARCH_TOOL_CMDS_LEAF24_X2.cmd
tool_cmds_sha256=
tool_closure_adj_price_sha256=93b54ae774651b3bf9c832f8c23d973893e446270eba92423767306c57d37849
tool_closure_panel_stitch_sha256=043fa68d4e6dd40f003db04fddfd79fb431c4a00f280a0a5db35cbe733d90620
tool_closure_moneyflow_sha256=ca04507616030ccc789128bd1650b573ea934014ae6ed5e69dd90088386e943c
tool_closure_nontextbook_sha256=8a56d13669b2820abc6b8757340a5774155581cdea854594ddffe058ed13c789
out_dir=/workspace/QuantLab/output/ai_factory/leaf24_imax_intraday
sensitivity_specs=src-total,k1,win60,exfin
serial_order=after_leaf23_complete>build_HILIQ>build_FULLA>eval>sensitivities
run_niceness=10
rss_limit_mb=1500
issued_at=
```
- 空值键在签发时必须填上；现在的解析器拒绝空值，所以这份草案原样不能用，这是有意的。
- 相对 b997cba8 §7 的变化：
  - 去掉所有 `*` 标注；
  - 新增 `data_mask_sha256`、`tool_cmds_path`、`tool_cmds_sha256`、`run_niceness`；
  - 删除 `tool_*_cmd`。
- `.cmd` 的内容由 Arch 在签发时写，当前计划如下：
  - `python3 research/leaf_selfcheck_v3.py --universe HI_LIQ_V1.1`
  - `python3 research/alpha_combo_marginal.py --universe hiliq --base capadv`
  - 具体的 alpha 路径参数，等主口径 eval 的 STAMP 出来后再定。

## 7. 顺带观察（不属本审范围，交给主 Agent 或 Data）
- 02:10 ET 在跑 `scripts/nightly_update.py --steps tier3`（142531，子进程 142545）。Data 重建 r3 的 P2-1 要求重建期间不跑写 raw 的 nightly 步骤。D1b execute 开跑前，门禁要确认这一点。

live=false；promotion=false。本审未建任何 .ok，未运行任何叶脚本或测试。
