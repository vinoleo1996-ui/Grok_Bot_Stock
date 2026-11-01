# 叶31 Amihud Impact Slow X2 selfcheck_v1 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T02:59:43-04:00（America/New_York；墙钟 2026-10-27 02:59 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 02:55 ET 派单（Alpha 闸 ACCEPT `a476567d` → 只起草 selfcheck）

## 一句话

叶31 Amihud Impact Slow alpha 已 **CONSUMED_PASS**（peak_kb=**847092**≪1500；alpha sha8 **`d4ceb78b`**；overlap **`8396f211`**；meta **`696ab1cc`**；Arch **`7bd6f33a`**；AI RUN **`49d6641c`**；`.ok` **`fdbaa512`** 已归档）。Alpha 闸 **`a476567d` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT**。**CONSUMED/ACCEPT 不解阻 X2**。本票 = 钉既有冻结 alpha → §3.3 评价权重 → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` sha8 **`e1fe578c`**（派生自叶30 `797724d4`）。rss≤1500 禁抬 + peak_proof。须 **新** Arch `.ok` + 主排新窗。`0087c928` **另队不夹带**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| alpha | **`d4ceb78b`** · 全长 `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` |
| meta | **`696ab1cc`** · 全长 `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` |
| overlap | **`8396f211`** · 全长 `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` |
| 构建脚本（UNCHANGED） | **`08f37fd2`**（禁改字节） |
| 本票新脚本（CHANGED） | **`e1fe578c`** · 全长 `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` |
| 模板（只读 UNCHANGED） | **`797724d4`**（`leaf30_crr_x2_selfcheck_v1.py`） |
| Arch CONSUMED | **`7bd6f33a`** |
| Alpha 闸 ACCEPT（仅构建） | **`a476567d`** |
| AI RUN_RECEIPT | **`49d6641c`** |
| CONSUMED `.ok`（禁 RESTORED） | **`fdbaa512`**（另禁 `aa25e989`/`7e239487`/`5af20222`/`5ae077fa`） |
| mechanism | `g1g5_ashare_amihud_impact_slow_v1`（构建侧 W/rebal 20/20） |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009` |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| 叶30 KEEP 另队 | **`0087c928`** 不夹带 |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` |
| **动作** | (1) 硬钉 alpha+meta+overlap sha；(2) 由冻结 alpha 生成 `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf31_amihud/selfcheck_v1.json` |
| **权重规则** | 每 5 日重算；每名 ≤4%、≤20 名；HILIQ 行业帽 0.25（SW L1 asof）；余额 510300.SH；硬排除 600519/002371 |
| **不改** | 构建脚本 `08f37fd2` / 叶30 模板 `797724d4` / `leaf_selfcheck_common.py` / rss 1500 / 钉盘 alpha |
| **Gate** | `leaf_selfcheck_common.evaluate` → decay KEEP/DOWNGRADE + portfolio A/B/current |
| **CLI** | 实现 `--universe/--window/--alpha-path/--meta-path/--dry-compile-only/--execute`；**禁** `--arch-ok-path`（未实现；流程门外挂） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面
- 复跑 alpha 构建 / RESTORED **`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**（及 forbid 其余项）
- 改 `08f37fd2` / `797724d4` 字节；git commit；本回合实跑 evaluate（**SELFCHECK_EXECUTED=false**）
- 夹带 `0087c928`；报 Leo

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审不签**（COVER+CMD+DIFF+脚本）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑单次；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` |

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false · leo_notify=false
