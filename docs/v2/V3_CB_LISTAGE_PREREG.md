# V3_CB_LISTAGE_PREREG — 上市龄[1,3]年 × 低转股溢价（无 ytm 带）

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:32 ET，在任何运行之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ②；MP-FAR fail_explore 后立即开跑。

## 0. 差异
| 对照 | 本臂 |
|---|---|
| **MATPREM / MP-NEAR / MP-FAR** | **无 ytm 期限带**；过滤= **list_date 起算年龄 ∈[1,3]年** + 已进转股期 |
| CB-SIZEPREM | 无 remain_size 收缩秩和 |
| CB3-BALLAST | 无回售/强赎/下修**事件入场**；纯日历龄 |
| CB1-FLOOR / SHARE-AC / NAV-DISC / LIQ-TV / MIX-FROZEN | 非价地板、非 ETF 份额/折溢价/货币时变/冻结混配 |

独特来源：季化窗口（上市 1–3 年）低溢价错价。付钱方：过度追逐新券或抛弃「半新」券的对手。  
X1 预检日均≈3.4（非空）。

## 1. 规则（写死）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain≥1亿、强赎提示/实施剔除、排除 132/120。  
- 须 `conv_start ≤ T`（已进转股期；end 缺则用 maturity 上界，超 maturity 剔除）。  
- **年龄** `(T − list_date).days/365.25 ∈ [1.0, 3.0]`；**不要求** ytm 带。  
- 合格池最低溢价 **15**；等权；CB 袖 **50%** + 压舱 **50%**（511010/518880 60日逆波）。空池→100% 压舱。  
- `strategy_v1`；L=1；**无 IC**；AUM ∈ {600000, 1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 失效
闸门失败；与低溢价全池高相关无增量。

## 4. 结果（2026-10-12 01:33 ET；`output/v3/cb_listage/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | -0.7%/-8.1%/-0.10 | 11.8%/-10.1%/0.89 | 12.4%/-15.2%/1.19 | **不通过**（X1夏普；X2&lt;12%） |
| 100万 | -0.7%/-8.2%/-0.10 | 12.0%/-10.2%/0.89 | 12.5%/-15.6%/1.18 | **不通过**（X1夏普；X2&lt;12%） |

短报：`output/v3/cb_listage/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
