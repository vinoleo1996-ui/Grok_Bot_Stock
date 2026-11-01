# daily_basic 增量重建设计（只写文档，不改代码；Data 起草，交 Arch 审、Eng 实现）

- 作者：QuantLab Data；写于 2026-10-18T16:35:47-0400（取自 date）。
- 背景：主 Agent 10-18 16:27 ET 选方案 A（今晚不改代码）。v3.1 驱动（run_nightly_v1.py f99dd11a）的 RSS 停止线是树合计 1484800 kB、单进程 1536000 kB（驱动 L85–86、L515–516）。daily_basic 全量重建唯一的实测峰值是 2143204 kB（见 1.4）。10-19 call B 可能在 daily_basic 这一步被 RSS 停树。本文给出从 10-20 起启用的增量方案。
- 本文只读了代码、日志和成品 parquet 的元数据（pyarrow.parquet.read_metadata / read_schema），没有读行数据，也没有运行项目代码。凡是标「估算」的数字都没有实测过，必须在 selftest 或影子运行里实测确认。
- live=false，promotion_approved=false；不涉及 8787 和 moneyflow。

---

## 1. 现状

### 1.1 代码位置
- 文件：scripts/acquire/tier1_materialize.py，sha256 e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb，650 行，mtime 2026-10-18 01:12:24 ET。这个 mtime 是 10-18 01:1x 恢复时重写留下的，不代表代码修改时间。
- 驱动把它钉在 sha_tier1_materialize（run_nightly_v1.py L66；.ok 申请 R3 L63）。所以改代码以后，驱动的钉 sha 和 .ok 都要换新版。
- 调用方：scripts/nightly_update.py L32 `m.materialize_daily_basic(end=ymd)`，经 L25 的 `python3 -c "import tier1_materialize as m; ..."` 起单独进程。默认 start=20140101，也就是从 2014 年全量重建。
- materialize_daily_basic：L285–419。
  - L291：取 start ≤ 文件名 ≤ end 的原始文件。
  - L309–314：如果成品已存在，先 shutil.copy2 备份到 backups/valuation/daily_basic_full_tushare.<YYYYMMDD_HHMM>.parquet，然后 _prune_daily_basic_backups 只留 5 份（L168–177；设了 QL_DAILY_BASIC_NO_PRUNE=1 就不删）。
  - L316–349 _one：逐个原始文件转换成 22 列，L348 按 (ts_code, trade_date) 去重，keep="last"。
  - L356–384：按年分批。每年把该年各文件的 DataFrame 放进 chunk 列表，L372 pd.concat，L373 del chunk，L374 在年内再去重一次（keep="last"），L381 写成 _daily_basic_parts_<stamp>/y<YYYY>.parquet，L382 del m。
  - L388–393：pq.ParquetWriter 以 2014 分片的 schema 为准（L388），**逐个分片**做 pq.read_table + write_table（L391–392），写到 daily_basic_full_tushare.tmp.parquet，最后 os.replace（L393）。最终合并**不做**全表 concat，内存里同时只有一年的 Arrow 表。
  - L396–399：history_diff，见 1.3。
  - L401–416：manifest。L416 直接 write_text，**不是原子写**。
  - L417 _patch_daily_basic_status（L247–283）：按 1 MiB 分块流式算成品 sha（L264–267），再把 output/daily_update_status.json 原子写回（L280–282）。
- 排序：代码里**没有显式排序**。行序由三层决定：年份升序（L363）、文件名升序（L291 sorted）、文件内原始顺序（经 L348 去重和 reset_index）。
- 去重键：(ts_code, trade_date)，keep="last"（L348、L374）。

### 1.2 成品元数据（read_metadata / read_schema，只读，16:3x ET）
- data/v2/valuation/daily_basic_full_tushare.parquet：745,129,744 B。12,309,945 行，18 个 row group，22 列。created_by parquet-cpp-arrow 26.0.0，format 2.6，SNAPPY 压缩。schema 里带 pandas 元数据（2798 B）。
- 列与类型：
  - ts_code、instrument_id：large_string；
  - trade_date：timestamp[us]；
  - close、turnover_rate、turnover_rate_f、volume_ratio、pe、pe_ttm、pb、ps、ps_ttm、dv_ttm、total_share、float_share、free_share、total_mv、float_mktcap：double，共 15 列；
  - available_at：timestamp[us, tz=Asia/Shanghai]；
  - source、quality_status：large_string；
  - promotion_approved：bool。
- 各年行数，由 row group 统计与 10-16 日志 running_rows 两边算出，两者一致：

| 年 | 行数 | 年 | 行数 |
|---|---|---|---|
| 2014 | 570,677 | 2021 | 1,062,121 |
| 2015 | 570,310 | 2022 | 1,171,417 |
| 2016 | 642,209 | 2023 | 1,258,463 |
| 2017 | 743,941 | 2024 | 1,292,960 |
| 2018 | 817,637 | 2025 | 1,313,182 |
| 2019 | 885,332 | 2026（到 10-16） | 1,035,157 |
| 2020 | 946,539 | | |

- row group 布局：每年调用一次 write_table（L392），Arrow 在 1,048,576 行处切开。2021–2025 每年各 2 个 row group，其余年份 1 个。按 trade_date 的 min/max 统计，**18 个 row group 都只含一个年份**。最大的 row group 有 1,048,576 行，未压缩数据页约 75.8 MB（rg15，2025 年前段）。全表未压缩约 873 MB，压缩后约 745 MB。

### 1.3 现有 history_diff 机制
- L396–399：有备份时调 _compare_daily_basic_files(备份, 新成品)，把结果写进 manifest 的 history_diff_rows（L413），并经 L274 写进 daily_update_status。eng_daily_panels.py L166 的注释写明要保留这两个字段。
- _compare_daily_basic_files（L207–245）按自然年比较：
  - L210 先把旧文件整列 trade_date 读进来取年份；
  - 每年用 filters 读新旧两边的 17 列，L225–226；
  - filters 失败就退回成整表读两份（L230–231），这条回退路径内存很高。
- _compare_daily_basic_history（L179–205）：
  - L183–184 先 copy；
  - L185–188 遇到重复键就 raise；
  - 只比较新旧都有的 trade_date；
  - L196 做 outer merge；
  - L203 判值不等。NaN 与 NaN 视为相等。浮点用 != 比较，所以 -0.0 与 0.0 视为相等。
- 现有实现只输出差异**行数**，不输出差异明细。

### 1.4 已知峰值（只引日志实测）
- 唯一实测：logs/nightly/daily_basic_rebuild_20261014b.log L31「elapsed=70.27 maxrss_kb=2143204 exit=0」，即约 2.04 GiB（≈2.1 GB）。
  - 这次跑时已经有按年分批：同一日志 L3–15 有「year 2014 -> y2014.parquet」等行（L384 才会打印），L16–28 有「history_diff year=…」（L243 才会打印）。
  - 也就是说，**分批之后**的峰值仍然是 2.1 GB。
  - 这次跑在 dupfix 之前：2023 年 running_rows 是 8668917，之后各次是 8668646，差 271 行；备份目录里也有 20261014_1137_dupbug。
- 10-14 18:03、10-17 23:57、10-18 00:20 这三次 daily_basic 日志（logs/nightly/20261014|15|16_daily_basic.log）**没有任何内存记录**。
- 峰值出在哪一阶段（年度构建、ParquetWriter 合并还是 history_diff）**没有分阶段实测**。按代码结构推断，2023–2025 这几年（约 1.26–1.31M 行）的 history_diff 是 outer merge，两边先各 copy（L183–184），再 merge 出 30 多列，很可能是峰值所在；年度构建的 concat 加去重（L372–374）在同一年会短暂同时持有两份。这一条是推断，未实测。

## 2. 设计

### 2.1 总体
- 新增 materialize_daily_basic(…, mode="incremental")，nightly 默认用这个模式。原来的全量路径保留为 mode="full"，但 nightly 不允许走 full。增量前置条件不满足时，直接失败（FAILED，reason=DB_INCR_PRECOND），**不自动退回全量**，因为全量实测会超过停止线。
- 重建集合 R：只包含 D 所在的年份 Y=D[:4]；遇到 2.2、2.3 的情况再加年份。
- 拷贝集合 C：2014..Y 中不在 R 里的年份。从上一版成品逐个 row group 拷贝。
- 输出：daily_basic_full_tushare.tmp.parquet（与现有 L389 同名）。逐年、逐 row group 写入，校验通过才 os.replace。

### 2.2 跨年边界与年初第一个交易日
- D 是当年第一个开市日时（例如 2027-01-04，以 PIN 交易日历为准），R={Y-1, Y}：上一年整年重建一次，补上 12 月最后几天原始文件的迟到修订。
- 整个 1 月（D[4:6]=="01"）都用 R={Y-1, Y}。代价是 1 月里每晚重建约 1.3M 行（估算按 2025 年 1,313,182 行），峰值接近一年中最高的情形。selftest 必须覆盖这个情形。
- 2 月 1 日起恢复为 R={Y}。
- Y 年当年还没有任何原始文件（不应发生）时：失败，不写。

### 2.3 当年 / 旧年源文件有修订
- 当年：R 里的年份每晚都从原始文件整年重建，修订会自动覆盖。
- 旧年：manifest 新增 raw_inventory，按年记录 {n_files, total_bytes, digest}。digest 是对排好序的 (文件名, size, mtime_ns) 列表取 sha256。
  - 每晚只对旧年做 os.stat，不读内容，开销很小。如果某个旧年的 digest 与上一版 manifest 不同（有文件新增、删除或改动），就把该年加进 R，同时在回执里写一条 P2 提示，列出变化的文件名。
  - 一晚加进 R 的旧年超过 2 个时：失败（DB_INCR_TOO_MANY_YEARS），交人工决定，不自动多年重建，以免超内存。
  - 待定：mtime_ns 会被恢复脚本改写。10-18 01:1x 那次恢复就改过所有 mtime。所以首次启用、以及每次恢复之后，要用一次 sha256 版 digest 重新定基线（只读，IO 约 1.4 GB）。是否每周做一次 sha 版全量复核，由 Arch 定。
- 上一版成品与 manifest 不匹配时，不能把它当拷贝源，直接失败，不退回全量。不匹配包括：sha 与 daily_update_status 记录的不同；schema 不同；某个 row group 横跨两年；各年行数与 manifest 的 rows_by_year 不同。

### 2.4 旧年怎么拼接：两种做法的比较（推荐 B）
- A. 旧年按年分片长期保存（例如 data/v2/valuation/_daily_basic_years/yYYYY.parquet），每晚读整年分片再写入。
  - 读写都以一年为单位，2025 年约 1.31M 行要整年进内存。
  - 要多存约 745 MB。
  - 分片和成品是两份真相，必须额外保证一致。
- B. 从上一版成品按 row group 流式拷贝：pq.ParquetFile(prev).read_row_group(i)，然后 writer.write_table(t)，再 del t。
  - 内存上界是最大的那个 row group：1,048,576 行，未压缩数据页约 75.8 MB。Arrow 内存表大约是同一量级（估算，因为 large_string 有偏移数组，要加一些）。
  - 没有第二份状态，上一版成品就是唯一来源。
  - 不足：每晚要解压再压缩旧年数据。CPU 时间估算与现有合并阶段（L390–392）相近，未实测。
- **推荐 B**：内存上界是 row group 级（约百 MB 级，估算），比 A 的一整年更低，而且不引入新的持久状态。
- 前提：每个 row group 只含一个年份（1.2 已核实现成品是这样）。实现时先用 row group 统计逐个核验，横跨两年的直接失败。新写入的当年数据按 1,048,576 行缓冲后再写（见 2.5），以保持这个性质。

### 2.5 当年怎么重建
- 每个原始文件仍用现有 _one（L316–349）转换，结果逐列与全量路径一致；然后马上转成 pa.Table.from_pandas(y, schema=SCHEMA, preserve_index=False)，丢掉 DataFrame。
- 新增断言：每个文件 trade_date 的 min=max=文件名日期。满足的话，年内跨文件不可能有重复键，L374 那次年内去重就退化为空操作。
  - 实现保留一个检查：用 Arrow 对整年 (ts_code, trade_date) 做唯一性统计，有重复就失败（DB_INCR_DUPKEY），不做静默去重。这样增量路径的行序与全量路径完全一致：文件升序，文件内原始顺序加 keep=last 去重。
- 把 Arrow 表放进缓冲区，累计到 ≥1,048,576 行或者到年末，就 pa.concat_tables 后写入一次，与现有 row group 布局一致。缓冲区上界约 1.05M 行（估算 200–300 MB，未实测）。

### 2.6 schema 固定
- SCHEMA 写成代码常量（22 列，名称、顺序、类型同 1.2），pandas 元数据取自上一版成品的 read_schema。每段写入前都 cast 到 SCHEMA，cast 失败就失败。
- 现有 L388 用 2014 分片的 schema 做准，增量版改为用常量，同时核对它与上一版成品的 schema 一致（比较时忽略 metadata；pandas 元数据里的列 dtype 另做一次比较）。
- 排序键（对账用）：(trade_date, ts_code)。去重键：(ts_code, trade_date)，keep="last"（与 L348、L374 一致）。
- 写盘行序：年份升序；旧年是上一版成品里的原 row group 顺序；当年是文件升序、文件内原始顺序。
- available_at = trade_date + 18:00 Asia/Shanghai（L341–342）；source、quality_status、promotion_approved 与 L343–345 相同。

### 2.7 备份（保留上一版）
- os.replace 之前，沿用 L309–314：shutil.copy2 把上一版成品复制到 backups/valuation/daily_basic_full_tushare.<YYYYMMDD_HHMM>.parquet，保留 5 份（L168–177，keep=5，按文件名排序后删最旧的）。
- 现有 5 份备份约 3.7 GB；/ 分区可用 73 GB（df，16:3x ET）。
- 备份失败就不替换。

### 2.8 history_diff 与差异报告
- 旧年：拷贝来的值和上一版成品逐值相同。每个 row group 写完，对新旧同一 row group 按 4.2 的办法算列 hash 再比较，开销是 row group 级，不再做 outer merge。只要有一年不同，就**不替换**成品，FAILED（DB_INCR_OLDYEAR_DIFF），并输出差异报告。
- R 里的年份：沿用 _compare_daily_basic_history（L179–205）的判定口径，但改成**按月**比较（每次约 0.1M 行，估算），替代按年比较，用来降低 L196 outer merge 的峰值。比较对象是 tmp 成品和上一版成品，也就是在 os.replace **之前**比较。
- 差异报告：output/daily_basic_history_diff/<D>_<stamp>.json，原子写，内容包括：
  - 按年、按月的差异行数；
  - 每类最多 100 个样例键 (ts_code, trade_date)，附差异列名和新旧值；
  - 新旧的 sha；
  - 写明 R 和 C 各是哪些年。
- R 里年份的差异（源文件修订）只记录并在回执里披露，阈值由 Arch 定。建议当年非最后 5 个开市日的历史差异行数 > 0 时记 P2，不挡 DONE。旧年差异一律挡。
- manifest 和 status 里的 history_diff_rows 保留原含义（总差异行数），另加 history_diff_by_year 和 history_diff_report 路径。

### 2.9 manifest 写法
- 保留现有全部键（L401–415），键名和含义不变，schema 字符串仍是 quantlab.v2.daily_basic_full_tushare.v1。新增 build 子对象：
  - mode（incremental / full）；
  - rebuilt_years、copied_years；
  - rows_by_year、row_groups_by_year；
  - prev_sha256、new_sha256；
  - raw_inventory（按年）；
  - peak_rss_kb、phase_rss_kb（各阶段读 /proc/self/status 的 VmHWM/VmRSS）；
  - history_diff_by_year、history_diff_report、backup_path。
- 改成 tmp + os.replace 原子写，修掉 L416 的非原子写。写的顺序：成品 os.replace，然后 manifest，然后 status（L417）。manifest 写失败就报错，退出码非 0。成品已替换但 manifest 是旧的这种不一致，要由下次运行的前置检查（2.3：sha 与 status 对不上）拦住。

### 2.10 失败回滚
- 任何异常（包括 RSS 自检超限）都这样处理：先关闭 writer，再删 tmp（只删本次创建的那个 tmp 路径），**不替换**成品，**不写**manifest 和 status，退出码非 0，打印 reason。
- 旧成品和旧 manifest 始终不动。本次做的备份是多出来的一份，无害，按 keep=5 正常轮转。
- 启动时如果发现上次残留的 daily_basic_full_tushare.tmp.parquet：不删，失败（DB_INCR_STALE_TMP），交人工处理，与「*.tmp.parquet 残留即不合格」的口径一致。
- 不再使用 _daily_basic_parts_<stamp> 目录。现有 L353–354 会 rmtree 同名目录，增量版去掉这一步。

### 2.11 年份切换（2027-01）
- 2027 年第一个开市日：R={2026, 2027}，C=2014..2025。2026 年整年重建（约 1.3M 行，估算），2027 年只有 1 个文件。
- 依赖：2027 年交易日历包（cal_2027，tier1_pull L85 写死了 20261231），以及 2027 原始文件能正常拉到。这些不属于本设计，但它们没就绪时，增量版要能清楚失败：比如 D 年份没有原始文件就失败，不能写出一个缺年份的成品。
- 2 月 1 日起 R={2027}。

### 2.12 end 小于成品末日（回补场景）
- 现有全量路径用 end=D 时，会把成品截到 D（BACKFILL_1014_1016_OK_REQUEST_ZH.md 的 F2）。
- 增量版的规则：end 所在年份 < 上一版成品最大年份时，直接失败；end 所在年份 = 当年时，当年只重建到 end，行为与现有一致，同样会截断，回执要写明。
- 是否要加一个「end < 成品末日就拒绝」的保护，由 Arch 定（列入未决问题）。

## 3. 峰值目标 ≤ 1.2 GB 与内存构成（全部是估算，需实测）

- 测量口径：VmHWM（进程峰值）和驱动树合计 RSS。目标是单进程峰值 ≤ 1.2 GB（建议按 1,200,000 kB 计），比驱动树合计停止线 1,484,800 kB 留约 280 MB 余量。
- 各阶段常驻内存（估算，没有实测）：
  1. 解释器 + pandas + pyarrow 导入：基线未知，这次没有测，selftest 第一项就是测它。
  2. 旧年拷贝：一次一个 row group，≤1,048,576 行。数据页未压缩约 75.8 MB（元数据实测），Arrow 解码后估算 ≤ 约 150 MB。
     - 推理：15 列 double 和 2 列 timestamp 是每行 8 B；2 列 ts_code / instrument_id 的 large_string 每行约 9–10 B 字符加 8 B 偏移；source / quality_status 在 Arrow 里不共享，每行各约 20 B 加偏移。
  3. 当年构建：缓冲 ≤ 约 1.05M 行 Arrow 表（估算 200–300 MB）。concat_tables 只拼接 chunk，不复制。write_table 时的编码缓冲另计，未知。
     - 单个文件的 pandas 中间结果约 5.5k 行，可忽略。
     - **不再**出现 L372 那种整年 pandas 对象的拼接（字符串是 Python 对象，估算每行 250–300 B）。
  4. history_diff（当年按月）：新旧各约 0.1M 行 × 17 列，加 merge 结果，估算 < 100 MB。
  5. 旧年 row group hash 比对：新旧各一个 row group，估算 ≤ 300 MB。这一步可以与第 2 步合成一遍：读一次旧 row group，写出，同时算 hash。
  6. 流式 sha（L264–267）：1 MiB 缓冲。
- 以上合计的峰值应出现在第 3 步或第 5 步，估算是基线加 300–400 MB 量级。**这只是按代码结构的推理，不能当成通过依据**，要在 selftest 的合成数据和影子运行里实测。
- Python 和 Arrow 的内存池不一定把内存还给系统（VmRSS 只增不减的可能）。所以每个阶段结束要显式 del，并调用 pa.default_memory_pool().release_unused()（如果可用），然后记录 VmRSS。
- RSS 自检与超限中止：
  - 每处理完一个 row group、一个原始文件、一个月，都读一次 /proc/self/status 的 VmRSS 和 VmHWM。
  - 超过 QL_DB_RSS_ABORT_KB（默认 1200000）就 raise（DB_INCR_RSS_SELF_ABORT），走 2.10 的回滚。
  - 各阶段的读数写进 stdout（格式：「PHASE <名> rss_kb=… hwm_kb=…」）和 manifest 的 build.phase_rss_kb。
  - 结束时打印「elapsed=… maxrss_kb=… exit=…」，与 10-14b 日志 L31 的格式相同，方便以后对比。
  - 驱动自身的 5 秒采样（驱动 L507–516）仍然是外层保护。

## 4. 对账方法（增量成品 vs 全量重建成品）

### 4.1 基准
- 现成品（built_at 2026-10-18T00:21:47-0400，end=20261016，12,309,945 行）本身就是一次全量重建的产物，可以直接当基准，**不用再跑一次 2.1 GB 的全量**。
- 影子增量：拷贝源用备份 daily_basic_full_tushare.20261017_2357.parquet（end=20261015 的全量），参数 end=20261016，输出到 /tmp。结果应与现成品逐年一致。这样旧年拷贝和当年重建两部分都能被检验到。
- 注意：影子运行要读真实原始文件（2026 年）和真实成品，必须单独签 .ok（allow_real_data=true，只读，out_dir 限 /tmp）。只能在空档跑，不和 94322 等重任务重叠，跑前通知主 Agent 和 Arch。
- 如果 Arch 要求另做一份新的全量基准，就是 2.1 GB 级别的运行，必须单独签 .ok 并安排空档。

### 4.2 算法（逐年、分块，控制内存）
- 每年先比行数：rows_inc[y] == rows_full[y]。
- 然后按月读取（filters trade_date 在当月），用 pyarrow.compute.sort_indices 按 (trade_date 升序, ts_code 升序) 排序后 take。排序键在去重后唯一，所以是全序。
- 对每一列维护一个 hashlib.sha256，按年累加，各月按时间顺序依次喂入。每列的规范化序列化：
  - double：先输出 1 字节有效位（null 或 NaN 记 0，否则记 1），再输出 8 字节小端值；无效值写 8 个 0x00；-0.0 规范成 +0.0。这样 NaN 等于 NaN、-0 等于 +0，与现有 L203 的判等口径一致。pandas 写盘时 NaN 会存成 null，两种都归为无效。
  - timestamp：1 字节有效位，再加 int64 微秒小端值。tz 不进 hash，单独比较 schema 里的 tz 字符串必须都是 Asia/Shanghai。
  - large_string：1 字节有效位，再加 4 字节小端长度和 UTF-8 字节。
  - bool：1 字节有效位，再加 1 字节值。
- 实现上用 pyarrow.compute 先算出有效位和规范值数组，再用 numpy 视图 tobytes 分批喂进 hash，每批 ≤ 65,536 行，不逐行跑 Python 循环。
- 输出 rows_by_year、hash_by_year_col（22 列 × 年数）、schema 对比（不含 metadata）和 pandas 元数据 dtype 对比。
- **一致标准**：每年的行数和 22 列 hash 全部相同，schema 相同。只要有一项不同就判不通过，并按月定位差异，列出样例键。
- 另外，对 tmp 成品按 1 MiB 分块算文件 sha。只用于记录，不作为一致标准，因为 row group 的编码可能不同。

### 4.3 门禁
- 对账脚本本身也需要 Arch 的 .ok，只在空档跑，单独一个进程，带 3 节的 RSS 自检。产出写到 /tmp/<out_dir>/，附回执和 sha。

## 5. 实施与门禁

### 5.1 分工与顺序
1. Data：本文交 Arch 审，抄送 Eng。Arch 定 2.3、2.8、2.12 和第 6 节的未决项。
2. Eng：10-19 18:40 ET 之后实现（10-19 纸面跑完之前不碰代码）。改代码前先把 scripts/acquire/tier1_materialize.py（e9c89a6c…）和 scripts/nightly_update.py（ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636）归档到 /workspace/QuantLab/_recovery/data/daily_basic_incr_<stamp>/，附 sha。改成新版文件，不要原地覆盖正在审的文件。
3. Eng：用 /tmp 合成数据测内存（5.2），交 selftest 回执。
4. Arch 审代码 diff 和 selftest 回执。审过后另签：影子运行 .ok（4.1）、10-20 日更 .ok。要同时更新驱动钉的 sha_tier1_materialize（驱动 L66）和 .ok 钉 sha，这涉及驱动或 .ok 换版，由 Arch 定。
5. 10-20 日更启用。nightly_update.py L32 改成显式 mode="incremental"，或者把增量设成默认，二者选一，由 Arch 定。首晚回执附 manifest.build 和全部 PHASE 读数。

### 5.2 selftest 与 .ok 要求
- .ok：scope=selftest，allow_real_data=false，out_dir 只能在 /tmp 下。测试文件开头先调用 enforce(modes=["selftest"])，写法照现有 selftest 的样式，例如 docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1_c.py L17 起。
- 合成数据：在 /tmp 生成假的原始 daily_basic 日文件，规模接近真实：每日约 5,500 个代码，覆盖 2014–2026 全部年份。总行数和每年行数接近 1.2 节；最大年约 1.31M 行。
- 必须覆盖的用例：
  - 普通日；
  - 年初第一个开市日（R={Y-1,Y}）；
  - 1 月非首日；
  - 旧年原始文件被改（digest 变化）；
  - 旧年改动超过 2 年（失败）；
  - row group 横跨两年的上一版成品（失败）；
  - 重复键（失败）；
  - 残留 tmp（失败）；
  - RSS 自检超限（把 QL_DB_RSS_ABORT_KB 调低来触发，确认会回滚）；
  - manifest 写失败；
  - end 年份小于成品年份（失败）；
  - 增量结果与同一合成数据的全量结果按 4.2 对账一致。
- 每个用例都要记录 VmHWM。最坏用例（1 月、最大年）的峰值必须 ≤ 1,200,000 kB，否则不进入 Arch 审。

### 5.3 风险与未决问题
1. 3 节全部是估算。只有 selftest 和影子运行的实测才算数。
2. 驱动钉了 tier1_materialize 的 sha（L66），改代码就要驱动或 .ok 换版。10-20 的时间表由 Arch 和主 Agent 定。
3. 旧年 digest 用的 mtime_ns 会被恢复脚本改写（10-18 01:1x 已经发生过）。需要 sha 基线，以及恢复后重新定基线的规则。
4. 当年历史差异（源文件修订）的上报阈值（2.8）。
5. 回补场景的截断（2.12，F2）：是否禁止 end 小于成品末日。
6. 1 月每晚都重建两年，是全年峰值最高的时段，可能需要单独的内存门槛。
7. 现有 L416 manifest 非原子、L230–231 filters 失败时退回整表读取：这两处是全量路径的现有问题，增量版去掉了，全量路径是否顺手修，由 Arch 定。
8. Arrow 内存池不一定把内存还给系统，selftest 里的 VmHWM 才是准的。
9. 10-19 今晚仍然是旧代码（方案 A），call B 在 daily_basic 一步可能触发 RSS 停树。按 R4.3 六.5 的口径，这记 P2，不重试。10-20 启用的前置条件是同时满足两项：出新版驱动（改掉 run_nightly_v1.py L66 钉的 sha_tier1_materialize e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb），并且 Arch 另签 .ok。

## 6. 建议代码草图（只作文档内容，**未应用到任何代码**；以 Eng 的实现和 Arch 的审查为准）

```python
# 草图：scripts/acquire/tier1_materialize.py 新增（不覆盖原函数）
RSS_ABORT_KB = int(os.environ.get("QL_DB_RSS_ABORT_KB", "1200000"))
RG_ROWS = 1048576

def _rss():
    v = {}
    for ln in open("/proc/self/status"):
        if ln.startswith(("VmRSS:", "VmHWM:")):
            k, n = ln.split()[:2]; v[k[:-1]] = int(n)
    return v

def _guard(phase, log):
    r = _rss(); log.append((phase, r)); print("PHASE", phase, "rss_kb=%d hwm_kb=%d" % (r["VmRSS"], r["VmHWM"]), flush=True)
    if r["VmRSS"] > RSS_ABORT_KB:
        raise RuntimeError("DB_INCR_RSS_SELF_ABORT %s %d" % (phase, r["VmRSS"]))

def materialize_daily_basic_incremental(end, start="20140101"):
    import pyarrow as pa, pyarrow.parquet as pq
    dest = ROOT/"data/v2/valuation/daily_basic_full_tushare.parquet"
    tmp = dest.with_suffix(".tmp.parquet")
    if tmp.exists(): raise RuntimeError("DB_INCR_STALE_TMP")
    prev = pq.ParquetFile(dest)                      # 前置：sha / schema / rows_by_year / rg 单年 校验（2.3）
    Y = int(end[:4]); R = {Y - 1, Y} if end[4:6] == "01" else {Y}
    R |= _changed_old_years(prev_manifest, end)     # 2.3 raw_inventory；>2 年即失败
    log = []; created = False
    try:
        w = pq.ParquetWriter(tmp, SCHEMA, compression="snappy"); created = True
        for y in range(int(start[:4]), Y + 1):
            if y not in R:
                for i in _rg_of_year(prev, y):          # 旧年：逐 row group 拷贝 + 列 hash 比对
                    t = prev.read_row_group(i).cast(SCHEMA); w.write_table(t); _hash_cmp(t, prev, i); del t
                    _guard("copy_%d_rg%d" % (y, i), log)
            else:
                buf, n = [], 0
                for f in _raw_files_of_year(y, end):    # 当年：逐文件 _one -> Arrow，缓冲到 RG_ROWS
                    df = _one(f)
                    if df is None: continue
                    _assert_single_date(df, f.stem)
                    buf.append(pa.Table.from_pandas(df, schema=SCHEMA, preserve_index=False)); n += len(df); del df
                    if n >= RG_ROWS:
                        w.write_table(pa.concat_tables(buf)); buf, n = [], 0; _guard("build_%d" % y, log)
                if buf: w.write_table(pa.concat_tables(buf)); buf = []
                _assert_unique_keys_year(tmp_or_buffers, y)  # 有重复即 DB_INCR_DUPKEY
                _guard("build_%d_end" % y, log)
        w.close()
        diff = _history_diff_by_month(dest, tmp, R)   # 2.8：R 年按月；旧年差异 -> 失败
        _backup_prev(dest)                             # 2.7：L309-314，keep=5
        os.replace(tmp, dest)
        _write_manifest_atomic(...); _patch_daily_basic_status(...)   # 2.9
    except BaseException:
        try: w.close()
        except Exception: pass
        if created and tmp.exists(): tmp.unlink()      # 只删本次创建的 tmp；旧成品不动
        raise
```

- 草图里的 _changed_old_years、_rg_of_year、_hash_cmp、_raw_files_of_year、_assert_single_date、_assert_unique_keys_year、_history_diff_by_month、_backup_prev、_write_manifest_atomic 都是待实现的辅助函数，按 2.x 节的约束实现。_assert_unique_keys_year 的具体做法（比如写入前对缓冲区做 Arrow group_by 计数）由 Eng 定，不能把整年重新读回成 pandas。

## 附：本文依据
- 代码：scripts/acquire/tier1_materialize.py e9c89a6c…（L164–177、L179–205、L207–245、L247–283、L285–419）；scripts/nightly_update.py ec079d56…（L25、L32）；run_nightly_v1.py f99dd11a…（L66、L85–86、L507–516）。
- 旧版：scripts/acquire/tier1_materialize.py.bak_20261014_1132（f68a5a6d…，L164 起是整表 concat，L198 concat 后 L201 写盘，没有分批）；.bak_20261014_dupfix（df37ad94…，已有分批，L278 起，keep=3，没有 L346–348 / L374 去重）；git HEAD（94a7a11，2026-10-12）里的版本没有分批。
- 日志：logs/nightly/daily_basic_rebuild_20261014b.log L1–31；daily_basic_rebuild_20261014.log L1–2；logs/nightly/20261014|15|16_daily_basic.log。
- 成品元数据：data/v2/valuation/daily_basic_full_tushare.parquet（read_metadata / read_schema，只读）；daily_basic_full_tushare_manifest.json。

## v2 变更记录
- 写于 2026-10-18T16:40:32-0400（取自 date）；依据 Arch 10-18 16:39 ET；源文档 docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_ZH.md（60d920231db67912658c94467c4d2efd4d8e6f3bf7307f8de25a0987742f580f，本身未动）。
- 只改两处：5.3 第 9 条末尾补写 10-20 启用的前置条件（新版驱动改掉 L66 钉的 tier1_materialize sha，且 Arch 另签 .ok）；文末新增本节。其余内容未动。
