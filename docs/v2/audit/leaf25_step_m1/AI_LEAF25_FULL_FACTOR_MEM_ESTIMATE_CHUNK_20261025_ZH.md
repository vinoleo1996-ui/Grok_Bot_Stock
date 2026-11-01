# 叶25 全叶因子窗 — 内存估算与强制分块方案（example / 估）

| 项 | 值 |
|---|---|
| 起草 | QuantLab AI · 2026-10-25 11:37:28 ET（America/New_York；墙钟 `2026-10-25T11:37:28-0400`） |
| 状态 | **DRAFT / 估测算 / 非实测全叶峰**；勿开跑 / 勿申 `.ok` |
| live | **false** |
| 对照 | 全叶窗草案 `994324c9…`；r6 预注册同批；step_m1 回执 `2bf4745d…` |
| 目的 | 主裁：AI 交 **MEM_ESTIMATE + 强制分块**；C4/stop/hard **对齐 step_m1**；**禁抬帽** |

> **声明**：下文峰值 / 缩放倍数标 **example / 估**。唯一实测锚点是步骤−1 recon 峰 `peak_kb=675792`（≈676MB）。**不得**把本文任何数字写成「已测全叶峰」。

---

## 1. 锚点（实测；step_m1）

| 项 | 值 | 来源 |
|---|---|---|
| ET_TS | `20261025_111646` | AI 回执 `2bf4745d…` / Arch CONSUMED `9c96bf35…` |
| peak_kb | **675792**（≈676 MB） | wrapper C4 口径 |
| C4 / STOPKB / hard | **1331200 / 1484800 / 1536000** kB | step_m1 / r5 §11；**全叶默认对齐，禁抬** |
| 工作量性质 | TTM recon 金标样本（三码 × 多 as-of；非全市场日面板） | r5 / 全叶草案 §2.1 |
| 输入行量级（估文件；Arch 曾核 schema） | income ~422k / cashflow ~316k / balance ~452k；日历 8035 | `LEAF25_STEP_M1_R5_MEM_ESTIMATE.md` |

step_m1 预估最坏 ~650MB；实测 676MB ≈ 同量级 → 全叶若一次性持有「全 A × 多日 × 多表宽面板」将 **显著超过** C4，故 **强制分块**，不涨 RSS 帽。

---

## 2. 估算方法（example / 估；外推）

### 2.1 缩放因子（示意，非标定）

设：

- `P_m1 ≈ 676 MB` = 实测 recon 峰
- 全叶 build 需在密封+X2 交易日上对 FULLA/HI_LIQ 截面算 α，并做残差 / 评价

**粗外推（example）**：

| 阶段 | 假设持有 | 估峰 RSS（example） | 相对 C4=1331200kB≈1.30GiB |
|---|---|---|---|
| A. 三表 PIT 投影列一次读入 | ~1.2M 行 × ~10–12 列 | ~0.5–0.8 GiB | 边界 / 可能破 |
| B. 日截面面板（FULLA ~5000 × ~1600 交易日密封+X2，宽表） | 若整窗 densify | **数 GiB–十余 GiB** | **必破**（对照叶27 ABORT 峰≈3557MB） |
| C. 残差 OLS + leaf19 对齐 | 每再平衡日一块 | 单日通常 <200MB；整窗累积则涨 | 取决于是否释放 |
| D. 评价簿 / CMC | 两档权重轨 | 通常 < step_m1 峰若分档 | 可并行风险 |

**结论（估）**：无分块的「整窗 densify」路径 **不可接受**；必须按日/行业/批次流式或块式，使 **单进程峰目标 ≤ ~900MB（example）≪ C4**，并为采样/峰值抖动留余量。

### 2.2 行数外推公式（披露用；非承诺）

```
RSS_est ≈ RSS_baseline(~150MB import)
        + k_row * N_rows_resident
        + k_cs  * N_names * N_days_in_chunk
        + transient_parquet_rg
```

- `k_row` / `k_cs`：**未在全叶标定**；仅用 step_m1 与历史叶经验作数量级。
- 任一块若 MEM_PROBE（另签 `.ok` 的 dry 小窗）实测峰 > 0.85×C4 → **再拆**，不申请抬 C4。

---

## 3. 强制分块策略（须写入 build/eval 设计）

### 3.1 原则

1. **禁抬帽**：C4=`1331200` / stop=`1484800` / hard=`1536000`（kB）与 step_m1 一致。
2. **不够就拆**：按日 → 按月 → 按行业 → 按批次；禁止「先跑着看再抬帽」。
3. **一块一峰**：块结束后 `del` + `gc.collect()`；禁止跨块累积宽面板。
4. **采样只 `/tmp`**：wrapper v5（P2 PASS `964cf57b…` / `4240ce82…`）。
5. **HI_LIQ 判决轨优先**：FULLA 披露可同脚本分轨，但内存预算以更宽轨的分块粒度覆盖。

### 3.2 推荐分块维（优先级）

| 优先级 | 维 | 建议粒度（example） | 说明 |
|---|---|---|---|
| P0 | **按再平衡日 / 交易日批** | 每块 20–60 个再平衡日（或 1 个自然月交易日） | α 截面天然按日；块间只落盘该块 parquet 分区 |
| P1 | **按年份切片** | 密封按年；X2 整段若仍紧再按季 | 降低单次日历索引跨度 |
| P2 | **按 SW L1 行业批**（残差前） | 每块 ≤6–8 个 L1 | 仅当 P0/P1 仍估破 C4 |
| P3 | **宇宙分轨串行** | 先 HI_LIQ 全流程，再 FULLA | 降峰值；总时长增加可接受 |
| P4 | **评价与 build 分进程** | build 出 α 后独立 eval/CMC 进程 | 避免评价簿与 PIT 同驻 |

### 3.3 落盘分区约定（拟）

```
output/ai_factory/_leaf25_full_factor/<ET_TS>/
  alpha_parts/HI_LIQ/part_YYYYMMDD_YYYYMMDD.parquet
  alpha_parts/FULLA/part_...
  alpha_HI_LIQ_merged.parquet      # 块合并（可另进程；峰单独估）
  alpha_FULLA_merged.parquet
  eval_x2/ ...
  run_meta_chunks/*.json           # 每块 peak_kb / rows / gc
```

合并步若估峰高 → **外置 merge 脚本 + 同帽**；合并失败则保持分区由 eval 流式读。

### 3.4 与叶27 ABORT 的对照（警示）

- 叶27 HI_LIQ ABORT：峰≈3557MB > limit 1500（回执链）。
- 全叶叶25 **不得**走同类「整窗加载」；本 MEM 的分块是 **硬前置**，不是优化可选项。

---

## 4. C4 / stop / hard（对齐 step_m1；禁抬帽）

| 键 | kB | 备注 |
|---|---|---|
| C4 | **1331200** | 与 step_m1 / r5 一致 |
| wrapper STOPKB | **1484800** | 默认 |
| hard | **1536000** | 默认 |
| 期望峰报告线（example） | **900000**（~879MB） | **估**目标；超过 = 拆块重设计，**不是**抬帽理由 |
| step_m1 实绩 | 675792 | 仅锚点 |

`.ok` / `.cmd` 若写成更高帽 → **Arch 应拒签**。

---

## 5. 脚本路径草案名（stub 清单；**未实现**）

> 下列为 **拟文件名**；sha **待写后钉**。本阶段禁实现开跑。

| stub | 拟路径 | 职责 |
|---|---|---|
| build | `research/leaf25_cfacc_desens_build_r1.py` | PIT→TTM→CFACC→脱敏→残差；**按块**写 `alpha_parts/`；读入 sha 自检；调用 `sw_l1_asof_with_gap_carry(..., cal=TradeCal)` |
| chunk plan | `research/leaf25_full_factor_chunk_plan_r1.py`（或 build 内模块） | 生成再平衡日列表 / 块边界 JSON（不读大表行也可先用日历） |
| merge | `research/leaf25_cfacc_desens_merge_r1.py` | 分区→合并；同帽；可跳过若 eval 支持流式 |
| eval X2 | `research/leaf25_cfacc_desens_x2_eval_r1.py` | HI_LIQ/FULLA 评价 + 门A/B 输入；**分档串行** |
| sealed eval | `research/leaf25_cfacc_desens_sealed_eval_r1.py` | 仅密封；**另 `.ok`** |
| mem probe | `research/leaf25_full_factor_mem_probe_r1.py` | 可选：单块 dry（另签小 `.ok`）；用于校准 §2，**非**全叶 |
| .cmd X2 | `docs/v2/audit/leaf25_full_factor/LEAF25_FULL_FACTOR_X2_R1.cmd` | wrapper **v5** `4240ce82…`；C4/stop/hard 如上；采样 `/tmp` |
| .cmd sealed | `docs/v2/audit/leaf25_full_factor/LEAF25_FULL_FACTOR_SEALED_R1.cmd` | 独立钉 |
| MEM（本文） | 本文件 | 估 + 分块策略 |

selfcheck / CMC：复用现盘 `leaf_selfcheck_v3` / `alpha_combo_marginal_v1_2`（sha 见 r6 §5）；FROZEN 重验。

---

## 6. 开跑前 MEM 自检清单（回执必勾）

- [ ] `.cmd` C4/stop/hard **等于** step_m1 三元组（未抬）
- [ ] wrapper = v5 `4240ce82…`；`SAMPLER_PATH` 在 `/tmp/...`
- [ ] chunk_plan 已写入 meta；单块 `N_days` / `N_industries` 有上限
- [ ] 每块回执含 `peak_kb`；任何块 ≥0.85×C4 → 停并拆（`ai_no_retry` 语义下报主/Arch，不自抬帽重试）
- [ ] 无整窗 densify 代码路径（静态审）
- [ ] 与叶27 降内存窗不重叠（主排窗）
- [ ] `live=false`；禁复用 `1c32ab1e`

---

## 7. 待主 / Arch

1. Arch：审本 MEM 分块策略是否足以签 X2 `.ok` 的内存键；是否要求先跑 **mem_probe** 小窗。
2. 主：排窗前确认叶27 降内存包已交审；本 MEM 不申请抬帽例外。
3. AI（后续另任务）：实现 stub → 新文件名 + sha 钉进 r6 冻结表；**本任务不写代码、不开跑**。

live=false；promotion_approved=false。
