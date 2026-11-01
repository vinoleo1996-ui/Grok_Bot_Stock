# Eng 纸面日终重跑回执 · D=20261026

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| written_at_et | 2026-10-26T19:11:17-04:00 |
| status | **OK** |
| exit | **0** |
| forced | false（**未**传 `--force`） |
| live / promotion | false / false |
| mode | EOD_only（recon） |
| DONE marker | `output/nightly_markers/nightly_20261026.DONE.json` sha8 **`fbddcd2b`** |
| readiness PASS | `output/loop/paper_daily_20261026/READINESS_20261026.md` sha8 **`3b76da6b`** |
| prior abort (kept) | `READINESS_ABORT_20261026.md` sha8 **`665232a5`** |
| log | `/tmp/paper_daily_20261026_rerun_20261026T185919_2993559.log` |
| OUT | `output/loop/paper_daily_20261026/` |
| weights_modified | **false** |
| NOTE_STALL_MERGE | 已写（10-15/16 并入本 D） |
| cand3 enable | **未触** |
| SW post | 89d4afa3 / 87d769aa **UNCHANGED** |

## Command
```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --run-nav
```

## Tracks（scorecard X2 口径；年化 244 日；月胜率 28 个月）

| track | AUM | NAV (last; bridge end) | CAGR | MDD | Calmar | 月胜率 | 日胜率 | note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| capacity_adv | 60万 | **810864.51** (X2H→2026-10-26) | 13.82% | −10.07% | 1.37 | 50% | 52.7% | track_status OK_HOLD_EXTEND |
| capacity_adv | 100万 | **1311336.95** (X2H→2026-10-26) | 12.23% | −11.62% | 1.05 | 57% | 53.6% | same |
| B4 conc 50/25/25 | 60万 | **829067.61** (X2H→2026-10-14) | 15.11% | −13.85% | 1.09 | 64% | 52.5% | X2H **PENDING** extend |
| B4 conc 50/25/25 | 100万 | **1353463.96** (X2H→2026-10-14) | 14.24% | −13.17% | 1.08 | 57% | 52.9% | X2H **PENDING** extend |

X2 BOOK end（冻结段末）: cap60=811507.18 / cap100=1308839.92 / b4_60=832994.41 / b4_100=1363919.46 @2026-10-09。

来源：`scorecard.json` / `scorecard.md` / `bridge_X2H/*/X2H/BOOK/nav.csv`；**未编造**。

## PENDING / REFUSED
| item | detail |
|---|---|
| b4 X2H bridge | **PENDING** — `b4_paper_extend exit 2 (bridge stops at last gated weights)`；bridge NAV 止于 2026-10-14 |
| s6 X2H bridge | **PENDING** — `s6_paper_extend exit 2`（shadow；非本令硬交付） |
| REFUSED | **无** |
| FWD | missing（official forward starts 2026-11-02） |

## Hard bans observed
- 无 `--force`；无候选3 enable；未改 capacity_adv FROZEN/PROVENANCE（mtime 仍 2026-10-25）；`weights_modified=false`
- B4 `STATUS.json` 被 paper-daily 正常写（mtime 2026-10-26 19:09 ET）；`FROZEN_CONFIG.json` 未改
- 未报 Leo；live=false

## Artifacts
| path | note |
|---|---|
| `paper_daily_recon.json` | recon |
| `scorecard.json` / `.md` | 统一记分卡 |
| `capacity_adv_paper/` | X2 NAV |
| `bridge_X2H/` | X2H hold-extend |
| `risk_flags.parquet` | risk |
| `SW_SHA_DISCLOSURE.md` | pre+post |
| `NOTE_STALL_MERGE.md` | stall merge note |

---
文档结束
