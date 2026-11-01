# Arch 审阅：叶33 SHARE_UNLOCK_PRESSURE_RESID · tz 已落地正式脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审**已落地**正式脚本） |
| 时刻 | `2026-10-27T07:08:00-04:00`（America/New_York；墙钟 `2026-10-27 07:08 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 补丁审 **`19cc790f` PASS_WC** · VOID **`8a3b25ba`** · RUN ABORT **`481bacda`** · FROZEN **`8ed43721`** · PIN **`4e17ccfc`** · who_pays审 **`55531e12`** · 旧基线脚本 **`05c45917`**（via `tz_patch_base_script_sha8`） |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / 真构建（仅对**正式脚本** `py_compile` + `--dry-compile-only`）；**不改**正式脚本/FROZEN/PIN/AI COVER·CMD·DIFF·RECEIPT；**不触** A18；`0087c928`/叶28/29 **另队**；禁 RESTORED `c5ed13df`+`5774bb6e`+二十票；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~07:03 ET · 叶33 tz 已落地正式脚本只审（脚本 `afbbe7e7` / COVER `9fd7af74` / CMD `7b0756db` / DIFF `99d40f9a` / RECEIPT `617f0481`） |
| 轻量复跑 | 正式脚本 `py_compile` **PASS**；`--dry-compile-only` exit **0**（pins：`tz_align_mode=naive_calendar_day` / `tz_patch_base_script_sha8=05c45917` / VOID=`8a3b25ba` / RUN=`481bacda`；H/H_back/W/rebal=20/5/20/20；α=`neg_rank_pressure_resid`；rss=1500；forbid=21；PRIMARY=HILIQ；script_sha8=`afbbe7e7`；executed=false）；`--universe FULLA`（dry 路径）STOP return **2**；无授权 STOP return **2**；FULLA+auth 真路径 STOP「FULLA forbidden as PRIMARY」return **2** |

## 0. 一句话

落地正式脚本 **`afbbe7e7` MATCH**（≠旧 `05c45917`；`cmp`≡`/tmp/leaf33_tz_patch_candidate.py`）；策略锁死 **`tz_align_mode=naive_calendar_day`**；`TZ_PATCH_BASE_SCRIPT_SHA8=05c45917` + VOID/`8a3b25ba` + RUN/`481bacda` pins 齐；助手覆盖 window PIT + per-day PIT + SW C-extra；落地 DIFF **`99d40f9a`** 正文≡草案 **`bf9ee97a`**（仅路径头标注 base sha）；C3/α/H/W/rebal/FROZEN/PIN/rss/forbid21/PRIMARY=HILIQ **未改**；dry-compile PASS。**本拍未签 / 未挂 / 未代跑**。请主另排独立 X2 签窗发**新** `.ok` 钉 **`afbbe7e7`**（**禁 RESTORED `c5ed13df`**+`5774bb6e`+二十票）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** · 2162 行 · ≠`05c45917` |
| candidate（对照） | `/tmp/leaf33_tz_patch_candidate.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** · `cmp` **IDENTICAL** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_LANDED_COVER_20261027_ZH.md` | `9fd7af74` | `9fd7af747293645700a021e75461c5fd1a6df4132b1c3f2c7492473582465045` | **MATCH** |
| CMD | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_LANDED_CMD_20261027_ZH.md` | `7b0756db` | `7b0756dbc46d2da87f95e4890ca32bca5a4afcade46dcfec4d3650c1a3b2cd7f` | **MATCH** |
| DIFF（落地） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_LANDED_DIFF_20261027.diff` | `99d40f9a` | `99d40f9a9ab1aecc3e696d9a3b98f562eee0b0271b4c1f7a10f9a0e99b14b43b` | **MATCH** · 正文≡草案 |
| DIFF（草案） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DIFF_DRAFT_20261027.diff` | `bf9ee97a` | `bf9ee97aefc2f0d5c9656ff591327d39eaca9ac58ef9ec5ae2f1f19ed6addf0e` | **MATCH** · 对照 |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_LANDED_RECEIPT_20261027_ZH.md` | `617f0481` | `617f0481bf86d720af89c75da4894d8bbfb273da25cba6bb5705ecd31865139f` | **MATCH** · EXECUTED=false（文末自报 `f1d8598a` 为陈旧 footer，以盘上 sha256 为准） |
| 补丁审（Arch） | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_REVIEW_20261027_ZH.md` | `19cc790f` | `19cc790f83b529e238e7e36b7e5142c6aa7f2d7e375098d35b7f035f408641c7` | **MATCH** · PASS_WC |
| Arch VOID | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_TYPEERROR_TZ_20261027_ZH.md` | `8a3b25ba` | （引用钉 MATCH） | **MATCH** |
| RUN ABORT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_RUN_RECEIPT_ABORT_TZ_20261027_ZH.md` | `481bacda` | （引用钉 MATCH） | **MATCH** |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | `8ed43721` | （引用钉 MATCH） | **MATCH** · 机制未改 |
| PIN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | （引用钉 MATCH） | **MATCH** · 机制未改 |
| who_pays 审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `55531e12` | （引用钉 MATCH） | **MATCH** |
| 叶32 模板 | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c00` | （只读） | **UNCHANGED** |
| live leaf33 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` / `*.ok` | 0 | 0 | **ABSENT**（旧 `c5ed13df` 仅 `_consumed`） |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

DIFF 等价性：落地 DIFF vs 草案 DIFF **归一化正文相等**（20 hunks；仅 `---` 行落地侧多 `(base 05c45917)` 标注）→ **正文≡`bf9ee97a` MATCH**；落地 sha8 因路径头差异 → **`99d40f9a`**。

## 2. 必审清单

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 正式脚本 sha=`afbbe7e7`；`cmp`≡candidate；≠`05c45917` | **PASS** | 全长 MATCH；`cmp -s` IDENTICAL；旧基线仅作 `tz_patch_base_script_sha8` 钉 |
| 2 | **策略锁死** `tz_align_mode=naive_calendar_day`；base/VOID/RUN pins；助手覆盖 window+per-day+SW | **PASS** | 常量 `TZ_ALIGN_MODE` / `TZ_PATCH_BASE_SCRIPT_SHA8=05c45917` / `TZ_VOID_ABORT_SHA8=8a3b25ba` / `TZ_RUN_ABORT_SHA8=481bacda`；`_as_naive_norm_ts/series`；window `_load_share_float_window` lo/hi/asof + `available_at`；per-day `sf.available_at`+`d`；SW in/out/available_at + `_sw_asof_codes` asof |
| 3 | DIFF `99d40f9a` 正文≡草案 `bf9ee97a`；相对旧脚本仅 tz 范围 | **PASS** | 归一化正文相等；无改 RSS/REBAL/PRESSURE/ALPHA/C3/FORBID 赋值；无 `--force`；无写 `.ok`；无叶28/29/`0087c928` 夹带 |
| 4 | C3/α/H/H_back/W/rebal/FROZEN/PIN/rss=1500/forbid21/PRIMARY=HILIQ **未改** | **PASS** | dry：C3=(a)+加价 close 钉；`ban_float_ratio_primary=true`；α=`neg_rank_pressure_resid`；H/H_back/W/rebal=20/5/20/20；FROZEN=`8ed43721` / PIN=`4e17ccfc`；PRIMARY=HILIQ；rss=1500；`FORBID_OK_SHA8` **21** 项含 `5774bb6e`（元组未扩 `c5ed13df`；文档/签文另禁 RESTORED） |
| 5 | dry-compile pins 齐；py_compile PASS；FULLA PRIMARY STOP；无授权 STOP | **PASS** | `py_compile` PASS；dry exit0 + tz pins 四钉；FULLA dry/run STOP return2；无授权 STOP return2 |
| 6 | CMD 拟 approved_cmd 含 `--allow-real-data` + `--arch-ok-path` 未来新 `.ok`；禁 `--no-overlap-report`；禁 RESTORED `c5ed13df` | **PASS** | CMD `7b0756db` 拟路径 `…LEAF33_…_X2_HILIQ.ok`；明示禁 `--no-overlap-report`；`.ok` 须新签发且 ≠`c5ed13df`；脚本真跑硬 STOP `--no-overlap-report` |
| 7 | live `.ok`=0；QUIET ABSENT；EXECUTED=false；本拍未签未挂未代跑 | **PASS** | `output/ai_factory/*.ok` ABSENT；`RESEARCH_QUIET.lock` ABSENT；AI RECEIPT EXECUTED=false；本拍仅 compile/dry；`__pycache__/leaf33*` 复跑后清为 ABSENT |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 真跑后其他表列仍可能 tz-aware 直比 | **低** | 本拍已覆盖 share_float PIT + SW；首跑若再炸 → 停+上报，禁自改复跑 |
| `FORBID_OK_SHA8` 未含 `c5ed13df` | **管控** | 刻意不扩元组；**新 `.ok` 签文硬禁 RESTORED `c5ed13df`**（流程 CONDITIONS） |
| AI RECEIPT 文末自报 sha8 陈旧 | **低** | 盘上文件 sha256=`617f0481` MATCH 主钉；以盘上为准 |
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 沿用原脚本风险；须 peak_proof；破→94/95，**禁抬帽** |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 脚本硬 STOP + 签文双闸 |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；发**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`afbbe7e7` only**（全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9`）。
2. **禁 RESTORED `c5ed13df`**：另禁 `5774bb6e`+二十票（forbid 21）；禁复用已 VOID 的 `c5ed13df` 内容/路径；禁复用叶25/27/30/31/32 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长如上；dry-compile PASS；tz pins 仍含 `naive_calendar_day` / base=`05c45917`；FROZEN `8ed43721` / PIN `4e17ccfc` / 补丁审 `19cc790f` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_sw` / `after_share_float_rebal_*` / `after_close_rebal_*` / `after_float_mktcap_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → Exit **94/95** 停+上报；**rss=1500 禁抬**。
5. **签文硬钉**：PRIMARY=HILIQ；禁 `--no-overlap-report`；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`；C3=(a)+加价 close 不复权；overlap 必写并消费（含 vs leaf32/margin_delta/hk_hold/moneyflow）。
6. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf33_share_unlock/<ET_TS>/`
7. sampler `/tmp/quantlab_leaf33_share_unlock_*`；Arch **不代跑**；可挂 leaf33 自有 QUIET（当前 QUIET **ABSENT**）。
8. **C10 仍另队**：`0087c928` / 叶28/29 不得借本脚本/签窗夹带；禁触 A18。
9. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶33 / RESTORED `c5ed13df`/`5774bb6e`+二十票）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 正式脚本 `afbbe7e7` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN
- **未** `--allow-real-data` / **未**代跑真构建（仅 `py_compile` + dry）；`research/__pycache__/leaf33*` **ABSENT**（复跑后清理）
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审/未夹带** `0087c928`/叶28/29；**未改** 叶32 模板 `4e0f3c00`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）；**未** SendToAgent（由父代理交主）

## 6. 硬钉下一跳

```
落地脚本 afbbe7e7（本审 PASS_WITH_CONDITIONS · 补丁审 19cc790f / VOID 8a3b25ba / RUN 481bacda / FROZEN 8ed43721 / PIN 4e17ccfc）
  → 请主另排独立 X2 签窗（新 .ok；钉 afbbe7e7；禁 RESTORED c5ed13df+5774bb6e+二十票；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof；rss=1500）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 正式脚本 | **`afbbe7e7` MATCH**（≠`05c45917`；≡candidate） |
| COVER / CMD / DIFF / RECEIPT | **`9fd7af74`** / **`7b0756db`** / **`99d40f9a`** / **`617f0481`** MATCH |
| 补丁审 | **`19cc790f` PASS_WC** MATCH |
| VOID / RUN / FROZEN / PIN / who_pays | **`8a3b25ba`** / **`481bacda`** / **`8ed43721`** / **`4e17ccfc`** / **`55531e12`** |
| dry-compile | **PASS**（exit0；tz pins 齐）；FULLA/无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（新 `.ok` 钉 `afbbe7e7`；禁 RESTORED `c5ed13df`；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_LANDED_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | script/`afbbe7e7` · COVER/`9fd7af74` · CMD/`7b0756db` · DIFF/`99d40f9a` · RECEIPT/`617f0481` · 补丁审/`19cc790f` · VOID/`8a3b25ba` · RUN/`481bacda` · base/`05c45917` |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
