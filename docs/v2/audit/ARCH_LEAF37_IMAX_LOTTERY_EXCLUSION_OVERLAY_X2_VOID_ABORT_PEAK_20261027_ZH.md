# Arch 叶37 IMAX_LOTTERY_EXCLUSION_OVERLAY X2 `.ok` VOID（ABORT_PEAK / RSS_SPLIT）

- **角色**：QuantLab Arch
- **written_et**：2026-10-27T17:57:54-04:00（America/New_York；盘 VOID 动作 2026-10-27T17:57:10-04:00）
- **voided_et**：2026-10-27T17:57:10-04:00
- **live**：false · **promotion_approved**：false · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · **≠A18**

## 结论

**VOID.ABORT_PEAK**（≡**ABORT_PEAK_HWM** / **RSS_SPLIT**；rc=**94**）— 原票 sha8=`4096d401` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**（仅 holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2` 这把）；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**不代改脚本**、**非 CONSUMED_PASS**。回执实际 status 字样 = **ABORT_PEAK / RSS_SPLIT**（与叶30 VOID.ABORT_PEAK_HWM / 叶35 VOID.ABORT_ZERO_MASK_ROWS / 叶33 VOID.ABORT_* 命名惯例对齐）。peak_kb=**1204776** ≥ split=**1131520** @`after_r_id` → Exit **94**；**非** hard 1500 破线（peak 1204776 < hard 1536000）；**禁抬帽**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_RUN_RECEIPT_20261027_ZH.md` |
| AI 回执 sha256 | `c2a120f7b1334bc21dae45e76d64cb5ebe5f56423273b58f4dc654b25a1bde16` |
| AI 回执 sha8 | `c2a120f7` — **MATCH** |
| AI 结论 | **ABORT_PEAK / RSS_SPLIT**；rc=**94**；`STOP: RSS >= 0.85*C4 peak_kb=1204776 >= split=1131520; split further — ban raise cap`；**非** Exit 95 hard；**非** AI SIGTERM；**无** alpha/mask/overlap/run_meta |
| RUNNING_ACK | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_RUNNING_ACK_20261027_ZH.md` sha256 `dd8a7d2e3aa3549244b410aea260f32bb71c37dfa8e534d22c044aab346a168c` / sha8 **`dd8a7d2e`** MATCH |
| 主令 | 主 ~17:56 ET priority Arch CONSUME VOID + lift QUIET（ABORT_PEAK / RSS_SPLIT rc=94） |
| ET_TS | `20261027_174829` |
| run_pid | **686086** — DEAD（pgrep leaf37 空） |
| rc | **94**（RSS_SPLIT / ABORT_PEAK） |
| peak_kb / split / hard | max peak_kb **1204776** @ `after_r_id` ≥ split **1131520**；hard=**1536000**；**未破** 1500MB 硬帽；Exit **94**（非 95） |
| after_mask | PRESENT peak_kb=607492 |
| after_panel_concat | PRESENT peak_kb=791864 |
| after_r_id | **STOP** peak_kb=1204776 vmrss_kb=816136 |
| after_mask_cs_rebal_* / after_daily_concat | **未到达** |
| alpha / mask / overlap / run_meta | **无**（OUT 仅 run.log） |
| OUT | `output/ai_factory/_leaf37_imax_lottery/20261027_174829/` — **仅** run.log sha8 **`58b72991`** / 全长 `58b729917d871be514dae8ffca033d80467af4ffbed29febe8feb1f3397cee85` MATCH |
| peak_proof | **无独立文件**；以 log `RSS_CHECK` 序列为证（REQUIRED 检查点未齐；止于 after_r_id） |
| 脚本钉 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` sha8 **`108aba8f`** / 全长 `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` MATCH（只读核；**UNCHANGED**） |
| SIGNED / 审 | **`953e470c`** / **`8d8ae2f3`**（只引用） |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` / `434ff42c` / `482009dc` **UNCHANGED**；叶36 HOLD 不回撤 |
| ≠成功 | **非 CONSUMED_PASS**；RSS split abort（无 PRIMARY mask 交付） |

### peak_proof：RSS_CHECK 序列（run.log）

1. `build_start` peak_kb=107296 vmrss=107296
2. `after_mask` peak_kb=607492 vmrss=607492
3. `after_panel_concat` peak_kb=791864 vmrss=791864
4. **`after_r_id` peak_kb=1204776 vmrss=816136 → STOP Exit 94**

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok`（**已不在 live**） |
| 原内容 sha256 | `4096d401a11124f4f6999efd66e1158e8e13378f24be355ffc8565975be44a74` |
| 原内容 sha8 | `4096d401` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.4096d401.VOID.ABORT_PEAK.20261027T1757ET.ok` |
| 归档文件 sha256 | `4096d401a11124f4f6999efd66e1158e8e13378f24be355ffc8565975be44a74` |
| 归档文件 sha8 | `4096d401`（内容钉不变；mv 不改内容） |
| live `.ok` | **ABSENT**（live leaf37 `.ok`=0） |
| 禁复用 / forbid RESTORED | **`4096d401`** + **`eb70eef4`** + **`00eec671`** + **`10927bd9`** + **`25ae4572`** + 旧票 |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；内容 sha8 **`beb7dc8c`** / 全长 `beb7dc8c23d6295a554a593d3b8a131cb29de3bf1085ba546ef2df98b66c6573`；holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2`；ok_sha8=`4096d401`；expires 19:07 ET；**未擅 lift** |
| 处置 | **lift**（仅本 holder）→ `output/loop/_lifted/RESEARCH_QUIET_leaf37_imax_lottery_exclusion_overlay_x2_ABORT_PEAK_LIFTED_20261027T1757ET.lock` |
| 原 QUIET 内容 sha256 | `beb7dc8c23d6295a554a593d3b8a131cb29de3bf1085ba546ef2df98b66c6573` |
| 原 QUIET 内容 sha8 | `beb7dc8c` |
| lift 文件 sha256 | `c79ca0a622fa2e3f12d63b03b661a2873a1c1b2fddeb4ab6e2945e2ebb2cb943` |
| lift 文件 sha8 | `c79ca0a6`（内容追加 lift 块后 ≠ 原 `beb7dc8c`） |
| 处置后 | live 锁 **ABSENT** |
| 占用核 | 无其他 leaf37 live 授权窗；live leaf37 `.ok`=0；**未触** `_lifted` 其他；**未触** A18 |

## 诊断摘要（照实 · 旁注 · 不代改）

- 路径：脚本 RSS_CHECK @`after_r_id` → peak ≥ 0.85×C4 split → `SystemExit(94)`
- 现象：`build_start`→`after_mask`→`after_panel_concat`→**`after_r_id` STOP**；未达 IMAX 主算 / mask_cs_rebal / daily concat / overlap 写出
- **可能根因方向（仅旁注，不代改、不开补丁）**：`after_r_id` 残差/面板峰值过高触发 split 软门——交主裁是否令 AI 出**低内存补丁另票**（分块 / 释缓 / 流式）或 HOLD；**禁抬 rss=1500**
- peak max **1204776** < hard **1536000**；Exit **94** 非 95；**无** alpha/mask/overlap/run_meta 产物

## 禁项（钉）

- **禁抬 rss**（仍 1500）；**禁**代改 `research/leaf37_*` 重跑；**禁** AI 自改复跑；**禁擅抬** split/soft/hard
- **禁 RESTORED** `4096d401` / `eb70eef4` / `00eec671` / `10927bd9` / `25ae4572`+旧票；本拍**不新签** `.ok`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **禁触** A18；叶36/35/34/33 HOLD 不回撤（`434ff42c` / `482009dc` / `afbbe7e7`）
- **不报 Leo**；live=false；Arch **不代跑**

## 下一跳（架构口径 · 仅文档建议 · 不代令）

1. **请主裁**——**(A)** HOLD 叶37 机制，或 **(B)** 令 AI 出**低内存补丁另票**（只出草案→Arch 只审；**禁 AI 自改复跑**；**禁抬帽**）或 **(C)** 他裁
2. **本拍不新签、不代跑、不改脚本**；禁 RESTORED `4096d401`+`eb70eef4`+旧票
3. ≠X2 ACCEPT；叶36/35/34 HOLD / 叶33 `afbbe7e7` 不回撤
4. Arch **不自决 HOLD/ACCEPT**；**不自派**下一跳；**不自签**

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；不抬帽；不 RESTORED；不触 A18；不报 Leo；live=false
