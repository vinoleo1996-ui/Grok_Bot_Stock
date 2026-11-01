# 主确认：叶27 分块装载 ndays=40 · 签窗

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-25T16:05:06-04:00`（America/New_York） |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_NDAYS40_REVIEW_20261025_ZH.md` sha8 **`18ea1567`**（PASS_WITH_CONDITIONS） |
| 盘证包 | COVER `ec5f67e9` / CMD `af6f0d49` / DIFF `5449dde5` / HAND `5547940b` / VERIFY `305f7a93` / HAND_TO_ARCH **`2986bd01`** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`262f9bf6`** UNCHANGED |
| 主交审令 | `b1cbafa1` |
| live / promotion | **false** / **false** |
| 对照 | month ABORT `03c58db5`；VOID `.ok` `8e51de63`→`30f7289d`；month 审 `85c6fb82` |

## 签窗（主确认）

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 16:15–17:00 ET** |
| expires | **17:02 ET**（+2min） |
| QUIET | **签时再挂**；现不挂 |
| 错开 | month VOID 齐；现盘无 live `.ok` / 无 QUIET；Mem≈6.7Gi |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok`（**新签**；禁 RESTORED 四票） |

## `.ok` 硬钉（抄自审 §签发清单）

- CLI PRIMARY（唯一）：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
- **无**同票 FALLBACK；ABORT → 停 + 另交 **hist-prune**（禁 silently 换 mode/ndays；禁抬帽）
- `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
- `forbid_restored_ok_sha8`: **`8e51de63`**, **`3a6caa4f`**, `8bcd79dc`, `725be3e0`（须明文进 `.ok`；dry meta 未含前两票）
- sampler：`/tmp/quantlab_leaf27_chunked_ndays40_*` only（签时显式钉）
- 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；峰证明 REQUIRED；≠X2

## 下一跳

1. **Arch**：入窗（≥16:15）签发上列 `.ok` 并挂短窗 QUIET；本窗前不签；forbid 四票明文。
2. **主**：签后盘证 MATCH → 令 AI prelaunch 单次 PRIMARY ndays40（Mem 宜≳5Gi；地板按 `.ok`）。
3. **AI**：持新 `.ok` 单次开跑；禁抬帽；禁复用 VOID；ABORT → 停等主令（另交 hist-prune）；≠X2。

本文件不是 `.ok`。live=false。
