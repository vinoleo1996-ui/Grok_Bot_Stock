# Arch 审阅：叶27 Post-GateA · baseline_evac_r1（跨块基线疏散）独立票

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T22:18:20-04:00`（America/New_York；墙钟 `2026-10-25 22:18 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；不抬帽；不解阻 X2；≠X2；live=false；promotion=false |
| 触发 | Gate A mktcap_cache ABORT_RSS 峰 **1507MB**@`chunk6_mktcap`≫1500 → `.ok` `e107383f` VOID（`ff0394d0`；回执 `f0f94c9e`）；旧 Gate A = **CLOSED_INSUFFICIENT**；Arch R2 **RECOMMENDED=A**（`c8dc89b6`）；Leo 开 A（`46dc8cb3`）；主 priority 交审 `00672672` |
| 对照 | 尖峰笔记 `0b483746` · Arch R2 `c8dc89b6` · 主闸 R2 `e8d7346c` · VOID `ff0394d0` · ABORT `f0f94c9e` · prev 脚本 `27aae6db` · 前审 Gate A `64057bfe` |
| 路径钉 | 本文件按主令：`docs/v2/audit/ARCH_LEAF27_BASELINE_EVAC_REVIEW_20261025_ZH.md`（≠旧 Gate A 审） |

## 0. 一句话

包钉 COVER/CMD/DIFF/HAND/VERIFY/H2A/脚本 **全部 MATCH**；脚本 **CHANGED** `585ba746…`（prev `27aae6db…`；**禁复用**）。DIFF **真正实装**（非注释）：块末 `evict_lim_cache_sessions`（按 `max(BETA_WIN,IVOL_WIN)=60` 因子窗更新 `_keep` 并剪 `_maps`）+ `flush_alpha_part`（`a_*` → part parquet → clear → 终局 concat）；**保留** `mktcap_cache_r1`（块末**不** `mktcap.clear`）+ `hist_prune_r1`。PRIMARY CLI **仍** HILIQ×x2×ndays40；**rss=1500 硬编码禁抬**；`VOID_OK_SHA8` **七票已钉满**（含 `e107383f`）；sampler/out 建议前缀**新**；无同票 FALLBACK；ABORT→停+上报。对准 R2 候选 A / `CHUNK6_PLUS10_OVER_3MB_SLACK`。**H2A 盘上 status=READY_FOR_MAIN_SUBMIT**（主令 `00672672` 视作 SUBMITTED）→ status 漂移记 CONDITIONS；HAND 内容 sha **无**漂移（`b0e01ea4` MATCH）。OUT_DIR 仍继承 lowmem；估峰贴帽须实峰。**本回合不签 `.ok`/不挂 QUIET**；等主排签窗。旧 Gate A 禁重批。≠X2。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| 主交审令 | `docs/v2/audit/MAIN_LEAF27_BASELINE_EVAC_SUBMIT_REVIEW_20261025_ZH.md` | `00672672` | `006726725c51f439b205f1704d5c72615179752aa31417e912f50eb717d8d988` | **MATCH** |
| Leo 开 A | `docs/v2/audit/MAIN_LEAF27_LEO_OPEN_A_BASELINE_EVAC_ORDER_20261025_ZH.md` | `46dc8cb3` | `46dc8cb34e1a17d0815e63ac80233eae6cf14dcd7220bd10cdb98b6a5112849f` | **MATCH** |
| Arch R2 | `docs/v2/audit/ARCH_LEAF27_MKTCAP_SPIKE_MITIGATION_DRAFT_R2_20261025_ZH.md` | `c8dc89b6` | `c8dc89b671e1d803a8295f1819653c135c41a99ef9f66b8a77ed049f82f3b3e2` | **MATCH** |
| 尖峰笔记 | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_ABORT_SPIKE_NOTE_20261025_ZH.md` | `0b483746` | `0b4837468310b57dfcb87b75cf00c21b4fe41f70c08d27176d2ab4720fd7fe14` | **MATCH** |
| 主闸 R2 | `docs/v2/audit/MAIN_LEAF27_POST_GATEA_SPIKE_GATE_R2_20261025_ZH.md` | `e8d7346c` | `e8d7346c2ca7a8b5f3346cdd422d59ecc20e311b7ad5281335029151b6644df6` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_COVER_DRAFT_20261025_ZH.md` | `0ff59ed4` | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` | **MATCH** |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_CMD_DRAFT_20261025_ZH.md` | `bf6ffe4a` | `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DIFF_DRAFT_20261025.diff` | `dc802879` | `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` | **MATCH** · 相对 bak `27aae6db` 正文 ≡ 盘脚本 diff（body sha8 `c8cd947f`） |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_HAND_20261025_ZH.md` | `b0e01ea4` | `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` | **MATCH** · status=**DRAFT_READY_FOR_ARCH_HOLD** |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_VERIFY_20261025_ZH.md` | `7ddd47e3` | `7ddd47e3c1172f9a3c2de49d1491ad66879f57fe085f872a4a61143dfaed72e0` | **MATCH** · 仍 HOLD / 未自称 SUBMITTED |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_HAND_TO_ARCH_20261025_ZH.md` | `416df9b9` | `416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676` | **MATCH** · 盘上 status=**READY_FOR_MAIN_SUBMIT**（主令视作 SUBMITTED；见 §2#10） |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` | **MATCH** · **CHANGED** vs `27aae6db` |
| prev 脚本 bak | `docs/v2/audit/_bak/leaf27_chunked_members_mktcap_r1.py.27aae6db.bak` | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` | **MATCH** |
| ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `f0f94c9e` | `f0f94c9ea116acb697e6e086c059a3b165493e01214363343a5410c2a5b57afa` | **MATCH** |
| VOID 权威 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_OK_VOID_ABORT_RSS_20261025_ZH.md` | `ff0394d0` | `ff0394d06333c956c72c96b826ec6ea937c6f0f128e2928080b0bbd647bf64b8` | **MATCH** |
| 前审 Gate A | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_REVIEW_20261025_ZH.md` | `64057bfe` | `64057bfeac7ab42d2946cfe0c51b61bde847c55da6717f06f5823b4acbbcd49e` | **MATCH**（对照；**禁重批**） |
| lowmem_v1 | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **UNCHANGED** |

live `.ok`=0；`output/loop` **无** QUIET 锁（本审**未挂**）；`pgrep` **NO_LEAF27_PROC**；MemAvailable≈8.3Gi。开审授权以 **主令交审 `00672672` + H2A `416df9b9`（主令视作 SUBMITTED）** 为准。

### 1.1 漂移表（口头 ≠ 盘）

| 项 | 口头/主令 | 盘上 | 判定 |
|---|---|---|---|
| HAND 内容 sha | `b0e01ea4` | `b0e01ea4…` | **无漂移** MATCH |
| H2A status | 主令 `00672672`：**视作 SUBMITTED** | 文件仍写 **READY_FOR_MAIN_SUBMIT** | **status 漂移**（记 CONDITIONS；开审以主令为准） |
| VERIFY/HAND status | — | 仍 HOLD / DRAFT_READY_FOR_ARCH_HOLD | 预期；不挡开审 |
| 脚本 vs 旧 Gate A | 禁 `27aae6db` | 现 `585ba746` | **CHANGED** 正确 |
| OUT_DIR 建议 vs 脚本 | 建议 `…hiliq_x2_baseline_evac` | `OUT_DIR=_lm.OUT_DIR` → `leaf27_on_minus_id_idio_ivol` | **路径漂移**（CONDITIONS） |

## 2. CMD / COVER / DIFF / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | CMD：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`；与 Gate A/ABORT **同 CLI**；**非** mode 变更；venv + `PYTHONDONTWRITEBYTECODE=1` |
| 2 | 无同票 FALLBACK | **PASS** | CMD/COVER/H2A 明文 PRIMARY only；ABORT → 停+上报；禁 silent 切 mode/ndays；禁抬帽；B/C 本拍不开 |
| 3 | rss / 禁抬 | **PASS** | 脚本 `RSS_LIMIT_MB = 1500  # HARD — forbid raise`；`_check_rss` soft gate；dry-compile `rss_limit_mb:1500`；COVER/CMD 均禁抬 |
| 4 | lim_cache 跨块驱逐（R2 A） | **PASS** | `evict_lim_cache_sessions` 实装：写 `_keep`、删 `_maps` 过期 session、空 map 键清理；块末按 `factor_win=max(BETA_WIN,IVOL_WIN)=60` 截 keep；日志 `lim_evict_n`/`lim_maps_n` |
| 5 | α 中段落盘（R2 A） | **PASS** | `flush_alpha_part`：写 `alpha_part_*_NNNN.parquet`、clear 七列表、`gc.collect`；终局 concat parts+残缓冲 → `alpha_*.parquet`；成功后 best-effort unlink parts；日志 `alpha_flush_rows`/`a_buf_n`；meta `alpha_flush_total_rows`/`alpha_part_n` |
| 6 | 非仅注释 | **PASS** | DIFF body ≡ bak→now（sha8 `c8cd947f`）；函数/调用点/meta/dry JSON 均在盘脚本 |
| 7 | 仍免全表重扫 mktcap | **PASS** | 保留 `load_mktcap_chunk_cached` + miss-only filters；块末注释+代码 **DO NOT mktcap.clear**（仅进程末 clear）；`MKTCAP_CACHE_TAG=mktcap_cache_r1`；**非**旧 Gate A 重批 |
| 8 | hist_prune_r1 保留 | **PASS** | `HIST_PRUNE_TAG=hist_prune_r1`；块边界 prune + di%40 路径保留；dry 双+evac 三 tag 同出 |
| 9 | forbid 七票 | **PASS** | 脚本 `VOID_OK_SHA8` 含 `e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；COVER/CMD/HAND/VERIFY/H2A/dry meta **均**明文 |
| 10 | sampler / out_dir | **PASS_WITH_CONDITIONS** | CMD/COVER 钉 sampler `/tmp/quantlab_leaf27_chunked_baseline_evac_*`（**新**；≠ mktcap_cache/histprune）；建议 out_dir `…hiliq_x2_baseline_evac`；脚本 `OUT_DIR` **仍继承** lowmem → 签 `.ok` 须显式钉 sampler+建议 out_dir / 披露双 out |
| 11 | HAND / H2A / VERIFY 门文 | **PASS_WITH_CONDITIONS** | HAND/VERIFY sha **MATCH** 无内容漂移；H2A status 盘上 READY vs 主令视作 SUBMITTED → **status 漂移**；开审以主令+H2A 为准；签时钉盘上 HAND/H2A 全长 |
| 12 | dry-compile / 静态 | **PASS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `baseline_evac_tag:baseline_evac_r1` + mktcap/hist tags + forbid 七票 + 对照钉 `c8dc89b6`/`0b483746`/`46dc8cb3`/`27aae6db`；本审复核 dry JSON；`pgrep` 空 |
| 13 | 静态风险：前视 / HI_LIQ / silent | **PASS** | `--universe FULLA|both` / `--window both` 脚本拒绝；HI_LIQ-only 路径；无 silent fallback 到旧票/其它 mode；因子钉宣称 UNCHANGED；lowmem **未改**；私有 `_keep`/`_maps` 访问依赖 LimitPanelCache 现结构（已核存在）——签条件披露脆弱点 |
| 14 | peak_proof | **PASS_WITH_CONDITIONS** | 静态审 ≠ 内存键 PASS；峰证明 REQUIRED；估峰带 1400–1490 须实峰；破帽 → ABORT，禁抬帽/禁自重跑/禁 silent |

## 3. 对照 R2 / Leo 开 A 意图

### 3.1 R2 候选 A（`c8dc89b6`）要对准的根因

| 标签 | 本包动作 | 判定 |
|---|---|---|
| `CHUNK6_PLUS10_OVER_3MB_SLACK`（主） | 压 lim_cache + α 基线持有，望抬高 chunk5 末余量 | **对准**（须实峰） |
| `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE` | 新进程少堆；不改 HWM 计量 | **部分对准**（计量未改；靠疏散） |
| `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD` | lim 驱逐 + α flush；hist_prune **保留** | **对准 lim/α**；hist 仍靠 prune |
| 旧 Gate A `CLOSED_INSUFFICIENT` | 新脚本 `585ba746`；禁 `27aae6db`/`e107383f` 同语义 | **遵守**；**非重批** |
| Leo 开 A（`46dc8cb3`） | 跨块基线疏散 lim_cache+α；rss=1500；七票 | **对齐** |

### 3.2 与旧 Gate A 的切分（防误复用）

| | 旧 Gate A（VOID） | 本票 baseline_evac |
|---|---|---|
| 脚本 | `27aae6db` | **`585ba746`** |
| 机制增量 | mktcap 跨块 cache | **+** lim 驱逐 + α 中段落盘（**保留** cache） |
| CLI | HILIQ×x2×ndays40 | **同** |
| `.ok` | `e107383f` VOID | **无**（须新签） |
| sampler | `…mktcap_cache_*` | **`…baseline_evac_*`** |
| 状态 | CLOSED_INSUFFICIENT | 本审 **PASS_WITH_CONDITIONS**；等签窗 |

### 3.3 残余风险（须写入签条件）

1. **估峰贴帽**：R2/COVER 估 1400–1490；若疏散不足，chunk6 +10 仍可能破 1500 → **停**；另票；**禁抬帽**。
2. **H2A status 漂移**：签 `.ok` 钉盘上 H2A 全长 `416df9b9…` + 主令交审 `00672672`；勿要求 AI 改 status 才开审。
3. **OUT_DIR 继承 lowmem**：产物路径与建议 `…baseline_evac` 不一致；签时钉 sampler + 建议 out_dir（或披露双 out）。
4. **峰未证明**：连续 ABORT 史（lowmem→…→Gate A 1507）记入条件；静态 ≠ 内存键 PASS。
5. **HWM 计量残留**：本包不改 `ru_maxrss`；若实峰仍破且证据指向计量假基线，须主另批 C——**本票不含**。
6. **`_keep`/`_maps` 私有耦合**：依赖 lowmem LimitPanelCache 现字段；lowmem 改版须重审。
7. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗 45min + expires+2；错开其他研究实跑；MemAvailable≳2.5Gi；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`（sha8 **`585ba746`**；**禁**再签旧字节 `27aae6db` / `8cb3e86f` / `262f9bf6`）
   - CLI PRIMARY 逐字：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
   - **无**同票 FALLBACK；ABORT → 停 + 上报（另票；禁 silent）
   - `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
   - `hist_prune_tag=hist_prune_r1` · `mktcap_cache_tag=mktcap_cache_r1` · `baseline_evac_tag=baseline_evac_r1`
   - `forbid_restored_ok_sha8`: **`e107383f`**, **`2be59acd`**, **`a7d98ac9`**, **`8e51de63`**, **`3a6caa4f`**, **`8bcd79dc`**, **`725be3e0`**
   - sampler: `/tmp/quantlab_leaf27_chunked_baseline_evac_*` only
   - out_dir 建议钉：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac`（或签文披露脚本 OUT_DIR 继承 + 日志/采样分离）
   - HAND：钉盘上 DRAFT_HAND 全长 `b0e01ea4…` + H2A `416df9b9…` + COVER `0ff59ed4…` / CMD `bf6ffe4a…` / DIFF `dc802879…` / VERIFY `7ddd47e3…` / 本审 sha / 主交审 `00672672` / Leo `46dc8cb3` / R2 `c8dc89b6`
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED；**禁重批旧 Gate A**
3. 签时挂短窗 QUIET；AI **单次** prelaunch；**peak_proof REQUIRED**（日志须含 `lim_evict_n`/`alpha_flush_rows`/`a_buf_n`/`mktcap_cache_days`/hist 计数 + rss 阶梯 + sampler_30s）；AI 勿擅 lift / 勿自重跑 / 勿抬帽 / 勿 silent 换 mode。
4. 再 ABORT → **停**；下一策略须主/Arch **另票另签**（禁抬帽；禁 silently fallback；B/C 须主另批）。
5. **≠X2**；不解阻叶25 全量 X2。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）；不抬帽
- 禁复用/RESTORED：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁抬 `rss_limit`；禁 `--window both`；禁 FULLA
- 禁签旧脚本字节 `27aae6db` / `8cb3e86f` / `262f9bf6` 冒充本票；禁重批旧 Gate A CLOSED_INSUFFICIENT
- 禁把本审当作 X2 或自动开跑授权
- 禁在本票内静默切其它 chunk-mode / 其它 ndays / 实现 B 或 C
- 禁改 lowmem_v1 / g1g5 因子路径

## 6. 建议签窗

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认后排 **下一空窗**（例：当日晚间或次日早段 45min；expires+2）；签时 QUIET；与其他 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok`（或主指定等价名）；**新签**，禁复用 VOID 内容（≠ `e107383f` / ≠ `2be59acd` / ≠ 其余五票）。
- **可排签窗**：是（在 CONDITIONS 满足前提下；由主排窗，Arch 入窗再签）。

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_baseline_evac_r1
kind: leaf27_run_ok
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec
prev_script_sha_forbid_resign: 27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5
cover_sha: 0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992
cmd_draft_sha: bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25
diff_sha: dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980
hand_sha_disk: b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c
hand_to_arch_sha: 416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676
hand_to_arch_status_oral_main: SUBMITTED
verify_sha: 7ddd47e3c1172f9a3c2de49d1491ad66879f57fe085f872a4a61143dfaed72e0
main_submit_sha: 006726725c51f439b205f1704d5c72615179752aa31417e912f50eb717d8d988
leo_open_a_sha: 46dc8cb34e1a17d0815e63ac80233eae6cf14dcd7220bd10cdb98b6a5112849f
arch_r2_sha: c8dc89b671e1d803a8295f1819653c135c41a99ef9f66b8a77ed049f82f3b3e2
main_gate_r2_sha: e8d7346c2ca7a8b5f3346cdd422d59ecc20e311b7ad5281335029151b6644df6
spike_note_sha: 0b4837468310b57dfcb87b75cf00c21b4fe41f70c08d27176d2ab4720fd7fe14
abort_receipt_sha: f0f94c9ea116acb697e6e086c059a3b165493e01214363343a5410c2a5b57afa
void_authority_sha: ff0394d06333c956c72c96b826ec6ea937c6f0f128e2928080b0bbd647bf64b8
prior_gate_a_review_sha: 64057bfeac7ab42d2946cfe0c51b61bde847c55da6717f06f5823b4acbbcd49e

cli_primary: --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
cli_fallback_same_ticket: NONE
hist_prune_tag: hist_prune_r1
mktcap_cache_tag: mktcap_cache_r1
baseline_evac_tag: baseline_evac_r1
next_on_abort: separate_ticket_main_arch
old_gate_a: CLOSED_INSUFFICIENT

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: e107383f, 2be59acd, a7d98ac9, 8e51de63, 3a6caa4f, 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
forbid_silent_chunk_mode_change: true
forbid_rebatch_old_gate_a: true
sampler_prefix: /tmp/quantlab_leaf27_chunked_baseline_evac_
out_dir_suggested: output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac
ok_requested_this_review: false
live: false
promotion_approved: false
peak_proof: REQUIRED_IN_SEPARATE_WINDOW
mem_key_pass_without_run: false
neq_x2: true
```

建议 PRIMARY CLI（**仅新 `.ok` 钉入后**；现不可跑）：

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf27_chunked_members_mktcap_r1.py \
  --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
```

## 8. 结论句

**PASS_WITH_CONDITIONS** — 叶27 Post-GateA baseline_evac 独立票：COVER/CMD/DIFF/HAND/VERIFY/H2A/脚本钉 **全部 MATCH**；机制对齐 R2 候选 A（lim_cache 因子窗驱逐 + α part flush；保留 mktcap_cache_r1/hist_prune_r1；PRIMARY 仍 HILIQ×x2×ndays40）；rss=1500 禁抬；forbid 七票脚本已钉满（含 `e107383f`）；无 silent fallback；旧 Gate A CLOSED 禁重批。条件：H2A status READY vs 主令视作 SUBMITTED；OUT_DIR 继承 lowmem；估峰贴帽须实峰；峰证明 REQUIRED。**本回合不签、不挂 QUIET、不代跑、不抬帽**；**可请主排签窗**；**≠X2**。

live=false · promotion_approved=false · ok_requested=false
