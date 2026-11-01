# Alpha 汇总 · Data D1–D4 回传验收（2026-10-13 更新）

**角色**：QuantLab Alpha · `promotion_approved=false` · **未跑 GP** · **未升 live** · **未代跑工厂**  
**更新**：D2 moneyflow 正式交付复检后升 **ACCEPT_FULL**（约 02:52 ET）

| ID | 裁决 | 一句话 |
|---|---|---|
| **D1** | **ACCEPT_FULL** | full 12,289,609 行 / 5,913 标的 / 2014-01-02→2026-10-12；原空窗 183 日 **missing_from_gap=0**；研究 asof 可消费；**非** promotion/密封 |
| **D2** | **ACCEPT_FULL** | moneyflow 9,498,309 行 / 5465 标的 / 20180102→20261012（SSE 2126 日全覆盖）；available_at PIT 无泄漏；可作闸门/短清单满样本；**非** promotion |
| **D3** | **ACCEPT** | mid_large PIT 555万行；≠CSI300；前一日市值 top50%（不变） |
| **D4** | **GAP ACCEPT** | 无历史 IOPV 源；拒收成立，不伪造（不变） |
| D5/D6 | 排队 | 未验 |

## 专单

- D1 阶段：`ALPHA_DATA_D1_VALUATION_ACCEPT_ZH.md`
- D1 残差复检（终态 ACCEPT_FULL）：`ALPHA_DATA_D1_RESIDUAL_RECHECK_ZH.md`
- D1 全量验收：`ALPHA_DATA_D1_VALUATION_FULL_ACCEPT_ZH.md`
- D2 全量验收：`ALPHA_DATA_D2_MONEYFLOW_ACCEPT_ZH.md`
- D3：`ALPHA_DATA_D3_MID_LARGE_ACCEPT_ZH.md`
- D4：`ALPHA_DATA_D4_IOPV_GAP_ZH.md`
- 机读：`output/alpha/d1d4_status_accept_20261012.json`；`output/alpha/d1_valuation_full_accept_20261012.json`；`output/alpha/AI_D2_MONEYFLOW_ACCEPT_20261013.json`

## 对 Data 下一拍

1. D1：full 已 ACCEPT_FULL — 无强制返工；保持 available_at 规则与日历对齐  
2. D2：已 ACCEPT_FULL — 无强制返工；可选补 `moneyflow_stock_daily_pit_manifest.json`（available_at=下一开市 09:00 ASH）；日常增量对齐 SSE  
3. D3：已 ACCEPT；注意 tip 可能滞后 moneyflow 1 session（如 2026-10-12）  
4. D4：缺口已接；有新源再开单  
5. D5/D6：排队可继续  
6. **禁止**把 D1/D2 ACCEPT 当作 GP 重启或 promotion 授权（`promotion_approved=false`）
