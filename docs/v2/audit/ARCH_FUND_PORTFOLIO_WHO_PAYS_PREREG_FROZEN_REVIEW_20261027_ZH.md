# Arch 审阅：fund_portfolio who_pays PREREG_FROZEN（另窗只审；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T22:21:08-04:00`（America/New_York；墙钟 `2026-10-27 22:21 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 fund `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数；**不改**上游 FROZEN/DRAFT/WHO/ALLA/C2/前缀；**未混叶38**（本审**未打开** leaf38 脚本/`.ok`/签窗/CONSUME）；**≠X2 ACCEPT**；**≠本票 ACCEPT**；live=false；promotion=false；**leo_notify=false**；旁线独立 |
| 触发 | 主 22:16 ET：FROZEN **`303e0185`** / RECEIPT **`df153eb9` MATCH** → Arch **只审 FROZEN**（C2=A 已升；不直接开 Eng；叶38 签窗并行不混） |

## 0. 一句话

PREREG_FROZEN **`303e0185`** / RECEIPT **`df153eb9`** 现算 **MATCH**；相对 who_pays DRAFT **`7cfbb3e5`** **已升格 FROZEN**（主裁 **C2=A**）；**EXECUTED=`false`**；主变体 **`dark_horse_add`**（crowd 备选；优先级先 DH 后 crowd，与 C2/DRAFT 一致未回退）；池=**ALLA 可交易**（`mid_large_主口径=false`；掩码 **`6ab6a305`** 判定日 `universe_mask(session)`）；**gate_pass=`true`** 与 C2 **`cb48e5d9`/`d6024472`/`81afda13`** 数字一致（DH X2 股 **2835**；年 **1727/2007/1614**；压舱 **1.65%**；peak≈249.2≪1500；本审**未**重跑）；WHO **`547b246e`** / ALLA **`724e1df5`** 条款区未改；前缀 **`05346562`/`9a90c4eb`** startswith=**True**；Arch DRAFT 审 **`985564ee`** CONDITIONS：C1/C3/C4/C5 认、**C2=A 已落地**为本 FROZEN；结构完整可作 Eng 开窗前冻结票。开放余项均为过程条件（须主令另开 Eng；禁自签；掩码硬钉）。**本拍不签**；≠X2 ACCEPT；未混叶38；leo_notify=false。

## 1. 钉表再核（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH** |
| **FROZEN RECEIPT** | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `df153eb9` | `df153eb9` | **MATCH** |
| who_pays DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` | `7cfbb3e5` | `7cfbb3e5` | **MATCH** |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `985564ee` | `985564ee` | **MATCH** |
| Arch C1C2 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | `5f7ff5a6` | **MATCH** |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO 冻结全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | `05346562` | **MATCH** |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | `9a90c4eb` | **MATCH** |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | `956588eb` | **MATCH** |
| 掩码脚本 | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e6613` | **MATCH** |
| AE parquet | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| Data RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc` | **MATCH** |
| live fund `.ok` | fund who_pays 相关 `.ok` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |

旁路：WHO/ALLA 全文 **startswith** 前缀快照 = **True**（WHO 5618 B；ALLA 2700 B）。FROZEN 文内上游钉表与本机复算一致。

### 1.1 C2 闸数字再核（JSON ↔ FROZEN；本审不重跑）

| 指标 | JSON `d6024472` | FROZEN `303e0185` | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| primary_variant_candidate | `dark_horse_add` | `dark_horse_add` | **MATCH** |
| mid_large_主口径 | false | false | **MATCH** |
| pool_filter | `ALLA_tradable_on_judgment_day` | ALLA 可交易；mask `6ab6a305` | **MATCH** |
| DH X2 不同股票 | 2835 | 2835（≥50） | **MATCH** |
| DH 年 2024/25/26 | 1727/2007/1614 | 同 | **MATCH** |
| DH 全压舱 | 1.65%（11/668）；sparse_risk=false | 1.65% | **MATCH** |
| crowd X2 股 / 年 | 2063；3302/3518/2656 | 同（备选） | **MATCH** |
| peak_rss_mb | 249.2 | 249.2（≤1500；未抬） | **MATCH** |
| mask 聚合 | rows=149775；in=142761；st=4758；susp=452；young=1874；adv=132 | 同 | **MATCH** |

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **状态=FROZEN**（相对 DRAFT `7cfbb3e5` 升格）；EXECUTED=false；≠`.ok`/≠X2 ACCEPT/≠Book-Smoke | **PASS** | FROZEN 文首/§10/§12；RECEIPT；盘证 fund `.ok` ABSENT；QUIET ABSENT |
| 2 | 主变体 **dark_horse_add**；crowd 备选；优先级先 DH 后 crowd；与 C2/DRAFT 一致未回退 | **PASS** | FROZEN §0/§1/§3；JSON `primary_variant_candidate`；DRAFT 审 `985564ee` |
| 3 | 池=**ALLA 可交易**；**mid_large 主口径=false**；钉掩码 `6ab6a305` 判定日逻辑 | **PASS** | FROZEN §4；JSON `pool_filter=ALLA_tradable_on_judgment_day`；mask `universe_mask(session)`：ST/停牌/<60d/ADV20≥200万（判定日 session） |
| 4 | gate_pass=true 与 C2 数字一致（DH 2835；年 1727/2007/1614；压舱 1.65%）；**未重跑** | **PASS** | §1.1；本审未代跑计数 |
| 5 | who_pays / PIT / 判定日 / 加仓定义与 WHO 冻结条款区一致；前缀 startswith 仍 True | **PASS** | FROZEN §1–§3 vs WHO `547b246e`；startswith=True；条款区未改 |
| 6 | 组合规则：单名 4%/≤20 名/SW L1≤28%/余额 510300；排除 600519/002371 | **PASS** | FROZEN §1；WHO/ALLA 仓位条款 |
| 7 | 硬闸完整（Jaccard/ρ/α/成本·衰减/RSS≤1.5GB）；终判 Eng Book-Smoke；本票不解阻 | **PASS** | FROZEN §6；明确 ≠本票 ACCEPT；本审未代跑 |
| 8 | 与 Arch DRAFT 审 `985564ee` CONDITIONS 衔接：C1/C3/C4/C5 认；**C2=A 已落地**为本 FROZEN | **PASS** | FROZEN §7；RECEIPT CONDITIONS 表；主令 C2=A |
| 9 | 结构完整可作 Eng 开窗前冻结票；**不混叶38** | **PASS** | §0–§12 齐全；本审未打开叶38 任何文件 |

## 3. CONDITIONS（相对 `985564ee`；C2=A 已闭合）

| # | 条件 | 本 FROZEN 审 | 状态 |
|---|---|---|---|
| C1 | DRAFT/FROZEN ≠ 可签 `.ok` / ≠ X2 ACCEPT | PREREG_FROZEN 仍 **≠** `.ok` / ≠ X2 ACCEPT；须**主令另开** Eng Book-Smoke / X2 独立窗 | **认（仍有效）** |
| **C2** | 全票冻结路径 A 或 B | 主裁 **C2=A** → DRAFT→本 FROZEN **已落地**；下一跳 = 主令开 Eng（禁自开） | **CLOSED（A 落地）** |
| C3 | Eng 池硬钉 ALLA | 正式窗必须沿用 `research/all_a_universe_mask.py` **`6ab6a305`** **判定日**掩码；**禁** mid_large 主口径；禁「计数无池滤、X2 再滤」 | **认（Eng 硬钉）** |
| C4 | 过程硬禁 | 禁签 fund `.ok`；禁挂 QUIET；禁代跑 X2/Book-Smoke/计数；**禁混叶38**；禁抬 rss 意向 1500；live=false；leo_notify=false | **认（本拍遵守）** |
| C5 | 轻量闸 ≠ 收益验收 | gate_pass 仅放行讨论/开窗；残差 α / Jaccard / 组合门 / 成本·衰减 **以 Eng Book-Smoke X2 终判**；本冻结与本审均**未**读收益 | **认（仍有效）** |

**无内容级 HOLD**（机制/池/闸/前缀/钉/升格均过）。开放项均为过程条件。

### 残留 NOTE（不改结论）

| ID | 级别 | 内容 |
|---|---|---|
| N1 | NOTE | WHO 前缀正文仍留「池：mid_large PIT top300」史句；已被 ALLA 补充 + C2 + 本 FROZEN `mid_large_主口径=false` supersede（沿用 `985564ee` N1）。 |
| N2 | NOTE | 旁线叶38 签窗并行；本审**未打开未混**；fund 与叶38 状态机隔离。 |

## 4. 建议主裁下一跳

**建议主裁：可令 Eng 开 Book-Smoke / X2 独立窗**（内容侧 FROZEN 冻结票齐；C2=A 已闭合），并硬钉：

1. 钉本 FROZEN **`303e0185`** + RECEIPT **`df153eb9`** + Arch 本审（落盘后 sha8）  
2. Eng：**ALLA 掩码 `6ab6a305` 判定日**；rss≤1500 禁抬 + peak_proof；**禁 mid_large 主口径**；**禁混叶38**  
3. **禁**把本 FROZEN / 本 Arch 审当 X2 ACCEPT；**禁**自签 fund `.ok`；独立 `.ok` 须主令另排签窗  
4. 叶38 旁线继续不夹本票

本票：**PASS_WITH_CONDITIONS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑**；**≠X2 ACCEPT**；**≠本票 ACCEPT**；未混叶38；leo_notify=false；live=false。

## 5. 禁项回执（本回合）

- 未签任何 fund `.ok`；未挂 `RESEARCH_QUIET.lock`；未代跑 X2 / Book-Smoke / 计数  
- 未改上游 FROZEN / RECEIPT / DRAFT / WHO / ALLA / C2 RECEIPT·JSON·events / 前缀 `.bin` / NOTE / 掩码  
- **未混叶38**（未打开 leaf38 脚本 / `.ok` / 签窗 / CONSUME / VOID）  
- live=false；promotion=false；leo_notify=false；EXECUTED 仍 false（上游）；≠X2 ACCEPT；≠本票 ACCEPT  
- QUIET=ABSENT；live fund `.ok`=ABSENT

## 6. 关键发现摘要

| 项 | 值 |
|---|---|
| 状态 | **FROZEN**（相对 DRAFT `7cfbb3e5` 升格；C2=A） |
| mid_large 主口径 | **false**（ALLA；mask `6ab6a305`） |
| gate_pass | **true**（C2 MATCH；未重跑） |
| 主变体 | **dark_horse_add**（crowd 备选亦过闸） |
| EXECUTED | **false** |
| peak_rss_mb | **249.2**（≪1500；未抬） |
| 前缀闭环 | **05346562 / 9a90c4eb** startswith=True |
| Arch DRAFT 审 | **985564ee PASS_WC**；C2=A 已落地；C1/C3/C4/C5 仍有效 |
| 叶38 | **旁线未混**（本审未打开） |

---

## 7. 文末钉

| 项 | 值 |
|---|---|
| 本审票路径 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` |
| 结论 | **PASS_WITH_CONDITIONS** |
| 上游 FROZEN / RECEIPT | `303e0185` / `df153eb9` |
| 钉点现算 | DRAFT `7cfbb3e5` / Arch DRAFT `985564ee` / C1C2 `5f7ff5a6` / C2 `cb48e5d9`·`d6024472`·`81afda13` / WHO `547b246e` / ALLA `724e1df5` / 前缀 `05346562`·`9a90c4eb` / NOTE `956588eb` / 掩码 `6ab6a305` |
| QUIET / fund `.ok` | ABSENT / ABSENT |
| 未签未挂未代跑 / 未混叶38 | 确认 |
| ≠X2 ACCEPT / ≠本票 ACCEPT | 确认 |
| 建议主裁 | **令 Eng 开 Book-Smoke/X2 独立窗**（钉 FROZEN `303e0185`；ALLA `6ab6a305`；禁自签；禁混叶38） |
| 本审票 sha8 | `a382e825` |
