# 叶27 ndays=40 DRAFT 盘证 · 2026-10-25 15:58 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| COVER | `ec5f67e9` | `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` | **MATCH** |
| CMD | `af6f0d49` | `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` | **MATCH** |
| DIFF | `5449dde5` | `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` | **MATCH**（NO_CODE_CHANGE） |
| HAND | `5547940b` | `5547940bec333aa5515af5defccdde241c8812a9fb87f5bcc495427586424a81` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| 脚本 | `262f9bf6` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | **MATCH UNCHANGED** |
| month ABORT 回执 | `03c58db5` | `03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177` | **MATCH**（触发源） |
| month baseline COVER/CMD/DIFF | `c8b33519` / `5323d614` / `5fa2a29e` | （既有包；本票不覆盖） | 对照保留 |
| HAND_TO_ARCH | （见同目录文件；本表不自指） | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HAND_TO_ARCH_20261025_ZH.md` | **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | OK：`live:false` `ok_requested:false` `rss_limit_mb:1500`；mechanism_tag 齐；**无实数加载** |
| `py_compile` → `/tmp/leaf27_chunked_members_mktcap_r1.pyc` | OK |
| pyflakes | **unavailable**（venv/系统均无） |
| `pgrep` leaf27 | **NO_LEAF27_PROC**（未开跑） |

## forbid_restored（明文）

`8e51de63`（month 已消费） / `3a6caa4f` / `8bcd79dc` / `725be3e0`

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND_TO_ARCH=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / Arch VOID month ok `8e51de63`
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁 lift QUIET
- PRIMARY only：`--chunk-mode ndays --chunk-ndays 40`
- live=false · ≠X2
