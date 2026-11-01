# AI 落盘回执：叶37 IMAX/lottery exclusion overlay · B1 / LOW_MEM 脚本（只落不跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 时刻 | `2026-10-27T18:09:50-04:00`（America/New_York；墙钟 `2026-10-27 18:09 ET`） |
| **结论** | **B1_LOWMEM SCRIPT READY** · **EXECUTED=false** |
| 触发 | 主裁 LOW_MEM_PATCH GO ~18:02 ET · Arch VOID.ABORT_PEAK **`998171e1`** · 基盘 **`108aba8f` 禁改** |
| live | **false** |
| leo_notify | **false** |
| 本拍动作 | 自基盘复制派生并列 `*_b1_lowmem.py`；年分块 panel/`r_id` + instrument 列块 IMAX；**未** `--allow-real-data`；**未**挂 QUIET；**未**申 `.ok`；**未** RESTORED；**未**改 `108aba8f`；**未**抬 rss；**未** git commit |

## 0. 一句话

新脚本 `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` sha8 **`32605aca`** 已落盘；`b1_lowmem=true`；`prev_script_sha8=108aba8f`；forbid 首项 **`4096d401`**（n=31）；`--dry-compile-only` **PASS**；pyflakes **CLEAN**；基盘 **`108aba8f` 未改**。交主→Arch **只审 B1_LOWMEM 脚本**（勿签 / 勿挂 / 勿代跑）。

## 1. 钉表

| 件 | 路径 / 值 | sha8 | 全长 | 结果 |
|---|---|---|---|---|
| **新 B1 脚本** | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` | **`32605aca`** | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **NEW** |
| 基盘（禁改） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **未改 MATCH** |
| COVER | `…_B1_LOWMEM_COVER_DRAFT_20261027_ZH.md` | `a4bfa39d` | `a4bfa39dce43a4c7c9d06fdbb4db06482610c520dced6524899ca05e5998b084` | NEW |
| CMD | `…_B1_LOWMEM_CMD_DRAFT_20261027_ZH.md` | `286e2104` | `286e2104466c01170a8744c3bbd8c67a2a6ed2de24e0b3b8f69511b470c1843f` | NEW |
| DIFF | `…_B1_LOWMEM_DIFF_DRAFT_20261027.diff` | `6d61fd79` | `6d61fd790e589f2d283f629c906393d1ff90eb997496f780ebc851701438ec96` | NEW vs 108aba8f |
| Arch VOID | `…_X2_VOID_ABORT_PEAK_20261027_ZH.md` | `998171e1` | — | MATCH |
| AI RUN_RECEIPT | `…_X2_RUN_RECEIPT_20261027_ZH.md` | `c2a120f7` | — | MATCH |
| ACK | `…_X2_RUNNING_ACK_20261027_ZH.md` | `dd8a7d2e` | — | MATCH |
| VOID `.ok` | archived `4096d401` | `4096d401` | forbid 首项 | 禁 RESTORED |
| FROZEN / PIN / 审 | — | `c5927f1b` / `e01be34c` / `8d8ae2f3` | — | 未改 |
| py_compile out | `/tmp/leaf37_b1_lowmem.pyc` | — | — | OK |
| dry-compile | `--dry-compile-only` rc=0 | — | — | **PASS** |
| pyflakes | qlvenv | — | — | **CLEAN** |

## 2. B1 LOW_MEM 实现要点

1. **禁止**一次拼全窗 panel 峰值：`for y in 2023..2026` 读 `cs_panel_YYYY.parquet`（列 `date,instrument,hiliq,ret,ret_on` + date filter warm..x2）→ merge HI_LIQ key → 算 `r_id` → 只留 `in_hiliq & r_id.notna` 瘦长行 → **del+gc** → `_rss(after_panel_year_YYYY)` / `after_r_id_year_YYYY`。
2. 瘦长 `concat` 后 pivot；`rolling_imax` **按 instrument 列块**（step=256），块内算完 `piv.drop`+gc；`_rss(after_imax_instr_chunk_*)` / `after_panel_imax`。
3. `check_rss` / Exit 94·95 / rss=1500 / peak_proof **保持**；**禁**抬 `--rss-limit-mb`；**禁**放宽 split。
4. 契约不变：mask-only q=0.20；C3=B；C11≠叶24；overlap 硬拒 18/18v/27；披露 24/34/35/36；KEEP 不解阻；COUNT APPROX≠ACCEPT。
5. sampler=`/tmp/quantlab_leaf37_imax_lottery_b1_`；forbid 首项 `4096d401`（n=31）。

## 3. 元数据钉（dry-compile 实测）

| 钉 | 值 |
|---|---|
| `schema` / `SCRIPT_REL` | `…_b1_lowmem_v1` / `…_b1_lowmem.py` |
| `SAMPLER_PREFIX` | `/tmp/quantlab_leaf37_imax_lottery_b1_` |
| `b1_lowmem` | true |
| `prev_script_sha8` | `108aba8f` |
| `void_ok_sha8` / VOID refs | `4096d401` / `998171e1` / `c2a120f7` / `dd8a7d2e` |
| `primary_load` | `panel_year_chunk_r_id_instr_chunk_imax` |
| `primary_delivery` / `top_q` / `c3_option` | `mask_only` / `0.20` / `B` |
| `rss_limit_mb` | 1500 |
| `FORBID_OK_SHA8`（n=31） | 首项 **`4096d401`**；含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票 |
| `peak_proof_required` | `after_mask` / `after_panel_year_*` / `after_r_id_year_*` / `after_r_id` / `after_imax_instr_chunk_*` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat` |
| `live` | false |

## 4. DIFF 摘要（相对基盘 `108aba8f`）

关键 hunk：
- **NEW FILE** 并列（禁改基盘）；`SCRIPT_REL` / `SAMPLER_PREFIX` → b1
- **FORBID_OK_SHA8** 首项增 `4096d401`（共 31）
- **`_load_panel_imax`**：年分块 + 瘦长保留 + instr 列块 IMAX + 分块 rss 标签
- dry/meta：`b1_lowmem=true`；`prev_script_sha8=108aba8f`；peak_proof 分块标签；schema b1

一行摘要：`B1 year-chunk panel+r_id + instr-chunk IMAX；forbid∋4096d401；基盘 108aba8f 未改。`

## 5. 验证

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf37_b1_lowmem.pyc` | **PASS** |
| pyflakes CLEAN | **PASS** |
| `--dry-compile-only` rc=0 | **PASS** |
| 无授权 STOP exit 2 | **PASS** |
| `--universe FULLA` dry STOP exit 2 | **PASS** |
| dry pins：b1 / prev / forbid∋4096d401 / rss1500 / C3=B / mask_only / q=0.20 | **ALL_PASS** |
| 基盘 sha8 仍 `108aba8f` | **PASS** |
| 真跑 / QUIET / `.ok` / RESTORED | **未做** |

## 6. 禁项（本拍遵守）

- 禁执行 / `--allow-real-data` / 挂 QUIET / 申 `.ok`
- 禁 RESTORED `4096d401` / `eb70eef4` / `00eec671` / `10927bd9` / `25ae4572`+旧票
- 禁抬 rss；禁改基盘 `108aba8f`；禁改 FROZEN/PIN；禁复开叶36
- 禁 SendToUser；≠X2 ACCEPT / selfcheck / Book-Smoke
- 禁 git commit

## 7. 下一跳

交主 → **Arch 只审 B1_LOWMEM 脚本**（`…_b1_lowmem.py` sha8 **`32605aca`**）→ 另排独立 X2 签窗（主排；钉 B1 only；禁 RESTORED `4096d401`）。本拍 **不签 / 不挂 / 不跑**。

---

**EXECUTED=false** · **leo_notify=false** · **live=false**
