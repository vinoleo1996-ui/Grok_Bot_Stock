# Arch 叶25 mem_probe r3b 实峰 probe `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T15:09:33-04:00`（America/New_York） |
| 主令 | 窗令 `bd13c878…` **15:00–15:45** expires 15:47；PASS_WITH_CONDITIONS 后签独立实峰 probe |
| 审阅 | `eaedd655…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立实峰 probe `.ok` 已落盘；**≠ X2.ok**；**Arch 不代跑**；X2 / NEED_MEM_PROBE **仍不解阻**，直至入窗实峰跑 PASS。禁复用 VOID `c5e54085` / `cd230f9c` / `1c32ab1e`。禁 `.draft.sh` / `e03a61b6`；`allow_c5_ignore=false`。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok` |
| `.ok` sha8 / 全长 | `6054b3bf` / `6054b3bfc44977614d299976da28e72d757885cf6a59fa26b361d4112060692b` |
| 脚本 | `research/leaf25_full_factor_mem_probe_r3.py` = `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea`（UNCHANGED） |
| wrapper PIN v6 C5TIGHTEN | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5`（路径 `cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh`；live v5 `4240ce82` 未动） |
| 审阅 | `eaedd6558c12dd7915448eb57bca829abb709d9f49378a3f723fcd058e4cad46` PASS_WITH_CONDITIONS |
| 主窗令 | `bd13c878daea8cac1f35f66be7925239256c52f9bbb67ffa5a59862b7203a8b8` |
| COVER/CMD/DIFF/HAND | `c5d0c4f0af18b3e23a9242717f3f68e9e31b2023c6940dcc98ed3eeda6cf5e8d` / `689dc55cee93b4cc767b5fe19ecd0e89cbb2182350ac5da7a2d5bf2ee6919770` / `e92796fe1b502f661eea5c9ac470005aaa184699d394b1f6ba375b35c3711fe7` / `9fab0ef416867abb80129a650bc136bb768cfab0153df511ac497488769d58bf` |
| chunk/stub | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` / `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3`（UNCHANGED） |
| 窗 | `2026-10-25T15:00:00-04:00` → `2026-10-25T15:45:00-04:00`；expires `2026-10-25T15:47:00-04:00`（叶27 14:00–14:45 已过 VOID `3a6caa4f`） |
| CLI 核 | HI_LIQ · `--mode month` · `--start 2024-06-03 --end 2024-06-28 --chunk-id 0` · `--allow-real-data` |
| 帽 | C4/stop/hard **1331200/1484800/1536000**；阈 **1131520**；**禁抬帽** |
| 采样 | 仅 `/tmp/quantlab_leaf25_mem_probe_r3b_*` |
| C5 | `allow_c5_ignore=false`；`forbid_c5_ignore_flag=true`；禁实峰 `--c5-ignore` |
| 禁复用 | `c5e540855bc836b97b7395a53dd63a6d3c295860fdd11e72e77abd6cf3152011`；`cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`；`1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；禁 `.draft.sh`；禁 `e03a61b6`；禁 r1 dry；禁 X2/密封同张 |
| 披露 | dry_run=false；float32；densify=false；claims_full_cfacc=false；alpha_kind=crude_accrual_cs_zscore_probe_only；peak_kb；end_date_filter=Timestamp |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock` 留给 AI prelaunch（**未 lift**） |

## 预检旁证

`ARCH_LEAF25_MEM_PROBE_R3B_PREOK_EVIDENCE_20261025_ZH.md` sha `6703e5926dca6f8cdaa571a5afb7cb7426cd9a932929c93bb9d4f15f2093da88`

## 下一跳

1. **请主令 AI prelaunch** 单次开跑（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（peak_kb 等）→ Arch 核 → 才解阻 X2 内存键
3. ≠X2；live=false；例程由主侧处理（本执行器不删例程）
