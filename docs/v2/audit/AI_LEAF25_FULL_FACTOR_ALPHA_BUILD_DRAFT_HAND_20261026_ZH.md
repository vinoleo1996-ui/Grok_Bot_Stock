# 叶25 全叶/HILIQ×x2 alpha 构建 · HAND 回执 · **DRAFT_READY_FOR_ARCH_HOLD**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T01:20:00-04:00（America/New_York；墙钟 2026-10-26 01:20 ET）
- **status**：**DRAFT_READY_FOR_ARCH_HOLD** — **未**声称已 SUBMITTED 给 Arch；本回合只回主；等主交审
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申 · **QUIET**：本回合 **未擅 lift**
- **票种**：alpha 构建（≠ selfcheck · ≠ Book-Smoke · ≠ X2 ACCEPT）
- **触发**：主令本拍「定下一票｜叶25 全叶 HILIQ×x2 alpha 构建 DRAFT」；旧 CMD `035e5818` / r6 令 `53331667` 未授权实跑

## 三件 + 脚本盘证

| 件 | 路径 | sha256 |
|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_COVER_DRAFT_20261026_ZH.md` | `07b0a1b869c15367cd0711a565327a6cdefdcc9712b6028720e2477c9d5cbd21` |
| CMD | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_CMD_DRAFT_20261026_ZH.md` | `8ab8831cb203ea42f998966d92e32231a038ef30bacbd4f260300253d918ce4e` |
| DIFF | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DIFF_DRAFT_20261026.diff` | `03d50f3f500d82fc453dd992a2e179a822f2969005114b5e4f2006d0c5269c17` |
| 脚本（NEW） | `research/leaf25_full_factor_alpha_build_r1.py` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` |

sha8 速查：COVER **`07b0a1b8`** · CMD **`8ab8831c`** · DIFF **`03d50f3f`** · 脚本 **`de7b3647`**

## 对照钉

| 钉 | 值 |
|---|---|
| 主令本拍 | 定下一票｜叶25 alpha 构建 DRAFT |
| 旧 CMD | `035e5818` |
| r6 令 | `53331667` |
| FROZEN / 基盘 / MEM | `4bb1ff2b` / `e8ca2bcc` / `103717df` |
| wrapper v5 | `4240ce82` |
| PRIMARY CLI | `--universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month` |
| rss_limit | 1500 禁抬 |
| sampler | `/tmp/quantlab_leaf25_full_alpha_*` only |
| forbid | `1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf` |
| 残差缺件 | β120 / mom / logADV20 / vol20 = PIN_GAP（CFACC 主路径已实装） |
| 交审门 | **等主交审**；Arch **只审不签**；本 HAND **未** SUBMITTED_TO_ARCH |

## 动作边界

- **未**交 Arch；**未**申 `.ok`；**未**实跑；**未** git commit
- **未**读真实行情大表做实跑；**未**抬帽；**未**启动任何实数进程
- 新脚本已落；stub / mem_probe_* **未覆盖**
- 静态 py_compile / pyflakes / dry-compile-only OK；pgrep 空
- 禁自开跑 / 禁自签 / 禁申 X2 ACCEPT / 禁复用 VOID/CONSUMED
- ≠X2 ACCEPT · live=false · **DRAFT_READY_FOR_ARCH_HOLD**（等主交审）
