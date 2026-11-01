# AI 回执：叶37 IMAX/隔夜彩票剔除 overlay 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 17:22 ET**（America/New_York；ISO `2026-10-27T17:22:01-04:00`） |
| 主令 | 2026-10-27 ~17:11 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`a5a9336d` MATCH**；FROZEN sha8 **`c5927f1b` MATCH**；PIN **`e01be34c` MATCH**；RECEIPT **`3992f0fa` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；py_compile **PASS**；pyflakes **CLEAN (exit 0)**；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（本拍只落脚本） |

## 0. 一句话

新脚本 sha8 **`108aba8f`** 已落；钉 FROZEN **`c5927f1b`** / RECEIPT **`3992f0fa`** / Arch **`a5a9336d`** / PIN **`e01be34c`**；mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**；soft-penalty 非 PRIMARY（默认关）；C3=B `IMAX_proxy`；再平衡日 panel→IMAX→mask；overlap 硬拒 vs 18/18v/27、披露 vs 24/34/35/36；rss=1500+peak_proof；forbid `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；KEEP 不解阻；C11/C12 入钉；叶36 HOLD CLOSED；叶33 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **`108aba8f`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `bbd16814e895e244784955b00ddd5e405533618f0c04d523ce793cfcfa06d0d6` | **`bbd16814`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `4b7351131caec10b819cbc093334cb83e21460488069d074d5002dc175e95624` | **`4b735113`** |
| DIFF DRAFT（NEW FILE vs /dev/null） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `40284f4f69a84a95f189b26d24c9a223bb444949619fba5f47329379f0b98f97` | **`40284f4f`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | — | **`c5927f1b`** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | — | **`3992f0fa`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`a5a9336d`** |
| PIN（只读） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | — | **`e01be34c`** |
| 叶33 正式（只读未改） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | — | **`afbbe7e7` UNCHANGED** |
| 叶35 正式（只读未改） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | — | **`434ff42c` UNCHANGED** |
| 叶34 模板（只读未改） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | — | **`482009dc`** |
| `research/leaf36*` | — | — | **ABSENT** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_imax_lottery_exclusion_overlay_v1`
- `primary_delivery` = **mask_only**；`top_q`=**0.20**；`alpha_sign`=`high_imax_mask0_exclusion`
- C3=B：`IMAX_proxy=mean(largest_5_finite_r_id_in_[t-19,t])`；`min_valid≥15`；`r_id=(1+ret)/(1+ret_on)-1`；`full_residual_e_id=false`；持续 APPROX
- soft-penalty：**默认关闭非 PRIMARY**；`--enable-soft-penalty` 须 SW+logmv+style
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf37_imax_lottery_`
- forbid ok sha8：**30** 项含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票
- `primary_load`=`panel_imax_proxy_rebal_cs`；peak_proof REQUIRED
- overlap：硬拒 `leaf18/18v/27`；披露 `leaf24/34/35/36`；COUNT ρ18≈0.505 / ρ27≈0.665 持续披露
- C11：`ban_leaf24_mechanism_main`=`g1g5_ashare_imax_intraday_v1`
- `keep_does_not_unblock_x2_accept`=true；`count_approx_not_x2_accept`=true
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py', cfile='/tmp/leaf37_build.pyc', doraise=True)"
/workspace/qlvenv/bin/python -m pyflakes research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）  
`--universe FULLA` dry → STOP PRIMARY（exit 2）  
`pgrep` data readers：**empty**

## 3. 对照 Arch CONDITIONS（`a5a9336d` / C1–C13）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C1** FROZEN 预注册 | 上游已 FROZEN | `c5927f1b` MATCH |
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`108aba8f`**；钉 FROZEN `c5927f1b` + PIN `e01be34c` |
| **C3** IMAX_proxy / C3=B | **入代码** | `C3_FORMULA_PIN` + `rolling_imax` + panel `r_id` |
| **C4** mask-only / soft-penalty | **明示** | PRIMARY=mask_only；soft-penalty 默认关非 PRIMARY |
| **C5** top_q=0.20 | **写死** | `TOP_Q=0.20`；禁事后翻 |
| **C6** HI_LIQ 主 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research`；`--universe FULLA` STOP |
| **C7** 重叠 | **已预留** | `write_overlap_report` → 硬拒 18/18v/27；披露 24/34/35/36；Jaccard≥0.7 exit 4 |
| **C8** forbid | **入钉** | `FORBID_OK_SHA8` 30 项含 `eb70eef4`… |
| **C9** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` |
| **C10** 叶36 HOLD | **遵守** | WHO `feaa5dbb` / JSON `575e8276` 常量；禁复开 |
| **C11** overlay≠叶24 主叶 | **遵守** | 交付 exclusion mask；`LEAF24_MECHANISM_BAN` |
| **C12** APPROX≠ACCEPT | **入钉** | `count_approx_not_x2_accept=true`；`approx=true` |
| **C13** decay KEEP | **仅钉** | 三闸+KEEP 不解阻；本脚本不跑闸 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未** RESTORED forbid 集；**未**改 FROZEN/PIN/COUNT
- **未**改叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` / HOLD `45dd87dc`
- **未**落地 `research/leaf36*`；**未**开备选 B；**未**联系 Leo
- `live=false`；`promotion_approved=false`；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 108aba8f（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED eb70eef4+00eec671+10927bd9+25ae4572+旧票；禁复用叶18/24/27/34–36）
          → X2（完整 exclusion mask + overlap 重算硬拒 18/18v/27 + 披露 24/34/35/36 + decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 sha8 | **`108aba8f`** |
| COVER / CMD / DIFF sha8 | **`bbd16814`** / **`4b735113`** / **`40284f4f`** |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false**
