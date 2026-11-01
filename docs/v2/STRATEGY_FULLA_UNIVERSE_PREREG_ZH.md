# 全 A 宇宙预注册 v1（FULLA_V1，Strategy）— FROZEN

- 冻结时间：2026-10-14 07:35 ET（在看到任何全 A 回测结果之前冻结）
- 依据：Leo 指令（经主 Agent）。07:24 ET Leo 取消小盘禁令：全 A 只剔除不可交易票，小盘贡献**仅披露**，不剔除，也不判违规。
- 冻结脚本：`research/strategy_fulla_universe_v1.py`，sha256 `4a606cdc8e6670b15ecaf1c05bdd46240150ebd038e8a61c8e40342a50ff02fe`。它基于 `research/all_a_universe_mask.py` 派生，只把 NAME_CAP 从 0.04 改为 0.06。
- 掩码：`output/strategy_fulla/universe_mask_fulla_v1.parquet`。列：date, instrument, in_universe 及剔除原因标志。覆盖 2023-09-01 至最新交易日。
- live=false；strategy_promotion=false。本宇宙**不改** FROZEN_CONFIG、capacity_adv 和 B4 纸面轨，也不碰密封窗口。全部为独立研究运行。

## 定义（PIT，对交易日 S，available_at = S 09:00 +08）
1. 基础池：沪深 A 股（不含北交所）。S 之前 20 个开市日内，tushare daily 至少有 1 根 K 线。
2. 剔除 ST/*ST：S 落在 namechange 派生的 ST 区间内（与 mid_large 同源）。
3. 剔除停牌：S 当日 suspend_d 中 suspend_type=S（盘前公告），或 S-1 无成交。
4. 剔除次新：list_date 到 S-1 不足 60 个开市日。
5. 剔除 ADV 不足：ADV20 取 S-20 到 S-1 的成交额均值，缺失或停牌按 0 计，单位为元。不可交易条件为 ADV20 < 6%×1,000,000 / 0.02 = **3,000,000 元**。其中 6% 是 100万档单票上限，0.02 是参与率上限，与 capacity_adv 的 ADV_PARTICIPATION_K 一致。
6. 不设市值下限，也不剔除小盘。
7. 只用 S 之前的数据；盘前停牌公告是唯一例外。

## 下游（冻结口径）
- 重生成：capacity_adv、earnings_event、insider_increase、equity_incentive（腿），以及叶11/叶14 等可交易的叶。由腿脚本的所有者（AI/Alpha）在本掩码上重生成；腿内逻辑不变，只替换候选池。
- B4 的合成方式不变：50/25/25，60万 N=6，100万 N=10，单票≤6%。
- 引擎：Eng book-smoke，strategy_v1 成本，按手取整，sleeves core=0/stock=1，244 日年化。
- 窗口：X2 2024-06-03 至 2026-10-09，**样本内**。
- 报告：60万/100万两档的 CAGR、MDD、Calmar、日胜率，并与 top300 版并列。
- 小盘归因（只披露）：按 PIT 总市值后 30% 计算收益贡献，同时给出申万一级行业分布。

## 试验计数
- 此前累计 29 组。本次是宇宙变更的预注册重跑：capacity_adv、B4，加上可交易的叶（叶11、叶14），每组两档。新增 4 组策略试验（capacity_adv、B4、叶11、叶14），累计 **33**。叶11/叶14 若不可重生成，就不计入。
- 宇宙参数只有这一组，不做网格。
- 掩码 sha256：`b5d9f1abd34bc550dd18a3eb2617a7d417cc60d29fbb02dceee02024e19fc7cd`。751 个交易日，每日在池数 4844–4997 只，均值 4952。


## ADV 裁决补记（2026-10-14 Strategy HI_LIQ v1.1）
- FULLA_V1 规范 ADV 底 = **300万**（6%×100万/2%）。
- `all_a_universe_mask.py` 的 200万变体 = **非规范/退役**；新研究腿以 FULLA_V1 掩码为准。
