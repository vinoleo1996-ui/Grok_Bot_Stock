# AI STOCK-DIV-IMP — Beta 完整 X1 冒烟复核（reject｜兼自拒）

更新：2026-10-12 09:32 ET（America/New_York）  
提案：`docs/v2/AI_STOCK_ARM_PROPOSAL_V33_DIV_IMP_ZH.md`  
AI 接线：`research/ai_factor_div_imp_panels.py`；包 `output/ai_factor/stock_div_imp_v33/`；接线回执 `docs/v2/AI_DIV_IMP_WIRING_RECEIPT_ZH.md`  
冒烟 runner：`output/v3/run_stock_div_imp_smoke.py`  
结果根：`output/v3/stock_div_imp/`（D1–D3 子目录 + `diagnostics.json`）  
pretest：`output/v3/pretest_batch_20261012_stock_div_imp.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。**不开 X2**。  
**≠ STOCK-INDEX-REBAL / STOCK-UNLOCK-SHARETYPE / STOCK-SEAT-SPLIT / ETF-DT-SEAT / 价叶·份额流 / ocf 教材；本臂是现金分红实施公告短窗个股篮。V31 未触碰、未晋级。**

---

## 0. 一句话裁决

**reject（完整 X1；兼 `self_reject=true`）。**  
D1–D3 @60万∧100万 **全 `fail_precheck`**（Sharpe 全 ≤0；`any_x1_pass=false`）。  
月频常驻 DY 对照 **D3 Sharpe60≈−0.001 ≥ D1≈−0.196** → **无实施入日事件增量** → **`self_reject=true`**（持仓 Jaccard(D1,D3)≈0.013，非持仓同构，但是**增量失败**）。  
`promotion_approved=false`；**handoff: NO**；**不交 Strategy**；**不开 X2**。  
回执路径本文件。

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `stock_event_div_imp` / **STOCK-DIV-IMP** |
| 机制 | 现金分红 **实施公告**（`imp_ann_date`∪`ann_date`）入日后短窗，中大盘上强制公司行动与持仓再配置；持**有现金实施的中大盘个股篮**；残差 **510300**。**不是**常驻股息率（DY）截面因子 |
| 主信号叶 | `div_imp_cash_flag`（`div_proc`含「实施」∧`cash_div>0`；排除停止实施） |
| 禁 | 小盘 / CB / 金主仓；行业 ETF tercile；份额流 / 价叶；龙虎 seat；unlock/share_type；LIMITUP；overnight*；ocf/accrual/roa 教材；异动标题叶（X1=0） |
| 宇宙 | CSI300∪CSI500；**X1 缺权 → float top800**（本窗 `index_weight` 自 2018，方法=`float_mktcap_top800_approx`）；滤 ST / 价&lt;2 / 停牌 |
| PIT | `pit=coalesce(imp_ann_date,ann_date)`；normalize Asia/Shanghai 日末 23:59 口径 → **下一开盘**；持有 **K=10** 交易日锚入日；**不可前移**；**不以 `ex_date` 倒推可用**；null pit 弃用 |
| 持仓 | 入日事件 top **N=25** 等权（过多按 cash_div→流通市值）；`w_stock=min(0.70,0.028*n)`；n=0→100% 510300 |
| 闸门 | 成本平台 `ExecConfig.strategy_v1`（研究目标 25bp）；容量 **60万∧100万**；Sharpe≤0 \| avg_names=0 → fail_precheck；去入日塌成月频 DY 无增量 → 自拒 |
| 覆盖标注 | **`coverage_blocked_x1=false`**（完整 X1 有事件）；冒烟窗=`2015-06-01→2017-12-29` |
| 冒烟元数据 | PID=2853513；peak_rss_MB≈1573.8；elapsed≈118.0s；n_sessions=634 |

### 1.1 三臂定义

| arm | note | 角色 |
|---|---|---|
| **D1** | 实施 cash>0 事件窗 K=10；同日 topN 按 cash_div→流通市值 | **主** |
| **D2** | 同窗按 cash_div 优先排序（敏感性） | 敏感性 |
| **D3** | 月频常驻 DY：trailing365d 实施 cash/价 top25；**无**实施入日窗 | **自拒对照（必须）** |

---

## 2. 覆盖诚实账

| 窗 | 事件数（实施∧cash>0，PIT=imp∪ann） | 判定 |
|---|---|---|
| 标准 X1 `2015-06-01→2017-12-31`（接线） | **5884** 行 / **2713** 只 / unique(ts_code,end_date)≈**5695** | **`coverage_ok`**（≠ blocked） |
| 同上按 `ann_date` | **5014** / 2655 只 | 次口径一致 |
| pit 窗 | 2015-06-01→2017-12-26；ex_date 覆盖≈99.97% | 未用 ex 前移 |
| 本轮入选（中大盘∩滤后） | D1/D2 ok=**2087**（uni 滤 4484；entry skip 3） | 日程 avg_names≈11.17 |
| D3 月频 | 31 个月 ×≤25 = **775** 持仓事件 | avg_names≈24.96 |
| 冒烟 NAV 窗 | **2015-06-01→2017-12-29**（完整 X1） | **full-X1** |

**结论：** 完整 X1 有事件覆盖成立（与提案/接线一致）；本轮**是**完整 X1 过闸叙事（结果为拒）。

---

## 3. 失败条件对照（提案 §4）

| # | 失败条件 | 本轮结果 | 判定 |
|---|---|---|---|
| 1 | 去掉「实施入日事件窗」改常驻月频 DY 同构/无增量 → **自拒** | best 事件臂 D1 Sharpe60=**−0.196** **&lt;** D3=**−0.001**（Δ≈−0.195）；Jaccard(D1,D3)≈**0.013**（持仓几乎不重叠，但**无正增量**） | **`self_reject=true`** |
| 2 | @60万∧100万 Sharpe≤0 或 avg_names=0 | D1–D3 Sharpe **全 ≤0**；avg_names∈[11.17, 24.96]（&gt;0） | **触** fail_precheck |
| 3 | PIT 违规 / 用 ex_date 前移 | 接线 `coalesce(imp,ann)` + `normalize()+1d→searchsorted`；未见用 ex | **未见**违规 |
| 4 | 主仓滑向小盘 / CB / 金 / ETF tercile / seat / 解禁 / ocf | 个股中大盘实施事件；残差 510300；禁叶 runner 断言 | **未见**违规 |
| 5 | 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP | 个股篮事件驱动 | **未见**违规 |

**自拒结论：** 月频常驻 DY（D3）相对实施入日事件臂 **无更差甚至更优（少负）** → **事件窗无交易增量** → **自拒成立**。持仓低重叠说明不是「同名换皮」，而是**机制本身不可交易**。

---

## 4. 真 NAV 冒烟（60万∧100万｜完整 X1）

规则：实施入日事件活集；顶 25 等权个股 + 510300；K=10；Sharpe≤0 → fail_precheck（不开 X2）。  
avg_names = **日程日活集均值**（含无事件日压舱；非 NAV 路径残留计数）。  
**总闸：`any_x1_pass=false`。`self_reject=true`。`coverage_blocked_x1=false`。**

| arm | note | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg_names | n_events | 处置 / 一句原因 |
|---|---|---|---|---|---|---|
| **D1** | 实施窗主 | −8.2%/−42.5%/ **−0.196** | ≈同/ **−0.214** | 11.17 | 2087 | **fail_precheck** — 双 AUM Sharpe≤0 |
| **D2** | cash_div 优先 | −9.9%/−44.3%/ **−0.264** | ≈同/ **−0.283** | 11.17 | 2087 | **fail_precheck** — 弱于 D1，仍负 |
| **D3** | 月频常驻 DY | −3.3%/−40.6%/ **−0.001** | ≈同/ **−0.001** | 24.96 | 775 | **对照 fail** — 亦负但 **≥** 事件臂 → 支撑自拒 |

†100万与60万同权表；数值接近。未开 X2 / S / 密封。n_sessions=634。  
成本：平台 `strategy_v1` impact_k=1；D1@60万 ann_turnover≈10.0、cost≈3.8% AUM（X1 累计）。D3 turnover≈3.0、cost≈1.0%（月频更低）。  
终值参考：D1 60万→≈48.1万；D2→≈45.8万；D3→≈55.0万（同窗）。  
宇宙方法：全程 `float_mktcap_top800_approx`（X1 无 CSI 权重快照）。

---

## 5. 覆盖 / PIT / 稀疏性

| 项 | 数值 / 结论 |
|---|---|
| 标准 X1 事件（接线） | 5884 / 2713 只 → coverage_ok |
| 冒烟入选 | D1/D2=2087（中大盘滤后）；D3=775 |
| 组合 avg_names（日程） | D1/D2≈11.17：K=10 短窗 → 部分日 n&lt;25 属常态；D3≈24.96 近满仓 |
| PIT | 与 AI 接线 `pit_rules()` 一致；K=10 写死；未用 ex_date |
| 禁叶 / 禁袖套 | runner + 接线 universe_rules 双端一致；**未碰 V31** |

---

## 6. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | float top800 / 中大盘；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁行业 ETF 时序 / 份额流 / 价叶 / seat / 解禁 / LIMITUP / ocf 教材 | ✅（个股分红实施事件） |
| 容量主结论 60万∧100万 | ✅（同 fail） |
| 完整 X1 Sharpe 叙事 | ✅（有覆盖；结果拒） |
| Sharpe≤0 → fail；不开 X2 | **已触** fail；**不开 X2** ✅ |
| 月频 DY 自拒 | 已跑 D3；**触发** ✅ |
| promotion / Strategy | `false` / **不交** ✅ |
| 必须预测组合收益且可交易 | **否** — 全负 Sharpe |

---

## 7. 处置

- **裁决：`reject`**（完整 X1 fail_precheck + **`self_reject=true`**）
- **`self_reject=true`**：实施入日事件臂相对月频常驻 DY **无 Sharpe 增量**（D1−D3≈−0.195）
- **`coverage_blocked_x1=false`** — 覆盖诚实；拒因是真 NAV，非缺数
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- **不开 X2 / 不密封 / 不磨** N/K/成本/同构变体（含再扫 cash_div 排序、再换 DY 窗）
- **勿晋级 V31**；本轮未触碰 V31 包或回执
- 停磨 seat / 解禁 type / ETF tercile / 价叶 / 份额流 / ocf 教材近亲

---

## 8. 路径索引

| 产物 | 路径 |
|---|---|
| runner | `output/v3/run_stock_div_imp_smoke.py` |
| pretest JSON | `output/v3/pretest_batch_20261012_stock_div_imp.json` |
| 诊断 | `output/v3/stock_div_imp/diagnostics.json` |
| 分臂 | `output/v3/stock_div_imp/stock-div-imp-d{1,2,3}/` |
| 跑日志 | `output/v3/stock_div_imp/run.log` |
| AI 接线 / 包 | `research/ai_factor_div_imp_panels.py`；`output/ai_factor/stock_div_imp_v33/` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V33_DIV_IMP_ZH.md` |
| 本复核 | `docs/v2/AI_V33_STOCK_DIV_IMP_BETA_REVIEW_ZH.md` |
