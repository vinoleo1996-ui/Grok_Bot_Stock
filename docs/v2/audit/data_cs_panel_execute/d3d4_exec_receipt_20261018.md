# D3D4_stock_delisted execute 回执（EXECUTE_v1.ok，r6c 代码 b9674c8b）

- 执行人：QuantLab Data；单进程；live=false，promotion_approved=false
- 放行依据：`docs/v2/ARCH_DATA_SD1_EXEC_D2_REVIEW_ZH.md`（Arch 05:31:02 EDT 书面放行 D3D4，已通读）
- 时间（America/New_York）：T0=2026-10-18 05:32:05.685396523 EDT；结束 05:32:06.999594612 EDT；**exit 0**
- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/fix_sd1/build_stock_delisted_v2.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok --execute`
  - 参数依据脚本 usage：`--arch-ok PATH [--execute]`
  - 外层用 /usr/bin/python3 跑 subprocess，用 getrusage 测峰值

## 前置核对（05:31:45–05:32:05 EDT，全部满足）
- .ok sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52 ✓
  - signed_et 05:16:02 不在未来（date 为 05:31:57）
  - expires 10-19 16:00 未过
  - 不在 forbid_window 内
- 两个期望键都在 .ok 中 ✓
  - `expected_face_value_recategorised=000861.SZ,002505.SZ,002509.SZ,600297.SH`
  - `expected_unknown_needs_source_count=56`
  - allow_d3d4_expectation_keys=true；d3d4_expectations_mode=enforce_both_keys_in_execute
- pin 核对
  - 代码 7 项：工作区、`git show b9674c8b` 与 .ok 三处一致 ✓
  - 数据 15 项：与 .ok 一致 ✓
- scripts/fix_sd1 状态干净，没有 __pycache__ ✓（运行前后都检查过）
- 目标文件运行前都不存在 ✓
  - data/v2/ref/stock_delisted_v2.parquet 及其 .manifest.json、.receipt.json
  - staging 目录和 VOID 文件
- D2 收据 sha256=06d06a79… ✓
- MemAvailable 均 ≥ 2GB ✓
  - ps 留证时 11,114,812 kB
  - **运行前 11,245,200 kB**
  - **运行后 11,103,900 kB**
- 进程留证：`pre_d3d4_exec_ps_20261018.txt`（sha256=48f4f8cf1e3147f5351856c532036bf8dd4cb82b440a0046176fd37541f1798a）
  - 只读 /proc 判断进程状态，没有用 kill -0
  - 禁止的进程都不在运行 ✓
  - 94403 不存在 ✓
  - 94322 state=**T** ✓
  - 80415 server.py 是 Web 看板，Arch 已确认
- 运行后 94322 仍为 T。没有 CONT，也没有 kill；要等 Arch 书面确认后才能 CONT。

## 门禁与提交
```
RUN_CONDITION_MATCHES []
GATE_PASS step=D3D4_stock_delisted mode=execute ok_sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52
COMMITTED /workspace/QuantLab/data/v2/ref/stock_delisted_v2.parquet
```
- 没有 VOID；data/v2/ref 下没有 staging 或 VOID 残留。

## 两个期望键在 execute 中已强制执行
- 依据代码（脚本第 32 行和第 128–130 行）：
  - `EXPECT = C.parse_d3d4_expectations(KV, EXEC)`：execute 模式下缺任一个键，门禁就会在读取数据之前阻断。
  - 第 128–130 行：面值集合不等于 EXPECT["face"]，或者 UNKNOWN 数不等于 EXPECT["unknown_count"]，就会 ST.void。
- stdout 证据：D3D4_FACE_CHECK 行中 **`"expect_from_ok": {"face": ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"], "unknown_count": 56}`**。v4a dry-run 中这一项是 `{"face": null, "unknown_count": null}`。
- 实测与期望一致，所以没有 VOID：
  - face_value_recategorised_codes 实测为 ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"]，等于期望
  - `"unknown_vs_56": {"measured": 56, "diag": 56, "diff": 0}`，实测 56 等于期望 56
- 脚本没有单独打印"expectations checked"这类行。强制执行的证据就是上面三点：expect_from_ok 不为空、两项比较都相等、没有 VOID。
- D3D4_FACE_CHECK 原文：
```
D3D4_FACE_CHECK {"face_value_recategorised_codes": ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"], "face_minus_diag4": [], "diag4_minus_face": [], "face_windows": [{"code": "000861.SZ", "v1_cat": "疑似主动/吸收合并/私有化退市(退市前非ST)", "v2_cat": "强制退市(面值退市)", "period_start": null, "n_closes": 20, "win_start": "20240625", "win_end": "20240805", "win_max_close": 0.99, "face_flag": true}, {"code": "002505.SZ", "v1_cat": "疑似主动/吸收合并/私有化退市(退市前非ST)", "v2_cat": "强制退市(面值退市)", "period_start": null, "n_closes": 20, "win_start": "20240604", "win_end": "20240702", "win_max_close": 0.96, "face_flag": true}, {"code": "002509.SZ", "v1_cat": "疑似主动/吸收合并/私有化退市(退市前非ST)", "v2_cat": "强制退市(面值退市)", "period_start": "20200604", "n_closes": 20, "win_start": "20200409", "win_end": "20200511", "win_max_close": 0.99, "face_flag": true}, {"code": "600297.SH", "v1_cat": "疑似主动/吸收合并/私有化退市(退市前非ST)", "v2_cat": "强制退市(面值退市)", "period_start": null, "n_closes": 20, "win_start": "20240620", "win_end": "20240717", "win_max_close": 0.99, "face_flag": true}], "unknown_vs_56": {"measured": 56, "diag": 56, "diff": 0}, "expect_from_ok": {"face": ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"], "unknown_count": 56}}
```

## manual_override 与统计
- check_manual_override 通过，没有 VOID（即 mo_err=[]）。只读复核结果：
  - delist_period_source=="manual_override" 的行只有 {002509.SZ}
  - 该行 delist_period_start=20200604
- 统计（manifest.stats 与 stdout 相同，并从 parquet 只读复核）：
  - rows 339 / rows_v1 339；v1_columns_equal=true
  - 只读复核：v1 列的顺序和值与 data/v2/ref/stock_delisted.parquet 完全相同（DataFrame.equals 为 True）
  - **face_value_flag 93** ✓
  - **entered 89 → 151** ✓
    - d4_zero_day_fixed 61；entered_newly_other 1（002509.SZ，override）；entered_lost 0
    - 零天整理期 61 → 0
  - **UNKNOWN 56** ✓（counts.unknown_needs_source=56；parquet 中 sd1_delist_type_default=="UNKNOWN" 的行也是 56）
  - **面值集合 4 个代码** ✓（000861.SZ、002505.SZ、002509.SZ、600297.SH）；face_value_expected_present 4 个都为 True
  - delist_reason_category_v2 分布：
    - 强制退市(进入退市整理期) 150
    - 强制退市(退市前1年内ST/*ST) 129
    - UNKNOWN(缺公告来源) 56
    - 强制退市(面值退市) 4
  - delist_period_source 分布：'' 188、namechange 150、manual_override 1

## P3-12 只读核对（`data/v2/ref/stock_delisted_v2.parquet`）
- 002509.SZ 那一行（共 1 行），以下是精确值：
  - delist_period_source = `manual_override`
  - delist_period_start = `20200604`
  - source_ann_no = `天广中茂 2020-053《关于公司股票终止上市的公告》; 深证上【2020】442号`
  - override_source_verified = `True`
  - source_url = `http://disc.static.szse.cn/download/disc/disk02/finalpage/2020-05-28/9f3e0d5c-66cd-4ab0-b727-ed74438ea31a.PDF`
  - 补充：source_published_date=20200528；delist_period_ann_date=20200527；entered_delisting_period_v2=True；delist_reason_category_v2=强制退市(面值退市)；face_value_delist_flag=True；sd1_delist_type_default=FORCED
- 非 override 行共 338 行。其中 source_ann_no、source_url、source_published_date 都为空（None、NaN 或空串）且 override_source_verified=False 的有 **338/338** ✓
  - 逐列：source_ann_no 空 338；source_url 空 338；source_published_date 空 338；override_source_verified False 338

## 输出
| 路径 | 字节 | sha256 |
|---|---|---|
| data/v2/ref/stock_delisted_v2.parquet | 60,860 | 9d757b96bb27540ea02ca0af323aacfb3880797604830a3984eb6fa4fdff3750 |
| data/v2/ref/stock_delisted_v2.parquet.manifest.json | 8,535 | 156bcf3a254e2a545f09156b3648b110f838c685e7ce9260fc0f7ff138761d99 |
| data/v2/ref/stock_delisted_v2.parquet.receipt.json | 2,313 | 417d918d0121722dd041cc0bb256f6604bd2358ff16677f268f596dfeadce2d0 |

- parquet 共 40 列。
- manifest：step=D3D4_stock_delisted；mode=execute；status=PASS；join_key=ts_code；live=false；promotion_approved=false；sha256=9d757b96…（等于 parquet）
- 收据 JSON：
  - status=PASS；sha256=9d757b96…
  - manifest_sha256=156bcf3a…，等于 manifest 文件
  - **ok_sha256=f03357f1…，与 D1a、D1b、D2 相同** ✓
  - **prev_receipt_sha256=06d06a792103abb69cc12aa2ba71932d202da50d20dfc94a41093656ee49a4c2（D2 收据）** ✓
- D3D4 的收据只有 step、ok_sha256、pins、status、prev_receipt_sha256、sha256、run_conditions、manifest_sha256 这几个键，不含 raw_content。这是设计如此，P3-9 只涵盖 D1a、D1b、D2。

## 峰值 RSS
- 388,336 KB（约 379 MB），低于 rss_cap 1450 MB ✓
- v4a dry-run 为 393,232 KB；脚本自报 rss_mb=379

## stdout 对比（v4a dry-run：d3d4_stdout_v4_20261018.txt，sha256 3fbe7474…）
- stdout：`d3d4_exec_stdout_20261018.txt`，sha256=34a3a861218b9f2c115ec2a45a7c3107a78c673c768c4103bd21c75b4bc254ff
- 原始 diff：`d3d4_exec_rawdiff_vs_v4a_dryrun.txt`，12 行，sha256=165d558691fd9d4aeb6717ecbd706208847f0b3fe063e83a2d99cdd0257caf91
  - GATE_PASS 行：mode 不同，ok_sha 不同
  - stats 行：只有 rss_mb 不同（384 对 379，已单独核实）
  - D3D4_FACE_CHECK 行：只有 expect_from_ok 不同（dry-run 为 null，execute 为两个期望值，已单独核实）
  - 末行：DRY-RUN PASS 对 COMMITTED
  - 包装行
  - RUN_CONDITION_MATCHES 两边都是 []，没有差异
- 规范化 diff：`d3d4_exec_normdiff_vs_v4a_dryrun.txt`，**0 行**，sha256=e3b0c442…（空）
  - 规范化规则：
    - 去掉 RUN_CONDITION_MATCHES 行和 WRAPPER_EXIT 行
    - ok_sha256 替换为 <OK>
    - mode 替换为 <MODE>
    - rss_mb 替换为 <RSS>
    - **新增一条：`"expect_from_ok": {...}` 替换为 <EXPECT>**。这是 execute 模式下必然出现的差异：dry-run 只打印、不带键，execute 强制带键。
    - 去掉 DRY-RUN PASS 和 COMMITTED 末行

## find -newermt T0 写入核对
- 命令：`find data/v2 output ref docs scripts -newermt '2026-10-18 05:32:05.685396523' -type f -not -path 'docs/v2/audit/data_cs_panel_execute/*'`

| 目录 | 文件数 | 说明 |
|---|---|---|
| data/v2/ref | 3 | 全部是 D3D4 输出（05:32:06.91） |
| data/v2/tushare_raw/fund_portfolio_dh | **0** | 94322 处于 T |
| output/loop | 1 | 其他 agent 写的，见下 |
| 其他目录 | 0 | |

- 其他 agent 的文件（不是本次运行写的）：`output/loop/TEAM_STATE_latest.md`
  - mtime 05:32:11.07，81,394 B，晚于 D3D4 结束时刻 05:32:07.00
  - 这是团队状态文件，由其他 agent 更新，本次没有写入

## 未做
- 没有 SIGCONT 94322，它保持 T，等 Arch 书面确认
- 没有删除 HOLD_FUNDPORT_MERGE，没有合并 fund_portfolio 或 broker_recommend
- 没有动补数队列和 moneyflow
- 没有启动 8787，没有发消息，没有做 git 操作
