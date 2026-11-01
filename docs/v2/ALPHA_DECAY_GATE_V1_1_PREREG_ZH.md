# 叶 α 衰减闸门 v1.1 预注册

状态：研究级；promotion_approved=false；live=false；不改任何纸面状态；不跑 GP。
前版：docs/v2/ALPHA_DECAY_GATE_PREREG_ZH.md（v1，sha eecc84ba…c13b），research/alpha_decay_gate.py 原样保留。

## 1. 缺陷（Arch 审计，经 QuantLab AI 转达）
v1 第 45 行：价格按持仓日重索引后 pct_change(fill_method=None)，再 fillna(0)。停牌期间价格为 NaN，复牌首日的前值也是 NaN，于是复牌日收益被置 0，停牌期间累积的涨跌整段丢失。

## 2. 唯一修正
- 先取复权收盘价（research/adj_price.py），去掉 NaN 后与持仓日并集重索引，向前填充（停牌期沿用最后成交价，收益为 0）；
- 再 pct_change(fill_method=None)，复牌日收益 = 复牌价 / 停牌前最后价 − 1，承载全部变动；
- 仅上市前/无数据的前导 NaN 记 0。
- 实现：research/alpha_decay_gate_v1_1.py（复用 v1 的 evaluate_returns，阈值、窗口 252、MINH 126、成本 17.5bp、规则 KEEP/DECAY_WATCH/DECAY_DOWNGRADE 全部不变）。

## 3. 重跑范围与规则
capacity_adv、earnings_event、insider_increase、equity_incentive、B4（50/25/25，60万/100万冻结权重）、叶11 report_rc_allup。权重文件沿用 v1 复判同一文件。
capacity_adv 与 B4 仍只能被标记（flag），不自动降级。标签变化逐条报告，由 Alpha 裁定；v1.1 冻结后不再按结果改规则。

## 4. 冻结
- 冻结时间：2026-10-14 06:23:56 ET（TZ=America/New_York date）
- sha256：对本文件全文求哈希（不含自身），记录于 output/alpha/ALPHA_DECAY_GATE_V1_1_RERUN_20261014.json 与 research/alpha_decay_gate_v1_1.py 运行输出
