# Arch 审阅：叶35 ETF_PASSIVE_FLOW_PRESSURE_OVERLAY · mapping recon（只审不改不签不代跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审 mapping recon 诊断票） |
| 时刻 | `2026-10-27T14:14:20-04:00`（America/New_York；墙钟 `2026-10-27 14:14 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | DRAFT **`350ed22b`** · COVER **`26def8fb`** · RECEIPT **`fb0c7a4b`** · 探针 DRAFT **`c2f2ca94`** · recon JSON **`ad4b47a2`** · VOID **`dfafff28`** · ok VOID **`10927bd9`** · QUIET lift **`f50975e4`** · 正式脚本 **`25ae4572` UNCHANGED** · PIN C3 **`dd17044a`** · COUNT JSON **`a17b75fb`** · 叶33 **`afbbe7e7` UNCHANGED** |
| 本回合动作 | **只审**；**不签**任何 `.ok`；**不挂** QUIET；**不代跑**探针/X2；**不改**正式脚本 `25ae4572`；**不** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+旧票；**不降门**；**不开叶36**；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 14:10 ET · 叶35 mapping recon 只审 GO（诊断票；非叶36；≠X2 ACCEPT） |
| Arch 推荐（讨论向） | **endorse Option A**（新签只读探针窗；禁 RESTORED `10927bd9`）为下一路径；Option B 补丁 DRAFT 须探针填数后再开；Option C HOLD 并列合法、**非首选** |

## 0. 一句话

叶35 mapping recon DRAFT 包 **PASS_WITH_CONDITIONS**：DRAFT/COVER/RECEIPT/探针/JSON/VOID/PIN/正式脚本 **MATCH**；EXECUTED_PROBE=**false**；主嫌疑 **A 份额 PIT**（正式 `trade_date==rebal ∧ available_at≤15:00 Asia/Shanghai` vs COUNT 未滤 `available_at`；与 PIN `dd17044a` §1.3「仅 `available_at≤t_ts`」存在实现张力）成立为 **HIGH 主嫌疑**；**B** 方案 A **MEDIUM 次**（`after_weight_pin` 已 PRESENT）；**E** top_q **已排除**（`after_mask_cs_*` ABSENT）。探针只读骨架：`py_compile`/`--dry-compile-only` **PASS**；`--allow-real-data` → **rc=3 STOP**（真值窗未实现）。**推荐 Option A**（新 `.ok` + 后续真值探针；禁 RESTORED）。本拍未签/未挂/未代跑/未改 `25ae4572`。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_DRAFT_20261027_ZH.md` | `350ed22b` | `350ed22b58f9bed4b15d28ec04ac2512760fc9ea08974870f858cc9a0133059a` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_COVER_DRAFT_20261027_ZH.md` | `26def8fb` | `26def8fba8b1ebd12a549a82cdca228ceb1259a5845a7422bd23f27dfd48fd5f` | **MATCH** |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_RECEIPT_20261027_ZH.md` | `fb0c7a4b` | `fb0c7a4ba0a2e81f4acf69bccf02766fa06ae8076955fa0af55cd7d589975a39` | **MATCH** · EXECUTED_PROBE=false |
| 探针 DRAFT py | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_DRAFT_20261027.py` | `c2f2ca94` | `c2f2ca94993ac6d74a352f07353dc5384d96d166069d46e8f1b9c146b66d65d4` | **MATCH** |
| recon JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_20261027.json` | `ad4b47a2` | `ad4b47a2791a9b508892a1b36aacb0f227f0527ade26d6e90ead03390b49c469` | **MATCH** · executed_probe=false |
| Arch VOID | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_VOID_ABORT_ZERO_MASK_ROWS_20261027_ZH.md` | `dfafff28` | `dfafff2887bbbe831821a54f6834ba3bbf31bdb9804b7bca2873bf4f0f3168c7` | **MATCH** |
| `.ok` VOID 归档 | `output/ai_factory/_consumed/…10927bd9.VOID.ABORT_ZERO_MASK_ROWS…ok` | `10927bd9` | `10927bd906f8982de930beb5b7945618b912f138b1f23da4332556edc604ab7d` | **MATCH** · live ABSENT |
| QUIET lift | `output/loop/_lifted/…ABORT_ZERO_MASK_ROWS_LIFTED_20261027T1359ET.lock` | `f50975e4` | `f50975e420c89357e957ab628445a0f599f775081d3a9374382ee83da67363d2` | **MATCH** |
| 正式脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `25ae4572` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **UNCHANGED** |
| PIN C3 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` | `a17b75fb` | `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6` | **MATCH**（引用核） |
| 叶33 正式 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED**（本票未触） |
| live leaf35 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **ABSENT** |

交叉引用：DRAFT↔COVER↔RECEIPT↔JSON 均钉 VOID/`dfafff28`、正式/`25ae4572`、PIN/`dd17044a`、COUNT/`a17b75fb`、推荐 Option A、禁 RESTORED `10927bd9`；per-rebal 真计数一律 `PIN_GAP_needs_ok_window`（非新签窗结果）。

## 2. 必审清单（架构裁决）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **嫌疑 A（份额 PIT）**：正式 `trade_date==rebal ∧ available_at≤15:00` vs COUNT APPROX；与 PIN §1.3 / C3 一致性 | **PASS（HIGH 主嫌疑成立）** | 正式 `_load_etf_flows_window` 预滤 `trade_date∈rebal`；`_pressure_on_day` 再 `trade_date==d` **且** `available_at_clock≤t_ts(15:00 SH)`，空则 `return None`。COUNT `load_etf_flows`：**仅** `trade_date∈rebal`；注释有 PIT、**代码未**施加 `available_at≤t_ts`。PIN `dd17044a` §1.3：**仅** `available_at≤t_ts`（**未**要求 `trade_date==rebal`）→ 实现比 PIN 更严 / 与 COUNT 分叉。STOP 文案首项=etf share。30/30 `after_pressure_rebal_*` 后 `after_mask_cs` ABSENT 与「同日行 available_at 常晚于 15:00 → 双过滤清空」机制对齐。**真值填数仍 PIN_GAP**（须 Option A）。 |
| 2 | **嫌疑 B（方案 A 权重）**：是否次要 | **PASS（MEDIUM 次嫌疑）** | `after_weight_pin` PRESENT（方案 A 合成未在 load 期 PIN_GAP 退出）；COUNT 用月末向后 asof（无 available_at）vs 正式方案 A 滞后。单独难解释 30/30 全空；探针须报 `n_weight_rows_schemeA`。 |
| 3 | **嫌疑 E（top_q）**：是否已排除 | **PASS（已排除为根因）** | `after_mask_cs_rebal_*` ABSENT ×30 → **从未**进入 `_cross_section_mask` / top_q=0.20；空发生在 `pressure_empty_or_unmappable` **之前**。E=现象标签，非根因。 |
| 4 | **EXECUTED_PROBE=false** 必须成立 | **PASS** | JSON `executed_probe=false`；RECEIPT 钉未真跑；本机 `--dry-compile-only` rc=0 / `executed_probe=false`；`--allow-real-data` → STOP rc=**3**（真值未实现）；无 diag out 新产物；本拍**未**加载份额/权重真值重算。 |
| 5 | 探针只读/诊断：不改正式脚本、不写 alpha/mask、不 RESTORED、不 `--force`/抬帽 | **PASS_WITH_CONDITIONS** | 探针住 `docs/v2/audit/`（非 `research/`）；钉 `FORMAL_SHA8_PIN=25ae4572`；drift→rc=2；`FORBIDDEN_OK`∋`10927bd9`+legacy；默认 dry；`--allow-real-data` 拒绝真跑。**条件**：当前字节**无** per-rebal 真值实现（rc=3）→ Option A 须「新 `.ok` + **后续真值探针版**」（DRAFT §4 已写「后续真值版」），**禁**把本骨架当可签即跑的完整探针。 |
| 6 | py_compile / dry-compile / 正式脚本 UNCHANGED | **PASS** | 本机 `python3 -m py_compile` **PASS**；`--dry-compile-only` **PASS** rc=0（`formal_sha8_observed=25ae4572`）；审后正式仍 **`25ae4572`**；叶33 **`afbbe7e7`** 未触。 |
| 7 | 状态干净：live `.ok`=0；QUIET ABSENT；≠X2 ACCEPT；≠叶36 | **PASS** | live leaf35 `.ok`=0；`RESEARCH_QUIET.lock` ABSENT；票面/JSON `x2_accept=false` / `not_leaf36=true` / live=false / leo_notify=false。 |
| 8 | 禁 RESTORED / 禁代改代跑 / 禁复跑 X2 | **PASS** | 三件套+探针 forbid 齐；本拍未签/未挂/未代跑/未改 `25ae4572`；未 RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+旧票。 |

## 3. CONDITIONS（采纳 Option 前）

1. **C1 本拍不落地**：不签 `.ok`；不挂 QUIET；不代跑探针/X2；不改正式脚本 **`25ae4572`**；不降门；不开叶36。PASS ≠ 可签 / 可真跑 / ≠X2 ACCEPT。
2. **C2 Option A（推荐）**：若主要填 per-rebal 真数，须发**新**只读探针 `.ok`（禁 RESTORED **`10927bd9`** / **`178e90e9`** / **`c1b71e64`** / **`245df63f`** / **`c5ed13df`** / **`5774bb6e`** / **`81521fb5`**+二十票）；输出列钉 `rebal_date,n_share_rows,n_share_rows_avail_le_tts,n_weight_rows_schemeA,n_mapped,n_pressure_nonnull,n_hiliq_intersect,empty_reason`。**本 DRAFT 探针 `--allow-real-data` 未实现** → 须另开**后续真值探针票**（或同路径补实现后再 Arch 只审）后方可签窗真跑；rss=1500 禁抬；peak_proof REQUIRED；**禁**写 alpha/mask/overlap；**禁**改 `25ae4572`。
3. **C3 Option B（次步）**：探针确认 A（及可选 B）后，另开**补丁 DRAFT 票**对照 PIN `dd17044a` §1.3 vs 实现「额外 `trade_date==rebal`」及方案 A 边界；**仍禁本拍改正式脚本**；补丁落地须新脚本 sha8 + 新 X2 `.ok`（与探针窗分离）。
4. **C4 Option C**：HOLD 不解阻 / 换机制 — 并列合法；若探针显示数据层不可修复或主裁放弃本机制则取 C；**非本拍首选**。
5. **C5 禁 RESTORED / 禁夹带**：禁复用 `10927bd9`+`178e90e9`+`c1b71e64`+旧票；禁触 A18；`0087c928`/叶28/29 另队；禁 `--force`；禁 Book-Smoke。
6. **C6 口径**：≠X2 ACCEPT；leo_notify=false；live=false；ok_requested=false（本审不代申）。

## 4. Option A / B / C 审意见

| Option | Arch 意见 | 说明 |
|---|---|---|
| **A 新签只读探针窗** | **推荐 / endorse** | 唯一能把 `PIN_GAP_needs_ok_window` 填成真计数的路径；禁 RESTORED；须后续真值探针实现（本骨架 rc=3）。 |
| **B 补丁 DRAFT** | **同意为次步；本拍不开** | PIN§1.3↔实现张力已立档；在无 per-rebal 数前改脚本属盲补丁。 |
| **C HOLD 不解阻** | **并列合法；非首选** | 主若弃本机制可取 C；否则先 A。 |

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含探针新签 / RESTORED `10927bd9`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未** `--allow-real-data` 真跑（仅验证 rc=3 STOP）；**未**复跑 X2
- **未改**正式脚本（仍 **`25ae4572`**）；**未改**探针字节（仍 **`c2f2ca94`**）
- **未改** PIN `dd17044a` / VOID `dfafff28` / AI DRAFT·COVER·RECEIPT·JSON
- **未** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+旧票
- **未**抬 rss；**未**触 A18；**未开**叶36；**未改**叶33 `afbbe7e7`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
mapping recon 只审 PASS_WITH_CONDITIONS（本回执）
  → 请主择：
      → Option A（Arch 推荐）：令 AI 出后续真值探针版（列钉齐；禁改 25ae4572）
            → Arch 只审探针实现 → 主令 Arch 新签只读探针 .ok（禁 RESTORED 10927bd9）
                → AI 持新 .ok 真跑 → per-rebal JSON 填空
                    → 主裁是否开 Option B 补丁 DRAFT（对照 PIN §1.3）
      → Option B：仅在 A 填数后另票（本拍不开）
      → Option C：HOLD 不解阻（并列；非首选）
```

**本拍不签 / 不挂 / 不代跑 / 不改 `25ae4572` / 不复跑 X2**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / RECEIPT | **`350ed22b`** / **`26def8fb`** / **`fb0c7a4b`** MATCH |
| 探针 / recon JSON | **`c2f2ca94`** / **`ad4b47a2`** MATCH |
| VOID / ok VOID / QUIET lift | **`dfafff28`** / **`10927bd9`** / **`f50975e4`** MATCH |
| 正式脚本 / PIN / COUNT | **`25ae4572` UNCHANGED** / **`dd17044a`** / **`a17b75fb`** MATCH |
| 叶33 | **`afbbe7e7` UNCHANGED** |
| 嫌疑 A / B / E | **HIGH 主** / **MEDIUM 次** / **已排除** |
| EXECUTED_PROBE | **false** |
| py_compile / dry-compile / allow-real | **PASS** / **PASS** rc=0 / **STOP** rc=3 |
| 推荐 Option | **A**（新签只读探针窗 + 后续真值版；禁 RESTORED `10927bd9`） |
| B / C | 次步 / 并列非首选 |
| live `.ok` / QUIET | **0** / **ABSENT** |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | DRAFT/`350ed22b` · COVER/`26def8fb` · RECEIPT/`fb0c7a4b` · probe/`c2f2ca94` · JSON/`ad4b47a2` · VOID/`dfafff28` · formal/`25ae4572` · PIN/`dd17044a` |

**EXECUTED=false** · **EXECUTED_PROBE=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
