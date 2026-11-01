# 10-14/15/16 补跑 .ok 申请 r3.1（方案 R；Data，待 Arch 审）

- 作者：QuantLab Data；起草 2026-10-18 约 11:22 ET。新文件。**以 r3（docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r3.md，76e5f1f1cc6f70e3c243cde7142bd0673a1f822df82ea90b13c8bc07ba5e4bd7）为全文底本**，本文只列 r3.1 的三处改动；未提到的条目以 r3 为准（r3 未提到的以 r2 2aad5036… 为准）。
- 依据：Arch 11:20 新前置条件（所有运行适用）；大分页探测标准改为 stock_basic。
- 本文所有命令均未运行。执行器只做过 ast 语法检查、/proc 辅助函数的 sleep 进程自测、一次只读 healthz GET 与一次 pgrep（11:21 ET：quiet=false、三个 running 均 false、child_pids={}；pgrep 无匹配，rc=1）。

## 改动 1：执行器换为 v3
- 路径：docs/v2/audit/backfill_1014_1016/run_backfill_r_v3.py
- sha256：**f006c0b2b19de4428d3ec943245e0fae4cbbd991ed1caf8e213205dbae40dd3d**（690 行；只用标准库 + pyarrow 元数据；不 import 项目代码）
- v3 = v2（28bc5e0e…）+ 改动 2 的 quiet 闸门；去掉 --quiet-evidence 参数（证据改由执行器自己采集写入结果 JSON）。
- 同目录 run_backfill_r.py（1e81c4f1…）与 run_backfill_r_v2.py（28bc5e0e…）均**作废，请勿钉、请勿运行**；按规则不覆盖，留在原处。
- 命令：
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/backfill_1014_1016/run_backfill_r_v3.py </dev/null
预检：同上加 --check-only（含完整 quiet 闸门，约 15–105 秒，不起任何运行）
```
- r3 §7 .ok 建议字段中 sha_runner 改为 f006c0b2b19de4428d3ec943245e0fae4cbbd991ed1caf8e213205dbae40dd3d；其余字段不变。

## 改动 2：RESEARCH_QUIET 前置条件（Arch 11:20，执行器强制）
顺序：
1. 操作员 / Arch 设好 /workspace/QuantLab/output/loop/RESEARCH_QUIET.lock（用 Arch 的锁模板）。**执行器不建锁、不删锁**；锁不存在即退出 2。
2. 执行器轮询 http://127.0.0.1:8795/healthz（每 3 秒，超时 5 秒）直到 quiet=true，最多 90 秒；超时即退出 2，不跑。
3. 再等 15 秒。
4. 复核 healthz：quiet=true，gen_running、snapshot_running、kline_running 均为 false，child_pids == {}；任一不符退出 2。
5. `pgrep -af "kline.py|export_static.py|snapshot.py|gen.py"` 必须无输出（rc=1）；否则退出 2。
6. 以上在 94322 状态核对之后、dry-run 之前执行（完整版）；run2 起跑前再做一次复核版（锁仍在 + 第 4、5 步，不再 90 秒轮询与 15 秒等待），不通过则不起 run2，退出 1。
7. 锁文件 sha 与前 500 字符、每次 healthz 响应、等待秒数、pgrep 结果全部写入结果 JSON 的 checks.quiet。
8. 释放锁：由设锁方（Arch / 操作员）在执行器退出、CONT 94322 之后进行；执行器结束时打印提醒。
说明：模式 snapshot.py 中的点是正则任意字符；快照工具 nightly_sha_scope_snapshot_v2_20261018.py 不匹配（snapshot 后面是 _v2，不是「任意一字符 + py」），tier3_daily_snapshot.py 会匹配，但它只在 run2 内部运行，quiet 闸门都在 run2 起跑之前。

## 改动 3：大分页探测标准
r3 §6 第 2 项的大分页接口由 index_member_all 改为 **stock_basic list_status=L limit=5000，返回恰好 5000 行**才算通。占位表更新为：
| 轮 | 时间 ET | 接口 | 参数 | 耗时 | HTTP | 行数 | 结论 |
|---|---|---|---|---|---|---|---|
| P1 | 待补 | trade_cal | SSE 20261014–20261020 | 待补 | 待补 | 待补（应 7） | 待补 |
| P1 | 待补 | stock_basic | list_status=L，limit=5000，第 1 页 | 待补 | 待补 | 待补（须恰好 5000） | 待补 |
| P2 | 待补 | trade_cal | 同上 | 待补 | 待补 | 待补（应 7） | 待补 |
| P2 | 待补 | stock_basic | 同上 | 待补 | 待补 | 待补（须恰好 5000） | 待补 |
两轮连续都通（trade_cal 7 行、stock_basic 恰好 5000 行）才申请 .ok；任一失败不申请。探测只读、不落盘到 data/。

## 其余前置证据（同 r3 §6，待补）
94322 STOP 前后 ps 与 /proc/94322/stat（T）；锁文件路径 / 内容 / 设锁时间（执行器另行自动记录 healthz 与 pgrep）；Arch 审过 r3 + 本文、执行器 v3（f006c0b2…）、范围（579c8605…）；13:30 ET 前拿到 .ok，否则放弃今天的补跑。

## 请 Arch 确认
- r3 的 Q1–Q6 仍待答。
- Q7：run2 前只做复核版 quiet 闸门（不重新 90 秒轮询 + 15 秒等待），是否足够？
