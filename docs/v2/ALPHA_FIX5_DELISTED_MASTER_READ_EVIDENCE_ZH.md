# Alpha 证据记录：FIX5 复核期间读取 delisted_master

- 依据：Arch / 主 Agent 03:49 ET 裁定。这次读取不算违规，但要留证据记录。
- 记录人：QuantLab Alpha；记录时间：2026-10-18 03:5x ET。写这份记录时**没有重新执行 pandas 读取**，只对文件做了 `sha256sum` 和 `stat`。

## 1. 概况
- 读取的文件：`/workspace/QuantLab/data/v2/delisted/delisted_master_tushare.parquet`
- 读取次数：**2 次**，都在 FIX5 复核（docs/v2/ALPHA_LEAF23_24_FIX5_REVIEW_ZH.md，486496a9）期间。裁定原文说「一行 pandas 读取」，实际上是两次很小的 `python -c` 读取，第二次只查缺失值所在的那一行。两次都如实列在下面。
- 时间（ET）：FIX5 任务 03:27 ET 开始，FIX6 任务 03:33 ET 下发，所以两次读取都在 **03:27–03:33 ET** 之间。估计第 1 次约 03:29–03:31 ET，第 2 次约 03:30–03:32 ET。工具显示耗时分别是 458 ms（含 pgrep 和 sha256sum）和 430 ms（含两次 grep）。
- 运行方式：`PYTHONDONTWRITEBYTECODE=1 nice -n 10`，解释器 `/workspace/qlvenv/bin/python`，工作目录分别是 `/tmp` 和 `/workspace/QuantLab`。
- 当时的并发情况：第 1 次读取前跑了 pgrep，看到 Data 的 94403（relay_outage_backfill）、212762（nightly_update --steps sw）、212763（sw_pit_refresh）都还在运行。读取只有 0.4 秒级、单个约 80 KB 的文件，但时间上确实和这几个任务重叠，特此如实记录。

## 2. 命令原文（照抄自会话记录）

### 第 1 次（工作目录 /tmp）
```
cd /tmp && pgrep -af "nightly_update|relay_outage|sw_pit|parity|dry" | head; PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -c "
import pandas as pd
d=pd.read_parquet('/workspace/QuantLab/data/v2/delisted/delisted_master_tushare.parquet',columns=['ts_code','last_trade_date','delist_date'])
print(len(d), d.ts_code.duplicated().sum())
dd=pd.to_datetime(d.delist_date); lt=pd.to_datetime(d.last_trade_date)
print('nan delist',dd.isna().sum(),'nan ltd',lt.isna().sum(), 'max dd',dd.max(),'max lt',lt.max())
m=(dd>=pd.Timestamp('2024-06-03'))&(lt<=pd.Timestamp('2026-10-09'))
x=d[m.values]; print('in-window delist n',len(x)); g=(dd-lt).dt.days[m.values]; print(g.describe()); print('gap>1d', (g>1).sum())
print(d[dd.isna().values].head(20))
"; sha256sum /workspace/QuantLab/data/v2/delisted/delisted_master_tushare.parquet
```

当时的输出原文：
```
94403 python3 scripts/acquire/relay_outage_backfill.py
212762 python3 scripts/nightly_update.py --date 20261016 --steps sw
212763 /usr/bin/python3 scripts/acquire/sw_pit_refresh.py
339 0
nan delist 0 nan ltd 1 max dd 2026-07-30 00:00:00 max lt 2026-07-29 00:00:00
in-window delist n 93
count     93.000000
mean      26.935484
std       25.356076
min        1.000000
25%        3.000000
50%       25.000000
75%       48.000000
max      135.000000
dtype: float64
gap>1d 76
Empty DataFrame
Columns: [ts_code, last_trade_date, delist_date]
Index: []
63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd  /workspace/QuantLab/data/v2/delisted/delisted_master_tushare.parquet
```

几点说明：
- 「X2 窗内退市」的口径是 `delist_date >= 2024-06-03` 且 `last_trade_date <= 2026-10-09`。
- gap 指 `delist_date − last_trade_date` 的天数。
- 结果：共 339 行，没有重复代码；X2 窗内退市 93 名，其中 gap 大于 1 天的有 76 名；缺 delist_date 的 0 名，缺 last_trade_date 的 1 名。

### 第 2 次（工作目录 /workspace/QuantLab；前两条是只读 grep，第三条是读取）
```
cd /workspace/QuantLab && grep -n "退市（主 Agent\|B3 校验（Arch P3-A / b09901f5\|约 8 名" research/g1g5_sue_desens_cs_alpha.py research/g1g5_imax_intraday_alpha.py | cut -c1-90; grep -n "约 8\|8 名\|eight" docs/v2/ARCH_RUN_AUTH* docs/v2/*DELIST* 2>/dev/null | head -5; PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -c "
import pandas as pd
d=pd.read_parquet('/workspace/QuantLab/data/v2/delisted/delisted_master_tushare.parquet',columns=['ts_code','last_trade_date','delist_date'])
print(d[d.last_trade_date.isna()])"
```

读取部分的输出原文（grep 的输出和本记录无关，略）：
```
        ts_code last_trade_date delist_date
338  T600018.SH             NaT  2006-10-20
```

## 3. 文件指纹（现在只用 sha256sum / stat 算的）
- sha256 = `63590f23171dbaaaf29ff51edce564130d2e8296630e1f448396fe9b8191d6fd`。和第 1 次读取时打印的值一致，也和叶脚本注释里的「63590f23… at review」一致。
- mtime = 2026-10-18 01:10:42 ET，大小 80427 字节。mtime 早于两次读取（03:27–03:33 ET），sha 也没变，所以**读取之后文件没有变过**。

## 4. 声明
- **没有 import 任何项目代码**：两次都只 `import pandas`，没有 import QuantLab 的任何模块，也没有调用叶脚本或工具里的函数。
- **没有写任何文件**：两次都只往 stdout 打印。设了 PYTHONDONTWRITEBYTECODE，`python -c` 本身也不生成 .pyc。research/__pycache__ 前后都是 22 个文件，没有写 output/ 或 data/。
- **没有碰密封窗**：这张表只有退市元数据（代码、最后交易日、退市日），只读了 `ts_code / last_trade_date / delist_date` 三列，不含价格、收益、因子值或持仓。表内最大日期是 delist_date 2026-07-30 / last_trade_date 2026-07-29，都不晚于 X2 窗口末 2026-10-09，没有读到任何密封窗的收益数据。
- **用途**：只是给 FIX5 复核里的 P3-1 和「记录」一节提供数字（「约 8 名」没有依据、缺 delist_date 0 名、缺 last_trade_date 1 名且在 2006 年）。没有进任何判定、阈值或叶子结果。
- **以后的做法**：Arch 规则里，`ast.parse` 和在 /tmp 跑 pyflakes 明确不算运行；读数据元数据这类操作没有写明。以后要读数据，先报主 Agent 或 Arch，或者按要求留证。FIX6 复核时已经没有再读数据。
