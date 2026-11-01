# 叶31 Amihud Impact Slow · Alpha 闸门审（研究级 α 构建过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 02:53 ET**（America/New_York） |
| **主裁决 VERDICT** | **ACCEPT**（研究级 α 构建过程过闸） |
| 语义分层 | 构建过程 **ACCEPT**；收益过程指标（IC/ICIR/WF）**ABSENT** → **不得宣称 IC 过闸**；组合闸（门A/B·GATE_V3）**未交数 → 不裁定** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠Book-Smoke** / **≠门B·GATE_V3 PASS/FAIL** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`7bd6f33a`**（`.ok` 归档 **`fdbaa512`**；禁 RESTORED） |
| out | `output/ai_factory/_leaf31_amihud/20261027_024204/` |
| 对齐口径 | 同叶30 构建闸 `1c992d62`（研究级构建 ACCEPT） |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **ACCEPT** | 钉全 MATCH + FROZEN 机制对齐 + coverage 过闸 + 无 Jaccard 硬拒 + Arch CONSUMED_PASS + x2_accept=false |
| 钉对齐 | **MATCH** | alpha/overlap/run_meta/脚本/AI/Arch/FROZEN/archived `.ok` 前 8 字符全 MATCH；live `.ok`=0；QUIET ABSENT |
| PIT / 残差·正交 | **对齐 FROZEN §1–§3** | Amihud W=20；rebal=20；α=−rank(impact_resid)；SW L1 demean + OLS(logmv T−1, mom20, vol20, logADV20)；mechanism_tag 钉住 |
| 覆盖 | **PASS** | coverage_median=**3146.0** ≥300；min=1450 / max=3828；n_rebal=**30**；gate_pass=true |
| 正交/重叠 | **无硬拒** | ρ19≈−0.021；ρ25≈−0.041；ρ27≈−0.057；ρ30≈0.008；j20_max≈0.026；Jaccard≥0.7 **未触发**；ρ>0.5 强度过滤 **未触发** |
| IC/ICIR/WF | **ABSENT** | 包内无正式 IC/ICIR/walk-forward 数字；脚本明示不算收益选号；**本审未开算** |
| 组合闸对照 | **不裁定** | 无 Book-Smoke / 无组合 CAGR·MDD·Calmar → 不得判门A/B 或 GATE_V3；≠Book-Smoke |
| parquet 轻核 | **OK** | 列 `trade_date,ts_code,alpha`；2024-06-03→2026-10-09；n=1579217；null/zero=0；非全零；peak_kb=847092≪1500 |

**主裁决词单列**：**ACCEPT** = 研究级 α **构建过程**过闸（RESEARCH_ACCEPT 口径，对齐叶30 `1c992d62`）。**不是** X2 ACCEPT，**不是** 收益过程过闸，**不是** 组合门过闸。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `7bd6f33a` | `7bd6f33ae302f15cf3b3803497ee20e8bba0f31beab1b3b8c6ee8be0d5284e66` | **MATCH** |
| archived `.ok` 内容 | `fdbaa512` | `fdbaa512fa8da9e6b5256c30f397cd5a3d2bd2c1fbd1a5a295af873ea7271d81`（路径 `_consumed/…fdbaa512.CONSUMED_PASS.20261027T0249ET.ok`） | **MATCH** |
| alpha parquet | `d4ceb78b` | `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` | **MATCH** |
| overlap JSON | `8396f211` | `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` | **MATCH** |
| run_meta.json | `696ab1cc` | `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` | **MATCH** |
| AI RUN_RECEIPT | `49d6641c` | `49d6641cb121d01aea04cadc95392fd99e36559474c5ef4d1908e9ccd38e1e4d` | **MATCH** |
| 脚本 build | `08f37fd2` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **MATCH** |
| FROZEN PREREG | `bcbec955` | `bcbec955937bd1d5c972cb81a9ba78e944fe14ccd2e9bf11fdbb874ced8aece4`（meta `frozen_sha8` 同钉） | **MATCH** |
| Arch FROZEN 审 | `7a6a1e1a` | `7a6a1e1adb6bfb71cd128fe08e71c16c763c59187dd4e1d4bb40abc6c2adc639` | **MATCH** |
| Arch who_pays 审 | `50cbef3c` | `50cbef3c9ff4e7824689f53497553b3e4513b8ca6f87c2532d2f47abc59a3149` | **MATCH** |

附加硬钉（自 run_meta / 盘面）：

| 项 | 值 | 判定 |
|---|---|---|
| x2_accept / live / promotion_approved / ok_requested | **false** / false / false / false | **PASS** |
| peak_kb / rss_limit_mb | **847092** / 1500（≈55.1% 硬帽；≪1500） | **PASS** |
| live `.ok` 计数 | **0**（`ARCH_RUN_AUTH_LEAF31*` ABSENT） | **PASS** |
| QUIET | **ABSENT**（原 `11cfe000` 已 lift → `_lifted/…PASS_LIFTED_20261027T0249ET.lock`） | **PASS** |
| 禁 RESTORED | `fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa` 仅在 `_consumed`；**未 RESTORED** | **PASS** |
| X2 窗 | `2024-06-03`→`2026-10-09`；universe=HILIQ；window=x2 | 结构钉住 |
| mechanism_tag | `g1g5_ashare_amihud_impact_slow_v1` | MATCH FROZEN |
| α / W / rebal / ic_sign_expected | −rank / 20 / 20 / positive | MATCH FROZEN §1–§2 |
| pin_gaps | `[]`；n_pin_gaps=0 | **PASS** |
| rc（AI 回执） | **0**；DONE；无 Exit 94/95 | **PASS** |
| 叶30 KEEP `0087c928` | meta 明示 **另队**；本审**未打开/未混办** | **PASS** |

## 2. PIT / 残差·正交（对照 FROZEN §1–§3；读脚本+meta，不编造）

| FROZEN 钉 | 脚本/meta 实现 | 判定 |
|---|---|---|
| Amihud_raw = mean_W(\|r\|/amount)；W=20；有效日≥15 | `AMIHUD_W=20`；meta `amihud_W=20` `amihud_min_valid=15` | **对齐** |
| 再平衡每 20 交易日 | `REBAL_EVERY=20`；meta `rebal_every_td=20`；n_rebal=30 | **对齐** |
| α_raw = −rank(impact_resid) | `ALPHA_SIGN=neg_rank_impact_resid`；`rnk = pct_rank(impact_resid)` → α=−rnk；禁 flip | **对齐** |
| SW L1 demean | `_residualize_cross_section`：groupby sw demean；缺 SW → PIN_GAP/STOP | **对齐** |
| log 流通市值 OLS（T−1 PIT） | `_load_logmv_t1` + OLS 列 `logmv` | **对齐** |
| style：mom20 / vol20 / logADV20 | `STYLE_COLS_PINNED`；meta `style_cols_pinned` 全钉；缺列 drop 不静默填 0 | **对齐** |
| IC 期望正；脚本不算收益 | `IC_SIGN_EXPECTED=positive`；注释「NEVER selects sign from returns」；meta notes 同 | **对齐**（故 IC **ABSENT**） |
| Jaccard≥0.7 硬拒；ρ>0.5 强度过滤 | overlap schema note + `jaccard_hard_reject_*` / `strength_filter_*`；`any_jaccard_hard_reject=false` | **对齐**；本次均 false |
| 禁会计 / on_minus_id 主输入 | 脚本 Ban 注释 + meta notes；主轴价量冲击 | **对齐** |
| PRIMARY=HILIQ；FULLA 不得静默升主 | meta `primary_universe=HILIQ`；FULLA 作 PRIMARY → STOP | **对齐** |

PIT 要点：amount 单位钉 `tushare_daily_thousand_CNY`×1000；logmv T−1；再平衡日 lazy bars；缺 style/logmv/sw → drop（非静默零）。本审**未**重跑引擎验证逐票 PIT 轨迹——以脚本契约 + Arch CONSUMED_PASS + meta 为据。

## 3. 覆盖

| 指标 | 值 |
|---|---|
| coverage_median | **3146.0** |
| coverage_gate / gate_pass | **300** / **true** |
| coverage min / max | **1450**（2024-07-30）/ **3828**（2025-09-22） |
| n_rebal | **30** |
| n_daily_rows | **1579217** |
| n_month_chunks_written | 29 |

闸：median≥300 → **PASS**。全序列 rebal n 均 ≥1450 ≫300；不构成拒收。

## 4. 正交 / 重叠（读 overlap 全表）

样本日 6：`2024-06-03` … `2026-10-09`；schema=`leaf31_overlap_vs_leaf19_25_27_30`；live=false；`any_jaccard_hard_reject=false`。

| 对照 | ρ min–max（mean） | j20_max | Jaccard hard reject | strength ρ>0.5 |
|---|---|---|---|---|
| vs 叶19 | **−0.045–0.007**（≈**−0.021**；6/6） | **≈0.026** | **无** | **无** |
| vs 叶25 | **−0.095–−0.011**（≈**−0.041**；4/6 有值；2026-04-27/2026-10-09 ρ=null） | **0.0** | **无** | **无** |
| vs 叶27 | **−0.188–−0.005**（≈**−0.057**；6/6） | **0.0** | **无** | **无** |
| vs 叶30 | **−0.014–0.039**（≈**0.008**；6/6） | **0.0** | **无** | **无** |

对照 FROZEN §4 失效条件：Jaccard≥0.7 近等权 **未触发**；ρ 绝对值均 ≪0.5 → 强度过滤未亮；相对叶19/25/27/30 **低相关**，正交披露健康。叶25 两日 ρ=null 仅披露，不构成硬拒。

## 5. IC / ICIR / walk-forward

| 项 | 状态 |
|---|---|
| 包内文件 | 仅 alpha / overlap / run_meta — **无** IC 表、无 WF 折、无收益序列 |
| 脚本 | 明示 **NEVER selects sign from returns**；不算收益 IC |
| 本审 | **禁止**自开实数 IC（需独立 `.ok`）；**未开算**；**不伪造** |

→ **收益过程指标 ABSENT**。分层结论：构建过程可 ACCEPT；**不得**在对外口径写「IC 过闸 / ICIR 达标 / WF 稳健」。下一步须 **另窗** IC/WF 评估（独立授权），非本审范围。

## 6. 组合闸对照（新口径 A/B 与现行 GATE_V3）— 过程结论 only

对照 `docs/v2/ALPHA_GATE_AB_PREREG_20261014_ZH.md` 与 `docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

- 门A/门B / 现行门 / GATE_V3 均要求组合级 CAGR·MDD·Calmar（及 Book-Smoke X2 终判）。
- **本包无** Book-Smoke 产物、无组合净值、无 CAGR/MDD/Calmar、无 selfcheck。
- 过程结论：**组合闸未交数 → 不裁定 PASS/FAIL**；**≠Book-Smoke**；Alpha **不自开烟、不自申 X2 ACCEPT**。
- run_meta `x2_accept=false` 与本审一致。

叶验收顺序提醒：HC→单叶研究 ACCEPT（本审此层）→CMC→衰减门→GATE_V3 本地→Eng Book-Smoke；后续步 **另排**。叶30 selfcheck HOLD/`f00536b9`（decay=DECAY_DOWNGRADE）**不回撤**本叶构建 ACCEPT，亦**不**借本票解阻叶30。

## 7. parquet 轻核（只读；未跑回测）

| 项 | 值 |
|---|---|
| 列 | `trade_date`, `ts_code`, `alpha` |
| 行数 | 1579217（= meta n_daily_rows） |
| 日期范围 | 2024-06-03 → 2026-10-09；n_unique_dates=570 |
| n_unique_codes | 5077 |
| null_frac / zero_frac / all_zero | 0 / 0 / False |
| alpha 值域 | min=**−1.0** / max≈**−0.00026** / mean≈**−0.488** / std≈**0.286**（−rank 百分位 → 值域落在 (−1,0]；非全零常数；截面残差量级合理） |
| peak_kb（自报） | 847092 |

## 8. 披露边界（硬）

1. **ACCEPT** = 研究级 **α 构建过程**过闸；**≠X2 ACCEPT**（本拍**不解阻**）。
2. **≠Book-Smoke**；**≠门A/门B/GATE_V3** 裁定；**≠selfcheck**。
3. **IC/ICIR/WF ABSENT** → 不得宣称收益过程过闸。
4. **勿升纸面**；`promotion_approved=false`；不改 `FROZEN_CONFIG` / paper；**不改 alpha_labels**。
5. 禁 RESTORED：`fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`；禁抬 rss；禁自开实数回测。
6. Arch 已 CONSUMED_PASS（`7bd6f33a`）；本审不恢复 `.ok`、不签新 `.ok`。
7. 叶30 KEEP 修复 **`0087c928` 另队**；本审未混办。
8. **leo_notify=false**；不报 Leo。

## 9. 下一步（可执行）

1. **主**知悉本闸审 ACCEPT（构建过程）；可排 **IC/WF 评估另窗**（独立 `.ok` / 授权；Alpha 不代启实数）。
2. 组合边际 / 门B·GATE_V3 / Book-Smoke / selfcheck：**等主另排**；Alpha 不自开烟、不自申 X2 ACCEPT。
3. 衰减 KEEP（FROZEN §7）须在独立评估窗验证；本构建 ACCEPT **不解阻** decay KEEP。
4. 叶30 HOLD/`f00536b9` 与 `0087c928` 另队继续；标签仍不动。
5. 对外话术保持分层：**构建 ACCEPT / 收益 HOLD / 组合不裁定**；主裁决词仍以本回执 **ACCEPT** 为准（研究构建契约）。

## 10. 状态动作

- 落盘本回执（本文件）。
- `TEAM ### Alpha`：更新为叶31 构建闸 VERDICT=ACCEPT + 本回执 sha8（≤3 行；先 cp 备份 `…bak_alpha_leaf31_build_gate_20261027`）；可带叶30 HOLD/`f00536b9` 一行。
- `alpha_labels`：**不动**。
- ql_bus：可选 `emit('QuantLab Alpha','gate',…)`。

live=false；promotion_approved=false；forbid_paper_handoff=true；leo_notify=false。
