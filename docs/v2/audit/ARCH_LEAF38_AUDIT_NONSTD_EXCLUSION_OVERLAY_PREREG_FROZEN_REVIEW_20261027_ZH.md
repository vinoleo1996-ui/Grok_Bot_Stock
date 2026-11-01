# Arch 审阅：叶38 非标审计意见剔除 overlay PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T20:55:00-04:00`（America/New_York；墙钟 `2026-10-27 20:55 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数；不改 FROZEN/RECEIPT/WHO/COVER/COUNT/脚本/JSON；**不出 LAND**；**不触** A18；叶37 HOLD CLOSED（Alpha `384fb9db` / Arch `4afd5ae1`）不回撤；叶36/35/34/33/32/`45dd87dc` HOLD 不回撤；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo**；旁线 fund_portfolio **不混本票** |
| 触发 | 主令：AI PREREG_FROZEN READY MATCH → 令 Arch **只审本 FROZEN**（对照 DRAFT 审 `acba0865` C1–C13；禁签禁挂禁代跑不出 LAND） |

## 0. 一句话

FROZEN **`ce0eb2ce`** / RECEIPT **`bb8051bd`** / 上游 Arch DRAFT 审 **`acba0865`** / WHO **`16c1f70b`** / COVER **`7c3b8691`** / JSON **`2b3babb5`** / COUNT 盘上 **`e82aefa2`**（文内自称 `7cc317d9` **勿采**）/ 脚本 **`ba34da2a`** / dig **`fa973826`**（自称 `a6ddc4ef` **勿采**）本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**（非仍标 DRAFT）；mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；**PRIMARY=mask-only** 负向 exclusion overlay（最新非标审计意见 PIT → mask=0）；soft-penalty **明示非 PRIMARY**；**≠完整多空审计 α 主叶**（C11）；PIT `available_at→T1` + 最新 `is_non_standard=True`；键=`ts_code`（C3）；厚度 median≥**30** ∧ frac(≥10)≥**0.60** ∧ zero_frac≤**0.50**（**勿盲抄** 300；C5）；vs negevent/叶36 Jaccard **>0.5 硬拒**（C7）；**C9** rss=**1500 禁抬** + peak_proof≤**1500** REQUIRED + **§6.1 压峰**（分进程/流式/降表示/单线程/硬 ABORT）写死；COUNT peak≈1584 仅 WATCH 参考；decay KEEP 三闸 + **KEEP≠ACCEPT**（C13；`45dd87dc`）；C12 gate_pass≠X2 ACCEPT；C1–C13 全文入钉且与 `acba0865` §3 对齐；`research/leaf38*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false；**未**自申 `.ok` / **未**自派 LAND_SCRIPT。开放余项：正式构建脚本另窗（C2；须含 §6.1）。**本拍不签、不出 LAND**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `ce0eb2ce` | `ce0eb2ce9486778e229d2722a647b6fb37e90810df2ac9f1530054d8040b93ed` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `bb8051bd` | `bb8051bd00d5b7ff30a017eaced668d26b3c60de8f1fb1139eedba49b445efeb` | **MATCH** |
| Arch who_pays DRAFT 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `acba0865` | `acba08650a034b7f40773a5a19923d529dcee0c0cabc6997ddee63501fe0caf2` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `16c1f70b` | `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `7c3b8691` | `7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea` | **MATCH** |
| COUNT RECEIPT（盘上） | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `e82aefa2` | `e82aefa24a158719e46acafa3933a33e2b78ca6ea674284f138d2b407087a20b` | **MATCH 盘上**；文内自称 `7cc317d9` **勿采** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `ba34da2a` | `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` | `2b3babb5` | `2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750` | **MATCH** |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101` | **MATCH**；自称 `a6ddc4ef` **勿采** |
| HI_LIQ mask（文钉） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | 前8 MATCH | **MATCH** |
| 叶37 HOLD CLOSED | Alpha / Arch | `384fb9db` / `4afd5ae1` | 主令 | **不回撤**；禁复跑 `015e6f06`/`32605aca`/`108aba8f` |
| 叶32 HOLD（只读） | KEEP≠ACCEPT | `45dd87dc` | 主令 | **不回撤** |
| 禁 RESTORED | — | `57ab9096`+`b5be1164`+`4096d401`+ | 主令 | **禁触** |
| 构建脚本 `research/leaf38*` | — | ABSENT | ABSENT | **MATCH 预期**（C2） |
| 叶38 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF38*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |

对照模板：叶37 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md`（sha8 `a5a9336d`）；叶34/35 FROZEN 审形态。

### 1.1 文内自称 vs 盘上（勿采清单）

| 自称 | 盘上现算 | 采信 |
|---|---|---|
| COUNT RECEIPT 文内 `7cc317d9` | **`e82aefa2`** | **只采盘上 `e82aefa2`** |
| dig 文内自称 `a6ddc4ef` | **`fa973826`** | **只采盘上 `fa973826`** |

## 2. C1–C13 对照表（相对 Arch DRAFT 审 `acba0865` §3）

| # | DRAFT 审条件（`acba0865`） | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C1** | 另窗冻结完整预注册 | 文首状态 **FROZEN**；冻结时点 20:50 ET；明示「冻结前**未**读任何本叶收益选定义/方向」；§0–§16 全文；相对 who/COVER/COUNT DRAFT **升格** | **PASS** |
| **C2** | 正式脚本另窗；计数非正式构建 | 文首+§14：本冻结 ≠ 构建脚本；`research/leaf38*` **ABSENT**（本拍禁落）；计数脚本 audit **`ba34da2a`**（非正式 α）；脚本另窗须含 §6.1 | **PASS_WITH_CONDITIONS**（余项：另窗落正式脚本） |
| **C3** | PIT / 非标定义冻结 | §1.1：`available_at→T1`（严格次一交易日）+ 最新 `is_non_standard=True`→mask=0；下一份意见 T1 改判；键=`ts_code`；禁偷看；禁用标准无保留当剔除 | **PASS** |
| **C4** | soft-penalty / mask-only | §1.2/§3：**明示 mask-only PRIMARY**；连续 soft-penalty **非 PRIMARY**；启用须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP | **PASS** |
| **C5** | 厚度阈冻结纪律 | §2/§4：median≥**30** ∧ frac(≥10)≥**0.60** ∧ zero_frac≤**0.50**；禁改≥300/≥6；禁读收益改阈；**勿盲抄** 300 | **PASS** |
| **C6** | HI_LIQ 主判决 + 窗 | §5/§6：HI_LIQ_V1.1 PRIMARY（mask `c5433e80`）；窗意向 2024-06-03→2026-10-09；成本 30bp；不得静默改 FULLA | **PASS** |
| **C7** | X2 前完整重叠；COUNT 不替 | §4：vs negevent/叶36 Jaccard **>0.5 硬拒**；vs 34/35/37（及必要时 18/24/27）披露；COUNT 轻量不替正式重叠 | **PASS** |
| **C8** | forbid 全集；禁复用旧 `.ok` | §10：forbid∋`57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；禁 `--arch-ok-path`；禁 RESTORED | **PASS** |
| **C9** | **rss=1500 + 压峰硬条件（首要）** | §6 + **§6.1**：rss=**1500 禁抬**；peak_proof≤**1500** REQUIRED；分进程/流式分块/降表示/单线程/超限硬 ABORT；无 peak_proof≤1500 不得申 `.ok`；COUNT peak≈1584 仅 WATCH | **PASS**（见 §2.1） |
| **C10** | 叶37 HOLD CLOSED + 旁线不混 | §11：禁复开叶37；禁复跑叶37 脚本/基盘；fund_portfolio **旁线不夹带**；叶32 `45dd87dc` / 叶35/33 不回撤 | **PASS（未审声明）** |
| **C11** | overlay ≠ 主叶硬钉 | §1.2/§9/§12：交付=负向 exclusion mask overlay 叠主干；**禁**完整多空审计 α 主叶；禁 ETF/应计/问询函/IMAX/negevent 换皮主输入 | **PASS** |
| **C12** | 轻量计数 ≠ X2 ACCEPT | §0/§6/§13/§14：gate_pass 仅放行 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 签 `.ok` | **PASS** |
| **C13** | decay KEEP；KEEP 不解阻 | §7：近端=**252**d（≥126 才出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（`45dd87dc` / 叶37 教训） | **PASS** |

### 2.1 C9 压峰专节（rss=1500 禁抬；peak_proof≤1500；§6.1 写死）

| 项 | FROZEN 落点 | 结果 |
|---|---|---|
| rss 意向 | **1500** MB **禁抬**；超限 → **硬 ABORT**；**禁止**改成 1600/1800「先跑通」 | **PASS** |
| peak_proof | **REQUIRED**：正式 X2 / 申 `.ok` 前须 **peak_proof≤1500**；无则不得申 `.ok` / 开 X2 | **PASS** |
| COUNT peak 参考 | ≈**1584** MB **WATCH**（仅参考；计数脚本非正式构建；**不解阻**） | **PASS（WATCH 维持）** |
| §6.1.1 分进程 | overlay mask 构建与 negevent/叶36 Jaccard **分进程**（或预落 pair 再只读）；禁同进程叠全帧 | **PASS 写死** |
| §6.1.2 流式/分块 | parquet 按日期块/row-group；`mask_all`→`mask_by` 后 `del`+`gc`；审计表建完 excl 后释放 | **PASS 写死** |
| §6.1.3 降表示 | categorical / 内部 int id；Jaccard `(date,inst)` 紧凑磁盘格式；勿巨型 Python set 长驻 | **PASS 写死** |
| §6.1.4 单线程 | 禁并行 worker 叠 RSS；单进程墙内 ≤1.5GB | **PASS 写死** |
| §6.1.5–6 硬 ABORT + peak_proof | peak>1500 → 硬 ABORT；正式窗须回传 `peak_rss_mb≤1500` | **PASS 写死** |

**结论（C9）**：DRAFT 审 `acba0865` §2.1/C9 首要硬条件已**全文入钉** FROZEN §6+§6.1；rss=1500 **未抬**；peak_proof≤1500 **REQUIRED**；压峰五路径写死。本拍**不**因 COUNT peak≈1584 降为 HOLD（属已知 WATCH + 脚本窗条件，非缺硬钉）。正式 `research/leaf38*` 必须落地 §6.1 并回传 peak_proof≤1500。

### 附加硬钉（主令重点核）

| 项 | 结果 | 证据 |
|---|---|---|
| 真正 FROZEN（非仍标 DRAFT） | **PASS** | 文首状态 **FROZEN**；冻结时点 20:50 ET；§16 状态钉 |
| mask-only 负向 overlay ≠ 主叶 / ≠完整多空 α | **PASS** | §0/§1.2/§9/§12 C11；RECEIPT 机制钉 |
| PIT T1 生效口径写死 | **PASS** | §1.1 C3：`available_at→T1`；最新非标→mask=0；键=`ts_code` |
| 厚度阈（median≥30 等；勿盲抄 300） | **PASS** | §2/§4/§12 C5；COUNT 附录 median=48 过闸仅参考 |
| 同构硬拒（Jaccard >0.5） | **PASS** | §4 C7；COUNT Jmax≈0.056/0.065 ≪0.5 仅参考 |
| **C9** rss=1500 禁抬 + peak_proof + §6.1 | **PASS** | §2.1 本审专节 |
| decay KEEP≠ACCEPT；≠X2 ACCEPT | **PASS** | §7 C13；§13/§14 C12 |
| `research/leaf38*` ABSENT；live `.ok` ABSENT；QUIET ABSENT | **PASS** | 盘证 §1 |
| C1–C13 完整入钉且与 `acba0865` 对齐 | **PASS** | §12 对照表 + 本审 §2 |
| 未越权申 `.ok` / 未自派 LAND_SCRIPT | **PASS** | 文钉 ok_requested=false；LAND_SCRIPT 出现次数=0；下一跳交主 |
| 叶37 HOLD CLOSED / 禁 RESTORED / 旁线不混 | **PASS** | §10/§11；本拍未触 |
| 机制与 who/COVER 无静默改号 | **PASS** | 同 tag；mask-only；厚度 30；PIT T1；窗同 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗（C2；下一跳首要）**：须钉本 FROZEN **`ce0eb2ce`**；落 `research/leaf38_*`（**必须含 §6.1 压峰**；目标 peak_proof≤1500）→ Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本 / 禁签 / 不出 LAND**（交主择令 LAND_SCRIPT）。
2. **X2 独立签窗**：完整 overlay；vs negevent（含 E1 若可行）与叶36（硬拒>0.5）及 **34/35/37**（披露）Jaccard/ρ **重算**；rss+**peak_proof≤1500**；decay KEEP 硬验收；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+；禁复跑叶37；禁 `--arch-ok-path`；**KEEP 不解阻** X2 ACCEPT。
3. **PRIMARY 纪律**：判决=HI_LIQ mask-only；不得静默改 FULLA；soft-penalty 启用须另窗+SW+style。
4. **C9 脚本落地纪律**：脚本须采纳 §6.1 五路径；超限硬 ABORT；**禁止**抬 rss 意向；无 peak_proof≤1500 **不得**申 `.ok`。
5. **C11 脚本落地纪律**：交付须为负向 exclusion mask overlay；禁完整多空审计 α；禁换皮主输入。
6. **C10 仍另队**：叶37 HOLD CLOSED 不复开；fund_portfolio recount **不夹带**；`0087c928` / 叶28/29 不得借本窗夹带。
7. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；COUNT gate_pass / peak≈1584 WATCH **不解阻**；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C13 **均已入钉**（含首要 **C9**）；余项仅为流程下一跳（首要 **C2 正式脚本另窗 + 压峰落地**），故 **PASS_WITH_CONDITIONS**（非 FAIL / 非 HOLD）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算完整 α；**不重跑**计数脚本
- 不改 FROZEN / RECEIPT / WHO / COVER / COUNT / 计数脚本 / JSON；不落构建脚本；**不出 LAND**；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke；**不抬** rss 意向 1500
- 不复开叶37；不夹带 fund_portfolio；不回撤叶37/36/35/34/33/32 HOLD；不碰 RESTORED `57ab9096+b5be1164+4096d401+`；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN ce0eb2ce + RECEIPT bb8051bd（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf38_*
      （钉本 FROZEN ce0eb2ce；mask-only PRIMARY；PIT T1；厚度 median≥30；
        **§6.1 压峰 + rss=1500 禁抬 + peak_proof≤1500**；C11≠主叶）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED 57ab9096+b5be1164+4096d401+；禁复跑叶37；须 peak_proof≤1500）
              → X2（完整重叠含 negevent/36/34/35/37；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

**本拍不签、不出 LAND、不自派**。**推荐主裁：令 AI LAND_SCRIPT**（C1–C13 入钉完整；开放项属 C2 脚本窗 + C9 压峰落地，而非硬缺陷）。若主认为 peak WATCH 未解前不宜开脚本窗，可 HOLD。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算**完整 α；**未重跑**计数脚本
- **未改** FROZEN / RECEIPT / WHO_PAYS / COVER / COUNT / 计数脚本 / JSON
- **未出 LAND**；**未自派**脚本窗
- **未复开**叶37；**未夹带** fund_portfolio；**未落** `research/leaf38*`
- 叶37 HOLD CLOSED（`384fb9db`/`4afd5ae1`）/ 叶32 HOLD **`45dd87dc`** 只读不回撤；禁 RESTORED 未触
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false；SIGNED=false；QUIET=false；LAND=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（FROZEN `ce0eb2ce` / RECEIPT `bb8051bd` / 上游审 `acba0865` / who `16c1f70b` / COVER `7c3b8691` / JSON `2b3babb5` / COUNT 盘上 `e82aefa2` / 脚本 `ba34da2a` / dig `fa973826`；自称勿采）；C1–C13 对照齐且与 DRAFT 审条件对齐；PRIMARY=mask-only 负向 overlay ≠主叶；PIT T1 写死；厚度 median≥30（勿盲抄 300）；Jaccard>0.5 硬拒；**C9** rss=1500 禁抬 + peak_proof≤1500 + §6.1 压峰五路径写死（COUNT peak≈1584 WATCH 维持、不解阻）；decay KEEP≠ACCEPT；C12≠X2 ACCEPT；forbid/叶37 CLOSED/旁线隔离齐；脚本/`.ok`/QUIET ABSENT；未越权申 `.ok`/未自派 LAND。开放余项见 §3（首要 **请主令 AI LAND_SCRIPT**，须含 §6.1）。**本回合不签、不挂、不代跑、不出 LAND、未写 leaf38 脚本**。

live=false.
