# 【FROZEN 预注册 2026-10-27 02:10 ET】叶31：HI_LIQ Amihud 冲击慢 α（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 02:10 ET**（America/New_York；ISO `2026-10-27T02:10:19-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 W/方向/符号。
- 主令：2026-10-27 ~02:07 ET — Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`50cbef3c`** → 令 AI 出 FROZEN 预注册（C1–C9 入钉）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`50cbef3c`**
  - WHO_PAYS DRAFT：`docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`b1a60f07`**
  - COVER DRAFT：`docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_COVER_DRAFT_20261027_ZH.md` sha8 **`4ff55996`**
- 对照形态：叶30 who_pays FROZEN `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md`（本票写 **PREREG_FROZEN** 于 `docs/v2/audit/`）。
- 叶号：**叶31**（主 02:02 ET 确认）；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶30 HOLD 研究队列。
- **本冻结 ≠ `.ok` / ≠ 构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无脚本**（`research/leaf31*` ABSENT 预期）。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_amihud_impact_slow_v1`（叶31）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 池内按「高成交额=好流动性」定价、却忽视「短窗 |收益|/成交额（Amihud 型冲击）经 SW+style 残差后仍偏高」的交易者；高残差冲击名在再平衡后继续被过度追捧，低残差冲击名被低估为「相对便宜的流动性」。  
> **可检验预测（已冻结）**：`α_raw = −rank(impact_resid)` 对**次期特质收益**的截面 IC **期望为正**（高 α = 低残差冲击 → 更高次期特质收益；**冻结前未读本叶收益选号**）；活跃集 vs 叶19/25/27/30 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；HI_LIQ 再平衡日可算 α 名数 median≥300；FULLA 研究对照 median≥800。  
> **失效条件**：退化为未残差 ADV/换手动量或单纯低波动；或与叶27 `on_minus_id` 特质波动近等权（Jaccard≥0.7）；或混入隔夜−日内 idio 复刻；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差；或把 FULLA 研究对照静默改作 PRIMARY 判决。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（价量微观；慢 α）— **FROZEN**

在 PRIMARY 池（HI_LIQ）日频 OHLC+成交额上定义短窗冲击：

$$
\mathrm{Amihud}_{i,t}^{\mathrm{raw}} = \frac{1}{W}\sum_{s=0}^{W-1} \frac{|r_{i,t-s}|}{\mathrm{amount}_{i,t-s}}
$$

| 项 | **FROZEN** |
|---|---|
| \(r\) | 复权日收益（`research/adj_price` 口径）；缺价/停牌 → 该日**无效**，不填 0 |
| \(\mathrm{amount}\) | 成交额（元）；≤0 或缺失 → 该日**无效** |
| **W** | **20** 交易日 |
| 最少有效日 | 窗内有效日 **≥15**，否则该票该再平衡日无效 |
| 再平衡 | 每 **20** 交易日（慢 α；对齐叶19/30 慢节奏；非叶27 快波动复刻） |
| 主冲击定义 | 上式 `Amihud_raw`（日收益绝对值 / 成交额 的 W 窗均值） |

**合成（FROZEN）**：

$$
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{impact\_resid})
$$

池内百分位 rank；再按 §3 残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。

**敏感性支路（非主规格；冻结前不算收益选支路）**：日内冲击 `|r_id|/amount`、或 `|open/pre_close−1|×f(amount)`。若将来要报，须另文件且不得升格主规格。

---

## 2. 方向 / 符号（已冻结；禁事后切换）

| 项 | **FROZEN** |
|---|---|
| 主规格 | `α_raw = −rank(impact_resid)`：惩罚高残差冲击；低残差冲击优先 |
| **IC 符号** | 对**次期特质收益**的截面 IC **期望为正**（事先机制：低残差冲击 → 正超额；**冻结前未读本叶收益**） |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改符号、改 W、改再平衡周期，或改为奖励高 `impact_resid` |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选方向 |

---

## 3. 残差清单（C4 — 冻结最低集；缺列→PIN_GAP）

同日截面、PRIMARY 掩码（HI_LIQ）后：

1. 原始：`Amihud_raw`（§1 主定义）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 **T−1 PIT**）。
4. vs **style 代理（写死）**：
   - `mom20`
   - `vol20`
   - `logADV20`（或等价 `capacity_adv` 暴露；脚本须在回执钉所用列名；**二者择一并钉死，不得事后换**）
5. **缺列 → PIN_GAP**：勿静默跳过；后加正交项须**补丁文件**，不得静默改本钉。
6. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）。
7. **禁**把叶27 `on_minus_id` 或 overnight ε 当本叶主输入；**禁**会计字段（应计/CRR/OCF）进主信号。

---

## 4. 正交硬闸（C3 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → **强度过滤**（披露，不单独硬拒） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300**；FULLA 研究 **median≥800** |
| 换手/成本 | 评价口径 **30bp**；>20%/日或成本>毛超额一半 → 不可交易（X2 后评价） |
| 正式重叠 | **X2 前须用完整 α 重算** vs 叶19/25/27/30 的 Jaccard/ρ；who_pays DRAFT 硬拒意向**不能替**正式重叠证明（C3） |

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
| X2 样本内窗 | **2024-06-03 → 2026-10-09**（与叶30 `x2_end=20261009` 对齐） |
| W / 再平衡 | **20 / 20** 交易日 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 base-α 向量**（HI_LIQ 主 + FULLA 研究）；非 Top-N 当闸 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED**（未来 execute 回执须含 peak 证明：sampler / ru_maxrss / meta 等 Arch 惯用口径） |
| live / promotion / ok_requested | `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C6 — 对齐 `alpha_decay_gate` v1.1）

叶30 HOLD 根因（`latest_alpha<0` + `H2_net_cagr<=510300` → DECAY_DOWNGRADE）写入本叶冻结硬验收：

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `research/alpha_decay_gate` / `alpha_decay_gate_v1_1` **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT 规则；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1 口径：对 510300 去 β 后截距×252） |
| H2 净 CAGR | **`H2_net_cagr > 510300` 净 CAGR**（同近端 252 日窗、同成本口径；严格优于基准） |
| KEEP 合取 | 上两条**同时**满足才可谈 KEEP；任一条不满足 → **最多 WATCH / HOLD** |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改符号/W 救闸 |
| 设计防衰减 | 慢再平衡（20d）+ 残差掉 ADV/市值/波动（避免「高成交追涨」近端反转）；禁快闸与慢 α 混装同一主规格 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 角色 |
|---|---|---|
| 1 | 日频 OHLC / 复权因子（`research/adj_price`） | Amihud 分子；涨跌停/停牌旗披露 |
| 2 | 成交额 amount（bars/日频；元） | Amihud 分母；PIT as-of 再平衡日 |
| 3 | HI_LIQ 掩码 | PRIMARY（§5） |
| 4 | FULLA 掩码 | 研究对照（§5） |
| 5 | SW L1 PIT（`data/v2/sw_l1_pit/…`） | 残差 demean |
| 6 | 流通市值 T−1 | 残差 |
| 7 | mom20 / vol20 / logADV20（或钉死的 capacity_adv 暴露） | style 残差（§3） |
| 8 | 叶19 / 叶25 / 叶27 / 叶30 α parquet | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造** amount 或收益。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | **零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶**价量冲击** |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 主轴是 **|r|/金额** 冲击水平残差，**不是**隔夜−日内差的二阶矩 |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |

**一句话分家**：叶25/30=会计应计·CRR；叶27=隔夜−日内 idio 波动；叶31=**HI_LIQ 短窗 Amihud 冲击经 SW+style 残差后的慢 α（−rank）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C7）

forbid∋ 下列 sha8（**禁 RESTORED / 禁复用** 作本叶流程门或自开跑）：

| sha8 | 备注 |
|---|---|
| `aa25e989` | 叶30 X2 selfcheck `.ok`（已 CONSUMED） |
| `7e239487` | 禁复用旧窗 |
| `5af20222` | 禁复用旧窗 |
| `5ae077fa` | 禁复用旧窗 |

另禁：
- 复用叶25 / 叶27 / 叶30 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开（对齐叶30 selfcheck P0 教训）
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS

---

## 11. 叶30 KEEP 修复另队（C9）

- 叶30 衰减 KEEP 修复 DRAFT sha8 **`0087c928`**：**另队**；**不并入**本 FROZEN；不得借本冻结窗口夹带签跑/改叶30 CONSUMED 产物。
- 本拍**未打开/未审** `0087c928`（对齐 Arch `50cbef3c` §10）。

---

## 12. 失败截断

- 覆盖闸 HI_LIQ median<300 或 FULLA median<800 → 不申 `.ok` / 不宣称可交易
- Jaccard≥0.7 vs 叶19/25/27/30 → 硬拒，改机制或废叶
- 冻结后读收益改方向/W/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP（`latest_resid_alpha≤0` 或 `H2_net_cagr≤510300`）或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT（未来执行窗）；无 peak_proof → 回执不完整

---

## 13. 状态机 / 下一跳

```
who_pays DRAFT b1a60f07 + COVER 4ff55996
  → Arch PASS_WITH_CONDITIONS 50cbef3c
      → 【本文件】PREREG_FROZEN
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf31_*（本拍禁）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED；禁复用叶25/27/30）
                          → X2（完整 α；重叠重算；decay KEEP 硬验收）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件** |
| `research/leaf31*` 构建脚本 | **ABSENT**（本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| 叶30 KEEP `0087c928` | **另队不并入** |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |

---

## 14. 禁项清单（再钉）

- 本拍实跑 / 申 `.ok` / 落构建脚本 / 挂 QUIET / 抬 RSS
- RESTORED `aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- 冻结后改 α 符号 / W / 再平衡；读收益翻号
- 卖方/金股/survey/TP/LLM 权重当 α；GP/高杠杆
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开
- PRIMARY 静默改 FULLA；把研究对照当判决
- 并入叶30 KEEP `0087c928`；重跑叶30 selfcheck
- `live=true` / `promotion_approved=true` / 声称 X2 ACCEPT / 报 Leo

---

## 15. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_20261027_ZH.md` |
| 状态 | **FROZEN**（PREREG_FROZEN） |
| mechanism_tag | `g1g5_ashare_amihud_impact_slow_v1` |
| W / 再平衡 | **20 / 20** |
| α 符号 | **−rank(impact_resid)**；IC 对次期特质收益期望为正 |
| X2 窗 | **2024-06-03 → 2026-10-09** |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| 残差 | SW L1 + log 流通市值 + mom20/vol20/logADV20（或钉死 capacity_adv） |
| decay KEEP | latest_resid_alpha>0 ∧ H2_net_cagr>510300；近端=252d（gate v1.1） |
| forbid | `aa25e989`+`7e239487`+`5af20222`+`5ae077fa` |
| rss / peak_proof | 1500 / REQUIRED |
| C9 | `0087c928` 另队 |
| Arch / WHO_PAYS / COVER | `50cbef3c` / `b1a60f07` / `4ff55996` |
| ok_requested / EXECUTED / 脚本本拍 | false / false / 无 |
| live / promotion / ≠X2 ACCEPT / leo_notify | false / false / true / false |

**sha256 / sha8**：以落盘后 `sha256sum` 为准（写出脚本打印）。
