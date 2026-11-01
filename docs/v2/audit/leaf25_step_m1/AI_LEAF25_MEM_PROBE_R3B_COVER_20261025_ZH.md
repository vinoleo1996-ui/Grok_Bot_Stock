# 叶25 mem_probe r3b · 交 Arch 审签封面（Arch PIN wrapper · 探针 UNCHANGED）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 起草/刷新 | `2026-10-25T13:11:30-0400`（America/New_York） |
| 状态 | **r3b 审签包已刷新钉 PIN** · **未申 `.ok`** · **本回合未实跑** · **未 git commit** · **未改生产 v5** |
| live | **false** · promotion_approved **false** |
| Arch VOID 裁定 | sha **`43fe482e462bb6e3f3c64c687f8dcda9693cbb7849d67593f23f9653f780b0ce`** |
| r3 FAIL 回执 | sha **`04552c3c83e3f2084ddeab35b6075f665536fdf4dc22b8952f6de01790e3e5f2`** |
| Arch C5 审阅 | sha **`74149e2995fde6ee04b9ce812b0a938a6749f006294eac76feb0356469b4812a`**（PASS_WITH_CONDITIONS · `74149e29`） |
| Arch PIN 文 | sha **`340ab36c357c2335fde4c9446038daec19fcc83bd96b800906367be2bb1f3617`**（`340ab36c`） |
| **启动 wrapper** | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` sha **`b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`** |
| 探针脚本 | `research/leaf25_full_factor_mem_probe_r3.py` **UNCHANGED** `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` |

## 0. 目的

r3 被 v5 C5 误杀（VOID_FAIL_C5_FALSE_POSITIVE）。本 r3b **仅换 wrapper 启动侧**为 Arch **已 PIN** 的 v6 C5TIGHTEN（路径名必须 `…_b1208d3c.sh`）；探针 **UNCHANGED**。交 Arch **另审另签新实峰 probe `.ok`**。≠授权开跑；≠解阻 X2；≠替换 live v5。

## 1. 输入钉（MATCH）

| 件 | sha256 | 结果 |
|---|---|---|
| Arch PIN wrapper | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` | **MATCH** |
| Arch PIN 文 | `340ab36c357c2335fde4c9446038daec19fcc83bd96b800906367be2bb1f3617` | **MATCH** |
| Arch 审阅 | `74149e2995fde6ee04b9ce812b0a938a6749f006294eac76feb0356469b4812a` | **MATCH** |
| Eng DIFF / COVER / 回执 | `a3a228a9…` / `6339f298…` / `dabe75ec…` | **MATCH**（全长见 CMD §1） |
| v5 live（未覆盖） | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |
| 探针 / chunk / stub | `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` / `e858b32d…` / `45537fb9…` | **UNCHANGED MATCH** |
| VOID / 回执 | `43fe482e…` / `04552c3c…` | **MATCH** |

`bash -n` PIN 脚本 → 见 §7。

## 2. 交付物

| 件 | 路径 | sha256 |
|---|---|---|
| **本封面** | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_COVER_20261025_ZH.md` | 以盘 `sha256sum` / 交手回执为准 |
| **CMD** | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_CMD_DRAFT_20261025_ZH.md` | **`689dc55cee93b4cc767b5fe19ecd0e89cbb2182350ac5da7a2d5bf2ee6919770`** |
| **DIFF** | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_20261025.diff` | **`e92796fe1b502f661eea5c9ac470005aaa184699d394b1f6ba375b35c3711fe7`** |
| 交手回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3B_HAND_TO_ARCH_RECEIPT_20261025_ZH.md` | 以盘为准 |

依赖 Eng DIFF `a3a228a9…`；探针无 py DIFF。  
**禁** AI 并行草案 `e03a61b6…`；**禁** CMD 启动 `.draft.sh`（同 sha 仅旁证）。

## 3. 三杠杆（Eng COVER `6339f298…`）

A 本跑 logdir/outdir fd 白名单 · B 良性 sleep/true/cat · C stdout→`/tmp/quantlab_wrapper_logs/`。  
未改 C4/STOP/HARD、`--c5-ignore` refuse-91、live v5。

## 4. 仍钉

C4/stop/hard = **1331200/1484800/1536000**；采样 `/tmp`；`allow_c5_ignore=false`；HI_LIQ 单块 month 2024-06；禁 `--window both`。

## 5. 排窗

错开叶27 **14:00–14:45 ET**；拟窗请主另排（建议 **≥15:00 ET** 或叶27 后）。

## 6. 禁项

禁自开跑 / 抬帽 / `--c5-ignore` 实峰 / 申 X2 / 复用 `c5e54085`/`cd230f9c`/`1c32ab1e` / 混用 `e03a61b6` / 启动 `.draft.sh` / 覆盖 v5 / git commit。

## 7. 静态自检

| 检查 | 结果 |
|---|---|
| PIN sha | **MATCH** `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` |
| CMD 启动路径含 `_b1208d3c.sh` | **是** |
| CMD 无 `.draft.sh` 启动行 | **是**（draft 仅旁证行） |
| 无 `e03a61b6` 作权威 | **是** |
| `bash -n` PIN | 见回执 |
| 实跑/申.ok/git | **未做** |

## 8. 下一跳

1. **Arch**：审本包 → **另签** `ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`（钉 PIN/`b1208d3c`/C4/`/tmp`/HI_LIQ；禁 VOID 旧票）。
2. **主**：排窗错开叶27。
3. **AI**：等新 `.ok`+入窗再跑；≠X2。

**本文件不是 `.ok`。** live=false。
