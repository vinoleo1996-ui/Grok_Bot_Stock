# 叶25 · 步骤−1 TTM recon 闸审披露（R5_v4）

- **日期**：2026-10-25 ≈11:24 ET · America/New_York
- **作者**：QuantLab Alpha（研究级 recon 闸审；非纸面/晋级）
- **范围**：叶25 **步骤−1 TTM hand reconciliation**（`step_m1`）；**不是**全叶 X2 / 门B / GATE_V3 / Book-Smoke
- **预注册**：`docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md`（step −1 required；PASS 含 rule_exercised i/ii/iii）
- **锁**：`live=false` · `promotion_approved=false` · `forbid_paper_handoff=true` · 不改 FROZEN_CONFIG · 不申 .ok · 不改 alpha_labels

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **裁决** | **STEP_M1_RECON_PASS** | 研究级 recon 通过；rule i/ii/iii 全 True；rc=0；C4=PASS |
| **钉对齐** | **MATCH** | `.ok` `1c32ab1e` / cmd R5c_v4 `8231cf2d`（旧 `7b279d47`/`be7f5e5a` = VOID，未复用） |
| **纸面** | **勿升** | 非叶级 RESEARCH_ACCEPT；全叶仍等后续因子 X2（独立 .ok） |
| **标签** | **不动** | 非叶级终裁；`alpha_labels` 不改 |

语义：**研究级 recon 通过** ≠ 叶级 ACCEPT / ≠ 纸面票。

## 钉核对（独立 sha256sum）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| AI 回执 | `2bf4745d` | `2bf4745d9f01a192738362aa8ccaa30957ea2d3a83b1348d612894f7df7457a4` | **MATCH** |
| `.ok` 内容（CONSUMED） | `1c32ab1e` | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` | **MATCH** |
| cmd R5c_v4 | `8231cf2d` | `8231cf2df598716cce30343bc335c8bf645614058eeab9d691a6ef768c011052` | **MATCH** |
| Arch 消费文 | `9c96bf35` | `9c96bf351ef6e6e69b127ef9e308569e01f574dd5840588866239a842473c838` | **MATCH** |
| raw_rows.csv | `5a0ba8fb` | `5a0ba8fb3939389b085efb522783f3293e3cd3e1916164dba9845c20e0ae80ed` | **MATCH** |
| ttm_script.csv | `ba6d57d6` | `ba6d57d613ac87789a824dd9231e03eb8ad9cd3f01e30150d95f4aa5670490c6` | **MATCH** |
| run_meta.json | `b3dc8343` | `b3dc83437c4bb679b088d52efd09462c61f522e4a0a0174330acbdf5487d8238` | **MATCH** |

- ET_TS：`20261025_111646`
- out_dir：`output/ai_factory/_leaf25_ttm_recon/20261025_111646/`
- CONSUMED 路径：`output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5_v4.1c32ab1e.CONSUMED.20261025T1122ET.ok`
- wrapper exit=**0**；C4=**PASS**；`peak_rss_kb`=**675792**（≈660MB；meta/回执一致）
- 旧 VOID `7b279d47` / R5c_v3 `be7f5e5a`：**未复用**（`.ok` 明示 supersedes）

## rule_exercised（摘自 run_meta；不编数字）

| 规则 | meta 键 | 值 | trigger 摘要（meta） |
|---|---|---|---|
| i | `i_one_table_correction` | **True** | 000505.SZ / balance / end=2024-06-30 / corr=2025-10-18；key_before uf=0 → key_after uf=1 |
| ii | `ii_annual_q1_same_day_or_q1_first` | **True** | 000003.SZ / y=2019 / a_date=q_date=2019-04-27 / same_day=true；asof 2019-04-29 status=OK E=Q1 |
| iii | `iii_ipo_lt4q` | **True** | 001220.SZ / first_period=2022-12-31 / first_date=2026-01-15；首报日 TTM=NaN_no_complete_E |

三 True ∧ rc=0 → 预注册 step −1 PASS 条件满足。

## 披露边界

1. 本裁决名 **STEP_M1_RECON_PASS** 仅覆盖步骤−1 TTM recon；**不是** GATE_V3 / 门B / Book-Smoke / 叶级 RESEARCH_ACCEPT。
2. `forbid_paper_handoff=true`；不 handoff Eng 晋级；不派烟。
3. 全叶闸审仍等 AI/Arch **另开**后续因子窗 + 独立 `.ok` + X2；**Alpha 不代启**。
4. Arch 已 CONSUMED（`9c96bf35…`）；P2 wrapper 默认采样改 `/tmp` 属 Arch/AI 后续，不挡本 recon 闸审。

## 状态动作

- `TEAM ### Alpha`：旧钉 `7b279d47`/`be7f5e5a` → 对齐 `1c32ab1e`/`8231cf2d`
- `alpha_labels`：**不动**（非叶级终裁；跳过 `build_alpha_labels.py`）
- 纸面 / promotion / live：**全部 false**

## 下一步

等 AI/Arch 开后续因子窗（独立 `.ok`）；Alpha 收包后再做叶级闸审。叶27 HI_LIQ ABORT/VOID 另叙，闸审仍等新 `.ok`+X2。

live=false；promotion_approved=false；forbid_paper_handoff=true。
