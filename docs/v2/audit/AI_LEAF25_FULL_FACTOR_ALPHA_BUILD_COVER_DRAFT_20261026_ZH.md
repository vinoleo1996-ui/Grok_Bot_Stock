# 叶25 全叶/HILIQ×x2 alpha 构建 · 侧稿封面 · **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T01:20:00-04:00（America/New_York；墙钟 2026-10-26 01:20 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · **禁自签** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**alpha 构建**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT）
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — 出齐后回主交审；等主排签窗；现勿交、勿签、勿开跑

## 一句话

主令本拍「定下一票｜叶25 全叶 HILIQ×x2 alpha 构建 DRAFT」：盘点 MATCH 叶25 无全窗 alpha→不可 selfcheck；须先落 **新** 全叶/HILIQ×x2 alpha 构建包。继承旧 CMD DRAFT sha8 **`035e5818`** 与 r6 FROZEN 令 sha8 **`53331667`**（戳记 **`4bb1ff2b`** · 基盘 **`e8ca2bcc`** · MEM **`103717df`**）。**新脚本** `research/leaf25_full_factor_alpha_build_r1.py` sha **`de7b3647`**（全长 `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`）——**禁**把已 VOID/CONSUMED 探针 `leaf25_full_factor_mem_probe_r1/r2/r3` 当构建本体；可参考其 PIT 投影/end_date 类型修复/HI_LIQ 成员加载。PRIMARY **HILIQ×x2**；rss 软帽 **1500 禁抬**；**禁 FULLA**；禁复用 `.ok`：`1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf`。机制 `g1g5_ashare_cfacc_desens_cs_v1`：CFACC TTM + desensitize(−CFACC) + 截面残差（协变量缺→PIN/meta；leaf19 缺→0）。X2 窗 **2024-06-03→2026-10-09**（`X2_END_TRADE_DATE=20261009`）。密封另签不含。叶26 本拍不交审。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| 主令本拍 | 定下一票｜叶25 全叶 HILIQ×x2 alpha 构建 DRAFT（~01:14 ET） |
| 旧 CMD DRAFT | **`035e5818`** · `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_X2_CMD_DRAFT_20261025_ZH.md` |
| r6 FROZEN 令 | **`53331667`** · `docs/v2/audit/MAIN_LEAF25_R6_FROZEN_ORDER_20261025_ZH.md` |
| FROZEN 戳记 | **`4bb1ff2b`** · `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` |
| 基盘 DRAFT | **`e8ca2bcc`** · `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` |
| MEM/分块 | **`103717df`** · `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` |
| wrapper v5 | **`4240ce82`** · `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` |
| **新脚本** | **`de7b3647`** · `research/leaf25_full_factor_alpha_build_r1.py` |
| mechanism_tag | `g1g5_ashare_cfacc_desens_cs_v1` |
| PRIMARY CLI | `--universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month` |
| rss_limit | **1500**（**禁抬**）；C4/stop/hard 1331200/1484800/1536000 kB |
| X2 窗 | 2024-06-03 → 2026-10-09 |

## 提案（CODE · PRIMARY CLI）

| 项 | 内容 |
|---|---|
| **新文件** | `research/leaf25_full_factor_alpha_build_r1.py`（**不**覆盖 stub `leaf25_cfacc_desens_build_r1.py` / 探针 `mem_probe_r*`） |
| **CFACC 主路径** | TTM（对齐 step_m1_r5）→ winsor1/99→rank→normal(−CFACC) |
| **残差** | SW L1 / logmv / leaf19 尽力；β120/mom/logADV20/vol20 = **PIN_GAP**（meta `residual_covars_status`）；缺 leaf19→0 |
| **分块** | import `leaf25_full_factor_chunk_plan_r1`；month 或 rebal；禁整窗 densify |
| **真路径闸** | `--allow-real-data` + 现盘 `--arch-ok-path`；ok sha ∉ forbid |
| **dry-compile-only** | 打印 live/ok_requested/rss/universe/window/forbid/mechanism；**零**大表加载 |
| **输出** | `alpha_parts/HI_LIQ/part_*.parquet` + `alpha_HILIQ_x2_<ET_TS>.parquet` + `run_meta.json` |
| **sampler** | `/tmp/quantlab_leaf25_full_alpha_*` only |
| **out_dir 建议** | `output/ai_factory/_leaf25_full_factor/<ET_TS>/` |

硬钉：

| 项 | 值 |
|---|---|
| universe / window | **HILIQ × x2**（禁 `both` / FULLA） |
| rss_limit | **1500** MB（**禁抬帽**） |
| script sha256 | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`（sha8 **`de7b3647`**） |
| wrapper | v5 `4240ce82`（CMD 亦可直接 python+sampler；二选一写清） |

## 禁止清单

- 申 `.ok` / 自开跑 / 自签 / 抬 `rss_limit` / 擅 lift QUIET / 申 X2 ACCEPT
- 复用 forbid `.ok`：**`1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf`** 及一切 VOID/CONSUMED
- 把 mem_probe r1/r2/r3 / stub 当构建入口或覆盖之
- `--window both` / `--universe FULLA`
- Book-Smoke / selfcheck / eval_weights（本票不做）
- 读真实行情大表做实跑（本 DRAFT 回合）
- git commit
- 叶26 本拍交审

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch；Arch **只审不签**；主排签窗后发**新** `.ok`（≠ forbid 任一）。
2. **Arch**：只审不签；PASS 后等主排窗；新 `.ok` 须钉脚本 sha `de7b3647` / PRIMARY HILIQ×x2 / rss=1500 / forbid 明文。
3. 残差 PIN_GAP（β120/mom/logADV20/vol20）须主/Data/Arch 另钉 reader 后方可声称「全残差」；本票 CFACC 主路径已实装。
4. ABORT → **停+上报**；禁自重试 / 禁抬帽。

## 盘证（本回合）

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_COVER_DRAFT_20261026_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_CMD_DRAFT_20261026_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DIFF_DRAFT_20261026.diff` |
| HAND | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_VERIFY_20261026_ZH.md` |
| H2A | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_HAND_TO_ARCH_20261026_ZH.md` |
| 脚本 | `research/leaf25_full_factor_alpha_build_r1.py` |

live=false · ≠X2 ACCEPT · ≠selfcheck · **HOLD_UNTIL_MAIN_SUBMIT** · ok_requested=false
