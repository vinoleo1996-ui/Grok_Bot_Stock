# V3_LPR_LEVEL_PREREG — LPR 1Y 绝对水平体制
研究级，promotion_approved=false。写于 2026-10-12 04:40 ET，运行前。

## 唯一收益来源（一句）
LPR 1Y 绝对水平相对自身扩展史的高低分档，调节 510300 权重（紧政策降仓、松政策加仓）。

## ≠ 禁族 / 近亲
- ≠ SHIBOR-dON（ΔON 差分）
- ≠ TERM-3M30 / TERM-3M（期限斜率）
- ≠ SHIBOR-ON / RATE-LEVEL（货币/短端水平；本臂为 **LPR 政策利率水平**）
- ≠ IND-RATE / heat 削仓

## 规则
LPR 1Y asof；扩展窗 z=(x-μ)/σ（min_periods=40）。
z>0.5→权益 25%；z<-0.5→权益 50%；否则 40%；余下 **518880**。
月度再平衡。主表仅 60万/100万。GOLD only。

## Strategy 对账附记（2026-10-12T04:44:55-04:00）
研究级复核：`output/strategy_recon/lpr_level/`；**pass_all=true**；**near_relative** vs IND-RATE-DIFF（日≈0.978）、GOLD-BETA（≈0.913）、CB-PARITY-BAND（≈0.898）→ **非独立 explore-pass** / research_observe。
主表 60/100万 X2≈18.11%/18.13%，MDD≈−19.0%；**X1 Sharpe≈0.08 / MDD≈−24.45%（近 Mandate 25%）**。
面板：`prepare_panels_for_execution(policy='full')`。GOLD only。**promotion_approved=false**。台账：`descriptive_LPR_LEVEL_near_relative_research_observe`。
