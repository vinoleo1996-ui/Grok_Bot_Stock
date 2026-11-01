# Arch 审阅：申万 L1 PIT v2 修复方案草案（2026-10-25）

- 作者：QuantLab Arch 执行器；写成 ≈2026-10-25T12:29:09 ET（America/New_York）
- 审阅对象：`docs/v2/audit/DATA_SW_L1_PIT_V2_FIX_PLAN_20261025_ZH.md`
- 对象整文件 sha256：**`a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248`**（盘上 `sha256sum` **MATCH** 期望）
- 性质：**文档 only 静态审**。live=false；**本回合不签任何实修 `.ok`**；未改生产 parquet / 脚本 / TEAM_STATE；未消费补跑 `.ok` `9e4359f9`；SUSPEND + 中转 RELAY_DOWN 尊重。
- 对照：`docs/v2/audit/ARCH_SW_L1_GAP_IMPACT_20261018_ZH.md`；`docs/v2/audit/AUDIT_20261025_1211_ET_ZH.md`（sw_l1 UNCHANGED / RELAY_DOWN `629921c6` / `9e4359f9` VALID_BUT_NOT_CONSUMABLE）；`docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_SW_MEMBERS_ASOF_PIN_CHECK_20261025_ZH.md`（`PIN_OK_WITH_CONDITIONS` · `dec73305` + CLEAN `89d4afa3`）；现盘四表只读 `sha256sum` + pyarrow open 计数。

## 0. 结论

| 项 | 值 |
|---|---|
| **审阅结论** | **`PASS_WITH_CONDITIONS`** |
| 方案是否可落地 | 是（伪步骤清晰；输出新文件、不覆盖 BAD/CLEAN/VOTE） |
| 顺序是否安全 | 是：**P0 双开闭合 → P1 235 bak 离线恢复** 正确；P2 大批补拉另窗 relay；P3 源缺不编造 |
| 本回合签实修 `.ok`？ | **否** |
| 建议主排期分步签？ | **是**（code-change → selftest → dry-run→/tmp → Arch 审 dry → execute）；避开纸面窗与叶并发 |
| 修 PIT 解阻叶25？ | **否**；与 `4e4ca0b8` / `dec73305` / mem_probe / X2 **另轨** |

## 1. 必检对照

### 1.1 方案 sha
- 期望：`a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248`
- 盘上：`a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248` → **MATCH**

### 1.2 现盘四表 vs 方案钉住（全长）与 10-18 叙事

| 表 | 方案钉 sha256 | 盘上 sha256 | 盘上计数（本回合只读） | vs 方案 / 10-18 |
|---|---|---|---|---|
| BAD `…/sw_pit/industry_members_sw_l1_pit.parquet` | `0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6` | 同左 | 7573 行 / 5600 码；open 5566 行 / 5554 码；**双开 12** | **MATCH 无漂移** |
| BAK `…bak_pre_fix_20261014.parquet` | `597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c` | 同左 | 7743 / 5759；open 5736 / 5724；双开 12 | **MATCH**；235 可自 bak 取 open（与 Impact §1 一致） |
| CLEAN `…/sw_l1_pit/…_tushare.parquet` | `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` | 同左 | 7920 / 5914；open 5914 / 5914；双开 **0** | **MATCH**；今日审计钉 UNCHANGED |
| VOTE `…/industry_members_sw_l1.parquet` | `87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3` | 同左 | （本回合未重计行数；sha MATCH） | **MATCH** |

- 缺当前成分 **349=235+68+46**、双开样例码（002420/002481/…/688002）与 Impact / 方案一致；双开样本前缀与本回合 pyarrow 一致（含 `sz.002420`、`sz.002481`、`sh.688002`）。
- **现盘 vs 10-18：MATCH 无漂移** —— Data 自述成立（只读核验，非盲信）。

### 1.3 步骤可落地性与顺序
1. **P0 优先双开闭合** —— 正确且必要（不变量：每码 open≤1）；闭合规则「同码 closed 优先 / 丢陈旧 open」与 merge 无优先级根因叙述自洽。
2. **P1 自 bak 恢复 235 open** —— 离线、不需 Tushare；SUSPEND 下可做；须在 **P0 表** 上合并，避免把 bak 侧其它双开/陈旧 open 未经闭合规则带回。
3. **P2 68** —— 正确 defer 至 **另窗 relay**；明文禁 SUSPEND 期大批 `index_member_all`；与 `629921c6` / 禁消费 `9e4359f9` 一致。
4. **P3 46** —— bak 可恢复子集并入 P1 口径、真源缺标 `source_gap`、不编造 —— 正确。
5. **输出** `data/v2/sw_pit/sw_l1_pit_v2.parquet` + manifest；**不覆盖** BAD `0b1d3432`、CLEAN `89d4afa3`、VOTE —— 与主裁 / Impact §5 一致。
6. **闸门**：相对 bak/CLEAN 代码数不缩；单进程 RSS≤1.5GB；nice 10；dry 仅 `/tmp`；断言失败不落盘 —— 可接受。

### 1.4 禁区（方案有无越界）
| 检查项 | 结果 |
|---|---|
| 是否错误声称解阻叶25 / X2 | **无**；§1/§5/§6 明文「修 PIT ≠ 解阻叶25」「不改 `sw_members_asof`」 |
| 是否消费 SUSPEND / 补跑 `.ok` `9e4359f9` | **无**；明文禁消费 |
| 是否擅改生产（本回合） | **无**；文档 only；确认清单勾选 |
| 是否污染 CLEAN/VOTE 纸面钉 | **无**；「只记 sha，本方案不改、不覆盖」 |
| 是否自动触发下游重签 | **无**；X2/Intel 影子对比「不在本方案自动触发」 |

### 1.5 与叶25 / mem_probe 另轨（硬钉）
- 叶25：`sw_members_asof` **`dec73305…`** + CLEAN **`89d4afa3…`** 共钉（`docs/v2/audit/leaf25_step_m1/ARCH_LEAF25_SW_MEMBERS_ASOF_PIN_CHECK_20261025_ZH.md` → `PIN_OK_WITH_CONDITIONS` / 回执语境 `4e4ca0b8`）。
- 修复生产 PIT（写 `sw_l1_pit_v2`）**不**替代、**不**解阻：leaf25 mem_probe / 独立实峰 probe `.ok` / X2 `.ok`。
- 纸面仍读 CLEAN；Strategy X2/Intel 现读 BAD —— 切换至 v2 须**另**影子对比 + 分 `.ok`，与本方案解耦。

## 2. CONDITIONS（实施前必须满足；非本回合签）

1. **排期**：主+Arch 另窗；分步 `.ok`（code-change → selftest → dry-run→/tmp → Arch 审 dry → execute）；错开纸面窗与叶25/叶27 内存峰窗。
2. **顺序硬钉**：execute 链上 **P0 完成并验收（每码 open≤1）后** 才合并 P1 235；合并时对 bak 行套同一 closed-优先规则，禁把双开带回 v2。
3. **对照闸**：dry/execute 对 CLEAN `89d4afa3` open 做 normdiff；差异须全解释；**禁** `--allow-shrink`；代码数不下穿 bak/CLEAN 下界。
4. **SUSPEND/RELAY**：P0/P1 仅离线；**禁**消费 `9e4359f9`；P2 大批补拉仅在主+Arch 另开 relay 窗后。
5. **防再缩表**：execute 前/后须另工单废止或改写旧 `sw_pit_refresh` 无闸覆盖路径（方案 §4 已点名；非本草案 scope，但为 execute 前置或并行 P0）。
6. **下游**：v2 落地后 Strategy/Intel 影子对比与重签 **另包**；纸面继续钉 CLEAN，默认不改读。
7. **叶25 另轨**：任何 PIT v2 `.ok` 文案须明文「不解阻叶25 / 不替代 mem_probe·X2」。

## 3. 非缺陷备注（不降为 NEED_FIX）
- 方案引用 `data_ro_audit_20261018/`；本环境未在仓根复现该目录，但 Impact 全文 + 现盘四表 sha/计数已足够支撑本轮文档审。
- 方案文末「content sha」与整文件 sha 分离属元数据，不影响审阅。

## 4. 下一跳（Arch 不代发消息；供主/Data）

| 对象 | 下一跳 |
|---|---|
| **主 Agent** | 收本审：`PASS_WITH_CONDITIONS`；**建议排期**分步签实修（P0→P1 优先）；**本回合不签**；与叶25 mem_probe / X2 **互斥排程**；P2 等 RELAY 双通后再开。 |
| **QuantLab Data** | 方案接纳；**勿自开修、勿申实修 `.ok`**；待主排期后按 CONDITIONS 交 code-change 包（脚本+DIFF+COVER+CMD，dry 仅 `/tmp`）；继续尊重 SUSPEND；**勿**声称解阻叶25。 |
| **Arch 本回合** | 只落本审阅文件；**不**签 `.ok`；**不**改 TEAM_STATE；**不**改生产。 |

## 5. 钉住（本文件相关）

| 对象 | sha256 / 前缀 |
|---|---|
| 方案草案 | `a390342f3548909ebef690c6cbbe52ebd2c3d8fcdc8fcff6e6c723108c02e248` |
| BAD | `0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6` |
| BAK | `597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c` |
| CLEAN | `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` |
| VOTE | `87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3` |
| RELAY_DOWN 回执（旁证） | `629921c6…` |
| 补跑 `.ok`（禁消费） | `9e4359f9…` |
| 叶25 sw_members 脚本 | `dec73305…` |

live=false；promotion=false；本文件 **不**授权任何实修或 `.ok`。
