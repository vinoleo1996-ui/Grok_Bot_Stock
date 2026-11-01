# Arch 叶27 分块装载 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T14:08:15-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_CHUNKED_OK_WINDOW` sha `97b432d4…`；窗 **14:00–14:45 ET** expires **14:47** |
| 审阅 | `282d6ca1…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `3a6caa4f` / `3a6caa4f20a3881d72e493661592550c982698db80c9a190d7cf919c8fedb758` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb` PASS_WITH_CONDITIONS |
| 主令窗 | `97b432d4d75c6beae1f37c8e4373e72ee7a6faa705269c5d4f2ff8737418ab99` |
| COVER / CMD / DIFF | `e42ce686d9d21d3cc9fd3f7fb9018f7f24b0dfa06806a43f3637bb31f2bd9f16` / `cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb` / `b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635` |
| 审计 P1-4 | `c8877760dbf1c5b2158b7dd9136bc95d9d09ea5b11cd7ba4d219de2c86673c1a`（sha8 `c8877760`） |
| 窗期 | `2026-10-25T14:00:00-04:00` → `2026-10-25T14:45:00-04:00`；expires `2026-10-25T14:47:00-04:00` |
| CLI | `--universe HILIQ --window x2 --chunk-mode quarter` |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_*` |
| 禁 RESTORED | `8bcd79dc` / `725be3e0`（已 VOID；禁同 cmd lowmem_v1） |
| FULLA / both / sealed | **不进本窗**（sealed 另签） |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock`（保留不 lift） |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_PREOK_EVIDENCE_20261025_ZH.md`

## 下一跳

1. **主**确认后令 AI prelaunch 单次（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS）→ Arch 核
3. 叶25 r3b 签窗仍 **15:00–15:45**；勿抢本 QUIET 至本窗消费/VOID
4. live=false
