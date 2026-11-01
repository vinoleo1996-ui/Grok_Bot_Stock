# 叶27 Gate A mktcap 跨块缓存侧稿封面 · **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T20:08:10-04:00（America/New_York；墙钟 2026-10-25 20:08 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — hist-prune ABORT 后主闸 **A**；本为 **代码修复** Gate A（mktcap 免全表重扫）票包；**等主交审**后再 hand Arch；现勿交、勿签、勿开跑
- **优先级**：次于主令交审；本包仅文档+工作树脚本补丁侧稿（未 git commit）

## 一句话

hist-prune 实峰 **ABORT_RSS 1518MB**@`chunk6_mktcap`（限 1500；回执 sha8 **`d8be85cb`**；VOID **`fd159322`**）。根因钉 **`MKTCAP_FULLSCAN_TRANSIENT_SPIKE`**（Arch 草案 **`a2307c8b`** · 尖峰笔记 **`dd193511`**）：每块对 mktcap parquet（12 RG / 无日期分区）全表 `read_row_group→to_pandas`。本侧稿在 **仅改** `research/leaf27_chunked_members_mktcap_r1.py`（**不**改 lowmem_v1 / g1g5）前提下，提案 **mktcap_cache_r1（Gate A）**：进程内保留 `DayFloatMap` 跨 chunk；每块只以 pyarrow `filters=[("trade_date","in", missing)]` 加载**缺失**日；块内继续 `drop_before`（T-1 不变）；**块末勿** `mktcap.clear()`（members/capadv 仍 clear+del+gc；**保留** hist_prune_r1）。**PRIMARY CLI 仍为** HILIQ×x2×ndays40。**rss_limit 仍 1500、禁抬帽**；peak_proof REQUIRED；须 **新** Arch `.ok` + 主排新窗。≠X2。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| Arch 缓解草案 | **`a2307c8b`** · `ARCH_LEAF27_MKTCAP_SPIKE_MITIGATION_DRAFT_20261025_ZH.md` |
| AI 尖峰笔记 | **`dd193511`** · `AI_LEAF27_CHUNKED_HIST_PRUNE_CHUNK56_SPIKE_NOTE_20261025_ZH.md` |
| hist-prune ABORT 回执 | **`d8be85cb`** |
| VOID 权威 | **`fd159322`** |
| prev 脚本（hist_prune_r1） | **`8cb3e86f`** · 全长 `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` |
| 新脚本（本补丁） | **`27aae6db`** · 全长 `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` |
| 主闸 | **A**（Leo 确认开 A） |
| rss_limit | **1500**（**禁抬**） |

## 先验对照（不覆盖）

| 件 | sha8 | 处置 |
|---|---|---|
| hist-prune COVER/CMD/DIFF/HAND | `85022506` / `4cc9773a` / `0c7af6ed` / `cc21f3c7` | **保留**；本文件为**新**独立侧稿 |
| hist-prune 脚本基线 | `8cb3e86f` | 被本补丁 **supersede**（工作树已改；未 git commit） |
| hist-prune ABORT 回执 | `d8be85cb` | **保留**；本包触发源 |
| VOID | `fd159322` | **保留**；禁 RESTORED 六票 |
| lowmem_v1 | `05bd81ea` | **UNCHANGED**；禁同 cmd 复用 |

## 提案（CODE · PRIMARY CLI 不变）

| 项 | 内容 |
|---|---|
| **改动范围** | **仅** `research/leaf27_chunked_members_mktcap_r1.py` |
| **PRIMARY 机制** | `load_mktcap_chunk_cached(store, dates_needed)`：hit 跳过；miss 用 `pq.read_table(..., filters=[("trade_date","in", missing_ts)])`（`trade_date=timestamp[us]`）；块末 **保留** store；块内 `drop_before` 不变 |
| **保留** | hist_prune_r1（块边界 + di%40）；因子钉 / BETA_WIN / IVOL_WIN / 残差序 / HI_LIQ-only |
| **不改** | `RSS_LIMIT_MB=1500` / lowmem_v1 / g1g5 / CLI ndays40 |
| **标签** | `MKTCAP_CACHE_TAG=mktcap_cache_r1` + `HIST_PRUNE_TAG=hist_prune_r1` |
| **PRIMARY CLI** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |

硬钉不变：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| sampler | `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache` |
| script | `research/leaf27_chunked_members_mktcap_r1.py` sha **`27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`**（sha8 **`27aae6db`**） |
| 因子钉 | 与 hist-prune/ndays40/month/quarter/lowmem 零改 |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit` / 擅 lift QUIET / 申 X2
- 复跑已消费票 / RESTORED 六票：**`2be59acd`** / **`a7d98ac9`** / **`8e51de63`** / **`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`**
- 同 cmd 复用 `…_lowmem_v1.py`（sha `05bd81ea`）
- `--window both` / `--universe FULLA|both`
- 覆盖 hist-prune/ndays40/month/quarter 包文件
- **静默**切其它 chunk-mode / 其它 ndays / silent mode
- 改 `lowmem_v1` / g1g5 因子路径
- git commit

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF+脚本新 sha `27aae6db`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（CLI 仍钉 ndays40 PRIMARY；脚本钉新 sha；禁 RESTORED 六票）。
3. 峰证明 REQUIRED；`ai_no_self_rerun`；本票单次；≠X2。
4. ABORT → **停+上报**；下一跳须主/Arch 另令（禁静默 fallback / 禁抬帽）。

## 盘证（本回合）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_COVER_DRAFT_20261025_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DIFF_DRAFT_20261025.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DRAFT_VERIFY_20261025_ZH.md` |

live=false · ≠X2 · **HOLD_UNTIL_MAIN_SUBMIT**
