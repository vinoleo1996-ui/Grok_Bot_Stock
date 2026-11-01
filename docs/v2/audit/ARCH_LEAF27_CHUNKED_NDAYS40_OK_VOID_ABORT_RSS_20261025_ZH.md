# Arch 叶27 ndays40 分块装载 `.ok` VOID（ABORT_RSS）

- **角色**：QuantLab Arch
- **written_et**：2026-10-25T16:27:54-04:00（America/New_York）
- **voided_et**：2026-10-25T16:27:38-04:00
- **live**：false · **promotion_approved**：false · **≠X2**

## 结论

**VOID.ABORT_RSS** — 原票 sha8=`a7d98ac9` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**；本回合**未新签** `.ok`、**不代跑**、**不抬帽**。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` |
| AI 回执 sha256 | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` |
| AI 回执 sha8 | `03064d50` — **MATCH** |
| 主 ack | `docs/v2/audit/MAIN_LEAF27_CHUNKED_NDAYS40_ABORT_RSS_ACK_20261025_ZH.md` |
| 主 ack sha256 | `169c432af88caf47d2c62a693595563053d5a898c9cd56b6c474705ebf9ad2c4` |
| 主 ack sha8 | `169c432a` — **MATCH** |
| ET_TS | `20261025_162212` |
| result | **ABORT_RSS_OVER_LIMIT** stage=`chunk6_mktcap` |
| peak_log_mb | **1514** ≫ limit **1500** |
| 脚本钉 | `262f9bf6…` MATCH |
| CLI | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| 进程 | pid gone；AI 未抬帽 / 未静默换 mode / 未自重跑 |

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok`（**已不在 live**） |
| 原内容 sha256 | `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90` |
| 原内容 sha8 | `a7d98ac9` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.a7d98ac9.VOID.ABORT_RSS.20261025T1627ET.ok` |
| 归档文件 sha256 | `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90` |
| 归档文件 sha8 | `a7d98ac9` |
| 禁复用 | `a7d98ac9` + 旧票 `8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`（均禁 RESTORED） |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；healthz quiet=true；pgrep 空 |
| 处置 | **lift** → `output/loop/_lifted/RESEARCH_QUIET_leaf27_ndays40_ABORT_RSS_LIFTED_20261025T1627ET.lock` |
| lift 文件 sha256 | `86d5723dd21138f7649de9c586441c4f6222910bb02673bcc61c5dd7a1bec558` |
| lift 文件 sha8 | `86d5723d` |
| 处置后 | live 锁**无**；healthz `{"ok": true, "quiet": false, …}` @`2026-10-25T16:27:38-04:00`；pgrep 空 |
| 占用核 | 无其他 live 授权窗；live `.ok`=0 |

## 下一跳（架构口径）

1. **禁抬帽**（rss 仍 1500）；**禁**复用本 VOID 票 `a7d98ac9`；**禁** RESTORED `a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
2. AI 另交 **hist-prune** DRAFT → Arch **另审另签**；**不解阻 X2**
3. AI 侧稿可备，**禁自开跑**；等主裁排窗后再令 prelaunch
4. Arch **不代跑**、**不新签** `.ok`

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；≠X2；live=false
