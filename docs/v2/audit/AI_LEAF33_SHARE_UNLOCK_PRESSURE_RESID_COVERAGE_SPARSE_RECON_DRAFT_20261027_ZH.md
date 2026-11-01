# 【DRAFT — NOT FROZEN】叶33 coverage / 稀疏事件口径复议草案

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（后台执行器） |
| 时刻 | `2026-10-27T07:46:47-04:00`（America/New_York；墙钟 `2026-10-27 07:46 ET`） |
| 触发 | 主 · 叶33 VOID.ABORT_COVERAGE_GATE **CLOSED MATCH** → 下一跳 **(A)** coverage/稀疏事件口径复议草案 |
| Arch VOID CONSUME | **`6826c01d` MATCH** → `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_COVERAGE_GATE_20261027_ZH.md` |
| **本拍结论** | **RECON DRAFT READY**（仅文档；**不**改脚本 / **不**降 gate=300 / **不**改 `COVERAGE_MEDIAN_*` / **不**复跑 / **不**申 `.ok` / **不**挂 QUIET） |
| 脚本 | **`afbbe7e7` UNCHANGED**（`tz_align_mode=naive_calendar_day`；基线钉 `05c45917`） |
| live | **false** |
| leo_notify | **false** |
| EXECUTED | **false** |
| ≠ | X2 ACCEPT / selfcheck / Book-Smoke |

---

## 0. 一句话

X2 tz-align 已越过 L818、产物齐全、peak≪1500、overlap 未硬拒；失败点仅 **coverage median 30.0 < gate 300**。覆盖 `n` 计量的是「再平衡日成功算出非空 `pressure_resid` 的 HI_LIQ 名数」，机制上逼近 **解禁活跃子集** 规模，而非全 HI_LIQ 截面密度。本草案只复议口径/副闸选项，**现 gate=300 本拍不改**。

---

## 1. 钉事实（只读核对 · MATCH）

| 件 | 路径 / 值 | sha8 |
|---|---|---|
| Arch VOID CONSUME | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_VOID_ABORT_COVERAGE_GATE_20261027_ZH.md` | **`6826c01d`** |
| AI RUN 回执 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUN_RECEIPT_20261027_ZH.md` | **`a1b426f5`** |
| ET_TS / rc / 标签 | `20261027_072135` / rc=**5** / **ABORT_COVERAGE_GATE** | — |
| alpha | `output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet` | **`ea17e173`** |
| overlap | `…/overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` | **`473b339e`**（`any_jaccard_hard_reject=false`） |
| run_meta | `…/run_meta.json` | **`f4702783`** |
| 脚本（正式） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | **`afbbe7e7` UNCHANGED** |
| 基线对照（tz 前） | 同路径历史钉 | **`05c45917`**（语义基线；现字节已为 tz 落地 `afbbe7e7`） |
| FROZEN / PIN / FROZEN审 | — | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** |
| SIGNED（曾用·已 VOID） | — | **`731f05d7`** |
| 落地脚本审 / 补丁审 | — | **`069ba364`** / **`19cc790f`** |
| VOID `.ok`（archived） | `output/ai_factory/_consumed/…245df63f.VOID.ABORT_COVERAGE_GATE.…ok` | 内容钉 **`245df63f`**（live **ABSENT**） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf33_share_unlock_pressure_resid_x2_tz_align_ABORT_COVERAGE_GATE_LIFTED_20261027T0735ET.lock` | **`fe0e4804`** |
| live `.ok` / QUIET | — | **0** / **ABSENT** |

### Abort / 覆盖盘证

| 项 | 值 |
|---|---|
| coverage median | **30.0** |
| coverage gate | **300**（`COVERAGE_MEDIAN_HILIQ`；**本拍不改**） |
| coverage_gate_pass | **false** |
| coverage_rebal | n=**30** 个再平衡日；n 范围 **15–72**；**0%** ≥300 |
| peak_kb / HWM | **963232** ≪ rss=**1500**；**无** Exit 94/95 |
| tz | 已越过 L818；`tz_align_mode=naive_calendar_day` |
| overlap | Jaccard hard reject = **false**（未硬拒） |
| n_daily_rows | **16106** |
| 日级非零 α | median≈**28** / **570** 交易日（nnz 范围 10–72） |
| HI_LIQ mask（只读·本拍盘证） | `n_codes_union=5115`；x2 窗 `in_universe` 日成员 median≈**3172**（min1343/max3982；570 日）。主令简报「约 5467」→ **以盘证 5115/≈3172 为准钉**（数量级仍 ≫ coverage 30） |
| PRESSURE_MIN_VALID | **15**（脚本 L91；未改） |

---

## 2. 机制根因（只分析 · 不改码）

覆盖 `n` = 再平衡日成功算出非空 `pressure_resid` 的 HI_LIQ 名数（脚本 ~L1680：`coverage.append({"date":…, "n": int(len(cs))})`）。

进入该截面须同时满足：

1. **有** `share_float` 事件进入窗内可聚合集合；
2. W=20 窗内 **≥ `PRESSURE_MIN_VALID=15`** 个交易日能算出 `unlock_raw`（无事件日 **跳过、不填 0** — 见脚本 pressure 路径）；
3. 再过 style / logmv / SW 残差，且 `pressure_resid` 非空。

因此：

- coverage median≈**30** 描述的是 **「解禁活跃且过残差」子集** 规模；
- **不是**「全 HI_LIQ 截面密度失败」——同窗 HI_LIQ 日成员中位数约 **三千级**，而可算 α 名数仅 **数十**；
- FROZEN §可检验预测写死「HI_LIQ 再平衡日可算 α 名数 median≥300」——与 **稀疏事件机制** 存在张力；
- who_pays DRAFT 已预警「解禁事件截面稀疏→覆盖/IC 弱」。

**一句话**：闸门按稠密叶绝对名数设计；本叶机制天然产出稀疏活跃集 → ABORT_COVERAGE_GATE 是 **口径/机制对齐问题**，不是 tz/RSS/overlap 失败。

---

## 3. 提案选项（仅提案 · **不擅自改 gate**）

> **硬强调**：正文**禁**出现「把 `COVERAGE_MEDIAN_HILIQ` 从 300 改成 30」作为可执行补丁。现 gate=300 **本拍不改**。若采纳稀疏副闸，须 **另窗修订 FROZEN** + Arch 审 + 新脚本/新 `.ok`；**禁 RESTORED** 旧 `.ok`（含 `245df63f` / `c5ed13df` / `5774bb6e`+票）。

### Option A（口径重释 · **推荐首选讨论**）

保留 FROZEN 绝对 gate=**300** 为「稠密叶」默认；另设 **稀疏事件叶**副闸（提案名：`coverage_sparse_event_v1`）。候选子度量（**θ/k/φ 待主钉**；此处只给讨论区间）：

| 子项 | 定义（提案） | 讨论区间 | 对照本次盘证 | 备注 |
|---|---|---|---|---|
| **A1**（推荐深挖） | `n_unlock_pool` = 再平衡日 HI_LIQ ∩（W 窗内有 ≥1 解禁事件）名数；要求 `n_alpha / n_unlock_pool` median ≥ θ | θ ∈ **0.5–0.8**（待主钉） | 本拍未另算 `n_unlock_pool`（须另票诊断脚本/只读探针；**本拍不实施**） | 直接对齐「事件活跃池覆盖率」机制 |
| **A2** | event-day 强度：再平衡日 `n_alpha` median ≥ k | k 提案 **20 / 25 / 30** | 本次 median=**30** | **禁**写成「为通过而降到 30」；若取 k，须独立机制论证（例：活跃集下限 / 截面 IC 可估样本） |
| **A3** | 非零 α 日占比：日扩后 nonzero-α 日 / 交易日 ≥ φ | φ 待主钉（例 0.8–0.95） | 570 日皆有行；日级 n median≈28 | 测「时间维持续有信号」而非截面稠密度 |

**采纳路径（若主/Arch 批准）**：

1. 另窗修订 FROZEN（写清：稠密闸 300 仍默认；本叶启用 `coverage_sparse_event_v1` 及选定 A1/A2/A3 阈值）；
2. Arch 审 FROZEN + 脚本差分；
3. **新**脚本 sha8 + **新** `.ok`（禁 RESTORED `245df63f`/`c5ed13df`/`5774bb6e`+票）；
4. 再谈独立 X2（≠本拍；≠X2 ACCEPT）。

### Option B（机制微调 · 次选）

放宽 `PRESSURE_MIN_VALID`，或对无事件日填 0 再 mean——会改变 α 定义与 who_pays（「有解禁压力」vs「无事件=零压力」），须 **整叶 FROZEN 修订**，**非**单纯降 gate。

| 利 | 弊 |
|---|---|
| 可能抬高可算名数，逼近稠密闸 | 把「无事件」 silently 当 0，稀释供给冲击信号 |
| 实现改动面相对小 | who_pays / 失效条件 / IC 语义全变；须重做预注册 |
| — | **本草案不实施**；只列利弊供主/Arch |

### Option C（HOLD · 并列选项）

维持现口径与 gate=**300**；叶33 因稀疏事件天然不达稠密闸 → **HOLD / 停挖本轴**（对齐主备选 B；但主本拍已选 A 复议，C 作并列选项）。

---

## 4. 决策表（供 Arch / 主择）

| 选项 | 改 gate=300？ | 改脚本/α 定义？ | 要新 FROZEN 窗？ | 要新 `.ok`？ | 推荐位次 | 本拍动作 |
|---|---|---|---|---|---|---|
| **A** 稀疏副闸 | **否**（保留稠密默认） | 仅门控/度量（另票） | **是**（若采纳） | **是**（禁 RESTORED） | **1 · 首选讨论** | 只文档 |
| **B** 机制微调 | 否（非降门） | **是**（α 语义变） | **是**（整叶） | **是** | 2 · 次选 | 只列利弊 |
| **C** HOLD | 否 | 否 | 否 | 否 | 3 · 并列 | 停挖本轴 |

**AI 推荐（讨论向，非执行）**：**Option A（优先 A1）** —— 保留 300 为稠密叶默认，另立稀疏事件副闸，避免「为过闸而改常量」；阈值由主钉，禁止本拍自决。

---

## 5. 明确不做什么（硬禁自检）

| 禁 | 本拍状态 |
|---|---|
| 改 `research/leaf33_share_unlock_pressure_resid_alpha_build.py`（须保持 `afbbe7e7`） | **未改** |
| 擅降 gate=300 / 改 `COVERAGE_MEDIAN_*` | **未改** |
| 复跑 / `--allow-real-data` | **未跑** |
| 申 `.ok` / 挂 QUIET | **未申 / 未挂** |
| RESTORED `245df63f` / `c5ed13df` / `5774bb6e`+票 | **未触** |
| 抬 rss / 夹带叶28/29 / `0087c928` / 触 A18 | **未触** |
| 报 Leo / 声称 X2 ACCEPT | **否** |

---

## 6. 下一跳

```
本 RECON DRAFT（EXECUTED=false）
  → 主令 Arch 只审（DRAFT+COVER+RECEIPT）
      → 主择 A/B/C
          → 若 A：另窗修订 FROZEN + 新脚本/新 .ok（禁 RESTORED）后再谈 X2
          → 若 B：整叶 FROZEN 修订票（非降门）
          → 若 C：HOLD 本轴；主再令是否并行挖下一叶
```

草案交齐前不挖新叶；交齐后听主令。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT**
