# Eng 纸面日终重桥回执 · D=20261026 · REFUSED

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| written_at_et | 2026-10-26T19:35:30-04:00 |
| status | **REFUSED**（content-gate rehash） |
| paper-daily bus exit | **0**（exits [0,0,0]；bus nav/holdings/gate/receipt=true） |
| rehash exits | B4 step exit=**1**；S6 step exit=**1** |
| forced | false（**未**传 `--force`） |
| live / promotion | false / false |
| mode | EOD_only（recon） |
| DONE marker | `output/nightly_markers/nightly_20261026.DONE.json` sha8 **`fbddcd2b`** |
| readiness PASS (reused) | `output/loop/paper_daily_20261026/READINESS_20261026.md` sha8 **`3b76da6b`** |
| prior abort (kept) | `READINESS_ABORT_20261026.md` sha8 **`665232a5`** |
| log | `/tmp/paper_daily_20261026_rebridge_20261026T193249_3057069.log` |
| OUT | `output/loop/paper_daily_20261026/` |
| weights_modified | **false** |
| FROZEN tip B4 | still `*_20261014_r2.parquet` tip sha8 `efcef7c4`/`4736c030`；**未**钉到 20261026 |
| FROZEN tip S6 | still `*_20261014.parquet` tip sha8 `6ce63a79`/`b1f9ae65`；**未**钉到 20261026 |
| cand3 enable | **未触** |
| 绕闸 | **未**（停报；未 `--force`） |

## Command
```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli paper-daily --run-nav
```

## Preconfirm pins（MATCH）
| pin | sha8 |
|---|---|
| `research/b4_paper_extend.py` | **`da62b28a`** |
| `research/s6_paper_extend.py` | **`93b00354`** |
| B4 pq 60w `…_20261026_r2.parquet` | **`7c99ab58`** |
| B4 pq 100w | **`48cbb6e2`** |
| S6 pq 60w `…_20261026.parquet` | **`8d76180a`** |
| S6 pq 100w | **`0d6ce661`** |
| execution.py | **`373fed30`** |
| trade_cal.parquet | **`141078fa…`** |
| baseline daily_basic | **`273163cc`** |
| P | `20261023` |
| RESEARCH_QUIET | absent |
| conflicting pgrep | empty |

## Content-gate REFUSED（verbatim）
### B4 (`quantlab.cli b4-paper --mode rehash …20261026…`)
```
content_gate.pass_=false
reason: script changed/missing: research/b4_paper_extend.py (check da62b28a43a8 vs pinned 6c927ae69268)
REHASH REFUSED: checks failed; FROZEN_CONFIG.json unchanged
```
（legs history/cadence/deferral 均 pass；卡在 **FROZEN 钉脚本 sha `6c927ae69268` ≠ 盘上 `da62b28a`**。Arch 追认 `da62b28a` / forbid `6c927ae6` 已落 TEAM_STATE，但 FROZEN script pin 未随热修更新，故闸拒。）

### S6 (`quantlab.cli paper-track --track s6 --mode rehash …20261026…`)
```
content_gate.pass_=false
reason: script changed/missing: research/s6_paper_extend.py (check 93b003543192 vs pinned 3b258bbe9bd2); script changed/missing: research/b4_paper_extend.py (check da62b28a43a8 vs pinned 6c927ae69268)
REHASH REFUSED: checks failed; FROZEN_CONFIG.json unchanged
```

## Tracks（scorecard X2 口径；年化 244 日；**未编造**）
| track | AUM | last NAV (bridge) | CAGR | MDD | Calmar | 月胜率 | 日胜率 | track_status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| capacity_adv | 60万 | **810864.51** (X2H→2026-10-26) | 13.82% | −10.07% | 1.37 | 50% | 52.7% | **OK_HOLD_EXTEND** |
| capacity_adv | 100万 | **1311336.95** (X2H→2026-10-26) | 12.23% | −11.62% | 1.05 | 57% | 53.6% | **OK_HOLD_EXTEND** |
| B4 conc 50/25/25 | 60万 | **829067.61** (X2H→2026-10-14) | 15.11% | −13.85% | 1.09 | 64% | 52.5% | **PENDING** |
| B4 conc 50/25/25 | 100万 | **1353463.96** (X2H→2026-10-14) | 14.24% | −13.17% | 1.08 | 57% | 52.9% | **PENDING** |
| S6 shadow 50/25/25 | 60万 | **863721.67** (X2H→2026-10-14) | 17.15% | −11.95% | 1.43 | 64% | 52.0% | **PENDING** |
| S6 shadow 50/25/25 | 100万 | **1413772.05** (X2H→2026-10-14) | 16.37% | −12.66% | 1.29 | 61% | 52.4% | **PENDING** |

来源：`scorecard.json` / `paper_daily_recon.json` segments.X2H_bridge；B4/S6 bridge **未**延至 20261026。

## PENDING remaining
| item | pending_reason (recon verbatim) |
|---|---|
| b4 X2H | `B4 rehash gate REFUSED; B4 stays on previously frozen files` |
| s6 X2H | `S6 rehash gate REFUSED (history/rules/cadence/pinned leg); S6 stays on previously frozen files` |
| FWD | WAITING（weights end 2026-10-14 < forward start 2026-11-02） |

## Hard bans observed
- 无 `--force`；无候选3；未绕闸；FROZEN mtime 仍 2026-10-25（本拍未改 tip）
- extend 步 NOOP_EXISTS_IDENTICAL（pq 已齐）；rehash 拒后继续用 20261014 tip 跑 bridge/monitor
- 未报 Leo；live=false

## Artifacts
| path | note |
|---|---|
| `paper_daily_recon.json` | track_status b4/s6=PENDING |
| `scorecard.json` / `.md` | rewritten 19:33 ET |
| `bridge_X2H/` | cap→10-26；B4/S6→10-14 |
| `/tmp/b4_rehash_refuse_capture.log` | 诊断复跑 capture（FROZEN unchanged） |
| `/tmp/s6_rehash_refuse_capture.log` | 同上 |

---
文档结束
