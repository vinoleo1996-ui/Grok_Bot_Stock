# 叶33 A1 只读 `n_unlock_pool` 诊断探针 · **COVER（一页）**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T08:05:28-04:00（America/New_York；墙钟 2026-10-27 08:05 ET）
- **状态**：**A1 DIAG DRAFT READY** · **ok_requested=false** · **不是 `.ok`** · live=false · **EXECUTED=false**
- **触发**：Arch复议审 **`29166bf7` PASS_WITH_CONDITIONS MATCH**；主路径 **A1**

## 一句话

A1 只读诊断票 **READY**：诊断脚本 **`083d09fe`** dry PASS；正式脚本 **`afbbe7e7` UNCHANGED**；本拍 **不实跑 / 不降门 / 不自决 θ**。交主→Arch **只审**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **结论** | **A1 DIAG READY** |
| 正式脚本 | **`afbbe7e7` UNCHANGED** |
| 诊断脚本 | **`083d09fe`** → `research/leaf33_n_unlock_pool_diag_probe_v1.py` |
| Arch复议审 | **`29166bf7`** |
| 复议 DRAFT | **`b84496fe`** |
| Arch VOID / RUN | **`6826c01d`** / **`a1b426f5`** |
| alpha / overlap / run_meta | **`ea17e173`** / **`473b339e`** / **`f4702783`** |
| FROZEN / PIN / FROZEN审 | **`8ed43721`** / **`4e17ccfc`** / **`bf5234a9`** |
| gate | **300 未改** |
| θ | **未自决**（∈0.5–0.8 等主钉） |
| live `.ok` / QUIET | **0** / **ABSENT** |
| dry-compile / dry-run | **PASS** / **PASS** |
| EXECUTED | **false** |

## 度量（极简）

- `n_unlock_pool` = HI_LIQ ∩（W=20 窗内 ≥1 PIT 解禁事件）名数 → **待签窗后跑**
- `n_alpha` 只读旁证（run_meta/`f4702783`）：median **30.0**（15–72；30 再平衡日）
- `ratio = n_alpha / n_unlock_pool`（分母 0→NaN）→ **待签窗后跑**

## 禁止清单

- 降 `COVERAGE_MEDIAN_HILIQ` / 改正式脚本 `afbbe7e7` / 复跑 X2
- 申 `.ok` / 挂 QUIET / 抬 rss / 自决 θ
- RESTORED **`245df63f`** / **`c5ed13df`** / **`5774bb6e`+票**
- 夹带叶28/29 / `0087c928` / 触 A18 / 报 Leo / 声称 X2 ACCEPT

## 请 Arch / 主

1. **主**：收 COVER+DRAFT+RECEIPT+diag_script → hand Arch **只审**。
2. **Arch**：只审不签；确认探针定义/门控；**不** endorse 降 gate。
3. 若审过：主另排**新** `.ok` 签窗跑诊断（禁 RESTORED）→ 得分布后再钉 θ / 另窗 FROZEN。
4. ≠X2 ACCEPT；leo_notify=false；live=false。

## 盘证路径

| 件 | 路径 | sha8 |
|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_DRAFT_20261027_ZH.md` | （见 RECEIPT / `/tmp/leaf33_a1_diag_sha8s.json`） |
| COVER | 本文件 | （见 json） |
| RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_N_UNLOCK_POOL_DIAG_RECEIPT_20261027_ZH.md` | （见 json） |
| 诊断脚本 | `research/leaf33_n_unlock_pool_diag_probe_v1.py` | **`083d09fe`** |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false · θ未自决
