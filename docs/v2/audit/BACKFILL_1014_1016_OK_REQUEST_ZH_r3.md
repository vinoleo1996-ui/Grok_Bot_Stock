# 10-14/15/16 补跑 .ok 申请 r3（方案 R；Data，待 Arch 审）

- 作者：QuantLab Data；起草 2026-10-18 约 11:20 ET。新文件，不改 r2（docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH_r2.md，2aad5036…）与 r1（122277e2…）。
- 依据：r2；Arch 审查 docs/v2/ARCH_DATA_TIMELINE_1019_AND_PLAN_R_REVIEW_ZH.md（717c3e7c642a7edf8bc05b23d02c8b4a74948938c146df5e149562502b46cbac）§5、§9 的 P2-3、P2-4、P2-5、P3-6、P3-7。
- 未写明的条目一律沿用 r2 原文（§1 cyq 只跑一次的代码依据、§2 钉 sha 表、§6 判定标准、§10 回执、§11 Q1–Q3）。
- **本文所有命令均未运行。** 执行器只做过 ast 语法检查与 /proc 辅助函数的 sleep 进程自测（与项目数据无关）。

## 0. r2 → r3 改动一览
| 编号 | r2 | r3 |
|---|---|---|
| P2-3 | §5 两条命令末尾带 `&`，读起来像并发 | **严格串行**：由执行器 run_backfill_r_v2.py 起 run1，wait 取 rc，跑后快照 + compare 退出 0，cyq 判定全过，才起 run2。命令里不再有 `&`。 |
| P2-4 | §7 每 15 秒人工 ps，人工判断中止 | **自动**：每 5 秒读 /proc/<pid>/status 的 VmRSS，对 nightly 进程与全部子孙**求和**；和 > 1484800 kB 即自动停（先子后父，TERM，10 秒后仍存活才 KILL，每次发信号前核 cmdline 与 PPID）。 |
| P2-5 | 快照用 v1（0aa6c650）+ 三项人工补偿 | **快照与 compare 用 v2** docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py（c930ed5c…），每次带 `--expect-scope-sha 579c8605…`；compare 退出码非 0 或含 META_ONLY_FAIL 即中止。r2 §5 的三项人工补偿不再需要（v2 内建）。 |
| P3-6 | run1 前备份 8 个文件 | 增加 output/data_v2_bundle/cyq/manifest.json 与 output/data_v2_bundle/cyq/cyq_perf_202610.parquet，共 10 个。 |
| P3-7 | 回执里 fallback r3.2 sha 写成 23d97887… | 更正为 **23d9788492f08c342f477c50fe6c03afb635720af13fe52b4f647c34f0de017b**（docs/v2/plans/DATA_DAILY_FALLBACK_PUBLIC_SOURCE_PLAN_ZH_r3_2.md，本次 sha256sum 复核）。 |

## 1. 执行器
- 路径：docs/v2/audit/backfill_1014_1016/run_backfill_r_v2.py
- sha256：28bc5e0e6304c31aa9d7a6c08b8e529ad6771973894bd0f6c136092edb6d71e0（641 行，只用标准库 + pyarrow 元数据读取，不 import 项目代码）
- 同目录 run_backfill_r.py（1e81c4f1…）是 11:18 的初稿，**作废、请勿钉、请勿运行**：判定函数遇异常（例如中转 fast-fail 后 10-16 manifest 不存在）会直接崩溃，漏写结果文件；v2 已修，并在 run2 判定里增查 summary steps.tier3/bundle/freshness 为 ok 且无 skipped。按规则不覆盖文件，所以初稿留在原处。
- 命令（单条，前台，由操作员在 94322 已 STOP 后执行）：
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/backfill_1014_1016/run_backfill_r_v2.py --quiet-evidence <RESEARCH_QUIET 证据文件> </dev/null
```
- 预检（不起任何运行，只核 .ok / 钉 sha / 时间 / 94322 状态 / 证据文件）：同上命令加 `--check-only`。
- 退出码：0 全过；1 判定或 compare 不过（已按规则中止，不起下一次）；2 前置条件不满足（未起任何运行）；3 RSS 或 15:55 截止触发了停进程。

### 1.1 执行器内部顺序（全部串行）
1. 解析 .ok：output/ai_factory/ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R.ok。要求 ok_id 相符、expires_et 带时区且在未来、allow_run_nightly_update_cyq=true、allow_run_nightly_update_tier3_bundle_freshness=true；若 .ok 写了 sha_* / scope_sha / sha_runner / rss_stop_kb，必须与执行器钉值一致；allow_daily_pull / allow_trade_cal / allow_sw / allow_force / allow_delete 任一为 true 即拒绝。
2. 钉 sha 全核（r2 §2 六个脚本 + 快照 v2 c930ed5c + 范围 579c8605 + daily_update_status 7991455a + tushare_raw/trade_cal 141078fa）；解释器必须是 /usr/bin/python3。
3. 时间：不在 16:40–18:40；run1 须在 14:45 前起。
4. /proc/94322/stat 第 3 字段须为 T（进程不存在则记录后继续，同 r1 §7）。
5. 第 0 步：两条命令各加 --dry-run 跑一次（nightly L106：dry-run 不起子进程、不探测中转；L137：不写 summary），日志写 /tmp/arch1018/backfill_dryrun_cmd1.log、cmd2.log（新文件，open 模式 x）。
6. run1 前备份（§2.1）→ SHA256SUMS_pre_run1（新文件、原子）。
7. 快照 before（v2）。
8. run1：`nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq`，stdout/stderr 追加到 logs/nightly/backfill_20261018_run1.out；RSS 采样写 /tmp/arch1018/backfill_rss_run1.log；wait 取 rc。
9. 快照 after_run1 + compare（before 对 after_run1）。
10. cyq 判定（r2 §6 run1 全部条目，执行器逐条机检，见 §3）；daily_update_status 仍为 7991455a。任一不过 → 退出 1，不起 run2。
11. 时间（run2 须在 15:00 前起）+ 94322 仍为 T + 7 个 20261016 目标文件均不存在。
12. run2 前备份（§2.2）→ SHA256SUMS_pre_run2。
13. run2：`--steps tier3,bundle,freshness`，同样采样 / wait。
14. 快照 after_run2 + compare（before 对 after_run2）。
15. run2 判定（r2 §6 tier3 / bundle / freshness 全部条目 + summary 状态）。
16. 写结果 JSON：docs/v2/audit/backfill_1014_1016/run_backfill_r_result_<时间>.json（新文件、原子），含每次运行的 NPID、出现过的全部 PID、开始 / 结束 ET、rc、RSS 采样峰值（和与单进程）、每条判定实测值、compare 输出尾部、94322 各时点状态、.ok sha、证据文件 sha。

### 1.2 执行器不做的事
- 不发 STOP / CONT 给 94322（操作员手工，执行器只核状态；结束时打印提醒）。
- 不移动 .ok 到 _consumed，不写回执、不写 TEAM_STATE（操作员 / Data 手工）。
- 不删任何文件；tier3 半写文件原样留给 Arch。
- 唯一的写回：cyq 判 FAIL 且 cyq_perf_202610.parquet 行数低于 22238 时，用备份原子恢复 cyq_perf_202610.parquet 与 data/v2/cyq/manifest.json（同目录 O_EXCL 临时文件 → fsync → sha 等于 SHA256SUMS_pre_run1 → os.replace → fsync 目录 → 再核 sha）。这是 r2 §6 已写的规则，现在自动化。**请 Arch 在 Q4 确认是否允许执行器自动做这一步**，不允许则改为只报告。

## 2. 备份（执行器内部 shutil.copy2，等同 cp -p；目标已存在即停）
目录 _recovery/data/backfill_1014_1016/（os.mkdir，已存在即停），保持相对路径。
### 2.1 run1 前（10 个）
data/v2/cyq/cyq_perf_202610.parquet、data/v2/cyq/manifest.json、logs/nightly/20261014_summary.json、logs/nightly/20261015_summary.json、logs/nightly/20261016_summary.json、output/relay_outage_backfill_queue.json、output/relay_health.json、output/data_freshness_status.json、**output/data_v2_bundle/cyq/manifest.json、output/data_v2_bundle/cyq/cyq_perf_202610.parquet（P3-6 新增）**。
### 2.2 run2 前（12 个，同 r2）
tier3_daily 下 concept_dc_index / concept_dc_member / anns / news / research_report 的 20261014、20261015.parquet，以及 manifests/20261014.json、20261015.json。
每个备份复制后立即比对 sha 与源一致；SHA256SUMS 每行「sha256␣␣相对路径」。

## 3. 判定（r2 §6 原文，执行器机检；以下只列 r3 的落地细节）
- cyq 日志段：记录 run1 前 logs/nightly/20261016_cyq.log 的字节长度（不存在记 0），只解析之后新增的内容。
- rows 精确相等：months.202610.rows == 22238 + 三天日志行数之和；备份 manifest 202610 rows 必须是 22238，否则判不过（基线已变，需人工看）。
- 202601–202609 manifest 条目逐项等于备份；月表与 ≤20261013 原始文件不变由快照 compare 保证。
- bundle：nightly L73、L81 对 ≥ 8 MB 的文件不复制、也不进 files 列表；执行器对这种情况记入 pit_flags.bundle_skip_ge_8mb，不判失败（r2 未写明，请 Arch 在 Q5 确认）。
- freshness generated_at_et：按 ISO 解析，须落在 run2 开始与结束之间。
- PIT 标注（r2 §6 末）：执行器把 available_at 写死值与实际拉取时段一并写入结果；concept_ths_index 若 ok，标「非 10-16 时点」。

## 4. RSS 自动停（P2-4）
- 采样：每 5 秒；对象 = nightly 进程（Popen 返回的确切 PID）+ /proc/<pid>/task/*/children 递归得到的全部子孙；读 /proc/<pid>/status VmRSS（kB），已退出记 0；求和。
- 阈值：和 > 1484800 kB。
- 动作：截止时刻重读子孙（P3-3），最深的先处理；每个 PID 发信号前核 cmdline（子进程须含 scripts/acquire/，nightly 须含 scripts/nightly_update.py）；不符则拒发并记录；TERM → 最多等 10 秒（Z 视为已退出）→ 仍存活才 KILL；已退出（ESRCH）不报错（P3-4）。然后父进程同样处理。
- 同一机制也用于 15:55 ET 截止。
- 采样日志：/tmp/arch1018/backfill_rss_runN.log（新文件，每行：时间、NPID、每个 pid:rss、和）。如实写明：这是 5 秒采样峰值，不是真实峰值（/usr/bin/time 未安装）。

## 5. 快照（P2-5）
```
S=docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt   # 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0
/usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py snap $S /tmp/arch1018/backfill_before.txt --expect-scope-sha 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0
/usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py snap $S /tmp/arch1018/backfill_after_run1.txt --expect-scope-sha 579c8605…（同上全长）
/usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py compare $S /tmp/arch1018/backfill_before.txt /tmp/arch1018/backfill_after_run1.txt --expect-scope-sha 579c8605…（同上全长）
（run2 同理：after_run2，compare 对 before）
```
以上由执行器调用（均加 nice -n 10、PYTHONDONTWRITEBYTECODE=1、stdin /dev/null），各自日志写 /tmp/arch1018/backfill_*.snaplog、backfill_compare_runN.log（新文件）。v2 自己保证：输出只能是新文件、范围 sha 不符即失败、两份快照范围 sha 必须相同、META_ONLY 计为失败（退出 1）。

## 6. 前置条件与占位证据（操作员 / Data 补）
1. 主 Agent 书面同意方案 R：已有（10:44）。
2. 中转探测两轮（probe 例程现用 index_member_all limit=5000 做大分页）：
| 轮 | 时间 ET | 接口 | 参数 | 耗时 | HTTP | 行数 | 结论 |
|---|---|---|---|---|---|---|---|
| P1 | 待补 | trade_cal | SSE 20261014–20261020 | 待补 | 待补 | 待补（应 7） | 待补 |
| P1 | 待补 | index_member_all | limit=5000 第 1 页 | 待补 | 待补 | 待补（完整一页 5000） | 待补 |
| P2 | 待补 | trade_cal | 同上 | 待补 | 待补 | 待补 | 待补 |
| P2 | 待补 | index_member_all | 同上 | 待补 | 待补 | 待补 | 待补 |
3. 94322 证据（待补）：STOP 前 `ps -o pid,ppid,stat,etimes,rss,args -p 94322`；`kill -STOP 94322` 后同一条 ps 与 /proc/94322/stat 第 3 字段 = T；结束后 `kill -CONT 94322` 后再一次 ps（S 或 R）。
4. RESEARCH_QUIET 证据（待补）：lock 文件路径与内容、设锁时间；设锁后等 15 秒；healthz 输出。整理成一个文本文件，路径作为 --quiet-evidence 传给执行器（执行器只记其 sha）。
5. Arch 审过本文、执行器 v2（28bc5e0e…）、范围（579c8605…）。
6. 13:30 ET 前拿到 .ok，否则放弃今天的补跑（r2 §9 不变）。

## 7. .ok 建议字段（Arch 签发时填写）
```
ok_id: ARCH_RUN_AUTH_DATA_BACKFILL_1014_1016_PLAN_R
ok_type: run
expires_et: 2026-10-18T15:55:00-04:00
single_use: true
sha_runner: 28bc5e0e6304c31aa9d7a6c08b8e529ad6771973894bd0f6c136092edb6d71e0
sha_nightly_update: ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636
sha_relay_health: 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f
sha_cyq_perf_monthly: 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f
sha_tier3_daily_snapshot: 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067
sha_data_freshness_status: a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50
sha_tushare_proxy: ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772
sha_snapshot_tool: c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a
scope_sha: 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0
rss_stop_kb: 1484800
allow_run_nightly_update_cyq: true
allow_run_nightly_update_tier3_bundle_freshness: true
allow_restore_cyq_202610_from_backup: true   # 仅当 Q4 同意
allowed_write: _recovery/data/backfill_1014_1016/**, /tmp/arch1018/backfill_*, logs/nightly/backfill_20261018_run{1,2}.out, docs/v2/audit/backfill_1014_1016/run_backfill_r_result_*.json, 以及范围文件中 EXPECTED_CHANGE 各项
```
注：执行器目前不读 allow_restore_cyq_202610_from_backup（恢复逻辑无条件按 r2 §6 执行）；Q4 若不同意，需要出 v3 去掉自动恢复。

## 8. 时间与放弃（r2 §9 不变，由执行器强制）
run1 14:45 前起、run2 15:00 前起、15:55 自动停、16:40–18:40 不跑；预计 run1 1–5 分钟、run2 30–45 分钟，含 dry-run 与三次快照约 45–60 分钟。目标 13:30 前完成。

## 9. 请 Arch 确认
- Q1–Q3：同 r2 §11。
- Q4：cyq 失败且 202610 月表行数低于 22238 时，执行器自动从备份原子恢复 cyq_perf_202610.parquet 与 manifest.json —— 同意，还是改为只报告？
- Q5：bundle 对 ≥ 8 MB 的 tier3 文件按 nightly 原逻辑不复制，执行器记录而不判失败 —— 是否同意？
- Q6：RSS 用子孙进程**求和**（比 r2 的单进程更严）—— 是否同意以和为准？
