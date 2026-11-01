# Arch 审阅：叶35 ETF_PASSIVE_FLOW_PRESSURE_OVERLAY · Option B 份额 PIT 补丁（只审不落不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审份额 PIT 补丁草案） |
| 时刻 | `2026-10-27T15:06:00-04:00`（America/New_York；墙钟 `2026-10-27 15:06 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| **endorse B1** | **是**（对齐 PIN §1.3；取消 `trade_date==rebal` 硬过滤；`available_at≤t_ts` asof 最新行） |
| 对照 | DRAFT **`bdfd3c56`** · COVER **`8ea77257`** · DIFF **`2d3abebd`** · RECEIPT **`3e053b3f`** · CMD **`8d35a619`** · 正式脚本 **`25ae4572` UNCHANGED** · PIN C3 **`dd17044a`** · FROZEN **`be9fc459`** · VTRUE CONSUMED **`0471f4f8`** · JSON **`446b60d1`** · 叶33 **`afbbe7e7` UNCHANGED** · consumed `.ok` **`00eec671`** · QUIET lift **`9306ceff`** |
| 本回合动作 | **只审**；**不** Apply DIFF；**不覆盖**正式 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py`；**不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / 真构建；**不** RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票；**不降门**；**不开叶36**；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 · 叶35 Option B 份额 PIT 补丁只审 GO（AI DRAFT READY MATCH；≠X2 ACCEPT；≠叶36） |

## 0. 一句话

份额 PIT 补丁草案 **PASS_WITH_CONDITIONS**：**endorse B1**——对齐 PIN **`dd17044a`** §1.3 / FROZEN **`be9fc459`**（份额**仅** `available_at≤t_ts`；**未**要求 `trade_date==rebal`）；取消正式脚本过严同日硬过滤；日侧 `available_at_clock≤t_ts ∧ trade_date≤d` 后按 ETF 取最新 `available_at`（标准 asof）；**不前视**；**不改**权重方案 A / mask-only / top_q=0.20 / C11≠叶26。五钉+正式脚本 **MATCH**；DIFF 标 **DO NOT APPLY**；正式仍 **`25ae4572` UNCHANGED**。根因闭环：VTRUE 主因 A=`share_avail_late` 30/30 直接针对。本拍**未落/未签/未挂/未代跑/未代改**。请主裁是否令 AI 落地新脚本（sha8≠`25ae4572`）→ Arch 另票只审新脚本 → 新 X2 签窗（禁 RESTORED）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DRAFT_20261027_ZH.md` | `bdfd3c56` | `bdfd3c56ca38591db842e3167176e683f7ed45d7564fb0672dbde98e5f701043` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_COVER_DRAFT_20261027_ZH.md` | `8ea77257` | `8ea772576fdf6add2a7054ec2cec891b05fd0b9800057c324db1e14183810a84` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DIFF_DRAFT_20261027.diff` | `2d3abebd` | `2d3abebd4032adacc6905b0db935305e1e9c767391a30540470341f217acf8c7` | **MATCH** · 文首 **DO NOT APPLY** |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_RECEIPT_20261027_ZH.md` | `3e053b3f` | `3e053b3f61822579fbc7c9c173d1a8f05ee320eca4742c9495613ce5ef155f62` | **MATCH** · EXECUTED=false |
| CMD | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_CMD_DRAFT_20261027_ZH.md` | `8d35a619` | `8d35a6194dd3cc2a2e64f76dbab9766e3045b468954236fd6d8bc822adbf3813` | **MATCH** · 本拍不执行 |
| **正式脚本** | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `25ae4572` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **UNCHANGED** · 仍含 `trade_date.isin(rebal)` / `trade_date==d` |
| PIN C3 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** · §1.3 仅 `available_at≤t_ts` |
| FROZEN | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | **MATCH** · 份额 PIT=`available_at≤t_ts` |
| VTRUE CONSUMED 终稿 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_CONSUMED_PASS_20261027_ZH.md` | `0471f4f8` | `0471f4f85c0b62eb69a64a88ef01c2e33a4acc56eb65e2bbc7562ec17f5b42e7` | **MATCH** |
| VTRUE JSON | `output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/mapping_recon_vtrue_per_rebal.json` | `446b60d1` | `446b60d1ccba05bfd3837843b6d4712ca2e5aa3a56eff830092197bf55a3306a` | **MATCH** · 30/30 `share_avail_late` |
| 叶33 正式 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED**（本票未触） |
| consumed `.ok` | `output/ai_factory/_consumed/…MAPPING_RECON_VTRUE_PROBE.00eec671.CONSUMED_PASS…ok` | `00eec671` | `00eec671fc904ac745752070fd4b84b8939715d350d5b089dd5de09b6c19b291` | **MATCH** · live ABSENT |
| QUIET lift | `output/loop/_lifted/…VTRUE…LIFTED_20261027T1449ET.lock` | `9306ceff` | `9306ceffba28eca00ac9f61b7a393e43a9f3b989b3105004e6898d2c34b30ea5` | **MATCH** |
| live leaf35 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` / `output/ai_factory/*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

DIFF 闸门：文首 `# DRAFT ONLY — DO NOT APPLY`；`+++` 指向 `/tmp/leaf35_share_pit_patch_DRAFT_B1_copy.py`（非正式）；`---` 标 `formal 25ae4572 UNCHANGED — DO NOT PATCH` → **本拍禁止落地**。

## 2. 必审清单

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **五钉 + 正式脚本 UNCHANGED**；DIFF 标 DO NOT APPLY | **PASS** | 上表 MATCH；正式 L843–844 仍 `isin(want)`、L861 仍 `trade_date==d`；DIFF 未 Apply |
| 2 | **AI 荐 B1** 对齐 PIN §1.3 | **PASS · endorse B1** | PIN §1.3：**仅** `available_at≤t_ts`；**未**要求同日 `trade_date`。B1：`_load` 窗 `[min(rebal)−40d, max(rebal)]` 取消 `isin(rebal_days)`；`_pressure_on_day`：`avail≤t_ts ∧ trade_date≤d` → 按 ETF 最新 avail。与 FROZEN §1.1「份额 PIT=`available_at≤t_ts`」同向 |
| 2a | **PIT 不前视** | **PASS** | 决策点仍 `_t_ts_1500(d)`=当日 15:00 Asia/Shanghai naive；过滤器保留 `available_at_clock≤t_ts`（严禁 >t_ts）；附加 `trade_date≤d` 禁未来交易日份额点；合法集内 `sort_values(available_at_clock).drop_duplicates(ts_code, keep=last)`=标准 asof。tz：沿用正式 `_to_naive_sh`（tz-aware→`Asia/Shanghai` localize None）与叶33/`afbbe7e7` naive 墙钟比较口径一致；DIFF **未改** tz 助手 |
| 2b | **与 PIN/FROZEN 张力** | **PASS（无有害张力）** | **不改** C3 权重方案 A（`_asof_weight_scheme_a` / 次月首交易日 09:00 合成）；**不改** mask-only / top_q=0.20 / Jaccard≥0.7 / rss=1500 / C11≠叶26；B1 仅消解「实现比 PIN 更严」的同日硬过滤。B3 才须修订钉文——本票不推 |
| 2c | **B2/B3 备选** | **PASS** | B2=保留同日+放宽时钟 → **易踩前视**，不荐；B3=修订 PIN/FROZEN 追认同日 → 近 Option C，须主裁，本票不推。**endorse B1** |
| 3 | **根因闭环**（主因 A） | **PASS** | VTRUE JSON `446b60d1`：30/30 `share_avail_late`；同日 `n_share_rows=3` 且 `avail_le_tts=0`；`pin13_avail_only`≈4695–6405；权重 schemeA=1800 **非主因**。B1 直接取消同日硬过滤、改 PIN§1.3 asof → 针对 A；**未**扩权重侧 / **未**降门 / **未**复跑 X2 |
| 4 | **闸门** | **PASS** | live leaf35 `.ok`=0；`output/ai_factory/*.ok`=0；QUIET ABSENT；禁 RESTORED 列表仍归档于 `_consumed`（未 RESTORED）；本拍不签不挂不代跑不代改；≠X2 ACCEPT；≠叶36；EXECUTED=false；leo_notify=false；live=false |
| 5 | **范围干净** | **PASS** | DIFF 仅 `_load_etf_flows_window` 预滤 + `_pressure_on_day` 日侧选取；保持 `pq.read_table`；无改 TOP_Q/PRIMARY/FORBID/rss/权重/映射三件套；无 `--force`；无写 `.ok` 逻辑；无夹带叶33/叶36 |

## 3. 残留风险（知情接受 · 落地窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 40d buffer 是否覆盖全部可 asof 行 | **低** | VTRUE 样例再平衡日前一交易日行已可用；若极端假期缺口 >40d → 落地后诊断再扩 buffer（另票），禁本拍拍脑袋 |
| asof 取「最新 available_at」跨多日 trade_date 后 flow 语义 | **低–中** | PIN §1.3 未钉「必须同日 flow」；与 COUNT/pin13_avail_only 口径同向。落地后首跑须盯 empty_reason / 覆盖；若异常 → 停+上报，禁自改复跑 |
| DIFF 仅 /tmp 候选；正式未落 | **管控** | 本拍禁止 `patch -p` / `cp` 进 research；须主另令 AI 落地 |
| 落地后仍可能空压（权重/映射侧） | **低** | VTRUE 已证 B 非主因；若 B1 后仍 STOP_ZERO_MASK_ROWS → 新诊断票，禁当 X2 ACCEPT |

## 4. CONDITIONS（下一窗落地 / 新 `.ok` 前）

1. **本拍不 Apply**：DIFF **`2d3abebd`** 标 DO NOT APPLY；正式须保持 **`25ae4572`** 直至主另令。
2. **主令 AI 落地**：覆盖/写出新 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py`（新 sha8 **≠`25ae4572`**）；基线钉 `share_pit_patch_base_script_sha8=25ae4572`。
3. **另票 Arch 只审新脚本**（非本拍、非自动升签）→ 通过后再主签**新** X2 `.ok`。
4. **禁 RESTORED**：`00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票；禁复用 VOID/CONSUMED 路径内容。
5. 真跑仍钉：PRIMARY=HILIQ；C3 方案 A；C4 mask-only；C5 top_q=0.20；须 overlap；peak_proof；rss=1500 禁抬；C11≠叶26；禁 `--no-overlap-report`；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`。
6. **≠X2 ACCEPT**；**≠叶36**；禁 Book-Smoke；禁复跑旧 X2；leo_notify=false；live=false。

## 5. 禁项 / 本回合非动作

- **未** Apply DIFF / **未**改正式脚本（仍 `25ae4572`）
- **未签**任何 `.ok`（含新叶35 / RESTORED `00eec671`/`10927bd9`/…）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未**代跑 X2 / `--allow-real-data` / 真构建
- **未改** PIN `dd17044a` / FROZEN `be9fc459` / 叶33 `afbbe7e7` / AI DRAFT·COVER·DIFF·RECEIPT·CMD 字节
- **未**降 top_q / 改 mask-only / 动权重方案 A / 触 C11
- **≠X2 ACCEPT** / ≠叶36 / ≠selfcheck ACCEPT
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
份额 PIT 补丁只审 PASS_WITH_CONDITIONS · endorse B1（本回执）
  → 请主裁是否令 AI 落地 B1 到 research/（新脚本 sha8 ≠ 25ae4572）
      → Arch 另票只审新脚本
          → 主签新 X2 .ok（禁 RESTORED 00eec671+10927bd9+178e90e9+c1b71e64+81521fb5+旧票）
              → AI prelaunch→execute（≠本拍；≠X2 ACCEPT；≠叶36）
```

**本拍不落 / 不签 / 不挂 / 不代跑 / 不代改**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| endorse B1 | **是** |
| DRAFT / COVER / DIFF / RECEIPT / CMD | **`bdfd3c56`** / **`8ea77257`** / **`2d3abebd`** / **`3e053b3f`** / **`8d35a619`** MATCH |
| 正式脚本 | **`25ae4572` UNCHANGED** |
| PIN / FROZEN | **`dd17044a`** / **`be9fc459`** MATCH · B1 对齐 §1.3 |
| VTRUE CONSUMED / JSON | **`0471f4f8`** / **`446b60d1`** · 主因 A 闭环 |
| 叶33 | **`afbbe7e7` UNCHANGED** |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **裁是否令 AI 落地 B1** → 另票 Arch 审新脚本 → 新签窗（禁 RESTORED） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| ≠叶36 | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| endorse B1 | **是** |
| 上游钉 | DRAFT/`bdfd3c56` · COVER/`8ea77257` · DIFF/`2d3abebd` · RECEIPT/`3e053b3f` · CMD/`8d35a619` · script/`25ae4572` · PIN/`dd17044a` · FROZEN/`be9fc459` · CONSUMED/`0471f4f8` · JSON/`446b60d1` |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · **≠叶36**
