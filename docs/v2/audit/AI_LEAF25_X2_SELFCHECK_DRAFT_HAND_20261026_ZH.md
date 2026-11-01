# 叶25 X2 selfcheck_v2 独立侧稿 HAND 回执 · **DRAFT_READY_FOR_ARCH_HOLD**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T13:35:00-04:00（America/New_York；墙钟 2026-10-26 13:35 ET）
- **status**：**DRAFT_READY_FOR_ARCH_HOLD** — **未**声称已 SUBMITTED 给 Arch；本回合只回主；等主交审
- **ok_requested**：false · **live**：false · **实跑**：未做 · **SELFCHECK_EXECUTED=false** · **`.ok`**：未申 · **QUIET**：本回合 **未挂/未擅 lift**（既有 lift `a4857568`）
- **三件+脚本盘证**：COVER `c151d351` / CMD `e2dde42d` / DIFF `eba5b6b2`；脚本 **CHANGED** `b1db0886`；构建脚本 UNCHANGED `de7b3647`
- **触发**：主令 13:31 — 全叶 alpha CONSUMED 后做 selfcheck_v2→X2 另包 DRAFT；钉 alpha `8be12024`
- **PIN_GAP PARTIAL**：β120/mom/logADV20/vol20；CFACC TTM+desens 已实装；**勿称全残差齐**

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| PIN | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` | `16706b04e015a1511ee88d04e11d5627ac7b403ea7f14984d40471d359cacbcc` |
| COVER | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_COVER_DRAFT_20261026_ZH.md` | `c151d3514764d680842e7f8f0f721de58a865e8541046cfaae423d88879a3073` |
| CMD | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_CMD_DRAFT_20261026_ZH.md` | `e2dde42d2def49e62f9575a9154dfa368cee01a211ee1c98ebec7a9070361c3c` |
| DIFF | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DIFF_DRAFT_20261026.diff` | `eba5b6b209a0027535e45de15a7487eaf1ee18b01845c1395fe363b8cb20f3b0` |
| 脚本（CHANGED） | `research/leaf25_x2_selfcheck_v2.py` | `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` |
| alpha（钉） | `output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet` | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` |
| meta（钉） | `output/ai_factory/_leaf25_full_factor/20261026_015610/run_meta.json` | `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` |

sha8 速查：PIN **`16706b04`** · COVER **`c151d351`** · CMD **`e2dde42d`** · DIFF **`eba5b6b2`** · 脚本 **`b1db0886`** · alpha **`8be12024`** · meta **`44c27f54`**

## 对照钉

| 钉 | 值 |
|---|---|
| PRIMARY | HILIQ × x2 selfcheck_v2（钉既有 alpha） |
| ≠ | 复跑 alpha 构建 / Book-Smoke / X2 ACCEPT |
| Arch CONSUMED | `fb19ac28`（不解阻 X2） |
| AI RUN_RECEIPT | `b8c0b050` |
| forbid 十二票 | `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`** |
| 构建脚本 | `de7b3647` UNCHANGED |
| rss 软/硬帽 | 1500 禁抬 + peak_proof |
| sampler | `/tmp/quantlab_leaf25_x2_selfcheck_*` only（若启用） |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` |
| PIN_GAP | PARTIAL · β120/mom/logADV20/vol20；CFACC 已实装 |
| Gate | decay + A/B/current |
| 交审门 | **等主交审**；本 HAND **未** SUBMITTED_TO_ARCH |
| ok_requested | **false** |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑 evaluate；**未** git commit
- **未**写 eval_weights 实数；**未**读大行情
- 静态 py_compile→/tmp / pyflakes / `--dry-compile-only` OK
- **未**改 `research/leaf25_full_factor_alpha_build_r1.py`（仍 `de7b3647`）
- **未**创建拟 `.ok`；**未** RESTORED `3c297052`
- 禁自开跑 / 禁申 X2.ok / 禁复用 VOID/CONSUMED / 禁 Book-Smoke / 禁开叶28/29 / 禁并行新全窗重票
- ≠X2 · live=false · **DRAFT_READY_FOR_ARCH_HOLD**（等主交审）
