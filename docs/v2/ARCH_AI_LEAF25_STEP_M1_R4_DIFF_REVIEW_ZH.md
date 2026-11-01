# Arch 差异复核：AI 叶25 步骤 −1 r4 包（_r4 脚本 / R4 .cmd / R4 内存估计）

- 审查人：QuantLab Arch。只做静态、只看差异：算 sha256；在 /tmp/l25r3（set -euo pipefail，已核对 pwd）独立重算 diff -u；AST 逐函数比对 _r3 与 _r4；/tmp 虚拟环境跑 pyflakes；日历只用 pq.read_metadata 读页脚统计（不读数据页）。没有运行项目脚本，没有 git apply，没有提交。
- 时间：2026-10-18T11:01:11-04:00（ET，取自 `date`）
- 上轮：docs/v2/ARCH_AI_LEAF25_STEP_M1_R3_DIFF_REVIEW_ZH.md（1b63c05f4d5b45fd0dff22dd540208e75e55a5d59cd901580969a5c3548fa521）。live=false，promotion=false。本审查不签任何 .ok。

## 一、sha 核对（全长）
| 文件 | sha256 | 结果 |
|---|---|---|
| research/leaf25_ttm_recon_step_m1_r4.py | 2f7ea7138c7f4b91eab77e169c48b65538b98f4cba5763fa358dade32b2797de | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R4.cmd | 7a18fb34987284c0482f821c3abaea3a95917b87fa8733d98cb53c59db93c42d | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R4_MEM_ESTIMATE.md | 618b76533d32b6e6a36618dc21b8c025b696b7b1c6f031ada7fee96fd4e717d6 | ✔ |
| DIFF_step_m1_r3_to_r4.diff / DIFF_cmd_R3_to_R4.diff / DIFF_mem_R3_to_R4.diff | bb1d767cfa8b5ca0e100ed847b53e6897ad829d60fc3fc04425d95d67d480a5f / bd3dc3cfd353aef16ec96053badc3854faa24604ad69880aec74e17696e315c2 / c2762f20bb5063f6265f0ac003a42b7bde707bbaadf73ab4b9139132e8791c66 | ✔ |
| 旧件 _r3.py / R3 .cmd / R3 估计 | eb979015… / 8a3024c4… / 198c60d6… | ✔ 未变 |
| 旧件 _r2.py | f46e0fb5… | ✔ 未变 |
| 预注册 r5 / r4 | 81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1 / 6678c9b7… | ✔ 未变（目录中无 r6） |
| 包装器 v4 | 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 | ✔ |
| 输入现值 | income bc0f4c3d…；cashflow 71d5c3d3…；balance 9ca05496…；calendar fa4260b8… | ✔ 与 _r4 INPUTS 一致（INPUTS 不在 diff 内） |

## 二、diff 忠实性
三对文件独立重算 `diff -u`，去掉头行后与 AI 的三份 diff 逐字节一致 ✔。

## 三、结论
- **PASS（有条件）**。无 P0/P1/P2。R3-P3-1、R3-P3-2 **关闭**，修法正确，没有引入新的 rc=4 或假通过路径。
- 新发现 1 个 P3（R4-P3-1，_r2 起就存在，非 r4 引入），不阻断，处理意见见第五节。
- 条件 = 第七节签发前置。

## 四、修复核查
### AST 与范围
- 逐函数比对：avail_E、periods、ttm_at、pick、component_periods、find_key、keystr、norm、read_keys、value_counts、orphan_groups、extra_dates、next_open、prev_open、run、stage、sha256、die、vmhwm_kb **全部相同**；只有 main 变化 ✔。模块级常量（INPUTS、KEY、VAL、TABLES 等）相同 ✔；main 顶层语句数 89 = 89。
- main 的变化只有四处：L298–L299 新增跳过、L322 same_day、L388 run_meta.script、L399 peak_check 文字 ✔。其余为文档字符串（L2–L5、L14 改钉 r5 81123646、L33–L36 规则说明）✔。L310 的候选筛选 `avail_sh_date_q <= avail_sh_date_a`（_r4 L314）未变 ✔。

### R3-P3-1（_r4 L298–L299）——关闭 ✔
- dd 已排序去重，dd[2] > dd[1]，故 next_open(dd[2]) ≥ next_open(dd[1]) = d_after；条件 `next_open(dd[2]) <= d_after` 等价于 dd[2] 与 dd[1] 落在同一生效日，正是上轮反例 ✔。
- 只查 dd[2] 已足够：dd[3] > dd[2]，若 dd[2] 在 d_after 不可用，dd[3] 更不可用 ✔。
- 跳过发生在 avail_E 之前，只减少候选、不放宽任何判定，不会产生假通过 ✔。保留下来的候选在 d_after 的最新可用版本必为 dd[1]，L355–L357 的 ka 判定成立。
- 候选池变空的风险：仅当所有候选都被跳过才会 die（rc=3，L307–L308，在 mkdir 之前，无输出、包装器作废），r3 选例已有 avail_E 两天条件，r4 只多剔除“更正后同生效日又有新版本”的极少数组；实际不会耗尽。最坏结果是 rc=3 浪费一张 .ok，不是错判。

### R3-P3-2（_r4 L322）——关闭 ✔
- same_day 改为 next_open(q_date) == next_open(a_date)。因候选已满足 q_date ≤ a_date：
  - 同生效日：dq = da，dq 当天 Q1(y) 与 A_{y−1} 收入行都可用 → 期望 OK、E=Q1、A 键为 (y−1)-12-31（L366–L368）✔；
  - 不同生效日：next_open(a_date) > dq，即 a_date ≥ dq，dq 当天年报不可用，ttm_at 必在一季上限处 break → NaN（L369–L370 期望 NaN）✔。两分支现在与生效日定义完全一致。
- n_annual_q1_same_day_all_codes（L315）仍按自然日计数，只作披露，不进判定；可接受，建议在结果说明中注明口径不同（观察）。

### next_open 越界
- 日历只读页脚统计：8035 行、1 个行组，cal_date 最小 20050101、最大 20261231。next_open(x) 只在 x ≥ 最后一个开市日（2026 年末）时 IndexError。dd[2]、q_date、a_date 都是数据中已有的可得日（不晚于今天 2026-10-18），且 r3 起 next_open(corr)、dq、da 就已有同类调用，r4 没有引入新风险类。若真有未来日期的异常行，结果是未捕获异常、rc=1、包装器作废，不是假通过（观察，不计发现）。2027 日历由 Data 另行负责，与本次无关。

### 其他
- pyflakes（/tmp/l25r3/venv）对 _r4 副本 rc=0，无输出 ✔。
- 新增只有标量 next_open 比较，无新 DataFrame，无新 I/O；写入仍只有 --out 下三份文件 ✔。内存估计“数值不变”成立 ✔。
- 日期类型：next_open 的入参是 Timestamp（us），与 opens（us）比较，无单位问题 ✔。
- **.cmd（R4）**：与 R3 相比只把 r3 改为 r4（注释三行、--arch-ok …_R4.ok、--assert leaf25_ttm_recon_step_m1_r4、--tag leaf25_step_m1_r4、脚本路径 _r4）✔；包装器 6174eacb、解释器 /workspace/qlvenv/bin/python、env、--meta、logdir/outdir 不变 ✔。--assert 子串只命中 _r4 脚本路径 ✔。

## 五、发现
### R4-P3-1（P3，_r4 L317–L322、L366–L368；_r2 起即存在，非 r4 引入）：规则 (ii) 同日分支只看收入表
trig_ii 只按收入表的可得日选例。同日分支期望 dq 当天 status=OK 且 E=Q1(y)，这还要求现金流表 Q1(y)、A_{y−1}、Q1(y−1) 与资产负债表 Q1(y)、Q1(y−1) 在 dq 都可用。若某表的 available_at 晚于收入表（例如分表拉取时间不同），ttm_at 会回退或给 NaN，ok_ii=false → rc=4。安全失败，不会假通过。不同生效日分支不受影响（收入年报不可用即 NaN）。
- 可选修法（一行）：选 jj 时，对 same_day 候选要求 `avail_E(code, next_open(q_date), G) == Q1(y)`（G 在 L331 才删除，此处可用），不满足则取下一个候选。
- 处理意见：不阻断。若 AI 能在 Data 补跑完成前交 _r5（新文件名、R5 .cmd、差异复核一次），值得修；否则按 _r4 签发，并在 .ok 备注里接受这一 rc=4 风险。由主 Agent 定。

## 六、观察
- n_annual_q1_same_day_all_codes 为自然日口径，与判定用的生效日口径不同，结果说明中注明。
- 内存估计沿用：典型约 466000 kB，最坏约 665000 kB，报告线 650000 超过只记 P3。

## 七、.ok 终值（按 _r4 签发时；签发人填写，本审查不签）
沿用 efb013d8 第六节键表，以下各项取本轮值：
```
prereg_sha256=81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1
script_path=/workspace/QuantLab/research/leaf25_ttm_recon_step_m1_r4.py
script_sha256=2f7ea7138c7f4b91eab77e169c48b65538b98f4cba5763fa358dade32b2797de
cmd_path=/workspace/QuantLab/docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R4.cmd
cmd_sha256=7a18fb34987284c0482f821c3abaea3a95917b87fa8733d98cb53c59db93c42d
mem_estimate_sha256=618b76533d32b6e6a36618dc21b8c025b696b7b1c6f031ada7fee96fd4e717d6
wrapper_sha256=6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169
interpreter=/workspace/qlvenv/bin/python
env=PYTHONDONTWRITEBYTECODE=1
assert=leaf25_ttm_recon_step_m1_r4
tag=leaf25_step_m1_r4
ok_path=output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R4.ok
input_income_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3     (签发时重算重钉)
input_cashflow_sha256=71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79   (同上)
input_balance_sha256=9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5    (同上)
input_calendar_sha256=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41   (同上)
guard_pid=94322
c4_limit_kb=1331200
stopkb=1484800
rss_limit_kb=1536000
expected_peak_kb=650000
expected_rc=0
single_use=true
run_serial=true
live=false
promotion=false
forbidden_window_et=2026-10-19T16:40/2026-10-19T18:40
signed_et / issued_at / expires_et = `date +%Y-%m-%dT%H:%M:%S%:z`（有效期不超过 24 小时，不得覆盖禁止窗）
out_dir / log_dir 写成字面值
note=若不修 R4-P3-1，写明接受规则 (ii) 同日分支因分表可得日不同而 rc=4 的风险
```

## 八、签发前仍须满足
1. **补跑完成并重钉输入 sha**：Data 10-14→10-16 补跑结束（或 16:00 ET 放弃），Arch 核完前后 sha；签发时重算四个输入 sha。任一变化 → 脚本 INPUTS 改钉、换新文件名并再做差异复核。
2. **94322 处于 T 状态或已退出**，附 Data 的 ps 证据（签发前、启动前各一次）。
3. **静默门禁**：设 RESEARCH_QUIET.lock，等待 ≥15 秒，留存 localhost:8795/healthz 证据：quiet=true、gen_running=false、child_pids={}。
4. 单进程、单次、不重试；不落在 10-19 16:40–18:40 ET；不与补跑或其他真实数据进程重叠。
5. 退出码 0 不等于成功：逐个核对三份输出、triggers（E_before / E_after、same_day）、每例 rule_exercised 与 report_type 计数；rc≠0 到 output/ai_factory/_void/ 取件。用后归档 _consumed/（sha8 + CONSUMED/VOID + ET 时间）。
