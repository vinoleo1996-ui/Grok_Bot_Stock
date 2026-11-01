# 叶25 X2 selfcheck_v2 · HAND_TO_ARCH（**等主交审**）

- **角色**：QuantLab AI
- **时刻**：`2026-10-26T13:35:00-04:00`（America/New_York；墙钟 2026-10-26 13:35 ET）
- **status**：**READY_FOR_MAIN_SUBMIT** · **未** SUBMITTED_TO_ARCH · 等主交审后 Arch **只审不签**
- **ok_requested**：false · **live**：false · **实跑**：未做 · **SELFCHECK_EXECUTED=false** · **`.ok`**：未申

## 包钉（盘证 MATCH）

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 脚本 | `b1db0886` | `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` · `research/leaf25_x2_selfcheck_v2.py` |
| PIN | `16706b04` | `16706b04e015a1511ee88d04e11d5627ac7b403ea7f14984d40471d359cacbcc` · `…PIN_RECEIPT_20261026_ZH.md` |
| COVER | `c151d351` | `c151d3514764d680842e7f8f0f721de58a865e8541046cfaae423d88879a3073` · `…COVER_DRAFT_20261026_ZH.md` |
| CMD | `e2dde42d` | `e2dde42d2def49e62f9575a9154dfa368cee01a211ee1c98ebec7a9070361c3c` · `…CMD_DRAFT_20261026_ZH.md` |
| DIFF | `eba5b6b2` | `eba5b6b209a0027535e45de15a7487eaf1ee18b01845c1395fe363b8cb20f3b0` · `…DIFF_DRAFT_20261026.diff` |
| HAND | `41c9d8a6` | `41c9d8a6d137aa5005cd464ba754441e465e75df0cdc6d4d0a5f569f81564c30` · `…DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `7b7ad21c` | `7b7ad21c0a776b63611f897dbf4a731b16e3f1b275459fcbdb08c1dced02aa0b` · `…DRAFT_VERIFY_20261026_ZH.md` |
| alpha | `8be12024` | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` |
| meta | `44c27f54` | `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` |

## 硬钉

- PRIMARY：HILIQ×x2；钉既有 alpha → 评价权重 → selfcheck_v2
- ≠ 复跑 alpha 构建；≠ Book-Smoke；≠ X2 ACCEPT
- 全叶 alpha CONSUMED（`fb19ac28` / `3c297052`→`d37a157e`）**不解阻 X2**
- rss 软/硬帽=1500 **禁抬** + peak_proof；sampler `/tmp/quantlab_leaf25_x2_selfcheck_*`
- **PIN_GAP PARTIAL**：β120/mom/logADV20/vol20；CFACC TTM+desens 已实装；**勿称全残差齐**
- forbid 十二票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**
- 拟 `.ok`（未创建）：`output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`
- 构建脚本 `de7b3647` **UNCHANGED**
- Gate：decay + portfolio A/B/current
- SELFCHECK_EXECUTED=false（本回合）

## 动作边界

- 本文件 **READY_FOR_MAIN_SUBMIT**（**不要**写 SUBMITTED_TO_ARCH）
- 等主交审 → Arch 只审不签
- 禁自开跑 / 禁自申.ok / 禁抬帽 / 禁 silent / ≠X2 / live=false / ok_requested=false
