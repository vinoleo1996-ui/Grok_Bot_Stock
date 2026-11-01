# Arch 叶33 SHARE_UNLOCK_PRESSURE_RESID X2 tz-align `.ok` VOID（ABORT_COVERAGE_GATE）

- **角色**：QuantLab Arch
- **written_et**：2026-10-27T07:36:58-04:00（America/New_York；盘 VOID 动作 2026-10-27T07:35:49-04:00）
- **voided_et**：2026-10-27T07:35:49-04:00
- **live**：false · **promotion_approved**：false · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · **≠A18**

## 结论

**VOID.ABORT_COVERAGE_GATE** — 原票 sha8=`245df63f` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**（仅 leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2 这把）；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**不代改脚本**、**非 CONSUMED_PASS**、**非 RSS**、**非 TypeError**。回执实际 status 字样 = **ABORT_COVERAGE_GATE**（与叶33 VOID.ABORT_TYPEERROR_TZ `8a3b25ba` / 叶30 VOID.ABORT_PEAK_HWM / 叶27 VOID.ABORT_RSS 命名惯例对齐）。coverage median **30.0** < gate **300** → rc=**5**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUN_RECEIPT_20261027_ZH.md` |
| AI 回执 sha256 | `a1b426f53c2552370bc5e7f7a268ca8d7445f961cffacf375c8ba2f528cec092` |
| AI 回执 sha8 | `a1b426f5` — **MATCH** |
| AI 结论 | **ABORT_COVERAGE_GATE**；rc=**5**；coverage_gate_pass=false（median=**30.0** < gate=**300**）；**非** Exit 94/95；**非** TypeError；**非** RSS |
| RUNNING_ACK | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_TZ_ALIGN_RUNNING_ACK_20261027_ZH.md` sha256 `170f71e1d3d9b0c3ffa6f55558e29409164f8adf6b219f27030ae2d2525093e6` / sha8 **`170f71e1`** MATCH |
| 主令 | 主 07:30 ET priority Arch CONSUME/VOID + lift QUIET（ABORT_COVERAGE_GATE） |
| ET_TS | `20261027_072135` |
| run_pid | **4194000** — DEAD（pgrep 空） |
| rc | **5**（coverage gate） |
| peak_kb / HWM | **963232** / **963232** ≪1500硬帽；**无** Exit 94/95；**非 RSS 失败** |
| alpha | `output/ai_factory/_leaf33_share_unlock/20261027_072135/alpha_HILIQ_x2_20261027_072552.parquet` sha8 **`ea17e173`** / 全长 `ea17e173d4e7b5f4945c9a8930945fecf2bde78f3b22b63fa3c2e8b4f90ad69d` MATCH |
| overlap | 同目录 `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json` sha8 **`473b339e`** / 全长 `473b339ec0c79d9c52400b2cbbf57059097cf288a6496ec733e2c0649765c76d`；`any_jaccard_hard_reject=false` MATCH |
| run_meta | 同目录 `run_meta.json` sha256 `f470278310233a6dc196d621c20782019053dadaa5fe0fd5406536e8b16058c9` / sha8 **`f4702783`**；coverage_median=**30.0**；coverage_gate=**300**；coverage_gate_pass=**false** MATCH |
| 越过 L818 | **是**（tz TypeError 已由脚本 `afbbe7e7` / `tz_align_mode=naive_calendar_day` 越过） |
| 脚本钉 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7`** / 全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` MATCH（只读核；**UNCHANGED**）；基线对照 `tz_patch_base_script_sha8=05c45917` |
| SIGNED / 落地审 / 补丁审 | `731f05d7` / `069ba364` / `19cc790f`（只引用） |
| VOID 上游 / 前次 RUN / FROZEN / PIN | `8a3b25ba` / `481bacda` / `8ed43721` / `4e17ccfc`（只引用） |
| ≠成功 | **非 CONSUMED_PASS**；coverage 未过门（虽有 alpha/overlap 写出） |

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok`（**已不在 live**） |
| 原内容 sha256 | `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc` |
| 原内容 sha8 | `245df63f` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.245df63f.VOID.ABORT_COVERAGE_GATE.20261027T0735ET.ok` |
| 归档文件 sha256 | `245df63f5c8e39052da15a4f2338132382d6e60751c2f22df316a7d71575e4cc` |
| 归档文件 sha8 | `245df63f`（内容钉不变；mv 不改内容） |
| live `.ok` | **ABSENT** |
| 禁复用 / forbid RESTORED | **`245df63f`** + **`c5ed13df`** + **`5774bb6e`** + 二十票（共 **23**） |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；内容 sha8 **`ca492c09`** / 全长 `ca492c09202addb0af5ab13ad078a99eeefb53f34305d41476068788183cdf72`；holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；ok_sha8=`245df63f`；expires 08:45 ET；**未擅 lift** |
| 处置 | **lift**（仅本 holder）→ `output/loop/_lifted/RESEARCH_QUIET_leaf33_share_unlock_pressure_resid_x2_tz_align_ABORT_COVERAGE_GATE_LIFTED_20261027T0735ET.lock` |
| 原 QUIET 内容 sha256 | `ca492c09202addb0af5ab13ad078a99eeefb53f34305d41476068788183cdf72` |
| 原 QUIET 内容 sha8 | `ca492c09` |
| lift 文件 sha256 | `fe0e4804056ac9e48d95309b56fde8a6242e34cfcdce60ecf84c7bc9ee00e794` |
| lift 文件 sha8 | `fe0e4804`（内容追加 lift 块后 ≠ 原 `ca492c09`） |
| 处置后 | live 锁 **ABSENT** |
| 占用核 | 无其他 leaf33 live 授权窗；live leaf33 `.ok`=0；**未触** `_lifted` 其他；**未触** A18 |

## 禁项（钉）

- **禁抬 rss**（仍 1500）；**禁**代改 `research/leaf33_*` 重跑；**禁** AI 自改复跑；**禁擅降 coverage gate**
- **禁 RESTORED** `245df63f` / `c5ed13df` / `5774bb6e`+二十票（共 23）；本拍**不新签** `.ok`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **禁触** A18；`0087c928`/叶28/29 另队
- **不报 Leo**；live=false；Arch **不代跑**

## 下一跳（架构口径 · 仅文档建议 · 不代令）

1. 请主决定——**(A)** coverage 门限 / 稀疏事件因子口径复议草案（AI **只出草案**→Arch **只审**；**禁 AI 自改复跑**；**禁擅降门**）或 **(B)** HOLD 叶33 机制
2. **本拍不新签、不代跑、不改脚本**；禁 RESTORED `245df63f`+`c5ed13df`
3. ≠X2 ACCEPT；叶28/29 / `0087c928` 另队

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；不抬帽；不擅降 coverage gate；不 RESTORED；不触 A18；不报 Leo；live=false
