# 叶25 mem_probe r3b · `.ok` 盘证 READY（等主令）

- **时刻**：2026-10-25T15:11:00-04:00（America/New_York）
- **角色**：QuantLab AI
- **status**：**READY_WAIT_MAIN_PRELAUNCH** — Arch 已签；**禁自开跑**；等主令后单次 prelaunch
- **live**：false · ≠X2

## 盘证

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok` sha **`6054b3bfc44977614d299976da28e72d757885cf6a59fa26b361d4112060692b`** |
| wrapper PIN | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` sha8 **`b1208d3c`**（禁 `.draft.sh` / `e03a61b6`） |
| probe | `research/leaf25_full_factor_mem_probe_r3.py` sha8 **`8da4f2e6`** |
| 帽 | C4=1331200 / STOP=1484800 / hard=1536000 **禁抬** |
| CLI | HI_LIQ · `--mode month` · chunk-id 0 · 禁 `--c5-ignore` · sampler `/tmp/quantlab_leaf25_mem_probe_r3b_*` |
| 窗 | 15:00–15:45 · expires **15:47** ET（`bd13c878`） |
| QUIET | 已挂 · 8795 `quiet=true` · 读者 pgrep 空 |

## 边界

- 等**主令** prelaunch 后单次开跑；交实峰回执
- 禁复用 VOID：`c5e54085` / `cd230f9c` / `1c32ab1e`
- Arch 不代跑；AI 不自开跑
