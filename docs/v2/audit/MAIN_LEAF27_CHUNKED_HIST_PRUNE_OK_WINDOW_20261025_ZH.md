# 主确认：叶27 hist-prune · 签窗

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-25T16:37:56-04:00`（America/New_York） |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_HIST_PRUNE_REVIEW_20261025_ZH.md` sha8 **`6543726a`**（PASS_WITH_CONDITIONS） |
| 盘证包 | COVER `85022506` / CMD `4cc9773a` / DIFF `0c7af6ed` / HAND `cc21f3c7` / VERIFY `4714256a` / HAND_TO_ARCH **`e8cc6058`** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`8cb3e86f`** CHANGED（prev `262f9bf6`；hist_prune_r1） |
| 主交审令 | `3806f922` |
| live / promotion | **false** / **false** |
| 对照 | ndays40 ABORT `03064d50`；VOID `.ok` `a7d98ac9`→`ad2947ef`；ndays40 审 `18ea1567` |

## 签窗（主确认）

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 16:45–17:30 ET** |
| expires | **17:32 ET**（+2min） |
| QUIET | **签时再挂**；现不挂 |
| 错开 | ndays40 VOID 齐；现盘无 live `.ok` / 无 QUIET；Mem≈7.0Gi |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok`（**新签**；禁 RESTORED 五票） |

## `.ok` 硬钉（抄自审 §签发清单 + 条件补钉）

- CLI PRIMARY（唯一）：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + 脚本 **`8cb3e86f`**（禁再签旧字节 `262f9bf6`）
- `hist_prune_tag=hist_prune_r1`；**无**同票 FALLBACK；ABORT → 停 + 另交主/Arch 票（禁 silently 换 mode；禁抬帽）
- `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
- `forbid_restored_ok_sha8`：**必须明文五票** `a7d98ac9`, `8e51de63`, `3a6caa4f`, `8bcd79dc`, `725be3e0`（脚本 dry meta 仅旧两票 → **签时补钉**）
- sampler：`/tmp/quantlab_leaf27_chunked_histprune_*` only（签时显式钉）
- out_dir 建议：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune`（或签文披露脚本 OUT_DIR 继承 + 采样分离）
- 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；峰证明 REQUIRED；≠X2
- 条件披露：不保证单块 mktcap 尖峰消失

## 下一跳

1. **Arch**：入窗（≥16:45）签发上列 `.ok` 并挂短窗 QUIET；本窗前不签；forbid 五票 + sampler/out_dir 明文。
2. **主**：签后盘证 MATCH → 令 AI prelaunch 单次 PRIMARY histprune（Mem 宜≳5Gi；地板按 `.ok`）。
3. **AI**：持新 `.ok` 单次开跑；禁抬帽；禁复用 VOID；ABORT → 停等主令；≠X2。

本文件不是 `.ok`。live=false。
