# V3_CB_SIZEPREM_PREREG — 余额收缩流 × 低溢价交互（无 ytm 日历）

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:28 ET，在任何运行之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ②；MP-NEAR 已交接，本臂立即开跑。

## 0. 差异（相对 MATPREM / MP-NEAR / 已失败臂）
| 对照 | 本臂 |
|---|---|
| **CB-MATPREM / MP-NEAR** | **无**转股期∩ytm 日历带；信号= **remain_size 20日收缩率 × 低溢价秩和** |
| CB1-FLOOR | 无价[95,115]；非地板价 |
| SHARE-AC | 非 ETF 份额流；用转债余额 PIT |
| CB2-DYN / CIB2-NOIC | 非全池低溢价；须收缩流排名 |
| LIQ-TV / MIX-FROZEN / NAV-DISC | 非 ETF-only |

独特来源：余额被动收缩（转股/注销）窗口仍给低溢价的错价。付钱方：忽视余额流或被迫减持者。

## 1. 规则（写死，禁止网格）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain_size≥1亿、强赎提示/实施剔除、排除 132/120、非 placeholder。  
- **不要求** conv/ytm 日历。  
- 对每只合格券：PIT `remain_size` 取 T 与 T−20 交易日（按 publish_date≤T 最近值）；  
  `shrink = −(log remain_T − log remain_{T-20})`；缺值或 remain≤0 → 剔除。  
- 在合格池内：`rank_shrink`（高收缩好，升序秩）与 `rank_prem`（低溢价好，升序秩）等权相加，取 **秩和最优 15**；等权。  
- 组合：CB 袖 **50%** + 压舱 **50%**（511010/518880 60日逆波）。空池→100% 压舱。  
- `strategy_v1`；L=1；**无 IC**；AUM ∈ {600000, 1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 失效
收缩信号稀疏；与低溢价高相关无增量；闸门失败。

## 4. 结果（2026-10-12 01:29 ET；`output/v3/cb_sizeprem/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | −3.8%/−11.5%/−0.41 | 15.8%/−8.1%/1.27 | 11.1%/−15.7%/0.96 | **不通过**（X1夏普） |
| 100万 | −3.9%/−11.6%/−0.42 | 16.2%/−8.2%/1.28 | 11.1%/−15.9%/0.95 | **不通过**（X1夏普） |

短报：`output/v3/cb_sizeprem/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
