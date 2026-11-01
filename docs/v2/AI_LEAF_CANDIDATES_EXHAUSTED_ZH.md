# 叶候选已穷尽说明（2026-10-13 ~14:58 ET，研究级，live/promotion=false）
授权背景：Leo 12:51 ET「连续开新叶（残差来源，避开已灭十三包）」。本文按要求在无满窗 PIT 且正交的候选时停下，不硬凑。

## 已用/已灭机制（需正交的集合）
capacity_adv、margin_delta、northbound、OCF/indcap、accrual、moneyflow_resid、earnings_event、insider_increase、buyback_cancel、idx_rebal_flow/predict、equity_incentive、industry_etf_rotation、capacity_adv_negevent（解禁/减持/质押/预减/处罚）、etf_core、resid_etf、d1_val_resid、friction_cost、low_turnover、nontextbook；以及 V29 龙虎榜席位（含机构单腿 A4）reject、V30 解禁 share_type reject、V33 分红实施 reject、V34 披露提前 reject、LIMITUP-FADE-REV fail。

## 盘上剩余数据逐项判定
| 数据 | 判定 | 理由 |
|---|---|---|
| dragon_tiger top_inst/top_list | 不可 | 机构席位个股篮 V29 A4 已 reject，复做即同构已灭 |
| share_float | 不可 | V30 + negevent 已灭 |
| dividend / dividend_by_exdate | 不可 | V33 已 reject（事件窗无增量） |
| disclosure_date | 不可 | V34 已 reject |
| pledge_stat / stk_holdertrade | 不可 | negevent/insider 已覆盖 |
| hk_hold / hsgt_top10 / moneyflow_hsgt | 不可 | 北向族已灭；北向持股明细 2024-08 后停披露，非满窗 |
| margin / margin_detail | 不可 | 两融族已灭；融券/转融通余额 2023-10 后制度性收缩，信号失真 |
| moneyflow / cyq_perf / stk_limit / daily_basic | 不可 | 量价衍生同族，历史与主干超额相关≈0.95；与 low_turnover/friction_cost/capacity_adv 同源 |
| events: inquiry_letter/reply、penalty | 不可 | 负向事件，属 negevent 族；做多无明确对手方 |
| events: earnings_beat/miss、forecast、express | 不可 | earnings_event 已用 |
| rights_issue（配股） | 不可 | 稀释事件，做多无谁付钱逻辑；样本稀少（中大盘年均个位数） |
| fina_audit | 不可 | 非标意见集中于小盘/ST，中大盘几无事件 |
| futures / 期货贴水 | 不可 | 60万/100万 AUM 无法不加杠杆持 1 手 |
| index_weight（调样） | 不可 | idx_rebal* 已用 |

## 需补的数据（可解锁新正交叶）
1. **大宗交易**（tushare block_trade，2018→，含折溢价/买卖营业部）：折价成交后的供给消化 vs 机构溢价接盘。
2. **公募基金季报持仓**（fund_portfolio，含 ann_date PIT）：重仓拥挤/季末粉饰（网研 C10）、基金清盘或巨额赎回被动卖出。
3. **分析师一致预期/研报评级**（付费：Wind/朝阳永续，或东财研报 PIT 快照）：网研 C3 上调事件。
4. **股权激励/员工持股详细字段**（规模、考核门槛、授予价）：可做 equity_incentive 强度分层（属同叶加强，非新叶）。
5. **ETF 份额日序列**（fund_share）：被动申赎流对成分股的冲击（需与 idx_rebal 区隔）。

## 结论
本轮不开第 7 叶，停下。补齐上述 1 或 2 后可重开，流程照旧 who_pays→X2→Alpha ACCEPT→Eng Book-Smoke。
