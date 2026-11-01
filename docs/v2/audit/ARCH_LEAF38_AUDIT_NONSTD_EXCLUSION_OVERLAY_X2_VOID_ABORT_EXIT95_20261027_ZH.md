# Arch 叶38 AUDIT_NONSTD_EXCLUSION_OVERLAY X2 `.ok` VOID（ABORT_EXIT95 / RSS hard）

- **角色**：QuantLab Arch
- **written_et**：2026-10-27T21:52:05-04:00（America/New_York；盘 VOID 动作 2026-10-27T21:51:57-04:00）
- **voided_et**：2026-10-27T21:51:57-04:00
- **live**：false · **promotion_approved**：false · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · **≠A18**

## 结论

**VOID.ABORT_EXIT95**（≡**ABORT_EXIT95_RSS_HARD**；rc=**95**）— 原票 sha8=`62acf9fc` **禁再消费 / 禁 RESTORED**；QUIET **本签始终 ABSENT**（**无需 lift**；本签禁挂）；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**不代改脚本**、**非 CONSUMED_PASS**。回执实际 status 字样 = **ABORT_EXIT95 / RSS hard**（与叶37 VOID.ABORT_PEAK / 叶35 VOID.ABORT_ZERO_MASK_ROWS / 叶33 VOID.ABORT_* 命名惯例对齐）。peak_kb=**1642812**（≈**1604.3** MiB）≥ hard=**1536000** @`after_hiliq_chunk_2024` → Exit **95**；**禁抬 rss=1500**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_RUN_RECEIPT_20261027_ZH.md` |
| AI 回执 sha256 | `4649335fb6f7435d3501336cd67a862befafd4df5d41fe75c5de35e298fafd3f` |
| AI 回执 sha8 | `4649335f` — **MATCH** |
| AI 结论 | **ABORT_EXIT95**；rc=**95**；`STOP: RSS hard breached peak_kb=1642812 vmrss=174304 >= hard=1536000; Exit 95 ABORT (ban raise rss)`；**未抬帽、未重试、未改脚本**；**无** mask/overlap/Jaccard |
| ABORT meta | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_213200/20261027_213201/run_meta_ABORT_EXIT95.json` sha256 `29f87a56a19c260f1792b33a70b7a48852b79184eadb467dec3053d0c09683a1` / sha8 **`29f87a56`** MATCH |
| SIGNED（只引用） | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_OK_SIGNED_20261027_ZH.md` sha8 **`0085e670`** MATCH |
| 主令 | 主 → Arch 叶38 X2 CONSUME/VOID（Exit95；禁抬 rss；禁 RESTORED `62acf9fc`；不混 fund） |
| ET_TS | `20261027_213200` / run_subdir `20261027_213201` |
| run_pid | **1151492** — DEAD（pgrep leaf38 空） |
| rc | **95**（RSS hard / ABORT_EXIT95） |
| peak_kb / hard | max peak_kb **1642812** @ `after_hiliq_chunk_2024` ≥ hard **1536000**；peak≈**1604.3** MiB；vmrss_kb_at_abort=**174304** |
| soft / split / c4 | soft=1536000 / split=1131520 / c4=1331200 / hard=1536000 |
| mask / overlap / Jaccard | **无**（ABORT 先于 audit excl / pair_land / Jaccard / disclose） |
| leaf36 staging | n_pairs=**5745**；staging_jsonl `dc257acf` / staging_meta `05831ef1` 已备；**未**落入 pair_dir（ABORT 先于 pair_land；**非** silent PIN_GAP） |
| OUT | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_213200/` — ABORT meta + run 旁证；**无** exclusion_mask / overlap JSON / leaf36_pairs.npy |
| 脚本钉 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` sha8 **`d5cf50bb`** / 全长 `d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263` MATCH（只读核；**UNCHANGED**） |
| QUIET | live `output/loop/RESEARCH_QUIET.lock` **ABSENT**（本签禁挂；**无需 lift**） |
| ≠成功 | **非 CONSUMED_PASS**；RSS hard abort（无 PRIMARY mask 交付） |

### peak_proof：RSS_CHECK 序列（AI RECEIPT / run 旁证）

soft=1536000 / split=1131520 / c4=1331200 / hard=1536000

1. `run_build_begin` ru_maxrss=105680
2. `load_hiliq_begin` ru_maxrss=105808
3. **`after_hiliq_chunk_2024` peak_kb=1642812 vmrss_kb=174304 → STOP Exit 95**（peak_rss_mb=1604.3）

（无 after_mask_by / after_audit_excl / after_mask_expand / after_jaccard_subprocess / final_peak_proof——未抵达。）

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_HILIQ.ok`（**已不在 live**） |
| 原内容 sha256 | `62acf9fc95e1b00b3d4284db3ecae3fe5349eb503a268d041a18a55166b78e15` |
| 原内容 sha8 | `62acf9fc` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_HILIQ.62acf9fc.VOID.ABORT_EXIT95.20261027T2151ET.ok` |
| 归档文件 sha256 | `62acf9fc95e1b00b3d4284db3ecae3fe5349eb503a268d041a18a55166b78e15` |
| 归档文件 sha8 | `62acf9fc`（内容钉不变；mv 不改内容） |
| live `.ok` | **ABSENT**（live leaf38 `.ok`=0） |
| 禁复用 / forbid RESTORED | **`62acf9fc`** + **`57ab9096`** + **`b5be1164`** + **`4096d401`** + |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` **ABSENT**（本签 `ban_hang_quiet_this_sign`；AI 未挂） |
| 处置 | **无需 lift**（不 invent lift；不 invent `_lifted`） |
| 处置后 | live 锁 **ABSENT** |
| 占用核 | 无 leaf38 live 授权窗；live leaf38 `.ok`=0；**未触** `_lifted`；**未触** A18；**未混** fund C1/C2 |

## 诊断摘要（照实 · 旁注 · 不代改）

- 路径：脚本 RSS_CHECK @`after_hiliq_chunk_2024` → peak ≥ hard → `SystemExit(95)`
- 现象：`run_build_begin`→`load_hiliq_begin`→**`after_hiliq_chunk_2024` STOP**；未达 audit excl / pair_land / Jaccard / disclose
- **可能根因方向（仅旁注，不代改、不开补丁）**：`_load_hiliq_mask_by_chunks` 年循环仍整表 `pq.read_table` 再滤——首年 2024 即把 ru_maxrss 推到 ≈1604MiB >1500。真 pushdown / 真正按年读表须**新 LAND→新审→新独立 `.ok`**；**本窗不修**；**禁抬 rss=1500**
- peak max **1642812** ≥ hard **1536000**；Exit **95**；**无** mask/overlap/Jaccard 产物
- leaf36 staging 5745 pairs 已备但 ABORT 先于 pair_land（**非** silent PIN_GAP）

## 禁项（钉）

- **禁抬 rss**（仍 1500）；**禁**代改 `research/leaf38_*` 重跑；**禁** AI 自改复跑；**禁擅抬** soft/split/c4/hard
- **禁 RESTORED** `62acf9fc` / `57ab9096` / `b5be1164` / `4096d401`+；本拍**不新签** `.ok`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **禁触** A18；**不混** fund C1/C2 另窗；叶37 HOLD / 叶36 不回撤
- **不报 Leo**；live=false；Arch **不代跑**；本签**禁挂 QUIET**

## 下一跳（架构口径 · 仅文档建议 · 不代令）

1. **请主裁**——**(A)** HOLD 叶38 机制，或 **(B)** 令 AI 出**真 pushdown / 按年读表**补丁另票（新 LAND→Arch 只审→新独立 `.ok`；**禁 AI 自改复跑**；**禁抬帽**；**禁 RESTORED `62acf9fc`**）或 **(C)** 他裁
2. **本拍不新签、不代跑、不改脚本**；禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+
3. ≠X2 ACCEPT；fund C1/C2 另窗并行不混
4. Arch **不自决 HOLD/ACCEPT**；**不自派**下一跳；**不自签**

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；不抬帽；不 RESTORED；不 invent QUIET lift；不触 A18；不混 fund；不报 Leo；live=false
