# Arch 审查：Data 交易日历 2027 延长包方案（静态审）

- 审查对象：docs/v2/plans/DATA_CALENDAR_2027_PACKAGE_PLAN_ZH.md，sha256 c472713b…（审前核对一致，147 行）。
- 审查人：QuantLab Arch；签署时间：2026-10-18T10:16:47-04:00（ET）。
- 方式：只做静态审。只用 Read / rg / sha256sum / ls 读文本与元数据；没读 parquet，没运行任何项目代码，没提交。
- 冻结提醒：paper_import_closure.json 所钉文件及 configs/data 89d4afa3 / 87d769aa 冻结到 10-19 纸面跑完；本包在此之前不写任何文件。
- live=false，promotion=false。

## 结论：PASS with conditions（有条件通过）
- 设计方向正确：新日历写成新版本文件 trade_cal_sse_pit.v2027.parquet + 独立 manifest，fa4260b8 与 manifest 7ccc911e 原样保留；读者切换只经 Arch 审过的 pin / 指针；10-19 纸面前什么都不写（§0 L9-13、§5 L88-100）。
- 现状核对属实：fa4260b8、7ccc911e、trade_cal_pit.py 90e3df43 的 sha 本次复核一致；trade_cal_pit.py L22-25 在内容变化时 os.replace 原地覆盖固定路径；research_loop.py L677 读该路径、L683 写 data_calendar_check；nightly_update.py L27 把 trade_cal 作为日更第一步。
- 须补 3 个 P2 后才签 code-change .ok。

## 关键声明复核
- **TRADE_CAL_SHA_PIN 不在任何 .py 中**：rg -n -g "*.py" "TRADE_CAL_SHA_PIN|fa4260b8" scripts scripts_eng research quantlab → 0 命中。该钉只在提案 docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3b.diff L165。**属实。**
- **fa4260b8 不在任何现行 .ok 中**：rg -l -g "*.ok" -g "!**/_consumed/**" fa4260b8 output docs → 0 命中（该范围内共 13 个 .ok）；连 _consumed 一起搜也是 0 命中。**属实。**

## 发现

### P1
- 无。

### P2
- **P2-1 trade_cal_pit.py 每次成功运行都会重写 manifest.json**。L30 无条件 M.write_text，且内容含 finished_at 与 rewritten，所以即使 parquet 没变，manifest 的 sha（7ccc911e）也会变，而且是非原子写。§1 L27 的风险提示只提到 parquet。要求：
  - §1 风险提示补上 manifest；
  - 10-19 05:55 日更（已由主 Agent 批准、Arch 同意以 --steps 跳过 trade_cal 与 sw）跑完后的 sha 核对必须同时包括 fa4260b8 与 7ccc911e；
  - 新脚本与 nightly 比对模式都不得写 data/v2/calendar/manifest.json，selftest 断言。
- **P2-2 2027 行的 available_at 可能早于 Data 实际得知时间**。§3 L74 规定 2027 行 available_at = 2026-12-31 09:00 上海；若拉取或写入晚于这个时点（公告晚发、实施拖延），就和 SW P1-1 是同一类前视。要求：available_at = max((cal_year-1)-12-31 09:00 上海, 休市公告发布时间, pulled_et 换算上海墙钟)，代码里强制，manifest 写明三者原值；不满足时拒绝写入并报 Arch。
- **P2-3 受保护路径集合要列全**。除 data/v2/calendar/trade_cal_sse_pit.parquet 与 manifest.json 外，还必须包括 data/v2/tushare_raw/trade_cal.parquet：它是纸面 Eng 日历来源（quantlab/portfolio/trade_calendar.py，在 closure L379；research_loop.py L651），capacity_adv_paper_extend.py L75 也读它。pull 模式只能写新目录 trade_cal_<YYYYMMDD_HHMMSS>/（§4 L80），selftest 断言不写上述三个路径。

### P3
- **P3-1 .ok 计数不一致**：§2.2 L47 写「data/ 以外共 46 个 .ok」，本次 output/ + docs/（不含 _consumed）为 13 个、全仓（-g "!data/**"）为 32 个。命中数都是 0，结论不变，但回执须写明计数命令与范围。
- **P3-2 nightly_update.py 两个包都要改**（本包 §3 L69 与 SW r3 §6 第 3 步）。须串行落地：每个 code-change .ok 钉 nightly_update.py 的基线 sha，后落的一方以前一方落地后的 sha 为基线。
- **P3-3 §8 枚举命令**：*.ok 搜索请分别报告「不含 _consumed」与「含 _consumed」两组结果；第二条命令加 -g "!**/_consumed/**" 的对照组。
- **P3-4 §2.1 行号**：research_loop.py L675-687 复核正确（L677 读、L683 判定、L687 异常）；data_freshness_status.py L10 CAL 常量正确；intel_common.py L175、sw_pit_freshness.py L41 / L55 正确。

## §9 开放问题答复
- **Q1 10-19 日更 trade_cal**：已定。主 Agent 批准 10-19 用 --steps 去掉 trade_cal 与 sw，Arch 同意并已给 Data 三个条件；按 P2-1 再加 manifest 7ccc911e 的前后 sha。
- **Q2 共享函数形态**：首次切换保留代码里的显式 sha 钉（TRADE_CAL_SHA_PIN 从 fa4260b8 改为 v2027 sha，走 code-change .ok）。指针 trade_cal_APPROVED.json 只作交叉核对，不作唯一信任点。理由：指针是代码审查之外的可写文件，钉在代码里能让 runner_sha256 绑定日历版本；以后若要改读指针，另行提案。
- **Q3 公告未按时发布**：同意不写「周一至周五」临时版本。若 12-15 前公告仍未发布，Data 报主 Agent 与 Arch，另议 sw_pit 自检在 2026-12-31 11:00 ET 硬停的处置，不得用推测数据。
- **Q4 / Q5**：归主 Agent 与 Intel 回答；本包排期以最早调用日期为准。
- **Q6 是否与 SW v2 同批**：同意不同批；SW 继续钉 fa4260b8，只有 v2.1 拖到 2027 才在同一 code-change .ok 改钉（SW r3 §1）。

## Data 下一步
1. 出 r2（增量即可）：P2-1、P2-2、P2-3 写进方案与 selftest 用例；P3 一并修订。
2. 10-19 05:55 日更后，回执附 fa4260b8 与 7ccc911e 的前后 sha。
3. 10-19 纸面跑完前不写任何代码或数据；方案定稿 11-30 前，Arch 12-15 前审完。
