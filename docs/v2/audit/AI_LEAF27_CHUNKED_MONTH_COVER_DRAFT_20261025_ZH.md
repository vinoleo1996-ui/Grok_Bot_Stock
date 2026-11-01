# 叶27 更深分块侧稿封面：month（主）/ ndays40（备）· **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T14:20:03-04:00（America/New_York；墙钟 2026-10-25 14:20 ET）
- **状态**：**DRAFT ONLY · READY·HOLD_UNTIL_MAIN_AFTER_R3B** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_AFTER_R3B** — Arch VOID `3a6caa4f`/`fc218dd1` **已盘证**；QUIET 已 lift；**交审排 r3b@15:00–15:45 之后听主令**；**现勿交 Arch**（勿抢 r3b）
- **优先级**：次于 **r3b@15:00**；本包仅文档侧稿，不挡 r3b 签窗/prelaunch

## 一句话

quarter 单次实峰 **ABORT_RSS**（峰日志 **1572MB** @`chunk4_mktcap`，限 1500）。本侧稿在 **脚本字节 UNCHANGED**（sha `262f9bf6…` 已支持 `month|ndays`）前提下，提案 **PRIMARY=`--chunk-mode month`**；若 month 仍 ABORT_RSS，再 **FALLBACK=`--chunk-mode ndays --chunk-ndays 40`**。**rss_limit 仍 1500、禁抬帽**；须 **新** Arch `.ok` + 主排新窗。

## 触发证据（ABORT）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| 回执 sha256 | `4e37aacc17998682a8713fe4e4648d40f4e8ac3fcbb3741182838ded849b879b` / sha8 **`4e37aacc`** |
| ET_TS | `20261025_141322` |
| CLI（已消费） | `--universe HILIQ --window x2 --chunk-mode quarter` |
| 峰（日志准） | **1572 MB** @ stage=`chunk4_mktcap`（限 1500） |
| 爬升轨迹 | chunk0 mktcap **897** → chunk1 **1288** → chunk2 **1397** → chunk3 **1439** → chunk4 capadv **1475** → ABORT **1572** |
| `.ok`（待 VOID） | sha8 **`3a6caa4f`** / 全长 `3a6caa4f20a3881d72e493661592550c982698db80c9a190d7cf919c8fedb758` — **禁复跑本票** |

## 历史包对照（不覆盖）

| 件 | sha8 / 全长 | 处置 |
|---|---|---|
| quarter COVER | `e42ce686` / `e42ce686d9d21d3cc9fd3f7fb9018f7f24b0dfa06806a43f3637bb31f2bd9f16` | **保留**；本文件为**新**侧稿 |
| quarter CMD | `cdf3a229` / `cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb` | **保留** |
| quarter DIFF | `b1a36d38` / `b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635` | **保留** |
| Arch 审 | `282d6ca1` / `282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb` | PASS_WITH_CONDITIONS（quarter）；本侧稿待 VOID 后再交另审 |
| 脚本 | `262f9bf6` / `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | **UNCHANGED**（本包不改 `research/*.py`） |
| lowmem_v1 | `05bd81ea` / `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **UNCHANGED**；禁同 cmd 复用 |

## 提案（CLI-only）

| 阶 | CLI | 何时 |
|---|---|---|
| **PRIMARY** | `--universe HILIQ --window x2 --chunk-mode month` | Arch VOID 后另审另签新窗首跑 |
| **FALLBACK** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` | **仅当** month 仍 ABORT_RSS；另签另窗；**仍禁抬帽** |

硬钉不变：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| sampler | `/tmp/quantlab_leaf27_chunked_month_*` only |
| script | `research/leaf27_chunked_members_mktcap_r1.py` sha **`262f9bf6…` UNCHANGED** |
| 因子钉 | 与 quarter/lowmem 零改（α/β/W/残差序/HI_LIQ-only） |

## 风险披露（必读 · hist 累积）

脚本设计：**跨块保留** `ret_hist` / `eps_hist` / `mkt_hist`（β60 / W20 连续）。quarter 实跑显示：块末 `del+gc` 后 **freed RSS 仍爬升**（897→1439），说明峰值不全是「单块装载尖峰」，还有 **滚动历史字典随存活标的累积**。

- **month** 可降低单块 members/mktcap/capadv 装载尖峰（块更短），**但未必单独修好 hist 增长**。
- 若 month 峰仍贴近/越过 1500，应走 **ndays 40** FALLBACK；若仍破，须另包（hist prune 策略或其它装载路径）— **本侧稿不发明代码改动**，不抬帽。
- Arch/主审时请把本风险写入条件；峰只能由新窗实跑证明。

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit`
- 复跑已消费票 / RESTORED：`8bcd79dc` / `725be3e0` / **`3a6caa4f`（Arch VOID 后仍禁 RESTORED）**
- 同 cmd 复用 `…_lowmem_v1.py`（sha `05bd81ea`）
- `--window both` / `--universe FULLA|both`
- 覆盖 quarter 包文件（COVER/CMD/DIFF/回执）
- 抢 **r3b@15:00** 窗或擅 lift QUIET
- git commit

## 请 Arch / 主（VOID 后）

1. **主/Arch**：VOID 已盘证；本 DRAFT **HOLD** 至 **r3b@15:00–15:45 签窗结束后**，听主令再交审 COVER+CMD+DIFF（脚本 UNCHANGED `262f9bf6`；勿抢 r3b）。
2. **主**：另排**新窗** + 令签**新** `.ok`（CLI 钉 month PRIMARY）；r3b@15:00 优先于本包交审/签窗。
3. 峰证明 REQUIRED；`ai_no_self_rerun`；本票单次；≠X2；≠解阻叶25 X2。

live=false。

## 本包盘证（落盘后回填于 HAND）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_COVER_DRAFT_20261025_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_CMD_DRAFT_20261025_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DIFF_DRAFT_20261025.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DRAFT_HAND_20261025_ZH.md` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` **UNCHANGED** |

live=false。
