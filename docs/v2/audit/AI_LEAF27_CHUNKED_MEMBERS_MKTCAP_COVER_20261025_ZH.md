# 叶27 下一包封面：members/mktcap 分块装载（chunked r1）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T12:23:09-04:00（America/New_York）
- **状态**：**交审 DRAFT** · **不申 `.ok`** · **不实跑** · live=false · promotion_approved=false
- **优先级**：次于叶25 real_peak r2（Arch 审中）；本包仅文档+脚本落盘

## 一句话

LOWMEM v1 在 `members_loaded days=644` 即峰≈1877–1933MB 破帽；本包按 Arch 审计 **P1-4**（sha8 **`c8877760`**）改为 **按季（默认）分块装** members + mktcap（+capadv）→用完 `del+gc`，**rss_limit 仍 1500、禁抬帽**。

## Arch 硬钉（写入对照）

| 钉 | 本包 |
|---|---|
| 审计指针 P1-4 sha8 `c8877760`（12:11 ET） | **MATCH** 全文 sha256 `c8877760dbf1c5b2158b7dd9136bc95d9d09ea5b11cd7ba4d219de2c86673c1a` |
| 须 members/mktcap **分块装载** | **YES** — `split_calendar_chunks` + per-chunk load |
| **禁**同 cmd 复用旧窗 | **YES** — 新脚本路径；CMD 草案显式新 CLI；禁复用 VOID `.ok` 窗 |
| **禁抬帽** rss≤1500 | **YES** — `RSS_LIMIT_MB=1500` 硬常量 + stage soft gate |
| **禁 RESTORED** `8bcd79dc…` / `725be3e0…` | **YES** — 封面/脚本/CMD 三处钉禁；不消费任何 VOID/CONSUMED |
| 禁自开跑；交 Arch 另审后再谈窗 | **YES** — 本回合仅 `--dry-compile-only` 验证；**未申 `.ok`** |

## SUPERSEDED / 禁复用

| 项 | sha256 / sha8 | 处置 |
|---|---|---|
| lowmem_v1 脚本 | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | SUPERSEDED_FOR_CHUNKED_LOAD（因子钉仍复用其 helper；**不改其字节**） |
| lowmem HILIQ×x2 `.ok` | `8bcd79dcc7a0e10640f2b7807a7e632ba2a6b7e20e385dfc1d58d07487fc9078` / `8bcd79dc` | **VOID · 禁 RESTORED · 禁同 cmd** |
| 旧 HI_LIQ `.ok` | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` / `725be3e0` | **VOID · 禁复用** |
| ABORT 回执 | `5b212115445bdf3a0a01748547e7782e703f5b83f486bda3bcf87daa80f27649` | 旁证（峰 1877MB @ members_loaded） |

## 机制（装载路径）

1. **切块**：默认 `--chunk-mode quarter`（可选 `month` / `ndays`，默认 ndays=60）
2. **每块**：
   - `member_and_suspend_chunk`：按 mask parquet **row-group date stats** 剪枝，只物化本块 sessions 的 set
   - `load_mktcap_chunk(dates_needed)`：本块 sessions ∪ 块首 T−1 前一交易日（PIT）
   - `load_capadv_chunk`：同块 span 过滤
   - 日循环（因子序与 lowmem_v1 **零改**）
   - 块末 `members/mktcap/capadv.clear()` + `del` + `gc.collect()`
3. **跨块保留**：`ret_hist` / `eps_hist` / `mkt_hist`（β60 / W20 连续）
4. **软闸**：任一装载 stage `rss_mb()>1500` → `ABORT_RSS_OVER_LIMIT`（**不**申请抬帽）
5. **CLI 拒**：`--universe FULLA|both`；`--window both`（首授权仅单窗）

## 峰值目标

| 项 | 值 |
|---|---|
| rss_limit | **1500 MB**（与既往 lowmem 同帽；**禁抬**） |
| 旧失败峰 | ≈1877–1933MB（644 日一次 `load_*`）/ 更早 HI_LIQ≈3557MB |
| 本包目标 | 单块 members+mktcap+capadv 常驻 ≪1500；全窗靠块间释放 |
| 证明状态 | **未实跑** — 峰只能由 Arch 另签窗后证明 |

## 因子钉（零改声明）

- `mechanism_tag=g1g5_ashare_on_minus_id_idio_ivol_v1`
- α_raw=−ivol；β60/min40；W20/min15
- 残差序：SW demean → logMV T−1 → β → capadv `target_weight` → ivol → size-domain
- `limit_policy=exclude_hit_or_unknown`；HI_LIQ only；FULLA GAP
- 路径钉：mktcap `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` / capadv HILIQ / etf 与 lowmem_v1 同 pin

## 新包盘证（全长）

| 件 | 路径 | sha256 |
|---|---|---|
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_DIFF_20261025.diff` | `b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635` |
| CMD 草案 | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_CMD_DRAFT_20261025_ZH.md` | `cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb` |
| 封面本文 | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_COVER_20261025_ZH.md` | （见文末盘证） |

## 静态检查（本回合）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf27_chunked_members_mktcap_r1_compile.pyc` | PASS |
| `pyflakes`（隔离 venv） | PASS（clean） |
| `--dry-compile-only` | PASS（`live:false`；`ok_requested:false`；`rss_limit_mb:1500`） |
| 实跑 / 读大表 | **未做**（禁） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 `rss_limit`
- RESTORED 或消费 `8bcd79dc` / `725be3e0` 及任何 VOID/CONSUMED
- 同 cmd 复用旧 LOWMEM×x2 窗
- `--window both` 首跑；FULLA
- 干扰叶25 r2 审阅文件；碰 mem_probe
- git commit

## 请 Arch / 主

1. **Arch**：审本 DIFF+封面+脚本；静态 PASS 后再议独立 probe/run `.ok`（**本包不申**）
2. **主**：P0 仍=叶25 r2；本包并行文档级；排窗须新 `.ok` 且 CLI 钉本脚本 sha
3. 若单季仍破帽：可再收紧为 `--chunk-mode month` 或 `ndays`（仍禁抬帽）

live=false。

## 落盘 sha256sum（盘证）

| 路径 | sha256 |
|---|---|
| `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_DIFF_20261025.diff` | `b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635` |
| `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_CMD_DRAFT_20261025_ZH.md` | `cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb` |
| `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_COVER_20261025_ZH.md` | （本文件；以 `sha256sum` 盘证为准） |

live=false。
