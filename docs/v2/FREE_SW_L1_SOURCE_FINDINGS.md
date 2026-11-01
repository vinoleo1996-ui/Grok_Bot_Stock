# 免费申万一级进出史渠道排查（2026-10-10）

## 结论
- **真正带 in/out 的公开免费全市场 API：未找到。**
- 当前可用免费路径：申万官网 `StockClassifyUse_stock.xls`（已用）+ `index_component_sw` 当前成分。
- Tushare Pro `index_member_all`（约 2000 积分）、JoinQuant 按日 `get_industry_stocks`、BigQuant `cn_stock_industry_change`、Wind 均为账号/付费门禁；本机环境 **无** TUSHARE/JQ/Wind token。

## 已用
| 源 | PIT 质量 |
|---|---|
| StockClassifyUse_stock.xls + level1_members 投票 | 研究级；leaf→L1≈60% 历史行 |

## 免费但不足
| 源 | 问题 |
|---|---|
| akshare index_component_sw | 无 out_date |
| cninfo industry_change | 多样本稀疏，非全市场 SW_L1 账本 |
| BaoStock industry | 非申万 PIT 进出 |

## 门禁（有 in/out）
- Tushare Pro `index_member_all`
- JoinQuant dated industry stocks
- BigQuant industry_change
- Wind

详见 `data/sw/pit_probe/FREE_SW_L1_SOURCE_FINDINGS.json`。
