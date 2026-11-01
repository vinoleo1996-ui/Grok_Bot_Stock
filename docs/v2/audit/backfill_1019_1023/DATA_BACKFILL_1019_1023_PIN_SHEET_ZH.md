# 补跑 1019–1023 数据/日历钉点表（Data 只读盘点）

- 作者：QuantLab Data 执行器
- 起草：2026-10-25T04:51:28-0400（America/New_York）
- 性质：**只读盘点 + 新文档**；**不写** `data/v2/**`；**不跑**中转拉取；**不伪造/不改**任何 `.ok`；不改驱动豁免；`live=false`
- 依据：主裁 **A**（仿 `docs/v2/audit/backfill_1014_1016/` + `BACKFILL_1014_1016_OK_REQUEST_ZH_r3_1.md`）；父代理确认 Arch 已签发补跑 `.ok`（见 §1）
- 本文**不声称可跑**。实跑前置见 §6。

## 1. Arch 已签补跑 .ok（引用，Data 未改）

| 项 | 值 |
|---|---|
| 路径 | `output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok` |
| sha256 | `9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714` |
| sha8 | `9e4359f9` |
| 签发回执 | `docs/v2/ARCH_DATA_BACKFILL_1019_1023_OK_SIGNED_ZH.md`（盘点时 sha `cb522fedc761274bc13b2d6b23a6a93f589de105c379594aca35ce249a0be542`） |
| date_list | `20261019,20261020,20261021,20261022,20261023` |
| allow_backfill | true |
| allow_run | true（**仅** date_list；`allow_run_scope=backfill_date_list_only`） |
| requires_dedicated_backfill_runner | **true** |
| forbid | 禁止用 `run_nightly_v1_dbincr_v3_1.py` 硬跑历史日（ET 日≠D） |
| expires_et | 2026-10-27T04:45:52-04:00 |
| enable_ok_sha256 | `4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73` |

**边界（与签发回执一致）**：本 `.ok` 授权补跑窗口与代码/日历钉，**不是** nightly 单日 `ok_type=run`。Eng 须交 **1019–23 专用补跑执行器包**，Arch **审 runner 后再实跑**。

## 2. 目标交易日（日历钉）

本地只读核：`data/v2/tushare_raw/trade_cal.parquet`（SSE）与 `data/v2/calendar/trade_cal_sse_pit.parquet` 一致——

| cal_date | is_open | pretrade_date | 备注 |
|---|---|---|---|
| 20261017 | 0 | 20261016 | 周末 |
| 20261018 | 0 | 20261016 | 周末 |
| **20261019** | **1** | 20261016 | 目标 |
| **20261020** | **1** | 20261019 | 目标 |
| **20261021** | **1** | 20261020 | 目标 |
| **20261022** | **1** | 20261021 | 目标 |
| **20261023** | **1** | 20261022 | 目标 |
| 20261024 | 0 | 20261023 | 周末（今日起草日为周日） |
| 20261025 | 0 | 20261023 | 周末 |

**目标列表（5 个交易日）**：`20261019`–`20261023`。

### 2.1 日历文件路径 + sha256（盘点时）

| 角色 | 路径 | sha256 | 备注 |
|---|---|---|---|
| Eng/纸面 trade_cal（.ok `pin_trade_cal`） | `data/v2/tushare_raw/trade_cal.parquet` | `141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086` | 与 Arch .ok 一致 |
| SSE PIT | `data/v2/calendar/trade_cal_sse_pit.parquet` | `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` | manifest 钉同表 |
| calendar manifest | `data/v2/calendar/manifest.json` | （盘点 sha8 `7ccc911e…`；内容声明表 sha=`fa4260b8…`） | MUST_NOT_CHANGE 候选 |
| asof_extend sessions | `data/v2/asof_extend_202610/calendar.parquet` | `bf0c33f27ee160a05fe31e9ebb1fe8363389020931d9c5545821b1e8f9aa9a2c` | **仅至 20261016**（n=3107）；1019–23 **不在**该表 |

## 3. 数据缺口表（只读）

### 3.1 daily_basic（主缺口）

| 资产 | last_date（盘点） | 1019–23 | 缺口结论 |
|---|---|---|---|
| `data/v2/tushare_raw/daily_basic/{D}.parquet` | **20261016**（Oct 文件：08/09/12–16） | 5 日文件均 **不存在** | **全缺** 1019–23 |
| `data/v2/valuation/daily_basic_full_tushare.parquet` | trade_date max **2026-10-16**（manifest 同）；rows=12309945 | 五日行数=0 | **全缺**；manifest sha8 `8c2c978b…` |
| `data/v2/valuation/daily_basic_valuation_tushare.parquet` | trade_date max **2026-10-09**（main）；+ ext 仅 **2026-10-12** | 五日行数=0 | **全缺**（较 full 更旧） |
| `data/v2/valuation/daily_basic_valuation_tushare_ext_20261012.parquet` | 仅 20261012 | 无 | 非本窗口 |

### 3.2 旁证缺口（非本包必跑范围，供 Eng/Arch 裁 scope）

| 资产 | last（盘点） | 1019–23 |
|---|---|---|
| `data/v2/tushare_raw/cyq_perf/{D}.parquet` | Oct 最后 **20261013** | 五日均缺 |
| `data/v2/tier3_daily/{anns,news,research_report,concept_dc_index,concept_dc_member}/` | Oct 最后 **20261015** | 五日均缺 |
| `asof_extend_202610/calendar.parquet` sessions | max **20261016** | 五日均不在表内 |

> 本钉点表聚焦 **daily_basic incr v3.1 启用后的五日补跑**；cyq/tier3/asof 是否纳入专用执行器 **由 Eng 包 + Arch 审 runner 决定**，Data 不扩权。

## 4. 依赖 enable / 代码钉（只引用，不改）

盘点时磁盘复核：

| 键（.ok / Eng SHA_KEYS） | 路径或语义 | 钉值 | 盘点 |
|---|---|---|---|
| `sha_daily_basic_incremental` | `scripts/acquire/daily_basic_incremental.py` | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` | **MATCH** |
| `pin_daily_basic_transform` | `__computed__/daily_basic_transform_sha`（非单文件；见 Eng `ENG_SHA_KEYS_INCR_TRANSFORM_20261025_ZH.md`） | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | 按 Eng/Arch 钉引用；本步未重算 transform |
| `sha_driver`（nightly 驱动，**禁止**硬跑历史日） | `docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py` | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` | **MATCH** |
| `sha_nightly_update` | （.ok 字段） | `2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b` | 引用 .ok |
| `sha_tier1_materialize` | （.ok 字段） | `7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c` | 引用 .ok |
| enable `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_ENABLE.ok` | `4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73` | 已存在；Eng 已签收 |

## 5. 中转探针状态（阻断实跑前置）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/relay_probe_20261025/RELAY_PROBE_RECEIPT_20261025T0448ET.md` |
| sha256 | `5d208af69e4c111e058edb36ef6a3a5663093ffdaebe27a17a3956a7980bddd3` |
| sha8 | **`5d208af6`** |
| 结论 | **不通**：trade_cal / stock_basic 均 SSLError（`UNEXPECTED_EOF_WHILE_READING` → Max retries）；无 HTTP 200、无 rows |
| 脚本 | 重建 `probe5_small` sha `1c3999c7…`（原钉 `601a092f…` 丢失；PIN_MISMATCH_REBUILT） |

### 硬声明

> **签 .ok 后的实跑、以及任何生产写入，须中转恢复并再探针通过后再进行。**  
> 当前 `5d208af6` = 不通 → **不可据此实跑 1019–23**。Arch 虽已签发窗口 `.ok`（`9e4359f9…`），仍受 `.ok` 内 `requires_dedicated_backfill_runner=true` 与探针失败双重约束。

## 6. 与 1014–1016 包差异（供 Eng 仿写专用执行器）

| 维 | 1014–1016（方案 R / r3.1） | 本窗口 1019–1023 |
|---|---|---|
| 目录 | `docs/v2/audit/backfill_1014_1016/` | `docs/v2/audit/backfill_1019_1023/`（本钉点表落此） |
| 目标日 | 3 日：1014/15/16；runner 以 `--date 20261016` 串 cyq→tier3/bundle | **5 日**：1019–23；聚焦 **daily_basic incr v3.1**（非 plan R cyq 主路径） |
| 执行器 | `run_backfill_r_v3_1.py` 等（已存在完整脚本+selftest） | **尚欠** Eng 专用 runner；本目录现有 `run_backfill_1019_1023_dbincr_v3_1.py.base` sha=`f1910e8a…` = **nightly 驱动字节副本**，内含 **ET==D** 闸门，**不能**直接当历史补跑执行器 |
| sha scope | `docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt`（`579c8605…`） | 本目录 `nightly_sha_scope_backfill_1019_1023.txt`（`428a05d4…`）源自 **10-19 日更/enable 包**，**不是**五日补跑专用 scope；另附草稿模板见 §7 |
| .ok 形态 | plan R 专用键（cyq/tier3 分允许等） | 已签 `ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok`（`9e4359f9…`）；要求专用 runner |
| 中转 | r3.1 要求两轮 trade_cal+stock_basic 通才申请 | **已有失败证据** `5d208af6`；通后再实跑 |
| 禁项 | 同：不改驱动豁免；quiet 闸门；RSS 停 | 同 + **禁止** nightly 驱动硬跑历史日 |

### 1014–1016 包结构备忘（仿写清单）

- 脚本：`run_backfill_r.py` → v2 → v3 → **v3_1**（现行参考 `c983aed3…`）
- selftest：`selftest_run_backfill_r_v3_1{,_b,_c}.py` + 回执
- OK 申请：`BACKFILL_1014_1016_OK_REQUEST_ZH_r3_1.md`（相对 r3 三处改动：执行器 v3、RESEARCH_QUIET 闸门、大分页改 stock_basic）
- 范围钉：`nightly_sha_scope_backfill_1014_1016.txt`

Eng 应交：仿上述结构交 **专用包**（runner + selftest + 五日 scope + 预检），**勿**把 `.base`/nightly 驱动改豁免后硬跑。

## 7. 同目录非执行清单

| 文件 | sha256（盘点） | 说明 |
|---|---|---|
| `DATA_BACKFILL_1019_1023_PIN_SHEET_ZH.md` | （本文件；写入后见回报） | 本钉点表 |
| `nightly_sha_scope_backfill_1019_1023.txt` | `428a05d4891ab1c37fb272870b4a1c721d98406748d638a100784a898caca0c5` | **既有**：enable/日更衍生；valuation 仍 MUST_NOT；**勿当作五日可跑 scope** |
| `SHA_SCOPE_BACKFILL_1019_1023_DRAFT_TEMPLATE.txt` | （见写入后 sha） | **新建草稿模板**：仅列缺口/钉点意图；**不可跑、未入快照工具** |
| `run_backfill_1019_1023_dbincr_v3_1.py.base` | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` | nightly 驱动副本；**非**专用补跑执行器 |

## 8. Data 本步未做 / 禁做

- 未写生产 `data/v2/**`；未中转拉取；未改驱动豁免；未伪造/覆盖 `.ok`
- 未声称可跑；未消费/移动 Arch `.ok`
- 未与叶25/paper/stream 混签

## 9. 请 Eng / Arch / 主

1. **Eng**：基于本钉点表 + 1014–1016 结构，交 1019–23 **专用**补跑执行器包（勿用 nightly ET==D 驱动硬跑）。
2. **Arch**：审 Eng runner 后，方可实跑；实跑前须中转探针 **通过**（取代 `5d208af6` 不通结论）。
3. **主**：编排上「`.ok` 已签 ≠ 可跑」——卡点为 **中转通 + 专用 runner 审过**。

live=false。
