# Arch 审阅：叶27 Post-GateA · baseline_evac_r1（跨块基线疏散）独立票

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T22:15:26-04:00`（America/New_York；墙钟 `2026-10-25 22:15 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；不抬帽；不解阻 X2；≠X2；live=false；promotion=false |
| 触发 | Gate A mktcap_cache ABORT_RSS 峰 **1507MB**@`chunk6_mktcap`≫1500 → `.ok` `e107383f` VOID（`ff0394d0`；回执 `f0f94c9e`）；旧 Gate A = **CLOSED_INSUFFICIENT**；Arch R2 **RECOMMENDED=A**（`c8dc89b6`）；Leo 开 A（`46dc8cb3`）；本包为 **代码** Post-GateA 票（PRIMARY CLI 仍 ndays40；**非** mode 变更） |
| 对照 | 尖峰笔记 `0b483746` · Arch R2 `c8dc89b6` · 主闸 R2 `e8d7346c` · VOID `ff0394d0` · ABORT `f0f94c9e` · prev 脚本 `27aae6db` · 前审 Gate A `64057bfe` |
| 主令交审 | 主→Arch 交审 baseline_evac（`00672672`；脚本 `585ba746`；COVER/CMD/DIFF/HAND/VERIFY/H2A 钉如下） |

## 0. 一句话

包钉 COVER/CMD/DIFF/VERIFY/脚本 **MATCH**；脚本 **CHANGED** `585ba746…`（prev `27aae6db…`；`baseline_evac_r1`：块末 `evict_lim_cache_sessions` 按因子窗驱逐 + `flush_alpha_part` 中段落盘/清空/终局 concat；**保留** `mktcap_cache_r1` + `hist_prune_r1`）。PRIMARY CLI **仍** HILIQ×x2×ndays40；**rss=1500 禁抬帽**；脚本 `VOID_OK_SHA8` **已钉满七票**（含 `e107383f`）；无同票 FALLBACK；ABORT→停+上报。对准 R2 候选 A / `CHUNK6_PLUS10_OVER_3MB_SLACK` + 基线持有。**H2A 盘上 status 仍 READY_FOR_MAIN_SUBMIT**（主令 `00672672` 明示「本令后视作 SUBMITTED」）→ 口头 vs 盘上 status 漂移记 CONDITIONS；VERIFY/HAND 仍 HOLD。估峰仍贴 1500；OUT_DIR 继承 lowmem；峰证明 REQUIRED。**本回合不签 `.ok`**；等主另排签窗。旧 Gate A 禁重批。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha8（主令） | 实测全长 | 结果 |
|---|---|---|---|---|
| 主交审令 | `docs/v2/audit/MAIN_LEAF27_BASELINE_EVAC_SUBMIT_REVIEW_20261025_ZH.md` | `00672672` | `006726725c51f439b205f1704d5c72615179752aa31417e912f50eb717d8d988` | **MATCH** |
| Leo 开 A | `docs/v2/audit/MAIN_LEAF27_LEO_OPEN_A_BASELINE_EVAC_ORDER_20261025_ZH.md` | `46dc8cb3` | `46dc8cb34e1a17d0815e63ac80233eae6cf14dcd7220bd10cdb98b6a5112849f` | **MATCH** |
| Arch R2 | `docs/v2/audit/ARCH_LEAF27_MKTCAP_SPIKE_MITIGATION_DRAFT_R2_20261025_ZH.md` | `c8dc89b6` | `c8dc89b671e1d803a8295f1819653c135c41a99ef9f66b8a77ed049f82f3b3e2` | **MATCH** |
| 尖峰笔记 | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_ABORT_SPIKE_NOTE_20261025_ZH.md` | `0b483746` | `0b4837468310b57dfcb87b75cf00c21b4fe41f70c08d27176d2ab4720fd7fe14` | **MATCH** |
| 主闸 R2 | `docs/v2/audit/MAIN_LEAF27_POST_GATEA_SPIKE_GATE_R2_20261025_ZH.md` | `e8d7346c` | `e8d7346c2ca7a8b5f3346cdd422d59ecc20e311b7ad5281335029151b6644df6` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_COVER_DRAFT_20261025_ZH.md` | `0ff59ed4` | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` | **MATCH** |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_CMD_DRAFT_20261025_ZH.md` | `bf6ffe4a` | `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DIFF_DRAFT_20261025.diff` | `dc802879` | `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` | **MATCH** · 相对 `27aae6db` 正文 ≡ 实测 diff（仅路径头不同） |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_HAND_20261025_ZH.md` | `b0e01ea4` | `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` | **MATCH** · status=**DRAFT_READY_FOR_ARCH_HOLD**（未自称 SUBMITTED） |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_DRAFT_VERIFY_20261025_ZH.md` | `7ddd47e3` | `7ddd47e3c1172f9a3c2de49d1491ad66879f57fe085f872a4a61143dfaed72e0` | **MATCH** · 表内仍 HOLD / **未 SUBMITTED** |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_BASELINE_EVAC_HAND_TO_ARCH_20261025_ZH.md` | `416df9b9` | `416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676` | **MATCH 存在** · 盘上 status=**READY_FOR_MAIN_SUBMIT**（主令视作 SUBMITTED；见 §2#10） |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `585ba746` | `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec` | **MATCH** · **CHANGED** vs `27aae6db` |
| prev 脚本 bak | `docs/v2/audit/_bak/leaf27_chunked_members_mktcap_r1.py.27aae6db.bak` | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` | **MATCH** |
| ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `f0f94c9e` | `f0f94c9ea116acb697e6e086c059a3b165493e01214363343a5410c2a5b57afa` | **MATCH** |
| VOID 权威 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_OK_VOID_ABORT_RSS_20261025_ZH.md` | `ff0394d0` | `ff0394d06333c956c72c96b826ec6ea937c6f0f128e2928080b0bbd647bf64b8` | **MATCH** |
| 前审 Gate A | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MKTCAP_CACHE_REVIEW_20261025_ZH.md` | `64057bfe` | `64057bfeac7ab42d2946cfe0c51b61bde847c55da6717f06f5823b4acbbcd49e` | **MATCH**（对照模板） |
| lowmem_v1 | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | **UNCHANGED** |

live `.ok`=0（本审未见叶27 live）；`output/loop` **无** QUIET 锁（本审**未挂**）；`pgrep` **NO_LEAF27_PROC**。开审授权以 **主令交审 `00672672` + H2A `416df9b9`（主令视作 SUBMITTED）** 为准（同 Gate A HAND 仍 HOLD + 主令交审模式）。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | CMD：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`（venv python；`PYTHONDONTWRITEBYTECODE=1`）；与 Gate A/ABORT 票同 CLI；**非** mode 变更 |
| 2 | 无同票 FALLBACK | **PASS** | CMD/COVER/H2A 明文 PRIMARY only；ABORT → 停+上报；禁 silent 切 mode/ndays / 禁抬帽；B/C 本拍不开（脚本无 miss-batch / VmRSS 软门实现） |
| 3 | rss / 禁抬 | **PASS** | 脚本 `RSS_LIMIT_MB=1500`；`_check_rss` soft gate `ABORT_RSS_OVER_LIMIT`；COVER/CMD 均禁抬；dry-compile `rss_limit_mb:1500` |
| 4 | baseline_evac_r1 机制（R2 候选 A） | **PASS** | `evict_lim_cache_sessions`：块末 `factor_win=max(BETA_WIN,IVOL_WIN)` → `keep_sessions=cal[i_end-factor_win+1:]` → 更新 `_keep` 并驱逐 `_maps` 过期 session；`flush_alpha_part`：块末 `a_*` → `alpha_part_*.parquet` → clear+gc；终局 concat parts+残余 → `alpha_*.parquet`；日志钉 `lim_evict_n`/`alpha_flush_rows`/`a_buf_n`；`BASELINE_EVAC_TAG=baseline_evac_r1` |
| 5 | mktcap_cache_r1 / hist_prune_r1 保留 | **PASS** | 两 tag 仍在；块末 **不** `mktcap.clear()`；块边界 prune + di%40 路径未见删除；dry-compile 三 tag 同出 |
| 6 | 因子钉 / WIN | **PASS** | DIFF/COVER 宣称残差序/HI_LIQ-only/αβW **未改**；仅改装载/疏散；lowmem_v1 **UNCHANGED** `05bd81ea` |
| 7 | 禁 VOID/RESTORED 七票 | **PASS** | COVER/CMD/H2A/VERIFY/脚本 dry meta **均**明文：`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；脚本 `VOID_OK_SHA8` 七元组（相对 Gate A 六票 **已扩含** `e107383f`） |
| 8 | 采样 / out_dir | **PASS_WITH_CONDITIONS** | CMD/COVER 钉 sampler `/tmp/quantlab_leaf27_chunked_baseline_evac_*`；建议 out_dir `…_hiliq_x2_baseline_evac`；脚本 `OUT_DIR` **仍继承** lowmem（`leaf27_on_minus_id_idio_ivol`）——**签 `.ok` 时须显式钉**采样+建议 out_dir/`/tmp` 策略 |
| 9 | DIFF vs 脚本 | **PASS** | 在 `/tmp` 隔离：`diff -u prev now` 正文 sha ≡ claimed DIFF 去头后正文（`c8cd947f…`）；无抬帽；无 silent fallback；无 B/C；驱逐/flush 真实存在 |
| 10 | HAND / H2A / VERIFY 门文 | **PASS_WITH_CONDITIONS** | VERIFY `7ddd47e3` 仍 HOLD；HAND `b0e01ea4`=DRAFT_READY_FOR_ARCH_HOLD；H2A `416df9b9` 盘上 **READY_FOR_MAIN_SUBMIT**（明示「不要写 SUBMITTED_TO_ARCH」）；主令 `00672672` 写「本令后视作 **SUBMITTED**」→ **口头/主令 status vs 盘上 status 漂移**；开审以主令+包钉为准；签时钉**盘上** HAND/H2A 全长（若 AI 后改 status，以签时盘证为准） |
| 11 | dry-compile / 静态 | **PASS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `baseline_evac_tag:baseline_evac_r1` `mktcap_cache_tag:mktcap_cache_r1` `hist_prune_tag:hist_prune_r1` + forbid 七票含 `e107383f`；对照钉 `c8dc89b6`/`0b483746`/`46dc8cb3`/`27aae6db`；AI 宣称 py_compile/pyflakes OK；`pgrep` NO_LEAF27_PROC |
| 12 | peak_proof | **PASS_WITH_CONDITIONS** | 静态/代码审 ≠ 内存键 PASS；峰证明 REQUIRED；破帽 → ABORT，禁抬帽、禁自重跑、禁 silent fallback |
| 13 | 旧 Gate A CLOSED | **PASS** | COVER/CMD/主令/R2 明文 CLOSED_INSUFFICIENT；禁重批 / 禁再签旧字节 `27aae6db` / 禁 RESTORED `e107383f` 同语义 |

## 3. 对照 Gate A ABORT · Post-GateA A 是否对准根因

### 3.1 实峰轨迹（ABORT 回执 `f0f94c9e` / 笔记 `0b483746` / R2 `c8dc89b6`）

| 阶段 | 峰 MB |
|---|---|
| chunk5 mktcap / hist_pruned+freed | **1497** / **1497**（Δ0；cache_days=2；hit=1 miss=40） |
| chunk6 members/capadv | 1497 |
| **ABORT** @chunk6_mktcap | **1507**（+10）≫ 1500 |

对照：ndays40 1514 → hist-prune 1518 → Gate A 1507（同 stage；Gate A 仅降 ~11MB，**不够过帽**）。根因升格：`CHUNK6_PLUS10_OVER_3MB_SLACK`（余量 3MB < 装载 +10）叠 `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE` + `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD`；`GATE_A_PEAK_RELIEF_INSUFFICIENT` 已证实。

### 3.2 baseline_evac_r1 相对根因的切分

- **对准（主）**：块末驱逐 `LimitPanelCache` 早于因子窗 session + α 中段 flush/清空 → 打压跨块基线爬升与 HWM 贴帽（R2 候选 A；原草案附录 D 升格）；保留 Gate A miss-only + hist_prune + PRIMARY ndays40。
- **不保证**：HWM 软门下基线仍可能贴帽（估峰 **1400–1490**，须实峰）；`ret_hist`/`eps_hist`/`mkt_hist` 未再疏散；计量口径（`ru_maxrss`）未动；疏散不足时 chunk6 +10 仍可能破帽（R2 已披露）。
- **无抬帽 / 无 silent fallback / 无 B·C**：DIFF/脚本未见。

### 3.3 残余风险（须写入签条件）

1. **估峰贴帽**：R2/COVER 估 1400–1490；若 lim 重复读 IO 或 α 拼接峰值过大，中后段仍可能破 1500 → **停**；另票另审；**禁抬帽**。
2. **H2A/HAND status 漂移**：盘上 H2A 仍 READY_FOR_MAIN_SUBMIT；主令视作 SUBMITTED；签 `.ok` 须钉盘上 HAND/H2A **全长**（现 `b0e01ea4…` / `416df9b9…`）或先冻结再核。
3. **OUT_DIR 继承 lowmem**：产物路径与建议 `…baseline_evac` 不一致；签时钉 sampler + 建议 out_dir（或披露双 out）；α part 亦落 OUT_DIR。
4. **峰未证明**：静态审 ≠ 内存键 PASS；连续 ABORT 史（lowmem→quarter→month→ndays40→hist-prune→Gate A）记入条件。
5. **HWM 计量残留**：本包不改 `_check_rss`/`ru_maxrss`；若实峰仍破且证据指向计量假基线，须主另批 C——**本票不含**。
6. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。
7. **旧 Gate A 禁重批**：禁把本票或签窗做成「复用 `27aae6db`/`e107383f` 同语义」。

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
   - out_dir 建议钉：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac`（或签文披露脚本 OUT_DIR 继承 + 日志/采样分离；α part 同目录）
   - HAND：钉**盘上** DRAFT_HAND 全长（现 `b0e01ea4…`）+ H2A `416df9b9…`；COVER `0ff59ed4…` / CMD `bf6ffe4a…` / DIFF `dc802879…` / VERIFY `7ddd47e3…` / 本审 sha
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED；禁重批旧 Gate A
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

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_baseline_evac_r1
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED；≠ Gate A 重批
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec
prev_script_sha_forbid_resign: 27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5
cover_sha: 0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992
cmd_draft_sha: bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25
diff_sha: dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980
hand_sha_disk: b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c
hand_to_arch_sha: 416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676
hand_to_arch_status_oral_main: SUBMITTED   # 主令 00672672 视作；盘上仍 READY_FOR_MAIN_SUBMIT
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

**PASS_WITH_CONDITIONS** — 叶27 Post-GateA baseline_evac 独立票：COVER/CMD/DIFF/VERIFY/脚本钉 MATCH；机制对齐 R2 候选 A（lim_cache 因子窗驱逐 + α part flush；保留 mktcap_cache_r1/hist_prune_r1；PRIMARY 仍 HILIQ×x2×ndays40）；rss=1500 禁抬；forbid 七票脚本已钉满（含 `e107383f`）；无 silent fallback；旧 Gate A CLOSED 禁重批。条件：H2A 盘上 READY vs 主令视作 SUBMITTED 漂移；OUT_DIR 继承；估峰贴帽须实峰；峰证明 REQUIRED。**本回合不签、不挂 QUIET、不代跑、不抬帽**；等主排签窗；**≠X2**。

live=false.
