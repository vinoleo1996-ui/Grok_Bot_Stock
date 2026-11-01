# 全 A 宇宙重判计划（2026-10-14，Alpha）

Leo 已把宇宙改为全 A：剔除 ST、停牌、上市不满 60 日，以及在 100万档按 ADV 不可交易的票。**精确定义由 Strategy 冻结，Alpha 不自定。**

## 工具
- `research/alpha_fullA_rejudge.py`：输入一个宇宙掩码文件（date, instrument, in_universe），按新口径（净、T+1、244 日）重算：
  - IC/ICIR 双读：全样本 ICIR + 滚动 252 日中位 ICIR，信号先对行业/市值/β 残差化
  - 残差相关（正交性）矩阵
  - CMC（叶验收 v2 §1，B0=B4）
  - 衰减门 v1.1
  - GATE_V3（规则不变）
- 对象：capacity_adv、earnings_event、insider_increase、equity_incentive、B4（60万/100万），以及叶11–15。
- 参数：`--weights` 传入全 A 新权重路径的 JSON；`--apply-mask` 只做诊断，把掩码外权重挪到 510300，不能代替重生成。
- 冒烟：用现行 top300 掩码复现已有数字，结果见 output/alpha/fullA/smoke_top300.json。

## 需要 Strategy
1. 冻结后的宇宙定义预注册，含 sha 和冻结时间（ET）。
2. 宇宙掩码文件：parquet，列 date, instrument, in_universe，覆盖 2023-09-01 至最新交易日，PIT（每日只用当日可得信息）。
3. 100万档 ADV 可交易阈值的口径：参与率、ADV 窗口。
4. 卖方/调研类叶的池子是否同步换成全 A，由 Strategy 定。

## 需要 Data
1. 全 A 日线：复权、开盘价、停牌、ST 标记、上市日期，PIT。
2. 全 A 的 float_mktcap 和申万一级行业历史，用于残差化。
3. 在全 A 上做加载和内存压测：现行 ctx 会逐票加载收盘价，约 5000 只票时需要确认耗时和峰值内存。

## 需要 AI 在全 A 上重新生成权重
- capacity_adv、earnings_event、insider_increase、equity_incentive（腿）
- 叶11 report_rc_allup、叶12 analyst_recoverage、叶13 stk_surv、叶14 insurer_surv、叶15 tp_rerate
- 新的 B4 60万/100万由 Strategy/Eng 用新腿合成

## 规则
- 门不改；叶11 的 Eng X2 FAIL 继续有效。全 A 上任何本地 PASS 都只是候选，仍以 Eng X2 为终判。
- 不跑 GP，不派烟；paper/promotion/live=false。

## 冒烟结果（top300 掩码，07:35 ET）
- 47 项比对通过 43 项：GATE_V3 的 CAGR/MDD/换手 与 2026-10-14 新口径重判逐位一致；衰减门 v1.1 结论全部一致；ΔIC 一致。
- CMC ΔCAGR 相对旧值约小 3%，是因为参照的 selfcheck_v2 仍是 252 日年化，现改为 244 日，属预期差异（叶12 绝对差 0.33pp，判定不变）。
- B4 的衰减 α 差 0.04–0.3pp，是因为 harness 用 20261013_r2 权重，旧重跑用的是未带后缀的旧权重。
- 掩码外权重 2–12%，主要因为掩码从 2024-06-03 起，比权重起点晚，不代表有宇宙违规。
