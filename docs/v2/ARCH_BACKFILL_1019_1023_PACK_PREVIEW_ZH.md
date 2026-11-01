# Arch 预审：1019–23 专用补跑执行器包

- 审阅方：QuantLab Arch（审查执行器）
- 时刻：2026-10-25T05:08:08-04:00（America/New_York）
- 包目录：`docs/v2/audit/backfill_1019_1023/`
- 依据：主裁方案 A；窗口授权 `9e4359f9…`；CONSUME_SUSPEND 仍在；主令 **先审包、不开跑**
- **live=false**；本审 **未**签 runner/实跑窗 .ok；**未**消费窗口授权；**未**写生产；**未**改主干；**未** commit

## 结论

**PACK_PREVIEW_PASS_WITH_CONDITIONS**

包本身（runner / scope / selftest / 钉点 / 禁方案 B）可接受，对齐窗口授权与方案 A。  
**条件（开跑仍阻塞，本轮不签实跑）**：

1. `ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND` **仍生效** → 禁签 runner 实跑窗、禁写生产。
2. 中转 **stock_basic 未两通**（trade_cal 已 PASS；stock_basic 仍超时/不稳）→ 解除暂缓前置未闭合。
3. 须另签专用 `ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER.ok`（本轮 **故意不签**）。

给 Eng/主一句话：**包预审过（PASS_WITH_CONDITIONS）；维持 SUSPEND，探针 stock_basic 通后再议 runner 实跑 .ok。**

## sha 表（复算）

| 文件 | 宣称 / 期望 | 复算 sha256 | 结果 |
|---|---|---|---|
| `run_backfill_1019_1023_dbincr_v3_1.py` | `fe2decee…` | `fe2deceef2cbce291e23ea96de5b9b8096d64f60791e1002b647912ff561d814` | **MATCH** |
| `nightly_sha_scope_backfill_1019_1023.txt` | `c204fd5f…` | `c204fd5f8274ae58cf99d936c39409cb4fb5ca6e9f94a6a86bb55e4f7b0e48e8` | **MATCH** |
| `selftest_run_backfill_1019_1023_dbincr_v3_1.py` | `7f4fb2a6…` | `7f4fb2a6021b2f2d76f28a09713be319f6898c0aa838fc02d4eda601d059376e` | **MATCH** |
| `SELFTEST_RECEIPT_20261025.txt` | `2d37f00c…` | `2d37f00cc542642a1566bc3642b6e7bd586725362410cd9c98600211110e5a53` | **MATCH** |
| `BACKFILL_1019_1023_OK_REQUEST_ZH.md` | `ecc20423…` | `ecc204238e2a157b25b9b175ef45b990f49fc1d1faa7a1d14139778c701f5b23` | **MATCH** |
| `ENG_BACKFILL_1019_1023_PACK_RECEIPT_ZH.md` | （SHA256SUMS） | `d53e7dfdd7024466bfd1f1e99bf74132fdd5658a79a7124191d4d186a8a89d7b` | **MATCH** |
| `DIFF_vs_planR_and_nightly_driver_ZH.md` | `1d78ff98…` | `1d78ff989e326b5eb3bd2da530e0a2435d64096f2473fef1dfb0f8acf4cad0f4` | **MATCH** |
| `PACK_META.json` | `d278ab60…` | `d278ab60ef9014f56f0bb44249a25321be97d3ece5d9c1c22f9af64a51d584ee` | **MATCH**（与 `PACK_META.sha256` 一致） |
| `DATA_ENG_PACK_PIN_ALIGN_20261025T0501ET.md` | `730ebca8…` | `730ebca8111bacb49586e22dc91fcd0b8ba7eb11c8eff1023ed102e37e6adc5f` | **MATCH** |
| 窗口授权 `.ok`（只读对照，未消费） | `9e4359f9…` | `9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714` | **MATCH** |

`SHA256SUMS.txt` 内 8 项与现盘逐文件复算全部 MATCH。

## 审查清单

### 1. 目录清单齐全；宣称 sha 复算 MATCH

**PASS** — `docs/v2/audit/backfill_1019_1023/` 含 runner、selftest、SELFTEST 回执、scope、REQUEST、DIFF、PACK_META(+sha)、Eng 回执、Data PIN_SHEET / SCOPE_SUPPLEMENT / trade_cal 证据 / PIN_ALIGN。Eng 宣称 runner `fe2decee…`、scope `c204fd5f…`、PIN_ALIGN `730ebca8…` 均复算 MATCH。

### 2. runner 不是 nightly 驱动硬跑历史日；date_list=1019–23；ET≠D 合法

**PASS** — `run_backfill_1019_1023_dbincr_v3_1.py:34` `DATE_LIST=["20261019"…"20261023"]`；`:41` `FORBIDDEN_DRIVER_BASENAME=run_nightly_v1_dbincr_v3_1.py`；`:976-980` `forbid_nightly_driver_invocation` 硬拒 argv 含该驱动；`:960-961` `start_window_check` 明文「不要求 ET 日==D」；只调 `scripts/nightly_update.py`（Call A/B）。对照 DIFF `DIFF_vs_planR_and_nightly_driver_ZH.md` 与仿 `backfill_1014_1016/run_backfill_r_v3_1` 闸门形态一致。`--date` 单日亦须 ∈ DATE_LIST（`:1625-1626`）。

### 3. 钉齐与窗口授权一致；SHA_KEYS 闭合

**PASS** — runner `SHA_KEYS`（23 键，`:68-92`）含并钉死：

| 键 | 钉值（完整） | 与 auth .ok |
|---|---|---|
| sha_driver_ref / auth sha_driver | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` | MATCH |
| sha_nightly_update | `2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b` | MATCH |
| sha_daily_basic_incremental | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` | MATCH |
| pin_daily_basic_transform | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | MATCH |
| sha_tier1_materialize | `7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c` | MATCH |
| pin_trade_cal | `141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086` | MATCH |

现盘 `check_pins()` → `None`（PASS）；`check_auth_ok()` → 无错。Data `PIN_ALIGN_PASS`（`730ebca8…`）与本审一致。`check_runner_ok` 要求将来 runner .ok 含全表 SHA_KEYS（`:864-868`）。

### 4. selftest 25/25 证据可核；无假绿

**PASS** — 原回执 `SELFTEST_RECEIPT_20261025.txt` 记 `pass=25 fail=0`、exit 语义清晰。Arch **只读复跑**同脚本（/tmp 假数据，非生产）：再次 `pass=25 fail=0`、进程 `EXIT:0`（2026-10-25T05:05:48-04:00）。自测含：py_compile、DATE_LIST、forbid nightly、leaf25/blackout、stop_tree 序、summary 陈旧拒、现盘 check_pins/check_auth_ok。失败会 `sys.exit(1)`（selftest `:153`），非 exit0 掩盖。

### 5. 内存 RSS≤1.5GB；串行/静默锁/healthz 前置

**PASS** — `:100-101` `RSS_STOP_KB=1484800`、`RSS_HARD_KB=1536000`（与 auth `rss_stop_kb`/`rss_hard_kb` 一致）；`:42` `MEM_AVAILABLE_MIN_KB=2621440`（2.5GiB）；`:114-115` `RESEARCH_QUIET.lock` + `healthz`；`:116-118` 串行 pgrep（web/data）；date_list 串行一次一真实数据进程（模块头 `:11`）。叶25 / BLACKOUT / HARD_STOP 15:55 硬闸（`:43,:112-113,:536-539`）。

### 6. 写生产范围仅 date_list；禁纸面/叶25/enable 混用

**PASS** — date_list 钉死五日；scope 将 valuation/daily_basic* 标 EXPECTED_CHANGE 且按 1019–23 路径注释；paper/stream/live/promotion 在 auth 与 runner.ok 校验中强制 false（`:816-818,:871-873`）；叶25 硬停；enable 仅核 `enable_ok_sha256` 钉、不混 enable 签。Marker/quiet purpose 绑定 `backfill_1019_1023*`（`:988-1005`）。

### 7. REQUEST 是否越权申请「立刻开跑」

**WARN** — `BACKFILL_1019_1023_OK_REQUEST_ZH.md` **未**写「立刻开跑/立刻写生产」；明文「未审前不跑」「生产跑未做」。但仍在 SUSPEND + stock_basic 未通时，向 Arch 问「是否可签专用 runner .ok」（§请 Arch 确认 #1）。**Arch 裁：包可预审通过，但拒签实跑 runner .ok 直至探针两通并解除 CONSUME_SUSPEND。** 非假开跑申请，属时机过早的签跑询问。

## 开跑仍阻塞项

| 项 | 状态 |
|---|---|
| CONSUME_SUSPEND | **仍在**（`docs/v2/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_ZH.md` + `output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt`） |
| trade_cal 探针 | 已有 PASS 回执（0455/hosts 后）；非本包缺陷 |
| stock_basic 探针 | **未闭合**（ReadTimeout / 不稳） |
| 专用 runner .ok | **未签**（本轮预审故意不签） |
| 窗口授权 9e4359f9 | 字节未动、**暂缓消费** |

**缺口（可立刻修、非挡预审）**：runner 源码 **未**读取 `CONSUME_SUSPEND` 标记（依赖 Arch 不签 runner.ok 做外部门禁）。建议将来 runner.ok 落地前，Eng 加一行：若 `output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_*.txt` 存在则 hard-fail——**非本轮必改，记 WARN**。另：`OK_KEYS_REQUIRED` 仍列 nightly 风格 `sha_driver`（`:134-137`），而 `check_runner_ok` 实际认 `sha_driver_ref|sha_driver`；属模板残留，不影响现逻辑。

## 建议将来 runner 实跑 .ok 字段草案（**勿真签**）

```
format=quantlab_run_auth_v1
ok_id=ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER
ok_type=backfill_runner
ok_path=output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023_RUNNER.ok
signed_by=arch
issuer=QuantLab Arch
sha_runner=fe2deceef2cbce291e23ea96de5b9b8096d64f60791e1002b647912ff561d814
backfill_auth_ok_sha256=9e4359f9b6521e9d8d2b9578c7031ac6e79d42bd7dc4e3003e34a7c0c3e32714
requires_dedicated_backfill_runner=true
sha_driver_ref=f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05
date_list=20261019,20261020,20261021,20261022,20261023
# 以下须与执行器 SHA_KEYS 全表逐键相等（23 键）：
# sha_cal_restore / sha_cal_compare / sha_snapshot_tool / sha_scope /
# sha_nightly_update / sha_tier1_pull / sha_tushare_proxy / sha_relay_health /
# sha_adj_factor_incr / sha_tier1_materialize / sha_etf_daily_adj_incr /
# sha_eng_daily_panels / sha_mid_large_universe_incr /
# sha_light_event_windows_pull / sha_forecast_manifest_declare /
# sha_fill_hsgt_top10_extend / sha_cyq_perf_monthly / sha_tier3_daily_snapshot /
# sha_data_freshness_status / sha_routine_fallback /
# sha_daily_basic_incremental / pin_daily_basic_transform / sha_driver_ref
pin_trade_cal=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086
rss_stop_kb=1484800
rss_hard_kb=1536000
call_b_budget_min=75
call_b_latest_finish=16:00
live=false
promotion_approved=false
allow_paper=false
allow_stream=false
allow_nightly_driver_for_historical_dates=false
# 前置未满足前不得签发：
# prerequisite_consume_suspend_cleared=true
# prerequisite_probe_trade_cal_pass=true
# prerequisite_probe_stock_basic_pass=true
expires_et=<Arch 填；不得宽于窗口授权 2026-10-27T04:45:52-04:00>
note=draft_only_not_signed;pack_preview_pass_with_conditions
```

## 分发

- Eng：包预审通过条件如上；可继续备跑材料；**勿**启生产；可选加 CONSUME_SUSPEND hard-fail。
- Data：维持不消费 `9e4359f9`；继续 stock_basic 复测（probe5 加固钉）。
- 主 Agent：结论 **PACK_PREVIEW_PASS_WITH_CONDITIONS**；开跑闸仍 = SUSPEND + stock_basic。

---
archive_by=Arch only
