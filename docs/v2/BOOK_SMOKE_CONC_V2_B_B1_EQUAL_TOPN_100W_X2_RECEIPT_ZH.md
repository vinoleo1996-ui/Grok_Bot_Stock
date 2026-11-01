# Book-Smoke 回执（个股+ETF 主书骨架）

**run_id**：`book_smoke_20261014_015510`  
**strategy_promotion_approved**：`false`  
**sealed_claim**：`false`（不声称过密封线）  
**Mandate**：`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`  

## 缺口

- （无）

## 袖套

```json
{"core": 0.0, "stock": 1.0, "alpha_event": 0.0}
```

## 可消费权重长表（KPI）

```json
{
  "stock": {
    "status": "book_consumable",
    "n_rows": 17556,
    "n_sessions": 570,
    "not_book_consumable": false,
    "path": "output/small_aum_concentration/v2/B_B1_equal_topN_100w.parquet",
    "error": null
  },
  "alpha_event": {
    "status": "not_book_consumable",
    "n_rows": 0,
    "n_sessions": 0,
    "not_book_consumable": true,
    "path": null,
    "error": "no_path"
  }
}
```

## 停机建议

连续 GATE_OK=0 包 → 停 GP；以 Book-Smoke / 可消费长表为进度 KPI

## 净值摘要（探索窗；成本开；非密封）

| AUM | arm | CAGR | MDD | Sharpe | cost/AUM | target_weight 行数 | 起止 |
|---|---|---|---|---|---|---|---|
| 1000000 | X2/BOOK | 0.1450 | -0.1522 | 0.897 | 0.0236 | 14823 | 2024-06-03→2026-10-09 |
| 1000000 | X2/C0 | 0.1127 | -0.1624 | 0.651 | 0.0002 | 570 | 2024-06-03→2026-10-09 |

JSON：`output/v3/book_smoke_stock_etf/book_smoke_summary.json`

> 无个股权重时长表时，BOOK≈C0（纯 510300）。有 `--stock-path` 后 BOOK 才会偏离 C0。


## 成交诊断
见 docs/v2/BOOK_SMOKE_CONC_V2_SUMMARY_ZH.md 表格对应行（scripts_eng/conc_fill_diag.py）。
