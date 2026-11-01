# AI 落盘回执：叶30 CRR α 构建 R3 peakcut 脚本（只落不跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 时刻 | `2026-10-27T00:17:13-0400`（America/New_York；墙钟 `2026-10-27 00:17 ET`） |
| **结论** | **R3 SCRIPT READY** · **EXECUTED=false** |
| 触发 | 主 GO · Arch 审 **`61830035`** PASS_WITH_CONDITIONS · **APPROVE_A**；提案 **`f111671a`** |
| live | **false** |
| leo_notify | **false** |
| 本拍动作 | 自 R2 基盘复制派生新脚本；**未** `--allow-real-data`；**未**挂 QUIET；**未**申 `.ok`；**未** RESTORED；**未**改 `0a264402`；**未**抬 rss；**未**混入 B 月桶 `load_mode`；**未** git commit |

## 0. 一句话

新脚本 `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` sha8 **`3ee9fed2`** 已落盘；PRIMARY=A 按 rebal **日**懒加载 `logmv_d` + 用完 del+gc + `_rss(after_logmv_rebal_YYYYMMDD)`；整窗预载 `logmv_rebal = _load_logmv_t1(..., rebal_days, …)` **已废除且无残留**；`--dry-compile-only` **PASS**；基盘 R2 **`0a264402` 未改**。交主→Arch **只审脚本**（勿签 / 勿挂 / 勿代跑）。

## 1. 钉表

| 件 | 路径 / 值 | sha8 | 全长 | 结果 |
|---|---|---|---|---|
| **新 R3 脚本** | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | **`3ee9fed2`** | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **NEW** |
| R2 基盘（禁改） | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` | `0a264402` | `0a2644021e8bbd16cbe7f69905a6a6dfcd47df3c798b6f5b272f7b6702220260` | **未改 MATCH** |
| Arch 提案审 | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_REVIEW_20261026_ZH.md` | `61830035` | `61830035fb732ecc0e2d3277b22cee8ad6dcd0dce21988a685c537755d6f8b92` | MATCH · APPROVE_A |
| AI R3 提案 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_PROPOSAL_20261026_ZH.md` | `f111671a` | `f111671abc41dd954f59aa6945d378462f545522588b461af916697173be83c1` | MATCH |
| Arch R2 VOID | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R2_VOID_ABORT_PEAK_HWM_20261026_ZH.md` | `df47501c` | （void_ref） | 入 void_ref |
| AI R2 跑回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_R2_X2_RUN_RECEIPT_20261026_ZH.md` | `fe5a2c1e` | （void_ref） | 入 void_ref |
| VOID `.ok` R2 | archived `5af20222` | `5af20222` | forbid 首项 | 禁 RESTORED |
| VOID `.ok` R1 | archived `5ae077fa` | `5ae077fa` | forbid 次项 | 禁 RESTORED |
| py_compile out | `/tmp/leaf30_r3_peakcut.pyc` | — | — | OK（禁写 repo `__pycache__`） |
| dry-compile | `--dry-compile-only` rc=0 | — | — | **PASS** |

## 2. PRIMARY=A 实现要点

1. **废除** R2 整窗预载块：`logmv_rebal = _load_logmv_t1(..., rebal_days, codes)` + `_rss("after_logmv_rebal")`。
2. 在 `for d in rebal_days:` **循环内**：
   - `logmv_d = _load_logmv_t1(Path(args.float_mktcap), [d], codes)`
   - map：`logmv_d.get((pd.Timestamp(dd), c))`（dd=d）
   - 当日消费完（含 early-continue 路径）：`del logmv_d; gc.collect(); _rss(f"after_logmv_rebal_YYYYMMDD")`
3. **禁止**残留任何整窗 `logmv_rebal = _load_logmv_t1(..., rebal_days, …)` — 源码静态断言已过。
4. **本拍省略** alpha_rebal 月 flush；**未**加入 `load_mode=month_bucket` / B 路径。
5. PIT/T−1 / overlap 必产 / Exit 94·95 / `check_rss` / rss=1500 硬帽 / `qend_ok_filter` **保持**。

## 3. 元数据钉（dry-compile 实测）

| 钉 | 值 |
|---|---|
| `schema` / `SCRIPT_REL` | `…_r3_peakcut` |
| `SAMPLER_PREFIX` | `/tmp/quantlab_leaf30_crr_r3_` |
| `r3_peakcut` | true |
| `prev_script_sha8` | `0a264402` |
| `arch_review_sha8` | `61830035` |
| `proposal_sha8` | `f111671a` |
| `void_ref` | `df47501c` / `fe5a2c1e` / `5af20222` |
| `primary_load` | `rebal_day` |
| `chunk_mode` | `month` |
| `qend_ok_filter` | true |
| `rss_limit_mb` | 1500 |
| `FORBID_OK_SHA8`（n=16） | 首项 **`5af20222`**；含 **`5ae077fa`**；其余原票保留：`5af20222, 5ae077fa, 3c297052, e107383f, 2be59acd, 1c32ab1e, ebc673bf, a7d98ac9, 8e51de63, 3a6caa4f, 8bcd79dc, 725be3e0, 0f50daf7, 3c19dd7d, 6054b3bf, 6de02e74` |
| `sign_notes` | ban_no_overlap_report；peak_proof_required=`after_daily_concat`+`after_logmv_rebal_*`；ban_restored 5af20222+5ae077fa；ban_blind_rerun a2cef5af / 0a264402-as-ticket |
| `live` | false |

## 4. DIFF 摘要（相对 R2 `0a264402`）

关键 hunk：
- **SCRIPT_REL / SAMPLER_PREFIX** → r3_peakcut / `/tmp/quantlab_leaf30_crr_r3_`
- **FORBID_OK_SHA8** 首项增 `5af20222`（共 16）
- **rebal 懒加载**：删整窗 `logmv_rebal` 预载；循环内 `logmv_d=[d]` + del+gc + `after_logmv_rebal_YYYYMMDD`
- dry/meta：`r3_peakcut=true`；`primary_load=rebal_day`；void/arch/proposal 钉

一行摘要：`PRIMARY=A rebal-day logmv lazy-load + forbid∋5af20222 + sampler/SCRIPT r3；废整窗 logmv_rebal 预载；R2 0a264402 未改。`

## 5. 验证

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf30_r3_peakcut.pyc` | **PASS** |
| `--dry-compile-only` rc=0 | **PASS** |
| 断言：qend_ok_filter / rss1500 / forbid∋5af20222+5ae077fa / r3+peakcut+rebal_day / 无整窗预载串 | **ALL_PASS** |
| repo `__pycache__` r3 | **ABSENT** |
| R2 sha8 仍 `0a264402` | **PASS** |
| 真跑 / QUIET / `.ok` / RESTORED | **未做** |

## 6. 禁项（本拍遵守）

- 禁执行 / `--allow-real-data` / 挂 QUIET / 申 `.ok`
- 禁 RESTORED `5af20222` / `5ae077fa`
- 禁盲重跑 r1 `a2cef5af` / 以 R2 `0a264402` 作新票脚本
- 禁抬 rss；禁改基盘 `0a264402`；禁混入 B `load_mode=month_bucket`
- 禁 SendToUser；≠X2 ACCEPT / selfcheck / Book-Smoke
- 禁 git commit

## 7. 下一跳

交主 → **Arch 只审脚本**（`…_r3_peakcut.py` sha8 **`3ee9fed2`**）→ 另排独立 X2 签窗（主排）。本拍 **不签 / 不挂 / 不跑**。

---

**EXECUTED=false** · **leo_notify=false** · **live=false**
