# Arch 叶25 X2 selfcheck_v2 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-26T16:21:06-04:00`（America/New_York） |
| 主令窗 | oral **16:15–17:45 ET** expires **17:47**；主 URGENT SIGN @16:16 ET |
| 审阅 | `23f371a1…` **PASS_WITH_CONDITIONS** |
| 催签 | 主 URGENT（例程未落盘→Arch 入窗立刻 SIGN） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶25 X2 selfcheck_v2（PRIMARY：钉既有 HILIQ×x2 全叶 alpha → 评价权重 → selfcheck_v2）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ Book-Smoke**；**≠ RESTORED** 十二票（含构建票 `3c297052`）；构建脚本 **UNCHANGED** `de7b3647`；脚本 `b1db0886`；HAND 钉盘上 **`41c9d8a6…`**（status=DRAFT_READY_FOR_ARCH_HOLD）；H2A 钉盘上 **`13294f83…`**（status 盘 READY_FOR_MAIN_SUBMIT vs 主令视作 SUBMITTED）；**PIN_GAP PARTIAL**（缺 β120/mom/logADV20/vol20；CFACC 已实装 TTM 脱敏；**勿称全残差齐**）；rss 软/硬 **1500** + 脚本硬 ABORT + peak_proof **REQUIRED**；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→硬 ABORT 停+上报（禁抬帽）。全叶 alpha CONSUMED **不解阻** X2。SELFCHECK_EXECUTED@签=**false**。**≠A18**（Eng `.ok` `6de02e74` 另线 ≥17:45）。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `ebc673bf` / `ebc673bfb64154d9226b6d1b65c3180411223cc00ca990fc6fac8a5da8bc6872` |
| 脚本 | `research/leaf25_x2_selfcheck_v2.py` = `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` |
| 构建脚本 UNCHANGED | `research/leaf25_full_factor_alpha_build_r1.py` = `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` |
| 审阅 | `23f371a1109ec19b6719ab2d2ac853778a1a0f830d360da6abbda03407c73274` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / VERIFY | `c151d3514764d680842e7f8f0f721de58a865e8541046cfaae423d88879a3073` / `e2dde42d2def49e62f9575a9154dfa368cee01a211ee1c98ebec7a9070361c3c` / `eba5b6b209a0027535e45de15a7487eaf1ee18b01845c1395fe363b8cb20f3b0` / `7b7ad21c0a776b63611f897dbf4a731b16e3f1b275459fcbdb08c1dced02aa0b` |
| HAND 盘上 / H2A | `41c9d8a6d137aa5005cd464ba754441e465e75df0cdc6d4d0a5f569f81564c30` / `13294f83af0729a6754bd0d65a515447e1cafa7fea889708bc9656388c6fa5b4` |
| PIN | `16706b04e015a1511ee88d04e11d5627ac7b403ea7f14984d40471d359cacbcc` |
| CONSUMED / RUN_RECEIPT | `fb19ac28411e25f6e34ca7f35202c74f7075a4958cabe4c01210c260d6f78997` / `b8c0b050d249490dedc78af4acecfebc7a4c3a08e0c42247bf6f1d99a85c669b` |
| alpha / meta | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` / `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` |
| 窗期 | `2026-10-26T16:15:00-04:00` → `2026-10-26T17:45:00-04:00`；expires `2026-10-26T17:47:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet --execute` |
| FALLBACK | **无**；峰＞1500 / 失败 → 硬 ABORT 停+上报（禁抬帽） |
| rss 软/硬 | **1500** / **1500** MB；forbid_raise_rss；script_hard_abort_rss=true |
| PIN_GAP | **PARTIAL**（β120/mom/logADV20/vol20；CFACC IMPLEMENTED_TTM_desens；claim_full_residual=false） |
| 采样（若启用） | 仅 `/tmp/quantlab_leaf25_x2_selfcheck_*` |
| 产物 | `_selfcheck/` + `leaf_reports/leaf25_full_factor/selfcheck_v2.json`（禁覆写钉盘 alpha/meta） |
| 禁 RESTORED | 十二票含 `3c297052`（`e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,3c297052`） |
| Book-Smoke / X2 ACCEPT | **false** / **false** |
| peak_proof | **REQUIRED** |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock` sha `5282f37f` / `5282f37fd78447713932733ce02fb3a22931d83e006e23db16222544a8d9d239`（保留不 lift） |
| MemAvailable@签 | 11398360 kB |
| ≠A18 | Eng `.ok` `6de02e74` 另线 ≥17:45；本票未触 |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-26T16:21:06-04:00` reason=leaf25_x2_selfcheck_v2 |
| pgrep kline/export_static/snapshot/gen | 空 |
| SELFCHECK_EXECUTED@签 | **false**（无 `_selfcheck/`、无 `selfcheck_v2.json`） |

## 下一跳

1. **主** MATCH 后令 AI prelaunch 单次 PRIMARY selfcheck_v2（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（权重 sha + selfcheck_v2.json sha + peak rss + **PIN_GAP PARTIAL 复述**；峰＞1500→硬 ABORT 停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；不解阻全量 X2；≠A18；live=false；**不报 Leo**
