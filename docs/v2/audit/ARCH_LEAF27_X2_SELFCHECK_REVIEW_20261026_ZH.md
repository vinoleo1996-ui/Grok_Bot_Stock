# Arch 审阅：叶27 X2 selfcheck_v2 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-26T00:40:14-04:00`（America/New_York；墙钟 `2026-10-26 00:40 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 CLI；不改主干；不抬 rss 帽；**不解阻 X2**；禁当 X2 ACCEPT；≠X2；live=false；promotion=false；**不推 Leo** |
| 触发 | 主令交审 `MAIN_LEAF27_X2_SELFCHECK_SUBMIT_REVIEW_20261026_ZH.md` sha8 **`9e0317ba`**；baseline_evac CONSUMED_PASS（Arch `78557480` / AI `1671eec4`）后 **另包** selfcheck_v2 |
| 对照 | PIN `4e0473bd` · COVER `1e28d0e5` · CMD `61c3ef3b` · DIFF `1c4fb74a` · HAND `3dd71dc3` · VERIFY `c47be63a` · H2A `48aa5db7` · 脚本 `a40d7069` · 构建 UNCHANGED `585ba746` · alpha `652b8a68` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有 HILIQ×x2 alpha → §3.3 评价权重 → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v2.json`；**≠** 复跑 baseline_evac / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `a40d7069` 不覆写钉盘 alpha/meta/summary，不碰构建脚本 `585ba746`；产物隔离 `_selfcheck/` + `leaf_reports/…/selfcheck_v2.json`。**SELFCHECK_EXECUTED=false** 盘证成立（无 `_selfcheck/`、无 `selfcheck_v2.json`）。rss 软帽 **1500** 文案禁抬（脚本为软披露、无硬 ABORT 门）。HAND/H2A 盘上仍 HOLD/READY_FOR_MAIN_SUBMIT，主令已交审 → status 漂移记 CONDITIONS。**本回合不签 `.ok`**；等主另排签窗 + 新 `.ok`（禁 RESTORED 八票含 `0f50daf7`）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 主交审令 | `docs/v2/audit/MAIN_LEAF27_X2_SELFCHECK_SUBMIT_REVIEW_20261026_ZH.md` | `9e0317ba` | `9e0317ba7feb8ed434ca7069ee099072f5d2a87c225d5d35bca1886b1e4e1fa3` | **MATCH** |
| 脚本（新 CHANGED） | `research/leaf27_x2_selfcheck_v2.py` | `a40d7069` | `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_COVER_DRAFT_20261026_ZH.md` | `1e28d0e5` | `1e28d0e5232df70a601870ae9b145074ba9608638c485dee31c4a9b0d39f77f4` | **MATCH** |
| CMD | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_CMD_DRAFT_20261026_ZH.md` | `61c3ef3b` | `61c3ef3bdf493ba7d40428a72fbb1a2798946398605f1110e116be7de058ef0a` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DIFF_DRAFT_20261026.diff` | `1c4fb74a` | `1c4fb74a2b3c70f86544905d95fc2a0babadd9add7ec56f984754ef9d46bad4b` | **MATCH** · 正文 ≡ 脚本 288 行 |
| HAND | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DRAFT_HAND_20261026_ZH.md` | `3dd71dc3` | `3dd71dc3e3d0b7f3636e80834bec5dd58f519c2b8f8ca141fcb453c4f5391dc0` | **MATCH** · status=**DRAFT_READY_FOR_ARCH_HOLD** |
| VERIFY | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DRAFT_VERIFY_20261026_ZH.md` | `c47be63a` | `c47be63a49ba1f8c848cc76aae92a306e6d82e6db9a45c68504dd75fe0affa32` | **MATCH** · HOLD / SELFCHECK_EXECUTED=false |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_HAND_TO_ARCH_20261026_ZH.md` | `48aa5db7` | `48aa5db7f737efbb38933b83554f8807e2d4f559a1ba396b846eed7e1de2b72a` | **MATCH** · 盘上 **READY_FOR_MAIN_SUBMIT** |
| PIN | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` | `4e0473bd` | `4e0473bdd312761a12b3be0defd5d33194a3f8ea3dca1ec5b7ad264f6ce3fb82` | **MATCH** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF27_CHUNKED_BASELINE_EVAC_CONSUMED_PASS_20261025_ZH.md` | `78557480` | `7855748076e926ff2c3ac036fd0f2fbb17648f60de0187af72f4d565ff44440d` | **MATCH** |
| AI RUN_RECEIPT | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `1671eec4` | `1671eec4485ccf959f2dce754c4e6a00e5121f40c01d83b344d8327066668fb4` | **MATCH** |
| alpha | `output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet` | `652b8a68` | `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` | **MATCH** |
| meta | `…/run_meta_HILIQ_x2_20261025_224033.json` | `85c2dc78` | `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` | **MATCH** |
| summary | `…/build_summary_20261025_224333.json` | `80596bff` | `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` | **MATCH** |
| 构建脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` | **MATCH UNCHANGED** |

live `.ok`=0；`output/loop` **无** QUIET 锁；本审**未挂** QUIET；`_selfcheck/` **不存在**；`selfcheck_v2.json` **不存在** → **SELFCHECK_EXECUTED=false** 成立。开审授权以主令 `9e0317ba` + 包钉为准。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 alpha → 权重 → selfcheck_v2 | **PASS** | COVER/CMD/脚本：HILIQ×x2；硬钉三件全长 sha；`build_eval_weights` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate` → `leaf_reports/…/selfcheck_v2.json`；**非**重算 alpha |
| 2 | ≠ 复跑 baseline_evac / Book-Smoke / X2 ACCEPT | **PASS** | 封面/CMD/脚本 dry meta：`book_smoke:false` `x2_accept:false` `baseline_evac_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | SELFCHECK_EXECUTED=false | **PASS** | PIN/VERIFY/HAND/H2A 明文 false；盘上无权重实数、无报告；本审**未代跑** CLI |
| 4 | CONSUMED 不解阻 X2；另包另审 | **PASS** | 主令/COVER/CONSUMED `78557480` 明文；本票独立脚本 `a40d7069`；禁复用 `0f50daf7` |
| 5 | forbid 八票禁 RESTORED | **PASS** | COVER/CMD/脚本 `FORBID_RESTORED`：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7` |
| 6 | rss 软帽 1500 禁抬 | **PASS_WITH_CONDITIONS** | 脚本 `RSS_SOFT_MB=1500` + `forbid_raise_rss:true`（dry）；**无**硬 `_check_rss`/ABORT 门（evaluate 仅披露 `peak_rss_mb`）→ 签时须钉软帽+破帽停报流程 |
| 7 | 不改写 alpha / 不碰 `585ba746` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v2.json` + side_meta；`assert_pins` 路径+全长 sha；构建脚本实测仍 `585ba746` |
| 8 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/_selfcheck`；报告 `leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json`；不覆写钉盘 run_meta/alpha/summary |
| 9 | DIFF vs 脚本 | **PASS** | `/dev/null`→新文件；去头 `+` 正文 288 行 ≡ `research/leaf27_x2_selfcheck_v2.py` |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | CMD/主令逐字：`PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path …/alpha_HILIQ_x2_20261025_224033.parquet --execute`；无同票 FALLBACK |
| 11 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → exit 2；`--execute` **alone** 仍 `live:false` 但**不**校验 live `.ok` 存在 → 流程门（新 `.ok`+主窗）必须签文硬钉 |
| 12 | 权重规则 §3.3 | **PASS** | NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH · HARD_EXCLUDE={600519.SH,002371.SZ}；无单独 gate 列（与 COVER 一致） |
| 13 | HAND / H2A status 漂移 | **PASS_WITH_CONDITIONS** | HAND=`DRAFT_READY_FOR_ARCH_HOLD`；H2A=`READY_FOR_MAIN_SUBMIT`（明示勿写 SUBMITTED）；主令已交审 → 同 baseline_evac 口径；签时钉**盘上**全长 |
| 14 | sampler | **PASS_WITH_CONDITIONS** | CMD 钉 `/tmp/quantlab_leaf27_x2_selfcheck_*`；脚本**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 15 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | alpha≈32MB / 1271399 行；`evaluate` 按名 `load_panel_features_x2` + capacity_adv 叠层 → 峰可能贴/破 1500；静态审 ≠ 峰证明；peak_proof REQUIRED |
| 16 | 静态自检（AI 宣称；本审未复跑） | **PASS**（采信 VERIFY） | VERIFY：`--dry-compile-only` / py_compile→/tmp / pyflakes exit0；本审遵「禁代跑」未复跑 |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费** baseline_evac 已落盘 alpha（`652b8a68`），生成评价权重并跑 selfcheck_v2；**不是**再建 alpha，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS 仅证明构建票完结，**不解阻**本票开跑。

### 3.2 残余风险（须写入签条件）

1. **rss 软披露无硬门**：破 1500 时脚本不会自 ABORT；须签文 + AI prelaunch 纪律：峰＞1500 → **停+上报**，禁抬帽、禁静默重跑。
2. **evaluate 装载面**：多票 panel + capacity_adv 叠层；MemAvailable 须听主软地板；建议短窗错开其它研究实跑。
3. **H2A/HAND status 漂移**：签 `.ok` 钉盘上 HAND `3dd71dc3…` / H2A `48aa5db7…` 全长（若 AI 后改 status，以签时盘证为准）。
4. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守。
5. **`selfcheck_v2.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak。
6. **≠X2 ACCEPT**：selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT/晋级。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0`（sha8 **`a40d7069`**）
   - CLI PRIMARY 逐字 = CMD：`--universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute`
   - 钉三件：alpha `652b8a68…` / meta `85c2dc78…` / summary `80596bff…`
   - **无**同票 FALLBACK；失败/异常 → 停 + 上报
   - `rss_soft_mb=1500` · `forbid_raise_rss=true`；峰＞1500 → 停+上报（流程门）
   - `forbid_restored_ok_sha8`：**八票** `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**
   - 构建脚本 **UNCHANGED** `585ba746`（禁改字节）
   - sampler（若启用）：`/tmp/quantlab_leaf27_x2_selfcheck_*` only
   - 权重目录：`…/leaf27_on_minus_id_idio_ivol/_selfcheck/`；报告：`…/leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json`
   - HAND/H2A/COVER/CMD/DIFF/VERIFY/PIN/本审 全长钉入签文
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **baseline_evac_consumed_not_x2_accept=true**
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v2.json sha + peak rss）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / evaluate.`peak_rss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻叶25/全量 X2；本审不构成自动开跑授权。
6. 禁 RESTORED 任一 VOID/CONSUMED（含归档 `7e06a5b3` 所对应内容 `0f50daf7`）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**
- 禁抬 rss 软帽；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 baseline_evac
- 禁改 `research/leaf27_chunked_members_mktcap_r1.py`（`585ba746`）；禁改 lowmem / g1g5 因子路径
- 禁开叶28/29；禁把 CONSUMED_PASS 当本票授权
- 禁静默 fallback / 禁换 universe/window / 禁换 alpha 路径

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认后排下一空窗（例 45min + expires+2）；签时 QUIET；与其它 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.ok`（或主指定等价名）；**新签**，禁复用八票任一内容。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**任何 CLI（含 `--dry-compile-only` / `--execute`）
- **未改**主干代码 / 构建脚本 / 钉盘 alpha
- **不解阻 X2**；**不当 X2 ACCEPT**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确；SELFCHECK_EXECUTED=false 成立；forbid 八票齐；输出隔离；DIFF≡脚本。开放项见 §4（新窗+新 `.ok`、软帽流程门、peak_proof、H2A/HAND 盘上全长、禁 RESTORED/禁 X2 ACCEPT）。**可请主排签窗**；本回合不签。

审阅文 sha8：落盘后由父代钉（本文不自指未定稿自身 sha）。

live=false。
