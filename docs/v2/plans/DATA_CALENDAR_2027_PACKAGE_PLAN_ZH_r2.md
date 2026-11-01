# Data 交易日历 2027 延长包方案 r2（增量，回应 Arch 审）

- 作者：QuantLab Data；起草 2026-10-18 11:00–11:20 ET。新文件，不改 r1 及任何现有文档。**仅方案**：没有写任何代码或数据，没有运行任何项目脚本，没有读 parquet，没有联网。
- 基线：docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md，sha256 c472713bed6837085044432335a3fe9eed36d139f982eeb1bcf88ddb22db03ea（起草前核对一致）。r1 未在本文出现的内容原样有效。
- 回应：docs/v2/ARCH_DATA_CALENDAR_2027_PLAN_REVIEW_ZH.md，sha256 5d35e63c3123e9368c9b7ec3c8a4a678b70e8f6a503e116ab0e05be2aeab5b52（起草前核对一致，PASS with conditions）。
- 冻结：paper_import_closure.json 所钉文件与 89d4afa3 / 87d769aa 冻结到 10-19 纸面跑完；本包在此之前不写任何文件；避开 10-19 16:40–18:40 ET。
- live=false，promotion_approved=false，strategy_promotion=false。

## 1. 审查意见逐条回应
| 编号 | Arch 要求（5d35e63c） | r2 处理 | 位置 |
|---|---|---|---|
| P2-1 | trade_cal_pit.py 每次成功都重写 manifest.json：§1 风险提示补 manifest；10-19 日更后 sha 核对同时含 fa4260b8 与 7ccc911e；新脚本与 nightly 比对模式不得写 calendar/manifest.json，selftest 断言 | §1 风险提示重写（parquet + manifest + 第三个受保护路径）；10-19 日更前后核对用 docs/v2/audit/nightly_sha_scope_20261018.txt（已含 fa4260b8 与 7ccc911e）；所有写操作经 _guard_write，受保护集合含 manifest.json；selftest 新增用例 9、10 | §2 |
| P2-2 | 2027 行 available_at = max(上一年 12-31 09:00 上海, 休市公告发布时间, pulled_et 换算上海)，代码强制，manifest 写三者原值，不满足拒绝 | 新函数 available_at_for_year()（文本），write 模式与 dry-run 都调用；manifest.available_at_components；公告时间只有日期时取该日 23:59:59 上海（保守上界）；selftest 用例 11 | §3 |
| P2-3 | 受保护路径列全（再加 tushare_raw/trade_cal.parquet）；pull 只写新目录 trade_cal_<stamp>/；selftest 断言三个路径都不写 | PROTECTED 三个路径；pull 目录 exist_ok=False；selftest 用例 10 覆盖三个模式。**另报：tushare_raw/trade_cal.parquet 现在由日更 daily_pull（tier1_pull.py L83–95）写，不是 trade_cal 步骤**，10-19 去掉 trade_cal 步骤也挡不住它（§4、Q7） | §4 |
| P3-1 | .ok 计数写明命令与范围 | 重新计数四组（默认忽略规则 / -uu，各含与不含 _consumed），命中都是 0；r1 的「46」无法复现，撤回 | §5 |
| P3-2 | nightly_update.py 两包串行落地，后落的以前一方落地后的 sha 为基线 | 写明：SW 包先落（基线 ec079d56 → 987e273d），日历包以 987e273d 为基线；若顺序相反则互换；任一 code-change .ok 都钉当时的基线 sha | §6 |
| P3-3 | §8 枚举命令分别报「不含 _consumed」与「含 _consumed」 | §8 命令改写，每条都有成对的对照组 | §5 |
| P3-4 | §2.1 行号复核正确 | 无改动；本轮再核 research_loop.py L677 读 calendar 路径一致 | — |
| Q1 | 已定：10-19 用 --steps 去掉 trade_cal 与 sw；加 7ccc911e 前后 sha | 接受；但见 Q7：同一套 --steps 里的 daily_pull 仍会写第三个受保护路径 | §2、§4 |
| Q2 | 首次切换保留代码里显式 sha 钉；指针只作交叉核对 | 接受：TRADE_CAL_SHA_PIN 从 fa4260b8 改为 v2027 全长 sha，走 code-change .ok；指针 trade_cal_APPROVED.json 只作交叉核对，两者不一致即拒绝 | §7 |
| Q3 | 不写「周一至周五」临时版；12-15 前公告未发布报主 Agent 与 Arch | 接受；selftest 用例 12：公告字段缺失即拒绝写 2027 段 | §7 |
| Q4 / Q5 | 归主 Agent 与 Intel | 保留为开放问题 | §8 |
| Q6 | 不同批；SW 继续钉 fa4260b8 | 接受 | §7 |

## 2. P2-1：manifest 重写风险与对策
- 事实（trade_cal_pit.py sha 90e3df43，本轮重读）：L24–25 只在内容变化时 os.replace 覆盖 parquet；但 **L26–30 无论是否变化都重建 manifest 并 M.write_text 写回**，内容含 finished_at（每次不同）与 rewritten，所以每次成功运行 7ccc911e 都会变，且是非原子写。
- §1 风险提示改为：「日更 trade_cal 步骤每次成功运行都会重写 data/v2/calendar/manifest.json（7ccc911e 必变，非原子）；relay 内容有任何不同还会原地重写 trade_cal_sse_pit.parquet（fa4260b8）。此外日更 daily_pull 步骤会重写 data/v2/tushare_raw/trade_cal.parquet（见 §4）。」
- 10-19 05:55 ET 日更（--steps 去掉 trade_cal 与 sw）：前后各取一次 sha 快照，范围用 docs/v2/audit/nightly_sha_scope_20261018.txt（sha256 b24a4a88b23efd8d1663238e6e590984afa08c719b5d397f589a87d9fc6319be；含 calendar/trade_cal_sse_pit.parquet fa4260b8、calendar/manifest.json 7ccc911e、tushare_raw/trade_cal.parquet 141078fa），工具 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py（0aa6c650）。回执写明这三个文件的前后 sha、size、mtime_ns、ctime_ns、inode。
- 新脚本 trade_cal_pit_v2.py：全部写操作经同一个 _guard_write(path)（§4），受保护集合含 calendar/manifest.json；nightly 比对模式的输出只写到 output/data/trade_cal_compare_<stamp>/（新目录），不写 data/v2/calendar 下任何文件，也不写 data/v2/tushare_raw/trade_cal.parquet。
- selftest 新增：
  - 用例 9（比对模式不写 manifest）：在 /tmp 合成根目录下放三个受保护文件，跑比对模式（内容相同、内容不同各一次），断言三个文件的 sha、size、mtime_ns、inode 全部不变，差异报告只出现在新目录。
  - 用例 10（三模式受保护路径）：pull / dry_run / write 三个模式各跑一次，同样断言三个受保护文件不变；另外直接调用 _guard_write 写每个受保护路径，断言抛出拒绝。

## 3. P2-2：2027 行的 available_at
- 规则（代码强制）：对 cal_year = Y 的行，
  - rule_floor = (Y−1)-12-31 09:00 Asia/Shanghai；
  - notice_at = 休市公告（国务院办公厅放假通知与上交所休市安排公告，取两者中较晚者）的发布时间换算上海墙钟；公告只给日期时取该日 23:59:59 上海（保守上界，与 SW P2-3「有证据的保守上界」同一原则）；
  - pulled_sh = pull 目录 COMPLETE.json.completed_et 换算上海墙钟；
  - available_at = max(rule_floor, notice_at, pulled_sh)。
- 拒绝条件：notice_at 缺失；任一时间无时区；notice_at > pulled_sh（拉取早于公告，数据不可能是公告内容）；写出前回读任一 2027 行的 available_at 小于三者任一。拒绝即非零退出，不写文件，报 Arch。
- 旧年份（2005–2026）的 available_at 保持 fa4260b8 原值不变（一致性检查已要求 2005–2026 段逐格相同）。
- 代码文本（未落 repo、未运行）：
```python
SH = "Asia/Shanghai"
def available_at_for_year(year, notice_published, pulled_et):
    # Arch 5d35e63c P2-2: max(规则下限, 公告发布时间, 拉取完成时间), 三者都须带时区; 返回上海无时区墙钟 (与现行列类型一致) 与三者原值
    floor = pd.Timestamp(f"{year-1}-12-31 09:00:00", tz=SH)
    if not notice_published:
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): {year} 休市公告发布时间缺失")
    n = pd.Timestamp(notice_published)
    if n.tzinfo is None:
        raise SystemExit("REFUSED (trade_cal_pit_v2): 公告发布时间须带时区; 只有日期时传该日 23:59:59+08:00")
    p = pd.Timestamp(pulled_et)
    if p.tzinfo is None:
        raise SystemExit("REFUSED (trade_cal_pit_v2): pulled_et 须带时区")
    n, p = n.tz_convert(SH), p.tz_convert(SH)
    if n > p:
        raise SystemExit("REFUSED (trade_cal_pit_v2): 拉取早于公告发布, 不可能是公告内容")
    v = max(floor, n, p)
    comp = dict(rule_floor=floor.isoformat(), notice_published_sh=n.isoformat(), pulled_sh=p.isoformat(), available_at=v.isoformat())
    return v.tz_localize(None), comp
```
- manifest 新字段：available_at_rule（文字：max((cal_year−1)-12-31 09:00 上海, 公告发布, 拉取完成)，2005–2026 沿用原规则）、available_at_components（上面 comp 原样）、holiday_notice（公告名称、文号或链接、发布日期、时间是否为保守上界）。
- 后果（请 Arch 知悉）：若拉取晚于 2026-12-31 09:00 上海，2027 年各行 available_at 会晚于该时点；按 available_at 过滤的读者在此之前看不到 2027 段，这是正确的知情时间口径。按计划在 12 月中旬前拉取，正常情况下 available_at = rule_floor。
- selftest 用例 11：公告正常（12-01）且拉取在 12-10 → rule_floor；公告晚发（2027-01-05 发布、2027-01-06 拉取）→ 取 pulled_sh；公告 2027-01-05 23:59:59 而拉取 2027-01-06 00:10 上海 → 取 pulled_sh，公告时间与拉取同为上界时取较大者；拉取晚于 rule_floor → 取 pulled_sh；公告缺失、无时区、公告晚于拉取 → 各拒绝一次；回读不足 → 拒绝。

## 4. P2-3：受保护路径
- PROTECTED（三个，全部解析为绝对路径后比较）：
  1. data/v2/calendar/trade_cal_sse_pit.parquet（fa4260b8）；
  2. data/v2/calendar/manifest.json（7ccc911e）；
  3. data/v2/tushare_raw/trade_cal.parquet（141078fa；纸面 Eng 日历来源：quantlab/portfolio/trade_calendar.py L12，research_loop.py L651；capacity_adv_paper_extend.py L75 也读）。
- 允许写的路径（白名单，其余一律拒绝）：pull 模式只写新建目录 data/v2/tushare_raw/trade_cal_<YYYYMMDD_HHMMSS>/（mkdir exist_ok=False）；dry_run 只写 /tmp 新目录；write 模式只写 data/v2/calendar/trade_cal_sse_pit.v2027.parquet 与 trade_cal_sse_pit.v2027.manifest.json（目标存在即拒绝，同目录 tmp → 回读 → os.link）；比对模式只写 output/data/trade_cal_compare_<stamp>/。
```python
PROTECTED = {(ROOT / p).resolve() for p in ("data/v2/calendar/trade_cal_sse_pit.parquet",
                                            "data/v2/calendar/manifest.json",
                                            "data/v2/tushare_raw/trade_cal.parquet")}
def _guard_write(path, allowed_roots):
    q = pathlib.Path(path).resolve()
    if q in PROTECTED:
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): 受保护路径 {q}")
    if not any(q.is_relative_to(r.resolve()) for r in allowed_roots):
        raise SystemExit(f"REFUSED (trade_cal_pit_v2): 不在本模式允许的写入目录 {q}")
    return q
```
- **daily_pull 标记（新发现，阻断级，须今天定）**：tushare_raw/trade_cal.parquet 不是被 trade_cal 步骤写，而是被日更 daily_pull 步骤写：tier1_pull.py（sha b630bca2）extend 分支 L85 经 datahub（不走中转，所以中转宕机时照样成功）拉 20260901–20261231，L87–92 与旧表合并后直接 to_parquet 覆盖（非原子）。logs/nightly 下 10-14、10-15、10-16 的 daily_pull 日志都有「cal refreshed」。所以：
  - 10-19 05:55 日更按已批准的 --steps（去掉 trade_cal 与 sw，保留 daily_pull）仍会写第三个受保护路径，sha 核对必然报 MUST_NOT_CHANGE；
  - 内容即使相同，parquet 字节与 mtime / inode 也会变。
  - 选项（Data 不擅自改，见 Q7）：(a) 10-19 日更再去掉 daily_pull（日线停在 10-16，纸面数据日期须评估）；(b) Arch 把该文件在 10-19 改为 EXPECTED_CHANGE，并改为核内容（cal_date / is_open 逐格相同）而非字节；(c) 纸面之后给 tier1_pull.py 加只读日历开关或改写到新目录（code-change，另 .ok）。
- **Eng 日历的 2027 问题（新发现）**：tier1_pull.py 拉取区间写死到 20261231（L85），所以 tushare_raw/trade_cal.parquet 也止于 2026-12-31（按代码推断，没有读 parquet 核对）。纸面的 trade_calendar.py、cyq_perf_monthly.py（L16）、fill_hsgt_top10_extend.py（L33、L39）、_light_event_windows_pull.py（L292）都读它，2027 年起同样会缺日。它不在本包交付物里（owner：Eng 纸面 + Data 采集），本包只把它列为受保护路径；延长方案另报（Q8）。

## 5. P3-1 / P3-3：.ok 计数（11:10 ET 重新计数，命令与范围如下）
- 范围 A：output docs（与 Arch 同范围）。范围 B：repo 顶层除 data 外全部目录（_recovery _review backups docs logs output qlab_b quantlab research rev scripts scripts_eng services tests），不含隐藏目录。
| 组 | 命令 | .ok 总数 | fa4260b8 命中 |
|---|---|---|---|
| A 不含 _consumed | `rg --files -g "*.ok" -g "!**/_consumed/**" output docs` | 13 | 0（`rg -l -g "*.ok" -g "!**/_consumed/**" fa4260b8 output docs`） |
| A 含 _consumed | `rg --files -g "*.ok" output docs` | 32 | 0 |
| B 不含 _consumed | `rg --files -g "*.ok" -g "!data/**" -g "!**/_consumed/**" <B 目录>` | 13 | 0 |
| B 含 _consumed | `rg --files -g "*.ok" -g "!data/**" <B 目录>` | 32 | 0 |
| B 不含 _consumed，-uu（不理会 .gitignore） | 同上加 -uu | 14 | 0 |
| B 含 _consumed，-uu | 同上加 -uu | 49 | 0 |
- 结论不变：没有活的 .ok 用 sha 钉住日历文件。r1 的「data/ 以外共 46 个」无法用任何一组复现，撤回；可能是当时混用了忽略规则或范围，记 Data 的错误。Arch 的「全仓 32」与 B 含 _consumed 一致。
- §8 枚举命令改为（每条都成对，先不含 _consumed 再含）：
  - `rg -l --no-messages -g "*.ok" -g "!data/**" -g "!**/_consumed/**" fa4260b8 <B 目录>` 与 `rg -l --no-messages -g "*.ok" -g "!data/**" fa4260b8 <B 目录>`，再各加 -uu 一次；
  - `rg -l --no-messages --max-filesize 2M -g "!data/**" -g "!*.parquet" -g "!**/_consumed/**" fa4260b8 <B 目录>` 与去掉 _consumed 排除的同一条；
  - `rg -n --no-messages -g "!data/**" "trade_cal_sse_pit|data/v2/calendar|TRADE_CAL_SHA_PIN|tushare_raw/trade_cal" -g "*.py" scripts scripts_eng research quantlab tests`（新增 tushare_raw/trade_cal，覆盖第三个受保护路径的读者）。
  - 不再用 `.` 作搜索根；结果写到文件再读，不接管道。

## 6. P3-2：nightly_update.py 串行落地
- 当前基线 ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636。
- 计划顺序：SW L1 PIT v2 包先落（ec079d56 → 987e273d6591244bb6c823bcd84492991f2407775a2278beb19c405a38787fd6，见 SW r3.1 §2.3），日历包的 nightly diff 以 987e273d 为基线重新生成后再申请 code-change .ok。若日历包先落，则 SW 包以日历包落地后的 sha 为基线重出 diff。
- 每份 code-change .ok 钉「基线 sha + 应用后 sha」；落地前重算基线，不一致即停。两包不在同一 .ok、不在同一天落地。

## 7. 开放问题答复的落实
- Q2：首次切换在代码里显式钉 v2027 全长 sha（TRADE_CAL_SHA_PIN，Strategy 交 code-change）；trade_cal_APPROVED.json 只作交叉核对：读者先验文件 sha = 代码钉，再验指针 sha = 代码钉，任一不符即拒绝。以后改为读指针另提案。
- Q3：不写周一至周五临时版。selftest 用例 12：holiday_notice 缺失时 write 模式拒绝写 2027 段。12-15 前公告未发布，Data 报主 Agent 与 Arch，另议 2026-12-31 11:00 ET 硬停的处置。
- Q6：不与 SW 同批；SW 继续钉 fa4260b8，只有 v2.1 拖到 2027 才在同一 code-change .ok 改钉。

## 8. 开放问题（更新）
- Q4：Intel 日常循环何时开始调用共享函数（主 Agent / Intel）。
- Q5：g1g5 三个脚本的 owner（主 Agent）。
- **Q7（今天须定）**：10-19 05:55 ET 日更里的 daily_pull 会写 tushare_raw/trade_cal.parquet（§4）。选 (a) / (b) / (c)？请 Arch 与主 Agent 定；与 BACKFILL_1014_1016_OK_REQUEST_ZH.md 的 F1 / Q1 是同一个问题。
- Q8：Eng 纸面日历（tushare_raw/trade_cal.parquet）的 2027 延长归谁做、何时做？建议与本包同期（12-15 前），由 Eng 定读者切换方式。

## 9. 排期（不变）
- r2 交 Arch：2026-10-18。定稿 11-30 前，Arch 12-15 前审完。代码落地与运行都在 10-19 纸面之后，各需 Arch .ok，一次一个，运行前对齐 94322 是否停 T。
