# Arch 审阅：fund_portfolio who_pays 全票 DRAFT（只审；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T22:05:24-04:00`（America/New_York；墙钟 `2026-10-27 22:05 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 fund `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数脚本；**不改**上游 DRAFT/WHO/ALLA/C2/前缀；**未混叶38**（pushdown 旁线；禁碰 leaf38 文件/CONSUME/签）；**≠X2 ACCEPT**；**≠本票 ACCEPT**；live=false；promotion=false；**leo_notify=false**；旁线独立 |
| 触发 | 主令：DRAFT **`7cfbb3e5` MATCH** → Arch **另窗只审** who_pays；裁是否进 FROZEN/X2 |

## 0. 一句话

who_pays 全票 DRAFT **`7cfbb3e5`** 现算 **MATCH**；相对指针 **`bd9fdbda`** 已升级为全票（机制 / who_pays / PIT / 事件 / ALLA 池 / C2 闸 / 硬闸 / 钉表齐全）。状态 **DRAFT NOT FROZEN**；**EXECUTED=`false`**；主变体 **`dark_horse_add`**（crowd 备选；优先级先 DH 后 crowd，写于计数前且与 C2 一致）；池=**ALLA 可交易**（`mid_large_主口径=false`）；**gate_pass=`true`** 与 C2 **`cb48e5d9`/`d6024472`/`81afda13`** 及 Arch C1C2 **`5f7ff5a6` PASS** 一致；WHO **`547b246e`** / ALLA **`724e1df5`** 条款区未改；前缀闭环 **`05346562`/`9a90c4eb`** startswith=True；peak≈249≪1500。旧 C1/C2 COND **CLOSED 未回退**。本票 **PASS_WITH_CONDITIONS**（过程条件：DRAFT≠可签 `.ok`；Eng 须沿用 ALLA 掩码；主令另开 X2 窗）；**不签**；≠X2 ACCEPT。

## 1. 钉表再核（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| who_pays DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` | `7cfbb3e5` | `7cfbb3e5` | **MATCH** |
| 指针草稿 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_DRAFT_ZH.md` | `bd9fdbda` | `bd9fdbda` | **MATCH** |
| Arch C1C2 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | `5f7ff5a6` | **MATCH** |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO 冻结全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | `05346562` | **MATCH** |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | `9a90c4eb` | **MATCH** |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | `956588eb` | **MATCH** |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e6613` | **MATCH** |
| AE parquet | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| Data RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc` | **MATCH** |
| mask 实现 | `research/all_a_universe_mask.py` | `6ab6a305`（DRAFT 文钉） | `6ab6a305` | **MATCH** |
| 旧审 RERUN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_COUNT_APPENDIX_RERUN_REVIEW_20261027_ZH.md` | `b410680b` | `b410680b` | **MATCH** |
| live fund `.ok` | `output/ai_factory/*fund*ok*` / `*.ok` | ABSENT | ABSENT（live `.ok`=0） | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| 叶38（只读不碰） | `.ok`/`脚本`/`RECEIPT` | `62acf9fc`/`d5cf50bb`/`4649335f` | 本审**未打开未改** | **不混** |

旁路：WHO/ALLA 全文 **startswith** 前缀快照 = **True**（WHO 5618 B；ALLA 2700 B；切点=首次 `## 计数附录`）。

### 1.1 C2 闸数字再核（JSON ↔ DRAFT ↔ RECEIPT ↔ C1C2）

| 指标 | JSON `d6024472` | DRAFT `7cfbb3e5` | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| primary_variant_candidate | `dark_horse_add` | `dark_horse_add` | **MATCH** |
| mid_large_主口径 | false | false（禁 mid_large 主口径） | **MATCH** |
| pool_filter | `ALLA_tradable_on_judgment_day` | ALLA 可交易 | **MATCH** |
| DH X2 不同股票 | 2835 | 2835（≥50） | **MATCH** |
| DH 年 2024/25/26 | 1727/2007/1614 | 同 | **MATCH** |
| crowd X2 股 / 年 | 2063；3302/3518/2656 | 同 | **MATCH** |
| 全压舱 | 1.65%（11/668）；sparse_risk=false | 1.65% | **MATCH** |
| peak_rss_mb | 249.2 | 249.2（≤1500；未抬） | **MATCH** |
| 基线对照剔量 | DH −272 / crowd −194 | 同；基线 `6c8e6613` | **MATCH** |
| mask 聚合 | st=4758 / susp=452 / young=1874 / adv=132 | 同 | **MATCH** |
| no_returns / no_price | true | 未读收益/股价 | **MATCH** |

## 2. 必审清单（对齐叶 who_pays DRAFT 审 + 工业选股支柱）

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **状态**：DRAFT NOT FROZEN；EXECUTED=false；≠X2 ACCEPT；未自签/未挂 QUIET/未 Book-Smoke | **PASS** | DRAFT 文首/§8/§10；盘证 live `.ok`=0；QUIET ABSENT |
| 2 | **主变体** dark_horse_add；crowd_add 备选；优先级先 DH 后 crowd 写于计数前且与 C2 一致 | **PASS** | DRAFT §0/§1/§3；JSON `primary_variant_candidate=dark_horse_add`；WHO 冻结优先级句 |
| 3 | **池**：ALLA 可交易（剔 ST/停牌/<60d/ADV 不足 100 万档→ADV20≥200 万）；**禁 mid_large 主口径** | **PASS** | DRAFT §4；JSON `mid_large_主口径=false`；ALLA 补充；C1C2 CLOSED C2 |
| 4 | **gate_pass=true** 与 C2 钉一致；厚度/年分布/压舱合理引用（不重跑） | **PASS** | §1.1；本审**未**代跑计数 |
| 5 | **who_pays 一句**可检验；PIT/available_at/判定日/加仓定义与 WHO 冻结一致（条款区未改） | **PASS** | DRAFT §0/§2 vs WHO：ann_date 次一交易日 09:00；判定日=季末后第 16 交易日；加仓≥20%/新进前十大；T2 入场持 60 日 |
| 6 | **前缀快照闭环**仍引用 `05346562`/`9a90c4eb`；未改条款前缀字节 | **PASS** | startswith=True；DRAFT §7；C1 CLOSED 未回退 |
| 7 | **组合规则**：单名 4%/≤20 名/SW L1≤28%/余额 510300；排除 600519/002371 | **PASS** | DRAFT §1；WHO/ALLA 仓位条款一致 |
| 8 | **失效/硬闸**引用完整（Jaccard/ρ/α/成本·衰减/RSS≤1.5GB 等）；终判 Eng Book-Smoke；本票不代跑 | **PASS** | DRAFT §6；明确 ≠本票 ACCEPT；本审未代跑 |
| 9 | **与 Arch C1C2 PASS `5f7ff5a6`** 衔接正确；旧 COND CLOSED 未回退 | **PASS** | DRAFT 触发/§7 钉 `5f7ff5a6`；C1/C2 CLOSED 认 |
| 10 | **结构完整度**：相对指针 `bd9fdbda` 已升级为全票 | **PASS** | 指针保留 10-14 早期 mid_large 史稿；现行全票迁 audit；§0–§10 齐全（机制/池/闸/硬闸/钉/禁项/下一跳） |

## 3. CONDITIONS（升窗前必须满足）

1. **C1 DRAFT ≠ 可签 `.ok` / ≠ X2 ACCEPT**：本拍审的是 **DRAFT NOT FROZEN**。PASS_WITH_CONDITIONS **不解阻** fund `.ok`、Book-Smoke、X2 ACCEPT、升纸面。须**主令另开** Eng Book-Smoke / X2 独立窗（独立 `.ok`；禁自派）。
2. **C2 全票冻结路径二选一（主裁）**：（A）令 AI 将本 DRAFT 升 **FROZEN who_pays 全票** → Arch 再审 FROZEN → 再开 X2；或（B）主明示「以本 DRAFT + 本 Arch 审直接开 Eng X2 窗」。未明示前 **禁** AI/Arch 自开 X2。
3. **C3 Eng 池硬钉**：正式窗必须沿用 `research/all_a_universe_mask.py`（现盘 **`6ab6a305`**）**判定日** ALLA 可交易掩码；**禁**改回 mid_large 主口径；禁「计数无池滤、X2 再滤」。
4. **C4 过程硬禁**：禁签 fund `.ok`；禁挂 `RESEARCH_QUIET.lock`；禁代跑 X2/Book-Smoke/计数；**禁混叶38**（禁碰/禁 RESTORED `62acf9fc`/`d5cf50bb`/`4649335f` 及叶38 VOID 链）；禁抬 rss 意向 1500；live=false；leo_notify=false。
5. **C5 轻量闸 ≠ 收益验收**：gate_pass 仅放行继续讨论/开窗；残差 α / Jaccard / 组合门 / 成本·衰减 **以 Eng Book-Smoke X2 终判**；本票与本审均**未**读收益。

**无内容级 HOLD**（机制/池/闸/前缀/钉均过）。开放项均为过程条件。

### 残留 NOTE（不改结论）

| ID | 级别 | 内容 |
|---|---|---|
| N1 | NOTE | WHO 冻结前缀正文仍留「池：mid_large PIT top300」史句；已被 ALLA 补充 + C2 主口径 supersede；DRAFT 正确标 `mid_large_主口径=false`。 |
| N2 | NOTE | 旧审 `b410680b` C3（计数脚本 /tmp 未入库）等旁注仍可在 Eng 窗跟踪；**不挡**本 who_pays DRAFT。 |
| N3 | NOTE | C1C2 审 N1（WHO/ALLA `.sha256` 文面 HIST 钉）仍有效；闭环锚为前缀快照，非伪造 HIST。 |

## 4. 建议主裁下一跳

**建议主裁：可进 Eng Book-Smoke / X2 窗准备**（内容侧过闸），但须先落 **C2（A 或 B）** 明示，并遵守 **C1/C3/C4/C5**。

推荐顺序（非本票代办）：
1. 主裁 C2 路径 →（若 A）AI 出 FROZEN 全票 → Arch 再审；或（若 B）主令直接开 Eng 窗  
2. Eng 独立窗：ALLA 掩码 + rss≤1.5GB + 禁 mid_large 主口径 + 禁混叶38  
3. 全程 **≠** 把本 DRAFT/本 Arch 审当 X2 ACCEPT

本票：**PASS_WITH_CONDITIONS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑**；**≠X2 ACCEPT**；**≠本票 ACCEPT**；未混叶38；leo_notify=false。

## 5. 禁项回执（本回合）

- 未签任何 fund `.ok`；未挂 `RESEARCH_QUIET.lock`；未代跑 X2 / Book-Smoke / 计数脚本  
- 未改上游 DRAFT / WHO / ALLA / C2 RECEIPT·JSON·events / 前缀 `.bin` / NOTE  
- **未混叶38**（未打开、未 CONSUME、未签 leaf38 相关文件）  
- live=false；promotion=false；leo_notify=false；EXECUTED 仍为 false（上游）；≠X2 ACCEPT；≠本票 ACCEPT  
- QUIET=ABSENT；live fund `.ok`=ABSENT

## 6. 关键发现摘要（含 mid_large / gate_pass / DH / EXECUTED）

| 项 | 值 |
|---|---|
| mid_large 主口径 | **false**（禁；ALLA 主口径） |
| gate_pass | **true**（C2 MATCH） |
| 主变体 | **dark_horse_add**（crowd 备选亦过闸） |
| EXECUTED | **false** |
| peak_rss_mb | **249.2**（≪1500；未抬） |
| 前缀闭环 | **05346562 / 9a90c4eb** startswith=True |
| Arch C1C2 | **5f7ff5a6 PASS**；COND CLOSED 未回退 |
| 相对指针 | **bd9fdbda → 7cfbb3e5 全票升级** |

---

## 7. 文末钉

| 项 | 值 |
|---|---|
| 本审票路径 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` |
| 结论 | **PASS_WITH_CONDITIONS** |
| 上游 DRAFT | `7cfbb3e5` |
| 钉点现算 | 指针 `bd9fdbda` / C1C2 `5f7ff5a6` / RECEIPT `cb48e5d9` / JSON `d6024472` / events `81afda13` / WHO `547b246e` / ALLA `724e1df5` / 前缀 `05346562`·`9a90c4eb` / NOTE `956588eb` |
| QUIET / fund `.ok` | ABSENT / ABSENT |
| 未签未挂未代跑 / 未混叶38 | 确认 |
| ≠X2 ACCEPT / ≠本票 ACCEPT | 确认 |
| 建议主裁 | **C2 明示后开 Eng Book-Smoke/X2 窗**（禁自开；禁混叶38） |
| 本审票 sha8 | `815e5996` |
