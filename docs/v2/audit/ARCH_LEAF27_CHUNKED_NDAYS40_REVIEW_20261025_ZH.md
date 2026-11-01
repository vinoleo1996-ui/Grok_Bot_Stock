# Arch 审阅：叶27 分块装载 · ndays=40 DRAFT（CLI-only · 独立票）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T16:03:29-04:00`（America/New_York；墙钟 `2026-10-25 16:03 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；≠X2；live=false |
| 触发 | month 实峰 ABORT_RSS 峰 **1502MB**@`chunk12_mktcap`≫1500 → `.ok` `8e51de63` VOID（Arch 回执 `30f7289d`；QUIET 已 lift）；本包 PRIMARY=`ndays=40`（**无**同票 FALLBACK） |
| 对照 | month 审 `85c6fb82` · quarter 审 `282d6ca1` · month ABORT `03c58db5` · VOID `30f7289d` |
| 主令交审 | `MAIN_LEAF27_CHUNKED_NDAYS40_SUBMIT_TO_ARCH_20261025_ZH.md` sha8 `b1cbafa1` |

## 0. 一句话

包钉全 MATCH；脚本字节 **UNCHANGED** `262f9bf6…`（已支持 `ndays`）；与 month 差异仅为 CLI `--chunk-mode ndays --chunk-ndays 40`（PRIMARY only；禁 silent）。**rss=1500 禁抬帽**；forbid RESTORED 明文含 **`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`**。month 再证 hist 跨块累积主导破帽（849→1502）——ndays=40 可再压单块尖峰，**未必单独修好 hist**；若再 ABORT → 另交 **hist-prune**（禁抬帽）。**本回合不签 `.ok`**；等主另排签窗。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha256 | 实测 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_COVER_DRAFT_20261025_ZH.md` | `ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d` | 同左 | **MATCH** · sha8 `ec5f67e9` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_CMD_DRAFT_20261025_ZH.md` | `af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b` | 同左 | **MATCH** · sha8 `af6f0d49` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DIFF_DRAFT_20261025.diff` | `5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66` | 同左 | **MATCH** · sha8 `5449dde5` · NO_CODE_CHANGE |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_HAND_20261025_ZH.md` | `5547940bec333aa5515af5defccdde241c8812a9fb87f5bcc495427586424a81` | 同左 | **MATCH** · sha8 `5547940b`（正文仍 HOLD_UNTIL_MAIN_SUBMIT） |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_DRAFT_VERIFY_20261025_ZH.md` | `305f7a93177d8d7a67204d4e58499374d5155cf79dc262f1515333a1545b4d5e` | 同左 | **MATCH** · sha8 `305f7a93`（表内 H2A 状态偏旧：仍写 DRAFT_READY） |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_NDAYS40_HAND_TO_ARCH_20261025_ZH.md` | `2986bd01bfe23bfcbbf169ea93e07647c64472b3cdaaddd25048275042ed7ddb` | 同左 | **MATCH** · sha8 `2986bd01` · **SUBMITTED_TO_ARCH** （≠TEAM 口头 `b7c33ca8` DRAFT_READY——以盘证 SUBMITTED `2986bd01` 为准） |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | 同左 | **MATCH** · sha8 `262f9bf6` **UNCHANGED** |
| 主令交审 | `docs/v2/audit/MAIN_LEAF27_CHUNKED_NDAYS40_SUBMIT_TO_ARCH_20261025_ZH.md` | `b1cbafa15d6a5e78c346b62d81d95384a3536e4a71bc25e73f9e5ed1d96d1e77` | 同左 | **MATCH** · sha8 `b1cbafa1` |
| month 审 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_REVIEW_20261025_ZH.md` | `85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119` | 同左 | **MATCH** · sha8 `85c6fb82` |
| quarter 审 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MEMBERS_MKTCAP_REVIEW_20261025_ZH.md` | `282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb` | 同左 | **MATCH** · sha8 `282d6ca1` |
| month VOID 回执 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MONTH_OK_VOID_ABORT_RSS_20261025_ZH.md` | `30f7289db17cf8fc4a878066162e79a92efb9344cc2773ed6935189c1988b394` | 同左 | **MATCH** · sha8 `30f7289d` |
| month ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177` | 同左 | **MATCH** · sha8 `03c58db5` |

live `.ok`=0；`output/loop` 无 QUIET 锁（本审**未挂**）。TEAM 口头 H2A `b7c33ca8` **作废**——以盘证 `2986bd01` 为准。

## 2. CMD / COVER 可执行块核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`（venv python；`PYTHONDONTWRITEBYTECODE=1`） |
| 2 | 无同票 FALLBACK | **PASS** | CMD/COVER 明文 PRIMARY only；ABORT → 另交 hist-prune；禁 silent 切 mode/ndays |
| 3 | rss / 禁抬 | **PASS** | `rss_limit=1500`；COVER/CMD/脚本硬常量均禁抬；`abort_on_rss_over` 语义沿用脚本硬帽 |
| 4 | 禁 VOID/RESTORED | **PASS** | 明文禁 **`8e51de63`** / `3a6caa4f` / `8bcd79dc` / `725be3e0`；禁 `lowmem_v1` 同 cmd；禁 `--window both`/FULLA |
| 5 | 采样 | **PASS_WITH_CONDITIONS** | CMD 钉 `/tmp/quantlab_leaf27_chunked_ndays40_*`；脚本 OUT_DIR 仍继承 lowmem——**签 `.ok` 时须显式钉**采样/`/tmp` 策略 |
| 6 | 与 month 差异 / DIFF | **PASS** | DIFF 空代码 hunk（NO_CODE_CHANGE）；仅 CLI `month→ndays 40`；因子钉宣称零改；脚本字节 UNCHANGED |
| 7 | lowmem_v1 | **PASS** | dry meta `supersedes_lowmem_v1_sha`；COVER/CMD 禁同 cmd 复用；helpers-only 引用可接受 |
| 8 | dry-compile | **PASS_WITH_CONDITIONS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500`；脚本 `forbid_restored_ok_sha8` 仅 `8bcd79dc`/`725be3e0`（**不含** `8e51de63`/`3a6caa4f`——须由 `.ok`/CMD 层补钉） |
| 9 | HAND / H2A 门文 | **PASS_WITH_CONDITIONS** | HAND `5547940b` 正文仍 HOLD；VERIFY 仍写 H2A DRAFT_READY；正式交审以 HAND_TO_ARCH `2986bd01`=SUBMITTED_TO_ARCH + 主令 `b1cbafa1` 为准——签发前以 H2A+本审为准即可 |
| 10 | peak_proof | **PASS_WITH_CONDITIONS** | 静态/CLI-only ≠ 内存键 PASS；峰证明 REQUIRED；破帽 → ABORT，禁抬帽、禁自重跑、禁 silent fallback |

## 3. 对照 month ABORT · ndays=40 是否够切

### 3.1 实峰轨迹（ABORT 回执 `03c58db5`）

| 阶段 | 峰 MB |
|---|---|
| chunk0 mktcap | 849 |
| … | … |
| chunk9 | 1419 |
| chunk10 | 1460 |
| chunk11 | 1467 |
| chunk12 capadv | 1467 |
| **ABORT** @chunk12_mktcap | **1502** ≫ 1500 |

CLI 为 `--chunk-mode month`；脚本 `262f9bf6`；帽未抬；未静默 ndays。

### 3.2 ndays=40 相对 month 的切分

- month：约 20–23 交易日/块；ABORT 于 chunk12_mktcap（中后段爬升）。
- ndays=40：单块 ≈40 会话——相对 month **略粗**于「更短块压尖峰」直觉，但为 Arch month 审 `85c6fb82` 已批准的 FALLBACK 下一刀，且本包升为 **独立 PRIMARY**（非 silent）。
- 真正驱动：跨块 `ret_hist`/`eps_hist`/`mkt_hist` 累积（β60/W20 连续）。ndays=40 **不改**该语义（脚本 UNCHANGED）——**未必单独修好 hist 增长**。
- COVER 已正确披露：若再破帽 → 另交 **hist-prune**（本包不发明改码、不抬帽）。

### 3.3 残余风险（须写入签条件）

1. **hist 累积主导破帽**：若 ndays40 中后段仍逼近/越过 1500 → **停**；另交 hist-prune 包；**禁抬帽**；**禁**再静默换更粗/更细切。
2. **mktcap 无 RG prune / capadv 整表读 / LimitPanelCache 全日历**：先验审残余仍在（脚本未改）。
3. **峰未证明**：静态审 ≠ 内存键 PASS。
4. **脚本 VOID 列表未含 `8e51de63`/`3a6caa4f`**：dry meta 仅钉旧两票；新 `.ok` **必须**明文 `forbid_restored_ok_sha8` 含四票。
5. **连续三跳 ABORT 历史**（lowmem→quarter→month）：累积残余记入 PASS_WITH_CONDITIONS；本票仍可另窗试跑，但不得当 X2/解阻。
6. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗 45min + expires+2；错开其他研究实跑；MemAvailable≳2.5Gi；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10`
   - CLI PRIMARY 逐字：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
   - **无**同票 FALLBACK；ABORT → 停 + 另交 hist-prune
   - `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
   - `forbid_restored_ok_sha8`: **`8e51de63`**, **`3a6caa4f`**, `8bcd79dc`, `725be3e0`
   - sampler: `/tmp/quantlab_leaf27_chunked_ndays40_*` only
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED
   - 钉 COVER/CMD/DIFF/本审 sha
3. 签时挂短窗 QUIET；AI **单次** prelaunch；峰证明 REQUIRED；AI 勿擅 lift / 勿自重跑 / 勿抬帽 / 勿 silent 换 mode。
4. ndays40 ABORT → **停**；另交 hist-prune 票另审另签（勿 silently fallback）。
5. **≠X2**；不解阻叶25 全量 X2。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑；不排签窗（等主）
- 禁复用/RESTORED：`8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁抬 `rss_limit`；禁 `--window both`；禁 FULLA
- 禁改脚本字节后仍宣称 UNCHANGED `262f9bf6`
- 禁把本审当作 X2 或自动开跑授权
- 禁在本票内静默切其它 chunk-mode / 其它 ndays

## 6. 建议签窗

- **勿本回合签**（主令硬钉）。
- 建议：主确认后排 **下一空窗**（例：当日晚间或次日早段 45min；expires+2）；签时 QUIET；与其他 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok`（或主指定等价名）；**新签**，禁复用 VOID 内容。

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_ndays40
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
cover_sha: ec5f67e9ba402449421339bd6b8fc47639aa5b19a818732862e2b6a47bb6f23d
cmd_draft_sha: af6f0d49dc89ae963e0e218b620184ecbf069d9e693b4aeeced62a33e82d8c2b
diff_sha: 5449dde5fed4fe73d6669572cdb8381c1764b27381c61a07ca5755d6794a6c66
hand_sha: 5547940bec333aa5515af5defccdde241c8812a9fb87f5bcc495427586424a81
hand_to_arch_sha: 2986bd01bfe23bfcbbf169ea93e07647c64472b3cdaaddd25048275042ed7ddb
verify_sha: 305f7a93177d8d7a67204d4e58499374d5155cf79dc262f1515333a1545b4d5e
main_submit_sha: b1cbafa15d6a5e78c346b62d81d95384a3536e4a71bc25e73f9e5ed1d96d1e77
abort_receipt_sha: 03c58db58e7f3e0e2ff1aa22e8e519a11bf3506d1526bec361f0b5c832039177
void_ok_sha8: 8e51de63
void_receipt_sha: 30f7289db17cf8fc4a878066162e79a92efb9344cc2773ed6935189c1988b394
prior_month_review_sha: 85c6fb82f8fcc841c63bab77c237f9b1e29f16bb718f43f55a04734ac0cb1119
prior_quarter_review_sha: 282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb

cli_primary: --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
cli_fallback_same_ticket: NONE
next_on_abort: separate_hist_prune_ticket

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: 8e51de63, 3a6caa4f, 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
forbid_silent_chunk_mode_change: true
sampler_prefix: /tmp/quantlab_leaf27_chunked_ndays40_
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

**PASS_WITH_CONDITIONS** — 叶27 ndays=40 DRAFT 包钉全 MATCH、CLI-only PRIMARY only 对准 month ABORT 后的批准下一刀，口径（1500/禁抬/禁 VOID 四票/禁 silent）正确；**可另回合**由主排窗后签独立 `.ok`。**本回合不签、不挂 QUIET、不代跑**；hist 累积与峰证明仍为条件；脚本 forbid 列表须由 `.ok` 补钉 `8e51de63`/`3a6caa4f`；**≠X2**。

live=false.
