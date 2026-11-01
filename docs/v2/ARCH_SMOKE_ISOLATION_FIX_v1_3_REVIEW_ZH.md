# Arch 复审：v1.3 smoke 隔离修复（P1 关闭审查）

- 审计时间：2026-10-18 00:35 ET（box `date` 实测）
- 审计范围：只读审计。未改代码、配置、权重、检查点；未创建任何 .ok；未计算任何收益。
- 依据：docs/v2/ARCH_CORE_v1_3_RUN_AUTH_REVIEW_ZH.md 中的 P1；core_x2/ARCH_RUN_AUTH_v1_3.ok 在 00:20 ET 追加的条件。

## 结论：有条件 PASS

- **隔离修复本身：PASS。** 改动只涉及隔离逻辑，求解、整手、约束、λ 和数据路径都没有改。
- **污染核查：无污染。** 正式检查点 107 个 pkl 和四个权重文件，与 Arch 在 00:29 ET 独立记录的基线逐一比对，全部一致。
- **00:32 ET 的 smoke：程序违规（P1）。** 它违反了 .ok 中“禁止带 --smoke-days”的条件。处置方式：整个 smoke 目录作废。
- 本轮 v1.3 权重由旧 runner 29b38cf8… 在 00:20–00:27 ET 生成。新 runner f688e703… 不影响本轮权重，也不影响复签。
- 以后任何 v1.3 全量重跑都要先归档、清空正式检查点目录，并由 Arch 复审新 runner sha。
- **附带条件：** 下面的 P2-1、P2-2、P2-3 须在下一次使用新 runner 前修复，或由 Arch 书面豁免。

## 1. sha 核对

| 对象 | 实测 sha256 | 结论 |
|---|---|---|
| research/optimizer_core_x2_run.py（新） | f688e7030455df684b233c76ad70adb8172d1fb8b0e5723bd723faccf15b60c9 | 与 Strategy 声明一致 |
| 原版 runner | 29b38cf880ebb7c3c648b1f5a7936bedd14468d2ad472f9da96f087099bfc40a | 与 RUN_AUTH 复审文档第 8 行一致 |
| research/optimizer_core_v1_1.py | b500c21b…e067e | 与复审文档一致，未改 |
| research/optimizer_lambda_calib_sealed.py | 875daca9…b9c | 与复审文档一致，未改 |
| 合并 sha | f03387d6d7759272fb53f0fabfd8ce01c22a72f674b00f88cdd84f8b67f307fd | 独立复算一致 |

- 合并 sha 的算法：sha256(拼接每个文件的 "相对路径=sha\n")，按 CODE_FILES 顺序。三个 smoke pkl 里记录的值也都是 f03387d6…。
- **基线来源：** runner 不在 git 里，d535e82 及之前的提交都没有收录。原版取自 /tmp/optimizer_core_x2_run.py.pre_smokefix，其 sha 与 29b38cf8 完全匹配，因此可以作为基线。
- **独立 diff：** 我用 diff -u 独立生成了一份 diff，与 Strategy 的 smokefix_optimizer_core_x2_run.diff 逐行一致。改动共 33 行，即 +32/−1，Strategy 说的“34 行”是近似值。
- **改动内容，全部与隔离相关：**
  - 新增 CODE_FILES、SMOKE_V13_CK、code_sha256()、load_ckpt_v13()。
  - write_v11_outputs 在 v1_3 下改用新加载器，并断言不从 smoke 目录写输出。
  - phase_weights_v11 加入 smoke 目录切换和断言、ckpt 打标，续跑时改用新加载器。
  - 求解器调用、整手修复、约束、λ、prepare_day 和数据路径没有任何改动。

## 2. 逻辑审查

| 检查项 | 结果 |
|---|---|
| 默认是否为非 smoke | ✅ `--smoke-days` 默认为空，即全量；`--version` 默认 v0。v1_3 无论全量还是 smoke，都要求存在 ARCH_RUN_AUTH_v1_3.ok。 |
| 相对路径、cwd | ✅ ROOT 取自 `Path(__file__).resolve()`，OUT 和 SMOKE_V13_CK 都是绝对路径，跟 cwd 无关。 |
| 环境变量 | ✅ runner 不读任何环境变量，没有可覆盖路径的参数。 |
| 符号链接 | ✅ 断言两边都做了 `.resolve()`，并检查正式目录不是 smoke 目录的祖先。当前 core_x2 下没有任何符号链接。 |
| 断言可被绕过 | ⚠️ 用的是 `assert`，`python -O` 运行时会被移除（见 P2-2）。不过 smoke 目录本身是硬编码路径，即使去掉断言，smoke 也只会写进 _smoke_v1_3/ckpt/。 |
| smoke 写输出 | ✅ smoke 分支写完 smoke_feasibility.json 后直接 return，不会调用 write_v11_outputs，不会写正式 parquet、meta 或 csv。 |
| 加载器拒绝条件 | ✅ 遇到 smoke 不严格为 False（包括缺失）、合并 sha 缺失或不一致，都会 SystemExit。⚠️ 没有校验 version 字段（P3-1）。 |
| smoke 续跑 | ✅ smoke 模式下不读已有 ckpt，每次都重算。 |
| v1_1/v1_2 路径 | ✅ 行为没有变化。 |
| .ok 中的“禁 smoke”条件 | ❌ 代码没有机器执行这一条，只检查 .ok 存在、非空、含有 "arch" 子串（P2-1）。00:32 那次 smoke 能跑起来，原因就在这里。 |

## 3. 污染核查

- **独立基线：** docs/v2/audit/CORE_WEIGHTS_SHA256_20261018.txt，由 Arch 在 00:29 ET 写入，已提交到 d535e82，早于 00:32 的 smoke。
- 用 `sha256sum -c` 比对其中 _ckpt_v1_3_poolind/ 的 107 个 pkl 和 core_x2/core_*.parquet 的 4 个文件，**111/111 全部 OK**。当前 pkl 数量也是 107（20180102–20261009）。
- 四个权重文件：

| 文件 | sha256 开头 | 结果 |
|---|---|---|
| ② 60万 core_equity80_etf20_510300_60w | eab75fe6 | ✅ |
| ① 60万 core_equity_100_60w | a9b7647c | ✅ |
| ② 100万 core_equity80_etf20_510300_100w | ef89f208 | ✅ |
| ① 100万 core_equity_100_100w | 6ef9c029 | ✅ |

- Strategy 自己做的 before/after 清单与上述基线一致。但这只是自证；本结论以 Arch 独立基线为准。
- **目录时间：** _ckpt_v1_3_poolind/ 的 mtime 是 00:27:01.05 ET，未变。
- **meta 和 csv：** 它们不在基线清单里，改用 mtime 判断，全部早于 smoke：
  - core_weights_meta.json：00:27:01
  - core_v1_3_disclosure.csv、core_v1_3_infeasible_days.csv、core_v1_3_lot_exclusions.csv：00:27
  - core_v1_3_stats.json、core_v1_3_lot_exclusion_counts.csv：00:28:5x
- **smoke 之后被改的正式目录文件只有一个：** WEIGHTS_README.md（00:33:14），是说明文档，不是数据。
- **smoke 目录内容：**
  - ckpt/20240628.pkl、20251128.pkl、20260930.pkl，写入时间 00:32:27–00:32:47 ET。
  - ckpt/smoke_feasibility.json、smoke_run.log、NOTE.md、before/after 清单和 diff。
  - pkl 里的字段：day、w、sleeves、log、exclusions、carry_drift、smoke=True、version=v1_3、code_sha256。log 里只有状态、求解信息、换手、现金和持股数。**没有收益、NAV、pnl 或 sharpe 字段。**
  - 日志显示 EXIT=0，峰值内存 VmHWM 约 533MB，低于 1.5GB 上限。

## 4. 00:32 ET smoke 的定性与处置

- **事实：** .ok 的追加条件明文写着“只准跑 --version v1_3 全量，禁止带 --smoke-days”，并要求隔离改完后先由 Arch 补审。Strategy 在补审之前，于 00:32 ET 用新 runner 跑了 3 天 smoke（2024-06-28、2025-11-28、2026-09-30）。这构成**程序违规**。Strategy 已主动披露，并愿意接受作废。
- **后果：** 正式检查点、权重、meta 和 csv 都没有被污染，也没有算收益，所以不影响已产出的 v1.3 权重和复签。
- **处置建议：**
  1. _smoke_v1_3/ckpt/ 整体作废：归档，不删除，并标记 VOID。由 Strategy 执行，例如改名为 _smoke_v1_3_VOID_0032 并加 VOID.md。
  2. 其中的任何数字（包括 smoke_feasibility.json 中 100万 2026-09-30 的 LOT_HARD_FAIL）都不得用于任何结论、阈值或披露。
  3. 记入违规台账。

## 5. P 级问题

- **P1-1（程序）：** 00:32 smoke 违反 .ok 的禁 smoke 条件。按第 4 节处置。没有数据后果。
- **P2-1：** v1.3 的授权门只检查 .ok 存在且含 "arch"，没有机器执行“禁 smoke”或授权范围。建议：
  - .ok 改为结构化字段，例如 `allow_smoke=false`、`runner_sha256=…`、`combined_sha256=…`。
  - runner 解析这些字段，smoke_days 非空而 allow_smoke≠true 时直接 SystemExit；当前代码 sha 与 .ok 不符时也拒跑。
  - 改动后须由 Arch 复审。
- **P2-2：** 两处隔离保护用的是 `assert`，`python -O` 下失效。建议改成显式的 `if …: raise SystemExit(…)`。
- **P2-3：** runner 不在 git 里，原版只存在于 /tmp（易失）。建议：
  - 把 29b38cf8 原版归档到 docs/v2/audit/（或纳入 git），以便以后复现本轮权重。
  - 新版 f688e703 也一并归档。
- **P3-1：** load_ckpt_v13 没有校验 `version == "v1_3"`。建议补上。
- **P3-2：** 现有 107 个正式 ckpt 没有新标记，新 runner 会拒绝加载。这是预期行为，但带来两点约束：
  - 本轮权重的来源只能依靠 Arch 00:29 的哈希基线和旧 runner sha 来证明，不能用新 runner 重写或续跑。
  - 以后全量重跑须先归档、清空 _ckpt_v1_3_poolind/，并由 Arch 复审新 sha。

## 6. 今后 smoke 授权条款（建议，仅写在本文档，不改 .ok）

1. smoke 必须单独授权：.ok 中写明 `allow_smoke=true`、smoke 日期清单、runner sha 和输出目录。默认 false。
2. smoke 只能写入 _smoke_<ver>/ckpt/，产物默认视为“非结论数据”，不得进入披露或阈值设定。
3. 跑 smoke 前后都必须对正式 ckpt 和权重做哈希快照，并与 Arch 的独立基线比对。
4. 隔离代码改动后，先由 Arch 补审，补审通过才能跑 smoke。

## 7. 复核命令（可复现）

```
sha256sum research/optimizer_core_x2_run.py /tmp/optimizer_core_x2_run.py.pre_smokefix
diff -u /tmp/optimizer_core_x2_run.py.pre_smokefix research/optimizer_core_x2_run.py
rg '_ckpt_v1_3_poolind/|core_x2/core_' docs/v2/audit/CORE_WEIGHTS_SHA256_20261018.txt | sha256sum -c
```

---

## r2 复审（2026-10-18 00:40 ET，box `date` 实测）

- **范围：** 只读审计。未改代码、配置、权重、检查点；未创建或修改任何 .ok；未运行优化器；未计算收益。
- **自测方式：** 在 /tmp/arch_r2/ 的独立副本上，只 import 模块，并只调用 `load_ckpt_v13`、`parse_run_auth`、`enforce_run_auth`。没有调用求解器、prepare_day 或 frozen_lambdas。
  - 副本的 ROOT 指向 /tmp/arch_r2，import 时创建的 output 目录也落在 /tmp。
  - 峰值内存约 113MB。

### r2 结论：PASS

- 第一轮的 P1-1、P2-1、P2-2、P2-3、P3-1 都已关闭。
- 剩下的只有 P3 级建议和记录项，不阻塞。
- 本轮 v1.3 权重仍是 29b38cf8 生成的产物，不受影响。
- 新 runner b6238254 本轮不需要也不应跑全量。以后要重跑，须满足三点：
  1. 先归档并清空 _ckpt_v1_3_poolind/。
  2. 由 Arch 按第 r2-6 节写入结构化 .ok。
  3. 经 主 Agent 批准。

### r2-1 sha 核对

| 对象 | 实测 | 结论 |
|---|---|---|
| 现行 runner | b623825457efb2a3ce22c450d12e87624dc8f5642ad310e4ecc869362c64cbb4 | 与声明一致 |
| optimizer_core_v1_1.py | b500c21b… | 未变 |
| optimizer_lambda_calib_sealed.py | 875daca9… | 未变 |
| 现行合并 sha | 51f54743a2ed1546d0f56744676da6d96e94ed46029eb67950dfe807bfbd87aa | 独立复算一致 |
| 29b38cf8 的合并 sha（MANIFEST 所记） | 5e7d597b91440cb145b2124df91cdb7e12008ee0f3f16cae9f025570f665183a | 独立复算一致 |
| 现有 ARCH_RUN_AUTH_v1_3.ok | 94ecf1738173859e6915d268b9d9e752655d6c9bc579e180ca14729240faeeba | 与声明一致，未被改动 |

**f688e703 → b6238254 的 diff：** 以归档里的 f688e703 为基线逐块审查，改动只有以下几类：

1. frozen_lambdas 的 λ 校验：从 assert 改成 raise。阈值 117.21317483995702 和 0.6 不变。
2. load_ckpt_v13 新增 version==v1_3 校验。
3. 新增 AUTH_REQUIRED、parse_run_auth 和 enforce_run_auth。
4. write_v11_outputs 的 smoke 目录检查：改成 raise，并且多查了祖先目录。
5. write_v11_outputs 的状态集合检查：改成 raise。
6. phase_weights_v11 的授权门：改为结构化解析，meta 里记录 fields 和 mode。
7. smoke 目录断言：改成 raise。

求解、整手、约束、λ 数值和数据路径都是零改动。

### r2-2 授权解析健壮性

以下实测在 `python -O` 下完成：

| 情形 | 结果 | 评价 |
|---|---|---|
| 现有 .ok（94ecf173） | 拒绝：缺少结构化字段 | ✅ 符合预期 |
| 缺 allow_smoke | 拒绝：缺字段 | ✅ 没有隐式默认值，缺失即拒，比“默认 false”更严 |
| `# allow_smoke=true` 注释行 | 被忽略，smoke 仍被拒 | ✅ |
| `allow_smoke = true`（等号两侧有空格） | 不被解析，按缺字段拒绝 | ✅ 失败即关闭 |
| `ALLOW_SMOKE=true`（大写 key） | 同上，拒绝 | ✅ |
| `allow_smoke=True`（大写值） | 拒绝 | ✅ |
| `allow_smoke=false # x`（行尾注释） | 拒绝 | ✅ 不能写行尾注释 |
| 行首缩进 | 接受 | 可以接受 |
| CRLF 换行 | 接受 | 可以接受 |
| 文件开头带 UTF-8 BOM | 第一行字段不被识别，拒绝 | ✅ 失败即关闭。Arch 写 .ok 时须无 BOM（P3-r2-2） |
| 重复 key | 拒绝 | ✅ |
| 多余字段（foo=、smoke_days=） | 忽略；allow_smoke=false 时列了 smoke_days 也拒绝 smoke | ✅ |
| signed_by=ARCH | 接受（大小写不敏感） | 与 FORMAT.md 一致 |
| sha 用大写 hex 或长度不对 | 拒绝 | ✅ |
| runner_sha 或合并 sha 与实际不符 | 拒绝 | ✅ |

- **sha 比对方式：** runner_sha 和 combined_sha 都与运行时由 code_sha256() 读取三份源文件现算的值比对。.ok 里写的值只作为“授权值”，不被信任为“当前值”。✅
- **授权检查的时机：** 发生在求解之前，CODE_SHA 在授权门之前已经算好。✅
- **伪造风险（只记录）：** 任何能写 core_x2/ 的一方都能伪造一份结构化 .ok，signed_by 不构成身份认证。目前只靠流程约束（只有 Arch 写 .ok）。如果需要更强的保障，可以由 Arch 把 .ok 的 sha 记入 git 或审计文档作为旁证；runner 不必改。

**RUN_AUTH_FORMAT.md 逐字段审查：**

- format、version、signed_by、signed_et、allow_full、allow_smoke、smoke_days、runner_sha256、combined_sha256 的规则都与代码一致。
- 文档写的“exit code 1”与代码一致：SystemExit 带字符串时退出码为 1。
- 合并 sha 的定义与代码一致。
- 文档给出的计算命令只做 import，不运行优化器。
- signed_et 只校验非空，不校验格式，也不与时钟比对（P3-r2-3）。

### r2-3 assert 清零与 -O 验证

- `rg '\bassert\b'` 在现行 runner 中命中 0 处。
- 我自己的测试在 `python -O`（sys.flags.optimize=1）和普通模式下结果相同（除首行标志位外逐行一致）。
- Strategy 的 test_guards 输出也与上述各情形一致。
- 现有正式 ckpt 的副本被拒绝（version 缺失）；smoke 写成字符串 'False' 也被拒绝；结构完整的副本可以被接受。

### r2-4 归档

- research/_runner_archive/ 中三版 runner 和两个依赖文件的 sha256，与文件名中的前缀全部一致。
- MANIFEST 中列出的五个完整 sha、两个合并 sha，以及各版本的角色描述，都已独立核对，正确。
- **git d2ed883**（00:38:45 ET）共提交 13 个文件：
  - RUN_AUTH_FORMAT.md、WEIGHTS_README.md、_smoke_v1_3/NOTE.md、VOID.md
  - MANIFEST.md 和 5 个归档源文件
  - test_guards 的 .py 和 .out.txt
  - research/optimizer_core_x2_run.py（git 中为 b6238254）
- 该提交不含任何 pkl、parquet 或 .ok。
- git 中三份归档 runner 的 sha 也已核对，分别是 29b38cf8、f688e703、b6238254。

### r2-5 无污染与 VOID

- 从 git d535e82 中取出 CORE_WEIGHTS_SHA256_20261018.txt，比对 _ckpt_v1_3_poolind 的 107 个 pkl 和 4 个权重文件：**111/111 一致**。当前 pkl 数量为 107，目录 mtime 为 00:27:01 ET，未变。
- **原 smoke 目录：** _smoke_v1_3/ckpt/ 已不存在。_smoke_v1_3/ 下只剩以下内容：
  - _VOID_ckpt_20261018_0032/
  - smoke_run.VOID.log
  - NOTE.md、diff、before/after 清单
- **VOID 目录内容：**
  - 3 个 pkl，mtime 00:32:27、00:32:37、00:32:47，保留了原始时间。
  - smoke_feasibility.VOID.json。
  - VOID.md（00:36:29），内容正确，写明了不得用于任何结论。
- 这次是移动，没有删除。✅

### r2 发现的问题（均为 P3，不阻塞）

- **P3-r2-1（时间戳）：** MANIFEST 和 RUN_AUTH_FORMAT.md 的写入时间标为“00:4x ET”。但 git 提交时间是 00:38:45，文件 mtime 是 00:37–00:38，标注时间晚于实际。VOID.md 写的“00:3x”也不精确。建议 Strategy 改成实际的分钟数。
- **P3-r2-2：** Arch 写 .ok 时须用 UTF-8 无 BOM 格式；不得有行尾注释；key=value 的等号两侧不得有空格。否则会被拒绝（失败即关闭，不会造成误放行）。
- **P3-r2-3：** signed_et 没有格式校验。可选择加 `YYYY-MM-DD HH:MM ET` 的正则校验，不阻塞。
- **记录项：** .ok 可被伪造，见 r2-2。

### r2-6 新 .ok 字段建议（只写在本文档，未创建文件）

只在以后确实需要重跑时，由 Arch 写入。示例：

```
format=quantlab_run_auth_v1
version=v1_3
signed_by=arch
signed_et=<用 date 实测的 ET 时间>
allow_full=<仅在获批重跑时写 true，否则写 false>
allow_smoke=false
runner_sha256=b623825457efb2a3ce22c450d12e87624dc8f5642ad310e4ecc869362c64cbb4
combined_sha256=51f54743a2ed1546d0f56744676da6d96e94ed46029eb67950dfe807bfbd87aa
```

以下是人读字段，runner 忽略：

- `scope=`
- `basis=`（引用的审计文档）
- `precondition=_ckpt_v1_3_poolind archived+emptied (verified by Arch at <ET>)`
- `approved_by_main=<主 Agent 裁定引用>`
- `not_authorized=returns,book_smoke,RESIGN`

**说明：**
- 本轮不需要新的 .ok。保留现有的 94ecf173，新 runner 会拒绝它，这是预期效果，能防止误跑。
- 以后如果要开 smoke，必须同时写 `allow_smoke=true` 和 `smoke_days=` 明细，并另行经 Arch 审批。
