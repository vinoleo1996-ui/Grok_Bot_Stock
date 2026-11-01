# S1 舆情 PIT 冻结接口（Data 交付契约）

研究级。对应 `docs/v2/V3_S1_SENTIMENT_BETA_PREREG.md`。  
**未交付前 Beta 不得开跑。**

## 路径
- 主表：`data/v2/sentiment/xueqiu_heat_pit.parquet`（可多源分表，见下）
- 主表：`data/v2/sentiment/ths_heat_pit.parquet`
- 市场级（可选）：`data/v2/sentiment/market_pulse_pit.parquet`
- 校验清单：`output/v3/s1/data_ready_checklist.json`（由 Data 填写）

## 必需字段（证券级日频）
| 字段 | 类型 | 含义 |
|---|---|---|
| `trade_date` | date | 交易日 |
| `source` | str | `xueqiu` / `ths` / … |
| `instrument` | str | `sh.600000` 或市场级 `MARKET` |
| `heat` | float | 讨论/关注热度（非负） |
| `sentiment_score` | float | 情绪分数（事先定义域，如 [-1,1]） |
| `available_at` | datetime | PIT 可交易知晓时刻；**不得早于平台可查时刻**；建议 ≥ T 18:00 Asia/Shanghai 或次日开盘前 |
| `promotion_approved` | bool | 必须 false 直至 Leo |

可选：`n_posts`, `n_unique_users`, `meta_json`。

## PIT 规则
- Beta 只用 `available_at` 的日历日 < 调仓信号日 T（若 available_at 为 T 18:00，则最早 T+1 开盘用）。  
- 禁止用当日盘中热度做当日收盘调仓。

## 校验（Data）
1. 无未来 `available_at`；时区明确。  
2. 探索窗 X1/X2 覆盖率报告。  
3. 断档与平台改版日列表。  
4. `output/v3/s1/schema.json` 字段一致。
