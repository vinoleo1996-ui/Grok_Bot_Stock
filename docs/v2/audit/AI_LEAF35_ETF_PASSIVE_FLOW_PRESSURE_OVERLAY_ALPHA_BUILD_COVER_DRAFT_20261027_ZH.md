# 叶35 ETF 被动压力 overlay · 正式构建脚本封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T13:26:18-04:00（America/New_York；墙钟 2026-10-27 13:26 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 2026-10-27 ~13:15 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`5a082d18`**（FROZEN **`be9fc459` MATCH**；PIN **`dd17044a` MATCH**；RECEIPT **`132ba6f1` MATCH**）→ C2 落正式脚本

## 一句话

新脚本 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`** 已落盘；硬钉 FROZEN **`be9fc459`** / PIN **`dd17044a`**：mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高 `|pressure|` mask=0）；soft-penalty **非 PRIMARY**（默认关）；**C3 方案 A**=次月首个交易日 09:00 Asia/Shanghai `weight_available_at` + 份额 `available_at≤t`（禁静默月末 asof）；**C11≠叶26** 完整残差 α；再平衡 20；X2 2024-06-03→2026-10-09；HI_LIQ PRIMARY；overlap vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–34；rss=1500+peak_proof；forbid∋`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票；KEEP 三闸+**KEEP 不解阻**；C12 APPROX≠X2 ACCEPT。`--dry-compile-only` **PASS**。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审脚本**。≠X2 ACCEPT。`0087c928`/叶28/29 另队；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 叶34 HOLD CLOSED **`178e90e9`** 不回撤。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **正式构建脚本（NEW）** | **`25ae4572`** · 全长 `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` |
| PREREG_FROZEN | **`be9fc459`** |
| FROZEN RECEIPT | **`132ba6f1`** |
| Arch FROZEN 审 | **`5a082d18`** |
| Arch who_pays 审 | **`ee7ec307`** |
| WHO / COVER / COUNT / JSON / PIN / 计数脚本 | **`05942769`** / **`f41d7db8`** / **`cbca88e7`** / **`a17b75fb`** / **`dd17044a`** / **`4e964d40`** |
| 模板（只读未改） | leaf34 skeleton **`482009dc`**；leaf33 formal **`afbbe7e7` UNCHANGED**；leaf32 HOLD **`45dd87dc`** |
| rss | **1500** 禁抬 + peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009`；**mask-only** top_q=0.20；C3 方案 A |
| FULLA | 仅 `--also-fulla-research`（默认关；不得作 PRIMARY） |
| forbid | `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5`+二十票（26 sha8） |
| C10 | `0087c928` 另队；叶28/29 不夹带 |
| C11 | overlay mask 叠主干；**!=**叶26 完整残差 α；禁 moneyflow/行业 ETF 持仓主输入 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` + 本批 COVER/CMD/DIFF/RECEIPT |
| **动作** | (1) 硬钉 FROZEN/PIN 常量；(2) dry-compile pins；(3) 真跑路径：方案 A 权重 PIT + 份额 PIT → pressure_raw → top_q mask → 日度 exclusion mask；(4) overlap JSON vs moneyflow/26resid/8a/25/27/30–34；(5) peak_proof |
| **真跑门** | `--allow-real-data` + 现存 `--arch-ok-path`（sha8 not in forbid）+ 主窗；**本拍未开** |
| **不改** | FROZEN/`afbbe7e7`/`482009dc`/`45dd87dc`/`178e90e9`/`0087c928`/任一 `.ok`/QUIET；禁 RESTORED forbid 全集 |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit
- RESTORED **`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5`+二十票**
- 事后改 top_q / 翻剔除方向；卖方/金股；叶26 完整残差 α / moneyflow / 行业 ETF 持仓当主 α
- 静默月末 asof 当 PIT 完备；PRIMARY 静默改 FULLA；并入 `0087c928`；夹带叶28/29
- 报 Leo；声称 X2 ACCEPT / Book-Smoke；**KEEP 不解阻**；COUNT APPROX 当 ACCEPT

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审脚本**（COVER+CMD+DIFF+脚本 `25ae4572`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` |

live=false · !=X2 · ok_requested=false · EXECUTED=false · leo_notify=false
