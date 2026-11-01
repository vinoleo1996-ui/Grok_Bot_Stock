# Data 回执：夜更 D=20261026 DONE marker — **未写（GAP）**

| 项 | 值 |
|---|---|
| 角色 | QuantLab Data |
| 时刻（America/New_York） | `2026-10-26T18:41:53-04:00`（墙钟 2026-10-26 18:41:53 EDT） |
| **结论** | **NO_DONE_MARKER**（未达 DONE 标准；**未**写 `output/nightly_markers/nightly_20261026.DONE.json`） |
| 主令 | A18 CONSUME 后写 DONE；未达则列缺口、勿假 DONE |
| live | false |

## 1. 已核验（MATCH）

| 项 | 结果 |
|---|---|
| baseline 路径 | `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` |
| baseline sha256 | `273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486`（sha8 **`273163cc`**）**PRESENT MATCH** |
| dest sha256 | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948`（sha8 `f6bbf9e5`）未改 |
| manifest sha256 | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8`（sha8 `8c2c978b`）未改 |
| Eng D1 MD/JSON | sha8 **`0ddeb1b7`** / **`1a50b8a5`**（全长见上） |
| Arch CONSUME | sha8 **`9758452c`**；`.ok` `a62881b9` → `_consumed/...CONSUMED_PASS...` |
| 夜更回执 | sha8 **`4013af82`**（`docs/v2/audit/nightly_20261026/NIGHTLY_RECEIPT_20261026_ZH.md`） |
| 纸面 ABORT | sha8 **`665232a5`**（`output/loop/paper_daily_20261026/READINESS_ABORT_20261026.md`；2a 无 marker） |
| baseline 字节 | **未改**（禁令遵守） |
| enable `4377eb59` | **未复用**；`allow_run=false` |
| 候选3 enable | **未触** |

## 2. freshness / REQUIRED（相对 D=`20261026` / P=`20261023`）

`daily_update_status.json`：status=**`partial`**；target_trade_date=`2026-10-26`。

`data_freshness_status.json`：overall=**`stale`**；expected_trade_date=`20261023`；stale_tables=`['daily_basic', 'mid_large_universe']`。

| REQUIRED 表 | last_date | rows | vs D=20261026 |
|---|---|---:|---|
| `etf_daily_adj` | 20261026 | 1575090 | **PASS** |
| `daily_ohlcv_raw_pit` | 20261026 | 100135 | **PASS** |
| `daily_basic` | 20261016 | 12309945 | **FAIL_last_date≠D** |
| `mid_large_universe` | 20261016 | 5565449 | **FAIL_last_date≠D** |
| `etf510300` | 20261026 | 3501 | **PASS** |
| `asof_ts` | 20261026 | None | **PASS** |

| manifest.has_build | **False** |
| manifest.date_max / rows | `2026-10-16` / 12309945 |
| incr 前置 `build.new_sha256` | **ABSENT** → 仍会 `DB_INCR_PRECOND` rc=20（A18） |
| baseline.raw_inventory_end | `20261016`（§5.3 钉终点；**尚未**物化续写至 D） |

## 3. 合法补跑评估（本回合）

| 候选动作 | 是否可做 | 原因 |
|---|---|---|
| 写假 DONE.json | **否** | REQUIRED `daily_basic`/`mid_large_universe` last≠D；status≠ok；驱动规则「6 张 REQUIRED 不全 → FAILED」；主令勿假 DONE |
| 跑 daily_basic incr / 物化 | **否** | 无新 `allow_run` `.ok`；enable `4377eb59` allow_run=false；Arch CONSUME 禁 seed/allow_run/物化；禁复用旧票 |
| seed `manifest.build` from baseline | **否** | 须 Arch/主另签；本票禁盲 seed；禁改 A18 baseline 字节 |
| 补 mid_large / freshness 重写 | **否** | 依赖估值物化后的合法 call-B；无授权 |
| hsgt/cyq/tier3 | **否** | 夜更已 RELAY_DOWN；属 WARN 白名单，但非本回合阻塞主因 |

**本回合唯一动作**：落本 GAP 回执；**不**创建 `output/nightly_markers/`；**不**写 DONE/FAILED marker。

## 4. 缺口清单（达 DONE 前必须）

1. **Arch/主另签**：baseline→`manifest.build`（含 `new_sha256`）种子票（≠盲 seed；钉 baseline `273163cc` + dest `f6bbf9e5`）。
2. **Arch/主另签**：daily_basic incr **allow_run**（覆盖缺口日至少 `20261019`–`20261023`+`20261026`；**勿复用** enable `4377eb59`）。
3. Data/Eng 合法补跑物化 → `daily_basic` last_date=`20261026`；再补 `mid_large_universe`（及 call-B 必要步）。
4. `daily_update_status.status=ok` 且 REQUIRED 六表 last_date==D 后，再由 Data 按驱动契约写 `output/nightly_markers/nightly_20261026.DONE.json`（steps[] sha/rows 交叉钉；cyq/tier3/hsgt 可 WARN+GAP_LIST）。
5. 然后主再令 Eng 重跑纸面 D=20261026（仍禁 `--force`）。

## 5. 禁区回执

- **未**写 `nightly_20261026.DONE.json` / `.FAILED.json`
- **未**改 baseline / parquet / manifest
- **未** seed / allow_run / 物化 / 复用 `4377eb59` / 候选3 enable
- **未** `--force` 纸面；**未**报 Leo
- live=false

---
文档结束（Data · DONE marker GAP；请主排种子+allow_run）
