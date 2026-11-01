# fund_portfolio 按期流式合并设计 v1

live=false；promotion_approved=false。本文**只定设计与接口**，不改代码、不跑合并、不读真实 parquet 行、不动备份目录。

- **归属：** Data 出本设计与接口说明；**Eng** 在 94322 TERM（或已自然退出且无最终产物）之后、且 Arch 签实现/启用 .ok 后再改代码；启用前另签运行 .ok。
- **动机：** 旧路径 `remaining_after_stk_surv.py` L96 对 34 期 × ~16538 页做整表 `pd.concat` + 两次 `drop_duplicates`，实测峰值 VmHWM ≈ 7.25GB，卡死/重启后仍无最终表（留证 dc1f94fb…）。Arch/主 Agent P3：按期分块 + ParquetWriter 流式写，峰值目标 ≤1.5GiB。
- **本设计峰值目标：** 单进程 RSS ≤ **1,000,000 kB**；进程树 1s 采样 ≤ **1,500,000 kB**；建议自中止线 1,200,000 kB（单进程）。

## 0. 相对旧 L96 的风险对照

| # | 旧 L96 风险 | 本设计如何消掉 |
|---|---|---|
| R1 | 16538 个文件一次 list 进内存再 concat | 按期处理：同进程内**一次只持有一期**的 DataFrame/Table；期与期之间 del + 写盘 |
| R2 | 全量 drop_duplicates() 无键 + 再按键 dedup，峰值翻倍 | 仅在期内按键 (ts_code,end_date,symbol)、sort ann_date、keep="first"；跨期键含 end_date 分离，不做跨期二次全表 dedup |
| R3 | to_parquet 直接写最终路径，中断留半截 | 期级 tmp → 最终 tmp → os.replace；禁止原地打开最终路径写入 |
| R4 | TERM/OOM 后无清理口径 | 失败/TERM：只删**本 run** 登记过 inode 的 tmp；不动源分片与他 run 文件 |
| R5 | 无内存硬顶 | 每期前后采 VmRSS；超 1,000,000 kB 记 P1 并 abort（exit≥20）；树采样超 1,500,000 kB 同样 abort |
| R6 | 日志仅在整表完成后打 done | 每期打 period_merged；最终打 done/partial；可断点跳过已有期级产物 |
| R7 | available_at 与 dedup 顺序绑在巨大帧上 | 期内复刻 L97–102 语义（见 §4）；用合成数据断言与参考实现一致 |
| R8 | 对账缺失 | manifest 含每期行数（去重前/后）、最终行数、键唯一、源 _DONE/页数元数据对账 |

## 1. 输入 / 输出路径（参数化）

| 角色 | 默认路径 | 说明 |
|---|---|---|
| 原始分片根 | `data/v2/tushare_raw/fund_portfolio_dh/<YYYYMMDD>/` | 只读；34 期已有 _DONE |
| 期列表 | 与现脚本 periods() 相同：20180331…20260630（34 期） | 实现须把 periods 作参数，自测注入子集 |
| 期级临时目录 | `data/v2/events/_tmp_fundport_stream/<run_id>/period_<YYYYMMDD>.parquet` | run_id=YYYYMMDDTHHMMSSZ+pid |
| 最终临时 | 同目录 `fund_portfolio_2018plus.parquet.tmp` | O_EXCL 创建后再交给 ParquetWriter |
| 最终表 | `data/v2/events/fund_portfolio_2018plus.parquet` | 仅 os.replace 落入 |
| manifest | `data/v2/events/fund_portfolio_2018plus_manifest.json` | 原子写 |
| DONE | `output/markers/fund_portfolio_2018plus.DONE` | 内容=最终表 sha256；仅 fails 空时写 |
| 回执 md | `docs/v2/DATA_FUND_PORTFOLIO_FULLWINDOW_RECEIPT_ZH.md` | 字段对齐旧 L109–118 |
| quarantine | `data/v2/events/_quarantine/` | 仅损坏最终候选；须运行 .ok 显式允许 |
| 自测根 | 强制位于 `/tmp/ql_fundport_stream_test_*` | 断言路径前缀 |

实现入口建议（Eng）：新建 `scripts/acquire/fund_portfolio_stream_merge.py`，由 `remaining_after_stk_surv.fund_portfolio` 在分页完成后调用**或**独立 CLI；**禁止**再走 L96 那一行。启用 .ok 前旧 L96 须删除或 `raise RuntimeError("disabled")`。

## 2. 算法（按期）

语义规范（非可运行补丁）：

1. 生成 run_id，mkdir `events/_tmp_fundport_stream/<run_id>`，建立 inode_ledger=[]。
2. 对每个 period p：
   - heavy_gate / MemAvailable 预检（阈值由运行 .ok 写明，建议 ≥2621440 kB）。
   - files = sorted(glob 该期 *.parquet 且 size>0)。
   - 期内读取并 concat（可分文件批，但**不得跨期持有**）。
   - rows_before = len(x)。
   - 按 §3 / §4 做类型规范化、键去重、available_at、promotion_approved=False。
   - 原子写 period_p.parquet（O_EXCL tmp + replace）；ledger 记 inode。
   - log period_merged(period, rows_before, rows_after, pages)。
   - del x。
3. 最终流式拼：
   - O_EXCL 创建最终 tmp；ParquetWriter 按 period 顺序每次只读一期 period_*.parquet 写入。
   - close；校验 metadata 行数=各期 rows_after 之和。
   - os.replace(tmp, 最终表)；写 manifest、回执；fails 空则写 DONE。
   - 成功后按 ledger 清理本 run tmp。

硬约束：
- **禁止**跨期 `pd.concat([...] for p in periods for f in ...)`。
- **禁止**一次读入全部期级 parquet 再 concat。
- 跨期去重：v1 不做（键含 end_date）。若发现跨期重复键，单开 Arch 议题。

## 3. 去重键与排序（对齐 L96–L98）

| 步骤 | 旧代码 | 流式 v1 |
|---|---|---|
| 粗 drop | L96 无子集 drop_duplicates() | **默认省略**（见开放项 O1） |
| 键去重 | L98 sort ann_date + drop_duplicates([ts_code,end_date,symbol], keep="first") | **期内原样** |

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

## 5. manifest / DONE / 回执字段

manifest（JSON，原子写）至少：

- table, sha256, rows, periods=[first,last], n_periods, n_funds
- source, available_at（说明字符串，同旧）
- n_no_ann, n_fails, fails（最多 50）
- per_period: [{period, pages, rows_before_dedup, rows_after_dedup, period_sha256}]
- run_id, merge_mode="stream_v1", peak_rss_kb_observed, script_sha256
- promotion_approved: false

DONE：`output/markers/fund_portfolio_2018plus.DONE` 内容为最终表 sha256；仅 n_fails==0。

回执 md：沿用旧标题结构，并增加 merge_mode=stream_v1、峰值 RSS、各期 rows 表。

## 6. 对账（可用 pyarrow 元数据，不读行到 pandas）

| 检查 | 方法 |
|---|---|
| 源页数 | 每期 glob(*.parquet) 个数 vs 日志/_DONE 旁证 |
| 去重前行数之和 | 每期各页 ParquetFile(f).metadata.num_rows 求和 |
| 去重后行数之和 | 各 period_*.parquet metadata 行数之和 == 最终表 metadata 行数 |
| 键唯一 | 期内断言；跨期靠 end_date 隔离；自测用合成数据强制重复键 |
| 与旧全量 | 不对现网缺失最终表做强制相等；启用后若 Arch 要求，另 .ok 做只读对照 |

## 7. 失败 / TERM / 清理

- 退出码从 **20** 起（避免 nightly_update 把 2/3 当成功/部分成功）。
- 建议码表：20 预检失败；21 内存；28 环境/版本；31 TERM；32 HUP（HUP 不自我重发）。
- 捕获 SIGTERM：停止 writer、close、**不** replace 最终路径；按 ledger 清本 run tmp；exit 31。
- 回滚期间忽略新的 TERM/HUP。
- 清理：只 unlink inode 在 ledger 且路径在 tmp_root 下的文件；禁止宽匹配 rm；禁止删 fund_portfolio_dh。
- 禁止原地写最终表。当前无旧最终表可备份；若将来覆盖，先硬链接到 events/_bak/（名带秒）再 replace，须 .ok。

## 8. 内存与门闩

- 启动前：`rg MemAvailable /proc/meminfo`；低于运行 .ok 阈值则 exit 20。
- 每期结束后采样 VmRSS；单进程 >1,000,000 kB → abort。
- 可选 1s 树采样（自身+子孙）>1,500,000 kB → abort。
- 若 `output/HOLD_FUNDPORT_MERGE` 存在 → 与现 merge_held 相同，只记日志 return，不合并。

## 9. 自测（Eng 交付必过；路径全在 /tmp）

1. CLI/函数接受 --raw-root/--events-dir/--markers-dir/--periods；断言全部落在传入的 tmp 根下。
2. 合成 2–3 期、含重复键与缺 ann_date；断言 available_at 与参考纯函数一致；最终键唯一。
3. 跑前/跑后对源分片做 sha256 清单，必须不变。
4. 中途注入 SIGTERM：最终路径不存在或未被 partial replace；tmp 按 ledger 清理。
5. 内存夹具：最大合成期下 RSS ≤1,000,000 kB（测量写入回执）。
6. 默认禁止测试读写 `/workspace/QuantLab/data/v2/...` 真路径。

## 10. 启用顺序（流程）

1. Arch 复审本文 → PASS 或 PASS_WITH_CONDITIONS。
2. 94322 经新 TERM .ok 结束（或已退出且无最终产物）——见 `docs/v2/audit/fundport_20261025/ROUTINE_94322_TERM_DRAFT_20261025.md`。
3. Eng 按本文改代码 + 自测绿。
4. Arch 签**实现审阅**与**单次运行** .ok（窗口、内存阈值、是否允许写真 data/v2/events/）。
5. Data/Eng 执行；交回执（sha、行数、报告期覆盖、重复键、与源页数/元数据行数对账、available_at、peak RSS）。
6. Arch 审过前下游不可读（无 DONE 则不得当完成）。

## 11. 开放项（须 Arch 拍板）

| ID | 问题 | Data 缺省建议 |
|---|---|---|
| O1 | 是否保留 L96 无键 drop_duplicates() | 不保留；合成证明对键首披露无影响即可 |
| O2 | 单期若仍超 1GB：是否允许期内按文件批再落一个 period 文件 | 允许，仍禁止跨期持有 |
| O3 | 最终拼接触发：替换 L96 原地 / 新 CLI 由例程调用 | 新 CLI + 旧函数改调用；L96 行删除或硬失败 |
| O4 | MemAvailable 运行阈值 | 2621440 kB（与 nightly 线对齐），写入运行 .ok |
| O5 | 与 broker_recommend 合并的调度关系 | fundport stream 成功并 DONE 后再进入 Q8；不在本文实现 Q8 |
| O6 | 旧日志仍指向 10-18 路径 | 运行 .ok 写明新 log 路径；合并阶段每期 flush 日志 |

## 12. 变更记录

| 版本 | 时间 ET | 说明 |
|---|---|---|
| v1 | 2026-10-25 ≈00:10 | 首版。响应主 Agent 00:08 路径 C 与 Arch P3（≤1.5GiB）。只设计不实现。对照旧 L96；按期流式；available_at 等价；对账与自测；退出码≥20；清理按 inode ledger。 |

