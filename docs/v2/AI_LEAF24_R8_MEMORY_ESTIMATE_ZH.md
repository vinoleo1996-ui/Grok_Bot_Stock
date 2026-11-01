# AI：叶24 r8 各阶段峰值内存估算（叶24 还没运行过）

- 写入：AI 执行代理，2026-10-18 ET。没有运行任何项目代码；用的是独立脚本 /tmp/l23_r210_est/est24.py（eval）和 est24b.py（build），只用 numpy/pandas/pyarrow + 标准库，在真实文件上只读运行，自带 1450000 kB 自杀线，nice -n 10，串行。
- 输入：panel_cache_v2_resumefix、mask、delisted、ETF、leaf18 和 leaf18v 的 X2 α 与权重文件（真实文件）。
- 叶24 的 alpha/gate 产物还不存在，所以 eval 用叶23 r2.9 的 alpha/gate 文件当行数代理：同池、同日期，HILIQ 1.62M 行、FULLA 2.70M 行；叶24 的 lu_share/fin 两列用宽度相同的列（float32/int8）替代。
- 校准余量沿用叶23 的数（实跑 1596 MB 对复现 ≥1474 MB，最多差 122 MB）。

## 1. eval（r8 仍是单进程跑 HILIQ+FULLA，和叶23 r2.9 结构相同）
| 写法 | HILIQ | FULLA |
|---|---|---|
| r8 原写法（单进程；每本书后清 FE 缓存重读；PX 带 logmv/col） | **≥1450，被杀**（HILIQ 分位数段，VmHWM 1450604 kB） | 跑不到 |
| 叶23 r2.10 写法（拆分 + 列裁剪 + trim + 缓存保留，作为提议） | 1013（+余量 ≈1135） | 1262（+余量 ≈1384） |

- **结论：叶24 r8 的 eval 按现结构几乎一定会超 1.5GB**，与叶23 r2.9 同样会在 eval 被看门狗杀掉。建议 r9 采用和叶23 r2.10 相同的改法：
  - `--stage eval --uni` 拆两个进程，加 `--stage merge`，元数据链对齐；
  - PX 列裁剪（需逐列核对叶24 eval 实际用到哪些列）；
  - pool_benchmarks 逐年及时 del，并在各段末 trim；
  - FE.rets 只加载一次并保留缓存；
  - pick_book 只喂调仓日的行。
- 拆分后 FULLA 仍有约 1.26–1.38GB 的风险。峰值在叶18/18v 重叠步：Al 全量 2,821,833 行的 x2 文件，两份先后读入。建议在 r9 里再把 Al 只读调仓日的行（Jaccard 只在调仓日用 Wls），预计可降 150–200 MB。

## 2. build（每个 universe 一个进程；r8 未改 build 逻辑，没有 trim）
| 年 | HILIQ VmHWM | FULLA VmHWM | 峰值所在 |
|---|---|---|---|
| 2024 | 893 | 1136 | Q/ER 残差和 pivot |
| 2025 | 1063 | **1320** | Q/ER（FULLA Q 2,006,919 行） |
| 2026 | 1063 | 1320 | — |
| 整个进程 | **1063（+余量 ≈1185）** | **1320（+余量 ≈1440）** | |

- 复现没有包含第二个逐日 OLS 循环，只用代理 AL/GL；这部分开销很小。
- 两年之间 RSS 不回落（FULLA 停在约 1050–1200 MB），同样是分配器占着不还。
- **建议 r9**：build 每年末加 trim()（gc + pyarrow pool.release_unused + malloc_trim），并在 Q/ER 算完后立即释放 Ee/Lu。按叶23 的经验预计可降 200–300 MB。r8 的看门狗现在同时查 VmHWM，年末还有 peak_check，超限会在年边界以 137 退出，不会悄悄越线。

## 3. r8 本版改动（只按 Arch P2）
- 看门狗同时查 VmRSS 和 VmHWM（> 1536000 kB 即 RSS_GUARD_KILL / os._exit(137)）。
- 新增 peak_check（同时看 VmHWM 和 ru_maxrss），调用点：build 每年末、pool_benchmarks 每年末、eval 每个 universe 末。
- 上限仍是 1536000 kB；其他逻辑没改。
- 以上 r9 建议（拆分、trim、列裁剪）都**没有**纳入 r8，请 Arch/主 Agent 定。
