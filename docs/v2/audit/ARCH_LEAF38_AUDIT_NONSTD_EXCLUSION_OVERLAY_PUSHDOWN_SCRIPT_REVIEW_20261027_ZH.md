# Arch 审阅：叶38 非标审计剔除 overlay · B1_PUSHDOWN 正式脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审 B1_PUSHDOWN 另票脚本） |
| 时刻 | `2026-10-27T22:07:45-04:00`（America/New_York；墙钟 `2026-10-27 22:07 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 新脚本 **`3a44471d`** · LAND PUSHDOWN **`37f55893`** · VOID Exit95 **`167996dd`** · 旧脚本审 **`87eb63f4`**（钉旧 `d5cf50bb`）· FROZEN **`ce0eb2ce`** · ArchFROZEN **`01753ff4`** · who_pays 审 **`acba0865`** · HI_LIQ **`c5433e80`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / `--allow-real-data`（仅 `py_compile` + `pyflakes` + `--dry-compile-only`）；**不改**脚本/LAND/VOID/FROZEN/上游件；**禁抬** rss=1500；**禁 RESTORED** `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+；**不混 fund** who_pays；叶37 HOLD CLOSED / 叶36 HOLD 不回撤；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false**；EXECUTED=false 认 |
| 触发 | 主 · 叶38 pushdown LAND READY MATCH（脚本 `3a44471d` / LAND `37f55893` / VOID `167996dd`）→ Arch 另窗只审脚本 GO（与 fund who_pays 审不混） |
| 轻量复跑 | `py_compile` **PASS**；`pyflakes` **CLEAN exit0**；`--dry-compile-only` exit **0**（`script_sha8=3a44471d` / `b1_pushdown=true` / `hiliq_load_mode=parquet_date_filters_year_chunk_pushdown` / `prev_script_sha8_readonly=d5cf50bb` / `arch_void_exit95_sha8=167996dd` / `voided_ok_sha8_ban_restored=62acf9fc` / forbid0=`62acf9fc` n=**34** / FROZEN=`ce0eb2ce` / PRIMARY=`mask_only` / rss=1500 / c4=1331200 / hard=1536000 / stop=1484800 / `section_6_1_peak_path.hiliq_parquet_date_pushdown=true` / `ban_whole_table_read_per_year=true` / executed=false）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

B1_PUSHDOWN 脚本 **`3a44471d` MATCH**（≠旧 `d5cf50bb`；同路径覆盖落地）：`_load_hiliq_mask_by_chunks` 年循环**硬核** `pq.read_table(..., filters=[(date,>=,d_lo),(date,<=,d_hi)]` ± `in_universe==True)`——**禁止**每年无 filters 整表再滤；与 VOID `167996dd` 根因（Exit95 peak≈1604 @`after_hiliq_chunk_2024`）对治对齐。rss=1500 / c4 / hard / Exit 94·95 **未抬**；FORBID 首项 **`62acf9fc`** n=**34**；§6.1 其余（分进程 Jaccard、leaf36 预落、禁 no-overlap、mask-only PRIMARY、peak_proof REQUIRED）保留；机制/厚度/Jaccard 硬拒 vs negevent·叶36 与旧票 `87eb63f4` 一致未回退；LAND `37f55893` EXECUTED=false / 未真跑 X2；2024 切片旁证 nbytes≈35× 压缩、行数 MATCH（**非** X2）；dry/py_compile/pyflakes PASS；live `.ok`/QUIET **ABSENT**。**真 pushdown 静态硬过**；全窗 peak_proof 未真跑 → **PASS_WITH_CONDITIONS**。**本拍不签**；请主另排**新独立 `.ok` 签窗**（钉 **`3a44471d` only**；禁 RESTORED `62acf9fc`+；禁抬 rss）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **B1_PUSHDOWN 脚本** | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` | `3a44471d` | `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` | **MATCH** · 1526 行 · ≠`d5cf50bb` |
| LAND PUSHDOWN RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PUSHDOWN_LAND_RECEIPT_20261027_ZH.md` | `37f55893` | `37f5589324e4947ffe9970efe489699b5853b148876ddd9298dfa8262e40ae9f` | **MATCH** · EXECUTED=false |
| Arch VOID Exit95 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_VOID_ABORT_EXIT95_20261027_ZH.md` | `167996dd` | `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895` | **MATCH** |
| 旧脚本审（只引用） | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` | `87eb63f4` | `87eb63f4805a9beaafccbe69497f5603b97bbe9b9cae50068587e678e1d1cbe9` | **MATCH** · 钉旧 `d5cf50bb` |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `ce0eb2ce` | 前8 MATCH | **MATCH** · 未改 |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `01753ff4` | 前8 MATCH | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `acba0865` | 前8 MATCH | **MATCH** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | **MATCH** |
| prev 脚本内容 | 同路径旧字节 `d5cf50bb…` | — | 现算脚本 ≠`d5cf50bb` | **旧内容已不在该路径**（只读对照常量 `PREV_SCRIPT_SHA8_READONLY=d5cf50bb`） |
| 叶34 / 叶35 / 叶37 基盘 / 叶37 B1 | `research/leaf34_*` / `leaf35_*` / `leaf37_*` / `…_b1_lowmem.py` | `482009dc` / `434ff42c` / `108aba8f` / `32605aca` | 前8 MATCH | **UNCHANGED**（B1 只读骨架；禁复用 IMAX） |
| 叶36 HOLD JSON | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` | `575e8276` | 前8 MATCH | **不回撤** |
| `research/leaf38*` | 仅正式脚本 1 件 | 1 | 1 | **MATCH** |
| VOIDED `.ok`（禁 RESTORED） | `_consumed/…62acf9fc.VOID.ABORT_EXIT95…` | `62acf9fc` | archived | **禁 RESTORED**（FORBID 首项） |
| live leaf38 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF38*` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| fund who_pays 旁线 | `docs/v2/audit/*FUND*WHO_PAYS*` | — | 本拍**未触** | **不混** |

哈希闭环：脚本常量钉 `PREV_SCRIPT_SHA8_READONLY=d5cf50bb` / `ARCH_VOID_EXIT95_SHA8=167996dd` / `VOIDED_OK_SHA8=62acf9fc` / FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays `acba0865` / HI_LIQ `c5433e80`；dry `script_sha8=3a44471d` 与本机现算 MATCH；LAND 声明 EXECUTED=false / 未真跑 X2 / 轻量 2024 旁证。

## 2. Pushdown 证据摘录（真 parquet filters · 硬核）

**VOID 根因（`167996dd`）**：旧 `_load_hiliq_mask_by_chunks` 年循环 `pq.read_table(mask_path, columns=cols)` **无 filters** → 首年 2024 整表入 RSS → peak_kb=1642812（≈1604.3 MiB）≥ hard=1536000 @`after_hiliq_chunk_2024` → Exit **95**。

**本票对治（脚本 L599–686）**：

```text
# 每年：d_lo/d_hi = year ∩ X2 window；空交 skip + 仍打 rss_cb
filt = [("date", ">=", d_lo), ("date", "<=", d_hi)]
if has_univ:
    filt.append(("in_universe", "==", True))
# TRUE pushdown — never whole-table read then filter
t = pq.read_table(mask_path, columns=cols, filters=filt)
```

| 检查 | 结果 | 证据 |
|---|---|---|
| 年循环 `pq.read_table` **必带** `filters=` | **PASS** | 唯一 HI_LIQ `read_table` 在 L651，参数含 `filters=filt`；`year_chunk=False` 分支亦带 `date>=lo & date<=hi` filters |
| 禁止每年无 filters 整表再滤 | **PASS** | 文内显式 ban；无 `pq.read_table(mask_path)` 无 filters 调用 |
| 可选 `in_universe==True` | **PASS** | schema 有列则追加；pandas 侧防御性再滤 |
| 列剪枝 + del/gc + `rss_cb(after_hiliq_chunk_YYYY)` | **PASS** | cols=date/instrument/in_universe；`after_hiliq_chunk_*` / `after_mask_by` 保留 |
| 与 VOID 根因对齐 | **PASS** | 文首/常量钉 prev=`d5cf50bb` / VOID=`167996dd` / peak@`after_hiliq_chunk_2024` |
| LAND 2024 切片旁证（非 X2） | **记为旁证** | pushdown 行=331034 = 整表再滤；nbytes 比 ≈35.14×；函数冒烟 peak≪1500；`/tmp/leaf38_pushdown_2024_proof.json`；**≠** `--allow-real-data` 全窗 |

**结论（本审点）**：**真 pushdown 静态硬过**。

## 3. 必审清单（vs VOID `167996dd` / 旧审 `87eb63f4` / FROZEN `ce0eb2ce` / §6.1·C9）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **真 parquet filters pushdown** | **PASS** | 见 §2；dry `hiliq_load_mode=parquet_date_filters_year_chunk_pushdown` / `b1_pushdown=true` / `section_6_1_peak_path.hiliq_parquet_date_pushdown=true` / `ban_whole_table_read_per_year=true` |
| 2 | **对治 VOID Exit95** | **PASS** | 根因点 `@after_hiliq_chunk_2024` 的整表读已改为带 filters；常量 `ARCH_VOID_EXIT95_SHA8`/`PREV_SCRIPT_SHA8_READONLY` |
| 3 | **rss=1500 / c4 / hard / Exit 94·95 未抬**；peak_proof REQUIRED；§6.1 其余保留 | **PASS_WITH_CONDITIONS** | `RSS_LIMIT_MB=1500` / `C4_KB=1331200` / `HARD_KB=1536000` / `STOP_KB=1484800`；`check_rss`→94/95；真路径+jaccard worker `rss_limit_mb>1500` **硬 STOP**；分进程 Jaccard / categorical·int id / OMP=1 / 禁 no-overlap 真路径 / mask-only PRIMARY / peak_proof 标签保留。**缺口（同旧审）**：CLI `--c4-kb`/`--hard-kb`/`--stop-kb` 仍可抬——须签文硬钉双保险；本拍**不改脚本** |
| 4 | **FORBID / 禁 RESTORED** 含 `62acf9fc` 首项；prev=`d5cf50bb` 只读 | **PASS** | `FORBID_OK_SHA8[0]=62acf9fc` n=**34**（旧审 33 + VOID `.ok`）；dry `voided_ok_sha8_ban_restored=62acf9fc`；`PREV_SCRIPT_SHA8_READONLY=d5cf50bb` |
| 5 | **LAND**：EXECUTED=false / 未真跑 X2 / 轻量旁证非 X2 | **PASS** | LAND `37f55893` §4–§8；dry `executed=false`；本拍未 `--allow-real-data` |
| 6 | **py_compile / 静态门** | **PASS** | `py_compile` PASS；`pyflakes` CLEAN；dry exit0；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| 7 | **机制/厚度/Jaccard 硬拒** 与旧票一致未回退 | **PASS** | mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；PRIMARY=mask-only；soft-penalty 非 PRIMARY；PIT `available_at→T1`；厚度 30/0.60/0.50；`JACCARD_HARD=0.5` vs negevent\|leaf36；disclose 34/35/37；窗 2024-06-03→2026-10-09；与 `87eb63f4` 业务钉一致 |
| 8 | **禁项核**：未签/未挂/未代跑/未抬 rss/未 RESTORED/不混 fund | **PASS** | live `.ok`=0；QUIET ABSENT；本拍只写本审票；未触 fund who_pays 文件 |

## 4. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 全窗 X2 peak_proof 未真跑（仅 2024 切片旁证） | **中** | pushdown 静态硬过；须新独立 `.ok` 真跑验 `after_hiliq_chunk_*` ≤1500；破 soft/hard→停+上报；**禁抬帽** |
| CLI `--c4-kb`/`--hard-kb`/`--stop-kb` 可被抬（`rss_limit_mb` 真路径已硬 STOP） | **管控** | 签文硬钉禁抬 c4/stop/hard；破→停 |
| leaf36 pairs 未预落 → PIN_GAP；`max=None` 不硬拒 | **管控** | 签窗须预落/重建；**禁** PIN_GAP 当硬过（同旧审） |
| `--no-overlap-report` CLI 仍在（真跑已硬 STOP） | **管控** | 脚本硬 STOP + 签文双闸 |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；不得抬作 PRIMARY |
| RESTORED `62acf9fc`（VOID.ABORT_EXIT95） | **硬禁** | forbid 首项；禁复用任何 VOID/CONSUMED 路径 |
| APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉明示不解阻 |

## 5. CONDITIONS（另窗签**新独立** `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`3a44471d` only**（全长 `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027`）；**禁**钉/跑旧 `d5cf50bb`；**禁 RESTORED** `62acf9fc`。
2. **禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+旧票**：forbid∋**34** sha8（首项 `62acf9fc`）；禁复用 VOID/CONSUMED / 叶18/24/27/30–37 任一 `.ok`；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`。
3. **真跑前主 MATCH**：script 全长如上；LAND `37f55893`；VOID `167996dd`；FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays `acba0865` / 本审回执；HI_LIQ `c5433e80`；叶34 `482009dc` / 叶35 `434ff42c` / 叶37 `108aba8f` 不回撤；叶36 HOLD `575e8276` 不复开；**旁线 fund 不混**。
4. **签文硬钉 rss=1500 禁抬**：PRIMARY CLI **不得**传 `--rss-limit-mb`>`1500` 或抬 `--c4-kb`/`--stop-kb`/`--hard-kb`；**禁**放宽 split；peak_proof REQUIRED（含 `after_hiliq_chunk_*` / `after_mask_by` / `after_audit_excl` / `after_mask_expand` / `after_jaccard_subprocess` / `final_peak_proof`）；破 soft/hard → 停+上报；**无 peak_proof≤1500 不得申 `.ok`**；须验证 pushdown 对原 ABORT 点有效。
5. **C7 签文硬钉**：真跑**必须**写并消费 overlap JSON；Jaccard>0.5 vs negevent **或** 叶36 → 硬拒；leaf36 pairs **须预落或完整重建**（PIN_GAP ≠ 硬过）；披露 34/35/37；签文 **禁** `--no-overlap-report`。
6. **PRIMARY 纪律**：判决=HILIQ **mask-only**；PIT `available_at→T1`；厚度阈不改；soft-penalty 不得作 PRIMARY；C11≠完整多空审计 α 主叶；`hiliq_load_mode` 必须保持 parquet date filters year-chunk pushdown。
7. **PRIMARY CLI 钉**（占位；现不可跑；无 `--no-overlap-report`；无抬 rss）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_PUSHDOWN_OK> --out output/ai_factory/_leaf38_audit_nonstd_exclusion/<ET_TS>/`
8. sampler `/tmp/quantlab_leaf38_audit_nonstd_*`；out `_leaf38_audit_nonstd_exclusion/<ET_TS>/`；Arch **不代跑**；本签窗 QUIET 政策由主裁（当前 QUIET **ABSENT**；本拍禁挂）。
9. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻 · KEEP 不解阻 · **不混 fund**。

## 6. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新 B1_PUSHDOWN / RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** 脚本 `3a44471d` / LAND `37f55893` / VOID `167996dd` / FROZEN / Arch 上游审
- **未** `--allow-real-data` / **未**代跑 X2 / **未** Book-Smoke（仅 `py_compile` + `pyflakes` + dry）
- **未** RESTORED；**未**抬 rss；**未**改厚度阈 / mask-only / Jaccard 阈
- **未改** 叶34/35/37；**未回撤** 叶37 HOLD CLOSED / 叶36 HOLD
- **未混** fund who_pays 另窗产物
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 7. 硬钉下一跳

```
脚本 3a44471d（本审 PASS_WITH_CONDITIONS · 真 pushdown 硬过 · prev d5cf50bb 只读 · VOID 167996dd · LAND 37f55893）
  → 请主另排独立 X2 签窗（新 .ok；钉 3a44471d only；禁 RESTORED 62acf9fc+57ab9096+b5be1164+4096d401+；禁抬 rss）
      → AI prelaunch→execute（无 --no-overlap-report；rss=1500 禁抬；peak_proof≤1500 含 after_hiliq_chunk_*；mask-only PRIMARY；leaf36 pairs 预落）
          → Arch CONSUME（≠X2 ACCEPT；叶37 HOLD CLOSED；旁线 fund 不混）
```

**本拍不签 / 不挂 / 不代跑**。建议主裁：**可开新独立 `.ok` 签窗**（钉 `3a44471d` only）；**本拍不代签**。

## 8. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 真 pushdown | **硬过**（年循环必带 date filters ± in_universe；禁整表再滤） |
| B1_PUSHDOWN 脚本 | **`3a44471d` MATCH**（≠`d5cf50bb`） |
| LAND / VOID / 旧审 | **`37f55893`** / **`167996dd`** / **`87eb63f4`** MATCH |
| FROZEN / ArchFROZEN / who_pays / HI_LIQ | **`ce0eb2ce`** / **`01753ff4`** / **`acba0865`** / **`c5433e80`** MATCH |
| forbid | 首项 **`62acf9fc`** · n=**34** |
| rss / c4 / hard / Exit | **1500** / **1331200** / **1536000** / **94·95** **未抬** |
| §6.1 / C9 | **全套保留** + pushdown 硬钉 |
| 叶34 / 叶35 / 叶37 | **UNCHANGED**；叶36 HOLD **不回撤** |
| dry / py_compile / pyflakes | **PASS**；FULLA STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排新独立 X2 签窗**（钉 `3a44471d` only；本拍不签） |
| 不混 fund | **确认** |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 9. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PUSHDOWN_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | script/`3a44471d` · LAND/`37f55893` · VOID/`167996dd` · 旧审/`87eb63f4` · FROZEN/`ce0eb2ce` · ArchFROZEN/`01753ff4` · who_pays/`acba0865` · HI_LIQ/`c5433e80` · forbid0/`62acf9fc` |

全文件 sha256 / sha8：落盘后本机 `sha256sum` 自算（文末）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑 · 不混 fund · 禁抬 rss · 禁 RESTORED `62acf9fc`+.

## 10. 本审票自算

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PUSHDOWN_SCRIPT_REVIEW_20261027_ZH.md` |
| 正文 sha256（§0–§9，不含本节） | `d1f32b5599a867971eee99208cf34cf9b0264ddcb7089e8e0e0a4d8c0e2a2ac9` |
| 正文 sha8 | `d1f32b55` |

落盘全文件 sha256 / sha8：写入本节后以本机 `sha256sum` 为准（见父回报）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑 · 不混 fund.
