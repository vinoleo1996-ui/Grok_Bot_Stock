# 【FROZEN 预注册 2026-10-27 03:50 ET】叶32：HI_LIQ 净融资流入强度残差慢 α（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 03:50 ET**（America/New_York；ISO `2026-10-27T03:50:00-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 W/方向/符号。
- 主令：2026-10-27 ~03:47 ET — Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`84df02b5`** → 令 AI 出 FROZEN 预注册（C1–C9 入钉）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`84df02b5`**（全长 `84df02b5ddfd10314bf8bc95acdf931d12ba9e53e43dd318e61fdc85b7b6fb01`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`fad5911e`**（全长 `fad5911eec855a3b77d77971f8d44241798bfa4355adebd3f14aa67910fc6c44`）
  - COVER DRAFT：`docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` sha8 **`ebda2603`**（全长 `ebda2603283198382c7225924f4105d9ec9891acad3ba83a022a2172a1dac9fc`）
- 对照形态：叶31 PREREG_FROZEN `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_20261027_ZH.md`（结构对齐；内容换叶32）。
- 叶号：**叶32**（主 03:41 ET 确认）；mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶30 HOLD `f00536b9` / 叶31 HOLD `7ef5aa11` **不回撤**（只读对照）；构建闸 `a476567d` 不回撤。
- **本冻结 ≠ `.ok` / ≠ 构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无脚本**（`research/leaf32*` ABSENT 预期）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_margin_net_flow_resid_v1`（叶32）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内把「融资余额/净融入上升」当成无条件利好、忽视经 SW+style 残差后仍偏高的杠杆拥挤的交易者；高残差净融入名在再平衡后继续被杠杆追捧，低残差（或净融出）名被相对低估。  
> **可检验预测（已冻结）**：`α_raw = −rank(flow_resid)` 对**次期特质收益**的截面 IC **期望为正**（高 α = 低残差净融资流入=低拥挤 → 更高次期特质收益；**冻结前未读本叶收益选号**）；活跃集 vs 叶19/25/27/30/31 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另须披露 vs 历史 `margin_delta`（Δrzye）；HI_LIQ 再平衡日可算 α 名数 median≥300；FULLA 研究对照 median≥800。  
> **失效条件**：退化为未残差融资余额排序或单纯杠杆动量；或与历史 `margin_delta`（Δrzye）近等权（Jaccard≥0.7）；或混入 hk_hold / northbound 换皮；或混入 Amihud/叶31 impact、叶27 on_minus_id、叶30 CRR/OCF、叶25 应计当主输入；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差；或把 FULLA 研究对照静默改作 PRIMARY 判决。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（两融微观；慢 α）— **FROZEN**

在 PRIMARY 池（HI_LIQ）日频个股两融明细上定义短窗净融资流入强度：

$$
\mathrm{net\_rz}_{i,t} = \mathrm{rzmre}_{i,t} - \mathrm{rzche}_{i,t}
$$

$$
\mathrm{flow\_raw}_{i,t} = \frac{1}{W}\sum_{s=0}^{W-1} \frac{\mathrm{net\_rz}_{i,t-s}}{\mathrm{float\_mktcap}_{i,t-s-1}}
$$

| 项 | **FROZEN** |
|---|---|
| `rzmre` | 融资买入额（元）；与源表单位一致 |
| `rzche` | 融资偿还额（元） |
| `net_rz` | `rzmre − rzche`（元；可为负=净融出）；**不**截断为 0 |
| `float_mktcap_T-1` | 流通市值（元）**T−1 PIT**；≤0 或缺失 → 该日**无效**，不填 0 |
| 两融缺值纪律 | `rzmre`/`rzche` **任一缺失** → 该日 `net_rz` **无效** |
| PIT | 两融行用 **`available_at`** as-of 再平衡日（严禁用未到 `available_at` 的行） |
| **W** | **20** 交易日 |
| 最少有效日 | 窗内有效日 **≥15**，否则该票该再平衡日无效 |
| 再平衡 | 每 **20** 交易日（慢 α；对齐叶19/30/31 慢节奏） |
| 主定义 | 上式 `flow_raw`（短窗净融资买入强度 / 流通市值） |

**合成（FROZEN）**：

$$
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{flow\_resid})
$$

池内百分位 rank；再按 §3 残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。

**边界（FROZEN）**：≠northbound/hk_hold 换皮；≠Δrzye `margin_delta` 复刻（`margin_delta` **仅**正交披露）；≠Amihud/叶31 impact；≠叶27 `on_minus_id`；≠叶30 CRR/应计/会计主轴。

---

## 2. 方向 / 符号（已冻结；禁事后切换）

| 项 | **FROZEN** |
|---|---|
| 主规格 | `α_raw = −rank(flow_resid)`：惩罚高残差净融资流入=拥挤；低残差（或净融出）优先 |
| **IC 符号** | 对**次期特质收益**的截面 IC **期望为正**（事先机制：低残差净融资流入 → 正超额；**冻结前未读本叶收益**） |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改符号、改 W、改再平衡周期，或改为奖励高 `flow_resid` |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选方向 |

---

## 3. 残差清单（C4 — 冻结最低集；缺列→PIN_GAP）

同日截面、PRIMARY 掩码（HI_LIQ）后：

1. 原始：`flow_raw = mean_W((rzmre−rzche)/float_mktcap_T−1)`（§1 主定义）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 **T−1 PIT**）。
4. vs **style 代理（写死）**：
   - `mom20`
   - `vol20`
   - `logADV20`（或等价 `capacity_adv` 暴露；脚本须在回执钉所用列名；**二者择一并钉死，不得事后换**）
5. **缺列 → PIN_GAP**：勿静默跳过；后加正交项须**补丁文件**，不得静默改本钉。
6. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 / 叶31 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）；**另须披露 vs 历史 `margin_delta`（Δrzye）**（C3）。
7. **禁**把 Amihud/叶31 impact、叶27 `on_minus_id`/overnight ε、叶30 CRR/OCF、叶25 应计、hk_hold 当本叶主输入。

---

## 4. 正交硬闸（C3 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **强度过滤**（披露，不单独硬拒） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 叶31 Amihud | 同上；禁 `|r|/amount` 冲击当主输入 |
| 历史 `margin_delta`（Δrzye） | **须披露** Jaccard/ρ；Jaccard≥0.7 → **硬拒**（同精神）；本叶主轴 ≠ Δrzye 存量边际 |
| 北向 / hk_hold | **禁** hk_hold 进主信号；≠northbound 换皮 |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300**；FULLA 研究 **median≥800** |
| 换手/成本 | 评价口径 **30bp**；>20%/日或成本>毛超额一半 → 不可交易（X2 后评价） |
| 正式重叠 | **X2 前须用完整 α 重算** vs 叶19/25/27/30/31 的 Jaccard/ρ，**另须披露 vs margin_delta**；who_pays DRAFT 硬拒意向**不能替**正式重叠证明（C3） |

---

## 5. 宇宙双钉（C5 — HI_LIQ 主判决 + FULLA 研究）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决**（纸面路径） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | median≥**300** |
| **FULLA_V1** | **研究对照**（仅披露；不得静默改 PRIMARY） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | median≥**800** |

- 评价书行业帽意向（与叶25 族对齐，供将来脚本钉）：HI_LIQ **25%** / FULLA **28%**（本预注册不跑评价）。
- **PRIMARY 不得静默改 FULLA**；FULLA 读数仅研究披露，不单独解阻 X2 ACCEPT。

---

## 6. 窗 / 再平衡 / 交付 / rss（C8）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗 | **2024-06-03 → 2026-10-09**（与叶25/30/31 对齐） |
| W / 再平衡 | **20 / 20** 交易日 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 base-α 向量**（HI_LIQ 主 + FULLA 研究）；非 Top-N 当闸 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED**（未来 execute 回执须含 peak 证明：sampler / ru_maxrss / meta 等 Arch 惯用口径） |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C6 — 对齐 `alpha_decay_gate` v1.1 + 叶30/31 HOLD 教训）

叶30 HOLD `f00536b9`、叶31 HOLD `7ef5aa11` 根因均含 **DECAY_DOWNGRADE**。本叶把 KEEP 三闸合取写死：

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `research/alpha_decay_gate` / `alpha_decay_gate_v1_1` **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT 规则；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1 口径：对 510300 去 β 后截距×252） |
| 连降 | **非连降 5 季**（衰减门 v1.1 季切点） |
| H2 净 CAGR | **`H2_net_cagr > 510300` 净 CAGR**（同近端 252 日窗、同成本口径；严格优于基准） |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**满足才可谈 KEEP；任一条不满足 → **最多 WATCH / HOLD** |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改符号/W 救闸 |
| 设计防衰减 | 慢再平衡（20d）+ 残差掉市值/行业/style（避免「融资追涨」近端反转）；禁快闸与慢 α 混装同一主规格 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | 个股两融日明细 | `data/v2/margin/margin_detail_daily_2018plus.parquet`（who_pays 已核：5,786,686 行；列含 `rzmre/rzche/available_at`）；PIT=`available_at` |
| 2 | 流通市值 T−1 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`（who_pays 已核：11,711,361 行；列含 `float_mktcap`） |
| 3 | HI_LIQ 掩码 | PRIMARY（§5） |
| 4 | FULLA 掩码 | 研究对照（§5） |
| 5 | SW L1 PIT（`data/v2/sw_l1_pit/…`） | 残差 demean |
| 6 | mom20 / vol20 / logADV20（或钉死的 capacity_adv 暴露） | style 残差（§3）；缺列→PIN_GAP |
| 7 | 叶19 / 叶25 / 叶27 / 叶30 / 叶31 α parquet | **仅** Jaccard/ρ；不进主信号 |
| 8 | （披露）历史 margin_delta 权重 | `output/ai_factory/g1g5_margin_delta_daily_weights_*.parquet`；**仅**正交披露 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造** 两融或市值。本拍**未**实算 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | **零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶**两融净流入** |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 主轴是 **净融资买入强度**，**不是**隔夜−日内差的二阶矩 |
| 叶31 Amihud 冲击慢 | `|r|/amount` 冲击残差 | 本叶**不**读 Amihud/成交额冲击；主输入=`rzmre−rzche` |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |
| 历史 `margin_delta` `g1g5_ashare_margin_delta_v1` | 全窗 **Δrzye** 存量边际 | 本叶主轴=**日净融资买入强度**短窗均值残差，**不是**融资余额差分；正交须披露 |
| 北向 `northbound_flow` | 主臂 **hk_hold** | 本叶 **不**读 hk_hold；**不**叫 northbound 换皮 |

**一句话分家**：叶25/30=会计应计·CRR；叶27=隔夜−日内 idio 波动；叶31=Amihud 冲击；叶32=**HI_LIQ 短窗净融资流入强度经 SW+style 残差后的慢 α（−rank）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C7）

forbid∋ 下列 sha8（**六票**；**禁 RESTORED / 禁复用** 作本叶流程门或自开跑）：

| sha8 | 备注 |
|---|---|
| `4bb141c9` | 叶31 X2 selfcheck `.ok`（已 CONSUMED） |
| `fdbaa512` | 叶31 X2 构建 `.ok`（已 CONSUMED） |
| `aa25e989` | 叶30 X2 selfcheck `.ok`（已 CONSUMED） |
| `7e239487` | 禁复用旧窗 |
| `5af20222` | 禁复用旧窗 |
| `5ae077fa` | 禁复用旧窗 |

另禁：
- 复用叶25 / 叶27 / 叶30 / 叶31 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开（对齐叶30 selfcheck P0 教训）
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS

---

## 11. 叶30 KEEP 修复另队（C9）

- 叶30 衰减 KEEP 修复 DRAFT sha8 **`0087c928`**：**另队**；**不并入**本 FROZEN；不得借本冻结窗口夹带签跑/改叶30 CONSUMED 产物。
- 本拍**未打开/未审** `0087c928`（对齐 Arch `84df02b5` §10 / C9）。
- 叶30/31 衰减 KEEP 修复可选另队，**不挡**本新叶。

---

## 12. 失败截断

- 覆盖闸 HI_LIQ median<300 或 FULLA median<800 → 不申 `.ok` / 不宣称可交易
- Jaccard≥0.7 vs 叶19/25/27/30/31（或 vs 历史 margin_delta）→ 硬拒，改机制或废叶
- 冻结后读收益改方向/W/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP（`latest_resid_alpha≤0` 或连降5季 或 `H2_net_cagr≤510300`）或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT（未来执行窗）；无 peak_proof → 回执不完整
- 误读 hk_hold / 误称 northbound 换皮 / 误用 Δrzye 当本叶主规格 → 废叶

---

## 13. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT fad5911e + COVER ebda2603
  → Arch PASS_WITH_CONDITIONS 84df02b5
      → 【本文件】PREREG_FROZEN（C1：另窗相对 DRAFT 升格）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf32_*（C2：本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED；禁复用叶25/27/30/31；forbid 六票）
                          → X2（完整 α；重叠重算含 vs margin_delta；decay KEEP 硬验收）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| `research/leaf32*` 构建脚本 | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| 叶30 KEEP `0087c928` | **另队不并入**（C9） |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |
| 叶30 HOLD `f00536b9` / 叶31 HOLD `7ef5aa11` | **不回撤**（只读对照） |

---

## 14. 禁项清单（再钉）

- 本拍实跑 / 申 `.ok` / 落构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid 六票 `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- 冻结后改 α 符号 / W / 再平衡；读收益翻号
- 卖方/金股/survey/TP/LLM 权重当 α；GP/高杠杆；moneyflow 80/20 叠仓
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开；叶31 Amihud 复刻
- Δrzye `margin_delta` 换皮当本叶主规格；hk_hold / northbound 换皮
- PRIMARY 静默改 FULLA；把研究对照当判决
- 并入叶30 KEEP `0087c928`；重跑叶30/31 selfcheck
- `live=true` / `promotion_approved=true` / 声称 X2 ACCEPT / 报 Leo

---

## 15. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` |
| 状态 | **FROZEN**（PREREG_FROZEN） |
| mechanism_tag | `g1g5_ashare_margin_net_flow_resid_v1` |
| W / 再平衡 / 最少有效日 | **20 / 20 / ≥15** |
| α 符号 | **−rank(flow_resid)**；IC 对次期特质收益期望为正 |
| X2 窗 | **2024-06-03 → 2026-10-09** |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| 残差 | SW L1 + log 流通市值 + mom20/vol20/logADV20（或钉死 capacity_adv） |
| decay KEEP | latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端=252d（gate v1.1） |
| forbid 六票 | `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |
| rss / peak_proof | 1500 / REQUIRED |
| C9 | `0087c928` 另队 |
| Arch / WHO_PAYS / COVER | `84df02b5` / `fad5911e` / `ebda2603` |
| 上下文 HOLD | 叶31 `7ef5aa11` / 构建闸 `a476567d` / 叶30 `f00536b9`（不回撤） |
| ok_requested / EXECUTED / 脚本本拍 | false / false / 无 |
| live / promotion / ≠X2 ACCEPT / leo_notify | false / false / true / false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
