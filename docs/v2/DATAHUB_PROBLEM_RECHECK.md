# DataHub 问题点独立复测（vs WorkBuddy 报告）

- **复测时间**：2026-10-10 12:42:49 ET
- **通道**：Mac Clash 代理 `http://100.102.49.98:7897` → `datahubco.com`
- **Base**：`http://datahubco.com/app-api/openapi/v1/tushare/<api>`
- **鉴权**：`X-API-Key`（来自 `.env.datasources`，本文不记录密钥）
- **对照**：WorkBuddy《Datahubco 接口验证报告》+ `DATAHUB_VERIFY_DIGEST.md`
- **原始明细**：`DATAHUB_PROBLEM_RECHECK_raw.json`（无密钥）
- **结论机读**：`DATAHUB_PROBLEM_RECHECK_summary.json`

> `promotion_approved=false`。本文件只做可用性真伪核对。

---

## 总表（相对 WorkBuddy）

| 主张 | WorkBuddy 说法 | 本轮结果 | 判定 |
|------|----------------|----------|------|
| `pro_bar` | 不支持 / 应跳过 | HTTP **400**，`X-Datahub-Validation=unknown_api`，msg=`api_name is not supported over HTTP: pro_bar` | **确认** |
| `stk_factor_pro` | 超时 / 502，应跳过 | 带 `ts_code` 时 HTTP **200** / `code=0`，`X-Data-Source=upstream`，21 行；缺 `ts_code` 才 400；偶发代理断开 | **推翻（部分）** |
| 8 个行业专题 | 上游直接拒 / 已死 | 全部不可用：多为上游 `40101 请指定正确的接口名`；部分先见 **502** 空体 | **确认（不可用）**，拒绝形态略有差别 |
| `margin_detail` P0 | 本地缓存静默丢 SZ/BJ；强制 `fields=` 回源 | **20260930** 无 fields → `sqlite/LOCAL` 仅 **SH=2001**；带 `fields=`（含 `name`）→ `upstream` **SH+SZ+BJ=4454** | **确认**，但**随交易日变化** |

---

## 1) `pro_bar` — 确认：HTTP 不支持

| 用例 | HTTP | code | msg | Final-Reason | Validation |
|------|------|------|-----|--------------|------------|
| `ts_code+start+end+freq=D` | 400 | 400 | api_name is not supported over HTTP: pro_bar | local_validation | unknown_api |
| `ts_code+start+end` | 400 | 400 | 同上 | local_validation | unknown_api |
| `ts_code+adj+freq` | 400 | 400 | 同上 | local_validation | unknown_api |

- `X-Datahub-Authenticated=0`（本地校验即拦，未真正打上游）
- **对 Leo**：别碰成立；要用复权/多周期请拆 `daily` / `adj_factor` 等。

---

## 2) `stk_factor_pro` — 推翻「一律 502/超时」

| 用例 | HTTP | code | 行数 | Source / Cache | 说明 |
|------|------|------|------|----------------|------|
| `trade_date=20260930&limit=5`（无 ts_code） | 400 | 400 | 0 | — | msg=`this interface requires ts_code`；local `required_parameter` |
| `ts_code=000001.SZ&start_date=20260901&end_date=20260930` | **200** | **0** | **21** | upstream / MISS | 成功，宽表含 OHLC/市值/技术因子 |
| `ts_code+trade_date+limit=5` | **200** | **0** | **1** | upstream / MISS | 成功 |
| `trade_date+limit=1`（首轮） | 代理错误 | — | — | — | Clash/远端断开，**不是**稳定 502 业务码 |

**相对 WorkBuddy**：  
- **推翻**：在正确参数（必须 `ts_code`）下**可用**，不是「超时/502 死接口」。  
- **不确定**：全市场按日批量是否会慢/限流/偶发代理失败——本轮未压测。  
- **对 Leo**：不要写进「别碰」；若要用，**按票拉**并自己限速；QuantLab 主路径仍优先 `daily`+`daily_basic`。

---

## 3) 八个行业专题 — 确认：全部不可用

接口：`tmt_twincome` `tmt_twincomedetail` `bo_monthly` `bo_weekly` `bo_daily` `bo_cinema` `film_record` `teleplay_record`

| 形态 | 代表接口 | HTTP | 业务码 / msg | Final-Reason |
|------|----------|------|--------------|--------------|
| 网关/上游炸掉 | 首轮 `tmt_*` / `bo_monthly` / `bo_weekly` | **502** | 空 body | （无 Datahub 头） |
| 上游拒接口名 | `bo_daily` `bo_cinema` `film_record` `teleplay_record` 及改参后的全部 8 个 | **400** | **40101** / `请指定正确的接口名` | upstream_parameter；`X-Cache=ERROR` |

换日期/参数（如 `20240501`、`month=`、`start_date/end_date`）后，8 个仍全部 `40101`。

**相对 WorkBuddy**：  
- **确认**：这 8 个对 QuantLab **不可用，应跳过**。  
- 细微差别：不全是「直接拒」一种形态，也可能先 **502**，但结果一样——拿不到数。

---

## 4) `margin_detail` P0 — 确认有坑，且与日期相关

强制回源用的 fields：  
`trade_date,ts_code,name,rzye,rqye,rzmre,rqyl,rzche,rqchl,rqmcl,rzrqye`  
（本地默认字段**不含** `name`，带上 `name` 可逼出 upstream。）

### 主对照日 `trade_date=20260930`（WorkBuddy 典型场景）

| 请求 | HTTP | code | n | 市场分布 | X-Data-Source | X-Cache |
|------|------|------|---|---------|---------------|---------|
| `limit=5000` **无 fields** | 200 | 0 | **2001** | **SH=2001，SZ=0，BJ=0** | **sqlite** | **LOCAL** |
| 同上 + **fields=**（含 name） | 200 | 0 | **4454** | **SH=2001，SZ=2108，BJ=345** | **upstream** | **MISS** |

→ **静默丢深市+北交所**在该日 **复现成功**（HTTP/code 仍成功，无告警）。

### 多日抽查（摘要）

| trade_date | 无 fields | 有 fields | 解读 |
|------------|-----------|-----------|------|
| 20260930 | LOCAL 仅 SH 2001 | upstream 全市场 4454 | **P0 典型** |
| 20260929 | LOCAL 已是 SH+SZ+BJ 4454 | upstream 同 4454 | 本地缓存**有时完整** |
| 20261008 | upstream 4454 全 | upstream 4454 全 | 当日无 LOCAL 残缺 |
| 20261009 | upstream **仅 SH 2001** | upstream **仍仅 SH 2001** | **fields 也救不了**（上游当日本身不全或未就绪） |
| 20260630 | upstream 4372 全 | 同 | OK |
| 20260926 | n=0 | n=0 | 非交易日/无数据 |

**相对 WorkBuddy**：  
- **确认**：本地缓存可对部分交易日 **只回 SH、且 code=0 不报错**；强制 `fields=`（含本地没有的列如 `name`）可回源补 SZ/BJ。  
- **补充**：不是「每一天无 fields 都缺」；也不是「有 fields 就一定全」——最新日可能上游本身只有 SH。  
- **对 Leo**：要用融资融券明细 → **永远带 fields= 回源**，并做 **SH/SZ/BJ 计数验收**；缺市场就重试或换日。

---

## 给 Leo 的三行结论

### 已确认
- `pro_bar`：HTTP 明确不支持（`unknown_api`）→ 别碰。
- 8 个电影/台系专题：全部拿不到有效数据（502 或上游 `40101`）→ 别碰。
- `margin_detail`：本地缓存会在部分日期 **静默只给沪市**；`fields=` 强制回源后可拿回深/北（例：20260930 2001→4454）。

### 已推翻 / 需改口
- `stk_factor_pro` **不是**「一律超时/502」。带 `ts_code` 时本轮 **稳定 200**，可按票取数。WorkBuddy「别碰」过严；Digest 里「502→跳过」应改为「须 ts_code；批量慎用」。

### 仍不确定
- `stk_factor_pro` 全市场扫板的耗时/配额/稳定性（未压测）。
- `margin_detail` 最新交易日上游为何仅 SH（数据延迟还是权限/裁剪）。
- 8 专题 502 vs 40101 是否随网关负载切换（对业务无影响）。

---

## 建议写入 Digest 的修正

1. `stk_factor_pro`：从「别碰」改为「可用但须 `ts_code`；非主路径」。  
2. `margin_detail`：保留 P0；补充「按日验收三市场计数；最新日可能上游也不全」。  
3. `pro_bar` + 8 专题：维持跳过。
