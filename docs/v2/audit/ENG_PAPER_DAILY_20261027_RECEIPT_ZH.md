# Eng 纸面日终回执 · D=20261027 · OK

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| written_at_et | 2026-10-27T18:33:03-04:00 |
| status | **OK**（content-gate rehash APPLIED；X2H→2026-10-27） |
| paper-daily bus exit | **0**（exits [0,0,0]；bus nav/holdings/gate/receipt=true） |
| rehash exits | B4=**0**；S6=**0**；cap extend/weight-gate=**0** |
| forced | false（**未**传 `--force`） |
| live / promotion | false / false |
| mode | EOD_only（recon） |
| DONE marker | `output/nightly_markers/nightly_20261027.DONE.json` sha8 **`5914e03b`** |
| prior ABORT (superseded) | `READINESS_ABORT_20261027.md` sha8 **`e8b72bf3`** |
| log | `/tmp/paper_daily_20261027_20261028T061905_715617.log` |
| OUT | `output/loop/paper_daily_20261027/` |
| weights_modified | **false** |
| FROZEN tip capacity_adv | `…_paper_20261027_r2.parquet` tip sha8 **`82f557c6`** |
| FROZEN tip B4 | 60w **`d5f480da`** / 100w **`42b01c56`** |
| FROZEN tip S6 | 60w **`fadd5c44`** / 100w **`d5843e20`** |
| leo_notify | false |

## Command
```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --run-nav
```

## Preconfirm pins（MATCH）
| pin | sha8 |
|---|---|
| DONE `nightly_20261027.DONE.json` | **`5914e03b`** |
| `quantlab/platform/execution.py` | **`373fed30`** |
| `data/v2/tushare_raw/trade_cal.parquet` | **`141078fa`** |
| RESEARCH_QUIET | absent |
| conflicting pgrep Data/Web/paper | empty（仅 keepalive） |

## Content-gate rehash（APPLIED · 自然）
- capacity_adv tip → `g1g5_capacity_adv_daily_weights_paper_20261027_r2.parquet` sha8 **`82f557c6`**；held_from=2026-10-27；next_rebalance=2026-10-30；status=**OK_HOLD_EXTEND**
- B4 rehash APPLIED → `docs/v2/B4_PAPER_REHASH_20261027_182823_ZH.md`；60w **`d5f480da`** / 100w **`42b01c56`**
- S6 rehash APPLIED → `docs/v2/S6_PAPER_REHASH_20261027_182952_ZH.md`；60w **`fadd5c44`** / 100w **`d5843e20`**

## Tracks（scorecard X2 口径；年化 244 日；last NAV=X2H bridge→2026-10-27；**未编造**）
| track | AUM | last NAV (bridge) | CAGR | MDD | Calmar | 月胜率 | 日胜率 | track_status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| capacity_adv | 60万 | **807275.35** (X2H→2026-10-27) | 13.82% | -10.07% | 1.37 | 50.0% | 52.7% | **OK_HOLD_EXTEND** |
| capacity_adv | 100万 | **1304771.20** (X2H→2026-10-27) | 12.23% | -11.62% | 1.05 | 57.1% | 53.6% | **OK_HOLD_EXTEND** |
| B4 conc 50/25/25 | 60万 | **811444.57** (X2H→2026-10-27) | 15.11% | -13.85% | 1.09 | 64.3% | 52.5% | **OK** |
| B4 conc 50/25/25 | 100万 | **1320592.54** (X2H→2026-10-27) | 14.24% | -13.17% | 1.08 | 57.1% | 52.9% | **OK** |
| S6 shadow 50/25/25 | 60万 | **843407.55** (X2H→2026-10-27) | 17.15% | -11.95% | 1.43 | 64.3% | 52.0% | **OK** |
| S6 shadow 50/25/25 | 100万 | **1377153.57** (X2H→2026-10-27) | 16.37% | -12.66% | 1.29 | 60.7% | 52.4% | **OK** |

来源：`scorecard.json` sha8 **`cabf70d9`** / `paper_daily_recon.json` sha8 **`30f94ac2`**；segments.X2H_bridge 均延至 20261027。

## Artifact sha8
| artifact | sha8 |
|---|---|
| scorecard.json | **`cabf70d9`** |
| scorecard.md | **`1f260a56`** |
| paper_daily_recon.json | **`30f94ac2`** |
| capacity_adv_FROZEN_CONFIG.json | **`9f5abfb6`** |
| DONE | **`5914e03b`** |

## PENDING remaining
| item | pending_reason |
|---|---|
| FWD | WAITING（official forward starts 2026-11-02） |
| freshness_calendar_mismatch | INFO only（Data cutoff 期待 2026-10-26 ≠ Eng session 2026-10-27；Eng rule used） |
| b4/s6/cap X2H | **cleared**（rehash APPLIED；track_status OK / OK_HOLD_EXTEND） |

## Hard bans observed
- 无 `--force`；未改 FROZEN 权重脚本；未碰 leaf37；未挂/抬 QUIET
- weights_modified=**false**；live=false；leo_notify=false
- tip 仅经合法 content-gate rehash 钉到 20261027 pq

## Anomalies
- 管道缓冲使 `/tmp` 日志主要留下尾部 X2H NAV；完整 exits 见 recon.steps + bus JSON
- 盘上仍留前序 `READINESS_ABORT_20261027.md` **`e8b72bf3`**（已 supersede，未删）

