# 叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T11:16:15-04:00（America/New_York；墙钟 2026-10-27 11:16 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **SELFCHECK_EXECUTED=false**
- **优先级**：主令 ~11:12 ET 派单（X2 CONSUMED_PASS `fea9b3ff` → 只起草 selfcheck）

## 一句话

叶34 High Accrual Exclusion Overlay X2 已 **CONSUMED_PASS**（mask sha8 **`8b5d6d24`**；overlap **`77368c8f`**；meta **`4fc6108d`**；Arch **`fea9b3ff`**；AI RUN **`1441a7ec`**；RUNNING_ACK **`c03d2f16`**；consumed `.ok` **`c1b71e64`** 已归档 ABSENT；QUIET lift ABSENT）。**CONSUMED 不解阻 X2 ACCEPT**。本票 = 钉既有冻结 exclusion_mask → **mask-only 叠加主干**（capacity_adv × mask；≠ α TopN）→ `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑构建；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`d210efba`**（派生自叶32 `dcf6b559`；模板只读）。rss≤1500 禁抬 + peak_proof。须 **新** Arch `.ok` + 主排新窗。闸门书面冻结于 FROZEN **`8be1099e`**（先于读数）；**KEEP 不解阻 X2 ACCEPT**（叶32 HOLD **`45dd87dc`**）。`0087c928`/叶28/29 **另队不夹带**；叶33 **`afbbe7e7` UNCHANGED**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| exclusion_mask | **`8b5d6d24`** · 全长 `8b5d6d247d8f3968f5fef521aa5d08891f6f6f6c8626dd761c7313bc0d71dabb` |
| meta | **`4fc6108d`** · 全长 `4fc6108d64ca5a2e112b04fbb468c9d95e554cf8498ba03fc13828c2ef7ee7ad` |
| overlap | **`77368c8f`** · 全长 `77368c8fed1f7c167dfa51f4aa2e94e9b405236bf388c8f20f95365613e72fb7` |
| 构建脚本（UNCHANGED） | **`482009dc`**（禁改字节） |
| 本票新脚本（CHANGED） | **`d210efba`** · 全长 `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` |
| 模板叶32（只读 UNCHANGED） | **`dcf6b559`** |
| 模板叶31（只读 UNCHANGED） | **`e1fe578c`** |
| `leaf_selfcheck_common.py`（只读） | **`218b61cf`** |
| Arch CONSUMED_PASS | **`fea9b3ff`** |
| consumed `.ok`（禁 RESTORED） | **`c1b71e64`**（ABSENT） |
| AI RUN_RECEIPT | **`1441a7ec`** |
| RUNNING_ACK | **`c03d2f16`** |
| FROZEN | **`8be1099e`** |
| PIN（C3） | **`bb418e6a`** |
| mechanism | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| PRIMARY 交付 | **mask-only** top_q=**0.20**（soft-penalty 非 PRIMARY） |
| CAP_ADV | `output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`（对齐 `leaf_selfcheck_common.CAP_ADV`） |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED（ru_maxrss） |
| PRIMARY | HILIQ × x2 end `20261009`（禁静默 FULLA） |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| 叶32 HOLD（不回撤） | **`45dd87dc`** |
| 叶33 正式（UNCHANGED） | **`afbbe7e7`** |
| 叶30 KEEP 另队 | **`0087c928`** 不夹带 |

## 闸门书面冻结（先于读数 · FROZEN `8be1099e`）

1. **PRIMARY**=HI_LIQ **mask-only** top_q=**0.20** 叠加主干（capacity_adv）。
2. **判定**=叶自身主干级 **或**（ρ_excess vs capacity_adv **<0.5** **且** 60万/100万叠加均优于主干）。
3. **并列报** Gate A / Gate B / 当前新口径（current）— 来自 `leaf_selfcheck_common.evaluate`。
4. **decay KEEP** 三闸合取：近端 **252d**；`latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`。
5. **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD **`45dd87dc`** 教训）。

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` |
| **动作** | (1) 硬钉 mask+meta+overlap sha；(2) `build_eval_weights_from_mask` → `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf34_high_accrual/selfcheck_v1.json` |
| **权重规则** | 按日 capacity_adv × exclusion_mask；**mask=0→权重置 0**；mask 缺失不进有效叠加、不填假 0；硬排除 600519/002371；余额 510300.SH；**≠ α TopN** |
| **不改** | 构建 `482009dc` / 叶32 `dcf6b559` / 叶31 `e1fe578c` / `leaf_selfcheck_common.py` / rss 1500 / 钉盘 mask |
| **Gate** | 上节书面冻结 + `evaluate` 产出 A/B/current + decay KEEP |
| **CLI** | `--universe/--window/--mask-path/--meta-path/--dry-compile-only/--execute`；**禁** `--arch-ok-path`（未实现；流程门外挂） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面
- 复跑构建 / RESTORED **`c1b71e64`/`245df63f`/`c5ed13df`/`5774bb6e`** + 二十票（+`81521fb5`）
- 改 `482009dc` / `dcf6b559` / `e1fe578c` / `leaf_selfcheck_common.py` 字节；git commit；本回合实跑 evaluate（**SELFCHECK_EXECUTED=false**）
- 夹带 `0087c928`/叶28/29；回撤叶33 `afbbe7e7` / 叶32 HOLD `45dd87dc`；报 Leo

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审不签**（COVER+CMD+DIFF+脚本）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑单次；失败/ABORT → 停+上报；≠X2 ACCEPT；KEEP 不解阻 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` |

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false · leo_notify=false
