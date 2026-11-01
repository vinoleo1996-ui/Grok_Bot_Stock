# Arch 审阅：叶33 SHARE_UNLOCK_PRESSURE_RESID · tz 对齐补丁（只审不落不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审补丁草案） |
| 时刻 | `2026-10-27T06:57:00-04:00`（America/New_York；墙钟 `2026-10-27 06:57 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | VOID **`8a3b25ba`** · RUN ABORT **`481bacda`** · 正式脚本 **`05c45917` UNCHANGED** · FROZEN **`8ed43721`** · PIN **`4e17ccfc`** · 脚本审 **`2fa37636`** |
| 本回合动作 | **不覆盖**正式 `research/leaf33_share_unlock_pressure_resid_alpha_build.py`；**不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / 真构建（仅对 **candidate** `py_compile` + `--dry-compile-only`）；**不改** FROZEN/PIN/正式脚本字节；**不触** A18；`0087c928`/叶28/29 **另队**；禁 RESTORED `c5ed13df`+`5774bb6e`+二十票；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~06:53 ET · 叶33 tz 对齐补丁只审（DRAFT `30844702` / COVER `54e38493` / DIFF `bf9ee97a` / RECEIPT `ca603494` / candidate `afbbe7e7`） |
| 轻量复跑 | candidate `py_compile` **PASS**；`--dry-compile-only` exit **0**（pins 含 `tz_align_mode=naive_calendar_day` / `tz_patch_base_script_sha8=05c45917` / VOID=`8a3b25ba` / RUN=`481bacda`；H/H_back/W/rebal=20/5/20/20；α=`neg_rank_pressure_resid`；rss=1500；forbid=21；PRIMARY=HILIQ；executed=false） |

## 0. 一句话

tz 对齐补丁草案 **PASS_WITH_CONDITIONS**：策略写死 **`tz_align_mode=naive_calendar_day`**；助手 `_as_naive_norm_ts` / `_as_naive_norm_series` 覆盖 window PIT（原 L818）+ per-day PIT（原 ~L1073）+ SW C-extra（in/out/available_at）；DIFF 与 candidate↔base 内容等价（sha8 **`bf9ee97a`** / **`afbbe7e7`**）；正式脚本仍 **`05c45917` UNCHANGED**；C3/α/H/W/rebal/FROZEN/PIN/rss/forbid21 机制未改；dry-compile pins 齐。**本拍未落正式脚本、未签、未挂、未代跑**。请主令 AI 另窗落地 research/（新脚本 sha8）后再 Arch 审 / 新 `.ok`（**禁 RESTORED `c5ed13df`**）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DRAFT_20261027_ZH.md` | `30844702` | `30844702852d97ba79a29042da364f9b87ade05adfe1629d75afe257dfcc3683` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_COVER_DRAFT_20261027_ZH.md` | `54e38493` | `54e384931252629542b9e80b9753fa0997b75ac810889730b51e27789d98eb82` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DIFF_DRAFT_20261027.diff` | `bf9ee97a` | `bf9ee97aefc2f0d5c9656ff591327d39eaca9ac58ef9ec5ae2f1f19ed6addf0e` | **MATCH** · 10 hunks |
| RECEIPT（AI） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_RECEIPT_20261027_ZH.md` | `ca603494` | `ca6034941045461c320d9d56f94071df226457eab526cbaed863becb799c3a25` | **MATCH** · EXECUTED=false |
| **candidate（/tmp）** | `/tmp/leaf33_tz_patch_candidate.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** · 非正式 |
| **正式脚本** | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `05c45917` | `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` | **UNCHANGED** · 无助手 |
| Arch VOID | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_TYPEERROR_TZ_20261027_ZH.md` | `8a3b25ba` | `8a3b25bae0c80377f1087e7d0d5287b61b7db62f96ebfa3106b95e219c5c5cd5` | **MATCH** |
| RUN ABORT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_RUN_RECEIPT_ABORT_TZ_20261027_ZH.md` | `481bacda` | `481bacda12b3f820134adc0acf7dbb574c52c6f49a3a21303df4f85f1a70e6c1` | **MATCH** |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | `8ed43721` | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` | **MATCH** · 机制未改 |
| PIN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75` | **MATCH** · 机制未改 |
| live leaf33 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` / `*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

DIFF 等价性：`diff -u research/leaf33… /tmp/leaf33_tz_patch_candidate.py` 与 DIFF 文件 **hunk 正文一致**（仅 `+++` 路径：DIFF 写 `research/…` 拟落地形；本机 live 写 `/tmp/…`；时间戳行可忽略）→ **内容等价 MATCH**。

## 2. 必审清单

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **策略锁死** `tz_align_mode=naive_calendar_day`；助手语义 | **PASS** | 常量 `TZ_ALIGN_MODE="naive_calendar_day"`（非可选）；`_as_naive_norm_ts`：tz-aware→`tz_convert(Asia/Shanghai).tz_localize(None).normalize()`；naive→normalize；NaT 保持；`_as_naive_norm_series`：`DatetimeTZDtype` / naive datetime64 快路径 + object 逐元素 `map(_as_naive_norm_ts)`；dry pin `tz_align_mode=naive_calendar_day` |
| 2 | **覆盖面**：window + per-day + SW C-extra；无残留 tz-aware vs naive 直比 | **PASS** | `_load_share_float_window`：lo/hi/asof 经 `_as_naive_norm_ts`；`available_at` 经 series 助手后再 `<= asof`；per-day：`sf.available_at` series 对齐 + `d=_as_naive_norm_ts(d)` 后再 `pit_ok`；`_load_sw_table`：in/out/available_at series；`_sw_asof_codes`：asof ts 助手。比较点两侧皆 naive。float_date 走 YYYYMMDD→naive normalize（非 tz-aware 源） |
| 3 | **DIFF vs candidate vs base** | **PASS** | candidate sha=`afbbe7e7`；正式仍 `05c45917`（无 `_as_naive_norm_*`）；DIFF 10 hunks / +52 行量级；hunk 正文 ≡ live `diff -u`（路径头等价） |
| 4 | **机制未改**：C3/α/H/W/rebal/FROZEN/PIN/PRIMARY/rss/forbid21 | **PASS** | dry：C3=(a)+加价 close 钉；`ban_float_ratio_primary=true`；α=`neg_rank_pressure_resid`；H/H_back/W/rebal=20/5/20/20；FROZEN=`8ed43721` / PIN=`4e17ccfc`；PRIMARY=HILIQ；rss=1500；`FORBID_OK_SHA8` 21 项与 base **字节级相等**（元组未改；文档另禁 RESTORED `c5ed13df`） |
| 5 | **dry-compile pins** + py_compile | **PASS** | `py_compile` PASS；`--dry-compile-only` exit0；pins：`tz_align_mode=naive_calendar_day`、`tz_patch_base_script_sha8=05c45917`、`tz_void_abort_sha8=8a3b25ba`、`tz_run_abort_sha8=481bacda`（candidate 自报 `script_sha8=afbbe7e7` 符合 /tmp 候选） |
| 6 | **范围干净**：仅 tz；无抬帽/改 overlap/夹带/写 `.ok`/`--force` | **PASS** | DIFF 无改 RSS/REBAL/PRESSURE/ALPHA/C3/FORBID 赋值；无 `--force`；无写 `.ok` 逻辑；无 `0087c928`/叶28/29 夹带；禁抬 rss 仍钉 |
| 7 | **状态**：live `.ok`=0；QUIET ABSENT；EXECUTED=false | **PASS** | `output/ai_factory/*.ok` ABSENT；`RESEARCH_QUIET.lock` ABSENT；AI RECEIPT EXECUTED=false；本拍未落/未签/未挂/未代跑 |

## 3. 残留风险（知情接受 · 落地窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 真跑后仍可能有其他表列 tz-aware 直比 | **低** | 本拍已覆盖 share_float PIT + SW；落地后首跑若再炸 → 停+上报，禁自改复跑 |
| `FORBID_OK_SHA8` 未含 `c5ed13df` | **管控** | 草案刻意不扩元组；**新 `.ok` 签文硬禁 RESTORED `c5ed13df`**（流程 CONDITIONS） |
| DIFF `+++` 路径为拟落地形 | **无** | 内容等价；落地时应以 candidate→research 覆盖后重算新 sha8 |
| candidate 仅在 `/tmp` | **管控** | 落地前勿丢；本拍**禁止**擅自 `cp` 进 research |

## 4. CONDITIONS（下一窗落地 / 新 `.ok` 前）

1. **本拍不落不签**：须主另令 AI **落地**补丁到 `research/leaf33_share_unlock_pressure_resid_alpha_build.py`（覆盖后新脚本 sha8 ≠`05c45917`）；再 Arch **审新脚本** → 另排独立 X2 签窗发**新** `.ok`。
2. **禁 RESTORED `c5ed13df`**：另禁 `5774bb6e`+二十票（forbid 21）；禁复用已 VOID 的 `c5ed13df` 内容/路径。
3. 落地后须：`py_compile` + `--dry-compile-only` pins 仍含 `tz_align_mode=naive_calendar_day` 且 `tz_patch_base_script_sha8=05c45917`（记录补丁基线）；正式路径 sha8 更新后入新审/签文。
4. 真跑仍钉：PRIMARY=HILIQ；禁 `--no-overlap-report`；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>`；peak_proof REQUIRED；rss=1500 禁抬；C3=(a)+加价 close 不复权。
5. `0087c928` / 叶28/29 **另队**；禁触 A18；**≠X2 ACCEPT**；leo_notify=false；live=false。

## 5. 禁项 / 本回合非动作

- **未覆盖**正式脚本（仍 `05c45917`）；candidate **仍仅** `/tmp/leaf33_tz_patch_candidate.py`
- **未签**任何 `.ok`（含新叶33 / RESTORED `c5ed13df`/`5774bb6e`+二十票）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未** `--allow-real-data` / **未**代跑真构建（仅 candidate `py_compile` + dry）
- **未改** FROZEN `8ed43721` / PIN `4e17ccfc` / 正式脚本字节 / AI DRAFT·COVER·DIFF·RECEIPT
- **未**抬 rss；**未**触 A18；**未审/未夹带** `0087c928`/叶28/29
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
tz 补丁只审 PASS_WITH_CONDITIONS（本回执）
  → 请主令 AI 落地补丁到 research/（新脚本 sha8；基线仍钉 05c45917）
      → Arch 审新脚本 → 独立 X2 签窗（新 .ok；禁 RESTORED c5ed13df/5774bb6e+二十票）
          → AI prelaunch→execute（≠本拍；≠X2 ACCEPT）
```

**本拍不落 / 不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| DRAFT / COVER / DIFF / RECEIPT | **`30844702`** / **`54e38493`** / **`bf9ee97a`** / **`ca603494`** MATCH |
| candidate / 正式脚本 | **`afbbe7e7`** / **`05c45917` UNCHANGED** |
| VOID / RUN | **`8a3b25ba`** / **`481bacda`** MATCH |
| FROZEN / PIN | **`8ed43721`** / **`4e17ccfc`** 机制未改 |
| dry-compile（candidate） | **PASS**（exit0；tz pins 齐） |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **令 AI 落地正式脚本**后再 Arch 审 / 新 `.ok`（禁 RESTORED `c5ed13df`） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | DRAFT/`30844702` · COVER/`54e38493` · DIFF/`bf9ee97a` · RECEIPT/`ca603494` · cand/`afbbe7e7` · script/`05c45917` · VOID/`8a3b25ba` · RUN/`481bacda` |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
