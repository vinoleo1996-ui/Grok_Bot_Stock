# Arch 审阅：Strategy moneyflow 剥舱+80/20 诊断脚本 v1

- 审阅人：QuantLab Arch（执行器）
- 时刻（America/New_York）：2026-10-25T04:55:51-04:00
- 方式：只读静态审阅；复算 sha；`py_compile` / `--help` / `normalize_code` 断言 / 用已有 code_change .ok 实测拒绝（exit 1）；**未**读权重/行情、**未**建 out_dir、**未**签 run .ok、**未**改主干、**未** commit
- **结论：PASS_WITH_CONDITIONS（有条件通过）**
- live=false；promotion=false；研究级；勿混叶25/补跑/enable/纸面

## 1. 结论摘要

code_change 范围内的新脚本与 DIFF **可接受**：路径合规、CMC 未改、剥舱语义正确（剔除 510300 后归一，**无**溢出回灌）、80/20→共同日→clip≥0 再归一→book-smoke（core=0）→门B+GATE_V3 接线齐全，安全门拒绝 code_change/DRAFT/_consumed/过期/allow_run≠true。

**条件（签 run .ok 前须满足，本审阅不代签）**：
1. run .ok 钉死下文「建议字段」全部 sha/路径（含 decay_outcome），`allow_run=true`，`live=false`，`research_only=true`，建议 `single_use=true`。
2. 实跑窗**避开**叶25 `2026-10-25T10:00:00-04:00`–`10:45:00-04:00`（脚本未硬编码避窗，靠 .ok/`avoid_windows`+人工排程）。
3. 单进程 RSS 意识：REQ 线 ≤1536MB；脚本无内置 RSS 看门狗——实跑须外挂 runguard/rss_wrap 或等价，或接受研究短跑风险并在回执披露 peak RSS。
4. CLI 可改 `--blend-trunk/--blend-sat/--strip-codes/--tiers`；run .ok 建议显式钉 `blend_trunk=0.8`、`blend_sat=0.2`、`strip_codes=510300`、`tiers=600000,1000000`（脚本 AUTH_REQUIRED 未强制这些键——**COND**）。
5. `decay_outcome` 须由 Arch 按既有衰减结果钉 KEEP|REJECT|WATCH|FAIL|SKIP（脚本强制存在且枚举校验）；未钉则无法跑。

不阻塞项（已 PASS）：sha/DIFF 范围、forbid CMC、剥舱方向、auth 拒绝实测、topN/单名缺口 summary 披露、无 shell=True/无密钥打印、out_dir 默认研究路径且禁 paper 标记。

## 2. sha 表

| 对象 | 路径 | 宣称 sha256 | 复算 | 结果 |
|---|---|---|---|---|
| 脚本 | `research/strategy_moneyflow_stack_diag_v1.py`（837 行） | `c2ff6045…694c63` | `c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63` | **MATCH** |
| DIFF | `docs/v2/audit/STRATEGY_MONEYFLOW_STACK_DIAG_V1_20261025.diff` | `3c0145e1…ea258` | `3c0145e1af9cd799e1bf9f1e668505203517e8a9b8338661d7a6f98cb16ea258` | **MATCH**；unified 重建字节=脚本 |
| code_change .ok | `output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_CODE_CHANGE.ok` | `951f3ce2…` | `951f3ce2e8f95d73e64c1be111bdf8013ffc3eb8e754762f5d7c93858043e67b` | **MATCH** |
| CMC（forbid） | `research/alpha_combo_marginal_v1_2.py` | `bba212af…`（既有钉） | `bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4` | **未改**；DIFF 无此文件；`git status` 对该路径为未跟踪 `??`，内容仍 bba212af |
| 接口 | `docs/v2/STRATEGY_MONEYFLOW_STACK_INTERFACE_20261025_ZH.md` | `17ac041f…` | `17ac041ff480472cc574635d4ba7b0b086c043a9cd381cd6e3a879a0070315b7` | MATCH |
| 申请 | `output/strategy_hiliq/REQ_MONEYFLOW_STACK_DIAG_AUTH.txt` | `48640e14…` | `48640e14480a235111fbaa7ea7812ff8c420ca88ebd0718086096f96087b4720` | MATCH |
| 裁示 A | `docs/v2/ARCH_STRATEGY_MONEYFLOW_STACK_DIAG_TOOL_DECISION_ZH.md` | （文内引用） | `02ce98c3fb594625a90cfa7ea31a521dd0183d4b6dfab5d63741b268ef0cc61b` | 存在 |

**DIFF 范围**：仅 1 个 `diff --git` → `research/strategy_moneyflow_stack_diag_v1.py`（`new file mode 100644`）；无 CMC/其他路径。

**建议钉入 run .ok 的输入复算（本机现盘，America/New_York 审阅时）**：

| 键 | 路径 | sha256 |
|---|---|---|
| script_sha256 | `research/strategy_moneyflow_stack_diag_v1.py` | `c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63` |
| trunk_sha256 | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` |
| sat_sha256 | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet` | `dd6da010cf8c505c82c7c1c0cabd3640b1083e9db8936b55e593414dae89317b` |
| trunk_ref_nav_60w_sha256 | `output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK/nav.csv` | `c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f` |
| trunk_ref_nav_100w_sha256 | `output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK/nav.csv` | `aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1` |

## 3. 审查清单（逐条）

### 3.1 sha 复算 + DIFF 仅新文件 — **PASS**
- 证据：上文 sha 表；DIFF L1–5 仅该新文件；重建 sha==脚本。

### 3.2 对照 code_change .ok — **PASS**
- `allowed_new_path=research/strategy_moneyflow_stack_diag_v1.py`：脚本在该路径（SCRIPT_REL L45；文件存在）。
- `forbid_modify=research/alpha_combo_marginal_v1_2.py`：CMC sha 仍 `bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4`；DIFF 不含。
- `forbid_cmc_extension=true`：新脚本独立，未 import/改 CMC。
- code_change `allow_run=false`：脚本实测拒绝该 .ok（见 3.4）。

### 3.3 对照接口（剥舱/80/20/共同日/clip/book-smoke/门）— **PASS**
- 剥舱：`strip_and_renorm` L307–327 剔除 strip_codes（默认 510300，L617–619），按日 Σw=1；**无**把溢出加回 510300（与 CMC 相反；`blend_policy.note_zh` L732 明示）。
- 80/20：默认 `--blend-trunk 0.8` / `--blend-sat 0.2`（L613–614）；和为 1 校验 L653–657。
- 共同日：`blend_weights` inner join L335–345；`calendar_policy=inner_join_common_sessions_only`。
- clip≥0 再归一：L356–360。
- book-smoke：`run_book_smoke` L441–513，`--run-nav`，sleeves `{"core":0,"stock":1,"alpha_event":0}`（L466），subprocess 列表无 shell。
- 门B+GATE_V3：`judge_gates` L543–598；summary 写出 L793–817。
- 产物：默认 out `output/strategy_hiliq/moneyflow_stack_8020_20261025`（L42）；写 `blended_weights_8020.parquet` / `summary.json` / `meta.json` / `ARTIFACT_MANIFEST.txt`（L704–821）；`check_out_dir` 要求事先不存在或空（L220–229）。

### 3.4 安全门 — **PASS**（实测）
- `--arch-ok` required=True（L606–608）。
- 拒 DRAFT / `_consumed` / `.consumed`（L103–106）。
- 拒 `auth_type/kind=code_change`、`allow_write_code` 且非 allow_run、`allow_run=false`（L119–134）。
- `enforce_run_auth`：`allow_run is True`、`live is False`、`promotion is False`、过期拒绝、sha 钉死（L173–209）。
- 实测：喂 `951f3ce2…` code_change .ok → `mf_stack_diag blocked: … code_change …` **exit 1**；out_dir **未创建**。

### 3.5 内存 / 叶25 窗 — **WARN → 条件**
- REQ：`rss_cap_mb_per_process=1536`；脚本**无** RSS 采样/硬杀。
- 有 `check_quiet_lock`（L232–235）但**无** 10:00–10:45 ET 硬避窗。
- 处置：run .ok 写 `avoid_windows=…`；实跑外挂内存护栏；人工避开叶25窗。不因此 FAIL 脚本（属运维钉，非剥舱逻辑错）。

### 3.6 缺口披露 — **PASS**
- docstring L18；`gate_v3.note_zh` L593–595；`blend_policy.topN/name_cap=None` + `note_zh` L730–732。
- `decay_outcome` ∈ AUTH_REQUIRED（L70）且枚举校验（L210–215）；注释要求 run .ok 钉（L10–11）。

### 3.7 静态风险 — **PASS**（附注）
- 写路径：仅授权后的 `out_dir`（研究默认）+ book-smoke 子目录；paper 标记路径拒绝（L46–52, L223–225）。
- 读数：权重/NAV 仅 auth 通过后；路径由 CLI 默认钉到已知研究 parquet/nav，且 sha 必须与 .ok 一致。
- 权重：默认 0.8/0.2，和校验；剥舱默认 510300。
- `subprocess.run(cmd_list, …)` **无** `shell=True`（L480–487）。
- 未见 api_key/password/secret 打印。
- 附注：`void()` 在失败时会 `mkdir` 并写 `VOID.md`（L251–260）——仅 auth 后；可接受。

### 3.8 建议 run .ok 字段（草案，**勿真签**）— 见第 5 节

## 4. 条件 / 阻塞项（签 run 前）

| ID | 级别 | 项 | 处置 |
|---|---|---|---|
| C1 | COND | 脚本无 RSS 硬帽 | 外挂 ≤1536MB 或回执披露 peak；.ok 可写 `rss_cap_mb=1536` |
| C2 | COND | 脚本无叶25避窗硬校验 | .ok `avoid_windows=2026-10-25T10:00:00-04:00/2026-10-25T10:45:00-04:00`；排程避开 |
| C3 | COND | blend/strip/tiers 未进 AUTH_REQUIRED | .ok 显式钉 0.8/0.2、510300、600000,1000000；CLI 勿改 |
| C4 | COND | `decay_outcome` 须 Arch 选定钉入 | 无钉则脚本拒跑（设计如此） |
| — | 非阻塞 | CMC / DIFF / 剥舱 / auth 拒绝 | 已 PASS |

**无 FAIL 级逻辑缺陷**（在 code_change 授权范围内）。

## 5. 建议 run .ok 字段草案（键值列表，勿真签）

```
format=quantlab_run_auth_v1
auth_type=run
kind=research_diag
signed_by=arch
allow_run=true
allow_write_code=false
live=false
promotion=false
promotion_approved=false
research_only=true
single_use=true
forbid_paper_handoff=true
no_new_moneyflow_solo_smoke=true
script_path=research/strategy_moneyflow_stack_diag_v1.py
script_sha256=c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63
trunk_path=output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet
trunk_sha256=3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
sat_path=output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet
sat_sha256=dd6da010cf8c505c82c7c1c0cabd3640b1083e9db8936b55e593414dae89317b
trunk_ref_nav_60w=output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK/nav.csv
trunk_ref_nav_60w_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
trunk_ref_nav_100w=output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK/nav.csv
trunk_ref_nav_100w_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
out_dir=output/strategy_hiliq/moneyflow_stack_8020_20261025
blend_trunk=0.8
blend_sat=0.2
strip_codes=510300
tiers=600000,1000000
decay_outcome=<Arch钉：KEEP|REJECT|WATCH|FAIL|SKIP>
rss_cap_mb=1536
avoid_windows=2026-10-25T10:00:00-04:00/2026-10-25T10:45:00-04:00
expires_et=<签发后短窗，建议≤48h，且避开叶25窗>
note=research_once_moneyflow_strip_8020;not_leaf25;not_backfill;not_paper
```

建议落盘路径（待签时）：`output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_MONEYFLOW_STACK_DIAG_RUN.ok`（本文件**未创建**）。

## 6. 静态抽检记录

- `py_compile`：OK（qlvenv）
- `--help`：OK，`--arch-ok` 必填
- code_change .ok 拒绝：exit 1，文案含 `auth_type/kind=code_change`；`moneyflow_stack_8020_20261025` 未创建
- `normalize_code('sh.510300'|'510300.SH'|'510300')=='510300'`：OK

## 7. 给 Strategy / 主 Agent 的一句话

**脚本+DIFF 有条件通过；CMC 未动；请主/Arch 在避开叶25窗且钉好 decay_outcome+五文件 sha 后另签 allow_run=true 的 run .ok，本审阅不代签、不实跑。**
