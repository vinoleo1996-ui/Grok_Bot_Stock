# 叶27 HI_LIQ 主路径独立 .ok 签发回执

- 时刻（America/New_York）：2026-10-25T11:02:19-04:00
- 依据：主令例程 `27-ok-10-50`；条件3 Data `acb8d3e0…` + AI ALL_MATCH `63185c9f…`；R2 `4c85a169…`；豁免 `b39954c3…`；预告 `31462908…`
- live=false；promotion=false

## .ok

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ.ok` |
| sha256 | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` |
| sha8 | `725be3e0` |
| 宇宙 | **仅 HILIQ**（FULLA **未签** / GAP） |
| 脚本 | `7a5f756c…` |
| DIFF / impl / 闭合 | `e2ed0fc8…` / `a532e6db…` / `f4327917…` |
| 窗 | **2026-10-25T10:50:00-04:00 → 2026-10-25T11:12:00-04:00**（expires 2026-10-25T11:14:00-04:00） |
| 避让 | 叶25 v4 `1c32ab1e` @ 11:15–12:00；禁复用 `7b279d47` |
| rss | ≤1500 MB |

## 预检

见 `docs/v2/audit/ARCH_LEAF27_PREOK_EVIDENCE_20261025_ZH.md` sha `36a143793a27e2d5d66eb6911b8cae8210f0a6fed287bc6c423fb1853399c2de`。

## 给 AI

窗内用本 `.ok` 仅跑 `--universe HILIQ`（禁 FULLA/both）；须在叶25 11:15 前结束或等禁窗过后再谈另签；开跑前自设 `RESEARCH_QUIET.lock` 并复检 healthz/pgrep。
