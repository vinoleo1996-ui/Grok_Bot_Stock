# AI 回执：叶34 高应计剔除 overlay 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 10:29 ET**（America/New_York；ISO `2026-10-27T10:29:55-04:00`） |
| 主令 | 2026-10-27 10:14 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`027efa26` MATCH**；FROZEN sha8 **`8be1099e` MATCH**；PIN **`bb418e6a` MATCH**；RECEIPT **`438ee33d` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（本拍只落脚本） |

## 0. 一句话

新脚本 sha8 **`482009dc`** 已落；钉 FROZEN **`8be1099e`** / RECEIPT **`438ee33d`** / Arch **`027efa26`** / PIN **`bb418e6a`**；mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**；soft-penalty 非 PRIMARY（默认关）；C3 ocf PIT+NP≤0+YTD；再平衡日懒加载 ocf；overlap vs 19/25/27/30/31/32/33；rss=1500+peak_proof；forbid `245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`；KEEP 不解阻；C11/C12 入钉；`0087c928`/叶28/29 另队；叶33 **`afbbe7e7` UNCHANGED**。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **`482009dc`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `c491e7a4bfcf40123cb4781bd8985a1df5ca6b4b96ac0e1e9ed7c879b7c6ca5d` | **`c491e7a4`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `cfa3ca4ec41a825ba0c9eb29d578c9798ed39c4120c19f1d64eef0a2629098c7` | **`cfa3ca4e`** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `f583b61645ad5a8fd2dd8e116fd91d60cc34f448e95c3fa65723b06112876919` | **`f583b616`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | — | **`8be1099e`** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | — | **`438ee33d`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`027efa26`** |
| PIN（只读） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` | — | **`bb418e6a`** |
| 叶33 正式（只读未改） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | — | **`afbbe7e7` UNCHANGED** |
| 叶32 模板（只读未改） | `research/leaf32_margin_net_flow_resid_alpha_build.py` | — | **`4e0f3c00`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_high_accrual_exclusion_overlay_v1`
- `primary_delivery` = **mask_only**；`top_q`=**0.20**；`alpha_sign`=`high_accrual_mask0_exclusion`
- C3 公式钉：`accrual_cf=1-ocf_to_profit`；PIT `e_available_at≤t`；NP≤0 剔除；`period_basis=YTD_cumulative`
- soft-penalty：**默认关闭非 PRIMARY**；`--enable-soft-penalty` 须 SW+style
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf34_high_accrual_`
- forbid ok sha8：**24** 项含 `245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`
- `primary_load`=`rebal_day_lazy_ocf_daily_pit`；peak_proof REQUIRED
- overlap：`leaf19/25/27/30/31/32/33`；披露叶25 尾窗
- `keep_does_not_unblock_x2_accept`=true；`count_approx_not_x2_accept`=true
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf34_high_accrual_exclusion_overlay_alpha_build.py', cfile='/tmp/leaf34_build.pyc', doraise=True)"
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）  
`--universe FULLA` dry → STOP PRIMARY（exit 2）

## 3. 对照 Arch CONDITIONS（`027efa26` / C1–C13）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C1** FROZEN 预注册 | 上游已 FROZEN | `8be1099e` MATCH |
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`482009dc`**；钉 FROZEN `8be1099e` + PIN `bb418e6a` |
| **C3** ocf/PIT/NP/period_basis | **入代码** | `C3_FORMULA_PIN` + lazy `_load_ocf_one_day` |
| **C4** mask-only / soft-penalty | **明示** | PRIMARY=mask_only；soft-penalty 默认关非 PRIMARY |
| **C5** top_q=0.20 | **写死** | `TOP_Q=0.20`；禁事后翻 |
| **C6** 双轨 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research`；`--universe FULLA` STOP |
| **C7** 重叠 | **已预留** | `write_overlap_report` → vs 19/25/27/30/31/32/33；Jaccard≥0.7 exit 4；叶25 尾窗披露 |
| **C8** forbid | **入钉** | `FORBID_OK_SHA8` 24 项 |
| **C9** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` |
| **C10** 另队 | **遵守** | `0087c928` 常量另队；叶28/29 不夹带 |
| **C11** overlay≠主叶 | **遵守** | 交付 exclusion mask；禁 CFACC TopN 主 α |
| **C12** APPROX≠ACCEPT | **入钉** | `count_approx_not_x2_accept=true` |
| **C13** decay KEEP | **仅钉** | 三闸+KEEP 不解阻；本脚本不跑闸 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**并入叶30 KEEP `0087c928`；**未** RESTORED forbid 集
- **未**改 FROZEN / 叶33 `afbbe7e7` / 叶32 `4e0f3c00` / HOLD `45dd87dc`
- `live=false`；`promotion_approved=false`；**不推 Leo**；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 482009dc（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED 245df63f+c5ed13df+5774bb6e+二十票+81521fb5；禁复用叶25/27/30–33）
          → X2（完整 exclusion mask + overlap 重算含 vs leaf33 + decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 sha8 | **`482009dc`** |
| COVER / CMD / DIFF sha8 | **`c491e7a4`** / **`cfa3ca4e`** / **`f583b616`** |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false**
