# fund_portfolio 按期流式合并设计 v1.1

live=false；promotion_approved=false。本文**只定设计与接口**，不改代码、不跑合并、不读真实 parquet 行、不动备份目录。

- **归属：** Data 出本设计与接口说明；**Eng** 在「无最终产物」且 Arch 签实现审阅 .ok + 单次运行 .ok 后再改代码与开跑；启用前不得动旧路径。
- **基线：** v1 `docs/v2/DATA_FUND_PORTFOLIO_STREAM_MERGE_DESIGN_v1_ZH.md` sha256 `b78cc9e1db381f9fef43e32d3b83d83b6053d6b80aa0ecf783353b733c5c14c7`（不动）。
- **闭合对象：** Arch 预备复审 `docs/v2/ARCH_FUND_PORTFOLIO_STREAM_MERGE_REVIEW_v1_ZH.md` sha256 `5a79b7e275b3bce00c2c574e0578823682e68f363348039a8cfeeb5a68046f42` 条件 C1–C8；开放项 O1–O6 按审查预备裁定全部采纳。
- **动机（沿用 v1）：** 旧路径 `remaining_after_stk_surv.py` L96 对 34 期 × ~16538 页做整表 `pd.concat` + 两次 `drop_duplicates`，实测峰值 VmHWM ≈ 7.25GB，卡死/重启后仍无最终表（留证 dc1f94fb…）。按期分块 + ParquetWriter 流式写。
- **峰值目标（沿用 v1，不放宽）：** 单进程 RSS ≤ **1,000,000 kB**；进程树 1s 采样 ≤ **1,500,000 kB**；建议自中止线 1,200,000 kB（单进程）。

## C1–C8 对照表

| ID | 级别 | 闭合摘要 | v1.1 节 | 行号 |
|---|---|---|---|---|
| C1 | P1 | 期内按文件批硬顶：每批 ≤128 文件且累计行数 ≤400000；批间 del | §2.1 | 65–78 |
| C2 | P1 | trade_cal 路径+sha pin（或只读 pin）；自测注入合成日历；禁止隐式读活路径 | §4.1 | 143–153 |
| C3 | P2 | 不保留无键 drop；合成夹具证明仅键去重 vs 先无键再键去重 在 keep=first 键集合一致 | §3、§9.3 | 115–128；207 |
| C4 | P2 | 新 CLI；启用 .ok 后旧 L96 `raise RuntimeError("disabled")` | §1.1、§10 | 56–62；216–223 |
| C5 | P2 | run_id 已存在则换新；禁止复用半截；只清本进程将创建的路径 | §2.2 | 79–87 |
| C6 | P2 | manifest/DONE 先 `.tmp` 再 `os.replace`；DONE=最终表 sha 且与 manifest.sha256 一致 | §5 | 154–174 |
| C7 | P3 | MemAvailable 2621440 kB 写入运行 .ok；脚本不硬编码 | §8 | 195–202 |
| C8 | P3 | 本窗口 `allow_broker_recommend=false` | §10.1 | 225–231 |

> 行号对应当前文件版本；若人工编辑本文，须同步更新本表。

## 0. 相对旧 L96 的风险对照

| # | 旧 L96 风险 | 本设计如何消掉 |
|---|---|---|
| R1 | 16538 个文件一次 list 进内存再 concat | 按期处理：同进程内**一次只持有一期**；期内再按文件批（§2.1），批间 del + 写盘 |
| R2 | 全量 drop_duplicates() 无键 + 再按键 dedup，峰值翻倍 | 仅在期内按键 (ts_code,end_date,symbol)、sort ann_date、keep="first"；跨期键含 end_date 分离；无键步默认省略（§3，C3 夹具） |
| R3 | to_parquet 直接写最终路径，中断留半截 | 期级 tmp → 最终 tmp → os.replace；禁止原地打开最终路径写入 |
| R4 | TERM/OOM 后无清理口径 | 失败/TERM：只删**本 run** 登记过 inode 的 tmp；不动源分片与他 run 文件 |
| R5 | 无内存硬顶 | 每期/每批前后采 VmRSS；超 1,000,000 kB 记 P1 并 abort（exit≥20）；树采样超 1,500,000 kB 同样 abort |
| R6 | 日志仅在整表完成后打 done | 每批/每期打日志；最终打 done/partial；可断点跳过已有期级产物（同 run_id 禁止复用，见 §2.2） |
| R7 | available_at 与 dedup 顺序绑在巨大帧上 | 期内复刻 L97–102 语义（§4）；用合成数据断言与参考实现一致 |
| R8 | 对账缺失 | manifest 含每期行数（去重前/后）、最终行数、键唯一、源页数元数据对账 |

## 1. 输入 / 输出路径（参数化）

| 角色 | 默认路径 | 说明 |
|---|---|---|
| 原始分片根 | `data/v2/tushare_raw/fund_portfolio_dh/<YYYYMMDD>/` | 只读；34 期已有 _DONE |
| 期列表 | 与现脚本 periods() 相同：20180331…20260630（34 期） | 实现须把 periods 作参数，自测注入子集 |
| trade_cal | 由运行 .ok / CLI 显式钉路径+sha（§4.1） | 禁止隐式读未声明活路径 |
| 期级临时目录 | `data/v2/events/_tmp_fundport_stream/<run_id>/period_<YYYYMMDD>.parquet` | run_id=YYYYMMDDTHHMMSSZ+pid；已存在则换新（§2.2） |
| 最终临时 | 同目录 `fund_portfolio_2018plus.parquet.tmp` | O_EXCL 创建后再交给 ParquetWriter |
| 最终表 | `data/v2/events/fund_portfolio_2018plus.parquet` | 仅 os.replace 落入 |
| manifest | `data/v2/events/fund_portfolio_2018plus_manifest.json` | 先 `.tmp` 再 os.replace（§5） |
| DONE | `output/markers/fund_portfolio_2018plus.DONE` | 内容=最终表 sha256 = manifest.sha256；仅 fails 空时写 |
| 回执 md | `docs/v2/DATA_FUND_PORTFOLIO_FULLWINDOW_RECEIPT_ZH.md` | 字段对齐旧 L109–118 |
| quarantine | `data/v2/events/_quarantine/` | 仅损坏最终候选；须运行 .ok 显式允许 |
| 自测根 | 强制位于 `/tmp/ql_fundport_stream_test_*` | 断言路径前缀 |
| 运行日志 | 路径由运行 .ok 写明（O6） | 合并阶段每期 flush |

### 1.1 入口与旧 L96 硬失败（C4 / O3）

- **必须**新建 CLI：`scripts/acquire/fund_portfolio_stream_merge.py`（参数：`--raw-root` / `--events-dir` / `--markers-dir` / `--periods` / `--trade-cal` / `--trade-cal-sha256` / `--run-ok` 等）。
- 旧 `remaining_after_stk_surv.fund_portfolio` 在分页完成后**改为调用新 CLI/函数**，或由例程直接调新 CLI。
- **启用 .ok 生效后**，旧 L96 那一行（整表 concat）必须改为：`raise RuntimeError("disabled")`。优先硬失败，不删除整函数（降低误伤风险）。
- 启用 .ok 前：禁止对真路径跑合并；自测只许 `/tmp/...`。

## 2. 算法（按期）

### 2.1 期内按文件批硬顶（C1 / O2）

正文硬约束（不只是「允许」）：

1. 对每一期 p，先 `files = sorted(glob 该期 *.parquet 且 size>0)`。
2. **必须**按文件批读取，不得一期一次性 concat 全部页（即使页数看起来不大，实现也走批路径，便于统一测内存）。
3. **批硬顶（二者同时生效，先触顶者切批）：**
   - `BATCH_MAX_FILES = 128`（每批最多 128 个 parquet 文件）；
   - `BATCH_MAX_ROWS = 400000`（每批累计 `ParquetFile(f).metadata.num_rows` 之和上限；超则当前文件归入下一批）。
4. 批内：读入 → concat → 累加到期内缓冲帧 `acc`；**批间：`del batch_frame`；不得跨批保留中间 list。**
5. 期内全部批读完后，对 `acc` 做一次 §3 键去重 + §4 available_at；再原子写 `period_p.parquet`；然后 **`del acc`**。
6. 若单文件自身 `num_rows > BATCH_MAX_ROWS`：该文件单独成批；写完仍超单进程 1,000,000 kB → abort exit 21，记 P1（不得悄悄抬顶）。
7. 上述常量写入脚本具名常量，并在运行回执/manifest 的 `batch_max_files` / `batch_max_rows` 字段回显；改常量算实现变更，须 Arch 复审。

### 2.2 run_id 与启动清理（C5）

1. `run_id = UTC YYYYMMDDTHHMMSSZ + "_" + str(pid)`。
2. `tmp_root = events/_tmp_fundport_stream/<run_id>/`。
3. **若 `tmp_root` 已存在（含空目录）：禁止复用**；立即换新 run_id（可在秒级时间戳后追加 `_r2`、`_r3`…），直到路径不存在。
4. 创建目录：`os.mkdir`（不 `exist_ok`）；ledger 仅登记本进程随后 `O_EXCL` 创建的文件 inode。
5. **禁止**启动时扫描/删除其他 run_id 目录；禁止宽匹配 `rm -rf _tmp_fundport_stream`。
6. 仅当本进程失败/TERM 时，按本 run 的 inode ledger 清理；成功结束后同样只清本 run。

### 2.3 主流程

语义规范（非可运行补丁）：

1. 按 §2.2 生成未占用的 run_id 与 tmp_root，inode_ledger=[]。
2. 读运行 .ok：校验窗口、`mem_available_min_kb`、`allow_broker_recommend=false`（§10.1）、trade_cal pin（§4.1）、log 路径。
3. 对每个 period p：
   - heavy_gate：`rg MemAvailable /proc/meminfo`；低于运行 .ok 的 `mem_available_min_kb` → exit 20（§8）。
   - 按 §2.1 分批读入并累加；rows_before = 去重前 len(acc)。
   - 按 §3 / §4 做类型规范化、键去重、available_at、promotion_approved=False。
   - 原子写 period_p.parquet（O_EXCL tmp + replace）；ledger 记 inode。
   - log period_merged(period, rows_before, rows_after, pages, n_batches)；flush。
   - del acc。
4. 最终流式拼：
   - O_EXCL 创建最终 tmp；ParquetWriter 按 period 顺序每次只读一期 period_*.parquet 写入。
   - close；校验 metadata 行数 = 各期 rows_after 之和。
   - os.replace(tmp, 最终表)。
   - 写 manifest（§5）、回执；fails 空则写 DONE（§5）。
   - 成功后按 ledger 清理本 run tmp。

硬约束：

- **禁止**跨期 `pd.concat([...] for p in periods for f in ...)`。
- **禁止**一次读入全部期级 parquet 再 concat。
- **禁止**期内无视 §2.1 硬顶的整期一次性 concat。
- 跨期去重：v1.1 不做（键含 end_date）。若发现跨期重复键，单开 Arch 议题。

## 3. 去重键与排序（C3 / O1）

| 步骤 | 旧代码 | 流式 v1.1 |
|---|---|---|
| 粗 drop | L96 无子集 drop_duplicates() | **不保留**（O1 采纳） |
| 键去重 | L98 sort ann_date + drop_duplicates([ts_code,end_date,symbol], keep="first") | **期内原样** |

**C3 必过夹具（写入 §9.3）：** 合成数据上同时跑：

- 路径 A：仅键去重（本设计）。
- 路径 B：先无键 `drop_duplicates()` 再键去重（旧 L96 两步）。

断言：两条路径在 `keep="first"` 语义下，键集合 `(ts_code,end_date,symbol)` **完全一致**（作为 frozenset 或排序后逐元组比较）。若不一致 → 不得省略无键步，须改回期内保留无键步并报 Arch。列值集合（含 available_at）以键对齐后逐列相等为准；夹具须覆盖：完全重复行、同键不同 ann_date、缺 ann_date、无键步会删而键步保留的边界行。

## 4. available_at 等价性（对齐 L97–L102）

对每一行（期内已按键 keep first 之后）：

1. ann_date、end_date → astype(str)，{"None","nan"}→None（L97）。
2. ad = to_datetime(ann_date, format="%Y%m%d", errors="coerce")（L99）。
3. dl = to_datetime(end_date.map(deadline), format="%Y%m%d")，deadline(p) 与现 L74–78 相同：
   - 0630 → {y}0831；1231 → {y+1}0331；其余 → tdays(p, y+1+"1231") 的第 min(len-1,15) 个交易日。
4. available_at_basis：ann 非空 → "ann_date+1d 09:00"，否则 "statutory_deadline+1d 09:00"（L101）。
5. available_at = ad.fillna(dl).dt.normalize() + Timedelta(days=1, hours=9)（L102）。
6. promotion_approved=False（L103）。

等价性验收：自测夹具上，参考纯函数（旧逻辑副本）与流式期内输出在列集合、available_at、available_at_basis 及键上去重后的行集合一致（排序后比较或整表哈希）。

### 4.1 trade_cal 钉扎（C2）

1. `deadline` / `tdays` **必须**通过显式参数获得交易日历，禁止在库内隐式打开未声明路径。
2. 生产：运行 .ok 或 CLI 同时给出：
   - `trade_cal_path`（绝对或相对仓库根的稳定路径）；
   - `trade_cal_sha256`（文件全长 sha256）。
3. 启动时打开该文件前：计算 sha256，与 pin 不一致 → exit 28，不读内容进业务逻辑。
4. 允许「只读 pin」形态：.ok 写 `trade_cal_pin_ref` 指向已审 pin 清单条目；实现仍须解析出 path+sha 并校验。
5. 自测：**必须**注入合成日历文件（位于 `/tmp/ql_fundport_stream_test_*/trade_cal.parquet` 或 csv），并传入其 path+sha；测试不得依赖 `/workspace/QuantLab/data/...` 活日历。
6. 回执/manifest 回写实际使用的 `trade_cal_path` 与 `trade_cal_sha256`。

## 5. manifest / DONE / 回执（C6）

manifest（JSON）至少字段：

- table, sha256, rows, periods=[first,last], n_periods, n_funds
- source, available_at（说明字符串，同旧）
- n_no_ann, n_fails, fails（最多 50）
- per_period: [{period, pages, rows_before_dedup, rows_after_dedup, period_sha256, n_batches}]
- run_id, merge_mode="stream_v1_1", peak_rss_kb_observed, script_sha256
- batch_max_files, batch_max_rows
- trade_cal_path, trade_cal_sha256
- promotion_approved: false
- allow_broker_recommend: false

**原子写（强制）：**

1. 最终表 sha256 算完后，先写 `fund_portfolio_2018plus_manifest.json.tmp`（O_EXCL 或同目录唯一临时名），再 `os.replace` 到正式 manifest 路径。
2. DONE：仅当 `n_fails==0`；先写 `fund_portfolio_2018plus.DONE.tmp`，内容为**最终表文件**的 sha256 十六进制小写；再 `os.replace` 到 `output/markers/fund_portfolio_2018plus.DONE`。
3. **一致性：** DONE 文本 == manifest 字段 `sha256` == 最终表文件当前 sha256；任一不符不得留下正式 DONE（写前校验，失败则删 .tmp、exit ≥20、不 replace DONE）。
4. 回执 md：沿用旧标题结构，并增加 merge_mode=stream_v1_1、峰值 RSS、各期 rows 表、batch 硬顶、trade_cal pin。

## 6. 对账（可用 pyarrow 元数据，不读行到 pandas）

| 检查 | 方法 |
|---|---|
| 源页数 | 每期 glob(*.parquet) 个数 vs 日志/_DONE 旁证 |
| 去重前行数之和 | 每期各页 ParquetFile(f).metadata.num_rows 求和 |
| 去重后行数之和 | 各 period_*.parquet metadata 行数之和 == 最终表 metadata 行数 |
| 键唯一 | 期内断言；跨期靠 end_date 隔离；自测用合成数据强制重复键 |
| 与旧全量 | 不对现网缺失最终表做强制相等；启用后若 Arch 要求，另 .ok 做只读对照 |
| DONE↔manifest | §5 第 3 步 |

## 7. 失败 / TERM / 清理

- 退出码从 **20** 起（避免 nightly_update 把 2/3 当成功/部分成功）。
- 建议码表：20 预检失败；21 内存；28 环境/版本/trade_cal pin 不符；31 TERM；32 HUP（HUP 不自我重发）。
- 捕获 SIGTERM：停止 writer、close、**不** replace 最终路径；按 ledger 清本 run tmp；exit 31。
- 回滚期间忽略新的 TERM/HUP。
- 清理：只 unlink inode 在 ledger 且路径在本 run tmp_root 下的文件；禁止宽匹配 rm；禁止删 fund_portfolio_dh。
- 禁止原地写最终表。当前无旧最终表可备份；若将来覆盖，先硬链接到 events/_bak/（名带秒）再 replace，须 .ok。

## 8. 内存与门闩（C7 / O4）

- 启动前与每期前：`rg MemAvailable /proc/meminfo`。
- **阈值不硬编码进脚本：** 必须从运行 .ok 读取 `mem_available_min_kb`。Arch/主默认值 **2621440** kB（与 nightly 线对齐）写入该 .ok；脚本若未见该字段 → exit 20。
- 每批/每期结束后采样 VmRSS；单进程 >1,000,000 kB → abort exit 21。
- 可选 1s 树采样（自身+子孙）>1,500,000 kB → abort exit 21。
- 若 `output/HOLD_FUNDPORT_MERGE` 存在 → 与现 merge_held 相同，只记日志 return，不合并。

## 9. 自测（Eng 交付必过；路径全在 /tmp）

1. CLI/函数接受 `--raw-root/--events-dir/--markers-dir/--periods/--trade-cal/--trade-cal-sha256`；断言全部落在传入的 tmp 根下。
2. 合成 2–3 期、含重复键与缺 ann_date；断言 available_at 与参考纯函数一致；最终键唯一。
3. **C3 夹具：** §3 路径 A/B 键集合一致（必过）。
4. **C2：** 注入合成 trade_cal；故意错 sha → 期望 exit 28；不传 path → 期望 exit 20/28。
5. 跑前/跑后对源分片做 sha256 清单，必须不变。
6. 中途注入 SIGTERM：最终路径不存在或未被 partial replace；tmp 按 ledger 清理。
7. **C5：** 预置同名 run_id 目录后启动 → 必须换新 run_id，且不删除预置目录。
8. **C6：** 打断 manifest/DONE 写半截 → 正式路径不存在或仍为旧完整文件；成功后 DONE 文本 == manifest.sha256。
9. **C1 内存：** 最大合成期（超过 BATCH_MAX_FILES 页）下 RSS ≤1,000,000 kB；回执含 n_batches≥2。
10. 默认禁止测试读写 `/workspace/QuantLab/data/v2/...` 真路径。

## 10. 启用顺序（流程）

1. Arch 复审本文 v1.1 → PASS 或正式去掉「预备」。
2. 确认无最终产物（当前 94322 已退出且无 parquet/DONE——历史留证 dc1f94fb / EXIT_SHAPE）；无需 TERM。
3. Eng 按本文改代码 + §9 自测绿。
4. Arch 签**实现审阅**与**单次运行** .ok（窗口、`mem_available_min_kb`、trade_cal pin、log 路径、是否允许写真 `data/v2/events/`、§10.1）。
5. Data/Eng 执行；交回执（sha、行数、报告期覆盖、重复键、与源页数/元数据行数对账、available_at、peak RSS、n_batches）。
6. Arch 审过前下游不可读（无 DONE 则不得当完成）。

### 10.1 本窗口与 Q8（C8 / O5 / O6）

- 本启用窗口运行 .ok **必须**含 `allow_broker_recommend=false`。
- 实现若见 `allow_broker_recommend=true` 或不存在该字段 → exit 20，不进入合并，也不触碰 Q8/broker_recommend。
- fundport stream 成功并 DONE 后，Q8 另窗另签；**不在本文实现 Q8**。
- 运行日志路径由运行 .ok 写明（O6）；合并阶段每期 flush。

## 11. 开放项状态（O1–O6 已全部闭合）

| ID | Arch 预备裁定 | v1.1 落点 | 状态 |
|---|---|---|---|
| O1 | 默认不保留无键 drop；C3 夹具必过 | §3、§9.3 | 已闭合 |
| O2 | 允许期内按文件批；C1 须写硬顶 | §2.1（128 文件 / 400000 行） | 已闭合 |
| O3 | 新 CLI + 旧路径硬失败 | §1.1 | 已闭合 |
| O4 | 2621440 kB 写入运行 .ok | §8 | 已闭合 |
| O5 | fundport DONE 后再谈 Q8；本 .ok 禁 Q8 | §10.1 | 已闭合 |
| O6 | 新 log 路径写入运行 .ok | §1 表、§10.1 | 已闭合 |

**开放项清空：** 是（相对审查文 O1–O6 与 C1–C8；实现/运行仍须另签 .ok，不在本文开放项内）。

## 12. 变更记录

| 版本 | 时间 ET | 说明 |
|---|---|---|
| v1 | 2026-10-25 ≈00:10 | 首版。响应主 Agent 00:08 路径 C 与 Arch P3（≤1.5GiB）。只设计不实现。 |
| v1.1 | 2026-10-25 ≈00:16 | 闭合 Arch 预备复审 C1–C8（审查 sha 5a79b7e2…）；采纳 O1–O6。新增期内批硬顶、trade_cal pin、C3 夹具、新 CLI+L96 disabled、run_id 不复用、manifest/DONE 原子一致、MemAvailable 与 allow_broker_recommend 进运行 .ok。峰值线/算法骨架/对账/自测 /tmp 保留。不改代码、不动 v1 文件。 |

