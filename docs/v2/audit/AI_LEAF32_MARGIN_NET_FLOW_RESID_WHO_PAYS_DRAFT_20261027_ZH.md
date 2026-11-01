# 【DRAFT — NOT FROZEN】叶32 who_pays：HI_LIQ 个股净融资流入强度残差慢 α

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 03:39 ET（America/New_York；ISO `2026-10-27T03:39:49-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER 草稿；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁实跑**。
- 叶号意向：**叶32**（台账下一空号；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶23 SUE / 叶24 IMAX 预注册另轨 **不复开为本叶**；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud 冲击慢 已占轴）。
- 主令上下文：叶31 selfcheck Alpha **HOLD** `7ef5aa11`（selfcheck `d4553423`；CONSUME `fc7e712a`；A/B/current **全 false**；untradable=true；**DECAY_DOWNGRADE**；不派 Eng Book-Smoke）。构建闸 `a476567d` 不回撤；叶30 HOLD `f00536b9` 不回撤。本票 = 工厂续挖新叶，**盯 decay KEEP**。
- 禁：GP / 高杠杆 / 教科书主线当主轴；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮；复跑叶30/31 selfcheck；RESTORED/`forbid` 六票 `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；申 `.ok`；挂/抬 QUIET；抬 RSS；`0087c928`（叶30 KEEP 修复）另队不夹带。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED=false`；**≠X2 ACCEPT**。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_margin_net_flow_resid_v1`（叶32 意向）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内把「融资余额/净融入上升」当成无条件利好、忽视经 SW+style 残差后仍偏高的杠杆拥挤的交易者；高残差净融入名在再平衡后继续被杠杆追捧，低残差（或净融出）名被相对低估。  
> **可检验预测**：残差化后的 `α_raw = −rank(flow_resid)`（符号冻结时写死；DRAFT 默认惩罚高残差净融资流入=拥挤）对次期特质收益的截面 IC 符号在预注册**冻结时**写死（本 DRAFT **不**读收益选号）；活跃集 vs 叶19/25/27/30/31 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；覆盖 HI_LIQ 再平衡日可算 α 名数 median≥300（计数闸意向，本票只写契约不实跑）。  
> **失效条件**：退化为未残差融资余额排序或单纯杠杆动量；或与历史 `margin_delta`（Δrzye）近等权（Jaccard≥0.7）；或混入 hk_hold / northbound 换皮；或混入 Amihud/叶31 impact、叶27 on_minus_id、叶30 CRR/OCF、叶25 应计当主输入；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT。

---

## 1. 选型理由（PRIMARY = HI_LIQ 两融净流入微观，非质量/冲击复开）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | 本叶**零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶两融流 |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 本叶主轴是 **净融资买入强度**，**不是**隔夜−日内差的二阶矩 |
| 叶31 Amihud 冲击慢 | `|r|/amount` 冲击残差 | 本叶**不**读 Amihud/成交额冲击；主输入=两融 `rzmre−rzche` |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻；另轨不复开 |
| 叶23 SUE | 盈余意外 | 另轨不复开为本叶 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |
| 历史 `margin_delta` `g1g5_ashare_margin_delta_v1` | 全窗 **Δrzye** 存量边际 | 本叶主轴=**日净融资买入强度** `net_rz=rzmre−rzche` 短窗均值残差，**不是**融资余额差分；正交须披露 vs 该包 Jaccard/ρ |
| 北向 `northbound_flow` | 主臂 **hk_hold**；历史上两融仅作 hk 断档补窗且明文「非升格独立主叶」 | 本叶 **升格独立主轴=个股两融净流入残差**；**不**读 hk_hold；**不**叫 northbound 换皮 |

**PRIMARY 选定**：**HI_LIQ 个股净融资流入强度残差慢 α**。  
**备选（§12）**：（A）AlphaLens 技术/拥挤/状态复合分已有 DRAFT 另队；（B）异常换手在控制 |r| 与 Amihud 后的残差——仅备注，**不**升 PRIMARY。

---

## 2. 机制（两融微观；慢 α）

在 HI_LIQ 池、日频个股两融明细上定义短窗净融资流入强度：

\[
\mathrm{net\_rz}_{i,t} = \mathrm{rzmre}_{i,t} - \mathrm{rzche}_{i,t}
\]

\[
\mathrm{flow\_raw}_{i,t} = \frac{1}{W}\sum_{s=0}^{W-1} \frac{\mathrm{net\_rz}_{i,t-s}}{\mathrm{float\_mktcap}_{i,t-s-1}}
\]

- `rzmre` = 融资买入额（元）；`rzche` = 融资偿还额（元）；单位与源表一致。
- `float_mktcap_T-1` = 流通市值（元）T−1 PIT；≤0 或缺失 → 该日无效，不填 0。
- **缺/负成交额纪律（DRAFT）**：本叶主信号**不**用成交额作能量分母；若后续敏感性支路引入 ADV，则 amount≤0 或缺失 → 该日无效。两融字段：`rzmre`/`rzche` 任一缺失 → 该日 `net_rz` 无效；负值按源表如实保留（净融出可为负），**不**截断为 0。
- **W DRAFT=20** 交易日（最少有效日冻结时写死，建议 ≥15）；再平衡建议每 **20** 日（慢 α，对齐叶19/30/31 慢节奏）。
- PIT：两融行用 `available_at` as-of 再平衡日（严禁用未到 available_at 的行）。

**合成（DRAFT）**：

\[
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{flow\_resid})
\]

池内百分位 rank；再按残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。  
**符号纪律**：DRAFT 默认「残差净融资流入过高=拥挤，惩罚」；**冻结时写死符号**；本 DRAFT **不**读收益选号。

---

## 3. 残差规格（截面；缺则记 GAP）

同日截面、HI_LIQ 掩码后：

1. 原始：`flow_raw`（短窗净融资强度）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 T−1 PIT）。
4. vs **style 代理**（DRAFT：mom20、vol20、logADV20 / capacity_adv 暴露）— 冻结时写死清单；缺列 → PIN_GAP，勿静默跳过。
5. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 / 叶31 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）；另披露 vs 历史 `margin_delta` 包（强度过滤，建议同硬拒精神）。
6. **禁**把 Amihud/叶31 impact、叶27 `on_minus_id`、叶30 CRR/OCF、叶25 应计、hk_hold 当本叶主输入。

---

## 4. 数据 PIT（本拍仅 schema/路径核对；禁实算 α/收益）

| # | 输入 | 备注 |
|---|---|---|
| 1 | 个股两融日明细 | `data/v2/margin/margin_detail_daily_2018plus.parquet`；**schema 核对 2026-10-27**：行数 **5,786,686**；列含 `trade_date, ts_code, name, rzye, rzmre, rzche, rqye, rqmcl, rzrqye, rqyl, rqchl, available_at, available_at_tz, available_at_rule, promotion_approved`；**`available_at` 存在**（timestamp[us]）；PIT 用 `available_at` |
| 2 | 流通市值 T−1 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`（与叶31 默认一致；列 `instrument_id, trade_date, float_mktcap, …`；行数 **11,711,361**） |
| 3 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（HI_LIQ_V1.1；与叶31 一致） |
| 4 | SW L1 PIT | `data/v2/sw_l1_pit/…` |
| 5 | style 代理 | mom20 / vol20 / logADV20（bars+adj_price；冻结时写死路径） |
| 6 | 叶19/25/27/30/31 α parquet | **仅** Jaccard/ρ；不进主信号 |
| 7 | （披露）历史 margin_delta 权重 | `output/ai_factory/g1g5_margin_delta_daily_weights_*.parquet`；**仅**正交披露 |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造** 两融或市值。本拍**未** pgrep 实跑、**未** import 重计算 α。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主**（纸面路径）；**FULLA 研究**对照双钉意向（预注册须同时冻结两池规格，但 PRIMARY 判决 = HI_LIQ） |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09**（与叶25/30/31 对齐；冻结时写死） |
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
5. **decay KEEP 硬验收**（见 §7）。
6. Jaccard/ρ 硬拒意向 vs 叶19/25/27/30/31（§8）；符号冻结写死。

---

## 7. decay KEEP 设计（盯近端；对齐叶30/31 HOLD 教训）

叶30 HOLD `f00536b9`、叶31 HOLD `7ef5aa11` 根因均含 **DECAY_DOWNGRADE**（叶31：latest/A/B/current 全 false）。本叶设计时即把 KEEP 当硬验收，而非事后补丁：

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（年化；衰减门 v1.1 口径） |
| 连降 | **非连降 5 季**（衰减门 v1.1 季切点；冻结时写死） |
| H2 净 CAGR | **H2_net_cagr > 510300 净 CAGR**（同窗、同成本口径） |
| KEEP 合取 | `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；否则 selfcheck 截断为 **DOWNGRADE** |
| 近端窗定义 | 冻结时写死（建议：X2 后半 / 最近 ~1y 交易日；与 `alpha_decay_gate` H2 对齐） |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；**不派** Book-Smoke；≠X2 ACCEPT |
| 设计防衰减 | 慢再平衡（20d）+ 残差掉市值/行业/style（避免「融资追涨」近端反转）；禁快闸与慢 α 混装同一主规格 |

**风险**：HI_LIQ 内两融覆盖可能偏窄或净流入截面离散度不足 → 覆盖/IC 弱；若与 `margin_delta`/杠杆动量/moneyflow 近等权则硬拒。失败即截断，不事后改符号。

---

## 8. 正交硬闸（对齐叶30/31 count gate 精神）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → 强度过滤（披露） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 叶31 Amihud | 同上；禁 `|r|/amount` 冲击当主输入 |
| 历史 margin_delta / northbound | 披露 Jaccard/ρ；建议 Jaccard≥0.7 同硬拒精神；**禁** hk_hold |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300** |
| 换手/成本 | 成本 30bp；>20%/日或成本>毛超额一半 → 不可交易（冻结后评价） |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

---

## 9. 失败截断

- 计数闸 median<300 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs 叶19/25/27/30/31 → 硬拒，改机制或废叶
- 冻结前读收益选方向/W/λ → 违规，作废本草稿轮
- decay 非 KEEP（缺 latest>0 / 连降5季 / H2≤510300）或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT（未来执行窗）
- 误读 hk_hold / 误称 northbound 换皮 / 误用 Δrzye 当本叶主规格 → 废叶

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER DRAFT | 本文件 + audit COVER；**ok_requested=false**；**EXECUTED=false** |
| 主排号 | 请主确认叶号=32（或台账下一空号）并登记台账意向行 |
| Arch | **只审不签**（文档契约）；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED/碰旧 `.ok` 六票；禁复用叶25/27/30/31 `.ok` |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |
| 叶23/24 | 另轨 **不复开为本叶** |
| 叶30/31 | HOLD 不回撤；`0087c928` 另队；**禁**重跑 selfcheck |
| 叶30/31 衰减 KEEP 修复 | 可选另队，**不挡**本新叶 |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开；叶31 Amihud 复刻
- 历史 `margin_delta`（Δrzye）换皮当本叶主规格
- forbid 六票：`4bb141c9` / `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`
- 推 Leo；`live=true`；`promotion_approved=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）

| 备选 | 说明 |
|---|---|
| （A）AlphaLens 技术/拥挤/状态复合分 | 已有 DRAFT **另队**；本票不升 PRIMARY |
| （B）异常换手残差 | 在控制 \|r\| 与 Amihud 后的换手残差——仅备注；须另证 vs 叶31 低相关 |

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_margin_net_flow_resid_v1` |
| PRIMARY | HI_LIQ 个股净融资流入强度残差慢 α |
| 上下文钉 | 叶31 HOLD Alpha `7ef5aa11`；selfcheck `d4553423`；CONSUME `fc7e712a`；构建闸 `a476567d` 不回撤；叶30 HOLD `f00536b9` 不回撤 |
| forbid 六票 | `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
