# 叶27 ndays=40 独立侧稿 HAND 回执 · **HOLD_UNTIL_MAIN_SUBMIT**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T15:57:35-04:00（America/New_York；墙钟 2026-10-25 15:57 ET）
- **status**：**HOLD_UNTIL_MAIN_SUBMIT** — **勿交 Arch 审**；等主令「交审」+ Arch VOID/CONSUME 已消费 month `.ok` `8e51de63` 后再 hand
- **ok_requested**：false · **live**：false · **实跑**：未做 · **脚本改动**：无 · **`.ok`**：未申 · **QUIET**：未 lift
- **三件盘证**：COVER `ec5f67e9` / CMD `af6f0d49` / DIFF `5449dde5`；脚本 UNCHANGED `262f9bf6`
- **触发**：month ABORT 回执 `03c58db5`（1502@chunk12）；Arch 审 `85c6fb82` 要求另交 ndays40 票

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_COVER_DRAFT_20261025_ZH.md` | `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_CMD_DRAFT_20261025_ZH.md` | `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DIFF_DRAFT_20261025.diff` | `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` |
| 脚本（UNCHANGED） | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |

## 对照钉

| 钉 | 值 |
|---|---|
| month ABORT 回执 | `03c58db5…`（ET_TS=`20261025_154958`；1502MB @chunk12_mktcap） |
| 已消费 month `.ok` | `8e51de63` **禁 RESTORED**（听 Arch VOID/CONSUME） |
| VOID/禁复用 | `3a6caa4f` / `8bcd79dc` / `725be3e0` / `8e51de63` |
| month baseline 包 | COVER `c8b33519` / CMD `5323d614` / DIFF `5fa2a29e`（**不覆盖**） |
| PRIMARY | `--chunk-mode ndays --chunk-ndays 40`（**唯一**；无 silent） |
| 若再 ABORT | 另交 hist-prune 包；禁抬帽 |
| rss_limit | 1500 禁抬 |
| sampler | `/tmp/quantlab_leaf27_chunked_ndays40_*` only |
| 交审门 | 等主令「交审」 |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未**改 `research/*.py`
- **未** lift QUIET；**未**抬帽；**未**启动任何实数进程
- 禁自开跑 / 禁申 X2.ok / 禁复用 VOID/CONSUMED / 禁静默切 mode
- ≠X2 · live=false
