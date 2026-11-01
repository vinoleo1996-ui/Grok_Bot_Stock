# 主确认：叶25 mem_probe r3b 签窗

| 项 | 值 |
|---|---|
| 角色 | 主 Agent |
| 时刻 | `2026-10-25T13:21:51-0400`（America/New_York） |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R3B_REVIEW_20261025_ZH.md` sha8 **`eaedd655`**（PASS_WITH_CONDITIONS） |
| 盘证包 | COVER `c5d0c4f0` / CMD `689dc55c` / DIFF `e92796fe` / 回执盘 `9fab0ef4`（忽略正文自指 `110f484f`） |
| wrapper PIN | `cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` / `b1208d3c` |
| 探针 | `8da4f2e6` UNCHANGED |
| live / promotion | **false** / **false** |

## 签窗（主确认）

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 15:00–15:45 ET** |
| expires | **15:47 ET**（+2min） |
| QUIET | **签时再挂**；现不挂 |
| 错开 | 叶27 **14:00–14:45 ET**（不抢） |
| 拟 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`（另签；禁复用 `c5e54085`/`cd230f9c`/`1c32ab1e`） |

## 下一跳

1. **Arch**：入窗签发上列 `.ok`（钉 PIN 路径+三帽+`allow_c5_ignore=false`+`/tmp` sampler+HI_LIQ 单块）并挂短窗 QUIET。
2. **主**：签后回令 AI prelaunch。
3. **AI**：持新 `.ok` 开跑；禁 `--c5-ignore`；≠X2；破 0.85×C4 → exit 94 拆块（禁抬帽）。

本文件不是 `.ok`。live=false。
