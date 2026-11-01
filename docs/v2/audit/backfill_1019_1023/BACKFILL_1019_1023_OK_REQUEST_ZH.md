# 1019–1023 专用补跑 runner .ok 申请（Eng；待 Arch runner 审）

- 作者：QuantLab Eng；起草 2026-10-25T04:58:08-04:00（America/New_York）
- 依据：主 Agent 04:44 方案 A；Arch 窗口授权回执 `docs/v2/ARCH_DATA_BACKFILL_1019_1023_OK_SIGNED_ZH.md`；Arch 补跑路径要求
- live=false；promotion=false；**未跑生产**；未改 nightly 驱动；未切例程

## 已有窗口授权（不是 runner 审）

| 项 | 值 |
|---|---|
| 路径 | `output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok` |
| sha256 | `9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714` |
| date_list | 20261019,20261020,20261021,20261022,20261023 |
| requires_dedicated_backfill_runner | true |
| allow_nightly_driver_for_historical_dates | false |

请 Arch **审 runner + scope + selftest** 后签 **专用补跑 runner .ok**（建议路径 `output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER.ok`），或在审回执写 PASS。未审前 Eng/Data **不跑**生产补跑。

## 交付包

目录：`docs/v2/audit/backfill_1019_1023/`

| 文件 | sha256 |
|---|---|
| `run_backfill_1019_1023_dbincr_v3_1.py` | `fe2deceef2cbce291e23ea96de5b9b8096d64f60791e1002b647912ff561d814` |
| `selftest_run_backfill_1019_1023_dbincr_v3_1.py` | `7f4fb2a6021b2f2d76f28a09713be319f6898c0aa838fc02d4eda601d059376e` |
| `SELFTEST_RECEIPT_20261025.txt` | `2d37f00cc542642a1566bc3642b6e7bd586725362410cd9c98600211110e5a53` |
| `nightly_sha_scope_backfill_1019_1023.txt` | `c204fd5f8274ae58cf99d936c39409cb4fb5ca6e9f94a6a86bb55e4f7b0e48e8` |
| `DIFF_vs_planR_and_nightly_driver_ZH.md` | `1d78ff989e326b5eb3bd2da530e0a2435d64096f2473fef1dfb0f8acf4cad0f4` |
| `BACKFILL_1019_1023_OK_REQUEST_ZH.md` | （本文；见 PACK_META） |
| `PACK_META.json` + `PACK_META.sha256` | （外置；勿自指） |

## 现盘钉（check_pins PASS）

| 键 | 钉值（前 16） | 路径/语义 |
|---|---|---|
| sha_driver_ref | f1910e8ab054c306 | nightly 驱动参考钉（**不调用**跑历史日） |
| sha_nightly_update | 2b4704e88a45e8bb | scripts/nightly_update.py |
| sha_daily_basic_incremental | a7ac54b3ecdf33d3 | scripts/acquire/daily_basic_incremental.py |
| pin_daily_basic_transform | 308b5054c3980111 | computed |
| sha_tier1_materialize | 7205ba43b4e4dc50 | scripts/acquire/tier1_materialize.py |
| pin_trade_cal | 141078fa6da0ef94 | data/v2/tushare_raw/trade_cal.parquet |
| sha_tier1_pull | 5b70dfed08a23703 | scripts/acquire/tier1_pull.py |
| sha_scope | c204fd5f8274ae58 | 本包 scope |
| enable_ok_sha256 | 4377eb592c18c3be | 已消费 enable |
| backfill_auth_ok_sha256 | 9e4359f9b6521e9d | 窗口授权 |
| 其余 SHA_KEYS | 与驱动表一致 | cal_restore_v2 / cal_compare / snapshot / proxy / relay_health / 各步骤脚本 / routine_fallback |

## CMD 形状（每 D 串行）

```
Call A: /usr/bin/python3 scripts/nightly_update.py --date D --steps daily_pull
  env: PYTHONDONTWRITEBYTECODE=1 TSPRO_RELAY_TIMEOUT=115 TIER1_SKIP_CAL_REFRESH=1
  SOURCE=relay 仅当 .ok source_relay_only=true
  → compare → cal_restore_v2 → 双核 pin_trade_cal（失败 P0）

Call B: --steps index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness
  → 再恢复链 + summary/REQUIRED_TABLES/freshness/trade_cal/scope compare
```

**禁止**：`run_nightly_v1_dbincr_v3_1.py --date <历史日>`（包内 `forbid_nightly_driver_invocation` 硬拒）。

## 闸门

- RESEARCH_QUIET.lock；healthz quiet；≥15s；括号 pgrep web 空；MemAvailable≥2.5GiB；串行
- BLACKOUT 16:40–18:40；HARD_STOP 15:55；**叶25 10:00–10:45** 硬停/不起
- 94322/94403：只核 T/Z/absent；不 STOP/CONT
- `--check-only` 退出 10（可不要求 runner .ok 已存在；正式跑必须）

## 自测

- `/tmp` 假数据；25/25 PASS（见 `SELFTEST_RECEIPT_20261025.txt`）
- `py_compile` 过；现盘 `check_pins` / `check_auth_ok` PASS
- 未写生产 data/；未移动 .ok；未启跑

## 建议 runner .ok 字段（Arch 填）

```
ok_id=ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER
ok_type=backfill_runner
sha_runner=fe2deceef2cbce291e23ea96de5b9b8096d64f60791e1002b647912ff561d814
backfill_auth_ok_sha256=9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714
requires_dedicated_backfill_runner=true
sha_driver_ref=f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05
date_list=20261019,20261020,20261021,20261022,20261023
# + 全表 SHA_KEYS（与执行器一致）
live=false
promotion_approved=false
allow_paper=false
allow_stream=false
call_b_budget_min=75
expires_et=<Arch 填>
```

## 请 Arch 确认

1. runner 源码 + scope + selftest 是否可签专用 runner .ok？
2. 叶25 窗 / HARD_STOP 15:55 是否接受（五日可能需多日窗内分段跑）？
3. 签后由 Data 还是 Eng 执跑（live=false）？

未审前不跑。
