# 叶27 month/ndays 侧稿 HAND 回执 · **HOLD_UNTIL_MAIN_SUBMIT**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T15:20:00-04:00（America/New_York；墙钟 2026-10-25 15:20 ET）
- **status**：**HOLD_UNTIL_MAIN_SUBMIT** — **勿交 Arch 审**；r3b PASS 回执 `a626000d` 主裁已收讫；等 **Arch CONSUME `.ok`+lift QUIET** 且主令「交审」后再 hand
- **ok_requested**：false · **live**：false · **实跑**：未做 · **脚本改动**：无
- **三件盘证（主裁钉 · 仍 MATCH）**：COVER `c8b33519` / CMD `5323d614` / DIFF `5fa2a29e`；脚本 UNCHANGED `262f9bf6`
- **注**：原 HAND sha8 `9428fcbf` 为 r3b 前 HOLD 文；本文件仅刷新交审门（内容钉不变）

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_COVER_DRAFT_20261025_ZH.md` | `c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_CMD_DRAFT_20261025_ZH.md` | `5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DIFF_DRAFT_20261025.diff` | `5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1` |
| 脚本（UNCHANGED） | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |

## 对照钉

| 钉 | 值 |
|---|---|
| ABORT 回执 | `4e37aacc…` |
| VOID `.ok` | `3a6caa4f`→`fc218dd1` **禁复用** |
| PRIMARY | `--chunk-mode month` |
| FALLBACK | `--chunk-mode ndays --chunk-ndays 40` |
| rss_limit | 1500 禁抬 |
| 禁 RESTORED | `8bcd79dc` / `725be3e0` / `3a6caa4f` |
| r3b | PASS 回执 `a626000d`（已过） |
| 交审门 | 等主令「交审」+ Arch CONSUME/lift |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未**改 `research/*.py`
- 禁自 lift QUIET / 禁申 X2.ok / 禁复跑 r3b / 禁抬帽
- ≠X2 · live=false
