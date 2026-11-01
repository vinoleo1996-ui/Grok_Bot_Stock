# V3_IND_REL_MOM_RESID_PREREG — 行业 ETF 相对强度 × 510300 残差
研究级，**promotion_approved=false**。写于 **2026-10-12 19:53 ET，运行前**。
批次：`ortho_relmom_pxvol`。等 AI v22 PIT；**不用份额流同构**。残差 **510300**（非 GOLD）。引擎：`run_weight_schedule` + `ExecConfig.strategy_v1` + `derive_nonstock_limits=True`。

## 独特收益来源（谁付钱）— A 股机制（探索）
冻结规则：**20 日相对收益相对截面均值的偏离**，做多 **顶 tercile**（continuation）。
- 谁付钱：公募/保险行业配置按季考核、按月调仓，对已确认景气行业只能分步加仓；短期相对领先行业继续吸收配置盘。
- **≠ 教科书主线声明**：Leo 禁动量主线；本臂仅 exploration。20d（非整 120d）缩短惯性窗，偏近端资金追逐延续，**非**经典 6 个月行业动量主书。
- 若正式数字像纯教科书动量（高换手、风格切换月集中超额）→ 标 **research_observe**，不交 Strategy。

## ≠
| 臂 | 持仓 / 信号 |
|---|---|
| IND-RATE / CREATE-HHI / NAV-STRESS | 510300↔GOLD 削仓 + **份额流**扳机 |
| IND-CREATE-REV / NAV-CHEAP / SHARE-REV | 份额/折溢价；或 GOLD 残差 |
| E1 120d 行业动量 | 120d SW 指数动量；本臂=ETF 自身 20d RS + **510300 残差** |
| **本臂** | 流动行业 ETF **顶 tercile** 等权；不足权重 → **510300** |

## 规则（FREEZE，不搜索）
- 池：`etf_basic.category==行业` ∩ `etf_daily_adj`；`amt20≥1000`；上市≥60 交易日。
- 信号：后复权收盘 20 日收益 `r20`；相对强度 `rs = r20 − CS_mean(r20)`（当日合格池截面均值）。
- 每月末：`rs` 降序顶 tercile（`k=max(1,N//3)`）等权；篮总权重 `w_basket=min(1, 0.7)` 固定 **0.7**（余 0.3→510300）；无合格 → `{510300:1}`。
- **禁**：份额流/申购/NAV 溢价信号；小盘个股；CB/金/债主仓；GOLD 压舱。
- AUM 60/100万。

## 闸门
HARD：X1 Sharpe≤0 或 avg_names==0 → fail_precheck。正式：X1&X2 Sharpe>0、MDD>−25%、X2 CAGR≥12%。  
必报 vs IND-RATE-DIFF 日 ρ（|ρ|>0.85 → near_relative）。仅 pass_explore 且非 near_relative 交接。promotion_approved=false。
