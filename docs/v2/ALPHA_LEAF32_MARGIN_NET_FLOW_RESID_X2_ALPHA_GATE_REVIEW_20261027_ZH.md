# 叶32 Margin Net Flow Resid · Alpha 闸门审（研究级 α 构建过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 04:54 ET**（America/New_York） |
| **主裁决 VERDICT** | **ACCEPT**（研究级 α 构建过程过闸） |
| 语义分层 | 构建过程 **ACCEPT**；收益过程指标（IC/ICIR/WF）**ABSENT** → **不得宣称 IC 过闸**；组合闸（门A/B·GATE_V3）**未交数 → 不裁定** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠Book-Smoke** / **≠门B·GATE_V3 PASS/FAIL** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`a1a5e35a`**（`.ok` 归档 **`02426b73`**；禁 RESTORED） |
| out | `output/ai_factory/_leaf32_margin_flow/20261027_042805/` |
| 对齐口径 | 同叶31 构建闸 `a476567d` / 叶30 构建闸 `1c992d62`（研究级构建 ACCEPT） |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **ACCEPT** | 钉全 MATCH + FROZEN 机制对齐 + coverage 过闸 + 无 Jaccard 硬拒 + Arch CONSUMED_PASS + x2_accept=false |
| 钉对齐 | **MATCH** | alpha/overlap/run_meta/脚本/AI/Arch/SIGNED/审/FROZEN/archived `.ok`/QUIET-lift 前 8 字符全 MATCH；live `.ok`=0；QUIET ABSENT |
| PIT / 残差·正交 | **对齐 FROZEN §1–§3** | flow W=20；rebal=20；α=−rank(flow_resid)；SW L1 demean + OLS(logmv T−1, mom20, vol20, logADV20)；mechanism_tag 钉住 |
| 覆盖 | **PASS** | coverage_median=**2454.0** ≥300；min=1232 / max=2847；n_rebal=**30**；gate_pass=true |
| 正交/重叠 | **无硬拒** | ρ19≈−0.016；ρ25≈0.053；ρ27≈−0.038；ρ30≈−0.016；ρ31≈0.028；ρ_margin_delta≈−0.159；j20_max≈0.026；Jaccard≥0.7 **未触发**；ρ>0.5 强度过滤 **未触发**；PIN_GAP=0 |
| IC/ICIR/WF | **ABSENT** | 包内无正式 IC/ICIR/walk-forward 数字；脚本明示不算收益选号；**本审未开算** |
| 组合闸对照 | **不裁定** | 无 Book-Smoke / 无组合 CAGR·MDD·Calmar → 不得判门A/B 或 GATE_V3；≠Book-Smoke |
| parquet 轻核 | **OK** | 列 `trade_date,ts_code,alpha`；2024-06-03→2026-10-09；n=1234632；null/zero=0；−rank 值域合理；peak_kb=929300≪1500 |

**主裁决词单列**：**ACCEPT** = 研究级 α **构建过程**过闸（RESEARCH_ACCEPT 口径，对齐叶31 `a476567d`）。**不是** X2 ACCEPT，**不是** 收益过程过闸，**不是** 组合门过闸。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `a1a5e35a` | `a1a5e35af07e297577aef47311e2f79c6c2f04ecdef3a5dd60fb7518a0b3f31e` | **MATCH** |
| archived `.ok` 内容 | `02426b73` | `02426b73d253237127772bd0023c52938ad58bdb76204feeddac87ceb385d736`（路径 `_consumed/…02426b73.CONSUMED_PASS.20261027T0451ET.ok`） | **MATCH** |
| QUIET lift 原 | `6d62911f` | `6d62911f53c0ab7820be756dbbbddae3fa7c78f623d58cdf377ec64edd3505a5`（`_lifted/…PASS_LIFTED_20261027T0451ET.lock`） | **MATCH** |
| alpha parquet | `13eee6fd` | `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` | **MATCH** |
| overlap JSON | `a643d71a` | `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` | **MATCH** |
| run_meta.json | `e510f346` | `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` | **MATCH** |
| AI RUN_RECEIPT | `f3e8f991` | `f3e8f9910f76fb70aaa9653a67f2fc026853917dd0b077c30be181c4527dbf89` | **MATCH** |
| 脚本 build | `4e0f3c00` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH** |
| Arch SIGNED | `39baa28e` | `39baa28e8c50a889987131aee334ea652f73c3e08b75ae4d1d0136032e927d21` | **MATCH** |
| Arch 脚本审 | `814939b8` | `814939b8bb1c911e48e3425953ee3e92826a0d0f0c00d7a0801503e8560b372a` | **MATCH** |
| FROZEN PREREG | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42`（meta `frozen_sha8` 同钉） | **MATCH** |
| Arch FROZEN 审 | `7c0d864f` | `7c0d864f7d544e8bd16817c74fa4dd7e35c9609c5066eedc4ee15f71765b5d84`（meta 钉） | **MATCH** |

附加硬钉（自 run_meta / 盘面）：

| 项 | 值 | 判定 |
|---|---|---|
| x2_accept / live / promotion_approved / ok_requested | **false** / false / false / false | **PASS** |
| peak_kb / rss_limit_mb | **929300** / 1500（≈60.5% 硬帽；≪1500） | **PASS** |
| live `.ok` 计数 | **0**（`output/ai_factory/ARCH_RUN_AUTH_LEAF32*` ABSENT；仅 `_consumed`） | **PASS** |
| QUIET | **ABSENT**（原 `6d62911f` 已 lift → `_lifted/…PASS_LIFTED_20261027T0451ET.lock`；`output/loop/RESEARCH_QUIET*` live ABSENT） | **PASS** |
| 禁 RESTORED | `02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` 仅在 `_consumed`；**未 RESTORED** | **PASS** |
| X2 窗 | `2024-06-03`→`2026-10-09`；universe=HILIQ；window=x2 | 结构钉住 |
| mechanism_tag | `g1g5_ashare_margin_net_flow_resid_v1` | MATCH FROZEN |
| α / W / rebal / ic_sign_expected | −rank(flow_resid) / 20 / 20 / positive | MATCH FROZEN §1–§2 |
| pin_gaps | `[]`；n_pin_gaps=0；overlap any_required_pin_gap=false | **PASS** |
| rc（AI 回执） | **0**；DONE；无 Exit 94/95 | **PASS** |
| 叶31 HOLD `7ef5aa11` / 构建 `a476567d` | **不回撤**；本审未打开/未混办 | **PASS** |
| 叶30 HOLD `f00536b9` / 构建 `1c992d62` | **不回撤**；`0087c928` 另队；本审未混办 | **PASS** |

## 2. PIT / 残差·正交（对照 FROZEN §1–§3；读脚本+meta，不编造）

| FROZEN 钉 | 脚本/meta 实现 | 判定 |
|---|---|---|
| flow_raw = mean_W((rzmre−rzche)/float_mktcap T−1)；W=20；有效日≥15 | `FLOW_W=20`；meta `flow_W=20` `flow_min_valid=15`；notes PIT=available_at | **对齐** |
| 再平衡每 20 交易日 | `REBAL_EVERY=20`；meta `rebal_every_td=20`；n_rebal=30 | **对齐** |
| α_raw = −rank(flow_resid) | `ALPHA_SIGN=neg_rank_flow_resid`；禁 flip；meta 同 | **对齐** |
| SW L1 demean | `_residualize_cross_section`：groupby sw demean；缺 SW → PIN_GAP/STOP | **对齐** |
| log 流通市值 OLS（T−1 PIT） | logmv T−1 + OLS；缺 float → PIN_GAP | **对齐** |
| style：mom20 / vol20 / logADV20 | `style_cols_pinned` 全钉；derived_from_daily_bars_W20 | **对齐** |
| IC 期望正；脚本不算收益 | `IC_SIGN_EXPECTED=positive`；注释「NEVER selects sign from returns」；meta notes 同 | **对齐**（故 IC **ABSENT**） |
| Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；含 vs margin_delta | overlap schema + `any_jaccard_hard_reject=false`；PIN_GAP=0 | **对齐**；本次均 false |
| 禁 Amihud / on_minus_id / CRR / hk_hold / margin_delta 作主输入 | 脚本 Ban 注释 + meta notes；主轴两融净流入残差 | **对齐** |
| PRIMARY=HILIQ；FULLA 不得静默升主 | meta `primary_universe=HILIQ`；FULLA 作 PRIMARY → STOP | **对齐** |

PIT 要点：两融 detail available_at；float_mktcap T−1；再平衡日 lazy margin/float/bars；缺 style/logmv/sw/margin → PIN_GAP/drop（非静默零）。本审**未**重跑引擎验证逐票 PIT 轨迹——以脚本契约 + Arch CONSUMED_PASS + meta 为据。

## 3. 覆盖

| 指标 | 值 |
|---|---|
| coverage_median | **2454.0** |
| coverage_gate / gate_pass | **300** / **true** |
| coverage min / max | **1232**（2024-07-30）/ **2847**（2025-09-22） |
| n_rebal | **30** |
| n_daily_rows | **1234632** |
| n_month_chunks_written | 29 |

闸：median≥300 → **PASS**。全序列 rebal n 均 ≥1232 ≫300；不构成拒收。

## 4. 正交 / 重叠（读 overlap 全表）

样本日 6：`2024-06-03` … `2026-10-09`；schema=`leaf32_overlap_vs_leaf19_25_27_30_31_margin_delta`；live=false；`any_jaccard_hard_reject=false`；`pin_gaps=[]`。

| 对照 | ρ min–max（mean） | j20_max | Jaccard hard reject | strength ρ>0.5 |
|---|---|---|---|---|
| vs 叶19 | **−0.063–0.071**（≈**−0.016**；6/6） | **≈0.026** | **无** | **无** |
| vs 叶25 | **0.009–0.122**（≈**0.053**；4/6 有值；2026-04-27/2026-10-09 ρ=null） | **0.0** | **无** | **无** |
| vs 叶27 | **−0.171–0.034**（≈**−0.038**；6/6） | **0.0** | **无** | **无** |
| vs 叶30 | **−0.079–0.018**（≈**−0.016**；6/6） | **0.0** | **无** | **无** |
| vs 叶31 | **−0.063–0.071**（≈**0.028**；6/6） | **0.0** | **无** | **无** |
| vs margin_delta | **−0.432–0.162**（≈**−0.159**；6/6） | **0.0** | **无** | **无** |

对照 FROZEN §4 失效条件：Jaccard≥0.7 近等权 **未触发**；ρ 绝对值均 ≪0.5（margin_delta 最大 |ρ|≈0.432）→ 强度过滤未亮；相对叶19/25/27/30/31 及历史 margin_delta **低相关**，正交披露健康。叶25 两日 ρ=null 仅披露，不构成硬拒。PIN_GAP=0。

## 5. IC / ICIR / walk-forward

| 项 | 状态 |
|---|---|
| 包内文件 | 仅 alpha / overlap / run_meta — **无** IC 表、无 WF 折、无收益序列 |
| 脚本 | 明示 **NEVER selects sign from returns**；不算收益 IC |
| 本审 | **禁止**自开实数 IC（需独立 `.ok`）；**未开算**；**不伪造** |

→ **收益过程指标 ABSENT**。分层结论：构建过程可 ACCEPT；**不得**在对外口径写「IC 过闸 / ICIR 达标 / WF 稳健」。下一步须 **另窗** IC/WF/selfcheck 评估（独立授权），非本审范围；Alpha **不自开**。

## 6. 组合闸对照（新口径 A/B 与现行 GATE_V3）— 过程结论 only

对照 `docs/v2/ALPHA_GATE_AB_PREREG_20261014_ZH.md` 与 `docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

- 门A/门B / 现行门 / GATE_V3 均要求组合级 CAGR·MDD·Calmar（及 Book-Smoke X2 终判）。
- **本包无** Book-Smoke 产物、无组合净值、无 CAGR/MDD/Calmar、无 selfcheck。
- 过程结论：**组合闸未交数 → 不裁定 PASS/FAIL**；**≠Book-Smoke**；Alpha **不自开烟、不自申 X2 ACCEPT**。
- run_meta `x2_accept=false` 与本审一致。

叶验收顺序提醒：HC→单叶研究 ACCEPT（本审此层）→CMC→衰减门→GATE_V3 本地→Eng Book-Smoke；后续步 **另排**。叶31 selfcheck HOLD/`7ef5aa11`（decay=DECAY_DOWNGRADE）与叶30 HOLD/`f00536b9` **不回撤**本叶构建 ACCEPT，亦**不**借本票解阻叶31/30。

## 7. parquet 轻核（只读；未跑回测）

| 项 | 值 |
|---|---|
| 列 | `trade_date`, `ts_code`, `alpha` |
| 行数 | 1234632（= meta n_daily_rows） |
| 日期范围 | 2024-06-03 → 2026-10-09；n_unique_dates=570 |
| n_unique_codes | 3555 |
| null_frac / zero_frac / all_zero | 0 / 0 / False |
| alpha 值域 | min=**−1.0** / max≈**−0.00035** / mean≈**−0.499** / std≈**0.289**（−rank 百分位 → 值域落在 (−1,0]；非全零常数；截面残差量级合理） |
| peak_kb（自报） | 929300 |

## 8. 披露边界（硬）

1. **ACCEPT** = 研究级 **α 构建过程**过闸；**≠X2 ACCEPT**（本拍**不解阻**）。
2. **≠Book-Smoke**；**≠门A/门B/GATE_V3** 裁定；**≠selfcheck**。
3. **IC/ICIR/WF ABSENT** → 不得宣称收益过程过闸。
4. **勿升纸面**；`promotion_approved=false`；不改 `FROZEN_CONFIG` / paper；**不改 alpha_labels**。
5. 禁 RESTORED：`02426b73` / `4bb141c9` / `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`；禁抬 rss；禁自开实数回测。
6. Arch 已 CONSUMED_PASS（`a1a5e35a`）；本审不恢复 `.ok`、不签新 `.ok`。
7. 叶31 HOLD/`7ef5aa11` + 构建 `a476567d`、叶30 HOLD/`f00536b9` + 构建 `1c992d62`、`0087c928` 另队；本审未混办、不回撤。
8. **leo_notify=false**；不报 Leo。

## 9. 下一步（可执行）

1. **主**知悉本闸审 ACCEPT（构建过程）；可排 **IC/WF/selfcheck 评估另窗**（独立 `.ok` / 授权；Alpha **不代启**实数）。
2. 组合边际 / 门B·GATE_V3 / Book-Smoke：**等主另排**；Alpha 不自开烟、不自申 X2 ACCEPT；不派 Eng。
3. 衰减 KEEP（FROZEN §7）须在独立评估窗验证；本构建 ACCEPT **不解阻** decay KEEP。
4. 叶31 HOLD/`7ef5aa11` 与叶30 HOLD/`f00536b9` 及 `0087c928` 另队继续；标签仍不动。
5. 对外话术保持分层：**构建 ACCEPT / 收益 HOLD / 组合不裁定**；主裁决词仍以本回执 **ACCEPT** 为准（研究构建契约）。

## 10. 状态动作

- 落盘本回执（本文件）。
- `TEAM ### Alpha`：更新为叶32 构建闸 VERDICT=ACCEPT + 本回执 sha8（恰好 3 行；先 cp 备份 `…bak_alpha_leaf32_build_gate_20261027`）；保留叶31 HOLD/`7ef5aa11`+构建 `a476567d` 与叶30 HOLD/`f00536b9`。
- `alpha_labels`：**不动**。
- ql_bus：`emit('QuantLab Alpha','gate',…)`（若可用）。

live=false；promotion_approved=false；forbid_paper_handoff=true；leo_notify=false。
