# AI STOCK-SEAT-SPLIT — Beta 研究级 X1 复核（reject）

更新：2026-10-12 09:11 ET（America/New_York）  
提案：`docs/v2/AI_STOCK_ARM_PROPOSAL_V29_SEAT_SPLIT_ZH.md`  
接线：`docs/v2/AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md`；模块 `research/ai_factor_dt_seat_panels.py`  
对照 prereg：`docs/v2/V3_EVT_DT_INST_STOCK_PREREG.md`（A4 ablation）  
冒烟 runner：`output/v3/run_stock_seat_split_smoke.py`  
结果根：`output/v3/stock_seat_split/`（A1–A4 子目录 + `x1_leaves/` + `diagnostics.json`）  
pretest：`output/v3/pretest_batch_20261012_stock_seat_split.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
**≠ ETF-DT-SEAT / V21–V23；本臂是个股中大盘篮，非行业 ETF 时序。**

---

## 0. 一句话裁决

**reject。**  
席位分裂个股臂 **A1–A4 全 `fail_precheck`**（60万∧100万 X1 Sharpe 全负；`any_x1_pass=false`）。  
A4（inst-only）ablation：与 A1 持仓 Jaccard≈0.56、得分 Spearman≈0.77（**未**达同构自拒阈）；A3（retail≤0 掩码）Sharpe 相对 A4 略好但仍为负——retail 腿有方向增量、**无**可交易增量。  
handoff: **NO**。`promotion_approved=false`。**勿磨同构 / 勿开 X2 / 勿交 Strategy。**

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `stock_event_seat_split` / **STOCK-SEAT-SPLIT** |
| 机制 | `dt_inst_net_*` vs `dt_retail_hot_net_*` 截面 z 分歧 → 中大盘个股 top25 等权；残差 **510300** |
| 叶（X1 自建） | `dt_inst_net_5/10`、`dt_retail_hot_net_5/10`（`build_dragon_seat_panels`；样例窗 `dt_seat_leaves_v1` 仅 2024-04→2025-06，**不可**直接用于 X1） |
| 禁 | 小盘 / CB / 金主仓；行业 ETF tercile；份额流 / 价叶 |
| 宇宙 | CSI300∪CSI500；X1 权重表自 20180131 → **float top800** 近似；滤 ST / 价&lt;2（有证据时）/ 停牌由引擎处理 |
| PIT | `available_at_alpha_conservative.normalize()+1d` → T+2 open；**不可前移** |
| 持仓 | top **N=25** 等权；`w_stock=min(0.70, 0.028*n)`；n=0→100% 510300；**周度**再平衡 |
| 闸门 | 成本平台 `ExecConfig.strategy_v1`（研究目标 25bp）；容量 **60万∧100万**；X1 Sharpe≤0 \| avg_names=0 → fail_precheck（**不开 X2**） |
| 冒烟元数据 | PID=2819685；peak_rss_MB≈2119；elapsed≈80.6s；X1=`2015-06-01→2017-12-29` |

### 1.1 四臂定义

| arm | note | 角色 |
|---|---|---|
| **A1** | `cs_z(dt_inst_net_5) − cs_z(dt_retail_hot_net_5)` | 主轴 split5 |
| **A2** | `cs_z(dt_inst_net_10) − cs_z(dt_retail_hot_net_10)` | 主轴 split10 |
| **A3** | split5 ∧ `retail_hot_net_5≤0` 掩码 | 加强 |
| **A4** | 仅 `cs_z(dt_inst_net_5)` | **ablation**（去 retail 腿 → EVT-DT-INST-STOCK 同构检验） |

A5（∩ 新鲜 ann_earn\|buyback / lu_streak）**未跑**：公告 PIT 自 20180101（X1 无覆盖）；`lu_streak` 叶未落盘。非主轴，不影响本轮闸门。

---

## 2. 失败条件对照（提案 §4）

| # | 失败条件 | 本轮结果 | 判定 |
|---|---|---|---|
| 1 | 去掉 retail 腿后与 EVT-DT-INST-STOCK 同构 / 无增量 → **自拒** | A1↔A4 Jaccard≈**0.56**、Spearman≈**0.77**；A3↔A4 Jaccard≈**0.31**。A3 Sharpe60=−0.637 **优于** A4=−0.793（仍负）→ 有方向差、**非**纯同构 | **未**触发自拒标签；但 **无**可交易增量 |
| 2 | X1@60万∧100万 Sharpe≤0 或 avg_names=0 | **四臂全** Sharpe≤0；avg_names∈[9.6, 24.1]（>0） | **fail_precheck**（主裁决） |
| 3 | PIT 违规 / 前移 available_at | 面板 gap 规则与接线回执一致；未见前移 | **未见**违规 |
| 4 | 与行业 ETF 时序近亲 | 持仓为个股篮+510300，**非** SW→ETF tercile；未跑 ind_ret ρ（袖套形态已排除） | **非** ETF-DT-SEAT 近亲 |
| 5 | 确认交叉过稀 / nonempty≈0 | 叶 nonempty_inst5≈0.028、retail5≈0.042；组合 avg_names>0 | 覆盖薄但**非**空仓级 |

**ablation 结论：** retail 腿改变排序与持仓（尤其 A3 掩码），**不是**「去掉即完全塌成 A4」的零信息维；然而在真 NAV 上 **不能**把负 Sharpe 抬过 0 → 按硬闸 **reject**，并记录「有形态差、无可交易增量」。

---

## 3. 真 NAV 冒烟（60万∧100万 X1）

规则：周度；顶 25 等权个股 + 510300；X1 Sharpe≤0 → **fail_precheck**（不开 X2）。  
avg_names = **调仓日 topN 日程均值**（非 NAV 路径残留计数）。  
**总闸：`any_x1_pass=false`。四臂全 fail。**

| arm | note | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg_names | 处置 / 一句原因 |
|---|---|---|---|---|---|
| **A1** | split5 | −29.2%/−61.2%/ **−0.981** | −31.0%/−64.0%/−1.018 | 19.16 | **fail_precheck** — X1 Sharpe≤0 |
| **A2** | split10 | −27.6%/−61.8%/ **−0.901** | −28.4%/−62.9%/−0.892 | 24.08 | **fail_precheck** — Sharpe≤0 |
| **A3** | split5∧retail≤0 | −20.2%/−54.1%/ **−0.637** | −22.1%/−56.3%/−0.691 | 9.55 | **fail_precheck** — Sharpe≤0（相对最轻负） |
| **A4** | inst-only ablation | −24.1%/−57.9%/ **−0.793** | −24.7%/−59.6%/−0.779 | 14.18 | **fail_precheck** — Sharpe≤0 |

†100万与60万同权表；数值接近。未开 X2 / S / 密封。n_rebalance≈133；宇宙方法=`float_mktcap_top800_approx`。  
成本：平台 `strategy_v1` impact_k=1；A1@60万 cost_pct_aum≈7.0%（含佣金/印花/冲击，研究目标 25bp 为口径参考）。

对照既有 **EVT-DT-INST-STOCK** X1@60万 Sharpe≈−0.55（不同得分：`Σnet_buy/amount`，非 rolling cs_z）——同族中大盘龙虎个股叙事，亦已 fail；本臂 split 变体 **未**翻盘。

---

## 4. 覆盖 / PIT

| 项 | 数值 / 结论 |
|---|---|
| X1 会话 | ≈634（2015-06-01→2017-12-29） |
| 面板日历 | 2015-05-04→2017-12-29（n=654，含 rolling 缓冲） |
| 面板列 | 1353（月度 float top800 并集） |
| 事件 | n_events≈101769；n_instruments≈1248 |
| nonempty | inst5≈0.0276；retail5≈0.0421；mean_names/day inst5≈37.4、retail5≈57.0 |
| 组合 avg_names | 9.6–24.1（>0；失败主因 Sharpe≤0） |
| PIT | conservative+1d→T+2 open；与接线回执一致 |
| 禁叶 / 禁袖套 | runner 断言禁份额流/价叶/行业 ETF tercile/CB/金 |

---

## 5. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | float top800 / 指数成分；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁行业 ETF 时序 / 份额流 / 价叶 | ✅（个股篮） |
| 容量主结论 60万∧100万 | ✅（同败） |
| X1 Sharpe≤0 → fail_precheck；不开 X2 | ✅ |
| promotion / Strategy | `false` / **不交** ✅ |
| ablation（去 retail） | 已跑 A4；非自拒同构，但无过闸增量 ✅ |
| 必须预测组合收益且可交易 | **不满足** — 四臂 X1 全负 Sharpe |

---

## 6. 处置

- **裁决：reject**（非 research_observe：无臂 X1 Sharpe>0）
- `self_reject=false`（retail 腿非零信息维，但 **无可交易增量**）
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- **勿磨** V21–V23 / ETF-DT-SEAT / 本臂同构变体（换窗、换 N、微调 z）
- 等真正新机制提案/包；本轮停

---

## 7. 路径索引

| 产物 | 路径 |
|---|---|
| runner | `output/v3/run_stock_seat_split_smoke.py` |
| pretest JSON | `output/v3/pretest_batch_20261012_stock_seat_split.json` |
| 诊断 | `output/v3/stock_seat_split/diagnostics.json` |
| X1 叶切片 | `output/v3/stock_seat_split/x1_leaves/*.parquet` |
| 分臂 | `output/v3/stock_seat_split/stock-seat-split-a{1,2,3,4}/` |
| 本复核 | `docs/v2/AI_V29_STOCK_SEAT_SPLIT_BETA_REVIEW_ZH.md` |
