# MAIN · 叶27 baseline_evac MATCH+GO

- et: 2026-10-25T22:38:00-04:00
- issuer: 主 Agent
- leaf: 27
- ticket: baseline_evac_r1 (Post-GateA · Leo 开 A)
- live: false
- neq_x2: true

## MATCH（主核盘，非口头）

| 钉 | sha8 / 值 | 盘证 |
|---|---|---|
| `.ok` | `0f50daf7` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok` |
| QUIET | `bdbef3ad` | `output/loop/RESEARCH_QUIET.lock`（Arch 保留，AI 勿 lift） |
| 窗令 | `5930388b` | 22:30–23:15 ET / expires 23:17 |
| 审 | `84fb87cf` | PASS_WITH_CONDITIONS |
| 签回收执 | `36d45a05` | Arch SIGNED |
| 预检 | `cf23c902` | Arch PREOK |
| 脚本 | `585ba746` | `research/leaf27_chunked_members_mktcap_r1.py`（禁 `27aae6db`/`8cb3e86f`/`262f9bf6`） |
| HAND | `b0e01ea4` | disk |
| H2A | `416df9b9` | |
| COVER/CMD/DIFF/VERIFY | `0ff59ed4` / `bf6ffe4a` / `dc802879` / `7ddd47e3` | |
| 8795 | quiet=true | lock 同源 |
| MemAvailable | ≈8Gi | 健康 |
| live `.ok` | 1 | 仅本票 |

## GO · 令 QuantLab AI prelaunch（单次）

- PRIMARY：HILIQ × window=x2 × chunk_mode=ndays × ndays=40
- tags：`baseline_evac_r1` + `mktcap_cache_r1` + `hist_prune_r1`
- rss abort：1500（**禁抬帽**）
- forbid 七票：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`
- sampler：`/tmp/quantlab_leaf27_chunked_baseline_evac_*`
- OUT_DIR：钉 `…hiliq_x2_baseline_evac`
- peak_proof：**REQUIRED**
- ABORT → 停；交 RUN_RECEIPT；**另票**（禁 silent 改 mode/ndays；禁重批旧 Gate A；禁复用 VOID `.ok`）
- 勿 lift QUIET；勿代签；勿申第二张 `.ok`
- ≠X2；live=false

## 收件人

1. **QuantLab AI**（priority）：立刻 prelaunch 单次，完后交 RUN_RECEIPT
2. **QuantLab Arch**（FYI）：MATCH+GO 已出；不代跑；ABORT→VOID+lift 另令

