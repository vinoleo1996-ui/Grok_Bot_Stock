# Arch 审查：Strategy 申万行业 as-of（PIT）修复（DIFF B）

- 审查时间：2026-10-18T05:40:19-04:00（`date +%Y-%m-%dT%H:%M:%S%:z`）
- 审查人：QuantLab Arch。只做静态审查：没有运行项目代码或测试，没有改动 research/、scripts/、data/，也没有写 .ok。真实数据只用普通 pandas 只读统计，没有 import 任何项目代码。
- 提案：docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018.diff，sha256 98633d9bb05eb1a034b26108e870b3387e487e3bbe4f2de5aa72a5e1cc55c346，428 行。实测与申报一致。
- 基线：commit 7dd5bea5。

## 结论：CHANGES REQUIRED（需交 r2）。P0/P1 无，P2 4 条，P3 7 条

as-of 口径本身是对的，hx2 的接入方式也是对的。阻塞点在两处：`--pitfix-compare` 这个运行入口缺少安全和成败判定；out_date 解析失败被静默当成“仍在成分”。r2 修完 4 条 P2 后，本文所列 sha 作废，需要重新计算并重审。r2 只需重审变化部分。

## 落地后 sha 核对（Arch 自算；作废前仅供参考）

两种顺序（先 A 后 B、先 B 后 A）都能干净 apply，结果逐文件 sha 一致，也都和 Strategy 申报的一致。

| 文件 | old（7dd5bea5） | new（B 落地后） |
|---|---|---|
| research/strategy_hiliq_capadv_b4_x2.py（hx2） | 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45 | c8728e494fd9d5fcc2499af756537d8b9f2052c4ceee48ceb5f72a21a3ffac5c |
| research/strategy_fulla_b4_x2.py（fulla） | 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316 | dd5774c5c0d52473964ec64f11496f3f5b6e95b7e99d8c74c866f6c28ea5f453 |
| research/sw_members_asof.py | （新文件） | d87356dca30e4b33acd4d9d34838c29c9559e46f6ba9d53308e3bdfa62eb527f |
| research/tests_sw_pit/test_sw_members_asof.py（实际路径就是这里） | （新文件） | b05b78621db3f8ff0ca2d361846122583a850275e2931f5f0d9d1db254ecd208 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | （新文件） | d1bb4603f2620ea9c049d9a34f099752d4b72237439a078a79b50f8414be0e56 |

## 真实 l1 表统计

数据：data/v2/sw_pit/industry_members_sw_l1_pit.parquet，sha 0b1d3432…89f6，7573 行，5600 个代码。

- **解析失败**：in_date 和 out_date 在 parquet 里已经是 datetime64[us]。in_date 解析失败 0 行；out_date 真空值 5566 行，非空却解析失败 0 行。所以 coerce 在当前这份表上没有实际影响，问题只在今后换表时的健壮性。
- **区间本身**：in_date > out_date 的 0 行，in_date == out_date 的 0 行。
- **重复**：三列 (ts_code, in_date, out_date) 完全重复 4 行；(ts_code, in_date) 重复 13 行。
- **重叠**：按规则 in_date < d ≤ out_date，有 **476 对**区间重叠，涉及 **423 个代码**，其中 254 对行业名不同。与 X2 窗口相交的有 22 对，其中 15 对名字不同。另有 **12 个代码**同时存在多条 out_date 为空、但行业名不同的记录。
- **文件行序**：508 个代码的行序不是按 in_date 递增排的，所以“文件里最后一行”和“in_date 最新一行”不是一回事。
- **两种取重规则的差异**：在 X2 的 570 个交易日里，“in_date 最新”和 Intel 的 `keep="last"`（按文件行序）有 **1209 个代码日**结果不同，涉及 4 个代码：000639.SZ、002481.SZ、003030.SZ、688002.SH。逐行看过，这几处都是旧行业留下的一条 out_date 为空的残留行；按“in_date 最新”取到的是正确的新分类，例如 002481.SZ 在 2021-07-30 以后应为农林牧渔，688002.SH 在 2026-08-21 以后应为电子。**裁定：采纳“in_date 最新”**，Intel 那边需要对齐（见 P3-5）。
- **as-of 与静态映射对比**：取 B4 三条腿 X2 内的非 ETF (code, session) 对，共 34100 个。
  - as-of 取不到行业的有 2500 个；静态映射取不到的有 2023 个。
  - 其中 **477 个是 as-of 取不到、静态映射却有值**。原因几乎全部是 sw 表缺少这些代码当前的成分行，例如 000592.SZ 唯一的一行在 2009-09-30 就结束了。也就是说，旧的静态映射一直在用 2009 年的分类。只有 1 个是改分类当天 in_date == d 造成的空档。
  - 两种映射结果不同的共 963 对（占 2.8%）。
- **静态映射的新旧实现**：旧 load_industry_map 和新 l1_static_last 在 5600 个代码里有 **2 个结果不同**：
  - 600650.SH：新实现会取到 2004 年就已结束的「社会服务」，这是错的；
  - 300858.SZ：两条记录 in_date 相同，旧实现取一条，新实现按行序取另一条。
  这 2 个代码不在任何一条 HI_LIQ 腿里（6 个腿文件都查过），所以对 B4 的数值没有影响。

## 逐项核对（hx2 / fulla / prereg）

1. **as-of 规则**：`in_date < d` 且（`out_date` 为空或 `out_date >= d`），d 先 normalize 到当天零点。`sw_members_asof` 和 `l1_asof` 用的是同一个口径。单测覆盖了 in_date == d 时排除、out_date == d 时包含。✔
2. **build_topn**：传入 IndustryAsOf 时，先用 `by_session` 为所有共同 session 预先算出 {session: {code: l1}}。每个 session 依次做单票上限、取 `im = lut.get(s, {})`，然后进 `apply_ind_cap(agg, im)`，最后统计最大行业占比时用的也是同一个 im。✔
3. **无前视**：腿文件里的 session 是决策日，book-smoke 用 strategy_v1 在次日开盘成交，所以 d 就是决策日。in_date 当天上海 18:00 才发布，严格 `<` 保证决策时只用到前一交易日及以前已发布的分类。✔
4. **SW_L1_SHA_PIN**：值为 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6，和真实文件一致。`assert_sw_l1_pin` 只在 pitfix_compare 里调用。用的是 assert，在 `python -O` 下会失效（见 P3-6）。
5. **--pitfix-compare**：在 60万（N=6）和 100万（N=10）两档，旧映射（before_static）和新映射（after_asof）各跑一次，共 4 次 build_topn 加 4 次 book-smoke。报告的指标有 cagr、mdd、calmar、日胜率、月胜率、cost_pct、n_ind_cap_sessions_x2、ind_cut_mean、max_ind_sleeve_share_after、reclass_share_x2，以及权重文件的 sha。✔ 但成败判定和输出目录都有问题，见 P2-2、P2-3。
6. **默认路径和现有调用方**：
   - hx2 的 main() 改成了用 load_industry_asof。这是本次修复的本意，但 hx2 main 如果重跑，产物会变；本次不授权重跑。
   - `load_industry_map()` 的签名没变，但实现换成了 l1_static_last，有 2 个代码的结果不同（见上）。
   - tie-sens 和 leg_review 仍走静态映射加 `apply_ind_cap(dict)`，前视偏差还在。
7. **optimizer_core_x2_run.py**：只在第 382 行 `from strategy_hiliq_capadv_b4_x2 import run_smoke`，而且这一行位于 `phase_smoke` 里 `raise SystemExit` 之后，是执行不到的死代码。run_smoke 本身没改。即使以后恢复这段，导入时多出来的也只是 `research.sw_members_asof`（hx2 会自己把 ROOT 加进 sys.path）。结论：行为不变。✔
8. **fulla**：只改了 smallcap_and_industry 里的行业占比和 reclass 披露。删掉的 `lookup` 原本就是没人调用的死代码。fulla 没有行业上限，权重和 NAV 都不受影响，确实只影响披露。✔
9. **prereg 与代码是否一致**：
   - 窗口 X2 = 2024-06-03..2026-10-09 ✔
   - B4 = capacity_adv/earnings_event/insider_increase 按 0.5/0.25/0.25 ✔
   - N_BY_AUM {600000: 6, 1000000: 10} ✔
   - 单票上限 CAP = 0.06 ✔，行业上限 IND_CAP = 0.25 ✔
   - book-smoke 用 run_weight_schedule + ExecConfig.strategy_v1：next_open、按 tick 取整、k = 1.0、参与率 10%、未成交顺延、按手取整、遵守涨跌停、处理公司行为；佣金 0.00025、最低 5 元、2023-08-28 之后印花税 0.0005。这些在 execution.py 373fed30 里都核对过 ✔
   - sleeves 和 arms 与 run_smoke 一致 ✔
   - 不调参 ✔
   - prereg 里写的命令是裸 `python`，需要改成具体的解释器（见 P3-7）。
10. **pyflakes**：没有新增警告。仅有的两条（fulla 的 nav_path、hx2 的 charts2）是基线就有的，只是行号挪了。
11. **f 前缀**：没有问题。唯一一处带 `{}` 却没加 f 的字符串是 by_session 的 docstring，属于正常写法。
12. **off-by-one**：X2 两端都是闭区间，n_ind_cap_x2、reclass 的 hold 筛选和 smallcap 现有写法一致；in_date 用严格 `<`、out_date 用 `>=`，正确。
13. **as_of 类型**：load_industry_asof 的 as_of 是 str 或 None（`'YYYY-MM-DD'`），交给 ensure_checked 去解析。session 在 load_leg 里统一截成 10 位字符串；l1_asof 内部再转成 Timestamp 并 normalize；`X2[0] <= s <= X2[1]` 是字符串比较，因为格式统一成 YYYY-MM-DD，所以结果正确。✔

## 发现

### P2（r2 必修，修完才签 code-change .ok）
- **P2-1：out_date 解析失败被静默当成“仍在成分”**。`prep_sw` 对 out_date 用 `errors="coerce"`，解析失败得到的 NaT 和真正的空值混在一起，于是这只股票会被当成至今仍在该行业，这是前视方向的错误。要求：在 coerce 之前先记下原值是否非空，得出 `n_out_unparsed = 原值非空且解析后为 NaT` 的行数；该数大于 0 就抛 SwPitIntegrityError，或者至少硬停并写进披露。in_date 解析失败按“永不命中”处理可以接受，但也要计数并在 meta 里披露。当前真实表上这两个数都是 0，修完后行为不变。
- **P2-2：--pitfix-compare 的输出目录没有任何保护**。现在是 `out_dir.mkdir(exist_ok=True)`，然后在里面覆盖写权重 parquet、smoke 子目录、run.log 和 summary.json。没有检查目录是否为空，也没有限制目录前缀。如果 .ok 把 out_dir 写成 output/strategy_hiliq/b4 或纸面、FROZEN 目录，会直接覆盖现有产物。另外 run_smoke 用了 `relative_to(ROOT)`，所以 out_dir 不在仓库下时，会在 build_topn 已经写完权重之后才抛 ValueError，留下半截产物。要求：
  - out_dir 必须解析到 ROOT/output/strategy_hiliq/ 之下，而且运行前不存在，否则一开始就退出；
  - 显式拒绝 b4、capadv_x2、legs，以及任何路径中带 paper、FROZEN 或 frozen 的目录；
  - 先做所有检查，再开始写任何文件。
- **P2-3：成败只看“文件在不在”，退出码恒为 0**。
  - run_smoke 判 ok 只看 book_smoke_summary.json 是否存在，不看 returncode；如果目录里留着旧的 summary，也会被当成本次结果读进来，所以 P2-2 不修，这一条只会更糟。
  - pitfix_compare 的结果里 `"ok"` 取自 extract_arm 的返回值，可那个字典里根本没有 ok 这个键，所以永远是 None。extract_arm 返回 error 时也不算失败。
  - 不管哪个 arm 失败，都会照样写 summary.json，然后 `SystemExit(0)` 退出。这和 prereg 第 3 节“没有 summary 就记 VOID”的约定矛盾。
  要求：每个 arm 的 ok 必须同时满足 returncode == 0、summary 文件是本次新生成的（mtime 晚于本次启动时间）、并且没有 error。任何一个 arm 不满足，就写 VOID.md，summary 里 all_ok=false，退出码非 0。
- **P2-4：legacy 静态映射的结果变了**。load_industry_map 声称“签名和行为都不变”，实测有 2 个代码结果不同，其中 600650.SH 是取错了。要求：load_industry_map（也就是 before 这一组）原样保留旧实现，即 `pd.to_datetime(in_date, errors="coerce")` 后 `sort_values("in_date").groupby("ts_code").tail(1)`，保证 before 组能复现历史上的静态映射。l1_static_last 只给 reclass_share 披露用；它在 in_date 相同时，应优先取 out_date 为空的那条（或 is_new 为 Y 的），再看行序。当前 HI_LIQ 腿里没有这 2 个代码，所以对数值没有影响。但“保持不变”这个承诺必须说到做到。

### P3（可在 r2 一并处理，不单独阻塞）
- **P3-1：_UNK_ 混淆**。as-of 映射下，X2 内多出 477 个 (code, session) 取不到行业（占 1.4%）。原因是 sw 表缺这些代码的当前成分行，而旧的静态映射一直在用 2009 年那种陈旧分类。apply_ind_cap 把这些股票全部归到同一个“_UNK_”行业，也按 25% 封顶，所以前后两组的差异并不全是“改分类时点不同”造成的。要求：summary 里按 arm 分别报 `n_rows_asof_missing`、`n_rows_static_missing`，以及 X2 内因 _UNK_ 触发上限的 session 数，并在 prereg 第 4 节写明。数据缺口转 Data。
- **P3-2：改分类当天的空档（设计假设，和 Intel 共有）**。全表 1545 次分类变更里，有 1109 次是“新 in_date = 旧 out_date + 1 天”。新 in_date 正好落在交易日时，这一天两条记录都不命中，股票当天会变成 _UNK_。这次 B4 的 X2 只碰到 1 个这样的 (code, session)，影响很小。这条报给主 Agent，裁定以后是否改成“新分类可用之前沿用旧分类”。本次不改。
- **P3-3：数据重叠**。476 对区间重叠、12 个代码有多条行业不同的未结束记录。“in_date 最新”在逐行查看的几个案例里都是对的，采纳。但 in_date 相同时（例如 300858.SZ 两条都没结束、in_date 都是 2020-08-03），现在按文件行序取，带有随意性。建议加一层优先级：is_new 为 Y 的优先，再看行序；同时把 meta 里的 `n_codes_overlap_on_d` 记下来。sw 表的残留行转 Data 清理。
- **P3-4：test_matches_intel_rowfilter 名不副实**。它比较的是 Strategy 自己那份 sw_members_asof 和 l1_asof，并没有用到 Intel 的函数；测试数据里也没有重叠记录，所以 Intel 的 keep="last" 和 Strategy 的 in_date 最新在这里结果恰好相同。建议改名为“行过滤与向量化结果一致”，另外补一个带重叠记录的用例，断言取的是 in_date 最新那条。
- **P3-5：转 Intel**。Intel 内部取重规则不一致：intel_common 用 `drop_duplicates("instrument_id", keep="last")`，event_study 和 c1 用 `drop_duplicates("ts_code")`，也就是保留第一条。在真实表上，keep="last" 会让 4 个代码共 1209 个代码日取到旧分类。今后合并成公共函数时，统一用“in_date 最新”（相同时再按 is_new 和行序）。
- **P3-6**：SW_L1_SHA_PIN 用的是 assert，`python -O` 运行时会被跳过。建议改成 `if got != PIN: raise SystemExit(...)`。另外 assert_sw_l1_pin 和 load_sw_l1 各读了一次文件，两次读取之间文件可能被换掉（TOCTOU），可以接受，但建议在 summary 里写明两次读取的 sha。
- **P3-7：prereg 第 3 节的命令要写全**：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python …`。hx2 import 了 matplotlib，而这几个环境里只有 qlvenv 装了 matplotlib；ql-enrich-venv 和 .venv_opt 都没有。prereg 还应补两条：
  - 披露 before 组的权重 sha，和现有 output/strategy_hiliq/b4/B4_50_25_25_topN_{60w,100w}.parquet（ca77bc8c… / f75ace33…）比对，只作披露，不作门槛；
  - 写明 tie-sens 和 leg_review 仍带前视偏差，留作后续修复项。tie-sens 如果要重跑，需要重新做预注册，因为 dep_hx2_sha256 已经过期。

## 待 r2 通过后才能用的信息（现在不能凭这些签 .ok）

### selftest
- 命令：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/arch_swpit_asof_selftest research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py`
- 预期：按当前版本是 5 + 12 = 17 passed。r2 加了用例后，以 r2 申报为准。
- test_sw_members_asof 只依赖 numpy 和 pandas，ql-enrich-venv 能跑。

### --pitfix-compare 运行
- 解释器：/workspace/qlvenv/bin/python，Python 3.12.14，pandas 3.0.6、pyarrow 25.0.1，装有 matplotlib。book-smoke 子进程用 sys.executable，所以也是同一个解释器。
- 命令：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/strategy_hiliq_capadv_b4_x2.py --pitfix-compare output/strategy_hiliq/pitfix_compare_20261018`
- out_dir 是 output/strategy_hiliq/pitfix_compare_20261018/，目前不存在。会写入的内容：
  - 4 个权重 parquet：{before_static,after_asof}_B4_{60,100}w.parquet；
  - 4 个 smoke 目录：smoke_{arm}_{60,100}w/，里面有 run.log、book_smoke_summary.json、aum_*/X2/BOOK/nav.csv；
  - summary.json。
  另外，导入 hx2 时会对已存在的 output/strategy_hiliq 执行一次 mkdir，这一步是 no-op。
- 运行 .ok 需要钉住的输入（当前 sha）：
  - data/v2/sw_pit/industry_members_sw_l1_pit.parquet：0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6
  - data/v2/sw_pit/manifest.json：7c73e70b152126d5a37ee9a002c55dd6a7542a7ae0519152c720a7384436d282
  - data/v2/calendar/trade_cal_sse_pit.parquet：fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41
  - 腿 capacity_adv：…20261014_195620.parquet，3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
  - 腿 earnings_event：…20261014_202822.parquet，6bb3b3f3160eafce410079ac49203faed609f9d722a55b9ef6f15c82af6d69e0
  - 腿 insider_increase：…20261014_202928.parquet，c4b93255b694adb9b0484e55413abf80072be1e48d750e25a39dc4e37917b5e2
  - quantlab/platform/execution.py：373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c；quantlab/platform/__init__.py：bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc
  - quantlab/portfolio/book_smoke.py：1a5fa1aa6ab847bd1ecda4d01bd4bda88b23535edceb91021520261be3e8251b；quantlab/cli.py：9e3ee7d1d76f90c187ab6878addf3fac3182473cdfc3c31746ab4cdbdcbd8b3e
  - 代码：r2 落地后的 hx2、sw_members_asof、sw_pit_freshness（A 落地后为 5191997e），以及 prereg 的 sha。
  - book-smoke 还会读行情和公司行为数据，这部分沿用 book-smoke 现有的钉住方式。
- 预计耗时：约 2–4 分钟。参照：hx2 main（capadv 加 B4 两档 smoke 加画图）上次用了 85.5 秒；tie-sens 每次 book-smoke 约 15–25 秒。
- 预计 RSS：
  - 父进程约 0.7–0.9 GB。依据：capacity_adv 腿 3,595,176 行，三条腿读进来再加 sw 表，用 pandas 3 实测峰值 639 MB；再加 matplotlib 和 by_session 查找表（约 4 万对）。
  - book-smoke 子进程约 0.4–0.6 GB（10-18 00:41 观察到的 RAND13_100w 为 0.42 GB）。
  - 两个进程各自都在 1.5 GB 以内。建议挂 1.5 GB 守护，并让脚本自己记录父进程和子进程的峰值 RSS。
- 跑完要做的事：用 `find -newermt T0` 确认只有 out_dir 下的文件被写过；同时确认 execution.py 和 __init__ 的 sha 没变（10-19 17:40 ET 纸面运行之前不得改动）。
