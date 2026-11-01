# AI STOCK-UNLOCK-SHARETYPE — Beta 研究级 X1 复核（reject）

更新：2026-10-12 09:17 ET（America/New_York）  
提案：`docs/v2/AI_STOCK_ARM_PROPOSAL_V30_UNLOCK_SHARETYPE_ZH.md`  
粗解禁对照：`docs/v2/V3_UNLOCK_WINDOW_RESID_PREREG.md`；结果 `output/v3/unlock_window_resid/`  
数据：`data/v2/share_float/share_float_pit.parquet`；覆盖回执 `docs/v2/SHARE_FLOAT_X1_2015_2017.md`  
冒烟 runner：`output/v3/run_stock_unlock_sharetype_smoke.py`  
结果根：`output/v3/stock_unlock_sharetype/`（U1–U5 子目录 + `diagnostics.json`）  
pretest：`output/v3/pretest_batch_20261012_stock_unlock_sharetype.json`  
复核方：QuantLab Beta。`promotion_approved=false`。**不交 Strategy**。  
**≠ UNLOCK-WINDOW-RESID / STOCK-SEAT-SPLIT / ETF-DT-SEAT / 价叶·份额流；本臂是个股中大盘解禁 share_type 构成。**

---

## 0. 一句话裁决

**reject（含自拒）。**  
解禁 **share_type** 个股臂 **U1–U5 全 `fail_precheck`**（60万∧100万 X1 Sharpe 全负；`any_x1_pass=false`）。  
U4（粗解禁 ablation）复现 UNLOCK-WINDOW-RESID：Sharpe60≈**−0.142**、avg_names≈**1.69**（与对照 pretest 一致）。  
type 主轴（U1/U2/U3/U5）相对 U4 **无 Sharpe 增量**（best U1=−0.149 **劣于** U4）→ **`self_reject=true`**（去掉 type 塌成粗解禁 / 无新信息维）。  
handoff: **NO**。`promotion_approved=false`。**勿磨同构 / 勿开 X2 / 勿交 Strategy。**

---

## 1. 包 / 机制摘要

| 项 | 内容 |
|---|---|
| sleeve / 族 | `stock_event_unlock_sharetype` / **STOCK-UNLOCK-SHARETYPE** |
| 机制 | 解禁窗按 **`share_type` 构成**筛「定增（及同类）占比/规模高」的中大盘；吃财务投资者退出抛压折价；残差 **510300** |
| 主信号 | **share_type 构成**，非粗 UNLOCK 残差 |
| 禁 | 小盘 / CB / 金主仓；行业 ETF tercile；份额流 / 价叶；龙虎 seat |
| 宇宙 | CSI300∪CSI500；X1 权重表自 20180131 → **float top800** 近似；滤 ST / 价&lt;2（有证据时）/ 停牌由引擎处理 |
| PIT | 表内 `available_at`（=`ann_date` 18:00 Asia/Shanghai）→ **下一开盘**；浮窗锚 **`float_date`**；评估日=float 前 1 会话 → 入场下一开盘（且 ≥ trade_ready）；平仓=float+2 会话；**不可前移** |
| 持仓 | top **N=25** 等权；`w_stock=min(0.70, 0.028*n)`；n=0→100% 510300；**事件日活集**（非周度） |
| 闸门 | 成本平台 `ExecConfig.strategy_v1`（研究目标 25bp）；容量 **60万∧100万**；X1 Sharpe≤0 \| avg_names=0 → fail_precheck（**不开 X2**） |
| 冒烟元数据 | PID=2829196；peak_rss_MB≈2640；elapsed≈61.6s；X1=`2015-06-01→2017-12-29` |

### 1.1 `share_type` → 叶映射（精确字符串）

权威列来自 `share_float_pit.parquet`；匹配规则为 **整串相等**（非子串模糊）：

| `share_type`（中文原串） | 叶角色 | 计入 |
|---|---|---|
| **定增股份** | `unlock_private_place_*` 主叶 | U1 ratio / U2 size 分子；U3 分子；U5 分子 |
| **股权激励限售流通** | `unlock_incentive_ratio_20` 对照 | U3 减项；**不**进 U5 分子 |
| **首发战略配售股份** | `unlock_strategic_ipo_ratio_20` 对照 | U3 减项；**不**进 U5 分子 |
| **首发原始股** | non_strategic_block 分子 | U5 分子 |
| **公开增发一般股份** | non_strategic_block 分子 | U5 分子 |
| 股权分置限售股份 / 其他类型 | 仅进分母总解禁量 | 不进主叶分子 |

事件聚合：`(ts_code, float_date)` 上 `float_share` 求和；  
`priv_ratio = 定增股份份额 / 总解禁份额`；  
`comp_diff = priv_ratio − inc_ratio − strat_ratio`；  
`nsb_ratio = (定增+公开增发+首发原始股) / 总`。

### 1.2 五臂定义

| arm | note | 角色 |
|---|---|---|
| **U1** | `unlock_private_place_ratio_20`：定增 ratio 高（priv&gt;0） | 主轴 |
| **U2** | `unlock_private_place_size_20`：定增 size=`log1p(priv_share)` 高 | 主轴 |
| **U3** | 定增 ratio − 激励 − 战略配售（构成差） | 加强 / 对照差 |
| **U4** | 粗解禁：UNLOCK-WINDOW-RESID 规则（resid20&lt;0，score=−resid），**无 type** | **ablation（必须）** |
| **U5** | `unlock_non_strategic_block_ratio_20`：(定增+公开增发+首发原始股)/总 | 可选扩展 |

---

## 2. 失败条件对照（提案 §4）

| # | 失败条件 | 本轮结果 | 判定 |
|---|---|---|---|
| 1 | 去掉 share_type 后与 UNLOCK-WINDOW-RESID 同构 / 无增量 → **自拒** | best type U1 Sharpe60=**−0.149** **&lt;** U4=**−0.142**；U1↔U4 Jaccard≈**0.43**（非持仓同构阈≥0.70，但 **零 Sharpe 增量**） | **`self_reject=true`** |
| 2 | X1@60万∧100万 Sharpe≤0 或 avg_names=0 | **五臂全** Sharpe≤0；avg_names∈[1.38, 2.16]（&gt;0） | **fail_precheck**（主裁决） |
| 3 | PIT 违规 / 前移 available_at | `available_at` 非空过滤；entry=max(eval 后开盘, trade_ready)；未见前移 | **未见**违规 |
| 4 | 主仓滑向小盘 / CB / 金 / ETF tercile / seat | float top800；残差 510300；runner 断言禁叶 | **未见**违规 |
| 5 | 定增叶过稀 / 与粗 float 单叶无增量 | avg_names 薄（1.4–2.2）但仍&gt;0；type 相对 U4 无过闸增量 | 覆盖薄 + **无增量** |

**ablation 结论：** type 分裂改变了入选集（Jaccard≈0.43–0.54，**非**纯克隆），但在真 NAV 上 **不能**把负 Sharpe 抬过 U4，更不能过 0 → 按提案失败条件 #1 **自拒**，并按硬闸 **reject**。

---

## 3. 真 NAV 冒烟（60万∧100万 X1）

规则：事件窗活集；顶 25 等权个股 + 510300；X1 Sharpe≤0 → **fail_precheck**（不开 X2）。  
avg_names = **日程日活集均值**（非 NAV 路径残留计数）。  
**总闸：`any_x1_pass=false`。五臂全 fail。`self_reject=true`。**

| arm | note | X1@60万 CAGR/MDD/Sharpe | X1@100万 C/M/S | avg_names | n_events | 处置 / 一句原因 |
|---|---|---|---|---|---|---|
| **U1** | 定增 ratio | −7.8%/−46.4%/ **−0.149** | −7.7%/−46.3%/−0.144 | 1.38 | 481 | **fail_precheck** — X1 Sharpe≤0 |
| **U2** | 定增 size | −7.8%/−46.4%/ **−0.149** | −7.7%/−46.3%/−0.144 | 1.38 | 481 | **fail_precheck** — Sharpe≤0（与 U1 同权路径：稀活集下 ratio/size 排序常共顶） |
| **U3** | 构成差 | −8.4%/−46.8%/ **−0.173** | −8.3%/−46.6%/−0.167 | 2.16 | 746 | **fail_precheck** — Sharpe≤0（最负） |
| **U4** | 粗解禁 ablation | −7.7%/−46.6%/ **−0.142** | −7.4%/−46.2%/−0.130 | 1.69 | 576 | **fail_precheck** — 对齐 UNLOCK-WINDOW-RESID |
| **U5** | non_strategic_block | −7.9%/−46.9%/ **−0.152** | −7.6%/−46.5%/−0.142 | 1.74 | 605 | **fail_precheck** — Sharpe≤0 |

†100万与60万同权表；数值接近。未开 X2 / S / 密封。n_sessions≈634；宇宙方法=`float_mktcap_top800_approx`（X1 段无指数权重快照）。  
成本：平台 `strategy_v1` impact_k=1；研究目标 25bp 为口径参考。  
对照既有 **UNLOCK-WINDOW-RESID** X1@60万 Sharpe≈−0.142、avg_names≈1.69 — **U4 数值对齐**；type 变体 **未**翻盘。

Spearman(U\* vs U4)=NaN：日活集常 &lt;5 名，秩相关样本不足；自拒主依据为 **Sharpe 无增量**（非持仓同构阈）。

---

## 4. 覆盖 / PIT

| 项 | 数值 / 结论 |
|---|---|
| X1 会话 | ≈634（2015-06-01→2017-12-29） |
| pit 表 float | 2015-01-05→2026-10-30；X1 float 行≈35814（A 股前缀后） |
| 聚合事件（pad∩宇宙） | n≈1784；names≈771；priv&gt;0≈932 |
| 入选 skip | cal=36；uni=802；entry=4；ann=0；price=0；ok_base=942 |
| type 臂事件 | U1/U2=481；U3=746；U5=605；U4=576 |
| 组合 avg_names | 1.38–2.16（&gt;0；失败主因 Sharpe≤0） |
| PIT | available_at→下一开盘；float 锚；与 SHARE_FLOAT / UNLOCK prereg 一致 |
| 禁叶 / 禁袖套 | runner 断言禁份额流/价叶/行业 ETF tercile/CB/金/seat |

---

## 5. 对照 Beta 约束

| 约束 | 判定 |
|---|---|
| 禁小盘主线 | float top800；残差 **510300** ✅ |
| 禁 CB/金主仓 | ✅ |
| 禁行业 ETF 时序 / 份额流 / 价叶 / seat | ✅（个股解禁 type） |
| 容量主结论 60万∧100万 | ✅（同败） |
| X1 Sharpe≤0 → fail_precheck；不开 X2 | ✅ |
| promotion / Strategy | `false` / **不交** ✅ |
| ablation（去 type → 粗解禁） | 已跑 U4；**触发自拒** ✅ |
| 必须预测组合收益且可交易 | **不满足** — 五臂 X1 全负 Sharpe |

---

## 6. 处置

- **裁决：reject**（非 research_observe：无臂 X1 Sharpe&gt;0）
- **`self_reject=true`**：type 相对粗解禁 **无 Sharpe 增量**（best type 反劣于 U4）→ 塌成 UNLOCK-WINDOW-RESID 信息维 / 无新机制
- `promotion_approved=false`；**handoff: NO**；**不交 Strategy**；不进 Alpha 短名单
- **勿磨** 同构变体（换窗、换 N、微调 ratio 阈值、再切 seat/ETF）
- 等真正新机制提案/包；本轮停

---

## 7. 路径索引

| 产物 | 路径 |
|---|---|
| runner | `output/v3/run_stock_unlock_sharetype_smoke.py` |
| pretest JSON | `output/v3/pretest_batch_20261012_stock_unlock_sharetype.json` |
| 诊断 | `output/v3/stock_unlock_sharetype/diagnostics.json` |
| 分臂 | `output/v3/stock_unlock_sharetype/stock-unlock-sharetype-u{1,2,3,4,5}/` |
| 粗解禁对照 | `output/v3/unlock_window_resid/` |
| 本复核 | `docs/v2/AI_V30_STOCK_UNLOCK_SHARETYPE_BETA_REVIEW_ZH.md` |
