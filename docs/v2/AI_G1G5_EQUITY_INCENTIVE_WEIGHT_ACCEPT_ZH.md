# Alpha 裁定：叶6 g1g5_ashare_equity_incentive_v1 —— RESEARCH_ACCEPT（Book-Smoke PENDING）
裁定时间：2026-10-13 ET。promotion_approved=false；live=false；handoff=NO；no_gp=true。Alpha 未跑烟测、未跑 GP。
核验脚本：output/alpha/verify_equity_incentive_20261013.py；原始输出 output/alpha/verify_equity_incentive_20261013_raw.json。

## 1. 硬闸（全部 PASS）
| 项 | 结果 |
|---|---|
| 长表 date,instrument,target_weight | PASS（另带 mechanism_tag 等冗余列，不影响消费） |
| 逐日 Σw=1 | 1.0/1.0，668 日，对 510300 交易日无缺日 |
| 负权 / NaN / 重复键 / stub | 0 / 0 / 0 / 无 |
| 单名上限 | max 4.00% |
| 600519 / 002371 | 恒 0 |
| 压舱 510300 | 均 30.4%（20%–72%） |
| 逐日 Jaccard vs 全部前包（output/ai_factory 19 个 + output/intel 7 个） | max 0.167（vs earnings_event），全部 <0.7 |
| PIT | 公告日归一后取严格之后第一交易日为 T1，T2 次日入场；w(t-1)×r(t) 计收益，入场严格晚于 available_at。PASS |

注：AI 脚本自带的同构判据为「max≥0.7 且 ≥50% 日」，比 Alpha 门（max≥0.7 即拒）宽；本叶 max 0.167，两口径均不触发，但请 AI 以后改用 Alpha 口径。

## 2. 重点核①：57448/668/86 与 earnings_event 相同——不是复制
- SHA256 不同（incentive 1cb6b984… / earnings_event 06b4c213…）。
- 长表行数=668 日×86 名（每日为全部事件名落 0 权行），两叶恰好各有 86 只事件股，所以行数重合；名单交集仅 41/86。
- 外连接 87508 行中正权且完全相等的行仅 568 行；日持仓 Jaccard 均值 0.038、最大 0.167。
- 结论：巧合，非误用/复制。

## 3. 自报数字复核（close-to-close、无成本、未复权，与 AI 同口径）——全部吻合
| 项 | 自报 | 复核 |
|---|---|---|
| 毛 CAGR / MDD | 15.62% / −16.50% | 15.62% / −16.50%（510300：9.45% / −16.25%） |
| β / 残差 α | 1.03 / +5.75% | 1.027 / +5.75% |
| 分年 α | +4.50 / −1.36 / +13.82 | +4.50 / −1.36 / +13.82 |
| ρ 残差 vs capacity_adv | 0.003 | 0.003 |

## 4. 重点核②：与 insider_increase / earnings_event 的残差相关
| 残差 ρ | 全样本 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| vs insider_increase | 0.328 | 0.267 | 0.213 | **0.453** |
| vs earnings_event | 0.187 | 0.453 | 0.082 | 0.095 |
| vs capacity_adv | 0.003 | −0.233 | −0.033 | 0.106 |
- 2026 年持仓几乎不重叠（日 Jaccard vs insider 0.036、vs earnings 0.039），但残差相关 0.45：2026 的超额与 insider_increase 有共同的风格/防守成分，不是同一批股票。
- 2026 下跌日年化相对超额：incentive +23%、insider +78%、earnings −44%。本叶 β 1.03，MDD 与 510300 相当，**不是防守叶**；2026 的 α 更多是上涨/风格暴露，而不是跌市护盘。
- 结论：和 capacity_adv 正交（主卫星用途成立）；与 insider_increase 部分同源，两者不宜同时作为“独立”卫星计数。

## 5. 重点核③：同数据收益研究 / 弱样本外
- 盘上检索 equity_incentive/股权激励/员工持股：仅有 V30 解禁 share_type 叶里的 `unlock_incentive_ratio_20` 对照（数据 share_float、机制为解禁抛压，不同数据、不同事件）、P8 回购映射中剔除“股权激励回购注销”、event_flow_build 的分类正则、网研 C6 引文（开源量化评论 118）。**未发现草案事件的收益研究**。
- 文件时间：预注册 14:32 ET 落盘，脚本 14:32，权重 14:33——预注册先于权重；但预注册写“~14:45 写定”、回执写“实跑约 14:50”，与文件时间不一致（AI 称盒钟漂移），记为文档缺口。
- 判定：**不标弱样本外**；但方向来自外部券商研报（已知正向文献），属于先验非盲，非严格样本外。

## 6. 软缺口
1. α 集中于 2026（+13.8%），2025 为 −1.4%；132 个事件、日均 17 名，样本偏小。
2. β 1.03，无回撤保护；书面 MDD −16.5% 依赖压舱稀释。
3. 与 insider_increase 2026 残差 ρ 0.45。
4. 未复权收盘；池锚 2024-06-28 致 2024H1 轻微前视；事件源 2023-10 起，2024 初持仓偏少。
5. 无激励规模/考核门槛字段，未分层。
6. 预注册与回执时间戳表述与文件 mtime 不一致。

## 7. 裁定
**RESEARCH_ACCEPT**；book_smoke=PENDING（由 New Bot→Eng 按 60万∧100万 跑一次，Book-Smoke 门不变：CAGR∈[12%,18%] 且 MDD≥−28%，两档都要过）。不晋级、不实盘、handoff=NO、禁 GP。烟测过门也只到 RESEARCH_CANDIDATE；纸面需 Leo 在 Alpha 聊天本人原话。

## 8. Book-Smoke 核验与标注（Alpha，2026-10-13）
- 来源：docs/v2/BOOK_SMOKE_G1G5_EQUITY_INCENTIVE_X2_RECEIPT_ZH.md、BOOK_SMOKE_G1G5_EQUITY_INCENTIVE_COMBO_SUMMARY_ZH.md；运行目录 output/v3/book_smoke_g1g5_equity_incentive_x2。
- 输入核验：summary.json 的 stock 路径即本叶权重（sha256 1cb6b984…）；两档 target_weights 与源权重在 570 session、10784 行逐行比对，最大差 2.4e-8。成本开（ExecConfig.strategy_v1，60万成本 1.58%/AUM、100万 1.75%），基准 C0=纯 510300。窗口 X2 2024-06-03→2026-10-09。
- 由 nav.csv 复算（日历年、按 252 交易日计 Sharpe）：

| 臂 | AUM | CAGR | MDD | Sharpe | 分年 2024/2025/2026 % | 510300 同期 % |
|---|---|---|---|---|---|---|
| 本叶 | 60万 | 14.31%（365.25 日口径 14.20%） | −14.80% | 0.81–0.83 | +8.74 / +22.32 / +2.70 | +12.15 / +20.82 / −5.34 |
| 本叶 | 100万 | 15.18%（15.06%） | −15.58% | 0.80–0.81 | +9.51 / +21.81 / +4.22 | +12.15 / +20.83 / −5.34 |

- 门：CAGR∈[12%,18%] 且 MDD≥−28%，两档都过 → **BOOK_SMOKE_PASS**。
- 对照：capacity_adv 13.82%/−10.07%/1.018、12.23%/−11.62%/0.881——本叶 CAGR 更高但 MDD 更深、Sharpe 更低，不胜主干；earnings_event 13.64%/−18.29%/0.734、13.87%/−19.08%/0.730；insider_increase 13.14%/−16.50%、13.14%/−17.20%——本叶在三片事件叶中 CAGR、MDD、Sharpe 均最好。
- 分年：2024 跑输 510300（−3.4pp/−2.6pp），2025 略优（+1.5/+1.0pp），2026 超额 +8.0/+9.6pp——超额仍集中在 2026。
- 组合（Eng 自报，未逐一重算 nav，仅核表）：70/30 两档不胜主干（60万 11.74% 未过门）；80/20 仅 100万 胜（12.67%/−11.41%），60万 11.40% 未过门；4 腿诊断两档不胜主干。**组合无改进**。
- 标签：**RESEARCH_CANDIDATE**；promotion_path=null；handoff=NO；live=false；promotion_approved=false；禁 GP；勿再烟。纸面需 Leo 在 Alpha 聊天本人原话。
