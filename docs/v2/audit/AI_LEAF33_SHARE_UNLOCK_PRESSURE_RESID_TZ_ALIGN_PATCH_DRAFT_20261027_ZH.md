# 叶33 SHARE_UNLOCK_PRESSURE_RESID · tz 对齐补丁草案（只审；不实跑）

- **角色**：QuantLab AI
- **时刻**：2026-10-27T06:51:37-04:00（America/New_York；墙钟 2026-10-27 06:51 ET）
- **状态**：**PATCH_DRAFT ONLY** · **EXECUTED=false** · **ok_requested=false** · **未申 `.ok`** · **未挂 QUIET** · live=false · promotion_approved=false
- **主令**：~06:44 ET；Arch VOID 回执 sha8 **`8a3b25ba` MATCH**；RUN ABORT **`481bacda` MATCH**；对照脚本 **`05c45917` UNCHANGED**
- **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · leo_notify=false

## 0. 一句话

根因：`_load_share_float_window` L818 处 `available_at`（`datetime64[us, Asia/Shanghai]`）与 naive `asof` 比较 → TypeError；per-day PIT ~L1073 同类。本拍**写死**对齐策略 **`tz_align_mode=naive_calendar_day`**（与叶32 margin PIT / 本脚本 trade_date/asof 惯例一致；**不**选整链 Asia/Shanghai）。候选脚本落 `/tmp/leaf33_tz_patch_candidate.py` sha8 **`afbbe7e7`**；unified DIFF 已落；**正式路径 `research/leaf33_share_unlock_pressure_resid_alpha_build.py` 仍为 `05c45917` 未覆盖**。交主→Arch **只审补丁**。不实跑 / 不申新 `.ok`。

## 1. 上游 MATCH

| 项 | sha8 | 状态 |
|---|---|---|
| Arch VOID 回执 | **`8a3b25ba`** | MATCH（`.ok` `c5ed13df` VOID 归档；live `.ok`=0） |
| QUIET lift | **`53ea26ba`** | MATCH；live QUIET ABSENT |
| RUN ABORT 回执 | **`481bacda`** | MATCH（ABORT_TYPEERROR_TZ） |
| 对照脚本（必须 UNCHANGED） | **`05c45917`** | MATCH；本拍**未**改正式路径 |
| FROZEN / PIN | **`8ed43721`** / **`4e17ccfc`** | 机制钉**未动** |
| SIGNED / 审（只引用） | `aaaff921` / `2fa37636` | 上游 |

## 2. 根因（钉）

```
TypeError: Cannot compare tz-naive and tz-aware datetime-like objects
File ".../leaf33_share_unlock_pressure_resid_alpha_build.py", line 818
    pit_ok = df["available_at"].isna() | (df["available_at"].dt.normalize() <= asof)
```

- `share_float_pit.available_at` → `datetime64[us, Asia/Shanghai]`（tz-aware）
- `asof = pd.Timestamp(asof_max).normalize()` → tz-naive
- per-day PIT ~L1073–1074：`eg["available_at"].dt.normalize() <= d`（`d` naive）同类风险
- peak_kb≈450768 ≪1500；**非 RSS**；alpha/overlap ABSENT

## 3. 对齐策略（写死 · 二选一已选定）

**选用：`naive_calendar_day`**（统一 naive 日历日）。

| 否决选项 | 原因 |
|---|---|
| 整链 `Asia/Shanghai` 后再 normalize | 与叶32 margin PIT / 本脚本 trade_date、rebal `asof`、日历日惯例不一致；扩散面更大 |

### 实现要点

1. 新增助手：
   - `_as_naive_norm_ts(x)`：tz-aware → `tz_convert("Asia/Shanghai").tz_localize(None)` → `.normalize()`；naive → `.normalize()`；NaT 保持
   - `_as_naive_norm_series(s)`：`DatetimeTZDtype` 快路径；naive `datetime64` 快路径；object/mixed **逐元素**（避免混 dtype 时 naive→NaT）
2. `_load_share_float_window`：`asof/lo/hi` 经 `_as_naive_norm_ts`；`df["available_at"]` 经 `_as_naive_norm_series`；再做 `pit_ok`（两侧皆 naive）
3. per-day PIT（原 ~L1073）：`d` 与 `eg["available_at"]` 两侧均经同一助手后再比较（`sf` 入口处先 series 对齐）
4. **C-extra（本拍一并纳入，推荐）**：`_load_sw_table` 的 `in_date/out_date/available_at` + `_sw_asof_codes` 的 `asof` 同助手，避免下一拍 SW 路径再炸
5. dry-compile pins 新增：
   - `tz_align_mode=naive_calendar_day`
   - `tz_patch_base_script_sha8=05c45917`
   - `tz_void_abort_sha8=8a3b25ba`
   - `tz_run_abort_sha8=481bacda`

## 4. 触及行号（相对 `05c45917`）

| 区域 | 原行号（约） | 拟改 |
|---|---|---|
| 常量 | PIN_SHA8 后 | + `TZ_ALIGN_MODE` / `TZ_PATCH_BASE_SCRIPT_SHA8` / VOID/RUN sha8 |
| 助手 | `normalize_universe` 后 | + `_as_naive_norm_ts` / `_as_naive_norm_series` |
| dry-compile | pin_sha8 附近 | + tz_* pins；note 追加 tz 引用 |
| `_load_sw_table` | ~602–604 | series 助手 |
| `_sw_asof_codes` | ~611 | `asof` 助手 |
| `_load_share_float_window` | ~785–818 | lo/hi/asof + available_at + pit_ok |
| `_compute_pressure_and_styles` | ~982–983 / ~1068–1075 | sf.available_at + per-day PIT |

DIFF 文件：`docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DIFF_DRAFT_20261027.diff` sha8 **`bf9ee97a`**。

## 5. 不变钉（禁改）

- C3=(a)+加价：`unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`；表内 `float_ratio` PRIMARY 禁用
- α=`−rank(pressure_resid)`；H/H_back/W/rebal=20/5/20/20
- FROZEN **`8ed43721`** / PIN **`4e17ccfc`** 机制
- rss=1500 禁抬；peak_proof REQUIRED；Jaccard≥0.7 硬拒
- overlap 目标清单；KEEP 三闸+**KEEP 不解阻**
- `FORBID_OK_SHA8` 元组**语义未改**（仍 21 项；`5774bb6e`+二十票）— 本拍 **文档声明** 另禁 RESTORED **`c5ed13df`**（VOID 票），不在本 DIFF 改元组以免夹带政策扩面；Arch 签新 `.ok` 时由主/Arch 显式禁 RESTORED

## 6. 禁令

- **禁**把候选覆盖回 `research/leaf33_*`（等 Arch 只审通过 + 主令落地）
- **禁**实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit
- **禁 RESTORED** `c5ed13df` + `5774bb6e` + 二十票
- **禁**复用已 VOID 的 `c5ed13df`；**禁**擅 lift QUIET（当前 live QUIET 已 ABSENT）
- `0087c928` / 叶28/29 **另队**；不报 Leo；≠X2 ACCEPT

## 7. 验证（本拍已做）

| 检查 | 结果 |
|---|---|
| 正式脚本 sha256 | **`05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2`** → sha8 **`05c45917` UNCHANGED** |
| 候选 `py_compile` → `/tmp` | **PASS** |
| 候选 `--dry-compile-only`（qlvenv） | **PASS**；pins 含 `tz_align_mode=naive_calendar_day` / base=`05c45917` / VOID=`8a3b25ba` / RUN=`481bacda` |
| 助手单测（Shanghai-aware vs naive 比较） | **PASS**（不再 TypeError） |
| `--allow-real-data` / 真跑 / 申 `.ok` / QUIET | **未做** |

## 8. 产出路径

| 件 | 路径 |
|---|---|
| DRAFT（本文件） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_COVER_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DIFF_DRAFT_20261027.diff` |
| RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_RECEIPT_20261027_ZH.md` |
| 候选（/tmp；非正式） | `/tmp/leaf33_tz_patch_candidate.py` sha8 **`afbbe7e7`** |

## 9. 下一跳

```
本 DRAFT + COVER + DIFF + RECEIPT
  → 主令 Arch 只审补丁
      → PASS 后另窗：落地补丁到 research/（新脚本 sha8）+ 新 .ok（禁 RESTORED c5ed13df/5774bb6e+二十票）
          → 再谈 X2 重跑（≠本拍；≠X2 ACCEPT）
```

**EXECUTED=false** · live=false · leo_notify=false · ok_requested=false
