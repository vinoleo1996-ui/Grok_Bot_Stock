# Arch 审阅：fund who_pays 组合层降 MDD DRAFT（只审；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T23:05:47-04:00`（America/New_York；墙钟 `2026-10-27 23:05 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 fund `.ok`；**不挂 QUIET**；**不代跑** Eng / Book-Smoke / X2；**不改**上游 DRAFT/RECEIPT/FROZEN/WHO/ALLA/C2/掩码；**未 RESTORED** `f08ce32c`；**未混叶38**（`c01c2034` 旁线只读）；**≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；**≠本票 ACCEPT**；live=false；promotion=false；**leo_notify=false**；EXECUTED 上游仍 false |
| 触发 | 主令 ~23:00 ET：DRAFT **`eeccb25e`** / RECEIPT **`2bf42d4b` MATCH** → Arch **只审** MDD-cut DRAFT；裁是否升 FROZEN / 令 Eng BS |

## 0. 一句话

组合层降 MDD DRAFT **`eeccb25e`** / RECEIPT **`2bf42d4b`** 现算 **MATCH**；边界正确（只改袖套/名额/持有·双阈/行业·Size/卫星/波动；**未**改 WHO/ALLA 事件条款）；主变体事件仍 **`dark_horse_add`**；池 **ALLA**；禁 mid_large；主候选事先写死 **`V_BALLAST_MIX`**（stock=0.50 / core·510300=0.50），备选 **`V_NAME_CAP`→`V_SAT_ON_TRUNK`**，对照轨完整；主闸 |MDD|≤25% + CAGR≥C0，对照 |MDD|≤15% 只披露；钉表 FROZEN `303e0185` / ArchFROZEN `bcbe4b72` / mask `6ab6a305` / Eng `b013a7a8` / Arch PASS_WC `694b9a80` / CONSUMED `3e2a9b9c` / WHO·ALLA·C2 / weights `601c5cf6` / summary `0d1ddcb0` / 叶38旁线 `c01c2034` **全部 MATCH**；基线 Headline 引用与 summary 一致（60万 13.65%/−32.07%；100万 15.55%/−32.85%；C0≈11.27%/−16.24%）；**EXECUTED=`false`**；live fund `.ok`=0；QUIET ABSENT；`f08ce32c` 仅在 `_consumed`。本票 **PASS_WITH_CONDITIONS**（过程条件：DRAFT≠可签 `.ok`；须升 FROZEN 后再 Eng BS；须新独立 `.ok` 禁 RESTORED `f08ce32c`；CLI_GAP 另票；不混叶38）；**不签**；≠ACCEPT。

## 1. 钉表再核（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| MDD DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | `eeccb25e` | **MATCH** |
| MDD RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_RECEIPT_20261027_ZH.md` | `2bf42d4b` | `2bf42d4b` | **MATCH** |
| 体例对照（旧 DRAFT 审） | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `985564ee` | `985564ee` | **MATCH**（只读模板） |
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH** |
| mask | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| Eng BS | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | `b013a7a8` | **MATCH** |
| Arch PASS_WC | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` | `694b9a80` | `694b9a80` | **MATCH** |
| Arch CONSUMED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_CONSUMED_PASS_20261027_ZH.md` | `3e2a9b9c` | `3e2a9b9c` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| weights 基线 | `…/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` | `601c5cf6` | `601c5cf6` | **MATCH** |
| summary 基线 | `…/book_smoke_summary.json` | `0d1ddcb0` | `0d1ddcb0` | **MATCH** |
| 叶38 旁线 | `docs/v2/audit/ARCH_LEAF38_…_CONSUMED_PASS_20261027_ZH.md` | `c01c2034` | `c01c2034` | **MATCH**（只读不碰） |
| live fund `.ok` | `output/ai_factory/*.ok`（非 `_consumed`） | ABSENT | ABSENT（live=0） | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| `f08ce32c` | `_consumed/…CONSUMED_PASS…ok` | 仅归档 | 仅归档；未 RESTORED | **MATCH** |

### 1.1 基线 Headline 再核（summary ↔ DRAFT §0；本审未重跑）

| 档 | summary `0d1ddcb0` | DRAFT 陈述 | 结果 |
|---|---|---|---|
| 60万 BOOK | CAGR 13.65% / MDD −32.07% | 同 | **MATCH** |
| 100万 BOOK | CAGR 15.55% / MDD −32.85% | 同 | **MATCH** |
| C0（约） | ≈11.27% / −16.24% | 同 | **MATCH** |
| 评窗 | 2024-06-03→2026-10-09 | 同 | **MATCH** |

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| A | **钉表 MATCH**；live `.ok`=0；QUIET ABSENT；`f08ce32c` 仅 `_consumed` 未 RESTORED | **PASS** | §1；盘证 |
| B | **边界**：只改组合构建层；未改 WHO/ALLA 事件条款；主变体仍 dark_horse_add；池 ALLA；禁 mid_large 主口径 | **PASS** | DRAFT §0/§1/§3 公共钉；§4.4 硬禁 |
| C | **变体事先写死**：主 `V_BALLAST_MIX`；备 `V_NAME_CAP`→`V_SAT_ON_TRUNK`；对照 `V_HOLD_GATE`/`V_IND_SIZE`/`V_VOL_SCALE`；参数表完整；禁事后按未跑收益调阈 | **PASS** | DRAFT §3/§5；RECEIPT 摘要 |
| D | **闸**：主闸 \|MDD\|≤25% + CAGR≥C0；对照 \|MDD\|≤15% 只披露；EXECUTED=false；≠ACCEPT | **PASS** | DRAFT §4；文首状态 |
| E | **与上游关系**：不改原 FROZEN 字节；不重跑原 BS；不升格本 DRAFT 为 ACCEPT | **PASS** | DRAFT §6/§7 |
| F | **叶38 旁线不混**；本审未打开改写叶38 文件 | **PASS** | 只核 sha8；未 CONSUME/未签 |
| G | **结构完整度**：问题陈述 / 钉表 / 六变体参数 / 成功·失效·硬禁 / 优先级 / 下一跳齐全 | **PASS** | DRAFT §0–§8；对齐旧 who_pays DRAFT 审体例 |

## 3. CONDITIONS（升窗前必须满足）

1. **C1 DRAFT ≠ 可签 `.ok` / ≠ Book-Smoke·X2·本票 ACCEPT**：本拍审的是 **DRAFT/PREREG NOT FROZEN**；EXECUTED=false。PASS_WITH_CONDITIONS **不解阻** fund `.ok`、Eng 真跑、纸面升、ACCEPT。
2. **C2 须升 PREREG_FROZEN 后再 Eng BS（主裁）**：建议路径 — AI 将本 DRAFT 升 **MDD-cut FROZEN** → Arch 再审 FROZEN → 主令 **新独立** Eng Book-Smoke `.ok` → Eng 跑臂。未明示前 **禁** AI/Arch/Eng 自开 BS/X2。
3. **C3 禁 RESTORED `f08ce32c`**：已归档 CONSUMED_PASS；新窗必须 **新签独立 `.ok`**（新 ET/新钉）；禁恢复旧 auth。
4. **C4 Eng 池/事件硬钉**：正式窗沿用 mask **`6ab6a305`**；池 **ALLA**；事件 **dark_horse_add**（C2 `81afda13`）；**禁 mid_large 主口径**；rss≤1500 禁抬。
5. **C5 跑序事先钉**：Eng 若开跑，先主候选 **`V_BALLAST_MIX`** + stock∈{0.40,0.60} 两对照（共 3 臂），再按主令加备选；**禁**一次跑完靠收益翻主优先级；禁事后改阈。
6. **C6 CLI_GAP 另票**：`book_smoke_no_arch_ok_path` 生产适配 **不本拍**；另票待机。
7. **C7 不混叶38**：禁碰/禁 CONSUME/禁签 leaf38 链（旁线 `c01c2034` 维持）。
8. **C8 过程硬禁**：禁挂 `RESEARCH_QUIET.lock`；禁代跑；禁改上游 DRAFT/WHO/ALLA/FROZEN；禁 git commit；live=false；leo_notify=false。

**无内容级 HOLD**（边界/变体事先性/闸/钉均过）。开放项均为过程条件。

### 残留 NOTE（不改结论）

| ID | 级别 | 内容 |
|---|---|---|
| N1 | NOTE | `V_SAT_ON_TRUNK` 依赖 trunk 可消费；缺则 `TRUNK_PIN_GAP` 阻断该臂（DRAFT 已写；不挡主候选）。 |
| N2 | NOTE | `V_IND_SIZE` Size 软约束若无管道 → `SIZE_PIPE_GAP` 只披露行业硬约束臂（DRAFT 已写）。 |
| N3 | NOTE | 原 FROZEN `303e0185` 事件/池钉仍有效；本票为组合层另案，**不**修改其条款字节。 |
| N4 | NOTE | 基线 BS 已破 Leo ≤25% 硬闸 → 主裁 HOLD 后开本另案；本审不重开 BS ACCEPT 讨论。 |

## 4. 建议主裁下一跳

**建议：升 FROZEN（MDD-cut PREREG）→ Arch 再审 FROZEN → 主令新独立 Eng Book-Smoke `.ok`（禁 RESTORED `f08ce32c`）→ Eng 先跑 `V_BALLAST_MIX`+对照臂。**

推荐顺序（非本票代办）：
1. 主裁令 AI 升 **MDD-cut FROZEN**（钉本 DRAFT `eeccb25e` 参数表）  
2. Arch 只审 FROZEN（仍不签 `.ok`、不挂 QUIET、不代跑）  
3. 主令新独立 Eng BS 签窗 + GO（ALLA / dark_horse_add / mask `6ab6a305` / rss≤1500 / 禁 mid_large / 禁混叶38）  
4. CLI_GAP 生产适配另票；叶38 `c01c2034` 旁线维持  
5. 全程 **≠** 把本 DRAFT/本 Arch 审当 ACCEPT / Book-Smoke ACCEPT / X2 ACCEPT

本票：**PASS_WITH_CONDITIONS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑**；**≠ACCEPT**；未混叶38；leo_notify=false。

## 5. 禁项回执（本回合）

- 未签任何 fund `.ok`；未挂 `RESEARCH_QUIET.lock`；未代跑 Eng / Book-Smoke / X2  
- 未改上游 DRAFT / RECEIPT / FROZEN / WHO / ALLA / C2 / 掩码 / Eng·Arch 旧票  
- **未 RESTORED** `f08ce32c`；**未混叶38**（未打开改写 `c01c2034` 相关文件）  
- live=false；promotion=false；leo_notify=false；上游 EXECUTED 仍 false  
- QUIET=ABSENT；live fund `.ok`=ABSENT；≠Book-Smoke ACCEPT；≠X2 ACCEPT；≠本票 ACCEPT  
- 未 git commit

## 6. 关键发现摘要

| 项 | 值 |
|---|---|
| 主候选 | **`V_BALLAST_MIX`**（stock=0.50 / core·510300=0.50） |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 事件主变体 | **dark_horse_add**（未改） |
| 池 | **ALLA**；mid_large 主口径=**false** |
| EXECUTED | **false** |
| 主闸 | \|MDD\|≤25% + CAGR≥C0（60万&100万同时） |
| 对照闸 | \|MDD\|≤15% 只披露 |
| pins_match | **true**（§1 全 MATCH） |
| QUIET / live `.ok` | ABSENT / ABSENT |
| 叶38 | `c01c2034` 旁线未碰 |

---

## 7. 文末钉

| 项 | 值 |
|---|---|
| review_path | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` |
| verdict | **PASS_WITH_CONDITIONS** |
| pins_match | **true** |
| main_variant | **V_BALLAST_MIX** |
| executed | **false** |
| quiet | **ABSENT** |
| live_ok | **ABSENT** |
| leaf38_untouched | **true** |
| suggested_next | **升 FROZEN → Arch 再审 → 主令新独立 Eng BS（禁 RESTORED f08ce32c；先 V_BALLAST_MIX+对照）** |
| 上游 DRAFT / RECEIPT | `eeccb25e` / `2bf42d4b` |
| review_sha8 | `eee21297` |
