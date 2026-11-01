# Arch 复审：Strategy LOTFIX v1.4 runner r3 + r4（含新 T、D21 r4）

- 复审时间：2026-10-18 03:02 ET；复审人：QuantLab Arch
- 基线：Arch r2 复审 docs/v2/ARCH_V1_4_RUNNER_REVIEW_R2_ZH.md（f9edf4a3，CONDITIONAL），r2 代码 246aa99（R 3df05b4b）
- 对象：r3 = ce45f3da（R 94643e27 / T 2ef7277a / D21 86c6f7bb / E 09dc431d）；r4 = 065cf63e + 336acd0f（只收 diff）
- 约束文件：CLARIFY-1 d075a2a6；CLARIFY-2 docs/v2/LOTFIX_V1_4_FREEZE_RECORD_APPENDIX_CLARIFY_2_ZH.md 85e843cd…651b（全文已读）；冻结规格 d921dd3f；冻结记录 0d47c52f
- 本次操作：只读、sha256sum、git show/diff、py_compile（cfile 写到 /tmp/arch_pc.pyc，已删）。没有运行 T、runner 或 D21，没有反序列化任何 pkl，没有 import 项目代码，仓库内没有产生 __pycache__。

## 0. 结论

**CONDITIONAL：P0 0 条，P1 1 条（P1-1），P2 2 条，P3 6 条。**
CLARIFY-2 的条款全部落实，sha/commit 都核对一致，没有发现前视、f 前缀或 pickle 不安全的问题。
但 T 新增了对 D21 模块的 import，而 DEPS 没有钉 D21（P1-1）。按 spec §2 和我对第（2）问的裁定，这正是被测进程里加载了未钉模块，所以本轮**不签 selftest .ok**。旧 .ok 33ef1df9 维持原样，不归档；它钉的是旧 T 和旧 R，对新 T 会被 enforce 拒绝。P1-1 修好后（一行改动，产生新的 T sha），我会直接签新的 selftest .ok。v1.4 和 D21 的运行 .ok 照旧不签，等 Leo 决定 Core 是否继续。

## 1. sha / commit 核对（全部一致）

| 项 | 申报 | 实测 |
|---|---|---|
| r4 diff STRATEGY_V1_4_r4_vs_ce45f3da.diff | 650b648a…0306 | 一致 |
| R optimizer_core_x2_run_v1_4.py | c844dbb4…43cd | 一致；combined（R,V,C）15fe0b78…26ca 已复算一致 |
| D21 optimizer_core_v1_3_basisC_recalc_d21.py | 497f9a2b…fc6f | 一致；combined（D21,R,V,C）ffa812fd…a416 已复算一致 |
| T test_v14_synthetic.py | d281916d…d9d9 | 一致 |
| E v1_4_snapshot_equiv_check.py | 09dc431d | 一致（未改） |
| V optimizer_core_v1_1.py / C optimizer_lambda_calib_sealed.py | b500c21b / 875daca9 | 一致 |
| 改动对照 STRATEGY_V1_4_RUNNER_CHANGES_ZH.md | 78ff073e… | 一致 |
| D21 说明 STRATEGY_D21_V1_3_BASISC_RECALC_ZH.md | 7ef2bd3a… | **不一致：提交版与工作区都是 db458d17…0852**（P3-1） |
| ckpt 清单 V13_CKPT_V1_3_POOLIND_SHA256.txt | 95831abf… | 一致；107 行，与目录 107 个 \d{8}.pkl 逐个 sha 相同，没有多余条目 |
| CLARIFY-2 | 85e843cd…651b | 一致 |
| 冻结规格 d921dd3f / 冻结记录 0d47c52f | — | 均未变 |
| core_x2/v1_4*、v1_3_basisC_d21 输出 | 不应存在 | 不存在 |
| ai_debate_memory_runner / g1g5_x2_panel_stitch | e1736d80 / 043fa68d | sha 一致，但**仍未提交**（P2-1） |

ckpt combined 的定义是：按文件名排序，每行 "name=sha\n" 拼接后取 sha256。实测结果恰好等于清单文件本身的 sha 95831abf，因为清单内容就是这些行。所以 .ok 键 v13_ckpt_combined_sha256 应当填 95831abf30e406264a1986a6c3055dd91bdb874a403065b97f3f5d1a5d8c45aa。

## 2. CLARIFY-2 逐条核对

| 条款 | 实现位置 | 结论 |
|---|---|---|
| §1.1 绝对 <24 升级 6% 单票帽，不按剩余天数换算 | R L1466 `below = nboth < S8_THRESHOLD`；L1497 动作文字含 LOTFIX §8 + CLARIFY-2 §1.1 | ✓ |
| §1.2 无数据日留在分母 29，记「不可证可行」 | R L1442–1464；denominator=S8_DENOM；unprov 列表；n_absent 计入 | ✓ |
| §1.3 单列日期与原因；ceil(0.8n) 对照只披露 | R L1467 `ctrl_thr=(4n+4)//5`，全文件只此一处计算；"below" 不进入 v100 和 v60_below | ✓。(4n+4)//5 = ⌈4n/5⌉ 对任意 n≥0 成立（恒等式 ⌈a/b⌉=(a+b−1)//b）；n=0..99999 已与 Fraction 精确上取整逐一比对 |
| §1.4 有效日 <29 不阻断；<24 直接升级 | judgeable=True；`valid_days_lt_24_direct_escalation` 进 v100 | ✓ |
| §1.5 两种算法同时输出，判定按本附录 | 两个字段都写入 summary；判定只用绝对门槛 | ✓ |
| §2.1 持仓沿用口径 A 决策，按口径 C 重判，作基线 | D21 replay(decide="A") 为 MAIN RESULT | ✓ |
| §2.2 口径 C 重新决策只作第二披露列 | replay(decide="C") 写入 *_Cdecision_disclosure_only.* | ✓ |
| §2.3 标签全等、权重差 ≤1e-6、手数相同，否则 VALID_WITH_DISCLOSURE | D21 repro_check：同时对 parquet 和 ckpt 比较（≤1e-6）、持仓集合相同、手数精确反推且成书日相同、ckpt 日 = 调仓日 | ✓（比条款更严，可以接受） |
| §3 运行 .ok 须等 Leo；D21 先于 v1.4 | 文档已写；代码不强制顺序 | 由 Arch 签发顺序把关（P3-3） |

我对第 (1)–(6) 问的裁定：
- (1) disclosure_missing 与 NO_DATA 分开计数，integrity_warning 只告警不阻断。R L1484/1491/1617 和 D21 summary 都按来源拆分。✓
- (2) panel_stitch 不在执行路径上：已亲自核对，见 §3。✓
- (3) T L463–477 的静态断言先核 C/V 的 sha，再查 6 个禁用词。R 不钉 sha，但 R 已由 enforce 的 DEPS 钉住。✓
- (4) 107 个 pkl 钉 sha，读字节、核 sha、从同一份字节反序列化，手数精确反推。✓，详见 §4。
- (5) AI 尚未提交，见 P2-1。
- (6) 新 T 已审，见 §5。

## 3. panel_stitch 调用链（亲自静态核对）

- C@875daca9 L142/L148：只在函数内懒加载 `_load_sw_members` 和 `sw_code_on`。
- 导入 nontextbook@8a56d136 时，模块顶层还会执行这些 import：quantlab.intel.debate_ledger、ai_debate_memory_runner、g1g5_wiring、g1g5_expand_g6，四个都在 11 文件闭包内。逐个 grep 过，四个文件的顶层都不 import panel_stitch。
- expand_g6 只在 L192/L490 的函数体内懒加载 panel_stitch。nontextbook 的 L114 位于 `_load_panel_features`，调用方只有 score_t1_overhang 和 score_limit_band（L281/L335）；L519 位于 run_nontextbook，调用方只有 main（L777）。v1.4 和 D21 都不调用这些函数。
- 兜底：end_of_run_recheck 会检查本进程已加载的项目模块，任何不在 code_files ∪ NT_CLOSURE_FILES 里的都触发 VOID。panel_stitch 一旦被加载，运行即作废，所以不需要把它钉进闭包。✓

## 4. D21 手数与 pickle

- **pickle 安全**：load_v13_ckpts 先读出全部字节，再逐个算 sha，汇总 combined 后与 .ok pin 比对，不一致就 RuntimeError，此时一个文件都没有反序列化。反序列化用的就是这份内存字节，不再重读文件，没有 TOCTOU 问题。preflight 只算 hash，不反序列化。运行结束前重算 combined。pickle 在 end_of_run_recheck 之前加载，所以反序列化如果引入了仓库模块，也会被已加载模块检查拦下。目录本身是符号链接、有非 \d{8}.pkl 条目或是空目录，都会拒绝。pickle 仍然会执行 pinned 字节里的代码，这是裁定 (4) 已接受的残余风险。
- **精确相等是否现实**：现实。lot_round_greedy（b500c21b L128）的写法是 q=np.floor(...)*L 加上若干次 +L，q 始终是精确整数的 float64，书权重 = (q*P)/aum。exact_lots 的写法是 np.float64(k)*L*P/a，左结合后同样是 ((k·L)·P)/a，运算顺序和操作数完全相同。P 两边都来自同一个 px 序列：D21 replay 用 px.astype(float) 存 pxs，lot_round_greedy 内部也是 float(p_)。a 是同一个整数。k 由 floor(x+0.5) 取得，x 与真实整数的偏差远小于 0.5，所以 k 唯一。T 用「偏一个 ulp」的用例验证了反推会失败。
- **误判 VALID_WITH_DISCLOSURE 的可能**：只有一种情况，就是 ckpt 成书时用的收盘价与 D21 重放读到的价不逐位相同（例如数据源在 v1.3 之后被改写）。但这种情况下 daily_basic 等输入 sha 本身就会变，preflight 会先拒绝。即便真的出现误判，后果也只是「解释前不得引用」，方向保守，可以接受。无价名（nopx）单独计数，不参与手数比较；BALLAST 跳过。✓
- **RSS**：ckpt 合计 1.4MB；pxs 约 107 日 × 约 5000 名的 dict，量级几十 MB，远低于 1.5GB。

## 5. 新 T 复审

- 只用合成数据。导入时先过 enforce，再做 _selftest_selfcheck：拒绝 BOM/CR；scope=selftest；allow_selftest=true，其他 allow_* 必须为 false；live/promotion=false；时间戳必须带时区，signed 不能在未来，不能过期；out_dir 只能是 mkdtemp 或 /tmp/<tag>，且不能在仓库内。路径隔离用 realpath 拦截对 data/ 和 output/ 的任何读写，以及仓库内的任何写入。✓
- 新增用例覆盖了：CLARIFY-2 已钉、错误 pin 被拒、常量为空被拒；3 天无数据（26/29，控制线 21）；6 天无数据压到 23<24 时升级，且控制线为 19 不改变判定；disclosure_missing 单条；与 NO_DATA 分开计数；ceil 参数化（n=0,4,5,9,14,19,29，含 5 的倍数这些边界）；D21 精确手数、偏 1 ulp、无价名、ckpt combined 定义、D21 白名单含 v13_ckpt 和 clarify2；静态禁用词。✓
- check_clarify2 在 T 中会读 docs/ 下的 CLARIFY-2，静态断言会读 research/ 源码文本。两者都不在 data/ 或 output/ 下，隔离允许。test_d21_* 不读任何 pkl。✓
- **P1-1 正是在这里发现的**：test_d21_exact_lots_and_ckpt_combined 执行了 `import optimizer_core_v1_3_basisC_recalc_d21 as D21`，但 DEPS（L38–43）只有 runner_v1_4、core_v1_1、calib_sealed、ok_runner_pin 四项。ok_runner_pin 只校验 runner 传进来的 deps，selftest .ok 里多写的键不会被校验。所以无论 .ok 怎么写，都绑定不了 D21 的字节。

## 6. 问题清单

### P1
- **P1-1 T 加载了未钉模块 D21。** 违反 selftest spec §2「每个被测模块一个 dep_sha256」，也违反裁定 (2)「闭包外模块作废运行」。修法：在 DEPS 中加 `"d21": ROOT / "research/optimizer_core_v1_3_basisC_recalc_d21.py"`，产生新的 T sha 后报给 Arch。selftest .ok 我会加 dep_sha256_d21=497f9a2b…fc6f。不要改动 R、D21 或 E 的字节。

### P2
- **P2-1** ai_debate_memory_runner（e1736d80）和 g1g5_x2_panel_stitch（043fa68d）仍是工作区未提交改动（裁定 5 由 AI 负责）。这不影响 selftest，但 AI 提交之前，v1.4 和 D21 的运行 .ok 都不签。
- **P2-2** D21 的 integrity_warning 汇总了三条路径（basisC、A 复现、C 决策披露列）。其中 C 决策列只作披露，它的 disclosure_missing 也会把顶层 integrity_warning 置为 true。这是保守做法，可以接受，但 summary 里 integrity_warning_by_source 必须保留，回执里要按来源报告。不需要改代码。

### P3
- **P3-1** D21 说明文档申报的 sha 是 7ef2bd3a，实测为 db458d17…0852（提交版与工作区相同）。下次回执请更正。该文档不在任何 .ok 里，不影响签发。
- **P3-2** n_absent（任何一档都没有行的调仓日）计入 disclosure_missing 和「不可证可行」，但因为日期未知，没有进入 not_provably_feasible_days 列表。可以接受，回执里需写明。
- **P3-3** CLARIFY-2 §3 要求 D21 先于 v1.4，代码不强制这个顺序。由 Arch 把关：D21 回执审完之前，不签 v1.4 运行 .ok。
- **P3-4** 同一天一袖 disclosure_missing、另一袖 NO_DATA 时，这一天只计为 disclosure_missing，NO_DATA 的明细保留在 reasons 里。这是保守做法，可以接受。
- **P3-5** research/_runner_archive/MANIFEST.md 在工作区有一条未提交的追加（01:59 hx2 条目，不是 Strategy 的改动），与本审无关，只在此记录。
- **P3-6** f 前缀扫描：r3 和 r4 新增行中，含 {…} 的字符串要么带 f 前缀，要么是 dict 字面量，没有漏写 f 的情况。

## 7. .ok 草案键数核对（不签）

- v1.4：11（format…equiv_script_sha256，含 expires_et）+ PINNED_DOCS 4 + clarify2_sha256 1 + 5（live/promotion/python_exe/out_dir/equiv_root）+ PINNED_INPUTS 21（DATA 7 + NT 闭包 10 + v1.3 权重 4）= **42** ✓
- D21：13 + PINNED_DOCS 4（lotfix/stoprule/clarify/clarify2；D21 不用 amend，合理）+ INPUT_KEYS_D21 23（PINNED_INPUTS 21 + v13_disclosure 1 + v13_ckpt 1；4 个权重键与 V13_WEIGHTS 同名去重）= **40** ✓
- 签发时的注意事项：
  1. v13_ckpt_combined_sha256 填 95831abf…45aa；
  2. clarify2_sha256 填 85e843cd…651b；
  3. nt_ai_debate_memory_runner_sha256 须等 AI 提交后复核（P2-1）；
  4. 先签 D21，审完 D21 回执后再签 v1.4（P3-3）；
  5. 两份都等 Leo 决定 Core 去留。

## 8. 下一步

Strategy 修 P1-1，报新的 T sha → Arch 签新的 selftest .ok（同路径，旧 33ef1df9 归档到 _superseded/）→ Strategy 跑 T，回执交 Arch 审。
