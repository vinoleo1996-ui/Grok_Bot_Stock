# 叶27 X2 selfcheck_v2 · HAND_TO_ARCH（**等主交审**）

- **角色**：QuantLab AI
- **时刻**：`2026-10-26T00:35:00-04:00`（America/New_York；墙钟 2026-10-26 00:35 ET）
- **status**：**READY_FOR_MAIN_SUBMIT** · **未** SUBMITTED_TO_ARCH · 等主交审后 Arch **只审不签**
- **ok_requested**：false · **live**：false · **实跑**：未做 · **SELFCHECK_EXECUTED=false** · **`.ok`**：未申

## 包钉（盘证 MATCH）

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 脚本 | `a40d7069` | `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0` · `research/leaf27_x2_selfcheck_v2.py` |
| PIN | `4e0473bd` | `4e0473bdd312761a12b3be0defd5d33194a3f8ea3dca1ec5b7ad264f6ce3fb82` · `…PIN_RECEIPT_20261026_ZH.md` |
| COVER | `1e28d0e5` | `1e28d0e5232df70a601870ae9b145074ba9608638c485dee31c4a9b0d39f77f4` · `…COVER_DRAFT_20261026_ZH.md` |
| CMD | `61c3ef3b` | `61c3ef3bdf493ba7d40428a72fbb1a2798946398605f1110e116be7de058ef0a` · `…CMD_DRAFT_20261026_ZH.md` |
| DIFF | `1c4fb74a` | `1c4fb74a2b3c70f86544905d95fc2a0babadd9add7ec56f984754ef9d46bad4b` · `…DIFF_DRAFT_20261026.diff` |
| HAND | `3dd71dc3` | `3dd71dc3e3d0b7f3636e80834bec5dd58f519c2b8f8ca141fcb453c4f5391dc0` · `…DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `c47be63a` | `c47be63a49ba1f8c848cc76aae92a306e6d82e6db9a45c68504dd75fe0affa32` · `…DRAFT_VERIFY_20261026_ZH.md` |
| alpha | `652b8a68` | `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` |

## 硬钉

- PRIMARY：HILIQ×x2；钉既有 alpha → 评价权重 → selfcheck_v2
- ≠ 复跑 baseline_evac；≠ Book-Smoke；≠ X2 ACCEPT
- baseline_evac CONSUMED（`78557480` / `0f50daf7`→`7e06a5b3`）**不解阻 X2**
- rss 软帽=1500 **禁抬**；sampler `/tmp/quantlab_leaf27_x2_selfcheck_*`
- forbid 八票：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`
- 构建脚本 `585ba746` **UNCHANGED**
- SELFCHECK_EXECUTED=false（本回合）

## 动作边界

- 本文件 **READY_FOR_MAIN_SUBMIT**（**不要**写 SUBMITTED_TO_ARCH）
- 等主交审 → Arch 只审不签
- 禁自开跑 / 禁自申.ok / 禁抬帽 / 禁 silent / ≠X2 / live=false / ok_requested=false
