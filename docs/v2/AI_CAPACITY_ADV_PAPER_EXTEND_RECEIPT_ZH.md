# capacity_adv 纸面轨续权重 回执（2026-10-13 ET）

红线：只做纸面，promotion=false，live=false；未跑 Book-Smoke；未起 8787；未联系任何人；没有建定时任务；信号代码和参数都没改（直接 import research/g1g5_capacity_adv_weights.py 的冻结函数）；冻结文件未动。

## 产出（已续到 2026-10-13）
| 文件 | 最后一天 | 行数 | sha256 |
|---|---|---|---|
| output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013.parquet（+ .check.json） | 2026-10-13 | 32830（历史 32732 + 新增 98） | c7561170761f728e26feb387851619b4f38b8993a06778121702e907014f1b3d |
| 冻结 g1g5_capacity_adv_daily_weights_20261013_111219.parquet（未动） | 2026-10-09 | 32732 | 4348877ef927c85197a0068c219ab5a5f5957c7d11451a3ca68b73fd985d5caf |

## 核对（自校验，任何一项不过就中止，不写文件）
- 历史行（≤2026-10-09）与冻结文件逐行一致：键、顺序、元数据完全相同，最大绝对差 0.0（容差 1e-8）。
- 新增 10-12、10-13 两天：单名最大 0.04，等于冻结上限 NAME_CAP 0.04；每日权重和为 1；无负权；600519/002371 未出现。
- 幂等：第二次运行结果是 NOOP_EXISTS_IDENTICAL。若同名文件内容不同，以退出码 3 中止。
- 资源：peak RSS 539 MB，耗时约 1 秒（这次没有触发调仓计算）。

## 调仓日历（冻结规则：月末 + 窗口首日 + 窗口末日）
- 冻结段共 35 个调仓日，最后几个是 …, 2026-07-31, 2026-08-31, 2026-09-30, **2026-10-09**。10-09 之所以是调仓日，只因为它是冻结窗口的末日；这一天作为历史保留。
- 续出段：每个自然月最后一个 SSE 开市日（来自 tushare trade_cal），依次是 **2026-10-30**、2026-11-30、2026-12-31……
- 续出段不再加「窗口末日」调仓。否则每天运行都会把前一天改写成调仓日，历史就不稳定了。这一点是我对冻结规则的解读，请 Alpha/Eng 确认。
- **10-12、10-13 按规则不是调仓日，沿用 10-09 那一期的权重**（新增行与 10-09 逐名相同）。
- 10-30 调仓时，只用冻结代码对当天单独算一次决策。

## 为什么历史部分直接复制冻结文件，而不是全窗口重算
我实测过全窗口重算，**无法复现冻结文件**：
- PYTHONHASHSEED=0 下有 404 天不一致，最大差 0.08；PYTHONHASHSEED=1 下有 471 天不一致，最大差 0.12。说明选股器的输出依赖哈希顺序（集合遍历或并列排序）。
- 另外，D1 daily_basic_full_tushare.parquet 在冻结之后被重写过（box 时间 10-13 18:13 CST）。

单日重算的结果：2026-09-30、2026-10-09 与冻结文件完全一致，种子 0 和种子 1 结果相同；2026-08-31 有 2 只票不同（002415/601766 对 002714/601899），原因待查。所以脚本固定 PYTHONHASHSEED=0，历史只复制、不重算。

## 10 月末换仓的就绪情况
- 调仓日历已确认 2026-10-30 会被识别为调仓日。
- **数据缺口**：data/v2/universe/mid_large_members_pit.parquet 只到 2026-10-09。冻结代码在没有成分覆盖的日子里会走 coverage_gap，变成 100% 510300。我用 `--simulate-rebalance 2026-10-13` 试跑，确实得到 100% 压舱。
- 脚本已加护栏，下面任一情况都会中止、不写文件：成分 PIT 没覆盖到调仓日；D1 没覆盖到调仓日的前一交易日（目前 D1 已到 10-13）；调仓结果是 100% 压舱。
- **10-30 之前需要 Data 把 mid_large_members_pit 续到 10-30**，否则 10-30 那次运行会中止。

## B4 能否复用本脚本
可以，而且已经接上了（B4 脚本只做了接线改动，没改 B4 规则）：
- B4 的 `--run-legs` 改为调用本脚本续 capacity_adv 腿。
- B4 的 `newest_leg` 会识别 `_paper_` 文件。
- 原来那种用冻结 capacity_adv 全脚本加 `--weight-end` 续腿的做法，会因为上面说的不可复现而导致历史不一致，不应再用。
- 注：原指令是「只报告，不改 B4」。之后 parent 的 steering 要求两个续出脚本都走同一条续出路径，所以改了接线。

## 运行
```
cd /workspace/QuantLab
python3 research/capacity_adv_paper_extend.py --calendar-only          # 看数据末日和调仓日历
python3 research/capacity_adv_paper_extend.py                          # 续到数据末日
python3 research/capacity_adv_paper_extend.py --simulate-rebalance D   # 试跑：强制 D 日调仓，只核对不写
```
- 脚本会自动设置 QL_X2_EXTEND_END（放开 X2 截断），并以 PYTHONHASHSEED=0 重新启动自身。
- 退出码：0 正常；2 自校验失败；3 同名文件内容不同；数据护栏触发时以 ABORT 文本退出。

## X2 截断
- research/g1g5_x2_panel_stitch.py 新增 X2_END_FROZEN="2026-10-09"。
- `X2_END = 环境变量 QL_X2_EXTEND_END 或 X2_END_FROZEN`：研究默认仍冻结在 10-09，只有两个续出脚本会设置这个环境变量。已验证：默认 10-09，设了环境变量后到 10-13。

## 更新 r2（2026-10-13 晚，ET；按 Strategy 裁定）
### 产出
- `output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013_r2.parquet`（+ .check.json），sha256 c7561170761f728e26feb387851619b4f38b8993a06778121702e907014f1b3d。内容与此前的 _20261013 文件一致（换仓节奏没变）。
- 历史 32732 行，最大差 0.0；新增 98 行，单名 ≤0.04，每日权重和为 1，无负权；第二次运行是 NOOP；peak RSS 519 MB。

### 换仓节奏（用冻结文件实测）
- capacity_adv 共 34 个变化日，全部是月末，外加 2026-10-09（冻结窗口末日）；没有非月末的变化。
- 续出段的预期换仓日是 10-30、11-30……；10-12、10-13 没有变化。
- 自校验新增 `rhythm_ok`：续出段的变化日必须是预期换仓日的子集。

### ① 修掉哈希种子依赖（research/g1g5_capacity_adv_weights.py，信号逻辑和参数不变，只改平局打破方式；原文件备份在 /tmp/capacity_adv_weights.pre_stable.bak）
1. `present` 原来是 set，改成按代码 `sorted`。它决定打分时的遍历顺序，也决定并列时的先后。
2. `ranked` 排序键从 `-score` 改成 `(-score, code)`，并列时按代码排。
3. `_d1_adv_snapshot` 里按 available_at 的排序改成稳定排序（mergesort）。
- 验证：全窗口重算用 PYTHONHASHSEED=0/1/42/12345 四个种子，结果哈希都是 7d65d020c4fe64e3，完全一致。修复后全窗口重算与单日重算一致。
- 修复后的重算与冻结文件仍有 406 天不一致，最大差 0.08。原因是冻结文件当初是在某个随机哈希顺序下生成的，所以历史继续直接复制冻结文件，不重算。
- 续出脚本里原来固定 PYTHONHASHSEED=0 的重启逻辑已经去掉，现在不需要了。

### 8-31 那 2 只票不一致的原因
- 2026-08-31 打分为正的只有 21 名，少于 25 名的目标，所以要从 0 分组里补名额。
- 有 8 只票所在的申万一级行业里只有它自己，行业去均值后残差恰好为 0，z 分都是 −0.0，完全并列：002415、002594、002714、600150、600309、601668、601766、601899。
- 冻结文件当时按 set 顺序选中了含 002714、601899 的那组；修复后按代码顺序选中了含 002415、601766 的那组。
- 结合 Data 的说明（D1 重写只有 ≤5e-6 的精度差），可以确定：**这不是精度差造成的。并列是结构性的：单成员行业的残差恒为 0，与 ADV 数值无关，完全由不稳定的平局打破决定。**精度差不足以改变非并列名的排序。
- 两次单日快照里，这 4 只票的 ADV 输入完全相同。

### ② D1 估值文件版本
- 路径：data/v2/valuation/daily_basic_full_tushare.parquet
- 修改时间：2026-10-13 06:13:56 ET（box 显示 18:13:56 +08:00）
- 大小：743,884,130 字节
- sha256：4820339fbed1ce21bf0aed0b56a10543b76659b330946de6e22334d76a4363dc
- trade_date 最大值：2026-10-13
- 每次运行都会把以上信息写进 .check.json 和换仓核对 json，sha 改为分块计算，避免占内存。
- 注：D1 的 available_at 是当日 18:00，快照按「available_at 归一到当日 ≤ 换仓日」取值，也就是换仓日用的是当日收盘后的数据。这是冻结代码原有的行为，没改，只记录。

### ③ 每次换仓做单日重算核对，输出 monitor json
- 每个续出换仓日都会用全窗口决策路径独立重算当天，与实际使用的单日决策比较。结果写到 `output/ai_factory/paper_monitor/capacity_adv_rebal_check_<YYYYMMDD>.json`，字段包括 max_abs_diff、ok、only_used、only_recompute、d1 版本，同时汇总进 .check.json。
- 用 10-13 试跑（模拟换仓）：max_abs_diff 0.0，ok。
- `--simulate-rebalance D` 现在会输出完整权重：`paper_monitor/capacity_adv_simulate_<D>.parquet` 和 `.json`，json 里含新权重、10-09 的上期权重、核对结果和 D1 版本；不写入纸面轨。
- 10-13 模拟结果：22 个持仓（压舱 0.20，单名最大 0.04），与 10-09 相比有 16 个名字权重变化。peak RSS 585 MB，耗时 18 秒。

### 数据新鲜度
- 换仓日必须同时满足以下条件，否则中止：
  - output/daily_update_status.json 里 `tables.mid_large_universe.last_date` ≥ 换仓日；
  - mid_large_members_pit.parquet 实际覆盖到换仓日；
  - D1 覆盖到换仓日的前一交易日；
  - 换仓结果不是 100% 压舱。
- 当前 mid_large_universe 已到 2026-10-13（Data 已补齐并加入日更），10-30 换仓的前提已经具备。
