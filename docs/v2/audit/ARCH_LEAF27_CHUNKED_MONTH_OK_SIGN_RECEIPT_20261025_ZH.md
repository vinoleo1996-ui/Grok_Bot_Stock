# Arch 叶27 分块装载 month · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T15:45:21-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_CHUNKED_MONTH_OK_WINDOW` sha `64c7da1e…`；窗 **15:40–16:25 ET** expires **16:27** |
| 审阅 | `85c6fb82…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 month 分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID（含 quarter `3a6caa4f`）；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok` |
| `.ok` sha8 / 全长 | `8e51de63` / `8e51de63d661ae67711bbc169300cf5b3f009806ef71ce4c76a6f2e46c29d9c4` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119` PASS_WITH_CONDITIONS |
| 主令窗 | `64c7da1e651ea2c08ac6d624e20262da4720673651d8120597ff1c02b5e07982` |
| COVER / CMD / DIFF | `c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b` / `5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077` / `5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1` |
| HAND / HAND_TO_ARCH / VERIFY | `cf2586207e5fffb0521ac0b5b5a9cb2ebc4f678dd30c9f1c3fe02f826ceb4057` / `eb3fb164869593e0f05bdb1397f86a1ebd6bf80a83d1ee5f56c31a0a5b43c8ab` / `f649ba15448dd1168b967e27a84e4073c9d71dd250212af603835037762e7d0a` |
| ABORT / VOID 回执 | `4e37aacc17998682a8713fe4e4648d40f4e8ac3fcbb3741182838ded849b879b` / `c1c6a95ce1c4c8565712f6f983712689934c66a7272fe7e4ff5737134415ce4e` |
| 窗期 | `2026-10-25T15:40:00-04:00` → `2026-10-25T16:25:00-04:00`；expires `2026-10-25T16:27:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode month` |
| FALLBACK | `--chunk-mode ndays --chunk-ndays 40` **仅另签**；禁 silently |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_month_*` |
| 禁 RESTORED | `3a6caa4f` / `8bcd79dc` / `725be3e0`（已 VOID；禁同 cmd lowmem_v1） |
| FULLA / both / sealed | **不进本窗**（sealed / ndays 另签） |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock`（保留不 lift） |
| MemAvailable@签 | 3344328 kB |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_PREOK_EVIDENCE_20261025_ZH.md` sha `92f20ba7f0adba99fba69b8f837761c12fcacd762c05ddaee9581f7529933925`

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY month（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS）→ Arch 核
3. month ABORT → **停**；另交 ndays40 票另审另签（勿 silently fallback）
4. ≠X2；live=false
