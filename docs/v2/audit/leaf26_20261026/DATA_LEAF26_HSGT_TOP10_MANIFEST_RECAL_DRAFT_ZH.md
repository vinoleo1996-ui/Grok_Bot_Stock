# Data：叶26 hsgt_top10 manifest 重算草案（**禁止覆盖生产**）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 约束：只读文件；DRAFT JSON 仅审计目录；**禁止**覆盖 `data/v2/northbound/hsgt_top10_manifest.json`

---

## 1. 当前文件 vs 生产 manifest（复测无 DELTA）

| 源 | max trade_date | rows | days | parquet sha |
|---|---|---|---|---|
| 文件 `hsgt_top10_daily_2018plus.parquet` | **20261016** | **38364** | **2033** | `c54935e82c8372bb5ac37023a4319ea16eff7f9fbc0aa03ef3106937f59a42f1` |
| 生产 `hsgt_top10_manifest.json` sha `4d5e6f5d…` | 止 **20261013** | 38304 | 2030 | 内嵌 `94fdb347…`（**≠**当前文件） |
| `northbound_summary.json` sha `85e87ac5…` | 止 **20261016** | 38364 | 2033 | 与文件 **对齐** |

漂移：manifest 落后文件 3 个交易日 / 60 行；内嵌 sha 过期。消费侧以 **文件** 为准。

---

## 2. 应按当前文件写入的字段（草案）

```json
{
  "table": "northbound/hsgt_top10_daily_2018plus.parquet",
  "rows": 38364,
  "days": 2033,
  "date_range": ["20180102", "20261016"],
  "available_at": "trade_date 18:00 Asia/Shanghai",
  "promotion_approved": false,
  "sha256": {
    "northbound/hsgt_top10_daily_2018plus.parquet": "c54935e82c8372bb5ac37023a4319ea16eff7f9fbc0aa03ef3106937f59a42f1"
  }
}
```

完整 DRAFT（含 delta 说明）：  
`docs/v2/audit/leaf26_20261026/hsgt_top10_manifest.DRAFT.json`  
（由当前文件只读重算；`/tmp` 同源副本 sha 见总回执）

---

## 3. 校准步骤（须 Arch `.ok`；本回合不执行）

1. 备份现生产 manifest → `_recovery/`。  
2. 用 DRAFT 字段重写 rows/days/date_range/内嵌 sha（保留 vendor_empty 等历史字段须人工合并）。  
3. 再 sha256sum 钉进 TEAM/回执。  
4. **本回合未** `mv` 覆盖生产。

---

## 4. 状态

**仍 PARTIAL**（文件可用；catalog 漂移未修）。推进：应写值算清 + DRAFT JSON 落审计目录。
