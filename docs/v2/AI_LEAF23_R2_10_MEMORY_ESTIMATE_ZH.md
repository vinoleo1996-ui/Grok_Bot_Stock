# AI：叶23 r2.10 eval 峰值内存估算（拆 universe 后每进程）

- 写入：AI 执行代理，2026-10-18 ET。没有运行任何项目代码（不 import research.* / quantlab.*）。
- 方法：自写的独立脚本 /tmp/l23_r210_est/est.py（只用 numpy/pandas/pyarrow + 标准库），按 r2.9 / r2.10 的 eval 读法和算法，原样复现其中占内存的部分，在真实文件上只读运行。复现的部分：authorize 的整文件 sha 和 build_version 读取、A/G 读入、PX 读入和 rr pivot、pool_benchmarks 2018–2026 逐年递推及其 idx×U 帧、FE.rets 收益缓存、5 个书的 pick 和 book_ret、分位数 15 次 book_ret、叶20 重叠。每个检查点读 /proc/self/status 的 VmRSS 和 VmHWM。脚本自带 1450000 kB 自杀线，低于 1.5GB 红线。
- 运行环境：/workspace/qlvenv/bin/python 3.12.14，nice -n 10，串行，同时没有其他研究进程。
- 输入：真实 r2.9 fund/build 产物 output/ai_factory/leaf23_sue_desens_cs/alpha_* 和 gate_*（只读）、panel_cache_v2_resumefix、mask、delisted、ETF、leaf20 文件。日志在 /tmp/l23_r210_est/*.log。

## 1. 校准
- r2.9 实跑（stage 04，/tmp/l23run_r29/s04_stdout.log）：`HILIQ eval done rss=1596`（ru_maxrss，约 1596 MB），包装采样 VmHWM 最大 1704112 kB，之后在 FULLA 段被杀。
- 复现脚本按 r2.9 写法跑 HILIQ（r29_HILIQ.log）：在「pb 帧仍在内存时读 FE.rets」这一步 VmHWM 达到 1473688 kB，触发 1.45GB 自杀线。实跑的 1596 MB 比它最多高 **≈122 MB**。下面各估计都把这 122 MB 作为保守余量加上。复现脚本没包含 capadv 书、手数取整、json 等，这部分开销由余量覆盖。
- 关键发现（probe.py）：PX 本身在内存里只有 124 MB（2,876,562 行，ret/close 存盘就是 float32），rr pivot 只有 11 MB（580×5222，float32）。但做完 pivot 后 RSS 到 676 MB；gc 加 pyarrow `release_unused()` 加 glibc `malloc_trim(0)` 后回落到 383 MB。**内存主要被分配器占着不还**（pyarrow 用 mimalloc 池），真正存活的数据帧并不大。

## 2. 帧尺寸（真实数据）
| 对象 | 规模 |
|---|---|
| idx × U（pool_benchmarks 输出帧） | 580 × 5467；float64 每帧 25.4 MB，bool 每帧 3.2 MB；同时存活约 10–12 帧（S/MV/VAL/LMV/S_dd/MV_dd/Mp/wv/Mpo/wvo/Mp2/wv2/RR） |
| pb 每年帧 | 约 244 × 5467，float64 每帧 10.7 MB；2024–2026 三年的 6 类 parts 共约 190 MB |
| A / G | HILIQ 1,618,456 / 1,628,867 行；FULLA 2,698,355 / 2,719,070 行（读入后 RSS 分别 +≈145 / +≈240 MB） |
| PX（r2.10 列：date/instrument/ret/close/ind/is_resume_day/carry） | 2,876,562 行，124 MB |
| FE 收益缓存（ret、ret_on 两张 pivot，float32） | 约 2 × 13 MB |
| 叶20 α（重叠步） | 全量 2,744,991 / 5,646,586 行 → r2.10 只读首个 W20 日期之后：1,163,959 / 1,881,849 行，merge 结果逐行相同（已核） |

## 3. 结果（VmHWM，MB）
| 写法 | HILIQ | FULLA | 说明 |
|---|---|---|---|
| r2.9（单进程，原写法） | ≥1474（被 1.45GB 线杀） | — | 实跑 1596 后在 FULLA 被杀 |
| r2.10 v1：拆分 + 列裁剪 + 及时 del | 1377 | — | 不够 |
| v2：再加 trim()（gc + pool.release_unused + malloc_trim） | 1184 | — | |
| v3：再把 FE.rets 提到 eval 开头加载一次并保留缓存（原代码每本书后清缓存重读）、N4 行业 pivot 提前 | 1062 | 1285 | FULLA 峰值落在 pick_book 每次全量 A.merge(G) |
| **v4 = r2.10 定稿**：pick_book 只喂调仓日行（byd 本来只用调仓日，选股逐行相同） | **1062** | **1159** | |
| **v4 + 122 MB 保守余量** | **≈1184** | **≈1281** | 两个进程都 < 1.3GB 目标 |
| merge 步 | 只读两份 json，约 authorize 基线 ≈200–420 | | |

- 各段峰值（v4）：authorize 约 420；FE.rets 预载 约 760；PX + rr pivot 约 1000（HILIQ）/ 1116（FULLA）；pool_benchmarks 2024–2026 年 约 1062 / 1159；之后各段都低于前面的峰值。
- 余下最大的瞬时峰值是 PX pivot（约 +400 MB 临时分配）和 pool_benchmarks 后三年。如果还要再压，可选（**本版未做**，需 Arch 定）：用 PX.pivot 代替 pivot_table（已核 (date, instrument) 无重复，值相同）；pool_benchmarks 的 pr 只读需要的行。

## 4. r2.10 已纳入的降内存改动（都不改数值）
1. (a) eval 按 universe 拆进程，merge 单独一步。
2. (b) 列裁剪：PX 去掉 logmv 和 <col>（eval 从没用过）；叶20 α 只读首个 W20 日期之后的行；pick_book 只喂调仓日的 A/G 行。不做任何 dtype 下转。
3. (c) pool_benchmarks 逐年及时 del（pr 在取 seed 后立刻 del；A/B/sus 在 S/MV 算完后 del；年末 del 并 trim）；cat 逐键 pop；Mpo/wvo/Mp2/wv2 读完即弃；trim() 在各段末执行；FE 收益缓存一次加载并保留（数据和键都相同）。
4. (d) 看门狗同时查 VmRSS 和 VmHWM；pool_benchmarks 每年末、每个 universe 的 eval 末、merge 末各做一次 peak_check（同时看 VmHWM 和 ru_maxrss）。
- 1536000 kB 上限不变。trim() 和缓存保留这两项属于 Arch (c) 范围外的补充，理由见上表的数字，请 Arch 一并审。
