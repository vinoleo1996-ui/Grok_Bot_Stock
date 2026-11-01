# V3_IND_FLOW_DIFFUSION_PREREG — 创设广度体制下份额滞后扩散书
研究级，**promotion_approved=false**。写于 **2026-10-12 06:51 ET，运行前**。
批次：`ortho_evt_ind3_book`（**替换** SW-DISP-TILT-BOOK：该臂 X1 Sharpe≤0 fail_precheck；且低波倾斜在薄池上易坍成行业 Beta）。
压舱 **GOLD 518880 only**（残差）。引擎同 hub。

## 独特收益来源（谁付钱）— A 股机制
多行业同时净创设（正 Δshare **广度**高）= 一级资金在产业主题间扩散；尚未被创设的**份额滞后行业**随后常承接渠道轮动（diffusion）。本臂：创设广度扩展 z 高 → 等权做多 **ΣΔshare 底半**（份额滞后）；广度不高 → 合格行业等权。付钱的是：只追正创设热点、忽视滞后行业补涨的渠道/散户。**非价格动量**（排序键是份额变化，非收益）。

## ≠
| 臂 | 区别 |
|---|---|
| **IND-CREATE-REV-BOOK** | 无条件底 tercile 创设反转 |
| **IND-SHARE-REV** | 份额 **pct** 底 3；已 fail |
| **SW-DISP-TILT** | 价格指数离散度 + 低波；本批已 fail_precheck |
| **本臂** | **创设广度体制** 门控 + 份额滞后半仓；持仓=行业篮 |

## 规则
- 池/PIT 同 CREATE-REV-BOOK（map-pit 每行业 1；amt20≥2000；上市≥60）。
- `breadth_t = mean_i(ΣΔshare_20,i > 0)`；`z=expanding_z(breadth, min=40)`。
- 月调仓：`z>0` → 等权 ΣΔ 底半（`max(1,N//2)`）；否则合格行业等权；无合格 → GOLD。
- **不持 510300**。AUM 60/100万；禁小盘/IC。

## 闸门
同 hub；必报 vs IND-RATE-DIFF 与 vs BH45/55。promotion_approved=false。
