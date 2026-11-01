# 申万 L1 PIT v2 修复 —— code-change 包封面（交 Arch 静态审）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Data（执行器） |
| 起草 | `2026-10-25T12:38:23-0400`（America/New_York；墙钟 2026-10-25 12:38 ET） |
| 状态 | **code-change 包已落盘** · **未申实修/dry `.ok`** · **未改生产** · **未消费 `9e4359f9`** |
| live | **false** · promotion_approved **false** |
| 对齐 | 主排期 `MAIN_SW_L1_PIT_V2_FIX_SCHEDULE_20261025_ZH.md`；方案 `a390342f…`；Arch 审 `32a69e25…` **PASS_WITH_CONDITIONS** |
| 动作本回合 | 新脚本 + COVER + CMD + CMD + 合成 dry；`py_compile`→`/tmp` + pyflakes；**禁** execute · **禁**改 BAD/CLEAN/VOTE · **禁**改 `sw_pit_refresh.py` |

## 0. 目的

交付 P0（双开闭合）/ P1（bak 235 离线恢复）可审脚本与文档，供 Arch **静态审**。  
**修 PIT ≠ 解阻叶25 / X2**；不替代 mem_probe / X2 `.ok`；不改 `sw_members_asof`。  
P0 签执行最早 **周一双通两轮齐后**；P1 接 P0；P2 等 RELAY。本包 **不**授权 dry/execute。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | 期望 | 盘证 |
|---|---|---|---|
| 主排期 | `docs/v2/audit/MAIN_SW_L1_PIT_V2_FIX_SCHEDULE_20261025_ZH.md` | （令文） | `db2b5e9b347bdf5185bb2bd7d9900f42d8100aac8bbb046aa37a8e4645e5e0c0` |
| 方案 | `docs/v2/audit/DATA_SW_L1_PIT_V2_FIX_PLAN_20261025_ZH.md` | `a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248` | **MATCH** |
| Arch 审 | `docs/v2/audit/ARCH_SW_L1_PIT_V2_FIX_PLAN_REVIEW_20261025_ZH.md` | `32a69e256152ba69a7be9cf500ffcf1296f764e916dc373e4ef329868193b240` | **MATCH** |
| BAD | `data/v2/sw_pit/industry_members_sw_l1_pit.parquet` | `0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6` | **MATCH** |
| BAK | `data/v2/sw_pit/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet` | `597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c` | **MATCH** |
| CLEAN | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` | **MATCH** |
| 235 分类 CSV | `docs/v2/audit/data_ro_audit_20261018/B_missing_codes_classified.csv` | （`in_bak & !in_cur_any` → 235） | 脚本启动计数钉 235 |

## 2. 交付物 sha256（全长；落盘后钉）

| 件 | 路径 | sha256 |
|---|---|---|
| 脚本 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/sw_l1_pit_v2_fix.py` | `a686335f386963a34d9e9339624401e502629bb17326baa3b5749483ad9c3293` |
| 本封面 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_CODECHANGE_COVER_20261025_ZH.md` | 以盘 `sha256sum` 为准 |
| dry CMD 草案 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_DRY_CMD_DRAFT_20261025_ZH.md` | `7cd0a75fd74d557c47f08aa90e182f4cc13a8a07bfba99c6875c9a5f8e7f00c1` |
| unified DIFF | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_20261025.diff` | `0a1f7a32f719d7ca7efcaee6e90e9fabe590b6474699fbda390ebc0dd2ead475` |
| 合成自检说明 | `docs/v2/audit/sw_l1_pit_v2_fix_20261025/DATA_SW_L1_PIT_V2_FIX_SYNTH_SELFTEST_20261025_ZH.md` | `e669df60407a28f315ff9478b471c511932955daf77f7c49b64be64fbce0ceb5` |

脚本路径说明：放在 audit 交付目录（新文件，**无需** archive）。**未**写入 `scripts/acquire/`；**未**改 `sw_pit_refresh.py`（废止无闸覆盖另工单，此处点名）。

## 3. 与 Arch CONDITIONS（§2）逐条对齐

| Arch §2 | 本包落实 |
|---|---|
| 1 排期分步 `.ok`；错开纸面/叶窗 | 封面/CMD 明文；**未申**任何 `.ok`；P0 最早双通后 |
| 2 顺序 P0 验收后才 P1；bak 行同 closed-优先 | `--mode p0\|p1`；P1 默认先跑/读 P0 mid 再合并；`close_dual_open` 共用 |
| 3 CLEAN normdiff；禁 shrink | P1 写 `normdiff_vs_clean_open_p1.txt`；`--allow-shrink` **硬拒**；P1 codes≥bak |
| 4 SUSPEND/RELAY；禁消费 `9e4359f9` | 脚本禁网；`.ok` sha 前缀拒 `9e4359f9`；P0/P1 离线 |
| 5 防再缩表 / `sw_pit_refresh` | **本包不改**该脚本；COVER/CMD 点名另工单为 execute 前置 |
| 6 下游影子/重签另包；纸面钉 CLEAN | 非目标；不改 CLEAN/VOTE 字节 |
| 7 叶25 另轨；`.ok` 文案不解阻 | docstring + `P0_OK`/`P1_OK` + 本封面明文「修 PIT ≠ 解阻叶25」；`.ok` 拒 `allow_leaf25`/`allow_x2` |

## 4. 禁项

- **禁**写生产：`data/v2/sw_pit/*.parquet`、CLEAN、VOTE、任何 `.ok`、TEAM_STATE
- **禁**消费 `9e4359f9…`；**禁**调 Tushare/中转
- **禁**声称解阻叶25 / X2
- **禁**改 `scripts/acquire/sw_pit_refresh.py`
- **禁** dry 写出 `/tmp` 以外；**禁**无 `.ok` 跑 `--execute`（本回合未跑 execute）
- **禁** `--allow-shrink`；**禁**在 research/audit 落 `__pycache__`（`py_compile`→`/tmp`）
- **禁** SendToAgent / 报 Leo（本执行器回合）

## 5. 静态检查

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/sw_l1_pit_v2_fix_pyc/sw_l1_pit_v2_fix.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（rc=0） |
| 交付目录 `__pycache__` / `.pyc` | **无** |
| 合成 P0 dry（`/tmp/sw_l1_pit_v2_fix_synth` → `/tmp/sw_l1_pit_v2_fix_dry_p0`） | **PASS**（双开闭合断言过） |
| dry 拒非 `/tmp` out / 拒 `--allow-shrink` / 拒无 ok 的 `--execute` | **PASS** |
| 生产 BAD/CLEAN sha（跑后复测） | **未变**（MATCH 钉住值） |
| 生产 `sw_l1_pit_v2*.parquet` | **不存在**（未写） |

## 6. 下一跳

1. **Arch**：静态审本包（脚本 sha + 本封面 + CMD + DIFF + 合成自检）；**本包 ≠ 授权 dry/execute**。
2. **主**：维持双通窗（周一 08:30 + 10:50 ET）；双通齐后再允申 dry `.ok`；错开叶25 r3 / 叶27。
3. **Data**：等 Arch 静态审通过 → 再申 `<ARCH_DRY_OK>` → dry→`/tmp` → Arch 审 dry →（双通后）分步 execute；P1 另签；**勿**自开修生产。

live=false；promotion_approved=false；修 PIT ≠ 解阻叶25。
