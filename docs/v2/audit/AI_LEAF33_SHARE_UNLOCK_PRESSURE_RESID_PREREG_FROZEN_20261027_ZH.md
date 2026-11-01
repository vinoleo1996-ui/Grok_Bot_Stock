# 【FROZEN 预注册 2026-10-27 05:54 ET】叶33：HI_LIQ 限售解禁压力残差慢 α（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 05:56 ET**（America/New_York；ISO `2026-10-27T05:56:15-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 W/方向/符号。
- 主令：2026-10-27 ~05:52 ET — Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`55531e12`** → 令 AI 出 FROZEN 预注册（C1–C10 入钉）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`55531e12`**（全长 `55531e129e89077e9390a45c2f1310d5e2a80421ff6d16927b46bbaf1a7ee3c5`）
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`1032477d`**（全长 `1032477d54c9c2c4b0bc4398066d76d852369d9187f3ff3e7c7610953c086075`）
  - COVER DRAFT：`docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` sha8 **`61d9f656`**（全长 `61d9f656b8dcfa686f512f92637c884ab3029dfd523956bda4d2bfbbf70c5f70`）
  - PIN 决议：`docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` sha8 **`4e17ccfc`**（全长 `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75`；选径 **(a)**，本 FROZEN 升级为 **(a)+加价** 以满足同口径无量纲）
- 对照形态：叶32 PREREG_FROZEN `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md`（结构对齐；内容换叶33）。
- 叶号：**叶33**（主 05:47 ET 确认）；mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶30 HOLD `f00536b9` / 叶31 HOLD `7ef5aa11` / 叶32 HOLD `45dd87dc`（selfcheck `99675387`；CONSUME Arch `efa033e0`；构建闸 `1aa432a5`）**不回撤**（只读对照）。
- **本冻结 ≠ `.ok` / ≠ 构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无脚本**（`research/leaf33*` ABSENT 预期）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_share_unlock_pressure_resid_v1`（叶33）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内低估「即将/刚发生的限售解禁供给冲击」经 SW+style 残差后的抛压错配者——高残差解禁压力名在再平衡后继续被供给冲击压价，低压力名相对不吃供给冲击。  
> **可检验预测（已冻结）**：`α_raw = −rank(pressure_resid)` 对**次期特质收益**的截面 IC **期望为正**（高 α = 低残差解禁压力 → 更高次期特质收益；**冻结前未读本叶收益选号**）；活跃集 vs 叶19/25/27/30/31/32 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另须披露 vs 历史 margin_delta / hk_hold / moneyflow；HI_LIQ 再平衡日可算 α 名数 median≥300；FULLA 研究对照 median≥800。  
> **失效条件**：退化为未残差解禁规模排序或单纯事件日历动量；或与叶32 两融净流入 / 叶31 Amihud / 叶27 on_minus_id / 叶30 CRR / 叶25 应计近等权（Jaccard≥0.7）；或混入 hk_hold / northbound / moneyflow / margin 换皮；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差；或用 `available_at > t` 的未来解禁公告偷看；或 PRIMARY 静默混用表内 `float_ratio`；或把 FULLA 研究对照静默改作 PRIMARY 判决。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（限售解禁供给冲击；慢 α）— **FROZEN**

在 PRIMARY 池（HI_LIQ）个股限售解禁 PIT 事件上定义短窗解禁压力。

对每个再平衡日 \(t\)，取事件集：

$$
\mathcal{E}_{i,t} = \{e:\; \mathrm{available\_at}_e \le t \;\wedge\; \bigl(\mathrm{float\_date}_e \in [t,\, t+H] \;\vee\; \mathrm{float\_date}_e \in [t-H_{\mathrm{back}},\, t]\bigr)\}
$$

### 1.1 C3 量纲（PIN_GAP=`float_ratio` — 选径 (a)+加价；PRIMARY 禁用表内 ratio）

PIN 决议 **`4e17ccfc`** 选径 **(a)**：主路径基于 `float_share`，**非**表内 `float_ratio`。  
Arch C3（`55531e12`）要求：若 `float_share`（股）与 `float_mktcap`（元）不同量纲，须**改公式或加价**，**勿静默**。  
本 FROZEN **升级为 (a)+加价**（不是改用 (b)）：

$$
\mathrm{unlock\_mv}_{i,t} = \sum_{j \in \mathcal{E}_{i,t}} \mathrm{float\_share}_{i,j} \times \mathrm{close}_{i,T-1}
$$

$$
\mathrm{unlock\_raw}_{i,t} = \frac{\mathrm{unlock\_mv}_{i,t}}{\mathrm{float\_mktcap}_{i,T-1}}
$$

$$
\mathrm{pressure\_raw}_{i,t} = \mathrm{mean}_W(\mathrm{unlock\_raw}_{i,\cdot}) \quad (W=20)
$$

| 项 | **FROZEN** |
|---|---|
| `float_share` | `data/v2/share_float/share_float_pit.parquet`；单位钉 **股**；事件 j 满足 `available_at≤t` 且 `float_date ∈ [t−H_back, t+H]`（即 ∈ \(\mathcal{E}_{i,t}\)） |
| `close_{T−1}` | 收盘价（**元/股**）。脚本须钉所用价列（建议与叶32/bars 契约一致的 **不复权收盘价元**，或仓库标准 adj close）；**二者择一不得事后换**；回执披露所选列名 |
| `unlock_mv` | `Σ float_share × close_T−1`（元；同口径市值量纲） |
| `float_mktcap_T−1` | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`；单位钉 **元**（对齐叶32 FROZEN）；≤0 或缺失 → 该日**无效**，不填 0 |
| `unlock_raw` | `unlock_mv / float_mktcap_T−1`（**无量纲**；同口径） |
| close 缺失 | 该事件/该日**无效**，不填 0 |
| **表内 `float_ratio`** | **PRIMARY 禁用**（不得静默混用；不得作主信号能量）；可选披露对照默认 **OFF**；对照失败不影响主路径 |
| 说明 | 由 PIN `4e17ccfc` 升级为加价公式以满足同口径无量纲；**不是**改用 (b) 表内 ratio |

### 1.2 窗参 / 合成

| 项 | **FROZEN** |
|---|---|
| **H** | **20** 交易日（前瞻：`float_date ∈ [t, t+H]`） |
| **H_back** | **5** 交易日（近窗已发生：`float_date ∈ [t−H_back, t]`） |
| **W** | **20** 交易日 |
| 最少有效日 | 窗内有效日 **≥15**，否则该票该再平衡日无效 |
| 再平衡 | 每 **20** 交易日（慢 α；对齐叶19/30/31/32 慢节奏） |
| PIT | 解禁行用 **`available_at ≤ t`** as-of 再平衡日；**严禁**用未到 `available_at` 的未来公告 |
| 主定义 | 上式 `pressure_raw`（短窗无量纲解禁压力） |

**合成（FROZEN）**：

$$
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{pressure\_resid})
$$

池内百分位 rank；再按 §3 残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。

**边界（FROZEN）**：≠northbound/hk_hold 换皮；≠叶32 两融净流入复刻；≠Amihud/叶31 impact；≠叶27 `on_minus_id`；≠叶30 CRR/应计/会计主轴；≠moneyflow 80/20；≠表内 `float_ratio` 当 PRIMARY。

---

## 2. 方向 / 符号（已冻结；禁事后切换）— **C1**

| 项 | **FROZEN** |
|---|---|
| 主规格 | `α_raw = −rank(pressure_resid)`：惩罚高残差解禁压力=供给冲击；低残差优先 |
| **IC 符号** | 对**次期特质收益**的截面 IC **期望为正**（事先机制：低残差解禁压力 → 正超额；**冻结前未读本叶收益**） |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改符号、改 W/H/H_back、改再平衡周期，或改为奖励高 `pressure_resid` |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选方向 |

---

## 3. 残差清单（C5 — 冻结最低集；缺列→PIN_GAP）

同日截面、PRIMARY 掩码（HI_LIQ）后：

1. 原始：`pressure_raw = mean_W(unlock_raw)`（§1 主定义；(a)+加价）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 **T−1 PIT**）。
4. vs **style 代理（写死）**：
   - `mom20`
   - `vol20`
   - `logADV20`（或等价 `capacity_adv` 暴露；脚本须在回执钉所用列名；**二者择一并钉死，不得事后换**）
5. **缺列 → PIN_GAP**：勿静默跳过；后加正交项须**补丁文件**，不得静默改本钉。
6. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 / 叶31 / 叶32 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）；**另须披露 vs 历史 margin_delta / hk_hold / moneyflow**（C4）。
7. **禁**把两融/叶32 flow、Amihud/叶31 impact、叶27 `on_minus_id`/overnight ε、叶30 CRR/OCF、叶25 应计、hk_hold、moneyflow、表内 `float_ratio` 当本叶主输入。

---

## 4. 正交硬闸（C4 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **强度过滤**（披露，不单独硬拒） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 叶31 Amihud | 同上；禁 `|r|/amount` 冲击当主输入 |
| 叶32 MARGIN_NET_FLOW_RESID | 同上；禁 `rzmre/rzche/rzye` / 两融净流入当主输入 |
| 历史 margin_delta / hk_hold / moneyflow | **须披露** Jaccard/ρ；Jaccard≥0.7 → **硬拒**（同精神）；禁 hk_hold / moneyflow 80/20 进主信号 |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300**；FULLA 研究 **median≥800** |
| 换手/成本 | 评价口径 **30bp**；>20%/日或成本>毛超额一半 → 不可交易（X2 后评价） |
| 正式重叠 | **X2 前须用完整 α 重算** vs 叶19/25/27/30/31/32 的 Jaccard/ρ，**另须披露 vs margin_delta / hk_hold / moneyflow**；who_pays DRAFT 硬拒意向**不能替**正式重叠证明（C4） |

---

## 5. 宇宙双钉（C6 — HI_LIQ 主判决 + FULLA 研究）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决**（纸面路径） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | median≥**300** |
| **FULLA_V1** | **研究对照**（仅披露；不得静默改 PRIMARY） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | median≥**800** |

- 评价书行业帽意向（与叶25 族对齐，供将来脚本钉）：HI_LIQ **25%** / FULLA **28%**（本预注册不跑评价）。
- **PRIMARY 不得静默改 FULLA**；FULLA 读数仅研究披露，不单独解阻 X2 ACCEPT。
- 两池规格**同时冻结**；PRIMARY 不得静默改 FULLA。

---

## 6. 窗 / 再平衡 / 交付 / rss（C9）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗 | **2024-06-03 → 2026-10-09**（与叶25/30/31/32 对齐） |
| H / H_back / W / 再平衡 / 最少有效日 | **20 / 5 / 20 / 20 / ≥15** |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 base-α 向量**（HI_LIQ 主 + FULLA 研究）；非 Top-N 当闸 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED**（未来 execute 回执须含 peak 证明：sampler / ru_maxrss / meta 等 Arch 惯用口径） |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C7 — 对齐 `alpha_decay_gate` v1.1 + 叶30/31/32 HOLD 教训）

叶30 HOLD `f00536b9`、叶31 HOLD `7ef5aa11` 根因均含 **DECAY_DOWNGRADE**；叶32 HOLD `45dd87dc` 则 **decay=KEEP 但仍** 门 A/B/current 总 false / untradable=true——**KEEP 不解阻** X2 ACCEPT。本叶把 KEEP 三闸合取写死：

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `research/alpha_decay_gate` / `alpha_decay_gate_v1_1` **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT 规则；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1 口径：对 510300 去 β 后截距×252） |
| 连降 | **非连降 5 季**（衰减门 v1.1 季切点） |
| H2 净 CAGR | **`H2_net_cagr > 510300` 净 CAGR**（同近端 252 日窗、同成本口径；严格优于基准） |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**满足才可谈 KEEP；任一条不满足 → **最多 WATCH / HOLD** |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD `45dd87dc` 教训）；组合闸仅意图，冻结后另验 |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改符号/W 救闸 |
| 设计防衰减 | 慢再平衡（20d）+ 残差掉市值/行业/style（避免「解禁惊吓」近端反转）；禁快闸与慢 α 混装同一主规格 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | 限售解禁 PIT | `data/v2/share_float/share_float_pit.parquet`（who_pays 已核：6,449,659 行；列含 `float_share/float_ratio/available_at`）；PIT=`available_at`；**PRIMARY 用 `float_share`，禁用 `float_ratio`** |
| 2 | 收盘价 T−1 | bars/价格契约列（脚本钉：不复权收盘价元 **或** 标准 adj close；二者择一不得事后换） |
| 3 | 流通市值 T−1 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet`（单位 **元**；who_pays 已核：11,711,361 行） |
| 4 | HI_LIQ 掩码 | PRIMARY（§5） |
| 5 | FULLA 掩码 | 研究对照（§5） |
| 6 | SW L1 PIT（`data/v2/sw_l1_pit/…`） | 残差 demean |
| 7 | mom20 / vol20 / logADV20（或钉死的 capacity_adv 暴露） | style 残差（§3）；缺列→PIN_GAP |
| 8 | 叶19 / 叶25 / 叶27 / 叶30 / 叶31 / 叶32 α parquet | **仅** Jaccard/ρ；不进主信号 |
| 9 | （披露）历史 margin_delta / hk_hold / moneyflow | **仅**正交披露 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造** 解禁/市值/价。本拍**未**实算 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | **零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶**解禁供给** |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 主轴是 **限售解禁压力**，**不是**隔夜−日内差的二阶矩 |
| 叶31 Amihud 冲击慢 | `|r|/amount` 冲击残差 | 本叶**不**读 Amihud/成交额冲击；主输入=`float_share×close` |
| 叶32 `MARGIN_NET_FLOW_RESID` | 两融净融资流入强度残差 | 本叶**不**读 `rzmre/rzche/rzye`；主轴=股本解禁日历供给冲击 |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |
| 历史 `margin_delta` / 北向 / moneyflow | 资金流换皮 | 本叶 **不**读 hk_hold / moneyflow / 两融；正交须披露 |

**一句话分家**：叶25/30=会计应计·CRR；叶27=隔夜−日内 idio 波动；叶31=Amihud 冲击；叶32=两融净流入；叶33=**HI_LIQ 短窗限售解禁压力（(a)+加价无量纲）经 SW+style 残差后的慢 α（−rank）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C8）

forbid∋ 下列 sha8（**`5774bb6e` + 二十票**；**禁 RESTORED / 禁复用** 作本叶流程门或自开跑）：

| sha8 | 备注 |
|---|---|
| `5774bb6e` | 叶32 selfcheck CONSUMED（主令点名） |
| `02426b73` | 二十票 |
| `4bb141c9` | 叶31 X2 selfcheck `.ok`（已 CONSUMED） |
| `fdbaa512` | 叶31 X2 构建 `.ok`（已 CONSUMED） |
| `aa25e989` | 叶30 X2 selfcheck `.ok`（已 CONSUMED） |
| `7e239487` | 禁复用旧窗 |
| `5af20222` | 禁复用旧窗 |
| `5ae077fa` | 禁复用旧窗 |
| `3c297052` | 二十票 |
| `e107383f` | 二十票 |
| `2be59acd` | 二十票 |
| `a7d98ac9` | 二十票 |
| `8e51de63` | 二十票 |
| `3a6caa4f` | 二十票 |
| `8bcd79dc` | 二十票 |
| `725be3e0` | 二十票 |
| `0f50daf7` | 二十票 |
| `3c19dd7d` | 二十票 |
| `1c32ab1e` | 二十票 |
| `6054b3bf` | 二十票 |
| `6de02e74` | 二十票 |

合取串：`5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`

另禁：
- 复用叶25 / 叶27 / 叶30 / 叶31 / 叶32 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开（对齐叶30 selfcheck P0 教训）
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS

---

## 11. 叶30 KEEP 修复 / 叶28/29 另队（C10）

- 叶30 衰减 KEEP 修复 DRAFT sha8 **`0087c928`**：**另队**；**不并入**本 FROZEN；不得借本冻结窗口夹带签跑/改叶30 CONSUMED 产物。
- 本拍**未打开/未审** `0087c928`（对齐 Arch `55531e12` §3 / C10）。
- 叶28/29 仍 **FROZEN**；**不夹带、不升**本叶 PRIMARY。
- 叶30/31/32 衰减 KEEP / 组合闸修复可选另队，**不挡**本新叶。

---

## 12. 失败截断

- 覆盖闸 HI_LIQ median<300 或 FULLA median<800 → 不申 `.ok` / 不宣称可交易
- Jaccard≥0.7 vs 叶19/25/27/30/31/32（或 vs 历史 margin_delta / hk_hold / moneyflow）→ 硬拒，改机制或废叶
- 冻结后读收益改方向/W/H/H_back/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP（`latest_resid_alpha≤0` 或连降5季 或 `H2_net_cagr≤510300`）或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT；**KEEP 亦不解阻** X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT（未来执行窗）；无 peak_proof → 回执不完整
- 误读 hk_hold / 两融 / Amihud / 偷看 `available_at>t` / 静默混用表内 `float_ratio` / 误用未加价股数÷市值 → 废叶

---

## 13. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT 1032477d + COVER 61d9f656 + PIN 4e17ccfc
  → Arch PASS_WITH_CONDITIONS 55531e12
      → 【本文件】PREREG_FROZEN（C1：另窗相对 DRAFT 升格；(a)+加价）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf33_*（C2：本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED 5774bb6e+二十票；禁复用叶25/27/30/31/32；forbid 合取）
                          → X2（完整 α；重叠重算含 vs margin_delta/hk_hold/moneyflow；decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| `research/leaf33*` 构建脚本 | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| 叶30 KEEP `0087c928` | **另队不并入**（C10） |
| 叶28/29 | **仍 FROZEN**（不夹带） |
| 叶26 | **不交审** |
| 叶30 HOLD `f00536b9` / 叶31 HOLD `7ef5aa11` / 叶32 HOLD `45dd87dc` | **不回撤**（只读对照） |

---

## 14. 禁项清单（再钉）

- 本拍实跑 / 申 `.ok` / 落构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid `5774bb6e`+二十票（见 §10）
- 冻结后改 α 符号 / W / H / H_back / 再平衡；读收益翻号
- 卖方/金股/survey/TP/LLM 权重当 α；GP/高杠杆；moneyflow 80/20 叠仓
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开；叶31 Amihud 复刻；叶32 两融净流入复刻
- 表内 `float_ratio` 当 PRIMARY；未加价股数÷市值静默混量纲
- hk_hold / northbound / moneyflow 换皮
- PRIMARY 静默改 FULLA；把研究对照当判决
- 并入叶30 KEEP `0087c928`；重跑叶30/31/32 selfcheck；夹带叶28/29
- `live=true` / `promotion_approved=true` / 声称 X2 ACCEPT / 报 Leo

---

## 15. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` |
| 状态 | **FROZEN**（PREREG_FROZEN） |
| mechanism_tag | `g1g5_ashare_share_unlock_pressure_resid_v1` |
| H / H_back / W / 再平衡 / 最少有效日 | **20 / 5 / 20 / 20 / ≥15** |
| C3 量纲 | **(a)+加价**：`unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`；表内 `float_ratio` PRIMARY 禁用 |
| α 符号 | **−rank(pressure_resid)**；IC 对次期特质收益期望为正 |
| X2 窗 | **2024-06-03 → 2026-10-09** |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| 残差 | SW L1 + log 流通市值 + mom20/vol20/logADV20（或钉死 capacity_adv） |
| decay KEEP | latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端=252d（gate v1.1）；**KEEP 不解阻** X2 ACCEPT |
| forbid | `5774bb6e`+二十票（见 §10） |
| rss / peak_proof | 1500 / REQUIRED |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| Arch / WHO_PAYS / COVER / PIN | `55531e12` / `1032477d` / `61d9f656` / `4e17ccfc` |
| 上下文 HOLD | 叶32 `45dd87dc` / selfcheck `99675387` / CONSUME `efa033e0` / 构建闸 `1aa432a5` / 叶31 `7ef5aa11` / 叶30 `f00536b9`（不回撤） |
| ok_requested / EXECUTED / 脚本本拍 | false / false / 无 |
| live / promotion / ≠X2 ACCEPT / leo_notify | false / false / true / false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
