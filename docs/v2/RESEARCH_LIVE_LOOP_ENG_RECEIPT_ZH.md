# 研究/纸面级「实时循环」Eng 回执（2026-10-13 ET）

红线：live=false；不下单；无守护进程、无 uvicorn/8787、无 GP；单进程，RSS 实测 ≤0.3GB（B4 回填 0.9GB）；capacity_adv 纸面轨（代码、输出、STATUS）未改；cli.py 只新增子命令。

## 第一阶段：B4 换哈希闸门与分段
- `b4-paper --mode rehash --new-60w P --new-100w P [--dry-run]`：历史（≤2026-10-09）逐行一致 ≤1e-8；新增行单名 ≤6%、Σw=1、无负权。两项都过才更新 FROZEN_CONFIG.json 并写回执，否则 exit 1、配置不变。测试结果见 docs/v2/B4_PAPER_ENG_ZH.md 的「换哈希闸门」节。
- **正式换哈希已执行**：AI 的 B_B4_50_25_25_topN_{60w,100w}_20261009.parquet 通过（历史 11206/17556 行，最大差 0.0，无新增日）。sha256 由 79ae20e8…/fa310b92… 换为 f7bf65e8…/2b2b1e28…，回执 docs/v2/B4_PAPER_REHASH_20261013_225407_ZH.md，旧值记入 rehash_history。
- monitor.json 新增 segment_finding（前半段两档都跑输 C0/主干：60万 −3.65/−7.81pp，100万 −3.46/−4.56pp）和 paper_segments（回填 H1、回填 H2、前向自 2026-11-02 三段分列，不合并）。

## 第二阶段：命令
```
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli loop-sync                 # 只读叶状态索引
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily               # EOD：新鲜度→(AI extend)→rehash→纸面更新
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --no-extend   # 2026-10-13 起默认调用 AI 续出；此参数关闭（见 PAPER_BRIDGE_X2H_ENG_RECEIPT_ZH.md）
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --force       # 数据不新鲜也强制跑（仅调试）
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli alert-ingest <file>       # 预警入库
```
代码：quantlab/portfolio/research_loop.py；quantlab/portfolio/b4_paper.py。

## paper-daily 流程（EOD only）
1. 数据新鲜度：510300 面板、etf_daily_adj 510300、X2 asof_extend 样本取最新日中的最小值，与预期交易日比较（按工作日计算，**未建模节假日**）。不新鲜则写 SKIPPED_DATA_STALE 后干净退出（exit 0）。今天实测：预期 2026-10-13，510300 只到 2026-10-09 → 跳过（output/loop/paper_daily_20261013/paper_daily_recon.json）。
2. AI 续出（仅 --run-extend 时；本次未跑：无新数据，RSS/耗时未经测试）。
3. rehash 闸门：发现带日期后缀且与 FROZEN_CONFIG 不同的 B4 文件时自动执行；被拒则沿用旧冻结文件。
4. capacity-adv-paper：原代码路径，输出改写到 output/loop/paper_daily_<date>/capacity_adv_paper*，不覆盖既有文档。
5. b4-paper forward（权重未过 2026-11-02 前为 WAITING）与 monitor。
6. 合并对账 paper_daily_recon.json（两轨指标、B4 分段、风险标记计数、weights_modified=false），以及 risk_flags.parquet。
- --force 测试：三步 exit 0，RSS 0.22GB。

## 输出路径
- output/loop/leaf_status_index.{json,parquet}（21 叶，8 个组合）
- output/loop/paper_daily_<YYYYMMDD>/{paper_daily_recon.json, risk_flags.parquet, capacity_adv_paper/}
- data/v2/alerts/alerts_<YYYYMMDD>.parquet（目前为空）
- output/strategy_paper_b4/{FROZEN_CONFIG.json, monitor.json, STATUS.json}

## 缺口
1. **approve→evolve 回写停用**，待 Leo 解除 GP 禁令（docs/v2/LOOP_APPROVE_EVOLVE_CONTRACT_ZH.md）。loop-sync 目前只是只读索引；Alpha 标签为文档首段的尽力解析。
2. **日更数据由 QuantLab Data 负责**：510300 和 etf_daily_adj 停在 2026-10-09（10-12、10-13 缺），paper-daily 因此跳过。
3. **无盘中数据源**：data/v2 只有日线（bars/daily_ohlcv_raw_pit），因此只做 EOD，盘中为缺口。
4. AI 续出脚本（--run-legs）的 RSS/耗时未测，默认不跑。
5. AI intel 尚无预警产出；接口已就绪（docs/v2/ALERT_INTERFACE_CONTRACT_ZH.md）。
6. 交易日历未建模 A 股节假日，节假日会误判为数据不新鲜（只会导致跳过，不会误跑）。
7. 前向段的主干对比要等 capacity_adv 有前向 NAV 后才有数值。
8. 没有调度器：由外部定时例程调用以上 CLI（本侧不起守护进程）。
