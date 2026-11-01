# Arch 审阅：叶33 SHARE_UNLOCK_PRESSURE_RESID · coverage/稀疏事件口径复议（只审不改不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审复议草案） |
| 时刻 | `2026-10-27T07:52:51-04:00`（America/New_York；墙钟 `2026-10-27 07:52 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | VOID **`6826c01d`** · RUN **`a1b426f5`** · alpha **`ea17e173`** · overlap **`473b339e`** · meta **`f4702783`** · 脚本 **`afbbe7e7` UNCHANGED** · FROZEN **`8ed43721`** · PIN **`4e17ccfc`** · FROZEN审 **`bf5234a9`** |
| 本回合动作 | **不改** gate=`COVERAGE_MEDIAN_HILIQ=300`；**不改**脚本字节；**不签**任何 `.ok`；**不挂** QUIET；**不代跑**；**不降门**；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票；`0087c928`/叶28/29 另队；禁触 A18；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 07:48 ET · 叶33 coverage/稀疏事件复议只审（DRAFT `b84496fe` / COVER `4e6a1921` / RECEIPT `ab61885e`） |
| Arch 推荐（讨论向） | **endorse Option A / A1** 为下一讨论路径；**不** endorse 降 gate=300；**不**本拍签/跑；HOLD（C）并列保留，**非首选** |

## 0. 一句话

coverage/稀疏事件复议草案 **PASS_WITH_CONDITIONS**：DRAFT/COVER/RECEIPT/脚本/VOID/RUN/产物 **MATCH**；ABORT 根因盘证为 **事件稀疏→再平衡日可算 α 名数 median 30 ≪ HI_LIQ 三千级**，非 tz/RSS/overlap；草案**未**把「300→30」写成可执行补丁；Option A（A1 稀疏副闸）机制对齐且保留稠密闸 300；B 改 α 语义须整叶 FROZEN（次选）；C HOLD 并列合法。**本拍未降门、未改脚本、未签、未挂、未代跑**。请主择：若采纳 A → 令 AI 出只读 `n_unlock_pool` 诊断票（或另窗 FROZEN 草案钉 θ）→ Arch 再审；若改 C → HOLD。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_DRAFT_20261027_ZH.md` | `b84496fe` | `b84496fe245fc91a5e40da9680723cb34b0659cb3c0b522570bf0659b6aa3230` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_COVER_20261027_ZH.md` | `4e6a1921` | `4e6a1921ca52834e785ef203dbc1f355cd10e1bdb883ca46e84c35502716815d` | **MATCH** |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_RECEIPT_20261027_ZH.md` | `ab61885e` | `ab61885e2bf96c804525f2c4d0917f8e5dd1a29758fc2c55cfbfdda1935ac1a4` | **MATCH** · EXECUTED=false |
| 脚本（正式） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| Arch VOID | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_COVERAGE_GATE_20261027_ZH.md` | `6826c01d` | `6826c01d80383cb92eb97104b0525d3495054151e4360603eba9d82fe840ef92` | **MATCH** |
| RUN ABORT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUN_RECEIPT_20261027_ZH.md` | `a1b426f5` | `a1b426f53c2552370bc5e7f7a268ca8d7445f961cffacf375c8ba2f528cec092` | **MATCH** |
| alpha | `output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet` | `ea17e173` | `ea17e173d4e7b5f4945c9a8930945fecf2bde78f3b22b63fa3c2e8b4f90ad69d` | **MATCH** |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` | `473b339e` | `473b339ec0c79d9c52400b2cbbf57059097cf288a6496ec733e2c0649765c76d` | **MATCH** · hard reject=false |
| run_meta | `…/run_meta.json` | `f4702783` | `f470278310233a6dc196d621c20782019053dadaa5fe0fd5406536e8b16058c9` | **MATCH** |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | `8ed43721` | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` | **MATCH** · 本拍未改 |
| PIN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75` | **MATCH** · 本拍未改 |
| FROZEN审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bf5234a9` | `bf5234a9fb732a7e71a0bc1ca5b7e6097e50d4e1d023778e534f2bf58e9c19d3` | **MATCH** |
| VOID `.ok`（archived） | `output/ai_factory/_consumed/…245df63f.VOID.ABORT_COVERAGE_GATE.…ok` | `245df63f` | `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc` | **MATCH** · live ABSENT |
| QUIET lift | `output/loop/_lifted/…ABORT_COVERAGE_GATE_LIFTED_20261027T0735ET.lock` | `fe0e4804` | `fe0e4804056ac9e48d95309b56fde8a6242e34cfcdce60ecf84c7bc9ee00e794` | **MATCH** |
| live leaf33 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET*leaf33*` | ABSENT | ABSENT | **ABSENT** |

## 2. 必审清单（架构裁决）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **事实核**：coverage 定义 / median/gate / rebal n / HI_LIQ 规模 vs ≈30；ABORT=稀疏非 tz/RSS/overlap | **PASS** | 脚本 L1673–L1680：`cs.dropna(subset=["pressure_resid"])` 后 `coverage.append({…,"n": int(len(cs))})`；`COVERAGE_MEDIAN_HILIQ=300`（L222）；`PRESSURE_MIN_VALID=15`（L91）；无事件日跳过不填 0（L1096/L1145）。run_meta：median **30.0** / gate **300** / pass=false；rebal n=**30** 日范围 **15–72**；0%≥300；`n_codes_union=5115`；peak **963232**≪1500；`overlap_any_jaccard_hard_reject=false`；已越过 L818（RUN `a1b426f5`）。数量级差：HI_LIQ 三千级 vs coverage≈30 → **「事件稀疏→覆盖逼近解禁活跃子集」属实** |
| 2 | **Option A / A1**：机制对齐；禁擅降 gate；草案未写「300→30」可执行补丁 | **PASS_WITH_CONDITIONS** | DRAFT §3 硬禁「把 `COVERAGE_MEDIAN_HILIQ` 从 300 改成 30」；A1=`n_alpha/n_unlock_pool` median≥θ（θ∈0.5–0.8 待主钉）；本拍**未盘证** `n_unlock_pool` → 须另票只读诊断（不改正式脚本）。采纳路径：另窗修订 FROZEN + 新脚本 + 新 `.ok`（禁 RESTORED）→ **C1–C4** |
| 3 | **Option B**：改 PRESSURE_MIN_VALID / 无事件填 0 = 改 α 语义；次选；本拍不实施 | **PASS（定位同意）** | DRAFT §3 B 利弊齐；须整叶 FROZEN；**非**单纯降 gate；本拍不实施 |
| 4 | **Option C HOLD**：并列合法；本拍不主动建议为首选 | **PASS** | 主已选 (A) 复议路径；C 保留并列。若 A1 诊断显示池覆盖率本身也很低 → 再回 C |
| 5 | 状态干净：EXECUTED=false；live `.ok`=0；QUIET ABSENT；脚本 UNCHANGED | **PASS** | AI RECEIPT 钉 + 本机盘证；本拍未改任何禁项文件 |
| 6 | 禁 RESTORED / 禁触 A18 / 叶28/29 另队 | **PASS** | DRAFT/COVER 禁止清单齐；本拍未触 `245df63f`/`c5ed13df`/`5774bb6e`+票；未触 A18；未夹带叶28/29/`0087c928` |

## 3. CONDITIONS（采纳 A 或落地前）

1. **C1 本拍不落地**：gate 保持 **300**；脚本保持 **`afbbe7e7`**；不签 `.ok`；不挂 QUIET；不代跑。PASS ≠ 可签 / 可复跑。
2. **C2 采纳 A 须另窗修订 FROZEN**：写清稠密闸 300 仍为默认；本叶启用 `coverage_sparse_event_v1` 及选定 A1（及可选 A2/A3）阈值；Arch 再审 FROZEN + 脚本差分 → **新**脚本 sha8 + **新** `.ok`。
3. **C3 A1 诊断先于改门控**：`n_unlock_pool` 本拍未盘证 → 建议主令 AI 出**只读**诊断探针票（另票；**不改正式脚本** `afbbe7e7`）；算再平衡日 HI_LIQ ∩（W 窗内≥1 解禁事件）名数及 `n_alpha/n_unlock_pool` 分布，再决定 θ。
4. **C4 θ 须主钉**：θ∈0.5–0.8 讨论区间**不得**由 AI/Arch 本拍自决；A2 的 k 若取用须独立机制论证（**禁**「为通过而降到 30」）。
5. **C5 禁 RESTORED**：禁复用 `245df63f` / `c5ed13df` / `5774bb6e`+二十票；任何新跑须新 `.ok` + `--arch-ok-path <NEW_OK>`；禁 `--no-overlap-report`；rss=1500 禁抬；peak_proof REQUIRED。
6. **C6 若改 C HOLD**：维持口径+gate=300；停挖本轴；不降门、不复跑；主再令是否并行挖下一叶。
7. **C7 范围**：`0087c928`/叶28/29 另队；禁触 A18；**≠X2 ACCEPT**；leo_notify=false；live=false。

## 4. 禁项 / 本回合非动作

- **未改** `COVERAGE_MEDIAN_HILIQ` / `COVERAGE_MEDIAN_FULLA` / `PRESSURE_MIN_VALID`（仍 300/800/15）
- **未改**脚本字节（仍 **`afbbe7e7`**）
- **未签**任何 `.ok`（含 RESTORED `245df63f`/`c5ed13df`/`5774bb6e`+票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未** `--allow-real-data` / **未**代跑真构建 / **未**复跑
- **未改** FROZEN `8ed43721` / PIN `4e17ccfc` / AI DRAFT·COVER·RECEIPT
- **未**抬 rss；**未**触 A18；**未审/未夹带** `0087c928`/叶28/29
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 5. 硬钉下一跳

```
coverage/稀疏事件复议只审 PASS_WITH_CONDITIONS（本回执）
  → 请主择落地路径：
      → 若采纳 A：令 AI 出只读 n_unlock_pool 诊断票（不改正式脚本）
            → 或直接另窗 FROZEN 草案钉 θ（及可选 A2/A3）
                → Arch 再审 → 新脚本 + 新 .ok（禁 RESTORED）后再谈 X2
      → 若改 C：HOLD 本轴（并列合法；非本拍首选）
      → B 仍次选（整叶机制修订；非降门）
```

**本拍不降门 / 不改脚本 / 不签 / 不挂 / 不代跑**。HOLD **否为首选**（并列保留 C）。

## 6. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / RECEIPT | **`b84496fe`** / **`4e6a1921`** / **`ab61885e`** MATCH |
| 脚本 | **`afbbe7e7` UNCHANGED** |
| VOID / RUN | **`6826c01d`** / **`a1b426f5`** MATCH |
| alpha / overlap / meta | **`ea17e173`** / **`473b339e`** / **`f4702783`** MATCH |
| coverage | median **30.0** < gate **300**；rebal 15–72；0%≥300 |
| peak / overlap reject | **963232**≪1500 / **false** |
| FROZEN / PIN / FROZEN审 | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** 未改 |
| 推荐选项 | **A / A1**（讨论向）；**不** endorse 降 gate；C 并列非首选 |
| 建议 HOLD 为首选？ | **否**（并列保留 C） |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | 择 A→诊断票/另窗 FROZEN；或 C→HOLD |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 7. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | DRAFT/`b84496fe` · COVER/`4e6a1921` · RECEIPT/`ab61885e` · script/`afbbe7e7` · VOID/`6826c01d` · RUN/`a1b426f5` |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
