# daily_basic 增量重建设计 v3（只写文档，不改代码；Data 起草，交 Arch 复核、Eng 实现）

- 作者：QuantLab Data；写于 2026-10-18T16:56:13-0400（取自 date）。
- 源：设计 v2 docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v2_ZH.md（e6372b9b0e67992a1ab1e77fcb038874e0f5ced85be37149fe6a84f88b74c08e，本身未动）。
- 主依据：Arch 审查 docs/v2/ARCH_DAILY_BASIC_INCREMENTAL_REVIEW_ZH.md（9ef7f89581120a0af9bd43406eee7a7554a13fef834afc4138e0d885b8b402b3，420 行，写于 2026-10-18T16:46:41-04:00），以及 Arch 10-18 16:50 ET 的 8 条 P1 指令。下文「审查 Lxx」指该文件行号，「代码 Lxx」指 scripts/acquire/tier1_materialize.py（e9c89a6c…）行号。
- 本文只读了代码、日志、审查文档和成品元数据。没有读真实数据行，没有运行项目代码，也没有跑合成数据。凡是内存数字都引自 Arch 审查里的「探针」（合成数据，只能判断量级，不能当验收依据，见审查 L15）；本文自己不再给估算数字。
- 本文是整篇重写，取代 v2。v2 的第 6 节代码草图作废（其中 L280 读两次 row group、L292 写出后再整年判唯一，均被审查判为不可行）。
- live=false，promotion_approved=false；不涉及 8787 和 moneyflow。

## R1–R13 逐条对照表

| 条目 | 审查要求（审查 L393–405） | 改在 v3 哪里 | 怎么改的 | 是否完全解决 |
|---|---|---|---|---|
| R1 | 拷贝阶段单驻留；写后回读；去掉 L280 自比（P1-1、P1-2） | §2.4（L88–L92）；§2.8（L110–L116）；§3.（L183–L199）；§8.（L283–L326） | 任何时刻内存里只有一个 row group；hash 在内存里的 t 上按 ≤65,536 行切片算，不再读第二次；w.close() 后用 iter_batches 回读 tmp 比 hash 与行数；内存一节按探针数字重写 | 设计层面已解决；内存是否达标以 selftest S2/S3 实测为准 |
| R2 | manifest.build.transform_sha 与 DB_INCR_TRANSFORM_CHANGED（P1-3） | §2.7（L104–L108）；§2.15（L157–L178） | 对 _one 及依赖的规范化源码取 sha256，与上一版不等即退出 28；引 10-14 的 1919 / 271 例子；变换改了要单独 .ok 用 ref_build 全年份重建再定基线 | 已解决；规范化算法由 Eng 定，需 Arch 审 |
| R3 | ref_build 分月参考重建器规格与等价性论证（P1-4） | §4.1（L203–L211） | 每次一个自然月、每进程一年；只输出逐年 hash；写明等价性论证；写明现成品（10-18 00:21）早于 01:1x 原始文件恢复，不能当基准，也不跑新全量 | 已解决 |
| R4 | SIGTERM / SIGHUP 转异常，按 inode 回滚（P1-5） | §2.12（L143–L147） | 入口装 handler 转异常；只删 (st_dev, st_ino) 与创建时相同的 tmp；回滚后恢复默认处理并重发信号，使退出码保持 -15 / -1；SIGKILL 残留按 STALE_TMP 处理 | 已解决；SIGHUP 的退出码 -1 是否进码表请 Arch 定 |
| R5 | 退出码表，不用 2 和 3；nightly_update L32 改 sys.exit 形式（P1-6、P2-13） | §2.15（L157–L178）；§2.1（L69–L73） | 新增码全部 ≥20；引 nightly_update L119–120；L32 改为 sys.exit(m.materialize_daily_basic_cli(...))，显式 mode=incremental，全量要 QL_DB_ALLOW_FULL=1 | 已解决；新增 31（pending 冲突）待 Arch 认可 |
| R6 | 10-19 现场盘点、引导基线文件、前置检查对 manifest.build（P1-7） | §5.（L233–L253） | 18:40 后只读盘点 tmp、_daily_basic_parts_*、新表配旧 manifest 等；引导步骤单独 .ok 写 build_baseline.json；前置检查改对 manifest.build.new_sha256（首晚对基线），不再对 eng_daily_panels 重算的 status sha | 已解决；盘点后残留的隔离（移动）需单独 .ok |
| R7 | 路径参数化；selftest 的 /tmp 断言；真文件前后 sha 不变（P1-8） | §2.1（L69–L73）；§6.2（L266–L272） | raw_dir、dest、manifest、status、bak_dir、diff_dir 全部传参；selftest 断言 realpath 都在 /tmp/ 下；前后记录真实成品、manifest、status、备份清单的 sha | 已解决 |
| R8 | 精确 1,048,576 行切 row group；逐文件证唯一；原始文件名严格匹配（P2-1、P2-2、P2-3） | §2.3（L81–L86）；§2.5（L94–L97） | 缓冲 concat 后 slice 出恰好 1,048,576 行写出，余数留下批；文件名 ^\d{8}$、互不相同、trade_date min=max=文件名、文件内 L348 去重，三条合起来证明年内唯一；R 年出现 *.tmp.parquet 即退出 27 | 已解决 |
| R9 | 内容 sha 版 raw_inventory；pending 日志与 fsync；硬链接备份、提交后轮转（P2-4、P2-5、P2-9） | §2.2（L75–L79）；§2.10（L125–L136） | 原始文件按内容 sha256 判变化，不看 mtime；提交前写 pending 并 fsync，启动时按三分支恢复；备份用 os.link，提交成功后才 prune，且不删本次备份 | 已解决；每晚全量读 1.4 GB 的耗时待 selftest 实测，超 60 秒再议 |
| R10 | 新字段只写进 manifest；全表汇总字段覆盖拷贝年（P2-6、P2-7） | §2.11（L138–L141） | status 只保留代码 L269–278 原有键加 manifest_path；rows、instruments、date_min、date_max 按全表算，instruments 在拷贝时从每个 row group 取并集 | 已解决 |
| R11 | history_diff 顺序扫描、按月分桶，去掉整表回退（P2-8） | §2.9（L118–L123） | 两边各一次 iter_batches 顺序扫描，按月攒满再比；判定口径同代码 L191–204；任何读错直接失败，不保留代码 L230–231 的整表回退 | 已解决 |
| R12 | 自检同时判 VmHWM；end 早于成品末日即拒绝（P2-10、P2-12） | §3.（L183–L199）；§2.13（L149–L151） | 每个检查点 VmRSS 或 VmHWM 任一 > 1,200,000 kB 即退出 22；end < 上一版 date_max 即退出 26，不截断 | 已解决 |
| R13 | 对账按审查第三节规格实现 | §4.2（L213–L227） | 逐年行数、row group 行数序列、22 列内容 hash、物理行序 hash、null / NaN 计数、不变量计数、schema 与 pandas dtype；规范化按审查 L313–318 | 已解决 |

## Arch 10-18 16:50 ET 的 8 条 P1 落实索引

| P1 | 要求 | v3 位置 |
|---|---|---|
| (1) | 单驻留、写后回读、去掉 v2 L280 读两次；内存按实测重写（整读 +400–500 MB，读两次 837,292–862,320 kB） | §2.4（L88–L92）；§2.8（L110–L116）；§3.（L183–L199） |
| (2) | 删掉 2.8 的自比，换成写后回读、raw 内容 hash、每周分年对账 | §2.8（L110–L116）；§2.2（L75–L79）；§4.3（L229–L231） |
| (3) | manifest 记 transform_sha，变了退出 28；引 1919 / 271 | §2.7（L104–L108） |
| (4) | ref_build 分月、每进程一年；等价性论证；现表 00:21 早于 01:1x 恢复 | §4.1（L203–L211） |
| (5) | TERM 转异常；只按 inode 删本次 tmp | §2.12（L143–L147） |
| (6) | 退出码从 20 起，不用 2、3；引 nightly_update L119–120；完整码表 | §2.15（L157–L178） |
| (7) | 10-19 遗留与 10-20 首晚预案；单独 .ok 建基准；前置检查对 manifest | §5.（L233–L253） |
| (8) | 路径传参；自测断言 /tmp；真文件前后 hash | §2.1（L69–L73）；§6.2（L266–L272） |

P2 落实索引：精确切片 §2.5（L94–L97）；逐文件证唯一 §2.3（L81–L86）；文件名 ^\d{8}$ §2.3（L81–L86）；内容 hash 判 raw 变化 §2.2（L75–L79）；pending 与 fsync §2.10（L125–L136）；硬链接备份、提交后修剪 §2.10（L125–L136）；VmHWM 超限中止 §3.（L183–L199）；拒绝 end 早于末日 §2.13（L149–L151）；显式 mode=incremental §2.1（L69–L73）；去掉 L230–231 整表回退 §2.9（L118–L123）；全表统计含拷贝年 §2.11（L138–L141）；status 字段被 eng_panels 覆盖（P2-6）§2.11（L138–L141）；R 年数上限的理由（P2-11）§2.2（L75–L79）；P3-1 至 P3-5 分别见 §2.2（L75–L79）、§2.6（L99–L102）、§3.（L183–L199）、§4.2（L213–L227）、§5.（L233–L253）。

---

## 1. 现状（与 v2 第 1 节相同的事实只摘要，新增事实标「新」）

### 1.1 代码位置
- scripts/acquire/tier1_materialize.py，sha256 e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb，650 行。materialize_daily_basic 在代码 L285–419：L291 选原始文件；L309–314 copy2 备份并 keep=5 轮转（L168–177）；L316–349 _one；L356–384 按年分批；L388–393 ParquetWriter 逐分片写 tmp 再 os.replace；L396–399 history_diff；L401–416 manifest（L416 非原子）；L417 写 status（L247–283，原子）。
- 新：代码 L291 的 `start <= p.stem <= end` 会把 20261015.tmp.parquet（stem 为 "20261015.tmp"）算进来（审查 P2-3）。Arch 已列目录核过，目前 daily_basic 原始目录里没有这种文件。
- 新：scripts/nightly_update.py（ec079d56…）L25 用 `python3 -c "import tier1_materialize as m; ..."` 起子进程，L32 调 `m.materialize_daily_basic(end=ymd)`。L118 取子进程 rc；L119 `if rc not in (0,2): break`；L120 `st="ok" if rc in (0,2) else ("partial" if rc==3 else f"fail rc={rc}")`。也就是说 rc=2 记成功，rc=3 记 partial，其他非 0 记 fail。L113 的 wait_mem 只在 MemAvailable < 2 GB 时暂停（L20–21）。
- 新：scripts/acquire/eng_daily_panels.py 的 daily_core（L144–153）对 daily_basic 成品读整列 trade_date（L151），并用 sha(f) 重算成品 sha、rows、last_date 写进 status（L152）；L166–173 只保留 history_diff_rows 和 backup_path 两个键。所以 status 里的 sha 只能说明「status 写入时的成品」，不能证明成品和 manifest 一致（审查 P1-7、P2-6）。
- 驱动 run_nightly_v1.py（f99dd11a，冻结）钉了 L61 sha_nightly_update、L66 sha_tier1_materialize、L68 sha_eng_daily_panels；RSS 外层保护在 L85–86、L515–516。

### 1.2 成品元数据（v2 已核，未变）
- data/v2/valuation/daily_basic_full_tushare.parquet：745,129,744 B，12,309,945 行，18 个 row group，22 列，SNAPPY；每个 row group 只含一个年份；2021–2025 每年 2 个 row group，其余 1 个；最大 row group 1,048,576 行。各年行数表见 v2 1.2。
- manifest built_at 2026-10-18T00:21:47-0400。原始文件在 10-18 01:1x 恢复时被重写，所以现成品早于现行原始文件（审查 P1-4）。

### 1.3 已知峰值
- 唯一真实运行实测：logs/nightly/daily_basic_rebuild_20261014b.log L31「elapsed=70.27 maxrss_kb=2143204 exit=0」，那次已经是按年分批的代码（同日志 L3–15、L16–28）。
- 10-14 18:03、10-17 23:57、10-18 00:20 三次 daily_basic 日志没有内存记录。
- 各阶段的拆分没有真实实测。Arch 对全量路径峰值位置的推断见审查 L240–248；增量路径的量级见本文第 3 节（引探针）。

### 1.4 现有 history_diff 与 10-14 的教训
- 代码 L396–399、L207–245、L179–205（口径见 v2 1.3）。
- 10-14b 日志 L16–28：history_diff 累计 1919 行，分布在 2023–2025 年；其中 2023 年的 271 行来自 dupfix 改代码（同年 running_rows 8668917 → 8668646）。这说明 _one 或去重规则一改，旧年的值就会变；增量只重算 R 年会把旧代码的产物冻结在旧年里（审查 P1-3）。

## 2. 设计

### 2.1 接入方式、模式与路径参数
- 新函数 materialize_daily_basic_incremental(*, end, raw_dir, dest, manifest, status, bak_dir, diff_dir, start="20140101")，所有路径都显式传参（审查 P1-8），函数体里不读模块级 ROOT、RAW。
- CLI 包装 materialize_daily_basic_cli(argv) 返回整数退出码，nightly_update.py L32 改成 `import sys; sys.exit(m.materialize_daily_basic_cli(["--mode","incremental","--end",ymd, ...]))`，显式传 mode=incremental，不把增量设成默认（审查 P2-13）。
- 全量路径保留，但必须显式设 QL_DB_ALLOW_FULL=1 才能跑，防止 nightly 误走全量。同一改动里全量路径只做三件事：去掉 L230–231 回退改为直接失败；L416 改原子写；加上这道门（审查第五节第 7 条）。
- 函数结束前（成功或失败）都打印唯一一行 `DB_INCR_RESULT {json}`，字段见 2.16。

### 2.2 重建集合 R 与原始文件变化
- R 默认 = {Y}，Y = end[:4]。1 月（end[4:6]=="01"）R = {Y-1, Y}。v2 里「当年第一个开市日」那条已经包含在「整个 1 月」里，删除（审查 P3-1）。
- 原始文件变化按**内容**判断，不看 mtime（审查 P2-4）：对每个年份，digest = sha256(按文件名排序的 (文件名, size, 内容 sha256) 列表)。内容 sha 按 1 MiB 流式读，页缓存不计入 RSS。共 3107 个文件约 1.4 GB；selftest 实测耗时，超过 60 秒再议改成「mtime 快筛 + 每周全量内容 sha」。
- 旧年 digest 与上一版 manifest.build.raw_inventory 不同 → 该年加进 R，回执报 P2 并列出变化的文件名。12 月的迟到修订如果 2 月以后才到，也由这一条发现。
- 一晚因原始文件变化加进 R 的旧年超过 2 个 → 失败，退出 25（DB_INCR_TOO_MANY_YEARS）。理由按审查 P2-11 写准：R 是逐年顺序处理，峰值不随年数增加，所以这条上限是控制运行时间和风险，不是控制内存。selftest S3 实测 R 为 4 年时的耗时。

### 2.3 原始文件选择与年内唯一性（逐文件证明）
- 文件名必须严格匹配 ^\d{8}$\.parquet（stem 为 8 位数字），且互不相同；R 年目录里出现任何 *.tmp.parquet → 失败，退出 27（DB_INCR_RAW_TMP）（审查 P2-3）。
- 每个文件经 _one 转换后，断言 trade_date 的 min = max = 文件名日期，否则退出 24（DB_INCR_DATE_MISMATCH）。
- _one 在代码 L348 已经做文件内去重（keep="last"）。
- 三条同时成立，年内 (ts_code, trade_date) 就一定唯一，逐文件检查即可，额外内存接近 0；不再做整年 group_by（审查 P2-2）。
- 这与全量路径 L374 的静默去重是有意的不同：增量路径遇到跨文件重复（理论上不会发生）就失败（退出 24，DB_INCR_DUPKEY），回执写明，人工核原始文件。

### 2.4 旧年拷贝（单驻留）
- 拷贝源是上一版成品，按 row group 逐个处理：t = pf.read_row_group(i)；校验 t 的 trade_date 统计只含该年（否则失败）；对 t 按 ≤65,536 行切片算 4.2 的列 hash，同时更新 instruments 并集和 rows；writer.write_table(t)；del t；release_unused()；记录 PHASE。
- 任何时刻内存里只有一个 row group，**不再读第二次**来比对（v2 草图 L280 的 `_hash_cmp(t, prev, i)` 删除）。
- 读取参数：pre_buffer=False、buffer_size=1 MiB、use_threads=False 作为起点，由 selftest 实测后定（审查 P1-1）。
- 拷贝时记下每个 row group 的 (行数, 22 列 hash)，供 2.8 写后回读比对。

### 2.5 当年构建（精确切片）
- 逐个原始文件：_one → 2.3 的断言 → pa.Table.from_pandas(y, schema=SCHEMA, preserve_index=False) → 放进缓冲；DataFrame 立即释放。
- 缓冲行数 ≥ 1,048,576 时：concat_tables 后 slice(0, 1048576) 写出，余下部分 slice 出来留在缓冲里（都是零拷贝），年末再写剩余部分（审查 P2-1）。这样每年的 row group 序列与全量路径一致：2021–2025 每年 [1048576, 余数]，其余年份 1 个。
- 写出的每个 row group 同样记下 (行数, 22 列 hash)，供 2.8 回读比对。

### 2.6 schema
- SCHEMA 是代码常量：22 列，名称、顺序、类型同 v2 1.2。写盘的 schema 元数据取自上一版成品（探针确认不带元数据的表可以写进带元数据的 writer；pandas_version 显示旧版本可以接受）。
- cast 用 safe=True；遇到 dictionary、string（不是 large_string）、ns 单位或 tz 不同都直接失败；schema 比较用 check_metadata=False（审查 P3-2）。
- 去重键 (ts_code, trade_date)，keep="last"（同代码 L348）；对账排序键 (trade_date, ts_code)；写盘行序为年份升序，旧年按上一版 row group 顺序，当年按文件升序和文件内原始顺序。available_at、source、quality_status、promotion_approved 按代码 L341–345 生成；拷贝年原样保留（审查 P3-4）。

### 2.7 变换版本钉（transform_sha）
- manifest.build.transform_sha = sha256(规范化后的源码)，覆盖 _one（代码 L316–349）及其依赖：to_iid（L12–22）、_daily_basic_val_cols（L164–166）、L341–345 的常量、SCHEMA 常量。规范化算法（例如对 inspect.getsource 的结果去掉行尾空白后按固定顺序拼接）由 Eng 选定后固定，写进代码和本节，需 Arch 审。
- 每晚前置检查：上一版 manifest.build.transform_sha（首晚为基线文件里的值）必须等于当前值，不等 → 失败，退出 28（DB_INCR_TRANSFORM_CHANGED）。
- 依据：10-14 的例子（1.4）——2023–2025 年 history_diff 共 1919 行，其中至少 271 行是去重修复造成的。代码一改旧年就该变；增量不重算旧年，所以必须挡住。
- 变换改了之后：单独签 .ok，用 4.1 的 ref_build 对所有年份重建并重新定基线，再恢复增量。

### 2.8 写后回读（取代 v2 2.8 的旧年自比）
- v2 2.8 对旧年拿拷贝和它的来源比 hash，等于自己比自己，查不出供应商修订，也查不出代码变更（审查 P1-2），删除。
- 取代为三件事：
  1. 写后回读：w.close() 之后，逐个 row group 用 iter_batches 读 tmp，算列 hash，与 2.4、2.5 记下的值比；同时比行数，并核对每个 row group 的 trade_date 统计只覆盖一个年份。查的是编码和写盘错误。不一致 → 失败，退出 23（DB_INCR_OLDYEAR_DIFF），tmp 回滚。
  2. 旧年相对原始文件是否一致：由 2.2 的原始文件内容 hash 发现变化。
  3. 每周按年对账：用 4.1 的 ref_build 对 2014..Y 每一年和现行原始文件对账（4.3）。
- 拷贝年份的差异不计入 history_diff_rows：它们由写后回读保证一致，不一致直接失败（审查第四节第 4 条）。

### 2.9 history_diff（只对 R 年；顺序扫描、按月分桶）
- 比较对象：tmp 成品与上一版成品，在 os.replace 之前做。
- 两边各用一次 iter_batches 顺序扫描（只取 ts_code、trade_date 和 15 个值列），按 trade_date 的自然月分桶，攒满一个月就调用一次 _compare_daily_basic_history（代码 L179–205）的口径比较：只比两边都有的 trade_date（L191–195），单边行计数（L197、L204），NaN 与 NaN 视为相等（L203）。不再用 filters 按月读（会把单年 row group 解码 24 次，审查 P2-8）。
- 任何读取或扫描错误直接失败；不保留代码 L230–231 那种整表回退。
- 差异报告：diff_dir/<D>_<stamp>.json，原子写，内容同 v2（按年月计数，每类最多 100 个样例键）。
- 上报阈值（审查第五节第 4 条），都只记录、不挡 DONE：早于 D 之前第 5 个开市日的日期上出现差异或单边行报 P2；单晚差异行超过 10,000 报 P1，由 Data 查原因；旧年因原始文件变化加进 R 报 P2。

### 2.10 提交顺序、pending 日志与备份
- 顺序（审查 P2-5、P2-9）：
  1. 写 tmp，fsync 文件；
  2. 原子写 daily_basic_full_tushare_manifest.pending.json（{prev_sha, new_sha, build...}），fsync 目录；
  3. 备份：os.link(dest, bak_dir/daily_basic_full_tushare.<YYYYMMDD_HHMM>.parquet)。data/ 与 backups/ 同一文件系统（st_dev=65040，Arch 已核），硬链接不拷贝 745 MB，os.replace 后旧 inode 由备份持有。os.link 失败（含跨文件系统）→ 不提交，失败；
  4. os.replace(tmp, dest)，fsync 目录；
  5. os.replace(pending, manifest)；
  6. 写 status（代码 L247–283 已是原子写）；
  7. 提交成功后才 prune 备份（keep=5，同 L168–177），且不删本次刚建的备份。
- 启动时如果有 pending：成品 sha == pending.new_sha → 补完第 5、6、7 步，报 P2；成品 sha == pending.prev_sha → pending 移到 _quarantine/（移动不删），报 P2；两者都不等 → 失败，退出 31（DB_INCR_PENDING_CONFLICT，本文新增，待 Arch 认可），报 P1。
- 第 4 步之后、第 5 或第 6 步失败 → 退出 30（DB_INCR_COMMIT_PARTIAL），报 P1；下次启动按 pending 分支处理。
- 取证备份 daily_basic_full_tushare.20261014_1137_dupbug.parquet 匹配代码 L172 的 glob，会被正常轮转删掉；处理方式见第 7 节未决项，本文不动它。

### 2.11 manifest 与 status
- manifest 保留现有全部键（代码 L401–415），schema 字符串不变。rows、instruments、date_min、date_max 按**全表**计算：rows 是各年之和；instruments 是所有年份 instrument_id 的并集（同 L376，现值 5917），拷贝年从每个 row group 内存里的 t 取并集，不能只算 R 年（审查 P2-7）。驱动 L1500 检查 rows 不小于跑前，L1498 检查 last_date==D。
- 新增字段只写进 manifest.build：mode、rebuilt_years、copied_years、rows_by_year、row_groups_by_year（含每个 row group 行数）、prev_sha256、new_sha256、transform_sha、raw_inventory（内容 sha 版）、peak_vmhwm_kb、phase_rss_kb、history_diff_rows、history_diff_by_year、history_diff_report、backup_path。
- status 只保留代码 L269–278 的原有键，最多加 manifest_path。新字段不进 status，因为 eng_daily_panels L166–173 会覆盖 tables.daily_basic，只保留 history_diff_rows 和 backup_path（审查 P2-6）。history_diff_rows 含义不变。

### 2.12 信号与回滚
- 函数入口装 SIGTERM 和 SIGHUP 的 handler，把信号转成异常（例如 raise DbIncrSignal(signum)），走统一回滚（审查 P1-5）。Python 默认处理 SIGTERM 是直接退出、不执行 except 和 finally，所以必须装 handler。
- 创建 tmp 时记下 (st_dev, st_ino)。回滚时只有当 tmp 路径存在且 os.stat 得到的 (st_dev, st_ino) 与记录相同时才 unlink，否则不删，报 P1。旧成品、manifest、status、备份都不动。
- 信号引起的回滚完成后，恢复默认处理并对自身重发同一信号，使父进程看到的退出码仍是 -15（SIGTERM）或 -1（SIGHUP），与码表 -15 一致，也让驱动记录到 TERM。
- SIGKILL 无法处理：tmp 残留时下一晚按 2.15 退出 21（DB_INCR_STALE_TMP）失败；人工把残留移到 _quarantine/（移动，不删除），单独签 .ok。

### 2.13 end 规则
- 增量模式下 end < 上一版 manifest 的 date_max → 失败，退出 26（DB_INCR_END_BEFORE_PREV），不截断（审查 P2-12）。回补另用工具，单独签 .ok。
- end 所在年份没有任何原始文件 → 退出 20（DB_INCR_PRECOND）。

### 2.14 年份切换（2027-01）
- 2027 年 1 月每晚：R = {2026, 2027}，C = 2014..2025；2 月起 R = {2027}。
- 依赖 2027 交易日历包（cal_2027；tier1_pull L85 写死 20261231）和 2027 原始文件，未就绪时按 2.13 清楚失败。

### 2.15 退出码表（写进代码和回执）
- 理由：nightly_update.py L119–120 把 rc∈(0,2) 记成 ok、rc==3 记成 partial（1.1）。增量版如果用 sys.exit(2) 表示失败，nightly 会当成成功。所以新增码全部从 20 起，**2 和 3 永不使用**（审查 P1-6）。python -c 里未捕获的异常返回 1，可以接受。

| 退出码 | reason_code | 含义 |
|---|---|---|
| 0 | OK | 成功 |
| 1 | EXCEPTION | 未分类异常（未捕获） |
| 20 | DB_INCR_PRECOND | 前置条件不满足：上一版成品 sha ≠ manifest.build.new_sha256（首晚对基线）、schema 不符、row group 跨年、rows_by_year 不符、end 年无原始文件等 |
| 21 | DB_INCR_STALE_TMP | 启动时已有残留 tmp |
| 22 | DB_INCR_RSS_SELF_ABORT | 检查点上 VmRSS 或 VmHWM 超过 QL_DB_RSS_ABORT_KB |
| 23 | DB_INCR_OLDYEAR_DIFF | 写后回读不一致 |
| 24 | DB_INCR_DUPKEY / DB_INCR_DATE_MISMATCH | 跨文件重复键，或文件 trade_date 与文件名不符 |
| 25 | DB_INCR_TOO_MANY_YEARS | 因原始文件变化加进 R 的旧年超过 2 个 |
| 26 | DB_INCR_END_BEFORE_PREV | end 早于上一版 date_max |
| 27 | DB_INCR_RAW_TMP | 原始目录 R 年里有 *.tmp.parquet |
| 28 | DB_INCR_TRANSFORM_CHANGED | transform_sha 与上一版不同 |
| 30 | DB_INCR_COMMIT_PARTIAL | 成品已替换但 manifest 或 status 没写成，P1 |
| 31 | DB_INCR_PENDING_CONFLICT | 启动时 pending 的 prev_sha 和 new_sha 都与成品不等，P1（本文新增，待 Arch 认可） |
| -15 | SIGNAL_TERM | 收到 SIGTERM，已回滚后按默认处理退出 |
| -1 | SIGNAL_HUP | 收到 SIGHUP，同上（是否列入请 Arch 定） |

- 任何非 0 退出码：nightly_update L120 记 `fail rc=N`，驱动 L595–598 判 FAILED，不重试，不写 DONE；成品、manifest 和旧备份都不动；纸面轨被门禁拦住属正常安全结果，报 P2。只有 30、31 报 P1（审查第四节第 3 条）。

### 2.16 DB_INCR_RESULT 行
- 新驱动从 logs/nightly/<D>_daily_basic.log 解析唯一一行 `DB_INCR_RESULT {json}`，字段：mode、rebuilt_years、copied_years、prev_sha256、new_sha256、transform_sha、rows、rows_by_year、peak_vmhwm_kb、phase_rss_kb、history_diff_rows、history_diff_by_year、raw_inventory_changed_years、backup_path、exit_code、reason_code。驱动再附上这一步的 rss_max_one 和 rss_max_sum。解析不到这一行按 FAILED 处理（审查第四节第 2 条）。

## 3. 内存（引 Arch 探针；验收以 selftest 实测为准）

- 探针来源：审查 L15、L46–60、L250–260，在 /tmp/arch_dbincr_probe/ 用合成数据测得（/usr/bin/python3，pandas 3.0.6，pyarrow 26.0.0）。合成数据每行约 125 B，真实成品约 60 B/行，只能判断量级。
- 探针数字：
  - 导入 pandas 后基线约 105,664 kB；
  - 一个 1,048,576 行、22 列的 row group，Arrow nbytes 225 MB；read_row_group 整读使 VmHWM 增加 +506,560 kB，关掉 use_threads 为 +499,124 kB，pre_buffer=False 加 buffer_size=1 MiB 为 +397,552 kB，即**读入一个 row group 会把峰值抬高约 400–500 MB**；
  - 同一个 row group 读两次（v2 草图 L280）：VmRSS 到 837,292 kB，write_table 之后 862,320 kB，即**约 840–860 MB**；
  - iter_batches(65536) 流式读写只增加 +142,064 kB（但会切成 16 个 row group，所以只用于写后回读和 history_diff 扫描，不用于拷贝写出）；
  - mimalloc：del 之后 VmRSS 回落到约 272 MB，但 VmHWM 不变；release_unused() 可用。
- 各阶段（审查 2.2 表）：旧年拷贝单驻留 +400–500 MB；当年缓冲约 225 MB 加 writer 缓冲（探针 +25 MB）；history_diff 顺序扫描约 +150–250 MB；写后回读约 +140 MB。Arch 推断照本文实现单进程峰值约 0.6–0.75 GB，以 selftest 为准。本文不另做估算。
- 内存验收线（selftest 合成数据最坏情况：1 月、R = {Y-1, Y}、Y-1 取 1,313,182 行的最大年，即审查 S2；以及 S3）：
  - 单进程 VmHWM ≤ 1,000,000 kB；
  - 外部 1 秒采样的进程树合计 ≤ 1,100,000 kB；
  - 进程自检中止线 QL_DB_RSS_ABORT_KB = 1,200,000 kB。
- 自检：每处理完一个 row group、一个原始文件、一个月桶，读 /proc/self/status 的 VmRSS 和 VmHWM；**任一**超过 1,200,000 kB 即抛异常回滚，退出 22（审查 P2-10，两次检查之间的尖峰由 VmHWM 兜住）。每阶段结束调用一次 release_unused 并打印「PHASE <名> rss_kb=… hwm_kb=…」；结束时打印「elapsed=… maxrss_kb=… exit=…」。
- 驱动外层保护不变：树合计 1,484,800 kB、单进程 1,536,000 kB（驱动 L85–86）。
- 真实运行首晚：VmHWM > 1,000,000 kB 报 P2，下一晚前由 Arch 复核；> 1,200,000 kB 自检中止，FAILED，不重试。

## 4. 对账

### 4.1 参考重建器 ref_build（基准）
- 基准**不用现成品**：现成品建于 10-18 00:21（manifest built_at 2026-10-18T00:21:47-0400），早于 10-18 01:1x 原始文件恢复，证明不了它和现行原始文件全量重建的结果一致。**也不跑新的全量**：全量实测 2,143,204 kB，超过单进程 1,536,000 kB 的硬约束，不能跑、不能签 .ok（审查 P1-4）。
- 规格：逻辑上等于代码 L316–349 的 _one 加 L372–374 的拼接和去重，但每次只处理一个 trade_date 自然月：按文件升序读该月文件，逐个 _one，concat，drop_duplicates(["ts_code","trade_date"], keep="last")，再按 4.2 喂 hash。每个进程只算一年，一年 12 个月顺序处理；只输出逐年 hash 和计数，不写成品。路径全部传参，带第 3 节的自检。
- 等价性论证：
  1. 去重键 (ts_code, trade_date) 包含 trade_date，同一个键的所有副本 trade_date 相同，只能落在同一个自然月，重复行不可能跨月；
  2. 全量路径年内 concat 保持文件顺序（L291 sorted，L365 顺序追加），按月分区后每个分区内的相对顺序与整年 concat 中的相对顺序相同；
  3. 所以每个月分区上 keep="last" 选出的行，和整年 drop_duplicates 选出的行完全相同，行序也相同（同为文件升序、文件内顺序）。
  4. 这一论证不依赖「每个文件只含一个日期」，即使某文件含其他日期的行也成立。
- 用途：合成数据上的增量对账（A4）；影子运行时对 2014..Y 每一年与现行原始文件对账（顺带核实全部拷贝年）；每周复核（4.3）。

### 4.2 对账规格（审查第三节）
1. 逐年比行数，以及 row group 行数序列。
2. 内容 hash：每年每列一个 sha256；先喂列头（列名、Arrow 类型字符串、该年行数）；行按 (trade_date, ts_code) 排序（键唯一）。规范化：
   - double：1 字节有效位（null 和任何 NaN 载荷记 0，后跟 8 个 0x00），否则记 1 加 8 字节小端 IEEE-754 值；-0.0 用 np.where(v == 0, 0.0, v) 规范成 +0.0；只喂原始字节，不经过任何文本格式化；
   - timestamp：断言单位 us、tz 为 Asia/Shanghai 或无 tz（与 schema 一致）；1 字节有效位加 int64 小端值；
   - large_string：1 字节有效位，加 8 字节小端长度，加原始 UTF-8 字节；不做 Unicode 规范化；断言 ts_code 和 instrument_id 只含 ASCII；
   - bool：1 字节有效位加 1 字节值；
   - 每批 ≤65,536 行，用 pyarrow.compute 加 numpy 视图，不逐行循环。
3. 物理行序 hash：按文件物理顺序再算一次全行 hash，上线前也必须相等。
4. 严格表示：每列每年分别统计 null 数和 NaN 数，两边相等（补上内容 hash 把 null 与 NaN 视为同值的口径差）。
5. 不变量计数，每年都必须是 0：available_at − trade_date ≠ 18 小时；source ≠ "tushare.daily_basic"；quality_status ≠ "research"；promotion_approved ≠ False；row group trade_date 统计跨年的个数。
6. schema 一致（check_metadata=False），pandas 元数据里各列 dtype 字符串一致。
7. 文件 sha 只记录，不作一致标准。
8. 不一致时按月定位，每类最多 100 个样例键。
- 一致标准：以上 1–6 全部相同。

### 4.3 每周复核与门禁
- 每周日空档，用 ref_build 对 2014..Y 每一年与现行成品按 4.2 对账，单独签 .ok：只读，输出限 /tmp，单进程（每年一个进程，顺序跑），不与 94322 等重任务重叠。
- 影子运行同样单独签 .ok。

## 5. 10-19 遗留与 10-20 首晚预案

### 5.1 10-19 旧代码可能留下的现场（审查 P1-7）
- 停在年度构建：留下 data/v2/valuation/_daily_basic_parts_<stamp>/；而 L311–313 已多做一份备份，并按 keep=5 删掉最旧一份（按文件名排序，10-19 若走到这里会删 daily_basic_full_tushare.20261014_1136.parquet）。
- 停在 L390–392：留下 daily_basic_full_tushare.tmp.parquet，会撞上增量版的 STALE_TMP（退出 21）。
- 停在 L393 之后（history_diff 阶段）：成品已换新，manifest 仍是旧的（L416 未执行），即「新表配一份过时 manifest」；随后 eng_panels 的 daily_core（L147–152）会按新文件重算 status 里的 sha、rows、last_date，status 看起来正常。

### 5.2 10-19 18:40 之后的只读盘点（Data 执行，不需要 .ok，只读）
- 列出并取 sha：daily_basic_full_tushare.tmp.parquet 是否存在（含 stat 的 inode、size、mtime）；data/v2/valuation/_daily_basic_parts_* 目录及内容清单；成品 sha 与 manifest（built_at、rows、date_max）、status（tables.daily_basic 的 sha256、rows、last_date）三者是否一致；backups/valuation/ 清单与 sha；原始目录里的 *.tmp.parquet。
- 判定「新表配过时 manifest」：成品 read_metadata 的行数 / 最大 trade_date 统计与 manifest 的 rows / date_max 不符，或成品 mtime 晚于 manifest built_at。
- 回执写到 docs/v2/audit/ 下新文件，附 sha，交 Arch 和主 Agent。发现的残留只列出，不处理；隔离（移到 _quarantine/，移动不删除）需单独签 .ok（审查 P3-5、A8）。

### 5.3 引导基线（单独签 .ok，一步）
- 前提：5.2 盘点无未处理残留，成品、manifest 一致或已由 Arch 裁定。
- 只读成品元数据，加上 4.1 的 ref_build 对 2014..Y 每一年的对账（真实原始文件，只读，输出 /tmp，空档，单进程逐年）。
- 原子写 data/v2/valuation/daily_basic_full_tushare_build_baseline.json：成品 sha、rows_by_year、row_groups_by_year、每年列 hash、schema、transform_sha、内容 sha 版 raw_inventory，以及 ref_build 对账结果。
- ref_build 与现成品有差异时，不写基线，列出差异交 Arch 和主 Agent 定（A9）。

### 5.4 前置检查改为对 manifest
- 增量前置检查：成品 sha == 上一版 manifest.build.new_sha256；首晚 == 基线文件里的成品 sha。
- status 里的 sha 由 eng_daily_panels L152 重算，只作旁证，不作前置依据。

## 6. 实施与门禁

### 6.1 顺序与时间线
1. Data 交 v3（本文）；Arch 10-19 18:40 前复核。
2. Eng 10-19 18:40 之后实现。改代码前把 tier1_materialize.py（e9c89a6c…）和 nightly_update.py（ec079d56…）归档到 /workspace/QuantLab/_recovery/data/daily_basic_incr_<stamp>/，附 sha；附代码 diff 交 Arch 审。
3. selftest .ok 与回执（6.2）。
4. 10-19 现场盘点（5.2）。
5. 引导基线 .ok，同时做影子分年对账（5.3）。
6. 新版驱动（新文件名，例如 run_nightly_v2.py；f99dd11a 冻结不改）重钉 L66 sha_tier1_materialize 和 L61 sha_nightly_update，L68 sha_eng_daily_panels 不改（本文不改 eng_daily_panels）；冻结清单和 sha 范围文件同步更新；Arch 另签 10-20 的 .ok，带增量注释行（模式、自检阈值、首晚 VmHWM 处置）。
- **到 10-20 05:00 ET 任何一步没就绪，10-20 那晚照旧走全量重建**；内存超限被驱动停掉一律按 P2 处理，不是事故，不重试。

### 6.2 selftest 与隔离
- .ok：scope=selftest，allow_real_data=false，out_dir 在 /tmp 下；测试文件开头先 enforce(modes=["selftest"])（写法同 docs/v2/audit/backfill_1014_1016/selftest_run_backfill_r_v3_1_c.py L17 起）。
- 隔离（审查 P1-8）：所有路径传参；开头断言 raw_dir、dest、manifest、status、bak_dir、diff_dir 的 realpath 都以 /tmp/ 开头；测试前后各取一次真实成品、manifest、status 的 sha 和 backups/valuation/ 清单（文件名与 sha），必须完全不变，写进回执（A7）。
- 合成数据与场景按审查 2.4：生成器在 /tmp 生成 2014-01-02 到 2026-10-16 的日文件，每年行数对齐 v2 1.2，原始 schema 由 Data 只用 read_schema 读一个原始文件的元数据后提供；场景 S1–S13（审查 L277–290）。
- 采样：进程内 PHASE 行；外部采样器每秒读 /proc/<pid>/status 按树合计，nice -n 10；/usr/bin/time -v（先 command -v 确认存在）。
- 校准按审查 L295–299（/tmp 里旧模块副本，分两个进程，看门狗 1,450,000 kB 按精确 PID 发 TERM），不允许整段全量跑完。
- 验收：审查第七节 A1–A11；内存按第 3 节验收线。

## 7. 未决项（需 Arch 或主 Agent 定）
1. 规范化源码求 transform_sha 的具体算法（2.7），Eng 提出、Arch 审定。
2. 新增退出码 31（DB_INCR_PENDING_CONFLICT）和 SIGHUP 对应的 -1 是否进码表（2.12、2.15）。
3. 原始文件每晚内容 sha 的耗时：selftest 实测超过 60 秒时，是否改「mtime 快筛 + 每周全量内容 sha」（2.2）。
4. **20261014_1137_dupbug 取证备份**：它匹配代码 L172 的 glob。现在备份目录正好 5 份，按文件名排序它是第二旧；旧代码每成功做一次备份就删最旧一份，所以 10-19 旧代码走到 L311–313 会删 20261014_1136，10-20 若仍走旧全量路径就会删 20261014_1137_dupbug。是否把它移出修剪范围（移到不匹配 glob 的取证目录），等主 Agent 批准并单独签 .ok；本文和本次工作都不动它。若要保住它，可由主 Agent 和 Arch 考虑在 10-19 / 10-20 的 nightly 环境里设 QL_DAILY_BASIC_NO_PRUNE=1（代码 L169–171 已支持），这也要 Arch 定。
5. eng_daily_panels daily_core L151–152 整列读 1230 万行 trade_date 并 astype(str) 的内存风险（审查 P2-6 末段），请 Eng 在合成数据上实测，另报。
6. 10-20 启用的前置条件：新版驱动重钉 L66 和 L61、Arch 另签 .ok、5.2 盘点与 5.3 基线完成，三者缺一即 10-20 走旧路径（审查第五节第 9 条）。
7. 5.2 盘点发现残留时的隔离 .ok，以及「新表配过时 manifest」时以哪一方为准，由 Arch 和主 Agent 定。

## 8. 代码草图（只作文档内容，未应用到任何代码；以 Eng 实现、Arch 审查为准）

```python
class DbIncrError(Exception):
    def __init__(self, code, reason): super().__init__(reason); self.code, self.reason = code, reason
class DbIncrSignal(BaseException):
    def __init__(self, signum): self.signum = signum

def _on_signal(signum, frame): raise DbIncrSignal(signum)

def materialize_daily_basic_incremental(*, end, raw_dir, dest, manifest, status, bak_dir, diff_dir, start="20140101"):
    import signal, pyarrow as pa, pyarrow.parquet as pq
    old = {s: signal.signal(s, _on_signal) for s in (signal.SIGTERM, signal.SIGHUP)}
    tmp = dest.with_suffix(".tmp.parquet"); tmp_id = None; w = None; res = {"mode": "incremental"}
    try:
        if tmp.exists(): raise DbIncrError(21, "DB_INCR_STALE_TMP")
        prev = _precheck(dest, manifest, end)                 # 2.13 / 5.4 / 2.7：26 / 20 / 28
        R = _rebuild_years(end, prev, raw_dir)                # 2.2：内容 sha；>2 旧年 -> 25；*.tmp -> 27
        w = pq.ParquetWriter(tmp, SCHEMA_WITH_PREV_META, compression="snappy")
        st = os.stat(tmp); tmp_id = (st.st_dev, st.st_ino)
        rec = []                                              # 每个写出 row group 的 (rows, col_hashes)
        for y in range(int(start[:4]), int(end[:4]) + 1):
            if y in R: _build_year(y, raw_dir, end, w, rec, res)   # 2.3 逐文件断言 + 2.5 精确切片
            else: _copy_year(y, prev, w, rec, res)                 # 2.4 单驻留：读一次、切片 hash、写、del
        w.close(); w = None
        _verify_readback(tmp, rec)                            # 2.8：iter_batches 回读，不一致 -> 23
        diff = _history_diff_scan(dest, tmp, R, diff_dir)     # 2.9：顺序扫描按月分桶，无整表回退
        _commit(tmp, dest, manifest, status, bak_dir, res, diff)   # 2.10：pending -> link 备份 -> replace -> manifest -> status -> prune
        return _result(res, 0, "OK")
    except BaseException as e:
        if w is not None:
            try: w.close()
            except Exception: pass
        if tmp_id is not None and tmp.exists():
            s2 = os.stat(tmp)
            if (s2.st_dev, s2.st_ino) == tmp_id: tmp.unlink()   # 只删本次创建的 tmp
        if isinstance(e, DbIncrSignal):
            _result(res, -e.signum, "SIGNAL"); signal.signal(e.signum, signal.SIG_DFL); os.kill(os.getpid(), e.signum)
        if isinstance(e, DbIncrError): return _result(res, e.code, e.reason)
        _result(res, 1, "EXCEPTION"); raise
    finally:
        for s, h in old.items(): signal.signal(s, h)
```
- _result 负责打印唯一一行 DB_INCR_RESULT（2.16）；_guard（第 3 节自检）在 _copy_year、_build_year、_verify_readback、_history_diff_scan 的每个检查点调用，超线抛 DbIncrError(22, ...)。_commit 中第 4 步之后的失败抛 DbIncrError(30, ...)，pending 冲突抛 DbIncrError(31, ...)。

## 附：本文依据
- 设计 v2：e6372b9b0e67992a1ab1e77fcb038874e0f5ced85be37149fe6a84f88b74c08e。
- Arch 审查：docs/v2/ARCH_DAILY_BASIC_INCREMENTAL_REVIEW_ZH.md 9ef7f89581120a0af9bd43406eee7a7554a13fef834afc4138e0d885b8b402b3（P1-1–P1-8、P2-1–P2-13、P3-1–P3-5、第二至七节）。
- 代码（只读）：tier1_materialize.py e9c89a6c…（L12–22、L164–177、L179–205、L207–245、L247–283、L285–419）；nightly_update.py ec079d56…（L20–21、L25、L32、L113–120）；eng_daily_panels.py（L144–153、L166–173）；run_nightly_v1.py f99dd11a…（L61、L66、L68、L85–86、L515–516）。
- 日志：logs/nightly/daily_basic_rebuild_20261014b.log L1–31。

## v3 变更记录
- 写于 2026-10-18T16:56:13-0400（取自 date）；依据 Arch 10-18 16:50 ET 的 8 条 P1 指令与审查文档 docs/v2/ARCH_DAILY_BASIC_INCREMENTAL_REVIEW_ZH.md（9ef7f89581120a0af9bd43406eee7a7554a13fef834afc4138e0d885b8b402b3）；源文件 docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v2_ZH.md（e6372b9b0e67992a1ab1e77fcb038874e0f5ced85be37149fe6a84f88b74c08e，本身未动；v1 60d92023… 也未动）。
- 整篇重写：文头加 R1–R13 对照表、P1 与 P2 落实索引；第 2 节按审查重排为 2.1–2.16；第 3 节内存改为引用 Arch 探针、去掉 v2 自己的估算；第 4 节对账基准改为 ref_build；新增第 5 节 10-19 遗留与 10-20 首晚预案；第 7 节未决项更新（含 20261014_1137_dupbug）；第 8 节草图重写，v2 第 6 节草图作废。
