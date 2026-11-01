# Arch 叶27 Gate A mktcap_cache · 签前预检证据

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T20:36:40-04:00`（America/New_York） |
| 窗令 | `docs/v2/audit/MAIN_LEAF27_CHUNKED_MKTCAP_CACHE_OK_WINDOW_20261025_ZH.md` sha8 **`c33c6382`** |
| 审阅 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_REVIEW_20261025_ZH.md` sha8 **`64057bfe`** PASS_WITH_CONDITIONS |
| live / promotion | **false** / **false** |

## 窗与场

| 项 | 值 |
|---|---|
| 签窗 | **2026-10-25 20:30–21:15 ET** expires **21:17** |
| 签时墙钟 | `2026-10-25T20:36:40-04:00` ∈ [20:30, 21:17) |
| QUIET 前 | `RESEARCH_QUIET.lock` **不存在**；8795 quiet=false |
| MemAvailable@签 | 10839220 kB（≳2.5Gi） |
| live `.ok` | 0（签前拟路径不存在） |

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T20:35:04-04:00` reason=`leaf27_mktcap_cache` |
| QUIET sha256 | `1d423cc60d9b89a6002f03ebab9c3fcefff7528e24d7f02d220797ecaac43727` |
| healthz quiet=true | `2026-10-25T20:35:04-04:00`（首轮即 true） |
| ≥15s 后复检 | `2026-10-25T20:35:20-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py\|[e]xport_static.py\|[s]napshot.py\|[g]en.py` **空** |

## 盘证硬钉

| 件 | sha8 / 全长 |
|---|---|
| 脚本 `research/leaf27_chunked_members_mktcap_r1.py` | `27aae6db` / `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`（禁 `8cb3e86f`/`262f9bf6`） |
| HAND 盘上 DRAFT_HAND | `a2abe662` / `a2abe662f741da7494c341fb70f86b18d639081ae9abf0fb0b5d8b81bcf7aef4`（禁口头 `70701c1d`） |
| H2A | `4cac1bae` / `4cac1baeaaed7b16073c079127e0733edb694742bc3a1fdf1db707ed14d724c8` |
| COVER / CMD / DIFF / VERIFY | `bf83073a` / `30c58132` / `779197d8` / `f01afc74` |
| 窗令 / 审阅 | `c33c6382` / `64057bfe` |
| forbid 六票 | `2be59acd`,`a7d98ac9`,`8e51de63`,`3a6caa4f`,`8bcd79dc`,`725be3e0` |

## 结论

预检 **PASS** → 本拍签发 `.ok` + 保留 QUIET（不代跑、不 lift）。≠X2；live=false。
