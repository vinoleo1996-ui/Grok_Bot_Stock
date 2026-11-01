# 叶35 ETF 被动压力 overlay · **mapping recon DRAFT**（非叶36）

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:07 ET (America/New_York)；ISO `2026-10-27T14:07:35-04:00`
- **票种**：**诊断票（mapping recon）** · **≠叶36** · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck**
- **状态**：HOLD CLOSED 后另开；**只读证据合成** · **EXECUTED_PROBE=false** · **未**复跑 X2 · **未**申 `.ok` · **未**挂 QUIET · **未**改正式脚本
- **正式脚本钉**：`research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`**（全长 `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0`）**本拍不改**

## 0. HOLD 闭合核（MATCH）

| 项 | sha8 / 值 |
|---|---|
| Arch VOID | **`dfafff28`** → `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_VOID_ABORT_ZERO_MASK_ROWS_20261027_ZH.md` |
| `.ok` VOID 归档 | **`10927bd9`** → `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.10927bd9.VOID.ABORT_ZERO_MASK_ROWS.20261027T1359ET.ok` |
| QUIET lift | **`f50975e4`** → `output/loop/_lifted/RESEARCH_QUIET_leaf35_etf_passive_flow_pressure_overlay_x2_ABORT_ZERO_MASK_ROWS_LIFTED_20261027T1359ET.lock` |
| live `.ok` / QUIET | **0 / ABSENT**（本拍复核） |
| X2 RUN_RECEIPT | **`1e255fff`**；ET_TS=`20261027_135145` |
| stdout / stderr | **`7f7f813d`** / **`e0cd835f`** |
| PIN C3 / FROZEN / COUNT JSON | **`dd17044a`** / **`be9fc459`** / **`a17b75fb`**（APPROX≠方案 A） |
| 叶33 正式 | **`afbbe7e7` UNCHANGED**（本票不触） |

## 1. 问题陈述

X2（pid 470069；rc=1）在 `after_mask` → `after_weight_pin` → `after_etf_share_window` 之后，对 **30** 个再平衡日逐一打出 `after_pressure_rebal_*`，但 **从未**进入 `after_mask_cs_rebal_*` / daily concat / overlap 写出；最终：

```
STOP: zero mask rows (check etf share / weights scheme A / HI_LIQ / top_q)
```

→ status **`STOP_ZERO_MASK_ROWS`**；Arch **VOID.ABORT_ZERO_MASK_ROWS**（`dfafff28`）。回执与 VOID 旁注：每日 `press empty/unmappable`（脚本 L1403–1407 `gap=pressure_empty_or_unmappable`）→ `rebal_rows` 空 → L1498–1501 `SystemExit`。

本票目标：用**已有**日志/回执/COUNT APPROX/PIN/脚本源码/parquet**仅列名·存在性**，分类空压根因，并给出供主/Arch 裁的 Option（**不自决复跑**）。

## 2. 证据链（只读）

### 2.1 X2 stdout 阶段链

| 阶段 | 状态 | 备注 |
|---|---|---|
| `after_mask` | PRESENT | peak_kb=**528588**（HI_LIQ 已载） |
| `after_weight_pin` | PRESENT | 方案 A 合成未在 load 期 PIN_GAP 退出 |
| `after_etf_share_window` | PRESENT | major 份额窗已载（RSS 略升） |
| `after_pressure_rebal_*` | **PRESENT ×30** | 日期见下表；**无** per-day 计数落盘 |
| `after_mask_cs_rebal_*` | **ABSENT ×30** | 从未进入 top_q / mask_cs |
| `after_daily_concat` | ABSENT | STOP 于 rebal_rows 空 |
| alpha/mask/overlap/run_meta | ABSENT | OUT 仅 stdout/stderr |

### 2.2 30× rebal 日（log-derived）

| # | rebal_date | log marker | after_mask_cs | 推断 empty_reason（待探针填数） |
|---|---|---|---|---|
| 1 | 2024-06-03 | `after_pressure_rebal_20240603` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 2 | 2024-07-02 | `after_pressure_rebal_20240702` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 3 | 2024-07-30 | `after_pressure_rebal_20240730` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 4 | 2024-08-27 | `after_pressure_rebal_20240827` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 5 | 2024-09-26 | `after_pressure_rebal_20240926` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 6 | 2024-10-31 | `after_pressure_rebal_20241031` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 7 | 2024-11-28 | `after_pressure_rebal_20241128` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 8 | 2024-12-26 | `after_pressure_rebal_20241226` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 9 | 2025-01-24 | `after_pressure_rebal_20250124` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 10 | 2025-03-03 | `after_pressure_rebal_20250303` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 11 | 2025-03-31 | `after_pressure_rebal_20250331` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 12 | 2025-04-29 | `after_pressure_rebal_20250429` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 13 | 2025-05-30 | `after_pressure_rebal_20250530` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 14 | 2025-06-30 | `after_pressure_rebal_20250630` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 15 | 2025-07-28 | `after_pressure_rebal_20250728` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 16 | 2025-08-25 | `after_pressure_rebal_20250825` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 17 | 2025-09-22 | `after_pressure_rebal_20250922` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 18 | 2025-10-28 | `after_pressure_rebal_20251028` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 19 | 2025-11-25 | `after_pressure_rebal_20251125` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 20 | 2025-12-23 | `after_pressure_rebal_20251223` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 21 | 2026-01-22 | `after_pressure_rebal_20260122` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 22 | 2026-02-27 | `after_pressure_rebal_20260227` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 23 | 2026-03-27 | `after_pressure_rebal_20260327` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 24 | 2026-04-27 | `after_pressure_rebal_20260427` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 25 | 2026-05-28 | `after_pressure_rebal_20260528` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 26 | 2026-06-26 | `after_pressure_rebal_20260626` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 27 | 2026-07-24 | `after_pressure_rebal_20260724` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 28 | 2026-08-21 | `after_pressure_rebal_20260821` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 29 | 2026-09-18 | `after_pressure_rebal_20260918` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |
| 30 | 2026-10-09 | `after_pressure_rebal_20261009` | ABSENT | `PIN_GAP_needs_ok_window`（日志仅能确认 pressure 空/不可映射） |

> 探针拟输出列（Option A）：`rebal_date,n_share_rows,n_share_rows_avail_le_tts,n_weight_rows_schemeA,n_mapped,n_pressure_nonnull,n_hiliq_intersect,empty_reason`

### 2.3 PIN `dd17044a` 方案 A（对照）

- 权重：月末点 → **次月首个交易日 09:00 Asia/Shanghai** = `weight_available_at`；再平衡 `weight_available_at ≤ t_ts`（`t_ts`=当日 15:00 SH）；**禁**静默月末向后 asof
- 份额：PRIMARY `etf_share_flow_pit_major`；**仅** `available_at ≤ t_ts`（PIN §1.3 **未**要求 `trade_date==rebal`）
- 映射钉死：`510300.SH↔000300.SH` / `510500.SH↔000905.SH` / `512100.SH↔000852.SH`
- COUNT APPROX **≠** 方案 A PIT（PIN §1.5 写死）

### 2.4 COUNT JSON `a17b75fb`（APPROX）为何过闸

| 项 | COUNT APPROX | 正式 X2（`25ae4572`） |
|---|---|---|
| 权重 asof | 月末 `trade_date` **向后 asof**（无 `available_at`） | **方案 A** synthetic `weight_available_at` |
| 份额 PIT | `trade_date∈rebal`；脚本体 **未**施加 `available_at≤t_ts`（注释有、代码无） | `trade_date==rebal` **且** `available_at_clock≤t_ts(15:00)` |
| 覆盖 | masked median **1552.5**；zero_frac=**0**；gate_pass=**true** | 30/30 pressure 空 → **STOP_ZERO_MASK_ROWS** |
| 结论 | APPROX 历史对照 | **不得**把 COUNT gate_pass 当 X2 ACCEPT（C12） |

**一句话**：APPROX 放宽了权重时点与份额 PIT；正式脚本按 PIN 收紧后，压力截面在 top_q 之前已全空。

### 2.5 脚本分支（源码只读；行号指 `25ae4572`）

1. `_load_etf_flows_window`：先 `trade_date.isin(rebal_days)` 预过滤  
2. `_pressure_on_day`：`day_etf = trade_date==d` → 再 `available_at_clock≤t_ts`；空则 `return None`  
3. 权重：`_asof_weight_scheme_a`；无候选则跳过该 ETF  
4. `members`（HI_LIQ）∩ 成分；`pressure` 空 → `None`  
5. 主环 L1403–1407：`press is None/empty` → `pin_gaps…pressure_empty_or_unmappable` + continue（**不**打 `after_mask_cs`）  
6. L1498–1501：`rebal_rows` 空 → STOP 文案含 share / scheme A / HI_LIQ / top_q  

**与 PIN 张力（供 Option B）**：PIN §1.3 份额 asof 只钉 `available_at≤t_ts`；实现额外要求 `trade_date==rebal`。若同日行的 `available_at` 常晚于 15:00，则实现会 30× 空，而 COUNT（无 available_at 过滤）仍过闸。

### 2.6 输入存在性 / 列名（非真值计数）

本拍**未**无 `.ok` 加载权重/份额真值做新全窗计数。schema 核：

| 表 | exists | 行数(meta) | 关键列 |
|---|---|---:|---|
| `etf_share_flow_pit_major` | yes | 14,258 | 含 `available_at`；三件套 PIN 称 PRESENT |
| `index_weight_csi300_500_1000` | yes | 189,000 | **无** `available_at`（须方案 A） |
| `trade_cal_sse_pit` | yes | 8,035 | 方案 A 用 |
| `universe_mask_hiliq_v1` | yes | 11,748,583 | X2 `after_mask` 已证明可载 |

## 3. 空压原因分类（A–E）

| 码 | 含义 | 本拍判定 | 依据 |
|---|---|---|---|
| **A** | 份额缺口 / 同日行 `available_at≤t_ts` 后为空 | **HIGH 主嫌疑** | 正式双过滤 vs COUNT 无 available_at 过滤；PIN/实现张力；STOP 文案首项 |
| **B** | 方案 A 使 `weight_available_at≤t_ts` 空或错期 | **MEDIUM 次嫌疑** | APPROX↔方案 A 时差；但 `after_weight_pin` 已成功；难单独解释 30/30 |
| **C** | 指数映射三件套失败 | **LOW** | 映射与 COUNT/PIN 一致；权重 `index_code` 列齐 |
| **D** | HI_LIQ 交集后可映射名=0 | **LOW–MEDIUM 待核** | `after_mask` 大块已载；COUNT 同 mask median 1552；须探针 `n_hiliq_intersect` |
| **E** | top_q=0.20 之前 pressure 已全空 | **是现象；非 top_q 根因** | `after_mask_cs_*` ABSENT ⇒ **未执行** top_q |

> 缺 per-rebal 真计数处一律标 **`PIN_GAP_needs_ok_window`**（见 JSON）。

## 4. 推荐选项（供主/Arch 裁；本执行器不自决）

| Option | 内容 | 本票态度 |
|---|---|---|
| **A（推荐）** | 签**新**只读 mapping 探针窗（**新** `.ok`；**禁** RESTORED `10927bd9`）；跑 `docs/v2/audit/…_MAPPING_RECON_PROBE_DRAFT_*.py` 的后续真值版 / 或同列输出，产出 per-rebal JSON | **推荐** |
| **B** | 另开**补丁 DRAFT 票**：对照 PIN `dd17044a` vs `25ae4572` 份额 asof（是否应 `available_at≤t` asof 而非 `trade_date==rebal`）及方案 A 边界；**仍禁本拍改正式脚本** | 探针确认 A/B 后 |
| **C** | HOLD 不解阻 / 换机制 | 若主裁放弃本机制 |

**本票推荐：Option A。**

## 5. 产物

| 文件 | 角色 |
|---|---|
| 本 DRAFT | 根因分析 |
| COVER DRAFT | 一句话交主→Arch 只审 |
| RECEIPT | 落盘核验 |
| PROBE DRAFT `.py` | 只读探针骨架；`--dry-compile-only`；**不**真跑 |
| `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_20261027.json` | log-derived / count-approx / PIN 合成；**非**新签窗真跑 |

## 6. 硬禁遵守

- **未**改 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py`（仍 **`25ae4572`**）
- **未**复跑 X2 / **未**自签 `.ok` / **未**挂 QUIET / **未** Book-Smoke
- **未** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票
- **未**改叶33 `afbbe7e7`；**未**开叶36；**未** git commit；**未**改 TEAM_STATE
- **未**无 `.ok` 加载行情/权重/份额真表做新全窗计数
- **≠X2 ACCEPT**；leo_notify=false；live=false；ok_requested=false

## 7. 下一跳

交主 → Arch **只审**本 mapping recon DRAFT 包 → 主裁 Option A/B/C。本执行器停笔。
