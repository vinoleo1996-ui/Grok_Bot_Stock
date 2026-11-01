# V3_CB_PREMRESID_PREREG — 溢价对平价残差 × 期限带（MATPREM 深化，非近亲切片）
研究级，**promotion_approved=false**。写于 **2026-10-12 02:40 ET，任何运行之前**。  
依据：`output/d1/EXTERNAL_AI_BETA_ALPHA_GAP_AUDIT_ZH.md` P0-3。

## 0. 与 MATPREM / NEAR / MERGE / RELAX 的差异（必须）
| | MATPREM 族 | **CB-PREMRESID** |
|---|---|---|
| 排序键 | 原始低 `cb_over_rate` | **溢价对平价残差** `prem − ĝ(parity)` |
| 机制 | 低溢价拥挤 | 同平价水平下期权错价（空间修正） |
| 扩族 | **禁止**再切期限近亲 | 单臂深化；非 NEAR/MERGE/RELAX |

## 1. 规则（写死）
- 日度截面：按 `cb_value`（平价）十分位，组内中位溢价 ĝ；`prem_resid = cb_over_rate − ĝ`。
- 候选：转股期 ∩ 剩余期限∈[1,3]年 ∩ ADV20≥1e7 ∩ remain_size≥1e8 ∩ 非已触发强赎。
- 分数：`score = −prem_resid`；取 top20 等权；CB 袖套 50% + **单压舱 511010 50%**（P0-4：不叠 GOLD）。
- `strategy_v1`；AUM∈{60万,100万}；无 IC/期货/小盘；L≤1。
- 闸门：X1 Sharpe>0 预检；正式双窗 MDD≤25%、Sharpe>0、X2 CAGR≥12%。
- 失败：与 MATPREM 日相关>0.85；或预检≤0。

## 2. 结果（2026-10-12 02:41 ET）
不通过。X1 Sharpe≈0.60（avg_names=0 空仓债底）；X2 CAGR≈10.5%<12%。见 `output/v3/cb_premresid/`。无交接。
