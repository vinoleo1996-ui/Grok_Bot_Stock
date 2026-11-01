# Arch 审查：Strategy DIFF C r3d（申万 L1 as-of 交易日规则，正式版）

- 审查人：QuantLab Arch；时间：2026-10-18 11:45 ET（美东）
- 审查对象（sha 前缀均已核对）：
  - 主审 `docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3d.diff`，090e9c2a4ebbd40cd056f6438e2216a1292b00b172d8be99675c778ab5eceaa8（全量，基线 b2 = HEAD + DIFF B r2）
  - `..._r3d_incremental.diff` cc340b2a…60dcad（154 行，基线 c3c）
  - `..._r3c_incremental.diff` cce08b50…（基线 c3b）
  - `..._r3d_vs_c3b.diff` 195d2382…c9ad702
  - 前序：`docs/v2/ARCH_STRATEGY_DIFF_C_R3B_REVIEW_ZH.md` 016ae55e；Data §14② 报告 `docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt` 0a5a5197
- 方式：只读。全部在 /tmp/arch_r3d_rev 的新副本里做，`set -euo pipefail` 加 cd 校验；仓库内没有 git apply，没有跑测试，没有读价格、收益或因子数据。

## 结论：有条件通过（PASS with conditions）

- P1：0 条。冻结清单没有重叠（见 §4）。
- P2：2 条，都不阻断代码落地：P2-1 在 pitfix 对照运行 .ok 签发前必须处理；P2-2 在 Intel 接入共享函数前必须修。
- P3：9 条，只作记录或下一轮改进。
- 可以签代码改动 .ok（B r2 d0fb1d3f 与 r3d 090e9c2a 连续落地），之后签自测 .ok（83 passed）。钉版见 §7。

## 1. 复现（任务 1）

- 基线：从仓库只读复制 hx2（1c51531a）、fulla（7bd657ed）、sw_pit_freshness（5191997e）、test_sw_pit_freshness（cee59fc5）到 /tmp。sw_members_asof、它的测试和 prereg 在 HEAD 上都不存在。
- 叠 DIFF B r2（d0fb1d3f）：`git apply --check` 和 apply 都是 EXIT=0，得到 b2：hx2 1728c126、fulla 88b6f367、sw_members_asof 0444d9d6、test 4f468b48、prereg c2b37127。只有一条尾部空行告警（B r2 第 265 行）。
- b2 上叠 r3d 全量：EXIT=0。最终 sha 全部符合预期：

| 文件 | r3d 最终 sha256 |
|---|---|
| research/sw_members_asof.py | 72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8 |
| research/tests_sw_pit/test_sw_members_asof.py | 3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2 |
| research/strategy_hiliq_capadv_b4_x2.py（hx2） | 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1 |
| research/strategy_fulla_b4_x2.py（fulla） | fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b |
| research/sw_pit_freshness.py（未动） | 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f |
| research/tests_sw_pit/test_sw_pit_freshness.py（未动） | cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e |

- 增量链互核：b2 + r3b（913e6830）得到 c3b；c3b + r3c_incremental 得到 c3c（sw_members_asof 52b0332f、test 9d5b00df、prereg c95c9138，与 Strategy 报的一致）；c3c + r3d_incremental 与全量结果 `diff -r` 完全一致；c3b + r3d_vs_c3b 也完全一致。
- 与 Strategy 的 /tmp/swr5/b2、c3d 对照：只差 tests_sw_pit/test_sw_pit_freshness.py（swr5 副本里没有这个文件），其余一致。

## 2. 裁定落实核对（任务 2）

| 裁定 | 位置（r3d 最终文件行号） | 结论 |
|---|---|---|
| CLEAN 表 lag ≤ 10 只写 lag_notes，不置 stale | sw_members_asof.py L389–393 | 已落实 |
| lag > 10 且无 coverage_gap：stale=True、stale_lag_only=True | L390–391、L409–421 | 已落实。这是 11:13/11:20 补充、11:28 确认后的细化规则：滞后本身不阻断运行，只是带标签的 stale |
| 有 coverage_gap：一律 stale=True，stale_lag_only=False | L394–395、L421（reasons 必须恰好是 ["lag"]） | 已落实 |
| legacy 阈值仍是 3 | L376–381 走 sw_pit_freshness（STALE_LAG_TDAYS=3，未动） | 已落实 |
| lag 口径：fetch_time 时点最近一个已收盘的 SSE 开市日 | L346–358、L307–319 | 已落实。“收盘”按 SH 18:00 发布时点计，见 P3-3 |
| 完全重复行去重（保留第一行）并计数 | L191–194（duplicated 默认 keep=first）、n_rows_exact_duplicate_dropped | 已落实 |
| 同代码、同 in_date、不同行业算冲突：raise 模式报错，count 模式进 overlap_codes（conflict=True） | L196–197 全表披露；L513–526 | 已落实。测试 L731–754 两种模式都覆盖 |
| .ok：expires_et 必须带时区偏移 | L843–848 | 已落实 |
| .ok：拒收 _consumed/ 下的文件；DRAFT 全文匹配、不分大小写（文件名和内容都查） | L812–822 | 已落实（见 P3-7） |
| 分块上限是参数，默认 1M，按整个 session 切；单个 session 超限就报错 | L88、L149–153、L609–669（L626–628 报错） | 已落实 |
| `Tsh.00018` strip 后完全相等才剔除，不归一化，披露计数；其他未知 id 一律报错 | L226、L259–271；测试 L464–469、L685–698 | 已落实 |
| A_PFX 与 A_DOT 都用 re.I | L221–222、L232–235 | 已落实 |
| 比较和连接前显式转成 datetime64[us] | L89、L118、L128、L180–181、L501、L510、L621 | 已落实（没有 merge_asof） |
| dtype 常量与 §14② L13–27 一致 | L212–216 对 §14② L15–25 | 逐列核对一致：11 列；instrument_id、sw_code、sw_name、source、quality_status、schema、is_new 为 str；in_date、out_date、available_at 为 datetime64[us]；revision 为 int64 |
| manifest 值从 manifest 读取，不写死；n_l1 = nunique(sw_code) 和 available_at_nulls 都在剔除前的原表上算；缺键就报错 | L268–277、L338–345 | 已落实。缺键时比较的是 str(None) 与表值，不等就报错；测试 L528–551 覆盖一致、不一致、缺键和“按剔除后的值算必须失败”四种情况 |

只读核对真实 manifest（data/v2/sw_l1_pit/manifest.json，0493991c，只读元数据）：tushare_candidate.path 是绝对路径；fetch_time 带 -04:00 偏移；六个 metrics 键都在，值与 §14② L42 一致。

## 3. 缺陷排查（任务 3）

### P2

- **P2-1** 预注册文件状态自相矛盾：`docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md` L1 写“r2 草稿，待 Arch 审签”，L3 写“状态：DRAFT，未运行”，而 §5 L43 已写“Arch 2026-10-18 11:28 ET 确认”。不影响代码落地（prereg 不是执行代码，check_allow_ok 只读 .ok 本身）。条件：签 pitfix 对照运行 .ok 之前，Strategy 要把 L1/L3 改成正式状态（会产生新的 prereg sha），届时一并重钉。本轮按原样钉 2e1347b5。
- **P2-2** 共享函数里 as_of 用字符串比较，结果依赖日期格式：`sw_members_asof.py` L375（`str(as_of)[:10]`）、L394（`a > coverage_day`）、L404（聚合时取较大的 as_of）。/tmp 合成探针复现：as_of 传 `20261009`（YYYYMMDD）时，`"20261009" > "2026-10-09"` 恒为真，误报 coverage_gap，stale=True；传 `2026-10-09` 或 Timestamp 时正确。聚合时混用两种格式，也会把较早的日期当成较大值。现有调用方不会触发：hx2 load_leg L100 把 session 规整成 str[:10]，X2 过滤也依赖带横线的格式；fulla 同理。误判方向是多报 stale，只影响披露、不阻断，所以不阻断本次落地。条件：Intel 调用 sw_l1_table_check 之前，或下一轮改动时，必须先把 as_of 规整为 `pd.Timestamp(as_of).strftime("%Y-%m-%d")`（解析失败就报错），并加 YYYYMMDD 用例。

### P3

- **P3-1** 注释过期：L419 还写着“pending Arch confirmation”，prereg 已改为 11:28 确认。下一轮顺手改。
- **P3-2** 用了墙钟：L382 和 L401 各调用一次 `datetime.now`（now_et 为 None 时，ref_day 和 checked_at 来自两次不同的读数）。lag 是按运行当天算的，与 as_of 无关，同一回测在不同日期重跑，披露会变。按现在的 fetch_time 推算，从 2026-10-26（SH 18:00，即 06:00 ET）起 lag=11，CLEAN 表会变成 stale_lag_only=True，除非 Data 在此之前刷新 manifest。建议只取一次 now；并提醒 Data 在 10-26 前刷新。
- **P3-3** “已收盘”按 SH 18:00（发布时点）判定，不是 15:00 收盘（L314）。与 sw_pit_freshness 的 SH_AVAIL_HOUR=18 一致；只在 SH 15:00–18:00 抓取时会多算 1 天，方向保守。接受，建议写进 prereg。
- **P3-4** coverage_gap 的判定 `as_of > coverage_day`（L394）保守了一个 session：coverage_day 18:00 发布的 in_date 从下一个开市日起才生效，所以 next_open(coverage_day) 其实也已覆盖。方向保守，只影响披露。接受。
- **P3-5** fetch_time 没有时区时，默认按 ET 处理（L351），属于静默兜底。真实 manifest 带偏移，现在不会触发。建议改为报错。
- **P3-6** 同义反复的测试：test_us_ns_precision_equivalent L722–723 比较两次 prev_open 结果的 dtype，但 prev_open 恒返回 open_days[i]（[us]），这条断言必然成立。test_clean_schema_constant_matches_fixture L415–417 只拿手写夹具和手写常量互比，没有对照 §14②。本审查已人工对照 §14②（见 §2），常量正确。
- **P3-7** DRAFT 全文子串匹配（L821）会误拒 REDRAFTED 这类词，也会误拒引用了 `_r3c_DRAFT2.diff` 这种文件名的 .ok（/tmp 探针已复现）。这是按裁定③设计的；操作要求：签 pitfix 等 allow .ok 时，正文不要引用任何名字带 DRAFT 的文件。
- **P3-8** 重签清单需要更正一项：“sw 表 0b1d3432 改成 89d4afa3”只适用于 hx2 main/合成和 fulla 的运行 .ok。pitfix 对照（PAUSED）两组都按设计读 legacy 表 0b1d3432（hx2 L49–52 SW_L1_LEGACY_SHA_PIN，L824–834），它的 .ok 必须继续钉 0b1d3432。目前没有任何在用的 .ok 钉 0b1d3432。
- **P3-9** ql-enrich-venv 里没有 pyflakes。本审查用的是 /tmp 独立 venv 的 pyflakes 3.4.0（Python 3.13.5）；Strategy 报的是 4.0.3。两版结果相同。

其他排查项都没有发现问题：交易日差一（gap carry 窗口 prev_open(d) ≤ out < d、lag 区间 (cov, ref]，按 §14② 例子算出 lag=5，与 Data 一致）；时区（fetch_time 和 now 都先转 ET，再转 SH 取日期）；静默兜底（未知 id、不可解析的 out_date、NaT session、日历外、缺日历都会报错）；分块统计合并（n_* 求和，代码列表按代码合并后重算 n_codes_*）；hx2 外部引用者需要的符号都还在（run_smoke、build_topn、load_industry_map、apply_ind_cap、load_leg、to_id、write_pos_weights、BAL/CAP/IND_CAP/N_BY_AUM/X2、_is_etf）。hx2/fulla 里的 time.time() 只用来算耗时。

## 4. 冻结核对（任务 4）

- 全量 diff（含 B r2）只改这 5 个文件：research/sw_members_asof.py（新）、research/tests_sw_pit/test_sw_members_asof.py（新）、research/strategy_hiliq_capadv_b4_x2.py、research/strategy_fulla_b4_x2.py、docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md（新）。
- `docs/v2/eng_sd1/paper_import_closure.json`（6919e7af，156 条 [path, sha]）：以上 5 个路径和它们的新旧 sha 一个都不在里面。156 个钉住的 .py 文件也都不引用 hx2、fulla、sw_members_asof、sw_pit_freshness。
- 没有改动 data/v2/sw_l1_pit 的 89d4afa3 和 87d769aa；r3d 只读这两个文件的 sha，落地前后要现场核对。
- 结论：无重叠，P1 = 0。落地时间仍受限：RESEARCH_QUIET.lock 存在期间（含 10-19 05:25 到日更写出 DONE/FAILED 标记）不落地，10-19 16:40–18:40 ET 不落地。

## 5. 静态检查（任务 5，/tmp 副本，2026-10-18 11:37:56 ET）

- 用括号写法的 pgrep `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py`：没有匹配，EXIT=1。
- `/workspace/ql-enrich-venv/bin/python`（3.13.5）py_compile 检查 6 个文件：EXIT=0。
- pyflakes 3.4.0：EXIT=1，只有 2 条基线遗留：hx2 L671 charts2、fulla L180 nav_path。这两条在 HEAD（L582/L165）和 b2（L632/L166）上原本就有，新代码 0 条。
- 收集前先核了导入时副作用：sw_members_asof 模块层只有常量；测试模块层只构造合成数据，sw_pit_freshness 模块层也不读数据，所以可以收集。`pytest --collect-only -q -p no:cacheprovider research/tests_sw_pit` 结果为 83 tests collected（71 + 12），EXIT=0，之后已清掉 __pycache__。回执：/tmp/arch_r3d_rev/static_receipt.txt。
- 仓库 research/ 和 research/tests_sw_pit/ 下都没有 __init__.py，也没有 conftest.py，所以 /tmp 副本和仓库的收集环境一致。

## 6. 重签清单核对（任务 6）

搜索范围：docs、output、research、scripts、_review 下除 _consumed、_superseded、_VOID、_recovery 以外的 .ok 和文档。搜索的旧 sha：hx2 1c51531a、3f7f75c3；fulla 7bd657ed；各中间版本（0444d9d6、e1adef52、52b0332f、4f468b48、9943b412、9d5b00df、c2b37127、9db7cd14、c95c9138）；sw 表 0b1d3432。

- 在用的 .ok 只命中一个：`output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok` L20 `dep_hx2_sha256=3f7f75c3…`。注意它和现在的 HEAD（1c51531a）本来就对不上，已经失效。prereg §5 也写明 tie-sens 要重跑须重新预注册。建议作废后重签，不要改原文件。
- 文档命中：`docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md` L75 `dep_hx2_sha256=3f7f75c3…`。
- 没有在用的 .ok 钉 fulla、sw_members_asof、test、prereg 的旧 sha（后三个在 HEAD 上不存在），也没有 .ok 钉 0b1d3432。
- 叶 23、叶 24：15 个 .ok（含草稿和已归档）都不引用这 5 个文件，也不引用它们的旧 sha；有 2 个已归档的叶 24 .ok 钉 89d4afa3，这张表不变。结论：不受影响。
- 其他命中都是审查文档、TEAM_STATE 历史、Intel 告警、Data 的 nightly sha 范围清单（0b1d3432 在那里是 legacy 文件自身的 sha，必须保留），不需要重签。

核对后的重签清单（Strategy 的版本是完整的，按 P3-8 修正一项）：
1. 凡钉 hx2 的 .ok 改为 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1：目前只有 TIE_SENS_v1.ok 的 dep_hx2（由 3f7f75c3 改；按作废重签处理）。
2. fulla 改为 fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b，并加钉 sw_members_asof 72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8（目前没有在用的 .ok，用于今后的运行 .ok）。
3. test 钉 3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3。
4. prereg 钉 2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2（P2-1 改完后再更新）。
5. TIE_SENS_v1.ok 的 dep_hx2，以及 STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md L75：都改为 7b8235dc（须重新预注册）。
6. sw 表：hx2 main/合成和 fulla 的运行 .ok 钉 89d4afa3（CLEAN）；pitfix 对照 .ok 继续钉 0b1d3432（legacy，P3-8）。
7. 叶 23、叶 24 的 .ok 不动。

## 7. 钉版

### 7.1 代码改动 .ok（Strategy 落地 B r2 和 r3d，中间不 commit）

- diff_b_r2 = docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018_r2.diff，d0fb1d3faa6962d19e8405280975e8818766ef406b00f390edcc9b02f81ee250
- diff_c_r3d = docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3d.diff，090e9c2a4ebbd40cd056f6438e2216a1292b00b172d8be99675c778ab5eceaa8
- 落地前（HEAD）：hx2 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45；fulla 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316；sw_members_asof.py、test_sw_members_asof.py、PREREG 都不存在
- 落地后：即 §1 表中的 5 个 r3d sha
- 不得改动：research/sw_pit_freshness.py 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f；research/tests_sw_pit/test_sw_pit_freshness.py cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e
- 数据前后必须一致，只算 sha：89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c、87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3、fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41、0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6、manifest 0493991cd34f72a85d8cb1139b1f3b947b0754fa38029f54ad06a45b2a26446b
- 前置条件：被覆盖的旧文件归档到 _recovery/strategy/<ET 时间>/；落地前后用括号写法的 pgrep 或脚本文件取证，并附 ps；RESEARCH_QUIET.lock 存在时不落地；10-19 16:40–18:40 ET 不落地。
- 授权开关：allow_commit=false、allow_run_tests=false、allow_read_prices=false、allow_read_returns=false、allow_read_factors=false、allow_read_sw_l1_clean=false、allow_force=false；live=false、promotion=false。

### 7.2 自测 .ok（落地并核对 sha 之后）

- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit`
- 期望：83 passed（test_sw_members_asof 71 + test_sw_pit_freshness 12），0 failed、0 error、0 skipped。退出码为 0 不算数，要核对输出里的计数。
- 钉的文件：sw_members_asof 72e4e4c3…5f2ea8、test 3fa3878d…a6c3、sw_pit_freshness 5191997e…b43f、test_sw_pit_freshness cee59fc5…fe0e。hx2 7b8235dc 和 fulla fa2e4629 测试不会导入，只核 sha。
- 测试只用 tmp_path 和合成日历，不读真实数据，不写仓库。跑完核对 research/tests_sw_pit 下没有新增 __pycache__ 或 .pytest_cache。
- 前置条件同 7.1。live=false、promotion=false。

## 8. 回执

- /tmp/arch_r3d_rev/apply.sh、chain.sh：复现和增量链互核
- /tmp/arch_r3d_rev/static_receipt.txt：pgrep、py_compile、collect-only
- /tmp/arch_r3d_rev/probe/p1.py：P2-2 和 P3-7 的合成探针（不读任何真实数据）
