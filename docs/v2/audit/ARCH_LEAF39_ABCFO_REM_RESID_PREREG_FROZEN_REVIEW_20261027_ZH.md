# Arch 审阅：叶39 ABCFO / 真实盈余管理残差 α PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-28T00:03:00-04:00`（America/New_York；墙钟 `2026-10-28 00:03 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数 / 正式脚本；不改 FROZEN/RECEIPT/DRAFT/COUNT/脚本字节；**不出 LAND**；**不自升**脚本/`.ok`；**不混** fund MDD HOLD CLOSED（Arch `ba7609af`/`fbc1bd9a`；`.ok` `335635dd` 已归档；禁 RESTORED `f08ce32c`/`335635dd`）；**不混**叶38 `c01c2034`/`5f694370`；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主令：AI PREREG_FROZEN READY **`150d1a28` MATCH** → Arch **只审本 FROZEN**（对照 ArchDRAFT `4a1b4dd0` COND C2–C5/C8/C9；禁签禁挂禁代跑） |

## 0. 一句话

FROZEN **`150d1a28`** / RECEIPT **`507f09f1`** / 上游 ArchDRAFT **`4a1b4dd0`** / DRAFT **`542138d6`** / DRAFT RECEIPT **`691bbc14`** / COUNT **`d0d11598`** / 脚本 **`20313ba3`** / dig **`440410de`**（自称 `87f65bbe` **勿采**）本机 sha256 **全 MATCH**；相对 DRAFT **已升格 PREREG_FROZEN**（非仍标 DRAFT）；mechanism=`g1g5_ashare_abcfo_rem_resid_v1`；**PRIMARY=截面质量残差 α 向量**（C8；**非** exclusion mask；**非** Top-N）；公式=YTD→单季后 CFO/A ~ 1/A+S/A+ΔS/A（**C2(a) 维持截面 SW L1 OLS APPROX；不升年×行业面板；未重跑计数**）→ ABCFO=ε → `α ∝ −ε`；HI_LIQ 主；银/地/非银硬掩码；窗 2024-06-03→2026-10-09；再平衡20；成本30bp；硬闸 vs 叶19/25/30 Jaccard∨ρ_excess>0.5 拒；**C2(b)** 正式 ρ_excess=@X2/LAND 前必须（Spearman 仅门控）；**C3** vs 叶34 Jaccard **PIN**（诚实未估；补估=Arch过审后/X2前；硬拒0.5；勿事后改 PRIMARY）；**C4** 禁自签/自开BS·X2；不混 fund HOLD·叶38；禁 RESTORED `f08ce32c`(+`335635dd`)；rss≤1500 + peak_proof REQUIRED；**C5** CRR_MOD2/IO 备选不升 PRIMARY；**C9** COUNT gate_pass≠X2 ACCEPT；COUNT 附录 gate_pass=true（median≈2838.5；zero_frac=0；J≈0.026/0/0；ρ≈−0.24/−0.11/−0.15；peak≈704.9≤1500）仅参考；`research/leaf39*` **ABSENT**；叶39 live `.ok` ABSENT；QUIET ABSENT；EXECUTED=false；**未**自申 `.ok` / **未**自派 LAND。开放余项：C3 叶34 Jaccard 仍 PIN；C2(b) ρ_excess 仍待；正式构建脚本另窗。**本拍不签、不出 LAND**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_20261027_ZH.md` | `150d1a28` | `150d1a2827c1284d6c1c890109a7a1e32ea0fb07925cc29959676b5816818d0f` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `507f09f1` | `507f09f19f8abbc3c8f1d44d765a724de4cc1e61e3f9811bfa1ed65d7d6b5c9a` | **MATCH** |
| Arch who_pays DRAFT 审 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `4a1b4dd0` | `4a1b4dd0ec9992a63466e31323828083dcd548663605a4c0eb4b99c1b609c06b` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `542138d6` | `542138d6893f820d98f9a5db91a3b99e55953829815226ce49a0f8b1a42e5882` | **MATCH** |
| DRAFT RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_RECEIPT_20261027_ZH.md` | `691bbc14` | `691bbc148780d88205a1f01996b2e6b662305d0bd868c652cb071aa70f6a52f9` | **MATCH** |
| COUNT JSON | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json` | `d0d11598` | `d0d115989805cd169ca9435de14a3795c18d2310366427170fb3a39e54d6abf8` | **MATCH** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_SCRIPT_20261027.py` | `20313ba3` | `20313ba3ea14ddaa9d328fa5177f33b15194d93b2135aec952395a252c0e8587` | **MATCH** |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_2330ET.md` | `440410de` | `440410de9b9a0e005d4c8021f93c26d120393c9109c645dbf92d7aa940add0d6` | **MATCH**；自称 `87f65bbe` **勿采** |
| 构建脚本 `research/leaf39*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶39 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF39*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH**（fund MDD 已归档旁线；本票不混） |
| fund MDD HOLD CLOSED | Arch / CONSUME / `.ok` | `ba7609af` / `fbc1bd9a` / `335635dd` | 主令 | **旁线不混**；禁 RESTORED |
| 叶38 旁线 | — | `c01c2034` / `5f694370` | 本拍未触 | **不混** |
| 禁 RESTORED | fund | `f08ce32c` (+`335635dd`) | 未触 | **禁触** |

对照模板：`docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md`（sha8 `01753ff4`）。

### 1.1 文内自称 vs 盘上（勿采清单）

| 自称 | 盘上现算 | 采信 |
|---|---|---|
| dig 文内自称 `87f65bbe` | **`440410de`** | **只采盘上 `440410de`** |

## 2. COND 入钉核验（相对 ArchDRAFT `4a1b4dd0` + 主令 C2–C5/C8/C9）

| # | 条件（主令 / ArchDRAFT） | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C2(a)** | 是否升年×行业历史面板 | §1.2：**维持截面 SW L1 OLS APPROX（不升面板）**；理由=与 COUNT `d0d11598`/脚本 `20313ba3` 一致 / 内存 / PDF 细节；**未重跑计数**；升面板须改公式+重跑+新 COUNT sha8 | **PASS 入钉** |
| **C2(b)** | 正式 ρ_excess 替换 Spearman | §1.2/§3：钉为 **X2/LAND 前必须**；本拍 Spearman 代理仅门控；硬拒阈仍 >0.5 | **PASS 入钉**（余项：正式 ρ 仍待 X2/LAND） |
| **C3** | vs 叶34 exclusion Jaccard 未估→PIN；硬拒 0.5；勿事后改 PRIMARY | §3/§3.1：**PIN（诚实）**；本拍不附补估；补估窗口=Arch 过审后 / X2 前；硬拒 0.5；禁事后改 PRIMARY | **PASS 入钉**（余项：补估仍 PIN） |
| **C4** | 禁自签/自开 BS·X2；不混 fund HOLD·叶38；禁 RESTORED；rss≤1500 | §5/§10：禁自签 `.ok`/自开 BS·X2/`--arch-ok-path`；不混 `ba7609af`/`fbc1bd9a`/`335635dd` / 叶38 `c01c2034`/`5f694370`；禁 RESTORED `f08ce32c`(+`335635dd`)；rss≤1500 禁抬；peak_proof≤1500 REQUIRED | **PASS 入钉** |
| **C5** | CRR_MOD2/IO 备选不升 PRIMARY | §6：两备选 **不升**；PRIMARY 维持 ABCFO 残差 α | **PASS 入钉** |
| **C8** | PRIMARY=截面质量残差 α 向量（非 exclusion；非 Top-N） | §1.3/§0：PRIMARY=**残差 α 向量**；明示非 mask / 非 Top-N；soft-penalty 不替代 | **PASS 入钉** |
| **C9** | 轻量计数 ≠ X2 ACCEPT | §4：gate_pass 仅放行讨论；**不解阻** ACCEPT / Book-Smoke / 签 `.ok` | **PASS 入钉** |

### 2.1 附加硬钉（主令重点核）

| 项 | 结果 | 证据 |
|---|---|---|
| 真正 PREREG_FROZEN（非仍标 DRAFT） | **PASS** | 文首状态 **PREREG_FROZEN**；冻结时点 23:58 ET；§15 状态钉 |
| who_pays / 公式可检验 | **PASS** | §0/§1.1：Roychowdhury ABCFO_Q1；YTD→单季；α∝−ε；伪代码写死 |
| mechanism 无静默改号 | **PASS** | `g1g5_ashare_abcfo_rem_resid_v1` 同 DRAFT/COUNT |
| HI_LIQ + 银/地/非银 + 窗/成本 | **PASS** | §2：HI_LIQ `c5433e80`；801780/801180/801790；窗 2024-06-03→2026-10-09；再平衡20；30bp |
| C2–C5/C8/C9 全文入钉且无漂移 | **PASS** | §11 对照表 + 本审 §2；与 `4a1b4dd0` COND 对齐；无改 PRIMARY/硬闸/掩码 |
| EXECUTED=false；未越权申 `.ok`/未自派 LAND | **PASS** | 文钉 + RECEIPT；`research/leaf39*` ABSENT；ok_requested=false |
| 上游字节未改（DRAFT/COUNT/脚本） | **PASS** | 本机 sha8 与期望全 MATCH；FROZEN 明示未改上游 |
| fund HOLD / 叶38 / RESTORED 隔离 | **PASS** | §5/§10；本拍未触 |
| ≠X2 ACCEPT；≠Book-Smoke | **PASS** | 文首 + §4 C9 + §14 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **C3 叶34 Jaccard 仍 PIN（脚本/X2 前补估）**：硬拒阈 0.5；补估结果只披露；**禁止**用补估事后改 PRIMARY 定义/方向。
2. **C2(b) 正式 ρ_excess 仍待 X2/LAND**：本拍 Spearman 代理不解阻；硬拒阈仍 >0.5。
3. **正式构建脚本另窗（下一跳首要）**：须钉本 FROZEN **`150d1a28`**；落 `research/leaf39_*`（截面 APPROX；PRIMARY=残差 α；HI_LIQ+银地非银；rss≤1500 + peak_proof）→ Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本 / 禁签 / 不出 LAND / 禁自开 X2**（交主择令 LAND_SCRIPT）。
4. **C9 维持**：COUNT gate_pass **≠** X2 ACCEPT / Book-Smoke / 签 `.ok`。
5. **C4 旁线隔离维持**：不混 fund MDD HOLD CLOSED（`ba7609af`/`fbc1bd9a`/`335635dd`）；不混叶38（`c01c2034`/`5f694370`）；禁 RESTORED `f08ce32c`/`335635dd`。
6. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；live=false；不报 Leo；**禁本拍签 `.ok`**。

缺 COND 硬钉才 FAIL/HOLD——本票 C2(a)(b)/C3/C4/C5/C8/C9 **均已入钉且无漂移**；余项仅为流程下一跳（首要 **正式脚本/LAND 另窗** + C3 补估 + C2(b)），故 **PASS_WITH_CONDITIONS**（非 FAIL / 非 HOLD）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算完整 α；**不重跑**计数脚本；不落 `research/leaf39*`
- 不改 FROZEN / RECEIPT / DRAFT / COUNT / 计数脚本；**不出 LAND**；不把本审当 X2 ACCEPT；不自开 Book-Smoke / X2
- **不混** fund MDD HOLD CLOSED；**不混**叶38；不碰 RESTORED `f08ce32c`/`335635dd`
- 不推 Leo；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false；SIGNED=false；QUIET=false；LAND=false

## 5. 硬钉下一跳 / 建议主裁

```
PREREG_FROZEN 150d1a28 + RECEIPT 507f09f1（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式构建脚本 research/leaf39_* / LAND_SCRIPT
      （钉本 FROZEN 150d1a28；C2(a) 截面 APPROX；PRIMARY=残差 α；
        HI_LIQ+银地非银；rss≤1500+peak_proof；禁自开 X2；禁混旁线）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED f08ce32c/335635dd；禁混叶38；须 peak_proof≤1500）
              → X2（正式 ρ_excess C2(b)；叶34 Jaccard 补估 C3；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

**本拍不签、不出 LAND、不自派**。**建议主裁：出正式构建脚本 / LAND_SCRIPT**（另窗；钉 FROZEN `150d1a28`；禁自开 X2；禁混 fund/叶38）。若主认为 C3 PIN 未补估前不宜开脚本窗，可 HOLD。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算**完整 α；**未重跑**计数脚本
- **未改** FROZEN / RECEIPT / DRAFT / COUNT / 脚本
- **未出 LAND**；**未自派**脚本窗；**未落** `research/leaf39*`
- **未混** fund MDD HOLD CLOSED；**未混**叶38；禁 RESTORED 未触
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false；SIGNED=false；QUIET=false；LAND=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（FROZEN `150d1a28` / RECEIPT `507f09f1` / ArchDRAFT `4a1b4dd0` / DRAFT `542138d6` / DRAFT RECEIPT `691bbc14` / COUNT `d0d11598` / 脚本 `20313ba3` / dig `440410de`；自称勿采）；COND C2(a)维持截面 APPROX / C2(b)ρ_excess@X2·LAND / C3 叶34 Jaccard PIN / C4 禁自签·旁线·rss / C5 备选不升 / C8 PRIMARY=残差 α / C9 计数≠ACCEPT **均已入钉无漂移**；who_pays/公式可检验；EXECUTED=false；脚本/`.ok`/QUIET ABSENT；未越权。开放余项见 §3（首要 **请主令 AI LAND_SCRIPT / 正式构建脚本**；仍 COND：C3 PIN、C2(b)、C9、禁本拍签 `.ok`）。**本回合不签、不挂、不代跑、不出 LAND、未写 leaf39 脚本、未混 fund/叶38**。

live=false.
