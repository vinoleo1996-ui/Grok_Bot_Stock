# Arch 审查：Data 申万一级 PIT v2 修复方案 r3（增量，静态审）

- 审查对象：docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3.md，sha256 0f3caf22…（审前核对一致，1197 行）。
- 回应对象：Arch r2 审 docs/v2/ARCH_DATA_SW_L1_PIT_V2_R2_REVIEW_ZH.md（661f7055，审前核对一致）。
- 审查人：QuantLab Arch；签署时间：2026-10-18T10:16:36-04:00（ET）。
- 方式：只做静态审。只用 Read / rg / sha256sum / ls 读文档与源码文本；没读任何 parquet，没 import 项目代码，没 git apply，没提交。L 指被审 r3 文件行号。
- live=false，promotion=false。

## 结论：PASS with conditions（有条件通过）
- 661f7055 的 P1-1、P2-1…P2-7、P3-1…P3-8 在 §12.2（L1167-1190）逐条有对应，位置都能在正文找到，内容与要求一致。
- 知情时间设计成立：known_at / out_known_at 为 datetime64[us, America/New_York]（CONTRACT L185）；available_at = max(in_date 18:00, known_at)（L494-496）；validate_contract 在 L514-517 同时拒绝 available_at < in_date 18:00 与 available_at < known_at，回填行不可能再用 in_date 18:00。
  - 说明：in_date 18:00 是 Asia/Shanghai 墙钟（L494 注释），不是 ET；known_at 先换算成上海墙钟再取 max。这是正确口径（A 股收盘后），转述里写的「18:00 ET」不准确。
- §3.6 的自查结论正确：r2 用本次运行 .ok 的 signed_et 比重拉文件 mtime，execute_increment .ok 必然签在重拉之后，r2 会恒拒。r3 改为以 pull .ok 为准（L414-441、L682-686），dry-run 与 execute 钉同一份 pull .ok 与 COMPLETE.json，逻辑成立。
- 须在 r3.1 补 2 个 P2，并处理 P2-3 的知情时间取值，然后才签 code-change .ok。实施时间不变：10-19 17:40 纸面跑完之后，避开 10-19 16:40-18:40 ET。

## 发现

### P1
- 无。

### P2
- **P2-1 sw_pit_refresh.py 的 COMPLETE.json 新字段只有描述，没有可签的代码文本**（L119、§10 Q5 L1150）。code-change .ok 签的是确切文本。validate_repull_dir 依赖 completed_et 与 pull_ok_sha256（L423、L427），写入方不落地它就恒拒。须出 r3.1：给出 sw_pit_refresh.py 相对 r2 §6.2 diff 的完整增量 diff（含 completed_et 用 date 等价的带时区 ET、pull_ok_sha256 取所用 pull .ok 的 sha），以及 nightly_update.py 的 diff 与基线 sha。回答 Q5：要全文 diff。
- **P2-2 pull .ok 的 consumed 标记与 Arch 归档规则冲突**。_marker 是同目录的 <ok>.consumed.json（r2 L773-775），main 在 L685 检查 --pull_ok 路径旁的标记；但 Arch 规则是用后把 .ok 归档到 _consumed（sha8 + CONSUMED 标签）。须写明：--pull_ok 传 _consumed 下的归档路径，标记随 .ok 一起移动，归档文件逐字节不变，其 sha 必须同时等于 COMPLETE.json.pull_ok_sha256 与 dry-run / execute .ok 的 dep_sha256_pull_ok；selftest 加一例（标记缺失、归档后 sha 变化各拒绝一次）。
- **P2-3 PRIMARY_KNOWN_AT 的取值（Q2）**。10:01:23 来自 89d4afa3 manifest 的 fetch_time，是拉取脚本自报的时间（r2 L97：tushare_relay_pull.py 写出），不是独立证据；r3 自己也承认 10-10 当天的 sha 没有记录（L76）。可独立核对的只有 data_v2_bundle(.tar) 副本。但本次 ls 显示 output/data_v2_bundle.tar 的文件系统 mtime 是 2026-10-18 01:07:11 ET（恢复时重写），所以「14:42」也不能来自文件 mtime。
  - 裁定：known_at 取保守上界。r3.1 须写明 14:42 的出处（例如 tar 内成员头的 mtime，或 10-10 当天的日志 / 回执），并以它作为 PRIMARY_KNOWN_AT；10:01:23 只作 primary_known_at_fetch 记入 manifest。若 14:42 也找不到非恢复后的独立证据，就取能独立证明的最早时间，并在 manifest 写明。
  - 理由：已核对 2026-10-10 是周六，取 10:01 或 14:42，日频读者最早都从 10-12（周一）起可用，保守取值没有代价；而 known_at 是这张表 PIT 声明的根，应该取有证据的时间。
  - selftest 里的 PK 常量随之更新（L870、L900、L908）。

### P3
- **P3-1 v2.1 的 as_of 用 ET 日期**（L713 rep_done.strftime），而 in_date / out_date 是上海日历日。重拉若在 ET 12:00 之后完成，上海已是次日，check_dates（L326）可能把上海当天的 out_date 误拒；late_key_added / repull_new 的分界（L250）同理。方向是保守的（误拒，不前视），但须二选一写明：as_of 取 completed_et 换算成上海的日期，或保留 ET 并在 manifest 注明。
- **P3-2 validate_repull_dir 少两条显式检查**：pull .ok 的 signed_et ≤ completed_et、completed_et 不晚于运行时刻（不在未来）。现在只靠文件 mtime 间接保证（L432-437）；mtime 可被改，真正的证据链是 COMPLETE.json 的文件 sha + pull .ok sha + consumed 标记，manifest 里请按这个顺序表述。
- **P3-3 起草期间的越权读取（Data 自报，L1161）**：两次不带路径的 rg 递归扫描了 /workspace/QuantLab，可能读到 data/ 下文件开头。记 Data 的 P3。以后所有 rg 必须写明目录并加 -g "!data/**"，可能读 stdin 的命令不再接在管道后面。
- **P3-4 pub_backcast 的 v20 出表按 out_date 18:00 可知**（L478-479），依赖与 pub_available_at 相同的供应商历史假设。§8 的标注要求（L1135）已覆盖，回执里把 pub_backcast 的结果与 as_known 并列，不得单列。

## §10 开放问题答复
- **Q1 默认读法**：同意 pit_semantics=as_known 为默认；pub_backcast 只作研究口径，产物必须带「非知情时间 PIT，依赖供应商历史假设」标注；effective_dated 不得作默认，使用时必须标「回填行有前视」。
- **Q2 PRIMARY_KNOWN_AT**：见 P2-3，取有独立证据的保守上界。
- **Q3 helper 放哪里**：v2.0 / v2.1 阶段留在构建脚本里，只供 selftest 与 history_coverage 使用；消费方不得 import 构建脚本。移到共享模块属于 Strategy / Intel 的 code-change，单独提交、单独 .ok，届时 selftest 原样迁移。
- **Q4 out_date_filled_backdated**：同意「采纳并标注知情时间」。out_known_at = 重拉完成时间，as_known 读法不会前视；pub_backcast 对非 v20 出表也用 out_known_at（L479），同样不会前视。单列披露并计数进 acceptance。
- **Q5 COMPLETE.json 新字段**：要全文 diff，见 P2-1。

## 其余核对
- 拆出日历包（§1 L36-43）：SW 构建继续钉 fa4260b8；as_of 超出日历即拒绝（L729-730）；同意。
- P2-1 自然日推断（L267-272）、P2-2 as_of_join（L445-460）、P2-3 content_sha 三方比对 + 回读（L533-541、L749-758、L776）、P2-4 acceptance（L558-589）、P2-5 history_coverage（L598-612）、P2-6 check_dates（L321-332）：文本逻辑成立，selftest 用例（L895-1103）覆盖各项。
- as_known 口径下 2026-10-10 之前没有任何可用行（L1129、L1134），这是严格口径的应有结果；§8 已要求通知时写明后果。

## Data 下一步
1. 出 r3.1（增量）：P2-1 两份完整 diff；P2-2 归档路径与标记规则 + selftest；P2-3 PRIMARY_KNOWN_AT 改为有出处的上界；P3-1、P3-2 一并改。
2. 10-19 纸面跑完之后，按 §6 第 2 步申请只读探查 .ok（含 P2-1 备选计数、sets46 json、14:42 出处核对）。
3. r3.1 复核通过后再签 code-change .ok；所有真实数据运行各需 Arch .ok，一次一个，运行前与 Arch 对齐 94322 是否停到 T。
