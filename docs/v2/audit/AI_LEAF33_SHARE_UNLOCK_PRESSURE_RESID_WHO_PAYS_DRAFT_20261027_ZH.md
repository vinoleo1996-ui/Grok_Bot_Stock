# 【DRAFT — NOT FROZEN】叶33 who_pays：HI_LIQ 限售解禁压力残差慢 α

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 05:43 ET（America/New_York；ISO `2026-10-27T05:43:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER 草稿；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁实跑**。
- 叶号意向：**叶33**（台账下一空号；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶23 SUE / 叶24 IMAX 预注册另轨 **不复开为本叶**；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud / 叶32 `MARGIN_NET_FLOW_RESID` 已占轴）。
- 主令上下文：叶32 selfcheck Alpha **HOLD** `45dd87dc`（selfcheck `99675387`；CONSUME Arch `efa033e0`；门 A/B/current **总 false**；untradable=true；decay=**KEEP** 但仍 HOLD——**KEEP 不解阻** X2 ACCEPT；不派 Eng Book-Smoke）。构建闸 `1aa432a5` 不回撤；叶31 HOLD `7ef5aa11` / 叶30 HOLD `f00536b9` 不回撤。本票 = 工厂续挖新叶，**盯 decay KEEP 且组合闸有过关路径**（叶32 KEEP 仍总 false —— 本叶选慢供给冲击、避免高换手微观追逐，**意图**改善可交易性；如实写意图，**勿宣称已过闸**）。
- 禁：GP / 高杠杆 / 教科书主线当主轴；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮；margin/Amihud 换皮；复跑叶30/31/32 selfcheck；禁改构建 `4e0f3c00` / selfcheck `dcf6b559` / 叶30 `3ee9fed2` / 叶31 `08f37fd2`；RESTORED/`forbid` **二十票齐** + 主令新增 `5774bb6e`（点名见 §11）；申 `.ok`；挂/抬 QUIET；抬 RSS；`0087c928`（叶30 KEEP 修复）另队不夹带。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_share_unlock_pressure_resid_v1`（叶33 意向）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内低估「即将/刚发生的限售解禁供给冲击」经 SW+style 残差后的抛压错配者——高残差解禁压力名在再平衡后继续被供给冲击压价，低压力名相对不吃供给冲击。  
> **可检验预测**：残差化后的 `α_raw = −rank(pressure_resid)`（符号冻结时写死；DRAFT 默认惩罚高解禁压力=供给冲击）对次期特质收益的截面 IC 符号在预注册**冻结时**写死（本 DRAFT **不**读收益选号）；活跃集 vs 叶19/25/27/30/31/32 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；覆盖 HI_LIQ 再平衡日可算 α 名数 median≥300（计数闸意向，本票只写契约不实跑）。  
> **失效条件**：退化为未残差解禁规模排序或单纯事件日历动量；或与叶32 两融净流入 / 叶31 Amihud / 叶27 on_minus_id / 叶30 CRR / 叶25 应计近等权（Jaccard≥0.7）；或混入 hk_hold / northbound / moneyflow / margin 换皮；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差；或用 `available_at > t` 的未来解禁公告偷看。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT。

---

## 1. 选型理由（PRIMARY = HI_LIQ 限售解禁供给冲击残差，非两融/冲击/会计复开）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | 本叶**零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶解禁供给 |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 本叶主轴是 **限售解禁压力**，**不是**隔夜−日内差的二阶矩 |
| 叶31 Amihud 冲击慢 | `\|r\|/amount` 冲击残差 | 本叶**不**读 Amihud/成交额冲击；主输入=解禁 `float_share` / 流通市值 |
| 叶32 `MARGIN_NET_FLOW_RESID` | 两融净融资流入强度残差 | 本叶**不**读 `rzmre/rzche/rzye`；主轴=股本解禁日历供给冲击（已 HOLD `45dd87dc`；同构禁复开） |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻；另轨不复开 |
| 叶23 SUE | 盈余意外 | 另轨不复开为本叶 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |
| 叶28 LLM / 叶29 tech_crowd | 另队 FROZEN / AlphaLens | **不夹带、不升本叶 PRIMARY** |
| 北向 / moneyflow / margin_delta | 资金流换皮 | 本叶 **升格独立主轴=限售解禁压力残差**；**不**读 hk_hold / moneyflow / 两融 |

**PRIMARY 选定**：**HI_LIQ 限售解禁压力残差慢 α**。  
**备选（§12）**：（A）异常换手残差（控\|r\|+Amihud）——叶32 §12-B；须另证 vs 叶31 低相关；本票不升；（B）AlphaLens tech_crowd / 叶29——另队已有 DRAFT/排号；本票不夹带不升。

---

## 2. 机制（解禁供给冲击；慢 α）

在 HI_LIQ 池、个股限售解禁 PIT 事件上定义短窗解禁压力：

对每个再平衡日 \(t\)，取事件集：

\[
\mathcal{E}_{i,t} = \{e:\; \mathrm{available\_at}_e \le t \;\wedge\; \bigl(\mathrm{float\_date}_e \in [t,\, t+H] \;\vee\; \mathrm{float\_date}_e \in [t-H_{\mathrm{back}},\, t]\bigr)\}
\]

日度原始压力（按交易日聚合事件）：

\[
\mathrm{unlock\_raw}_{i,d} = \frac{\sum_{e:\,\mathrm{float\_date}_e=d} \mathrm{float\_share}_e}{\mathrm{float\_mktcap}_{i,d-1}}
\]

短窗：

\[
\mathrm{pressure\_raw}_{i,t} = \frac{1}{W}\sum_{s=0}^{W-1} \mathrm{unlock\_raw}_{i,t-s}
\]

- **主输入钉**：`data/v2/share_float/share_float_pit.parquet`（**6,449,659** 行；列：`ts_code, ann_date, float_date, float_share, float_ratio, holder_name, share_type, available_at[Asia/Shanghai], availability_basis, source, quality_status, promotion_approved`）。sidecar `share_float_2015_2017.parquet` / `share_float_2018plus.parquet` / manifest **不**作主输入。
- **H DRAFT=20** 交易日前瞻窗；**H_back DRAFT=5**（近窗已发生解禁）；冻结时写死。
- **W DRAFT=20** 交易日短窗均值；最少有效日建议 ≥15（冻结时写死）。
- **分母**：`float_mktcap_T-1` = `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`；缺/≤0 → 该日无效，**不填 0**。
- **`float_ratio` 单位纪律（PIN_GAP）**：表内 `float_ratio` 分布混杂（多数 ∈(0,1]，亦有 >1 至 ~91）——**单位未核死**（百分比点 vs 流通比分数）。**DRAFT 默认主路径 = `sum(float_share)/float_mktcap_T-1`**；若冻结前核死 `float_ratio` 已是「占流通比」且单位一致，可改用表内 ratio（须 COVER/FROZEN 写清选哪、单位核对纪律）。**勿静默混用**。
- PIT：解禁行用 `available_at` as-of 再平衡日（严禁用未到 `available_at` 的行；manifest：`ann_date 18:00 Asia/Shanghai`）。
- 再平衡建议每 **20** 日（慢 α，对齐叶19/30/31/32 慢节奏；意图降低换手、改善可交易性相对叶32 微观追逐——**仅意图，未宣称过闸**）。

**合成（DRAFT）**：

\[
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{pressure\_resid})
\]

池内百分位 rank；再按残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。  
**符号纪律**：DRAFT 默认「高残差解禁压力=供给冲击，惩罚」；**冻结时写死符号**；本 DRAFT **不**读收益选号。

---

## 3. 残差规格（截面；缺则记 GAP）

同日截面、HI_LIQ 掩码后：

1. 原始：`pressure_raw`（短窗解禁压力）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 T−1 PIT）。
4. vs **style 代理**（DRAFT：mom20、vol20、logADV20 / capacity_adv 暴露）— 冻结时写死清单；缺列 → PIN_GAP，勿静默跳过。
5. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 / 叶31 / 叶32 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）。
6. **禁**把两融/叶32 flow、Amihud/叶31 impact、叶27 `on_minus_id`、叶30 CRR/OCF、叶25 应计、hk_hold、moneyflow 当本叶主输入。

---

## 4. 数据 PIT（本拍仅 schema/路径核对；禁实算 α/收益）

| # | 输入 | 备注 |
|---|---|---|
| 1 | 限售解禁 PIT | `data/v2/share_float/share_float_pit.parquet`；**schema 核对 2026-10-27**：行数 **6,449,659**；`available_at` 存在（timestamp[us, tz=Asia/Shanghai]）；float_date 覆盖约 2015→2026-10-30；ann_date 约 2005→2026-10-10；`promotion_approved=false`（manifest research_grade） |
| 2 | 流通市值 T−1 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`（与叶31/32 默认一致） |
| 3 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（HI_LIQ_V1.1；与叶31/32 一致） |
| 4 | SW L1 PIT | `data/v2/sw_l1_pit/…` |
| 5 | style 代理 | mom20 / vol20 / logADV20（bars+adj_price；冻结时写死路径） |
| 6 | 叶19/25/27/30/31/32 α parquet | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造** 解禁或市值。`float_ratio` 单位 → **PIN_GAP**（见 §2）。本拍**未** pgrep 实跑、**未** import 重计算 α。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主**（纸面路径）；**FULLA 研究**对照双钉意向（预注册须同时冻结两池规格，但 PRIMARY 判决 = HI_LIQ） |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09**（与叶25/30/31/32 对齐；冻结时写死） |
| 再平衡 | DRAFT **20** 交易日 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 base-α 向量** → 优化器；非 Top-N 当闸 |
| rss 意向 | **1500** MB 禁抬；peak_proof REQUIRED（脚本阶段再钉） |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. **截面残差**：SW L1 + style（上表清单）。
2. **HI_LIQ 判决**为主；FULLA 仅研究披露。
3. **walk-forward** 分段披露（冻结时钉切点；本 DRAFT 不跑）。
4. **Gate B / GATE_V3** 评价清单；衰减门 v1.1。
5. **decay KEEP 硬验收**（见 §7）；**组合闸有过关路径**须在冻结规格中可检验（本 DRAFT 只写意图/契约）。
6. Jaccard/ρ 硬拒意向 vs 叶19/25/27/30/31/32（§8）；符号冻结写死；`float_ratio` 单位核死或弃用。

---

## 7. decay KEEP 设计（盯近端；对齐叶30/31/32 HOLD 教训）

叶30 HOLD `f00536b9`、叶31 HOLD `7ef5aa11` 根因含 **DECAY_DOWNGRADE**；叶32 HOLD `45dd87dc` 则 **decay=KEEP 但仍** 门 A/B/current 总 false / untradable=true——**KEEP 不解阻** X2 ACCEPT。本叶设计时同时盯 KEEP **与**组合闸路径：

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（年化；衰减门 v1.1 口径） |
| 连降 | **非连降 5 季**（衰减门 v1.1 季切点；冻结时写死） |
| H2 净 CAGR | **H2_net_cagr > 510300**（同窗、同成本口径；近端=252d 意向） |
| KEEP 合取 | `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；否则 selfcheck 截断为 **DOWNGRADE** |
| 组合闸路径（意图） | 慢再平衡（20d）+ 事件日历供给冲击（非高换手微观追逐）→ **意图**降低 untradable / 改善 Gate A·B·current 过关可能；**如实写意图，勿宣称已过闸** |
| 近端窗定义 | 冻结时写死（建议：X2 后半 / 最近 ~252 交易日；与 `alpha_decay_gate` H2 对齐） |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；**不派** Book-Smoke；≠X2 ACCEPT |
| 设计防衰减 | 慢再平衡 + 残差掉市值/行业/style（避免「解禁惊吓」近端反转噪声主导）；禁快闸与慢 α 混装同一主规格 |

**风险**：解禁事件截面稀疏 → 覆盖/IC 弱；`float_ratio` 单位错用 → 尺度污染；若与两融/冲击/会计近等权则硬拒。失败即截断，不事后改符号。

---

## 8. 正交硬闸（对齐叶30/31/32 count gate 精神）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → 强度过滤（披露） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 叶31 Amihud | 同上；禁 `\|r\|/amount` 冲击当主输入 |
| 叶32 MARGIN_NET_FLOW_RESID | 同上；禁 `rzmre/rzche/rzye` / 两融净流入当主输入 |
| 北向 / moneyflow / margin_delta | 披露 Jaccard/ρ；建议 Jaccard≥0.7 同硬拒精神；**禁** hk_hold / moneyflow 80/20 |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300** |
| 换手/成本 | 成本 30bp；>20%/日或成本>毛超额一半 → 不可交易（冻结后评价） |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

---

## 9. 失败截断

- 计数闸 median<300 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs 叶19/25/27/30/31/32 → 硬拒，改机制或废叶
- 冻结前读收益选方向/W/λ → 违规，作废本草稿轮
- decay 非 KEEP（缺 latest>0 / 连降5季 / H2≤510300）或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT（未来执行窗）
- 误读 hk_hold / 两融 / Amihud / 偷看 `available_at>t` / 静默混用未核死 `float_ratio` → 废叶

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER DRAFT | 本文件 + audit COVER；**ok_requested=false**；**EXECUTED=false** |
| 主排号 | 请主确认叶号=33（或台账下一空号）并登记台账意向行 |
| Arch | **只审不签**（文档契约）；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED/`forbid` 二十票齐 + `5774bb6e`；禁复用叶25/27/30/31/32 `.ok` |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN**；不夹带不升 |
| 叶23/24 | 另轨 **不复开为本叶** |
| 叶30/31/32 | HOLD 不回撤；`0087c928` 另队；**禁**重跑 selfcheck；禁改 `4e0f3c00`/`dcf6b559`/`3ee9fed2`/`08f37fd2` |
| 叶30 KEEP 修复 / 叶32 组合闸修复 | 可选另队，**不挡**本新叶 |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮；margin/Amihud 换皮
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开；叶31 Amihud 复刻；叶32 两融净流入复刻
- 禁改构建脚本 `4e0f3c00` / selfcheck `dcf6b559` / 叶30 `3ee9fed2` / 叶31 `08f37fd2`
- `0087c928` 另队不夹带
- **RESTORED / forbid 二十票齐**（Arch 叶32 selfcheck 清单）+ **主令新增** `5774bb6e`（叶32 selfcheck CONSUMED）：
  - 主令点名：`5774bb6e`, `02426b73`, `4bb141c9`, `fdbaa512`, `aa25e989`, `7e239487`, `5af20222`, `5ae077fa`
  - 二十票全集 sha8：`02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
  - 本叶禁 RESTORED 合取：`5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`（二十票 + `5774bb6e`）
- 推 Leo；`live=true`；`promotion_approved=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）

| 备选 | 说明 |
|---|---|
| （A）异常换手残差（控\|r\|+Amihud） | 叶32 §12-B；须另证 vs 叶31 低相关；**本票不升** |
| （B）AlphaLens tech_crowd / 叶29 | 另队已有 DRAFT/排号；**本票不夹带不升** |

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_share_unlock_pressure_resid_v1` |
| PRIMARY | HI_LIQ 限售解禁压力残差慢 α |
| 上下文钉 | 叶32 HOLD Alpha `45dd87dc`；selfcheck `99675387`；CONSUME Arch `efa033e0`；构建闸 `1aa432a5` 不回撤；叶31 HOLD `7ef5aa11` / 叶30 HOLD `f00536b9` 不回撤 |
| forbid | 二十票齐 + `5774bb6e`（见 §11） |
| PIN_GAP | `float_ratio` 单位未核死 → DRAFT 主路径用 `float_share/float_mktcap` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
