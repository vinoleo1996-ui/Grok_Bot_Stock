# Arch 审阅：叶25 全叶 HILIQ×x2 alpha 构建（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-26T01:29:20-04:00`（America/New_York；墙钟 `2026-10-26 01:29 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**任何 CLI / research 脚本；不改主干；不抬 rss 帽；**不解阻 X2**；禁当 X2 ACCEPT；≠selfcheck；≠Book-Smoke；live=false；promotion=false；**不推 Leo** |
| 触发 | 主交审令 `MAIN_LEAF25_FULL_FACTOR_ALPHA_BUILD_SUBMIT_REVIEW_20261026_ZH.md` sha8 **`504b6a9d`**；票种=全叶 alpha 构建（新脚本 `de7b3647`） |
| 对照 | COVER `07b0a1b8` · CMD `8ab8831c` · DIFF `03d50f3f` · HAND `21bf0d41` · VERIFY `d6750c94` · H2A `2ac86676` · 脚本 `de7b3647` · 旧 CMD `035e5818` · r6令 `53331667` · FROZEN `4bb1ff2b` · 基盘 `e8ca2bcc` · MEM `103717df` · wrapper v5 `4240ce82` |

## 0. 一句话

包钉全件 **MATCH**；PRIMARY = 新脚本 `leaf25_full_factor_alpha_build_r1.py` 在 HILIQ×x2×end `20261009`×chunk-mode month 下构建 CFACC TTM+desens+部分截面残差 alpha；产物隔离 `_leaf25_full_factor/<ET_TS>/`；**≠** 探针 stub/mem_probe_r* · **≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT。rss 软帽 **1500** 文案禁抬，且脚本 `check_rss` 对 soft/hard **均硬 ABORT**（强于叶27 selfcheck 仅软披露）。**PIN_GAP**：β120/mom/logADV20/vol20 未钉 reader → **勿称全残差已齐**；CFACC TTM+desens 主路径已实装。forbid 十一票齐（`1c32ab1e`+八票+`3c19dd7d`+`6054b3bf`）。HAND=`DRAFT_READY_FOR_ARCH_HOLD` / H2A=`READY_FOR_MAIN_SUBMIT`，主令已交审 → status 漂移记 CONDITIONS。live `.ok`=0；QUIET 无。**本回合不签 `.ok`**；等主另排签窗 + 新 `.ok`（禁 RESTORED 十一票）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 主交审令 | `docs/v2/audit/MAIN_LEAF25_FULL_FACTOR_ALPHA_BUILD_SUBMIT_REVIEW_20261026_ZH.md` | `504b6a9d` | `504b6a9da3cee23c942c4de5c2afebe412cb294d9e506717c558dffb1ea2147b` | **MATCH** |
| 脚本（NEW） | `research/leaf25_full_factor_alpha_build_r1.py` | `de7b3647` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` | **MATCH** · 1110 行 |
| COVER | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_COVER_DRAFT_20261026_ZH.md` | `07b0a1b8` | `07b0a1b869c15367cd0711a565327a6cdefdcc9712b6028720e2477c9d5cbd21` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_CMD_DRAFT_20261026_ZH.md` | `8ab8831c` | `8ab8831cb203ea42f998966d92e32231a038ef30bacbd4f260300253d918ce4e` | **MATCH** · 修订自旧 `035e5818` |
| DIFF | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DIFF_DRAFT_20261026.diff` | `03d50f3f` | `03d50f3f500d82fc453dd992a2e179a822f2969005114b5e4f2006d0c5269c17` | **MATCH** · 去头 `+` 正文 ≡ 脚本 1110 行 |
| HAND | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_HAND_20261026_ZH.md` | `21bf0d41` | `21bf0d418cc76427e91eb50d767b95d01b5682245d9774709ec7488d5dfc64fd` | **MATCH** · status=**DRAFT_READY_FOR_ARCH_HOLD** |
| VERIFY | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_DRAFT_VERIFY_20261026_ZH.md` | `d6750c94` | `d6750c94ee32f98fd5437b0ca65f623427b5d5a291b266e32f059aa1110f8452` | **MATCH** · HOLD / 未实跑 |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF25_FULL_FACTOR_ALPHA_BUILD_HAND_TO_ARCH_20261026_ZH.md` | `2ac86676` | `2ac866767fdbcd2847801c0abe5ae26f56737cca16a5211cc3e4d545c4590224` | **MATCH** · 盘上 **READY_FOR_MAIN_SUBMIT** |
| 旧 CMD（继承） | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_X2_CMD_DRAFT_20261025_ZH.md` | `035e5818` | `035e5818954e0f08798a860ad870312f278784b0291bcc424e602f8cf1be1c78` | **MATCH** · 不覆盖 |
| r6 FROZEN 令 | `docs/v2/audit/MAIN_LEAF25_R6_FROZEN_ORDER_20261025_ZH.md` | `53331667` | `53331667295488e334121d0fdcb4db7867417358dc8736e481eb00b0d27a844e` | **MATCH** |
| FROZEN 戳记 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | `4bb1ff2b` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **MATCH** |
| 基盘 DRAFT | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` | `e8ca2bcc` | `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` | **MATCH** |
| MEM/分块 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **MATCH** |
| wrapper v5（可选） | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** · 可选外壳 |

live `.ok`=0（`output/ai_factory/ARCH_RUN_AUTH*.ok` 空）；`output/loop` **无** `RESEARCH_QUIET.lock`；本审**未挂** QUIET；`output/ai_factory/_leaf25_full_factor/` **不存在**（未实跑）。stub `research/leaf25_cfacc_desens_build_r1.py` 与 `leaf25_full_factor_mem_probe_r{1,2,3}.py` **仍在且未覆盖**。开审授权以主令 `504b6a9d` + 包钉为准。MemAvailable≈12.0Gi（旁证，非峰证明）。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY：HILIQ×x2×end 20261009×month → 全叶 α | **PASS** | COVER/CMD/脚本：`g1g5_ashare_cfacc_desens_cs_v1`；CFACC TTM→winsor1/99→rank→normal(−CFACC)→部分残差；out=`_leaf25_full_factor/<ET_TS>/` + `alpha_parts/HI_LIQ/part_*.parquet` + `alpha_HILIQ_x2_<ET_TS>.parquet` + `run_meta.json` |
| 2 | ≠ selfcheck / Book-Smoke / X2 ACCEPT | **PASS** | 封面/CMD/脚本 notes 明文；无 eval_weights / 无 selfcheck 路径；票种=alpha 构建 |
| 3 | 禁 FULLA / `--window both` | **PASS** | argparse `choices=("HILIQ","HI_LIQ")` / `("x2",)`；FULLA 故意缺席；`run_build`/`dry_compile` 见 FULLA/both → STOP exit 2 |
| 4 | rss=1500 禁抬 + 硬 ABORT | **PASS** | `RSS_LIMIT_MB=1500`；抬帽 CLI → STOP；`check_rss`：soft≥1500MB **或** hard≥1536000kB → `SystemExit` ABORT（无自重试）；C4/stop/hard 1331200/1484800/1536000 禁抬 |
| 5 | forbid 十一票禁 RESTORED | **PASS** | 脚本 `FORBID_OK_SHA8`：`1c32ab1e`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`6054b3bf`；`--arch-ok-path` sha8∈forbid → STOP |
| 6 | 真路径闸 | **PASS** | 实跑须 `--allow-real-data` + 现盘 `--arch-ok-path`；缺任一 → STOP；dry-compile-only 零大表 |
| 7 | sampler 前缀 | **PASS_WITH_CONDITIONS** | 文档/常量钉 `/tmp/quantlab_leaf25_full_alpha_*`；脚本 `assert_tmp_quantlab` 仅强制 `/tmp/quantlab_*`（略宽）→ 签文须硬钉具体前缀 |
| 8 | 输出路径隔离 | **PASS** | CMD/COVER 建议 `output/ai_factory/_leaf25_full_factor/<ET_TS>/`；parts 子树 `alpha_parts/HI_LIQ/`；盘上目录尚不存在（未跑） |
| 9 | DIFF vs 脚本 | **PASS** | `/dev/null`→新文件；去头 `+` 正文 1110 行 ≡ `research/leaf25_full_factor_alpha_build_r1.py`（字节级） |
| 10 | PRIMARY CLI（仅文档对照；现禁跑） | **PASS** | 主令/CMD 逐字：`PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_full_factor_alpha_build_r1.py --universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/`；开跑另加 `--allow-real-data --arch-ok-path <NEW_OK>`；无同票 FALLBACK |
| 11 | 探针/stub 非本票脚本 | **PASS** | 新路径独立；stub/mem_probe_r1/r2/r3 未覆盖；COVER/CMD 明文禁当构建入口 |
| 12 | PIN_GAP 披露 | **PASS**（见 §3.3） | `_residual_covars_status`：β120/mom/logADV20/vol20=`PIN_GAP`；overall=`PARTIAL`；meta notes 明文；CFACC TTM+desens=`True` |
| 13 | HAND / H2A status 漂移 | **PASS_WITH_CONDITIONS** | HAND=`DRAFT_READY_FOR_ARCH_HOLD`；H2A=`READY_FOR_MAIN_SUBMIT`（明示勿写 SUBMITTED）；主令已交审 → 同叶27口径；签时钉**盘上**全长 |
| 14 | 分块 / chunk_plan | **PASS** | import `leaf25_full_factor_chunk_plan_r1`；PRIMARY month；禁整窗 densify；盘上 chunk_plan 模块存在 |
| 15 | 静态自检（AI 宣称；本审未复跑） | **PASS**（采信 VERIFY） | VERIFY：`--dry-compile-only` / py_compile→/tmp / pyflakes exit0 / pgrep 空；本审遵「禁代跑」未复跑 |
| 16 | 内存峰值风险 | **PASS_WITH_CONDITIONS** | 全叶×x2×month 分块仍可能贴/破 1500；静态审 ≠ 峰证明；peak_proof REQUIRED；ABORT→停+上报禁抬帽 |

## 3. 硬钉对齐

### 3.1 PRIMARY 语义

本票正确切分：**新建** 全叶/HILIQ×x2 alpha（CFACC TTM + desensitize(−CFACC) + 可用协变量截面残差），产物入 `_leaf25_full_factor/`；**不是** mem_probe 峰探，**不是** stub，**不是** selfcheck_v2，**不是** Book-Smoke，**不是** X2 ACCEPT。旧 CMD `035e5818` 仅作形源修订，不授权实跑。

### 3.2 PIN_GAP（专节钉明）

| 协变量 | 脚本 status | 含义 |
|---|---|---|
| SW L1 | PINNED_PATH | 实跑尽力；缺则残差跳过 SW |
| logmv | PINNED_PATH_PARTIAL | float_mktcap 钉；列 MATCH 时可用 |
| leaf19 α | PINNED_PATH | 缺→0（FROZEN §1） |
| **β120** | **PIN_GAP** | 无专用 reader；残差跳过；α_raw 仍产出 |
| **mom** | **PIN_GAP** | t-120→t-20 reader 未钉 |
| **logADV20** | **PIN_GAP** | reader 未钉 |
| **vol20** | **PIN_GAP** | reader 未钉 |
| overall | PARTIAL | CFACC+desens **REQUIRED 已实装**；残差仅用可用协变量 |

**钉明文案（须入签文 / `.ok`）**：本票 **勿称「全残差已齐」**；β120 / mom / logADV20 / vol20 = **PIN_GAP**（未钉 reader，残差跳过）；CFACC TTM + desensitize(−CFACC) 主路径 **已实装**；overall=`PARTIAL`。另钉 reader 后方可升级「全残差」声称。

### 3.3 残余风险（须写入签条件）

1. **全叶峰贴帽**：month 分块 + PIT/mask/残差叠层可能贴/破 1500；脚本会硬 ABORT，但须签文+AI prelaunch：峰＞1500 → **停+上报**，禁抬帽、禁静默重跑。
2. **sampler 断言略宽**：运行时仅强制 `/tmp/quantlab_*`；签文须硬钉 `/tmp/quantlab_leaf25_full_alpha_*` only。
3. **H2A/HAND status 漂移**：签 `.ok` 钉盘上 HAND `21bf0d41…` / H2A `2ac86676…` 全长（若 AI 后改 status，以签时盘证为准）。
4. **wrapper 可选**：PRIMARY 核=直接 python CLI；wrapper v5 `4240ce82` 可选外壳；签时二选一写清，二者均须新 `.ok`。
5. **≠X2 ACCEPT**：即使 alpha 落盘成功亦不自动构成 X2/ACCEPT/晋级/selfcheck 授权。
6. **PIN_GAP 叙事风险**：对外/对 Leo/回执禁写「全因子残差齐」；须带 PARTIAL + 四缺件名单。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗；错开其它研究实跑；MemAvailable 听主软地板；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856`（sha8 **`de7b3647`**）
   - CLI PRIMARY 逐字 = CMD：`--universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/` + 开跑 `--allow-real-data --arch-ok-path <NEW_OK>`
   - **无**同票 FALLBACK；失败/ABORT → 停 + 上报
   - `rss_limit_mb=1500` · `forbid_raise_rss=true`；C4/stop/hard=1331200/1484800/1536000；峰＞1500 → 停+上报（脚本硬 ABORT + 流程门）
   - `forbid_restored_ok_sha8`：**十一票** `1c32ab1e` / `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / **`3c19dd7d`** / **`6054b3bf`**
   - sampler：`/tmp/quantlab_leaf25_full_alpha_*` only
   - out_dir：`output/ai_factory/_leaf25_full_factor/<ET_TS>/`
   - mechanism_tag：`g1g5_ashare_cfacc_desens_cs_v1`
   - **PIN_GAP 披露写入 `.ok`**：β120/mom/logADV20/vol20 未齐；勿称全残差；CFACC TTM+desens 已实装；overall=PARTIAL
   - HAND/H2A/COVER/CMD/DIFF/VERIFY/本审/主令 全长钉入签文
   - live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false
   - 探针 stub/mem_probe_r* **禁**当本票脚本；禁覆盖之
3. 签时挂短窗 QUIET；AI **单次** prelaunch（healthz / wait≥15s / pgrep 空 / 脚本 sha MATCH / dry-compile 复核：`live:false` `ok_requested:false` `rss_limit_mb:1500` `universe:HILIQ` `window:x2` + forbid 含 `1c32ab1e`/`6054b3bf`）后开跑；交回执（alpha sha + run_meta sha + peak rss + PIN_GAP 披露复述）；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. **peak_proof REQUIRED**（至少：`ru_maxrss` / VmHWM 或脚本 peak_kb；若挂 sampler 则 sampler 峰）。
5. **≠X2 ACCEPT**；不解阻叶27/全量 X2；本审不构成自动开跑授权；≠selfcheck；≠Book-Smoke。
6. 禁 RESTORED 任一 VOID/CONSUMED（含 `1c32ab1e` step_m1、`6054b3bf` r3b、`3c19dd7d` selfcheck 等十一票）。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：`1c32ab1e` / `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / **`3c19dd7d`** / **`6054b3bf`**
- 禁抬 rss 软帽；禁 FULLA；禁 `--window both`；禁 Book-Smoke；禁当 X2 ACCEPT；禁当 selfcheck
- 禁把 stub / mem_probe_r1/r2/r3 当构建入口或覆盖之
- 禁开叶26 本拍交审联动；禁静默 fallback；禁换 universe/window/end
- 禁把 PIN_GAP 叙事写成「全残差已齐」

## 6. 建议签窗 / 拟 `.ok` 名（勿本回合创建）

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认后排下一空窗（例 45–60min + expires+2）；签时 QUIET；与其它 leaf 实跑错开；MemAvailable 听主软地板。
- 拟名：`ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2.ok`（或主指定等价名）；**新签**，禁复用十一票任一内容。

## 7. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**任何 CLI（含 `--dry-compile-only` / 实跑）
- **未改**主干代码 / stub / mem_probe / 钉盘其它 alpha
- **不解阻 X2**；**不当 X2 ACCEPT**；**不当 selfcheck**
- live=false · promotion=false · **不推 Leo**

## 8. 结论

**PASS_WITH_CONDITIONS** — 包钉全 MATCH（令/脚本/COVER/CMD/DIFF/HAND/VERIFY/H2A + 五件继承 + wrapper）；DIFF≡脚本；PRIMARY 语义正确；禁 FULLA；rss=1500 有硬 ABORT；forbid 十一票齐；输出隔离；PIN_GAP 专节钉明（β120/mom/logADV20/vol20 未齐；CFACC 主路径已实装）。开放项见 §4（新窗+新 `.ok`、PIN_GAP 写入签文、sampler 具体前缀、peak_proof、H2A/HAND 盘上全长、禁 RESTORED/禁 X2 ACCEPT）。**可请主排签窗**；本回合不签。

审阅文 sha8：落盘后由本机 `sha256sum` 钉（见文末或父代钉）。

live=false。
