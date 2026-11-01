# V3_CB_CONVACT_PREREG — 转股活跃（Δacc_convert_ratio>0）× 低溢价

研究级，**promotion_approved=false**。  
**写于 2026-10-12 01:34 ET，在任何运行之前。**  
依据：`docs/v2/BETA_NEXT_AUM_ARMS_ZH.md` ①；CB-LISTAGE fail 后草稿池清空。

## 0. 差异（非 ytm 近亲）
| 对照 | 本臂 |
|---|---|
| SIZEPREM | 信号= **acc_convert_ratio 20日增量>0**，非 remain_size 收缩 |
| MATPREM / MP-NEAR / MP-FAR / LISTAGE | **无** ytm/上市龄带 |
| CB1-FLOOR / CB2-DYN | 非双低、非价≤130 全池低溢价 |
| CB3 | 无公告事件入场 |

独特来源：转股已发生仍给低溢价的「确认错价」。付钱方：忽视转股进度的定价。

## 0b. X1 池深预检（写 prereg 前已跑）
avg_names≈3.62，frac_empty≈0.09，name-days≈246。X2 avg≈14.5。

## 1. 规则（写死）
- 选券日每 10 交易日；FULLCB：ADV≥1000万、remain≥1亿、强赎提示/实施剔除、排除 132/120。  
- PIT `acc_convert_ratio`：`Δ20 = acc_T − acc_{T−20交易日}`；仅保留 **Δ20>0**。  
- 在该子集取最低转股溢价 **15**；等权；CB 袖 **50%** + 压舱 **50%**（511010/518880 60日逆波）。空池→100% 压舱。  
- `strategy_v1`；L=1；**无 IC**；AUM ∈ {600000,1000000} only。

## 2. 判定
探索 X1+X2 一次；S 描述。通过 = 每 AUM：两窗 MDD≤25%、夏普>0，X2 CAGR≥12%。通过才交接。

## 3. 失效
转股增量稀疏；闸门失败。

## 4. 结果（2026-10-12 01:35 ET；`output/v3/cb_convact/results.json`）

| AUM | X1 | X2 | S（描述） | 判定 |
|---|---|---|---|---|
| 60万 | −4.2%/−12.2%/−0.45 | 15.3%/−8.6%/1.24 | 11.0%/−16.4%/0.99 | **不通过**（X1夏普） |
| 100万 | −4.3%/−12.4%/−0.45 | 15.8%/−8.7%/1.26 | 10.9%/−16.5%/0.97 | **不通过**（X1夏普） |

X1 池非空（avg≈3.7）但仍夏普为负。短报：`output/v3/cb_convact/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
