# Arch 差异复核：AI 叶25 步骤 −1 r5 包（_r5 脚本 / R5 .cmd / R5 内存估计）

- 审查人：QuantLab Arch。只做静态、只看差异：算 sha256；在 /tmp/l25r3（set -euo pipefail，已核对 pwd）独立重算 diff -u；AST 逐函数比对 _r4 与 _r5；/tmp 虚拟环境跑 pyflakes；用 /workspace/qlvenv 的 pandas 3.0.6 只对合成 DataFrame 做 iterrows 类型实验（不导入项目代码、不读数据）。没有运行项目脚本，没有 git apply，没有提交。
- 时间：2026-10-18T11:05:02-04:00（ET，取自 `date`）
- 上轮：docs/v2/ARCH_AI_LEAF25_STEP_M1_R4_DIFF_REVIEW_ZH.md（3c508dd77505e9e8fe8b9329d91205d51e483964565186b337fffecc67fbe066）。live=false，promotion=false。本审查不签任何 .ok。

## 一、sha 核对（全长）
| 文件 | sha256 | 结果 |
|---|---|---|
| research/leaf25_ttm_recon_step_m1_r5.py | f43b901671728204437279da1f49c7729ec11f11d8070e73434b5d6288953d68 | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5.cmd | 0f48bc428cbcd292d901b6be27333207f4678257204b9c25be8d65ae19ad31d7 | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5_MEM_ESTIMATE.md | c2fef26b1911b061b6c61137737cc5c52ebb6233e98d7566239de06525822e24 | ✔ |
| DIFF_step_m1_r4_to_r5.diff / DIFF_cmd_R4_to_R5.diff / DIFF_mem_R4_to_R5.diff | 4675b96d5583e0099b0bd3e01c5d3000f93e0a7c05ead62b778ff64a6765bd8f / 848a724b681b3ac4528a184d0514e1c7c7550b110ba343f9556d62597ef61916 / df357b2ef9b7bdd11e0dab8e6c61c0cd4b22c409bc46457557dba3bece710330 | ✔ |
| 旧件 _r4.py / R4 .cmd / R4 估计 | 2f7ea713… / 7a18fb34… / 618b7653… | ✔ 未变 |
| 旧件 _r3.py | eb979015… | ✔ 未变 |
| 预注册 r5 | 81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1 | ✔ 未变（无 r6） |
| 包装器 v4 | 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 | ✔ |
| 输入现值 | income bc0f4c3d…；cashflow 71d5c3d3…；balance 9ca05496…；calendar fa4260b8… | ✔ 与 _r5 INPUTS 一致（INPUTS 不在 diff 内） |

## 二、diff 忠实性
三对文件独立重算 `diff -u`，去掉头行后与 AI 的三份 diff 逐字节一致 ✔。

## 三、结论
- **PASS（有条件）**。无 P0/P1/P2/P3。R4-P3-1 **关闭**，修法正确，没有引入新的假通过路径，新增的 rc=3 路径在任何写入之前。
- 脚本、.cmd、估计文可按本轮 sha 进入签发流程；条件 = 第七节签发前置。本系列（S-P2-1、S-P3-1、R4-P3-1〔预注册〕、R3-P3-1、R3-P3-2、R4-P3-1〔脚本〕）全部关闭。

## 四、修复核查
### AST 与范围
- 逐函数比对：avail_E、periods、ttm_at、pick、component_periods、find_key、keystr、norm、read_keys、value_counts、orphan_groups、extra_dates、next_open、prev_open、run、stage、sha256、die、vmhwm_kb **全部相同**；只有 main 变化 ✔；模块级常量相同 ✔。
- main 的变化只有：L321–L323（选例 + 空则 die）、L391 run_meta.script、L402 peak_check 文字 ✔。文档字符串 L2–L5、L36–L37 同步说明 ✔。L315 候选筛选 `avail_sh_date_q <= avail_sh_date_a` 未变 ✔；trig_ii 字典（L324–L325）未变 ✔。

### R4-P3-1（_r5 L321–L323）——关闭 ✔
- 生成器按 jj 原有排序（ts_code、y）逐行取第一个满足条件者：不同生效日候选（next_open(q) != next_open(a)）短路为真，行为与 _r4 完全相同 ✔；同生效日候选要求 `avail_E(code, next_open(q_date), G) == Q1(y)`。
- 正确性：avail_E 返回 Q1(y) 意味着 dq 当天三表的全部分量期（收入/现金流 Q1(y)、A_{y−1}、Q1(y−1)；资产负债表 Q1(y)、Q1(y−1)）都有可用行。avail_E 与 ttm_at 的选 E 规则逐字等价（r3 复核已证），故第二阶段 ttm_at 在 dq 必选 E=Q1(y)；收入 A 键必为 (y−1)-12-31 开头。L369–L371 的同日判定因此成立 ✔。
- G 的生命周期：G 在 L290 建立、L334 才删除，L321 使用时仍在 ✔。
- 不会假通过：新条件只减少候选，判定条件（L369–L373）未放宽 ✔。

### 新增 rc=3 路径
- L322–L323：所有候选都不满足时 die（rc=3）。位置在第一阶段，早于 L336 stage("phase1_pick")、第二阶段读取与 L385 的 out.mkdir，**不写任何文件** ✔。包装器按 rc≠0 处理；结果是浪费一张 .ok，不是错判。jj 中不同生效日候选恒满足条件，实际耗尽概率极低。
- L319–L320 原有的 jj.empty die 保留，两处信息相同，可接受。

### 类型
- avail_E 返回值来自 `set(g.loc[..., "end_s"])` 的元素，为 pd.Timestamp（us）或 None；比较对象 `pd.Timestamp(year=int(r["y"]), month=3, day=31)` 为 pd.Timestamp（us）。r3 复核已证 s/us/ns 单位间相等与 hash 一致 ✔。返回 None 时 `None == Timestamp` 为 False，候选被跳过，不报错 ✔。
- 合成实验（pandas 3.0.6）：iterrows 对 str / int64 / datetime64[us] 混合列逐行返回 str、int、Timestamp（us），next_open 入参类型与 _r4 相同 ✔；空迭代时 next(…, None) 返回 None ✔。

### 其他
- pyflakes（/tmp/l25r3/venv）对 _r5 副本 rc=0，无输出 ✔。
- 无新 I/O；写入仍只有 --out 下三份文件 ✔。
- 内存：只复用已有的 G，逐行惰性迭代、命中即停，无新 DataFrame；iterrows 每行一个小 Series，可忽略。估计文“数值不变”成立 ✔。耗时：每个同生效日候选 1 次 avail_E（3 次 get_group），秒级。
- **.cmd（R5）**：与 R4 相比只把 r4 改为 r5（注释三行、--arch-ok …_R5.ok、--assert leaf25_ttm_recon_step_m1_r5、--tag leaf25_step_m1_r5、脚本路径 _r5）✔；包装器 6174eacb、解释器 /workspace/qlvenv/bin/python、env、--meta、logdir/outdir 不变 ✔。--assert 子串只命中 _r5 脚本路径 ✔。

## 五、发现
无 P0–P3。

## 六、观察（不计发现）
- n_candidates.ii（L332）仍为 jj 筛选前的代码数，不反映因 avail_E 跳过的同日候选数；结果说明中注明即可，不需改代码。
- 理论残余：若某代码在 Q1(y) 首次生效日之前已有比 Q1(y) 更新的收入期（数据异常），avail_E 可能以回退方式返回 Q1(y)，ttm_at 给 FALLBACK → rc=4。只有数据异常时才会出现，且安全失败。
- n_annual_q1_same_day_all_codes 仍为自然日口径，只作披露（同上轮）。
- next_open 越界（日历止于 20261231）：同上轮，无新风险。

## 七、.ok 终值（按 _r5 签发；签发人填写，本审查不签）
沿用 efb013d8 第六节键表，以下各项取本轮值：
```
prereg_sha256=81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1
script_path=/workspace/QuantLab/research/leaf25_ttm_recon_step_m1_r5.py
script_sha256=f43b901671728204437279da1f49c7729ec11f11d8070e73434b5d6288953d68
cmd_path=/workspace/QuantLab/docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5.cmd
cmd_sha256=0f48bc428cbcd292d901b6be27333207f4678257204b9c25be8d65ae19ad31d7
mem_estimate_sha256=c2fef26b1911b061b6c61137737cc5c52ebb6233e98d7566239de06525822e24
wrapper_sha256=6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169
interpreter=/workspace/qlvenv/bin/python
env=PYTHONDONTWRITEBYTECODE=1
assert=leaf25_ttm_recon_step_m1_r5
tag=leaf25_step_m1_r5
ok_path=output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5.ok
input_income_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3     (签发时重算重钉)
input_cashflow_sha256=71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79   (同上)
input_balance_sha256=9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5    (同上)
input_calendar_sha256=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41   (同上)
column_whitelist=ts_code,end_date,ann_date,f_ann_date,available_at,update_flag,report_type,n_income,n_income_attr_p,n_cashflow_act,total_assets,cal_date,is_open
allow_read_financials_pit=true
allow_read_prices=false
allow_read_returns=false
allow_read_weights=false
allow_read_factors=false
allow_fina_indicator_columns=false
allow_write_outside_out=false
allow_no_guard=false
allow_c5_ignore=false
guard_pid=94322
c4_limit_kb=1331200
stopkb=1484800
rss_limit_kb=1536000
expected_peak_kb=650000
expected_rc=0
run_serial=true
single_use=true
live=false
promotion=false
promotion_approved=false
research_only=true
forbidden_window_et=2026-10-19T16:40/2026-10-19T18:40
signed_et / issued_at / expires_et = `date +%Y-%m-%dT%H:%M:%S%:z`（有效期不超过 24 小时，不得覆盖禁止窗）
out_dir / log_dir / meta 写成字面值
```

## 八、签发前仍须满足
1. **补跑完成并重钉输入 sha**：Data 10-14→10-16 补跑结束（或 16:00 ET 放弃），Arch 核完前后 sha；签发时重算四个输入 sha。任一变化 → 脚本 INPUTS 改钉、换新文件名并再做差异复核。
2. **94322 处于 T 状态或已退出**，附 Data 的 ps 证据（签发前、启动前各一次）。
3. **静默门禁**：设 RESEARCH_QUIET.lock，等待 ≥15 秒，留存 localhost:8795/healthz 证据：quiet=true、gen_running=false、child_pids={}。
4. 单进程、单次、不重试；不落在 10-19 16:40–18:40 ET；不与补跑或其他真实数据进程重叠。
5. 退出码 0 不等于成功：逐个核对三份输出、triggers（E_before / E_after、same_day）、每例 rule_exercised 与 report_type 计数；rc≠0 到 output/ai_factory/_void/ 取件。用后归档 _consumed/（sha8 + CONSUMED/VOID + ET 时间）。
