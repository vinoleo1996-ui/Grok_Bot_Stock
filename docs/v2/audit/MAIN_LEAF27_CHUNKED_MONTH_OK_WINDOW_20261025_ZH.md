# 主确认：叶27 分块装载 month · 签窗

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-25T15:26:00-04:00`（America/New_York） |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_REVIEW_20261025_ZH.md` sha8 **`85c6fb82`**（PASS_WITH_CONDITIONS） |
| 盘证包 | COVER `c8b33519` / CMD `5323d614` / DIFF `5fa2a29e` / HAND `cf258620` / VERIFY `f649ba15` / HAND_TO_ARCH `eb3fb164` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`262f9bf6`** UNCHANGED |
| live / promotion | **false** / **false** |
| 对照 | quarter ABORT `4e37aacc`；VOID `.ok` `3a6caa4f`→`fc218dd1`；先验审 `282d6ca1` |

## 签窗（主确认）

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 15:40–16:25 ET** |
| expires | **16:27 ET**（+2min） |
| QUIET | **签时再挂**；现不挂 |
| 错开 | 叶25 r3b 已 CONSUMED_PASS（`6054b3bf`→`74b5f209`）；现盘无 live `.ok` / 无 QUIET / 无研究 python |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok`（**新签**；禁 RESTORED `3a6caa4f`/`8bcd79dc`/`725be3e0`） |

## `.ok` 硬钉（抄自审 §7）

- CLI PRIMARY：`--universe HILIQ --window x2 --chunk-mode month`
- FALLBACK：**仅** month 再 ABORT 后另签 `--chunk-mode ndays --chunk-ndays 40`（禁 silently fallback）
- `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
- `forbid_restored_ok_sha8`: **`3a6caa4f`**, `8bcd79dc`, `725be3e0`（须明文进 `.ok`；dry meta 未含 `3a6caa4f`）
- sampler：`/tmp/quantlab_leaf27_chunked_month_*` only
- 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；峰证明 REQUIRED；≠X2

## 下一跳

1. **Arch**：入窗（≥15:40）签发上列 `.ok` 并挂短窗 QUIET；本窗前不签。
2. **主**：签后盘证 MATCH → 令 AI prelaunch 单次 PRIMARY month。
3. **AI**：持新 `.ok` 单次开跑；禁抬帽；禁复用 VOID；month ABORT → 停等主令（勿自切 ndays）；≠X2。

本文件不是 `.ok`。live=false。
