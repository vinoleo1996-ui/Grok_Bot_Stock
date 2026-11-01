# 主收讫 · 叶27 ndays40 ABORT_RSS → VOID + hist-prune 另票

- **时刻**：2026-10-25T16:24:49-04:00（America/New_York）
- **角色**：主 Agent
- **结论**：**ABORT_RSS_OVER_LIMIT 盘证收讫** · **禁抬帽** · **禁静默换 mode**

## 盘证
| 项 | 值 |
|---|---|
| ET_TS | `20261025_162212` · pid `1576337` **gone** |
| 日志 | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_ndays40/_logs/run_20261025_162212.log` |
| 峰（日志） | **1514MB** @`chunk6_mktcap` / limit **1500** |
| sampler peak_kb | 1147568（≈1121MB；间隔低估） |
| 末态 chunk | chunk[5] freed 1479MB → chunk[6] members/capadv 1479 → mktcap **ABORT** |
| `.ok` | `a7d98ac9` **仍在盘** → 令 Arch **VOID**（勿 CONSUME_PASS） |
| QUIET | 仍挂 → VOID 后 Arch 可 lift |
| 主令 GO | `005db5df` 已消耗于本 ABORT |
| AI RUN_RECEIPT | **待交**（RUNNING 回执 `13411f8f` 已见；本回合主以日志盘证先 ack） |
| 未做 | 抬帽 / 静默换 mode / 申 X2 / 自重跑 |

## 编排下一跳
1. **AI**：立刻写 RUN_RECEIPT（峰/stage/ET_TS/pid）；**另交 hist-prune DRAFT**（COVER/CMD/DIFF/HAND）— DRAFT only；禁自开跑、禁申新 `.ok`、禁抬 rss、禁 silently 换 chunk-mode。
2. **Arch**：立刻 VOID `ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok`（sha `a7d98ac9`），归档；lift QUIET；回执主。
3. **硬钉延续**：rss=1500；forbid RESTORED 含本票 `a7d98ac9` + `8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；≠X2；live=false。

## 备注
ndays40 仍因 hist 累积在 chunk6 破帽（month 曾 @chunk12/1502；同族）；下一跳 **hist-prune 另票**，非 silent fallback。
