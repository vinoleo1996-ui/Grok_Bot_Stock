# S6 影子纸面线续出回执（2026-10-14 ET）
红线：只出纸面权重；live=false，promotion=false；未跑 Book-Smoke，未起 8787，未用 GP；没有覆盖任何冻结文件或已有文件。预注册 docs/v2/STRATEGY_S6_SHADOW_PREREG_ZH.md 的参数一项未改：50/25/25 配比；60万 N=6、100万 N=10；单名 ≤6%；余额进 510300。

## 历史对照基准
盘上没有单独冻结的 S6 文件。历史对照用的是 Strategy WF 的源权重：output/strategy_wf_combo/weights_S6_{60w,100w}.parquet，区间 2024-05-06→2026-10-09，生成脚本 output/strategy_wf_combo/wf_screen.py。
腿的对照基准沿用 wf_screen 的 P：
- capacity_adv：20261013_111219
- earnings_event：20261014_005430
- equity_incentive：20261014_023222

## 脚本
research/s6_paper_extend.py，沿用 b4_paper_extend 的模式。
- 参数 --run-legs：用冻结脚本续 equity_incentive 腿，代码不动，只设 WEIGHT_END。
- 参数 --legs-only-check：只做检查。
- 幂等：第二次运行结果为 NOOP_EXISTS_IDENTICAL。

## equity_incentive 腿续出
- 文件：output/ai_factory/g1g5_equity_incentive_daily_weights_20261014_135031.parquet
- sha256：58920f2068251b3bf5b9a2f9c2895793a83210bff182ac5be113120ef26c4a6a
- 2024-01-02→2026-10-13，57,620 行
- ≤10-09 的历史与冻结腿逐行一致，最大差 0.0
- 新增 10-12、10-13 共 172 行：每日权重和为 1，无负权
- peak RSS 约 1.12 GB
- Eng 要的 sidecar：同目录下 …_135031.parquet.check.json，写明冻结脚本重算、last_date、历史最大差、sha256

## S6 产出（output/strategy_paper_s6/）
| 文件 | 最后一天 | 历史行（与对照逐行） | 历史最大差 | 新增行 | sha256 |
|---|---|---|---|---|---|
| S6_cap50_ee25_eq25_topN_60w_20261013.parquet | 2026-10-13 | 9658=9658 | 1.1e-16 | 26 | 73c69684420a25c11adf09bbb21d0cc67e14e7eecf5ffd5c0a33e726673636dd |
| S6_cap50_ee25_eq25_topN_100w_20261013.parquet | 2026-10-13 | 15039=15039 | 0.0 | 40 | b626d6a68eb447975f05b90c4f7560b58e8772003bf36a835e9a7daeadbecd47 |

- 新增行：单名最大 6.00%，每日权重和为 1，无负权。
- 自检结果写在同名 .check.json 里。
- 用的腿：capacity_adv paper_20261013_r2、earnings_event 20261014_111825、equity_incentive 20261014_135031；三条腿 ≤10-09 的历史都与对照一致。
- S6 这一步 peak RSS 约 350 MB。

## 换仓节奏
- 历史变化日与对照文件完全一致：60万 224 天、100万 235 天，全部落在三条腿变化日的并集里。
- 续出段：腿在 10-13 有变化，但没有影响前 N 名或单名上限，所以 S6 在 10-12、10-13 沿用 10-09 的权重，没有新的变化日。
- 冻结窗口末日 10-09 在续出段不算换仓日。capacity_adv 下一次在月末 10-30 换仓。

## 哈希种子
- equity_incentive 腿在 PYTHONHASHSEED=0/1/42/12345 下各跑一次，四份输出 DataFrame.equals 全部为 True。
- 种子 1/42/12345 的三份文件只作核验用：…_135306、…_135414、…_135522，内容与 135031 相同。
- S6 叠加在四个种子下都重建了一次，60万和 100万两档的内容哈希都相同。

## 遗留问题
1. **并列名次的处理**：任务要求「按代码排序打破并列」，实测这样做会改掉 60万档的历史。
   - 原因：capacity_adv 在 2024-05-31 到 06-27 有 12 只股票同为 4%，从中取前 6 名时，选哪 6 只取决于排序方式。
   - 因此保留 Strategy 原来的排法：pandas 默认的 quicksort，作用在腿文件的行序上。这个结果是确定的，和哈希种子无关（四个种子已验证），但不是按代码打破并列。
   - 如果 Strategy 要改成按代码排序，需要另起预注册，历史也会跟着变。
2. **腿文件的选择**：newest_leg 按「结束日最新、同日取最新文件」挑腿文件。下次运行会挑到种子核验留下的 135522，内容与 135031 相同，重跑结果会是 NOOP。如果 Eng 要钉住 135031，可以把核验文件改名或移走。
3. **业绩参考**：X2 段属于样本内，S6 是事后挑出来的。前向自 2026-11-02 起算。

## 追加（2026-10-14 02:10 ET）：为 Eng 内容门补 check 字段
- 新增/更新 .check.json 并写入 frozen_script_sha256（取生成时的脚本 sha，与 FROZEN_CONFIG 一致）：
  - 组合：B4 60w/100w _20261013_r2.check.json；S6 60w/100w _20261013.check.json（腿已改指 equity_incentive _135031）。
  - 腿 <file>.parquet.check.json：earnings_event 111825、insider_increase 111825、equity_incentive 135031、capacity_adv paper_20261013_r2 与 paper_20261013（同内容，capacity_adv_FROZEN_CONFIG 指向后者）。均含 recomputed_with_frozen_script、basis_zh、last_date=2026-10-13、历史最大差 0.0、parquet sha256。
- 重复腿 _135306/_135414/_135522（含 meta/run_meta/ledger）已移入 output/ai_factory/_dup_archive/，未删除。
- 三个扩展脚本改为自动写这些字段；腿选择优先带 .check.json 的文件；同分排序保留 Strategy 原始顺序。脚本 sha 因此变化：s6_paper_extend be216b8a→ba888465，b4_paper_extend e182f980→2964996b，capacity_adv_paper_extend 2a8801d4→bfb05630。**Eng 需复核后更新 FROZEN_CONFIG，否则下次真实扩展会被门拒绝（"script changed"）。** check.json 中 scripts_on_disk_now_sha256 列出新值。
- 改后三脚本重跑均 NOOP_EXISTS_IDENTICAL；8 个权重文件 sha256 全部不变；peak RSS ≤544MB。
- 依据说明：earnings_event/insider_increase 的 recomputed=true 依据 2026-10-13 23:18 ET 冻结脚本重算记录 + 脚本 mtime 早于产出 + sha 与 FROZEN_CONFIG 一致，本次未再重跑。capacity_adv_paper_extend.py 的 mtime 比 r2 文件晚 30 秒，已用当前（改前）脚本重跑确认 NOOP 等价。
