# Arch 审阅：fund who_pays 组合层降 MDD · PREREG_FROZEN（只审；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T23:20:55-04:00`（America/New_York；墙钟 `2026-10-27 23:20 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 fund `.ok`；**不挂 QUIET**；**不代跑** Eng / Book-Smoke / X2；**不改**上游 FROZEN/RECEIPT/DRAFT/WHO/ALLA/掩码/原 who_pays FROZEN；**未 RESTORED** `f08ce32c`；**未混叶38**（`c01c2034` 旁线只读核 sha）；**≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；**≠本票 ACCEPT**；live=false；promotion=false；**leo_notify=false**；EXECUTED 上游仍 false |
| 触发 | 主令 ~23:17 ET：FROZEN **`d489c937`** / RECEIPT **`058ec68e` MATCH** → Arch **只审本 FROZEN**；裁是否令**新独立** Eng BS |

## 0. 一句话

MDD-cut **PREREG_FROZEN `d489c937`** / RECEIPT **`058ec68e`** 现算 **MATCH**；相对源 DRAFT **`eeccb25e`** / Arch DRAFT 审 **`41d4fc76` PASS_WC**（文内 `eee21297` 勿采）**已升格 FROZEN**；参数/主候选/对照相对 DRAFT **未漂移**（主 **`V_BALLAST_MIX`** stock=0.50/core·510300=0.50；对照 stock∈{0.40,0.60}；备选 V_NAME_CAP→V_SAT_ON_TRUNK；六变体阈冻结）；**EXECUTED=`false`**；组合层 only；事件仍 **dark_horse_add**；池 **ALLA**；禁 mid_large；原 who_pays FROZEN **`303e0185`** 字节旁线未覆盖；钉表 mask/`b013a7a8`/`694b9a80`/`3e2a9b9c`/WHO/ALLA/C2/叶38 **全 MATCH**；live fund `.ok`=0；QUIET ABSENT；`f08ce32c` 仅 `_consumed`。本票 **PASS_WITH_CONDITIONS**（FROZEN 可建议 Eng 开窗，但仍 ≠可签 `.ok`/≠ACCEPT；须主令**新独立** `.ok` 禁 RESTORED `f08ce32c`；先 V_BALLAST_MIX+对照；CLI_GAP 另票；不混叶38）；**不签**；≠ACCEPT。

## 1. 钉表再核（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| **MDD PREREG_FROZEN** | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_20261027_ZH.md` | `d489c937` | `d489c937` | **MATCH** |
| **FROZEN RECEIPT** | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `058ec68e` | `058ec68e` | **MATCH** |
| 源 MDD DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | `eeccb25e` | **MATCH** |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` | `41d4fc76` | `41d4fc76` | **MATCH**（文内 `eee21297` 勿采） |
| 体例对照（旧 who_pays FROZEN 审） | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH**（只读） |
| 原 who_pays FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH**（旁线钉；本票不覆盖） |
| mask | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| Eng BS | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | `b013a7a8` | **MATCH** |
| Arch PASS_WC | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` | `694b9a80` | `694b9a80` | **MATCH** |
| Arch CONSUMED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_CONSUMED_PASS_20261027_ZH.md` | `3e2a9b9c` | `3e2a9b9c` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| 叶38 旁线 | `docs/v2/audit/ARCH_LEAF38_…_CONSUMED_PASS_20261027_ZH.md` | `c01c2034` | `c01c2034` | **MATCH**（只读不碰） |
| live fund `.ok` | `output/ai_factory/*.ok`（非 `_consumed`） | ABSENT | ABSENT（live=0） | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| `f08ce32c` | `_consumed/…CONSUMED_PASS…ok` | 仅归档 | 仅归档；未 RESTORED | **MATCH** |

### 1.1 相对 DRAFT 参数漂移抽检（本审不改字节）

| 抽检项 | DRAFT `eeccb25e` | FROZEN `d489c937` | 结果 |
|---|---|---|---|
| V_BALLAST sleeves | `{"core":0.50,"stock":0.50,"alpha_event":0.0}` | 同 | **无漂移** |
| 对照 stock | ∈{0.40, 0.60} | 同（事先 3 臂） | **无漂移** |
| V_NAME_CAP | 2.5%/≤40；SW≤20% | 同 | **无漂移** |
| V_SAT sat_weight | 0.30（trunk 0.70） | 同 | **无漂移** |
| V_HOLD_GATE | hold_slow=40；fast≤−12% | 同 | **无漂移** |
| V_IND_SIZE | ind_cap≤18%；Size soft | 同 | **无漂移** |
| V_VOL_SCALE | target_vol=0.12 | 同 | **无漂移** |
| 事件/池 | dark_horse_add；ALLA；禁 mid_large | 同 | **无漂移** |
| EXECUTED | false | false | **MATCH** |
| 原 FROZEN `303e0185` | 不改字节 | 明确不覆盖 | **MATCH** |

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| A | 钉表本机 sha 全 MATCH；live `.ok`=0；QUIET ABSENT；`f08ce32c` 仅 `_consumed` | **PASS** | §1；盘证 |
| B | FROZEN 相对 DRAFT：参数/主候选/对照未漂移；EXECUTED=false；组合层 only；禁改 WHO/ALLA 事件；ALLA+dark_horse_add+禁 mid_large | **PASS** | §1.1；FROZEN §1/§3/§7 |
| C | 状态=**PREREG_FROZEN**（相对 DRAFT 升格）；仍 ≠可签 `.ok` / ≠ACCEPT | **PASS** | FROZEN 文首/§9–§11；RECEIPT |
| D | Arch DRAFT 审 `41d4fc76` COND C1–C8 已入钉；C2（升 FROZEN）**本票已闭合** | **PASS** | FROZEN §6；RECEIPT CONDITIONS 表 |
| E | 跑序事先钉：先 V_BALLAST_MIX+{0.40,0.60}；禁靠收益翻主 | **PASS** | FROZEN §5 |
| F | 叶38 旁线不混；本审未改写叶38 文件 | **PASS** | 只核 sha8 |
| G | 结构完整可作 Eng 开窗前冻结票 | **PASS** | §0–§11 齐全；对齐旧 who_pays FROZEN 审体例 |

## 3. CONDITIONS（继承 `41d4fc76`；C2 升格已闭合）

| # | 条件 | 本 FROZEN 审 | 状态 |
|---|---|---|---|
| C1 | FROZEN ≠ 可签 `.ok` / ≠ Book-Smoke·X2·本票 ACCEPT | PREREG_FROZEN 仍 **≠** `.ok` / ≠ ACCEPT；须**主令另开**新独立 Eng BS 窗 | **认（仍有效）** |
| **C2** | 须升 PREREG_FROZEN 后再 Eng BS | 主裁 FROZEN GO → 本文件 **已落地**；下一跳 = 主令新独立 Eng BS（禁自开） | **CLOSED（升格落地）** |
| C3 | 禁 RESTORED `f08ce32c` | 新窗必须 **新签独立 `.ok`**（新 ET/新钉）；禁恢复旧 auth | **认（Eng 硬钉）** |
| C4 | Eng 池/事件硬钉 | mask **`6ab6a305`**；池 **ALLA**；事件 **dark_horse_add**（C2 `81afda13`）；**禁 mid_large**；rss≤1500 禁抬 | **认（Eng 硬钉）** |
| C5 | 跑序事先钉 | 先 **`V_BALLAST_MIX`** + stock∈{0.40,0.60}（共 3 臂），再按主令加备选；禁靠收益翻主；禁事后改阈 | **认（仍有效）** |
| C6 | CLI_GAP 另票 | `book_smoke_no_arch_ok_path` **不本拍**；另票待机 | **认** |
| C7 | 不混叶38 | 旁线 `c01c2034` 维持；禁碰/禁 CONSUME/禁签 leaf38 链 | **认（本拍遵守）** |
| C8 | 过程硬禁 | 禁挂 QUIET；禁代跑；禁改上游；禁 git commit；live=false；leo_notify=false | **认（本拍遵守）** |

**无内容级 HOLD**（升格/参数/边界/钉均过）。开放项均为过程条件（须主令新独立 `.ok` + Eng BS）。

### 残留 NOTE（不改结论）

| ID | 级别 | 内容 |
|---|---|---|
| N1 | NOTE | `V_SAT_ON_TRUNK` 依赖 trunk 可消费；缺则 `TRUNK_PIN_GAP`（不挡主候选首跑）。 |
| N2 | NOTE | `V_IND_SIZE` Size 管道缺则 `SIZE_PIPE_GAP` 只披露行业硬约束臂。 |
| N3 | NOTE | 原 who_pays FROZEN `303e0185` 事件/池钉仍有效；本票为组合层另案，**不**覆盖其字节。 |
| N4 | NOTE | 基线 BS 已破 Leo ≤25% → 本另案目标降 MDD；本审不重开旧 BS ACCEPT。 |

## 4. 建议主裁下一跳

**建议主裁：令新独立 Eng Book-Smoke**（内容侧 FROZEN 冻结票齐；C2 升格已闭合），硬钉：

1. 钉本 FROZEN **`d489c937`** + RECEIPT **`058ec68e`** + 本 Arch 审（落盘后盘上 sha8）  
2. **新独立** Eng BS `.ok`（**禁 RESTORED `f08ce32c`**；新 ET/新钉）  
3. Eng 首跑：**`V_BALLAST_MIX` stock=0.50** + 对照 stock∈{0.40,0.60}（共 3 臂）；ALLA / dark_horse_add / mask `6ab6a305`；rss≤1500；**禁 mid_large**；**禁混叶38**  
4. CLI_GAP 另票待机；备选臂另令  
5. 全程 **≠** 把本 FROZEN/本 Arch 审当 ACCEPT / Book-Smoke ACCEPT / X2 ACCEPT  

本票：**PASS_WITH_CONDITIONS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑**；**≠ACCEPT**；未混叶38；leo_notify=false。

## 5. 禁项回执（本回合）

- 未签任何 fund `.ok`；未挂 `RESEARCH_QUIET.lock`；未代跑 Eng / Book-Smoke / X2  
- 未改上游 FROZEN / RECEIPT / DRAFT / WHO / ALLA / 原 who_pays FROZEN `303e0185` / 掩码 / Eng·Arch 旧票  
- **未 RESTORED** `f08ce32c`；**未混叶38**（未改写 `c01c2034` 相关文件）  
- live=false；promotion=false；leo_notify=false；上游 EXECUTED 仍 false  
- QUIET=ABSENT；live fund `.ok`=ABSENT；≠Book-Smoke ACCEPT；≠X2 ACCEPT；≠本票 ACCEPT  
- 未 git commit

## 6. 关键发现摘要

| 项 | 值 |
|---|---|
| 状态 | **PREREG_FROZEN**（相对 DRAFT `eeccb25e` 升格；C2 CLOSED） |
| 主候选 | **`V_BALLAST_MIX`**（stock=0.50 / core·510300=0.50） |
| 对照臂 | stock∈{0.40, 0.60}（事先 3 臂） |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 事件/池 | dark_horse_add；ALLA；mid_large=**false** |
| EXECUTED | **false** |
| pins_match | **true** |
| QUIET / live `.ok` | ABSENT / ABSENT |
| 叶38 | `c01c2034` 旁线未碰 |
| 原 who_pays FROZEN | `303e0185` 旁线未覆盖 |

---

## 7. 文末钉

| 项 | 值 |
|---|---|
| review_path | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_REVIEW_20261027_ZH.md` |
| verdict | **PASS_WITH_CONDITIONS** |
| pins_match | **true** |
| main_variant | **V_BALLAST_MIX** |
| executed | **false** |
| quiet | **ABSENT** |
| live_ok | **ABSENT** |
| leaf38_untouched | **true** |
| suggested_next | **令新独立 Eng BS（禁 RESTORED f08ce32c；先 V_BALLAST_MIX+对照 {0.40,0.60}）** |
| 上游 FROZEN / RECEIPT | `d489c937` / `058ec68e` |
| 关键 CONDITIONS | C1 仍≠`.ok`/ACCEPT；C2 CLOSED；C3 新独立`.ok`；C4 ALLA+DH+mask；C5 先3臂；C6 CLI_GAP另票；C7 不混叶38；C8 过程硬禁 |
| review_sha8 | `e9788147` |
