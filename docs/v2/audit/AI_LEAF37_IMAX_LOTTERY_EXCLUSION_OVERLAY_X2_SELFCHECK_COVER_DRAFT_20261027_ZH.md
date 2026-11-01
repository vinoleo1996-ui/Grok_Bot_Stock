# 叶37 IMAX/隔夜彩票剔除 Overlay X2 selfcheck_v1 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T18:58:01-04:00（America/New_York；墙钟 2026-10-27 18:58 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **SELFCHECK_EXECUTED=false**
- **优先级**：主令 ~18:51 ET 派单（B1_LOWMEM X2 CONSUMED_PASS `c0a6b5ae` → 只起草 selfcheck 另票）

## 一句话

叶37 IMAX Lottery Exclusion Overlay B1_LOWMEM X2 已 **CONSUMED_PASS**（mask sha8 **`2503a41e`**；overlap **`8177578f`**；meta **`e9e9aa1d`**；Arch **`c0a6b5ae`**；AI RUN **`c6d8b1ce`**；RUNNING_ACK **`08652c66`**；SIGNED **`7b3bd298`**；审 **`b403a7e5`**；VOID **`998171e1`**；consumed `.ok` **`b5be1164`** 已归档 ABSENT；QUIET 已 lift）。**CONSUMED 不解阻 X2 ACCEPT**。本票 = 钉既有冻结 exclusion_mask → **mask-only 叠加主干**（capacity_adv × mask；≠ α TopN）→ `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 B1/基盘；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`015e6f06`**（派生自叶34 `d210efba`；模板只读）。C3=**B** IMAX_proxy；b1_lowmem=**true**；coverage_median=**2816.5**≥300；rss≤1500 禁抬 + peak_proof。须 **新** Arch `.ok` + 主排新窗。闸门书面冻结于 FROZEN **`c5927f1b`** / PIN **`e01be34c`**（先于读数）；**KEEP 不解阻 X2 ACCEPT**。`0087c928`/叶28/29 **另队不夹带**；叶33 **`afbbe7e7`** / 叶35 **`434ff42c`** / 叶34 **`482009dc` UNCHANGED**；叶36 HOLD **不复开**；C11≠叶24 `g1g5_ashare_imax_intraday_v1`。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| exclusion_mask | **`2503a41e`** · 全长 `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` |
| meta | **`e9e9aa1d`** · 全长 `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` |
| overlap | **`8177578f`** · 全长 `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` |
| OUT | `output/ai_factory/_leaf37_imax_lottery/20261027_183719/` |
| B1 构建脚本（UNCHANGED） | **`32605aca`**（禁改字节） |
| 基盘脚本（UNCHANGED ban_as_live） | **`108aba8f`**（禁改/禁跑） |
| 本票新脚本（CHANGED） | **`015e6f06`** · 全长 `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` |
| 模板叶34（只读 UNCHANGED） | **`d210efba`** |
| 模板叶32（只读 UNCHANGED） | **`dcf6b559`** |
| `leaf_selfcheck_common.py`（只读） | **`218b61cf`** |
| Arch CONSUMED_PASS | **`c0a6b5ae`** |
| consumed `.ok`（禁 RESTORED） | **`b5be1164`**（ABSENT） |
| VOID `.ok`（禁 RESTORED） | **`4096d401`** |
| AI RUN_RECEIPT | **`c6d8b1ce`** |
| RUNNING_ACK | **`08652c66`** |
| SIGNED | **`7b3bd298`** |
| 审 | **`b403a7e5`** |
| VOID 回执 | **`998171e1`** |
| FROZEN | **`c5927f1b`** |
| PIN（C3=B） | **`e01be34c`** |
| mechanism | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| C3 | **B** IMAX_proxy；full_residual_e_id=**false** |
| PRIMARY 交付 | **mask-only** top_q=**0.20**（soft-penalty 非 PRIMARY） |
| b1_lowmem | **true** |
| coverage_median / gate | **2816.5** / ≥**300** PASS |
| peak_kb（build） | **1107536** |
| CAP_ADV | `output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`（对齐 `leaf_selfcheck_common.CAP_ADV`） |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED（ru_maxrss） |
| PRIMARY | HILIQ × x2 end `20261009`（禁静默 FULLA） |
| forbid | 首项 **`b5be1164`**+**`4096d401`**+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+…（n=**32**） |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| 叶33/35/34（UNCHANGED） | **`afbbe7e7`** / **`434ff42c`** / **`482009dc`** |
| 叶32 HOLD / 叶36 HOLD | **`45dd87dc`** 不回撤 / **不复开** |
| 叶30 KEEP 另队 | **`0087c928`** 不夹带 |

## 闸门书面冻结（先于读数 · FROZEN `c5927f1b` · 对齐叶34）

1. **PRIMARY**=HI_LIQ **mask-only** top_q=**0.20** 叠加主干（capacity_adv）。
2. **判定**=叶自身主干级 **或**（ρ_excess vs capacity_adv **<0.5** **且** 60万/100万叠加均优于主干）。
3. **并列报** Gate A / Gate B / 当前新口径（current）— 来自 `leaf_selfcheck_common.evaluate`。
4. **decay KEEP** 三闸合取：近端 **252d**；`latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`。
5. **KEEP 不解阻 X2 ACCEPT**（叶32 HOLD **`45dd87dc`**；叶36 HOLD 不复开）。

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` |
| **动作** | (1) 硬钉 mask+meta+overlap sha；(2) `build_eval_weights_from_mask` → `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf37_imax_lottery/selfcheck_v1.json` |
| **权重规则** | 按日 capacity_adv × exclusion_mask；**mask=0→权重置 0**；mask 缺失不进有效叠加、不填假 0；硬排除 600519/002371；余额 510300.SH；**≠ α TopN** |
| **不改** | B1 `32605aca` / 基盘 `108aba8f` / 叶34 模板 `d210efba` / 叶32 `dcf6b559` / `leaf_selfcheck_common.py` / rss 1500 / 钉盘 mask |
| **Gate** | 上节书面冻结 + `evaluate` 产出 A/B/current + decay KEEP |
| **CLI** | `--universe/--window/--mask-path/--meta-path/--dry-compile-only/--execute`；**禁** `--arch-ok-path`（未实现；流程门外挂） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面
- 复跑 B1/基盘 / RESTORED **`b5be1164`/`4096d401`/`eb70eef4`/`00eec671`/`10927bd9`/`25ae4572`/`178e90e9`/`c1b71e64`** + 旧票（n=32）
- 改 `32605aca` / `108aba8f` / `d210efba` / `dcf6b559` / `leaf_selfcheck_common.py` 字节；git commit；本回合实跑 evaluate（**SELFCHECK_EXECUTED=false**）
- 夹带 `0087c928`/叶28/29；回撤叶33/35/34；复开叶36；冒充叶24 `g1g5_ashare_imax_intraday_v1`；报 Leo

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审不签**（COVER+CMD+DIFF+脚本）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑单次；失败/ABORT → 停+上报；≠X2 ACCEPT；KEEP 不解阻 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` |

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false · leo_notify=false
