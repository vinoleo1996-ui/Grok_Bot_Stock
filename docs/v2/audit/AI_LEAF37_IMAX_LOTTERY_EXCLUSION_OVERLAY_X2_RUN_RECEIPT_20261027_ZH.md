# AI 回执：叶37 IMAX Lottery Exclusion Overlay X2 · ABORT_PEAK / RSS_SPLIT（≡ABORT_PEAK_HWM；Exit 94）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 执行器 |
| 时刻 | **2026-10-27 17:51:47 EDT**（America/New_York） |
| **结论** | **ABORT_PEAK / RSS_SPLIT**（≡ABORT_PEAK_HWM；脚本 `SystemExit(94)`；非 Exit 95 hard；非 AI 主动 SIGTERM；**禁抬帽、禁自重试**） |
| ET_TS | `20261027_174829` |
| run_pid | `686086`（已退出） |
| **rc** | **94**（log 末行：`STOP: RSS >= 0.85*C4 peak_kb=1204776 >= split=1131520; split further — ban raise cap`） |
| script | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` sha8 **`108aba8f`** expect=`108aba8f` **UNCHANGED** |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok` sha8 **`4096d401`** expect=`4096d401` **仍在位**（未自 CONSUME/VOID；∉ forbid30） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`beb7dc8c`** expect=`beb7dc8c` holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2` **未 lift** |
| SIGNED | sha8 **`953e470c`** expect=`953e470c` |
| Arch 审 | `8d8ae2f3` PASS_WC |
| FROZEN / PIN | `c5927f1b` / `e01be34c` |
| leaf33/34/35 | `afbbe7e7` / `482009dc` / `434ff42c` UNCHANGED；叶36 HOLD 不复开 |
| RUNNING_ACK | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_RUNNING_ACK_20261027_ZH.md` sha8=`dd8a7d2e` |
| out | `output/ai_factory/_leaf37_imax_lottery/20261027_174829/` |
| log | `output/ai_factory/_leaf37_imax_lottery/20261027_174829/run.log` sha8=`58b72991` |
| CLI | 主令 exact：`--universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path … --out …`；**无** `--no-overlap-report`；**无** FULLA；rss=1500 **禁抬且未抬** |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke / selfcheck |

## 1. peak_proof 摘要

| 源 | 值 |
|---|---|
| 最后 `RSS_CHECK` | **`after_r_id`** peak_kb=**1204776** vmrss_kb=**816136** soft=1536000 split=1131520 c4=1331200 hard=1536000 |
| 触发 | peak_kb ≥ split（0.85×C4=1131520）→ Exit **94**；文案「split further — ban raise cap」 |
| 全局 max peak_kb | **1204776** |
| hard 破 1500MB | **否**（soft/hard=1536000；peak 1204776 < 1536000） |
| `after_mask` | PRESENT peak_kb=607492 |
| `after_panel_imax` / panel 阶段 | `after_panel_concat` PRESENT peak_kb=791864；止于 `after_r_id`（IMAX 前） |
| `after_mask_cs_rebal_*` | **未到达** |
| `after_daily_concat` | **未到达** |
| 独立 `peak_proof*` 文件 | **无**（abort 早于写出）；peak_proof 以 log `RSS_CHECK` 序列为证（REQUIRED 检查点未齐） |

### RSS_CHECK 序列

1. `build_start` peak_kb=107296 vmrss=107296
2. `after_mask` peak_kb=607492 vmrss=607492
3. `after_panel_concat` peak_kb=791864 vmrss=791864
4. **`after_r_id` peak_kb=1204776 vmrss=816136 → STOP Exit 94**

## 2. overlap / Jaccard / ρ

- **未产出**：out 无 `overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json`
- Jaccard hard reject vs leaf18/18v/27：**N/A**（未跑到判定）
- ρ：**N/A**
- 声明：本次 **未** 使用 `--no-overlap-report`；失败原因为 RSS split abort（rc=94），非跳过 overlap、非 Jaccard 硬拒

## 3. 产物

- out 文件列表：['run.log']
- mask / overlap / run_meta / alpha parquet：**无**
- artifact sha8：无
- log 全文（5 行有效 + STOP）：已落 `output/ai_factory/_leaf37_imax_lottery/20261027_174829/run.log`

## 4. 钉与禁止项声明

| 项 | 状态 |
|---|---|
| `.ok` `4096d401` | **仍在**（交 Arch CONSUME/VOID；AI 未自消费） |
| QUIET `beb7dc8c` | **仍在；未擅 lift** |
| 脚本 `108aba8f` | **UNCHANGED** |
| 抬帽 / 盲重跑 / 新 `.ok` | **禁且未做** |
| RESTORED forbid | 未复用 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票 |
| ≠X2 ACCEPT / Book-Smoke | 声明成立 |
| live / leo_notify | false / false |

## 5. 下一跳

交主 / Arch：**ABORT_PEAK_HWM rc=94**；peak 于 `after_r_id`（1204776≥split=1131520）；无 mask/overlap/run_meta；peak_proof REQUIRED 检查点未齐；**.ok `4096d401` 仍在位**；**QUIET `beb7dc8c` 未 lift**。**禁**自重试；**禁**抬 `--rss-limit-mb`；**勿报 Leo**；≠X2 ACCEPT。
