# V3_EQBOND_CORR_PREREG — 股债滚动相关体制
研究级，promotion_approved=false。写于 2026-10-12 04:40 ET，运行前。

## 唯一收益来源（一句）
股债日收益滚动相关 ρ 升高→风险同向→削减 510300、抬高 518880；ρ 低→权益倾斜。

## ≠ 禁族
- ≠ IND-RATE / heat→削 510300（非行业流/拥挤广度）
- ≠ CORR-CUT（彼为股-金相关削金；本臂为股-债相关调权益，压舱仅 GOLD）
- ≠ MATPREM / PARITY / PREMRESID-COV

## 规则
信号腿：510300 与 511010 的 60 日滚动相关（511010 仅作信号，不持仓）。
ρ>0.30→权益 25%；ρ<0→权益 50%；否则 40%；余下 **518880**。
月度再平衡。主表 AUM 仅 60万/100万。HARD GATE：X1 Sharpe≤0→fail_precheck。

## Strategy 台账附记（2026-10-12T04:43:33-04:00）
X1 Sharpe 预检失败（Sharpe≈**−0.04**；avg_names=**1.00**）→ **fail_precheck**；未开正式双窗；无交接；ortho5。
源：`output/v3/eqbond_corr/`。台账：`descriptive_EQBOND_CORR_fail_precheck`。**promotion_approved=false**；GOLD only。
