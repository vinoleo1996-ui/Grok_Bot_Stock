# V3_MP_NEAR_PREREG — MATPREM 变体：ytm[0.5,1.5] + 最低溢价10 + 单券帽8%

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:25 ET，在任何运行之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ①；MIX-FROZEN fail 后草稿池清空。

## 0. 相对母臂与已失败臂
| 对照 | 本臂 |
|---|---|
| **CB-MATPREM（母）** | ytm **[0.5,1.5]**（母[1,3]）；最低溢价 **10**（母20）；单券 **≤8%** 组合权重（母等权无帽） |
| CB1-FLOOR | 无价[95,115]；日历近端带 |
| CB2-DYN / CIB2-NOIC | 非全池低溢价；先日历过滤 |
| CB3-BALLAST / SHARE-AC / NAV-DISC / LIQ-TV / MIX-FROZEN | 无事件入场、无 ETF 份额/折溢价/货币时变/冻结混配 |

独特来源：近端转股期条款窗的低溢价错价。付钱方：不愿持近到期博弈的对手。

## 1. 规则（写死，禁止网格）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain≥1亿、强赎提示/实施剔除、排除 132/120。  
- `conv_start ≤ T ≤ conv_end`（end 缺→maturity）；**ytm∈[0.5, 1.5]**。  
- 合格池最低溢价 **10**；目标 CB 袖 50% 等权；若单券 >**8%** 组合权重则截断，**差额补入压舱**（不强制抬回 50%，使上限有约束力）。  
- 压舱 50%：511010/518880 60 日逆波（同母臂）。空池→100% 压舱。  
- `strategy_v1`；L=1；**无 IC**；AUM ∈ {600000,1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 失效
池过浅；闸门失败；相对母臂无研究增量。

## 4. 结果（2026-10-12 01:27 ET；`output/v3/mp_near/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | 2.7%/−5.0%/0.80 | **14.5%/−7.6%/1.27** | 3.5%/−12.4%/0.68 | **通过** |
| 100万 | 2.7%/−5.0%/0.80 | **14.8%/−7.6%/1.29** | 3.5%/−12.6%/0.67 | **通过** |

X1 近端日历池空（avg names=0）。短报：`output/v3/mp_near/SHORT_ZH.md`。  
**已交接** `output/v3/handoff_strategy/mp_near/`。promotion_approved=false。

## 5. Strategy 对账（2026-10-12T01:31:04-04:00；研究级）
- 路径：`output/strategy_recon/mp_near/`（Eng A `run_weight_schedule` + handsim B；与 Beta NAV 一致）。
- X1 近端日历池 **EMPTY**（空仓 100%，纯压舱）已在短报写明。
- `promotion_approved=false`；不作晋升证据。MATPREM 仍为 pass 候选。

