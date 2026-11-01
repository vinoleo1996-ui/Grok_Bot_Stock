# Tushare loaders（SW 默认已升；其余仍候选）

依据 `docs/v2/PROMOTION_ACCEPTANCE.md` 与 `output/d1/ENG_PING_PATHS.json`：

- **SW** `research_preferred` = **tushare**（数据集验收 PASS；`promotion_approved` 可在**数据集**级为 true）
- **整体** `promotion_approved_overall=false`（float / financials / dividend 仍 FAIL）
- ETF 主路径仍是 **`panels/sh.510300.parquet`**
- float / financials / dividend **未**切到 tushare 默认

## SW_L1 Tushare（现默认）

| 项 | 值 |
| --- | --- |
| 路径 | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` |
| roots 字段 | `default_v2_roots().sw_l1_path`（= `sw_l1_tushare_path`） |
| Loader | `load_sw_l1_members()` 或 `load_sw_l1_members_tushare()` / `variant="tushare"` |
| 回退 | prefix → `variant="prefix"` / `sw_l1_prefix_path`；vote → `variant="legacy_vote"` |
| 质量 | `source_variant=tushare`；数据集 `promotable` / `promotion_approved` 跟随 Data manifest |
| 整体 | Mandate / paper / eng 输出仍 `promotion_approved=false` |

```python
from quantlab.data.v2_readers import load_sw_l1_members, load_sw_l1_members_tushare

sw_default = load_sw_l1_members()                 # tushare (accepted)
sw_prefix = load_sw_l1_members(variant="prefix")  # research fallback
sw_ts = load_sw_l1_members_tushare()              # same as default
assert sw_default.source_variant == "tushare"
# Dataset flags may be True; overall strategy promotion is separate.
```

## 510300 fund_daily Tushare（仍候选）

| 项 | 值 |
| --- | --- |
| 路径 | `data/v2/etf_510300/fund_daily_tushare_510300.parquet` |
| roots 字段 | `default_v2_roots().etf_fund_daily_tushare_path` |
| Loader | `load_etf_510300_fund_daily_tushare()` |
| 默认 | **否** — `load_etf_510300()` / `etf_510300_daily_returns()` 仍用 panel |

## asof_extend Tushare panels（验收 PASS；未切 merge 默认）

| 项 | 值 |
| --- | --- |
| 路径 | `data/v2/asof_extend_tushare_202610/panels` |
| roots | `asof_extend_tushare_dir`（secondary） |
| 默认 merge | **仍** `asof_extend_202610` |

## 未切换的默认

| 数据集 | 状态 |
| --- | --- |
| float_mktcap | 主路径仍 `data/v2/float_mktcap/`（日频 tushare FAIL：历史浅） |
| financials_available_at | 主路径未改（tushare FAIL：标的过少） |
| dividend | 未改（tushare FAIL：1c85 解释率不足） |
| ETF panel | 仍 `panels/sh.510300.parquet` |

## 谁该怎么调

| 角色 | 默认应调 | 说明 |
| --- | --- | --- |
| Alpha（行业正交等） | `load_sw_l1_members()` | 现为 tushare；A/B 可用 `variant="prefix"` |
| Beta / Strategy 净值 | `load_etf_510300()` / feed | ETF 仍 panel |
| Eng 冒烟 | 现有默认路径 | 报告数据集 SW flags ≠ 整体晋级 |
