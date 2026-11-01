# Arch 审查：Strategy 申万行业 as-of 修复 DIFF B r2

- 审查时间：2026-10-18T05:56:33-04:00（`date +%Y-%m-%dT%H:%M:%S%:z`）
- 审查人：QuantLab Arch。只做静态审查。没有运行项目代码或测试，没有 import 项目模块，没有写 .ok，没有给任何人发消息。真实数据只用普通 pandas 只读统计。
- 上一轮审查：docs/v2/ARCH_STRATEGY_SW_PIT_ASOF_FIX_REVIEW_ZH.md（3f195231）。
- 提案：docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018_r2.diff，sha256 d0fb1d3faa6962d19e8405280975e8818766ef406b00f390edcc9b02f81ee250，692 行。实测一致。
- 审查副本：`git archive HEAD`（HEAD 263be32）解包到 /tmp/arch_r2，再 apply r2。没有用 /tmp/swr5。

## 结论：PASS。P0 无，P1 无，P2 无，P3 9 条

4 条 P2 都修好了。主 Agent 05:45 的裁定按字面实现正确。纸面轨不受影响。
d−1 取自然日还是交易日，我建议取“上一个上交所交易日”（见第 3 节）。这条对本次 B4 对照的数值没有影响（实测 0 个持仓代码日不同），所以不阻塞本次签字。但必须在 Intel 下一轮调用这个公共函数之前改掉，单独出 diff。

## 0. 事故自报（Arch 自身流程问题，请主 Agent 记录）

- 05:50:42 ET，我构建副本的命令写错了：`git archive ... | tar` 失败后，`&&` 链断开，后面的 `git init -q .`、`git apply` 在 /workspace/QuantLab 里执行了。结果 r2 diff 被误 apply 到了正式仓库。
- 05:51:18 ET，我用 `git apply -R` 原样撤回。撤回后：
  - hx2 sha 回到 1c51531a…，fulla 回到 7bd657ed…，`git status` 对这两个文件是干净的；
  - sw_members_asof.py、test_sw_members_asof.py、PREREG 三个新文件已删除；
  - `git init -q` 是对已有仓库的重新初始化，.git/config、HEAD 都没变。
- 窗口内（约 36 秒）没有任何进程 import 或运行 hx2、fulla（05:51:11 ps 核对）。没有生成 pyc。
- 留下的痕迹：hx2 和 fulla 的 mtime 变成了 05:51:18；research/、research/tests_sw_pit/ 两个目录的 mtime 也变了。任何 T0 早于 05:51:18 的 `find -newermt T0` 回执都会看到这几项。它们是我造成的，不是被审方写的。内容已恢复，sha 可核。
- 我没有改回 mtime，以保留证据。

## 1. 落地后 sha（Arch 自算，与申报一致）

| 文件 | old（HEAD 263be32） | new（r2 落地后） |
|---|---|---|
| research/strategy_hiliq_capadv_b4_x2.py（hx2） | 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45 | 1728c12666af87ece9c5a76486c279e3f3b0f7868ef027464a6ea21f6b2695a2 |
| research/strategy_fulla_b4_x2.py（fulla） | 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316 | 88b6f36746ecf2e062d78fe67f390f1c6d8d886a85f660a527d44910cd7ff824 |
| research/sw_members_asof.py | 新文件 | 0444d9d6f6b66195d19a91cf9c45e53ed0cb715b81b2a595c1388a47ecc2e945 |
| research/tests_sw_pit/test_sw_members_asof.py | 新文件 | 4f468b482613329912e82ab71b2bd4c0d062efdc4451d508e16e21812eeb3ffb |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 新文件 | c2b37127772bdb792cd4f85851c47325fbe9a13794cb99ecbb2c374de8d1003c |
| research/sw_pit_freshness.py | 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f | 不改 |

apply 时 git 只报了一条空白警告：hx2 末尾多一个空行。

## 2. 4 条 P2 核对

### P2-1 out_date 解析失败 ✔
- prep_sw 先记下原值是否非空（非 NaN 且去空格后不为空串），再 `to_datetime(errors="coerce")`。
- `n_out_unparsed` = 原值非空且解析后为 NaT。大于 0 就抛 SwPitIntegrityError。真正的空值单独计为 n_out_null。
- in_date 解析失败计为 n_in_unparsed，写进 stats，经 reclass_share 披露为 n_in_unparsed_table。这些行在主规则下永不命中。
- 真实表上：两类解析失败都是 0，行为不变。
- 小问题见 P3-2：空档沿用那条路径没有排除 in_date 为 NaT 的行。

### P2-2 out_dir 保护 ✔
- pitfix_out_dir_guard：base 和 out_dir 都 `resolve()`，所以符号链接会被解析。
- 必须在 ROOT/output/strategy_hiliq/ 之下，不能是这个目录本身。
- 第一层是 b4、capadv_x2、legs 时拒绝。任一层名字含 paper 或 frozen（不分大小写）时拒绝。
- 已存在（含悬空链接）时拒绝。
- 顺序：guard → 腿文件存在 → check_sw_l1_pin（显式 raise）→ load_leg → load_industry_map → load_industry_asof → as-of 加载 sha 再核一次 → `mkdir(parents=False, exist_ok=False)`。mkdir 之前没有任何写入。sw_pit_freshness 只读不写，已核。
- 导入 hx2 时的 `OUT.mkdir(exist_ok=True)` 对已存在的 output/strategy_hiliq 是 no-op，与上一轮相同。
- 因为 out_dir 在 ROOT 之下，run_smoke 里的 `relative_to(ROOT)` 不会再半路报错。output/strategy_hiliq 不是符号链接，已核。

### P2-3 成败判定 ✔
- run_smoke：要求 returncode == 0，summary 的 mtime ≥ 子进程启动时刻，且若原来就有 summary，新 mtime 必须更大。否则 ok=False。
- _arm_ok：ok、returncode==0、summary_fresh、无 error、cagr 和 mdd 都不为 None，全部满足才算成功。
- 任一 arm 失败：summary.json 写 all_ok=false，写 VOID.md，返回 1，`raise SystemExit(1)`。
- **副作用追踪（hx2 run_smoke 和 main 的所有调用方）：**
  - hx2 自己：main 第 539 行（capadv）、第 576 行（B4），以及 pitfix_compare。main 里失败分支原本就存在，判定只是更严。本次不授权重跑 main。
  - optimizer_core_x2_run.py 第 382 行：仍在 phase_smoke 的 `raise SystemExit` 之后，是死代码。
  - tie-sens（strategy_capadv_topn_tie_sensitivity*.py、strategy_tie_sensitivity_prereg_v1.py）用的 `lr.run_smoke` 是 strategy_b4_hiliq_leg_review.py 自己的 run_smoke，不是 hx2 的。leg_review 也有自己的 run_smoke。它们只用 hx2 的 load_industry_map、_is_etf，这两个都没变。
  - 纸面轨：quantlab/portfolio/b4_paper.py 有自己的 _run_smoke，不 import hx2，读的是 output/small_aum_concentration/v2/ 的权重。全仓库（research/、scripts/、scripts_eng/、quantlab/）没有别的地方 import hx2 或调用它的 main。crontab 为空。
  - **结论：纸面轨和 10-19 17:40 ET 的纸面运行都不受影响。无 P1。**
  - 提醒：alpha_combo_marginal_v1_1 读 output/strategy_hiliq/b4/B4_50_25_25_topN_{60w,100w}.parquet。hx2 main 如果重跑会覆盖它们，所以 main 仍然不得在没有 .ok 的情况下重跑。pitfix_compare 只读这两个文件做比对，guard 也挡住了写入 b4/。

### P2-4 load_industry_map 原样保留 ✔
- 用 AST（去掉注释后）比较基线和 r2 的函数体：完全相同。只多了两行注释。
- apply_ind_cap、extract_arm、load_leg 也逐一比较，完全相同。main 只改了一行（load_industry_map → load_industry_asof）。

## 3. 主 Agent 05:45 裁定：sw_l1_asof_with_gap_carry

- 主规则：`in_date < d` 且（out_date 为空或 `out_date >= d`），d 先 normalize。✔
- 空档沿用：d 日没有有效行时，找 out_date == d − 1 自然日的旧行；有多条时按同样的去重顺序取一条；只沿用当天。其余情况为 None（_UNK_）。✔ 按字面实现正确。
- 披露：n_rows_gap_carry、share_rows_gap_carry、n_rows_unknown、全表 n_reclass_gap_rows、n_rows_multi_match、n_codes_overlap_on_d。✔
- 依赖：hashlib、io、pathlib、numpy、pandas，以及 research.sw_pit_freshness 的 SwPitIntegrityError。sw_pit_freshness 自己只用标准库和 pandas。✔ 不依赖 hx2、fulla。

### d−1 取自然日还是交易日（真实数据统计）

数据：sw l1 表 0b1d3432…，trade_cal_sse_pit fa4260b8…（日历覆盖 2005-01-01..2026-12-31）。
口径：每个代码按 (in_date, 行序) 排序，相邻两行且前一行 out_date 非空，算一次“变更”，共 1912 次（其中 400 次是新 in_date ≤ 旧 out_date 的重叠，没有空档）。
“空档交易日”指 (旧 out_date, 新 in_date] 里的交易日。

- 全表：
  - 新 in_date = 旧 out_date + 1 自然日：1088 次（代码里的 n_reclass_gap_rows 在这张表上也应是 1088）。
  - **间隔大于 1 个自然日、中间只隔着非交易日：315 次。其中新 in_date 是交易日的 303 次（旧 out_date 也都是交易日），这 303 次都会产生 1 个空档交易日。** 另 12 次新 in_date 本身是非交易日，没有空档。间隔分布：2 天 13 次，3 天 182 次，4 天 37 次，5 天 30 次，10 天 40 次，其余零星。
  - 至少有 1 个空档交易日的变更：1482 次。自然日规则能沿用 1146 次，交易日规则能沿用 1480 次。多出的 334 次全是周末或节假日造成的。没有哪一次是自然日规则能沿用、交易日规则不能的。
  - 109 次变更有 2 个以上空档交易日，两种规则都只沿用第 1 天，其余天归入未知。
- X2（2024-06-03..2026-10-09）：
  - 第一个空档交易日落在 X2 的变更：227 次。自然日规则沿用 208 次，交易日规则沿用 227 次，差 19 次。
  - 这 19 次里，17 次是 2025-08-08（周五）出、2025-08-11（周一）进，1 次是 2025-11-28→12-01，1 次是 2024-05-31→06-03。按自然日规则，2025-08-11 这一天会有 17 个代码同时变成未知行业。
- B4 三条腿 X2 内非 ETF 持仓 (代码, session)：34100 个。不沿用时未知 2500 个；两种规则都只沿用 1 个，未知 2499 个。**两种规则结果不同的持仓代码日：0。**

**建议：d−1 解读为“上一个上交所交易日”。**
- 理由：主 Agent 原意是“最多沿用 1 个交易日”。自然日规则在每个周一和节后第一天系统性失效，全表 303 次、X2 19 次，而且会集中出现（2025-08-11 一天 17 个）。交易日规则覆盖了自然日规则的全部情况，没有反例。
- 实现要求：交易日历作为参数传进公共函数（钉 sha），模块仍只依赖 stdlib/numpy/pandas；d 超出日历覆盖范围时 raise，不得退回自然日。日历只到 2026-12-31，续期已交 Data（11-30 前）。
- 时点：本次 B4 对照两种规则数值完全相同，所以按 r2 的自然日实现签本次 .ok，并在 summary 披露“d−1 按自然日；B4 X2 持仓上与交易日口径差 0”。交易日版本单独出 diff，必须在 Intel 下一轮调用前落地。需要主 Agent 确认。

## 4. 去重顺序

- 实现：有效行按 (in_date, _pri, _ord) 升序，取最后一条。_pri = 2×(is_new=="Y") + (out_date 为空)，所以 is_new=Y 优先，其次 out_date 为空，再其次文件行序。与申报一致。✔ l1_static_last 和空档沿用也用同一顺序。
- 真实表，全部 5600 个代码 × X2 的 570 个交易日，共 3,192,000 个代码日：
  - 有多条有效行的代码日 8539 个；
  - 新顺序与“in_date 最新、再按行序”相比，**不同的代码日：0**。B4 腿持仓的 34100 个代码日上也是 0。
  - 所以 is_new / out_date 空这两层只在 X2 外或 in_date 相同但行业相同的地方起作用，本次不影响数值。

## 5. 测试

- test_sw_members_asof.py：11 个用例（11 个 def test_，没有 parametrize）。test_sw_pit_freshness.py：10 个 def，其中 1 个 parametrize 3 组，共 12 个。**合计 23。** ✔
- 只用内存 DataFrame 和 tmp_path，不读真实数据，不联网。✔
- Intel 函数副本：与当前 research/intel/intel_common.py（25f23dff）第 309–313 行的 sw_members_asof 逐字一致，只省略了 docstring。也与 _review/intel_sw_pit_freshness_20261018_r2.diff（0e968759）第 90–94 行一致。✔
- 夹具覆盖：重叠（O.SZ，旧的未结束行排在后面）、in_date 相同（T.SZ，is_new 决胜，并把文件倒序再测一次）、空档（G.SZ 沿用、H.SZ out_date = d−2 不沿用、Z.SH 无后继）、out_date 解析失败抛错、in_date 解析失败计数、by_session、reclass_share、out_dir guard。✔
- 逐个手推了 11 个用例的预期值，都与实现一致（未运行）。
- 缺口见 P3-5。

## 6. Prereg c2b37127

- 命令写了完整解释器 `/workspace/qlvenv/bin/python`，加 PYTHONDONTWRITEBYTECODE=1 和 nice -n 10。✔
- 改前组：写明原样保留 load_industry_map，与代码一致（AST 相同）。✔
- 成败判定、VOID、out_dir 保护、披露项与代码一致。✔
- 小问题见 P3-4。

## 7. 静态检查

- pyflakes（`PYTHONPATH=/tmp/pf python3 -m pyflakes`）：只有基线就有的两条（hx2 charts2、fulla nav_path），行号挪了。新文件 0 条。✔
- 漏 f 前缀：用 AST 扫了 4 个文件里所有非 f-string 的字面量，没有带 `{name}` 的。✔
- `max(..., default=)`：没有。
- off-by-one：in_date 严格 `<`，out_date `>=`；X2 两端闭区间；空档条件 `out_date == d − 1 天`。✔
- assert 用作检查：新代码没有。pitfix 路径上仍有基线就有的 build_topn 权重和断言（第 214 行）和 main 的腿存在断言。命令不带 -O，可以接受（P3-6）。
- PIN 校验改成了 raise。✔

## 8. 文档快照

- docs/v2/audit/snapshots/ 下：tie-sens 快照 00e63f98…，leg_review 快照 dc28262a…，sha 都对，文件只读。✔
- 现行文档：tie-sens ad0639fb…，leg_review 4df5550d…。与快照 diff：各只多了第 3 行横幅“行业映射存在前视，待修”和一个空行。✔
- 这两份文档不在 git 里（HEAD 中不存在），只能靠快照留证。

## 9. 写 summary 前就抛异常时没有 VOID.md

- 建议定为 **P3（可选）**，不作 P2。
- 理由：
  - out_dir 是新建的隔离目录，没有 summary.json 就没有可引用的汇总数值；
  - 未捕获的异常会让 Python 以非 0 退出；
  - 被 OOM 或 SIGKILL 杀掉时，try/finally 也写不了 VOID，所以无论如何都需要外部规则兜底。
- 要求写进 run .ok：退出码非 0，或者没有 summary.json，或者 all_ok 不为 true，都算 VOID，由 Strategy 手写 VOID.md，并在回执里附退出码和 run.log 末尾。
- 下一轮可加 `try/except BaseException` 写 VOID.md 再 re-raise，作为改进。

## 发现

### P0 / P1 / P2
无。

### P3
- **P3-1：d−1 口径。** 建议改为上一个上交所交易日（第 3 节）。本次数值无影响。交易日版本单独出 diff，在 Intel 调用公共函数之前落地。需主 Agent 确认。
- **P3-2：空档沿用路径的两个小口子。**
  - (a) 没有排除 in_date 为 NaT 的行。in_date 解析失败的行如果 out_date == d−1，会被沿用，和“永不命中”的说法矛盾。当前表上为 0。修法：沿用候选加 `in_date.notna()`。
  - (b) 沿用不要求有后继行。docstring 写的是“new in_date = old out_date + 1 的情况”，代码其实对所有 out_date == d−1 都沿用，包括退出申万、没有新行的代码（全表 46 个这样的退出，次日是交易日的 37 个，X2 内 1 个）。这符合主 Agent 裁定的字面意思，但 docstring 和 prereg 要改成一致的说法，并单独披露“无后继沿用”的次数。
- **P3-3：VOID on exception。** 见第 9 节。本次靠 .ok 条款兜底。
- **P3-4：prereg 里的数字。** prereg 第 4 节引用“1545 次变更中 1109 次”，那是 r1 审查时的口径。按代码 prep_sw 的定义，这张表上应是 1088。summary 以代码算出的 n_reclass_gap_rows 为准，prereg 注明“r1 口径，仅供参考”。
- **P3-5：guard 测试不全。** 没测符号链接指向 b4 的情况，也没测 capadv_x2、legs。代码是对的（resolve 后再判断），但应补用例。另外，多层且父目录不存在的 out_dir（如 new/sub）会在所有检查之后、mkdir 时报 FileNotFoundError，没有写入，可以接受。
- **P3-6：基线遗留的 assert。** build_topn 的权重和断言、main 的腿存在断言，在 `python -O` 下会失效。不在本次改动范围，命令不带 -O。下一轮改成 raise。
- **P3-7：hx2 main 判定更严。** 只影响 hx2 main 自己。main 重跑会覆盖 output/strategy_hiliq/b4/，而 CMC v1.1 读这两个文件。重申：没有 .ok 不得重跑 main。
- **P3-8：空白。** hx2 末尾多一个空行，git apply 有警告。不影响功能。
- **P3-9：和叶 23 错开。** pitfix 对照与叶 23 都靠 `find -newermt T0` 做写入回执，也都有 1.5GB 的 RSS 预算。建议叶 23 全部跑完、Arch 审过回执之后再跑 pitfix，不要并行。

## 签 .ok 用的材料

### (1) code-change .ok
- diff：docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018_r2.diff，sha256 d0fb1d3faa6962d19e8405280975e8818766ef406b00f390edcc9b02f81ee250。
- 落地方式：`cd /workspace/QuantLab && git apply --check <diff> && git apply <diff>`。apply 前逐个核对 old sha，apply 后核对 new sha（工作区、.ok 两方一致；若授权提交，再核 git）。
- 目标：

| 文件 | old | new |
|---|---|---|
| research/strategy_hiliq_capadv_b4_x2.py | 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45 | 1728c12666af87ece9c5a76486c279e3f3b0f7868ef027464a6ea21f6b2695a2 |
| research/strategy_fulla_b4_x2.py | 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316 | 88b6f36746ecf2e062d78fe67f390f1c6d8d886a85f660a527d44910cd7ff824 |
| research/sw_members_asof.py | 不存在 | 0444d9d6f6b66195d19a91cf9c45e53ed0cb715b81b2a595c1388a47ecc2e945 |
| research/tests_sw_pit/test_sw_members_asof.py | 不存在 | 4f468b482613329912e82ab71b2bd4c0d062efdc4451d508e16e21812eeb3ffb |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 不存在 | c2b37127772bdb792cd4f85851c47325fbe9a13794cb99ecbb2c374de8d1003c |

- 不变项（前后都要核）：research/sw_pit_freshness.py 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f。
- 旧文件归档到 _recovery/strategy/sw_pit_asof_pre_r2_20261018/，只读，附 SHA256SUMS。py_compile 只编译到 /tmp，用完删除。
- 落地后，所有钉 hx2 sha 的 .ok 都要按 1728c126 重签（tie-sens 的 dep_hx2_sha256 已过期）。

### (2) selftest .ok
- 解释器：/workspace/ql-enrich-venv/bin/python（pytest 9.1.1、pandas 3.0.6、numpy 2.5.3）。
- 运行前：basetemp 目录 /tmp/arch_swpit_asof_r2_selftest 不存在；两个测试文件 sha 等于 4f468b48… 和 cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e。
- 命令（只跑一次）：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/arch_swpit_asof_r2_selftest research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py > "$R/stdout.txt" 2> "$R/stderr.txt"; rc=$?; echo "$rc" > "$R/exit.txt"`
  其中 R=docs/v2/audit/strategy_sw_pit_asof_r2_selftest。不准接 `|| true`，不准用管道，rc 必须在命令后立刻取。
- 预期：23 passed，exit 0。
- 运行后：删除 basetemp；research/ 下没有新的 __pycache__ 或 .pytest_cache。

### (3) pitfix-compare 运行 .ok
- 前提：(1)(2) 已通过并经 Arch 审过回执；叶 23 已全部结束并审过；d−1 口径按本文第 3 节由主 Agent 确认“本次按自然日、交易日另出 diff”。
- 解释器：/workspace/qlvenv/bin/python（Python 3.12.14，装有 matplotlib）。book-smoke 子进程用 sys.executable，同一解释器。
- 命令（只跑一次）：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/strategy_hiliq_capadv_b4_x2.py --pitfix-compare output/strategy_hiliq/pitfix_compare_20261018 > "$R/stdout.txt" 2> "$R/stderr.txt"; rc=$?; echo "$rc" > "$R/exit.txt"`
  R 为回执目录，不得放在 out_dir 里。
- out_dir：output/strategy_hiliq/pitfix_compare_20261018/。05:55 ET 核对时不存在，运行前必须仍不存在。
- 输入钉（运行前逐个核对）：
  - data/v2/sw_pit/industry_members_sw_l1_pit.parquet：0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6
  - data/v2/sw_pit/manifest.json：7c73e70b152126d5a37ee9a002c55dd6a7542a7ae0519152c720a7384436d282
  - data/v2/calendar/trade_cal_sse_pit.parquet：fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41
  - output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet：3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
  - output/strategy_hiliq/legs/g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet：6bb3b3f3160eafce410079ac49203faed609f9d722a55b9ef6f15c82af6d69e0
  - output/strategy_hiliq/legs/g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet：c4b93255b694adb9b0484e55413abf80072be1e48d750e25a39dc4e37917b5e2
  - quantlab/platform/execution.py：373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c
  - quantlab/platform/__init__.py：bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
  - quantlab/portfolio/book_smoke.py：1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b
  - quantlab/cli.py：9e3ee7d1d76f90c187ab6878addf3fac3182473cdfc3c31746ab4cdbdcbd8b3e
  - research/strategy_hiliq_capadv_b4_x2.py：1728c12666af87ece9c5a76486c279e3f3b0f7868ef027464a6ea21f6b2695a2
  - research/sw_members_asof.py：0444d9d6f6b66195d19a91cf9c45e53ed0cb715b81b2a595c1388a47ecc2e945
  - research/sw_pit_freshness.py：5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f
  - docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md：c2b37127772bdb792cd4f85851c47325fbe9a13794cb99ecbb2c374de8d1003c
  - 只读比对用（不是门槛，但要记 sha）：output/strategy_hiliq/b4/B4_50_25_25_topN_60w.parquet ca77bc8cf05a8cc5665a0532ce5221e05f3d0431cf87ee614c7779064cad627a；…_100w.parquet f75ace33da3e919e799ee1e63fd141ed6d34b3b2a509d7bdf7659ab05849e315
  - book-smoke 读的行情和公司行为数据沿用 book-smoke 现有的钉住方式。
- 会写入：out_dir 下 4 个权重 parquet、4 个 smoke_{arm}_{60,100}w/ 目录、summary.json，失败时还有 VOID.md。别处不得有新文件。
- VOID 条款：exit ≠ 0，或没有 summary.json，或 all_ok ≠ true，都算 VOID；Strategy 手写 VOID.md，附退出码和 run.log 末尾；数值一律不得引用。
- 披露条款：summary 和报告写明“d−1 按自然日；B4 X2 持仓上与交易日口径差 0（Arch 实测）”，标题行带 disclosure_zh（sw_pit stale）。
- 预计耗时：约 2–4 分钟（4 次 build_topn 加 4 次 book-smoke，每次 15–25 秒；as-of 查找表约 4 万对，额外开销可忽略）。
- 预计 RSS：父进程约 0.7–0.9 GB，book-smoke 子进程约 0.4–0.6 GB，各自都在 1.5 GB 以内。挂 1.5 GB 守护；summary 里的 peak_rss_mb_self / peak_rss_mb_children 要写进回执。05:55 ET 机器可用内存约 10.9 GB。
- 跑完：`find -newermt T0` 只允许 out_dir 和回执目录有新文件；execution.py、__init__.py 的 sha 不变（10-19 17:40 ET 纸面运行前不得改动）；research/ 下没有新的 pyc。

## 附：Arch 误写仓库事件（P2，主 Agent 06:01 定级）

- 记录时间：2026-10-18T06:01:24-04:00
- 经过：05:50:42 ET，r2 diff 被误打进真实仓库；05:51:18 ET 用 git apply -R 还原。
- 受影响条目及其当前 mtime：
  - research/strategy_hiliq_capadv_b4_x2.py：05:51:18
  - research：05:51:18
  - research/tests_sw_pit：05:51:18
  - research/strategy_fulla_b4_x2.py：05:51:18；还原后 sha 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316

- 还原后的 sha：
  - 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45  research/strategy_hiliq_capadv_b4_x2.py

- 处理口径：凡是 newermt 回执里出现 05:50–05:51 的上述条目，都认定是 Arch 造成的。
- 整改：静态审一律在 /tmp 下用 set -e，先 cd 进去并确认成功，再做 git apply。
- d−1 的口径：按上一个 SSE 交易日（主 Agent 06:01 裁定）。本次 pitfix 先按日历日版本跑，并披露 208/227 和 B4 差异 0。交易日版本单独出 diff。
