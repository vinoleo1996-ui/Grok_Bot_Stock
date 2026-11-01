# Alpha 验收 · Data D5/D6（2026-10-13）

研究级验收。promotion_approved=false，live=false。未运行 GP。

## 结论
| 数据集 | 裁定 |
|---|---|
| D5 csi_review_calendar（18 行） | ACCEPT_PARTIAL |
| D5 index_member_events（5,840 行） | ACCEPT_PARTIAL |
| D6 rights_issue_em（984 行） | ACCEPT_FULL（研究级，样本稀疏） |
| hsgt_top10（附带） | ACCEPT_PARTIAL |
| SW L1/L2 PIT（附带） | ACCEPT_PARTIAL |

## 核验结果
- **行数**：与交付短文和 manifest 全部一致（18/5,840/984/30,961/L1 7,743）。
- **SHA256**：所有 manifest 都没有哈希字段，无法比对。Alpha 已把当前哈希记入 JSON 作为基线（缺口 G0）。
- **重复**：D5、D6 和 hsgt 的全行重复与主键重复都是 0。SW L1 的 (instrument, in_date) 有 13 条重复，另有 12 个代码同时挂在两个当前 L1 行业下。
- **事件表质量分布**：public 4,018 / rule_inferred 1,716 / non_periodic_no_ann 106，与 manifest 一致。逐批次看，2018-12、2019-06、2019-12、2020-06、2022-06 这五批全部是 rule_inferred。
- **前视检查**：ann_date 晚于 effective_date 的 0 条；available_at 晚于 20261013 的 0 条；有 ann_date 的事件中，available_at 晚于快照日的 0 条。
- **未来批次**：2026-12 只出现在日历里，标为 scheduled_future_rule，事件表里没有它的成分事件。它只是预测，不能当已发生的事件使用。

## 使用约束（硬性）
1. **public_report**：可在 ann_date 20:00 后使用，T2 严格晚于 available_at 入场。
2. **rule_inferred（1,716 条）**：不得在推断的 ann_date 使用。2019-12 的媒体日期是 12/02–03，而推断日为 11/29，按推断日用会提前数日，构成前视。在找到真实公告日之前，最早只能从 effective_date 开盘起使用，相当于不能作为公告事件信号。
3. **non_periodic_no_ann（106 条）**：没有事件时点，只能在 snapshot_date 之后当成分状态使用。
4. 中证 500/1000 成分来自月末快照夹逼，in/out 的确切日期只确定在 (prev_snapshot, snapshot_date] 区间内。

## D6
- available_at 全部由 first_notice_date 20:00 得出（984/984），兜底规则没有用到。
- 除权日晚于 20261013 的 0 条。有 2 条 available_at 晚于除权日，属于晚到，方向保守，可以接受。
- 2018 年以来只有 61 条，2024 年以来只有 1 条，不足以单独做因子。适合用于除权核对和事件排除。

## 附带数据
- **hsgt_top10**：2022-06 到 2023-12 完全没有行，另有 7 个供应商空日。这段时间不能用于回测或 IC。
- **SW PIT**：available_at 取 in_date 18:00，只是近似，可能有回填；有键重复和多行业挂靠；197 只在交易的股票没有当前 SW 分类。不替代已晋级的 sw_l1_pit。

## 缺口（请 Data 后续处理，不阻塞研究使用）
- **G0**：manifest 补上 sha256。
- **G1**：5 个 rule_inferred 批次补真实公告日，优先 2019-12。
- **G2**：给 106 条临时调整补公告日。
- **G3**：回补 hsgt_top10 2022-06~2023-12。
- **G4**：SW PIT 去重，处理多 L1 挂靠，补 197 只缺失分类。
