# Data 日线降级备用方案 r3.1（影子披露轨，增量，回应 Arch r3 审）

- 作者：QuantLab Data；起草 2026-10-18 11:20–11:40 ET。新文件，不改 r3 及任何现有文档。**仅方案**：没有写代码或数据，没有运行项目脚本，没有读 parquet，没有联网。
- 基线：docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3.md，sha256 f7cacfb1a53e681ba3bf56e15d840b97f203218c9cb971233a5eb29219427df2（起草前核对一致，286 行）。r3 未在本文出现的内容原样有效。
- 回应：docs/v2/ARCH_DATA_DAILY_FALLBACK_PLAN_R3_REVIEW_ZH.md，sha256 f977d4b945176a04e4e229a8ca5c75678d68786a1dc760ee92a03a3539ce8dfe（起草前核对一致，PASS with conditions）。
- promotion_approved=false，live=false，strategy_promotion=false。影子轨的产物永远不进纸面、ledger、NAV 或给 Leo 的报告（r3 §7 不变）。

## 1. 审查意见逐条回应
| 编号 | Arch 要求（f977d4b9） | r3.1 处理 | 位置 |
|---|---|---|---|
| P2-1 | 黑名单第 4 项改为 output/data_freshness_status.json 与 output/daily_update_status.json；影子脚本不得设置或导出 QL_FRESH_PATH；run .ok 签发前 Arch 再核该路径与 sha 并写进 .ok | 第 4 项改为两个确切路径（已用 rg 核对写入方与读取方行号）；脚本启动时若环境里已有 QL_FRESH_PATH 即拒绝运行，代码里不出现对它的任何赋值，selftest 断言；run .ok 增加 fresh_path / fresh_sha256 / status_path / status_sha256 四个字段 | §2 |
| P2-2 | 前后 sha 清单扩大到：黑名单 1–3 目录全量、两个状态 JSON、两个 announcements parquet、tushare_raw/trade_cal.parquet、closure 所钉全部文件；白名单与 sha 清单两道都要 | 新常量 GUARD_SCOPE（写死在脚本里）；文件部分直接复用 docs/v2/audit/nightly_sha_scope_20261018.txt（已含全部所列文件，另含日历与 SW 表，取超集），目录部分逐文件枚举；本次所有项一律 MUST_NOT_CHANGE | §3 |
| Q2 | 全量 sha，不抽样；记 size、mtime_ns、ctime_ns、inode；前后清单在同一 run .ok 内；只哈希不解析；任何不一致整体 FAIL | 全部采纳 | §3、§4 |
| Q3 | 路径已核实 | 同 P2-1 | §2 |
| Q4 / P3-2 | 「据 Arch」行号已复核；Data 实施前自己再跑同样的 rg，结果附回执后去掉标注 | 10-18 10:27 与 10:36 ET 已重跑一遍（显式文件路径，不进 data/），结果见 §6；实施当天再跑一次附回执 | §6 |
| P3-1 | run_event_leg 是 L169–179 | 更正：r3 L84 与 L111 的「L160–178 / L169–178」改为 run_legs L160–168、run_event_leg L169–179（return 在 L179） | §5 |
| P3-3 | §12 Q1（10-19 是否执行 extend）仍待 Strategy / Eng | 保留为开放问题，不阻塞 B | §8 |
| P3-4 | 清单逐文件加 st_ctime_ns 与 inode | 采纳 | §3 |
| Data 下一步 2 | code-change .ok 申请须附脚本与 selftest 完整文本（含白名单、黑名单、P2-2 清单范围的写死常量） | 本文给出三个常量块文本（§2、§3）；脚本与 selftest 全文作为下一份交付，不在本 r3.1 内 | §7 |
| Data 下一步 3 | 只有 10-19 14:30 ET 中转仍不通且主 Agent 书面转达「Leo 选 B」才申请 run .ok；避开 16:40–18:40 | 采纳；时间窗与中止规则见 §4 | §4 |

## 2. P2-1：黑名单第 4 项与 QL_FRESH_PATH
- 核对（10:27 ET，rg 显式文件）：
  - 写入方：scripts/acquire/data_freshness_status.py L9 `OUT=ROOT/"output/data_freshness_status.json"`；nightly_update.py L43 freshness 步骤注释同一路径。
  - 读取方：quantlab/portfolio/research_loop.py L654 `fp = Path(os.environ.get("QL_FRESH_PATH") or (ROOT / "output/data_freshness_status.json"))`，L665 `source="output/data_freshness_status.json"`。
  - output/daily_update_status.json：eng_daily_panels.py 写，capacity_adv_paper_extend.py L44、L137 读（r3 §3.2）。
  - data/v2/acquire_status 不存在（Arch 已核），r3 第 4 项的写法作废。
- 更新后的写入黑名单（任何一项被写即违规，运行中止并上报）：
  1. data/v2/asof_extend_202610/（整个目录）
  2. data/v2/asof_extend_tushare_202610/（整个目录）
  3. data/v2/float_mktcap/（整个目录）
  4. **output/data_freshness_status.json 与 output/daily_update_status.json**（确切路径）
  5. 任何 Tushare 表（data/v2/bars、adj、valuation、index、etf、cb、futures、tushare_raw、corporate_actions）
  6. data/v2/events/
- QL_FRESH_PATH 禁令：
  - 脚本不读、不设置、不导出 QL_FRESH_PATH；不起子进程（因此也不会把环境传下去）。
  - 启动时（enforce 之后、任何读写之前）若 `"QL_FRESH_PATH" in os.environ` 即拒绝运行：影子轨不应在一个把纸面新鲜度指向别处的环境里运行，这样也能及早暴露环境被改的情况。
  - selftest：①带 QL_FRESH_PATH 启动 → 拒绝；②正常运行前后 os.environ 中都没有 QL_FRESH_PATH；③源码文本里没有 `QL_FRESH_PATH` 的赋值或 putenv（ast 检查）。
- run .ok 新增字段（Arch 签发前再核，写进 .ok）：`fresh_path=output/data_freshness_status.json`、`fresh_sha256=<签发时全长 sha>`、`status_path=output/daily_update_status.json`、`status_sha256=<签发时全长 sha>`。脚本启动时核这两个 sha，不符即拒绝（说明 .ok 签发后有日更或别的进程写过它们，须重新签）。
- 常量文本（写死在 daily_shadow_public.py，未落 repo）：
```python
WRITE_ALLOW = [ROOT / "data/v2/_shadow_public/20261019"]
WRITE_DENY_DIRS = [ROOT / p for p in ("data/v2/asof_extend_202610", "data/v2/asof_extend_tushare_202610", "data/v2/float_mktcap",
                                      "data/v2/bars", "data/v2/adj", "data/v2/valuation", "data/v2/index", "data/v2/etf", "data/v2/cb",
                                      "data/v2/futures", "data/v2/tushare_raw", "data/v2/corporate_actions", "data/v2/events")]
WRITE_DENY_FILES = [ROOT / "output/data_freshness_status.json", ROOT / "output/daily_update_status.json"]
FORBIDDEN_ENV = ("QL_FRESH_PATH",)
```

## 3. P2-2 / Q2 / P3-4：运行前后 sha 清单
- 范围（GUARD_SCOPE，全部 MUST_NOT_CHANGE，全量 sha，不抽样）：
  - 目录（递归逐文件，不跟随符号链接）：data/v2/asof_extend_202610/、data/v2/asof_extend_tushare_202610/、data/v2/float_mktcap/。Arch 10-18 实测约 10404 + 11161 + 9 个文件、约 720M。
  - 文件：直接复用 docs/v2/audit/nightly_sha_scope_20261018.txt（sha256 b24a4a88b23efd8d1663238e6e590984afa08c719b5d397f589a87d9fc6319be，167 项）。它包含 Arch 列的全部文件：output/data_freshness_status.json、output/daily_update_status.json、两个 announcements_classified_pit*.parquet、data/v2/tushare_raw/trade_cal.parquet、docs/v2/eng_sd1/paper_import_closure.json（6919e7af）及其所钉 156 个文件；另含 calendar/trade_cal_sse_pit.parquet 与 manifest.json、三份 SW L1 表，多核不少核。
  - 该范围文件里两个状态 JSON 标为 EXPECTED_CHANGE（那是给日更用的）；**影子轨运行中它们一律按 MUST_NOT_CHANGE 核**。实现上影子脚本读范围文件后忽略类别，全部当 MUST_NOT_CHANGE。
- 逐文件字段：path、size、mtime_ns、ctime_ns、inode、sha256；按路径排序；清单文件本身再算一个汇总 sha。ctime 不能用 utime 改回，可抓到「写后改回 mtime」的情形（P3-4）。
- 比对：前后两份清单的路径集合必须相同（多一个或少一个文件都算不一致），每个文件六个字段全部相同。任何一项不一致：影子轨整体 FAIL，不出影子估值，立即报 Arch。
- 时机：BEFORE 在 run .ok 内、94322 停 T 之后、第一次联网之前；AFTER 在全部写入完成之后；两者都在同一 run .ok 内。只哈希，不解析内容；用标准库 hashlib 流式读（每次 1MB），RSS 很小；约 865MB 顺序读，估计 10–60 秒，占的是页缓存。
- 另核：closure 所钉 156 个文件的 sha 必须等于 paper_import_closure.json 里写的 pin（不只是前后相同）；10-18 10:22 ET 的基线 docs/v2/audit/nightly_sha_baseline_20261018_1022.txt（dfdc2555）已全部吻合，可作参考，但 run 当天以 BEFORE 为准。
- 常量文本（未落 repo）：
```python
GUARD_DIRS = [ROOT / p for p in ("data/v2/asof_extend_202610", "data/v2/asof_extend_tushare_202610", "data/v2/float_mktcap")]
GUARD_FILE_SCOPE = ROOT / "docs/v2/audit/nightly_sha_scope_20261018.txt"
GUARD_FILE_SCOPE_SHA256 = "b24a4a88b23efd8d1663238e6e590984afa08c719b5d397f589a87d9fc6319be"   # 范围文件自身先核 sha, 不符即拒绝
GUARD_FIELDS = ("path", "size", "mtime_ns", "ctime_ns", "inode", "sha256")
def _row(p):
    st = os.stat(p, follow_symlinks=False)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return dict(path=str(p), size=st.st_size, mtime_ns=st.st_mtime_ns, ctime_ns=st.st_ctime_ns, inode=st.st_ino, sha256=h.hexdigest())
```
- 写入白名单（只许 data/v2/_shadow_public/20261019/，已存在即退出）仍是第一道防线；sha 清单是证据。两者都要。

## 4. run .ok 的条件与时间窗
- 前提（缺一不可）：①10-19 14:30 ET 中转仍不通（附探测记录）；②主 Agent 书面转达「Leo 选 B」；③code-change .ok 已签且脚本落地 sha 与 .ok 一致；④Arch 签发时核过 §2 的四个字段。
- 时间窗：14:30 ET 之后申请，**必须在 16:40 ET 之前结束**（16:40–18:40 不运行任何东西），因此 Data 的内部规则：16:00 ET 前未开始就不开始；16:30 ET 仍未结束就停（只对自己起的确切 PID 发 TERM，留 ps 证据），已写的影子文件原样保留并标 INCOMPLETE，照常做 AFTER 清单。
- 一次一个重任务；94322 是否停 T 与 Arch 对齐，STOP / CONT 前后都留 `ps -o pid,ppid,stat,etime,rss,args -p 94322` 输出。
- 外部域名只允许 push2his.eastmoney.com 与 web.ifzq.gtimg.cn；范围只有 20261019 加 5 日对照（r3 §11 不变）。
- 与日更的关系：10-19 05:55 ET 日更若跑 daily_pull，会重写 data/v2/tushare_raw/trade_cal.parquet（tier1_pull.py L83–95，见 docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH.md F1）。这发生在影子轨 BEFORE 之前，不影响影子轨本身的前后比对；但会影响「closure 与 10-18 基线一致」的说法，回执里如实写明该文件在 BEFORE 时的 sha 与 10-18 基线是否相同。

## 5. P3-1：行号更正
- research/b4_paper_extend.py（10:27 ET 核对）：run_legs 定义 L160，L163 跑 capacity_adv_paper_extend.py，L164 起按顺序跑事件腿；run_event_leg 定义 L169，L173 设 WEIGHT_END，L174 subprocess.run，L178 写 .parquet.check.json，**L179 return**。r3 L84「160-178」、L111「L160–168」「L169–178」统一更正为 run_legs L160–168、run_event_leg L169–179。

## 6. P3-2：Data 自己重跑的 rg（10:27 与 10:36 ET，显式文件路径，-g "!data/**"）
| 引用 | 结果 | 结论 |
|---|---|---|
| quantlab/data/v2_readers.py L90、L149、L1625、L1678、L1680、L1779、L1781、L1853 | L90 DEFAULT_ASOF_EXTEND_FALLBACK_DIR；L149 asof_extend_fallback_dir；L1625 读回退 manifest；L1678 / L1680 calendar 回退；L1779 面板回退路径；L1781 extend_panel_fallback 标记；L1853 is_st_at_open_ffill_research | 属实，去掉「据 Arch」 |
| tier1_materialize.py L62–71、L114–115、L124 | L62 suspend 注释、L64 suspend_d 路径；L114 注释与 L115 panel_dir = asof_extend_tushare_202610/panels；**实际写在 L147 `merged.to_parquet(destp)`（非原子）**；L124 is_st_at_open=False | 属实；补充写入行 L147 |
| b4_paper.py L93–96、L99–118 | L93 _run_smoke、L94 import book_smoke.run；L99 backfill()、L102 _run_smoke；L106 forward()、L108 import v2_multisleeve_book、L117 _run_smoke | 属实，去掉「据 Arch」 |
| capacity_adv_paper_extend.py L75、L84–85 | L75 读 tushare_raw/trade_cal.parquet；L83 d1_end()，L85 `pq.ParquetFile(str(C.D1_VALUATION))`；另 L99 stat D1_VALUATION、L133 D1 过期即 ABORT | 属实，去掉「据 Arch」 |
| s6_paper_extend.py L36、L42 | L36 列冻结 weights 脚本；L42 B.run_event_leg("equity_incentive", end, env) | 属实 |
| g1g5_{earnings_event,insider_increase,equity_incentive}_weights.py L51–52 | 三个文件都在 L51–52 定义 EVENTS = 两个 announcements_classified_pit*.parquet | 属实 |
| research_loop.py L654、L665；data_freshness_status.py L9；nightly_update.py L43 | 见 §2 | 属实 |
- 实施当天（code-change 落地前）再跑同一组命令，输出写到文件后附回执。

## 7. 下一份交付（code-change .ok 申请）
- scripts/acquire/daily_shadow_public.py 与 tests/test_daily_shadow_public.py 全文，包含 §2、§3 常量；selftest 覆盖 r3 §11 所列各项，加：QL_FRESH_PATH 三例（§2）、黑名单第 4 项两个文件被写即拦截、GUARD_SCOPE 范围文件 sha 不符即拒绝、前后清单多文件 / 少文件 / ctime 变化 / inode 变化各判 FAIL（合成目录）。
- 交付时间：10-19 纸面跑完之后；code-change 与 run 分开签。

## 8. 开放问题（更新）
- Q1（P3-3，仍开）：10-19 纸面流程是否执行 extend？请 Strategy / Eng 按运行手册确认；决定 A / C 路径是否需要 10-19 的 events。
- Q5（新）：10-19 日更 daily_pull 写 tushare_raw/trade_cal.parquet 的问题（§4 末条），请 Arch 与主 Agent 与日更方案一起定。
- Q6（新）：14:30–16:40 ET 的时间窗约两小时，扣除对齐与 sha 清单，联网拉取与对照须在约 1.5 小时内完成；若 Arch 认为太紧，影子轨可改为只做 10-19 当日（去掉 5 日对照），请裁定。
