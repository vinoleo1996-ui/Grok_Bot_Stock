# Eng 回执 · fund who_pays Book-Smoke（dark_horse_add · ALLA）

- 角色：QuantLab Eng
- 时点：**2026-10-27 22:41 ET**（America/New_York）
- 主令：~22:33 ET GO 真跑 Book-Smoke（`.ok` MATCH 后）
- **结论：`DONE`**
- **EXECUTED=`true`**
- **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；`live=false`；`leo_notify=false`；`promotion_approved=false`

---

## 0. 结论摘要

| 项 | 值 |
|---|---|
| 结论 | **DONE** |
| EXECUTED | **true** |
| 主变体 | dark_horse_add |
| 池 | ALLA 可交易（**禁** mid_large 主口径） |
| peak_rss_mb | **651.9**（≤1500；未抬帽；peak_proof REQUIRED ✓） |
| CLI_GAP | `book_smoke_no_arch_ok_path` — wrapper 预核 `.ok`；**未改** `book_smoke.py` `1a5fa1aa` |
| ≠ACCEPT | Book-Smoke / X2 均 **false** |

### Headline（探索窗 X2；成本开；**非密封 / ≠ACCEPT**）

| AUM | arm | CAGR | MDD | Sharpe | cost/AUM |
|---:|---|---:|---:|---:|---:|
| 60万 | X2/BOOK | **0.1365** | **-0.3207** | **0.581** | 0.0296 |
| 60万 | X2/C0 | 0.1127 | -0.1624 | 0.651 | 0.0002 |
| 100万 | X2/BOOK | **0.1555** | **-0.3285** | **0.628** | 0.0336 |
| 100万 | X2/C0 | 0.1127 | -0.1624 | 0.651 | 0.0002 |

一行：**60万 CAGR=13.65% MDD=-32.07% Sharpe=0.581；100万 CAGR=15.55% MDD=-32.85% Sharpe=0.628**（vs C0 CAGR=11.27% MDD=-16.24%）。

---

## 1. 硬钉 MATCH 表（开跑前+交卷复算）

| 钉 | 路径 | 期望 sha8 | 实算 | 状态 |
|---|---|---|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.ok` | `f08ce32c` | `f08ce32c` | **MATCH** |
| SIGNED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md` | `c0a8099b` | `c0a8099b` | **MATCH**（文内自称 `fe0a9383` **勿采**） |
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH** |
| 掩码 | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| Eng BLOCKED | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_BLOCKED_AUTH_20261027_ZH.md` | `9c4a8ad5` | `9c4a8ad5` | **MATCH** |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH**（只用 `events_dark_horse_add`） |
| C2 JSON | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| AE parquet | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` | `1a5fa1aa` | `1a5fa1aa` | **MATCH（未改）** |

窗：valid `2026-10-27T22:31`→`2026-10-28T00:01` ET；expires `00:05` ET — 开跑 ~22:40 ET **在窗内**。

---

## 2. CLI_GAP 说明（须 `--arch-ok-path`）

- **CLI_GAP=`book_smoke_no_arch_ok_path`**
- `quantlab/portfolio/book_smoke.py`（`1a5fa1aa`）**无** `--arch-ok-path` 参数（`.ok` `approved_cmd_note` 已提示可能需 Eng 适配）。
- **Eng 做法**：out_dir 侧稿 `preflight_book_smoke_wrapper.py` 预核 `.ok` sha=`f08ce32c`、窗未过期、rss 帽=1500、禁 mid_large、QUIET ABSENT、peak_proof 采样，再 `subprocess` 调用：
  ```
  PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -m quantlab.portfolio.book_smoke \
    --windows X2 --capitals 600000,1000000 \
    --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' \
    --stock-path <weights.parquet> --out <out_dir> --receipt <本回执路径>
  ```
- **未修改** 钉住的 `1a5fa1aa` 生产文件；侧稿仅写在 out_dir；侧稿 `py_compile` PASS（Arch：侧稿 py_compile 无需另 `.ok`）。

---

## 3. 权重长表

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/_fund_portfolio_who_pays_book_smoke_dark_horse_add/20261027_223826/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` |
| sha8 | **`601c5cf6`** |
| meta | 同路径 `.meta.json` |
| 机制 tag | `g1g5_ashare_fund_portfolio_v1_allA`（基 tag `g1g5_ashare_fund_portfolio_v1`） |
| 规则 | 判定日=T1；**T2 入场**；持有 **60**；同票新事件截断；4% / ≤20 / SW L1≤28%；余额 510300；排除 600519/002371 |
| 事件 | C2 `events_dark_horse_add` n=12763（已 ALLA 滤；本窗未改 mid_large） |
| 权重覆盖窗（FROZEN） | **2024-01-02 → 2026-10-09** |
| book_smoke `WINDOWS["X2"]` | **2024-06-03 → 2026-10-09**（与 FROZEN 意向起点不同；**已披露**；权重覆盖 FROZEN 全窗，BS 只评 X2 模块窗） |
| 日均持股 / max | 19.67 / 20 |
| ind_max_observed | 0.28 |
| builder peak_rss_mb | 527.0 |
| 侧稿 | `…/20261027_223826/build_fund_portfolio_dark_horse_add_weights_side.py` sha8 `34a47cda`（py_compile OK） |

可消费核验（book_smoke probe）：stock **book_consumable** rows=13808 sessions=570。

---

## 4. Book-Smoke 产物

| 项 | 值 |
|---|---|
| out_dir | `output/ai_factory/_fund_portfolio_who_pays_book_smoke_dark_horse_add/20261027_223826/` |
| summary | `…/book_smoke_summary.json` sha8 **`0d1ddcb0`** |
| run_id | `book_smoke_20261028_104027` |
| sleeves | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| arms | BOOK, C0 |
| peak_rss_mb（外采 /proc VmRSS） | **651.9** |
| wrapper | `preflight_book_smoke_wrapper.py` sha8 `1c7562cc`；`wrapper_result.json` EXECUTED=true；rc=0 |
| 预条件 | kline/export_static/snapshot/gen 空；Data nightly/tier1/run_nightly 空 |

---

## 5. 禁项回执

| 禁项 | 回执 |
|---|---|
| 未混叶38 | **是**（未打开/消费 `…LEAF38…794f6578`；未碰其 out） |
| 未挂 QUIET | **是**（QUIET **ABSENT** 维持） |
| 未改 mid_large 主口径 | **是**（池=ALLA；`allow_mid_large_primary=false`） |
| 未自签 `.ok` | **是** |
| 未改 `book_smoke.py` | **是**（`1a5fa1aa` 交卷仍 MATCH） |
| 未抬 rss | **是**（帽 1500；峰 651.9） |
| 未消费 fundport stream `…v1_1_r2` | **是** |
| 未 git commit | **是** |
| 未跑 X2 正式窗（另令） | **是**（本拍仅 Book-Smoke） |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **是** |

---

## 6. 下一跳

- 交 **主 Agent** → **Arch 只审/CONSUME**（Eng 不自签 CONSUME）。
- X2 正式跑 **另令**（本 `.ok` `x2=false`）。
- 本回执 **≠ACCEPT**；数字仅探索 Book-Smoke 披露。

---

**本回执 sha8**：以 `sha256sum` 本文件盘算为准（交主时附）。
