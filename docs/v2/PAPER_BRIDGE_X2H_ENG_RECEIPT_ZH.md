# 纸面桥接段 X2H —— Eng 回执（2026-10-13 ~23:15 ET）

按 Strategy 裁定执行：只做纸面；live/promotion=false；无 uvicorn/GP；单进程。X2 研究窗冻结不动；X2H（2026-10-12→2026-11-01）是独立的桥接段；正式前向 FWD 从 2026-11-02 开始。三段分开展示，不合并。capacity_adv 原纸面 STATUS/输出未改（mtime 仍为 17:06）；B4 FROZEN_CONFIG 未改。

## 1. B4：AI 续出首次监督运行
- 运行前 ps：有 Data 采集链 queue_chain_20261014.py（RSS 1.1GB，CPU 0.8%，空闲为主）；可用内存 8.1GB。
- 命令 `python3 research/b4_paper_extend.py --run-legs`（/usr/bin/time -v）：**exit 0，墙钟 4.7s，峰值 RSS 363MB**。
- 结果：两档均为 **NOOP_EXISTS_IDENTICAL**（new_rows=0，hist_ok，max_diff 0.0），没有 10-12/10-13 新行，因此**未触发 rehash**。
- 原因：AI 的 research/g1g5_x2_panel_stitch.py 把 asof_extend 截在 X2_END=2026-10-09（`edf = edf[edf.index <= X2_END]`），所以脚本判断的 data_end=10-09。虽然 Data 已把面板补到 10-13，腿也不会续。**需要 AI 改它自己的取数终点**，Eng 不改 AI 代码。
- 判断干净（低 RSS、无副作用），paper-daily 默认开启续出步骤（关闭用 `--no-extend`）；执行时用 qlvenv python 调用 AI 脚本。

## 2. capacity_adv 桥接（hold_extend）与月末保护
- 权重：output/loop/paper_daily_<date>/bridge_X2H/capacity_adv_weights_X2H_hold_extend.parquet。原 X2 行标为 segment=X2_frozen，延续行标为 hold_extend。
- 调仓规律：权重变化日为 07-31、08-31、09-30（每月最后交易日；10-09 为数据截止日）。下一次计划调仓 = 当月最后一个工作日（A 股节假日未建模）→ 2026-10-30。
- 保护规则：只在“上次权重日 < 日期 < 下次计划调仓日”区间内持有。窗口内一旦到达计划调仓日，而 capacity_adv 没有更新的权重，该日起**不再持有旧权重**，轨道记为 **PENDING**，写入 recon 的 track_status 和 output/loop/paper_status.json，原因写明。模拟（日历到 11-01）：最后持有到 10-29，PENDING=True。当前（数据到 10-13）：OK_HOLD_EXTEND。
- 桥接 NAV 的跑法：以“X2 + 持有”连续回放，只截取 ≥10-12 的部分，锚定 10-09 收盘；X2 部分与冻结结果逐值一致，不另行报告。

| 档 | 10-09（锚） | 10-12 | 10-13 | 桥接段收益 | vs C0 | 段内 MDD |
|---|---|---|---|---|---|---|
| 60万 | 811,507 | 817,569 | 816,368 | +0.60% | +1.51pp | −0.15% |
| 100万 | 1,308,840 | 1,318,759 | 1,317,300 | +0.65% | +1.56pp | −0.11% |
（标签 hold_extend；只有两个交易日，仅作桥接记录。）

## 3. B4 桥接
不允许持有近似。正式桥接只用经 rehash 闸门、且超过 2026-10-09 的权重。当前无新行 → **B4 X2H = PENDING**。此前的持有近似数（835,205 / 1,363,378）仍只留在 output/loop/hold_extend_dryrun/，不进入正式 NAV。

## 4. 分段展示
- paper_daily_recon.json：segments = {X2（冻结说明）, X2H_bridge（capacity_adv 与 b4 分列）, FWD（自 2026-11-02）}，另有 track_status。
- output/strategy_paper_b4/monitor.json 的 paper_segments：X2_frozen_H1、X2_frozen_H2、X2H_bridge_2026-10-12_to_2026-11-01、forward_from_2026-11-02。

## 5. paper-daily 实测
`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --run-nav`：全部步骤 exit 0，墙钟 18.1s，峰值 RSS 0.93GB。

## 路径
- 桥接：output/loop/paper_daily_20261013/bridge_X2H/{capacity_adv_600000_X2H_nav.csv, capacity_adv_1000000_X2H_nav.csv, capacity_adv_weights_X2H_hold_extend.parquet, capacity_adv_aum_*/}
- 对账：output/loop/paper_daily_20261013/paper_daily_recon.json；循环状态：output/loop/paper_status.json
- B4：output/strategy_paper_b4/{monitor.json, FROZEN_CONFIG.json}

## 待办
1. AI 修改 g1g5_x2_panel_stitch 的 X2_END 截断（或给续出路径另设终点），B4 才能续出 10-12 以后的数据。
2. AI 编写 capacity_adv 续出脚本；否则 10-30 起 capacity_adv 进入 PENDING。
3. 交易日历补 A 股节假日（目前用工作日近似）。

## 追加（2026-10-13 23:4x ET）：Strategy 裁定——调仓节奏 + capacity_adv 条件

### 1. 调仓节奏 cadence 门（`scripts_eng/cadence_check.py`，`b4_paper.cadence_check`）
冻结 X2 文件（2024-06 ~ 2026-10-09）权重变化次数/月：

| 文件 | 月数 | 变化次数 | 月均 | 单月最多 | 有月内调仓的月数 |
|---|---|---|---|---|---|
| capacity_adv 腿 | 29 | 29 | 1.00 | 1 | 0（纯月末，+窗口末 10-09） |
| earnings_event 腿 | 25 | 116 | 4.64 | 12 | 21 |
| insider_increase 腿 | 28 | 168 | 6.00 | 11 | 27 |
| B4 60w 组合 | 29 | 227 | 7.83 | 17 | 28 |
| B4 100w 组合 | 29 | 242 | 8.34 | 17 | 28 |

扩展段（10-12/10-13）：各文件均无新的变化日（2 天太短，不能单独证明节奏）。
规则/代码审查：`research/b4_paper_extend.py run_legs()`——capacity_adv 腿用 `capacity_adv_paper_extend.py`（非调仓日沿用，月末调仓日单日冻结代码决策 = 冻结规则）；事件腿用冻结脚本 `g1g5_{earnings_event,insider_increase}_weights.run()`，只移动 WEIGHT_END，**事件腿可月内调仓，未被压到月末**。
门的自动化判据（rehash 时读取扩展文件旁的 `.check.json`）：两条事件腿必须是重新计算的新腿文件（不是冻结腿文件）、leg_end ≥ 新最后交易日、腿历史逐行一致；否则 FAIL 退回 AI。
结果：当前 `B_B4_50_25_25_topN_{60w,100w}_20261013` 重新过门 **PASS**（hist + 6%/和为1/非负 + cadence）；负例（把 earnings_event 换成冻结腿、leg_end=10-09）→ REHASH REFUSED，exit 1，配置不变（/tmp 已删）。

### 2. capacity_adv 条件
- (b) 已实现：`python -m quantlab.cli capacity-adv-pin [--repin]` → `output/loop/capacity_adv_FROZEN_CONFIG.json`，记录 D1 输入 sha256/行数/最大日期：
  `data/v2/valuation/daily_basic_full_tushare.parquet` sha 4820339fbed1…（max 2026-10-13），`data/v2/universe/mid_large_members_pit.parquet` sha b53f091c9b07…（max 2026-10-13）。
  paper-daily 每次校验；任一 sha 变化 → capacity_adv 回退冻结 X2 权重并标 PENDING（原因写入 recon/STATUS），复核后 `--repin`（记录新旧 hash）。
  注意：Data 每日追加 daily_basic 会改变 sha，因此按字面规则每次数据更新后都需要人工复核并 repin。
- (c) 钩子：`research_loop.recompute_hook`，对扩展权重中 >10-09 的每个新调仓日调用 AI 的 `capacity_adv_paper_extend.py --simulate-rebalance <日>`（只检查不写入），结果写 `output/loop/capacity_adv_monitor.json`。目前没有前向调仓日（下一个是 10-30）→ 为空。偏差字段暂为 null：AI 的 simulate 只输出 n_changed_vs_prev，需要 AI 输出重算权重后才能算偏差。
- (a) 未修复前的已知风险：**capacity_adv full window not reproducible**（选股器依赖 hash seed，历史行逐字复制）——已写入 FROZEN_CONFIG.known_risks、capacity_adv_monitor.json 和 paper-daily recon。

### 3. loop-sync 以 alpha_labels.json 为准
factory_feedback 现在优先用 `output/loop/alpha_labels.json`（带别名映射，例如 northbound_flow→northbound）；只在没有标签时回退到解析文档。变化：10 个叶子从 unlabeled/accept_smoke_fail 变为 watch_smoke_fail（优先级 30）；黑名单仍 12 个；回退解析 0 个。

## 追加（2026-10-13 23:5x ET）：前视检查 + 重算钩子接入 AI 产物

### 1. 前视（look-ahead）检查——结论：无前视
- 引擎：`ExecConfig.strategy_v1` 默认 `fill="next_open"`（quantlab/platform/execution.py:347）；Book-Smoke 用它（v2_multisleeve_book.py:478）。
- 时序（execution.py:628-631 文档；860-861 在 t 日开盘执行挂单；868-880 信号日 t 收盘按 NAV 锁定目标、生成挂单）：**T 日权重行 → T+1 开盘成交**。v2_multisleeve_book.py:501 只把信号日对齐到 ≥T 的交易日，不会往前移。
- 实证（capacity_adv X2 100万）：2025-06-30 新入选 sh.600309/601668：06-30 目标 5.21%、实际 0；07-01 实际 5.12%。2025-07-31 → 08-01 同样如此。
- capacity_adv D1：`available_at.normalize() <= session`（research/g1g5_capacity_adv_weights.py:178），即用 T 日 18:00 数据定 T 日权重，在 T+1 开盘成交前已经可得 → 合法。
- 事件腿：`searchsorted(公告日, side="right")`（g1g5_earnings_event_weights.py:114；insider 同样在 :115），入场日严格晚于公告日，再叠加引擎的 T+1 开盘成交 → 无前视（反而偏保守）。
- B4 与 paper-daily/b4_paper 的 NAV 都走同一个 book_smoke → 同样 T+1 开盘成交。无需做滞后一天的重跑。

### 2. 重算钩子 + FROZEN_CONFIG
- `recompute_hook` 现在读取 `output/ai_factory/paper_monitor/capacity_adv_rebal_check_<日>.json`（AI 的偏差）和 `capacity_adv_simulate_<日>.parquet`（Eng 用模拟权重对比实际使用的权重，独立计算偏差），写入 `output/loop/capacity_adv_monitor.json`；只有计划调仓日偏差 >1e-8 才标 DEVIATION。
- 10-13：AI max_abs_diff=0.0、ok；Eng 对比得 0.0346，原因是 10-13 不是调仓日，实际使用的是沿用的 10-09 权重。标为 INFO_nonrebalance_day（漂移指标，不算失败）。第一次真正的检验是 10-30。
- FROZEN_CONFIG 已 repin，现记录 mtime/size：daily_basic_full_tushare sha 4820339f…63dc 与 AI 一致，size 743884130，mtime 2026-10-13T06:13:56 ET。
- 已知风险更新为：seed 依赖已修复（4 个 seed 全窗口一致），但全窗口重算与冻结文件仍有 406 天不同，历史 ≤10-09 继续逐字复制。

## 追加（2026-10-14 02:2x ET）：按内容钉住腿/组合文件（Strategy 批准；适用于 S6、B4、capacity_adv 腿）
- 新的腿/组合文件通过需要同时满足：(1) 历史 ≤ 上次 pin 日期逐行一致（键集合相同，|Δw|≤1e-8；有 1 行不同即拒绝）；(2) 由冻结脚本重算，且有 .check.json（腿要有 `recomputed_with_frozen_script=true`）；(3) cadence_check 通过；(4) .check.json 的 `frozen_script_sha256` 等于 FROZEN_CONFIG 中记录的脚本 sha，脚本有改动即拒绝。通过后追加 rehash_history 并更新 leg_pins。路径名不再参与判断（取代 S6 按路径钉住 _135031 的做法；内容 sha 与 _135031 相同）。
- 代码：`b4_paper.content_gate / ensure_pins / _hist_rows_equal`（组合历史比对的截止日改为当前冻结文件的最后一天，即 10-13）；`research_loop.cap_content_gate`（capacity_adv 腿：通过后才进 weight-gate）。同分排序沿用原始顺序，未改。
- FROZEN_CONFIG 新增 `frozen_script_sha256` 与 `leg_pins`（权重 hash 不变）：B4 = b4_paper_extend e182f980、capacity_adv_paper_extend 2a8801d4、g1g5_capacity_adv_weights c7a05486、earnings_event 059ab23a、insider_increase 16d93948；S6 额外有 s6_paper_extend be216b8a、equity_incentive 2a396239；capacity_adv_FROZEN_CONFIG 记录前两项 + leg_pin（_r2，10-13）。
- 测试（S6，dry-run）：改名但内容相同的腿 → PASS；改动 1 行历史 → 拒绝（"equity_incentive: 1 history rows differ"）；伪造脚本 sha → 拒绝（"script changed: research/s6_paper_extend.py"）；每次 RSS 约 210MB；/tmp 已清理。
- NOOP：paper-daily --run-nav exit 0，57s，峰值 RSS 801MB；没有触发 rehash/gate（文件没变）；三条轨 OK，X2H 10-13 NAV 不变（capacity_adv 816,368/1,317,300；B4 835,205/1,363,378；S6 870,612/1,425,853）；B4/S6 权重 hash 不变。
- **AI 需要补的字段**：现有 .check.json 都没有脚本 sha，所以下一次真正的扩展会被拒绝。需要在每个组合与腿的 .check.json 中加 `frozen_script_sha256: {脚本路径: sha256}`（覆盖 FROZEN_CONFIG 中列出的脚本）；事件腿/capacity_adv 腿文件还要有自己的 `<腿文件>.parquet.check.json`（带 `recomputed_with_frozen_script`）。目前 earnings_event/insider_increase 只有 .meta.json；S6 组合 .check.json 现在引用的是 _135522，它没有 .check.json。

## 追加（2026-10-14 02:3x ET）：审查 AI 的 3 个扩展脚本改动并重钉脚本 sha
- 改动：s6_paper_extend be216b8a→ba888465；b4_paper_extend e182f980→2964996b；capacity_adv_paper_extend 2a8801d4→bfb05630。没有 git/备份，改为读代码，并对照之前回执里记录的代码片段：权重逻辑和同分排序的代码行没变（b4 build 中 `st.sort_values(ascending=False)`；s6 topn `kind="quicksort"`；capacity_adv `order = prev + new`；6% 封顶 / 溢出到 510300 / 归一化不变）。改动只涉及：写 `frozen_script_sha256` / `<腿>.parquet.check.json` 的函数，以及 newest_leg 优先选带 .check.json 的腿文件（腿选择）。
- 冻结腿脚本没变：g1g5_capacity_adv c7a05486、earnings_event 059ab23a、insider_increase 16d93948、equity_incentive 2a396239。
- 重跑证据：三个脚本输出重定向到临时目录重跑，用的解释器和 paper-daily 相同（python3，pyarrow 26），输出与钉住的 capacity_adv _r2、B4 60w/100w _r2、S6 60w/100w 20261013 **逐字节相同（cmp）**。注：用 venv（pyarrow 25）写出的 capacity_adv/B4 字节不同，但 DataFrame.equals=True，差异只来自 parquet 写入器版本。临时目录已删。重复的腿文件已被 AI 移到 output/ai_factory/_dup_archive/（未删除）。
- 已重钉：B4、S6、capacity_adv 三个 FROZEN_CONFIG 的 frozen_script_sha256 已更新，各自追加 rehash_history（原因 "AI metadata-only script change, Eng reviewed"，含新旧 sha 和上述证据），权重 hash 不变。
- 过程中发现：AI 当时提交的 .check.json 还写着**旧**脚本 sha，所以门第一次 dry-run 拒绝了三条轨（门按设计工作）。NOOP paper-daily 让脚本用当前 sha 重写了 .check.json 后，再跑 dry-run：B4 PASS，S6 PASS，capacity_adv content gate PASS。
- NOOP paper-daily --run-nav：exit 0，58s，峰值 RSS 797MB；三条轨 OK；X2H 10-13 NAV 不变（capacity_adv 816,368/1,317,300；B4 835,205/1,363,378；S6 870,612/1,425,853）。live=false。

## 2026-10-14 capacity_adv 10-30 月末再平衡覆盖检查
- 链路：paper-daily 默认 run_extend=True → research/capacity_adv_paper_extend.py。10-30 是 SSE 交易日，也是 trade_cal 的下一个月末，会触发单日冻结代码决策，并由 rebal_crosscheck 写 rebal_check_20261030.json → cap_content_gate（≤leg_pin 的历史逐行比对、.check.json、脚本 sha）→ weight-gate → 更新 leg_pin。D1 用历史切片 pin，日常追加能通过，改写历史则 PENDING。extend 在 D1、mid_large 未到 10-30 时 ABORT，当天 capacity_adv 记 PENDING（月末守卫不持有旧权重），等数据到位后下一次运行补上。
- 修复：recompute_hook 原先在真实再平衡日只认 simulate parquet，而 AI 在真实再平衡时只写 rebal_check，偏差会是空值。现改为回退读取 rebal_check 的 max_abs_diff（deviation_source=ai_rebal_check.max_abs_diff）；两者都缺时标 flag=UNCHECKED。已用合成的 10-30 再平衡在 output/loop/_review_tmp 中测试，两种情况都符合预期，测试后已清理。
