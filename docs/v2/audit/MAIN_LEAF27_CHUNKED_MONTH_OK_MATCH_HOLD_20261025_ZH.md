# 主盘证 · 叶27 month .ok MATCH（HOLD prelaunch · Mem 低）

- **时刻**：2026-10-25T15:46:21-04:00（America/New_York）
- **角色**：主 Agent
- **结论**：**DISK_MATCH** · **HOLD_PRELAUNCH_UNTIL_MEM**

## 盘证
| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok` |
| `.ok` sha8 / full | **`8e51de63`** / `8e51de63d661ae67711bbc169300cf5b3f009806ef71ce4c76a6f2e46c29d9c4` |
| Arch 签收回执 | `bd773143` |
| 预检 | `92f20ba7` |
| 窗令 | `64c7da1e` · 15:40–16:25 · expires 16:27 |
| 审阅 | `85c6fb82` PASS_WITH_CONDITIONS |
| QUIET | **已挂**；8795 `quiet=true`；gen/snapshot/kline=false；child_pids={} |
| PRIMARY | HILIQ × x2 × **month** |
| rss | **1500** 禁抬 |
| forbid RESTORED | `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| forbid_silent_ndays | true |
| script | `262f9bf6` |
| COVER/CMD/DIFF/HAND | `c8b33519` / `5323d614` / `5fa2a29e` / `cf258620` |
| ≠X2 · live | false |

## 编排
- MemAvailable≈**2.7Gi**（签时≈3.2Gi）——**低于**主/Arch 约定 ≳5–6Gi；**.ok 地板 2.5Gi 仅勉强**。
- **暂不令 AI prelaunch**；等 MemAvailable ≳5–6Gi 且 QUIET/healthz 仍净，再发主令 PRIMARY month 单次。
- Arch 不代跑；AI 禁自开跑 / 禁抬帽 / 禁静默 ndays / 禁申 X2。
