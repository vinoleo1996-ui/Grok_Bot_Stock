# Arch 审阅：叶27 分块装载 · month DRAFT（CLI-only）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T15:24:28-04:00`（America/New_York；墙钟 `2026-10-25 15:24 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不挂 QUIET**；**不代跑**；≠X2；live=false |
| 触发 | quarter 实峰 ABORT_RSS 峰 **1572MB**@`chunk4_mktcap`≫1500 → `.ok` `3a6caa4f` VOID；本包 PRIMARY=`month` / FALLBACK=`ndays=40` |
| 对照 | 先验审 `282d6ca1`（quarter）· VOID 回执 `c1c6a95c` · ABORT 回执 `4e37aacc` |

## 0. 一句话

包钉全 MATCH；脚本字节 **UNCHANGED** `262f9bf6…`（已支持 `month|ndays`）；与 quarter 差异仅为 CLI `--chunk-mode month`（备 `ndays 40`）。**rss=1500 禁抬帽**、禁 RESTORED/VOID 旧票口径正确。month 可压低单块 members/mktcap 尖峰，但 **hist 跨块累积**（quarter 爬升 897→1572）仍是主残余风险——**峰只能另窗证明**。**本回合不签 `.ok`**；可另排主令签窗后另签独立票。

## 1. 钉表再核（本机 sha256 · 全长）

| 件 | 路径 | 期望 sha256 | 实测 | 结果 |
|---|---|---|---|---|
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_COVER_DRAFT_20261025_ZH.md` | `c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b` | 同左 | **MATCH** · sha8 `c8b33519` |
| CMD | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_CMD_DRAFT_20261025_ZH.md` | `5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077` | 同左 | **MATCH** · sha8 `5323d614` |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DIFF_DRAFT_20261025.diff` | `5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1` | 同左 | **MATCH** · sha8 `5fa2a29e` |
| HAND | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DRAFT_HAND_20261025_ZH.md` | `cf2586207e5fffb0521ac0b5b5a9cb2ebc4f678dd30c9f1c3fe02f826ceb4057` | 同左 | **MATCH** · sha8 `cf258620`（≠旧 `9428fcbf`） |
| VERIFY | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_DRAFT_VERIFY_20261025_ZH.md` | `f649ba15448dd1168b967e27a84e4073c9d71dd250212af603835037762e7d0a` | 同左 | **MATCH** · sha8 `f649ba15` |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_CHUNKED_MONTH_HAND_TO_ARCH_20261025_ZH.md` | `eb3fb164869593e0f05bdb1397f86a1ebd6bf80a83d1ee5f56c31a0a5b43c8ab` | 同左 | **MATCH** · sha8 `eb3fb164` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | 同左 | **MATCH** · sha8 `262f9bf6` **UNCHANGED** |
| 先验审 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_MEMBERS_MKTCAP_REVIEW_20261025_ZH.md` | `282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb` | 同左 | **MATCH** · sha8 `282d6ca1` |
| VOID 回执 | `docs/v2/audit/ARCH_LEAF27_CHUNKED_OK_VOID_ABORT_RSS_20261025_ZH.md` | `c1c6a95ce1c4c8565712f6f983712689934c66a7272fe7e4ff5737134415ce4e` | 同左 | **MATCH** · sha8 `c1c6a95c` |
| ABORT 回执 | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_RUN_RECEIPT_20261025_ZH.md` | `4e37aacc17998682a8713fe4e4648d40f4e8ac3fcbb3741182838ded849b879b` | 同左 | **MATCH** · sha8 `4e37aacc` |

live `.ok`=0；`output/loop` 无 QUIET 锁（本审**未挂**）。

## 2. CMD / COVER 可执行块核验

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | PRIMARY CLI | **PASS** | `--universe HILIQ --window x2 --chunk-mode month`（venv python；`PYTHONDONTWRITEBYTECODE=1`） |
| 2 | FALLBACK CLI | **PASS** | `--chunk-mode ndays --chunk-ndays 40`；**仅** month 再 ABORT 后另签 |
| 3 | rss / 禁抬 | **PASS** | `rss_limit=1500`；COVER/CMD/脚本硬常量均禁抬 |
| 4 | 禁 VOID/RESTORED | **PASS** | 明文禁 `3a6caa4f` / `8bcd79dc` / `725be3e0`；禁 `lowmem_v1` 同 cmd；禁 `--window both`/FULLA |
| 5 | 采样 | **PASS_WITH_CONDITIONS** | CMD 钉 `/tmp/quantlab_leaf27_chunked_month_*`；脚本 OUT_DIR 仍继承 lowmem——**签 `.ok` 时须显式钉**采样/`/tmp` 策略 |
| 6 | 与 quarter 差异 | **PASS** | DIFF 空代码 hunk；仅 CLI `quarter→month`；因子钉宣称零改 |
| 7 | 探针语义 | **PASS** | 非叶25 probe；未改 mem_probe / C4/C5 语义 |
| 8 | dry-compile | **PASS** | `--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500`；`forbid_restored_ok_sha8` 含 `8bcd79dc`/`725be3e0`（**不含** `3a6caa4f`——须由 `.ok`/CMD 层补钉） |
| 9 | HAND 门文 | **PASS_WITH_CONDITIONS** | HAND `cf258620` 正文仍写 HOLD_UNTIL_MAIN_SUBMIT；正式交审以 HAND_TO_ARCH `eb3fb164`=SUBMITTED_TO_ARCH 为准（三件钉未改）——签发前以 HAND_TO_ARCH+本审为准即可 |

## 3. 对照 quarter ABORT / 先验审 · month 是否够切

### 3.1 实峰轨迹（ABORT 回执 `4e37aacc`）

| 阶段 | 峰 MB |
|---|---|
| chunk0 mktcap | 897 |
| chunk1 | 1288 |
| chunk2 | 1397 |
| chunk3 | 1439 |
| chunk4 capadv | 1475 |
| **ABORT** @chunk4_mktcap | **1572** ≫ 1500 |

CLI 为 `--chunk-mode quarter`；脚本 `262f9bf6`；帽未抬。

### 3.2 month 相对 quarter 的切分

- 先验审：x2+暖启动约 **644** 日 → quarter **12** 块、单块 max≈**66** 日。
- month：块长约 **1/3** quarter（≈20–23 交易日/块，量级），可显著压低**单块** members/mktcap/capadv 装载尖峰——**针对 chunk4_mktcap 尖峰路径合理收紧**。
- COVER 已披露：块末 `del+gc` 后 RSS 仍爬升 → 主因含 **跨块 `ret_hist`/`eps_hist`/`mkt_hist` 累积**（β60/W20 连续）。month **不改**该语义（脚本 UNCHANGED）——**未必单独修好 hist 增长**。

### 3.3 残余风险（须写入签条件）

1. **hist 累积主导破帽**：若 month 中后段仍逼近/越过 1500，走 FALLBACK `ndays=40`；若仍破 → **另包**（hist prune / 装载路径），**禁抬帽**。
2. **mktcap 无 RG prune / capadv 整表读 / LimitPanelCache 全日历**：先验审 §4 残余仍在（脚本未改）。
3. **峰未证明**：静态/CLI-only ≠ 内存键 PASS；破帽 → ABORT，禁抬帽、禁自重跑。
4. **脚本 VOID 列表未含 `3a6caa4f`**：dry meta 仅钉旧两票；新 `.ok` **必须**明文 `forbid_restored_ok_sha8` 含 `3a6caa4f`（及 `8bcd79dc`/`725be3e0`）。
5. **≠X2 / ≠自动解阻**：本审不构成叶25/全量 X2 授权。

## 4. 条件（另回合签发前必须满足）

1. **主排新签窗**（建议短窗 45min + expires+2；错开其他研究实跑；MemAvailable≳2.5Gi；无叠加 QUIET 冲突）——**本回合不签**。
2. 新 `.ok` 硬钉：
   - script sha `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10`
   - CLI PRIMARY 逐字：`--universe HILIQ --window x2 --chunk-mode month`
   - FALLBACK 仅另签：`--chunk-mode ndays --chunk-ndays 40`
   - `rss_limit_mb=1500` · `forbid_raise_rss_limit=true`
   - `forbid_restored_ok_sha8`: **`3a6caa4f`**, `8bcd79dc`, `725be3e0`
   - sampler: `/tmp/quantlab_leaf27_chunked_month_*` only
   - 禁 `both`/FULLA；禁 `lowmem_v1` 同 cmd；禁 RESTORED 任意 VOID/CONSUMED
   - 钉 COVER/CMD/DIFF/本审 sha
3. 签时挂短窗 QUIET；AI **单次** prelaunch；峰证明 REQUIRED；AI 勿擅 lift / 勿自重跑 / 勿抬帽。
4. month ABORT → **停**；另交 ndays40 票另审另签（勿 silently fallback）。
5. **≠X2**；不解阻叶25 全量 X2。

## 5. 禁项（本回合 + 签后）

- **本回合不签** `.ok`；不挂 QUIET；不代跑
- 禁复用/RESTORED：`3a6caa4f` / `8bcd79dc` / `725be3e0`
- 禁抬 `rss_limit`；禁 `--window both`；禁 FULLA
- 禁改脚本字节后仍宣称 UNCHANGED `262f9bf6`
- 禁把本审当作 X2 或自动开跑授权

## 6. 建议签窗

- **勿本回合签**（主令硬钉）。
- 建议：主确认后排 **下一空窗**（例：当日晚间或次日早段 45min；expires+2）；签时 QUIET；与其他 leaf 实跑错开。
- 拟名：`ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_MONTH.ok`（或主指定等价名）；**新签**，禁复用 VOID 内容。

## 7. 签前硬钉键（抄入未来 `.ok`；本文件≠`.ok`）

```text
assert: leaf27_chunked_members_mktcap_r1_month
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
cover_sha: c8b3351931a593d7e7d5f747e318db29278407d19d07949b1f866f25bae8819b
cmd_draft_sha: 5323d6140b3a0fa4659febbf694561fc9bd048cda9c668cdc914429f9ca11077
diff_sha: 5fa2a29e2bb6b8b49a38ec7350e4ada33f61b49906fbd5e4e31f9dbb12988ac1
hand_sha: cf2586207e5fffb0521ac0b5b5a9cb2ebc4f678dd30c9f1c3fe02f826ceb4057
hand_to_arch_sha: eb3fb164869593e0f05bdb1397f86a1ebd6bf80a83d1ee5f56c31a0a5b43c8ab
verify_sha: f649ba15448dd1168b967e27a84e4073c9d71dd250212af603835037762e7d0a
abort_receipt_sha: 4e37aacc17998682a8713fe4e4648d40f4e8ac3fcbb3741182838ded849b879b
void_ok_sha8: 3a6caa4f
prior_quarter_review_sha: 282d6ca127f44050b8c1266d027417593365dc12dd6a13073a6f432124e690bb

cli_primary: --universe HILIQ --window x2 --chunk-mode month
cli_fallback_separate_ok: --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: 3a6caa4f, 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
sampler_prefix: /tmp/quantlab_leaf27_chunked_month_
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
  --universe HILIQ --window x2 --chunk-mode month
```

## 8. 结论句

**PASS_WITH_CONDITIONS** — 叶27 month DRAFT 包钉全 MATCH、CLI-only 收紧对准 quarter ABORT 的 chunk4 尖峰路径，口径（1500/禁抬/禁 VOID）正确；**可另回合**由主排窗后签独立 `.ok`。**本回合不签、不挂 QUIET、不代跑**；hist 累积与峰证明仍为条件；**≠X2**。

live=false。
