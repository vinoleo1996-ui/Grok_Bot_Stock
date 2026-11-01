# 盘中/分钟线接口权限探测（小样本）

- 探测时间（箱内）: 2026-10-14T13:28:59
- 超时: 30s / 次
- 样本: {'ts_code': '000001.SZ', 'day': '20261013'}
- 源: relay=`pcd.mobcvb.cn` (TSPRO_PROXY_KEY)；datahub=`datahubco.com` (DATAHUB_API_KEY + DATAHUB_HTTP_PROXY)
- 未动 PID 4151716/243082；未启 8787；未碰 moneyflow；无大批量拉取

| 接口 | 参数摘要 | relay/promax | datahub |
|---|---|---|---|
| `realtime_quote` | `{"ts_code": "000001.SZ"}` | **未登记/未开通** (1.65s) | **未登记/未开通** (0.78s) |
| `rt_k` | `{"ts_code": "000001.SZ"}` | **成功** (4.77s) | **无权限** (0.65s) |
| `rt_min` | `{"ts_code": "000001.SZ", "freq": "1MIN"}` | **成功** (1.69s) | **无权限** (0.63s) |
| `stk_mins` | `{"ts_code": "000001.SZ", "freq": "1min", "start_date": "20261013", "end_date": "20261013"}` | **成功** (1.65s) | **无权限** (0.63s) |
| `pro_bar` | `{"ts_code": "000001.SZ", "freq": "1min", "start_date": "2026-10-13", "end_date": "2026-10-13"}` | **成功** (2.08s) | **无权限** (0.67s) |

## 报错原文
- **realtime_quote / relay** → 未登记/未开通: `HTTP 404 code=None msg=未登记的接口: realtime_quote`
  - raw: `{"ok": false, "error": "unknown_api", "message": "未登记的接口: realtime_quote"}`
- **realtime_quote / datahub** → 未登记/未开通: `HTTP 403 code=403 msg=[api_not_enabled] API name is unknown or not enabled on this site; check the supported interface guide`
  - raw: `{"code": 403, "msg": "[api_not_enabled] API name is unknown or not enabled on this site; check the supported interface guide", "data": null, "help": {"guide": "https://datahubco.com/customer_sdk_calling_guide.md", "retry_same_request": fals`
- **rt_k / relay** → 成功: `HTTP 200 code=0 rows=1 msg=ok`
  - raw: `{"request_id": "", "code": 0, "msg": "ok", "data": {"fields": ["ts_code", "name", "pre_close", "high", "open", "low", "close", "vol", "amount", "num"], "items": [["000001.SZ", "平安银行", 11.57, 11.72, 11.57, 11.51, 11.52, 58297636, 677987519.1`
- **rt_k / datahub** → 无权限: `HTTP 403 code=403 msg=[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API`
  - raw: `{"code": 403, "msg": "[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API", "data": null, "help": {"guide": "https://datahubco.com/customer_sdk_calling_guide.md", "retry_same_request": false, "max`
- **rt_min / relay** → 成功: `HTTP 200 code=0 rows=1 msg=ok`
  - raw: `{"request_id": "", "code": 0, "msg": "ok", "data": {"fields": ["ts_code", "trade_time", "freq", "open", "high", "low", "close", "vol", "amount"], "items": [["000001.SZ", "2026-10-14 09:36:00.000", "1MIN", 11.66, 11.66, 11.64, 11.64, 641400,`
- **rt_min / datahub** → 无权限: `HTTP 403 code=403 msg=[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API`
  - raw: `{"code": 403, "msg": "[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API", "data": null, "help": {"guide": "https://datahubco.com/customer_sdk_calling_guide.md", "retry_same_request": false, "max`
- **stk_mins / relay** → 成功: `HTTP 200 code=0 rows=240 msg=`
  - raw: `{"request_id": "", "code": 0, "msg": "", "data": {"fields": ["ts_code", "trade_time", "freq", "open", "high", "low", "close", "vol", "amount"], "items": [["000001.SZ", "2026-10-13 14:59:00", "1MIN", 11.57, 11.57, 11.57, 11.57, 2452900, 2838`
- **stk_mins / datahub** → 无权限: `HTTP 403 code=403 msg=[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API`
  - raw: `{"code": 403, "msg": "[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API", "data": null, "help": {"guide": "https://datahubco.com/customer_sdk_calling_guide.md", "retry_same_request": false, "max`
- **pro_bar / relay** → 成功: `HTTP 200 code=0 rows=240 msg=ok`
  - raw: `{"request_id": "", "code": 0, "msg": "ok", "data": {"fields": ["ts_code", "trade_time", "freq", "open", "high", "low", "close", "vol", "amount"], "items": [["000001.SZ", "2026-10-13 14:59:00", "1MIN", 11.57, 11.57, 11.57, 11.57, 2452900, 28`
- **pro_bar / datahub** → 无权限: `HTTP 403 code=403 msg=[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API`
  - raw: `{"code": 403, "msg": "[api_scope_denied] API is outside this site's 15000-point product scope; stop retrying this API", "data": null, "help": {"guide": "https://datahubco.com/customer_sdk_calling_guide.md", "retry_same_request": false, "max`

## daily_basic 给 Eng 的结论（附）
- 现表 mtime: 2026-10-13 23:42 ET；sha256 前缀 `3356730c…`；大小 744049878
- 重写前备份 `backups/valuation/daily_basic_full_tushare.20261014_1136.parquet` sha 前缀 `4820339f…`
- 与备份在 `ts_code,trade_date,close,pe_ttm,pb,total_mv,turnover_rate,volume_ratio` 上 **hist exact equals=True**；行数均为 12,293,250；无重复键；max trade_date=2026-10-13
- 结论：文件级 sha/大小因 parquet 重写变化，但 trade_date≤10-13 历史内容未改。中间曾有 dupbug 备份（23:37 ET）已去重恢复。
- capacity_adv 若锁的是**内容切片哈希**可不重算；若锁的是**文件字节 sha** 需按新 sha 更新。
