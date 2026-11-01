# B4 纸面轨续出 回执（2026-10-13 ET）

红线：只做纸面，promotion=false，live=false；未跑 Book-Smoke；未起 8787/uvicorn；未联系任何人；冻结文件未覆盖；B4 参数未改；peak RSS 约 347 MB。

## 结论
**最新可用数据日是 2026-10-09**，与冻结文件的最后一天相同。510300（etf_daily_adj）和 X2 panels（asof_extend_tushare_202610）都只到 20261009，10-12、10-13 两个交易日还没落数据。所以这次续出**没有新行**：新文件内容等于历史部分，并通过了逐行核对。数据到位后，用下面的脚本续出。

| 文件 | 覆盖最后一天 | 行数 | sha256 |
|---|---|---|---|
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261009.parquet | 2026-10-09 | 11206 | f7bf65e80a7273d9e7e1890711f74d00f5a4ca46c8622d91d02c1daf51e1ca49 |
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261009.parquet | 2026-10-09 | 17556 | 2b2b1e2890e86a102d6e10e91d35cf45caf48bb8585db960f229a39b4ac72afe |
| 冻结 B_B4_50_25_25_topN_60w.parquet（未动） | 2026-10-09 | 11206 | 79ae20e84d36798ef77af21f647390b5bf4517d8fb5f96edbdb8e8d91b10b6d4 |
| 冻结 B_B4_50_25_25_topN_100w.parquet（未动） | 2026-10-09 | 17556 | fa310b9211c89068f21b4025050f1c118f4aa0944e1bd8cafeead8b051daa0c9 |

新文件与冻结文件的哈希不同，原因是 parquet 写出的元数据不同。**内容逐行一致**：(session, instrument) 的键和顺序一致；weight 和 target_weight 的最大绝对差为 0.0（容差 1e-8）；date、instrument_id、mechanism_tag、who_pays_zh、universe_id 全部一致。每个文件的自校验结果写在同名 `.check.json` 里。

## 参数（未改）
- 三腿权重：capacity_adv / earnings_event / insider_increase = 50/25/25。
- 每腿只取股票部分的前 N 名（60万 N=6，100万 N=10），在腿内按该腿股票预算重新归一。
- ETF 部分直接透传。
- 组合层合并后单名上限 6%，溢出部分进 510300.SH，最后整体归一。
- 腿文件：capacity_adv 20261013_111219，earnings_event 20261014_005430，insider_increase 20261014_011841。

## 三腿能否续到最新日
- 三条腿当前都到 2026-10-09，等于数据最新日，这次不需要重跑。
- 冻结脚本的终点是写死的：capacity_adv 用 `--weight-end`；earnings_event 和 insider_increase 用模块常量 `WEIGHT_END`（无 CLI）。`--run-legs` 只改终点，不改信号代码。
- 上次自检段改动不会影响权重输出：earnings_event 和 insider_increase 的权重在第 189/196 行落盘，改动全部在其后的 `def leaf_ret` 段（第 220/254 行起）；capacity_adv 没有改动。
- 注意：腿脚本是全窗口重算的。如果 PIT 事件数据回补导致历史变了，B4 的历史核对会失败，脚本会中止，不写文件。

## 自校验（写在脚本里，任何一项不过就中止）
- 历史行（session ≤ 2026-10-09）与冻结文件逐行一致，容差 ≤1e-8。
- 新增行：单名股票 ≤6%，每日权重和为 1（容差 1e-9），无负权。
- 不覆盖：目标文件已存在且内容相同时什么都不做（NOOP，幂等）；内容不同时中止（退出码 3）。

## 运行说明（research/b4_paper_extend.py）
没有建定时任务。建议每个交易日 ET 晚上、数据落地以后手动运行，或者由 Leo 自行配置定时：
```
cd /workspace/QuantLab
python3 research/b4_paper_extend.py --legs-only-check   # 查看数据最新日 / 各腿最新日
python3 research/b4_paper_extend.py --run-legs          # 腿落后于数据时，先用冻结脚本续腿，再续出 B4
python3 research/b4_paper_extend.py                     # 只用现有最新的腿文件续出
```
- 输出：`B_B4_50_25_25_topN_{60w,100w}_<最后一天YYYYMMDD>.parquet`，加上 `.check.json`（含状态、哈希、核对结果）。
- 退出码：0 正常（WRITTEN 或 NOOP）；2 自校验失败；3 同名文件内容不同。
- 已实测：第一次运行 WRITTEN，第二次运行 NOOP_EXISTS_IDENTICAL。
- 前向纸面从 **2026-11-02** 起算，脚本已就绪。
- `--run-legs` 本次没有实跑（因为没有新数据）。第一次真正续腿时，要看一眼它的 RSS 和耗时。capacity_adv 的脚本里有 debate ledger 步骤，没看到网络调用，但第一次运行时最好盯一下。

## 两处小修
- research/g1g5_block_trade_weights.py 的文件头已改成本叶的说明（机构专用买方、溢价 ≥−3%、成交额占比 ≥5%、剔除减持窗口、T2 入场、HOLD 默认 20），代码未改，py_compile 通过。
- 叶台账叶 9 那一行已补上：复权后毛 CAGR 12.91%/−14.94%，残差 α +1.60%。

## 更新（2026-10-13 晚，ET）：放开截断后实跑到 10-13
- 首次监督运行 NOOP 的原因：stitch 把 asof_extend 截在 X2_END=10-09。现在改为只在续出路径上放开：环境变量 QL_X2_EXTEND_END；研究默认仍是 10-09（详见 AI_CAPACITY_ADV_PAPER_EXTEND_RECEIPT_ZH.md）。
- 三条腿续到 10-13：
  - capacity_adv：`output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013.parquet`（由 capacity_adv_paper_extend.py 产出，历史直接复制冻结文件）。
  - earnings_event：`g1g5_earnings_event_daily_weights_20261014_111825.parquet`，sha256 665f5b4d…39aa。冻结脚本只改了 WEIGHT_END；peak RSS 1.08 GB，耗时 5 分 53 秒。
  - insider_increase：`g1g5_insider_increase_daily_weights_20261014_111825.parquet`，sha256 45a929ae…297b。peak RSS 1.16 GB，耗时 3 分 47 秒。
  - 三条腿 ≤10-09 的历史与各自冻结腿逐行一致（最大差 0.0）。B4 脚本新增了腿历史核对，不一致时以退出码 4 中止。
  - 两条事件腿在 10-12、10-13 没有新入场，与 10-09 相同。
  - 注意：这两条事件腿这次是并行跑的，合计约 2.3 GB；单个进程都没超过 1.5 GB。`--run-legs` 是顺序执行的。
- B4 产出：

| 文件 | 最后一天 | 历史行 | 新增行 | sha256 |
|---|---|---|---|---|
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013.parquet | 2026-10-13 | 11206，最大差 0.0 | 28 | ec5645ac8eb96c85560939644d48d45349fa8651123fd8ad21f9cac6a4777643 |
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013.parquet | 2026-10-13 | 17556，最大差 0.0 | 44 | 40c24cd937239672a7930ca8afeeee7b2ebc2e947c3f9b760beb7630bb3db2dd |

- 新增行：60w 单名最大 6.00%，100w 单名最大 4.00%；每日权重和为 1；无负权。**10-12、10-13 按冻结规则不换仓，沿用上期（10-09）权重，逐名相同。**
- B4 这一步 peak RSS 367 MB，耗时 5 秒；第二次运行是 NOOP。冻结文件哈希没变；之前写出的 _20261009 文件保留。
- 10-30 换仓的前提：mid_large_members_pit 要续到 10-30（见 capacity_adv 回执）。

## 更新 r2（2026-10-13 晚，ET；按 Strategy 裁定）
### 换仓节奏（用冻结文件实测）
- capacity_adv 腿：34 个变化日，全部是月末，外加冻结窗口末日 10-09。
- earnings_event 腿：143 个变化日；insider_increase 腿：211 个变化日。两条事件腿按事件变化（入场 T2，持有期满退出），例如 9-17、9-22、10-09；三腿变化日的并集共 325 天。
- ee 的 10-09 变化是事件造成的，不是窗口末日：把终点放到 10-13 重跑时这一天照样出现。
- B4 60w 有 275 个变化日，100w 有 293 个，**全部落在三腿变化日的并集里**。其余并集日子 B4 不变，是因为腿的变化没有影响到前 N 名或单名上限。
- 也就是说，冻结的 B4 等价于「每天用当天三条腿的权重重新叠加」，任一腿变化的日子都会重新叠加，不只在月末。续出脚本正是逐日从腿重建，所以自动复现这个节奏。
- 窗口末日在续出段不当换仓日：capacity_adv 只在 10-30 这类月末换；事件腿由冻结脚本按事件生成，与终点无关。

### 产出（r2，不覆盖已有文件）
| 文件 | 最后一天 | sha256 |
|---|---|---|
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013_r2.parquet | 2026-10-13 | ec5645ac8eb96c85560939644d48d45349fa8651123fd8ad21f9cac6a4777643 |
| output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013_r2.parquet | 2026-10-13 | 40c24cd937239672a7930ca8afeeee7b2ebc2e947c3f9b760beb7630bb3db2dd |

- 腿文件：capacity_adv 用 paper_20261013_r2；earnings_event 和 insider_increase 用 20261014_111825。三条腿 ≤10-09 的历史与冻结腿一致（最大差 0.0）。
- 自校验新增两项：`hist_change_days_identical`（重建结果的历史变化日与冻结 B4 相同）为 True；`rhythm_ok`（续出段变化日 ⊆ 腿变化日）为 True。
- 10-12、10-13 三条腿都没有变化，B4 也没有变化，沿用 10-09 的权重。
- 新增行：60w 单名最大 6.00%，100w 单名最大 4.00%；每日权重和为 1；无负权。
- peak RSS 364 MB，耗时 5 秒；第二次运行是 NOOP。
- 数据新鲜度：output/daily_update_status.json 的 target_trade_date、status 和 mid_large_universe 都写进 .check.json；当前 mid_large_universe 已到 2026-10-13。
- 事件腿只在 PYTHONHASHSEED=0 下验证过一次可复现（历史完全一致），没有做多种子验证。

## 追加（2026-10-14 02:10 ET）：为 Eng 内容门补 check 字段
- 新增/更新 .check.json 并写入 frozen_script_sha256（取生成时的脚本 sha，与 FROZEN_CONFIG 一致）：
  - 组合：B4 60w/100w _20261013_r2.check.json；S6 60w/100w _20261013.check.json（腿已改指 equity_incentive _135031）。
  - 腿 <file>.parquet.check.json：earnings_event 111825、insider_increase 111825、equity_incentive 135031、capacity_adv paper_20261013_r2 与 paper_20261013（同内容，capacity_adv_FROZEN_CONFIG 指向后者）。均含 recomputed_with_frozen_script、basis_zh、last_date=2026-10-13、历史最大差 0.0、parquet sha256。
- 重复腿 _135306/_135414/_135522（含 meta/run_meta/ledger）已移入 output/ai_factory/_dup_archive/，未删除。
- 三个扩展脚本改为自动写这些字段；腿选择优先带 .check.json 的文件；同分排序保留 Strategy 原始顺序。脚本 sha 因此变化：s6_paper_extend be216b8a→ba888465，b4_paper_extend e182f980→2964996b，capacity_adv_paper_extend 2a8801d4→bfb05630。**Eng 需复核后更新 FROZEN_CONFIG，否则下次真实扩展会被门拒绝（"script changed"）。** check.json 中 scripts_on_disk_now_sha256 列出新值。
- 改后三脚本重跑均 NOOP_EXISTS_IDENTICAL；8 个权重文件 sha256 全部不变；peak RSS ≤544MB。
- 依据说明：earnings_event/insider_increase 的 recomputed=true 依据 2026-10-13 23:18 ET 冻结脚本重算记录 + 脚本 mtime 早于产出 + sha 与 FROZEN_CONFIG 一致，本次未再重跑。capacity_adv_paper_extend.py 的 mtime 比 r2 文件晚 30 秒，已用当前（改前）脚本重跑确认 NOOP 等价。
