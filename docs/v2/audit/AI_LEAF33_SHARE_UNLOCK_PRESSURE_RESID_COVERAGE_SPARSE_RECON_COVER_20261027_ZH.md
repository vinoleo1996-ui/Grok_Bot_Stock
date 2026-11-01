# 叶33 coverage / 稀疏事件口径复议 · **COVER（一页）**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T07:46:47-04:00（America/New_York；墙钟 2026-10-27 07:46 ET）
- **状态**：**RECON DRAFT READY** · **ok_requested=false** · **不是 `.ok`** · live=false · **EXECUTED=false**
- **触发**：Arch VOID **`6826c01d` MATCH**；主下一跳 **(A)** 复议草案

## 一句话

coverage median **30.0** < gate **300** → ABORT；根因=稀疏解禁活跃子集（非全 HI_LIQ 密度失败）。提案默认讨论 **Option A（稀疏副闸 `coverage_sparse_event_v1`，优先 A1）**；**现 gate=300 不改**。脚本 **`afbbe7e7` UNCHANGED**。交主→Arch **只审**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **结论** | **RECON DRAFT READY** |
| 脚本 | **`afbbe7e7` UNCHANGED** |
| Arch VOID | **`6826c01d`** |
| RUN | **`a1b426f5`**（ET_TS=`20261027_072135`；rc=5） |
| alpha / overlap / run_meta | **`ea17e173`** / **`473b339e`** / **`f4702783`** |
| coverage | median **30.0**；rebal n=15–72（30 日；0%≥300）；gate **300** |
| peak | **963232**≪1500；无 Exit 94/95；已过 L818 tz |
| live `.ok` / QUIET | **0** / **ABSENT**（VOID `245df63f`；lift `fe0e4804`） |
| FROZEN / PIN / FROZEN审 | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** |
| DRAFT sha8 | **`b84496fe`** |
| 推荐选项 | **A（A1 优先）**；并列 B/C |
| 下一跳 | **主→Arch 只审** |

## 三选项（极简）

| 选项 | 要旨 | 本拍 |
|---|---|---|
| **A** | 保留 300 稠密默认；另设稀疏副闸（A1 池覆盖率 / A2 事件日强度 / A3 非零日占比） | 只提案 |
| **B** | 放宽 `PRESSURE_MIN_VALID` 或无事件填 0——改 α 语义，须整叶 FROZEN | 只列利弊 |
| **C** | HOLD：维持口径+gate，停挖本轴 | 并列 |

## 禁止清单

- 降 `COVERAGE_MEDIAN_HILIQ` 300→30（或任何「为过闸改常量」）
- 改脚本 `afbbe7e7` / 复跑 / 申 `.ok` / 挂 QUIET / 抬 rss
- RESTORED **`245df63f`** / **`c5ed13df`** / **`5774bb6e`+票**
- 夹带叶28/29 / `0087c928` / 触 A18 / 报 Leo / 声称 X2 ACCEPT

## 请 Arch / 主

1. **主**：收 COVER+DRAFT+RECEIPT → hand Arch **只审**。
2. **Arch**：只审不签；择 A/B/C（若 A，阈值待主钉）。
3. 任何落地/新 `.ok`/重跑 = **另窗**；禁 RESTORED；≠X2 ACCEPT。

## 盘证路径

| 件 | 路径 | sha8 |
|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_DRAFT_20261027_ZH.md` | **`b84496fe`** |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_COVER_20261027_ZH.md` | （本文件；见 `/tmp/leaf33_coverage_recon_sha8s.json`） |
| RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVERAGE_SPARSE_RECON_RECEIPT_20261027_ZH.md` | （见 json） |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
