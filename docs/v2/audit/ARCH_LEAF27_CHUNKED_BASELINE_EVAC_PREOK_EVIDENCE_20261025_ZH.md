# Arch 叶27 Post-GateA baseline_evac · 签前预检证据

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T22:34:17-04:00`（America/New_York） |
| 窗令 | `docs/v2/audit/MAIN_LEAF27_BASELINE_EVAC_OK_WINDOW_20261025_ZH.md` sha8 **`5930388b`** |
| 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_BASELINE_EVAC_REVIEW_20261025_ZH.md` sha8 **`84fb87cf`** PASS_WITH_CONDITIONS |
| live / promotion | **false** / **false** |

## 窗与场

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 22:30–23:15 ET** expires **23:17** |
| 签时墙钟 | `2026-10-25T22:34:17-04:00` ∈ [22:30, 23:17) |
| QUIET 前 | `RESEARCH_QUIET.lock` **不存在**；8795 quiet=false |
| MemAvailable@签 | 8885104 kB（≳2.5Gi） |
| live `.ok` | 0（签前拟路径不存在） |

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T22:33:00-04:00` reason=`leaf27_baseline_evac` |
| QUIET sha256 | `bdbef3ad0972e6fde6f0951ac34f413aa64e7dbb27e818fd92494c30d34f1deb` |
| healthz quiet=true | `2026-10-25T22:33:16-04:00`（锁后首轮即 true） |
| ≥15s 后复检 | `2026-10-25T22:33:32-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py\|[e]xport_static.py\|[s]napshot.py\|[g]en.py` **空** |

## 盘证硬钉

| 件 | sha8 / 全长 |
|---|---|
| 脚本 `research/leaf27_chunked_members_mktcap_r1.py` | `585ba746` / `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`（禁 `27aae6db`/`8cb3e86f`/`262f9bf6`） |
| HAND 盘上 DRAFT_HAND | `b0e01ea4` / `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` |
| H2A | `416df9b9` / `416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676` |
| COVER / CMD / DIFF / VERIFY | `0ff59ed4` / `bf6ffe4a` / `dc802879` / `7ddd47e3` |
| 窗令 / 审阅 | `5930388b` / `84fb87cf` |
| forbid 七票 | `e107383f`,`2be59acd`,`a7d98ac9`,`8e51de63`,`3a6caa4f`,`8bcd79dc`,`725be3e0` |
| 三 tag | `baseline_evac_r1`+`mktcap_cache_r1`+`hist_prune_r1` |
| OUT_DIR 签文钉 | `…hiliq_x2_baseline_evac` |
| sampler | `/tmp/quantlab_leaf27_chunked_baseline_evac_*` |
| rss | 1500 禁抬；peak_proof REQUIRED |

## 结论

预检 **PASS** → 本拍签发 `.ok` + 保留 QUIET（不代跑、不 lift）。≠X2；live=false。
