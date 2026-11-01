# Arch 审阅：fund_portfolio C1 前缀快照闭环 + C2 ALLA 可交易池复滤（只审；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T21:53:06-04:00`（America/New_York；墙钟 `2026-10-27 21:53 ET`） |
| **结论** | **PASS** |
| 本回合动作 | **不签**任何 fund `.ok`；**不挂 QUIET**；**不代跑** who_pays / X2 / Book-Smoke / 计数脚本；**不改**上游 WHO/ALLA/RECEIPT/JSON/events/Data；**未混叶38**（`.ok` `62acf9fc` / 脚本 `d5cf50bb` / RECEIPT `4649335f` **只读不碰**）；**≠X2 ACCEPT**；live=false；promotion=false；**leo_notify=false**；旁线独立；对照旧审 **`b410680b`** PASS_WC |
| 触发 | 主令：AI 旁线 C1+C2 DONE → Arch **另窗只审** 快照闭环 + ALLA 复滤附录；裁是否开 who_pays |

## 0. 一句话

C1：WHO/ALLA「## 计数附录」前缀 `.bin` **`05346562`** / **`9a90c4eb`** + NOTE **`956588eb`** 现算 **MATCH**；切点 = 首次 `## 计数附录` 之前；sidecar 全长与现算一致；历史 `a7add118`/`ee7bfc79` **ABSENT 认**（未伪造 HIST）。C2：RECEIPT **`cb48e5d9`** / JSON **`d6024472`** / events **`81afda13`** / WHO **`547b246e`** / ALLA **`724e1df5`** **MATCH**；主口径 **ALLA 可交易池**（`mid_large_主口径=false`；`pool_filter=ALLA_tradable_on_judgment_day`）；**gate_pass=true**；主变体 **`dark_horse_add`**；peak_rss≈**249.2**≪1500（相对旧峰 676 **未抬**叙事）；相对基线 events **`6c8e6613`** DH 剔 272 / crowd 剔 194。旧审 **`b410680b`** 之 **C1/C2 COND 已闭环**。本票 **PASS**；**不签**；≠X2 ACCEPT。

## 1. 钉表再核（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | `05346562` | **MATCH** |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | `9a90c4eb` | **MATCH** |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | `956588eb` | **MATCH** |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e6613` | **MATCH** |
| 旧审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_COUNT_APPENDIX_RERUN_REVIEW_20261027_ZH.md` | `b410680b` | `b410680b` | **MATCH** |
| 历史 WHO `a7add118` | 文内/sidecar 钉 | — | 盘上无该字节文件 | **ABSENT 认** |
| 历史 ALLA `ee7bfc79` | 文内钉 | — | 盘上无该字节文件 | **ABSENT 认** |
| live fund `.ok` | `output/ai_factory/*fund*ok*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| 叶38（只读） | `.ok` / 脚本 / RECEIPT | `62acf9fc` / `d5cf50bb` / `4649335f` | 同 | **只读 MATCH；未碰** |

旁路：WHO/ALLA `.bin.sha256` 全长与现算 **一致**（`05346562…` / `9a90c4eb…`）。

## 2. C1 — 冻结前缀字节快照闭环

| 核点 | 结果 |
|---|---|
| 前缀 = 全文首次 `## 计数附录` UTF-8 之前 | WHO nbytes=5618；ALLA nbytes=2700；**切点 MATCH** |
| 现全文 startswith 快照 | **True**（附录-only 路径；条款字节未改） |
| NOTE 写清「历史 ABSENT + 现算前缀闭环」 | **PASS**（§1 ABSENT；§2 现算钉；禁伪造 HIST） |
| 未伪造 HIST 快照文件 | **PASS**（全盘 sha8 检索无 `a7add118`/`ee7bfc79` 文件） |
| WHO sidecar 文面仍钉历史 `a7add118…` | **NOTE**：冻结全文钉文面保留；闭环以现算前缀快照为准（主已允附录-only 合法路径） |
| ALLA `.sha256` 文面 `09eff235…` ≠ 现全文/`ee7bfc79` | **NOTE**：与 NOTE/RECEIPT 披露一致；**未**当 HIST 假快照 |

**C1 结论：闭环 PASS**（对照旧审 COND C1）。

## 3. C2 — ALLA 可交易池复滤再计数

| 指标 | JSON | RECEIPT | 结果 |
|---|---|---|---|
| 主口径 | `pool.primary_口径=ALLA`；`mid_large_主口径=false`；`params.pool_filter=ALLA_tradable_on_judgment_day` | 「池 **ALLA**；**非** mid_large 主口径」 | **MATCH**；**禁 mid_large 主口径 ✓** |
| 池规则 | 剔 ST / 停牌 / &lt;60d / ADV20&lt;2e6（=100万档 capacity_adv） | 同；实现 `research/all_a_universe_mask.py` | **MATCH**（与 ALLA 冻结「100万档 ADV → ADV20≥200万」一致） |
| gate_pass | true | true | **MATCH** |
| primary_variant | `dark_horse_add` | `dark_horse_add` | **MATCH**（crowd_add 亦过闸，备选） |
| DH 全窗 / X2 股 / 年 24–26 | 12763 / 2835 / 1727·2007·1614 | 同 | **MATCH**（≥50 股 ∧ 年≥25） |
| crowd 全窗 / X2 股 / 年 | 21557 / 2063 / 3302·3518·2656 | 同 | **MATCH** |
| 全压舱 | 1.65%（11/668）；sparse_risk=false | 同 | **MATCH**（≪40%） |
| peak_rss_mb | 249.2 | 249.2（≤1500；未抬） | **MATCH**；相对旧峰 676.3 **更低**，未抬 rss 叙事 |
| 基线对照 `6c8e6613` | contrast：DH 13035→12763（−272）；crowd 21751→21557（−194）；drop reason=`not_in_all_a` | 同 | **MATCH** |
| mask 披露 | mask_st=4758 / susp=452 / young=1874 / adv=132 | — | **PASS**（可交易组分已披露） |
| events 符号 | 仅 `.SH`/`.SZ`；bad=0 | — | **PASS** |
| 未「计数无池滤、X2 再滤」书面放过 | 本拍已在计数侧复滤 | — | **PASS**（旧 COND C2 闭环） |

**C2 结论：闭环 PASS**（对照旧审 COND C2 / 主拍板 CONDITIONS）。

## 4. 对照旧审 `b410680b` CONDITIONS

| ID | 旧状态 | 本拍 | 结果 |
|---|---|---|---|
| **C1** | 冻结前缀无字节快照 | 现算前缀 `.bin`+NOTE+sidecar；HIST ABSENT 认 | **CLOSED** |
| **C2** | 未施 mid_large/ALLA 池滤 | ALLA 可交易池复滤主口径；禁 mid_large | **CLOSED** |
| C3 | 计数脚本在 `/tmp` 未入库 | 本票范围外（未代跑/未入库审） | **NOTE 残留**（不挡 C1/C2） |
| C4 | ALLA 文末历史「批准进入 X2」句 | 仍在正文；**≠**本拍 X2 ACCEPT | **NOTE** |
| C5 | 浮筹缺口剔除披露 | 沿用基线；未读股价 | **NOTE** |

## 5. CONDITIONS / 风险（本票）

**无阻挡 CONDITIONS。** 残留 NOTE（不改 PASS）：

| ID | 级别 | 内容 |
|---|---|---|
| N1 | NOTE | WHO `.sha256` 仍文面钉历史 `a7add118`；ALLA `.sha256` 文面 `09eff235` 与现全文不一致——已由 NOTE/RECEIPT 披露；闭环锚为前缀快照而非 HIST 伪造。 |
| N2 | NOTE | 事件 drop 聚合为 `not_in_all_a`（掩码内已含 ST/停牌/次新/ADV）；升 X2 时 Eng 应沿用同一 `all_a_universe_mask.py` 判定日掩码，勿改回 mid_large 主口径。 |
| N3 | NOTE | 旧 C3/C4/C5 仍作旁注；**≠X2 ACCEPT**。 |

## 6. 建议主下一跳

**建议主裁：可开 who_pays→X2 窗**（C1+C2 已闭环；本票未代开）。

顺序提醒（非本票代办）：who_pays 全票 →（过闸后）Eng Book-Smoke X2；全程禁 mid_large 主口径；不混叶38。

本票：**PASS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑**；**≠X2 ACCEPT**；未混叶38；leo_notify=false。

## 7. Arch 禁项回执

- 未签任何 fund `.ok`；未挂 `RESEARCH_QUIET.lock`；未代跑 who_pays / X2 / Book-Smoke / 计数脚本
- 未改上游件；未混叶38（`.ok` `62acf9fc` / 脚本 `d5cf50bb` / RECEIPT `4649335f` 只读）
- live=false；promotion=false；leo_notify=false；≠X2 ACCEPT
- QUIET=ABSENT

---

## 8. 文末钉

| 项 | 值 |
|---|---|
| 本审票路径 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` |
| 钉点现算 | WHO_BIN `05346562` / ALLA_BIN `9a90c4eb` / NOTE `956588eb` / RECEIPT `cb48e5d9` / JSON `d6024472` / events `81afda13` / WHO `547b246e` / ALLA `724e1df5` / 基线 events `6c8e6613` / 旧审 `b410680b` |
| QUIET | ABSENT |
| 未签未挂未代跑 | 确认 |
| ≠X2 ACCEPT | 确认 |
| 建议主裁 | **开 who_pays**（C1+C2 CLOSED） |
