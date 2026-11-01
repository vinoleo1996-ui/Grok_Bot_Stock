# 叶35 mapping recon · RECEIPT（DRAFT 落盘核）

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:07 ET (America/New_York)；ISO `2026-10-27T14:07:35-04:00`
- **结论**：mapping recon **DRAFT 包已落盘**；**EXECUTED_PROBE=false**；正式脚本仍 **`25ae4572`**；live `.ok`=**0**；QUIET live=**ABSENT**；**≠X2 ACCEPT**；**≠叶36**

## 产物 sha

| 文件 | sha8 | sha256 全长 | 字节 |
|---|---|---|---:|
| DRAFT | `350ed22b` | `350ed22b58f9bed4b15d28ec04ac2512760fc9ea08974870f858cc9a0133059a` | 12972 |
| COVER | `26def8fb` | `26def8fba8b1ebd12a549a82cdca228ceb1259a5845a7422bd23f27dfd48fd5f` | 1501 |
| PROBE DRAFT py | `c2f2ca94` | `c2f2ca94993ac6d74a352f07353dc5384d96d166069d46e8f1b9c146b66d65d4` | 4760 |
| recon JSON | `ad4b47a2` | `ad4b47a2791a9b508892a1b36aacb0f227f0527ade26d6e90ead03390b49c469` | 21000 |

## 路径

1. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_DRAFT_20261027_ZH.md`
2. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_COVER_DRAFT_20261027_ZH.md`
3. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_RECEIPT_20261027_ZH.md`
4. `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_DRAFT_20261027.py`
5. `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_20261027.json`

## 质量核

| 项 | 结果 |
|---|---|
| 正式脚本 sha8 | **`25ae4572`**（要求 `25ae4572`；MATCH） |
| 叶33 `afbbe7e7` | 本票未触 |
| 新 `.ok` | **无** |
| QUIET live | **ABSENT** |
| VOID/COUNT/PIN | `dfafff28` / `a17b75fb` / `dd17044a` MATCH 引用 |
| 探针 dry | 落盘后另核 `py_compile`+`pyflakes`+`--dry-compile-only` |
| 真跑探针 / `--allow-real-data` | **未执行**（EXECUTED_PROBE=false） |
| 推荐 Option | **A** |
| leo_notify / live | false / false |

## 对照上游

| 上游 | sha8 |
|---|---|
| Arch VOID | dfafff28 |
| X2 RUN_RECEIPT | 1e255fff |
| stdout | 7f7f813d |
| ok VOID 归档 | 10927bd9 |
| QUIET lift | f50975e4 |
| PIN C3 | dd17044a |
| FROZEN | be9fc459 |
| COUNT JSON | a17b75fb |

## 交主

交主 → Arch **只审** mapping recon DRAFT。本执行器 **不**复跑、**不**改脚本、**不**自签 `.ok`。≠X2 ACCEPT。


## 探针质量核（落盘后）

| 项 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf35_mapping_recon_probe_draft_20261027.pyc` | **PASS** |
| `python -m pyflakes`（uv 装入 qlvenv 4.0.3） | **PASS**（0 findings；rc=0） |
| `--dry-compile-only` | **PASS** rc=0；`formal_sha8_observed=25ae4572`；`executed_probe=false` |
| `--allow-real-data` | **未执行**（DRAFT 遇之则 STOP rc=3） |
| EXECUTED_PROBE | **false** |

## 本文件

落盘后以 `sha256sum` 为准（本段不含自指 sha，避免循环）。
