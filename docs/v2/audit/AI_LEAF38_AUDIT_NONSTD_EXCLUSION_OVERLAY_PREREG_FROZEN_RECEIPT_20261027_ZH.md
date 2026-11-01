# 叶38 非标审计意见剔除 overlay · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 20:50 ET（America/New_York；ISO `2026-10-27T20:50:00-04:00`）
- 动作：按主裁 **FROZEN GO** + Arch **PASS_WITH_CONDITIONS** `acba0865` 落 **PREREG_FROZEN**（C1–C13 入钉；**首要 C9 压峰**）
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf38*` / **未挂 QUIET** / **未** RESTORED forbid / **未** git commit / **未** SendToUser / **未**改 DRAFT 上游文 / **未**开 X2 / Book-Smoke / **未**夹带 fund_portfolio
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | **`ce0eb2ce`** | `ce0eb2ce9486778e229d2722a647b6fb37e90810df2ac9f1530054d8040b93ed` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `acba0865` | MATCH（`acba08650a034b7f40773a5a19923d529dcee0c0cabc6997ddee63501fe0caf2`） |
| WHO_PAYS DRAFT | `…WHO_PAYS_DRAFT…` | `16c1f70b` | MATCH（`16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c`） |
| COVER DRAFT | `…COVER_DRAFT…` | `7c3b8691` | MATCH（`7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea`） |
| COUNT RECEIPT（盘上） | `…COUNT_GATE_RECEIPT…` | `e82aefa2` | MATCH（`e82aefa24a158719e46acafa3933a33e2b78ca6ea674284f138d2b407087a20b`；文内 `7cc317d9` 勿采） |
| COUNT SCRIPT | `…COUNT_GATE_SCRIPT…` | `ba34da2a` | MATCH（`ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296`） |
| COUNT JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` | `2b3babb5` | MATCH（`2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750`） |
| dig | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | MATCH（`fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`；自称 `a6ddc4ef` 勿采） |

路径说明：落于 `docs/v2/audit/`（与叶34/35/37 同目录）。

## C1–C13 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册 | **FROZEN 全文**：mask-only；PIT 非标；厚度；X2 窗 2024-06-03→2026-10-09；成本 30bp；判定路径 |
| C2 | 正式脚本另窗 | `research/leaf38*` **ABSENT**；计数脚本 audit **`ba34da2a`**（非正式构建） |
| C3 | PIT / 非标定义 | `available_at→T1` + 最新 `is_non_standard=True`→mask=0；键=`ts_code`；禁偷看；禁用标准无保留当剔除 |
| C4 | soft-penalty / mask | **明示 mask-only PRIMARY**；soft-penalty 非 PRIMARY；另窗须 SW L1+logmv+style |
| C5 | 厚度阈冻结 | median≥**30** ∧ frac(≥10)≥**0.60** ∧ zero_frac≤**0.50**；禁改≥300/≥6；禁读收益改阈 |
| C6 | HI_LIQ 主 | HI_LIQ PRIMARY（mask hiliq_v1 `c5433e80`）；不得静默改 FULLA |
| C7 | X2 前完整重叠 | vs negevent/叶36 硬拒>0.5；vs 34/35/37（及必要时 18/24/27）披露；COUNT 轻量不替 |
| C8 | forbid | `57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；禁 `--arch-ok-path`；禁 RESTORED |
| C9 | **rss+压峰（首要）** | rss=1500 禁抬；peak_proof≤1500 REQUIRED；分进程/流式分块/降表示/单线程/超限硬 ABORT；无 peak_proof≤1500 不得申 `.ok` |
| C10 | 叶37 HOLD CLOSED + 旁线 | 禁复开叶37；fund_portfolio 不夹带 |
| C11 | overlay≠主叶 | 交付=负向 exclusion mask overlay；禁完整多空审计 α；禁换皮主输入 |
| C12 | COUNT≠X2 ACCEPT | gate_pass 仅放行讨论；**不解阻** ACCEPT / Book-Smoke / 签 `.ok` |
| C13 | decay KEEP | 近端=252d（≥126 才出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻**（`45dd87dc`） |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_audit_nonstd_exclusion_overlay_v1` |
| PIT | `available_at→T1`；最新非标 → mask=0；键=`ts_code` |
| C4 | **mask-only PRIMARY** |
| C5 厚度 | median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50 |
| C6 / 窗 / 成本 | HI_LIQ；2024-06-03→2026-10-09；30bp |
| C9 | rss=1500 禁抬；peak_proof≤1500；§6.1 压峰 |
| C11 | **≠** 完整多空审计 α 主叶 |
| 判定 | ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| COUNT 附录（不解阻） | median=48；frac_ge10=1.0；j≈0.056/0.065；peak≈1584 WATCH |

## 盘证（本拍后）

| 项 | 值 |
|---|---|
| `research/leaf38*` | **ABSENT** |
| live `.ok`（ai_factory 非 consumed/superseded） | **0**（本拍未申） |
| QUIET `output/loop/RESEARCH_QUIET.lock` | **ABSENT**（未挂） |
| 叶37 HOLD CLOSED | **不回撤**（`384fb9db`/`4afd5ae1`） |
| DRAFT 上游文 | **未改**（who/COVER/COUNT/JSON/SCRIPT） |
| fund_portfolio | **旁线未混** |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗（C2 正式 `research/leaf38*` 须含压峰）。≠X2 ACCEPT。勿报 Leo。fund recount 另排不夹本票。

live=false · EXECUTED=false · ok_requested=false.
