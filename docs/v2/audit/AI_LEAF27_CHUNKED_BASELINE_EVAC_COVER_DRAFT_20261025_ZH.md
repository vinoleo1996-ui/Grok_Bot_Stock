# 叶27 Post-GateA 基线疏散（baseline_evac_r1）侧稿封面 · **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T22:06:00-04:00（America/New_York；墙钟 2026-10-25 22:06 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — Leo 确认开 **A**（跨块基线疏散）；本为 **代码** Post-GateA 票包；**等主交审**后再 hand Arch；现勿交、勿签、勿开跑
- **优先级**：次于主令交审；本包仅文档+工作树脚本补丁侧稿（未 git commit）

## 一句话

Gate A mktcap_cache 实峰 **ABORT_RSS 1507MB**@`chunk6_mktcap`（限 1500；回执 sha8 **`f0f94c9e`**；VOID `.ok` **`e107383f`**；VOID Arch **`ff0394d0`**）。根因升格 **`CHUNK6_PLUS10_OVER_3MB_SLACK`**（Arch R2 **`c8dc89b6`** · AI 笔记 **`0b483746`**）：chunk5 末 HWM=1497，余量仅 3MB，装载 +10 破帽；旧 Gate A = **CLOSED_INSUFFICIENT**（**禁重批** / 禁复用脚本 **`27aae6db`** 同语义）。本侧稿在 **仅改** `research/leaf27_chunked_members_mktcap_r1.py`（**不**改 lowmem_v1）前提下，提案 **baseline_evac_r1**：块末驱逐 `LimitPanelCache` 早于因子窗的 session 键（可触 `_maps`/`_keep`）+ α 中段落盘（`a_*` → part parquet → 清空 → 终局 concat）；**保留** Gate A `mktcap_cache_r1` 与 `hist_prune_r1`。**PRIMARY CLI 仍为** HILIQ×x2×ndays40。**rss_limit 仍 1500、禁抬帽**；peak_proof REQUIRED；估峰带 **1400–1490 须实峰**（非保证）。B/C 本拍不开。须 **新** Arch `.ok` + 主排新窗。≠X2。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| 主令（Leo 开 A） | **`46dc8cb3`** · `MAIN_LEAF27_LEO_OPEN_A_BASELINE_EVAC_ORDER_20261025_ZH.md` |
| 主闸 R2 | **`e8d7346c`** · `MAIN_LEAF27_POST_GATEA_SPIKE_GATE_R2` |
| Arch 缓解草案 R2 | **`c8dc89b6`** · RECOMMENDED=A |
| AI Gate A 尖峰笔记 | **`0b483746`** |
| Gate A ABORT 回执 | **`f0f94c9e`** |
| VOID 权威（Gate A 后） | **`ff0394d0`** |
| VOID `.ok`（禁 RESTORED） | **`e107383f`** |
| prev 脚本（Gate A） | **`27aae6db`** · 全长 `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` |
| 新脚本（本补丁） | **`585ba746`** · 全长 `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` |
| 主闸 | **A**（Leo 确认开 A · 基线疏散） |
| rss_limit | **1500**（**禁抬**） |

## 先验对照（不覆盖）

| 件 | sha8 | 处置 |
|---|---|---|
| Gate A mktcap_cache COVER/CMD/DIFF/HAND | 旧包 `AI_LEAF27_CHUNKED_MKTCAP_CACHE_*` | **保留**；本文件为**新**独立侧稿（勿覆写） |
| Gate A 脚本基线 | `27aae6db` | 被本补丁 **supersede**（工作树已改；未 git commit） |
| Gate A ABORT 回执 / VOID `.ok` | `f0f94c9e` / `e107383f` | **保留**；禁 RESTORED / 禁重批旧 Gate A |
| lowmem_v1 | `05bd81ea` | **UNCHANGED**；禁同 cmd 复用 |

## 提案（CODE · PRIMARY CLI 不变）

| 项 | 内容 |
|---|---|
| **改动范围** | **仅** `research/leaf27_chunked_members_mktcap_r1.py` |
| **PRIMARY 机制 A** | (1) `evict_lim_cache_sessions`：块末按因子窗（`max(BETA_WIN,IVOL_WIN)`）更新 `_keep` 并驱逐 `_maps` 内过期 session 键；(2) `flush_alpha_part`：块末把 `a_*` flush 到 `OUT_DIR/alpha_part_*.parquet` 后清空；跑完 concat 写最终 `alpha_*.parquet` |
| **保留** | `mktcap_cache_r1`（跨块 DayFloatMap + miss-only filters + 块末不 clear mktcap）；`hist_prune_r1`；因子钉 / BETA_WIN / IVOL_WIN / 残差序 / HI_LIQ-only / drop_before T-1 |
| **不改** | `RSS_LIMIT_MB=1500` / lowmem_v1 / g1g5 / CLI ndays40 / B（miss 小批）/ C（VmRSS 软门） |
| **标签** | `BASELINE_EVAC_TAG=baseline_evac_r1` + `MKTCAP_CACHE_TAG=mktcap_cache_r1` + `HIST_PRUNE_TAG=hist_prune_r1` |
| **PRIMARY CLI** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |

硬钉不变：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| sampler | `/tmp/quantlab_leaf27_chunked_baseline_evac_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac` |
| script | `research/leaf27_chunked_members_mktcap_r1.py` sha **`585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`**（sha8 **`585ba746`**） |
| 估峰带 | **1400–1490**（须实峰证明；非保证） |
| peak_proof | **REQUIRED**（日志 `lim_evict_n`/`alpha_flush_rows`/`a_buf_n`/`mktcap_cache_days`/hist 计数 + rss 阶梯 + sampler_30s） |
| 因子钉 | 与 Gate A/hist-prune/ndays40/lowmem 零改 |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit` / 擅 lift QUIET / 申 X2
- 复跑已消费票 / RESTORED **七**票：**`e107383f`** / **`2be59acd`** / **`a7d98ac9`** / **`8e51de63`** / **`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`**
- 重批旧 Gate A / 复用脚本 `27aae6db` 同语义 / 复用 VOID `.ok` `e107383f` 语义
- 同 cmd 复用 `…_lowmem_v1.py`（sha `05bd81ea`）
- `--window both` / `--universe FULLA|both`
- 覆盖 Gate A / hist-prune / ndays40 旧包文件
- **静默**切其它 chunk-mode / 其它 ndays / silent mode / 实现 B 或 C
- 改 `lowmem_v1` / g1g5 因子路径
- git commit

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF+脚本新 sha `585ba746`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（CLI 仍钉 ndays40 PRIMARY；脚本钉新 sha；禁 RESTORED 七票）。
3. 峰证明 REQUIRED；估峰 1400–1490 须实峰；`ai_no_self_rerun`；本票单次；≠X2。
4. ABORT → **停+上报**；下一跳须主/Arch 另令（禁静默 fallback / 禁抬帽）。

## 盘证（本回合）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_COVER_DRAFT_20261025_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DIFF_DRAFT_20261025.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_VERIFY_20261025_ZH.md` |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_HAND_TO_ARCH_20261025_ZH.md` |

live=false · ≠X2 · **HOLD_UNTIL_MAIN_SUBMIT** · ok_requested=false
