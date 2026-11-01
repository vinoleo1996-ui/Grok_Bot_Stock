# 叶27 month/ndays DRAFT · HAND TO ARCH（只交不跑）

- **时刻**：2026-10-25T15:22:57-04:00（America/New_York）
- **角色**：QuantLab AI
- **依据**：主令「交审 GO」2026-10-25 15:22 ET；Arch CONSUME+lift 已盘证
- **status**：**SUBMITTED_TO_ARCH** · ok_requested=**false** · **禁自开跑** · live=false
- **废**：口头旧 HAND `9428fcbf`（以现 HAND `cf258620` 为准）

## 交审钉（盘证 MATCH）

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_COVER_DRAFT_20261025_ZH.md` | `c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_CMD_DRAFT_20261025_ZH.md` | `5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DIFF_DRAFT_20261025.diff` | `5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DRAFT_HAND_20261025_ZH.md` | `cf2586207e5fffb0521ac0b5b5a9cb2ebc4f678dd30c9f1c3fe02f826ceb4057` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DRAFT_VERIFY_20261025_ZH.md` | `f649ba15448dd1168b967e27a84e4073c9d71dd250212af603835037762e7d0a` |
| 脚本 UNCHANGED | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |

## 提案

- PRIMARY：`--chunk-mode month`（HILIQ × x2）
- FALLBACK：`--chunk-mode ndays --chunk-ndays 40`（仅 month 再 ABORT）
- rss_limit：**1500** 禁抬帽
- 禁复用 VOID：`3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁自开跑；禁申 X2.ok；≠X2

## 请 Arch

- 只审 COVER+CMD+DIFF（脚本宣称 UNCHANGED `262f9bf6`）
- **本回合不签 `.ok` / 不代跑**；签窗另排听主
- 审毕回执即可

live=false · promotion_approved=false
