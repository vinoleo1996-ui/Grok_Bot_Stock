# Eng 回执 · fund MDD-cut Book-Smoke（V_BALLAST_MIX · 3 臂 · dark_horse_add · ALLA）

- 角色：QuantLab Eng
- 时点：**2026-10-27 23:41 ET**（America/New_York）
- 主令：~23:30/23:35 ET MATCH→GO 真跑 Book-Smoke（`.ok` `335635dd` / SIGNED `dcef54f8` MATCH）
- **结论：`DONE`**
- **EXECUTED=`true`**
- **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；`live=false`；`leo_notify=false`；`promotion_approved=false`

---

## 0. 结论摘要

| 项 | 值 |
|---|---|
| 结论 | **DONE** |
| EXECUTED | **true** |
| 组合主臂 | **V_BALLAST_MIX** stock=0.50 / core·510300=0.50 / alpha_event=0 |
| 对照臂 | stock∈{0.40,0.60}（共 **3** 臂） |
| 事件变体 | dark_horse_add |
| 池 | ALLA 可交易（**禁** mid_large 主口径） |
| overall peak_rss_mb | **733.2**（≤1500；未抬帽；peak_proof REQUIRED ✓） |
| CLI_GAP | `book_smoke_no_arch_ok_path` — wrapper 预核 `.ok` `335635dd`；**未改** `book_smoke.py` `1a5fa1aa`；**禁** RESTORED `f08ce32c` |
| 主闸披露 | **三臂×两 AUM 全过** \|MDD\|≤25% 且 CAGR≥C0（C0≈11.27%/−16.24%） |
| \|MDD\|≤15% 对照 | **全未过**（非主闸；仅披露） |
| ≠ACCEPT | Book-Smoke / X2 均 **false** |

### Headline（探索窗 X2；成本开；**非密封 / ≠ACCEPT**）

| AUM | arm | stock/core | CAGR | MDD | Sharpe | cost/AUM | 主闸 | ≤15%对照 |
|---:|---|---|---:|---:|---:|---:|:---:|:---:|
| 60万 | X2/BOOK | **0.50/0.50** | **0.1447** | **-0.1714** | **0.730** | 0.0164 | PASS | fail |
| 60万 | X2/C0 | — | 0.1127 | -0.1624 | 0.651 | 0.0002 | — | — |
| 100万 | X2/BOOK | **0.50/0.50** | **0.1317** | **-0.2014** | **0.653** | 0.0159 | PASS | fail |
| 100万 | X2/C0 | — | 0.1127 | -0.1624 | 0.651 | 0.0002 | — | — |
| 60万 | X2/BOOK | 0.40/0.60 | 0.1294 | -0.1635 | 0.699 | 0.0129 | PASS | fail |
| 100万 | X2/BOOK | 0.40/0.60 | 0.1307 | -0.1734 | 0.676 | 0.0130 | PASS | fail |
| 60万 | X2/BOOK | 0.60/0.40 | 0.1352 | -0.2110 | 0.657 | 0.0181 | PASS | fail |
| 100万 | X2/BOOK | 0.60/0.40 | 0.1324 | -0.2249 | 0.634 | 0.0190 | PASS | fail |

一行（主臂）：**60万 CAGR=14.47% MDD=−17.14% Sharpe=0.730；100万 CAGR=13.17% MDD=−20.14% Sharpe=0.653**（vs C0 CAGR=11.27% MDD=−16.24%）。相对基线 who_pays 纯股袖（MDD≈−32%）主臂 MDD 明显收窄并过 25% 主闸。

---

## 1. 硬钉 MATCH 表（开跑前+交卷复算）

| 钉 | 路径 | 期望 sha8 | 实算 | 状态 |
|---|---|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX.ok` | `335635dd` | `335635dd` | **MATCH** |
| SIGNED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md` | `dcef54f8` | `dcef54f8` | **MATCH**（文内 `d9771793` **勿采**） |
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_20261027_ZH.md` | `d489c937` | `d489c937` | **MATCH** |
| RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `058ec68e` | `058ec68e` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `2f039c3d` | `2f039c3d` | **MATCH** |
| DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | `eeccb25e` | **MATCH** |
| ArchDRAFT | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` | `41d4fc76` | `41d4fc76` | **MATCH** |
| 掩码 | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| C2 JSON | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| AE parquet | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` | `1a5fa1aa` | `1a5fa1aa` | **MATCH（未改）** |
| 基线 Eng BS | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | `b013a7a8` | **MATCH**（旁线） |
| 基线 weights | `…/20261027_223826/…weights….parquet`（复用） | `601c5cf6` | `601c5cf6` | **MATCH** |

窗：valid `2026-10-27T23:29:00-04:00`→`2026-10-28T01:00:00-04:00`；expires `01:05 ET` — 开跑 ~23:38 ET **在窗内**。

---

## 2. CLI_GAP 说明（须 `--arch-ok-path`）

- **CLI_GAP=`book_smoke_no_arch_ok_path`**
- `quantlab/portfolio/book_smoke.py`（`1a5fa1aa`）**无** `--arch-ok-path` 参数（`.ok` `cli_gap` / `approved_cmd_note` 已提示 Eng 可用 wrapper 预核）。
- **Eng 做法**：out_dir 侧稿 `preflight_book_smoke_wrapper.py`（sha8 `93e3c2b2`；py_compile OK）预核本窗 `.ok` sha=`335635dd`、窗未过期、rss 帽=1500、禁 mid_large、禁 RESTORED `f08ce32c`、QUIET ABSENT、peak_proof 采样，再 `subprocess` 调用：
  ```
  PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -m quantlab.portfolio.book_smoke \
    --windows X2 --capitals 600000,1000000 \
    --sleeves '<arm>' --stock-path <weights.parquet> --out <arm_subdir> --receipt <scaffold>
  ```
- **未修改** 钉住的 `1a5fa1aa` 生产文件；侧稿仅写在 out_dir；侧稿 py_compile PASS（无需另 `.ok`）。
- **未**从 `_consumed` 拷回旧 who_pays `.ok` `f08ce32c`。

---

## 3. 权重长表（复用基线）

| 项 | 值 |
|---|---|
| 源（复用） | `output/ai_factory/_fund_portfolio_who_pays_book_smoke_dark_horse_add/20261027_223826/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` |
| 本窗副本 | `output/ai_factory/_fund_portfolio_mdd_cut_book_smoke_v_ballast_mix/20261027_233811/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` |
| sha8 | **`601c5cf6`**（源=副本 MATCH） |
| 规则 | dark_horse_add；ALLA；T2 入场；持有60；4%/≤20/SW≤28%；余额510300；排除600519/002371 |
| 权重覆盖窗 | **2024-01-02 → 2026-10-09** |
| book_smoke `WINDOWS["X2"]` | **2024-06-03 → 2026-10-09** |
| 重建 | **未**重建（事件/池/掩码未变；复用可行） |

可消费核验（book_smoke probe）：stock **book_consumable** rows=13808 sessions=570。

---

## 4. Book-Smoke 产物

| 项 | 值 |
|---|---|
| out_dir | `output/ai_factory/_fund_portfolio_mdd_cut_book_smoke_v_ballast_mix/20261027_233811/` |
| 汇总 | `…/book_smoke_summary.json` sha8 **`2021a06c`** |
| 主臂 summary | `…/arm_stock_050/book_smoke_summary.json` sha8 **`cee57a6e`**；peak **691.0** |
| 对照040 summary | `…/arm_stock_040/…` sha8 **`a9a93906`**；peak **733.2** |
| 对照060 summary | `…/arm_stock_060/…` sha8 **`5834075a`**；peak **709.4** |
| sleeves 主 | `{"core":0.50,"stock":0.50,"alpha_event":0.0}` |
| sleeves 040 | `{"core":0.60,"stock":0.40,"alpha_event":0.0}` |
| sleeves 060 | `{"core":0.40,"stock":0.60,"alpha_event":0.0}` |
| arms | BOOK, C0（每臂×两 AUM） |
| overall peak_rss_mb（外采 /proc VmRSS） | **733.2** |
| wrapper | `preflight_book_smoke_wrapper.py` sha8 `93e3c2b2`；三臂 wrapper_result EXECUTED=true；rc=0 |
| 预条件 | kline/export_static/snapshot/gen 空；Data nightly/tier1/run_nightly 空 |

---

## 5. 禁项回执

| 禁项 | 回执 |
|---|---|
| 未混叶38 `c01c2034` | **是**（未打开/消费其 out/.ok） |
| 未挂 QUIET | **是**（QUIET **ABSENT** 维持） |
| 未改 mid_large 主口径 | **是**（池=ALLA；`allow_mid_large_primary=false`） |
| **未 RESTORED `f08ce32c`** | **是**（未从 `_consumed` 拷回；本窗独立 `.ok` `335635dd`） |
| 未自签 `.ok` | **是** |
| 未改 `book_smoke.py` | **是**（`1a5fa1aa` 交卷仍 MATCH） |
| 未抬 rss | **是**（帽 1500；峰 733.2） |
| 未 git commit | **是** |
| 未 `--force` | **是** |
| 未跑 X2 正式窗（另令） | **是**（本拍仅 Book-Smoke） |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **是** |

---

## 6. 下一跳

- 交 **主 Agent** → **Arch 只审/CONSUME**（Eng 不自签 CONSUME）。
- X2 正式跑 **另令**（本 `.ok` `x2=false`）。
- 本回执 **≠ACCEPT**；数字仅探索 Book-Smoke 披露。
- BLOCKER：无。

---

**本回执 sha8**：以 `sha256sum` 本文件盘算为准（交主时附）。
