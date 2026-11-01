# AI STOCK-DISC-EARLY — Beta 完整 X1 冒烟复核（reject｜兼自拒）

更新：2026-10-12 09:46 ET（America/New_York）  
提案：`docs/v2/AI_STOCK_ARM_PROPOSAL_V34_DISC_EARLY_ZH.md`  
AI 接线：`research/ai_factor_disc_early_panels.py`；包 `output/ai_factor/stock_disc_early_v34/`；接线回执 `docs/v2/AI_DISC_EARLY_WIRING_RECEIPT_ZH.md`  
冒烟 runner：`output/v3/run_stock_disc_early_smoke.py`  
结果根：`output/v3/stock_disc_early/`（E1–E3 子目录 + `diagnostics.json`）  
pretest：`output/v3/pretest_batch_20261012_stock_disc_early.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。**不开 X2**。  
**≠ STOCK-DIV-IMP / STOCK-INDEX-REBAL / STOCK-UNLOCK-SHARETYPE / STOCK-SEAT-SPLIT / ETF-DT-SEAT / 价叶·份额流 / ocf 教材；本臂是定期报告早于同伴披露的入日短窗个股篮。V31 未触碰、未晋级。**

---

## 0. 一句话裁决

**reject（完整 X1；兼 `self_reject=true`）。**  
E1–E3 @60万∧100万 **全 `fail_precheck`**（Sharpe 全 ≤0；`any_x1_pass=false`）。  
去「早于中位」对照 **E2 Sharpe60≈−0.230 ≥ E1≈−0.470** → **无早披露维增量** → **`self_reject=true`**（持仓 Jaccard(E1,E2)≈0.313，非完全同构，但是**增量失败**）。  
晚披露 E3≈−0.345 亦 ≥ E1 → 早晚旗无方向优势（第二自拒支撑）。  
`promotion_approved=false`；**handoff: NO**；**不交 Strategy**；**不开 X2**。  
回执路径本文件。

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `stock_event_disc_early` / **STOCK-DISC-EARLY** |
| 机制 | 定期报告 **同 `end_date` 下首次 `available_at` 早于中大盘同伴中位** 的入日短窗；持**早披露中大盘个股篮**；残差 **510300**。**不是** ocf/应计/盈余幅度 / 常驻 DY / 调样 |
| 主信号叶 | `disc_early_flag`（`aa < 同 end_date 同伴中位`） |
| 禁 | 小盘 / CB / 金主仓；行业 ETF tercile；份额流 / 价叶；龙虎 seat；unlock/share_type；LIMITUP；overnight*；分红/DY；ocf 质量主攻；盈余幅度主轴；V31 调参 |
| 宇宙 | CSI300∪CSI500；**X1 缺权 → float top800**（本窗 `index_weight` 自 2018，方法=`float_mktcap_top800_approx`）；滤 ST / 价&lt;2 / 停牌 |
| PIT | `pit=first available_at per (instrument_id,end_date)`（报告日 18:00 Asia/Shanghai）→ **下一开盘**；持有 **K=10**；**不可前移**；重述不回改历史首次入日 |
| 持仓 | 早披露 top **N=25** 等权（过多按更早 aa→流通市值）；`w_stock=min(0.70,0.028*n)`；n=0→100% 510300 |
| 闸门 | 成本平台 `ExecConfig.strategy_v1`（研究目标 25bp）；容量 **60万∧100万**；Sharpe≤0 \| avg_names=0 → fail_precheck；去早于中位无增量 → 自拒 |
| 覆盖标注 | **`coverage_blocked_x1=false`**（完整 X1 有事件）；冒烟窗=`2015-06-01→2017-12-29` |
| 冒烟元数据 | PID=2984737；peak_rss_MB≈1578.8；elapsed≈100.9s；n_sessions=634 |

### 1.1 三臂定义

| arm | note | 角色 |
|---|---|---|
| **E1** | 早披露：aa&lt;同 end_date 中大盘同伴中位；K=10；topN 更早 aa→流通市值 | **主** |
| **E2** | 全部已披露 ablation：去「早于中位」；持窗内全部中大盘首次披露入日 | **自拒对照（必须）** |
| **E3** | 晚披露敏感性：aa&gt;同 end_date 中位 | 敏感性 / 第二自拒支撑 |

---

## 2. 覆盖诚实账

| 窗 | 事件数 / 说明 | 判定 |
|---|---|---|
| 标准 X1 `2015-06-01→2017-12-31` 首次 aa（SH/SZ） | **39373** 行 / **4279** 只；aa 2015-06-01→2017-12-30 | **`coverage_ok`** |
| 同上 ∩ float top800（本轮月频 asof） | **7952** / **1209** 只 | 提案 8195/1254；差因 lookback≤3 vs 月频快照 |
| 同上且 aa&lt;同 end_date 中位（早披露） | **3534** / 19 簇 | 提案/接线 **3664/1057/18**；同差因，**非伪造** |
| AI 接线（lookback≤3） | **3664** / **1057** / 18 簇；`coverage_blocked_x1=false` | 口径一致；脚手架仅对照 |
| 本轮入选（中大盘∩滤后，pad 窗事件） | E1 ok=**4028**；E2=**9059**；E3=**3898** | 日程 avg_names E1≈10.06 |
| 冒烟 NAV 窗 | **2015-06-01→2017-12-29**（完整 X1） | **full-X1** |

**结论：** 完整 X1 有事件覆盖成立（与提案/接线同量级）；本轮**是**完整 X1 过闸叙事（结果为拒）。V31 未触碰。

---

## 3. 失败条件对照（提案 §4）

| # | 失败条件 | 本轮结果 | 判定 |
|---|---|---|---|
| 1 | 去掉「早于中位」改全部已披露同构/无增量 → **自拒** | E1 Sharpe60=**−0.470** **&lt;** E2=**−0.230**（Δ≈−0.240）；Jaccard(E1,E2)≈**0.313** | **`self_reject=true`** |
| 2 | 用晚披露 / 非早晚旗替代后无方向优势 | E3=**−0.345** ≥ E1；Jaccard(E1,E3)≈**0.001** | **支撑自拒**（早晚无优势） |
| 3 | @60万∧100万 Sharpe≤0 或 avg_names=0 | E1–E3 Sharpe **全 ≤0**；avg_names∈[5.21, 11.30]（&gt;0） | **触** fail_precheck |
| 4 | PIT 违规 / 前移 | first-aa + normalize()+1d→searchsorted；未见前移 | **未见**违规 |
| 5 | 主仓滑向小盘 / CB / 金 / ETF tercile / seat / 解禁 / ocf / 分红 DY / V31 | 个股中大盘披露日历事件；残差 510300；禁叶断言 | **未见**违规 |

**自拒结论：** 全部已披露（E2）相对早披露主臂 **更少负** → **早于中位无交易增量** → **自拒成立**。持仓中等重叠说明不是「同名换皮」，而是**机制本身不可交易**。

---

## 4. 真 NAV 冒烟（60万∧100万｜完整 X1）

规则：披露入日事件活集；顶 25 等权个股 + 510300；K=10；Sharpe≤0 → fail_precheck（不开 X2）。  
avg_names = **日程日活集均值**（含无事件日压舱；非 NAV 路径残留计数）。  
**总闸：`any_x1_pass=false`。`self_reject=true`。`coverage_blocked_x1=false`。**

| arm | note | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg_names | n_events | 处置 / 一句原因 |
|---|---|---|---|---|---|---|
| **E1** | 早披露主 | −16.2%/−49.9%/ **−0.470** | ≈同/ **−0.445** | 10.06 | 4028 | **fail_precheck** — 双 AUM Sharpe≤0 |
| **E2** | 全部已披露 ablation | −9.8%/−46.2%/ **−0.230** | ≈同/ **−0.194** | 11.30 | 9059 | **对照 fail** — 亦负但 **≥** E1 → 支撑自拒 |
| **E3** | 晚披露敏感性 | −12.9%/−47.5%/ **−0.345** | ≈同/ **−0.339** | 5.21 | 3898 | **对照 fail** — ≥ E1 → 无早晚方向优势 |

†100万与60万同权表；数值接近。未开 X2 / S / 密封。n_sessions=634。  
成本：平台 `strategy_v1` impact_k=1；E1@60万 ann_turnover≈22.7、cost≈8.0% AUM（X1 累计）。E2 turnover≈15.7、cost≈5.5%。E3≈12.7 / 4.2%。  
终值参考：E1 60万→≈37.9万；E2→≈45.9万；E3→≈41.9万（同窗）。  
宇宙方法：全程 `float_mktcap_top800_approx`（X1 无 CSI 权重快照）。

---

## 5. 覆盖 / PIT / 稀疏性

| 项 | 数值 / 结论 |
|---|---|
| 标准 X1 首次 aa | 39373 / 4279 只 → coverage_ok |
| 早披露∩top800（本轮/接线） | 3534 vs 接线 3664 → 同量级；差写入 diagnostics |
| 冒烟入选 | E1=4028；E2=9059；E3=3898（中大盘滤后 pad 窗） |
| 组合 avg_names（日程） | E1≈10.06：K=10 短窗 → 部分日 n&lt;25 属常态；E3≈5.21 更稀 |
| PIT | 与 AI 接线一致；K=10 写死；未见前移 |
| 禁叶 / 禁袖套 | runner 断言；**未碰 V31**；未开第二套 NAV |

---

## 6. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | float top800 / 中大盘；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁行业 ETF 时序 / 份额流 / 价叶 / seat / 解禁 / LIMITUP / ocf / 分红 DY | ✅（个股披露日历事件） |
| 容量主结论 60万∧100万 | ✅（同 fail） |
| 完整 X1 Sharpe 叙事 | ✅（有覆盖；结果拒） |
| Sharpe≤0 → fail；不开 X2 | **已触** fail；**不开 X2** ✅ |
| 去早于中位自拒 | 已跑 E2；**触发** ✅ |
| promotion / Strategy | `false` / **不交** ✅ |
| 必须预测组合收益且可交易 | **否** — 全负 Sharpe |
| V31 | **未触碰、未晋级** ✅ |

---

## 7. 处置

- **裁决：`reject`**（完整 X1 fail_precheck + **`self_reject=true`**）
- **`self_reject=true`**：早披露相对全部已披露 **无 Sharpe 增量**（E1−E2≈−0.240）；晚披露亦不更差于早披露
- **`coverage_blocked_x1=false`** — 覆盖诚实；拒因是真 NAV，非缺数
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- **不开 X2 / 不密封 / 不磨** N/K/成本/同构变体（含再扫中位定义、再换盈余/ocf 打分主轴）
- **勿晋级 V31**；本轮未触碰 V31 包或回执
- 停磨 seat / 解禁 type / ETF tercile / 价叶 / 份额流 / 分红 DY / ocf 教材近亲

---

## 8. 路径索引

| 产物 | 路径 |
|---|---|
| runner | `output/v3/run_stock_disc_early_smoke.py` |
| pretest JSON | `output/v3/pretest_batch_20261012_stock_disc_early.json` |
| 诊断 | `output/v3/stock_disc_early/diagnostics.json` |
| 分臂 | `output/v3/stock_disc_early/stock-disc-early-e{1,2,3}/` |
| 跑日志 | `output/v3/stock_disc_early/run.log` |
| AI 接线 / 包 | `research/ai_factor_disc_early_panels.py`；`output/ai_factor/stock_disc_early_v34/` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V34_DISC_EARLY_ZH.md` |
| 本复核 | `docs/v2/AI_V34_STOCK_DISC_EARLY_BETA_REVIEW_ZH.md` |
