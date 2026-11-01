# Arch 叶27 baseline_evac CONSUMED_PASS 回执

- **角色**：QuantLab Arch
- **written_et**：2026-10-25T22:48:47-04:00（America/New_York）
- **live**：false · **promotion_approved**：false · **≠X2**

## 结论


**CONSUMED_PASS** — AI 回执 `1671eec4` MATCH；DONE 非 ABORT；peak=**1401**/1500；sampler peak_kb=**1324124**≈1293MB；n_chunks=**17**；peak_proof（lim_evict/alpha_flush）非零；`.ok` `0f50daf7` 已成功消费归档（**禁 RESTORED**）；QUIET **已 lift**（healthz quiet=false）。

**闸门**：本票 PASS → 叶27 Post-GateA baseline_evac 实跑完结。**仍 ≠ 自动签 X2.ok**；X2 须另包另审另签；本回合**未签**任何 X2 `.ok`；不解阻 X2。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| AI 回执 sha8 | `1671eec4` — **MATCH** |
| ET_TS | `20261025_224033` |
| 状态 | **DONE**（非 ABORT） |
| peak_rss_mb（log/meta） | **1401.22** / 限 1500 |
| sampler peak_kb | **1324124**（≈1293MB；EXIT） |
| n_chunks | **17** 全过 |
| lim_evict_n 合计 | **2676042** |
| alpha_flush_rows | **1271399**（alpha_part_n=16；a_buf_n 块末=0） |
| mktcap_cache_days | 块末均为 **2** |
| `.ok` 内容 sha8 | `0f50daf7` — **MATCH** |
| 脚本 | `585ba746` |
| 主 GO / 窗令 / 审 | `f8ee378e` / `5930388b` / `84fb87cf` |
| alpha / meta / summary | `652b8a68` / `85c2dc78` / `80596bff` |
| 进程 | gone（pgrep 空） |

## CONSUME 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok`（**已不在 live**） |
| 原内容 sha8 | `0f50daf7` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.0f50daf7.CONSUMED_PASS.20261025T2248ET.ok` |
| 归档文件 sha8 | `7e06a5b3` |
| 命名 | **CONSUMED_PASS**（成功消费；**禁 RESTORED**；非 VOID） |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` sha8 `bdbef3ad`；healthz quiet=true |
| 处置 | **lift** → `output/loop/_lifted/RESEARCH_QUIET_leaf27_baseline_evac_PASS_LIFTED_20261025T2248ET.lock` |
| lift 文件 sha8 | `207ae67d` |
| 处置后 | live 锁**无**；healthz @2026-10-25T22:48:27-04:00：`ok=true` · `quiet=false` · `live=false`；live `.ok`=0；pgrep 空 |

## 硬钉

- forbid 七票仍禁 RESTORED：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`（另本票 `0f50daf7` 禁 RESTORED）
- 禁抬帽；禁代跑；禁新签；**不解阻 X2**；旧 Gate A 禁重批
- 对照：GateA 1507 / hist-prune 1518 / ndays40 1514 → 本票峰 **1401** 帽内完结

## 下一跳

1. 请主确认 CONSUMED_PASS + QUIET lift MATCH
2. X2：**另包另审另签**；勿把本 PASS 当 X2 ACCEPT
3. 禁 RESTORED `0f50daf7`

## 非动作

- 不新签 `.ok`（含 X2）；不代跑；不改主干；不抬帽；live=false

live=false。
