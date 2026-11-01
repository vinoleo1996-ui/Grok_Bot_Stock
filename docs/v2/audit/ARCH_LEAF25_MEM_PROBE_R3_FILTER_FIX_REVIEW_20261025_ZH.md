# Arch 审阅：叶25 mem_probe r3 滤子类型修补包

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-25T12:44:17-04:00`（America/New_York；墙钟 `2026-10-25 12:44 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **执行器不签** `.ok`；**不实跑**真实行情/财务大表；不解阻 X2 / NEED_MEM_PROBE |
| 主补充令（~12:40 ET） | r3 审 **PASS / PASS_WITH_CONDITIONS** 后，**Arch 父本回合另签**独立实峰 probe `.ok`（≠X2；禁复用 VOID `cd230f9c…`） |
| live / promotion_approved | **false** / **false** |
| 对齐 Arch VOID+r3 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_FAIL_VOID_R3_RULE_20261025_ZH.md` sha **`6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f`** |
| 对齐 r2 审阅模板 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_REAL_PATH_REVIEW_20261025_ZH.md` sha **`1b706f9b40054b69e4e25968f9a3d20ec530965a4dfaf3a61be7584d3296b0c7`** |
| 对齐采纳 (A) | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` sha **`14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e`** |

## 0. 一句话

r3 **最小滤子修**已对齐裁定 `6ef34f99…`：`end_date` 对 `timestamp[us]` 改用 `pd.Timestamp` RHS（禁再喂 YYYYMMDD string）；`_norm_pit`/asof 日归一 naive 两侧一致；真实峰路径（PIT→截面α→float32 落盘→gc）、C4 三帽、`/tmp`、HI_LIQ、无.ok→STOP、双禁 `.ok` 均仍钉。静态/合成烟测 PASS。**足以供 Arch 父本回合另签独立实峰 probe `.ok`**（主已授权；≠X2；禁复用 `cd230f9c`/`1c32ab1e`）。**本执行器回合不签**；短窗须**错开叶27 14:00–14:45 ET**；实峰跑 PASS 前 **不解阻 X2**。

## 1. 输入 sha256 再核（全长 · 本机 `sha256sum`）

| 件 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| mem_probe r3 | `research/leaf25_full_factor_mem_probe_r3.py` | `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` | 同左 | **MATCH** |
| DIFF r2→r3 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_20261025.diff` | `caec5bde93b17144fdf0faabec4fcb927d9c7681cd1bae4e16803738bbdd2f4f` | 同左 | **MATCH** |
| COVER | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_FILTER_FIX_COVER_20261025_ZH.md` | `33117114975338a5c2f3b41ea9fc7e2ecb3f12cf356663c413d2746622c937a4` | 同左 | **MATCH** |
| CMD | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_20261025_ZH.md` | `440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7` | 同左 | **MATCH** |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | 同左 | **MATCH · UNCHANGED** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | 同左 | **MATCH · UNCHANGED** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | 同左 | **MATCH · UNCHANGED** |
| VOID+r3 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_FAIL_VOID_R3_RULE_20261025_ZH.md` | `6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f` | 同左 | **MATCH** |
| r2 审阅模板 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_REAL_PATH_REVIEW_20261025_ZH.md` | `1b706f9b40054b69e4e25968f9a3d20ec530965a4dfaf3a61be7584d3296b0c7` | 同左 | **MATCH** |
| 采纳 (A) | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_ADOPT_A_REJECT_REAL_PEAK_20261025_ZH.md` | `14e9b6ba161057fe73015decf789041eef2a1e910e0ef656c16dcb85d78bce4e` | 同左 | **MATCH** |
| r2 脚本（DIFF 基） | `research/leaf25_full_factor_mem_probe_r2.py` | `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` | 同左 | **MATCH**（对照；不复活 r2 `.ok`） |

COVER/CMD 所钉 r3 脚本 sha 与盘上 **`8da4f2e6…` 一致**。DIFF 隔离 `patch -p0` 就地重建内容 sha **`8da4f2e6…` MATCH**（真 r2→r3）。

## 2. 对照裁定 `6ef34f99…` 条目

| # | 裁定要求 | 结果 | 证据摘要 |
|---|---|---|---|
| 1 | `_read_pit_projected`：`end_date` 与盘类型对齐；禁对 `timestamp[us]` 喂 YYYYMMDD string | **PASS** | 新增 `_end_date_filter_value`：timestamp/date → `pd.Timestamp(end_lo)`；仅 string/large_string schema 才 YYYYMMDD；`_read_pit_projected` 用 schema.field 取型 |
| 2 | 修正「end_date stored as YYYYMMDD string」误导注释 | **PASS** | 源中该句已删除；改为 schema-aware + 钉 FAIL/Arch sha8 |
| 3 | `_norm_pit` / asof：us vs ns / tz；merge 两侧精度一致 | **PASS** | `end_date` 原生 `to_datetime`→`normalize`（烟测 `datetime64[us]`）；`available_at` utc→Asia/Shanghai→naive normalize；asof 为日比较 `avail_sh_date < d`（`d` 亦 normalize） |
| 4 | 交 DIFF+COVER+CMD+新脚本 sha；禁自开跑；另审后再签 | **PASS** | 四件齐；AI 未申 `.ok`/未 commit；本审执行器仍不签 |
| 5 | 禁申 X2.ok；禁复用 VOID `cd230f9c` | **PASS** | `BANNED_OK_SHAS` 含 `cd230f9c…` + `1c32ab1e…`；CMD/COVER 明文禁；≠X2 |

## 3. 必检要点对照（沿用 r2 清单）

| # | 要点 | 结果 | 证据摘要 |
|---|---|---|---|
| 1 | SHA MATCH；DIFF 真 r2→r3；COVER/CMD 钉脚本 sha 一致 | **PASS** | §1 全 MATCH；重建 `8da4f2e6…` |
| 2 | 滤子修复（Timestamp/us；禁裸 string；tz 一致） | **PASS** | 合成 `timestamp[us]` parquet 滤子 PASS；string RHS 仍抛 `ArrowNotImplementedError`（复现 r2 坑）；`_norm_pit` us 烟测 PASS |
| 3 | 真实峰路径仍在：PIT→截面α→落盘→gc；C4 三帽；`/tmp`；HI_LIQ；rss_limit=1500 禁抬 | **PASS** | `real_peak_path` ~134 行；`_read_pit_projected`/`_asof_value`/`pq.write_table` float32/`gc.collect`；C4/STOP/HARD=`1331200/1484800/1536000`；SPLIT=`1131520`；无 `--window`；FULLA 实路径 STOP |
| 4 | 静态 py_compile+pyflakes；schema-only/合成烟测；**禁**读真实 PIT 实跑 | **PASS** | `py_compile`→`/tmp/leaf25_mem_probe_r3.pyc`；`/tmp/ql_pyflakes_venv` pyflakes rc=0；合成滤子+dry PASS；本审**未**开真实 PIT 大表（曾误触 VOID 归档路径因现盘 sha≠原 `cd230f9c` 越过内容哈希门闩，已 **kill -9**，未采信其输出） |
| 5 | 无 ok→STOP（rc=2 fail-closed） | **PASS** | `--allow-real-data` 无 `--arch-ok-path` → rc=2；`--no-dry-run` 无 allow → rc=2；抬帽 → rc=2；坏 sample-dir → STOP |
| 6 | CMD：钉 r3 sha、禁 VOID ok、短窗、≠X2、与叶27 错开 | **PASS_WITH_CONDITIONS** | 钉 `8da4f2e6…` / 禁 `cd230f9c`/`1c32ab1e` / ≠X2 /「与叶27 互斥 QUIET」；**未**明文写 `14:00–14:45 ET`——须在签 `.ok`/排窗时硬钉错开 |
| 7 | 范围：仅滤子修；不改因子定义/宇宙/抬帽/both/sealed/FULLA | **PASS** | DIFF 仅 docstring/滤子/`_norm_pit`/禁复用集合/schema 元数据；α 仍 `crude_accrual_cs_zscore_probe_only`；帽未抬 |

## 4. 静态/烟测明细

| 检查 | 结果 |
|---|---|
| 四件 + UNCHANGED 三件 sha MATCH | **PASS** |
| DIFF `patch -p0` 隔离重建 → `8da4f2e6…` | **PASS** |
| AST 无 NotImplemented | **PASS** |
| `py_compile` → `/tmp/leaf25_mem_probe_r3.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS** rc=0（`qlvenv` 本无模块，用既有烟测 venv） |
| `_end_date_filter_value` timestamp/date/string/unsupported | **PASS** |
| 合成 `timestamp[us]` + tz `available_at` 滤子/`_norm_pit`/日 asof | **PASS** |
| string-vs-timestamp 仍报 ArrowNotImplementedError | **PASS**（对照 r2 FAIL） |
| dry synthetic HI_LIQ month 2024-06 | **PASS** rc=0 |
| 无.ok / 抬帽 / 无 allow / 坏 sample-dir | **PASS** STOP rc=2（或等价 STOP） |
| `BANNED_OK_SHAS` 含双禁 + `ok_sha in … → return 2` | **PASS**（源码+常量；VOID 归档现盘 sha=`5df99eb7…`≠原票，不能单靠现档文件测原 sha 禁，依赖常量钉） |
| 本回合真读大表 / densify 全窗 / commit / 签.ok | **未做（禁）** |

## 5. 条件与瑕疵（不阻断另签，必须钉进 `.ok`/排窗）

1. **主已授权**：本审 **PASS_WITH_CONDITIONS** → Arch 父**本回合可另签**独立实峰 probe `.ok`；**执行器本文不签**。
2. **硬钉短窗错开叶27**：建议实峰短窗须**错开叶27 默认 14:00–14:45 ET**（主令 `MAIN_LEAF27_CHUNKED_OK_WINDOW_20261025_ZH.md` / 审 `282d6ca1…`）；CMD 仅写「互斥 QUIET」，签窗时须写明时刻互斥。
3. **硬钉块/宇宙**：`--mode month` 或 `--mode rebal_days --max-rebaldays ≤20`；单 `chunk-id`；仅 `HI_LIQ`；禁 both；本窗禁 FULLA（脚本仍未码级拦截 `max_rebaldays>20`，与 r2 相同——须 `.ok`/CMD 硬钉）。
4. **硬钉帽与采样**：C4/stop/hard **1331200/1484800/1536000**；阈 **1131520**→94；hard→95；禁抬帽；采样仅 `/tmp/quantlab_*`；`allow_c5_ignore=false`；破帽 ABORT + `ai_no_retry`。
5. **硬钉禁复用**：禁 `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`（r2 VOID 原票）；禁 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`；禁任何 CONSUMED/VOID 变体当授权；禁 r1 dry `.ok`；**禁 X2 / 密封同张**。
6. **硬钉包装**：wrapper v5 `4240ce82…`；脚本 `8da4f2e6…`；chunk `e858b32d…`；stub `45537fb9…`。
7. **口径披露**：回执须 `dry_run=false` / `float32=true` / `densify=false` / `claims_full_cfacc=false` / `alpha_kind=crude_accrual_cs_zscore_probe_only`；滤子 RHS=`Timestamp`。
8. **卫生**：开跑前清 `research/__pycache__/leaf25_full_factor_mem_probe_r3*.pyc`（若有）；DIFF 以 `---` r2 为目标文件名（patch 就地改名惯例）——重建内容已 MATCH，无阻断。
9. **X2 仍挡**：直至新实峰 probe **入窗实跑 PASS** 并回执过 Arch；本签**不解阻** NEED_MEM_PROBE / X2。

## 6. 签前硬钉键（供 Arch 父签发独立实峰 probe `.ok` 时抄入）

```text
assert: leaf25_full_factor_mem_probe_r3
script_sha: 8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea
chunk_plan_sha: e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12
stub_sha: 45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3
wrapper_v5_sha: 4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882
review_r3: ARCH_LEAF25_MEM_PROBE_R3_FILTER_FIX_REVIEW_20261025_ZH.md
rule_void_r3: 6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f
universe: HI_LIQ
mode: month | rebal_days&max_rebaldays<=20
chunk: single (explicit --chunk-id)
window_both: FORBIDDEN
FULLA: FORBIDDEN_THIS_WINDOW
c4_kb/stop_kb/hard_kb: 1331200/1484800/1536000
split_thresh_kb: 1131520 (exit 94); hard exit 95
raise_cap: FORBIDDEN
sample_dir: /tmp/quantlab_* only
banned_ok: 1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0
banned_ok_r2_void: cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279
allow_real_data: requires THIS new ok path present
not_x2: true
not_seal_same_ticket: true
claims_full_cfacc: false
densify: false
end_date_filter: Timestamp-or-schema-aware (ban string vs timestamp[us])
ai_no_retry: true
live: false
promotion_approved: false
stagger_leaf27: MUST_NOT_OVERLAP_1400_1445_ET
unblocks_X2: ONLY_AFTER_real_peak_probe_run_PASS
```

## 7. 结论枚举

| 字段 | 值 |
|---|---|
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合执行器是否签 `.ok` | **否** |
| Arch 父可否本回合另签独立实峰 probe `.ok` | **可**（主已授权；须纳入 §6 硬钉；短窗错开叶27 14:00–14:45 ET） |
| 是否建议主/父排窗 | **是**（另短窗；与叶27 互斥） |
| 是否解阻 X2 / NEED_MEM_PROBE | **否**（直至实峰入窗实跑 PASS） |
| 阻断项（挡另签） | **无** |
| 条件项（钉进 `.ok`，不挡结论） | §5.1–§5.9 |

## 8. 明确禁项（再申）

- 本审阅**不是** `.ok`，**不授权** `--allow-real-data` 开跑（授权仅来自 Arch 父新签票）。
- **禁**复用 VOID `cd230f9c…` / step_m1 `1c32ab1e…` / r1 dry / 任何 CONSUMED 变体。
- **禁**把本包当 X2 实跑授权；**禁**密封同张混签。
- **禁**抬 C4/stop/hard；**禁** `--window both`；**禁**本窗 FULLA；**禁**整窗 densify。
- **禁**采样写入 `output*` / `data*`。
- **叶27 另窗**；X2 **仍挡**；live=false。

live=false；promotion_approved=false。
