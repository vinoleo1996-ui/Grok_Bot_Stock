# AI STOCK-INDEX-REBAL — Beta 可用段冒烟复核（research_observe｜coverage_shifted）

更新：2026-10-12 09:26 ET（America/New_York）  
提案：`docs/v2/AI_STOCK_ARM_PROPOSAL_V31_INDEX_REBAL_ZH.md`  
AI 接线：`research/ai_factor_index_rebal_panels.py`；包 `output/ai_factor/stock_index_rebal_v31/`；接线回执 `docs/v2/AI_INDEX_REBAL_WIRING_RECEIPT_ZH.md`  
冒烟 runner：`output/v3/run_stock_index_rebal_smoke.py`  
结果根：`output/v3/stock_index_rebal/`（R1–R4 子目录 + `diagnostics.json`）  
pretest：`output/v3/pretest_batch_20261012_stock_index_rebal.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。**不开 X2**。  
**≠ STOCK-UNLOCK-SHARETYPE / STOCK-SEAT-SPLIT / ETF-DT-SEAT / 价叶·份额流；本臂是 CSI300/500 成分调入事件驱动个股篮。**

---

## 0. 一句话裁决

**research_observe（仅 coverage_shifted 可用段；≠ full-X1）。**  
标准 X1（2015-06→2017-12）**coverage_blocked**（事件=0，**勿伪造**）。  
在 **2018-06-01→2026-09-30** 可用段 @60万∧100万：主臂 **R1–R3 均 Sharpe>0**（`any_shifted_pass=true`）；随机同 N 对照 R4 Sharpe 亦>0 但 **明显弱于** 调入臂（R1 Sharpe60=**0.284** ≫ R4=**0.161**）→ **`self_reject=false`**（有调样事件增量）。  
`promotion_approved=false`；**handoff: NO**；**不交 Strategy**；**不开 X2**（非完整 X1 过闸叙事）。  
回执路径本文件。

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `stock_event_index_rebal` / **STOCK-INDEX-REBAL** |
| 机制 | CSI300/CSI500 **成分调入**公告后、生效日前后吃被动强制再平衡流；持**中大盘个股篮**；调出默认不持、**不做空**；残差 **510300** |
| 主信号叶 | `idx_add_flag`（`event=in` ∧ `index_code∈{000300.SH,000905.SH}`）；`idx_del_flag` 仅定义、本轮不持空 |
| 禁 | 小盘 / CB / 金主仓；行业 ETF tercile；份额流 / 价叶；龙虎 seat；unlock/share_type；LIMITUP-FADE；**排除 000852/CSI1000** |
| 宇宙 | 事件涉及的 CSI300∪CSI500（本就中大盘）；滤 ST / 价&lt;2 / 停牌 |
| PIT | `available_at.normalize()+1d` → `searchsorted(cal,left)` = 下一开盘；持有窗锚 **`effective_date`**；**K=10** 交易日写死；null `available_at` 弃用；**不可前移** |
| 持仓 | 调入多头 top **N=25** 等权（&gt;N 时：CSI300 优先 + float mktcap 排序，**非**价动量叶）；`w_stock=min(0.70,0.028*n)`；n=0→100% 510300 |
| 闸门 | 成本平台 `ExecConfig.strategy_v1`（研究目标 25bp）；容量 **60万∧100万**；Sharpe≤0 \| avg_names=0 → fail_precheck；随机同 N ≥ 本臂 → 自拒 |
| 覆盖标注 | **`coverage_blocked_x1=true`**；**`coverage_shifted≠full-X1`**；冒烟窗=`2018-06-01→2026-09-30` |
| 冒烟元数据 | PID=2843556；peak_rss_MB≈1778；elapsed≈77.0s；n_sessions=2024 |

### 1.1 四臂定义

| arm | note | 角色 |
|---|---|---|
| **R1** | CSI300∪CSI500 调入 top25 | **主** |
| **R2** | 仅 CSI300 调入 top25 | 分解 |
| **R3** | 仅 CSI500 调入 top25 | 分解 |
| **R4** | 同再平衡窗从中大盘宇宙 **随机抽 N=25**（seed=20261012） | **自拒对照（必须）** |

---

## 2. 覆盖诚实账（必读）

| 窗 | 事件数（000300∪000905，avail 非空） | 判定 |
|---|---|---|
| 标准 X1 `2015-06-01→2017-12-31` | **0**（add=0 / del=0） | **`coverage_blocked_x1`** — **勿伪造**早年调样 |
| 表内 earliest `available_at` | 2018-05-25 20:00 | 审查历自 2018-06 |
| AI 接线「可用段 avail≥2018-06」 | 2180（in 1090 / out 1090） | 与脚手架一致 |
| 本轮冒烟纳入（`effective_date≥2018-06-01` 的 **in**） | **1167** 行（含 2018-06 审查：avail=2018-05-25，持仓落入 6 月窗） | R1 入选 ok=**1161**（价&lt;2 滤 6） |
| 冒烟 NAV 窗 | **2018-06-01→2026-09-30**（EQ 日历止） | **`coverage_shifted≠full-X1`** |
| 审查次数 | 17（2018-06→2026-06） | 与 `csi_review_calendar` 对齐 |

**结论：** 本轮**不是**完整 X1 过闸；一切正 Sharpe / observe 仅对 **coverage_shifted** 窗成立。规程若强制完整 X1 → 仍标 blocked 并不得回填。

---

## 3. 失败条件对照（提案 §4）

| # | 失败条件 | 本轮结果 | 判定 |
|---|---|---|---|
| 1 | 同日/同窗随机同 N ≥ 本臂 → **自拒** | best 调入 R1 Sharpe60=**0.284** **&gt;** R4=**0.161**（Δ≈+0.123）；R1↔R4 Jaccard≈**0.006**（持仓几乎不重叠） | **`self_reject=false`**（有事件增量） |
| 2 | @60万∧100万 Sharpe≤0 或 avg_names=0 | R1–R3（及 R4）Sharpe 全 **&gt;0**；日程 avg_names∈[2.76, 3.90]（&gt;0；稀疏事件窗拉低全日均值） | **未触** fail_precheck |
| 3 | PIT 违规 / 前移 available_at | 接线规则 `normalize()+1d→searchsorted`；null avail 已弃；未见前移 | **未见**违规 |
| 4 | 主仓滑向小盘 / CB / 金 / ETF tercile / seat / 解禁 | 仅 000300/000905 调入；残差 510300；runner 断言禁叶 | **未见**违规 |
| 5 | 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP | 个股篮事件驱动 | **未见**违规 |

**自拒结论：** 随机同 N **未**达到或超过调入臂 → **不自拒**。增量来自调入事件集本身（非持仓偶然重合）。

---

## 4. 真 NAV 冒烟（60万∧100万｜coverage_shifted）

规则：事件窗活集；顶 25 等权个股 + 510300；K=10 锚 effective；Sharpe≤0 → fail_precheck（不开 X2）。  
avg_names = **日程日活集均值**（含审查间空窗；非 NAV 路径残留计数）。  
**总闸：`any_shifted_pass=true`。`self_reject=false`。`coverage_shifted≠full-X1`。**

| arm | note | shifted@60万 CAGR/MDD/Sharpe | shifted@100万 C/M/S | avg_names | n_events | 处置 / 一句原因 |
|---|---|---|---|---|---|---|
| **R1** | 300∪500 调入 | +3.7%/−42.9%/ **+0.284** | +3.9%/≈同/ **+0.296** | 3.90 | 1161 | **observe_shifted_pass** — 双 AUM Sharpe&gt;0 且 &gt;R4 |
| **R2** | 仅 CSI300 | +3.6%/−42.3%/ **+0.278** | +3.7%/≈同/ **+0.286** | 2.76 | 316 | **observe_shifted_pass** — 略弱于 R1，仍过闸 |
| **R3** | 仅 CSI500 | +3.0%/−44.7%/ **+0.252** | +3.1%/≈同/ **+0.259** | 3.90 | 845 | **observe_shifted_pass** — 弱于 R1/R2，仍过闸 |
| **R4** | 随机同 N | +1.3%/−43.2%/ **+0.161** | +1.4%/≈同/ **+0.167** | 3.90 | 425 | **对照** — 亦正 Sharpe（压舱+稀持股市况），但 **显著弱于** 调入臂 → 支撑「事件增量」 |

†100万与60万同权表；数值接近。未开 X2 / S / 密封。n_sessions=2024。  
成本：平台 `strategy_v1` impact_k=1；R1@60万 ann_turnover≈2.81、cost≈3.2% AUM（长窗累计）。  
终值参考：R1 60万→≈81.0万；R4 60万→≈66.5万（同窗）。  
NAV 路径 avg_names（引擎残留计数）偏高（R1≈27），**闸门以日程活集 avg_names 为准**（与 V30 一致）。

---

## 5. 覆盖 / PIT / 稀疏性

| 项 | 数值 / 结论 |
|---|---|
| 标准 X1 | 事件 **0** → blocked |
| 冒烟窗 | 2018-06-01→2026-09-30；17 次半年度审查 |
| R1 入选 | ok=1161；price&lt;2 skip=6；ST=0 |
| R2 / R3 | 316 / 845 |
| R4 | 17 窗 ×25 =425；宇宙方法=`index_weight_asof` |
| 组合 avg_names（日程） | 2.76–3.90：K=10 短窗 + 半年一审 → **大部分交易日 n=0 压舱**，属事件臂常态，非空信号 |
| PIT | 与 AI 接线 `pit_rules()` 一致；K=10 写死 |
| 禁叶 / 禁袖套 | runner + 接线 universe_rules 双端一致 |

---

## 6. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | CSI300/500 事件名；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁行业 ETF 时序 / 份额流 / 价叶 / seat / 解禁 / LIMITUP | ✅（个股调样事件） |
| 容量主结论 60万∧100万 | ✅（同过） |
| 标准 X1 Sharpe 叙事 | **不适用** — coverage_blocked；仅 shifted 窗 ✅ |
| Sharpe≤0 → fail；不开 X2 | 未触 fail；**仍不开 X2**（非 full-X1）✅ |
| 随机同 N 自拒 | 已跑 R4；**未触发** ✅ |
| promotion / Strategy | `false` / **不交** ✅ |
| 必须预测组合收益且可交易 | **shifted 窗满足观察门槛**（正 Sharpe + 事件增量）；**不足以**当 full-X1 晋级 |

---

## 7. 处置

- **裁决：`research_observe`**（coverage_shifted 可用段；**不是** reject，也**不是** promotion）
- **`self_reject=false`**：调入臂相对随机同 N 有清晰 Sharpe 增量（R1−R4≈+0.12）
- **`coverage_blocked_x1=true`**；**`coverage_shifted≠full-X1`** — 任何对外叙述必须带此标注
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单晋级
- **不开 X2 / 不密封 / 不磨** N/K/成本微调同构；不把本窗正 Sharpe 写成「X1 已过」
- 若后续要升格：须另立规程（扩史数据或接受 shifted 窗为正式窗），**本轮不停在 observe**
- 停磨 seat / 解禁 type / ETF tercile / 价叶 / 份额流 近亲

---

## 8. 路径索引

| 产物 | 路径 |
|---|---|
| runner | `output/v3/run_stock_index_rebal_smoke.py` |
| pretest JSON | `output/v3/pretest_batch_20261012_stock_index_rebal.json` |
| 诊断 | `output/v3/stock_index_rebal/diagnostics.json` |
| 分臂 | `output/v3/stock_index_rebal/stock-index-rebal-r{1,2,3,4}/` |
| 跑日志 | `output/v3/stock_index_rebal/run.log` |
| AI 接线 / 包 | `research/ai_factor_index_rebal_panels.py`；`output/ai_factor/stock_index_rebal_v31/` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V31_INDEX_REBAL_ZH.md` |
| 本复核 | `docs/v2/AI_V31_STOCK_INDEX_REBAL_BETA_REVIEW_ZH.md` |
