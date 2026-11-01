# Arch 审阅：叶27 members/mktcap 分块装载包（P1-4 / chunked r1）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T12:28:08-04:00`（America/New_York；墙钟 `2026-10-25 12:28 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何叶27 `.ok`；**不实跑**真实行情/members/mktcap 大表 densify；不抢 QUIET；不更新 TEAM_STATE；不发其他 agent |
| live / promotion_approved | **false** / **false** |
| 对齐审计 P1-4 | `docs/v2/audit/AUDIT_20261025_1211_ET_ZH.md` sha256 `c8877760dbf1c5b2158b7dd9136bc95d9d09ea5b11cd7ba4d219de2c86673c1a`（sha8 **`c8877760`**） |
| 并行约束 | 叶25 mem_probe r2 实峰 `.ok` 已签 `cd230f9c…`（窗进行中）——本审**勿**签叶27、勿抢实跑 |

## 0. 一句话

本包以**新脚本**按季（可 month/ndays）分块装 members（mask **RG date 剪枝**）+ mktcap/capadv →块末 `del+gc`，`rss_limit=1500` 硬常量禁抬帽，禁 RESTORED `8bcd79dc`/`725be3e0`，禁同 cmd 复用 lowmem_v1 窗；静态 `py_compile` / `--dry-compile-only` / DIFF 隔离重建 / lowmem_v1 字节 **UNCHANGED** 均过。**设计对齐 P1-4，足以供父另签独立叶27 `.ok`（附硬钉）**；**本回合不签**；**峰待另窗证明**，未实跑**不算** PASS 内存键。

## 1. 输入 sha256 再核（全长 · 本机 `sha256sum`）

| 件 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` | 同左 | **MATCH** |
| DIFF | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_DIFF_20261025.diff` | `b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635` | 同左 | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_MKTCAP_COVER_20261025_ZH.md` | `e42ce686d9d21d3cc9fd3f7fb9018f7f24b0dfa06806a43f3637bb31f2bd9f16` | 同左 | **MATCH** |
| CMD草案 | `docs/v2/audit/AI_LEAF27_CHUNKED_MEMBERS_CMD_DRAFT_20261025_ZH.md` | `cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb` | 同左 | **MATCH** |
| lowmem_v1（对照） | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | 同左 | **MATCH · UNCHANGED** |
| 审计 P1-4 | `docs/v2/audit/AUDIT_20261025_1211_ET_ZH.md` | `c8877760dbf1c5b2158b7dd9136bc95d9d09ea5b11cd7ba4d219de2c86673c1a` | 同左 | **MATCH** |

## 2. 必检要点对照

| # | 要点 | 结果 | 证据摘要 |
|---|---|---|---|
| 1 | 按季（或声明粒度）分块装 members/mktcap；mask RG 剪枝；块间 del+gc；峰值策略是否可信降低 DayFloatMap/members 全窗驻留 | **PASS_WITH_CONDITIONS** | `split_calendar_chunks` 默认 `quarter`（可选 `month`/`ndays`）；`member_and_suspend_chunk` 用 parquet RG `date` statistics 剪枝后只物化本块 sessions；`load_mktcap_chunk(dates_needed)` / `load_capadv_chunk(sessions)` 仅持本块；块末 `members/suspended/mktcap/cap.clear()`+`del`+`gc`。x2+暖启动日历 **644** 日 → quarter **12** 块、单块 max **66** 日（≈旧全窗 10%）。**条件**：mktcap 助手仍**逐 RG 全扫再滤**（无 RG prune）；capadv 每块**先整表 read_parquet 再滤**（盘约 12MB）；`LimitPanelCache(keep_sessions=set(cal))` 仍挂全日历；α/`ret_hist`/`eps_hist` 跨块累积——峰**未实跑证明** |
| 2 | rss_limit=**1500MB** 禁抬帽；禁 RESTORED `8bcd79dc`/`725be3e0`；禁同 cmd | **PASS** | `RSS_LIMIT_MB=1500` 硬常量；`_check_rss` → `ABORT_RSS_OVER_LIMIT`（文案含 forbid raise）；`VOID_OK_SHA8=("8bcd79dc","725be3e0")` 写入 dry meta；CMD/COVER 明文禁同 cmd / 禁复用 VOID；新脚本路径 ≠ `…_lowmem_v1.py` |
| 3 | 与 lowmem_v1 `05bd81ea` 关系：包装器/调用方还是替换？字节是否 UNCHANGED？ | **PASS** | **新入口替换装载编排**（`run_one` 重写）；经 `importlib` **调用** lowmem_v1 的因子/IO helper（`DayFloatMap`/`load_mktcap_by_session`/`resid_*` 等）。lowmem_v1 字节 **UNCHANGED** `05bd81ea…`；封面称 SUPERSEDED_FOR_CHUNKED_LOAD = **装载路径/入口被取代**，非改其文件 |
| 4 | `py_compile`/`--dry-compile-only`→`/tmp`；DIFF 隔离重建 MATCH | **PASS** | `py_compile`→`/tmp/leaf27_chunked_members_mktcap_r1_compile.pyc` PASS；`--dry-compile-only` rc=0，`live:false` `ok_requested:false` `rss_limit_mb:1500` `forbid_restored_ok_sha8:["8bcd79dc","725be3e0"]`；DIFF（`/dev/null`→新文件）隔离重建脚本 sha **`262f9bf6…` MATCH**；隔离 venv `pyflakes` **clean** |
| 5 | 是否足以另签独立叶27 `.ok`？列签前硬钉；本回合**不签** | **是（附硬钉）· 本回合不签** | 见 §4–§5；须主排**新窗**+新 `.ok`；**≠** X2；**≠** RESTORED 旧 VOID |
| 6 | 峰待另窗证明；未实跑不算 PASS 内存键 | **确认** | 本审仅静态/dry-compile；**未** densify 全窗、**未**读 HI_LIQ mask/mktcap 大表实跑；任何「内存 PASS」须另窗实跑回执 |

## 3. 静态检查明细

| 检查 | 结果 |
|---|---|
| 五件+审计 sha MATCH | **PASS** |
| lowmem_v1 字节 UNCHANGED | **PASS** `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| `py_compile` → `/tmp/leaf27_chunked_members_mktcap_r1_compile.pyc` | **PASS** |
| `/tmp/pyflakes_venv` pyflakes | **PASS**（clean） |
| `--dry-compile-only` | **PASS** rc=0；钉 `chunked_tag=leaf27_chunked_members_mktcap_r1`、`audit_p14_sha8=c8877760`、pins 与 lowmem 一致 |
| DIFF 隔离重建 | **PASS** → `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10` |
| CLI 拒 FULLA / both / `--window both` | **PASS**（源码 `SystemExit`） |
| 本回合真跑 / densify 全窗 | **未做（禁）** |

### dry-compile 关键字段（摘录）

```json
{
  "mechanism_tag": "g1g5_ashare_on_minus_id_idio_ivol_v1",
  "chunked_tag": "leaf27_chunked_members_mktcap_r1",
  "rss_limit_mb": 1500,
  "chunk_mode_default": "quarter",
  "supersedes_lowmem_v1_sha": "05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8",
  "audit_p14_sha8": "c8877760",
  "forbid_restored_ok_sha8": ["8bcd79dc", "725be3e0"],
  "live": false,
  "ok_requested": false
}
```

## 4. 条件与瑕疵（不阻断「可另签」，但必须钉进 `.ok`/开跑前）

1. **峰未证明**：静态只能论证「驻留从 644 日一次装 → 单块 ≤66 日 + 块间释放」的**可信降峰策略**；旧 ABORT 在 `members_loaded`≈1877MB，本包对该路径有 RG 剪枝质变。**实峰 / 是否 <1500 只能另窗证明**；破帽 → ABORT，**禁抬帽**，可收紧 `--chunk-mode month` 或 `ndays`（仍禁抬帽）。
2. **mktcap 助手无 RG prune**：复用 `load_mktcap_by_session`，每块仍遍历 mktcap 全部 **12** 个 RG（约 11.7M 行文件）再按 `dates_needed` 过滤——稳态 DayFloatMap 已缩，但**瞬时扫表峰**仍是残余风险；若实跑逼近帽，下一包应对 mktcap 加 RG date prune（本包不因此 FAIL）。
3. **capadv 整表读**：`load_capadv_target_weight` 每块 `pd.read_parquet` 全文件（≈12MB 盘）再 sessions 滤——残余；通常远小于旧 members 峰，仍记条件。
4. **LimitPanelCache 全日历**：`keep_sessions=set(cal)` 懒加载面板可随日累积；开跑回执须报阶段 rss（含 `chunk*_members_loaded` / `*_mktcap` / 日环）。
5. **跨块历史**：`ret_hist`/`eps_hist`/`mkt_hist` 有意跨块保留（β60/W20 连续）——正确，但是长驻内存；已有 `_prune_hist`，回执须观察。
6. **CLI 仍含 FULLA/both choices**：运行期拒绝；`.ok`/CMD 仍须明文仅 `HILIQ`×`x2`（sealed 另签）。
7. **采样路径**：CMD 草案写 `/tmp/quantlab_leaf27_chunked_*`；脚本 `OUT_DIR` 继承 lowmem（非强制 `/tmp`）——**签 `.ok` 时须钉**输出/采样落点策略（偏好 `/tmp/quantlab_*`；若沿用 OUT_DIR 须在 `.ok` 显式批准）。
8. **并行**：叶25 r2 窗进行中——叶27 **另排窗**，禁抢 QUIET / 禁同机重峰叠跑（由主调度）。

## 5. 签前硬钉键（供父**另回合**签发独立叶27 `.ok` 时抄入；**本文件不构成 `.ok`**）

```text
assert: leaf27_chunked_members_mktcap_r1
kind: leaf27_run_ok   # 独立新签；≠ X2；≠ RESTORED
script: research/leaf27_chunked_members_mktcap_r1.py
script_sha: 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
lowmem_v1_sha_unchanged: 05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8
audit_p14_sha: c8877760dbf1c5b2158b7dd9136bc95d9d09ea5b11cd7ba4d219de2c86673c1a
cover_sha: e42ce686d9d21d3cc9fd3f7fb9018f7f24b0dfa06806a43f3637bb31f2bd9f16
cmd_draft_sha: cdf3a2295e395358fca9cbc4ccaf3bcfec6531878811597d294ff8d7b24685eb
diff_sha: b1a36d3849dfe6e74f8ed7f14bc78410f4289071f75e0124f07c998f44022635

cli: --universe HILIQ --window x2 --chunk-mode quarter
# 破帽后备（仍禁抬帽）: --chunk-mode month | --chunk-mode ndays --chunk-ndays ≤60

rss_limit_mb: 1500
forbid_raise_rss_limit: true
forbid_restored_ok_sha8: 8bcd79dc, 725be3e0
forbid_same_cmd_lowmem_v1: true
forbid_window_both: true
forbid_universe_FULLA_or_both: true
ok_requested_this_review: false
live: false
promotion_approved: false
peak_proof: REQUIRED_IN_SEPARATE_WINDOW
mem_key_pass_without_run: false
```

建议 CLI（**仅在新 `.ok` 钉入后**；现不可跑）：

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf27_chunked_members_mktcap_r1.py \
  --universe HILIQ --window x2 --chunk-mode quarter
```

## 6. 阻断项（本回合）

| 阻断 | 说明 |
|---|---|
| **本回合不签 `.ok`** | 父任务硬钉；静态 PASS_WITH_CONDITIONS ≠ 授权开跑 |
| **未实跑 ≠ 内存键 PASS** | 峰/ABORT 只能另窗证明 |
| **禁 RESTORED / 禁同 cmd** | 不得复活 `8bcd79dc` / `725be3e0`；不得再签 `…_lowmem_v1.py --universe HILIQ --window x2` |
| **禁抬帽** | 破帽只许收紧 chunk，不许 `rss_limit>1500` |
| **勿抢叶25 QUIET** | r2 实峰窗优先；叶27 另排 |

## 7. 结论句

**PASS_WITH_CONDITIONS** — P1-4 要求的 members/mktcap **分块装载**设计变更已落地且静态门闩齐全；**可以**在主排新窗后由 Arch **另签**独立叶27 `.ok`（硬钉见 §5）。**本回合不签、不实跑**；峰证明与内存键 PASS **待另窗**。

live=false。
