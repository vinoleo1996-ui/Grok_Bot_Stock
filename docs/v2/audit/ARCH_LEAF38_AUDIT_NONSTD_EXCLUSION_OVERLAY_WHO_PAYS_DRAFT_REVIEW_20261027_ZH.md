# Arch 审阅：叶38 非标审计意见剔除 overlay who_pays + COVER + COUNT（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T20:45:00-04:00`（America/New_York；墙钟 `2026-10-27 20:45 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数脚本；不改 DRAFT/脚本/COUNT/JSON；**不出 FROZEN**；不触 A18；叶37 HOLD CLOSED（Alpha `384fb9db` / Arch `4afd5ae1`）不回撤；叶36/35/34/33/32/`45dd87dc` HOLD 不回撤；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo**；旁线 fund_portfolio FAIL **不混本票** |
| 触发 | 主令：AI dig 下一叶 DONE MATCH → 令 Arch **只审叶38** 非标审计剔除 overlay DRAFT |

## 0. 一句话

WHO **`16c1f70b`** / COVER **`7c3b8691`** / JSON **`2b3babb5`** / COUNT RECEIPT 盘上 **`e82aefa2`**（文内自称 `7cc317d9` **勿采**）/ 计数脚本 **`ba34da2a`** 本机 sha256 **MATCH**；PRIMARY=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1` 可检验（最新可用审计意见 `is_non_standard=True` → PIT T1 生效 → 日度 **exclusion mask** 叠 capacity_adv / HI_LIQ；**负向 overlay 非主线**；**非**完整多空 α 主叶）；厚度闸写死 median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50（**勿盲抄** median≥300；叶36 median=6 FAIL 教训）；COUNT 闸 **gate_pass=true**：median=**48.0**；frac_ge10=**1.0**；zero_frac=**0.0**；Jmax vs negevent≈**0.0562** / vs 叶36≈**0.0649** ≪0.5；hard_reject_jaccard=false；**peak_rss≈1584.4MB >1500 → WATCH**（rss 意向 **1500 禁抬**；正式 X2 前须压峰，见 §3.C9）；APPROX 披露诚实（negevent 无 E1；叶36 同漏斗重建；**≠X2 ACCEPT**）；HI_LIQ 主；禁卖方/金股/survey/TP/LLM/GP/高杠杆/复跑叶18/24/25/27/30–37；DRAFT **NOT FROZEN** / EXECUTED_full_alpha=false / ok_requested=false；`research/leaf38*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；dig 盘上 **`fa973826`**（文内自称 `a6ddc4ef` **勿采**）。开放项见 §3（须另窗 FROZEN；**压峰硬条件**；完整重叠补算）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `16c1f70b` | `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `7c3b8691` | `7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` | `2b3babb5` | `2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `e82aefa2`（主钉盘上） | `e82aefa24a158719e46acafa3933a33e2b78ca6ea674284f138d2b407087a20b` | **MATCH 盘上**；文内自称 `7cc317d9` **勿采** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `ba34da2a` | `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296` | **MATCH** |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | 前8 MATCH | **MATCH**；WHO 文内自称 `a6ddc4ef` **勿采** |
| 叶37 HOLD CLOSED | Alpha / Arch | `384fb9db` / `4afd5ae1` | 主令 | **不回撤**；禁复跑 `015e6f06`/`32605aca`/`108aba8f` |
| 叶32 HOLD（只读） | KEEP≠ACCEPT | `45dd87dc` | 主令 | **不回撤** |
| 禁 RESTORED | — | `57ab9096`+`b5be1164`+`4096d401`+ | 主令 | **禁触** |
| 构建脚本 `research/leaf38*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶38 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF38*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md`（sha8 `4a074f0a`）；叶34 who_pays 审（高应计剔除 overlay）。

### 1.1 COUNT 闸数字再核（JSON ↔ COUNT ↔ who_pays ↔ COVER）

| 指标 | JSON | COUNT / WHO / COVER | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| gate_cov_pass | true | true（median=48.0；frac_ge10=1.0；zero_frac=0.0） | **MATCH** |
| median（触窗剔除名全日） | 48.0 | 48.0 | **MATCH**（≥30） |
| frac_days_excl_ge10 | 1.0 | 1.0 | **MATCH**（≥0.60） |
| zero_frac_masked | 0.0 | 0.0 | **MATCH**（≤0.50） |
| jaccard_max_vs_negevent | 0.056179775280898875 | ≈0.0562 / 0.056180 | **MATCH**（≪0.5） |
| jaccard_max_vs_leaf36 | 0.06493506493506493 | ≈0.0649 / 0.064935 | **MATCH**（≪0.5） |
| hard_reject_jaccard | false | false | **MATCH** |
| peak_rss_mb | 1584.37890625 | 1584.4 | **MATCH**（**>1500 → WATCH**） |
| mechanism_tag | g1g5_ashare_audit_nonstd_exclusion_overlay_v1 | 同 | **MATCH** |
| delivery | daily_exclusion_mask_overlay_NOT_mainline_alpha | 形态 A mask-only；非主线 | **MATCH** |
| APPROX | approx[] 非空（无 E1；叶36 重建；ts_code 映射） | APPROX/GAP 醒目 | **MATCH**（诚实） |
| ok_requested / x2_run / book_smoke / live | false | false | **MATCH** |
| EXECUTED_full_alpha | （未申） | false | **MATCH** |

附注：厚度阈写死 median≥30（非 300）有叶36 FAIL 论证；本拍实测 48 过闸属机制预期（年报级 PIT 状态厚于问询函短窗）。Jaccard 轻量 APPROX ≠ 正式 X2 完整重叠证明 → **C7**。未算 vs 叶34/35/37 → GAP / **C7**。

### 1.2 文内自称 vs 盘上（勿采清单）

| 自称 | 盘上现算 | 采信 |
|---|---|---|
| COUNT RECEIPT 文末 `7cc317d9` | **`e82aefa2`** | **只采盘上 `e82aefa2`**；文内自称 **勿采** |
| dig 文内自称 `a6ddc4ef`（WHO） | **`fa973826`**（`DIG_FACTOR_20261027_2026ET.md`） | **只采盘上 `fa973826`**；自称 **勿采** |

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：审计非标 PIT 最新意见 → mask=0；形态 A 日度 exclusion mask 叠主干（**非**完整多空 α）；失效条件齐 | **PASS** | WHO §0/§2/§3；COVER 一句话；禁事后改定义/偷看 available_at>t |
| 2 | **mask-only 负向 overlay**；不误撞主线/禁域（GP/高杠杆/live/卖方/金股/TP/LLM）；≠复开叶36/37 | **PASS** | WHO §1 差表 + 文首禁项；tag 非主线；叶37 HOLD CLOSED 不回撤 |
| 3 | COUNT 闸：median/frac_ge10/zero/J* 与 JSON+RECEIPT 一致；gate_pass 成立；**勿把计数当 X2 ACCEPT** | **PASS_WITH_CONDITIONS** | §1.1 MATCH；APPROX 醒目 → **C12** |
| 4 | vs negevent / 叶36 Jaccard≪0.5 可接受；硬拒阈=0.5 写死 | **PASS_WITH_CONDITIONS** | J≈0.056 / 0.065；完整重叠 + vs 34/35/37 → **C7** |
| 5 | **peak_rss≈1584>1500 WATCH**：已披露；压峰路径可落地；**禁抬** rss=1500；正式 X2 前必须过 | **PASS_WITH_CONDITIONS** | WHO §3/§5；COVER；JSON；压峰专节 §2.1 + **C9** |
| 6 | who_pays 职责边界清晰；COVER 与 who 一致；不越权签跑 | **PASS** | WHO §6 交主裁 A/B/C；COVER 钉路径齐；ok_requested=false；本拍未签未挂 |
| 7 | DRAFT NOT FROZEN / 无构建脚本 / 无 `.ok` / QUIET ABSENT | **PASS** | 文钉 + 盘证 §1 |
| 8 | 禁 RESTORED `57ab9096+b5be1164+4096d401+`；禁复跑叶37 脚本/基盘；叶32 `45dd87dc` KEEP≠ACCEPT | **PASS** | 主令；→ **C8** |
| 9 | 旁线 fund_portfolio FAIL 不混本票 | **PASS** | WHO 文首/§1/§6；主令另令 Data；本审不夹带 |
| 10 | HI_LIQ 主；窗 2024-06-03→2026-10-09 意向；输入 sha8 披露 | **PASS_WITH_CONDITIONS** | WHO §4；FROZEN 写死 → **C6** |

### 2.1 peak WATCH 专节（正式 X2 前压峰路径；禁抬 rss=1500）

| 项 | 值 |
|---|---|
| 本拍计数 peak_rss_mb | **1584.4**（JSON `1584.37890625`） |
| rss 意向 | **1500**（硬 ABORT 阈；**禁抬**） |
| 状态 | **WATCH** — 闸数字可过，但 **peak 超意向**；**不解阻** `.ok` / X2 |
| 计数脚本已做 | `gc.collect` / `del` 大帧；parquet 列裁剪；ru_maxrss 采峰 |

**正式构建 / X2 前必须落地的压峰路径（可检验；写死进 FROZEN/脚本审）：**

1. **分进程**：overlay mask 构建与 negevent/叶36 Jaccard 重建 **分进程**（或预落 pair 集再只读加载）；禁止同一进程同时持有 CAP_ADV+NEGEVENT_W 全帧 + ANN_MAIN/POST + HI_LIQ mask_by + excl 大 dict。
2. **流式/分块**：HI_LIQ / 权重 / 公告 parquet 按日期块或 row-group 过滤读入；`mask_all` 建成 `mask_by` 后立即 `del`+`gc`；审计表建完 excl 后立即释放。
3. **降表示**：instrument 用 categorical / 内部 int id，避免海量 `str`×`set` 双份；Jaccard 对照用磁盘上的 `(date,inst)` 紧凑格式，勿长期驻留巨型 Python set。
4. **单线程**：禁并行 worker 叠 RSS；单进程墙内 ≤1.5GB。
5. **peak_proof**：正式窗必须回传 `peak_rss_mb≤1500` 证明；超限 → **硬 ABORT**，**禁止**把意向改成 1600/1800「先跑通」。
6. **本拍计数 peak 仅参考**：COUNT 脚本 `ba34da2a` **不是** α 构建；压峰改造落在未来 `research/leaf38*`（现 ABSENT），另窗 Arch 审脚本时复核。

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31–37 who_pays）。PASS ≠ 可签 `.ok`。请主择令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2；或 HOLD。
2. **C2 正式构建脚本尚未写**：`research/leaf38*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。计数脚本 `ba34da2a` 已落 audit；正式构建勿把计数脚本当 α 构建。
3. **C3 PIT / 非标定义冻结**：`available_at→T1`（严格次一交易日）+ 最新意见 `is_non_standard=True` → mask=0；下一份意见 T1 改判；映射键=`ts_code`（禁 `instrument_id` 硬拼）。FROZEN 写死；**禁**用标准无保留当剔除；**禁**偷看 `available_at>t`。
4. **C4 mask-only 主路径**：交付=日度 exclusion mask 叠主干；若日后选 soft-penalty=`-1`，须另钉 SW+style 残差并重审。本拍 soft-penalty 未做 → FROZEN 明示「mask-only」。
5. **C5 厚度阈冻结纪律**：median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50 写死；**禁**事后改成 median≥300 或放宽到 median≥6；**禁**读收益改阈。
6. **C6 HI_LIQ 主判决 + 窗**：PRIMARY 宇宙=HI_LIQ；X2 样内窗意向 2024-06-03→2026-10-09；不得静默改 FULLA 当主。
7. **C7 X2 前完整重叠重算**：须用完整 overlay 重算 vs negevent（含 E1 若可行）与叶36（硬拒>0.5）；并披露 vs 叶34/35/37（及必要时 18/24/27）；DRAFT 轻量计数 **不能**替正式重叠证明。
8. **C8 禁 RESTORED / 禁复用旧窗**：forbid∋`57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；禁复用叶18/24/27/30–37 `.ok`；禁 `--arch-ok-path` 自开。
9. **C9 rss=1500 + 压峰硬条件（本票首要）**：rss 意向 **1500 禁抬**；正式执行窗 peak>1500 → **硬 ABORT**。FROZEN/脚本须采纳 §2.1 压峰路径（分进程/流式分块/降表示/单线程/peak_proof）；**无 peak_proof≤1500 不得申 `.ok` / 开 X2**。本拍计数 peak≈1584 仅 WATCH 参考。
10. **C10 叶37 HOLD CLOSED + 旁线不混**：禁复开叶37 IMAX/彩票主轴；禁改叶37 产物；fund_portfolio FAIL 另由 Data 补 fund_basic，**不夹带**本票。
11. **C11 overlay ≠ 主叶硬钉**：FROZEN/脚本须钉交付=**负向 exclusion mask overlay**；**禁**输出完整多空审计事件 α 主叶；禁把 ETF/应计/问询函/IMAX/negevent 换皮当本叶主输入。
12. **C12 轻量计数 ≠ X2 ACCEPT**：gate_pass 仅放行继续 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面 / 签 `.ok`。
13. **C13 decay KEEP 冻结口径**：预注册写死近端窗与 KEEP 条件；失败 → 最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc` / 叶37 HOLD 教训）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算完整 α / 不开全窗 X2 / 不重跑计数脚本
- 不改 WHO / COVER / COUNT / SCRIPT / JSON DRAFT；不把 DRAFT 当 FROZEN；不把 COUNT 当 X2 ACCEPT；不出 FROZEN
- 不触 A18；不解阻 X2；≠Book-Smoke；**不抬** rss 意向 1500
- 不回撤叶37/36/35/34/33/32 HOLD；不碰 RESTORED `57ab9096+b5be1164+4096d401+`；不推 Leo；live=false
- 旁线 fund_portfolio 不混；EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 5. 硬钉下一跳

```
who_pays DRAFT 16c1f70b + COVER 7c3b8691 + JSON 2b3babb5
  + COUNT 盘上 e82aefa2（文内 7cc317d9 勿采）/ 脚本 ba34da2a
  （本审 PASS_WITH_CONDITIONS；gate_pass=true；peak≈1584 WATCH）
  → 请主择令 AI 出 FROZEN 预注册
      （钉：mask-only / PIT 非标定义 / 厚度阈 / 同构硬拒 /
        **压峰路径§2.1 + rss=1500 禁抬 + peak_proof** /
        overlay≠主叶 / ≠X2 ACCEPT）
      或 HOLD
      → Arch 审 FROZEN / 正式脚本（另窗；research/leaf38* 现 ABSENT；脚本须含压峰）
          → 独立新窗 .ok（禁 RESTORED 57ab9096+b5be1164+4096d401+；禁复跑叶37）
              → X2（完整重叠；peak_proof≤1500；decay KEEP）
```

**本拍不签**。**推荐主裁：出 FROZEN**（闸已过、同构/厚度/负向 overlay 边界诚实；**开放首要=压峰写死**，属冻结/脚本条件而非硬缺陷）。若主认为 peak WATCH 未解前不宜升纸，可 HOLD。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/完整 α / 计数脚本；**未改** DRAFT/COUNT/JSON/SCRIPT；**未出** FROZEN
- 叶37 HOLD CLOSED（`384fb9db`/`4afd5ae1`）/ 叶32 `45dd87dc` 只读不回撤；禁 RESTORED 未触
- 旁线 fund_portfolio 未混；**不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED_full_alpha=false；EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 7. 结论

**PASS_WITH_CONDITIONS** — WHO+COVER+COUNT DRAFT 契约可收；五钉 MATCH（COUNT 采盘上 `e82aefa2`，文内 `7cc317d9` 勿采；dig 采 `fa973826`，自称 `a6ddc4ef` 勿采）；机制=审计非标 PIT **mask-only 负向 overlay 非主线**；COUNT 闸 gate_pass=true（median=48；frac_ge10=1.0；J≪0.5）；**peak≈1584→WATCH**（§2.1 压峰路径；rss=1500 禁抬）；禁项/forbid/叶37 CLOSED/旁线隔离齐。开放项见 §3（C1–C13），首要 **另窗 FROZEN（请主择令）** 与 **C9 压峰硬条件**。本回合不签、不挂、不代跑、不出 FROZEN。

live=false.
