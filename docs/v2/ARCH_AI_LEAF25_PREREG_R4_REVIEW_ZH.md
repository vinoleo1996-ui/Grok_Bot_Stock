# Arch 审查：AI 叶25 预注册 r4 + 步骤 −1 r2 包

- 审查人：QuantLab Arch。只做静态审查：读文档；算 sha256；用 pyarrow.parquet.read_schema 读列名（不读数据页）；脚本复制到 /tmp（set -euo pipefail，核对 pwd）只做 AST 检查，未执行；读包装器源码；没有运行项目代码，没有提交。
- 时间：2026-10-18T10:50:35-04:00（ET，取自 `date`）
- 上轮：docs/v2/ARCH_AI_LEAF25_PREREG_R3_REVIEW_ZH.md（fc5fa937）。live=false，promotion=false。本审查不签任何 .ok。

## 一、sha 核对
| 文件 | sha256 | 结果 |
|---|---|---|
| docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r4.md（142 行） | 6678c9b7bb459f5c7f96800c0a05154ca54adb6dd5eaee49be778b9279fc02e9 | ✔ |
| research/leaf25_ttm_recon_step_m1_r2.py（399 行，未跟踪） | f46e0fb5898ba58566c4c6fa6ed05b370a36a38941f766ffcbbee56d316956da | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R2.cmd | 73aceedc05716dd7fdf1c0908b6163a2958aa4c1688fd8ea2944735ab9e6b69f | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R2_MEM_ESTIMATE.md | e95db81ddf24f09aed904e96871b4a537260a5029c151c7f0216f631ea5e6dfd | ✔ |
| 旧件：step_m1.py / .cmd / 估计 | 7edf577f… / 6e01e1de… / bf2c29fe… | ✔ 未变 |
| 旧件：r1 / r2 / r3 | 993c4ce5… / 6dcc919d… / 0fb784f2… | ✔ 未变 |
| 输入（现值） | income bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3；cashflow 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79；balance 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5；calendar fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 | 与脚本 INPUTS 一致 |

## 二、结论
- **§2：PASS**（无 P1/P2；1 个 P3 文字澄清 R4-P3-1）。
- **r4 整体：PASS（有条件）**：r3 审查的 N-P2-1/2/3 与 N-P3-1~8 全部关闭；仍不可冻结——DIFF C r3b（913e6830）未审、共享函数未落地（r4 L5、L95）。
- **步骤 −1 静态：PASS（有条件）——现版本不签**。脚本正确性无问题，但有 1 个 P2（S-P2-1：规则 (i) 选例按“最新报告期”而非回退后的期判断，单次 .ok 有较大概率以 rc=4 白白作废）。须出 research/leaf25_ttm_recon_step_m1_r3.py（新文件名）修 S-P2-1，并顺带修 S-P3-1；改完只需 Arch 复核差异即可进入签发前置。

## 三、r3 审查发现关闭情况（r4 行号）
| 项 | r4 位置 | 判定 |
|---|---|---|
| N-P2-1 report_type 标签 | L74、L76；脚本 L99–L100、L120–L129、L253–L254、L365 | ✔ 只认「1」；空值记为 <NULL> 不映射；三表逐值计数（全表/2018 起）写入 run_meta；>0.5% 标记 arch_ruling |
| N-P2-2 单名上限 | L109 | ✔ 两档 6%、余额 510300，依据写明 |
| N-P2-3 选例/日期/rule_exercised | L132–L137；脚本 L257–L351 | ✔ 触发元组全程携带；但规则 (i) 的期判断见 S-P2-1 |
| N-P3-1 fina 列禁用 | L63；脚本 L58–L60 | ✔ AST/文本扫描：正文无 eps/roe/bps/profit_dedt/fina_ |
| N-P3-2 孤立更正 | L77；脚本 L132–L136 | ✔ |
| N-P3-3 与叶19 版本口径差异 | L55 | ✔（r4 §0 写 §5，实际在 §0.1 L55，可接受） |
| N-P3-4 两份年报规则 | L82 | ✔ 删除并披露 |
| N-P3-5 第二阶段内存 | L130；估计文 | ✔ |
| N-P3-6 --out 检查 | 脚本 L225 | ✔ OUT_BASE.resolve() 须在 out.parents 中：基目录本身、同名前缀目录都被拒 |
| N-P3-7 --meta | .cmd | ✔ 见第四节 (iii) |
| N-P3-8 新文件名 | 全部 | ✔ |
| 覆盖出处 | L4 | ✔ mtime 10:33:22 ET 与本人上轮所见一致 |

### R4-P3-1 一季报早于年报时的结果（r4 L83）
r4 L83 写「Q1 earlier than annual → fallback rule」。按 §2.3 L79 回退最多一季：最新期为 Q1(y)，可回退的上一季正是尚未披露的年报 A_{y−1}，再往前的 Q3(y−1) 已超一季上限 → 该段时间 **TTM = NaN**，不是取到某个回退值。L83 改为「→ NaN until the annual is usable（fallback cap of one quarter），counted」。代码（L166 的 break）与此一致。

## 四、步骤 −1 r2 脚本静态复审
| 项 | 结果 |
|---|---|
| import | __future__、argparse、datetime、hashlib、json、pathlib、resource、sys、zoneinfo、pandas、pyarrow.parquet ✔；无 subprocess/os.system/research.*/quantlab.* |
| 读取 | 只有 pq.read_schema、pq.read_table(path, columns=…, filters=…)、日历两列 ✔；第一阶段 5 键列全表（选例必需），第二阶段按 ts_code 过滤 ✔ |
| 列名（schema 复读） | financials_pit_tushare：ts_code、end_date、ann_date、f_ann_date、available_at、update_flag、report_type、n_income、n_income_attr_p 全在；cashflow：键列 + n_cashflow_act 全在；balancesheet：键列 + total_assets 全在；日历 cal_date、is_open 全在 ✔ |
| sha 自检 | L229–L234 全长比对，不符 exit 3 ✔ |
| 写入 | 只有 out.mkdir、raw_rows.csv、ttm_script.csv、run_meta.json ✔ |
| rc=4 | L356–L371 先写三份输出（run_meta 内 rc=4），L374–L376 再返回 4 ✔。注意：包装器对 rc≠0 会把 --outdir 中启动后新建的文件移到 output/ai_factory/_void/leaf25_step_m1_r2_rc4_<时间>/（包装器 L95–L96），峰值读取（L90–L91）在移动之前，不受影响。复核时到 _void 取件 |
| <4 个 as-of 日 | L352–L354 exit 3（在写输出前）✔ |
| 触发元组携带 | trig_i/ii/iii 由第一阶段产生，第二阶段只用它们；run_meta 写出 triggers ✔ |
| report_type 计数 | L250、L365 写入 report_type_update_flag_counts；L253 写 arch_ruling 标记 ✔ |
| JSON | Timestamp 走 default=str；numpy float64 为 float 子类可序列化；NaN 写为 NaN ✔ |

### (i) as-of TTM 用最新期还是回退后的期
- 按 §2.3（r4 L79）：当日 TTM 用“各分量都可用的最新期 E”，必要时回退一季；判断某次更正是否进入当日 TTM，应以**回退后的 E** 为准。
- `ttm_at`（L157–L202）本身正确：按 E 降序找第一个分量齐全的期，并受一季、15 个月两道上限约束 ✔。
- **S-P2-1**：规则 (i) 选例（L273–L277）用的是 d_after 当天“可用收入表的最大 end_s”，即最新期，**不是回退后的 E**；而且只检查 d_after，不检查 d_before。rule_exercised 的判定（L329–L331）却要求被更正期在 d_before、d_after 两天的 TTM 键里都出现。典型反例：更正与下一期定期报告同日披露——d_after 的 E 是新期，被更正期是它的 YTD_{E−1y}；d_before 的 E 是上一期，组件集合不同，key_before 为 None → rule_exercised=false → rc=4，单次 .ok 作废。结论安全（不会误判为已验证），但浪费授权的概率不低。
- 要求（_r3）：选例时用与 ttm_at 相同的可用性规则（只看可得日、不看数值）分别求 d_before、d_after 的回退后 E，并要求被更正期同时属于两天对应表的组件期集合，才取该代码。

### (ii) 一季报早于年报的判定
- 候选条件 L288 为 `avail_q <= avail_a`（不晚于），同日与 Q1 先出两种都纳入 ✔，不是只认同日；same_day 标记区分 ✔；全体计数 n_same_day、n_q1_first 都写入 ✔。
- 同日分支（L340–L342）要求 status=OK、E=Q1(y)、income_A_key 以 (y−1)-12-31 开头 ✔，判定有力。
- **S-P3-1**：Q1 先出分支（L343–L344）只要求“不是 OK 且 E=Q1(y)”，过宽：若代码误回退到 Q3(y−1)（违反一季上限）也会判 true。按 R4-P3-1 应要求 status 以 NaN 开头。手算对账会逐行复核，此项不单独阻断，但 _r3 一并改。

### (iii) 包装器 v4 的 --meta 与 --assert
- --meta：L17 只记录路径；L90–L91 在命令结束后才读，且先判断 `[ -f "$META" ]`，文件不存在则跳过（P4/P5/P6 为空），**启动前不校验存在性** → 运行后才生成的 run_meta.json 可以接受 ✔。读取用 jq（/usr/bin/jq 存在）取 .peak_rss_kb，脚本 meta 有该键 ✔；.vm_peak_kb 不入峰值 ✔。
- --assert：L68 在启动后 5 秒内反复 `grep -qa -- "$ASSERT" /proc/$PID/cmdline`，是对整条命令行的**子串匹配**，不是对脚本 basename 的精确匹配。setsid 先起 env，再 exec 为 python，同一 PID，两个阶段的命令行都含脚本路径 ✔。「leaf25_ttm_recon_step_m1_r2」命中 research/leaf25_ttm_recon_step_m1_r2.py；--out 路径只含 _leaf25_ttm_recon，不会误命中 ✔。注意旧名「leaf25_ttm_recon_step_m1」会同时命中所有版本，故必须带版本后缀；_r3 落地后 --assert 改为 leaf25_ttm_recon_step_m1_r3。
- .ok：包装器只要求文件存在并记录其 sha（L25），只读 allow_no_guard、allow_c5_ignore 两个键；其余键由 Arch 签发时人工核对。guard 默认 94322，T 或已退出才启动、运行中离开 T 即停组（L35、L39、L76）✔。

### .ok 路径
- 现有惯例：真实数据运行授权用 ARCH_RUN_AUTH_<名>.ok 放在 output/<域>/ 下；只读且不读数值的用 ARCH_READONLY_AUTH_（如 7NAME，allow_real_data_values=false）。步骤 −1 会读财报数值，属 RUN_AUTH。
- 建议：`output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R3.ok`（若按现 _r2 签则为 …_R2.ok，AI 所提路径符合惯例）；用后归档为 `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R3_<sha8>_CONSUMED_<YYYYMMDD_HHMM>ET.ok`（rc=4 时用 `_VOID_RC4_RULE_NOT_EXERCISED_`）。

### 内存
估计典型约 466000 kB、最坏约 650 MB：**可信**。补充：L262 的 inc_by 按代码拆约 5900 个小表，多出几十 MB 对象开销，仍在最坏估计内；离 C4 1331200 余量约一半。不需要改读法。

## 五、观察（不计发现）
主 Agent / Leo 侧裁定：在 /tmp 用 shell heredoc 写纯 ASCII 的 Python 脚本不违反规则；禁 heredoc 只针对中文文档。记录为观察。

## 六、步骤 −1 .ok 应写入的键（签发时以届时实测为准）
```
format=quantlab_run_auth_v1
signed_by=arch
leaf=25
mechanism_tag=g1g5_ashare_cfacc_desens_cs_v1
purpose=step_m1_ttm_hand_reconciliation
prereg_sha256=6678c9b7bb459f5c7f96800c0a05154ca54adb6dd5eaee49be778b9279fc02e9   (若 r4 再修订则改钉)
script_path=/workspace/QuantLab/research/leaf25_ttm_recon_step_m1_r3.py       (现 _r2：f46e0fb5898ba58566c4c6fa6ed05b370a36a38941f766ffcbbee56d316956da)
script_sha256=<_r3 全长 sha>
cmd_path=/workspace/QuantLab/docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R3.cmd   (现 _R2：73aceedc05716dd7fdf1c0908b6163a2958aa4c1688fd8ea2944735ab9e6b69f)
cmd_sha256=<R3 全长 sha>
mem_estimate_sha256=<对应版本；现 R2 e95db81ddf24f09aed904e96871b4a537260a5029c151c7f0216f631ea5e6dfd>
wrapper_sha256=6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169
interpreter=/workspace/qlvenv/bin/python
env=PYTHONDONTWRITEBYTECODE=1
assert=leaf25_ttm_recon_step_m1_r3                                            (现 _r2)
tag=leaf25_step_m1_r3
input_income_sha256=bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3      (签发时重算重钉)
input_cashflow_sha256=71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79    (同上)
input_balance_sha256=9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5     (同上)
input_calendar_sha256=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41    (同上)
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
out_dir=/workspace/QuantLab/output/ai_factory/_leaf25_ttm_recon/<YYYYMMDD_HHMMSS>/   (签发时写成字面值)
log_dir=/workspace/QuantLab/output/ai_factory/_leaf25_ttm_recon/<YYYYMMDD_HHMMSS>_logs/
meta=<out_dir>/run_meta.json
guard_pid=94322
c4_limit_kb=1331200
stopkb=1484800
rss_limit_kb=1536000
expected_peak_kb=650000            (超过只记 P3 复核，不作废)
expected_rc=0                      (rc=4 = rule_exercised 为 false：停、报；rc=3 = sha/列/日期数不符)
run_serial=true
single_use=true
run_niceness=10
live=false
promotion=false
promotion_approved=false
research_only=true
forbidden_window_et=2026-10-19T16:40/2026-10-19T18:40
signed_et=<date>
issued_at=<date>
expires_et=<date；有效期不超过 24 小时，且不得覆盖禁止窗>
```

## 七、签发前仍须满足
1. AI 提交 research/leaf25_ttm_recon_step_m1_r3.py（修 S-P2-1、S-P3-1）及对应 R3 .cmd（--assert …_r3、--tag …_r3、.ok 路径 …_R3）与估计文；Arch 只复核差异。r4 L83 按 R4-P3-1 改字（可在 r5 或签发前修正说明）。
2. Data 今日 10-14→10-16 补跑已结束（或 16:00 ET 放弃），Arch 核完补跑前后 sha；四个输入文件在签发时重算，若有变化则脚本再换新文件名重钉。
3. 94322 处于 T 或已退出，附 Data 的 ps 证据（前、后各一次）。
4. 设 RESEARCH_QUIET.lock，等 ≥15 秒，附三项证据：pgrep -P <server.py PID> 为空；全机无 gen/snapshot/kline/export_static 进程及 deploy_loop 此类子进程；localhost:8795/healthz 显示 gen_running=false（Web v2.1 安装回执核验前有效）。
5. 单进程、不重试；不落在 10-19 16:40–18:40 ET；不与 Data 补跑重叠。
6. 退出码 0 不等于成功：逐个核对三份输出、triggers、每例 rule_exercised 与 report_type 计数；任一非「1」值占比 >0.5% 先裁定再谈冻结。
