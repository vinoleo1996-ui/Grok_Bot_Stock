# Arch 审阅：fund_portfolio 计数附录 RERUN（只审过闸契约；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T21:22:20-04:00`（America/New_York；墙钟 `2026-10-27 21:22 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑** X2 / Book-Smoke / 计数脚本；**不改**上游 WHO/ALLA/RECEIPT/JSON/Data；**不开** who_pays 全票；**未混叶38**；叶37 HOLD CLOSED 维持；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+；**≠X2 ACCEPT**；live=false；promotion=false；**leo_notify=false**；旁线独立 |
| 触发 | 主令：AI RERUN gate_pass=true MATCH → 令 Arch **只审计数附录/过闸契约**（叶38 正式脚本审已 PASS_WC `87eb63f4` / 脚本 `d5cf50bb`，本票不混） |

## 0. 一句话

WHO **`604d777d`** / ALLA **`0cbfacd9`** / RECEIPT RERUN **`e3cc0143`** / JSON **`9f214237`** / events **`6c8e6613`** 本机 sha256 **MATCH**；Data AE/O/E/DATA RECEIPT/dig/旧 FAIL **全 MATCH**；**gate_pass=true**；主变体候选 **`dark_horse_add`**（crowd_add 亦过闸）；peak_rss≈**676.3**≪1500（rss 意向未抬）；34 季 AE∩前十大；**未施** mid_large/ALLA 池滤（已披露）；脚本/JSON/事件字段未见收益/价格序列消费（trade_cal 仅日历；浮筹用持仓 mkv/stk_float_ratio）；旧 FAIL **`f36d0a04`** 保留；未自签 `.ok`；QUIET ABSENT。冻结正文前缀文内钉 `a7add118` **盘上无字节快照可复算**（附录前缀现算 `05346562`）→ **C1**。**本拍不签**；≠X2 ACCEPT。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO（仅换附录） | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `604d777d` | `604d777d2ecb2954b3a35e442aed77f041fe9df53ee6e946b527033b2719a5f0` | **MATCH**（旧附录版 `5393a769`） |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `0cbfacd9` | `0cbfacd9f0495df30abd8d041747788916f89984524c6dc9de27c2685746bee9` | **MATCH**（旧 `8ef304f5`） |
| RECEIPT RERUN | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_RERUN_ZH.md` | `e3cc0143` | `e3cc0143fb20f1fa597a1716676daccbbb92021fd70a84e1205ffe741e9f055d` | **MATCH** |
| JSON | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun.json` | `9f214237` | `9f214237fe8a86a0c870eeed1d094e37af688098f786a2ffa36ccda07b42c75f` | **MATCH** |
| events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e661325e7571140bc68c227f4f878921d6c3d196ccf64eea196d57340cafa` | **MATCH** |
| DATA RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc2b46d0e317f00be8e1700119250335fb016f3d76cf1366e33f177234` | **MATCH** |
| AE | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e12951bf53b76016927bd7417dae1a0e41f6c748a69860c710e52390f8` | **MATCH** |
| O | `data/v2/etf/raw/fund_basic_O.parquet` | `50b32700` | `50b32700ae819f85d531bbd95c4ca7cd7af3f516fa14ad4a3ce81c1db4aa39b2` | **MATCH** |
| E | `data/v2/etf/raw/fund_basic_E.parquet` | `07e01516` | `07e0151624b02eefd11c88c0a1de31e6a70db8736c5dd019a73aaab902b66d8f` | **MATCH**（mtime 2026-10-25；未动） |
| 旧 FAIL RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_ZH.md` | `f36d0a04` | `f36d0a04a67c4b550858a4e777aa26e7d3e4cab8430ba93613edf5dab93b7b2b` | **MATCH**（保留） |
| dig | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101` | **MATCH**；文内自称 `a6ddc4ef` **勿采** |
| WHO sidecar（冻结钉） | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md.sha256` | `a7add118`… | 文面钉在 | **钉文在**；盘上无该字节快照 → **C1** |
| live `.ok`（本票） | `output/ai_factory/*fund*ok` / `ARCH_RUN_AUTH_FUND*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |

文内自称勿采：dig `a6ddc4ef`；只采盘上 `fa973826`。

## 2. 过闸契约再核（JSON ↔ RECEIPT ↔ WHO 附录）

| 指标 | JSON | RECEIPT / WHO 附录 | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| primary_variant_candidate | `dark_horse_add` | `dark_horse_add` | **MATCH** |
| primary_pass / dh gate_pass | true / true | 两变体均过闸；优先级取 DH | **MATCH** |
| crowd_add gate_pass | true | 亦过闸（备选） | **MATCH** |
| n_quarters / 窗 | 34；20180331→20260630 | 34 季 MATCH | **MATCH** |
| ae_n | 14241 | AE 14241 | **MATCH** |
| pool_filter | `none_mid_large_or_ALLA_…` | **未施** mid_large/ALLA 池滤 | **MATCH**（披露诚实 → **C2**） |
| symbol_filter | postfilter `.SH`/`.SZ` | 股票后缀仅 A 股 | **MATCH**；events 无非 `.SH`/`.SZ` |
| dh X2 不同股票 | 2847（≥50） | 2847 PASS | **MATCH** |
| dh 年 2024/2025/2026 | 1739/2019/1628（均≥25） | 同 | **MATCH** |
| dh 全压舱日 | 1.65%（11/668）；sparse_risk=false | 同 | **MATCH**（≪40%） |
| crowd X2 股 / 年 | 2068；3316/3529/2666 | 同 | **MATCH** |
| peak_rss_mb | 676.3 | 676.3（≤1500） | **MATCH**；脚本 `RSS_LIMIT_MB=1500` **未抬** |
| pins_before WHO/ALLA | `5393a769` / `8ef304f5` | 旧附录版 | **MATCH** 叙事 |
| ok / x2 / book_smoke / live | 未申 | 未申 / 等主排 | **MATCH** |

计数闸（WHO §计数闸）对照：X2 不同股票≥50 ∧ 2024–2026 各年≥25 ∧ 全压舱≤40% → **DH 与 crowd 均过**；按冻结优先级主变体=`dark_horse_add`。

## 3. 必审清单

| # | 项 | 结论 |
|---|---|---|
| 1 | gate_pass=true 与 JSON/RECEIPT 一致；主变体 dark_horse_add | **PASS** |
| 2 | peak≈676≪1500；rss 意向未抬 | **PASS** |
| 3 | 自称未读收益 | **PASS（证据）**：脚本 docstring「no returns」；读入仅 AE / trade_cal / fund_portfolio_dh（mkv·amount·ratio）；JSON 敏感键仅 `judgment_nth_open_after_qend`；events 无 ret/pnl/price/close；`float_mkt_est`/`dmkv` 源自持仓字段非股价表；注释 “at current prices”=当期持仓 mkv 推算，**非**日线 |
| 4 | 34 季；AE∩前十大；未施 mid_large/ALLA 池滤 | **PASS**（池滤缺失已披露 → **C2**） |
| 5 | WHO/ALLA 仅附录追加；冻结条款未改；旧 FAIL 仍在 | **PASS_WC**：现行全文钉 MATCH；旧 FAIL `f36d0a04` 在；附录段结构清晰；**但**冻结前缀 `a7add118`/`ee7bfc79` 盘上无快照字节可复算 → **C1** |
| 6 | Data 钉 AE/O/E/DATA MATCH；E 未动；未用 ETF 冒充主动权益 | **PASS**（Data RECEIPT 写死 O∩股票/混合−指数/ETF/联接；E mtime 2026-10-25） |
| 7 | 未自签 `.ok`；未挂 QUIET；本票无关侧不碰 | **PASS** |
| 8 | 未混叶38；≠X2 ACCEPT | **PASS** |

## 4. CONDITIONS / 风险

| ID | 级别 | 内容 |
|---|---|---|
| **C1** | COND | 冻结正文前缀文内/sidecar 钉 `a7add118`（ALLA 条款前 `ee7bfc79`）**盘上无对应字节快照**；现算「## 计数附录」前缀 WHO=`05346562` / ALLA=`9a90c4eb`。条款章节结构目视完整、旧 FAIL→RERUN 叙事一致，但**字节级未闭环**。建议主在开 who_pays/X2 前补冻结快照或书面接受结构对照。 |
| **C2** | COND | 本拍事件计数 **未施** mid_large / ALLA（ST/停牌/次新/ADV）池滤；厚度偏松（有利于过闸）。升 X2 前须按选定池（全 A 主口径或 mid_large 对照）**复滤事件名**再送 Eng。 |
| **C3** | NOTE | 计数脚本落在 `/tmp/fund_count_rerun/run_count.py`（盘上 sha8 **`e6fdabea`**），**未**入库 `research/`；本票范围不含脚本入库审。 |
| **C4** | NOTE | ALLA 文末「追加说明」仍含 2026-10-14「主 Agent 批准进入 X2」历史句——**不等于**本 RERUN 过闸即 X2 ACCEPT。 |
| **C5** | NOTE | 浮筹缺口剔除 4343（持仓字段无法可靠估算）；已披露；未读股价补洞。 |

## 5. 建议主下一跳

**请主裁是否开 who_pays→X2 窗。**

建议顺序（非本票代办）：
1. 接受或补闭环 **C1**（冻结前缀字节）；
2. 拍板池口径并按 **C2** 复滤（或书面接受「计数无池滤、X2 再滤」）；
3. 再开 who_pays 全票窗 →（过闸后）Eng Book-Smoke X2。

本票：**PASS_WITH_CONDITIONS**；**不签 `.ok`**；**不挂 QUIET**；**不代跑 X2**；**≠X2 ACCEPT**；未混叶38；leo_notify=false。

## 6. Arch 禁项回执

- 未签任何 `.ok`；未挂 QUIET；未代跑 X2 / Book-Smoke；未改上游件
- 未开 who_pays 全票；未混叶38；叶37 HOLD CLOSED 维持
- 禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+
- live=false；promotion=false；leo_notify=false；≠X2 ACCEPT
