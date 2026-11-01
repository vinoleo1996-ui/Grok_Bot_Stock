# Arch 审查：daily_basic 增量重建设计 v2

- 审查对象：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v2_ZH.md，sha256 e6372b9b0e67992a1ab1e77fcb038874e0f5ced85be37149fe6a84f88b74c08e，316 行（已核）。v2 相对 v1（60d920231db67912658c94467c4d2efd4d8e6f3bf7307f8de25a0987742f580f，已核）只改了 L245 的未决项 9，并在文末加了变更记录。L1–312 行号与 v1 相同，下文引用的「设计 Lxx」两版通用。
- 对照代码（sha 已核，均只读）：
  - scripts/acquire/tier1_materialize.py：e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb，650 行；
  - scripts/nightly_update.py：ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636；
  - docs/v2/audit/nightly_20261019/run_nightly_v1.py：f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a；
  - scripts/acquire/eng_daily_panels.py：只读 L140–181。
- 日志和元数据（只读）：
  - logs/nightly/daily_basic_rebuild_20261014b.log 的 L1–31；
  - data/v2/valuation/daily_basic_full_tushare_manifest.json；
  - 目录列表：backups/valuation/、tushare_raw/daily_basic/（只看文件名，共 3107 个）；
  - df 和 stat：data/、backups/、/tmp 在同一文件系统，st_dev=65040。
- 没有读任何真实数据行，没有运行项目代码，没有改仓库里的任何文件。本文是唯一的新文件。
- 合成探针：在 /tmp/arch_dbincr_probe/ 里只用随机合成数据跑过，不读真实数据，用的是驱动解释器 /usr/bin/python3（驱动 L36），pandas 3.0.6、pyarrow 26.0.0。文中凡标「探针」的数字都出自这里。合成数据是随机值，压缩比比真实数据差：合成每行约 125 B，真实成品 745,129,744 B / 12,309,945 行，约 60 B/行。所以这些数字只用来判断量级，不能当验收依据。
- 写于 2026-10-18T16:46:41-04:00（取自 date）。

## 结论：PASS_WITH_CONDITIONS（有条件通过）

方向正确，我同意以下几点：
- 旧年按 row group 流式拷贝（方案 B）；
- 当年从原始文件重建；
- 前置条件不满足就失败，不自动退回全量；
- 先写 tmp，校验通过后再 os.replace；
- schema 写成常量；
- 1 月同时重建上一年；
- 旧成品始终不动。

但有 8 条 P1 必须先写进设计 v3，经 Arch 复核后 Eng 才能动手。最关键的三条：
1. 第 3 节的内存估算偏低 3–4 倍，而且草图 L280 让同一个 row group 在内存里同时存在两份（P1-1）；
2. 2.8 节对旧年做的 hash 比对是拿拷贝和它的来源比，等于自己比自己，查不出任何修订（P1-2）；
3. 4.1 节的对账基准不可用：一是 10-18 01:1x 恢复原始文件之前就已建好，二是要做新的全量基准必然超过单进程 1536000 kB 的硬约束（P1-4）。

时间表：
- Data 在 10-19 12:00 ET 前交 v3；
- Arch 在 10-19 18:40 前复核；
- Eng 在 10-19 18:40 之后实现；
- 10-20 能否启用，看 selftest 和影子对账是否在 10-20 05:00 ET 前全部通过。任何一项没过，10-20 继续走旧路径，也就是接受方案 A 那样的 RSS 停树，这是 P2，不是事故。

---

## 一、发现（按等级）

### P1（实现前必须改）

**P1-1 内存估算偏低，真正的峰值在旧年拷贝和比对时 row group 的双驻留**（设计 L101、L168–176、L280）
- 设计估算解码一个 row group「≤ 约 150 MB」，拷贝加比对「≤ 300 MB」，总峰值是「基线加 300–400 MB」。
- 探针实测：一个 1,048,576 行、22 列、同 schema 的合成 row group，Arrow 表 nbytes 是 225 MB。
  - read_row_group 整读：VmHWM 增加 +506,560 kB；
  - 关掉 use_threads：+499,124 kB；
  - pre_buffer=False 加 buffer_size=1 MiB：+397,552 kB；
  - 同一个 row group 读两次，即草图 L280 的 `_hash_cmp(t, prev, i)` 再读一次旧 row group：VmRSS 到了 837,292 kB，write_table 之后是 862,320 kB；
  - 用 iter_batches(65536) 流式读写：只增加 +142,064 kB，但会切成 16 个 row group；
  - 导入 pandas 之后基线约 105,664 kB。
- 结论：如果照草图实现，单是拷贝阶段就会到约 0.85–0.95 GB（含基线），再加上 mimalloc 不还内存（探针：del 之后 VmRSS 回落到 272 MB，但 HWM 不变），很容易贴近 1,200,000 kB 的自检线。
- 要求：
  - 任何时刻只能有一个 row group 在内存里；
  - 拷贝时对内存里的 t 按 ≤65,536 行切片算 hash，不再读第二次；
  - 写完以后的校验改成「写后回读」，见 P1-2；
  - 读取用 pre_buffer=False、buffer_size=1 MiB、use_threads=False，selftest 里实测后再定。

**P1-2 2.8 节的「旧年 hash 比对」是自己比自己，起不到检测作用**（设计 L126、L174、L280）
- 写出的 t 就是从上一版 row group 读出来的，两边一定相等。它查不出供应商修订，也查不出代码变更，最多只能查出 cast 的问题，而 schema 一致时 cast 本来就是零拷贝。
- 改成两件事：
  1. 写后回读：w.close() 之后，逐个 row group 用 iter_batches 读 tmp，算列 hash，和拷贝时记下的 hash 比；同时比较行数，并核对 row group 的 trade_date 统计只覆盖一个年份。这样能查出编码和写盘的错误，峰值约 +140 MB（探针）。
  2. 旧年相对原始文件是否一致，交给 P2-4 的原始文件内容 sha 和 P1-4 的每周分年参考对账，不在每晚的拷贝里做。

**P1-3 拷贝旧年会把上一版的变换代码冻结住，必须钉住变换版本**（设计 L78、L100–104；代码 L316–349）
- 全量每晚用现行的 _one 重算所有年份；增量只用现行代码重算 R 里的年份，旧年保留的是建上一版成品时的代码的产物。
- 历史证据：10-14b 日志 L16–28 里 history_diff 累计 1919 行，分布在 2023–2025，其中 2023 年的 271 行就是 dupfix 改代码造成的（设计 L69）。
- 一旦 _one 或常量被改（比如单位、available_at 规则、去重规则），增量成品就会变成多个代码版本混在一起，而回执看不出来。
- 要求：
  - manifest.build 增加 transform_sha：对 _one 及其依赖（to_iid L12–22、_daily_basic_val_cols L164–166、L341–345 的常量）的规范化源码取 sha256，实现可以由 Eng 选，但必须固定；
  - 每晚前置检查：上一版的 transform_sha 必须等于当前的，不等就失败，reason_code=DB_INCR_TRANSFORM_CHANGED，退出码 28；
  - 变换改了以后，需要单独签 .ok，用 P1-4 的分年参考重建器重建所有年份，再重新定基线。

**P1-4 对账基准不能用现成品，也不能跑新的全量；改用分月参考重建器**（设计 L188–191）
- 现成品建于 10-18 00:21（manifest built_at 2026-10-18T00:21:47-0400），而原始文件在 10-18 01:1x 恢复时被重写了（设计 L13、L92）。所以现成品不能证明它和「现在的原始文件」做全量重建的结果一致。
- 再做一次 2.1 GB 的全量基准，违反单进程 RSS ≤ 1536000 kB 的硬约束，不能跑，也不能签 .ok。
- 替代办法：写一个参考重建器 ref_build。
  - 逻辑上就是 L316–349 的 _one，加上 L372–374 的拼接和去重，但按 trade_date 的自然月分区来做，一个进程只处理一年。
  - 为什么等价：去重键 (ts_code, trade_date) 包含 trade_date，同一个键不可能跨月；而 concat 保持文件顺序，所以每个分区里 keep="last" 的结果和整年去重完全一样。这一点不依赖「每个文件只有一个日期」的假设。
  - 每月约 0.1M 行，峰值低，具体数字由 selftest 实测。
- ref_build 只输出 4.2 节的逐年 hash，不写成品。它同时用于：
  1. 合成数据上的增量对账；
  2. 影子运行时，对 2014–2026 每一年和现行原始文件对账，这一步也顺带核实了所有拷贝年份；
  3. 每周复核（未决项 3）。
- 影子运行和每周复核都要单独签 .ok：只读，输出限 /tmp，单进程，不和 94322 等重任务重叠。

**P1-5 驱动的 TERM 不会触发回滚，tmp 会残留并且永久挡住后面的运行**（设计 L148、L150；驱动 L329、L516）
- 驱动 RSS 停树时用 stop_tree 发 TERM。Python 默认处理 SIGTERM 是直接退出，不执行 except 和 finally，所以草图 L299–303 的清理不会运行。
- 结果是 daily_basic_full_tushare.tmp.parquet 留下来，下一晚按 L150 判 DB_INCR_STALE_TMP，之后每晚都失败，直到人工处理。
- 要求：
  - 函数入口装 SIGTERM 和 SIGHUP 的 handler，把信号转成异常，走 2.10 的回滚；
  - 记下 tmp 创建时的 (st_dev, st_ino)，回滚时只删 inode 相同的那个文件；
  - SIGKILL 没法处理，残留时照 L150 失败；人工把残留移到 _quarantine/（移动，不删除），并单独签 .ok。

**P1-6 退出码不能用 2 和 3**（nightly_update.py L119–120）
- nightly_update 把 rc∈(0,2) 记成 ok，rc==3 记成 partial。如果增量版用 sys.exit(2) 表示失败，nightly 会把它当成功。
- python -c 里没有捕获的异常返回 1，这是可以的。
- 码表要求（必须写进代码和回执）：

| 退出码 | 含义 |
|---|---|
| 0 | OK |
| 1 | 未分类异常 |
| 20 | DB_INCR_PRECOND |
| 21 | DB_INCR_STALE_TMP |
| 22 | DB_INCR_RSS_SELF_ABORT |
| 23 | DB_INCR_OLDYEAR_DIFF（写后回读不一致） |
| 24 | DB_INCR_DUPKEY 或 DB_INCR_DATE_MISMATCH |
| 25 | DB_INCR_TOO_MANY_YEARS |
| 26 | DB_INCR_END_BEFORE_PREV |
| 27 | DB_INCR_RAW_TMP |
| 28 | DB_INCR_TRANSFORM_CHANGED |
| 30 | DB_INCR_COMMIT_PARTIAL（成品已替换，但 manifest 或 status 没写成，记 P1） |
| -15 | 驱动 TERM |

- 码号 2 和 3 永不使用。nightly_update.py L32 要改成 `sys.exit(m.materialize_daily_basic_cli(...))` 这种形式，见 P2-13。

**P1-7 10-19 旧代码失败后的现场和 10-20 首晚的引导（bootstrap）没有设计**（设计 L93、L145、L245；代码 L309–314、L352–355、L389–393、L416；eng_daily_panels L147–152）
- 10-19 的 call B 可能在不同位置被 RSS 停掉，每种留下的现场不同：
  - 停在年度构建：留下 data/v2/valuation/_daily_basic_parts_<stamp>/，这个目录要等 L353 遇到同名 stamp 才会清；而 L311–313 已经多做了一份备份，还按 keep=5 删掉了最旧的一份。
  - 停在 L390–392：留下 daily_basic_full_tushare.tmp.parquet，正好撞上增量版的 STALE_TMP。
  - 停在 L393 之后（history_diff 阶段）：成品已经换成新版，但 manifest 是旧的（L416 没执行）。随后 eng_panels 的 daily_core（L147–152）会按新文件重算 status 里的 sha、rows 和 last_date。
- 所以设计 L93 的「sha 与 daily_update_status 记录的不同」这项前置检查，证明不了成品和 manifest 一致。另外首晚的上一版 manifest 根本没有 build、rows_by_year、raw_inventory 这些键。
- 要求：
  1. 10-19 18:40 之后做一次只读的现场盘点：tmp、parts 目录、成品 sha 与 manifest、status 是否一致、备份清单、原始文件里的 *.tmp.parquet。回执要列 sha。
  2. 写一个独立的引导步骤，单独签 .ok：只读成品元数据，加上 P1-4 的分年对账，结果写到新文件 daily_basic_full_tushare_build_baseline.json（原子写）。内容包括：
     - 成品 sha；
     - rows_by_year、row_groups_by_year；
     - 每年的列 hash；
     - schema；
     - transform_sha；
     - 原始文件内容 sha 版的 raw_inventory。
  3. 增量前置检查改成：成品 sha == 上一版 manifest.build.new_sha256（首晚用基线文件的 sha）。status 里的 sha 只作旁证。

**P1-8 selftest 隔离：现有代码的路径是写死的**（代码 L5、L8、L249、L293–295）
- ROOT、RAW、status、valuation、backups 这些路径都写死了。selftest 如果直接调用，就会读真实原始文件、覆盖真实成品和 status，这违反「合成数据只能在 /tmp」的规定。
- 要求：
  - 新函数用参数显式传入 raw_dir、dest、manifest、status、bak_dir、diff_dir；
  - selftest 在开头断言所有路径 realpath 都以 /tmp/ 开头，并调用 enforce(modes=["selftest"])（设计 L219）；
  - 测试前后对真实成品、manifest、status 和备份目录清单各取一次 sha，必须完全不变，写进回执。

### P2

**P2-1 row group 布局与全量路径不一致**（设计 L105、L111、L289–291）
- 探针结果：一张 1,050,000 行的表 write_table 一次写成 [1048576, 1424] 两个 row group，再 write_table 一次 10 行又多出一个 row group。草图「≥ RG_ROWS 就写整个缓冲」会在每一年里产生零碎的 row group，和设计 L111「与现有布局一致」矛盾。
- 要求：缓冲达到 1,048,576 行时，只写前 1,048,576 行（concat_tables 后 slice，都是零拷贝），余下的留到下一批，年末再写剩余部分。
- 验收：row_groups_by_year 和每个 row group 的行数序列，和 ref_build 及现有成品的布局规则一致。2021–2025 每年 2 个，其余年份 1 个（设计 L49）。

**P2-2 年内唯一性按构造来证明，不要整年 group_by**（设计 L109–110、L292、L306）
- 草图 L292 `_assert_unique_keys_year(tmp_or_buffers, y)` 在缓冲已经写出之后，没法再检查。
- 按构造证明：
  - 文件名匹配 ^\d{8}$ 且互不相同；
  - 每个文件 trade_date 的 min=max=文件名日期（DB_INCR_DATE_MISMATCH）；
  - _one 的 L348 已经在文件内去重；
  - 这三条同时成立，年内 (ts_code, trade_date) 就一定唯一。
- 所以逐文件检查就够了，额外内存接近 0。
- 这和全量路径 L374 的静默去重是有意的不同（失败而不是去重），回执要写明。如果真触发了，要人工核原始文件。

**P2-3 原始文件选择会把 *.tmp.parquet 算进来**（代码 L291）
- `start <= p.stem <= end` 对 20261015.tmp.parquet（stem 是 "20261015.tmp"）在 end ≥ 20261016 时成立，会被当成原始文件读进来。目前 daily_basic 目录里没有这种文件（已列目录核过）。
- 增量版要求：严格匹配 ^\d{8}$；R 年份里出现任何 *.tmp.parquet 就失败（DB_INCR_RAW_TMP，退出码 27）。

**P2-4 raw_inventory 不能靠 mtime**（设计 L89–92）
- 恢复脚本如果用 shutil.copy2，会保留 mtime。同样大小的文件被替换后，(名称, size, mtime_ns) 完全不变，检测不到。
- 建议：每晚对旧年原始文件取内容 sha256。
  - 共 3107 个文件，约 1.4 GB，按 1 MiB 流式读；页缓存不计入 RSS。
  - digest 取排好序的 (文件名, size, sha256) 列表再做 sha256。
  - selftest 实测耗时；超过 60 秒再改成「mtime 快筛 + 每周 sha 全量」。

**P2-5 提交顺序要能从崩溃中恢复**（设计 L145、L148–150）
- 设计的顺序是：成品 os.replace，然后 manifest，然后 status。中间崩溃，manifest 就落后于成品；按 P1-7 的分析，status 掩盖不了这个问题，但会让排查变困难。
- 要求加一个 pending 日志：
  1. 写 tmp，fsync；
  2. 原子写 daily_basic_full_tushare_manifest.pending.json，内容 {prev_sha, new_sha, build…}，fsync 目录；
  3. 建备份（P2-9）；
  4. os.replace 成品，fsync 目录；
  5. os.replace(pending, manifest)；
  6. 写 status（L247–283 已经是原子写）。
- 启动时如果有 pending：
  - 成品 sha == pending.new_sha：补完第 5、6 步，报 P2；
  - 成品 sha == pending.prev_sha：pending 移到 _quarantine/，报 P2；
  - 两个都不等：失败，报 P1。

**P2-6 status 字段会被 eng_panels 覆盖**（代码 L247–283；eng_daily_panels L166–173）
- eng_panels 的 daily_core 会覆盖 tables.daily_basic 的 path、last_date、rows、sha256，只保留 history_diff_rows 和 backup_path（L170）。设计 L134 新增的 history_diff_by_year、history_diff_report 如果写进 status，下一步就会被抹掉。
- 建议：
  - 新字段只写进 manifest.build；
  - status 保持 L269–278 的原有键，最多加一个 manifest_path；
  - 如果一定要进 status，就得改 eng_daily_panels L170，并重钉驱动 L68，不建议。
- 另外提醒一个超出本设计范围的问题：daily_core 在 L151–152 把 1230 万行的 trade_date 整列读进来，还做 astype(str)。这一步本身也有内存风险。请 Eng 在合成数据上实测它的 VmHWM，结果另报。

**P2-7 manifest 的汇总字段必须覆盖拷贝的年份**（代码 L375–379、L401–405）
- rows、instruments、date_min、date_max 必须是全表的值。
- 其中 instruments 在现有代码里是所有年份 instrument_id 的并集（L376），现值 5917。拷贝时要从每个 row group 内存里的 instrument_id 取并集，不能只算 R 年份。
- 驱动 L1500 会检查 rows 不小于跑前，L1498 会检查 last_date==D。

**P2-8 history_diff 按月用 filters 读，会把单年的 row group 解码 24 次**（设计 L127；代码 L225–226）
- 每个 row group 装的是一整年，filters 只能按行过滤，没法在 row group 级别跳过。按月读的话，每个月两边各解码一次整年的 row group，一共 12×2 次，每次都是 P1-1 那种 400–500 MB 的瞬时高点。
- 改法：两边各用一次 iter_batches 顺序扫描，按 trade_date 的月份分桶，攒满一个月就调用 _compare_daily_basic_history 比一次。
- 判定口径保持不变：只比两边都有的 trade_date（L191–195），单边存在的行要计数（L197、L204），NaN 和 NaN 视为相等（L203）。
- 不要保留 L230–231 那种整表回退：filters 或扫描出错就直接失败。

**P2-9 备份用硬链接，轮转放到提交之后**（设计 L121–123；代码 L168–177、L309–314）
- data/ 和 backups/ 在同一文件系统上（st_dev=65040 已核），所以可以用 os.link(dest, bak) 代替 shutil.copy2：不拷贝 745 MB，os.replace 之后旧 inode 由备份持有。
- _prune 移到提交成功之后执行，并且不能删本次刚建的备份。
- 取证文件 daily_basic_full_tushare.20261014_1137_dupbug.parquet 匹配 L172 的 glob，会被正常轮转删掉。建议用单独的 .ok 把它移到不匹配 glob 的取证目录。这是写操作，要主 Agent 同意。

**P2-10 RSS 自检要同时判 VmHWM**（设计 L178–181、草图 L263）
- 两次检查之间出现的尖峰会被漏掉。检查点上如果 VmHWM > QL_DB_RSS_ABORT_KB，说明已经越过线了，也要失败（退出码 22）。

**P2-11 R 年份数量的上限，本质是时间和风险控制，不是内存控制**（设计 L91）
- R 里的年份是逐年顺序处理的，峰值不随年数增加。保留「超过 2 个旧年就失败」我同意，但理由要写准确。selftest 要实测 R={Y-1, Y, 两个旧年} 的耗时。

**P2-12 end 小于成品末日：拒绝**（设计 L158–161）
- 增量模式下，只要 end 小于上一版的 date_max 就失败（DB_INCR_END_BEFORE_PREV，退出码 26），不截断。回补另用工具，单独签 .ok。

**P2-13 nightly_update 的接入方式**（设计 L216；nightly_update.py L25、L32）
- 选「显式 mode="incremental"」，并通过 `sys.exit(...)` 把码表传出去，不要把增量设成默认。
- 全量路径加一道门：只有显式设置 QL_DB_ALLOW_FULL=1 才能跑，防止 nightly 误走全量。
- 这样 nightly_update.py 也要重钉（驱动 L61）。

### P3
- P3-1 1 月规则（设计 L82–84）：「当年第一个开市日」已经包含在「整个 1 月」里，删掉这条冗余，只留按 D[4:6]=="01" 判断。12 月的迟到修订如果 2 月以后才到，交给 P2-4 的内容 sha 来发现。
- P3-2 schema（设计 L113–118）：探针确认，pandas 3.0.6 下 `astype(str)` 得到 StringDtype，转出来是 large_string；`to_datetime` 加 18 小时 Timedelta 再 `tz_localize` 得到 timestamp[us] 和 timestamp[us, tz=Asia/Shanghai]；全空的数值列 `to_numeric` 后是 float64。要求：
  - cast 用 safe=True；
  - 遇到 dictionary（categorical）、string（不是 large_string）、ns 单位或 tz 不同，都直接失败；
  - schema 比较用 check_metadata=False；
  - 写盘的 schema 元数据取自上一版成品（探针确认：不带元数据的表可以写进带元数据的 writer）。pandas_version 会显示旧版本，可以接受。
- P3-3 Arrow 内存池：探针确认后端是 mimalloc，release_unused() 可以用。但只有 VmHWM 算数（设计 L177、L244）。
- P3-4 available_at、source、quality_status、promotion_approved（设计 L118）：增量和全量都按 L341–345 生成常量；拷贝的年份原样保留。对账时额外做不变量计数，见 4.4。
- P3-5 2.10（L151）去掉 parts 目录是对的。但 P1-7 提到的 10-19 可能残留的 _daily_basic_parts_* 目录，要在现场盘点里处理：移到隔离区，不删除。

---

## 二、内存：峰值在哪里，上限和实测怎么定

### 2.1 全量路径的 2.1 GB 可能出在哪里（推断，未分段实测）
1. 年度构建（L363–384）：chunk 列表和 L372 的 concat 结果同时存在；L374 的 drop_duplicates 又生成一份。pandas 3 的字符串列由 pyarrow 存储，不是 Python 对象，所以设计 L172 估的「每行 250–300 B」可能偏高。但 1.31M 行同时存在 2–3 份，仍然是数百 MB。
2. history_diff（L210、L225–226、L183–184、L189–190、L194–196）：
   - L210 先读 1230 万行的 trade_date 整列；
   - 每年新旧两边各读 17 列；
   - copy 一次，to_datetime 一次，isin 过滤又复制一次；
   - 最后 outer merge 出 30 多列，再加 indicator。
   - 2025 年那一轮最可能是峰值，Data 的推断我同意。
3. L230–231 的回退：如果 filters 出错，会把两份全表各 17 列整读，量级约 2×12.3M×约 145 B，大约 3.5 GB 以上，必然超线。增量版必须去掉这条回退（P2-8）；全量路径也建议改成直接失败（未决项 7）。

### 2.2 增量路径的阶段估算（按探针修正；仍需实测）

| 阶段 | 设计估算 | Arch 修正（探针或推理） | 控制手段 |
|---|---|---|---|
| 导入基线 | 未知 | 约 105 MB（探针，导入 pandas 后） | 无 |
| 旧年拷贝一个 row group | ≤150 MB | 整读 +400–500 MB；读两次约 +780 MB | 单驻留；pre_buffer=False；写后回读用 iter_batches，约 +140 MB |
| 当年缓冲 1,048,576 行 | 200–300 MB | 表 nbytes 约 225 MB，加上 writer 缓冲（探针 +25 MB）和单个文件的 pandas 中间结果 | 精确切片写出（P2-1） |
| history_diff | <100 MB | 按月用 filters 每次 +400–500 MB；顺序扫描约 +150–250 MB | 顺序扫描分桶（P2-8） |
| 写后回读校验 | 未设计 | 约 +140 MB | 一次只读一个 row group 的批次 |

整体预期：照 P1-1、P2-1、P2-8 实现的话，单进程峰值大约是基线加 0.5–0.65 GB，也就是约 0.6–0.75 GB。这是推断，以 selftest 实测为准。

### 2.3 上限（建议写进 v3 和 .ok 注释）
- 验收线：合成数据最坏情况（见 2.4 的 S2 和 S3）VmHWM ≤ 1,000,000 kB；外部 1 秒采样的树合计 ≤ 1,100,000 kB。
- 自检中止线：QL_DB_RSS_ABORT_KB=1,200,000，VmRSS 或 VmHWM 任一超过就中止（P2-10）。
- 驱动的外层保护不变：树合计 1,484,800 kB，单进程 1,536,000 kB（驱动 L85–86）。
- 真实运行首晚：VmHWM 超过 1,000,000 kB 报 P2，下一晚之前由 Arch 复核；超过 1,200,000 kB 自检中止，判 FAILED，不重试。

### 2.4 实测计划（只用 /tmp 合成数据；只需 selftest .ok 和回执）
- 生成器：
  - 在 /tmp/<out_dir>/raw/daily_basic/ 下按交易日生成 YYYYMMDD.parquet，2014-01-02 到 2026-10-16；
  - 每年行数对齐设计 1.2 节的表（2025 年 1,313,182 行），每天约 5,500 个代码；
  - 列名和类型抄现行原始文件的 schema。由 Data 只用 read_schema 读一个原始文件的元数据，把结果贴进生成器，不读数据行；
  - 每列约 5% NaN，含 -0.0；
  - 构造个别「文件内重复键」的日子，模拟 20231024；
  - 含一个空文件。
- 用合成数据先跑 ref_build，得到上一版成品，然后跑增量。
- 场景：
  - S1：普通日（D=10 月某日）；
  - S2：1 月首个开市日，R={Y-1, Y}，并把 Y-1 设成 1.31M 行的最大年；
  - S3：S2 再加 2 个旧年的原始文件被修改，R 一共 4 年；
  - S4：自检阈值调低到 300,000 kB，确认会回滚，且 tmp 被删；
  - S5：运行中向进程发 SIGTERM，确认会回滚（P1-5）；
  - S6：残留 tmp；
  - S7：原始目录里有 *.tmp.parquet；
  - S8：日期不符或重复键；
  - S9：上一版成品有一个 row group 跨两年；
  - S10：transform_sha 不同；
  - S11：end 早于成品末日；
  - S12：pending 日志的三个分支；
  - S13：manifest 写失败（退出码 30）。
- 采样：
  - 进程内 PHASE 行；
  - 外部采样器每秒读 /proc/<pid>/status 的 VmRSS，按树合计，用 nice -n 10 跑，和驱动一致；
  - 用 /usr/bin/time -v 取 Maximum resident set size，先用 `command -v` 确认它存在。
- 校准（只看量级）：在 /tmp 拷一份旧模块，只改 ROOT 指向 /tmp，不在仓库里打补丁，也不用 git apply。分两个独立进程跑：
  - 一个只做 2025 年那么大的单年构建（L363–384 那一段）；
  - 一个只做 2025 年那么大的单年 _compare_daily_basic_files。
  - 外部看门狗到 1,450,000 kB 就按精确 PID 发 TERM。
  - 目的是确认合成数据能复现 GB 级的高点，从而说明合成数据有代表性。不要求，也不允许整段全量跑完。
- 回执要写：
  - 每个场景的 VmHWM、树最大值、耗时；
  - 生成器的 sha；
  - 真实成品、manifest、status 前后的 sha 必须不变（P1-8）。

---

## 三、对账方法（对设计 4.2 的修订）
1. 基准用 P1-4 的 ref_build，不用现成品，也不跑全量。
2. 逐年比两样：行数，以及 row group 的行数序列（P2-1）。
3. 内容 hash：每年每列一个 sha256。
   - 喂数据之前，先喂一个列头：列名、Arrow 类型字符串、该年行数。
   - 行序：先按 (trade_date, ts_code) 排序（排序键唯一，见 P2-2）。
   - 各类型的规范化：
     - double：1 字节有效位（null 和任何 NaN 载荷都记 0，0 后面跟 8 个 0x00），否则记 1，再加 8 字节小端 IEEE-754 值；-0.0 用 `np.where(v == 0, 0.0, v)` 规范成 +0.0。只喂原始字节，绝不经过文本格式化（不用 repr、str 或 format）。
     - timestamp：断言单位是 us，tz 是 Asia/Shanghai 或无 tz（和 schema 一致）；喂 1 字节有效位，再加 int64 小端值。
     - large_string：1 字节有效位，加 8 字节小端长度（和 large_string 的 64 位偏移一致），再加原始 UTF-8 字节。不做 Unicode 规范化，因为字节必须完全一致。另外断言 ts_code 和 instrument_id 只含 ASCII。
     - bool：1 字节有效位，加 1 字节值。
   - 每批 ≤65,536 行，用 pyarrow.compute 加 numpy 视图来算，不逐行循环。
4. 物理行序 hash：再按文件里的物理顺序算一次全行 hash（规范化同上）。设计 L117 声称「行序与全量一致」，上线前这一项也必须相等；不等就判不通过。
5. 严格表示检查：每列每年分别统计 null 个数和 NaN 个数，两边都要相等。内容 hash 把 null 和 NaN 视为同一个值，这一步用来补上这个口径差别。
6. 不变量计数，每年都必须是 0：
   - available_at − trade_date ≠ 18 小时的行数；
   - source ≠ "tushare.daily_basic" 的行数；
   - quality_status ≠ "research" 的行数；
   - promotion_approved ≠ False 的行数；
   - row group 的 trade_date 统计跨年的个数。
7. schema 一致（check_metadata=False），pandas 元数据里各列的 dtype 字符串也要一致。
8. 文件 sha 只记录，不作为一致标准（设计 L204），同意。
9. 发现不一致时，按月定位，每类最多给 100 个样例键（同设计 L130）。

---

## 四、接入与治理
1. 驱动：f99dd11a 已冻结，不改。另出新版驱动，用新文件名，例如 run_nightly_v2.py。新版里要更新的钉值：
   - L66 sha_tier1_materialize（必改）；
   - L61 sha_nightly_update（P2-13，必改）；
   - L68 sha_eng_daily_panels（只有采纳 P2-6 的「进 status」方案时才改，不建议）；
   - 冻结清单和 sha 范围文件（L48–49）也要同步更新。
   - 新驱动、新范围文件和新的 .ok 都由 Arch 审查签发。.ok 增加注释行，写明增量模式、自检阈值和首晚 VmHWM 的处置。
2. 回执：新驱动从 logs/nightly/<D>_daily_basic.log 里解析唯一一行 `DB_INCR_RESULT {json}`，这一行由增量函数在结束前打印，失败时也要打印。回执里写入：
   - mode、rebuilt_years、copied_years；
   - prev_sha256、new_sha256、transform_sha；
   - rows、rows_by_year；
   - peak_vmhwm_kb、phase_rss_kb；
   - history_diff_rows、history_diff_by_year；
   - raw_inventory_changed_years；
   - backup_path、exit_code、reason_code。
   - 再加上驱动自己统计的这一步的 rss_max_one 和 rss_max_sum。
   - 没解析到这一行，就按 FAILED 处理。
3. 失败的含义：
   - 任何非 0 退出码，nightly_update L120 都记 `fail rc=N`，驱动 L595–598 判 FAILED，不重试，不写 DONE；
   - 成品、manifest 和旧备份都不动；
   - 纸面轨被门禁拦住，算正常的安全结果，报 P2；
   - 只有退出码 30（成品已替换、提交没完成）和「pending 分支里两个 sha 都不等」报 P1。
4. history_diff_rows 怎么写进 status（L247–260、L269–278）：
   - 含义不变：本次比较中差异行的总数（只比两边都有的日期，单边行计入）；
   - 现在由增量版在提交阶段写入；
   - eng_panels L170 会保留这个值；
   - 「拷贝年份的差异」不计入，因为它们由写后回读保证一致；不一致时直接失败，不进入计数。
5. 启用顺序：
   1. Data 交 v3；Arch 复核；
   2. Eng 在 10-19 18:40 之后实现，附代码 diff；
   3. selftest .ok 和回执；
   4. 10-19 现场盘点；
   5. 引导基线 .ok，同时做影子分年对账（真实数据，只读，输出 /tmp，空档运行，单独签 .ok）；
   6. 新驱动和 10-20 的 .ok。
   - 任何一步没在 10-20 05:00 ET 前完成，10-20 就用旧路径。

---

## 五、设计里 9 个未决项的建议（设计 L237–245）
1. 估算没有实测：同意以实测为准。估算本身按 2.2 表修正；验收线 1,000,000 kB，自检线 1,200,000 kB（2.3 节）。
2. 驱动钉 sha：新版驱动加新的 .ok，内容见第四节第 1 条；同时重钉 nightly_update（P2-13）。f99dd11a 不改。
3. mtime 被恢复脚本改写：每晚改用原始文件内容 sha（P2-4），首晚和每次恢复后都重新定基线（P1-7）。每周日空档做一次全年份的 ref_build 对账，单独签 .ok。
4. 当年历史差异的上报阈值，所有差异都只记录、不挡 DONE：
   - 早于 D 之前第 5 个开市日的日期上，出现差异行或单边行：报 P2；
   - 单晚差异行超过 10,000：报 P1，请 Data 查原因；
   - 旧年因为原始文件变化而被加进 R 时：报 P2，附变化的文件名；
   - 拷贝年份的写后回读不一致：失败，退出码 23。
5. end 小于成品末日：拒绝（P2-12）。
6. 1 月的内存门槛：不另设。R 年份顺序处理，峰值和 R 的大小无关，以 S2、S3 场景实测 ≤1,000,000 kB 为前提。05:30 前 MemAvailable ≥2,621,440 kB×3 的门槛照旧。
7. 全量路径的已知问题：在同一次改动里只做三件事：
   - L230–231 的回退改成直接失败；
   - L416 改成 tmp 加 os.replace；
   - 加上 QL_DB_ALLOW_FULL=1 这道门（P2-13）。
   - 全量路径其他地方不动。
8. Arrow 内存池：后端是 mimalloc，release_unused 可用（探针）。只以 VmHWM 为准，阶段结束后调用一次 release_unused 并记录读数。
9. 10-19 仍是旧代码：同意 v2 的写法。另外加上 P1-7 的现场盘点和引导步骤，作为 10-20 启用的第三个前置条件。

---

## 六、Eng 动手前必须完成的修改（写进设计 v3）
- R1：拷贝阶段单驻留；写后回读校验；去掉 L280 的自比（P1-1、P1-2）。
- R2：manifest.build.transform_sha，以及 DB_INCR_TRANSFORM_CHANGED（P1-3）。
- R3：ref_build 分月参考重建器的规格，以及它的等价性论证（P1-4）。
- R4：SIGTERM 和 SIGHUP 转成异常，按 inode 回滚（P1-5）。
- R5：退出码表，不用 2 和 3；nightly_update L32 改成 sys.exit 形式（P1-6、P2-13）。
- R6：10-19 现场盘点、引导基线文件；前置检查改为对 manifest.build（P1-7）。
- R7：路径参数化；selftest 的 /tmp 断言；真实文件前后 sha 不变（P1-8）。
- R8：按 1,048,576 行精确切分 row group；逐文件证明唯一性；严格匹配原始文件名（P2-1、P2-2、P2-3）。
- R9：用内容 sha 做 raw_inventory；pending 日志和 fsync；硬链接备份，提交后再轮转（P2-4、P2-5、P2-9）。
- R10：新字段只写进 manifest；补全全表汇总字段（P2-6、P2-7）。
- R11：history_diff 改为顺序扫描、按月分桶，并去掉整表回退（P2-8）。
- R12：自检同时判 VmHWM；end 早于成品末日就拒绝（P2-10、P2-12）。
- R13：对账按第三节规格实现。

## 七、验收测试清单
- A1：设计 v3 和代码 diff 都经 Arch 审过；改动之前的 tier1_materialize.py 和 nightly_update.py 已按设计 L213 归档并附 sha。
- A2：selftest .ok（scope=selftest，allow_real_data=false，out_dir 在 /tmp 下）；S1–S13 全部通过；回执带生成器的 sha。
- A3：S2 和 S3 的 VmHWM ≤ 1,000,000 kB，外部树合计 ≤ 1,100,000 kB；S1 的耗时有记录。
- A4：合成数据上，增量和 ref_build 按第三节逐年完全一致：行数、row group 序列、22 列内容 hash、物理行序 hash、null 和 NaN 计数、不变量为 0、schema 和 pandas 元数据 dtype。
- A5：S4 和 S5 结束后，tmp 已删除，成品、manifest、status 和备份都不变；退出码分别是 22 和 -15（或驱动记录的 TERM）。
- A6：S6–S11、S13 的退出码和码表完全一致；没有任何场景返回 2 或 3。
- A7：真实成品、manifest、status、backups 清单在 selftest 前后 sha 都不变（P1-8）。
- A8：10-19 现场盘点的回执已交，所有残留都已隔离处理（移动，不删除，单独签 .ok）。
- A9：引导基线和影子对账：现行原始文件经 ref_build 得到的 2014–2026 每一年，都和现成品逐年一致；或者把差异列出来，交 Arch 和主 Agent 定。影子增量（上一版用基线成品，end 取最近开市日，输出 /tmp）和 ref_build 一致；VmHWM ≤ 1,000,000 kB。
- A10：新版驱动的钉值和范围文件都更新；`--check-only` 退出码为 10；10-20 的 .ok 由 Arch 签发，带增量注释行。
- A11：10-20 首晚回执带 DB_INCR_RESULT 的全部字段；VmHWM 和 history_diff_by_year 已披露；任何失败都按第四节第 3 条处理。

（完）

---

## 复审（v3）

- 复审对象：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_ZH.md，sha256 13fd86b67ba6c8d074aba08d8a3ad3cac93fd7ebbae9acbe41547e80c15d0aab，336 行（已核）。本节「v3 Lxx」都指这个文件的行号；「本审 Px」指本文前面第一节的发现。复审前本文 sha 是 9ef7f89581120a0af9bd43406eee7a7554a13fef834afc4138e0d885b8b402b3。
- 只做了静态只读复核，没有读真实数据行，没有运行代码，这一轮也没有跑探针。只读核对过的是：
  - 驱动 run_nightly_v1.py 的 L88 TERM_WAIT_S=10；
  - L330–353 的 stop_tree 顺序：先 SIGSTOP，再 TERM 加 CONT，等 10 秒，还在就 KILL；
  - sha 范围文件 nightly_sha_scope_20261019.txt 里不含 backups/。
- 写于 2026-10-18T17:02:25-04:00（取自 date）。

### 复审结论：PASS_WITH_CONDITIONS，Eng 可以在 10-19 18:40 ET 之后开工

- 8 条 P1 里：
  - 5 条已关闭：P1-1、P1-2、P1-4、P1-6、P1-8。其中 P1-6 还差 SIGHUP 的码号，要随 C2 补上。
  - 3 条部分关闭：P1-3、P1-5、P1-7。
  - 没有仍然打开的 P1。
- 剩下的都是文字级的修改，见下面 C1–C12。开工条件有两个：
  1. Data 在 10-19 18:40 ET 前交 v3.1，把 C1–C12 写进去，Arch 确认。
  2. Eng 交代码 diff 时，逐条对应 C1–C12。
- 10-20 能否启用的条件不变（v3 L264、L280）：新版驱动、selftest、盘点、基线、10-20 的 .ok，到 10-20 05:00 ET 缺任何一项，10-20 那晚就走旧的全量路径，内存超限停树记 P2。

### 一、R1–R13 逐条复核

| 条目 | 状态 | v3 位置 | 说明 |
|---|---|---|---|
| R1 | 已关闭 | L88–92、L110–116、L183–199 | 拷贝时单驻留，hash 在内存里的 t 上切片算，写后用 iter_batches 回读。内存以 S2、S3 实测为准。 |
| R2 | 部分关闭 | L104–108 | 规范化算法改按 Arch 决定 (c)：AST 加去掉 docstring。还要补上库版本和 _one 外提的等价性验证（C3、C4）。 |
| R3 | 已关闭 | L203–211 | 规格和等价性论证都写对了。ref_build 自己的内存验收补进 A13（C9）。 |
| R4 | 部分关闭 | L143–147、L286–324 | SIGHUP 不能用 -1（C2）；回滚过程中要屏蔽信号（C5）；tmp 先用 O_EXCL 创建再记 inode（C6）；TERM 到退出要在 10 秒内（C7）。 |
| R5 | 部分关闭 | L157–178、L69–73 | 接受 31。还要按 C2 给 SIGHUP 加一个专用码号。 |
| R6 | 部分关闭 | L233–253 | 写进 Arch 决定 (e)：新表配过时 manifest 时两边都不信，用 ref_build 重新定基线（C8）。 |
| R7 | 已关闭 | L69–73、L266–272 | 无 |
| R8 | 部分关闭 | L81–97 | L82 的正则写错了（Arch 决定 (g)，C1）。 |
| R9 | 部分关闭 | L75–79、L125–136 | 原始文件按 Arch 决定 (d) 处理，快筛要加 ctime（C10）；启动时 pending 恢复的顺序要写明（C11）；硬链接备份在提交中途失败时的处理（C12）。 |
| R10 | 已关闭 | L138–141 | 无 |
| R11 | 已关闭 | L118–123 | 附带 P3：L185–188 的重复键 ValueError 要映射成退出码 24，否则会落到 1（D3）。 |
| R12 | 已关闭 | L149–151、L197 | 无 |
| R13 | 已关闭 | L213–227 | 附带 P3：基线里的「每年列 hash」要写明就是 4.2 节排序后的内容 hash（D4）。 |

### 二、8 条 P1 逐条复核

| P1 | 状态 | v3 位置 | 说明 |
|---|---|---|---|
| P1-1 内存双驻留 | 已关闭 | L88–92、L183–199 | 设计上解决了；是否达标以 A3 实测为准。 |
| P1-2 自己比自己 | 已关闭 | L110–116 | 无 |
| P1-3 变换版本 | 部分关闭 | L104–108 | 见 C3、C4。 |
| P1-4 对账基准 | 已关闭 | L203–211 | ref_build 的内存验收见 C9。 |
| P1-5 TERM 回滚 | 部分关闭 | L143–147 | 见 C2、C5、C6、C7。 |
| P1-6 退出码 | 已关闭（差 SIGHUP 码号） | L157–178 | SIGHUP 码号随 C2 补。 |
| P1-7 10-19 遗留和引导 | 部分关闭 | L233–253、L281 | 见 C8。 |
| P1-8 隔离 | 已关闭 | L69–73、L266–272 | 无 |

### 三、Arch 对 v3 未决项（L274–281）的决定
- (a) 第 4 项，取证备份：20261014_1137_dupbug 和 20261014_1136 两份备份，用 os.link 硬链接到 backups/valuation_pinned/。这个目录不在代码 L172 的 glob 里，也不在 sha 范围文件里（已核）。要单独签 .ok，并等主 Agent 批准。**不用** QL_DAILY_BASIC_NO_PRUNE。
  - 时间提醒：10-19 旧代码在 call B 的 daily_basic 步走到 L311–313 时，会按 keep=5 删掉 20261014_1136（v3 L236、L278）。所以要保住 1136，链接必须在 10-19 call B 起跑之前做完（Arch 锁 05:25，驱动 05:30）。错过的话，只能保住 dupbug（10-20 如果仍走旧路径，才会删到它）。
- (b) 第 2 项，退出码：接受 31（DB_INCR_PENDING_CONFLICT）。SIGHUP 不用 -1：handler 把它转成异常，回滚之后用专用退出码退出，并写进码表。
  - 码号冲突：Arch 原定用 30，但 v3 L173 已经把 30 给了 DB_INCR_COMMIT_PARTIAL，一个码不能有两个含义。本复审暂定 SIGHUP 用 32（DB_INCR_SIGNAL_HUP），请 Arch 确认。如果坚持用 30，COMMIT_PARTIAL 就要改号，两张码表（v3 L160–176 和本文 P1-6）一起改。
- (c) 第 1 项：transform_sha = sha256(规范化 AST dump)。范围是去掉 docstring 之后的变换函数，加上常量表。具体实现由 Eng 提出，Arch 审定。见 C3。
- (d) 第 3 项：原始文件内容 sha 先实测耗时。
  - 不超过 60 秒：每晚做内容 sha。
  - 超过 60 秒：每晚做 size、mtime、inode 快筛（按 C10 再加 ctime），每周做一次全量内容 sha。
  - 只要当晚之前发生过原始文件的恢复、拷贝或回补，那一晚必须做全量内容 sha。
- (e) 第 7 项：盘点出来的残留用单独的 .ok 隔离，只移动，不删除。遇到「新表配过时 manifest」时，表和 manifest 都不信，必须先用 ref_build 重新定基线，之后才允许启用增量。见 C8。
- (f) 第 5 项：Eng 在合成数据上实测 eng_daily_panels L151–152 整列读 trade_date 并转成字符串的内存，作为验收项 A12。
- (g) L82 的正则写错了，下一版修正。见 C1。

### 四、剩余必须修改的项（写进 v3.1）
- C1（P2）：v3 L82 的 `^\d{8}$\.parquet` 改成「完整文件名匹配 `^\d{8}\.parquet$`」，或者写成「stem 匹配 `^\d{8}$`，且后缀正好是 .parquet」。
- C2（P1-5、P1-6）：SIGHUP 按 Arch 决定 (b) 处理。码表 L160–176 删掉 -1 那一行，加上 SIGHUP 的专用码（暂定 32，见三 (b)）。草图 L319–320 对 SIGHUP 不再给自己重发信号，直接返回这个码。SIGTERM 维持回滚后重发信号、退出码 -15。
- C3（P1-3）：v3 L105 的「inspect.getsource 去掉行尾空白」改成 Arch 决定 (c)。指纹里还要加上运行时版本（python、pandas、pyarrow、numpy 的版本字符串），写进 manifest.build。版本变了，同样退出 28，要单独签 .ok 才能放行。理由：to_datetime 的时间单位、to_numeric 的行为会随版本变化，cast(safe=True) 不一定拦得住。
- C4（P1-3）：现在的 _one 是 materialize_daily_basic 里面的闭包（代码 L316），增量和 ref_build 都要先把它外提成模块级函数。验收增加一项：在 /tmp 合成文件上，外提后的 _one 和旧闭包（在 /tmp 拷一份旧模块，不在仓库里打补丁）对每个文件的输出，22 列 hash 完全相等。否则外提时引入的变化会同时出现在增量和 ref_build 两边，对账查不出来。
- C5（P1-5）：草图 L312 一进入 except，就先把 SIGTERM 和 SIGHUP 设成 SIG_IGN，清理完再按 C2 退出。否则驱动第二次发 TERM 会打断回滚，tmp 留下来。
- C6（P1-5）：tmp 先用 os.open(O_CREAT|O_EXCL) 创建并立刻记下 (st_dev, st_ino)，再把文件对象交给 ParquetWriter。这样既消除了 L298 检查和 L301 创建之间的竞态，也消除了「已创建但还没记 inode」的窗口。
- C7（P1-5，新问题）：驱动 stop_tree 发 TERM 之后只等 10 秒（L88、L345–348）就 KILL。而 Python 的 handler 要等 pyarrow 的 C 调用返回才会运行，写出一个 1,048,576 行的 row group 可能要几秒。S5 要在拷贝、构建、回读、diff、提交五个阶段各随机发一次 TERM，从 TERM 到进程退出必须 ≤5 秒，回执写实测值。
- C8（P1-7）：v3 L246 的「或已由 Arch 裁定」改写成 Arch 决定 (e)：新表配过时 manifest 时，两边都不信。过时的 manifest 不能作为任何前置依据；基线只能由 5.3 的 ref_build 全年份对账产生，对账不一致就不写基线，不启用增量。另外：
  - v3 L240「不需要 .ok」的只读盘点也必须在 10-19 18:40 之后做，并且当时没有其他真实数据进程在跑；
  - 命令清单先交 Arch 看；
  - 只做 read_metadata、stat 和 sha256 的文件读取，不读数据行。
- C9（P1-4）：ref_build 也要过内存验收：合成数据上最大的一年（1,313,182 行）VmHWM ≤ 1,000,000 kB，作为 A13。影子对账和每周复核都按这个线执行。
- C10（P2-4，新问题）：快筛只看 size、mtime、inode 不够。shutil.copy2 写到已有路径上时，inode 不变，mtime 被复制，大小也可能相同，三项全部不变。快筛必须加上 st_ctime_ns：任何写入都会更新 ctime，用户态也改不回去。另外，恢复、拷贝、回补工具要在原始目录外写一个 raw_touched 标记，或者在当晚的 .ok 里写 raw_full_sha_required=true。有了这个标记，当晚强制做全量内容 sha。
- C11（P2-5）：启动顺序写明为：pending 恢复（L134 的三个分支），然后 STALE_TMP 检查，然后前置检查（L299）。草图里漏了 pending 恢复。如果先做前置检查，「成品已换、manifest 未换」的情况会被误判成退出 20，而不是按 pending 补完。另外，失败回滚时，如果成品没变（sha 等于 prev_sha），由本次运行自己把 pending 移到 _quarantine/，不留给下一晚。
- C12（P2-9，新问题）：v3 L129 的硬链接备份，在第 3 步之后、第 4 步之前失败时，会和现役成品共用同一个 inode。之后如果有任何工具对成品做原地写（比如恢复脚本用 copy2 写到已有路径），备份会被一起改坏。要求：
  - 这种情况下，回滚时删掉本次新建的链接，并核对它的 inode 和成品相同；
  - 文档写明：成品只能用 os.replace 替换，任何工具都不许原地写；
  - 备份文件名精确到秒（%Y%m%d_%H%M%S），避免同一分钟内两次运行时 os.link 撞名失败。

### 五、P3（建议，不挡开工）
- D1：v3 L240 的盘点回执写进 docs/v2/audit/ 时，按「中文文档不用 heredoc」的规定，用 python 显式 UTF-8 和 LF 写。
- D2：手动维护的「v3 Lxx」行号容易漂移，v3.1 改完后要整体复核一遍对照表 L12–41 的行号。
- D3：_compare_daily_basic_history 在 L185–188 抛的重复键 ValueError，要映射成退出码 24（DB_INCR_DUPKEY）。
- D4：基线 L248 里的「每年列 hash」要写明就是 4.2 节排序后的内容 hash。写后回读用的是每个 row group 按物理顺序算的 hash，两者分别命名，不要混用。

### 六、验收清单增补（在本文第七节 A1–A11 之后）
- A12：在合成数据上实测 eng_daily_panels L151–152 的 VmHWM（Arch 决定 (f)），回执写实测值。超过 1,000,000 kB 报 P2，并另出改法。
- A13：ref_build 最大年的 VmHWM ≤ 1,000,000 kB（C9）。
- A14：外提后的 _one 和旧闭包在合成文件上逐文件一致（C4）。
- A15：S5 里五个阶段从 TERM 到退出都 ≤5 秒，且回滚完整：tmp 已删除，本次新建的链接已撤回或从未建立，pending 已处理（C5、C6、C7、C11、C12）。
- A16：SIGHUP 场景退出码等于 C2 定的码，不是 -1，也不是 2 或 3。
- A17：在合成环境里用 copy2 把一个旧年原始文件覆盖成同样大小、同样 mtime 的不同内容，快筛（含 ctime）能发现，并把该年加进 R（C10）。
- A18：「新表配过时 manifest」场景：不写基线，增量拒绝启动，退出 20，直到 ref_build 重新定基线（C8）。

（复审完）
