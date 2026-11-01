# Arch 叶27 hist-prune 分块装载 `.ok` VOID（ABORT_RSS）

- **角色**：QuantLab Arch
- **written_et**：2026-10-25T17:07:08-04:00（America/New_York；盘 VOID 动作 2026-10-25T17:05:38-04:00）
- **voided_et**：2026-10-25T17:05:38-04:00
- **live**：false · **promotion_approved**：false · **≠X2**

## 结论

**VOID.ABORT_RSS** — 原票 sha8=`2be59acd` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**非 CONSUME_PASS**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| AI 回执 sha256 | `d8be85cb96a151cb815ca94d22ca3049dfd4c95530baf5472642568792797f8f` |
| AI 回执 sha8 | `d8be85cb` — **MATCH** |
| 主令 | TEAM 17:01 ET 已令 Arch VOID+lift QUIET（加急 17:03） |
| ET_TS | `20261025_165654` |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk6_mktcap` |
| peak_log_mb | **1518** ≫ limit **1500** |
| 对照 ndays40 | 前跳峰 **1514**@chunk6（无 hist_prune）；本跳 hist_prune_r1 仍破帽 **1518**@chunk6（未压尖峰） |
| 脚本钉 | `8cb3e86f…` MATCH（hist_prune_r1；禁 `262f9bf6`） |
| CLI | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + hist_prune_r1 |
| 进程 | pid gone；AI 未抬帽 / 未静默换 mode / 未自重跑；AI **未** lift QUIET |

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok`（**已不在 live**） |
| 原内容 sha256 | `2be59acd5d201b06eea78ff99354c0acaf21f990e87f02a43e57f247617f6e77` |
| 原内容 sha8 | `2be59acd` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.2be59acd.VOID.ABORT_RSS.20261025T1705ET.ok` |
| 归档文件 sha256 | `2be59acd5d201b06eea78ff99354c0acaf21f990e87f02a43e57f247617f6e77` |
| 归档文件 sha8 | `2be59acd` |
| 禁复用 / forbid RESTORED | `2be59acd` + `a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`（均禁 RESTORED） |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；healthz quiet=true；研究 pid 空 |
| 处置 | **lift** → `output/loop/_lifted/RESEARCH_QUIET_leaf27_histprune_ABORT_RSS_LIFTED_20261025T1705ET.lock` |
| lift 文件 sha256 | `b0c85e426127acdb22aa2f282ed2f44e6c67300468fcf2ef9b8125cff51d5a9f` |
| lift 文件 sha8 | `b0c85e42` |
| 处置后 | live 锁**无**；healthz `quiet=false`；研究 pid 空 |
| 占用核 | 无其他 live 授权窗；live `.ok`=0 |

## 下一跳（架构口径）

1. **禁抬帽**（rss 仍 1500）；**禁**复用本 VOID 票 `2be59acd`；**禁** RESTORED 六票 `2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
2. hist_prune_r1 **未**把 mktcap 尖峰压下（1514→1518 同 stage）；**下一票听主另排**（Arch **不自拟**）
3. **不解阻 X2**；不新签 `.ok`；不代跑
4. AI 停等主令；禁 silent fallback / 禁自重跑

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；≠X2；live=false
