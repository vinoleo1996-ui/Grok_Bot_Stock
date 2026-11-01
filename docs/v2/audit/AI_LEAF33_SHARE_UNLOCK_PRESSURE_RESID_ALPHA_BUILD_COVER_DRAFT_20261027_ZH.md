# 叶33 限售解禁压力残差慢 α · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T06:13:30-04:00（America/New_York；墙钟 2026-10-27 06:13 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 ~06:04 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`bf5234a9`**（FROZEN **`8ed43721` MATCH**；PIN **`4e17ccfc` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`05c45917`** 已落盘；硬钉 FROZEN **`8ed43721`** / PIN **`4e17ccfc`**：mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；C3=(a)+加价 `unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`；`pressure_raw=mean_W`；α=`−rank(pressure_resid)`；H/H_back/W/rebal=20/5/20/20；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；残差 SW L1 + logmv + mom20/vol20/logADV20；close 钉 **不复权 `close`**；表内 `float_ratio` PRIMARY 禁用；overlap vs 叶19/25/27/30/31/32 + margin_delta/hk_hold/moneyflow；rss=1500+peak_proof；forbid∋`5774bb6e`+二十票；KEEP 三闸+**KEEP 不解阻**。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。`0087c928`/叶28/29 另队。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`05c45917`** · 全长 `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` |
| PREREG_FROZEN | **`8ed43721`** |
| FROZEN RECEIPT | **`8f43e2f8`** |
| Arch FROZEN 审 | **`bf5234a9`** |
| Arch who_pays 审 | **`55531e12`** |
| WHO_PAYS / COVER / PIN | **`1032477d`** / **`61d9f656`** / **`4e17ccfc`** |
| 模板（只读未改） | leaf32 build **`4e0f3c00`**；leaf31 **`08f37fd2`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009` |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| C3 | (a)+加价；close=`close`（不复权收盘价元）；float_ratio PRIMARY 禁用 |
| forbid | `5774bb6e`+二十票（21 sha8） |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf33_share_unlock_pressure_resid_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN/PIN 常量；(2) dry-compile pins；(3) 真跑路径：再平衡日懒加载 share_float+close+mktcap+bars → pressure_raw → 残差 → −rank → 日度 α；(4) overlap JSON；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | FROZEN/`4e0f3c00`/`08f37fd2`/`3ee9fed2`/`dcf6b559`/`0087c928`/任一 `.ok`/QUIET；禁 RESTORED `5774bb6e`+二十票 |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit
- RESTORED **`5774bb6e`+二十票**（含 `02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`…）
- 事后翻 α 符号 / W / H / H_back / 再平衡；卖方/金股；Amihud/on_minus_id/CRR/hk_hold/moneyflow/两融/`float_ratio` 主输入
- PRIMARY 静默改 FULLA；并入 `0087c928`；夹带叶28/29
- 报 Leo；声称 X2 ACCEPT / Book-Smoke；**KEEP 不解阻** X2 ACCEPT

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `05c45917`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
