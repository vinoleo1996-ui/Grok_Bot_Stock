# Arch 审阅：叶27 Gate A · mktcap_cache_r1（免全表重扫）独立票

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T20:15:20-04:00`（America/New_York；墙钟 `2026-10-25 20:15 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；≠X2；live=false；promotion=false |
| 触发 | hist-prune ABORT_RSS 峰 **1518MB**@`chunk6_mktcap`≫1500 → `.ok` `2be59acd` VOID（`fd159322`；回执 `d8be85cb`）；主闸 **RECOMMENDED=A**（草案 `a2307c8b`）；Leo 开 A；本包为 **代码修复** Gate A（PRIMARY CLI 仍 ndays40；**非** mode 变更） |
| 对照 | 尖峰笔记 `dd193511` · hist-prune 审 `6543726a` · VOID `fd159322` · ABORT `d8be85cb` · prev 脚本 `8cb3e86f` |
| 主令交审 | 主→Arch 交审 Gate A（脚本 `27aae6db`；COVER/CMD/DIFF/HAND/VERIFY 钉如下） |

## 0. 一句话

包钉 COVER/CMD/DIFF/VERIFY/脚本 **MATCH**；脚本 **CHANGED** `27aae6db…`（prev `8cb3e86f…`；`mktcap_cache_r1`：跨块 `DayFloatMap` + miss-only `pq.read_table(filters=trade_date in missing)` + 块末**勿** `mktcap.clear`；**保留** `hist_prune_r1`）。PRIMARY CLI **仍** HILIQ×x2×ndays40；**rss=1500 禁抬帽**；脚本 `VOID_OK_SHA8` **已钉满六票**；无同票 FALLBACK；ABORT→停+上报。对准 `MKTCAP_FULLSCAN_TRANSIENT_SPIKE` / CROSS_CHUNK 持有（草案 A）。**HAND 主令钉 `70701c1d` 与盘上 DRAFT_HAND `a2abe662` 漂移**（交审后改 status）；VERIFY 仍写 HOLD——开审以 H2A `4cac1bae`=SUBMITTED + 主令为准。估峰仍贴 1500；OUT_DIR 继承 lowmem；峰证明 REQUIRED。**本回合不签 `.ok`**；等主另排签窗。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha8（主令） | 实测全长 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_COVER_DRAFT_20261025_ZH.md` | `bf83073a` | `bf83073aab0b6e2a42db13181a7c0d4ba69c8b49e316058de9dc94aaab1cd3be` | **MATCH** |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_CMD_DRAFT_20261025_ZH.md` | `30c58132` | `30c581329708ad57e83cc8d2eb3775b686759c57287bd57554e8ce248d6fe04c` | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DIFF_DRAFT_20261025.diff` | `779197d8` | `779197d81e296102e61e5b7174e13e02e206fd523d8e0bcac4cc3be2a468b801` | **MATCH** · 相对 `8cb3e86f` 正文 ≡ 实测 diff（仅路径头不同） |
| HAND（主令钉） | `…DRAFT_HAND…` | `70701c1d` | 盘上现 **`a2abe662f741da7494c341fb70f86b18d639081ae9abf0fb0b5d8b81bcf7aef4`** | **MISMATCH / 漂移** · 见 §2#10 |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_HAND_TO_ARCH_20261025_ZH.md` | （主未钉；交审门） | `4cac1baeaaed7b16073c079127e0733edb694742bc3a1fdf1db707ed14d724c8` | **MATCH 存在** · status=**SUBMITTED_TO_ARCH** · 正文仍引 HAND=`70701c1d` |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_DRAFT_VERIFY_20261025_ZH.md` | `f01afc74` | `f01afc7435e3c5e682f8c3880fdd0b62afab15729cd1993a79b994c7b6744056` | **MATCH** · 表内仍写 HOLD / HAND=`70701c1d` / **未 SUBMITTED** |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `27aae6db` | `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5` | **MATCH** · **CHANGED** vs `8cb3e86f` |
| prev 脚本 bak | `docs/v2/audit/_bak/leaf27_chunked_members_mktcap_r1.py.8cb3e86f.bak` | `8cb3e86f` | `8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012` | **MATCH** |
| Arch 草案 A | `docs/v2/audit/ARCH_LEAF27_MKTCAP_SPIKE_MITIGATION_DRAFT_20261025_ZH.md` | `a2307c8b` | `a2307c8bf48ab8523c566298a4cd42ef3fc3a704ff2d0be910f943ecbc49fe54` | **MATCH** |
| 尖峰笔记 | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CHUNK56_SPIKE_NOTE_20261025_ZH.md` | `dd193511` | `dd193511f82b21440c8462730f26449bfc1bb8c12c4047df394872e72002eae1` | **MATCH** |
| ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `d8be85cb` | `d8be85cb96a151cb815ca94d22ca3049dfd4c95530baf5472642568792797f8f` | **MATCH** |
| VOID 权威 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_HIST_PRUNE_OK_VOID_ABORT_RSS_20261025_ZH.md` | `fd159322` | `fd1593225e50300b24e56bbeb0a461efac3fbeedf1e4a2fa8d79a6dc38ea1826` | **MATCH** |
| lowmem_v1 | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea` | `05bd81ea…`（本审截断核） | **UNCHANGED** |

live `.ok`=0；`output/loop` **无** QUIET 锁（本审**未挂**）；`pgrep` **NO_LEAF27_PROC**。开审授权以 **主令交审 + H2A `4cac1bae`=SUBMITTED** 为准（同 hist-prune HAND 仍 HOLD + 主令交审模式）。

## 2. CMD / COVER / 脚本核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | CMD：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`（venv python；`PYTHONDONTWRITEBYTECODE=1`）；与 hist-prune/ABORT 票同 CLI；**非** mode 变更 |
| 2 | 无同票 FALLBACK | **PASS** | CMD/COVER/H2A 明文 PRIMARY only；ABORT → 停+上报；禁 silent 切 mode/ndays / 禁抬帽 |
| 3 | rss / 禁抬 | **PASS** | 脚本 `RSS_LIMIT_MB=1500`；`_check_rss` soft gate `ABORT_RSS_OVER_LIMIT`；COVER/CMD 均禁抬；dry-compile `rss_limit_mb:1500` |
| 4 | mktcap_cache_r1 机制（草案 A） | **PASS** | `load_mktcap_chunk_cached(store, dates_needed)`：hit 跳过；miss → `pq.read_table(..., filters=[("trade_date","in", missing_ts)])`；进程级 `mktcap=DayFloatMap()`；块末 **不** `mktcap.clear()`（members/capadv 仍 clear+del+gc）；环内 `drop_before` 保留；`MKTCAP_CACHE_TAG=mktcap_cache_r1` |
| 5 | hist_prune_r1 保留 | **PASS** | `HIST_PRUNE_TAG=hist_prune_r1` 仍在；块边界 prune + di%40 路径未见删除；dry-compile 双 tag 同出 |
| 6 | 因子钉 / WIN | **PASS** | DIFF/COVER 宣称残差序/HI_LIQ-only/αβW **未改**；仅改装载；lowmem_v1 **UNCHANGED** `05bd81ea` |
| 7 | 禁 VOID/RESTORED 六票 | **PASS** | COVER/CMD/H2A/VERIFY/脚本 dry meta **均**明文：`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`；脚本 `VOID_OK_SHA8` 已扩为六元组（相对 hist-prune 仅旧两票有进步） |
| 8 | 采样 / out_dir | **PASS_WITH_CONDITIONS** | CMD/COVER 钉 sampler `/tmp/quantlab_leaf27_chunked_mktcap_cache_*`；建议 out_dir `…_hiliq_x2_mktcap_cache`；脚本 `OUT_DIR` **仍继承** lowmem（`leaf27_on_minus_id_idio_ivol`）——**签 `.ok` 时须显式钉**采样+建议 out_dir/`/tmp` 策略 |
| 9 | DIFF vs 脚本 | **PASS** | 在 `/tmp` 隔离：`diff -u prev now` 正文 sha ≡ claimed DIFF 去头后正文；无抬帽；无 silent fallback 到旧票；无读盘副作用进 dry 路径 |
| 10 | HAND / H2A / VERIFY 门文 | **PASS_WITH_CONDITIONS** | VERIFY `f01afc74` 仍 HOLD + 钉 HAND=`70701c1d`；H2A `4cac1bae`=SUBMITTED 但正文仍引 `70701c1d`；盘上 DRAFT_HAND 现 **`a2abe662`**（status 已改 SUBMITTED）→ **口头 sha 漂移**；开审以主令+H2A 为准；签时钉**盘上** HAND 全长 |
| 11 | dry-compile / 静态 | **PASS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500` `hist_prune_tag:hist_prune_r1` `mktcap_cache_tag:mktcap_cache_r1` + forbid 六票；AI 宣称 py_compile/pyflakes OK（本审复核 dry JSON）；`pgrep` NO_LEAF27_PROC |
| 12 | peak_proof | **PASS_WITH_CONDITIONS** | 静态/代码审 ≠ 内存键 PASS；峰证明 REQUIRED；破帽 → ABORT，禁抬帽、禁自重跑、禁 silent fallback |

## 3. 对照 hist-prune ABORT · Gate A 是否对准根因

### 3.1 实峰轨迹（ABORT 回执 `d8be85cb` / 笔记 `dd193511`）

| 阶段 | 峰 MB |
|---|---|
| chunk5 mktcap / hist_pruned+freed | **1485** / **1485**（Δ0） |
| chunk6 members/capadv | 1485 |
| **ABORT** @chunk6_mktcap | **1518**（+33）≫ 1500 |

对照 ndays40（无 prune）1514@chunk6。根因标签：`MKTCAP_FULLSCAN_TRANSIENT_SPIKE`（每块 12 RG 全表重扫）叠 `BASELINE_NO_RSS_DROP`（HWM 计量）+ `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD`；`HIST_PRUNE_R1_NO_PEAK_RELIEF` 已证实。

### 3.2 mktcap_cache_r1 相对根因的切分

- **对准（主）**：免每块 `load_mktcap_by_session` 全表 12×RG→pandas；改 miss-only + pyarrow filters；跨块保留 store → 直接打 `MKTCAP_FULLSCAN_TRANSIENT_SPIKE` / 降低重复分配推高 HWM（草案 A）。
- **保留** hist_prune_r1 + PRIMARY ndays40（代码修复，非再换 mode）。
- **不保证**：HWM 软门下基线仍可能贴帽（估峰 **1400–1490**，草案 A 明文须实峰）；`LimitPanelCache`/α 列表/计量口径未动；缓存持有过宽或 filters 仍扫底表之风险已在草案披露。
- **无抬帽 / 无 silent fallback**：DIFF/脚本未见。

### 3.3 残余风险（须写入签条件）

1. **估峰贴帽**：草案 A 估 1400–1490；若 miss 集大或缓存日过多，chunk 中后段仍可能破 1500 → **停**；另票另审；**禁抬帽**。
2. **HAND sha 漂移**：签 `.ok` 须钉盘上 DRAFT_HAND 全长（现 `a2abe662…`）或先冻结再核；勿盲抄主令口头 `70701c1d`。
3. **OUT_DIR 继承 lowmem**：产物路径与建议 `…mktcap_cache` 不一致；签时钉 sampler + 建议 out_dir（或披露双 out）。
4. **峰未证明**：静态审 ≠ 内存键 PASS；连续 ABORT 史（lowmem→quarter→month→ndays40→hist-prune）记入条件。
5. **HWM 计量残留**：本包不改 `_check_rss`/`ru_maxrss`；若实峰仍破且证据指向计量假基线，须主另批 B——**本票不含**。
6. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗 45min + expires+2；错开其他研究实跑；MemAvailable≳2.5Gi；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5`（sha8 **`27aae6db`**；**禁**再签旧字节 `8cb3e86f` / `262f9bf6`）
   - CLI PRIMARY 逐字：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
   - **无**同票 FALLBACK；ABORT → 停 + 上报（另票；禁 silent）
   - `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
   - `hist_prune_tag=hist_prune_r1` · `mktcap_cache_tag=mktcap_cache_r1`
   - `forbid_restored_ok_sha8`: **`2be59acd`**, **`a7d98ac9`**, **`8e51de63`**, **`3a6caa4f`**, **`8bcd79dc`**, **`725be3e0`**
   - sampler: `/tmp/quantlab_leaf27_chunked_mktcap_cache_*` only
   - out_dir 建议钉：`output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache`（或签文披露脚本 OUT_DIR 继承 + 日志/采样分离）
   - HAND：钉**盘上** DRAFT_HAND 全长（现 `a2abe662…`）+ H2A `4cac1bae…`；COVER `bf83073a…` / CMD `30c58132…` / DIFF `779197d8…` / VERIFY `f01afc74…` / 本审 sha
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED
3. 签时挂短窗 QUIET；AI **单次** prelaunch；**peak_proof REQUIRED**（日志须含 `mktcap_cache hit/miss/load_n` + rss 阶梯 + sampler_30s）；AI 勿擅 lift / 勿自重跑 / 勿抬帽 / 勿 silent 换 mode。
4. 再 ABORT → **停**；下一策略须主/Arch **另票另签**（禁抬帽；禁 silently fallback；B/C 须主另批）。
5. **≠X2**；不解阻叶25 全量 X2。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）
- 禁复用/RESTORED：`2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁抬 `rss_limit`；禁 `--window both`；禁 FULLA
- 禁签旧脚本字节 `8cb3e86f` / `262f9bf6` 冒充本票
- 禁把本审当作 X2 或自动开跑授权
- 禁在本票内静默切其它 chunk-mode / 其它 ndays
- 禁改 lowmem_v1 / g1g5 因子路径

## 6. 建议签窗

- **勿本回合签**（主令硬钉只审不签）。
- 建议：主确认后排 **下一空窗**（例：当日晚间或次日早段 45min；expires+2）；签时 QUIET；与其他 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MKTCAP_CACHE.ok`（或主指定等价名）；**新签**，禁复用 VOID 内容（≠ `2be59acd` / ≠ `a7d98ac9`）。

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_mktcap_cache_r1
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 27aae6dbec0c80d96799c3cf6a7baba1bf8eaea866f0dae5feb2876e201175f5
prev_script_sha_forbid_resign: 8cb3e86f0d5b199c474b38eba1950a44b18e4c0a1ded67d0f371429a55810012
cover_sha: bf83073aab0b6e2a42db13181a7c0d4ba69c8b49e316058de9dc94aaab1cd3be
cmd_draft_sha: 30c581329708ad57e83cc8d2eb3775b686759c57287bd57554e8ce248d6fe04c
diff_sha: 779197d81e296102e61e5b7174e13e02e206fd523d8e0bcac4cc3be2a468b801
hand_sha_disk: a2abe662f741da7494c341fb70f86b18d639081ae9abf0fb0b5d8b81bcf7aef4
hand_sha_oral_stale: 70701c1dfcea94e03dba7bbe3e6387c28a5213942815a234a66e6b8f22c66eab
hand_to_arch_sha: 4cac1baeaaed7b16073c079127e0733edb694742bc3a1fdf1db707ed14d724c8
verify_sha: f01afc7435e3c5e682f8c3880fdd0b62afab15729cd1993a79b994c7b6744056
arch_draft_a_sha: a2307c8bf48ab8523c566298a4cd42ef3fc3a704ff2d0be910f943ecbc49fe54
spike_note_sha: dd193511f82b21440c8462730f26449bfc1bb8c12c4047df394872e72002eae1
abort_receipt_sha: d8be85cb96a151cb815ca94d22ca3049dfd4c95530baf5472642568792797f8f
void_authority_sha: fd1593225e50300b24e56bbeb0a461efac3fbeedf1e4a2fa8d79a6dc38ea1826
prior_hist_prune_review_sha: 6543726acda009512558612687552083969d61ed3c1a1de79515fe6ba1730a86

cli_primary: --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
cli_fallback_same_ticket: NONE
hist_prune_tag: hist_prune_r1
mktcap_cache_tag: mktcap_cache_r1
next_on_abort: separate_ticket_main_arch

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: 2be59acd, a7d98ac9, 8e51de63, 3a6caa4f, 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
forbid_silent_chunk_mode_change: true
sampler_prefix: /tmp/quantlab_leaf27_chunked_mktcap_cache_
out_dir_suggested: output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_mktcap_cache
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

**PASS_WITH_CONDITIONS** — 叶27 Gate A mktcap_cache 独立票：COVER/CMD/DIFF/VERIFY/脚本钉 MATCH；机制对齐草案 A（免全表重扫 + 跨块补日；保留 hist_prune_r1；PRIMARY 仍 HILIQ×x2×ndays40）；rss=1500 禁抬；forbid 六票脚本已钉满；无 silent fallback。条件：HAND 口头 `70701c1d`↔盘上 `a2abe662` 漂移；OUT_DIR 继承；估峰贴帽须实峰；峰证明 REQUIRED。**本回合不签、不挂 QUIET、不代跑**；等主排签窗；**≠X2**。

live=false.
