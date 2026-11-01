# V3_IND_CREATE_HHI_PREREG — 行业 ETF 申购集中度（HHI）→ 削 510300
研究级，**promotion_approved=false**。写于 **2026-10-12 06:47 ET，运行前**。
批次：`ortho_evt_ind2`。压舱 **GOLD 518880 only**。引擎同 hub。

## 独特收益来源（谁付钱）— A 股机制
行业 ETF 一级市场**净申购（正 Δshare）**在少数主题上高度集中时，HHI 升高 = 主题 FOMO 申购蜂拥（渠道/AP 集中创设）。随后主题退潮与宽基风险偏好回落往往同向。本臂：正 Δshare 的 HHI 扩展 z 高 → **削 510300**，余 GOLD。付钱的是：集中主题申购的散户/渠道与为其创设流动性的 AP（FOMO creators）。

## ≠
| 臂 | 机制 |
|---|---|
| **IND-RATE-DIFF** | 跨行业份额变化率 **截面均值** → 削 510300（拥挤流入总量） |
| **IND-SHARE-REV** | 份额变化率截面 **反转多头** 行业 ETF 组合 |
| **本臂** | 仅正 Δ 上的 **HHI 集中度**（谁在被创设），非均值、非反转多头书 |

## 规则
- 池：`etf_basic.category==行业` ∩ `etf_share_flow_pit_all`（自 2014-01-02；X1 日均约 32 只）。
- PIT：`share_available_at`（可用日 = available_at 的日历日，保守不前移）。
- 每日：对 `d_share_wan>0` 的行业 ETF，\(w_i=\Delta_i/\sum\Delta_+\)，\(\mathrm{HHI}=\sum w_i^2\)；无正申购 → HHI=0。
- `z=expanding_z(HHI, min=40)`；`z>0` → `w_eq=0.25`；否则 `0.45`；余 **518880**。
- 月度调仓；AUM 60/100万；禁小盘/IC。

## 闸门
同 hub；报 vs IND-RATE-DIFF 日 \|ρ\|。
