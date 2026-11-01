# V3_SHIBOR_DON_PREREG — ON 利率 20 日变化调节权益
研究级，promotion_approved=false。写于 2026-10-12 02:00 ET。X1 预检 Sharpe **0.16**。
## 差异
信号=Shibor ON 的 **20 日差分**（非水平 RATE-LEVEL/SHIBOR-ON，非斜率 TERM）。压舱纯 511010。≠ GOLD-BETA/DD-BALLAST。
## 规则
月末：Δ20(ON)>0.10 → w_eq=0.25；<−0.10 → 0.50；否则 0.40。其余 511010。无期货。AUM 60/100万。
闸门：X1夏普>0、两窗MDD≤25%、X2 CAGR≥12%。
## 结果
不通过。X1 Sharpe≈0.16；X2 CAGR≈6.8%<12%。见 `output/v3/shibor_don/`。
