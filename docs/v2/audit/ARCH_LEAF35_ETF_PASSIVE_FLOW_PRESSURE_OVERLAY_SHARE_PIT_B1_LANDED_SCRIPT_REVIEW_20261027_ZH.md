# Arch 审阅：叶35 ETF_PASSIVE_FLOW_PRESSURE_OVERLAY · 份额 PIT B1 已落地正式脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审**已落地**正式脚本） |
| 时刻 | `2026-10-27T15:17:42-04:00`（America/New_York；墙钟 `2026-10-27 15:17 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 补丁审 **`31a08790` PASS_WC · endorse B1** · DRAFT **`bdfd3c56`** · DIFF DRAFT **`2d3abebd`** · LANDED DIFF **`06a202c3`** · COVER **`fb514f52`** · RECEIPT **`dd99468d`** · CMD **`e2773c12`** · 旧基线 **`25ae4572`**（禁当活脚本） · PIN **`dd17044a`** · FROZEN **`be9fc459`** · 叶33 **`afbbe7e7` UNCHANGED** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / `--allow-real-data` 真构建（仅对正式脚本 `py_compile` + `--dry-compile-only`）；**不改**正式脚本/PIN/FROZEN/AI LANDED 件；禁 RESTORED `25ae4572` 当活脚本 + `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票；**≠X2 ACCEPT**；**≠叶36**；live=false；**不报 Leo** |
| 触发 | 主 · 叶35 B1 新脚本另票只审 GO（AI LANDED MATCH；EXECUTED_X2=false） |
| 轻量复跑 | 正式脚本 `py_compile` **PASS**；`--dry-compile-only` exit **0**（`script_sha8=434ff42c` / PIN=`dd17044a` / FROZEN=`be9fc459` / top_q=0.20 / PRIMARY_DELIVERY=`mask_only` / rss=1500 / PRIMARY=HILIQ / C3 scheme A / C11≠叶26；executed=false） |

## 0. 一句话

落地正式脚本 **`434ff42c` MATCH**（≠旧 `25ae4572`；`/tmp/leaf35_formal_25ae4572_BEFORE.py` 仍钉旧基线）；B1 已写入：`_load_etf_flows_window` 取消 `trade_date.isin(rebal)`→`[min−40d,max]` 窗；`_pressure_on_day` 取消 `trade_date==d`→`available_at_clock≤t_ts ∧ trade_date≤d` 后 per-ETF 最新 avail；LANDED DIFF **`06a202c3`** 正文≡草案 **`2d3abebd`**（仅 DRAFT/LANDED 标注与路径头）；PIT 不前视；C3A/mask-only/top_q=0.20/C11/rss **未改**；dry-compile PASS。**本拍未签 / 未挂 / 未代跑 X2**。请主另排**新** X2 `.ok` 签窗，钉脚本 **`434ff42c` only**（禁 RESTORED `25ae4572` 当活脚本 + `00eec671`+`10927bd9`+旧票）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本 AFTER** | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` | **MATCH** · 2007 行 · ≠`25ae4572` |
| 正式 BEFORE（对照） | `/tmp/leaf35_formal_25ae4572_BEFORE.py` | `25ae4572` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **MATCH** · 仅历史；**禁 RESTORED 为活脚本** |
| LANDED DIFF | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_DIFF_20261027.diff` | `06a202c3` | `06a202c3edcda56a687063a0ac6374f41761587681418ed8b5245d93b38e7347` | **MATCH** · 正文≡草案 |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_COVER_20261027_ZH.md` | `fb514f52` | `fb514f526255072d1929d3a5bc72b24c1d7409fae735783d357a4a25672017d5` | **MATCH** |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_RECEIPT_20261027_ZH.md` | `dd99468d` | `dd99468d841617fc062ad868420fbbde4033d08395c132cbf9600fe737360402` | **MATCH** · EXECUTED_X2=false（文末自报 `d81e40f2` 为陈旧 footer，以盘上为准） |
| CMD | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_CMD_20261027_ZH.md` | `e2773c12` | `e2773c12395f110b6293d4230d7d6848010ee63c13c457872f95f83c8d41b66a` | **MATCH** · X2 占位禁跑 |
| 补丁审（Arch） | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_REVIEW_20261027_ZH.md` | `31a08790` | `31a08790967f49fb25443e81d93c0dcb68dab46a7abaa378f89d6c2ede9b3eac` | **MATCH** · PASS_WC · endorse B1 |
| DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DRAFT_20261027_ZH.md` | `bdfd3c56` | `bdfd3c56ca38591db842e3167176e683f7ed45d7564fb0672dbde98e5f701043` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DIFF_DRAFT_20261027.diff` | `2d3abebd` | `2d3abebd4032adacc6905b0db935305e1e9c767391a30540470341f217acf8c7` | **MATCH** · 对照 |
| PIN C3 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| FROZEN | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | **MATCH** |
| 叶33 正式 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| live leaf35 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` / `*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

DIFF 等价性：LANDED vs DRAFT 归一化正文 **相等**（67 hunk 行；仅 `PATCH DRAFT B1`↔`PATCH B1 LANDED` 标注 + `---`/`+++` 路径头：草案 `/tmp/…DRAFT…` → 落地两侧 `research/…`）→ **正文≡`2d3abebd` MATCH**；落地 sha8 因头差异 → **`06a202c3`**。live `diff -u` BEFORE→AFTER = 3 hunk / 仅 `_load_etf_flows_window` + `_pressure_on_day`。

## 2. 必审清单

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 新脚本 sha=`434ff42c`；与 LANDED 件一致；≠`25ae4572` | **PASS** | 全长 MATCH；dry `script_sha8=434ff42c`；BEFORE 备份仍 `25ae4572`；COVER/RECEIPT/CMD/DIFF 钉齐 |
| 2 | **B1 落地核验** | **PASS** | `_load`：无 `isin(want)`/`isin(rebal_days)`；有 `Timedelta(days=40)` 窗。`_pressure_on_day`：无 `etf_df[trade_date]==d`；有 `avail≤t_ts ∧ trade_date≤d` + `drop_duplicates(ts_code, keep=last)`。对齐补丁审 `31a08790` / PIN §1.3 / FROZEN |
| 3 | **PIT 不前视**；tz；未误扩权重/mask/top_q/C11；不降门 | **PASS** | `_t_ts_1500` + `available_at_clock≤t_ts` 仍钉；`_to_naive_sh` Asia/Shanghai；权重仍 `_asof_weight_scheme_a`；`TOP_Q=0.20`；`PRIMARY_DELIVERY=mask_only`；`ban_leaf26_full_residual_alpha_main` / C11 钉；rss=1500；`pq.read_table` 保持 |
| 4 | 相对旧脚本 diff **仅**份额 PIT | **PASS** | 3 hunk；norm 正文≡草案；他处 `isin(want)`（overlap L1189）/ `alpha_df trade_date==d`（L1226）**非**份额硬过滤，未改 |
| 5 | dry-compile / pyflakes | **PASS** | RECEIPT 记 py_compile+pyflakes PASS；本拍复核 `py_compile` PASS + `--dry-compile-only` exit0 pins 齐；**未**代跑 X2 |
| 6 | 闸门：live ok=0；QUIET ABSENT；EXECUTED_X2=false；本拍不签不挂 | **PASS** | `output/ai_factory/*.ok`=0；QUIET ABSENT；AI RECEIPT EXECUTED_X2=false；CMD X2 占位禁跑 |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 40d buffer 极端假期缺口 | **低** | 补丁审已记；首跑若仍空压 → 停+上报另票，禁自改复跑 |
| asof 跨日 flow 语义 | **低–中** | 对齐 PIN §1.3 / VTRUE pin13；签窗后盯 empty_reason/覆盖 |
| RECEIPT 文末自报 sha 陈旧 | **低** | 盘上 `dd99468d` MATCH 主钉；以盘上为准 |
| 旧 `25ae4572` 仍在 /tmp | **管控** | **禁**当新窗活脚本 / 禁 RESTORED 进 research |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；发**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`434ff42c` only**（全长 `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a`）。
2. **禁 RESTORED**：禁把 **`25ae4572`** 当活脚本；禁 `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票；禁复用 VOID/CONSUMED 路径。
3. **真跑前主 MATCH**：script 全长如上；dry-compile PASS；PIN `dd17044a` / FROZEN `be9fc459` / 补丁审 `31a08790` / 本审回执；叶33 `afbbe7e7` 不回撤。
4. **签文硬钉**：PRIMARY=HILIQ；C3 方案 A；C4 mask-only；C5 top_q=0.20；C11≠叶26；须 overlap；peak_proof REQUIRED；rss=1500 禁抬；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`；禁 `--no-overlap-report`（若脚本硬 STOP 则双闸）。
5. **PRIMARY CLI 钉**（占位；现不可跑）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf35_etf_passive_flow_pressure/<ET_TS>/`
6. Arch **不代跑**；可挂叶35 自有 QUIET（当前 QUIET **ABSENT**）。
7. live=false · promotion=false · book_smoke=false · **x2_accept=false** · **≠X2 ACCEPT** · **≠叶36**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶35 / RESTORED `00eec671`/`10927bd9`/`25ae4572` 当活脚本）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** 正式脚本 `434ff42c` / LANDED COVER·CMD·DIFF·RECEIPT / PIN / FROZEN
- **未** `--allow-real-data` / **未**代跑 X2（仅 `py_compile` + dry）；`research/__pycache__/leaf35*` 复跑后清理
- **未** RESTORED；**未**抬 rss；**未**降 top_q / 改 mask-only / 动权重方案 A
- **未碰** 叶33 `afbbe7e7`；**≠X2 ACCEPT** / ≠叶36 / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
落地脚本 434ff42c（本审 PASS_WITH_CONDITIONS · 补丁审 31a08790 endorse B1 · PIN dd17044a · FROZEN be9fc459）
  → 请主另排独立 X2 签窗（新 .ok；钉 434ff42c only；禁 RESTORED 25ae4572 活脚本 + 00eec671+10927bd9+178e90e9+c1b71e64+81521fb5+旧票）
      → AI prelaunch→execute（peak_proof；rss=1500；C11≠叶26）
          → Arch CONSUME（≠X2 ACCEPT；≠叶36）
```

**本拍不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 正式脚本 | **`434ff42c` MATCH**（≠`25ae4572`） |
| COVER / CMD / LANDED DIFF / RECEIPT | **`fb514f52`** / **`e2773c12`** / **`06a202c3`** / **`dd99468d`** MATCH |
| 补丁审 / DRAFT / DIFF DRAFT | **`31a08790` PASS_WC** / **`bdfd3c56`** / **`2d3abebd`** |
| PIN / FROZEN / 叶33 | **`dd17044a`** / **`be9fc459`** / **`afbbe7e7` UNCHANGED** |
| dry-compile | **PASS**（exit0；`script_sha8=434ff42c`；C3A/mask/top_q/C11/rss 钉） |
| EXECUTED_X2 | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（新 `.ok` 钉 `434ff42c` only；禁 RESTORED；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| ≠叶36 | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | script/`434ff42c` · COVER/`fb514f52` · CMD/`e2773c12` · LANDED DIFF/`06a202c3` · RECEIPT/`dd99468d` · 补丁审/`31a08790` · DRAFT/`bdfd3c56` · DIFF DRAFT/`2d3abebd` · base/`25ae4572` · PIN/`dd17044a` · FROZEN/`be9fc459` |

**EXECUTED_X2=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · **≠叶36**
