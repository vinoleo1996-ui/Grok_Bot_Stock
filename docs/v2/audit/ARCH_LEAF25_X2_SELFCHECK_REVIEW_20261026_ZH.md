# Arch 审阅：叶25 X2 selfcheck_v2 独立票（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-26T13:44:00-04:00`（America/New_York；墙钟 `2026-10-26 13:44 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 CLI；不改主干；不抬 rss 帽；**不解阻 X2**；禁当 X2 ACCEPT；≠X2；live=false；promotion=false；**不推 Leo**；**不混 A18 方案 A** |
| 触发 | 主 13:40 ET 交审（TEAM_STATE 顶条）；**无** `MAIN_LEAF25_X2_SELFCHECK*_SUBMIT*` 文件 → 开审授权以主令消息 + 包钉为准 |
| 对照 | PIN `16706b04` · COVER `c151d351` · CMD `e2dde42d` · DIFF `eba5b6b2` · HAND `41c9d8a6` · VERIFY `7b7ad21c` · H2A `13294f83` · 脚本 `b1db0886` · 构建 UNCHANGED `de7b3647` · alpha `8be12024` · meta `44c27f54` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 钉既有 HILIQ×x2 全叶 alpha（`8be12024`）→ §3.3 评价权重 → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v2.json`；**≠** 复跑 alpha 构建 / **≠** Book-Smoke / **≠** X2 ACCEPT。新脚本 `b1db0886` 不覆写钉盘 alpha/meta，不碰构建脚本 `de7b3647`；产物隔离 `_selfcheck/` + `leaf_reports/leaf25_full_factor/selfcheck_v2.json`。**SELFCHECK_EXECUTED=false** 盘证成立（无 `_selfcheck/`、无报告目录、无 `selfcheck_v2.json`）。rss 软/硬同钉 **1500** + `check_rss_hard` **硬 ABORT**（优于叶27仅软披露）+ peak_proof。**PIN_GAP PARTIAL**（β120/mom/logADV20/vol20；CFACC 已实装；**勿称全残差齐**）须入签文。forbid **十二**票含构建票 **`3c297052`**。HAND/H2A 盘上仍 HOLD/READY_FOR_MAIN_SUBMIT，主令已交审 → status 漂移记 CONDITIONS。**本回合不签 `.ok`**；等主另排签窗 + 新 `.ok`（禁 RESTORED 十二票含 `3c297052`）。A18 方案 A **另线**勿混本票。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 脚本（新 CHANGED） | `research/leaf25_x2_selfcheck_v2.py` | `b1db0886` | `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` | **MATCH** |
| PIN | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` | `16706b04` | `16706b04e015a1511ee88d04e11d5627ac7b403ea7f14984d40471d359cacbcc` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_COVER_DRAFT_20261026_ZH.md` | `c151d351` | `c151d3514764d680842e7f8f0f721de58a865e8541046cfaae423d88879a3073` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_CMD_DRAFT_20261026_ZH.md` | `e2dde42d` | `e2dde42d2def49e62f9575a9154dfa368cee01a211ee1c98ebec7a9070361c3c` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DIFF_DRAFT_20261026.diff` | `eba5b6b2` | `eba5b6b209a0027535e45de15a7487eaf1ee18b01845c1395fe363b8cb20f3b0` | **MATCH** · 正文 ≡ 脚本 393 行 |
| HAND | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DRAFT_HAND_20261026_ZH.md` | `41c9d8a6` | `41c9d8a6d137aa5005cd464ba754441e465e75df0cdc6d4d0a5f569f81564c30` | **MATCH** · status=**DRAFT_READY_FOR_ARCH_HOLD** |
| VERIFY | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DRAFT_VERIFY_20261026_ZH.md` | `7b7ad21c` | `7b7ad21c0a776b63611f897dbf4a731b16e3f1b275459fcbdb08c1dced02aa0b` | **MATCH** · HOLD / SELFCHECK_EXECUTED=false |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_HAND_TO_ARCH_20261026_ZH.md` | `13294f83` | `13294f83af0729a6754bd0d65a515447e1cafa7fea889708bc9656388c6fa5b4` | **MATCH** · 盘上 **READY_FOR_MAIN_SUBMIT** |
| Arch CONSUMED | `docs/v2/audit/ARCH_LEAF25_FULL_FACTOR_ALPHA_BUILD_CONSUMED_PASS_20261026_ZH.md` | `fb19ac28` | `fb19ac28411e25f6e34ca7f35202c74f7075a4958cabe4c01210c260d6f78997` | **MATCH** |
| AI RUN_RECEIPT | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2_RUN_RECEIPT_20261026_ZH.md` | `b8c0b050` | `b8c0b050d249490dedc78af4acecfebc7a4c3a08e0c42247bf6f1d99a85c669b` | **MATCH** |
| alpha | `output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet` | `8be12024` | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` | **MATCH** |
| meta | `output/ai_factory/_leaf25_full_factor/20261026_015610/run_meta.json` | `44c27f54` | `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` | **MATCH** |
| 构建脚本 | `research/leaf25_full_factor_alpha_build_r1.py` | `de7b3647` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` | **MATCH UNCHANGED** |

**路径注**：除 PIN 外，COVER/CMD/DIFF/HAND/VERIFY/H2A 盘上文件名**无**中间 `_V2_`（与 PIN 的 `…_V2_PIN_…` 不一致）；sha8 与主令包钉一致，以盘上实名+全长为准。

live `.ok`=0；拟 `.ok` **未创建**；`output/loop` **无** QUIET 锁（叶25 构建 QUIET 已 lift `a4857568`）；本审**未挂** QUIET；`_selfcheck/` **不存在**；`leaf_reports/leaf25_full_factor/` **不存在**；`selfcheck_v2.json` **不存在** → **SELFCHECK_EXECUTED=false** 成立。无 `MAIN_LEAF25_X2_SELFCHECK*_SUBMIT*` → 开审授权以主 13:40 交审令 + 包钉为准。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：钉 alpha → 权重 → selfcheck_v2 | **PASS** | COVER/CMD/脚本：HILIQ×x2；硬钉 alpha+meta 全长 sha；`build_eval_weights` → `_selfcheck/eval_weights_*.parquet` → `LC.evaluate` → `leaf_reports/leaf25_full_factor/selfcheck_v2.json`；**非**重算 alpha |
| 2 | ≠ 复跑 alpha 构建 / Book-Smoke / X2 ACCEPT | **PASS** | 封面/CMD/脚本 dry meta：`book_smoke:false` `x2_accept:false` `alpha_build_consumed_not_x2_accept:true`；构建脚本禁改 |
| 3 | SELFCHECK_EXECUTED=false | **PASS** | PIN/VERIFY/HAND/H2A 明文 false；盘上无权重实数、无报告；本审**未代跑** CLI |
| 4 | CONSUMED 不解阻 X2；另包另审 | **PASS** | 主令/COVER/CONSUMED `fb19ac28` 明文；本票独立脚本 `b1db0886`；禁复用 `3c297052` |
| 5 | forbid **十二**票禁 RESTORED | **PASS** | COVER/CMD/脚本 `FORBID_RESTORED` 十二票齐，含 **`3c297052`** |
| 6 | rss 软/硬帽 1500 + 硬 ABORT + peak_proof | **PASS** | 脚本 `RSS_SOFT_MB=RSS_HARD_MB=1500`；`check_rss_hard` 破则 `SystemExit`（硬 ABORT）；`peak_proof_required=true`；`forbid_raise_rss:true`（dry） |
| 7 | 不改写 alpha / 不碰 `de7b3647` | **PASS** | 写路径仅 `_selfcheck/*` + `selfcheck_v2.json` + side_meta；`assert_pins` 路径+全长 sha；构建脚本实测仍 `de7b3647` |
| 8 | 输出路径隔离 | **PASS** | `SELFCHECK_SUB=…/20261026_015610/_selfcheck`；报告 `leaf_reports/leaf25_full_factor/selfcheck_v2.json`；不覆写钉盘 run_meta/alpha |
| 9 | DIFF vs 脚本 | **PASS** | `/dev/null`→新文件；去头 `+` 正文 393 行 ≡ `research/leaf25_x2_selfcheck_v2.py` |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | CMD/主令逐字：`PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet --execute`；无同票 FALLBACK |
| 11 | `--execute` 门 / 无 .ok 运行时检查 | **PASS_WITH_CONDITIONS** | 缺 `--execute` → exit 2；`--execute` **alone** 仍 `live:false` 但**不**校验 live `.ok` 存在 → 流程门（新 `.ok`+主窗）必须签文硬钉 |
| 12 | 权重规则 §3.3 | **PASS** | NAME_W=0.04 · MAX_NAMES=20 · REBAL_EVERY=5 · IND_CAP(HILIQ)=0.25 · BALLAST=510300.SH · HARD_EXCLUDE={600519.SH,002371.SZ}；无单独 gate 列；SW L1 asof 挂行业 |
| 13 | **PIN_GAP PARTIAL** 披露 | **PASS** | 脚本 `pin_gap_disclosure` + meta `residual_covars_status.overall=PARTIAL`；缺口 β120/mom/logADV20/vol20；CFACC IMPLEMENTED；`claim_full_residual=false`；COVER/CMD/PIN/HAND/H2A 齐 |
| 14 | HAND / H2A status 漂移 | **PASS_WITH_CONDITIONS** | HAND=`DRAFT_READY_FOR_ARCH_HOLD`；H2A=`READY_FOR_MAIN_SUBMIT`（明示勿写 SUBMITTED）；主令已交审 → 同叶27口径；签时钉**盘上**全长 |
| 15 | sampler | **PASS_WITH_CONDITIONS** | CMD/脚本钉 `/tmp/quantlab_leaf25_x2_selfcheck_*`；脚本**未内建** sampler → 若启用须签文/prelaunch 外挂；禁其它前缀 |
| 16 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | alpha≈11MB / 1633512 行 / 570 日；`evaluate` 按名装 panel + capacity_adv 叠层 → 峰可能贴/破 1500；硬 ABORT 会停，但静态审 ≠ 峰证明；peak_proof REQUIRED |
| 17 | 静态自检（AI 宣称；本审未复跑） | **PASS**（采信 VERIFY） | VERIFY：`--dry-compile-only` / py_compile→/tmp / pyflakes exit0；本审遵「禁代跑」未复跑 |
| 18 | 叶26 / A18 隔离 | **PASS** | 叶26 不交审；A18 方案 A 另线（TEAM_STATE 另条）；本审未触 A18 物化 |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**消费**全叶 alpha 构建已落盘产物（`8be12024` / meta `44c27f54`；peak_kb=751032；parts=29），生成评价权重并跑 selfcheck_v2；**不是**再建 alpha，**不是** Book-Smoke，**不是** X2 ACCEPT。CONSUMED_PASS（Arch `fb19ac28` / `.ok` 内容 `3c297052`→归档 `d37a157e`）仅证明构建票完结，**不解阻**本票开跑，更**不解阻 X2**。

### 3.2 PIN_GAP PARTIAL（签文必披露）

| 字段 | 状态 |
|---|---|
| β120 / mom / logADV20 / vol20 | **PIN_GAP**（meta 与脚本一致） |
| CFACC TTM+desens | **已实装**（mechanism / pin_gap.cfacc_ttm_desens=IMPLEMENTED） |
| overall | **PARTIAL** |
| 禁称 | **全残差齐** / 全 residual 齐备 |

回执与签文须复述本表；selfcheck 数字即使「过闸」亦不抹平 PIN_GAP。

### 3.3 残余风险（须写入签条件）

1. **evaluate 装载面**：多票 panel + capacity_adv 叠层；硬 ABORT 会停，但仍须 peak_proof；MemAvailable 听主软地板；建议短窗错开其它研究实跑。
2. **`--execute` 无 `.ok` 校验**：禁在无新 `.ok`/窗外执行；流程门由主+Arch 执守。
3. **H2A/HAND status 漂移**：签 `.ok` 钉盘上 HAND `41c9d8a6…` / H2A `13294f83…` 全长（若 AI 后改 status，以签时盘证为准）。
4. **`selfcheck_v2.json` 固定路径**：重跑会覆写报告；权重/side_meta 带 stamp；回执须交权重 sha + 报告 sha + peak + **PIN_GAP PARTIAL 复述**。
5. **≠X2 ACCEPT**：selfcheck 数字即使「过闸」亦不自动构成 X2/ACCEPT/晋级；全叶 alpha CONSUMED 不解阻 X2。
6. **禁 RESTORED `3c297052`**：构建票内容已归档 `d37a157e`；新签禁复用/恢复。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑与 **A18 方案 A** 物化；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3`（sha8 **`b1db0886`**）
   - CLI PRIMARY 逐字 = CMD：`--universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet --execute`
   - 钉两件：alpha `8be12024…` / meta `44c27f54…`
   - **无**同票 FALLBACK；失败/异常/硬 ABORT → 停 + 上报
   - `rss_soft_mb=1500` · `rss_hard_mb=1500` · `forbid_raise_rss=true`；破硬帽脚本 ABORT；禁抬帽
   - `forbid_restored_ok_sha8`：**十二票** `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**
   - 构建脚本 **UNCHANGED** `de7b3647`（禁改字节）；禁动已 CONSUMED 归档 `.ok`
   - sampler（若启用）：`/tmp/quantlab_leaf25_x2_selfcheck_*` only
   - 权重目录：`…/_leaf25_full_factor/20261026_015610/_selfcheck/`；报告：`…/leaf_reports/leaf25_full_factor/selfcheck_v2.json`
   - **PIN_GAP PARTIAL** 明文入签文（β120/mom/logADV20/vol20；CFACC已实装；勿称全残差齐）
   - HAND/H2A/COVER/CMD/DIFF/VERIFY/PIN/本审 全长钉入签文
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · **alpha_build_consumed_not_x2_accept=true**
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核）后 `--execute`；交回执（权重 sha + selfcheck_v2.json sha + peak rss + **PIN_GAP PARTIAL 复述**）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`rss_mb_peak_self` / `peak_proof.ru_maxrss_mb`；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻叶26/全量 X2；本审不构成自动开跑授权；**不混 A18**。
6. 禁 RESTORED 任一 VOID/CONSUMED（含归档 `d37a157e` 所对应内容 `3c297052`）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**
- 禁抬 rss 软/硬帽；禁 Book-Smoke；禁当 X2 ACCEPT；禁复跑 alpha 构建
- 禁改 `research/leaf25_full_factor_alpha_build_r1.py`（`de7b3647`）；禁动已 CONSUMED `.ok`
- 禁开叶26 交审 / 叶28/29；禁把 CONSUMED_PASS 当本票授权；禁称全残差齐
- 禁静默 fallback / 禁换 universe/window / 禁换 alpha 路径
- **禁混 A18 方案 A** 签窗/物化入本票

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认后排下一空窗（例 45min + expires+2）；签时 QUIET；与其它 leaf 实跑及 A18 §5.x **错开**。
- 拟名：`output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`；**新签**，禁复用十二票任一内容（尤其 **`3c297052`**）。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**任何 CLI（含 `--dry-compile-only` / `--execute`）
- **未改**主干代码 / 构建脚本 / 钉盘 alpha
- **未动**叶25 已 CONSUMED `.ok`（内容 `3c297052` / 归档 `d37a157e`）
- **未触** A18 方案 A 签文/物化
- **不解阻 X2**；**不当 X2 ACCEPT**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH；PRIMARY 语义正确；SELFCHECK_EXECUTED=false 成立；forbid 十二票齐（含 `3c297052`）；rss 硬 ABORT+peak_proof；PIN_GAP PARTIAL 已披露；DIFF≡脚本；输出隔离。开放项见 §4（新窗+新 `.ok`、流程门、peak_proof、H2A/HAND 盘上全长、PIN_GAP 复述、禁 RESTORED/禁 X2 ACCEPT、错开 A18）。**可请主排签窗**；本回合不签。

审阅文 sha8：落盘后由执行器钉（见文末）。

live=false。
