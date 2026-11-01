# Arch 差异复核：AI 叶25 步骤 −1 r3 包（_r3 脚本 / R3 .cmd / R3 内存估计 / 预注册 r5）

- 审查人：QuantLab Arch。只做静态、只看差异：算 sha256；在 /tmp/l25r3（set -euo pipefail，已核对 pwd）独立重算 diff -u；AST 逐函数比对 _r2 与 _r3；/tmp 虚拟环境跑 pyflakes；用 /workspace/qlvenv 的 pandas 3.0.6 仅对合成 Timestamp 做类型实验（不导入项目代码、不读任何数据页）。没有运行项目脚本，没有 git apply，没有提交。
- 时间：2026-10-18T10:55:41-04:00（ET，取自 `date`）
- 上轮：docs/v2/ARCH_AI_LEAF25_PREREG_R4_REVIEW_ZH.md（efb013d87397e2f344bf03f7b718c78c3ea7d0ec17483c6e5288d0a0363df651）。live=false，promotion=false。本审查不签任何 .ok。

## 一、sha 核对（全长）
| 文件 | sha256 | 结果 |
|---|---|---|
| research/leaf25_ttm_recon_step_m1_r3.py（421 行，未跟踪） | eb979015b9cfb85f8bda97ebfc6ee0e402d92d5cd53fed0c9d64bcc01b977e2e | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R3.cmd | 8a3024c4d17504304c995a49f82ca05a42f990733bc676a131c3fce50fc7a510 | ✔ |
| docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R3_MEM_ESTIMATE.md | 198c60d60740d7096531e3c9ad29e2a2a584b09f9fefdc73af8604884cc0d568 | ✔ |
| docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md | 81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1 | ✔ |
| 旧件 _r2.py / R2 .cmd / R2 估计 | f46e0fb5898ba58566c4c6fa6ed05b370a36a38941f766ffcbbee56d316956da / 73aceedc05716dd7fdf1c0908b6163a2958aa4c1688fd8ea2944735ab9e6b69f / e95db81ddf24f09aed904e96871b4a537260a5029c151c7f0216f631ea5e6dfd | ✔ 未变 |
| 旧件 预注册 r4 | 6678c9b7bb459f5c7f96800c0a05154ca54adb6dd5eaee49be778b9279fc02e9 | ✔ 未变 |
| 包装器 v4 | 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 | ✔ |
| 输入现值 | income bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3；cashflow 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79；balance 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5；calendar fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 | ✔ 与 _r3 INPUTS（L56–L61）一致，INPUTS 不在 diff 内，即与 R2 相同 |
| 申万主表（冻结项，核对用） | data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 89d4afa3…；industry_members_sw_l1.parquet 87d769aa… | ✔ 未变。注意：步骤 −1 脚本不读申万表，它不是本次运行的输入 |

## 二、四份 diff 的忠实性
在 /tmp/l25r3 对四对文件独立重算 `diff -u`，去掉 ---/+++ 头行后与 AI 提交的四份 diff 逐字节比对：DIFF_step_m1_r2_to_r3.diff、DIFF_cmd_R2_to_R3.diff、DIFF_mem_R2_to_R3.diff、DIFF_prereg_r4_to_r5.diff **全部一致** ✔。头行时间戳与文件 mtime 一致。

## 三、结论
- **PASS（有条件）**。无 P0/P1/P2；2 个 P3（R3-P3-1、R3-P3-2），都只会让结果判为 rc=4（安全失败，不会误判为已验证），不阻断。
- S-P2-1、S-P3-1、R4-P3-1 **全部关闭**。
- 条件 = 第七节的签发前置；脚本本身不需再改即可进入签发流程（是否顺手修两个 P3 见第五节，由 AI 定，若修须新文件名 _r4 并再走一次差异复核）。

## 四、上轮发现关闭情况
### S-P2-1（_r3 L217–L234、L287–L302）——关闭 ✔
- 新函数 `avail_E`（L217–L234）是 `ttm_at`（L162–L207）选 E 规则的只看可得日镜像：
  - 数据源 G（L287）取自 U（L280：report_type=="1"、qend_ok、avail_sh_date 非空），与 ttm_at L163–L164 及 pick L146 的过滤条件相同；
  - 可用判定 `avail_sh_date < d`（L224）与 pick 相同；
  - newest = 收入表可用期最大值；一季上限 `E < newest − 3 个月` 与 15 个月上限 `E < d − 15 个月` 即 break（L230–L231），与 ttm_at L171–L172 逐字相同；
  - 分量齐全判定 `component_periods(E, tb) <= have[tb]`（L232）：收入/现金流年报只要 E，非年报要 E、A_{y−1}、YTD_{E−1y}；资产负债表要 TA_E、TA_{E−1y}。与 ttm_at L176–L188 实际调用 pick 的期完全一致。
  - 结论：对同一代码、同一天，avail_E 返回的 E 与 ttm_at 选出的 E 相同（或同为无）。
- 选例（L294–L299）对 d_before = prev_open(d_after) 与 d_after 分别求 Eb、Ea，任一为 None 跳过；被更正期须同时属于 Eb、Ea 在该表的分量期。由于 avail_E 要求分量在当天可用，被更正期在 d_before 必有一个早于更正的版本可用（d_before ≤ corr_date，故更正版本在 d_before 不可用），在 d_after 更正版本可用。第二阶段 L351–L353 的 kb、ka 判定因此在正常情况下必然成立。
- 上轮反例（更正与下一期定期报告同日披露，导致两天 E 不同、组件集合不同）现在会在选例时被跳过，而不是在运行后 rc=4 ✔。
- 触发元组字段 E_at_corr 改为 E_before / E_after（L300–L301）；全仓库除 _r2 与 diff 外无其他引用 ✔。
### S-P3-1（_r3 L365–L366）——关闭 ✔
Q1 先出分支改为 `status` 以 NaN 开头才算 true。按一季上限：dq 当天 newest=Q1(y)，A_{y−1} 尚不可用、不进可用期列表，下一期 Q3(y−1) 早于 newest − 3 个月 → break → 返回 NaN_no_complete_E_within_caps（L207）。误回退到 Q3(y−1) 的实现会得到 FALLBACK 并判 false，判定变严 ✔。同日分支 L362–L364 未变 ✔。
### R4-P3-1（r5 L84）——关闭 ✔
r5 L84 改为「NaN until the annual report is available」，与代码 L171–L172 的 break 一致；r5 L3 新增修订说明，其余未改（diff 只有标题、修订说明、L84 三处）✔。

### 未改动的部分
- AST 逐函数比对 _r2 与 _r3：ttm_at、pick、component_periods、find_key、keystr、norm、read_keys、value_counts、orphan_groups、extra_dates、stage、sha256、die、vmhwm_kb 全部**完全相同**；只有 main 变化、新增 avail_E（含内部函数 periods）✔。
- 上轮所称 L288 的 (ii) 候选筛选 `avail_sh_date_q <= avail_sh_date_a`：_r2 L288 与 _r3 L310 逐字相同 ✔。
- main 的变化只有 diff 所示四处：选例块、del 列表（L327 删 G）、S-P3-1 分支、run_meta.script 与 peak_check 文字改为 _r3 ✔。

## 五、发现
### R3-P3-1（P3，_r3 L292–L294、L351–L353）：规则 (i) 残余 rc=4 情形
若该 (代码, 期, 表) 有第三个版本 dd[2]，且 corr_date < dd[2] 而 next_open(dd[2]) == d_after（如 dd[1] 为周五、dd[2] 为周六），则 d_after 当天最新可用版本是 dd[2]，ka 的可得日 ≠ corr_date → rule_exercised=false → rc=4。安全失败，概率低。可选修法：选例时要求 len(dd)==2 或 next_open(dd[2]) > d_after。
### R3-P3-2（P3，_r3 L318、L362–L366）：规则 (ii) 同日判定按上海日历日而非生效日
same_day 用 q_date == a_date（自然日）判定。若 q_date < a_date 但 next_open(q_date) == next_open(a_date)（如 Q1 周六、年报周日），dq 当天年报已可用 → status=OK，而分支期望 NaN → rc=4。安全失败，概率低（只看排序最前的一个候选）。可选修法：same_day 定义为 next_open(q_date) == next_open(a_date)，或在 jj 中剔除此类候选。
### 对两个 P3 的处理意见
不阻断。若 AI 愿意修，成本很小，但须新文件 research/leaf25_ttm_recon_step_m1_r4.py、R4 .cmd（--assert …_r4、.ok …_R4）并再走一次差异复核；若不修，签发时在 .ok 备注里写明接受这两种 rc=4 风险。由 AI 提议、主 Agent 定。

## 六、专项核查（不计发现）
- **get_group 的 KeyError 捕获（L219–L223）**：try 内只有 `G[tb].get_group(code)` 一句。G 的键固定为 TABLES，G[tb] 不会 KeyError；能捕获的只有“该代码不在该表”。而 trig_raw 来自 m.dropna()（L284），要求 (代码, 期) 在三表都有，所以这条分支实际上走不到。即便有未知 KeyError 被吞，结果也只是返回空集 → avail_E 为 None → 跳过候选 → 最差 die（rc=3，L303–L304），不会产生假通过。范围足够窄，不掩盖真实错误 ✔。pandas 3.0.6 合成实验：缺失键的 get_group 抛 KeyError ✔。
- **按代码 groupby 的构建开销**：L287 为三表各复制 3 列（约 119 万行 × 约 30 B ≈ 35 MB），首次 get_group 时建分组索引（约 119 万个 int64 ≈ 10 MB，加约 1.8 万个小数组开销）；替换掉 _r2 的 inc_by（约 5900 个小 DataFrame 的对象开销，几十 MB）。净变化约 ±30 MB，在估计文最坏约 665000 kB 之内，离 C4 1331200 仍有一半余量。每个候选 6 次 get_group，全是按位置取数，即使候选上万也只是秒级。估计文“数值不变”的说法可接受 ✔。
- **日期类型（pandas 3.0.6 / pyarrow 25.0.1）**：合成实验确认 to_datetime(format=…) 与 utc=True 转换都得到 datetime64[us]；DateOffset 运算保持 us；s / us / ns 三种单位的同一 Timestamp 相等且 hash 相同，集合包含关系（L224、L232、L299 的 set 运算）不受单位影响 ✔。_r3 全文没有 merge_asof；变化行只用 Timestamp 比较与 set 运算，无 us/ns 混用风险 ✔。
- **I/O**：import 与 _r2 相同（无 subprocess/os/项目模块）；读取仍只有 pq.read_schema、pq.read_table 与 /proc/self/status；写入只有 L378 mkdir、L380 raw_rows.csv、L381 ttm_script.csv、L393 run_meta.json，全部在 --out 下，--out 须严格位于 output/ai_factory/_leaf25_ttm_recon/ 之下（L250–L251）✔。无新增 I/O 路径。
- **pyflakes**：/tmp/l25r3/venv 中对 /tmp 副本运行，rc=0，无输出 ✔。
- **.cmd（R3）**：包装器 v4 6174eacb ✔；--arch-ok output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R3.ok ✔；--assert leaf25_ttm_recon_step_m1_r3 ✔（子串匹配，只命中 _r3 脚本路径；--out 路径只含 _leaf25_ttm_recon，不会误命中）；--tag leaf25_step_m1_r3 ✔；--meta 指向 run_meta.json ✔；解释器 /workspace/qlvenv/bin/python 与 R2 相同 ✔；env PYTHONDONTWRITEBYTECODE=1 ✔；STOPKB 1484800 为包装器默认值（注释写明，命令未覆盖）✔。
- **观察**：_r3 文档字符串 L14 仍写「prereg r4 s2」；r5 只改文字，规则不变，可接受，但 .ok 的 prereg_sha256 须钉 r5（81123646…）。估计文最坏约 665000 kB 略高于 expected_peak 报告线 650000，沿用上轮口径（超过只记 P3 复核，不作废）。

## 七、签发前仍须满足（本审查不签 .ok）
1. **补跑完成并重钉输入 sha**：Data 今日 10-14→10-16 补跑已结束（或 16:00 ET 放弃），Arch 核完补跑前后 sha；签发时重算四个输入文件 sha。若任一变化，脚本 INPUTS 须改钉，即换新文件名（_r4）并再做差异复核。
2. **94322 处于 T 状态或已退出**，附 Data 的 ps 证据（签发前、启动前各一次）。
3. **静默门禁**：设 RESEARCH_QUIET.lock，等待 ≥15 秒，留存 localhost:8795/healthz 证据：quiet=true、gen_running=false、child_pids={}（09:46 的三项核对已于 10:30 退役，Web v2.1 已核验）。
4. 单进程、单次、不重试；不落在 10-19 16:40–18:40 ET；不与 Data 补跑或其他真实数据进程重叠。
5. .ok 用 efb013d8 第六节的键表，以下几项改为本轮值：
   - prereg_sha256=81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1
   - script_path=/workspace/QuantLab/research/leaf25_ttm_recon_step_m1_r3.py
   - script_sha256=eb979015b9cfb85f8bda97ebfc6ee0e402d92d5cd53fed0c9d64bcc01b977e2e
   - cmd_path=/workspace/QuantLab/docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R3.cmd
   - cmd_sha256=8a3024c4d17504304c995a49f82ca05a42f990733bc676a131c3fce50fc7a510
   - mem_estimate_sha256=198c60d60740d7096531e3c9ad29e2a2a584b09f9fefdc73af8604884cc0d568
   - assert=leaf25_ttm_recon_step_m1_r3，tag=leaf25_step_m1_r3
   - c4_limit_kb=1331200，stopkb=1484800，rss_limit_kb=1536000，expected_peak_kb=650000
   - signed_et / issued_at / expires_et 取自 `date +%Y-%m-%dT%H:%M:%S%:z`；out_dir、log_dir 写成字面值
   - 若不修 R3-P3-1/2，在 .ok 备注接受这两种 rc=4 风险
6. 退出码 0 不等于成功：逐个核对三份输出、triggers（含 E_before / E_after）、每例 rule_exercised 与 report_type 计数；rc≠0 时到 output/ai_factory/_void/ 取件。用后归档 _consumed/（sha8 + CONSUMED/VOID + ET 时间）。
