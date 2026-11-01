# 叶30 CRR R3 PEAKCUT · Alpha 闸门审（研究级 α 构建过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 01:21 ET**（America/New_York） |
| **主裁决 VERDICT** | **ACCEPT**（研究级 α 构建过程过闸） |
| 语义分层 | 构建过程 **ACCEPT**；收益过程指标（IC/ICIR/WF）**ABSENT** → **不得宣称 IC 过闸**；组合闸（门A/B·GATE_V3）**未交数 → 不裁定** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠Book-Smoke** / **≠门B·GATE_V3 PASS/FAIL** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`20efb33f`**（`.ok` 归档 **`7e239487`**；禁 RESTORED） |
| out | `output/ai_factory/_leaf30_crr/20261027_003132/` |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **ACCEPT** | 钉全 MATCH + FROZEN 机制对齐 + coverage 过闸 + 无 Jaccard 硬拒 + Arch CONSUMED_PASS + approx=false |
| 钉对齐 | **MATCH** | alpha/overlap/run_meta/脚本/AI/Arch/FROZEN/archived `.ok` 前 8 字符全 MATCH；live `.ok`=0 |
| PIT / 残差·正交 | **对齐 FROZEN §3** | OP CRR 16Q + vol_pen；λ=1.0；SW L1 demean + logmv OLS；银/地/非银硬排除；mechanism_tag 钉住 |
| 覆盖 | **PASS** | coverage_median=**1913.5** ≥300；min=937 / max=2342；n_rebal=**30** |
| 正交/重叠 | **无硬拒** | ρ19≈0.34–0.45；ρ25≈0.20–0.22（4/6）；j20_max≈0.053；Jaccard≥0.7 **未触发**；ρ>0.5 强度过滤 **未触发** |
| IC/ICIR/WF | **ABSENT** | 包内无正式 IC/ICIR/walk-forward 数字；脚本明示不计算收益；**本审未开算** |
| 组合闸对照 | **不裁定** | 无 Book-Smoke / 无组合 CAGR·MDD·Calmar → 不得判门A/B 或 GATE_V3；≠Book-Smoke |
| parquet 轻核 | **OK** | 列 `trade_date,ts_code,alpha`；2024-06-03→2026-10-09；n=974711；null/zero=0；非全零；peak_kb=917820≪1500 |

**主裁决词单列**：**ACCEPT** = 研究级 α **构建过程**过闸（RESEARCH_ACCEPT 口径）。**不是** X2 ACCEPT，**不是** 收益过程过闸，**不是** 组合门过闸。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| alpha parquet | `c8c7a5a5` | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` | **MATCH** |
| overlap JSON | `f9991d9d` | `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` | **MATCH** |
| run_meta.json | `a6acfe27` | `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` | **MATCH** |
| 脚本 r3_peakcut | `3ee9fed2` | `3ee9fed2c91a8c523128d9a0b0956f29a11fd2935d961e978aa07b9eafb0a182` | **MATCH** |
| AI RUN_RECEIPT | `88a08738` | `88a08738117915362a51bd5fd2b68c38750520e8fc86bde63651405798b290ec` | **MATCH** |
| Arch CONSUMED_PASS | `20efb33f` | `20efb33f660c92088d4e558fb5ff0e3e4a49b6fc9565aacf838b72ebe6e1db6d` | **MATCH** |
| FROZEN who_pays | `93cad965` | `93cad965bd9aa34b6bb8dc5e43d6f0095c4d111420c5fa53b196ad4220d40fba` | **MATCH** |
| archived `.ok` 内容 | `7e239487` | `7e2394879ff83f19c52e36895cbf200bffd9e957817026d2ed4a489b60359991`（路径 `_consumed/…7e239487.CONSUMED_PASS.20261027T0116ET.ok`） | **MATCH** |

附加硬钉（自 run_meta / 盘面）：

| 项 | 值 | 判定 |
|---|---|---|
| approx | **false**（正式 16Q OP CRR+vol_pen；≠COUNT APPROX） | **PASS** |
| live / promotion_approved / execute_flag | false / false / false | **PASS** |
| peak_kb / rss_limit_mb | **917820** / 1500（≈59.8% 硬帽；≪1500） | **PASS** |
| live `.ok` 计数 | **0** | **PASS** |
| VOID R1/R2 `.ok` | `5ae077fa` / `5af20222` 仅在 `_consumed` VOID；**未 RESTORED**；forbid 列表含二者 | **PASS** |
| X2 窗 | `2024-06-03`→`2026-10-09`；universe=HILIQ；window=x2 | 结构钉住 |
| mechanism_tag | `g1g5_ashare_crr_cfooe_volpen_v1` | MATCH FROZEN |
| λ / ic_sign_expected | 1.0 / positive | MATCH FROZEN §4 |

## 2. PIT / 残差·正交（对照 FROZEN §3；读脚本+meta，不编造）

| FROZEN 钉 | 脚本/meta 实现 | 判定 |
|---|---|---|
| OP=`operate_profit`；OCF=`n_cashflow_act`；禁净利润替营业利润 | `KNOWN`/读列钉 `operate_profit`+`n_cashflow_act`；approx_note 明示 ≠ocf_to_profit | **对齐** |
| CRR L≈16 / min_q=12 | meta `crr_L=16` `crr_min_q=12` | **对齐** |
| CFOOE ε → vol_pen 窗 8 / min 6 | meta `vol_win=8` `vol_min=6`；`attach_eps_vol_pen` 截面 OLS(SW dummy+logmv)→rolling_std | **对齐** |
| α_raw = rank(CRR)−λ·rank(vol_pen)，λ=1.0 | `LAMBDA_FROZEN=1.0`；`raw = r_crr - LAMBDA_FROZEN * r_vol` | **对齐** |
| SW L1 demean + log 流通市值 OLS 残差 | `alpha_dm = groupby(sw_code).transform(mean)` demean → `ols_resid(alpha_dm, [1,logmv])` | **对齐** |
| 行业硬排除 银行/地产/非银 | `EXCLUDE_SW` 801780/801180/801790；rebal 与日扩均 `members - excl` | **对齐** |
| IC 期望正；脚本不算收益 | 注释钉 + meta notes「script does not compute returns」 | **对齐**（故 IC **ABSENT**） |
| Jaccard≥0.7 硬拒；ρ>0.5 强度过滤 | overlap schema note + `jaccard_hard_reject_*` / `strength_filter_*` | **对齐**；本次均 false |

PIT 要点：fund 用 `avail<=rebal_day` 取最新季报；logmv 为 T−1（`_load_logmv_t1`）；qend_ok_filter=true。本审**未**重跑引擎验证逐票 PIT 轨迹——以脚本契约 + Arch CONSUMED_PASS + meta 为据。

## 3. 覆盖

| 指标 | 值 |
|---|---|
| coverage_median | **1913.5** |
| coverage_gate_median_ge_300 | **true** |
| coverage min / max | **937** / **2342** |
| n_rebal | **30** |
| n_daily_rows | **974711** |
| n_month_chunks_written | 29 |

闸：median≥300 → **PASS**。前期若干 rebal（如 2024-07-30 n=937）仍 ≥300 下限；不构成拒收。

## 4. 正交 / 重叠（读 overlap 全表）

样本日 6：`2024-06-03` … `2026-10-09`；leaf25_sha8=`8be12024`；live=false。

| 对照 | ρ min–max（mean） | j20_max | Jaccard hard reject | strength ρ>0.5 |
|---|---|---|---|---|
| vs 叶19 | **0.341–0.450**（≈0.399） | **≈0.053** | **无** | **无** |
| vs 叶25 | **0.195–0.221**（≈0.207；4/6 有值；2026-04-27/2026-10-09 ρ=null） | **0.0** | **无** | **无** |

对照 FROZEN 失效条件：Jaccard≥0.7 近等权 **未触发**；非单点 OCF÷利润；行业排除已做；λ/符号未事后翻；approx 未升格。ρ19 落在 0.34–0.45（<0.5）→ 强度过滤未亮，仅披露。

## 5. IC / ICIR / walk-forward

| 项 | 状态 |
|---|---|
| 包内文件 | 仅 alpha / overlap / run_meta — **无** IC 表、无 WF 折、无收益序列 |
| 脚本 | 明示 **NEVER computes returns / IC** |
| 本审 | **禁止**自开实数 IC（需独立 `.ok`）；**未开算**；**不伪造** |

→ **收益过程指标 ABSENT**。分层结论：构建过程可 ACCEPT；**不得**在对外口径写「IC 过闸 / ICIR 达标 / WF 稳健」。下一步须 **另窗** IC/WF 评估（独立授权），非本审范围。

## 6. 组合闸对照（新口径 A/B 与现行 GATE_V3）— 过程结论 only

对照 `docs/v2/ALPHA_GATE_AB_PREREG_20261014_ZH.md` 与 `docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

- 门A/门B / 现行门 / GATE_V3 均要求组合级 CAGR·MDD·Calmar（及 Book-Smoke X2 终判）。
- **本包无** Book-Smoke 产物、无组合净值、无 CAGR/MDD/Calmar。
- 过程结论：**组合闸未交数 → 不裁定 PASS/FAIL**；**≠Book-Smoke**；Alpha **不自开烟、不自申**。

叶验收顺序提醒（清单 §3）：HC→单叶研究 ACCEPT（本审此层）→CMC→衰减门→GATE_V3 本地→Eng Book-Smoke；后续步 **另排**。

## 7. parquet 轻核（只读；未跑回测）

| 项 | 值 |
|---|---|
| 列 | `trade_date`, `ts_code`, `alpha` |
| 行数 | 974711（= meta n_daily_rows） |
| 日期范围 | 2024-06-03 → 2026-10-09；n_unique_dates=570 |
| n_unique_codes | 3561 |
| null_frac / zero_frac / all_zero | 0 / 0 / False |
| alpha 值域 | min≈−1.313 / max≈1.220 / mean≈0.00027 / std≈0.337（截面残差量级合理；非全零常数） |
| peak_kb（自报） | 917820 |

## 8. 披露边界（硬）

1. **ACCEPT** = 研究级 **α 构建过程**过闸；**≠X2 ACCEPT**。
2. **≠Book-Smoke**；**≠门A/门B/GATE_V3** 裁定。
3. **IC/ICIR/WF ABSENT** → 不得宣称收益过程过闸。
4. **勿升纸面**；`promotion_approved=false`；不改 `FROZEN_CONFIG` / paper；**不改 alpha_labels**（非叶级终裁含组合/IC 全链）。
5. 禁 RESTORED：`7e239487` / `5af20222` / `5ae077fa`；禁抬 rss；禁自开实数回测。
6. Arch 已 CONSUMED_PASS（`20efb33f`）；本审不恢复 `.ok`、不签新 `.ok`。
7. **leo_notify=false**；不报 Leo。

## 9. 下一步（可执行）

1. **主**知悉本闸审 ACCEPT（构建过程）；可排 **IC/WF 评估另窗**（独立 `.ok` / 授权；Alpha 不代启实数）。
2. 组合边际 / 门B·GATE_V3 / Book-Smoke：**等 Eng** 另窗；Alpha 不自开烟。
3. 叶25 / 叶27 等候线不挡本叶构建 ACCEPT；标签仍不动。
4. 若主要求「必须先有 IC 才对外称过闸」——对外话术保持分层：**构建 ACCEPT / 收益 HOLD**，主裁决词仍以本回执 **ACCEPT** 为准（研究构建契约）。

## 10. 状态动作

- 落盘本回执（本文件）。
- `TEAM ### Alpha`：更新为叶30 R3 闸审 VERDICT=ACCEPT + 本回执 sha8（≤3 行；先 cp 备份 `…bak_alpha_leaf30_r3_gate_20261027`）。
- `alpha_labels`：**不动**。
- ql_bus：可选 `emit('QuantLab Alpha','gate',…)`。

live=false；promotion_approved=false；forbid_paper_handoff=true。
