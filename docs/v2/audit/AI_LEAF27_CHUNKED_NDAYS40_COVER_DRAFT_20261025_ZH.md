# 叶27 更深分块侧稿封面：ndays=40（独立票）· **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T15:56:48-04:00（America/New_York；墙钟 2026-10-25 15:56 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — month 已 ABORT；本为 **独立** ndays=40 票包；**等主交审**后再 hand Arch；现勿交、勿签、勿开跑
- **优先级**：次于 Arch VOID/CONSUME 已消费 month `.ok` `8e51de63`；本包仅文档侧稿

## 一句话

month 单次实峰 **ABORT_RSS**（峰日志 **1502MB** @`chunk12_mktcap`，限 1500）。按 Arch 审 `85c6fb82` 条件：**month ABORT → 另交 ndays=40 票，禁静默 fallback**。本侧稿在 **脚本字节 UNCHANGED**（sha `262f9bf6…` 已支持 `ndays`）前提下，提案 **PRIMARY=`--chunk-mode ndays --chunk-ndays 40`（仅此一阶；无 silent 任何）**。**rss_limit 仍 1500、禁抬帽**；须 **新** Arch `.ok` + 主排新窗。若 ndays=40 仍 ABORT，须另交 **hist-prune** 包（本侧稿不发明代码、不抬帽）。

## 触发证据（month ABORT）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| 回执 sha256 | `03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177` / sha8 **`03c58db5`** |
| ET_TS | `20261025_154958` |
| CLI（已消费） | `--universe HILIQ --window x2 --chunk-mode month` |
| 峰（日志准） | **1502 MB** @ stage=`chunk12_mktcap`（限 1500） |
| sampler peak_kb | **1264396**（≈1235 MB；30s 采样偏低） |
| 爬升轨迹 | chunk0 mktcap **849** → … → chunk9 **1419** → chunk10 **1460** → chunk11 **1467** → chunk12 capadv **1467** → ABORT **1502** |
| `.ok`（已消费/待 VOID） | sha8 **`8e51de63`** — **禁复跑本票 / 禁 RESTORED** |
| Arch 审（month） | `85c6fb82` PASS_WITH_CONDITIONS：month ABORT → **另交** ndays=40 票 |

## 先验对照（不覆盖）

| 件 | sha8 | 处置 |
|---|---|---|
| quarter ABORT 回执 | `4e37aacc`（1572@chunk4） | **保留**；VOID ok `3a6caa4f` **禁复用** |
| month COVER / CMD / DIFF | `c8b33519` / `5323d614` / `5fa2a29e` | **保留作 baseline**；本文件为**新**独立侧稿 |
| month 回执 | `03c58db5` | **保留**；本包触发源 |
| month `.ok` | `8e51de63` | **已消费**；听 Arch VOID/CONSUME；**禁 RESTORED** |
| 脚本 | `262f9bf6` | **UNCHANGED**（本包不改 `research/*.py`） |
| lowmem_v1 | `05bd81ea` | **UNCHANGED**；禁同 cmd 复用 |

## 提案（CLI-only · PRIMARY ONLY）

| 阶 | CLI | 何时 |
|---|---|---|
| **PRIMARY（唯一）** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` | Arch VOID month ok 后另审另签新窗首跑 |
| **禁 silent fallback** | （无） | **不得**在本票内静默切其它 chunk-mode / ndays；破帽即停 |
| **若再 ABORT** | 另交 **hist-prune** 包（代码策略另票） | **仍禁抬帽**；本侧稿不发明改码 |

硬钉不变：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| sampler | `/tmp/quantlab_leaf27_chunked_ndays40_*` only |
| out_dir 建议 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40` |
| script | `research/leaf27_chunked_members_mktcap_r1.py` sha **`262f9bf6…` UNCHANGED** |
| 因子钉 | 与 month/quarter/lowmem 零改（α/β/W/残差序/HI_LIQ-only） |

## 风险披露（必读 · hist 累积）

脚本设计：**跨块保留** `ret_hist` / `eps_hist` / `mkt_hist`（β60 / W20 连续）。month 实跑再证：块末 `del+gc` 后 **freed RSS 仍爬升**（849→1467→破 1502），驱动是 **滚动历史字典随存活标的累积**，非仅单块装载尖峰。

- **ndays=40** 为 Arch 批准的下一刀：进一步缩短单块装载窗，**可能**压低尖峰，**但未必单独修好 hist 增长**。
- 若 ndays=40 峰仍贴近/越过 1500，须另包 **hist-prune**（或其它装载路径）— **本侧稿不发明代码改动**，**不抬帽**。
- Arch/主审时请把本残余风险写入条件；峰只能由新窗实跑证明。

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit` / 擅 lift QUIET
- 复跑已消费票 / RESTORED：**`3a6caa4f`** / **`8bcd79dc`** / **`725be3e0`** / **`8e51de63`（month 已消费）**
- 同 cmd 复用 `…_lowmem_v1.py`（sha `05bd81ea`）
- `--window both` / `--universe FULLA|both`
- 覆盖 month/quarter 包文件（COVER/CMD/DIFF/回执）
- **静默**切其它 chunk-mode / 其它 ndays / 复用 month 窗
- git commit

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF；脚本 UNCHANGED `262f9bf6`）。
2. **Arch**：VOID/CONSUME 已消费 month `.ok` `8e51de63`；另审本 ndays40 独立票；PASS 后主排**新窗**并签发**新** `.ok`（CLI 钉 ndays40 PRIMARY only）。
3. 峰证明 REQUIRED；`ai_no_self_rerun`；本票单次；≠X2；≠解阻叶25 X2。
4. 若 ndays40 再 ABORT：另交 hist-prune 包，**禁抬帽 / 禁静默 fallback**。

live=false。

## 本包盘证（落盘后回填于 HAND / VERIFY）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_COVER_DRAFT_20261025_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DIFF_DRAFT_20261025.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_HAND_20261025_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_VERIFY_20261025_ZH.md` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` **UNCHANGED** |

live=false。
