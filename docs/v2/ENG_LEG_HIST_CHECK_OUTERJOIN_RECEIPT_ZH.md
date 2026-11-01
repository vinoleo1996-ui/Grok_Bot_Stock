# Eng 回执：leg_hist_check 外连接补 0 + 已记账日规则（2026-10-14 ~07:15 ET）
live=false；promotion_approved=false；仅研究/纸面。未动 output/strategy_paper_capacity_adv 和 capacity-adv-paper CLI；没有起 uvicorn，没有占用 8787；单进程，峰值 RSS 约 340MB。

## 1. 代码改动（research/b4_paper_extend.py，S6 共用）
- `leg_hist_check`：在 (session, instrument) 上做外连接，缺失补 0，再要求 |Δw|≤1e-8。规则是严格的：只在一侧出现的列，在比较区间（≤2026-10-09）内必须全为 0；否则判失败，`fail_reason` 写明列名。重复键或交易日集合不同也判失败。新增输出字段：compare、cols_only_in_new/frozen、zero_cols_added、rows_only_in_*。
- 验证：今日 earnings_event 腿（184648）结果为 ok，max_abs_diff=0，zero_cols_added=[600256.SH]。反例：把 600256.SH 历史改成 0.01 后判 FAIL，并写明列名。
- 新增 `splice_booked`/`booked_path`（主 Agent 07:03 ET 规则）：(10-09, 已记账末日] 区间沿用已记账的行，不改写；重算从下一交易日起生效。对应的节奏检查只额外允许“递延调仓日”（即已记账末日之后的第一个交易日），并在 check.json 的 booked_days 中记录。
- research/s6_paper_extend.py 调用上面同样的拼接逻辑。build/topN/cap 的排序代码没有改，平局顺序保持原样。

## 2. 新 sha（已写入 B4/S6 FROZEN_CONFIG 的 frozen_script_sha256，并追加 rehash_history）
- research/b4_paper_extend.py：2964996b… → d96630993883120b8e851d43b42bf4035595652b9171d2a5c4d953bf746ed76a
- research/s6_paper_extend.py：ba888465… → 3b258bbe9bd213fefc06f0dfa27d363fdb50e7672157831957d461f44eb92e7a

## 3. 已记账日
10-13 的 B4/S6 已记账权重没有改写：新文件 ≤10-13 的部分与已记账文件 DataFrame.equals=True；B4 60万差异 5 行，S6 60万差异 3 行，记在各自的 .check.json 的 booked_days 字段。10-13 腿级权重差异的审计记录由 AI 负责，见 docs/v2/AI_EARNINGS_EVENT_LEG_MISMATCH_DIAG_ZH.md。

## 4. 续算结果：仍为 PENDING（阻塞）
- 两条扩展都已写出：B4 `B_B4_50_25_25_topN_{60w,100w}_20261014_r2.parquet`，S6 `S6_cap50_ee25_eq25_topN_{60w,100w}_20261014.parquet`。自检全部通过（hist ≤1e-8，节奏 OK）。
- 但 rehash 内容门拒绝了。原因是腿 pin（≤10-13）的逐行比较不一致：
  - earnings_event：672 行不一致 = 668 行 600256.SH 全 0 历史 + 10-13 当日修订（510300 0.96→0.88，600176/600256 0→0.04）；
  - insider_increase（**新发现，AI 诊断中没有提到**）：10-13 有 4 行被修订（000338.SZ、600733.SH 0.04→0；600938.SH、601168.SH 0→0.04）。
- 按“其余检查保持不变”的要求，Eng **没有**放宽内容门。B4/S6 继续使用 10-13 的已门控权重，X2H 停在 10-13。
- 待决（主 Agent/Strategy 拍板）：内容门的腿 pin 检查是否也采用 (a) ≤10-09 外连接补 0，以及 (b) (10-09, pin] 区间允许晚到数据修订腿权重（前提是组合已记账行不变，且修订有审计记录）。拍板后改动很小，改完重跑即可通过。

## 5. 更新（07:12 ET）：内容门 (a)+(b) 已获主 Agent 批准并实施 → B4/S6 = OK
- 改动文件：quantlab/portfolio/b4_paper.py（这个文件此前没有登记 sha，新旧 sha 都已记入两条轨 rehash_history 的最新条目）。
  - `_hist_rows_equal`：先做外连接补 0。≤冻结末日（变量 FROZEN_END，即 X2 原始冻结末日，没有写死日期）的区间：|Δw|≤1e-8；只在一侧出现的列必须全为 0，否则判失败并写明列名。(冻结末日, 当前 pin] 区间允许腿权重修订，每一条都记为 (session, leg, instrument, old, new)。
  - `content_gate`：汇总得到 leg_revision_audit。rehash 通过后，审计列表写入 rehash_history 和新组合的 .check.json（字段 leg_revision_audit / leg_revision_window）。
  - 组合层：check_extension 对 ≤pin 区间的已记账组合行仍然逐行严格比较，任何改动都判失败。
  - `deferral_check`（门侧）以及 splice_booked 中的断言（扩展侧）：递延调仓日必须恰好是已记账末日之后的下一个 SSE 交易日，更晚一律拒绝。
- 新 sha：research/b4_paper_extend.py = 6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c（B4/S6 都已登记）；s6_paper_extend.py 未变（3b258bbe…）。
- 测试（scripts_eng/tests/test_content_gate_revisions.py，结果在 output/loop/content_gate_tests_20261014.json）全部符合预期：真实腿通过（3 条修订，600256 是全 0 列）；单侧非零列被拒（写明列名）；10-09 处的修订被拒；组合 10-13 改动 1e-6 被拒；递延 2 天被拒（门侧、扩展侧都拒）；递延 1 天通过。
- 用 /usr/bin/python3（pyarrow 26）重跑 paper-daily，exit 0，峰值 RSS 约 760MB。B4/S6 rehash 已应用（回执 B4_PAPER_REHASH_20261014_071137_ZH.md / S6_PAPER_REHASH_20261014_071143_ZH.md），paper_status 显示 b4=OK、s6=OK。审计条数：B4 7 条（earnings_event 3 条 + insider_increase 4 条），S6 3 条。
- 10-14 X2H NAV：capacity_adv 814,527 / 1,314,932；B4 829,068 / 1,353,464；S6 863,722 / 1,413,772（依次为 60万 / 100万）。
