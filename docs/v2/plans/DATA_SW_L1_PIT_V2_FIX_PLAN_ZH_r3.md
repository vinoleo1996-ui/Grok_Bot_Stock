# Data 申万一级 PIT 修复方案 r3（sw_l1_pit_v2）——增量修订，仅方案，待 Arch 审

- 作者：QuantLab Data；起草 2026-10-18 09:4x–10:xx ET。
- **本文件是 r3，新文件，增量修订**。基线 r2 = docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r2.md（sha 482d8a2b06ef95348aa8935ce53261cde7d81053648acc0c2fd5fe53cf69b28b，93439 字节，已冻结，未改动；写本文件前后各核一次 sha）。r1 = 2d9f5b8e…（冻结，未动）。
- 回应：Arch 静态审 docs/v2/ARCH_DATA_SW_L1_PIT_V2_R2_REVIEW_ZH.md（sha 661f7055a91cd2e46b40ddb938878322a6b467da1f289011b9b51f0f5e65384c，12478 字节，审查时间 2026-10-18T09:32:43-04:00），结论**有条件通过**：方案层面通过；代码文本 1 个 P1、7 个 P2 须在 r3 修正，P3 一并修订。Arch 允许 r3 做增量修订（只改涉及的函数、契约和 selftest，不需要全文重审）。逐条回应见 §12。
- 同时落实主 Agent 转达的要求：(a) 增加 known_at、out_known_at 两列（Data 实际得知入表记录 / 出表记录的时间，带时区，America/New_York）；(b) 事后回填的行不能用 in_date 18:00 当 available_at；(c) 日历 2027 包从本方案拆出，单独交方案（docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md）。
- 状态：**仅方案**。下文代码只是文本：没有在 repo 创建任何 .py，没有 git apply，没有运行。起草期间 Arch 正在本机跑只读核查与 memtest，因此本轮只用 rg、sha256sum 与 Read 读了源码与文档文本，**没有读任何 parquet / 数据文件，没有 import 项目代码，没有联网**。
- live=false，promotion_approved=false，strategy_promotion=false。

## 0. 读法与范围
- r3 = r2 全文 + 本文件的替换与新增。**本文件没写到的章节，以 r2 原文为准**；本文件写到的章节或函数，以本文件为准（整段替换，不做行内合并）。
- 被替换 / 新增的部分：

| r2 位置 | r3 处理 | 本文件章节 |
|---|---|---|
| §1 排期第 1 条（与日历包同批交付） | 替换：日历包拆出；CAL pin 顺序 | §1 |
| §4 规则 7（交易日历） | 替换：转日历包方案 | §1 |
| §6.4 CONTRACT、to_contract、validate_contract | 替换：加 known_at / out_known_at 等列 | §2、§3.1、§4 |
| §6.4 _std、load_primary | 替换：行数对账（P3-4）、知情时间打标 | §3.2 |
| §6.4 resolve | 替换：2005 年前自然日推断（P2-1）、out_date_inferred（P3-3）、out_known_at | §3.3 |
| §6.4 新增 check_dates | 新增：out_date ≥ in_date、out_date ≤ as_of（P2-6、P1-1） | §3.4 |
| §6.4 merge_increment、increment_check | 替换：知情时间、out_date 合法性（P1-1、P2-6） | §3.5 |
| §6.4 validate_repull_dir | 替换：改以 pull .ok 的 signed_et 为准（r3 自查发现的问题，见 §3.6） | §3.6 |
| §6.4 新增 as_of_join、members_asof | 新增：us 精度连接（P2-2）、两种读法（P1-1） | §3.7 |
| §6.4 新增 content_sha | 新增：dry-run 内容哈希与 execute 绑定（P2-3） | §3.8 |
| §6.4 新增 acceptance、history_coverage | 新增：判据（P2-4、P3-5）、历史覆盖（P2-5） | §3.9、§3.10 |
| §6.4 main | 替换 | §3.11 |
| §6.5 selftest | 增补用例，并调整受影响的 r2 用例 | §5 |
| §6.6 契约表 | 替换 | §4 |
| §7 / §7.1 执行步骤与 .ok 清单 | 替换 | §6 |
| §8 修后预期 | 补充口径（P3-7） | §7 |
| §13 下游迁移 | 增补：两种读法、name 非 PIT（P3-8） | §8 |
| §14 开放项 | 替换 | §10 |
| §15 回应表 | 保留 r2 的 §15（f17f4771），另加 r3 回应表 | §12 |

## 1. 排期与日历包拆分（P2-7；主 Agent (c)）
1. 实施时间不变：叶23 r2.11、叶24 已于 10-18 09:05 ET 前跑完；本方案的任何真实数据运行都在 **10-19 17:40 ET 纸面跟踪跑完之后**，并避开 10-19 16:40–18:40 ET。截止 2026-12-15（与 r2 相同）。
2. **日历 2027 延长包从本方案拆出**，单独交方案：docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md（与本 r3 同时交 Arch）。本方案**不写 data/v2/calendar**，也不包含 20130424 pretrade_date 的修正（改由日历包负责）。r2 §1 第 1 条“与交易日历 2027 延长包同批交付”与 r2 §4 规则 7 作废。
3. **CAL pin 的先后顺序（Arch 要求写明）**：
   - SW v2 构建（v2.0 与 v2.1）**继续钉 fa4260b8**（data/v2/calendar/trade_cal_sse_pit.parquet，2005-01-01..2026-12-31）。v2.0 窗口 WIN 到 2026-10-16、as_of 2026-10-10，v2.1 实施日计划在 2026-12-15 之前，都在 fa4260b8 覆盖范围内；2005 年以前的 out_date 推断改用自然日（§3.3），不需要更长的日历。
   - 防护：main 检查 as_of（v2.1 为重拉日期）不晚于日历最后一个 cal_date，否则拒绝（§3.11）。若 v2.1 拖到 2027 年，须在**同一份 code-change .ok** 里把 INPUTS["cal"] 改钉日历包产出的新版本文件，由 Arch 签，不另开口子。
   - 日历包改钉新 sha 时，SW v2 构建脚本不随之自动切换；切换须单独列入 code-change .ok。
4. 每次运行前通知主 Agent 与 Arch（开始时间、预计时长），并与 Arch 对齐是否要把 94322 停到 T（主 Agent 09:2x 的要求：读真实数据的运行先对齐）。

## 2. 知情时间 PIT（P1-1；主 Agent (a)(b)）
### 2.1 问题
- r2 契约里 available_at = in_date 18:00，等于假设“生效日当天收盘后就已知”。Arch 指出三类行实际是事后才知道的：(a) SW2021 体系 2021-07-30 才发布，但 89d4afa3 里很多行 in_date 远早于这一天（例：000537 801180 in_date 1993-12-10），是回填历史；(b) v2.1 采纳的 key_added 行中 in_date 早于 v2.0 as_of 的；(c) out_date_filled 与 resolve 推断出的 out_date。
- 另外，按主 Agent 的定义，Data **实际**得知 89d4afa3 全部内容的时间是 10-10 拉取时（manifest fetch_time 2026-10-10T10:01:23-04:00）。严格地说，v2.0 的每一行都是 10-10 才到 Data 手里的。

### 2.2 设计：两类时间分开存，读法分开写
- **known_at**（入表记录的知情时间）、**out_known_at**（出表记录的知情时间）：dtype `datetime64[us, America/New_York]`（带时区，ET），含义是 **Data 实际拿到这条信息的时间**。out_date 为空时 out_known_at 必须为空；out_date 非空时 out_known_at 必须非空。
- **available_at**（严格口径，as_known）：`max(in_date 18:00, known_at)`，统一换算成 Asia/Shanghai 墙钟后去掉时区，dtype `datetime64[us]`（与 r2 契约和其它 Data 表的 available_at 口径一致：无时区 = Asia/Shanghai 墙钟）。**任何事后回填的行，available_at 都不会是 in_date 18:00**，因为 known_at 晚于 in_date 18:00 时取 known_at。
- **pub_available_at**（研究口径，pub_backcast，Arch P1-1 (a) 的写法）：
  - v2.0 来自 89d4afa3、in_date ≥ 2021-07-30 的行：in_date 18:00（假设：10-10 快照里的历史 = 申万当时公开发布的历史）；
  - v2.0 来自 89d4afa3、in_date < 2021-07-30 的行（类 a）：max(in_date, 2021-07-30) 18:00；
  - 事后改动或新增的行（类 b，以及 v2.1 新增的所有键）：等于 available_at（即 max(in_date 18:00, known_at)），**不用 in_date 18:00**。
  - dtype 同 available_at。
- **known_class / out_known_class**（string）：说明知情时间的来源类别，供读者与回执分类计数。取值：

| 列 | 取值 | 含义 | known_at / out_known_at 取值 |
|---|---|---|---|
| known_class | v20_primary | 89d4afa3 行，in_date ≥ 2021-07-30 | PRIMARY_KNOWN_AT（10-10 拉取时间） |
| known_class | pre_sw2021_backcast | 89d4afa3 行，in_date < 2021-07-30（类 a） | PRIMARY_KNOWN_AT；pub_available_at 用 2021-07-30 18:00 下限 |
| known_class | late_key_added | v2.1 新增键且 in_date ≤ v2.0 as_of（类 b） | 重拉完成时间 completed_et |
| known_class | repull_new | v2.1 新增键且 in_date > v2.0 as_of | 重拉完成时间 completed_et |
| out_known_class | none | out_date 为空 | 空 |
| out_known_class | v20_primary | out_date 来自 89d4afa3 原样 | PRIMARY_KNOWN_AT |
| out_known_class | out_filled_repull | v2.1 补的 out_date，或 v2.1 新增键自带的 out_date（类 c） | completed_et |
| out_known_class | out_inferred_resolve | resolve 推断（older_open_closed，类 c） | 触发推断的两行 known_at 中较晚者 |

- manifest 新增：`pit_semantics = "as_known"`（默认读法）；`pit_semantics_alt = "pub_backcast"`（研究读法，带前视说明）；`known_at_rule`、`pub_available_at_rule` 原文；`primary_known_at` 与其不确定性说明（§2.3）；各 known_class / out_known_class 的计数。
- 若 Arch 决定改为“生效日口径”（effective_dated），manifest 与 §8 必须写明“不是知情时间 PIT，回填行有前视”，不能只叫 PIT。本方案默认 as_known（见 §10 开放问题 Q1）。

### 2.3 known_at 的取值与不确定性
- **v2.0（89d4afa3 恢复内容）**：PRIMARY_KNOWN_AT = `2026-10-10T10:01:23-04:00`（89d4afa3 manifest.json 的 fetch_time 截到秒；原值 2026-10-10T10:01:23.213525-04:00，本轮只用 rg 读了该 manifest 的这一行）。不确定性须写进 manifest.primary_known_at_note：
  - 10-10 当天文件的 sha 未记录，无法证明 89d4afa3 与 10-10 写出的文件逐字节一致；可证的是与 output/data_v2_bundle 及 data_v2_bundle.tar（10-10 14:42 ET）副本一致。因此“10-10 已在手”的上界取 14:42 ET（PRIMARY_KNOWN_AT_UPPER，只记入 manifest，不进行级列）。
  - 89d4afa3 现有 inode 是 10-18 01:13 ET 工作区恢复时重写的，文件时间不能作证据；known_at 依据是 manifest 内容 + tar 副本一致性，不是 mtime。
  - 若 Arch 认为应保守取上界，可把 PRIMARY_KNOWN_AT 改为 14:42 ET。影响：严格口径 available_at 从上海 10-10 22:01 变为 10-11 02:42；2026-10-10 是周六、10-11 是周日，两者最早都从 10-12（周一）交易时段起可用，对日频读者无实质差别。
- **v2.1（实施日重拉）**：known_at / out_known_at 取重拉目录 COMPLETE.json 里的 `completed_et`（带时区的拉取完成时间，由 sw_pit_refresh.py --pull-only 写入；r3 要求该字段存在且带时区，否则拒绝）。不用 dry-run 或 execute 的运行时间，保证 dry-run 与 execute 算出的内容一致（P2-3）。
- **resolve 推断的 out_date**：out_known_at = 触发推断的“较旧 open 行”和“较新 open 行”两者 known_at 的较晚者（新 open 行被知道时，才知道旧行结束）。
- **已有行的知情时间不可改**：v2.1 不得改 v2.0 行的 known_at、available_at、pub_available_at；只有补 out_date 时写入 out_known_at（increment_check 检查，§3.5）。

### 2.4 out_date 晚于 as_of 的行
- 规则：版本 as_of（v2.0 = 2026-10-10；v2.1 = 重拉日期）之后的 out_date 不可能在 as_of 时已发生，**一律拒绝**（check_dates 显式 fail），计数进 acceptance（期望 0）。
- in_date 晚于 as_of 的行（预告的未来调整）不拒绝，计数进 acceptance 披露项（期望 0），按原样保留，available_at 仍按 max(in_date 18:00, known_at)。

## 3. 代码修订（sw_l1_pit_v2_build.py；文本，未应用、未运行）
各小节说明改了什么；完整替换文本在 §3.12（一个代码块，未列出的函数沿用 r2 §6.4）。

### 3.1 契约常量（P1-1、P3-1）
- CONTRACT 加 known_at、out_known_at（`datetime64[us, America/New_York]`）、pub_available_at（`datetime64[us]`）、known_class、out_known_class（string）。列顺序见 §4。
- 新常量：SW2021_PUB（2021-07-30）、PRIMARY_KNOWN_AT / PRIMARY_KNOWN_AT_UPPER、PIT_SEMANTICS、INC_ROLLBACK_FRAC（0.005）、NON_A_EXPECTED（{T00018}）、INTERPRETER（/workspace/qlvenv/bin/python）。
- 工作表统一用 WORK 列（含知情时间列），to_contract 再补 ts_code、name、available_at、pub_available_at、source、revision、promotion_approved。

### 3.2 读入、行数对账与知情时间打标（P3-4、P1-1）
- _std 多返回一个 recon：rows_in、dropped_non_a_rows、dropped_exact_dup_rows、rows_out，且 rows_in − 非 A 股 − 完全重复 = rows_out，不平即拒绝。89d4afa3 原始 7920 行的对账进 manifest.recon 与 acceptance。
- load_raw_dir 同样透传 recon（62 raw 与重拉目录各一条）。
- 新增 stamp_known：按 §2.2 打 known_at、out_known_at、known_class、out_known_class，quality_status 初值 ok。

### 3.3 resolve（P2-1、P3-3、P1-1 (c)）
- 新增 prev_day：日历内有更早开市日时取前一交易日（quality_status = out_date_inferred）；否则（nxt 之前日历内没有开市日；fa4260b8 从 2005-01-01 起，首个开市日按 Arch 引用为 2005-01-04，本轮未读数据核实）取**自然日前一天**（quality_status = out_date_inferred_natural_day）。r2 在这种情况下会 fail，挡住 v2.0（Arch 用 000537 两条 open 合成数据复现）。
- 推断的 out_date 打 out_known_class = out_inferred_resolve，out_known_at = 两行 known_at 中较晚者。
- 推断出的 out_date 早于本行 in_date 时仍显式拒绝。resolve 结束后检查键唯一。
- 备选证明（Arch 允许二选一）：§6 第 2 步的只读探查里一并计数 89d4afa3 中“同代码两条 open 且较新一条 in_date ≤ 2005-01-04”的行数；代码不依赖这个计数为 0。

### 3.4 check_dates（P2-6、P1-1）
- 显式拒绝 out_date < in_date；拒绝 out_date 晚于版本 as_of；检查 out_date 与 out_known_at 同空同非空、known_at 非空。in_date 晚于 as_of 的行计数披露。
- 调用位置：resolve 与 check_one_open 之后，闸门之前（v2.0 与 v2.1 都调用）。

### 3.5 merge_increment / increment_check（P1-1 (b)(c)、P2-6）
- 新增参数 base_as_of（v2.0 的 as_of）。
- 补 out_date：重拉的 out_date < 原 in_date → 不采纳，记 out_date_lt_in_ignored；否则采纳，out_known_at = 重拉完成时间，out_known_class = out_filled_repull；out_date ≤ v2.0 as_of 的记为 out_date_filled_backdated（采纳但单列披露，P2-6 二选一中选“按 P1-1 标注知情时间”）。
- 新增键：自带 out_date < in_date 的不采纳（key_added_out_lt_in_ignored）；其余按 known_class（late_key_added / repull_new）打知情时间。
- increment_check 额外拒绝：已有行的 known_at 或 known_class 被改（known_at_changed）、已有 out_date 行的 out_known_at 被改（out_known_at_changed）。

### 3.6 validate_repull_dir（r3 自查发现的 r2 缺陷）
- r2 用“本次运行 .ok 的 signed_et”比重拉文件的 mtime，并要求目录日期 = 今天。v2.1 的 execute_increment .ok 一定是 Arch 审完 dry-run 之后才签，晚于重拉，所以 r2 的 execute_increment **一定会被拒绝**；跨日执行也会被拒绝。Arch 661f7055 未提此项，是我起草 r3 时发现的。
- r3 改为：以 **pull .ok** 为准。main 新增 --pull_ok；COMPLETE.json 必须含 completed_et（带时区）与 pull_ok_sha256；目录名日期 = completed_et 的 ET 日期；文件 mtime 晚于 pull .ok 的 signed_et；pull .ok 必须已有 consumed 标记；dry-run 与 execute .ok 都以 dep_sha256_pull_ok、dep_sha256_repull_complete 钉住。
- 这要求 sw_pit_refresh.py --pull-only 写 COMPLETE.json 时加 completed_et 与 pull_ok_sha256 两个字段：属 r2 §6.2 diff 的一处增量，落代码时在同一 code-change .ok 内改，r3 不重贴整段 diff（见 §10 Q5）。

### 3.7 读者 helper：as_of_join、members_asof（P2-2、P1-1）
- as_of_join：连接前双方统一为 datetime64[us]；tz-aware 与 naive 混用、时区不同、键含 NaT 一律拒绝；内部稳定排序后调用 pd.merge_asof。解决 Arch 实测的 pandas 3.0.6 下 ns 对 us 直接 MergeError。
- members_asof(df, d, t, mode)：d 为生效日，t 为带时区的决策时点。as_known 用 available_at 与 out_known_at；pub_backcast 用 pub_available_at，v2.0 原样的 out_date 视为 out_date 18:00 可知，事后补的 out_date 仍用 out_known_at。t 时还不知道的出表视为仍在任。
- 这两个 helper 放在构建脚本里供 selftest 与 history_coverage 使用；消费方是否复用、放到哪个共享模块，由 Strategy / Intel 与 Arch 定（§8、§10 Q3）。

### 3.8 dry-run 与 execute 绑定（P2-3）
- content_sha：按 (instrument_id, l1_code, in_date) 稳定排序，逐列规范化成字符串（日期用 ISO 格式，tz-aware 带偏移，空值记为 \N），列名与 dtype 也纳入哈希；不依赖 parquet 元数据。
- dry-run：summary.json 写 content_sha256（summary.json 本身改为原子写）。
- execute：必须给 --dryrun_dir；execute .ok 用 dep_sha256_dryrun_summary 钉住 Arch 审过的 summary.json，并另写一个键 dryrun_content_sha256；execute 重算内容哈希，与 summary 和 .ok 三方一致才写，step、as_of、inputs、repull_dir、repull_sha256 也须与 dry-run 一致。写盘后用 read_contract_parquet 回读再算一次，不一致即报 Arch、不更新指针。
- 幂等：同一输入重复执行，内容哈希相同；目标文件已存在时原子写拒绝（r2 已有）。

### 3.9 acceptance（P2-4、P3-5、P3-7）
- summary.json 新增 acceptance 段，每项写 got 与 want，ok 为 true / false / null（null = 只披露）。checks_ok = 所有非 null 项为 true，且闸门通过、increment_check 无违例。

| 项 | 期望值 | 判定 |
|---|---|---|
| daily_missing_after | 09-24..10-16 每天缺成分的代码，除 as_of 之后新上市的股票外，全部逐只列在 source_gap 里（期望 0） | 不符即 false |
| non_a_share_excluded | 集合恰为 {T00018} | 不符即 false |
| normdiff_vs_raw0108 | 0 行（唯一差异 T00018 已被 norm_code 两侧剔除，即 Arch 说的“只允许 T00018”） | 不符即 false |
| conflicts_by_reason | deleted_vs_89d4afa3_baseline 与 deleted 为 0；其余 reason 计数披露 | deleted 非 0 即 false |
| recon_rows | 每个来源行数对账平 | 不平即 false |
| open_rows_235 / _68 / _46 | 三组代码在 v2.0 里全部有 open 行（核对清单要求 dry-run 实测复核） | 不符即 false |
| in_date_after_as_of | 期望 0 | 只披露 |
| inc_in_base_not_in_repull_frac（v2.1） | ≤ 0.5% 的 v2.0 键 | 超过即 false = 回退，不更新指针（P3-5） |
| inc_out_date_conflict_ignored_frac（v2.1） | ≤ 0.5% | 同上 |
| inc_out_lt_in（v2.1） | out_date_lt_in_ignored + key_added_out_lt_in_ignored = 0 | 非 0 即 false |
| inc_kinds（v2.1） | 各类差异计数 | 只披露 |
| history_coverage | §3.10 | 只披露 |

- 235 / 68 / 46 三组代码清单以 json 文件经 --sets46 传入，由 dry-run .ok 的 dep_sha256_sets46 钉住；该 json 在 §6 第 2 步由 Data 从已交审计 CSV 用 rg 摘出生成，路径与 sha 随只读探查结果交 Arch（本轮未生成）。

### 3.10 history_coverage（P2-5）
- 月末取样 2018-01..2026-10（取每月最后一个开市日）；股票池 = 当日在市的沪深 A 股，**包含后来退市的**（stock_basic_incl_delisted + stock_delisted_v2，较早退市日）。
- 每月报：universe、其中后来退市的数量、生效日口径缺成分数及其中后来退市的数量、as_known 口径缺成分数、pub_backcast 口径缺成分数。as_known 在 2026-10-10 之前预计全部缺失（因为 Data 10-10 才拿到），这正是严格口径的含义，回执会写明。
- 列为 acceptance 披露项，不设硬阈值（Arch 原文为“披露项”）。

### 3.11 main（汇总）
- 新参数：--pull_ok、--dryrun_dir、--sets46；--step 仍只有 v2.0 / v2.1（v2.2 及以后另行修订，P3-6，见 §10）。
- enforce 的 deps 增加 sets46、pull_ok、repull_complete（有重拉时）、dryrun_summary（execute 时）。
- enforce 之后先 check_interpreter（.ok 的 interpreter 键须为 /workspace/qlvenv/bin/python，且 sys.executable 实际路径一致，P3-1）。
- as_of 晚于日历最后一天即拒绝（§1 第 3 条）。
- manifest 新增：content_sha256、pit_semantics、pit_semantics_alt、known_at_rule、available_at_rule、pub_available_at_rule、primary_known_at（含上界与说明）、join_rule、runtime（python / pandas / pyarrow 版本与解释器路径，P3-1）、recon、acceptance、known_class_counts、out_known_class_counts、name_note。
- read_pointer 改用 read_contract_parquet 回读，校验契约与 manifest 的 content_sha256。
- daily_missing 报告拆为 daily_missing_before.csv、daily_missing_after.csv（按天计数），逐只代码进 acceptance。

### 3.12 替换文本
```python
# ===== r3: scripts/acquire/sw_l1_pit_v2_build.py 的替换与新增 (文本, 未落 repo, 未运行) =====
# 未列出的函数与常量沿用 r2 §6.4 原文. 新增 import: bisect, hashlib, platform.
import bisect, hashlib, platform

SH = ZoneInfo("Asia/Shanghai")
ET_US = "datetime64[us, America/New_York]"
SW2021_PUB = pd.Timestamp("2021-07-30")                    # SW2021 发布日 (Arch 661f7055 P1-1 (a))
PRIMARY_KNOWN_AT = "2026-10-10T10:01:23-04:00"             # 89d4afa3 manifest.fetch_time (截到秒)
PRIMARY_KNOWN_AT_UPPER = "2026-10-10T14:42:00-04:00"       # data_v2_bundle(.tar) 时间; 只进 manifest
PIT_SEMANTICS = "as_known"
INC_ROLLBACK_FRAC = 0.005                                  # P3-5: 超过 0.5% 的键即不建议更新指针
NON_A_EXPECTED = {"T00018"}                                # P2-4
INTERPRETER = "/workspace/qlvenv/bin/python"               # P3-1: 与叶/纸面同一解释器; .ok 的 interpreter 键再钉一次
CONTRACT = [  # v2 schema 契约 r3 (见方案 r3 §4)
    ("instrument_id", "string"), ("ts_code", "string"), ("name", "string"),
    ("l1_code", "string"), ("l1_name", "string"),
    ("in_date", "datetime64[us]"), ("out_date", "datetime64[us]"), ("is_new", "string"),
    ("known_at", ET_US), ("out_known_at", ET_US),
    ("available_at", "datetime64[us]"), ("pub_available_at", "datetime64[us]"),
    ("known_class", "string"), ("out_known_class", "string"),
    ("source", "string"), ("src", "string"),
    ("revision", "string"), ("quality_status", "string"), ("promotion_approved", "bool"),
]
WORK = ["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new", "src",
        "known_at", "out_known_at", "known_class", "out_known_class", "quality_status"]


def et_ts(s, what):
    t = pd.Timestamp(parse_tz(s, what))
    return t.tz_convert(ET).as_unit("us")


def to_sh_naive(s):
    # tz-aware Series -> Asia/Shanghai 墙钟, 去时区, us
    return s.dt.tz_convert(SH).dt.tz_localize(None).astype("datetime64[us]")


def check_interpreter(kv):
    want = {v.get("interpreter", "") for v in kv.values()}
    if want != {INTERPRETER}:
        fail(f".ok 的 interpreter 须为 {INTERPRETER}: {want}")
    if os.path.realpath(sys.executable) != os.path.realpath(INTERPRETER):
        fail(f"解释器不符: {sys.executable}")


def runtime_info():
    import pyarrow
    return {"python": platform.python_version(), "executable": sys.executable,
            "pandas": pd.__version__, "pyarrow": pyarrow.__version__}


# ---------- 读入与规范化 (r3: 行数对账 P3-4) ----------
def _std(d, code_col, src):
    rows_in = len(d)
    d = d.copy()
    d["instrument_id"] = d[code_col].map(norm_code)
    non_a_mask = d.instrument_id.isna()
    non_a = sorted(d.loc[non_a_mask, code_col].astype(str).unique())
    d = d[~non_a_mask].copy()
    d["in_date"] = parse_dates(d["in_date"], f"{src}.in_date")
    d["out_date"] = parse_dates(d["out_date"], f"{src}.out_date")
    d["src"] = src
    cols = ["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new", "src"]
    n_before = len(d)
    out = d[cols].drop_duplicates()
    recon = {"src": src, "rows_in": rows_in, "dropped_non_a_rows": int(non_a_mask.sum()),
             "dropped_exact_dup_rows": n_before - len(out), "rows_out": len(out)}
    if recon["rows_in"] - recon["dropped_non_a_rows"] - recon["dropped_exact_dup_rows"] != recon["rows_out"]:
        fail(f"行数对账不平: {recon}")
    return out, non_a, recon


def stamp_known(d, known_at, as_of, kind):
    # kind="primary": v2.0 行; kind="repull": v2.1 重拉行 (known_class 在 merge_increment 里细分)
    d = d.copy()
    k = et_ts(known_at, f"{kind}.known_at")
    d["known_at"] = pd.Series(k, index=d.index).astype(ET_US)
    d["out_known_at"] = d["known_at"].where(d.out_date.notna())
    if kind == "primary":
        d["known_class"] = (d.in_date < SW2021_PUB).map({True: "pre_sw2021_backcast", False: "v20_primary"})
        d["out_known_class"] = d.out_date.notna().map({True: "v20_primary", False: "none"})
    else:
        d["known_class"] = (d.in_date <= pd.Timestamp(as_of)).map({True: "late_key_added", False: "repull_new"})
        d["out_known_class"] = d.out_date.notna().map({True: "out_filled_repull", False: "none"})
    d["quality_status"] = "ok"
    return d[WORK]


def load_primary():
    p, want = INPUTS["primary"]
    if sha(p) != want:
        fail("主来源 89d4afa3 sha 不符")
    d = pd.read_parquet(p, columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "is_new"])
    d = d.rename(columns={"sw_code": "l1_code", "sw_name": "l1_name"})
    m, non_a, recon = _std(d, "instrument_id", "89d4afa3")
    return stamp_known(m, PRIMARY_KNOWN_AT, PRIMARY_AS_OF, "primary"), non_a, recon


# ---------- 冲突处理: 不删键 (r3: P2-1 / P3-3 / out_known_at) ----------
def prev_day(nxt, tset):
    # tset: 升序交易日. 日历 (fa4260b8) 从 2005-01-01 起; nxt 之前没有日历内开市日时, 用自然日前一天 (P2-1)
    i = bisect.bisect_left(tset, nxt)
    if i > 0:
        return tset[i - 1], "out_date_inferred"
    return nxt - pd.Timedelta(days=1), "out_date_inferred_natural_day"


def resolve(m, tdays):
    # 1) 完全重复行去重; 2) 同键 open + closed: 保留 closed; 3) 同一代码多条 open: 较旧的补 out_date
    m = m.drop_duplicates(subset=[c for c in WORK if c != "src"]).reset_index(drop=True)
    conf = []
    m["_k"] = list(zip(m.instrument_id, m.l1_code, dkey(m.in_date)))
    drop_idx = []
    for k, grp in m.groupby("_k"):
        if len(grp) == 1:
            continue
        closed = grp[grp.out_date.notna()]
        if closed.out_date.nunique() > 1:
            fail(f"同键多个不同 out_date: {k}")
        if len(closed):
            for i in grp.index[grp.out_date.isna()]:
                drop_idx.append(i)
                conf.append(dict(instrument_id=k[0], l1_code=k[1], in_key=k[2], reason="same_key_open_merged_into_closed",
                                 explain="同键已有 closed 版本; open 版本并入, 键保留"))
            drop_idx.extend(closed.index[1:])
        else:
            drop_idx.extend(grp.index[1:])
    m = m.drop(index=drop_idx)
    tset = sorted(tdays)
    o = m[m.out_date.isna()].sort_values(["instrument_id", "in_date"])
    for iid, grp in o.groupby("instrument_id"):
        if len(grp) < 2:
            continue
        idx = list(grp.index)
        for a, b in zip(idx[:-1], idx[1:]):
            nxt = m.at[b, "in_date"]
            prev, q = prev_day(nxt, tset)
            if prev < m.at[a, "in_date"]:
                fail(f"{iid}: 推断的 out_date {prev:%Y%m%d} 早于 in_date")
            m.at[a, "out_date"] = prev
            m.at[a, "out_known_at"] = max(m.at[a, "known_at"], m.at[b, "known_at"])
            m.at[a, "out_known_class"] = "out_inferred_resolve"
            m.at[a, "quality_status"] = q                                   # P3-3: 不再混为 ok
            conf.append(dict(instrument_id=iid, l1_code=m.at[a, "l1_code"], in_key=m.at[a, "in_date"].strftime("%Y%m%d"),
                             reason="older_open_closed", explain=f"补 out_date={prev:%Y%m%d} ({q}; 新 open {nxt:%Y%m%d})"))
    m = m.drop(columns="_k")
    dup = m.duplicated(subset=["instrument_id", "l1_code", "in_date"])
    if dup.any():
        fail(f"resolve 后仍有重复键: {int(dup.sum())}")
    return m, pd.DataFrame(conf)


# ---------- 日期合法性 (r3 新增: P2-6 / P1-1) ----------
def check_dates(m, as_of):
    a = pd.Timestamp(as_of)
    lt = m[m.out_date.notna() & (m.out_date < m.in_date)]
    if len(lt):
        fail(f"out_date < in_date: {len(lt)} 行, 样例 {lt.instrument_id.head(5).tolist()}")
    late = m[m.out_date.notna() & (m.out_date > a)]
    if len(late):
        fail(f"out_date 晚于 as_of {as_of}: {len(late)} 行, 样例 {late.instrument_id.head(5).tolist()}")
    bad_ok = m[(m.out_date.isna() != m.out_known_at.isna()) | m.known_at.isna()]
    if len(bad_ok):
        fail(f"known_at / out_known_at 与 out_date 不一致: {len(bad_ok)} 行")
    return {"in_date_after_as_of": int((m.in_date > a).sum())}


def load_raw_dir(raw_dir, n_files=62):
    # r3: 与 r2 相同, 只是返回值多一个 recon (P3-4); 重拉行的知情时间由 main 里 stamp_known(kind="repull") 打上
    fs = sorted(pathlib.Path(raw_dir).glob("801*.SI_[YN].parquet"))
    if len(fs) != n_files:
        fail(f"{raw_dir}: 文件数 {len(fs)} != {n_files}")
    parts = []
    for f in fs:
        l1, isn = f.stem.split("_")
        d = pd.read_parquet(f, columns=["ts_code", "l1_code", "l1_name", "in_date", "out_date"])
        d = d[d.l1_code == l1].copy()
        d["is_new"] = isn
        parts.append(d)
    return _std(pd.concat(parts, ignore_index=True), "ts_code", pathlib.Path(raw_dir).name)


# ---------- step v2.1 增量规则 (r3: 知情时间 + out_date 合法性) ----------
def merge_increment(base, rep, base_as_of):
    # base: 指针指向的 v2.0 (WORK 列); rep: stamp_known(kind="repull") 之后的重拉行
    # 只加新键; base open 而 rep closed -> 补 out_date (out_known_at = 重拉完成时间); 其余差异只报告不采纳
    a = pd.Timestamp(base_as_of)
    b = base.copy()
    b["_k"] = list(zip(b.instrument_id, b.l1_code, dkey(b.in_date)))
    r = rep.copy()
    r["_k"] = list(zip(r.instrument_id, r.l1_code, dkey(r.in_date)))
    rb = r.drop_duplicates("_k").set_index("_k")
    diff = []
    for i, row in b.iterrows():
        if row["_k"] not in rb.index:
            diff.append(dict(key=row["_k"], kind="in_base_not_in_repull", adopted=False))
            continue
        rr = rb.loc[[row["_k"]]].iloc[0]
        ro = rr.out_date
        if pd.isna(row.out_date) and pd.notna(ro):
            if ro < row.in_date:
                diff.append(dict(key=row["_k"], kind="out_date_lt_in_ignored", adopted=False, value=f"{ro:%Y%m%d}"))
                continue
            b.at[i, "out_date"] = ro
            b.at[i, "out_known_at"] = rr.known_at                         # 重拉完成时间, 不是 out_date 18:00
            b.at[i, "out_known_class"] = "out_filled_repull"
            kind = "out_date_filled_backdated" if ro <= a else "out_date_filled"   # 早于 as_of: 采纳但单列披露 (P2-6)
            diff.append(dict(key=row["_k"], kind=kind, adopted=True, value=f"{ro:%Y%m%d}"))
        elif pd.notna(row.out_date) and pd.isna(ro):
            diff.append(dict(key=row["_k"], kind="repull_reopen_ignored", adopted=False))
        elif pd.notna(row.out_date) and pd.notna(ro) and ro != row.out_date:
            diff.append(dict(key=row["_k"], kind="out_date_conflict_ignored", adopted=False,
                             value=f"{row.out_date:%Y%m%d}->{ro:%Y%m%d}"))
    add = r[~r["_k"].isin(set(b["_k"]))].drop_duplicates("_k")
    bad_add = add[add.out_date.notna() & (add.out_date < add.in_date)]
    for k in bad_add["_k"]:
        diff.append(dict(key=k, kind="key_added_out_lt_in_ignored", adopted=False))
    add = add.drop(index=bad_add.index)
    for k, kc in zip(add["_k"], add["known_class"]):
        diff.append(dict(key=k, kind="key_added", adopted=True, known_class=kc))
    out = pd.concat([b, add], ignore_index=True).drop(columns="_k")
    return out[WORK], pd.DataFrame(diff)


def increment_check(base, new):
    # v2.1 只许加键或补 out_date; 删键 / 重新打开 / 改已有 out_date / 改已有知情时间 一律拒绝
    nb = new.assign(_k=list(zip(new.instrument_id, new.l1_code, dkey(new.in_date)))).set_index("_k")
    bad = []
    for _, row in base.iterrows():
        k = (row.instrument_id, row.l1_code, row.in_date.strftime("%Y%m%d"))
        if k not in nb.index:
            bad.append((k, "deleted"))
            continue
        n = nb.loc[[k]].iloc[0]
        if pd.notna(row.out_date) and pd.isna(n.out_date):
            bad.append((k, "reopened"))
        elif pd.notna(row.out_date) and n.out_date != row.out_date:
            bad.append((k, "out_date_changed"))
        if n.known_at != row.known_at or n.known_class != row.known_class:
            bad.append((k, "known_at_changed"))
        if pd.notna(row.out_date) and n.out_known_at != row.out_known_at:
            bad.append((k, "out_known_at_changed"))
    return bad


# ---------- 重拉目录独立性 (r3: 以 pull .ok 为准) ----------
def validate_repull_dir(p, pull_ok_signed_et, pull_ok_sha, raw0108=RAW_0108, n_files=62):
    # r2 用 run .ok 的 signed_et 比 mtime, 而 execute_increment .ok 一定签在重拉之后 -> 永远拒绝 (r3 自查). 改为:
    # 目录名日期 = COMPLETE.json.completed_et 的 ET 日期; mtime 晚于 pull .ok signed_et; COMPLETE.json 记 pull .ok 的 sha
    p = pathlib.Path(p).resolve()
    if p == pathlib.Path(raw0108).resolve():
        fail("repull_dir 不能是 RAW_0108")
    if (p / "INCOMPLETE.json").exists() or not (p / "COMPLETE.json").exists():
        fail("repull_dir 不完整 (INCOMPLETE 存在或 COMPLETE 缺失)")
    cj = json.loads((p / "COMPLETE.json").read_text())
    done = et_ts(cj.get("completed_et", ""), "COMPLETE.completed_et")
    m = re.fullmatch(r"index_member_all_(\d{8})_(\d{6})", p.name)
    if not m or m.group(1) != done.strftime("%Y%m%d"):
        fail(f"repull_dir 名称日期须等于 completed_et 的 ET 日期: {p.name}")
    if cj.get("pull_ok_sha256") != pull_ok_sha:
        fail("COMPLETE.json 的 pull_ok_sha256 与所给 pull .ok 不符")
    fs = sorted(p.glob("801*.SI_[YN].parquet"))
    if len(fs) != n_files:
        fail(f"repull_dir 文件数 {len(fs)} != {n_files}")
    t0 = parse_tz(pull_ok_signed_et, "pull .ok signed_et").timestamp()
    old = [f.name for f in fs if f.stat().st_mtime <= t0]
    if old:
        fail(f"repull_dir 有文件早于 pull .ok 签发时间: {old[:5]}")
    if done.timestamp() < max(f.stat().st_mtime for f in fs):
        fail("completed_et 早于目录内文件 mtime")
    got = {f.name: sha(f) for f in fs}
    if got != cj["files"]:
        fail("repull_dir 文件 sha 与 COMPLETE.json 不符")
    return got, done


# ---------- 读者 helper (r3 新增: P2-2 / P1-1) ----------
def as_of_join(left, right, left_on, right_on, by=None, direction="backward"):
    # 连接前双方统一为 datetime64[us]; tz-aware 与 naive 混用、时区不同、键含 NaT 一律拒绝
    l, r = left.copy(), right.copy()
    for df, c, side in ((l, left_on, "left"), (r, right_on, "right")):
        if not pd.api.types.is_datetime64_any_dtype(df[c]):
            fail(f"as_of_join: {side}.{c} 不是 datetime")
        if df[c].isna().any():
            fail(f"as_of_join: {side}.{c} 含 NaT")
    tl, tr = getattr(l[left_on].dt, "tz", None), getattr(r[right_on].dt, "tz", None)
    if (tl is None) != (tr is None) or (tl is not None and str(tl) != str(tr)):
        fail(f"as_of_join: 时区不一致 {tl} vs {tr}")
    l[left_on] = l[left_on].dt.as_unit("us")
    r[right_on] = r[right_on].dt.as_unit("us")
    l = l.sort_values(left_on, kind="mergesort")
    r = r.sort_values(right_on, kind="mergesort")
    return pd.merge_asof(l, r, left_on=left_on, right_on=right_on, by=by, direction=direction)


def members_asof(df, d, t, mode="as_known"):
    # d: 生效日 (naive 日期, Asia/Shanghai 日历日); t: 决策时点 (必须带时区)
    # 返回: 在 t 时已知、且 d 日在任的行. t 时还不知道的出表视为仍在任.
    t = pd.Timestamp(t)
    if t.tzinfo is None:
        fail("members_asof: t 必须带时区")
    t_sh = t.tz_convert(SH).tz_localize(None).as_unit("us")
    t_et = t.tz_convert(ET).as_unit("us")
    d = pd.Timestamp(d).as_unit("us")
    out_seen_known = df.out_known_at.notna() & (df.out_known_at <= t_et)
    if mode == "as_known":
        seen = df.available_at <= t_sh
        out_seen = out_seen_known
    elif mode == "pub_backcast":                     # 研究口径: 有前视假设, 产物须标注
        seen = df.pub_available_at <= t_sh
        v20 = df.out_known_class == "v20_primary"
        out_seen = (v20 & df.out_date.notna() & (df.out_date + pd.Timedelta(hours=18) <= t_sh)) | (~v20 & out_seen_known)
    else:
        fail(f"members_asof: 未知 mode {mode}")
    eff_out = df.out_date.where(out_seen)
    return df[seen & (df.in_date <= d) & (eff_out.isna() | (d <= eff_out))]


# ---------- 契约 (r3) ----------
def to_contract(m, sb, revision):
    names = sb.assign(iid=sb.ts_code.map(norm_code)).dropna(subset=["iid"]).drop_duplicates("iid").set_index("iid")["name"]
    out = m.copy()
    out["ts_code"] = out.instrument_id.map(to_ts)
    out["name"] = out.instrument_id.map(names)                                  # 当前名称, 不是 PIT 名称 (P3-8)
    out["known_at"] = out["known_at"].dt.tz_convert(ET).astype(ET_US)
    out["out_known_at"] = out["out_known_at"].dt.tz_convert(ET).astype(ET_US)
    eff = out.in_date + pd.Timedelta(hours=18)                                  # 无时区 = Asia/Shanghai 墙钟
    kn = to_sh_naive(out["known_at"])
    out["available_at"] = pd.concat([eff, kn], axis=1).max(axis=1).astype("datetime64[us]")
    floor = out.in_date.where(out.in_date >= SW2021_PUB, SW2021_PUB) + pd.Timedelta(hours=18)
    late = out.known_class.isin(["late_key_added", "repull_new"])
    out["pub_available_at"] = floor.where(~late, out["available_at"]).astype("datetime64[us]")
    out["source"] = "tushare.index_member_all(SW2021)"
    out["revision"] = revision
    out["promotion_approved"] = False
    out = out[[c for c, _ in CONTRACT]]
    for c, t in CONTRACT:
        if t != ET_US:
            out[c] = out[c].astype(t)
    return out.sort_values(["instrument_id", "in_date", "l1_code"], kind="mergesort").reset_index(drop=True)


def validate_contract(df):
    got = [(c, str(df[c].dtype)) for c in df.columns]
    if got != [(c, t) for c, t in CONTRACT]:
        fail(f"schema 契约不符: {got}")
    if (df.available_at < df.in_date + pd.Timedelta(hours=18)).any():
        fail("available_at 早于 in_date 18:00")
    if (df.available_at < to_sh_naive(df.known_at)).any():
        fail("available_at 早于 known_at")                                       # 回填行不得用 in_date 18:00
    if (df.pub_available_at > df.available_at).any():
        fail("pub_available_at 晚于 available_at")
    bad_q = set(df.quality_status) - {"ok", "out_date_inferred", "out_date_inferred_natural_day"}
    if bad_q:
        fail(f"quality_status 非法取值: {bad_q}")


# ---------- dry-run 内容哈希 (r3 新增: P2-3) ----------
def _canon(s):
    if pd.api.types.is_datetime64_any_dtype(s):
        fmt = "%Y-%m-%dT%H:%M:%S.%f" + ("%z" if getattr(s.dt, "tz", None) is not None else "")
        return s.dt.strftime(fmt).astype("string").fillna("\\N")
    return s.astype("string").fillna("\\N")


def content_sha(df):
    # 按契约排序后逐列规范化成字符串再算 sha; 不依赖 parquet 元数据, parquet 回读后应得同值
    validate_contract(df)
    d = df.sort_values(["instrument_id", "l1_code", "in_date"], kind="mergesort").reset_index(drop=True)
    h = hashlib.sha256(json.dumps([[c, str(d[c].dtype)] for c in d.columns]).encode("utf-8"))
    cols = [_canon(d[c]).tolist() for c in d.columns]
    for row in zip(*cols):
        h.update(("\x1f".join(row) + "\n").encode("utf-8"))
    return h.hexdigest()


# ---------- 通过判据 (r3 新增: P2-4 / P3-5 / P3-7) ----------
def daily_missing_codes(t, days, sb, dmap):
    out = {}
    for d in days:
        out[d.strftime("%Y%m%d")] = sorted(listed_on(d, sb, dmap) - set(t[is_member(t, d)].instrument_id))
    return out


def listed_after(as_of, sb):
    s = sb[sb.ts_code.str.fullmatch(r"\d{6}\.(SH|SZ)")]
    ld = parse_dates(s.list_date, "stock_basic.list_date")
    return set(s[ld > pd.Timestamp(as_of)].ts_code.map(norm_code))


def acceptance(step, miss_after, gap, new_listed, non_a, nds, conf, inc_diff, n_base_keys, recon, date_info, sets46):
    acc = {}

    def chk(name, ok, got, want):
        acc[name] = {"ok": None if ok is None else bool(ok), "got": got, "want": want}

    miss = sorted(set().union(*miss_after.values())) if miss_after else []
    unexplained = sorted(set(miss) - set(gap) - set(new_listed))
    chk("daily_missing_after", not unexplained, {"n_codes": len(miss), "unexplained": unexplained[:50]},
        "全为 0; 或只差 as_of 之后新上市的股票 (P3-7); 其余差异须逐只列进 source_gap")
    chk("non_a_share_excluded", set(non_a) == NON_A_EXPECTED, sorted(non_a), sorted(NON_A_EXPECTED))
    nd = nds.get("normdiff_vs_raw0108")
    if nd is not None:
        chk("normdiff_vs_raw0108", len(nd) == 0, len(nd), "0 行 (唯一差异 T00018 已被 norm_code 两侧剔除)")
    reasons = conf["reason"].value_counts().to_dict() if len(conf) and "reason" in conf else {}
    chk("conflicts_by_reason", reasons.get("deleted_vs_89d4afa3_baseline", 0) == 0 and reasons.get("deleted", 0) == 0,
        reasons, "deleted 类为 0; 其余按 reason 计数披露")
    chk("recon_rows", all(r["rows_in"] - r["dropped_non_a_rows"] - r["dropped_exact_dup_rows"] == r["rows_out"] for r in recon),
        recon, "每个来源 rows_in - 非 A 股 - 完全重复 = rows_out (P3-4)")
    chk("in_date_after_as_of", None, date_info["in_date_after_as_of"], "披露, 期望 0")
    for name, s in sets46.items():                                              # 核对清单: 46/235/68 用 v2.0 实测复核
        chk(f"open_rows_{name}", s["n_with_open"] == s["n"], s, "全部有 open 行")
    if step == "v2.1":
        k = inc_diff["kind"].value_counts().to_dict() if len(inc_diff) else {}
        for kind in ("in_base_not_in_repull", "out_date_conflict_ignored"):
            frac = k.get(kind, 0) / max(n_base_keys, 1)
            chk(f"inc_{kind}_frac", frac <= INC_ROLLBACK_FRAC, round(frac, 6), f"<= {INC_ROLLBACK_FRAC} (超过即回退, 不更新指针; P3-5)")
        chk("inc_out_lt_in", k.get("out_date_lt_in_ignored", 0) + k.get("key_added_out_lt_in_ignored", 0) == 0,
            {x: k.get(x, 0) for x in ("out_date_lt_in_ignored", "key_added_out_lt_in_ignored")}, "0")
        chk("inc_kinds", None, k, "按类披露")
    checks_ok = all(v["ok"] for v in acc.values() if v["ok"] is not None)
    return acc, checks_ok


# ---------- 历史覆盖 (r3 新增: P2-5) ----------
def month_ends(tdays, lo="20180101", hi="20261031"):
    s = pd.Series(sorted(t for t in tdays if pd.Timestamp(lo) <= t <= pd.Timestamp(hi)))
    return s.groupby(s.dt.to_period("M")).max().tolist()


def history_coverage(t, tdays, sb, dmap):
    # 月末取样 2018-01..2026-10; 股票池 = 当日在市 (含后来退市的); 两种读法各报缺成分数
    ever_delisted = set(dmap.index.map(norm_code)) - {None}
    rows = []
    for d in month_ends(tdays):
        uni = listed_on(d, sb, dmap)
        eff = set(t[is_member(t, d)].instrument_id)
        tk = (d + pd.Timedelta(hours=18)).tz_localize(SH)
        known = set(members_asof(t, d, tk, "as_known").instrument_id)
        pub = set(members_asof(t, d, tk, "pub_backcast").instrument_id)
        miss = uni - eff
        rows.append({"date": d.strftime("%Y%m%d"), "universe": len(uni), "universe_later_delisted": len(uni & ever_delisted),
                     "missing_effective": len(miss), "missing_effective_later_delisted": len(miss & ever_delisted),
                     "missing_as_known": len(uni - known), "missing_pub_backcast": len(uni - pub)})
    return pd.DataFrame(rows)


def write_reports(od, summary_extra, **frames):
    od = pathlib.Path(od)
    od.mkdir(parents=True, exist_ok=False)          # dry-run 证据目录必须新建
    summary = {}
    for name, obj in frames.items():
        if isinstance(obj, pd.DataFrame):
            obj.to_csv(od / f"{name}.csv", index=False)
            summary[name] = len(obj)
        else:
            (od / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
            summary[name] = "json"
    summary.update(summary_extra)                   # content_sha256 / acceptance / checks_ok / inputs / runtime
    atomic_write_json(summary, od / "summary.json")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ok", action="append", required=True)
    ap.add_argument("--step", choices=["v2.0", "v2.1"], required=True)     # v2.2 及以后另行修订 (P3-6)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--repull_dir")
    ap.add_argument("--pull_ok")                                           # r3: 重拉目录以 pull .ok 为准
    ap.add_argument("--dryrun_dir")                                        # r3 P2-3: execute 必填
    ap.add_argument("--allow-shrink", dest="allow_shrink", action="store_true")
    ap.add_argument("--out_dir", default=None)
    ap.add_argument("--sets46", required=True)                             # 46/235/68 代码清单 json, 由 .ok 钉 sha
    a = ap.parse_args(argv)
    mode = ("execute" if a.execute else "dry_run") + ("_increment" if a.step == "v2.1" else "")
    modes = [mode]
    if a.allow_shrink:
        if a.step == "v2.0":
            fail("v2.0 首次写入为硬闸门, 不接受 --allow-shrink")
        modes.append("allow_shrink")
    deps = {k: p for k, (p, _) in INPUTS.items()}
    deps["sets46"] = pathlib.Path(a.sets46)
    if a.repull_dir:
        if not a.pull_ok:
            fail("--repull_dir 需要 --pull_ok")
        deps["pull_ok"] = pathlib.Path(a.pull_ok)
        deps["repull_complete"] = pathlib.Path(a.repull_dir) / "COMPLETE.json"
    if a.execute:
        if not a.dryrun_dir:
            fail("execute 需要 --dryrun_dir (Arch 审过的 dry-run 证据目录)")
        deps["dryrun_summary"] = pathlib.Path(a.dryrun_dir) / "summary.json"   # .ok 用 dep_sha256_dryrun_summary 钉住
    G = enforce(__file__, a.ok, modes=modes, deps=deps)                    # 第一件事
    kv = {o: parse_ok(pathlib.Path(o)) for o in a.ok}
    check_interpreter(kv)
    if a.execute:
        check_unconsumed(a.ok)
    verify_inputs()
    stamp = dt.datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    od = pathlib.Path(a.out_dir or f"/tmp/sw_l1_pit_v2_{a.step}_{mode}_{stamp}")
    sb, dl = load_universe_frames()
    dmap = delist_map(sb, dl)
    tdays_all = trading_days("19900101", "20271231")
    cal_end = max(tdays_all)
    days = trading_days(*WIN)
    prev = pd.read_parquet(INPUTS["prev_0b1d"][0], columns=["instrument_id", "l1_code", "in_date", "out_date"])
    prev = prev.assign(instrument_id=prev.instrument_id.map(norm_code),
                       in_date=parse_dates(prev.in_date, "0b1d.in_date"), out_date=parse_dates(prev.out_date, "0b1d.out_date"))
    prim, non_a, rec_p = load_primary()
    recon = [rec_p]
    raw_sha = verify_raw_list(RAW_0108, INPUTS["raw0108_list"][0])
    raw, _, rec_r = load_raw_dir(RAW_0108)                                 # r3: load_raw_dir 透传 _std 的 recon
    recon.append(rec_r)
    rep_sha, rep_done, inc_diff, n_base_keys, bad = None, None, pd.DataFrame(), 0, []
    if a.repull_dir:
        pull_kv = parse_ok(pathlib.Path(a.pull_ok))
        rep_sha, rep_done = validate_repull_dir(a.repull_dir, pull_kv["signed_et"], sha(pathlib.Path(a.pull_ok)))
        if not _marker(a.pull_ok).exists():
            fail("pull .ok 没有 consumed 标记, 重拉来源不可证")
        rep0, non_a_rep, rec_q = load_raw_dir(a.repull_dir)
        recon.append(rec_q)
    if a.step == "v2.0":
        if read_pointer() is not None:
            fail("已有已审版本, v2.0 不能重复写")
        m, conf = resolve(prim, tdays_all)
        check_one_open(m)
        date_info = check_dates(m, PRIMARY_AS_OF)
        gate = hard_gate(m, prim)
        deleted = sorted(keys(prim) - keys(m))
        conf = pd.concat([conf, pd.DataFrame([dict(instrument_id=k[0], l1_code=k[1], in_key=k[2], reason="deleted_vs_89d4afa3_baseline",
                                                   explain="v2 无此键; 闸门拒绝") for k in deleted])])
        nds = {"normdiff_vs_raw0108": normdiff_all(m, raw)}
        if a.repull_dir:                                                  # gap2 预交付, 只出报告
            _, nds["gap2_delta"] = gap2_report(prim, rep0)
            nds["normdiff_v20_vs_repull"] = normdiff_all(m, rep0)
        as_of, tag = PRIMARY_AS_OF, "v2.0"
    else:
        ptr = read_pointer()                                              # r3: read_pointer 把 known_at/out_known_at 还原为 ET_US
        if ptr is None or ptr["version"] != "v2.0":
            fail("v2.1 需要已审 v2.0 指针")
        if not a.repull_dir:
            fail("v2.1 需要 --repull_dir 与 --pull_ok")
        non_a = sorted(set(non_a) | set(non_a_rep))
        base = ptr["df"][WORK]
        n_base_keys = len(keys(base))
        as_of = rep_done.strftime("%Y-%m-%d")
        rep = stamp_known(rep0, rep_done.isoformat(), ptr["as_of"], "repull")
        merged, inc_diff = merge_increment(base, rep, ptr["as_of"])
        m, conf = resolve(merged, tdays_all)
        check_one_open(m)
        date_info = check_dates(m, as_of)
        bad = increment_check(base, m)
        if bad:
            conf = pd.concat([conf, pd.DataFrame([dict(key=k, reason=r) for k, r in bad])])
        base_built = parse_tz(ptr["built_et"], "pointer.built_et")
        gate = soft_gate(m, base, delisted=delisted_between(base_built.date(), rep_done.date(), dmap),
                         shrink_granted="allow_shrink" in G["modes"])
        _, g2 = gap2_report(prim, rep0)
        nds = {"normdiff_v21_vs_repull": normdiff_all(m, rep0), "normdiff_v20_vs_repull": normdiff_all(base, rep0),
               "normdiff_v21_vs_raw0108": normdiff_all(m, raw), "gap2_delta": g2}
        tag = "v2.1"
    if pd.Timestamp(as_of) > cal_end:
        fail(f"as_of {as_of} 超出日历 {cal_end:%Y%m%d}; 须在 code-change .ok 中改钉日历包新版本 (r3 §1)")
    out = to_contract(m, sb, tag)
    validate_contract(out)
    csha = content_sha(out)
    gap = sorted(listed_on(pd.Timestamp(WIN[1]), sb, dmap) - set(out[out.out_date.isna()].instrument_id))
    miss_before, miss_after = daily_missing_codes(prev, days, sb, dmap), daily_missing_codes(out, days, sb, dmap)
    s46 = json.loads(pathlib.Path(a.sets46).read_text())                  # {"235": [...], "68": [...], "46": [...]}
    open_ids = set(out[out.out_date.isna()].instrument_id)
    sets46 = {k: {"n": len(v), "n_with_open": len({norm_code(x) for x in v} & open_ids)} for k, v in s46.items()}
    acc, checks_ok = acceptance(tag, miss_after, gap, listed_after(as_of, sb), non_a, nds, conf, inc_diff,
                                n_base_keys, recon, date_info, sets46)
    checks_ok = checks_ok and bool(gate["ok"]) and not (tag == "v2.1" and bad)
    hist = history_coverage(out, tdays_all, sb, dmap)                     # P2-5 披露项
    extra = {"step": tag, "mode": mode, "as_of": as_of, "content_sha256": csha, "acceptance": acc, "checks_ok": checks_ok,
             "inputs": {k: (want or sha(p)) for k, (p, want) in INPUTS.items()}, "repull_dir": a.repull_dir,
             "repull_sha256": rep_sha, "repull_completed_et": rep_done.isoformat() if rep_done is not None else None,
             "runtime": runtime_info(), "recon": recon, "known_class_counts": out.known_class.value_counts().to_dict(),
             "out_known_class_counts": out.out_known_class.value_counts().to_dict(),
             "quality_status_counts": out.quality_status.value_counts().to_dict()}
    if a.execute:                                                         # P2-3: 与 Arch 审过的 dry-run 逐项比对
        dr = json.loads((pathlib.Path(a.dryrun_dir) / "summary.json").read_text())
        want_c = {v.get("dryrun_content_sha256") for v in kv.values()}
        # 内容哈希三方一致: dry-run summary / execute .ok 的 dryrun_content_sha256 / 本次重算
        got_c = dr.get("content_sha256")
        if want_c != {got_c} or got_c != csha:
            fail(f"execute 内容哈希 {csha} 与已审 dry-run / .ok 不一致: {got_c} / {want_c}")
        for k2 in ("step", "as_of", "inputs", "repull_dir", "repull_sha256"):
            if dr.get(k2) != json.loads(json.dumps(extra[k2], default=str)):
                fail(f"execute 与 dry-run 的 {k2} 不一致")
    summary = write_reports(od, extra, conflicts=conf, increment_diff=inc_diff,
                            daily_missing_before=pd.DataFrame([(d, len(v)) for d, v in miss_before.items()], columns=["date", "missing"]),
                            daily_missing_after=pd.DataFrame([(d, len(v)) for d, v in miss_after.items()], columns=["date", "missing"]),
                            twelve_codes_resolution=out[out.instrument_id.isin(TWELVE)],
                            source_gap=pd.DataFrame({"instrument_id": gap}),
                            non_a_share_excluded=pd.DataFrame({"code": non_a}),
                            history_coverage=hist,
                            shrink_gate={**{k: v for k, v in gate.items() if k != "missing_keys"},
                                         "missing_keys": gate.get("missing_keys", []), "info": {"vs_0b1d3432": info_missing_keys(out, prev)}},
                            **nds)
    print(json.dumps({"step": tag, "mode": mode, "checks_ok": checks_ok, "content_sha256": csha, "out_dir": str(od)}, ensure_ascii=False))
    if not checks_ok:
        fail(f"检查未通过, 证据在 {od}")
    if not a.execute:
        return 0
    final = SWD / f"sw_l1_pit_{tag}.parquet"
    s = atomic_write_parquet(out, final, len(out))
    if content_sha(read_contract_parquet(final)) != csha:                  # 回读后内容哈希不变
        fail("回读内容哈希不一致 (文件已写, 不更新指针; 报 Arch)")
    man = dict(table="sw_l1_pit", version=tag, path=str(final.relative_to(ROOT)), sha256=s, content_sha256=csha, rows=len(out),
               instruments=int(out.instrument_id.nunique()), open_rows=int(out.out_date.isna().sum()),
               as_of=as_of, built_et=now_et(), out_date_semantics="inclusive: member iff in_date <= d <= out_date",
               pit_semantics=PIT_SEMANTICS, pit_semantics_alt="pub_backcast (有前视假设: 10-10 快照的历史 = 当时发布的历史)",
               known_at_rule="known_at/out_known_at = Data 实际得知时间 (ET); v2.0 = PRIMARY_KNOWN_AT; v2.1 = COMPLETE.completed_et; 推断 out = 两行 known_at 较晚者",
               available_at_rule="max(in_date 18:00, known_at) 换算 Asia/Shanghai 墙钟, 无时区",
               pub_available_at_rule="v2.0 行: max(in_date, 2021-07-30) 18:00; 事后新增行: = available_at",
               primary_known_at=PRIMARY_KNOWN_AT, primary_known_at_upper=PRIMARY_KNOWN_AT_UPPER,
               primary_known_at_note="10-10 sha 未记录; 与 data_v2_bundle(.tar, 10-10 14:42 ET) 副本一致; 文件 mtime 因 10-18 01:13 恢复不可用",
               schema=CONTRACT, dates="in_date/out_date: datetime64[us] naive 零点 = Asia/Shanghai 日历日; known_at/out_known_at: datetime64[us, America/New_York]",
               join_rule="连接前双方统一 datetime64[us]; 用 as_of_join", runtime=extra["runtime"], recon=recon,
               inputs={k: {"path": str(p), "sha256": (want or sha(p))} for k, (p, want) in INPUTS.items()},
               raw0108=dict(sha256=raw_sha, status="source_unknown (supporting evidence only)"),
               repull=dict(dir=a.repull_dir, sha256=rep_sha, completed_et=extra["repull_completed_et"]) if rep_sha else None,
               primary=dict(sha256=INPUTS["primary"][1], status="accepted (condition_a_met, Arch 94e91ffa)"),
               time_evidence="lost: bak/0b1d3432 原始时间戳被 2026-10-18 01:13 ET 工作区恢复覆盖; 以 sha + 行级 diff 内容证据代替",
               non_a_share_excluded=non_a, source_gap=gap, n_conflicts=len(conf), acceptance=acc,
               known_class_counts=extra["known_class_counts"], out_known_class_counts=extra["out_known_class_counts"],
               name_note="name 为 stock_basic 当前名称, 不是 PIT 名称", ok_gate=G, promotion_approved=False)
    atomic_write_json(man, final.with_suffix(".manifest.json"))
    consume_ok(a.ok, {"step": tag, "out": str(final), "sha256": s, "content_sha256": csha})
    print("WROTE", final, s, "-> 待 Arch 审回执后由 Arch 更新指针", POINTER)
    return 0


def read_contract_parquet(p):
    # 回读并还原契约 dtype (parquet 保存 tz-aware 列的时区; 仍逐列 astype 一次以统一精度)
    df = pd.read_parquet(p)
    for c, t in CONTRACT:
        df[c] = df[c].dt.tz_convert(ET).astype(ET_US) if t == ET_US else df[c].astype(t)
    return df


def read_pointer(path=POINTER):
    # r3: 与 r2 相同, 但用 read_contract_parquet 回读, 并校验契约与 content_sha256
    path = pathlib.Path(path)
    if not path.exists():
        return None
    j = json.loads(path.read_text())
    for k in ("version", "path", "sha256", "manifest", "manifest_sha256", "as_of", "built_et", "approved_by", "approved_et"):
        if k not in j:
            fail(f"指针缺字段 {k}")
    parse_tz(j["built_et"], "pointer.built_et")
    parse_tz(j["approved_et"], "pointer.approved_et")
    p = ROOT / j["path"]
    if sha(p) != j["sha256"] or sha(ROOT / j["manifest"]) != j["manifest_sha256"]:
        fail("指针指向的文件 sha 不符")
    df = read_contract_parquet(p)
    validate_contract(df)
    man = json.loads((ROOT / j["manifest"]).read_text())
    if content_sha(df) != man.get("content_sha256"):
        fail("指针指向文件的内容哈希与 manifest 不符")
    j["df"] = df
    return j
```

## 4. v2 schema 契约 r3（替换 r2 §6.6 的表）
| # | 列 | dtype | 说明 | 0b1d3432 对应 | 89d4afa3 对应 |
|---|---|---|---|---|---|
| 1 | instrument_id | string | sh.600000 形式，唯一规范化 | instrument_id | instrument_id |
| 2 | ts_code | string | 600000.SH，由 instrument_id 推出 | ts_code | （推出） |
| 3 | name | string | stock_basic（2ef2d71d）的**当前**名称，**不是 PIT 名称**（P3-8） | name | （无） |
| 4 | l1_code | string | 申万一级代码 | l1_code | sw_code |
| 5 | l1_name | string | 申万一级名称 | l1_name | sw_name |
| 6 | in_date | datetime64[us] | 无时区、零点 = Asia/Shanghai 日历日；生效日 | in_date | in_date |
| 7 | out_date | datetime64[us] | 同上；含当天（最后在任日）；空 = 在任；≥ in_date；≤ 版本 as_of | out_date | out_date |
| 8 | is_new | string | Y/N（来源原样） | is_new | is_new |
| 9 | known_at | datetime64[us, America/New_York] | Data 实际得知入表记录的时间（§2.3），非空 | （新增） | （新增） |
| 10 | out_known_at | datetime64[us, America/New_York] | Data 实际得知出表记录的时间；out_date 空则空 | （新增） | （新增） |
| 11 | available_at | datetime64[us] | 严格口径：max(in_date 18:00, known_at)，Asia/Shanghai 墙钟、无时区 | available_at（口径不同） | 不沿用，重算 |
| 12 | pub_available_at | datetime64[us] | 研究口径：v2.0 行 max(in_date, 2021-07-30) 18:00；事后新增行 = available_at；恒 ≤ available_at | （新增） | （新增） |
| 13 | known_class | string | v20_primary / pre_sw2021_backcast / late_key_added / repull_new | （新增） | （新增） |
| 14 | out_known_class | string | none / v20_primary / out_filled_repull / out_inferred_resolve | （新增） | （新增） |
| 15 | source | string | tushare.index_member_all(SW2021) | source | source |
| 16 | src | string | 行来源：89d4afa3 / 重拉目录名 | （新增） | — |
| 17 | revision | string | v2.0 / v2.1 | （新增） | revision |
| 18 | quality_status | string | ok / out_date_inferred / out_date_inferred_natural_day（P3-3） | （新增） | quality_status |
| 19 | promotion_approved | bool | 恒为 False | promotion_approved | — |

- validate_contract 除列与 dtype 外还检查：available_at ≥ in_date 18:00；available_at ≥ known_at（换算上海墙钟）——**这条保证事后回填行不会用 in_date 18:00**；pub_available_at ≤ available_at；quality_status 取值合法。
- 连接规则（P2-2）：任何与本表的 as-of 连接，**连接前双方统一为 datetime64[us]**；带时区列只和同时区的列连接；推荐用 as_of_join。按 ns 构造的日期键直接 merge_asof 会在 pandas 3.0.6 报 MergeError。
- 0b1d3432 的实际 dtype 仍未读，列入 §6 第 2 步只读探查（r2 §14-2 不变）。

## 5. selftest 修订（tests/test_sw_l1_pit_v2_build.py；只用合成数据）
- 门禁不变：先 enforce(__file__, [OK_PATH], modes=["selftest"], deps={...}) 再 import 被测模块；.ok 须 scope=selftest、allow_real_data=false、out_dir 在 /tmp 且有 expires_et。运行命令的解释器改为 /workspace/qlvenv/bin/python（P3-1）。
- r2 用例的调整：_df 改为产出 WORK 列；test_repull_dir_validation 由 test_repull_dir_validation_r3 替换；test_contract_columns_and_dtypes 由 test_contract_r3_columns_and_guards 替换；test_increment_adds_keys_and_fills_out_date_only 改为传 base_as_of 并用 _rep 构造重拉行；其余 r2 用例只换构造函数，断言不变。
- 新增用例覆盖：P1-1 (a)(b)(c) 三类与两种读法（含“出表已生效但 t 时未知仍视为在任”、t 无时区拒绝）；P2-1 日历之前的自然日推断；P2-2 ns 对 us 连接与时区不一致拒绝；P2-3 内容哈希对行序稳定、parquet 回读不变、知情时间改动即变；P2-4 / P3-5 / P3-7 判据；P2-5 历史覆盖含后来退市股票；P2-6 out_date < in_date、晚于 as_of、增量中 out < in 不采纳、已有行知情时间不可改；P3-1 解释器钉；P3-3 推断标记；P3-4 行数对账；r3 自查的重拉目录校验。
```python
# ===== r3: tests/test_sw_l1_pit_v2_build.py 的增补与调整 (文本, 未落 repo, 未运行) =====
# 门禁部分 (enforce 在 import 被测模块之前, scope=selftest, allow_real_data=false, out_dir 在 /tmp) 与 r2 §6.5 相同.
# 运行 (仅在 selftest .ok 签发后): PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python tests/test_sw_l1_pit_v2_build.py
# r3 调整: _df 改为产出 WORK 列 (默认按 primary 打知情时间); 受影响的 r2 用例改用 _df / _rep.
PK = B.PRIMARY_KNOWN_AT
REP_T = "2026-11-20T21:30:00-05:00"


def _df(rows, known=PK, kind="primary", as_of="2026-10-10"):
    d = pd.DataFrame(rows, columns=COLS[:6])
    d["src"] = "t"
    d["in_date"] = B.parse_dates(d.in_date, "in")
    d["out_date"] = B.parse_dates(d.out_date, "out")
    return B.stamp_known(d, known, as_of, kind)


def _rep(rows):
    return _df(rows, known=REP_T, kind="repull")


def _sb(*codes):
    return pd.DataFrame({"ts_code": list(codes), "name": ["n"] * len(codes)})


def _ts(s):
    return pd.Timestamp(s)


# --- P1-1 (a): SW2021 发布前的回填行 ---
def test_known_class_a_pre_sw2021():
    out = B.to_contract(_df([["sz.000537", "801180.SI", "", "19931210", None, "Y"]]), _sb("000537.SZ"), "v2.0")
    r = out.iloc[0]
    assert r.known_class == "pre_sw2021_backcast"
    assert r.pub_available_at == _ts("2021-07-30 18:00")
    assert r.available_at == _ts("2026-10-10 22:01:23")              # 10:01:23 ET = 22:01:23 上海
    assert r.available_at != r.in_date + pd.Timedelta(hours=18)
    assert str(out.known_at.dtype) == "datetime64[us, America/New_York]"


def test_v20_primary_after_sw2021_pub_floor_not_applied():
    out = B.to_contract(_df([["sz.000001", "801780.SI", "", "20230103", None, "Y"]]), _sb("000001.SZ"), "v2.0")
    assert out.pub_available_at.iloc[0] == _ts("2023-01-03 18:00")
    assert out.available_at.iloc[0] == _ts("2026-10-10 22:01:23")


# --- P1-1 (b): v2.1 新增键, in_date 早于 v2.0 as_of ---
def test_known_class_b_late_key_never_in_date_1800():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    rep = _rep([["sz.000001", "801780.SI", "", "20140101", None, "Y"],
                ["sz.000002", "801180.SI", "", "20250102", None, "Y"],
                ["sz.000003", "801010.SI", "", "20261015", None, "Y"]])
    new, diff = B.merge_increment(base, rep, "2026-10-10")
    out = B.to_contract(new, _sb("000001.SZ", "000002.SZ", "000003.SZ"), "v2.1").set_index("instrument_id")
    assert out.loc["sz.000002", "known_class"] == "late_key_added"
    assert out.loc["sz.000003", "known_class"] == "repull_new"
    for c in ("sz.000002", "sz.000003"):
        assert out.loc[c, "available_at"] == _ts("2026-11-21 10:30:00")    # 21:30 EST = 次日 10:30 上海
        assert out.loc[c, "pub_available_at"] == out.loc[c, "available_at"]
    assert B.increment_check(base, new) == []


# --- P1-1 (c): 补的 out_date 与推断的 out_date ---
def test_known_class_c_out_filled_uses_repull_time():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    rep = _rep([["sz.000001", "801780.SI", "", "20140101", "20261020", "N"]])
    new, diff = B.merge_increment(base, rep, "2026-10-10")
    r = new.iloc[0]
    assert r.out_known_class == "out_filled_repull" and r.out_known_at == pd.Timestamp(REP_T)
    assert r.known_at == pd.Timestamp(PK)                                # 入表知情时间不变
    assert set(diff.kind) == {"out_date_filled"}


def test_out_filled_backdated_is_labelled():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    rep = _rep([["sz.000001", "801780.SI", "", "20140101", "20260901", "N"]])
    _, diff = B.merge_increment(base, rep, "2026-10-10")
    assert list(diff.kind) == ["out_date_filled_backdated"]


def test_known_class_c_inferred_out_known_at():
    a = _df([["sz.002481", "801120.SI", "", "20111010", None, "Y"]])
    b = _rep([["sz.002481", "801010.SI", "", "20261015", None, "Y"]])
    m, conf = B.resolve(pd.concat([a, b], ignore_index=True), TD)
    old = m[m.l1_code == "801120.SI"].iloc[0]
    assert old.out_known_class == "out_inferred_resolve" and old.out_known_at == pd.Timestamp(REP_T)
    assert old.quality_status == "out_date_inferred"                     # P3-3


# --- P1-1: 读法 ---
def test_members_asof_no_lookahead():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    rep = _rep([["sz.000001", "801780.SI", "", "20140101", "20261020", "N"],
                ["sz.000001", "801010.SI", "", "20261021", None, "Y"]])
    new, _ = B.merge_increment(base, rep, "2026-10-10")
    out = B.to_contract(new, _sb("000001.SZ"), "v2.1")
    t_before = pd.Timestamp("2026-10-05T09:00:00-04:00")
    assert B.members_asof(out, _ts("2020-01-02"), t_before, "as_known").empty      # 10-10 之前严格口径不可用
    assert len(B.members_asof(out, _ts("2020-01-02"), t_before, "pub_backcast")) == 1
    t_mid = pd.Timestamp("2026-11-01T09:00:00-04:00")                              # 出表已生效但还不知道
    got = B.members_asof(out, _ts("2026-10-30"), t_mid, "as_known")
    assert list(got.l1_code) == ["801780.SI"]
    t_after = pd.Timestamp("2026-11-23T09:00:00-05:00")
    got = B.members_asof(out, _ts("2026-10-30"), t_after, "as_known")
    assert list(got.l1_code) == ["801010.SI"]
    _raises(lambda: B.members_asof(out, _ts("2026-10-30"), pd.Timestamp("2026-11-23 09:00"), "as_known"), "时区")


# --- P2-1: 日历之前的 out_date 推断 ---
def test_pre_calendar_natural_day():
    d = _df([["sz.000537", "801180.SI", "", "19931210", None, "Y"],
             ["sz.000537", "801010.SI", "", "20040601", None, "Y"]])
    td05 = [pd.Timestamp(x) for x in pd.bdate_range("2005-01-04", "2026-12-31")]
    m, conf = B.resolve(d, td05)
    old = m[m.l1_code == "801180.SI"].iloc[0]
    assert old.out_date == _ts("2004-05-31") and old.quality_status == "out_date_inferred_natural_day"
    B.check_one_open(m)


# --- P2-2: us / ns 连接 ---
def test_as_of_join_ns_vs_us_and_tz_refusal():
    left = pd.DataFrame({"d": pd.to_datetime(["2026-10-12", "2026-10-13"]).astype("datetime64[ns]"), "k": ["a", "a"]})
    right = pd.DataFrame({"t": pd.to_datetime(["2026-10-10"]).astype("datetime64[us]"), "k": ["a"], "v": [1]})
    j = B.as_of_join(left, right, "d", "t", by="k")
    assert j.v.tolist() == [1, 1] and str(j.d.dtype) == "datetime64[us]"
    tz = right.assign(t=right.t.dt.tz_localize("Asia/Shanghai"))
    _raises(lambda: B.as_of_join(left, tz, "d", "t", by="k"), "时区")


# --- P2-3: 内容哈希 ---
def test_content_sha_stable_roundtrip_and_sensitive():
    sb = _sb("000001.SZ", "000002.SZ")
    m = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"], ["sz.000002", "801180.SI", "", "20150101", "20200101", "N"]])
    out = B.to_contract(m, sb, "v2.0")
    h = B.content_sha(out)
    assert B.content_sha(out.iloc[::-1].reset_index(drop=True)) == h
    f = _tmp() / "c.parquet"
    out.to_parquet(f, index=False)
    assert B.content_sha(B.read_contract_parquet(f)) == h
    m2 = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"], ["sz.000002", "801180.SI", "", "20150101", "20200101", "N"]], known="2026-10-10T14:42:00-04:00")
    assert B.content_sha(B.to_contract(m2, sb, "v2.0")) != h


# --- P2-4 / P3-5: 判据 ---
def test_acceptance_flags():
    base_args = dict(miss_after={"20261016": []}, gap=[], new_listed=set(), nds={"normdiff_vs_raw0108": pd.DataFrame()},
                     conf=pd.DataFrame(), inc_diff=pd.DataFrame(), n_base_keys=1000,
                     recon=[{"rows_in": 3, "dropped_non_a_rows": 1, "dropped_exact_dup_rows": 0, "rows_out": 2}],
                     date_info={"in_date_after_as_of": 0}, sets46={"46": {"n": 46, "n_with_open": 46}})
    assert B.acceptance("v2.0", non_a=["T00018"], **base_args)[1] is True
    assert B.acceptance("v2.0", non_a=["T00018", "X1"], **base_args)[1] is False
    bad = {**base_args, "miss_after": {"20261016": ["sz.000009"]}}
    assert B.acceptance("v2.0", non_a=["T00018"], **bad)[1] is False
    ok_new = {**bad, "new_listed": {"sz.000009"}}                       # P3-7: 只差 as_of 后新上市
    assert B.acceptance("v2.0", non_a=["T00018"], **ok_new)[1] is True
    inc = {**base_args, "inc_diff": pd.DataFrame({"kind": ["in_base_not_in_repull"] * 6})}
    acc, ok = B.acceptance("v2.1", non_a=["T00018"], **inc)
    assert ok is False and acc["inc_in_base_not_in_repull_frac"]["got"] == 0.006


# --- P2-6: out_date 合法性 ---
def test_check_dates_refuses_out_lt_in_and_after_as_of():
    _raises(lambda: B.check_dates(_df([["sz.000001", "a", "", "20200101", "20191231", "N"]]), "2026-10-10"), "out_date < in_date")
    _raises(lambda: B.check_dates(_df([["sz.000001", "a", "", "20200101", "20261012", "N"]]), "2026-10-10"), "晚于 as_of")
    assert B.check_dates(_df([["sz.000001", "a", "", "20261012", None, "Y"]]), "2026-10-10") == {"in_date_after_as_of": 1}


def test_increment_out_lt_in_ignored():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    rep = _rep([["sz.000001", "801780.SI", "", "20140101", "20131231", "N"]])
    new, diff = B.merge_increment(base, rep, "2026-10-10")
    assert list(diff.kind) == ["out_date_lt_in_ignored"] and new.out_date.isna().all()


def test_increment_check_refuses_known_at_change():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]])
    new = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"]], known=REP_T)
    assert ("sz.000001", "801780.SI", "20140101") in {k for k, r in B.increment_check(base, new) if r == "known_at_changed"}


# --- P2-5: 历史覆盖含后来退市的股票 ---
def test_history_coverage_counts_later_delisted():
    sb = pd.DataFrame({"ts_code": ["000001.SZ", "000002.SZ"], "name": ["a", "b"],
                       "list_date": ["20100101", "20100101"], "delist_date": [None, "20200615"]})
    dl = pd.DataFrame({"ts_code": ["000002.SZ"], "delist_date": ["20200615"]})
    dmap = B.delist_map(sb, dl)
    t = B.to_contract(_df([["sz.000001", "801780.SI", "", "20100101", None, "Y"]]), sb, "v2.0")
    h = B.history_coverage(t, TD, sb, dmap)
    r = h[h.date == "20180131"].iloc[0]
    assert r.universe == 2 and r.missing_effective == 1 and r.missing_effective_later_delisted == 1
    assert h[h.date == "20201030"].iloc[0].universe == 1


# --- r3 自查: 重拉目录以 pull .ok 为准 (替换 r2 test_repull_dir_validation) ---
def test_repull_dir_validation_r3():
    root = _tmp()
    raw = root / "index_member_all"
    raw.mkdir()
    rp = root / "index_member_all_20261120_213000"
    rp.mkdir()
    f = rp / "801010.SI_Y.parquet"
    pd.DataFrame({"a": [1]}).to_parquet(f)
    done = pd.Timestamp.now(tz="America/New_York")
    rp2 = root / f"index_member_all_{done:%Y%m%d}_213000"
    rp.rename(rp2)
    f = rp2 / "801010.SI_Y.parquet"
    cj = {"files": {f.name: B.sha(f)}, "completed_et": done.isoformat(), "pull_ok_sha256": "x"}
    (rp2 / "COMPLETE.json").write_text(json.dumps(cj))
    got, t = B.validate_repull_dir(rp2, "2026-01-01T00:00:00-05:00", "x", raw0108=raw, n_files=1)
    assert t == pd.Timestamp(done.isoformat())
    _raises(lambda: B.validate_repull_dir(rp2, "2026-01-01T00:00:00-05:00", "y", raw0108=raw, n_files=1), "pull_ok_sha256")
    _raises(lambda: B.validate_repull_dir(rp2, "2099-01-01T00:00:00-05:00", "x", raw0108=raw, n_files=1), "早于")
    _raises(lambda: B.validate_repull_dir(rp2, "2026-01-01T00:00:00", "x", raw0108=raw, n_files=1), "时区")
    _raises(lambda: B.validate_repull_dir(raw, "2026-01-01T00:00:00-05:00", "x", raw0108=raw, n_files=1), "RAW_0108")


# --- P2-11 / r3 契约 (替换 r2 test_contract_columns_and_dtypes) ---
def test_contract_r3_columns_and_guards():
    out = B.to_contract(_df([["sz.000001", "801780.SI", "银行", "20140101", None, "Y"]]), _sb("000001.SZ"), "v2.0")
    B.validate_contract(out)
    assert [c for c, _ in B.CONTRACT][8:12] == ["known_at", "out_known_at", "available_at", "pub_available_at"]
    bad = out.copy()
    bad["available_at"] = (bad.in_date + pd.Timedelta(hours=18)).astype("datetime64[us]")       # 回填行用 in_date 18:00
    _raises(lambda: B.validate_contract(bad), "known_at")


# --- P3-1: 解释器 ---
def test_interpreter_pin_refuses_other():
    _raises(lambda: B.check_interpreter({"x.ok": {"interpreter": "/usr/bin/python3"}}), "interpreter")


# --- P3-4: 行数对账 ---
def test_std_recon():
    d = pd.DataFrame([["600000.SH", "801780.SI", "银行", "20140101", None, "Y"],
                      ["600000.SH", "801780.SI", "银行", "20140101", None, "Y"],
                      ["T00018", "801780.SI", "x", "20140101", None, "Y"]],
                     columns=["code", "l1_code", "l1_name", "in_date", "out_date", "is_new"])
    m, non_a, rec = B._std(d, "code", "t")
    assert rec == {"src": "t", "rows_in": 3, "dropped_non_a_rows": 1, "dropped_exact_dup_rows": 1, "rows_out": 1}
```

## 6. 执行步骤与 .ok 清单（替换 r2 §7、§7.1）
1. 前置（不归 Data）：Arch / Eng 把 scripts_eng/ok_runner_pin.py（c7805d9a）提交入库。
2. 前置（Data，10-19 纸面跑完之后，只读 .ok 下）：生成 raw0108_sha256.txt（命令写死，P3-2：`cd data/v2/tushare_raw/index_member_all && sha256sum 801*.SI_[YN].parquet`，输出先写 /tmp 再原子落到 docs/v2/audit/sw_l1_pit_v2/raw0108_sha256.txt，每行“sha 两个空格 文件名”，不带路径）；探查 89d4afa3 / 0b1d3432 / stock_delisted_v2 / stock_basic 的列名与 dtype；计数 89d4afa3 中多 open、同键 open/closed、以及 2005-01-04 前的多 open（P2-1 备选证明）；生成 sets46 json。结果交 Arch。
3. Arch 审本 r3，签 code-change .ok（4 个文件：新建 sw_l1_pit_v2_build.py、新建 tests/test_sw_l1_pit_v2_build.py、修改 sw_pit_refresh.py（含 COMPLETE.json 新字段）、修改 nightly_update.py）。归档旧脚本到 _recovery/data/sw_l1_pit_v2_pre_<date>/ 后落代码。
4. selftest .ok → 跑 selftest（qlvenv）。
5. gap2 预交付：pull .ok → `sw_pit_refresh.py --pull-only`；dry_run .ok → `--step v2.0 --repull_dir <目录> --pull_ok <pull.ok> --sets46 <json>`，交 gap2_delta 与各 normdiff。
6. v2.0：dry_run → Arch 审报告（含 acceptance、content_sha256、history_coverage）→ execute .ok（钉 dep_sha256_dryrun_summary 与 dryrun_content_sha256）→ `--step v2.0 --execute --dryrun_dir <已审目录>` → 回执 → Arch 更新指针。
7. v2.1（实施日）：pull .ok → 重拉 → dry_run_increment（--pull_ok 同一个）→ Arch 审 → execute_increment .ok（钉 dry-run summary）→ 写 v2.1 → 回执 → Arch 决定是否更新指针。acceptance 的 P3-5 阈值超标即回退，停在 v2.0。
8. 队列三项 sw 标 superseded；下游迁移（§8）；迁移方 .ok 由 Arch 重签。
- 每次运行前：通知主 Agent 与 Arch，并对齐是否把 94322 停到 T；pgrep 无冲突进程、MemAvailable ≥ 2GB、.ok 的 expires_et 未过且 signed_et 不在未来；运行中只读 /proc 看 RSS 与状态。

| .ok | mode | 次数 | r3 新增要求 |
|---|---|---|---|
| code-change（4 个文件） | — | 一次 | — |
| selftest | selftest | 有效期内可重复 | interpreter=/workspace/qlvenv/bin/python |
| 只读探查（第 2 步） | 只读 | 一次 | — |
| pull（gap2 预交付 / 实施日） | pull | 单次 | COMPLETE.json 写 completed_et、pull_ok_sha256 |
| v2.0 dry_run | dry_run | 有效期内可重复 | interpreter；dep_sha256_sets46；有重拉时 dep_sha256_pull_ok、dep_sha256_repull_complete |
| v2.0 execute | execute | 单次 | 另加 dep_sha256_dryrun_summary、dryrun_content_sha256 |
| v2.1 dry_run_increment / execute_increment | 同名 | dry-run 可重复；execute 单次 | 同上 |

## 7. 修后预期（补充 r2 §8；P3-7）
- r2 §8 表中“修后预期 0”改为：**0，或只差 2026-10-10 之后新上市的股票**（v2.0 as_of 是 10-10，而窗口到 10-16）。acceptance 的 daily_missing_after 已按此判定。
- 上述是生效日口径（in_date ≤ d ≤ out_date）。按 as_known 口径，09-24..10-09 每天都会显示全部缺失（Data 10-10 才拿到 89d4afa3），回执会同时列出两种口径。
- known_class 预期分布（v2.0）：pre_sw2021_backcast 占多数（SW2021 回填历史），其余为 v20_primary；late_key_added / repull_new 只在 v2.1 出现。具体计数以 dry-run 为准。

## 8. 下游迁移（增补 r2 §13）
- 迁移方必须在三种读法中明确选择一种，并写进自己的产物元数据：
  1. **as_known（默认，严格知情时间 PIT）**：members_asof(..., mode="as_known")，或自行按 available_at ≤ t 且“出表须 out_known_at ≤ t 才生效”的规则实现。后果：2026-10-10 之前没有任何可用行，**历史回测不能用 v2 做严格 PIT 的行业中性**。
  2. **pub_backcast（研究口径）**：用 pub_available_at。假设 10-10 快照的历史就是申万当时发布的历史；SW2021 发布（2021-07-30）之前没有可用行；事后补的行仍用知情时间。产物须标注“非知情时间 PIT，依赖供应商历史假设”。
  3. **effective_dated（生效日口径）**：只看 in_date / out_date（r2 的 is_member）。产物须标注“不是知情时间 PIT，回填行有前视”，不得只写 PIT。
- 连接一律先统一 datetime64[us]（§4）。
- name 列是当前名称，不是 PIT 名称；需要 PIT 名称的消费方另议（P3-8）。
- 不在迁移范围的消费方不变：读 89d4afa3 的 g1g5、cs_panel、纸面跟踪、叶23 / 叶24（89d4afa3 不变）。
- 通知 Strategy、Intel、cs_panel 由主 Agent 负责；as_known 的后果须在通知里写明。

## 9. 回滚
- 同 r2 §10。r3 无新增写路径；所有产出仍是新版本文件，回滚 = 不更新或回退指针（由 Arch 操作）。

## 10. 开放项与待 Arch 决定的问题（替换 r2 §14）
1. **Q1 默认读法**：本方案默认 pit_semantics = as_known，pub_backcast 为研究口径。若 Arch 改定 effective_dated 或 pub_backcast 为默认，只需改 PIT_SEMANTICS 与 manifest 文字，列不变。
2. **Q2 PRIMARY_KNOWN_AT 取 fetch_time（10:01:23 ET）还是 tar 时间（14:42 ET）**：本方案取 fetch_time，上界进 manifest；对日频读者无实质差别（§2.3）。
3. **Q3 as_of_join / members_asof 放哪里**：目前写在构建脚本中；是否移到共享模块供 Strategy / Intel 复用，由 Arch 与两位 owner 定。
4. **Q4 out_date_filled_backdated**：P2-6 的二选一，本方案选“采纳并标注知情时间”。若 Arch 要“不采纳、记 out_date_conflict_ignored”，改 merge_increment 一处分支。
5. **Q5 sw_pit_refresh.py 的 COMPLETE.json 新字段**（completed_et、pull_ok_sha256）：需要在 r2 §6.2 diff 上加几行；r3 只描述，未重贴 diff。Arch 若要全文 diff，我出 r3.1。
6. ok_runner_pin.py 未入 git：前置条件，归 Arch 或 Eng（r2 §14-1 不变）。
7. 实际 dtype 与列名未读、89d4afa3 的冲突计数、sets46 json：§6 第 2 步只读探查后交（r2 §14-2、§14-3 不变）。
8. gap2（09-24..10-09）：Data 开放项，实施前交（r2 §14-4 不变）。
9. **v2.2 及以后的刷新**：--step 只有 v2.0 / v2.1；v2.2 起的入口另行修订方案，不在本方案范围（P3-6）。
10. nightly_update.py 改动影响工作日 05:55 ET 日更：须在实施窗口内与其它变更同批落地，同一 code-change .ok（r2 §14-6 不变）。
11. Arch 审查 P3-1 附带请 AI 复核“裸 python3 缺 pyarrow”的说法，不归 Data，已在回应表注明，由主 Agent 转 AI。

## 11. 本轮过程记录
- 只读命令（09:37–10:xx ET）：sha256sum（r2、r1 各版本、661f7055、f17f4771、日历文件与 manifest、trade_cal_pit.py、research_loop.py、sw_pit_freshness.py、intel_common.py）；rg 读源码与文档文本；Read 读 r2 全文、661f7055 全文、trade_cal_pit.py、sw_pit_freshness.py 前 70 行、optimizer_core_x2_run_v1_4.py 两小段。只用 rg 读了 89d4afa3 的 manifest.json（fetch_time 一行），没有读任何 parquet。
- 代码文本只在 /tmp/sw_r3/ 用 python3 的 ast.parse 做了语法检查（不 import、不执行），PYTHONDONTWRITEBYTECODE=1、nice -n 10。
- **失误（只读，无写入）**：起草时有三次把 `rg ... </dev/null` 接在管道后面，rg 的标准输入被 /dev/null 覆盖，于是改为递归搜索当前目录。前两次当前目录是 /workspace/QuantLab（模式分别为 arch.*sw 与一组函数名），产生约 9MB、50MB 的输出（已删除）；第三次当前目录是 /tmp/sw_r3（只有草稿，无影响）。没有写 repo、没有 import 项目代码；但前两次 rg 会打开并扫描 repo 内文件（rg 默认按 .gitignore 跳过部分目录、遇二进制即停，但不能排除读到 data/ 下文件的开头），违反了“不读数据文件”的要求，在此如实报告。之后的 rg 都写明了路径、不再接管道。

## 12. 审查回应表
### 12.1 r2 对 f17f4771 的回应
- 见 r2 §15，原样有效（Arch 661f7055 已确认 3 个 P1、11 个 P2、10 个 P3 都已逐条回应）。

### 12.2 r3 对 661f7055 的回应（新增）
| Arch 661f7055 条目 | 要求要点 | r3 处理 | 位置 |
|---|---|---|---|
| P1-1 缺知情时间 | known_at / out_known_at 或 backcast 标记；(a) max(in_date, 2021-07-30) 18:00；(b)(c) 取 as_of 或拉取日；manifest 写 pit_semantics；out_date 晚于 as_of 拒绝或标记；§13 写两种读法；selftest 三类用例 | 两列都加（ET 带时区，Data 实际得知时间），另加 known_class / out_known_class 标记；available_at 改为 max(in_date 18:00, known_at)，回填行不再用 in_date 18:00；(a) 的写法落在 pub_available_at；(b)(c) 取重拉完成时间，推断 out 取两行较晚 known_at；manifest 写 pit_semantics=as_known 与 alt；out_date 晚于 as_of 一律拒绝；三种读法；selftest (a)(b)(c) 与读法用例 | §2、§3.1–§3.5、§3.7、§4、§5、§8 |
| P2-1 日历起点 2005 | 2005 年前用自然日前一天并标 out_date_inferred；或只读计数证明不需要 | 两者都做：代码改自然日推断（quality_status=out_date_inferred_natural_day），只读探查时附计数 | §3.3、§5、§6 第 2 步 |
| P2-2 merge_asof us/ns | 契约写明连接前统一 us；as_of_join helper；selftest 覆盖 ns 对 us | 三项都做；另拒绝时区不一致与 NaT 键 | §3.7、§4、§5 |
| P2-3 execute 与 dry-run 无绑定 | summary.json 记契约表内容哈希；execute .ok 钉住；execute link 前重算比对 | content_sha；execute .ok 用 dep_sha256_dryrun_summary 钉 summary 文件并带 dryrun_content_sha256；写前三方比对，写后回读再比；step / as_of / inputs / repull 也比 | §3.8、§3.11、§6 |
| P2-4 判据只覆盖闸门 | acceptance 段写期望值；不符即 checks_ok=false；回执逐项报 | acceptance 函数与表；checks_ok 由 acceptance + 闸门 + increment_check 决定 | §3.9、§5 |
| P2-5 幸存者偏差 | 历史覆盖报告：月末取样 2018-01..2026-10，股票池含后来退市的，按月报缺成分数，列为披露项 | history_coverage，另报 as_known / pub_backcast 口径缺数 | §3.10、§5 |
| P2-6 out_date 合法性 | 拒绝 out_date < in_date；早于 as_of 的回补记 conflict_ignored 或标知情时间 | check_dates 拒绝 out < in 与晚于 as_of；merge_increment 不采纳 out < in；早于 as_of 的回补采纳并记 out_date_filled_backdated、out_known_at = 重拉时间（选“标知情时间”，Q4） | §3.4、§3.5、§5 |
| P2-7 日历包无交付物 | 单独方案；版本化新文件不覆盖 fa4260b8；纸面跑完前不写 data/v2/calendar；20130424 推导写进 manifest；写明 CAL pin 先后；纸面改读新日历另行审批 | 已拆出，见 docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md；本方案 CAL 继续钉 fa4260b8，切换须在同一 code-change .ok 中改钉，as_of 超出日历即拒绝 | §1、日历包方案 |
| P3-1 解释器与版本 | manifest 记 python / pandas / pyarrow；.ok 钉解释器 | 统一 /workspace/qlvenv/bin/python；.ok 的 interpreter 键 + check_interpreter；manifest.runtime | §3.1、§3.11、§5、§6 |
| P3-1 附：裸 python3 缺 pyarrow | 请 AI 复核 | 不归 Data，请主 Agent 转 AI | §10-11 |
| P3-2 raw0108 清单格式 | 写明生成命令（cd 进目录再 sha256sum） | 命令写死，不带路径 | §6 第 2 步 |
| P3-3 quality_status 全是 ok | 推断 out_date 标 out_date_inferred | out_date_inferred / out_date_inferred_natural_day | §3.3、§4 |
| P3-4 规范化前后行数对账 | 写进 manifest | _std 返回 recon，对账不平即拒绝，进 manifest 与 acceptance | §3.2、§3.9 |
| P3-5 回退未量化 | 给阈值并写进 acceptance | in_base_not_in_repull、out_date_conflict_ignored 各 ≤ 0.5% 的键，超过即回退 | §3.9 |
| P3-6 只有 v2.0 / v2.1 | §14 写明以后另行修订 | 已写 | §10-9 |
| P3-7 窗口与 as_of 不一致 | §8 预期改为“0 或只差 10-10 后新上市” | 已改，acceptance 同口径 | §7、§3.9 |
| P3-8 name 是当前名称 | §13 提醒 | 已写，契约与 manifest 也注明 | §4、§8 |
| 核对清单：46 只须用 v2.0 实测复核 | dry-run 复核 | acceptance 的 open_rows_235 / _68 / _46 | §3.9 |
| 核对清单：成功不只看退出码、幂等（部分通过） | 见 P2-3、P2-4 | 同上 | §3.8、§3.9 |
| 前置条件 ok_runner_pin.py 入库 | 归 Arch / Eng | 不变 | §6 第 1 步、§10-6 |
| 不变项 | 实施在 10-19 纸面之后；89d4afa3、87d769aa、fa4260b8 纸面前不动；真实数据运行各需 Arch .ok，一次一个 | 遵守 | §1、§6 |

### 12.3 主 Agent 转达要求的对应
| 要求 | 位置 |
|---|---|
| (a) known_at、out_known_at 两列，ET 带时区 | §2.2、§4 |
| (b) 回填行不得用 in_date 18:00 当 available_at；v2.0 取 10-10 拉取时间并披露不确定性；v2.1 取拉取时间；schema、读者行为、闸门检查、selftest | §2.3、§3.5、§3.7、§3.9、§4、§5、validate_contract |
| (c) 日历包拆出 | §1；DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md |
