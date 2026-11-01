# 叶32 Margin Net Flow Resid X2 selfcheck_v1 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T05:02:32-04:00（America/New_York；墙钟 2026-10-27 05:02 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false · **EXECUTED=false**
- **优先级**：主令 04:57 ET 派单（Alpha 闸 ACCEPT `1aa432a5` → 只起草 selfcheck）

## 一句话

叶32 Margin Net Flow Resid alpha 已 **CONSUMED_PASS**（peak_kb=**929300**≪1500；alpha sha8 **`13eee6fd`**；overlap **`a643d71a`**；meta **`e510f346`**；Arch **`a1a5e35a`**；AI RUN **`f3e8f991`**；RUNNING_ACK **`3c4d0124`**；`.ok` **`02426b73`** 已归档）。Alpha 闸 **`1aa432a5` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT**。**CONSUMED/ACCEPT 不解阻 X2**。本票 = 钉既有冻结 alpha → §3.3 评价权重 → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` sha8 **`dcf6b559`**（派生自叶31 `e1fe578c`）。rss≤1500 禁抬 + peak_proof。须 **新** Arch `.ok` + 主排新窗。盯 **decay KEEP**（叶30/31 均 DECAY_DOWNGRADE HOLD；decay 三闸是关键路径）。`0087c928` **另队不夹带**。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| alpha | **`13eee6fd`** · 全长 `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` |
| meta | **`e510f346`** · 全长 `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` |
| overlap | **`a643d71a`** · 全长 `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` |
| 构建脚本（UNCHANGED） | **`4e0f3c00`**（禁改字节） |
| 本票新脚本（CHANGED） | **`dcf6b559`** · 全长 `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` |
| 模板（只读 UNCHANGED） | **`e1fe578c`**（`leaf31_amihud_impact_slow_x2_selfcheck_v1.py`） |
| 叶30 模板（只读） | **`797724d4`**（勿改） |
| Arch CONSUMED | **`a1a5e35a`** |
| Alpha 闸 ACCEPT（仅构建） | **`1aa432a5`** |
| AI RUN_RECEIPT | **`f3e8f991`** |
| RUNNING_ACK | **`3c4d0124`** |
| FROZEN | **`6b8de5e9`** |
| CONSUMED `.ok`（禁 RESTORED 七票） | **`02426b73`** + **`4bb141c9`** + `fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` |
| mechanism | `g1g5_ashare_margin_net_flow_resid_v1`（构建侧 W/rebal 20/20；selfcheck 组合评价 0.04/20/5） |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED（ru_maxrss） |
| PRIMARY | HILIQ × x2 end `20261009` |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok` |
| 叶30 KEEP 另队 | **`0087c928`** 不夹带 |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` |
| **动作** | (1) 硬钉 alpha+meta+overlap sha；(2) 由冻结 alpha 生成 `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf32_margin_flow/selfcheck_v1.json` |
| **权重规则** | 每 5 日重算；每名 ≤4%、≤20 名；HILIQ 行业帽 0.25（SW L1 asof）；余额 510300.SH；硬排除 600519/002371（组合评价侧沿用叶31/`leaf_selfcheck_common` 口径） |
| **不改** | 构建脚本 `4e0f3c00` / 叶31 模板 `e1fe578c` / 叶30 `797724d4` / `leaf_selfcheck_common.py` / rss 1500 / 钉盘 alpha |
| **Gate** | `leaf_selfcheck_common.evaluate` → **decay KEEP 三闸**（KEEP/DOWNGRADE）+ portfolio A/B/current；盯 decay KEEP |
| **CLI** | 实现 `--universe/--window/--alpha-path/--meta-path/--dry-compile-only/--execute`；**禁** `--arch-ok-path`（未实现；流程门外挂） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面
- 复跑 alpha 构建 / RESTORED **`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`**（及 forbid 其余项）
- 改 `4e0f3c00` / `e1fe578c` / `797724d4` 字节；git commit；本回合实跑 evaluate（**SELFCHECK_EXECUTED=false**）
- 夹带 `0087c928`；报 Leo

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审不签**（COVER+CMD+DIFF+脚本）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED 七票；拟名见上）。
3. 实跑单次；失败/ABORT → 停+上报；≠X2 ACCEPT；盯 decay KEEP。

## 盘证

| 件 | 路径 |
|---|---|
| COVER | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` |

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false · leo_notify=false
