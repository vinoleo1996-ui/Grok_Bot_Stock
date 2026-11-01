# Eng 纸面日终重桥2回执 · D=20261026 · OK

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| written_at_et | 2026-10-26T19:43:45-04:00 |
| status | **OK**（content-gate rehash APPLIED；X2H→2026-10-26） |
| paper-daily bus exit | **0**（exits [0,0,0]；bus nav/holdings/gate/receipt=true） |
| rehash exits | B4 step exit=**0**；S6 step exit=**0** |
| forced | false（**未**传 `--force`） |
| live / promotion | false / false |
| mode | EOD_only（recon） |
| DONE marker | `output/nightly_markers/nightly_20261026.DONE.json` sha8 **`fbddcd2b`** |
| readiness PASS (reused) | `output/loop/paper_daily_20261026/READINESS_20261026.md` sha8 **`3b76da6b`** |
| log | `/tmp/paper_daily_20261026_rebridge2_20261026T194014_3361020.log` |
| OUT | `output/loop/paper_daily_20261026/` |
| weights_modified | **false** |
| FROZEN tip B4 | `*_20261026_r2.parquet` tip sha8 `7c99ab58`/`48cbb6e2`；file sha8 **`650b5f2a`** |
| FROZEN tip S6 | `*_20261026.parquet` tip sha8 `8d76180a`/`0d6ce661`；file sha8 **`eb456b52`** |
| cand3 enable | **未触** |
| 绕闸 | **未** |

## Command
```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --run-nav
```

## Preconfirm pins（MATCH；parent re-pin 后）
| pin | sha8 |
|---|---|
| `research/b4_paper_extend.py` | **`da62b28a`** |
| `research/s6_paper_extend.py` | **`93b00354`** |
| B4 FROZEN file (pre-run) | **`c06023f9`** |
| S6 FROZEN file (pre-run) | **`e4b9227e`** |
| B4 pq 60w `…_20261026_r2.parquet` | **`7c99ab58`** |
| B4 pq 100w | **`48cbb6e2`** |
| S6 pq 60w `…_20261026.parquet` | **`8d76180a`** |
| S6 pq 100w | **`0d6ce661`** |
| RESEARCH_QUIET | absent |
| conflicting pgrep | empty |

## Content-gate rehash（APPLIED）
### B4 (`quantlab.cli b4-paper --mode rehash …20261026…`)
```
ok: true
REHASH APPLIED; receipt /workspace/QuantLab/docs/v2/B4_PAPER_REHASH_20261026_194022_ZH.md
```
tip 600000 → `…_60w_20261026_r2.parquet` sha `7c99ab58…`；1000000 → `…_100w_20261026_r2.parquet` sha `48cbb6e2…`。

### S6 (`quantlab.cli paper-track --track s6 --mode rehash …20261026…`)
```
ok: true
REHASH APPLIED; receipt /workspace/QuantLab/docs/v2/S6_PAPER_REHASH_20261026_194028_ZH.md
```
tip 600000 → `…_60w_20261026.parquet` sha `8d76180a…`；1000000 → `…_100w_20261026.parquet` sha `0d6ce661…`。

## Tracks（scorecard X2 口径；年化 244 日；**未编造**）
| track | AUM | last NAV (bridge) | CAGR | MDD | Calmar | 月胜率 | 日胜率 | track_status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| capacity_adv | 60万 | **810864.51** (X2H→2026-10-26) | 13.82% | -10.07% | 1.37 | 50% | 52.7% | **OK_HOLD_EXTEND** |
| capacity_adv | 100万 | **1311336.95** (X2H→2026-10-26) | 12.23% | -11.62% | 1.05 | 57% | 53.6% | **OK_HOLD_EXTEND** |
| B4 conc 50/25/25 | 60万 | **823047.48** (X2H→2026-10-26) | 15.11% | -13.85% | 1.09 | 64% | 52.5% | **OK** |
| B4 conc 50/25/25 | 100万 | **1336310.29** (X2H→2026-10-26) | 14.24% | -13.17% | 1.08 | 57% | 52.9% | **OK** |
| S6 shadow 50/25/25 | 60万 | **852856.16** (X2H→2026-10-26) | 17.15% | -11.95% | 1.43 | 64% | 52.0% | **OK** |
| S6 shadow 50/25/25 | 100万 | **1392491.40** (X2H→2026-10-26) | 16.37% | -12.66% | 1.29 | 61% | 52.4% | **OK** |

来源：`scorecard.json` / `paper_daily_recon.json` segments.X2H_bridge；B4/S6/cap bridge **均**延至 20261026。

## PENDING remaining
| item | pending_reason |
|---|---|
| FWD | WAITING（weights end 2026-10-26 < forward start 2026-11-02） |
| b4/s6 X2H | **cleared**（rehash APPLIED；track_status OK） |

## Hard bans observed
- 无 `--force`；无候选3；未绕闸；FROZEN tip 经合法 content-gate rehash 钉到 20261026 pq
- extend 步 NOOP_EXISTS_IDENTICAL（pq 已齐）；rehash 后 bridge/monitor 用 20261026 tip
- 未报 Leo；live=false

## Artifacts
| path | note |
|---|---|
| `paper_daily_recon.json` | track_status b4/s6=OK；cap=OK_HOLD_EXTEND |
| `scorecard.json` / `.md` | rewritten ~19:41 ET |
| `bridge_X2H/` | cap/B4/S6 → 10-26 |
| `docs/v2/B4_PAPER_REHASH_20261026_194022_ZH.md` | rehash APPLIED |
| `docs/v2/S6_PAPER_REHASH_20261026_194028_ZH.md` | rehash APPLIED |

## Anomalies
- log file only captured X2H bridge stdout (Python block-buffering); extend/rehash evidence taken from paper_daily_recon.json steps + FROZEN rehash_history + REHASH APPLIED receipts
- FWD still WAITING (weights end 2026-10-26 < forward start 2026-11-02) — expected
- B4/S6 tip NAV moved from 2026-10-14 end to 2026-10-26 after rehash+bridge (cap already at 10-26)

---
文档结束
