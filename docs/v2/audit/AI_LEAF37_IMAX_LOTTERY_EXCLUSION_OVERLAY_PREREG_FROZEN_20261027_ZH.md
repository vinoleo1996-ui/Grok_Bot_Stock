# 【FROZEN 预注册 2026-10-27 17:00 ET】叶37：IMAX/隔夜彩票剔除 overlay（PREREG_FROZEN）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 17:00 ET**（America/New_York；ISO `2026-10-27T17:00:00-04:00`）
- 状态：**FROZEN**（相对 who_pays/COVER/COUNT **DRAFT** 升格为预注册冻结）。冻结前**未**读任何本叶收益选 q/方向。
- 主令：2026-10-27 ~16:58 ET — 主裁 **叶37 出 FROZEN GO**；Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`4a074f0a`** → 令 AI 出 FROZEN（C1–C13 入钉；C3=**(B)**）。
- 上游钉（本机 MATCH）：
  - Arch 审：`docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` sha8 **`4a074f0a`**（全长 `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859`）
  - WHO_PAYS DRAFT：`…WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`0ed8e9d8`**（全长 `0ed8e9d81edd2a751b4cf7c8b0e4116ba300c418b12d88476220a336238616cf`）
  - COVER DRAFT：sha8 **`847245f8`**（全长 `847245f8ef5786e95e68b6b73e713a12a3bc573fcd49b40ba757ee33013e01b6`）
  - COUNT RECEIPT：sha8 **`154bc157`**（全长 `154bc157d6b054ddd039e1c9bd800abf388b0406e85ed279dfd67bd3c4258023`）
  - COUNT SCRIPT：sha8 **`c10b735f`**（全长 `c10b735f20e00e74dfc1e16519947903cf0199b8ed1b5925e55f26262b9251ad`）
  - COUNT JSON：`output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` sha8 **`2217f580`**（全长 `2217f5801b558fd8227da4390f7f77c84f9bd9242863e26610dabe6e5562291d`）
  - dig：`output/d1/DIG_FACTOR_20261027_1625ET.md` sha8 **`74234fca`**
  - PIN（C3=B）：`docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md`（本拍同落；sha8 以磁盘为准）
- 对照形态：叶35 PREREG_FROZEN `be9fc459`；叶34 PREREG_FROZEN `8be1099e`（结构对齐；内容换叶37）。
- 叶号：**叶37**；mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`。
- **上游叶36**：inquiry 剔除 overlay **HOLD CLOSED**（WHO `feaa5dbb` / JSON `575e8276`）→ 改派备选 A 本票；**禁复开 inquiry 主轴**；**禁放宽其覆盖阈**（C10）。
- 旁线不回撤：叶35 正式脚本 `434ff42c` / `.ok` `eb70eef4`…；叶34 HOLD；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`**。
- **本冻结 ≠ `.ok` / ≠ 正式构建脚本 / ≠ X2 / ≠ selfcheck / ≠ Book-Smoke**；**禁**自申 `.ok`；**本拍无** `research/leaf37*`（ABSENT 预期；C2）；**EXECUTED=false**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_imax_lottery_exclusion_overlay_v1`（叶37）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内忽视日内彩票右尾（高 IMAX）、仍给高彩票名足额权重的持仓者——剔除后主干少踩散户追高彩票股的反转。  
> **可检验预测（已冻结）**：PRIMARY 交付 = **mask-only** 日度 exclusion mask（池内 `IMAX_proxy` top_q=**0.20** 高尾名 `mask=0`，其余可算名 `mask=1`；不可算名不进有效集、不填假 0）；**叠主干**；**不是**叶24 `g1g5_ashare_imax_intraday_v1` 完整 −IMAX 排序主 α；**不是**叶18/27 波动主 α。`IMAX_proxy`=raw `r_id` 20d top-5（≥15 valid）；`full_residual_e_id=false`（C3=B；持续 APPROX）。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃剔除集 vs 叶18/18v/27 高风险尾 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另须完整重叠披露 vs 叶24/34/35/36；HI_LIQ 再平衡日可算 IMAX 名 median≥300、剔除名 median≥30。  
> **失效条件**：退化为叶24 完整 −IMAX 主叶；或 vs 叶18/27 Jaccard≥0.7；或主信号混入叶18/27/24 α / 精神叙事 / 卖方/金股/TP/LLM；或冻结后事后改 q/翻向读收益；或静默把 proxy 当全 e_id；或复开叶36 inquiry / 放宽其覆盖阈；或把 COUNT APPROX gate_pass 当 X2 ACCEPT；或 KEEP 被误读为解阻 ACCEPT。  
> **交 Alpha 时点**：Arch 审本 FROZEN → 另窗正式构建脚本 → Arch 审脚本 → 本叶**独立**新窗 `.ok` + X2 回执之后。

---

## 1. 机制（高 IMAX 彩票剔除 overlay；慢）— **FROZEN**

### 1.1 C3=B：`IMAX_proxy` 交付定义（PIN 入钉）

PIN 决议（本拍同落）写死：

| 项 | **FROZEN** |
|---|---|
| 面板 | `output/ai_factory/panel_cache_v2_resumefix/cs_panel_*.parquet` |
| `r_id` | `(1+ret)/(1+ret_on)−1`（panel 列 `ret`/`ret_on`；定义对齐叶24） |
| `IMAX_proxy` | `mean(largest 5 r_id in [t−19,t])`，有效日 **≥15** |
| `full_residual_e_id` | **`false`** |
| APPROX | **持续披露**；**勿**静默当全残差 e_id IMAX |
| 升级 | 升 e_id **须另窗**重跑计数闸 + 修订 PIN/FROZEN；本拍**不**升级 |

### 1.2 剔除规则 / 交付（C4 / C5 / C11 — **mask-only PRIMARY**）

```
H_t = { i ∈ HI_LIQ_t ∩ computable_t : IMAX_proxy(i,t) ≥ Q_{1−q}(IMAX_proxy(·,t)) }
q = 0.20
```

| 项 | **FROZEN** |
|---|---|
| **PRIMARY 交付** | **mask-only**：可算名 `i∈H_t` → `mask=0`；其余可算名 → `mask=1`；不可算名 **不进有效集、不填假 0**；**叠主干** |
| 明示（C4） | **mask-only PRIMARY**；soft-penalty **非 PRIMARY** |
| soft-penalty 另窗 | 若启用连续 soft-penalty，须 **SW L1 + log 流通市值 + style（mom20/vol20/logADV20）**；缺列→**PIN_GAP** |
| 符号（C5） | 「高 IMAX=剔除」；`q=0.20`；**禁**读收益改阈值/翻方向 |
| 再平衡 | 每 **20** 交易日 |
| C11 | 交付=形态 A **mask-only overlay 叠主干**；**禁**完整 `g1g5_ashare_imax_intraday_v1` 排序/多层残差主 α；**禁**叶18/27/24 α 当主输入 |
| 边界 | ≠叶24 −IMAX 主叶；≠叶18/18v/27 波动主 α；≠叶36 inquiry；≠叶34/35 各自主轴换皮 |

---

## 2. 方向 / 符号（已冻结；禁事后切换）— **C1 / C5**

| 项 | **FROZEN** |
|---|---|
| 主规格 | 高 IMAX 尾部剔除（top_q=0.20 → mask=0） |
| 符号 | 「高 IMAX=剔除」；冻结前**未**读本叶收益 |
| 禁事后翻 | **禁止**因 X2/密封/selfcheck 读数改 q、改符号、改再平衡，或改为奖励高 IMAX |
| 禁读收益选号 | 冻结前/本拍**未**打开本叶任何收益序列选 q/方向 |

---

## 3. soft-penalty / 残差（C4 — 非 PRIMARY；启用另窗）

1. **PRIMARY = mask-only**（§1.2）：不做 SW+style 全残差。
2. **若另窗启用连续 soft-penalty**：同日 PRIMARY 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP；后加正交项须**补丁文件**。
3. 披露 vs 叶18/18v/27（硬拒口径）及叶24/34/35/36（披露）的 **Jaccard** 与 **ρ**（C7）。
4. **禁**把叶18/27/24 α、两融/Amihud/应计/ETF/问询函当本叶主输入（C11）。

---

## 4. 正交硬闸（C7 — 口径本 FROZEN 写死）

| 对照 | 硬规则 |
|---|---|
| 叶18 / 叶18v / 叶27 | 剔除集 vs 其 α **高风险尾**（α 最低 q=0.20）Jaccard **≥0.7 → 硬拒**；ρ_mean>0.5 → **强度过滤**（披露） |
| 叶24 −IMAX 主叶 | **禁**重开完整排序主叶；Jaccard/ρ **披露**；反同构靠形态 A |
| 叶34 / 35 / 36 inquiry | 披露 Jaccard/ρ；**禁**复开叶36 inquiry / 放宽其覆盖阈（C10） |
| 覆盖 | HI_LIQ 再平衡日可算 IMAX 名 **median≥300**；剔除名 **median≥30**；`zero_frac≤0.05` |
| 换手/成本 | 评价口径 **30bp** |
| 正式重叠 | **X2 前须用完整 overlay 重算** vs 18/18v/27（硬拒）及 **24/34/35/36**（披露）；COUNT 轻量 **不能替**正式重叠证明 |
| 强度过滤钉 | COUNT：ρ18≈**0.505** / ρ27≈**0.665** 已触 → FROZEN **持续披露**；**不解阻也不单独废叶** |

COUNT 轻量摘要（APPROX，≠X2）：computable_median=**2816.5**；excl_median=**564**；zero_frac=**0**；J18_max≈**0.311** / J27_max≈**0.443** / J24≈**0.223** ≪0.7；peak≈**1030**MB。

---

## 5. 宇宙（C6 — HI_LIQ 主判决）

| 池 | 角色 | 掩码路径（FROZEN） | 覆盖硬闸 |
|---|---|---|---|
| **HI_LIQ_V1.1** | **PRIMARY 判决** | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（sha8 `c5433e80`） | 可算 median≥**300**；剔除 median≥**30** |

- **PRIMARY 不得静默改 FULLA**；若另窗加 FULLA 研究对照须补钉，不得替换 PRIMARY。
- C6：HI_LIQ 主（本叶 COUNT/who_pays 口径；与叶35 双钉不同处：本票未强制 FULLA 双池，**明示 HI_LIQ-only PRIMARY**）。

---

## 6. 窗 / 再平衡 / 交付 / rss（C9）

| 项 | **FROZEN** |
|---|---|
| X2 样本内窗 | **2024-06-03 → 2026-10-09** |
| 再平衡 | **20** 交易日 |
| top_q / 符号 | **0.20** / 高 IMAX=剔除 |
| 成本口径 | **30bp**（评价；本冻结不跑 PnL） |
| 主交付 | **日度 exclusion mask**（HI_LIQ）；形态 A overlay 叠主干；soft-penalty 非 PRIMARY |
| 判定路径 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| **rss** | **1500** MB 禁抬；未来执行窗 **硬 ABORT** |
| **peak_proof** | **REQUIRED** |
| live / promotion / ok_requested / EXECUTED | `false` / `false` / `false` / `false` |

---

## 7. decay KEEP 硬验收（C13 — 对齐 `alpha_decay_gate` v1.1 + 叶32/34/35/36 教训）

| 闸 | **FROZEN** |
|---|---|
| 近端窗定义 | 与 `alpha_decay_gate` v1.1 **H2 同口径**：评估日 t 起**最近 252 个交易日**净收益窗（不足则按闸门 SHORT_HISTORY/INSUFFICIENT；**≥126** 日才出 α） |
| 近端残差 α | **`latest_resid_alpha > 0`**（年化；v1.1：对 510300 去 β 后截距×252；若以叠加超额评价则同口径披露） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **`H2_net_cagr > 510300`** |
| KEEP 合取 | `latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` **三闸同时**；任一条不满足 → **最多 WATCH / HOLD** |
| KEEP 不解阻 | **KEEP 不解阻 X2 ACCEPT**（叶32/34/35/36 HOLD 教训） |
| 失败截断 | **不派** Book-Smoke；**≠X2 ACCEPT**；不得事后改 q/符号救闸 |

本冻结**不跑**衰减门；验收在独立 `.ok`+X2/selfcheck 另窗。

---

## 8. PIT 输入（正式构建契约）

| # | 输入 | 路径 / 角色（FROZEN） |
|---|---|---|
| 1 | cs_panel_v2_resumefix | PRIMARY：`ret`/`ret_on`/`hiliq`；年块按需；PIN C3=B |
| 2 | HI_LIQ 掩码 | PRIMARY（§5） |
| 3 | SW L1 / style / 市值 | **仅** soft-penalty 另窗强制；mask-only PRIMARY 可后钉 |
| 4 | 叶18/18v/27/24/34/35/36 α 或剔除集 | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 **PIN_GAP**，**勿静默编造**。`IMAX_proxy` APPROX 持续披露（C3=B）。本拍**未**实算完整 α。

---

## 9. 相对已占轴分家

| 已占轴 | 机制 | 本叶必须多出来的正交 |
|---|---|---|
| **叶24** imax_intraday | −IMAX **完整排序主 α** | 本叶=**高 IMAX mask-only overlay 叠主干**；不输出完整 −IMAX α |
| **叶18 / 18v** | 隔夜特质波动主 α | 本叶主轴=**日内**右尾剔除；Jaccard≥0.7 硬拒 |
| **叶27** on_minus_id ivol | 隔夜−日内残差波动主 α | 不输出波动主 α；Jaccard≥0.7 硬拒 |
| **叶36** inquiry | 财务问询 exclusion | **HOLD CLOSED**；不复开；不放宽覆盖阈 |
| 叶35 ETF 压力 / 叶34 高应计 | 各 overlay | 不读 ETF/应计；HOLD 不回撤 |
| 叶33/32/31/30/25 | 各已占 | 零解禁/两融/冲击/CRR/应计主输入 |
| 叶28/29 / `0087c928` | 另队 | **不夹带** |

**一句话分家**：叶24=−IMAX 完整主 α；叶18/27=波动主 α；叶37=**HI_LIQ 高 IMAX_proxy top20% mask-only 彩票剔除 overlay（非主 α）**。

---

## 10. 禁 RESTORED / 禁复用旧窗（C8）

forbid∋ 下列合取串（主令点名 **`eb70eef4+00eec671+10927bd9+25ae4572`** + Arch C8 全集）：

`eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`

| sha8 | 备注 |
|---|---|
| **`eb70eef4`** | 叶35 B1 `.ok` CONSUMED；禁 RESTORED |
| **`00eec671`** | 主令点名 RESTORED |
| **`10927bd9`** | 主令点名 RESTORED |
| **`25ae4572`** | 主令点名 RESTORED（禁碰叶35 旧票） |
| `178e90e9` | 叶34 selfcheck `.ok` CONSUMED |
| `c1b71e64` / `245df63f` / `c5ed13df` / `5774bb6e` / `81521fb5` | 旧窗 / 叶32/33 等 |
| 二十票 | `02426b73`…`6de02e74`（同 Arch C8） |

另禁：
- 复用叶18 / 24 / 27 / 30–36 任一 live/CONSUMED `.ok` 当本叶授权
- 脚本 CLI `--arch-ok-path` 自开
- 本拍申任何 `.ok`；挂/抬 QUIET；抬 RSS；RESTORED 上列任一票

---

## 11. 叶36 HOLD / 另队（C10）

- **叶36 inquiry HOLD CLOSED**（WHO `feaa5dbb` / JSON `575e8276`）：**禁复开** inquiry 主轴；**禁放宽**其覆盖阈；本票不得借窗口夹带改叶36。
- 叶30 衰减 KEEP 修复 **`0087c928`**：**另队**；**不并入**本 FROZEN。
- 叶28/29 仍 **FROZEN**；**不夹带**。
- 叶35 正式 **`434ff42c`** / 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤。
- 备选 B（行业级客户动量）**不升 PRIMARY**；本拍**勿自开**。

---

## 12. C1–C13 对照表（Arch `4a074f0a` §3 全文入钉）

| # | 条件（Arch §3） | 本 FROZEN |
|---|---|---|
| C1 | 另窗冻结完整预注册 | **本文件**全文（mechanism/公式/窗/再平衡/交付/判定） |
| C2 | 正式脚本另窗；计数非正式构建 | `research/leaf36*|leaf37*` **ABSENT**；计数脚本 audit **`c10b735f`**（非正式 α 构建） |
| C3 | IMAX APPROX 二选一 | **择 (B)**：`IMAX_proxy` 为交付定义；`full_residual_e_id=false`；持续 APPROX；PIN 入钉；**不**升全 e_id |
| C4 | soft-penalty / mask-only | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW+style |
| C5 | top_q=0.20 符号冻结 | q=0.20；高 IMAX=剔除；禁读收益改阈值/翻方向；再平衡=20 |
| C6 | HI_LIQ 主判决 | HI_LIQ PRIMARY；不得静默改 FULLA |
| C7 | X2 前完整重叠；ρ 强度过滤披露 | vs 18/18v/27 硬拒；vs 24/34/35/36 披露；ρ18≈0.505 / ρ27≈0.665 披露；COUNT 轻量不替 |
| C8 | forbid 全集；禁复用旧 `.ok`；禁 `--arch-ok-path` | §10；含 `eb70eef4+00eec671+10927bd9+25ae4572`+旧票 |
| C9 | rss=1500 + peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | 叶36 inquiry HOLD CLOSED | 禁复开 inquiry；禁放宽覆盖阈；§11 |
| C11 | overlay ≠ 叶24 −IMAX 主叶 | 交付=mask-only overlay 叠主干；禁完整 imax_intraday 主 α；禁 18/27/24 α 主输入 |
| C12 | APPROX 计数 ≠ X2 ACCEPT | gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** ACCEPT / Book-Smoke / 升纸面 |
| C13 | decay KEEP；KEEP 不解阻 ACCEPT | 近端=252d（≥126 才出 α）；KEEP 三闸合取；KEEP 不解阻（叶32/34/35/36 教训） |

---

## 13. 失败截断

- 覆盖闸 HI_LIQ 可算 median<300 或剔除 median<30 或 zero_frac>0.05 → 不申 `.ok`
- Jaccard≥0.7 vs 叶18/18v/27 → 硬拒，改机制或废叶
- 退化为叶24 完整 −IMAX 主叶 → 废叶
- 冻结后读收益改方向/q/再平衡 → 违规，作废本轮 FROZEN（须新修订文件）
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 最多 WATCH/HOLD；不派烟、≠X2 ACCEPT；**KEEP 亦不解阻** X2 ACCEPT
- 内存 peak≥1500 MB → 硬 ABORT；无 peak_proof → 回执不完整
- 静默把 proxy 当全 e_id / 复开叶36 / 放宽叶36 覆盖阈 / 误读 18/27/24 α 当主输入 → 废叶
- 把 COUNT APPROX 当 X2 ACCEPT → 违规（C12）

---

## 14. 状态机 / 下一跳（C1 / C2）

```
who_pays DRAFT 0ed8e9d8 + COVER 847245f8 + COUNT 154bc157 / JSON 2217f580 / 脚本 c10b735f
  → Arch PASS_WITH_CONDITIONS 4a074f0a
      → 【本文件】PREREG_FROZEN（C1；C3=B IMAX_proxy；mask-only；≠叶24）
          → 主排 Arch 只审 FROZEN（本拍目标）
              → 另窗 AI 写正式构建脚本 research/leaf37_*（C2：本拍禁；ABSENT）
                  → Arch 审脚本
                      → 独立新窗 .ok（禁 RESTORED eb70eef4+00eec671+10927bd9+25ae4572+旧票）
                          → X2（完整重叠含 18/18v/27/24/34–36；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件**（C1） |
| PIN C3=B | 本拍同落 `…IMAX_PROXY_PIN…` |
| 计数脚本 | **`c10b735f`**（audit/；非正式构建） |
| `research/leaf37*` | **ABSENT**（C2：本拍禁落） |
| 申 `.ok` / X2 / selfcheck / Book-Smoke | **禁**（等主/Arch） |
| COUNT APPROX | gate_pass=true；**≠X2 ACCEPT**（C12） |
| 叶36 inquiry | **HOLD CLOSED** 不复开（C10） |
| 备选 B | **不升 / 勿自开** |
| 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶32 `45dd87dc` | **不回撤** |

---

## 15. 禁项清单（再钉）

- 本拍实跑完整 α / 申 `.ok` / 落 `research/leaf37*` 构建脚本 / 挂 QUIET / 抬 RSS / git commit
- RESTORED forbid（见 §10）含 `eb70eef4+00eec671+10927bd9+25ae4572`
- 重开叶24 完整 −IMAX 主叶；复开叶36 inquiry；放宽叶36 覆盖阈
- 禁改叶33 `afbbe7e7` / 叶35 `434ff42c`
- 自开备选 B；推 Leo；`live=true`；声称 X2 ACCEPT

---

## 16. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` |
| PIN C3=B | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` |
| RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` |
| 状态 | **PREREG_FROZEN**（≠ `.ok`；≠ X2 ACCEPT） |
| mechanism_tag | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| C3 | **(B)** IMAX_proxy 交付；`full_residual_e_id=false` |
| C4 | **mask-only PRIMARY** |
| C5 | q=**0.20**；高 IMAX=剔除；再平衡=20 |
| C11 | **≠** 叶24 −IMAX 主叶 |
| Arch | `4a074f0a` PASS_WITH_CONDITIONS |
| dig | `74234fca` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
