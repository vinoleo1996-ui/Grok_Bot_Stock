# 【DRAFT — NOT FROZEN】叶33 A1 只读 `n_unlock_pool` 诊断探针票

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（后台执行器） |
| 时刻 | `2026-10-27T08:05:28-04:00`（America/New_York；墙钟 `2026-10-27 08:05 ET`） |
| 触发 | 主 · Arch复议审 **`29166bf7` PASS_WITH_CONDITIONS MATCH** → 路径 **A1 只读诊断票** |
| Arch 复议审 | **`29166bf7` MATCH** → `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_REVIEW_20261027_ZH.md` |
| 复议 DRAFT | **`b84496fe` MATCH** |
| **本拍结论** | **A1 只读诊断票 READY**（另票诊断脚本候选 + DRAFT/COVER/RECEIPT；**正式脚本 UNCHANGED**；**本拍不实跑 / 不降门 / 不自决 θ**） |
| 正式脚本 | **`afbbe7e7` UNCHANGED**（`research/leaf33_share_unlock_pressure_resid_alpha_build.py`） |
| 诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` · sha8 **`083d09fe`** |
| live | **false** |
| leo_notify | **false** |
| EXECUTED | **false** |
| ok_requested | **false** |
| ≠ | X2 ACCEPT / selfcheck / Book-Smoke / 降门补丁 / 正式 α 构建 |

---

## 0. 一句话

A1 只读 `n_unlock_pool` 诊断探针票 **READY**：另票脚本候选已落且 **dry-compile / dry-run PASS**；正式脚本 **`afbbe7e7` UNCHANGED**；本拍 **不**实跑真数据、**不**降 gate=300、**不**自决 θ（θ∈0.5–0.8 **等主钉**）。交主→Arch **只审**。

---

## 1. 钉事实（只读核对 · MATCH）

| 件 | 路径 / 值 | sha8 |
|---|---|---|
| Arch 复议审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_REVIEW_20261027_ZH.md` | **`29166bf7`** |
| 复议 DRAFT / COVER / RECEIPT | 同目录 `…COVERAGE_SPARSE_RECON_…` | **`b84496fe`** / **`4e6a1921`** / **`ab61885e`** |
| Arch VOID CONSUME | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_COVERAGE_GATE_20261027_ZH.md` | **`6826c01d`** |
| AI RUN ABORT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUN_RECEIPT_20261027_ZH.md` | **`a1b426f5`** |
| alpha | `output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet` | **`ea17e173`** |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` | **`473b339e`** |
| run_meta | `…/run_meta.json` | **`f4702783`** |
| 正式脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | **`afbbe7e7` UNCHANGED** |
| FROZEN / PIN / FROZEN审 | PREREG_FROZEN / FLOAT_RATIO_PIN / PREREG_FROZEN_REVIEW | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** |
| 本票诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` | **`083d09fe`** |
| live `.ok` / QUIET | — | **0** / **ABSENT** |

### 上游复议锚点（只引用）

- Arch C3：A1 诊断先于改门控；`n_unlock_pool` 须另票只读探针（**不改正式脚本**）。
- Arch C4：θ∈0.5–0.8 **须主钉**；本票 **不自决**。
- 主 07:56 ET：路径 = A1；推荐 A/A1；**不** endorse 降 gate；**(C) HOLD 暂不取**。

---

## 2. 度量定义（钉死）

与正式叶33 / FROZEN / run_meta 对齐：

| 符号 | 定义 |
|---|---|
| **W** | `PRESSURE_W = 20` 交易日 |
| **rebal_every_td** | `20`（正式脚本 `REBAL_EVERY`；再平衡日 = X2 窗交易日 `days[::20]`） |
| **tz_align_mode** | `naive_calendar_day`（与正式脚本 `afbbe7e7` 相同；`available_at` 取日历日） |
| **再平衡日集合** | 与叶33 X2 窗一致：`X2_START=2024-06-03` … `X2_END=2026-10-09`；本拍 run_meta `coverage_rebal` 已列 **30** 个再平衡日（只读对照） |
| **`n_unlock_pool[d]`** | 再平衡日 `d`：HI_LIQ ∩（W=20 交易日窗内存在 **≥1** 条 PIT 可见解禁事件）名数；事件源 = `share_float`；PIT = `available_at`（`naive_calendar_day`） |
| **`n_alpha[d]`** | 再平衡日 `d` 非空 `pressure_resid` / α 名数（= 正式 `coverage_rebal.n`；可由已落盘 alpha **`ea17e173`** 只读聚合交叉验证） |
| **`ratio[d]`** | `n_alpha[d] / n_unlock_pool[d]`；**分母 0 → NaN**（不填 0） |

> **本脚本 = 诊断探针**，≠正式 α 构建，≠降门补丁。真跑（另窗 + 新 `.ok`）才计算 `n_unlock_pool`；本拍 dry **不**读 `share_float` / 行情 / 掩码真表。

---

## 3. 诊断脚本候选

| 项 | 值 |
|---|---|
| 路径 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` |
| sha256（全长） | `083d09feaf5cca609b8d18657685c8d42c0e75295af18532807ea7fb4ab6a746` |
| sha8 | **`083d09fe`** |
| 默认 | `--dry-run`：只打印 pins/计划/拟输出 schema；**exit 0** |
| 真跑门 | 须同时 `--allow-real-data` + 现存 `--arch-ok-path`；缺任一项 → **STOP exit 2**；**禁** CLI 自造默认 `--arch-ok-path` |
| 正式脚本 | **禁止** import / 改写 / 覆盖；结束时 sha8 仍须 **`afbbe7e7`** |
| py_compile | **PASS**（`/tmp/leaf33_a1_diag.pyc`） |
| dry-run | **PASS**（本拍已跑默认 dry；**未** `--allow-real-data`） |
| 拟输出目录 | `output/ai_factory/_leaf33_share_unlock/diag_n_unlock_pool_v1/`（或 `/tmp/quantlab_leaf33_n_unlock_pool_diag_*`）；**本拍不写真结果** |
| sampler | 仅 `/tmp/quantlab_*` |
| forbid | 含 **`245df63f`** / **`c5ed13df`** / **`5774bb6e`**+二十票 |
| θ | **不自决**；输出禁写「建议 θ=…通过」 |

---

## 4. 只读旁证（`n_alpha` · 不读行情/share_float）

数据源：run_meta **`f4702783`** 的 `coverage_rebal`（字段 `n` = 再平衡日非空 α 名数）；并与 alpha **`ea17e173`** 按日非空计数交叉验证 → **0 mismatch**。

### 4.1 `n_alpha` 分布（30 个再平衡日）

| 统计 | 值 |
|---|---|
| n_rebal | **30** |
| median | **30.0** |
| p10 | **16.9** |
| p25 | **25.0** |
| p75 | **35.0** |
| p90 | **47.6** |
| min / max | **15** / **72** |
| mean | **32.0** |

（与复议 DRAFT / Arch审盘证 coverage median **30.0**、范围 15–72 **一致**。）

### 4.2 再平衡日 `n_alpha` 全表（只读）

| 再平衡日 | n_alpha（=coverage_rebal.n） |
|---|---|
| 2024-06-03 | 30 |
| 2024-07-02 | 24 |
| 2024-07-30 | 16 |
| 2024-08-27 | 15 |
| 2024-09-26 | 17 |
| 2024-10-31 | 40 |
| 2024-11-28 | 35 |
| 2024-12-26 | 47 |
| 2025-01-24 | 29 |
| 2025-03-03 | 28 |
| 2025-03-31 | 23 |
| 2025-04-29 | 35 |
| 2025-05-30 | 27 |
| 2025-06-30 | 36 |
| 2025-07-28 | 35 |
| 2025-08-25 | 32 |
| 2025-09-22 | 53 |
| 2025-10-28 | 30 |
| 2025-11-25 | 32 |
| 2025-12-23 | 25 |
| 2026-01-22 | 16 |
| 2026-02-27 | 25 |
| 2026-03-27 | 32 |
| 2026-04-27 | 25 |
| 2026-05-28 | 30 |
| 2026-06-26 | 28 |
| 2026-07-24 | 34 |
| 2026-08-21 | 33 |
| 2026-09-18 | 72 |
| 2026-10-09 | 56 |

### 4.3 `n_unlock_pool` / `ratio`（本拍）

| 项 | 状态 |
|---|---|
| `n_unlock_pool` 分布 | **待签窗后跑**（须读 HI_LIQ + share_float PIT；**本拍禁实跑**） |
| `ratio = n_alpha / n_unlock_pool` | **待签窗后跑** |
| θ | **未钉**（∈0.5–0.8 **等主钉**；诊断数字齐后再由主决定） |

---

## 5. 明确不做什么（硬禁自检）

| 禁 | 本拍状态 |
|---|---|
| 改正式脚本（须保持 `afbbe7e7`） | **未改** |
| 降 gate=300 / 改 `COVERAGE_MEDIAN_*` / `PRESSURE_MIN_VALID` | **未改** |
| `--allow-real-data` 真跑 / 读 share_float·行情算 `n_unlock_pool` | **未跑** |
| 复跑 X2 | **未复跑** |
| 申 `.ok` / 挂 QUIET | **未申 / 未挂** |
| RESTORED `245df63f` / `c5ed13df` / `5774bb6e`+票 | **未触** |
| 自决 θ / 写「建议 θ=…通过」 | **未自决** |
| 声称 X2 ACCEPT / Book-Smoke/selfcheck 当 ACCEPT | **否** |
| 报 Leo / 夹带叶28/29 / `0087c928` / 触 A18 | **否** |

---

## 6. 下一跳

```
本 A1 诊断票（EXECUTED=false；dry PASS）
  → 主→Arch 只审（DRAFT+COVER+RECEIPT+diag_script）
      → 主决定是否为探针另排新 .ok 签窗跑诊断（禁 RESTORED）
          → 得 n_unlock_pool / ratio 分布后
              → 主钉 θ（∈0.5–0.8）/ 是否另窗修订 FROZEN
                  → 若采纳稀疏副闸：新脚本+新 .ok → 再谈独立 X2（≠本拍）
```

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **θ 未自决** · **≠X2 ACCEPT**
