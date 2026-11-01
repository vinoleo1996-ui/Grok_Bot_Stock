# HI_LIQ equity_incentive 腿拒收：REJECT_IND_CAP（不进 B4）

- 时间：2026-10-14 08:22 ET
- 依据：Arch 增量审计 P1 N1（`docs/v2/audit/AUDIT_20261014_0817_ET_ZH.md`）
- 约束：不改 FROZEN / 纸面轨；promotion_approved=false；live=false；禁 GP；**不派 SendToAgent**（本轮由父任务直办）

## 裁决

| 项 | 值 |
|---|---|
| 腿 | `g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_195554.parquet` |
| check | `output/strategy_hiliq/legs/g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_195554.parquet.check.json` |
| `ind_cap_script` / `ind_cap` | 0.25 |
| `max_book_ind_weight` | 0.28 |
| `max_sleeve_frac` | 0.35000000000000003 |
| `ind_cap_ok_book` | **False** |
| 状态 | **REJECT_IND_CAP** |
| B4 / 密封合成 | **禁止纳入**，直至 AI 重生且 `ind_cap_ok_book=True` |

## 处置

1. Alpha 验收清单已加硬断言：`docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md` §2.1。
2. AI 须修裁剪/断言后重生该腿；重生前 Strategy **不得**把本腿编进 B4。
3. capacity_adv HI_LIQ 腿（行业抽检 OK）不受本拒收影响。

可选镜像：`output/alpha/ALPHA_HILIQ_EQUITY_INCENTIVE_REJECT_IND_CAP_20261014.json`
