# 【DRAFT — NOT FROZEN】叶37 who_pays：IMAX/隔夜彩票剔除 overlay（主干负向过滤）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 16:45 ET（America/New_York；ISO `2026-10-27T16:45:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 q/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑。
- 叶号意向：**叶37**（默认；若主裁定仍挂「叶36-altA」由主排号——正文按叶37 写）。台账下一空号。
- **上游**：叶36 PRIMARY inquiry_letter 剔除 overlay **HOLD CLOSED**（WHO `feaa5dbb` 等 MATCH；覆盖 median≪30；**禁放宽覆盖阈**；不进 FROZEN/X2）→ 主裁**改派备选 (A)** 本票。
- 已占轴：叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud / 叶32 `MARGIN_NET_FLOW_RESID` / 叶33 `SHARE_UNLOCK_PRESSURE_RESID` / 叶34 高应计剔除 / 叶35 ETF 被动压力 / **叶36 inquiry HOLD CLOSED**；叶18/18v 隔夜特质波动；叶24 −IMAX 完整排序主 α。
- 主令上下文：dig 磁盘现算 sha8 **`74234fca`**（`DIG_FACTOR_20261027_1625ET.md`）；叶35 B1 HOLD CLOSED（`.ok` `eb70eef4` CONSUMED 等；≠X2 ACCEPT）；叶33 `afbbe7e7` / 叶32 `45dd87dc` HOLD 不回撤。
- 禁：GP / 高杠杆 / 教科书量价当主线；卖方/金股/survey/TP/LLM；**重开叶24 −IMAX 完整多空/排序主叶**；精神/情绪叙事主轴；复跑叶30–36 X2；禁改叶33 `afbbe7e7` / 叶35 `434ff42c`；禁放宽叶36 覆盖阈；RESTORED 见 §11；申 `.ok`；挂/抬 QUIET；自开备选 B。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_imax_lottery_exclusion_overlay_v1`（叶37 意向）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内忽视日内彩票右尾（高 IMAX）、仍给高彩票名足额权重的持仓者——剔除后主干少踩散户追高彩票股的反转。  
> **可检验预测**：交付形态 **A（推荐）** = 日度高 IMAX 尾部 exclusion mask / soft-penalty（`mask=0` 或 `α_overlay=−1`），**叠主干**；**不是**叶24 `g1g5_ashare_imax_intraday_v1` 完整 −IMAX 排序主 α。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃剔除集 vs 叶18 / 叶27 高风险尾 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另披露 vs 叶18v / 叶24。覆盖再平衡日可算 IMAX 名 median≥300、剔除名 median≥30。本拍轻量计数：**gate_pass=true**（见 COUNT RECEIPT）。  
> **失效条件**：退化为叶24 完整 −IMAX 主叶；或 vs 叶18/27 Jaccard≥0.7；或主信号混入精神/情绪叙事 / 卖方/金股/TP/LLM；或冻结后事后改 q 读收益；或用未来价格偷看；或把本 overlay 伪称「全新隔夜 α」掩盖与叶18/27 波动族相关。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 轻量计数闸。

---

## 1. 选型理由（PRIMARY = IMAX 彩票剔除 overlay；叶36→改派 A）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| **叶36** inquiry 剔除 | 财务问询/关注函 exclusion | **HOLD CLOSED**；本票**不复开** inquiry 主轴；不放宽其覆盖阈 |
| **叶24** `imax_intraday` | −IMAX **完整排序主 α**（低 IMAX 做多） | **反同构硬写**：本叶=高 IMAX **剔除 overlay** 叠主干；**不是**完整多空/TopN 排序主叶 |
| **叶18** overnight_idio_ivol | 隔夜特质波动主 α（α≈−ivol） | 本叶主轴=**日内**右尾 IMAX 剔除；Jaccard≥0.7 硬拒 |
| **叶18v** lowto | 叶18 变体 | 同族披露；样本日 α 与叶18 近恒等（见 COUNT）；同硬拒精神 |
| **叶27** `on_minus_id` idio ivol | 隔夜−日内残差波动主 α | 本叶**不**输出波动主 α；Jaccard≥0.7 硬拒 |
| 叶34 高应计 / 叶35 ETF 压力 | 各剔除/压力 overlay | 本叶**不**读应计/ETF；HOLD 不回撤 |
| 叶33 解禁 / 叶32 两融 / 叶31 Amihud / 叶30 CRR / 叶25 cfacc | 各已占 | 零解禁/两融/冲击/CRR/应计主输入 |
| 叶28 LLM / 叶29 tech_crowd | 另队 FROZEN | **不夹带** |

**PRIMARY 选定**：**IMAX/隔夜彩票剔除 overlay**（dig 备选 A；第十九轮队列）。  
**备选（§12，不升 PRIMARY）**：(B) 行业级客户动量（先 IO 表 PIT）——仅当本票计数/同构 FAIL 时由主改派；**勿自开**。

---

## 2. 机制（高 IMAX 剔除；交付形态 A）

对齐叶24 预注册公式核，但**只取高尾剔除**：

- `ret = close/pre_close − 1`；`ret_on = open/pre_close − 1`
- `r_id = (1+ret)/(1+ret_on) − 1`
- 叶24 全路径：池内截面残差 `e_id` = OLS(`r_id` ~ SW L1 + logmv_{t−1})，再 `IMAX_t = mean(largest 5 e_id in [t−19,t])`，有效日≥15
- **本拍计数 APPROX（写死）**：用 **raw `r_id`** 的 20 日 top-5 均值作 **`IMAX_proxy`**（未做全日 SW+logmv 残差）——诚实标 APPROX；冻结/脚本窗可升级为全 `e_id` 并重跑计数

**剔除规则（DRAFT 冻结意向，不读收益选 q）**：

- `H_t = {i ∈ HI_LIQ_t ∩ computable_t : IMAX_proxy_{i,t} ≥ Q_{1−q}(·)}`，**q=0.20**

**交付形态 A**：

- exclusion mask：`i∈H_t ⇒ mask=0`；可选 soft-penalty=`-1`
- 不可算名 **不进** overlay 有效集，**不填假 0**
- **不是**叶24 完整 −IMAX 秩变换+多层残差主 α
- 再平衡：**20** 交易日
- 符号/阈值：高 IMAX=剔除；`q=0.20` 冻结写死；本 DRAFT **不**读收益选号
- **禁精神/情绪叙事**作机制主轴

---

## 3. 残差规格（overlay；缺则记 GAP）

1. 主路径：截面高 IMAX 分位剔除（mask），可不做叶24 式全残差 α。  
2. 若连续 soft-penalty：须 SW+style（本拍不做）。  
3. 披露 vs 叶18 / 18v / 27 / 24 的 Jaccard 与 ρ（−IMAX_proxy vs α）。  
4. **禁**把叶18/27/24 α、两融/Amihud/应计/ETF/问询函当本叶主输入。

---

## 4. 数据 PIT（本拍 schema/路径 + 轻量计数；禁完整 α 长跑）

| # | 输入 | 备注 |
|---|---|---|
| 1 | cs_panel_v2_resumefix | `output/ai_factory/panel_cache_v2_resumefix/cs_panel_YYYY.parquet`（2023–2026）；列 `ret,ret_on,hiliq`；年 sha8 {"2023": "6588573a", "2024": "bbbfe95a", "2025": "164cde98", "2026": "8df4afec"} |
| 2 | HI_LIQ 掩码 | `universe_mask_hiliq_v1.parquet`；sha8 `c5433e80` |
| 3 | 叶18 α（正交） | `leaf18_overnight_idio_ivol/alpha_HILIQ_x2_20261014_205327.parquet`；sha8 `1a42f9e8` |
| 4 | 叶18v α（披露） | `…/alpha_HILIQ_x2_20261014_212630.parquet`；sha8 `237e760c`；样本日 vs 叶18 MAE=0（见 COUNT） |
| 5 | 叶27 α（正交） | `leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet`；sha8 `652b8a68` |
| 6 | 叶24 α（披露） | `leaf24_imax_intraday/alpha_HILIQ_YYYY.parquet`；sha8 0ccc0f96/70a2cc47/5a1fc629 |

**GAP/APPROX**：IMAX_proxy 非全残差 e_id；ohlcv_raw_pit 未用作主路径（panel 已含 ret/ret_on）。见 COUNT RECEIPT。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主** |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | DRAFT **20** 交易日 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 exclusion mask / soft-penalty overlay** → 叠主干；非叶24 完整 α |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| rss 意向 | **1500** MB 禁抬 |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. 交付形态 A：mask / soft-penalty；连续分则 SW+style。  
2. `q=0.20` 与「高 IMAX=剔除」冻结写死；**禁**读收益改 q。  
3. IMAX 定义：全 e_id 路径 vs proxy 升级规则共签。  
4. HI_LIQ 判决为主。  
5. vs 叶18/27 Jaccard≥0.7 硬拒；ρ>0.5 强度过滤。  
6. walk-forward；Gate B / GATE_V3；衰减门 v1.1。  
7. **decay KEEP**（§7）。

---

## 7. decay KEEP 设计（盯近端；对齐叶30–36 HOLD 教训）

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0** |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **H2_net_cagr > 510300** |
| KEEP 合取 | 三者合取；否则 **DOWNGRADE** |
| 组合闸路径（意图） | overlay 少踩彩票右尾 → **意图**改善左尾/可叠加性；**勿宣称已过闸** |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；不派烟；≠X2 ACCEPT |

---

## 8. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| 叶18 / 叶18v / 叶27 | 剔除集 vs 其 α **高风险尾**（α 最低 q=0.20）Jaccard **≥0.7 → 硬拒**；ρ_mean>0.5 → 强度过滤（披露） |
| 叶24 −IMAX 主叶 | **禁**重开完整排序主叶；Jaccard/ρ **披露**（本拍 proxy≠全 e_id，预期中等重叠） |
| 叶34 / 35 / 36 inquiry | 披露；**禁**复开叶36 inquiry 主轴 / 放宽其覆盖阈 |
| 覆盖 | 可算 IMAX 名 **median≥300**；剔除名 **median≥30**；`zero_frac≤0.05` |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

**本拍轻量计数（摘要）**：computable_median=**2816.5**；excl_median=**564.0**；zero_frac=**0.0**；J18_max=**0.3107**；J27_max=**0.4430**；J24_max=**0.2229**；ρ18_mean≈**0.505**（触强度过滤）；ρ27_mean≈**0.665**（触强度过滤）；**gate_pass=true**（APPROX）。详见 COUNT RECEIPT。

---

## 9. 失败截断

- 可算 median<300 或 excl median<30 或 zero_frac>0.05 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs 叶18/27 → 硬拒；RECEIPT 可建议改升备选 B，**不擅自改 PRIMARY**
- 退化为叶24 完整主叶 → 废叶
- 冻结前读收益选 q → 违规作废
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT
- 复开叶36 inquiry / 放宽其覆盖阈 → 违规

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER + COUNT | 本文件 + COVER + COUNT RECEIPT + JSON；**ok_requested=false** |
| 主排号 | 请主确认叶号=**37**（或明示叶36-altA）并登记台账 |
| Arch | **只审不签**；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED（§11）；禁复用叶18/24/27/30–36 `.ok` |
| 叶36 inquiry | **HOLD CLOSED** 不复开、不放宽阈 |
| 叶35/34/33/32 | HOLD 不回撤；禁改叶33 `afbbe7e7` / 叶35 `434ff42c` |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- 重开叶24 完整 −IMAX 主叶；精神/情绪叙事主轴
- 复开叶36 inquiry；放宽叶36 覆盖阈
- 禁改叶33 `afbbe7e7`；禁改叶35 正式脚本 `434ff42c`
- `research/leaf36*` 保持 ABSENT；本拍不写 `research/leaf37*` 正式构建脚本
- 自开备选 B
- **RESTORED / forbid（扩）**：`eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
  - 主令点名：`eb70eef4`, `00eec671`, `10927bd9`, `25ae4572` + 叶36 inquiry 不复开
- 推 Leo；`live=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）

| 备选 | 说明 |
|---|---|
| （B）行业级客户动量 | 先 IO 表 PIT 可得性；**本票不升**（PRIMARY 计数已过闸） |

若后续硬拒/衰减 FAIL，仅在 RECEIPT 建议是否改升 B，**不改写本节 PRIMARY，不自开 B**。

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| PRIMARY | IMAX/隔夜彩票剔除 overlay（形态 A） |
| 叶号意向 | **37**（叶36 inquiry HOLD CLOSED → 改派 A） |
| 上下文钉 | dig `74234fca`；叶36 HOLD WHO `feaa5dbb`；叶35 `.ok` `eb70eef4`；叶33 `afbbe7e7`；叶32 `45dd87dc` |
| gate_pass（轻量） | **true**（APPROX；见 COUNT） |
| live / promotion / ok_requested / EXECUTED_full_alpha | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
