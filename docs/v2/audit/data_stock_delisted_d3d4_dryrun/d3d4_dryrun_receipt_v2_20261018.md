# D3D4 dry-run 回执 v2（build_stock_delisted_v2.py，v2.ok）
- 时间：2026-10-18 02:18:41–02:18:43 EDT；执行人：QuantLab Data；单进程，live=false，promotion=false
- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/build_stock_delisted_v2.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok`
  - 没有加 --execute；用法与脚本 docstring 一致。
- 外层监视：/tmp/d34_mon.py，用完已删除。每秒读一次 VmRSS，超过 1450MB 发 SIGTERM；跑完读 getrusage。
- 运行前自查（02:18:38）：
  - .ok sha 为 cc04d83d…，未过期。
  - 7 个文件与快照 SHA256SUMS 一致（7/7）。
  - MemAvailable 约 11.5 GB。
  - 门禁禁止名单（research/、daily_pull、tier1_pull、tier1_materialize、adj_factor、bars_materialize）没有命中。
- 运行期间 nightly tier3 仍在跑：PID 142531（nightly_update.py --date 20261015 --steps tier3，01:47:28 启动，父进程为 94403）和 142545（tier3_daily_snapshot.py），整个运行期间都存活。dry-run 没有受影响。
- stdout：d3d4_dryrun_stdout_20261018_v2.txt。
  - GATE_PASS step=D3D4_stock_delisted mode=dryrun ok_sha256=cc04d83d…
  - 末行为 "DRY-RUN PASS: nothing written"，exit 0。
- 没有出现 VOID，也没有触发不变式。

## 1. 统计（脚本自报）
| 项目 | 值 |
|---|---|
| 行数 / v1 行数 | 339 / 339，v1 列完全相等（v1_columns_equal=true） |
| 退市整理期 0 天：v1 → v2 | 61 → 0，已全部修正（D-4） |
| 进入退市整理期：v1 → v2 | 89 → 151 |
| face_value_flag=True | 93 |
| rss_mb | 394 |

### 无法从 stdout 核对的三项
- 第 95 行在打印时把 recategorised、unknown_needs_source、manual_override 三个字段替换成了 "..."，这是设计如此，用来控制 dry-run 输出长度，完整内容只写进 execute 的 manifest。因此：
  - **面值退市 4 只（600297/002505/000861/002509）是否改归为"强制退市(面值退市)"**：dry-run 无法确认，留到 execute 时用 manifest.stats.recategorised 核对。face_value_flag=93 是全体中满足"20 个交易日收盘价都低于 1 元"的标记数，不是改归类的数目。
  - **UNKNOWN 56 只**：dry-run 无法确认个数，留到 execute 时用 unknown_needs_source 核对。
  - **manual_override**：只能由代码静态确认。代码第 37 行只覆盖 002509.SZ，delist_period_start=20200604，ann_date=20200527，override_source_verified=True。
- 本轮没有改代码，也没有额外读数据。

## 2. 资源与零写入
- 峰值 RSS：getrusage 测得 403,872 KB（约 394 MB）；VmRSS 监视最大 341,136 KB（运行只有约 2 秒，1 秒采样会漏掉峰值）；脚本自报 394。没有发 SIGTERM。
- 零写入确认：
  - 四个目标路径都不存在（4/4 报 No such file）。
  - .ok 之后 output/、data/ 新增的 staging/VOID 文件为 0 个。
  - scripts/fix_sd1 下的 __pycache__ 为 0 个。
- 至此四步 dry-run（D1a、D1b、D2、D3D4）全部完成。
