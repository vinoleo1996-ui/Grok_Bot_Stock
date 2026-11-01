# 叶35 ETF 被动压力 overlay · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 13:03 ET（America/New_York；ISO `2026-10-27T13:03:36-04:00`）
- 动作：按主令 2026-10-27 ~12:57 ET + Arch **PASS_WITH_CONDITIONS** `ee7ec307` 落 **PREREG_FROZEN**（C1–C13 入钉）+ C3 PIN（方案 A）+ 计数脚本迁仓
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf35*` / **未挂 QUIET** / **未** RESTORED forbid / **未**并入 `0087c928` / **未** git commit / **未** SendToUser / **未** SendToAgent / **未**改 TEAM_STATE / **未**改叶33 `afbbe7e7`
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | **`be9fc459`** | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` |
| **PIN（C3）** | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | **`dd17044a`** | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` |
| **计数脚本迁仓** | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | **`4e964d40`** | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `ee7ec307` | MATCH（`ee7ec307e22bb5e6b98b6521d76e5f62a04311ffc9917efafde24524861a6f93`） |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `05942769` | MATCH（`0594276917a88969456ed3b7103d7f51ca26d4b2923125295507f1a8f2802997`） |
| COVER DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `f41d7db8` | MATCH（`f41d7db8f0632a8433972def18bd92b6f76f625fdabd9603b5fe18be74ca92a1`） |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `cbca88e7` | MATCH（`cbca88e797c4c423e082d8db189ef1e0265747e90990817bbfd823f09798b431`） |
| COUNT JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` | `a17b75fb` | MATCH（`a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6`） |

路径说明：落于 `docs/v2/audit/`（与叶34 同目录）；未写 `docs/v2/` 根下双份。

## C1–C13 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册 | **FROZEN 全文**：mask-only；q=0.20；再平衡 20d；X2 窗 2024-06-03→2026-10-09；成本 30bp；判定双路径 |
| C2 | 正式脚本另窗；计数迁仓 | `research/leaf35*` **ABSENT**；计数脚本迁仓 **`4e964d40`**（内容=原 /tmp） |
| C3 | 权重 asof 升级方案 A | PIN **`dd17044a`**：次月首个**交易日** 09:00 Asia/Shanghai = `weight_available_at`；份额 `available_at≤t`；映射三件套；禁静默 APPROX |
| C4 | soft-penalty / mask | **明示 mask-only PRIMARY**；连续 soft-penalty 非 PRIMARY，启用须 SW+style |
| C5 | top_q 符号冻结 | q=0.20；高 `|pressure|`=剔除；禁读收益改阈值/翻方向；行业 ETF 禁主轴 |
| C6 | FULLA 双钉 | HI_LIQ PRIMARY（mask hiliq_v1，median≥300）+ FULLA 研究（mask fulla_v1，median≥800） |
| C7 | X2 前完整重叠 | vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–34；COUNT 轻量不替；leaf26-like J=1.0 不得当硬拒或正交已证 |
| C8 | forbid | `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5`+二十票；禁复用叶25/27/30–34 `.ok`；禁 `--arch-ok-path`；禁 RESTORED |
| C9 | rss+peak_proof | rss=1500 禁抬；peak_proof REQUIRED |
| C10 | 另队 | `0087c928`/叶28/29 不夹带 |
| C11 | overlay≠叶26 完整残差 α | 交付=mask-only overlay 叠主干；禁叶26 完整 α / moneyflow / 行业 ETF 持仓主输入；raw 同幅持续披露 |
| C12 | APPROX≠X2 ACCEPT | COUNT gate_pass（APPROX）≠ X2 ACCEPT / Book-Smoke / 升纸面 |
| C13 | decay KEEP | 近端=252d（≥126 才出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc` / 叶34 `178e90e9`） |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1` |
| 公式 | `pressure_raw=Σ w×flow_est_proxy` → top_q=0.20 by `|pressure|` → **mask-only** |
| C3 | 方案 A：次月首个交易日 09:00 Asia/Shanghai |
| C4 | **mask-only PRIMARY** |
| 再平衡 / X2 窗 / 成本 | 20 / 2024-06-03→2026-10-09 / 30bp |
| PRIMARY / 研究 | HI_LIQ_V1.1 / FULLA_V1 |
| 边界 | ≠叶26 完整残差 α；≠叶8a 交易 ETF；≠moneyflow 主轴 |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |

## 盘证（本拍后）

| 项 | 值 |
|---|---|
| `research/leaf35*` | **ABSENT** |
| live `.ok`（ai_factory 非 consumed/superseded） | **0** |
| QUIET `output/loop/RESEARCH_QUIET.lock` | **ABSENT** |
| 叶33 正式 | **`afbbe7e7` UNCHANGED** |
| 叶32 HOLD / 叶34 HOLD CLOSED | **不回撤**（`45dd87dc` / `178e90e9`） |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗（C2 正式 `research/leaf35*`）。≠X2 ACCEPT。勿报 Leo。

live=false · EXECUTED=false · ok_requested=false.
