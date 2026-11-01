# 叶37 IMAX/隔夜彩票剔除 overlay · B1 / LOW_MEM 补丁脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T18:09:50-04:00（America/New_York；墙钟 2026-10-27 18:09 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主裁 叶37 LOW_MEM_PATCH GO（另票）~18:02 ET；Arch VOID.ABORT_PEAK **`998171e1` MATCH**；基盘 **`108aba8f` UNCHANGED**（禁改）→ 并列 B1 低内存补丁

## 一句话

并列新脚本 `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` sha8 **`32605aca`** 已落盘（标注 **B1 / LOW_MEM**；`prev_script_sha8=108aba8f`；`b1_lowmem=true`）。**未改**基盘正式脚本 **`108aba8f`**。PRIMARY 工程：按年读 panel → 块内算 `r_id` → 只留瘦长表 → del+gc；pivot 后按 instrument 列块算 `rolling_imax`；rss=**1500 禁抬**；peak_proof 含 `after_panel_year_*` / `after_r_id_year_*` / `after_imax_instr_chunk_*`。契约不变：PRIMARY=mask-only top_q=**0.20**；C3=B IMAX_proxy；C11≠叶24；forbid∋**`4096d401`**+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票（n=**31**）。`--dry-compile-only` **PASS**；pyflakes **CLEAN**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审 B1_LOWMEM 脚本**。≠X2 ACCEPT。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **B1 LOW_MEM 脚本（NEW）** | **`32605aca`** · 全长 `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` |
| 基盘正式脚本（禁改） | **`108aba8f` UNCHANGED** · 全长 `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` |
| Arch VOID.ABORT_PEAK | **`998171e1`** |
| AI X2 RUN_RECEIPT | **`c2a120f7`** |
| X2 RUNNING ACK | **`dd8a7d2e`** |
| VOID `.ok`（禁 RESTORED） | **`4096d401`**（archived `…VOID.ABORT_PEAK.20261027T1757ET.ok`） |
| ABORT 事实 | peak_kb=**1204776** ≥ split=**1131520**（0.85×C4=1331200）@`after_r_id`；rc=94；**非** hard 1500 |
| PREREG_FROZEN / PIN / ArchFROZEN / 脚本审 | **`c5927f1b`** / **`e01be34c`** / **`a5a9336d`** / **`8d8ae2f3`** |
| who_pays / COVER / COUNT / PIN | **`4a074f0a`** / **`847245f8`** / **`154bc157`** / **`e01be34c`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED（分块检查点） |
| PRIMARY | HILIQ × x2；**mask-only** top_q=0.20；C3=B；`full_residual_e_id=false` |
| sampler | `/tmp/quantlab_leaf37_imax_lottery_b1_` |
| forbid | **`4096d401`**+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票（≥31） |
| QUIET / live `.ok` | **ABSENT** / **ABSENT** |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok` |

## 提案（工程改动）

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `…_b1_lowmem.py` + 本批 COVER/CMD/DIFF/RECEIPT；**禁改** `108aba8f` |
| **PRIMARY 热点** | `_load_panel_imax`：禁一次拼全窗 panel；按年读+滤+merge+`r_id`+瘦长保留+del/gc；IMAX 按列块 |
| **峰证明标签** | `after_mask` / `after_panel_year_*` / `after_r_id_year_*` / `after_r_id` / `after_imax_instr_chunk_*` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat` |
| **保持** | `check_rss` / Exit 94·95 / rss=1500 / 禁放宽 split / mask·overlap·CLI 契约 |
| **真跑门** | 另票 Arch 只审 → 主排新窗 → **新** `.ok`（禁 RESTORED `4096d401`）；**本拍未开** |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / 放宽 split / git commit
- 改基盘 **`108aba8f`** / 改 FROZEN/PIN / 改叶33/34/35 / 复开叶36
- RESTORED **`4096d401`**+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票
- 事后改 top_q / 翻剔除方向；静默升全 `e_id`；叶24 主 α
- 报 Leo；声称 X2 ACCEPT / Book-Smoke；KEEP 不解阻；COUNT APPROX 当 ACCEPT

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审 B1_LOWMEM 脚本**（COVER+CMD+DIFF+脚本 `32605aca`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（钉 B1 脚本 only；禁 RESTORED `4096d401`；rss=1500 禁抬）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_SCRIPT_RECEIPT_20261027_ZH.md` |
| B1 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` |
| 基盘（禁改） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
