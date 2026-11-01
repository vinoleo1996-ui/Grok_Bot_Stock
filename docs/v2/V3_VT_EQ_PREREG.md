# V3_VT_EQ_PREREG — 波动目标权益敞口

研究级，**promotion_approved=false**。写于 2026-10-12 01:42 ET（正式双窗前）。  
X1 预检 Sharpe **0.37**（`output/v3/vt_eq/x1_sharpe_pretest.json`）→ 允许双窗。

## 规则
- 月末：σ=510300 过去 60 日收益标准差×√244；\(w_{eq}=\mathrm{clip}(0.10/\sigma, 0.20, 0.55)\)。  
- 其余权重：511010/518880 60 日逆波。无期货。L=1。AUM∈{60万,100万}。  
- 判定：两窗 MDD≤25%、夏普>0；X2 CAGR≥12%。

## 结果（2026-10-12 01:43 ET；`output/v3/vt_eq/results.json`）

| AUM | X1 | X2 | S | 判定 |
|---|---|---|---|---|
| 60万 | 2.9%/-14.2%/0.37 | 11.7%/-6.8%/1.16 | 2.1%/-21.9%/0.27 | **不通过**（X2 CAGR<12%） |
| 100万 | 2.9%/-14.2%/0.37 | 11.7%/-6.8%/1.16 | 2.1%/-21.9%/0.27 | **不通过**（X2 CAGR<12%） |

短报：`output/v3/vt_eq/SHORT_ZH.md`。**无 Strategy 交接。** promotion_approved=false。
