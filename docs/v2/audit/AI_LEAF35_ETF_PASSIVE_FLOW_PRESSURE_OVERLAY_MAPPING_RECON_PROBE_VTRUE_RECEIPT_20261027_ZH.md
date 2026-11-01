# 叶35 mapping recon · 真值只读探针 RECEIPT（Option A · DRAFT 落盘核）

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:22 ET（America/New_York）；ISO `2026-10-27T14:22:19-04:00`
- **结论**：真值只读探针版 **DRAFT 包已落盘**；**EXECUTED_PROBE=false**；正式脚本仍 **`25ae4572`**；骨架仍 **`c2f2ca94`**；叶33 **`afbbe7e7`**；live `.ok`=**0**；QUIET=**ABSENT**；**≠X2 ACCEPT**；**≠叶36**
- **交主→Arch 只审**本真值版；真跑须后续新签探针窗

## 产物 sha

| 文件 | sha8 | sha256 全长 | 字节 |
|---|---|---|---:|
| VTRUE 探针 py | `2c2226e0` | `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` | 21637 |
| VTRUE DRAFT ZH | `b7b9c61d` | `b7b9c61d28857fedf78c45de44dae1ddcc92208807f2624601dd91749010d523` | 6028 |
| VTRUE COVER | `554bc027` | `554bc027080c7910523db3251cec6d42b9808a33ced289f221ce8003faa0f63b` | 1111 |
| VTRUE CMD | `cd0c6c56` | `cd0c6c56f97cb963aa72379f5f67320c58592fb4e280937b376dc5ac1c88d169` | 2899 |
| pending JSON | `1f17fee8` | `1f17fee87a5cf91114fd9d51ea64c387ffe8a9c5fc27ff5ef61227977258100f` | 1096 |
| VTRUE RECEIPT | （自指；落盘后 `sha256sum`） | （自指） | — |

> RECEIPT 自指 sha 以落盘后 `sha256sum` 为准（避免循环自指）。

## 路径

1. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py`
2. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027_ZH.md`
3. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_COVER_DRAFT_20261027_ZH.md`
4. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_CMD_DRAFT_20261027_ZH.md`
5. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_RECEIPT_20261027_ZH.md`
6. `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_vtrue_pending_20261027.json`

## 质量核

| 项 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf35_mapping_recon_probe_vtrue_draft_20261027.pyc` | **PASS** |
| `pyflakes` | **PASS** rc=0 |
| `--dry-compile-only` | **PASS** rc=0；`executed_probe=false`；formal=`25ae4572`；skel=`c2f2ca94` |
| 无 `--allow-real-data` | **STOP** rc=3 |
| `--allow-real-data` 缺 `.ok` | **STOP** rc=4 |
| `--allow-real-data` + VOID `10927bd9` | **STOP** rc=5（forbid） |
| 正式脚本 | **`25ae4572` UNCHANGED** |
| 骨架探针 | **`c2f2ca94` UNCHANGED** |
| 叶33 | **`afbbe7e7` UNCHANGED** |
| live `.ok` / QUIET | **0 / ABSENT** |
| EXECUTED_PROBE / 真跑 | **false / 未执行** |
| Arch recon 上游 | **`cb3ca975`** |
| Option | **A** |
| leo_notify / live / x2_accept | false / false / false |

## 对照上游

| 上游 | sha8 |
|---|---|
| Arch recon 审 | cb3ca975 |
| recon DRAFT / COVER / RECEIPT | 350ed22b / 26def8fb / fb0c7a4b |
| 骨架探针 / JSON | c2f2ca94 / ad4b47a2 |
| VOID / ok VOID / QUIET lift | dfafff28 / 10927bd9 / f50975e4 |
| PIN / COUNT / COUNT script | dd17044a / a17b75fb / 4e964d40 |
| 正式 / 叶33 | 25ae4572 / afbbe7e7 |

## 交主

交主 → Arch **只审**本真值探针版。推荐下一跳：Arch 只审通过 → 主签**新**只读探针 `.ok`（禁 RESTORED `10927bd9`）→ AI 真跑填 per-rebal。本执行器 **不**自签、**不**真跑、**不**改 `25ae4572`。≠X2 ACCEPT。
