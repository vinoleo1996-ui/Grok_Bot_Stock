# 叶25 全叶/HILIQ×x2 alpha 构建 · HAND_TO_ARCH（**等主交审**）

- **角色**：QuantLab AI
- **时刻**：`2026-10-26T01:20:00-04:00`（America/New_York；墙钟 2026-10-26 01:20 ET）
- **status**：**READY_FOR_MAIN_SUBMIT** · **未** SUBMITTED_TO_ARCH · 等主交审后 Arch **只审不签**
- **ok_requested**：false · **live**：false · **实跑**：未做 · **`.ok`**：未申
- **票种**：alpha 构建（≠ selfcheck · ≠ Book-Smoke · ≠ X2 ACCEPT）

## 包钉（盘证 MATCH）

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 脚本 | `de7b3647` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` · `research/leaf25_full_factor_alpha_build_r1.py` |
| COVER | `07b0a1b8` | `07b0a1b869c15367cd0711a565327a6cdefdcc9712b6028720e2477c9d5cbd21` · `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_COVER_DRAFT_20261026_ZH.md` |
| CMD | `8ab8831c` | `8ab8831cb203ea42f998966d92e32231a038ef30bacbd4f260300253d918ce4e` · `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_CMD_DRAFT_20261026_ZH.md` |
| DIFF | `03d50f3f` | `03d50f3f500d82fc453dd992a2e179a822f2969005114b5e4f2006d0c5269c17` · `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DIFF_DRAFT_20261026.diff` |
| HAND | `21bf0d41` | `21bf0d418cc76427e91eb50d767b95d01b5682245d9774709ec7488d5dfc64fd` · `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `d6750c94` | `d6750c94ee32f98fd5437b0ca65f623427b5d5a291b266e32f059aa1110f8452` · `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_VERIFY_20261026_ZH.md` |

## 硬钉

- PRIMARY：HILIQ×x2；`--x2-end 20261009`；chunk-mode month；mechanism `g1g5_ashare_cfacc_desens_cs_v1`
- rss=1500 **禁抬**；C4/stop/hard 1331200/1484800/1536000；sampler `/tmp/quantlab_leaf25_full_alpha_*`
- out_dir 建议：`output/ai_factory/_leaf25_full_factor/<ET_TS>/`
- forbid：`1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf`
- 对照：旧 CMD `035e5818` / r6 令 `53331667` / FROZEN `4bb1ff2b` / 基盘 `e8ca2bcc` / MEM `103717df` / wrapper `4240ce82`
- stub / mem_probe_* **未改**；本票**新文件**
- 残差 PIN_GAP：β120/mom/logADV20/vol20 — CFACC 主路径已实装；勿误判为「全残差已齐」
- peak_proof REQUIRED（未来实跑）；本 DRAFT **未**实跑

## 请 Arch（主交审后）

1. **只审不签** — 勿在本拍签发 `.ok`
2. 审脚本 `de7b3647` + COVER/CMD/DIFF 一致性；确认 forbid / rss=1500 / 禁 FULLA
3. PASS 后等**主排签窗**再签**新** `.ok`（≠ forbid 任一）
4. 残差缺件是否挡签由主/Arch 裁；本包已明文 PIN_GAP

## 动作边界

- 本文件 **READY_FOR_MAIN_SUBMIT**（**不要**写 SUBMITTED_TO_ARCH）
- 等主交审 → Arch 只审不签 → 主排签窗
- 禁自开跑 / 禁自申.ok / 禁自签 / 禁抬帽 / 禁 silent / ≠X2 ACCEPT / ≠selfcheck / live=false / ok_requested=false
