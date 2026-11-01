# Data 交易日历 2027 延长包方案（trade_cal 2027）——仅方案，待 Arch 审

- 作者：QuantLab Data；起草 2026-10-18 10:xx ET。新文件。
- 来由：Arch 静态审 docs/v2/ARCH_DATA_SW_L1_PIT_V2_R2_REVIEW_ZH.md（sha 661f7055a91cd2e46b40ddb938878322a6b467da1f289011b9b51f0f5e65384c）P2-7“日历包没有可审的交付物”，要求日历包单独交方案；Arch docs/v2/ARCH_STRATEGY_SW_PIT_FRESHNESS_R5_REVIEW_ZH.md P3-1（日历止于 20261231，美东 2026-12-31 11:00 起所有调用 sw_pit 自检的地方硬停，Data 须在 12 月中旬前延长到 2027）；Arch docs/v2/ARCH_STRATEGY_SW_PIT_ASOF_TRADEDAY_C_REVIEW_ZH.md P3-6（20130424 pretrade_date 空串）。本包原先挂在 SW L1 PIT v2 方案里，现按 Arch 要求拆出（见 docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3.md §1）。
- 与 Strategy 一起做：共享函数（Strategy 的交易日历读取函数与 sha 钉）归 Strategy，Data 负责数据文件、manifest 与写入脚本。
- 状态：**仅方案**。没有写任何代码或数据，没有运行任何脚本；**Arch 签 .ok 之前不跑任何代码**。本轮只用 rg、sha256sum、Read 读了源码、文档与 data/v2/calendar/manifest.json（文本），没有读 parquet。
- live=false，promotion_approved=false。

## 0. 硬约束
1. **10-19 17:40 ET 纸面跟踪跑完之前，不写 data/v2/calendar 下任何文件**；避开 10-19 16:40–18:40 ET。
2. **永不覆盖** 现行日历 data/v2/calendar/trade_cal_sse_pit.parquet（sha fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41）及其 manifest.json（sha 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4）。新日历写成**新的版本文件**；读者从旧文件切到新文件，只能通过 Arch 批准后的**指针 / pin 切换**完成。
3. 所有运行（只读探查、relay 拉取、dry-run、写入、selftest）各需 Arch .ok，一次只跑一个重任务；nice -n 10、PYTHONDONTWRITEBYTECODE=1；RSS ≤ 1.5GB，MemAvailable < 2GB 即暂停。
4. 纸面（quantlab/portfolio/research_loop.py）改读新日历属于冻结范围，须另行审批，不在本包内自动发生。

## 1. 现状（只读核对，2026-10-18 09:4x ET）
| 项 | 值 | 依据 |
|---|---|---|
| 现行文件 | data/v2/calendar/trade_cal_sse_pit.parquet，77822 字节，mtime 10-18 01:13 ET（工作区恢复重写） | ls、sha256sum |
| sha | fa4260b8…8a41（与 manifest 一致） | sha256sum、manifest.json |
| 覆盖 | 20050101–20261231，8035 个自然日，5343 个开市日 | manifest.json |
| 列 | cal_date（str YYYYMMDD）、is_open（int）、pretrade_date（str）、available_at（Asia/Shanghai 无时区） | trade_cal_pit.py 文档串；intel_common.py L175 注释 |
| available_at 规则 | (cal_year − 1)-12-31 09:00 Asia/Shanghai | manifest.json |
| 写入脚本 | scripts/acquire/trade_cal_pit.py（sha 90e3df43ca13e9df75e831ae702b5d4c137efa1168ec52133d1b37b841e72f54）：默认 end=20261231；L25 内容有变化时用 os.replace **原地覆盖固定路径**；L30 直接写 manifest.json（非原子） | Read |
| 日更调用 | scripts/nightly_update.py L27：trade_cal 是日更步骤之一（工作日 05:55 ET） | rg |
| 20130424 | is_open=1，pretrade_date 为空串；原始拉取 data/v2/tushare_raw/trade_cal.parquet 中该行是第 0 行、位于分页边界；trade_cal_pit.py 原样复制 pretrade_date，不推导。其余 5342 个开市日里 5341 个与“前一个开市日”一致，唯一不一致就是 20130424（Arch ASOF_C 审 L48） | docs/v2/audit/data_ro_audit_20261018/EVIDENCE_data_ro_audit_20261018.md L22；Arch ASOF_C 审 |

- **风险提示（请 Arch / 主 Agent 知悉，本方案不改任何东西）**：日更第一步会跑 trade_cal_pit.py。只要 relay 返回的 2005–2026 内容与现文件有任何不同（例如 relay 端补上了 20130424 的 pretrade_date），它就会原地重写 fa4260b8，所有 sha 钉随之失效（Arch ASOF_C 审 L188 已指出）。中转目前不通，10-19 05:55 ET 的这一步大概率直接失败、不写文件；但若中转在 10-19 纸面之前恢复，存在改写风险。是否在 10-19 跳过 trade_cal 步骤，请 Arch 与主 Agent 决定（§9 Q1）。

## 2. 读取方与钉住方清单（rg 结果，2026-10-18 09:4x ET）
### 2.1 按固定路径读日历的代码
| 文件 | 位置 | owner（按目录推断） | 说明 |
|---|---|---|---|
| research/sw_pit_freshness.py（5191997e） | L41、L52-55 | Strategy / Intel 共用 | sw_pit 自检；cal_end 之后硬停（r5 calendar guard） |
| research/intel/intel_common.py（25f23dff） | L175 TRADE_CAL 常量 | Intel | Intel 日常循环读日历 |
| quantlab/portfolio/research_loop.py（d3ded87e） | L675-687 data_calendar_check | Eng（纸面，冻结） | 失败不致命，但写进纸面产物 |
| research/optimizer_core_x2_run_v1_4.py | L97 DATA_INPUTS["calendar_sha256"]、L355 | Strategy | 运行 .ok 用 calendar_sha256=<全长 sha> 钉日历（见 docs/v2/STRATEGY_V1_4_RUNNER_CHANGES_ZH.md L211、L392：fa4260b8） |
| research/optimizer_lambda_calib_sealed.py | L45 CAL_PATH | Strategy | |
| research/strategy_hiliq_universe_v1.py、research/strategy_fulla_universe_v1.py、research/all_a_universe_mask.py | L40、L38、L38 | Strategy | |
| research/g1g5_overnight_idio_ivol_coverage.py、g1g5_major_contract_growth_events.py、g1g5_tech_qual_cert_events.py | L12、L17、L16 | 待确认（g1g5 研究线） | |
| scripts/acquire/data_freshness_status.py | L10 | Data | data_freshness 判定 |
| scripts/acquire/forecast_history_pull.py、relay_outage_backfill.py | L69、L31 | Data | |
| scripts/acquire/trade_cal_pit.py | L11 | Data | 写入方 |
| research/tests_sw_pit/test_sw_pit_freshness.py、research/intel/test_sw_freshness.py | 合成目录 | Strategy / Intel | 测试用 tmp 路径，不读真实文件 |

### 2.2 钉 fa4260b8 的地方
- **共享函数的钉**：Strategy 提案 docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3b.diff L165 `TRADE_CAL_SHA_PIN = "fa4260b8…8a41"`（Arch ASOF_C 审 L33 确认 load_trade_cal 校验此钉）。**rg 结果：截至本次核对，repo 里没有任何 .py 含 TRADE_CAL_SHA_PIN 或 fa4260b8**，即该钉尚未落入代码（只在提案 diff 中）。落地时间以 Strategy 为准；本包按“钉已落地”设计切换步骤。
- **.ok 文件**：data/ 以外共 46 个 .ok，rg 全长 sha 与前缀 fa4260b8 均 **0 命中**；提到 trade_cal / calendar 的只有 docs/v2/eng_sd1/ARCH_SD1_TEST.ok、output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok 以及两个 _superseded 的 SD1 .ok，指的都是 Eng 的 quantlab/portfolio/trade_calendar 模块，不是本文件。因此**当前没有活的 .ok 用 sha 钉住日历文件**。
- **文档 / 产物中记录 fa4260b8 的**（只是记录，不是校验）：r1 / r2 / r3 SW 方案（INPUTS["cal"]）、STRATEGY_V1_4_RUNNER_CHANGES_ZH.md、DATA_FRESHNESS_CALENDAR_RECEIPT_ZH.md、DATA_REBOOT_INVENTORY_20261018_ZH.md、多份 Arch 审查文档与 audit 文件、output/data_freshness_status.json（日更重算）、logs/nightly/2026101{4,5,6}_trade_cal.log。

### 2.3 切换时须重签 / 新签的 .ok（预计）
| .ok | 原因 | 签发人 |
|---|---|---|
| 日历包 code-change（新写入脚本、nightly_update.py 的 trade_cal 步骤、data_freshness_status.py 读指针） | 代码变更 | Arch |
| 日历包 pull / dry-run / write / selftest | 运行 | Arch |
| Strategy 共享函数改钉（TRADE_CAL_SHA_PIN → 新 sha，或改为读指针） | runner_sha256 随代码变 | Arch（Strategy 交） |
| sw_pit_freshness.py、intel_common.py 若改读新文件或指针 | runner_sha256 随代码变；Strategy R5、Intel R3 的 code-change / selftest .ok 都已消费，需新签 | Arch（Strategy / Intel 交） |
| optimizer_core_x2_run_v1_4 下一次运行 .ok | calendar_sha256 改填新 sha | Arch |
| SW L1 PIT v2 构建 | 继续钉 fa4260b8；只有 v2.1 拖到 2027 时才在同一 code-change .ok 改钉（见 SW r3 §1） | Arch |
| 叶23 / 叶24 / 纸面相关 .ok | 本包**不改**它们读的文件；不重签。纸面改读新日历须另行审批 | — |
- 实施前用同一组 rg 命令重新枚举（命令见 §8），以实施当天结果为准，结果附在回执里。

## 3. 交付物
| 文件 | 说明 |
|---|---|
| data/v2/calendar/trade_cal_sse_pit.v2027.parquet | 新版本文件，20050101–20271231；列与现行文件完全相同（cal_date、is_open、pretrade_date、available_at），读者代码不需要改列名 |
| data/v2/calendar/trade_cal_sse_pit.v2027.manifest.json | 新 manifest（见下）；现行 manifest.json 不动 |
| data/v2/calendar/trade_cal_APPROVED.json | 已审版本指针：version、path、sha256、manifest、manifest_sha256、built_et、approved_by、approved_et、review_doc（时间带时区）。**只由 Arch 在审完回执后创建 / 更新**；Data 代码只读 |
| scripts/acquire/trade_cal_pit_v2.py（新建） | 版本化写入脚本，替代 trade_cal_pit.py 的写盘部分 |
| scripts/nightly_update.py（修改） | trade_cal 步骤改为“只拉取比对、出差异报告”，不再写固定路径 |
| tests/test_trade_cal_pit_v2.py（新建） | selftest，只用合成数据 |

- manifest 字段：table、version=v2027、path、sha256、rows、start、end、open_days、available_at_rule、source（relay / 原始拉取文件 sha）、pulled_et（带时区）、base_version（fa4260b8 及其 manifest sha）、diff_vs_base（2005–2026 段的逐格差异，期望只有 20130424 一格）、patches、holiday_notice（2027 年休市安排的依据与发布时间）、runtime（解释器与版本）、promotion_approved=false。
- **20130424 修正**（源数据问题，本地推导）：pretrade_date = 本地按 is_open 推导的前一个开市日 = 20130423。写进 manifest.patches：`{"cal_date": "20130424", "field": "pretrade_date", "from": "", "to": "20130423", "basis": "derived from is_open; source row 0 at page boundary was empty", "source_sha": <原始拉取文件 sha>}`。若推导值不是 20130423，或 relay 新拉取已带非空值且与推导不一致，即拒绝并报 Arch。
- **2027 年数据的来源与可用时间**：2027 年休市安排以国务院办公厅放假通知与上交所休市安排公告为准（通常 11–12 月发布）。拉取必须在公告发布之后，manifest.holiday_notice 记公告名称、日期与核对方式；available_at 沿用 (cal_year − 1)-12-31 09:00 Asia/Shanghai，即 2027 年各行为 2026-12-31 09:00。若届时公告未发布，本包不写 2027 数据，报 Arch 与主 Agent 另议（§9 Q3）。
- 一致性要求：新文件 2005–2026 段与 fa4260b8 逐格相同，唯一允许的差异是 20130424 的 pretrade_date；否则拒绝写入。2027 段须连续无缺日；开市日的 pretrade_date 全部等于本地推导值。

## 4. 代码方案（文本，未落 repo、未运行）
- scripts/acquire/trade_cal_pit_v2.py 要点：
  1. 入口第一件事 `enforce(__file__, ok_paths, modes, deps)`（ok_runner_pin，真实签名）；modes：pull / dry_run / write；deps 钉 base 文件 fa4260b8、base manifest 7ccc911e、原始拉取目录的 COMPLETE.json；.ok 带 interpreter=/workspace/qlvenv/bin/python。
  2. pull 模式：经 relay 拉 trade_cal（SSE，20050101–20271231）到**新建目录** data/v2/tushare_raw/trade_cal_<YYYYMMDD_HHMMSS>/，写 COMPLETE.json（文件 sha、completed_et、pull_ok_sha256）；单次 .ok，用后写 consumed 标记。不碰 data/v2/calendar。
  3. dry_run 模式：读拉取目录与 fa4260b8（只读），规范化列与 dtype，推导 pretrade_date，比较 2005–2026 段，生成全部报告到 /tmp 新目录（exist_ok=False），summary.json 写 content_sha256 与 acceptance；不写 data/v2/calendar。
  4. write 模式：必须给 Arch 审过的 dry-run 目录，.ok 钉其 summary.json；重算内容哈希一致才写；目标路径 trade_cal_sse_pit.v2027.parquet 已存在即拒绝；写同目录 tmp → 回读校验行数与 sha → os.link 到目标（不覆盖）→ 删 tmp；manifest 同样原子写。**代码里不出现固定路径 trade_cal_sse_pit.parquet 的写操作**，selftest 断言这一点。
  5. 不写指针；指针只由 Arch 写。
- nightly_update.py：trade_cal 步骤改调 trade_cal_pit_v2.py 的“比对模式”（只拉取到新目录、与指针所指版本比对、写差异报告到 output/data/），不写 data/v2/calendar；比对发现差异时日更标 warn，由 Data 报 Arch。现有 trade_cal_pit.py 归档到 _recovery/data/ 后停用（不删除）。
- data_freshness_status.py：日历改为经指针读取；指针不存在时回退读 fa4260b8 并在状态里写 calendar_version。此改动影响 data_freshness，须避开 10-19 交付窗口，放在纸面之后与本包同批。
- 共享函数（Strategy）：TRADE_CAL_SHA_PIN 从 fa4260b8 改为新 sha，或改为“读指针并校验指针中的 sha”。具体做法由 Strategy 提交、Arch 审；Data 提供新文件、manifest 与指针格式。

## 5. 切换顺序（pin switch）
1. **10-19 纸面跑完之前**：什么都不写。只交本方案。
2. Arch 审方案 → 签 code-change .ok → 归档旧脚本 → 落代码 → selftest。
3. 2027 休市公告发布后：pull .ok → 拉取到新目录 → dry_run .ok → dry-run 报告交 Arch（diff_vs_base 期望只有 20130424 一格）。
4. write .ok → 写 trade_cal_sse_pit.v2027.parquet 与 manifest → 回执（sha、行数、开市日数、patches、diff_vs_base、命令、时间、峰值 RSS）。
5. Arch 审回执 → **Arch 创建指针 trade_cal_APPROVED.json 指向 v2027**。
6. 读者切换（各 owner 交、Arch 审，一处一签）：
   - 先：Strategy 共享函数改钉（TRADE_CAL_SHA_PIN → v2027 sha，或读指针）——**必须在 Intel 日常循环开始调用该共享函数之前落地**；若 Intel 已经在调用，则在一个日更间隙内与 Intel 同批切换。
   - 同批：sw_pit_freshness.py、intel_common.py 改读新文件或指针（否则 2026-12-31 11:00 ET 起硬停）。
   - 之后：其余读者（§2.1）按 owner 排期切换；optimizer v1_4 下一次运行 .ok 填新 calendar_sha256。
   - 纸面 research_loop.py：另行审批；不切换时它继续读 fa4260b8，2027 年起 data_calendar_check 会出现 only_eng 天数（不致命，但会写进纸面产物），须提前告知 Eng。
   - SW L1 PIT v2 构建：继续钉 fa4260b8，除非 v2.1 拖到 2027（见 SW r3 §1）。
7. fa4260b8 与原 manifest.json **原样保留**，不覆盖、不删除；回滚即把指针改回或删除指针（Arch 操作），读者按指针回到旧版本。

## 6. selftest 用例（只用合成数据，scope=selftest、allow_real_data=false、out_dir 在 /tmp）
1. 20130424 类：分页边界一行 pretrade_date 为空 → 推导为前一开市日，进 patches；推导与源非空值不一致 → 拒绝。
2. base 段一致性：2005–2026 段除允许的一格外有任何差异 → 拒绝。
3. 2027 段缺日、重复日、is_open 非 0/1 → 拒绝。
4. 原子写：目标已存在 → 拒绝；tmp 残留不留；写入路径不可能是固定路径 trade_cal_sse_pit.parquet（受保护路径集合）。
5. write 与 dry-run 绑定：内容哈希不一致 → 拒绝。
6. available_at：2027 行 = 2026-12-31 09:00；旧行不变。
7. 比对模式（nightly）：与指针版本有差异时只写报告、不写 data/v2/calendar。
8. enforce 在 import 被测模块之前；.ok 缺 interpreter 或不符 → 拒绝。

## 7. 排期
| 事项 | 时间 |
|---|---|
| 方案初稿（本文件） | 2026-10-18 交 Arch（不急，随 SW r3 一起） |
| 方案定稿交付 | **2026-11-30 前** |
| Arch 审完 | **2026-12-15 前** |
| 代码落地、拉取与写入 | 10-19 纸面之后；2027 休市公告发布之后；避开 10-19 16:40–18:40 ET；每次运行前通知主 Agent 与 Arch，并对齐 94322 是否停到 T |
| 共享函数改钉 | Intel 日常循环调用共享函数之前；最迟早于 2026-12-31 11:00 ET（上海 2027-01-01 00:00）硬停时点，建议留至少一周余量 |

## 8. 实施前重新枚举的命令（只读）
- `rg -l --no-messages fa4260b8 -g "*.ok" output docs scripts research`
- `rg -l --no-messages --max-filesize 2M -g "!data/**" -g "!*.parquet" fa4260b8 .`
- `rg -n --no-messages "trade_cal_sse_pit|data/v2/calendar|TRADE_CAL_SHA_PIN" -g "*.py" scripts scripts_eng research quantlab tests`
- 结果、命令时间与 sha 附在回执里。

## 9. 开放问题
1. **Q1 10-19 日更的 trade_cal 步骤**：中转若在纸面前恢复，trade_cal_pit.py 可能原地改写 fa4260b8。是否在 10-19 跳过该步骤，请 Arch 与主 Agent 决定；Data 不擅自改。
2. **Q2 共享函数的形态**：Strategy 改钉新 sha，还是改为读指针并校验指针中的 sha？后者以后换版本不必再改代码，但指针成为新的信任点。
3. **Q3 2027 休市公告未按时发布**：是否允许先写“2027 年按周一至周五开市”的临时版本？本方案默认**不允许**（会把节假日算成开市日）。
4. **Q4 Intel 日常循环何时开始调用共享函数**：需要 Intel / 主 Agent 给出日期，以确定改钉的最晚时间。
5. **Q5 g1g5 三个脚本的 owner**：rg 只能看到路径，owner 待主 Agent 确认。
6. **Q6 SW v2 与日历包是否同批**：Arch 要求写明顺序；本方案与 SW r3 都按“不同批、SW 继续钉 fa4260b8”写。若 Arch 要同批，在同一 code-change .ok 中改钉即可。

## 10. 回应对照
| 来源 | 要求 | 位置 |
|---|---|---|
| Arch 661f7055 P2-7 | 单独方案并经 Arch 审 | 本文件 |
| 同上 | 新版本文件（如 trade_cal_sse_pit.v2027.parquet）加 manifest，不覆盖 fa4260b8 | §0-2、§3 |
| 同上 | 10-19 17:40 纸面跑完之前不写 data/v2/calendar | §0-1、§5-1 |
| 同上 | 20130424 pretrade_date=20130423 的推导写进 manifest | §3 |
| 同上 | 写明与 SW v2 同批落地时 CAL pin 的先后 | §5-6、§9 Q6；SW r3 §1 |
| 同上 | 纸面或 research_loop 改读新日历另行审批 | §0-4、§5-6 |
| 同上 | trade_cal_pit.py L25 原地覆盖固定路径 | §1、§4（新脚本不写固定路径；nightly 改比对模式） |
| Arch R5 P3-1 | 12 月中旬前延长到 2027 | §7 |
| Arch ASOF_C P3-6 | 20130424 空串 | §3 |
| 主 Agent | 更新共享函数钉、列出须重签的 .ok、先于 Intel 日常循环、11-30 交 / 12-15 审、Arch .ok 前不跑代码 | §2.2、§2.3、§5、§7、§0-3 |
