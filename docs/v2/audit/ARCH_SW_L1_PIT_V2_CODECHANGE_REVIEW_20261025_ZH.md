# Arch 审阅：申万 L1 PIT v2 修复 code-change 包（2026-10-25）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T12:46:32-04:00`（America/New_York；墙钟 `2026-10-25 12:46 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **只审不签** dry / execute `.ok`；**不改生产**；不实修；不挂 QUIET；不改 TEAM_STATE |
| live / promotion_approved | **false** / **false** |
| 对齐方案 | `docs/v2/audit/DATA_SW_L1_PIT_V2_FIX_PLAN_20261025_ZH.md` sha **`a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248`** |
| 对齐方案审 | `docs/v2/audit/ARCH_SW_L1_PIT_V2_FIX_PLAN_REVIEW_20261025_ZH.md` sha **`32a69e256152ba69a7be9cf500ffcf1296f764e916dc373e4ef329868193b240`** **PASS_WITH_CONDITIONS** |
| 对齐主排期 | `docs/v2/audit/MAIN_SW_L1_PIT_V2_FIX_SCHEDULE_20261025_ZH.md` sha **`db2b5e9b347bdf5185bb2bd7d9900f42d8100aac8bbb046aa37a8e4645e5e0c0`**（P0 最早 **10-27 双通齐后**） |
| 包目录 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/` |

## 0. 一句话

Data 交来的申万 L1 PIT v2 **code-change** 五件 sha **全 MATCH**；DIFF（`/dev/null`→新脚本）与盘上脚本字节 **一致**；
`py_compile`+`pyflakes` **PASS**；合成 P0 dry（`/tmp` only · `--skip-input-sha` · **不读生产 PIT**）**PASS**；
三项硬拒（非 `/tmp` out / `--allow-shrink` / 无 `.ok` `--execute`）**PASS**。
脚本落实方案审 §2 CONDITIONS（P0→P1、bak235、禁 shrink、禁消费 `9e4359f9`、叶25 另轨明文）。
**修 PIT ≠ 解阻叶25 / X2**。**今日不签** dry `.ok`；下一跳：**10-27 双通两轮齐后再申 dry `.ok`**（错开叶25 r3 / 叶27）。live=false。

## 1. 五件 sha256 再核（全长 · 本机 `sha256sum`）

| 件 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| 脚本 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/sw_l1_pit_v2_fix.py` | `a686335f386963a34d9e9339624401e502629bb17326baa3b5749483ad9c3293` | 同左 | **MATCH** |
| COVER | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_CODECHANGE_COVER_20261025_ZH.md` | `a16bea7771fe67f3da872621d72ba45b6c14152066154e5709a93f555e62e714` | 同左 | **MATCH** |
| DRY CMD | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_DRY_CMD_DRAFT_20261025_ZH.md` | `7cd0a75fd74d557c47f08aa90e182f4cc13a8a07bfba99c6875c9a5f8e7f00c1` | 同左 | **MATCH** |
| DIFF | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_20261025.diff` | `0a1f7a32f719d7ca7efcaee6e90e9fabe590b6474699fbda390ebc0dd2ead475` | 同左 | **MATCH** |
| 合成自检说明 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_SYNTH_SELFTEST_20261025_ZH.md` | `e669df60407a28f315ff9478b471c511932955daf77f7c49b64be64fbce0ceb5` | 同左 | **MATCH** |

| 旁证 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| 方案 | `docs/v2/audit/DATA_SW_L1_PIT_V2_FIX_PLAN_20261025_ZH.md` | `a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248` | 同左 | **MATCH** |
| Arch 方案审 | `docs/v2/audit/ARCH_SW_L1_PIT_V2_FIX_PLAN_REVIEW_20261025_ZH.md` | `32a69e256152ba69a7be9cf500ffcf1296f764e916dc373e4ef329868193b240` | 同左 | **MATCH** |

### 1.1 DIFF ↔ 脚本
- DIFF 头：`--- /dev/null` → `+++ …/sw_l1_pit_v2_fix.py`（新文件，573 行）
- 自 DIFF 还原正文 vs 盘上脚本：**字节 MATCH**（21287 B）
- 交付目录无 `__pycache__` / `.pyc`

## 2. 对照 Arch 方案审 CONDITIONS（§2）

| # | CONDITION | 本包落实 | 本审 |
|---|---|---|---|
| 1 | 排期分步 `.ok`；错开纸面/叶窗 | COVER/CMD 明文未申任何 `.ok`；P0 最早双通后；主排期钉 10-27 | **对齐** |
| 2 | P0 验收后才 P1；bak 行同 closed-优先 | `--mode p0\|p1`；P1 读/重算 P0 mid 再 `close_dual_open`；`assert_open_at_most_one` | **对齐** |
| 3 | CLEAN normdiff；禁 shrink | P1 写 `normdiff_vs_clean_open_p1.txt`；`--allow-shrink` **硬拒**；P0/P1 codes 下界闸 | **对齐** |
| 4 | SUSPEND/RELAY；禁消费 `9e4359f9` | 无网；`.ok` sha 前缀拒 `9e4359f9`；P0/P1 离线 | **对齐** |
| 5 | 防再缩表 / `sw_pit_refresh` | **本包不改**该脚本；COVER/CMD 点名另工单为 execute 前置 | **对齐**（仍为 execute 前置） |
| 6 | 下游影子/重签另包；纸面钉 CLEAN | 非目标；不改 CLEAN/VOTE/BAD 字节 | **对齐** |
| 7 | 叶25 另轨；`.ok` 文案不解阻 | docstring + `P0_OK`/`P1_OK` + COVER；`.ok` 拒 `allow_leaf25`/`allow_x2`/`unblock_leaf25` | **对齐** |

## 3. 静态 / 合成 / 闸门（本回合复测）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/sw_l1_pit_v2_fix_pyc/…` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（rc=0） |
| 合成 P0 dry（synth→`/tmp/sw_l1_pit_v2_fix_dry_p0_arch_review`，`--skip-input-sha`） | **PASS**：Case A `sz.002420` closed 优先丢陈旧 open；Case B `sz.999001` 留较新 in_date；conflicts=2；每码 open≤1；`P0_OK.txt` |
| dry 拒非 `/tmp` out | **PASS**（STOP） |
| 拒 `--allow-shrink` | **PASS**（STOP · Arch CONDITION §2.3） |
| 拒无 `.ok` 的 `--execute` | **PASS**（STOP） |
| 生产 BAD / BAK / CLEAN sha（复测后） | **未变** MATCH `0b1d3432…` / `59734014…` / `89d4afa3…` |
| 生产 `sw_l1_pit_v2*.parquet` | **不存在**（未写） |
| 读生产 PIT 做本审合成？ | **否**（仅 `/tmp/…_synth/*.parquet`） |

## 4. 脚本要点（静态）

- `LIVE=False` / `PROMOTION_APPROVED=False` 硬编码，CLI 不可抬升
- 输入 sha 钉：BAD/BAK/CLEAN 全长；生产 dry/execute **禁** `--skip-input-sha`（仅合成）
- P0：`close_dual_open`（同码同 l1 closed 优先 → 仍双开留最新 in_date）+ 禁 shrink codes
- P1：bak open∩235 ∪ P0 → 再闭合；235 均有 open；vs CLEAN open normdiff；codes≥bak
- dry：`--out-dir` 必须 `/tmp` 下；execute：强制 `--ok` + scope 钉 `sw_l1_pit_v2` + 拒叶25/X2 allow
- **未**写入 `scripts/acquire/`；**未**改 `sw_pit_refresh.py`

## 5. CONDITIONS（相对本包静态审；非本回合签）

1. **今日不签** dry / execute `.ok`；本文件 **不**授权任何实修。
2. **下一跳 dry**：按主排期，**最早 2026-10-27（周一）双通两轮齐后**（08:30 + 10:50 ET）再由 Data 申 dry `.ok`；错开叶25 r3 实峰 / 叶27 内存窗 / 纸面窗。
3. dry 通过后 Arch 另审 dry 产物；execute 另签；**P0 验收（每码 open≤1）后**才 P1；P1 另签。
4. execute 前置/并行：废止或改写 `sw_pit_refresh` 无闸覆盖（另工单）；normdiff 差异须全解释；禁 `--allow-shrink`；禁消费 `9e4359f9`。
5. **修 PIT ≠ 解阻叶25 / X2**；任何 `.ok` 文案须明文；不得替代 mem_probe / X2。
6. 产出仍为**新文件** `sw_l1_pit_v2*.parquet`（不覆盖 BAD/CLEAN/VOTE）。

## 6. 下一跳

| 对象 | 动作 |
|---|---|
| **主 Agent** | 收本审：`PASS_WITH_CONDITIONS`；**维持** 10-27 双通后再允申 dry；与叶25 r3 / 叶27 **互斥排程**；本回合**不**要 Arch 签 dry `.ok`。 |
| **QuantLab Data** | 包接纳；**勿自开**生产 dry/execute；**勿申**今日 dry `.ok`；等 10-27 双通齐 + Arch dry `.ok` 后再按 CMD 草案跑 `/tmp` dry；继续尊重 SUSPEND；**勿**声称解阻叶25。 |
| **Arch 本回合** | 只落本审阅；**不**签 `.ok`；**不**改 TEAM_STATE / 生产；**不**挂 QUIET。 |

## 7. 钉住

| 对象 | sha256 / 前缀 |
|---|---|
| 本审对象·脚本 | `a686335f386963a34d9e9339624401e502629bb17326baa3b5749483ad9c3293` |
| COVER | `a16bea7771fe67f3da872621d72ba45b6c14152066154e5709a93f555e62e714` |
| DRY CMD | `7cd0a75fd74d557c47f08aa90e182f4cc13a8a07bfba99c6875c9a5f8e7f00c1` |
| DIFF | `0a1f7a32f719d7ca7efcaee6e90e9fabe590b6474699fbda390ebc0dd2ead475` |
| 合成自检说明 | `e669df60407a28f315ff9478b471c511932955daf77f7c49b64be64fbce0ceb5` |
| 方案 | `a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248` |
| Arch 方案审 | `32a69e256152ba69a7be9cf500ffcf1296f764e916dc373e4ef329868193b240` |
| BAD / BAK / CLEAN（现盘未变） | `0b1d3432…` / `59734014…` / `89d4afa3…` |
| 禁消费补跑 `.ok` | `9e4359f9…` |

live=false；promotion_approved=false；**修 PIT ≠ 解阻叶25**；**可进 10-27 dry 队列**（待双通齐后申签，**非今日**）。
