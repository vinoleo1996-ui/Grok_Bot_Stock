# SW 默认 tushare + prefix 回退 + EM EITIME 二次时钟

整体 `promotion_approved=false`（`ENG_PING` / `PROMOTION_ACCEPTANCE` overall still partial FAIL）。  
SW **数据集** tushare 已验收 PASS，可作为 `research_preferred` 默认。

## float_mktcap（未改）

主路径仍是 `data/v2/float_mktcap/`（asof + daily）。readers 未把默认切到 `float_mktcap_daily_tushare.parquet`。

## SW_L1 研究默认

| 优先级 | 路径 | 说明 |
| --- | --- | --- |
| **默认（accepted）** | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | Data PASS；数据集 `promotion_approved` 可 true |
| **回退** | `data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet` | XLS prefix→801xxx；强制不可晋升 |
| **回退** | `data/v2/sw_l1_pit/industry_members_sw_l1.parquet` | 旧 vote 映射；强制不可晋升 |
| 上游 raw（非默认） | `data/v2/free_hunt/sw_pit/sw_l1_pit_from_xls_prefix.parquet` | 原生列；需显式 `path=` |

入口：`load_sw_l1_members` / `resolve_sw_l1_research_path`。  
`default_v2_roots().sw_l1_path` → tushare；`sw_l1_prefix_path` → prefix；`sw_l1_fallback_path` → vote。

**标志分层**：
- `SWL1TableView.promotable` / `.promotion_approved`：仅 tushare 可跟 Data 数据集验收
- D1 `sw_l1_promotable`：反映数据集标志
- Mandate / paper / eng **整体** `promotion_approved`：仍强制 false

Prefix 未映射 L1 以 `PREFIX_*` 出现在 `sw_code`；空 `sw_name` 在加载时填 `SW_L1:<sw_code>`。

## EM EITIME 二次 available_at（不替换主财务 PIT）

| 项 | 值 |
| --- | --- |
| Manifest | `data/v2/financials_pit/research_free_hunt_secondary_manifest.json` |
| 默认表 | `data/v2/financials_pit/research_em_yjbb_pit_seed_notice_le_20260630.parquet` |
| 二次 EP | `data/v2/financials_pit/research_ep_from_em_yjbb_asof_20260630.parquet` |
| Helper | `load_em_eitime_available_at` / `em_eitime_lookup` |
| 标签 | `source=em_eitime` |

主路径不变：`financials_available_at.parquet` / `ep_research_asof_*.parquet`。  
EITIME = 东财入库时间，非交易所 as-filed；不可晋升。

## 冒烟（可选）

```bash
cd /workspace/QuantLab
PYTHONPATH=. python -c "from quantlab.data.v2_readers import default_v2_roots, load_sw_l1_members, load_em_eitime_available_at, load_float_mktcap_asof; r=default_v2_roots(); sw=load_sw_l1_members(roots=r); em=load_em_eitime_available_at(roots=r); fm=load_float_mktcap_asof(roots=r); print(sw.path, sw.source_variant, sw.n_rows, sw.promotable, sw.promotion_approved, sw.quality_label); print(em.path, em.available_at_source, em.n_rows); print(fm.path, 'float_ok', fm.promotion_approved)"
```
