# Arch 审查：Data 申万一级 PIT v2 修复方案 r2（静态审）

- 审查对象：docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r2.md，sha256 482d8a2b06ef95348aa8935ce53261cde7d81053648acc0c2fd5fe53cf69b28b（93439 字节）。审的是 /tmp 下 cp -p 的副本，审前审后各核一次 sha，都一致。
- 版本说明：主 Agent 巡检把 2d9f5b8e 称作「r2」，但 2d9f5b8e 其实是 r1（docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH.md）。r1 已由 ARCH_DATA_SW_L1_PIT_V2_PLAN_REVIEW_ZH.md（f17f4771）审过。本文审的是对 f17f4771 作回应的 r2（482d8a2b）。
- 审查时间：2026-10-18T09:32:43-04:00（ET）
- 方式：只做静态审，没读任何 parquet 或真实数据，没 git apply，没 import 项目代码。
  - §6.4、§6.5 的代码抽到 /tmp，用 qlvenv 做了 py_compile，通过。
  - 在 /tmp 用合成数据单独测了几个函数，没调用 main、没读 repo 数据：parse_dates、merge_increment、increment_check、resolve、to_contract/validate_contract 回读，以及 merge_asof 的 us/ns 行为。测试时把 ok_runner_pin 的 import 换成了本地 stub。
  - 另外只读了以下源码文本：research_loop.py L670-690（纸面读 Data 日历的位置）、scripts/acquire/trade_cal_pit.py、data/v2/calendar/manifest.json。
- 行号 L 指被审文件的行号。live=false，promotion=false。

## 结论：有条件通过
- **方案层面通过。** f17f4771 的 3 个 P1、11 个 P2、10 个 P3，r2 都逐条回应了（§15）：
  - 两步设计合理：v2.0 是 as_of 10-10 的 89d4afa3 清洗版，v2.1 是实施日重拉的增量。
  - 不再用 FULL 全量文件。
  - 唯一规范化函数 norm_code。
  - 日期用显式格式解析，统一成 us 精度，并做空值与 NaT 数守恒检查。
  - 冲突处理不删键。
  - 有已审版本指针，并且只由 Arch 更新。
  - 写盘原子化、不覆盖。
  - 运行门禁改为复用 enforce。
  - 重拉目录做独立性校验。
- **代码文本：** 1 个 P1、7 个 P2，须在 r3 修正后才签 code-change .ok。r3 可以做增量修订，只改涉及的函数、契约和 selftest，不需要全文重审。
- **实施时间不变：** 在叶23 r2.11、叶24 和 10-19 17:40 纸面跑完之后进行，避开 10-19 16:40-18:40 ET。
- **前置条件（不归 Data）：** scripts_eng/ok_runner_pin.py（c7805d9a）目前仍不在 git 中，须由 Arch/Eng 先提交入库。

## 核对清单
| 项 | r2 | 结论 |
|---|---|---|
| 不覆盖 89d4afa3 / 0b1d3432 | PROTECT（sha）+ PROTECT_PATHS（路径）；只写 sw_l1_pit_v2.0/v2.1.parquet；_pre_write 在写之前检查；os.link 不覆盖 | 通过 |
| 不碰纸面在用的日历 | 本方案不写 data/v2/calendar；CAL 只读并钉 fa4260b8 | 通过；日历包另见 P2-7 |
| 46 只合并 | §3.2：46 只在 89d4afa3 里都有 open 行；§12.2：其中 33 只是 10-14 那次丢的，13 只更早丢失，丢失机制标为推测 | 通过；r2 沿用 r1 的只读结果，dry-run 时须用 v2.0 实测复核 |
| 95 只追溯 | §12：95 只都是「来源未知」，bak 被截断只作推测；§12.1：95 与 117 对账，补上了 300893.SZ | 通过 |
| 主来源与 62 个 raw、重拉交叉核验 | 89d4afa3 为主（accepted，94e91ffa）；62 个 raw 只作佐证，出全键 normdiff；实施日重拉只进 v2.1，差异分 5 类披露 | 通过；但「大面积不一致即回退」没有量化（P3-5） |
| 89d4afa3 来源 | manifest 记 7920 行 / 5914 代码；与 data_v2_bundle(.tar) 逐字节一致；10-10 的 sha 未记录，写进 primary.note | 通过 |
| out_date 口径 | in_date ≤ d ≤ out_date（含当天）；与 Intel 单测一致；须通知 cs_panel 和 Intel | 通过 |
| dtype 与精度 | 统一 datetime64[us]、无时区、零点；字符串列为 string；parquet 回读后 validate_contract 通过（合成数据实测） | 通过；merge_asof 见 P2-2 |
| 成功不只看退出码 | dry-run 先写报告，checks_ok 不通过即非零退出；summary.json 记各项计数 | 部分通过（P2-4） |
| 幂等 | v2.0 遇到已有指针或已有目标文件即拒绝；dry-run 证据目录必须新建 | 部分通过（P2-3） |

## 发现

### P1
- **P1-1 「PIT」缺知情时间，as-of 连接会有前视。**
  - 契约里 available_at = in_date 18:00（L797、L1236），也就是默认生效日当天收盘后就已知。下面三类行实际是事后才知道的：
    - (a) SW2021 体系 2021-07-30 才发布，但 89d4afa3 里很多行的 in_date 远早于这一天，例如 000537 801180 的 in_date 是 1993-12-10（L1341）。这些是回填历史，2021-07 之前并不存在。
    - (b) v2.1 merge_increment 采纳的 key_added 行（L637-639）中，in_date 早于 v2.0 as_of 的那些，是 10-10 之后才知道的。
    - (c) out_date_filled（L629-631）和 resolve 推断的 out_date（older_open_closed，L520）都是事后补的。
  - 消费方按 available_at 或 in_date 做 as-of 连接时，会在历史上用到当时还不知道的分类，这在严格意义上是前视。
  - 须改（r3）：
    - 契约增加 known_at 列，或 backcast 标记加 out_known_at 列：
      - (a) 类：known_at 取 max(in_date, 2021-07-30) 18:00；
      - (b)、(c) 类：known_at / out_known_at 取 as_of 或拉取日。
    - manifest 写明 pit_semantics：effective_dated（生效日口径）还是 as_known（知情口径）。
    - out_date 晚于 as_of 的行要拒绝或标记。
    - 消费方迁移说明（§13）写清两种读法。
    - selftest 增加 (a)、(b)、(c) 三类用例。
  - 若 Arch 决定保持「生效日口径」，也必须在 manifest 和 §13 里写明「不是知情时间 PIT，回填行有前视」，不能叫 PIT 而不加说明。

### P2
- **P2-1 日历起点 2005 会让 resolve 拒绝。** trading_days("19900101", ...)（L856）读的日历 fa4260b8 只覆盖 2005-01-01 到 2026-12-31（calendar manifest）。同一代码有两条 open、且新 open 的 in_date ≤ 2005-01-04 时，prev_td 为 None，fail（L517-519）。合成数据实测：000537 两条 open（1993、2004）时报「无法为较旧 open 找到合法 out_date」。会显式拒绝，不会静默出错，但会挡住 v2.0。须改：2005 之前的部分用自然日前一天，并标 out_date_inferred；或先用只读计数证明 89d4afa3 里没有这种情况。
- **P2-2 merge_asof 的 us/ns 精度冲突。** pandas 3.0.6 下，datetime64[ns] 与 datetime64[us] 做 merge_asof 会直接 MergeError（已实测）。消费方迁移到 v2 后，按 ns 构造的日期键会报错。会报错不会静默，但须改：§6.6 契约写明「连接前双方统一为 datetime64[us]」，最好提供一个 as_of_join helper，并在 selftest 里覆盖 ns 对 us 的情形。
- **P2-3 execute 和已审的 dry-run 之间没有绑定。** execute 会从头重算（L839-928），代码不检查结果是否与 Arch 审过的 dry-run 一致。须改：
  - dry-run 在 summary.json 里记录契约表的内容哈希，即按 to_contract 排序后、逐列规范化再算的 sha，不依赖 parquet 元数据；
  - execute .ok 用 dep_sha256_dryrun_content 钉住这个哈希；
  - execute 在 link 之前重算并比对，不一致就拒绝。
  - 这同时保证了幂等。
- **P2-4 通过判据只覆盖闸门。** checks_ok 只来自 hard_gate 和 increment_check（L871、L899）。daily_missing_after、source_gap、non_a_share_excluded、conflicts 各类计数、各 normdiff 计数都不参与判定。须改：
  - summary.json 增加 acceptance 段，事先写明期望值：daily_missing_after 全为 0，或差异逐只列进 source_gap；non_a 的集合是 {T00018}；normdiff_vs_raw0108 只允许 T00018；conflicts 按 reason 分类计数；
  - 不符合期望就把 checks_ok 置为 false；
  - 回执逐项报告。
- **P2-5 幸存者偏差检查只看现在的在市股票。** daily_missing 和 source_gap 只检查 2026-09-24..10-16 的在市股票（listed_on，L547-552）。X2 期间（2024-06 至今）后来退市的股票、历史上任一天的覆盖情况都没有检查。须改：dry-run 加一份历史覆盖报告，至少按月末取样 2018-01..2026-10，股票池为当日在市（含后来退市的），按月报缺成分名数，列为 acceptance 披露项。
- **P2-6 out_date 合法性。** parse_dates 之后没有检查 out_date ≥ in_date。merge_increment 采纳重拉的 out_date 时，不检查它是否 ≥ 原 in_date、是否 ≥ v2.0 as_of（与 P1-1 相关）。须改：显式拒绝 out_date < in_date；早于 as_of 的回补改记 out_date_conflict_ignored，或按 P1-1 标注知情时间。
- **P2-7 日历包没有可审的交付物。** 今天的 docs/、scripts/、data/v2/calendar、output/data 里都没找到日历 2027 延长包的方案、代码或数据。现有日历是 trade_cal_sse_pit.parquet（fa4260b8，2005-2026，manifest 7ccc911e）。发现的问题：
  - scripts/acquire/trade_cal_pit.py（90e3df43）L25 用 os.replace **原地覆盖固定路径**；
  - 纸面在用的 research_loop.py L677 读同一路径，用于 data_calendar_check（失败不致命，但会写进纸面产物）；
  - 本方案 INPUTS 钉的是 fa4260b8（L317-318）。
  - 要求：
    - 日历包须单独交方案并经 Arch 审；
    - 输出新版本文件，例如 trade_cal_sse_pit.v2027.parquet 加 manifest，不覆盖 fa4260b8；
    - 10-19 17:40 纸面跑完之前不写 data/v2/calendar；
    - 20130424 pretrade_date=20130423 的推导写进 manifest；
    - 写明和 SW v2 同批落地时 CAL pin 的先后顺序。SW 构建继续钉 fa4260b8，或者在同一 code-change .ok 里改钉新日历；
    - 纸面或 research_loop 改读新日历，属于冻结范围，须另行审批。

### P3
- **P3-1 解释器与版本。** r2 用 /usr/bin/python3（3.13.5、pandas 3.0.6、pyarrow 26.0.0），叶和纸面用 qlvenv（3.12.14、pandas 3.0.6、pyarrow 25.0.1）。manifest 要记录 python/pandas/pyarrow 版本，.ok 要钉解释器路径。
  - 另外，09:0x AI 在 CMC 回执里说「裸 python3 缺 pyarrow」，本次实测 /usr/bin/python3.13 有 pyarrow 26.0.0，两者不符，请 AI 复核。
- **P3-2 raw0108_sha256.txt 的格式。** verify_raw_list 按文件名比对（L475-479）。如果用带路径的 sha256sum 生成清单就会全部不符。须写明生成命令：cd 到目录内执行 sha256sum 801*.SI_[YN].parquet。
- **P3-3 quality_status 全是 ok。** 推断出的 out_date（older_open_closed）应标 out_date_inferred，不应和来源原样的行混为 ok。
- **P3-4 规范化前后的行数对账没有记录。** 89d4afa3 原始 7920 行，经 _std 去掉完全重复行和非 A 股行后，各少了多少，要写进 manifest。hard_gate 的基线是规范化后的 prim，看不到这一步。
- **P3-5 「大面积不一致即回退」没有量化（L82）。** 须给出阈值，例如 in_base_not_in_repull 或 out_date_conflict_ignored 超过 0.5% 的键就回退，并写进 acceptance。
- **P3-6 只有 v2.0 和 v2.1 两步。** --step 只能选这两个（L834），v2.2 及之后的刷新没有入口，要在 §14 写明以后另行修订。
- **P3-7 窗口和 as_of 不一致。** v2.0 的 as_of 是 10-10，WIN 却到 10-16。10-12..10-16 新上市的股票在 v2.0 里会显示为缺失，§8「修后 0」的预期要写成「0 或只差 10-10 之后新上市的股票」。
- **P3-8 name 列取当前名称。** 已披露，不是 PIT 名称，§13 要提醒消费方。

## Data 须修改（r3，增量提交）
1. P1-1：known_at / out_known_at（或 backcast 标记）、pit_semantics 写进 manifest、§13 写两种读法、selftest。
2. P2-1：2005 年以前的 out_date 推断（或只读计数证明不需要）。
3. P2-2：契约写明 us 精度要求；as_of_join helper 和 selftest。
4. P2-3：dry-run 内容哈希，由 execute .ok 钉住并在 execute 时比对。
5. P2-4：acceptance 段和期望值，不符合即 checks_ok=false。
6. P2-5：历史覆盖报告（含后来退市的股票）。
7. P2-6：out_date ≥ in_date 和 as_of 的检查。
8. P2-7：日历包单独交方案，版本化、不覆盖 fa4260b8，纸面跑完之前不写。
9. P3 一并修订，不单独阻塞。
- 不变：实施在 10-19 纸面跑完之后；89d4afa3、87d769aa、fa4260b8 在纸面跑完前一律不动；所有真实数据运行（只读探查、pull、dry-run、execute）各自需要 Arch .ok，且一次只跑一个。
