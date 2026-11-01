# daily_basic 增量重建设计 v3.1（只写文档，不改代码；Data 起草，交 Arch 确认）

- 作者：QuantLab Data；写于 2026-10-25T00:24:44-0400（取自 date）。
- **本文件 = 设计 v3 + Arch 复审 C1–C12 闭合**（含决定 (a)–(g)、P3 的 D1–D4、验收增补 A12–A18）。
- 审查源（全文必读，含「复审（v3）」）：docs/v2/ARCH_DAILY_BASIC_INCREMENTAL_REVIEW_ZH.md，**全长 sha256 48a64380682e593adb1d3386ae92126df4173e31c61b7699ff6ce8f7b06fe18a**，524 行（已核）。下文「复审 Lxx」指该文件行号。
- 基线设计 v3（**本身未动**）：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_ZH.md，**全长 sha256 13fd86b67ba6c8d074aba08d8a3ad3cac93fd7ebbae9acbe41547e80c15d0aab**，336 行（已核）。下文旧「v3 Lxx」仅作溯源；正文行号以本文件为准（Arch D2：对照表已按 v3.1 新行号整体复核）。
- 复制改写自 v3，**不得覆盖 v3**。live=false，promotion_approved=false；不涉及 8787 和 moneyflow。
- 本文只读了审查文档与 v3 设计。没有读真实数据行，没有运行项目代码，没有改仓库代码，没有发信号，没有动备份。
- **BACKUP_PIN（决定 (a)）已于 2026-10-25 00:15 ET 完成**：回执 docs/v2/audit/fundport_20261025/BACKUP_PIN_RECEIPT_20261025.json，sha256 15905d602e0df9041f50248dccfdea513d43284dde48fc23a630bcd3fac48cf1；1136 与 1137_dupbug 均已 os.link 至 backups/valuation_pinned/，nlink=2。v3.1 **不再**把它列为待办。
- **启用窗口说明**：原定 10-20 05:00 ET 启用窗口已过期。启用条件改为：**Arch 确认 v3.1 + Eng 代码 diff 逐条对应 C1–C12 + 另签 Arch .ok**；未满足则继续旧全量路径。实现/运行仍须另签 Arch .ok。

## C1–C12 对照表（写完后填实行号）

| ID | 优先级 | 摘要 | 落点节 | 行号 |
|---|---|---|---|---|
| C1 | P2 | 正则改为完整文件名 `^\d{8}\.parquet$`（或 stem `^\d{8}$` 且后缀恰为 .parquet） | §2.3 | L112–L120 |
| C2 | P1-5/P1-6 | SIGHUP 退出码 **32**（DB_INCR_SIGNAL_HUP）；码表删 -1；SIGTERM 仍回滚后重发、退出 -15 | §2.15 / §2.12 / §8 | L197–L205; L217–L240; L345–L414 |
| C3 | P1-3 | transform_sha = sha256(规范化 AST dump，去 docstring) + 常量表；指纹含 python/pandas/pyarrow/numpy 版本；版本变亦退出 28 | §2.7 | L137–L143 |
| C4 | P1-3 | _one 外提为模块级；A14：外提后与旧闭包在合成文件上 22 列 hash 逐文件相等 | §2.7b | L144–L148 |
| C5 | P1-5 | except 入口先把 SIGTERM/SIGHUP 设为 SIG_IGN，清理完再按 C2 退出 | §2.12 / §8 | L197–L205; 草图 except |
| C6 | P1-5 | tmp 用 O_CREAT\|O_EXCL 创建并立刻记 (st_dev, st_ino)，再交给 ParquetWriter | §2.12b / §8 | L206–L209 |
| C7 | P1-5 | S5：拷贝/构建/回读/diff/提交五阶段各随机 TERM；TERM→退出 ≤5 s | §6.2b | L324–L328 |
| C8 | P1-7 | 新表+过时 manifest 两边都不信，基线只能由 ref_build 产生；盘点时序与只读边界 | §5.2 / §5.3 | L294–L300 |
| C9 | P1-4 | ref_build 最大年 VmHWM ≤ 1,000,000 kB（A13） | §4.1b | L261–L264 |
| C10 | P2-4 | 快筛加 st_ctime_ns；raw_touched / raw_full_sha_required=true 强制全量内容 sha | §2.2 | L102–L111 |
| C11 | P2-5 | 启动：pending 恢复 → STALE_TMP → 前置；失败且成品未变则本次自移 pending 至隔离 | §2.10b | L181–L191 |
| C12 | P2-9 | 硬链接失败撤回（核对同 inode）；成品只许 os.replace；备份名精确到秒 | §2.10 | L166–L179 |

## Arch 决定 (a)–(g) 落实索引

| 决定 | 内容 | v3.1 落点 |
|---|---|---|
| (a) | 取证备份硬链接到 valuation_pinned/；不用 NO_PRUNE | **已完成**（2026-10-25 00:15 ET）；见文首；§7 不再列为待办 |
| (b) | 接受 31；SIGHUP 用 **32**（DB_INCR_SIGNAL_HUP），不用 -1 | §2.12、§2.15、§8 草图 |
| (c) | transform_sha = sha256(规范化 AST dump，去 docstring)+常量表 | §2.7（C3） |
| (d) | 内容 sha 先实测；>60s 则快筛（含 ctime）+ 每周全量；恢复/回补夜强制全量 | §2.2（C10） |
| (e) | 新表+过时 manifest 两边都不信，须 ref_build 定基线 | §5.2、§5.3（C8）；A18 |
| (f) | Eng 实测 eng_daily_panels L151–152 VmHWM → A12 | §6.2、A12 |
| (g) | L82 正则写错 → C1 | §2.3 |

## R1–R13 对照表（按 v3.1 新行号复核，Arch D2）

| 条目 | 状态 | v3.1 位置 | 相对 v3 的闭合补丁 |
|---|---|---|---|
| R1 | 已关闭 | §2.4；§2.8；§3 | 同 v3 |
| R2 | 闭合（C3、C4） | §2.7；§2.7b | AST+版本；_one 外提+A14 |
| R3 | 闭合（C9） | §4.1；§4.1b | 补 A13 内存线 |
| R4 | 闭合（C2、C5、C6、C7） | §2.12；§2.12b；§6.2b；§8 | SIGHUP=32；SIG_IGN；O_EXCL；TERM≤5s |
| R5 | 闭合（C2） | §2.15；§2.1 | 码表加 32、删 -1 |
| R6 | 闭合（C8） | §5 | 新表+过时manifest 都不信 |
| R7 | 已关闭 | §2.1；§6.2 | 同 v3 |
| R8 | 闭合（C1） | §2.3；§2.5 | 正则修正 |
| R9 | 闭合（C10、C11、C12） | §2.2；§2.10；§2.10b | ctime+raw_touched；pending 顺序；硬链接撤回+秒级名 |
| R10 | 已关闭 | §2.11 | 同 v3 |
| R11 | 已关闭（附 D3） | §2.9 | 重复键 ValueError→24 |
| R12 | 已关闭 | §3；§2.13 | 同 v3 |
| R13 | 已关闭（附 D4） | §4.2；§5.3 | 基线「每年列 hash」=4.2 排序内容 hash；与写后回读物理序 hash 分名 |

## P1 逐条状态（相对复审）

| P1 | 状态 | v3.1 |
|---|---|---|
| P1-1 | 已关闭 | §2.4；§2.8；§3 |
| P1-2 | 已关闭 | §2.8 |
| P1-3 | 闭合（C3、C4） | §2.7；§2.7b |
| P1-4 | 闭合（C9） | §4.1；§4.1b |
| P1-5 | 闭合（C2、C5、C6、C7） | §2.12；§2.12b；§6.2b |
| P1-6 | 闭合（C2） | §2.15 |
| P1-7 | 闭合（C8） | §5 |
| P1-8 | 已关闭 | §2.1；§6.2 |

---

## 1. 现状（与 v3 第 1 节相同的事实只摘要）

### 1.1 代码位置
- scripts/acquire/tier1_materialize.py，sha256 e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb，650 行。materialize_daily_basic 在代码 L285–419：L291 选原始文件；L309–314 copy2 备份并 keep=5 轮转（L168–177）；L316–349 _one（**闭包**，见 §2.7b C4 外提要求）；L356–384 按年分批；L388–393 ParquetWriter 逐分片写 tmp 再 os.replace；L396–399 history_diff；L401–416 manifest（L416 非原子）；L417 写 status（L247–283，原子）。
- 代码 L291 的 `start <= p.stem <= end` 会把 20261015.tmp.parquet（stem 为 "20261015.tmp"）算进来（审查 P2-3）。增量版按 §2.3（C1）严格匹配。
- scripts/nightly_update.py（ec079d56…）L25 用 `python3 -c` 起子进程，L32 调 `m.materialize_daily_basic(end=ymd)`。L119 `if rc not in (0,2): break`；L120 把 rc∈(0,2) 记 ok、rc==3 记 partial。增量版码表从 20 起，**2 和 3 永不使用**（§2.15）。
- scripts/acquire/eng_daily_panels.py 的 daily_core（L144–153）对 daily_basic 成品读整列 trade_date（L151）并用 sha(f) 重算 status；L166–173 只保留 history_diff_rows 和 backup_path。status 的 sha 只作旁证（§5.4）。L151–152 内存实测为 A12（决定 (f)）。
- 驱动 run_nightly_v1.py（f99dd11a，冻结）钉了 L61 / L66 / L68；RSS 外层 L85–86、L515–516；stop_tree：先 SIGSTOP，再 TERM+CONT，等 TERM_WAIT_S=10 秒，还在就 KILL（复审 L428–430）。因此回滚必须在 ≤5 秒内完成（C7），并在 except 入口 SIG_IGN（C5），否则第二次 TERM 会打断清理。

### 1.2 成品元数据（同 v3）
- data/v2/valuation/daily_basic_full_tushare.parquet：745,129,744 B，12,309,945 行，18 个 row group，22 列，SNAPPY；每个 row group 只含一个年份；2021–2025 每年 2 个，其余 1 个；最大 row group 1,048,576 行。
- manifest built_at 2026-10-18T00:21:47-0400。原始文件在 10-18 01:1x 恢复时被重写，现成品早于现行原始文件（审查 P1-4）→ 基准用 ref_build（§4.1），不能用现成品，也不跑新全量。

### 1.3 已知峰值
- 唯一真实运行实测：logs/nightly/daily_basic_rebuild_20261014b.log L31「elapsed=70.27 maxrss_kb=2143204 exit=0」。
- 探针量级见 §3（引 Arch 审查）；验收以 selftest 实测为准。

### 1.4 history_diff 与 10-14 教训
- 10-14b：history_diff 累计 1919 行（2023–2025），其中 2023 年 271 行来自 dupfix 改代码。增量只重算 R 年会把旧代码产物冻结在旧年 → 必须钉 transform_sha（§2.7 / C3），并外提 _one 以免增量和 ref_build 同步引入同一偏差（§2.7b / C4）。

## 2. 设计

### 2.1 接入方式、模式与路径参数
- 新函数 materialize_daily_basic_incremental(*, end, raw_dir, dest, manifest, status, bak_dir, diff_dir, start="20140101")，所有路径显式传参（审查 P1-8），函数体不读模块级 ROOT、RAW。
- CLI：materialize_daily_basic_cli(argv) 返回整数退出码；nightly_update.py L32 改成 `sys.exit(m.materialize_daily_basic_cli(["--mode","incremental","--end",ymd, ...]))`，显式 mode=incremental，不把增量设成默认（审查 P2-13）。
- 全量路径保留，须 QL_DB_ALLOW_FULL=1；同一次改动只做三件事：去掉 L230–231 整表回退改为直接失败；L416 改原子写；加这道门。
- 函数结束前（成功或失败）都打印唯一一行 `DB_INCR_RESULT {json}`（§2.16）。

### 2.2 重建集合 R 与原始文件变化
- R 默认 = {Y}，Y = end[:4]。1 月（end[4:6]=="01"）R = {Y-1, Y}。删除「当年第一个开市日」冗余条（审查 P3-1）。
- **内容判变（决定 (d) / C10）**：
  1. 先实测每晚对全部旧年原始文件做内容 sha256 的耗时（1 MiB 流式读；共约 3107 个文件、约 1.4 GB）。
  2. **≤60 秒**：每晚做内容 sha。digest = sha256(按文件名排序的 (文件名, size, 内容 sha256) 列表)。
  3. **>60 秒**：每晚做快筛，每周做一次全量内容 sha。快筛键 = (文件名, size, mtime_ns, **st_ino**, **st_ctime_ns**)。**必须含 ctime**：shutil.copy2 写到已有路径时 inode 与 mtime 可变相保持不变、大小也可相同，三项全不变；任何写入都会更新 ctime，用户态改不回去（复审 C10）。
  4. **强制全量内容 sha 的触发**：当晚之前发生过原始文件的恢复、拷贝或回补时，必须做全量内容 sha。实现约定：恢复/拷贝/回补工具在原始目录外写 `raw_touched` 标记文件，**或**在当晚 .ok 注释里写 `raw_full_sha_required=true`；增量前置见到任一标记即强制全量内容 sha，用完后按 .ok 约定清除标记（清除属写操作，须该 .ok 授权）。
- 旧年 digest / 快筛结果与上一版 manifest.build.raw_inventory 不同 → 该年加进 R，回执报 P2 并列出变化文件名。
- 一晚因原始文件变化加进 R 的旧年超过 2 个 → 退出 25（DB_INCR_TOO_MANY_YEARS）。理由：R 逐年顺序处理，峰值不随年数增加；上限控时间与风险，不控内存（审查 P2-11）。selftest S3 实测 R=4 年耗时；A17 验证 copy2 同大小同 mtime 不同内容时快筛（含 ctime）能发现。

### 2.3 原始文件选择与年内唯一性（逐文件证明；C1）
- **C1（复审 L490）**：完整文件名必须匹配 `^\d{8}\.parquet$`（等价写法：stem 匹配 `^\d{8}$` **且** 后缀正好是 `.parquet`）。v3 L82 的 `^\d{8}$\.parquet` 是错误写法（`$` 位置错），废止。
- 文件名互不相同；R 年目录里出现任何 `*.tmp.parquet` → 退出 27（DB_INCR_RAW_TMP）（审查 P2-3）。
- 每个文件经 _one 转换后，断言 trade_date 的 min = max = 文件名日期，否则退出 24（DB_INCR_DATE_MISMATCH）。
- _one 在文件内去重（keep="last"；外提后的模块级函数，见 §2.7b）。
- 三条同时成立 → 年内 (ts_code, trade_date) 唯一；不做整年 group_by（审查 P2-2）。
- 与全量路径 L374 静默去重有意不同：增量遇跨文件重复即失败（退出 24，DB_INCR_DUPKEY），回执写明，人工核原始文件。
- **D3**：`_compare_daily_basic_history` 在代码 L185–188 抛的重复键 ValueError，映射为退出码 24（DB_INCR_DUPKEY），不得落到未分类 1。

### 2.4 旧年拷贝（单驻留）
- 拷贝源是上一版成品，按 row group 逐个：t = pf.read_row_group(i)；校验 trade_date 统计只含该年；对 t 按 ≤65,536 行切片算 §4.2 列 hash，同时更新 instruments 并集和 rows；writer.write_table(t)；del t；release_unused()；记录 PHASE。
- 任何时刻内存里只有一个 row group，**不再读第二次**（v2 草图自比删除）。
- 读取参数起点：pre_buffer=False、buffer_size=1 MiB、use_threads=False，selftest 实测后定。
- 拷贝时记下每个 row group 的 (行数, 22 列 **物理序** hash)，供 §2.8 写后回读比对（与 §4.2 / 基线的「排序内容 hash」分名，见 D4）。

### 2.5 当年构建（精确切片）
- 逐个原始文件：_one → §2.3 断言 → pa.Table.from_pandas(..., schema=SCHEMA, preserve_index=False) → 缓冲；DataFrame 立即释放。
- 缓冲 ≥ 1,048,576 行：concat_tables 后 slice(0, 1048576) 写出，余数留下批，年末写剩余（审查 P2-1）。每年 row group 序列与全量一致：2021–2025 为 [1048576, 余数]，其余 1 个。
- 每个写出的 row group 同样记下 (行数, 22 列物理序 hash)。

### 2.6 schema
- SCHEMA 是代码常量：22 列，名称、顺序、类型同 v2 1.2。写盘 schema 元数据取自上一版成品。
- cast 用 safe=True；遇到 dictionary、string（非 large_string）、ns 单位或 tz 不同都直接失败；schema 比较 check_metadata=False（审查 P3-2）。
- 去重键 (ts_code, trade_date)，keep="last"；对账排序键 (trade_date, ts_code)；写盘行序：年份升序，旧年按上一版 row group 顺序，当年按文件升序和文件内原始顺序。available_at、source、quality_status、promotion_approved 按代码 L341–345 生成；拷贝年原样保留（审查 P3-4）。

### 2.7 变换版本钉（transform_sha；C3 / 决定 (c)）
- **C3**：`manifest.build.transform_sha = sha256(规范化 AST dump)`。范围 = 去掉 docstring 之后的变换函数源（外提后的模块级 `_one` 及其直接依赖：`to_iid`、`_daily_basic_val_cols`、L341–345 常量、SCHEMA 常量），加上常量表。**废止** v3 的「inspect.getsource 去掉行尾空白」写法。具体 AST 规范化实现由 Eng 提出、Arch 审定后钉死进代码与本节。
- **运行时版本指纹**（同写进 manifest.build，例如 `runtime_versions`）：python、pandas、pyarrow、numpy 的版本字符串。任一与上一版（首晚为基线）不同 → 同样退出 28（DB_INCR_TRANSFORM_CHANGED），须单独签 .ok 才能放行。理由：to_datetime 时间单位、to_numeric 行为会随版本变化，cast(safe=True) 不一定拦得住（复审 C3）。
- 每晚前置：上一版 transform_sha **与** runtime_versions 均须等于当前值；不等 → 退出 28。
- 依据：§1.4 的 1919 / 271 例子。
- 变换或运行时版本改了之后：单独签 .ok，用 §4.1 ref_build 对所有年份重建并重新定基线，再恢复增量。

### 2.7b _one 外提与等价性（C4 / A14）
- 现行 `_one` 是 `materialize_daily_basic` 内闭包（代码 L316）。增量路径与 ref_build **都必须**先把它外提成模块级函数（同一份实现）。
- **A14**：在 /tmp 合成文件上，外提后的 `_one` 与旧闭包（在 /tmp 拷一份旧模块，**不在仓库里打补丁**）对每个文件的输出，22 列 hash 完全相等。否则外提引入的变化会同时出现在增量和 ref_build 两边，对账查不出来（复审 C4）。
- 外提 diff 须在 Eng 交 Arch 的代码 diff 里单独成段，对应 C4。

### 2.8 写后回读（取代 v2 旧年自比）
- v2 旧年自比删除（审查 P1-2）。
- 三件事：
  1. 写后回读：w.close() 后，逐个 row group 用 iter_batches 读 tmp，算**物理序**列 hash，与 §2.4 / §2.5 记下的值比；同时比行数，并核对每个 row group 的 trade_date 统计只覆盖一个年份。不一致 → 退出 23（DB_INCR_OLDYEAR_DIFF），tmp 回滚。
  2. 旧年相对原始文件：由 §2.2 内容 hash / 快筛发现变化。
  3. 每周按年对账：§4.1 ref_build（§4.3）。
- 拷贝年份差异不计入 history_diff_rows（审查第四节第 4 条）。
- **D4 命名**：写后回读用的是「row_group_physical_col_hashes」；基线 / §4.2 对账用的是「year_sorted_content_col_hashes」。二者分别命名，禁止混用。

### 2.9 history_diff（只对 R 年；顺序扫描、按月分桶）
- 比较对象：tmp 与上一版成品，在 os.replace 之前做。
- 两边各一次 iter_batches 顺序扫描（ts_code、trade_date 与 15 个值列），按自然月分桶，攒满一月调用 `_compare_daily_basic_history`（口径同代码 L191–204）。不用 filters 按月读（审查 P2-8）。
- 读错直接失败；不保留 L230–231 整表回退。
- 重复键 ValueError → 退出 24（D3）。
- 差异报告：diff_dir/<D>_<stamp>.json，原子写。
- 上报阈值（审查第五节第 4 条），只记录、不挡 DONE：早于 D 之前第 5 个开市日的差异/单边 → P2；单晚差异行 >10,000 → P1；旧年因 raw 变化进 R → P2。

### 2.10 提交顺序、pending 日志与备份
- 顺序（审查 P2-5、P2-9；**C12**）：
  1. 写 tmp（§2.12b O_EXCL），fsync 文件；
  2. 原子写 `daily_basic_full_tushare_manifest.pending.json`（{prev_sha, new_sha, build...}），fsync 目录；
  3. 备份：`os.link(dest, bak_dir/daily_basic_full_tushare.<YYYYMMDD_HHMMSS>.parquet)` —— **文件名精确到秒**（`%Y%m%d_%H%M%S`），避免同一分钟内两次运行 os.link 撞名（C12）。data/ 与 backups/ 同文件系统（st_dev=65040）。os.link 失败（含跨 FS）→ **不提交**，走回滚：若本步已建出链接，则删掉本次新建链接，并核对链接的 inode 与成品相同后才 unlink；失败则报 P1。
  4. `os.replace(tmp, dest)`，fsync 目录；
  5. `os.replace(pending, manifest)`；
  6. 写 status（代码 L247–283 已原子）；
  7. 提交成功后才 prune 备份（keep=5），且不删本次刚建的备份。
- **C12 额外约束**：
  - 第 3 步之后、第 4 步之前失败时，新建链接与现役成品共用 inode；回滚必须撤回该链接（见上）。
  - **成品只能用 os.replace 替换**；任何工具（含恢复脚本）都不许对成品路径做原地写（copy2 写到已有路径会同时改坏硬链接备份）。
- 第 4 步之后、第 5/6 步失败 → 退出 30（DB_INCR_COMMIT_PARTIAL），P1；下次启动按 pending 分支处理。
- **取证备份**：1136 与 1137_dupbug 已于 2026-10-25 00:15 ET 硬链接到 `backups/valuation_pinned/`（决定 (a) 已完成，见文首）。正常 prune 的 glob 不覆盖该目录；v3.1 不再要求 NO_PRUNE，也不再把移动取证列为待办。

### 2.10b 启动顺序：pending → STALE_TMP → 前置（C11）
- **C11**：每次进入增量函数，严格按此顺序：
  1. **pending 恢复**（若存在 pending 文件）：
     - 成品 sha == pending.new_sha → 补完 §2.10 第 5、6、7 步，报 P2；
     - 成品 sha == pending.prev_sha → pending 移到 `_quarantine/`（移动不删），报 P2；
     - 两者都不等 → 退出 31（DB_INCR_PENDING_CONFLICT），P1。
  2. **STALE_TMP 检查**：若 tmp 路径已存在 → 退出 21（DB_INCR_STALE_TMP）。
  3. **前置检查**（§2.7 / §2.13 / §5.4）：20 / 26 / 28 等。
- 禁止先做前置再处理 pending：否则「成品已换、manifest 未换」会被误判为退出 20，而不是按 pending 补完。
- **失败回滚时**：若成品 sha 仍等于本次 prev_sha（成品未变），由**本次运行自己**把本次写的 pending 移到 `_quarantine/`，不留给下一晚。

### 2.11 manifest 与 status
- 保留现有全部键；rows、instruments、date_min、date_max 按**全表**算；instruments 拷贝年从每个 row group 取并集（审查 P2-7）。
- 新增字段只写 manifest.build：mode、rebuilt_years、copied_years、rows_by_year、row_groups_by_year、prev_sha256、new_sha256、transform_sha、**runtime_versions**、raw_inventory、peak_vmhwm_kb、phase_rss_kb、history_diff_rows、history_diff_by_year、history_diff_report、backup_path。
- status 只保留代码 L269–278 原有键，最多加 manifest_path。新字段不进 status（审查 P2-6）。

### 2.12 信号与回滚（C2、C5）
- 入口装 SIGTERM 与 SIGHUP 的 handler，转成 `DbIncrSignal(signum)`，走统一回滚（审查 P1-5）。
- **C5**：`except` **一进入**，先把 SIGTERM 和 SIGHUP 设为 `signal.SIG_IGN`，再关 writer、按 inode 删 tmp、处理 pending（§2.10b）；清理完成后再按 C2 退出。否则驱动在 TERM_WAIT_S=10 内二次发 TERM 会打断回滚，tmp 残留。
- 回滚时只有 tmp 存在且 `(st_dev, st_ino)` 与创建时记录相同才 unlink；否则不删，报 P1。旧成品、manifest、status、既有备份都不动。硬链接撤回见 §2.10 / C12。
- **C2 / 决定 (b)**：
  - **SIGTERM**：回滚完成后，恢复默认处理并对自身重发 SIGTERM，使父进程看到退出码 **-15**；码表保留 -15（SIGNAL_TERM）。
  - **SIGHUP**：回滚完成后，**不再**给自己重发信号；直接以退出码 **32**（DB_INCR_SIGNAL_HUP）返回。码表**删除** -1 那一行。
- SIGKILL 无法处理：tmp 残留 → 下一晚退出 21；人工移到 `_quarantine/`（移动不删），单独签 .ok。

### 2.12b tmp 创建：O_EXCL + 立即记 inode（C6）
- **C6**：创建 tmp 时用 `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)`（或等价），**立刻** `fstat` 记下 `(st_dev, st_ino)`，再把该 fd / 文件对象交给 `ParquetWriter`。
- 这样消除「exists 检查与创建之间的竞态」，以及「已创建但尚未记 inode」的窗口（复审 C6）。若 O_EXCL 因文件已存在而失败 → 按 STALE_TMP（21）处理（与启动顺序一致时不应走到这里；若走到说明竞态，仍 21）。

### 2.13 end 规则
- end < 上一版 date_max → 退出 26（DB_INCR_END_BEFORE_PREV），不截断（审查 P2-12）。
- end 年无原始文件 → 退出 20（DB_INCR_PRECOND）。

### 2.14 年份切换（2027-01）
- 2027 年 1 月：R = {2026, 2027}，C = 2014..2025；2 月起 R = {2027}。依赖 cal_2027 与 2027 原始文件，未就绪按 §2.13 清楚失败。

### 2.15 退出码表（写进代码和回执；C2）
- 理由同 v3：nightly_update 把 rc∈(0,2) 当 ok、rc==3 当 partial。新增码全部 ≥20；**2 和 3 永不使用**。

| 退出码 | reason_code | 含义 |
|---|---|---|
| 0 | OK | 成功 |
| 1 | EXCEPTION | 未分类异常（未捕获） |
| 20 | DB_INCR_PRECOND | 前置不满足：成品 sha ≠ manifest.build.new_sha256（首晚对基线）、schema 不符、row group 跨年、rows_by_year 不符、end 年无原始文件、新表+过时 manifest 未重新定基线（A18）等 |
| 21 | DB_INCR_STALE_TMP | 启动时已有残留 tmp |
| 22 | DB_INCR_RSS_SELF_ABORT | 检查点 VmRSS 或 VmHWM > QL_DB_RSS_ABORT_KB |
| 23 | DB_INCR_OLDYEAR_DIFF | 写后回读不一致 |
| 24 | DB_INCR_DUPKEY / DB_INCR_DATE_MISMATCH | 跨文件重复键、文件 trade_date 与文件名不符、或 history_diff 内重复键 ValueError（D3） |
| 25 | DB_INCR_TOO_MANY_YEARS | 因 raw 变化加进 R 的旧年超过 2 个 |
| 26 | DB_INCR_END_BEFORE_PREV | end 早于上一版 date_max |
| 27 | DB_INCR_RAW_TMP | R 年原始目录有 *.tmp.parquet |
| 28 | DB_INCR_TRANSFORM_CHANGED | transform_sha 或 runtime_versions 与上一版不同 |
| 30 | DB_INCR_COMMIT_PARTIAL | 成品已替换但 manifest/status 未写成，P1 |
| 31 | DB_INCR_PENDING_CONFLICT | pending 的 prev_sha 与 new_sha 都与成品不等，P1（决定 (b) 接受） |
| 32 | DB_INCR_SIGNAL_HUP | 收到 SIGHUP，已回滚后以本码退出（**决定 (b)**；不用 -1） |
| -15 | SIGNAL_TERM | 收到 SIGTERM，已回滚后重发信号退出 |

- **已删除**：`-1 / SIGNAL_HUP`（C2）。
- 任何非 0：nightly 记 fail，驱动 FAILED，不重试，不写 DONE；成品/manifest/旧备份不动（30/31 除外的语义见审查第四节第 3 条）。30、31 报 P1。A16：SIGHUP 场景退出码必须是 32，不是 -1，也不是 2 或 3。

### 2.16 DB_INCR_RESULT 行
- 字段：mode、rebuilt_years、copied_years、prev_sha256、new_sha256、transform_sha、runtime_versions、rows、rows_by_year、peak_vmhwm_kb、phase_rss_kb、history_diff_rows、history_diff_by_year、raw_inventory_changed_years、backup_path、exit_code、reason_code。驱动再附 rss_max_one、rss_max_sum。解析不到按 FAILED。

## 3. 内存（引 Arch 探针；验收以 selftest 实测为准）

- 探针来源：审查 L15、L46–60、L250–260（合成数据，只能判断量级）。
- 要点：导入 pandas 后基线约 105 MB；单 row group 整读 +400–500 MB；读两次约 840–860 MB（已禁止）；iter_batches 回读约 +140 MB；mimalloc 下 VmHWM 不回落，以 VmHWM 为准。
- 验收线（S2/S3）：单进程 VmHWM ≤ 1,000,000 kB；外部树合计 ≤ 1,100,000 kB；自检 QL_DB_RSS_ABORT_KB = 1,200,000（VmRSS **或** VmHWM 任一超过即退出 22）。
- 驱动外层：树 1,484,800 kB、单进程 1,536,000 kB。
- 真实首晚：VmHWM > 1,000,000 → P2；> 1,200,000 → 自检中止 FAILED。
- **ref_build 同线**：见 §4.1b（C9 / A13）。

## 4. 对账

### 4.1 参考重建器 ref_build（基准）
- 不用现成品，也不跑新全量（审查 P1-4）。
- 规格：逻辑 = 外提后的模块级 `_one` + L372–374 拼接去重，但每次一个自然月、每进程一年；只输出逐年 hash 与计数，不写成品。路径传参，带 §3 自检。
- 等价性论证（同 v3）：去重键含 trade_date → 重复不跨月；concat 保文件序 → 月内 keep="last" 与整年相同；不依赖「每文件只含一日」。
- 用途：合成增量对账（A4）；影子 2014..Y 对账；每周复核（§4.3）；**以及「新表+过时 manifest」时重新定基线（C8 / 决定 (e)）**。

### 4.1b ref_build 内存验收（C9 / A13）
- **C9**：ref_build 在合成数据上处理最大一年（1,313,182 行）时，VmHWM ≤ 1,000,000 kB，记为 **A13**。
- 影子对账与每周复核均按此线执行；超线不得签 .ok。

### 4.2 对账规格（审查第三节；D4）
1. 逐年行数，以及 row group 行数序列。
2. **year_sorted_content_col_hashes**（内容 hash）：每年每列一个 sha256；先喂列头；行按 (trade_date, ts_code) 排序。规范化同审查 L313–318（double / timestamp us / large_string / bool；每批 ≤65,536）。
3. **file_physical_row_hash**（物理行序 hash）：按文件物理顺序再算一次全行 hash，上线前必须相等。
4. 严格表示：每列每年 null 数与 NaN 数两边相等。
5. 不变量计数每年为 0（available_at 差 18h、source、quality_status、promotion_approved、row group 跨年个数）。
6. schema（check_metadata=False）与 pandas dtype 字符串一致。
7. 文件 sha 只记录，不作一致标准。
8. 不一致时按月定位，每类最多 100 样例键。
- **D4**：基线文件里的「每年列 hash」= 本条的 year_sorted_content_col_hashes；写后回读用 row_group_physical_col_hashes；禁止混名。

### 4.3 每周复核与门禁
- 每周日空档，ref_build 对 2014..Y 与现行成品按 §4.2 对账，单独签 .ok：只读，输出 /tmp，单进程逐年，不与重任务重叠。影子运行同样单独签 .ok。

## 5. 遗留盘点与引导基线（原 10-19 / 10-20 预案；窗口已过期，流程仍适用）

### 5.1 旧代码可能留下的现场（审查 P1-7）
- 停在年度构建：`_daily_basic_parts_<stamp>/`；且 L311–313 可能已按 keep=5 删掉最旧备份。
- 停在 L390–392：残留 tmp → 增量 STALE_TMP（21）。
- 停在 L393 之后：成品已换、manifest 仍旧（「新表配过时 manifest」）；eng_panels 会重算 status 使其看起来正常。

### 5.2 只读盘点（Data 执行；C8 时序）
- **C8**：只读盘点必须在 Arch 指定空档执行，且当时**没有其他真实数据进程在跑**；**命令清单先交 Arch 看**后再执行。
- 只做 `read_metadata`、`stat`、文件 sha256 读取，**不读数据行**（复审 C8）。
- 列出并取 sha：tmp 是否存在（inode/size/mtime）；`_daily_basic_parts_*`；成品 sha 与 manifest、status 三者是否一致；backups 清单；原始目录 `*.tmp.parquet`。
- 判定「新表配过时 manifest」：成品 read_metadata 行数/最大 trade_date 与 manifest 的 rows/date_max 不符，或成品 mtime 晚于 manifest built_at。
- **D1**：盘点回执写到 `docs/v2/audit/` 时，用 Python 显式 UTF-8 + LF 原子写（先 .tmp 再 os.replace），禁止 heredoc。
- 发现的残留只列出；隔离（移 `_quarantine/`，移动不删）须单独签 .ok。

### 5.3 引导基线（单独签 .ok，一步）
- **C8 / 决定 (e)**：废止 v3「或已由 Arch 裁定」把过时 manifest 当依据的写法。遇到「新表配过时 manifest」时，**表与 manifest 两边都不信**；过时 manifest 不能作为任何前置依据。基线**只能**由本小节的 ref_build 全年份对账产生；对账不一致 → **不写基线、不启用增量**（A18：增量拒绝启动，退出 20，直到 ref_build 重新定基线）。
- 前提：§5.2 盘点无未处理残留；若存在「新表+过时 manifest」，跳过「以任一方为准」，直接走 ref_build 重新定基线路径。
- 只读成品元数据 + §4.1 ref_build 对 2014..Y（真实原始文件，只读，输出 /tmp，空档，单进程逐年）。
- 原子写 `data/v2/valuation/daily_basic_full_tushare_build_baseline.json`：成品 sha、rows_by_year、row_groups_by_year、**year_sorted_content_col_hashes**（D4）、schema、transform_sha、runtime_versions、内容 sha 版 raw_inventory、ref_build 对账结果。
- ref_build 与现成品有差异 → 不写基线，列差异交 Arch 和主 Agent（A9）。

### 5.4 前置检查改为对 manifest
- 成品 sha == 上一版 manifest.build.new_sha256；首晚 == 基线文件成品 sha。
- status sha 只作旁证。
- 无合格基线 / 处于「新表+过时 manifest」未重定基线状态 → 退出 20（A18）。

## 6. 实施与门禁

### 6.1 顺序与启用条件（10-20 窗口已过期）
1. Data 交 **v3.1**（本文）；**Arch 确认 v3.1**（C1–C12 已写入）。
2. Eng 实现，代码 diff **逐条对应 C1–C12**；改代码前归档 tier1_materialize.py（e9c89a6c…）与 nightly_update.py（ec079d56…）到 `_recovery/data/daily_basic_incr_<stamp>/`，附 sha。
3. selftest .ok 与回执（§6.2；含 A12–A18）。
4. 只读盘点（§5.2）与必要隔离 .ok。
5. 引导基线 .ok + 影子分年对账（§5.3；A13）。
6. 新版驱动（新文件名；f99dd11a 不改）重钉 L66 与 L61；范围文件同步；**Arch 另签启用 .ok**（注释：增量模式、自检阈值、首晚 VmHWM 处置、SIGHUP=32）。
- **启用条件**：Arch 确认 v3.1 + Eng diff 对 C1–C12 + 另签 .ok。**未满足则继续旧全量路径**；内存超限停树记 P2，不是事故，不重试。
- **实现/运行仍须另签 Arch .ok**；本文只定设计，不授权写真实数据或改代码。

### 6.2 selftest 与隔离
- .ok：scope=selftest，allow_real_data=false，out_dir 在 /tmp；开头 enforce(modes=["selftest"])。
- 隔离（P1-8）：路径传参；realpath 均以 /tmp/ 开头；测试前后真实成品/manifest/status/backups 清单 sha 不变（A7）。
- 场景：审查 S1–S13，外加 A12–A18 所需场景（S5 强化见 §6.2b；SIGHUP→32 为 A16；copy2 快筛为 A17；新表+过时 manifest 为 A18）。
- 采样与校准同 v3 / 审查 2.4。

### 6.2b S5 TERM 时限（C7 / A15）
- **C7**：驱动 stop_tree 发 TERM 后只等 10 秒就 KILL；Python handler 须等 pyarrow C 调用返回。S5 须在 **拷贝、构建、回读、diff、提交** 五个阶段各随机发一次 TERM。
- 验收：**从 TERM 到进程退出 ≤5 秒**，回执写每阶段实测值。
- **A15**：五阶段均 ≤5 s，且回滚完整——tmp 已删；本次新建硬链接已撤回或从未建立；pending 已按 §2.10b 处理（C5、C6、C7、C11、C12）。

## 7. 未决 / 已决项

### 7.1 已由 Arch 决定（不再待办）
- (a) BACKUP_PIN：**已完成**（2026-10-25 00:15 ET；回执 sha256 15905d602e0df9041f50248dccfdea513d43284dde48fc23a630bcd3fac48cf1；nlink=2）。不用 NO_PRUNE。
- (b) 退出码 31 接受；SIGHUP = **32**（DB_INCR_SIGNAL_HUP）；码表删 -1。
- (c) transform_sha = AST dump（去 docstring）+ 常量表（细节实现 Eng 提、Arch 钉）。
- (d) 内容 sha 耗时分支 + 快筛含 ctime + 强制全量标记（§2.2）。
- (e) 新表+过时 manifest → 两边都不信，须 ref_build（§5.3）。
- (f) eng_panels L151–152 → A12。
- (g) 正则 → C1。

### 7.2 仍须 Eng/Arch 钉死的实现细节（不挡 v3.1 确认，但挡启用 .ok）
1. AST 规范化的具体代码（函数集、dump 选项、字节序）—— Eng 提案，Arch 审定后写入代码注释与本节修订（或 v3.2 补丁段）。
2. `raw_touched` 标记的路径与清除权属（须进入恢复/回补工具的 .ok 模板）。
3. 新版驱动文件名与冻结清单更新（Arch 签）。

## 8. 代码草图（只作文档；未应用到任何代码；以 Eng 实现、Arch 审查为准）

```python
class DbIncrError(Exception):
    def __init__(self, code, reason):
        super().__init__(reason); self.code, self.reason = code, reason

class DbIncrSignal(BaseException):
    def __init__(self, signum): self.signum = signum

def _on_signal(signum, frame):
    raise DbIncrSignal(signum)

def materialize_daily_basic_incremental(*, end, raw_dir, dest, manifest, status, bak_dir, diff_dir, start="20140101"):
    import signal, os, pyarrow.parquet as pq
    old = {s: signal.signal(s, _on_signal) for s in (signal.SIGTERM, signal.SIGHUP)}
    tmp = dest.with_suffix(".tmp.parquet"); tmp_id = None; w = None; fd = None
    res = {"mode": "incremental"}; pending_written = False
    try:
        _recover_pending(dest, manifest, status, bak_dir)   # C11：先 pending
        if tmp.exists():
            raise DbIncrError(21, "DB_INCR_STALE_TMP")      # C11：再 STALE_TMP
        prev = _precheck(dest, manifest, end)               # C11：最后前置（20/26/28）
        R = _rebuild_years(end, prev, raw_dir)              # 2.2：内容 sha / 快筛+ctime；>2 -> 25；*.tmp -> 27
        # C6：O_EXCL 创建并立刻记 inode
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        st = os.fstat(fd); tmp_id = (st.st_dev, st.st_ino)
        w = pq.ParquetWriter(os.fdopen(fd, "wb"), SCHEMA_WITH_PREV_META, compression="snappy"); fd = None
        rec = []
        for y in range(int(start[:4]), int(end[:4]) + 1):
            if y in R: _build_year(y, raw_dir, end, w, rec, res)  # 2.3 C1 正则 + 2.5 切片
            else: _copy_year(y, prev, w, rec, res)                # 2.4 单驻留
        w.close(); w = None
        _verify_readback(tmp, rec)                          # 2.8；不一致 -> 23
        diff = _history_diff_scan(dest, tmp, R, diff_dir)   # 2.9；DupKey -> 24
        _commit(tmp, dest, manifest, status, bak_dir, res, diff)  # 2.10 / C12：秒级名；link 失败撤回
        return _result(res, 0, "OK")
    except BaseException as e:
        # C5：一进入 except 先屏蔽信号，防止驱动二次 TERM 打断回滚
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        if w is not None:
            try: w.close()
            except Exception: pass
        if fd is not None:
            try: os.close(fd)
            except Exception: pass
        if tmp_id is not None and tmp.exists():
            s2 = os.stat(tmp)
            if (s2.st_dev, s2.st_ino) == tmp_id:
                tmp.unlink()
        _rollback_backup_link_if_needed(res)                # C12
        _quarantine_pending_if_product_unchanged(dest, res) # C11
        if isinstance(e, DbIncrSignal):
            _result(res, 32 if e.signum == signal.SIGHUP else -e.signum,
                    "DB_INCR_SIGNAL_HUP" if e.signum == signal.SIGHUP else "SIGNAL_TERM")
            if e.signum == signal.SIGTERM:
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
                os.kill(os.getpid(), signal.SIGTERM)        # C2：TERM 重发 -> -15
            return 32                                       # C2：HUP 直接 32，不重发
        if isinstance(e, DbIncrError):
            return _result(res, e.code, e.reason)
        _result(res, 1, "EXCEPTION"); raise
    finally:
        for s, h in old.items():
            try: signal.signal(s, h)
            except Exception: pass
```
- `_result` 打印唯一一行 DB_INCR_RESULT（§2.16）。`_guard` 在各检查点调用，超线抛 DbIncrError(22,…)。`_commit` 第 4 步后失败 → 30；pending 冲突 → 31。文件名匹配用 `^\d{8}\.parquet$`（C1）。

## 9. 验收清单

### 9.1 原 A1–A11（同审查第七节，口径不缩）
- A1：设计（现为 v3.1）与代码 diff 经 Arch 审；改动前归档附 sha。
- A2：selftest .ok；S1–S13 通过；回执带生成器 sha。
- A3：S2/S3 VmHWM ≤ 1,000,000 kB；树合计 ≤ 1,100,000 kB。
- A4：合成上增量与 ref_build 按 §4.2 逐年完全一致。
- A5：S4 退出 22；S5 见 A15；结束后 tmp 已删，成品/manifest/status/备份不变。
- A6：S6–S11、S13 退出码与码表一致；无 2 或 3。
- A7：selftest 前后真实文件 sha 不变。
- A8：盘点回执已交；残留隔离（移动不删）单独 .ok。
- A9：引导基线与影子对账；差异列明交 Arch/主 Agent。
- A10：新驱动钉值与范围文件更新；启用 .ok 由 Arch 签发。
- A11：首晚回执含 DB_INCR_RESULT 全字段。

### 9.2 增补 A12–A18（复审第六节）
- **A12**：合成数据上实测 eng_daily_panels L151–152 的 VmHWM（决定 (f)）；回执写实测值；>1,000,000 kB 报 P2 并另出改法。
- **A13**：ref_build 最大年 VmHWM ≤ 1,000,000 kB（C9）。
- **A14**：外提后 `_one` 与旧闭包在合成文件上逐文件 22 列 hash 一致（C4）。
- **A15**：S5 五阶段 TERM→退出均 ≤5 s，且回滚完整（C5、C6、C7、C11、C12）。
- **A16**：SIGHUP 场景退出码 = **32**，不是 -1，也不是 2 或 3（C2）。
- **A17**：合成环境用 copy2 把旧年原始文件覆盖成同样大小、同样 mtime 的不同内容，快筛（含 ctime）能发现并将该年加进 R（C10）。
- **A18**：「新表配过时 manifest」：不写基线，增量拒绝启动，退出 20，直到 ref_build 重新定基线（C8）。

## 10. P3 建议（D1–D4；建议不挡开工，但仍写入）

| ID | 内容 | 落点 |
|---|---|---|
| D1 | 盘点回执用 Python UTF-8+LF 原子写，不用 heredoc | §5.2 |
| D2 | 对照表「v3 Lxx」类引用按 v3.1 新行号整体复核 | 文首 R1–R13 表与 C1–C12 表 |
| D3 | history_diff 重复键 ValueError → 退出 24 | §2.3；§2.9；码表 24 |
| D4 | 基线「每年列 hash」= §4.2 排序内容 hash；与写后回读物理序 hash 分名 | §2.8；§4.2；§5.3 |

## 附：本文依据
- 基线 v3：13fd86b67ba6c8d074aba08d8a3ad3cac93fd7ebbae9acbe41547e80c15d0aab（未动）。
- Arch 审查（含复审）：48a64380682e593adb1d3386ae92126df4173e31c61b7699ff6ce8f7b06fe18a。
- BACKUP_PIN 回执：15905d602e0df9041f50248dccfdea513d43284dde48fc23a630bcd3fac48cf1。
- 代码（只读，同 v3 附）：tier1_materialize.py e9c89a6c…；nightly_update.py ec079d56…；eng_daily_panels.py；run_nightly_v1.py f99dd11a…。

## v3.1 变更记录
- 写于 2026-10-25T00:24:44-0400；由 v3 复制改写，闭合 Arch 复审 C1–C12 与决定 (a)–(g)，纳入 A12–A18 与 D1–D4。
- v3 文件本身未动（sha 见文首）。
- 启用条件改为「Arch 确认 v3.1 + Eng diff 对 C1–C12 + 另签 .ok」；10-20 窗口已过期。
- 实现/运行仍须另签 Arch .ok；live=false。

（完）
