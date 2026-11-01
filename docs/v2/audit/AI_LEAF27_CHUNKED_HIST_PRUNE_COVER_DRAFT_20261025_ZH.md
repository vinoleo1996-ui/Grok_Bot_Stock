# 叶27 hist-prune 侧稿封面（chunk-boundary）· **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T16:28:37-04:00（America/New_York；墙钟 2026-10-25 16:28 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — ndays40 已 ABORT；本为 **代码修复** hist-prune 票包；**等主交审**后再 hand Arch；现勿交、勿签、勿开跑
- **优先级**：次于 Arch 对已消费 ndays40 `.ok` `a7d98ac9` 的 VOID/归档确认；本包仅文档+工作树脚本补丁侧稿

## 一句话

ndays40 单次实峰 **ABORT_RSS**（峰日志 **1514MB** @`chunk6_mktcap`，限 1500；回执 sha8 **`03064d50`**）。先验：quarter 1572@chunk4 / month 1502@chunk12 / ndays40 1514@chunk6 — **跨块 hist 字典累积**驱动 freed RSS 爬升。本侧稿在 **仅改** `research/leaf27_chunked_members_mktcap_r1.py`（**不**改 lowmem_v1 / g1g5）前提下，提案 **chunk-boundary hist prune（hist_prune_r1）**：每块末 `_prune_hist(ret_hist/eps_hist, alive_recent)` → reset `alive_recent` 为末日 codes → `gc.collect()` → `_check_rss(chunk{ci}_hist_pruned)`。**保留** 环内 `di%40` prune。**PRIMARY CLI 仍为** HILIQ×x2×ndays40（**代码修复，非 mode 变更**）。**rss_limit 仍 1500、禁抬帽**；须 **新** Arch `.ok` + 主排新窗。≠X2。

## 触发证据（ndays40 ABORT）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| 回执 sha256 | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` / sha8 **`03064d50`** |
| 主 ack | **`169c432a`**（`MAIN_LEAF27_CHUNKED_NDAYS40_ABORT_RSS_ACK_20261025_ZH.md`） |
| ET_TS | `20261025_162212` · pid=`1576337` gone |
| CLI（已消费） | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| 峰（日志准） | **1514 MB** @ stage=`chunk6_mktcap`（限 1500） |
| sampler peak_kb | **1147568**（≈1121 MB；30s 采样偏低） |
| 爬升轨迹 | chunk0 mktcap **913** → … → chunk5 freed **1479** → chunk6 capadv **1479** → ABORT **1514** |
| `.ok`（已消费/待禁 RESTORED） | sha8 **`a7d98ac9`** — **禁复跑本票 / 禁 RESTORED** |
| 旧脚本 | sha **`262f9bf6`**（ABORT 时 UNCHANGED） |
| 新脚本（本补丁） | sha **`8cb3e86f`**（全长见下） |

## 先验对照（不覆盖）

| 件 | sha8 | 处置 |
|---|---|---|
| quarter ABORT | 1572@chunk4；VOID ok `3a6caa4f` | **保留**；**禁 RESTORED** |
| month ABORT 回执 | `03c58db5`（1502@chunk12） | **保留**；ok `8e51de63` **禁 RESTORED** |
| ndays40 COVER/CMD/DIFF | `ec5f67e9` / `af6f0d49` / `5449dde5` | **保留作 baseline**；本文件为**新**独立侧稿（代码修复票） |
| ndays40 回执 | `03064d50` | **保留**；本包触发源 |
| ndays40 `.ok` | `a7d98ac9` | **已消费/VOID**；**禁 RESTORED** |
| 旧脚本 | `262f9bf6` | 被本补丁 **supersede**（工作树已改；未 git commit） |
| lowmem_v1 | `05bd81ea` | **UNCHANGED**；禁同 cmd 复用 |

## 提案（CODE · PRIMARY CLI 不变）

| 项 | 内容 |
|---|---|
| **改动范围** | **仅** `research/leaf27_chunked_members_mktcap_r1.py` |
| **PRIMARY 机制** | 每 chunk 日循环结束后、释放 members/capadv/mktcap 时：`_prune_hist(ret_hist, alive_recent)` + `_prune_hist(eps_hist, alive_recent)`；删空 deque；`alive_recent`→末日 codes；`gc.collect()`；`_check_rss(f"chunk{ci}_hist_pruned")` 并打印 rss + hist 键数 |
| **环内 prune** | **保留** `if di % 40 == 0` 既有 prune（COVER 说明：边界+环内双闸） |
| **不改** | BETA_WIN / IVOL_WIN / MIN_* / 残差序 / HI_LIQ-only / `RSS_LIMIT_MB=1500` / lowmem_v1 / g1g5 |
| **标签** | `HIST_PRUNE_TAG=hist_prune_r1`；**supersedes** ndays40-only 票（下一授权用本补丁脚本） |
| **PRIMARY CLI** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`（与 ABORT 票同 CLI；**非** mode 变更） |

硬钉不变：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| sampler | `/tmp/quantlab_leaf27_chunked_histprune_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune` |
| script | `research/leaf27_chunked_members_mktcap_r1.py` sha **`8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012`**（sha8 **`8cb3e86f`**） |
| 因子钉 | 与 ndays40/month/quarter/lowmem 零改（α/β/W/残差序/HI_LIQ-only） |

## 机制说明（hist 累积）

脚本原设计：**跨块保留** `ret_hist` / `eps_hist` / `mkt_hist`（β60 / W20 连续）。块末 `del+gc` 仅释放 members/mktcap/capadv，**hist 字典随存活标的累积** → freed RSS 仍爬（quarter/month/ndays40 三证）。`di%40` 环内 prune 不足以在块边界把死码清掉到帽下。

- **hist_prune_r1** 在块边界再剪一次，目标压低跨块爬升；**不保证**单块装载尖峰单独消失。
- 峰只能由新窗实跑证明；破帽 → **停 + 上报**（禁静默换 mode / 禁抬帽）。

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit` / 擅 lift QUIET / 申 X2
- 复跑已消费票 / RESTORED：**`a7d98ac9`** / **`8e51de63`** / **`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`**
- 同 cmd 复用 `…_lowmem_v1.py`（sha `05bd81ea`）
- `--window both` / `--universe FULLA|both`
- 覆盖 ndays40/month/quarter 包文件（COVER/CMD/DIFF/回执）
- **静默**切其它 chunk-mode / 其它 ndays / 复用 ndays40 窗
- 改 `lowmem_v1` / g1g5 因子路径
- git commit

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF+脚本新 sha `8cb3e86f`）。
2. **Arch**：确认 ndays40 `.ok` `a7d98ac9` VOID/归档；另审本 hist-prune 独立票；PASS 后主排**新窗**并签发**新** `.ok`（CLI 仍钉 ndays40 PRIMARY；脚本钉新 sha）。
3. 峰证明 REQUIRED；`ai_no_self_rerun`；本票单次；≠X2；≠解阻叶25 X2。
4. ABORT → **停+上报**；下一跳须主/Arch 另令（禁静默 fallback）。

## 盘证（本回合将填 HAND/VERIFY）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_COVER_DRAFT_20261025_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DIFF_DRAFT_20261025.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_VERIFY_20261025_ZH.md` |

live=false · ≠X2 · **HOLD_UNTIL_MAIN_SUBMIT**
