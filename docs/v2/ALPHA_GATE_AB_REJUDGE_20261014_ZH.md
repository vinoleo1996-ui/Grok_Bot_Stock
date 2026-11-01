# 组合门 A/B 并列重判（研究级，仅报告）2026-10-14

live=false，promotion_approved=false。预注册：docs/v2/ALPHA_GATE_AB_PREREG_20261014_ZH.md（sha256 f59eb36a…，先于读结果冻结）。不改任何状态，alpha_labels.json 未动，未派烟测，禁 GP。

窗口 2024-01-03→2026-10-09（667 日），复权价，成本：单边15bp+卖出印花5bp，按日换手；门A对冲 4.3%/年×β名义。

主干 capacity_adv：CAGR 16.37%，MDD -13.55%，Calmar 1.208。

## 80/20 主口径（60万=100万，见注）

| 叶 | 现行组合 CAGR/MDD/Calmar | 门A 去β组合 CAGR/MDD | 现行 | 门A | 门B | 建议 |
|---|---|---|---|---|---|---|
| leaf7_block_trade | 15.63%/-14.42%/1.084 | 12.69%/-11.59% | 不过 | 不过 | 不过 | no smoke |
| leaf9_interim_div_init | 15.34%/-14.02%/1.094 | 12.52%/-11.55% | 不过 | 不过 | 不过 | no smoke |
| leaf11_report_rc_allup | 16.32%/-14.40%/1.133 | 13.18%/-11.52% | 不过 | 不过 | 不过 | no smoke |
| leaf12_analyst_recoverage | 9.70%/-15.13%/0.641 | 6.57%/-12.25% | 不过 | 不过 | 不过 | no smoke |
| leaf13_stk_surv | 15.41%/-14.38%/1.072 | 12.01%/-11.54% | 不过 | 不过 | 不过 | no smoke |
| equity_incentive | 17.46%/-14.17%/1.232 | 14.02%/-11.11% | 不过 | 不过 | 过 | recommend Book-Smoke via New Bot |

敏感性 90/10、70/30：结论与主口径一致（equity_incentive 三档权重门B 均过，其余均不过）。详见 JSON。

尝试数：主判定 18（6 叶×3 门），敏感性读数 36。

## 注意
- 60万/100万读数相同（本地混合，无整手效应）；未用 Eng 分档净值
- 门A：IF 一手名义约110-120万，20%卫星（12万/20万）不足一手，实盘不可行，仅研究口径
- 门A结构性劣势：卫星β≈1被对冲后组合整体β降约0.2，CAGR 必然大幅下降，MDD 虽变浅但 CAGR 门几乎不可过
- equity_incentive 门B 余量很薄（Calmar 1.232 vs 1.208），且 Eng 已有 80/20 Book-Smoke 未在 CAGR+MDD 上两档胜主干；超额集中在2026

- 更正说明（2026-10-14 05:30 ET）：叶12 差异已查明（非 bug）：毛口径复跑本脚本得单叶 CAGR 13.80%/MDD −15.17%，与 verify_analyst_recoverage 完全一致；差异全部来自成本。该叶权重文件每日双边换手 63.2%（单边 31.6%），全部为进出场（20 名、无 510300 压舱），按 17.5bp 计约 −28%/年成本拖累，净 CAGR −13.9%。符号、权重拼接、日期对齐均无误。毛口径复核六叶三门：结论与净口径完全相同（仅 equity_incentive 门B 过，毛 Calmar 1.356 vs 主干 1.340）。

## 补记（2026-10-14 ~05:55 ET）：equity_incentive 80/20 门B Book-Smoke X2 实测 → 门B 最终 **FAIL**
- 来源：Eng 回执 docs/v2/BOOK_SMOKE_EQINC_8020_GATEB_ZH.md；Alpha 已对文件逐项核对：
  - output/v3/book_smoke_g1g5_combo_capadv_eqincent_80_20_x2/book_smoke_summary.json（run book_smoke_20261014_024557）
  - output/v3/book_smoke_g1g5_capacity_adv_x2/book_smoke_summary.json（run book_smoke_20261013_111418）
  - 两者窗口均为 X2/BOOK 2024-06-03→2026-10-09。

| AUM | capacity_adv CAGR/MDD/Calmar | 80/20 CAGR/MDD/Calmar | 门B |
|---|---|---|---|
| 60万 | 13.82% / −10.07% / **1.372** | 11.40% / −9.94% / **1.147** | ✗ |
| 100万 | 12.23% / −11.62% / **1.052** | 12.67% / −11.41% / **1.111** | ✓ |
MDD 两档都在 15% 内 ✓；但 Calmar 只一档胜 → **门B FAIL**。

- **口径规定：门B 的最终判定以 Book-Smoke X2（整手、T+1 开盘、分档、strategy_v1 成本）为准**；本文上方 Alpha 本地 close-to-close 读数（1.232 vs 1.208）只作候选筛选，不作终判。差异原因见 Eng 回执（窗口起点、整手、成本、余量仅 0.024）。另注意 80/20 在 60万档成交率 61%（主干 97%），卫星小单被整手稀释。
- 状态：equity_incentive **单叶**标签不变（BOOK_SMOKE_PASS / RESEARCH_CANDIDATE）；**组合门B 不过**，不走纸面、不晋级。live=false；promotion_approved=false；禁 GP。
