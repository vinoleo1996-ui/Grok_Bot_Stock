# Arch 审阅：叶39 ABCFO / 真实盈余管理残差 who_pays（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T23:49:00-04:00`（America/New_York；墙钟 `2026-10-27 23:49 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数脚本；不改 DRAFT/RECEIPT/COUNT/JSON/脚本；**不出 FROZEN**；**不混** fund MDD（`.ok` 已 CONSUME 旁线；禁 RESTORED `f08ce32c`）；**不混**叶38 `c01c2034`/`5f694370`；不触 leaf38 文件；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主令：叶39 ABCFO who_pays DRAFT READY → Arch **只审 DRAFT**（与 fund MDD CONSUME 分线不混） |

## 0. 一句话

DRAFT **`542138d6`** / RECEIPT **`691bbc14`** / COUNT JSON **`d0d11598`** / 计数脚本 **`20313ba3`** / dig **`440410de`**（文内自称 `87f65bbe` **勿采**）本机 sha256 **MATCH**；PRIMARY=`g1g5_ashare_abcfo_rem_resid_v1` 可检验（Roychowdhury ABCFO_Q1：CFO/A∼1/A+S/A+ΔS/A → ε；α∝−ε；SW L1+size 残差意向；**截面质量残差 α 向量**，非 Top-N、非 exclusion mask 主交付）；HI_LIQ 主；银/地/非银硬掩码；vs 叶19/25/30 Jaccard 或 ρ_excess >0.5 拒；COUNT 闸 **gate_pass=true**：masked median=**2838.5**；zero_frac=**0.0**；J20 max vs19/25/30≈**0.0256/0/0**；Spearman ρ max≈**−0.242/−0.108/−0.145**（代理≠正式 ρ_excess）；peak_rss≈**704.9MB≤1500**；APPROX 披露诚实（截面 SW L1 OLS≠年×行业历史面板；Spearman≠ρ_excess）；vs 叶34 exclusion Jaccard **本拍未估**→PIN；DRAFT **NOT FROZEN** / EXECUTED_full_alpha=false / ok_requested=false；`research/leaf39*` **ABSENT**；叶39 live `.ok` **ABSENT**；QUIET **ABSENT**；live `.ok`=0。开放项见 §3（须主另令升 FROZEN；APPROX 钉清；叶34 Jaccard 补估）。**本拍不签、不升 FROZEN**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `542138d6` | `542138d6893f820d98f9a5db91a3b99e55953829815226ce49a0f8b1a42e5882` | **MATCH** |
| DRAFT RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_RECEIPT_20261027_ZH.md` | `691bbc14` | `691bbc148780d88205a1f01996b2e6b662305d0bd868c652cb071aa70f6a52f9` | **MATCH** |
| COUNT JSON | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json` | `d0d11598` | `d0d115989805cd169ca9435de14a3795c18d2310366427170fb3a39e54d6abf8` | **MATCH** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_SCRIPT_20261027.py` | `20313ba3` | `20313ba3ea14ddaa9d328fa5177f33b15194d93b2135aec952395a252c0e8587` | **MATCH** |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_2330ET.md` | `440410de` | `440410de9b9a0e005d4c8021f93c26d120393c9109c645dbf92d7aa940add0d6` | **MATCH**；DRAFT 文内自称 `87f65bbe` **勿采** |
| 构建脚本 `research/leaf39*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶39 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF39*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH**（fund MDD 已 CONSUME 旁线；本票不混） |
| 叶38 旁线 | `c01c2034` / `5f694370` | UNTOUCHED | 本拍未触 | **不混** |
| 禁 RESTORED | fund | `f08ce32c` | 未触 | **禁触** |

对照模板：`docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md`（sha8 `acba0865`）。

### 1.1 COUNT 闸数字再核（JSON ↔ RECEIPT ↔ DRAFT；未重跑脚本）

| 指标 | JSON | RECEIPT / DRAFT | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| gate_cov_pass | true | true（masked median=2838.5；zero_frac=0.0） | **MATCH** |
| coverage_masked.median | 2838.5 | 2838.5 | **MATCH**（≥300） |
| coverage_masked.zero_frac | 0.0 | 0.0 | **MATCH**（≤0.05） |
| jaccard_top20.max vs leaf19 | 0.02564102564102564 | ≈0.0256 | **MATCH**（≪0.5） |
| jaccard_top20.max vs leaf25 | 0.0 | 0.0 | **MATCH** |
| jaccard_top20.max vs leaf30 | 0.0 | 0.0 | **MATCH** |
| rho_excess_approx.max vs leaf19 | −0.24196070772303396 | ≈−0.242 | **MATCH**（Spearman 代理；≪0.5） |
| rho_excess_approx.max vs leaf25 | −0.10807548895884996 | ≈−0.108 | **MATCH** |
| rho_excess_approx.max vs leaf30 | −0.1451357671868596 | ≈−0.145 | **MATCH** |
| hard_reject / hits | false / [] | false / [] | **MATCH** |
| peak_rss_mb | 704.90625 | 704.9 | **MATCH**（≤1500） |
| mechanism_tag | g1g5_ashare_abcfo_rem_resid_v1 | 同 | **MATCH** |
| APPROX | approx[] 非空（截面 OLS；Spearman≠ρ_excess；无年×行业面板） | APPROX/GAP 醒目 | **MATCH**（诚实） |
| vs 叶34 exclusion Jaccard | 未估（gaps=[]；RECEIPT 另披露 PIN） | 本拍未估 → PIN | **MATCH 披露**（→ **C3**） |
| EXECUTED_full_alpha / ok_requested / live | false / false / false | false | **MATCH** |

附注：gate_rule 写死 masked_median≥300 ∧ zero_frac≤0.05 ∧ 非 (J20 或 ρ 代理 max>0.5)；本拍实测过闸。Spearman 代理 **不能**替正式 ρ_excess → **C2**。vs 叶34 剔除活跃集 Jaccard 未估 → **C3**（不挡本 DRAFT 覆盖闸）。

### 1.2 文内自称 vs 盘上（勿采清单）

| 自称 | 盘上现算 | 采信 |
|---|---|---|
| dig 文内自称 `87f65bbe`（DRAFT） | **`440410de`** | **只采盘上 `440410de`**；自称 **勿采** |
| RECEIPT 自称产物钉 | 与盘上一致 | 采盘上；RECEIPT 自身以盘上 `691bbc14` 为准 |

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：ABCFO_Q1 期望 OCF 残差 → α∝−ε；截面质量残差 α（非 exclusion / 非 Top-N）；失效条件齐 | **PASS** | DRAFT §0/§2；RECEIPT 公式摘要；禁偷看 available_at>t；禁退化为叶19/25/34 |
| 2 | 不误撞主线/禁域（GP/高杠杆/卖方/金股/TP/LLM）；≠复开叶19/25/30–38；备选 CRR_MOD2/IO **不升 PRIMARY** | **PASS** | DRAFT §1 差表 + 文首禁项；备选维持不升 → **C5** |
| 3 | COUNT 闸：median/zero/J*/ρ* 与 JSON+RECEIPT+DRAFT 一致；gate_pass 成立；**勿把计数当 X2 ACCEPT** | **PASS_WITH_CONDITIONS** | §1.1 MATCH；APPROX 醒目 → **C2/C4** |
| 4 | vs 叶19/25/30 Jaccard/ρ 代理 ≪0.5 可接受；硬拒阈=0.5 写死 | **PASS_WITH_CONDITIONS** | J≈0.026/0/0；ρ≈−0.24/−0.11/−0.15；正式 ρ_excess → **C2** |
| 5 | peak_rss≈704.9≤1500；正式跑须维持 ≤1500 禁抬 | **PASS** | JSON/RECEIPT；→ **C4** |
| 6 | who_pays 职责边界清晰；交主裁升 FROZEN；不越权签跑 | **PASS** | DRAFT §6；ok_requested=false；本拍未签未挂未升 |
| 7 | DRAFT NOT FROZEN / 无构建脚本 / 无叶39 `.ok` / QUIET ABSENT | **PASS** | 文钉 + 盘证 §1 |
| 8 | 不混 fund MDD / 叶38；禁 RESTORED `f08ce32c` | **PASS** | 主令；盘证未触 → **C4** |
| 9 | HI_LIQ 主 + 银/地/非银硬掩码；窗意向 2024-06-03→2026-10-09 | **PASS** | DRAFT §4；JSON exclude_sw / window |
| 10 | vs 叶34 exclusion Jaccard 本拍未估诚实 PIN | **PASS_WITH_CONDITIONS** | RECEIPT APPROX/GAP → **C3** |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 DRAFT≠FROZEN；须主另令升 FROZEN**：本拍审的是 **DRAFT NOT FROZEN**。PASS ≠ 可签 `.ok`。Arch **本拍不升** FROZEN。请主择令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2；或 HOLD。
2. **C2 APPROX 钉清**：本拍=再平衡日 **截面 SW L1 OLS**（非年×行业历史面板）；ρ=**Spearman 代理**≠正式 ρ_excess。升 FROZEN / 开 X2 前须钉清：（a）是否升年×行业历史面板期望回归；（b）正式 ρ_excess（excess-return）替换代理；重钉后须重跑计数闸。
3. **C3 vs 叶34 exclusion Jaccard 本拍未估**：不挡本 DRAFT 覆盖闸，但须 **PIN**：升 FROZEN 前或 X2 前补估 vs 叶34 高应计剔除活跃集 Jaccard（硬拒阈同 0.5）；披露即可，勿事后改 PRIMARY 定义。
4. **C4 禁自签 `.ok` / 自开 X2·BS；不混 fund/叶38；rss≤1500**：禁 `--arch-ok-path` 自开；禁 RESTORED `f08ce32c`；禁混叶38 `c01c2034`/`5f694370`；正式跑 peak_rss **≤1500 禁抬**；无 peak_proof≤1500 不得申 `.ok`。轻量计数 ≠ X2 ACCEPT / Book-Smoke。
5. **C5 备选不升 PRIMARY**：CRR_MOD2 / IO 拥挤度维持备选；**不**升本叶 PRIMARY（DRAFT 已写；FROZEN 须维持）。

补充（对齐既有纪律，写入 FROZEN 时采纳）：
- **C6 正式构建脚本尚未写**：`research/leaf39*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；计数脚本 `20313ba3` ≠ α 构建。
- **C7 PIT / 公式冻结**：available_at≤t；YTD→单季差分；ABCFO_Q1=Roychowdhury CFO 模型；α∝−ε；银/地/非银硬掩码；禁偷看；禁冻结后改公式读收益。
- **C8 交付形态**：PRIMARY=截面质量残差 **α 向量**（非 exclusion mask 主交付；非 Top-N）；soft-penalty 若用须另钉且不替代 PRIMARY。
- **C9 轻量计数 ≠ X2 ACCEPT**：gate_pass 仅放行继续 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面 / 签 `.ok`。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算完整 α / 不开全窗 X2 / 不重跑计数脚本
- 不改 DRAFT / RECEIPT / COUNT / SCRIPT / JSON；不把 DRAFT 当 FROZEN；不把 COUNT 当 X2 ACCEPT；**不出 FROZEN**
- 不解阻 X2；≠Book-Smoke；**不抬** rss 意向 1500
- **不混** fund MDD CONSUME / RESTORED `f08ce32c`；**不混**叶38 `c01c2034`/`5f694370`；不触 leaf38 文件
- 不推 Leo；live=false；EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 5. 硬钉下一跳

```
who_pays DRAFT 542138d6 + RECEIPT 691bbc14 + JSON d0d11598
  + 脚本 20313ba3 + dig 440410de
  （本审 PASS_WITH_CONDITIONS；gate_pass=true；peak≈704.9≤1500）
  → 请主择令 AI 出 FROZEN 预注册
      （钉：ABCFO_Q1 公式 / HI_LIQ+银地非银 /
        Jaccard|ρ_excess>0.5 硬拒 /
        APPROX→是否升年×行业面板 + 正式 ρ_excess /
        vs 叶34 Jaccard PIN /
        残差α≠exclusion / 备选不升 PRIMARY /
        rss=1500 禁抬 / ≠X2 ACCEPT）
      或 HOLD
      → Arch 审 FROZEN / 正式脚本（另窗；research/leaf39* 现 ABSENT）
          → 独立新窗 .ok（禁 RESTORED f08ce32c；禁混叶38）
              → X2（正式 ρ_excess；叶34 Jaccard；peak_proof≤1500）
```

**本拍不签、不升 FROZEN**。**推荐主裁：出 FROZEN**（钉全 MATCH、gate_pass 与 JSON 一致、who_pays 可检验、APPROX/叶34 PIN 诚实、未越权签跑）。若主认为 APPROX（截面 OLS / Spearman）未钉清前不宜升纸，可 HOLD。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/完整 α / 计数脚本；**未改** DRAFT/RECEIPT/COUNT/JSON/SCRIPT；**未出** FROZEN
- **未混** fund MDD；**未触**叶38 `c01c2034`/`5f694370`；禁 RESTORED `f08ce32c` 未触
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED_full_alpha=false；EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 7. 结论

**PASS_WITH_CONDITIONS** — who_pays+COUNT DRAFT 契约可收；五钉 MATCH（DRAFT `542138d6` / RECEIPT `691bbc14` / JSON `d0d11598` / 脚本 `20313ba3` / dig `440410de`）；mechanism=`g1g5_ashare_abcfo_rem_resid_v1`（ABCFO 真实盈余管理残差 α）；COUNT 闸 gate_pass=true（masked median=2838.5；zero_frac=0；J/ρ≪0.5；peak≈704.9≤1500）；APPROX/叶34 PIN 诚实；禁项/旁线隔离齐。开放项见 §3（C1–C9），首要 **另窗 FROZEN（请主择令）** 与 **C2 APPROX 钉清** / **C3 叶34 Jaccard**。本回合不签、不挂、不代跑、不出 FROZEN、不混 fund/叶38。

live=false.
