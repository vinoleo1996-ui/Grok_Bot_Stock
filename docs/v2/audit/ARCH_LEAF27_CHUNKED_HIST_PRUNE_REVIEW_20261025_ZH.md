# Arch 审阅：叶27 分块装载 · hist-prune（chunk-boundary）独立票

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T16:34:23-04:00`（America/New_York；墙钟 `2026-10-25 16:34 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；≠X2；live=false |
| 触发 | ndays40 实峰 ABORT_RSS 峰 **1514MB**@`chunk6_mktcap`≫1500 → `.ok` `a7d98ac9` VOID（Arch 回执 `ad2947ef`；QUIET 已 lift）；本包为 **代码修复** hist_prune_r1（PRIMARY CLI 仍 ndays40；**非** mode 变更） |
| 对照 | ndays40 审 `18ea1567` · ndays40 VOID `ad2947ef` · ndays40 ABORT `03064d50` · month VOID `30f7289d` · month 审 `85c6fb82` |
| 主令交审 | `MAIN_LEAF27_CHUNKED_HIST_PRUNE_SUBMIT_TO_ARCH_20261025_ZH.md` sha8 `3806f922` |

## 0. 一句话

包钉全 MATCH；脚本 **CHANGED** `8cb3e86f…`（prev `262f9bf6…`；`hist_prune_r1`：块边界 `_prune_hist(ret/eps)+空 deque 清理+保留 di%40`）。PRIMARY CLI **仍** HILIQ×x2×ndays40（代码修复，非换 mode）；**rss=1500 禁抬帽**；无同票 FALLBACK；ABORT→停+上报。forbid RESTORED 明文须含 **`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`**（脚本 dry meta 仍仅旧两票——签 `.ok` 时补钉）。对准 ndays40 ABORT 根因（跨块 hist 累积；chunk5 freed 1479→chunk6 破帽 1514）；**不保证**单块 mktcap 尖峰单独消失。峰证明 REQUIRED。**本回合不签 `.ok`**；等主另排签窗。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha256 | 实测 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_COVER_DRAFT_20261025_ZH.md` | `850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019` | 同左 | **MATCH** · sha8 `85022506` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CMD_DRAFT_20261025_ZH.md` | `4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3` | 同左 | **MATCH** · sha8 `4cc9773a` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DIFF_DRAFT_20261025.diff` | `0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90` | 同左 | **MATCH** · sha8 `0c7af6ed` · CODE_CHANGE vs `262f9bf6` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_HAND_20261025_ZH.md` | `cc21f3c762bac4f370b25cac0b6c6b3d788a6cfa3008c195a909598ddb8b6152` | 同左 | **MATCH** · sha8 `cc21f3c7`（正文仍 **DRAFT_READY_FOR_ARCH_HOLD**） |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_DRAFT_VERIFY_20261025_ZH.md` | `4714256a107a724cfb85b404be9564ed042772b935062c4f5f6bafa276165931` | 同左 | **MATCH** · sha8 `4714256a`（表内仍写 HOLD / 未 SUBMITTED） |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_HAND_TO_ARCH_20261025_ZH.md` | `e8cc6058b0c081b01142de559b42c56bc9f7d8eae2d141ef336af0d3fa84c8f6` | 同左 | **MATCH** · sha8 `e8cc6058` · **SUBMITTED_TO_ARCH** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` | 同左 | **MATCH** · sha8 `8cb3e86f` **CHANGED** vs `262f9bf6` |
| 主令交审 | `docs/v2/audit/MAIN_LEAF27_CHUNKED_HIST_PRUNE_SUBMIT_TO_ARCH_20261025_ZH.md` | `3806f92228ea8577530773161dc36090ffbe153ade0db804fe1092384397d6aa` | 同左 | **MATCH** · sha8 `3806f922` |
| ndays40 审 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_NDAYS40_REVIEW_20261025_ZH.md` | `18ea156743f320beb31aa8eba02f21a7df04f4ad79f4734039993b3ffb1e5d04` | 同左 | **MATCH** · sha8 `18ea1567` |
| ndays40 VOID | `docs/v2/audit/ARCH_LEAF27_CHUNKED_NDAYS40_OK_VOID_ABORT_RSS_20261025_ZH.md` | `ad2947ef0403ff4b2db1e49d9aa0456589f371555cc484a1a83d583282870640` | 同左 | **MATCH** · sha8 `ad2947ef` |
| ndays40 ABORT | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099` | 同左 | **MATCH** · sha8 `03064d50` |
| month VOID | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_OK_VOID_ABORT_RSS_20261025_ZH.md` | `30f7289db17cf8fc4a878066162e79a92efb9344cc2773ed6935189c1988b394` | 同左 | **MATCH** · sha8 `30f7289d` |
| month 审 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_REVIEW_20261025_ZH.md` | `85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119` | 同左 | **MATCH** · sha8 `85c6fb82` |

live `.ok`=0；`output/loop` 无 QUIET 锁（本审**未挂**）。HAND 正文 HOLD + 主令交审 `3806f922` + H2A `e8cc6058`=SUBMITTED ——与 ndays40 HAND 仍 HOLD + 主令交审同模式；**开审授权以主令+H2A 为准**。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`（venv python；`PYTHONDONTWRITEBYTECODE=1`）；与 ABORT 票同 CLI |
| 2 | 无同票 FALLBACK | **PASS** | CMD/COVER/H2A 明文 PRIMARY only；ABORT → 停+上报；禁 silent 切 mode/ndays / 禁抬帽 |
| 3 | rss / 禁抬 | **PASS** | 脚本 `RSS_LIMIT_MB=1500`；`_check_rss` soft gate `ABORT_RSS_OVER_LIMIT`；COVER/CMD 均禁抬 |
| 4 | hist_prune_r1 机制 | **PASS** | 块末：`_prune_hist(ret_hist/eps_hist, alive_recent)` → 删空 deque → `alive_recent=末日 codes` → `gc` → `_check_rss(chunk{ci}_hist_pruned)`；环内 `di%40` **保留**；`HIST_PRUNE_TAG=hist_prune_r1` |
| 5 | 因子钉 / WIN | **PASS** | `BETA_WIN`/`IVOL_WIN`/`_prune_hist` 仍自 lowmem helpers；DIFF/COVER 宣称残差序/HI_LIQ-only/αβW **未改**；本审未见改因子路径 |
| 6 | 禁 VOID/RESTORED | **PASS_WITH_CONDITIONS** | COVER/CMD/H2A 明文五票：`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；**脚本** `VOID_OK_SHA8` 仍仅 `8bcd79dc`/`725be3e0`——须由 `.ok`/CMD 层补钉三新票 |
| 7 | 采样 / out_dir | **PASS_WITH_CONDITIONS** | CMD 钉 sampler `/tmp/quantlab_leaf27_chunked_histprune_*`；COVER 建议 out_dir `…_hiliq_x2_histprune`；脚本 `OUT_DIR` 仍继承 lowmem（`leaf27_on_minus_id_idio_ivol`）——**签 `.ok` 时须显式钉**采样+建议 out_dir/`/tmp` 策略 |
| 8 | DIFF vs 脚本 | **PASS** | DIFF `0c7af6ed` 准确描述相对 `262f9bf6` 的 hist_prune_r1 变更；无 silent fallback；无抬帽；无读盘副作用；dry-compile 路径不变 |
| 9 | dry-compile / 静态 | **PASS_WITH_CONDITIONS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `hist_prune_tag:hist_prune_r1`；`forbid_restored_ok_sha8` 仅旧两票；py_compile OK；pyflakes exit 0；`pgrep` NO_LEAF27_PROC |
| 10 | HAND / H2A 门文 | **PASS_WITH_CONDITIONS** | HAND `cc21f3c7` 正文仍 HOLD；VERIFY 仍写未 SUBMITTED；正式交审以 HAND_TO_ARCH `e8cc6058`=SUBMITTED_TO_ARCH + 主令 `3806f922` 为准 |
| 11 | peak_proof | **PASS_WITH_CONDITIONS** | 静态/代码审 ≠ 内存键 PASS；峰证明 REQUIRED；破帽 → ABORT，禁抬帽、禁自重跑、禁 silent fallback |

## 3. 对照 ndays40 ABORT · hist-prune 是否对准根因

### 3.1 实峰轨迹（ABORT 回执 `03064d50`）

| 阶段 | 峰 MB |
|---|---|
| begin / calendar | 103 / 330（n_chunks=17） |
| chunk0 mktcap | 913 |
| chunk1 mktcap | 1290 |
| chunk2–4 mktcap | 1332→1381→1410 |
| chunk5 mktcap / freed | **1479** / **1479** |
| chunk6 members/capadv | 1479 |
| **ABORT** @chunk6_mktcap | **1514** ≫ 1500 |

CLI 为 `--chunk-mode ndays --chunk-ndays 40`；脚本 `262f9bf6`；帽未抬；未静默换 mode。先验：quarter 1572@chunk4 / month 1502@chunk12 / ndays40 1514@chunk6 —— **跨块 hist 字典累积**驱动 freed RSS 爬升（块末 del+gc 仅释 members/mktcap/capadv）。

### 3.2 hist_prune_r1 相对根因的切分

- **对准**：块边界再剪 `ret_hist`/`eps_hist` 死码 + 空键清理 + 重置 `alive_recent`，目标压低跨块爬升基线（chunk5 freed 已 1479，头寸仅 ~21MB）。
- **保留** `di%40` 环内 prune + β60/W20 连续语义（因子钉未动）。
- **不保证**：单块 `mktcap` 装载尖峰（ABORT 正落在 `chunk6_mktcap`，+35MB）单独消失——COVER 已正确披露。
- **PRIMARY CLI 不变**：属代码修复票，非再换更细切；符合「ABORT→另交 hist-prune、禁 silent mode」链。

### 3.3 残余风险（须写入签条件）

1. **基线仍可能贴帽**：若 prune 后中后段 freed 仍≳1470，下一块 mktcap 尖峰可再破 1500 → **停**；另票另审；**禁抬帽**；禁再静默换 mode。
2. **脚本 VOID 列表未含三新票**：dry meta 仅 `8bcd79dc`/`725be3e0`；新 `.ok` **必须**明文 `forbid_restored_ok_sha8` 含五票（含 `a7d98ac9`）。
3. **OUT_DIR 继承 lowmem**：产物路径与建议 `…histprune` 不一致；签时钉 sampler=`/tmp/quantlab_leaf27_chunked_histprune_*` + 建议 out_dir（或接受双 out 披露）。
4. **峰未证明**：静态审 ≠ 内存键 PASS；连续四跳 ABORT 史（lowmem→quarter→month→ndays40）记入条件。
5. **mktcap 无 RG prune / capadv 整表读 / LimitPanelCache** 等先验残余仍在（本补丁未动）。
6. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗 45min + expires+2；错开其他研究实跑；MemAvailable≳2.5Gi；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012`（sha8 **`8cb3e86f`**；**禁**再签旧字节 `262f9bf6`）
   - CLI PRIMARY 逐字：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
   - **无**同票 FALLBACK；ABORT → 停 + 上报（另票；禁 silent）
   - `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
   - `hist_prune_tag=hist_prune_r1`
   - `forbid_restored_ok_sha8`: **`a7d98ac9`**, **`8e51de63`**, **`3a6caa4f`**, `8bcd79dc`, `725be3e0`
   - sampler: `/tmp/quantlab_leaf27_chunked_histprune_*` only
   - out_dir 建议钉：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune`（或签文披露脚本 OUT_DIR 继承 + 日志/采样分离）
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED
   - 钉 COVER/CMD/DIFF/HAND/H2A/VERIFY/本审/主令 sha
3. 签时挂短窗 QUIET；AI **单次** prelaunch；**peak_proof REQUIRED**；AI 勿擅 lift / 勿自重跑 / 勿抬帽 / 勿 silent 换 mode。
4. 再 ABORT → **停**；下一策略须主/Arch **另票另签**（禁抬帽；禁 silently fallback）。
5. **≠X2**；不解阻叶25 全量 X2。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）
- 禁复用/RESTORED：`a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁抬 `rss_limit`；禁 `--window both`；禁 FULLA
- 禁签旧脚本字节 `262f9bf6` 冒充本票
- 禁把本审当作 X2 或自动开跑授权
- 禁在本票内静默切其它 chunk-mode / 其它 ndays

## 6. 建议签窗

- **勿本回合签**（主令硬钉）。
- 建议：主确认后排 **下一空窗**（例：当日晚间或次日早段 45min；expires+2）；签时 QUIET；与其他 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_HISTPRUNE.ok`（或主指定等价名）；**新签**，禁复用 VOID 内容（≠ `a7d98ac9`）。

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_hist_prune_r1
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012
prev_script_sha_forbid_resign: 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
cover_sha: 850225060aeb07d4350d38ca569fe241956359605ee492520235105aca6b8019
cmd_draft_sha: 4cc9773a4ebde6548308e717e694df520a4b72877a02a8c40f20df0220f7b3a3
diff_sha: 0c7af6ed66b9a9152a95ee3a0d008264ee3bb3b6801e496ff4ab587e27686e90
hand_sha: cc21f3c762bac4f370b25cac0b6c6b3d788a6cfa3008c195a909598ddb8b6152
hand_to_arch_sha: e8cc6058b0c081b01142de559b42c56bc9f7d8eae2d141ef336af0d3fa84c8f6
verify_sha: 4714256a107a724cfb85b404be9564ed042772b935062c4f5f6bafa276165931
main_submit_sha: 3806f92228ea8577530773161dc36090ffbe153ade0db804fe1092384397d6aa
abort_receipt_sha: 03064d50bc1997e40cff3a10c55d10e91930473472a183d7ac0c0782b514b099
void_ok_sha8: a7d98ac9
void_receipt_sha: ad2947ef0403ff4b2db1e49d9aa0456589f371555cc484a1a83d583282870640
prior_ndays40_review_sha: 18ea156743f320beb31aa8eba02f21a7df04f4ad79f4734039993b3ffb1e5d04
prior_month_void_sha: 30f7289db17cf8fc4a878066162e79a92efb9344cc2773ed6935189c1988b394
prior_month_review_sha: 85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119

cli_primary: --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
cli_fallback_same_ticket: NONE
hist_prune_tag: hist_prune_r1
next_on_abort: separate_ticket_main_arch

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: a7d98ac9, 8e51de63, 3a6caa4f, 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
forbid_silent_chunk_mode_change: true
sampler_prefix: /tmp/quantlab_leaf27_chunked_histprune_
out_dir_suggested: output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_histprune
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

**PASS_WITH_CONDITIONS** — 叶27 hist-prune 独立票包钉全 MATCH；脚本 CHANGED `8cb3e86f`（hist_prune_r1）合理对准 ndays40 ABORT 的跨块 hist 累积根因；PRIMARY 仍 HILIQ×x2×ndays40；口径（1500/禁抬/禁 silent/禁五票 RESTORED）正确；**可另回合**由主排窗后签独立 `.ok`。**本回合不签、不挂 QUIET、不代跑**；脚本 forbid 列表须由 `.ok` 补钉 `a7d98ac9`/`8e51de63`/`3a6caa4f`；单块 mktcap 尖峰与峰证明仍为条件；**≠X2**。

live=false.
