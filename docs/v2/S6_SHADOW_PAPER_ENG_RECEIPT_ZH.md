# S6 影子纸面轨 Eng 回执（2026-10-14 ET）

状态 SHADOW_PAPER_CANDIDATE；live=false；promotion=false；不替换 B4；未改任何冻结文件。预注册：docs/v2/STRATEGY_S6_SHADOW_PREREG_ZH.md。

## 实现（通用化，没有复制粘贴）
- `quantlab/portfolio/b4_paper.py` 改为由 track spec 驱动（`SPEC` + `configure()`），默认 spec 与 B4 完全一致。验证：B4 FROZEN_CONFIG 字节不变；B4 monitor 重跑后只有 X2H 段因最新 paper_daily 更新而变化，其它全部一致；B4 rehash dry-run 仍 PASS。
- `quantlab/portfolio/paper_track.py`：S6 spec（权重、腿、事件腿 = earnings_event + equity_incentive、退役门）+ peers 对比。
- CLI：`python -m quantlab.cli paper-track --track s6 --mode {backfill|forward|monitor|all|rehash} [--new-60w P --new-100w P --dry-run]`
- 冻结：`output/strategy_paper_s6/FROZEN_CONFIG.json`（weights_S6_60w/100w 的 sha256，forward_start=2026-11-02，retire_gate）。
- paper-daily：自动跑 S6 forward（11-02 前为 WAITING）、X2H 桥接（没有 gated 扩展就 PENDING）、bridge 之后跑 monitor；recon.track_status 增加 s6。记分卡增加 S6 [SHADOW] 行。

## 回填（单进程，10.6s，峰值 RSS 822MB）
| AUM | CAGR | MDD | Sharpe | 成本/AUM | 年化单边换手 | 目标单名最大 | 实际单名最大 |
|---|---|---|---|---|---|---|---|
| 60万 | 17.15% | −11.95% | 1.03 | 2.48% | 6.45 | 6.00% | 6.57%（价格漂移） |
| 100万 | 16.37% | −12.66% | 1.00 | 2.23% | 5.84 | 6.00% | 6.00% |
与预注册数字一致。X2 为样本内（16 组事后挑选），只作参考。

同表对比（X2）：60万 S6 17.15/−11.95，B4 15.11/−13.85，capacity_adv 13.82/−10.07；100万 S6 16.37/−12.66，B4 14.24/−13.17，capacity_adv 12.23/−11.62（monitor.json `peers_X2`）。

## 换仓节奏（冻结 X2）
| 文件 | 月数 | 变化次数 | 月均 | 单月最多 | 有月内调仓的月数 |
|---|---|---|---|---|---|
| equity_incentive 腿（事件腿） | 29 | 128 | 4.41 | 9 | 26 |
| S6 60w | 29 | 217 | 7.48 | 15 | 28 |
| S6 100w | 29 | 228 | 7.86 | 15 | 28 |
cadence 门：S6 rehash 时要求扩展文件旁有 `.check.json`，earnings_event 与 equity_incentive 两条事件腿都必须由冻结脚本重算（不能沿用冻结腿文件，leg_end ≥ 新最后交易日，腿历史一致），否则 FAIL。自检 dry-run PASS（没有新行）。

## 段与退役门
- X2（冻结）/ X2H（桥接，当前 PENDING：等 AI 的 equity_incentive 续出脚本）/ FWD（2026-11-02 起），分开展示、不合并。
- 退役门（monitor.retire_gate）：任一档 FWD MDD < −15% → RETIRE，STATUS 改为 RETIRED_BY_PREREG_GATE。满 6 个月的对比规则写在规则里，届时人工判定。目前 NO_FWD_YET。

## 其它
- D1 重写：Data 确认 history_diff_rows=0；Strategy 接受顺序无关 hash → 标为已解决（见 LOOP_SCORECARD 回执）。
- 盘中数据计划已按 Data 的探测结果更新（docs/v2/INTRADAY_DATA_FEASIBILITY_ZH.md）。

## 路径
output/strategy_paper_s6/{FROZEN_CONFIG.json,monitor.json,STATUS.json,backfill_x2/}；output/loop/scorecard_latest.md

## 追加（2026-10-14 02:0x ET）：S6 扩展到 10-13 换哈希 + X2H 解除 PENDING
- 输入：AI 回执 docs/v2/AI_S6_PAPER_EXTEND_RECEIPT_ZH.md；S6_cap50_ee25_eq25_topN_60w_20261013（sha 73c69684…36dd）/ _100w_20261013（b626d6a6…cd47）。
- equity_incentive 腿**按路径 + sha 明确钉住**：`g1g5_equity_incentive_daily_weights_20261014_135031.parquet`，sha 58920f20…4a6a（spec `pinned_legs`；cadence_check 校验 .check.json 的腿路径等于钉住路径且 sha 一致）。AI 留下的重复文件 _135306/_135414/_135522（内容相同）**忽略，未删除**。
- dry-run：历史逐行一致（60w 9658 行，最大差 1.1e-16；100w 15039 行，0.0）；新行 10-12/10-13：单名最大 6.00%，和为 1，无负权；cadence PASS（earnings_event 与 equity_incentive 都是重算的新腿文件，leg_end=10-13，腿历史 ok，钉住腿匹配）→ 已正式换哈希，回执 docs/v2/S6_PAPER_REHASH_20261014_020102_ZH.md。
- 记录：为保住 60w 的历史，AI 沿用了 Strategy 原始的同分排序（tie order），没有改成按代码排序。这是有意为之，不算规则变更；以后重算若改成按代码排序，60w 历史行会不一致，过不了门。
- `paper-daily --run-nav`（没有其它大任务）：exit 0，55s，峰值 RSS 799MB。
  - S6 X2H OK：10-13 NAV 60万 870,612（+0.33%，超 C0 +1.24pp）；100万 1,425,853（+0.11%，超 C0 +1.03pp）。
  - B4 不受影响：FROZEN_CONFIG 字节不变，X2H 10-13 为 835,204 / 1,363,378（与上一次运行相同）。capacity_adv 不受影响：gate 记录不变，X2H 816,368 / 1,317,300（相同），OK_HOLD_EXTEND。
  - 三条轨：capacity_adv OK_HOLD_EXTEND，B4 OK，S6 OK（STATUS 为 SHADOW_PAPER_CANDIDATE_BACKFILL_READY_FORWARD_PENDING；退役门 NO_FWD_YET）。
- 注意：paper-daily 目前只对 B4 自动换哈希；S6 以后的扩展需要手动跑 `paper-track --track s6 --mode rehash`（或下次再把 S6 加进自动流程）。

- 追加（2026-10-14 02:1x ET）：S6 已接入 paper-daily 的自动 extend+rehash（与 B4 相同）：先跑 `research/s6_paper_extend.py --run-legs`，如果有新的、带 .check.json 的 S6 文件，就跑 `paper-track --track s6 --mode rehash`；扩展脚本非 0 退出或门拒绝 → S6 标 PENDING（原因写入 recon），继续用之前冻结的文件。NOOP 测试（当前文件）：exit 0，54s，峰值 RSS 802MB；B4/S6 FROZEN_CONFIG 与 capacity_adv gate 字节不变（capacity_adv_FROZEN_CONFIG 只更新 last_slice_check，切片 pin 不变）；X2H 10-13 三条轨的 NAV 与上一次相同；三条轨都 OK。注意：equity_incentive 腿钉住 _135031；以后数据日 AI 重算会生成新的腿文件名，钉住检查会让 S6 进入 PENDING，直到复核后更新 pin。

## 追加（2026-10-14 02:2x ET）：按内容钉住腿/组合文件（Strategy 批准；适用于 S6、B4、capacity_adv 腿）
- 新的腿/组合文件通过需要同时满足：(1) 历史 ≤ 上次 pin 日期逐行一致（键集合相同，|Δw|≤1e-8；有 1 行不同即拒绝）；(2) 由冻结脚本重算，且有 .check.json（腿要有 `recomputed_with_frozen_script=true`）；(3) cadence_check 通过；(4) .check.json 的 `frozen_script_sha256` 等于 FROZEN_CONFIG 中记录的脚本 sha，脚本有改动即拒绝。通过后追加 rehash_history 并更新 leg_pins。路径名不再参与判断（取代 S6 按路径钉住 _135031 的做法；内容 sha 与 _135031 相同）。
- 代码：`b4_paper.content_gate / ensure_pins / _hist_rows_equal`（组合历史比对的截止日改为当前冻结文件的最后一天，即 10-13）；`research_loop.cap_content_gate`（capacity_adv 腿：通过后才进 weight-gate）。同分排序沿用原始顺序，未改。
- FROZEN_CONFIG 新增 `frozen_script_sha256` 与 `leg_pins`（权重 hash 不变）：B4 = b4_paper_extend e182f980、capacity_adv_paper_extend 2a8801d4、g1g5_capacity_adv_weights c7a05486、earnings_event 059ab23a、insider_increase 16d93948；S6 额外有 s6_paper_extend be216b8a、equity_incentive 2a396239；capacity_adv_FROZEN_CONFIG 记录前两项 + leg_pin（_r2，10-13）。
- 测试（S6，dry-run）：改名但内容相同的腿 → PASS；改动 1 行历史 → 拒绝（"equity_incentive: 1 history rows differ"）；伪造脚本 sha → 拒绝（"script changed: research/s6_paper_extend.py"）；每次 RSS 约 210MB；/tmp 已清理。
- NOOP：paper-daily --run-nav exit 0，57s，峰值 RSS 801MB；没有触发 rehash/gate（文件没变）；三条轨 OK，X2H 10-13 NAV 不变（capacity_adv 816,368/1,317,300；B4 835,205/1,363,378；S6 870,612/1,425,853）；B4/S6 权重 hash 不变。
- **AI 需要补的字段**：现有 .check.json 都没有脚本 sha，所以下一次真正的扩展会被拒绝。需要在每个组合与腿的 .check.json 中加 `frozen_script_sha256: {脚本路径: sha256}`（覆盖 FROZEN_CONFIG 中列出的脚本）；事件腿/capacity_adv 腿文件还要有自己的 `<腿文件>.parquet.check.json`（带 `recomputed_with_frozen_script`）。目前 earnings_event/insider_increase 只有 .meta.json；S6 组合 .check.json 现在引用的是 _135522，它没有 .check.json。
