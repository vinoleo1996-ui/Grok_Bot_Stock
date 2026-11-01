# Arch 审核：B4 并列打破敏感性预注册 v1

- 审计时间：2026-10-18 00:49 ET（box `date` 实测）
- 范围：只读审计。没有运行任何回测或 book-smoke，没有算收益，没有创建 .ok。
- 只做了一次纯权重构建自测：import 被审脚本，调用 `ts.build`，与参考权重比对。没有写入任何文件，主进程峰值 RSS 约 636MB。

## 结论：有条件（暂不可建 .ok）

设计主体是合格的：
- 主键不变，只替换次级键。
- RAND 用的是持久、与数据无关的优先级。
- 只跑 X2 窗口，不碰密封窗。
- 输出目录是独立的。

但有 3 个 P1 问题须在运行前改正，并重新提交 sha。改完后由 Arch 复审，通过才建 .ok。

## 1. sha 与目录

| 对象 | 实测 sha256 | 结论 |
|---|---|---|
| docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md | e237e919241678fe8e7dea0009abe1c567e8e5d61a7d30425a66d52c312ab6a2 | 与声明一致 |
| research/strategy_tie_sensitivity_prereg_v1.py | 8993e643fedba3b9e55d2d8c3355a3337de53f3b4f65bdf2a532001262465211 | 与预注册 §5 一致 |
| docs/v2/STRATEGY_CAPADV_TOPN_TIE_AUDIT_ZH.md | 31d93b6843867375ac07e5d1ae4bd9b75092ccd7c438b824e7974f0d7705ccb9 | 前缀 31d93b68，一致 |
| research/strategy_capadv_topn_tie_sensitivity.py | 912fb00794ae3a1119633fa9521cd1dae8f7f547c055c13be043a05d752c0e8e | 一致 |
| research/strategy_b4_hiliq_leg_review.py | fed36cf2567190d31b64dd1b28c6cdfc52f757ea4e514a52b2372ed98b8c1960 | 一致 |
| research/strategy_hiliq_capadv_b4_x2.py | 3f7f75c31611de6ab066d1bd2961cae3214aad26cfe144ad1641b305e49532c2 | 一致 |

- output/strategy_hiliq/tie_sens_prereg_v1/：不存在 ✅
- output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok：不存在 ✅

## 2. 构建逻辑

- **只改了并列打破。** `ts.build` 和 `lr.build` 以及纸面线使用的 `hx2.build_topn` 流程相同：腿×配比 → ETF 分离 → 逐腿取前 N 并按腿股票预算归一 → 6% 截顶（溢出转 510300） → 申万一级 25% 截顶 → 归一。唯一的差别是 selector。
- **参考权重复现。** 我做了纯权重比对，对照 b4_leg_review/weights_B4_50_25_25_{60w,100w}：

| 变体 | 结果 |
|---|---|
| **PROD** | max\|Δw\| 在两档都 = 0，12293 行和 19671 行逐行一致 ✅ |
| **CODE** | **不能**复现参考权重（60万 max\|Δw\|=0.142，10804 行不同） |

  - 这符合设计：参考权重（N1 诊断版）是由 PROD 规则生成的。
  - CODE 对应的是旧腿和纸面 B4 的实际效果（纸面事件腿文件按代码排序）。这一点是根据审计文档 §5 的说法，本次没有对纸面重建做比对。
  - 所以“CODE 逐行复现参考权重”这个前提不成立，正确的说法是 **PROD 逐行复现参考权重**。
- **RAND 只在并列者之间打破。** 抽样 790 个（腿, 日, N）组合，没有一例违反：所有权重严格大于第 N 名的股票都被选中，也没有选入权重低于第 N 名的股票。
  - 同输入重复调用，790/790 完全一致，可以复现。
  - 种子之间用 md5(seed|leg|instrument)，彼此独立。
  - 60万档名单 Jaccard 均值：RAND1 vs RAND2 = 0.44，PROD vs RAND1 = 0.44，PROD vs CODE = 0.45。
- **未来信息：**
  - RAND 和 CODE 的键与任何行情数据无关，不引入未来信息。
  - ADV = float_mktcap×turnover_rate/100，按 trade_date 计算 rolling(20, min_periods=10).mean()，再 shift(1)，在调仓日 s 只用到 s−1 及更早的数据 ✅。
  - PROD 依赖腿文件行序（来自 PYTHONHASHSEED 决定的 set 顺序）。行序已经固化在磁盘上的文件里，不含未来信息。

## 3. 安全性

- **.ok 门控：** 脚本只检查 `GATE.exists()`。没有结构化字段，不自算 sha，不区分模式，达不到 core_x2 RUN_AUTH_FORMAT 的严格程度（**P1-1**）。
- **输出位置：**
  - 权重、smoke 子目录和 summary.json 都写在 OUT 下。
  - book-smoke 的 `--receipt` 已重定向到 smoke 子目录，不会写 docs/。
  - 导入的模块会对已存在的 topn_tie_audit/ 和 b4_leg_review/ 执行 mkdir(exist_ok)，不写文件。
- **只读输入：** 3 个 N1 腿、valuation 数据、b4_leg_review 的 capadv_only_pos_weights、审计 CSV。不碰 paper、FROZEN、sealed、core_x2 ✅
- **窗口：** `--windows X2`，只跑 X2 ✅
- **串行：** run_smoke 用的是 subprocess.run，会阻塞等待，所以同一时间只有一个 book-smoke 子进程 ✅
- **内存估算：**
  - 主进程：腿缓存加构建实测约 0.64GB，加上 ADV 透视表（约 5000 列×约 460 日）预计 <1GB。
  - 子进程：约 0.43–0.7GB。
  - 单进程低于 1.5GB。
- **耗时估算：** 23 个变体，每次构建约 2 秒；46+1 次 smoke，每次 14–32 秒。合计约 12–26 分钟。

## 4. 设计审查

**判读规则：**
- §4 已经事前写死了第 1 条（超出 [p10, p90] 标记为敏感）、第 2 条（头条用 RAND 中位数 [p10, p90]）、第 3 条（p90−p10 > 5pp 降级）。
- 欠缺：
  - 第 4 条只禁止选用 ADV，**没有一般性地禁止“事后挑选最好的变体来替换现行规则”**。
  - 第 6 条只说“不改变纸面轨或诊断版权重”，**没有明说“无论结果如何都不改纸面 B4 规则；如要修改，必须走冻结流程加 Leo 决定加新的预注册”**（**P1-3**）。
- 已满足：以 RAND 分布代替单一 X2 数字；披露 PROD、CODE、ADV 的分位（严格小于该值的比例）✅

**预注册前已看过的信息：**
- 中止批次的部分结果全部看过：60万 n=15，100万 n=15（含 RAND15_100w），也看到了 CODE 在第 73 百分位、ADV 低于最小值、PROD 在 100万档超出 p90 等。
- 种子数 20 在中止批次开跑时就已定下（审计文档 §4 的理由是 p10/p90 各至少 2 个观测点），不受结果影响 ✅
- **但第 3 条的 5pp 阈值是在看过 60万档 p90−p10 ≈ 6.8pp 之后写的**，事实上可以预见会触发。须如实披露（**P2-5**）。
- 判读规则在看过结果之后才写出，这本身已经在文档中披露。

**指标：**
- 脚本只记录 CAGR、MDD、Calmar。
- 预注册 §3 承诺的“成本占初始资金、成交率”，脚本**没有落盘**。
- 胜率和换手也没有。nav_metrics 本身已经返回 win_daily 和 win_monthly，book_smoke_summary 里有 cost 和 fill，可以直接取用（**P2-2**）。

**窗口：** 只有 X2，没有其他窗口，也没有密封窗 ✅

**SPLIT（并列者等权分摊）：**
- 行业惯例是用确定性、与收益无关的打破方式。
- SPLIT 的做法：并列组跨越第 N 名时，把剩余名额的预算等权分给整个并列组，名单可以多于 N。这是唯一不做任意选择的无偏基准。
- 代价：持股数和整手冲击会变化，须单独披露持股数和成交率。
- 建议作为对预注册的修改加入，在运行前完成，并给定确切定义（**P2-1**）。
- SPLIT 同样只作基准披露，不得被选用。

## 5. P 级问题

**P1（须在建 .ok 之前修复）：**

- **P1-1：门控过弱。** 改为与 core_x2 RUN_AUTH_FORMAT 同等严格：
  - 解析 `^key=value$`，缺字段、重复字段、格式错都拒绝。
  - 布尔值只接受 true 或 false，没有默认值。
  - 脚本在运行时自算以下文件的 sha，并与 .ok 比对，不符即拒：
    - 脚本本身
    - 预注册文档
    - 3 个依赖：ts、lr、hx2
    - 审计 CSV
    - capadv_only_pos_weights
  - 校验 out_dir。
  - 用 raise SystemExit，不用 assert。
- **P1-2：脚本没有复现校验。** 须在任何 smoke 之前：
  - 断言 PROD 两档权重与 b4_leg_review 参考权重 max\|Δw\| = 0（参考文件 sha 写入预注册）。不通过就整次中止。
  - 预注册 §1 和 §2 须更正表述：参考权重由 PROD 复现；CODE 对应纸面 B4 和旧腿的实际效果。
- **P1-3：判读规则补两条。**
  - (a) 任何变体（包括 SPLIT、ADV、CODE 和 RAND 中最好的种子）都不得因结果被选为新规则。
  - (b) 无论结果如何，都不修改纸面 B4 和诊断版规则。如要修改，必须由 Leo 决定，并走冻结流程和新的预注册，用 X2 之外的前瞻数据检验。

**P2（建议在运行前修复，否则须在预注册中书面豁免）：**

- **P2-1：** 加入 SPLIT 基准（见第 4 节），作为第 24 个变体，写明确切定义。
- **P2-2：** summary.json 增加以下字段：win_daily、win_monthly、成本占初始资金、成交率、年化单边换手（由权重文件计算）。并按 RAND 分布报告其分位。
- **P2-3：** capadv-only 的零效应前提目前依赖中止批次的审计 CSV，而且用的是 assert。须改为二选一，并改用 raise：
  - 在脚本内重算；或
  - 把该 CSV 的 sha 写入预注册和 .ok。
- **P2-4：** 预注册第 5 条“capadv-only 与现有 capadv_x2 差异 ≤1e-6”在脚本里没有实现。须写明参考 nav 路径和 sha，并加入比对代码。
- **P2-5：** 补充失败处理：任何一次 smoke 失败或 nav 缺失，整次运行作废，不报告部分结果。目前 m=None 时，后面的分位计算会报错或混入 None。另外须披露第 3 条的 5pp 阈值是在看过部分结果之后设定的。

**P3（记录项）：**

- **P3-1：** keyed 变体对权重做了 round(12)，PROD 不做。差异在 1e-12 以下，影响可以忽略。
- **P3-2：** ADV 缺失时记 0，ADV 也相同时，lexsort 是稳定排序，会退回到文件行序。须披露。
- **P3-3：** 20 个种子下，p10 和 p90 各只由约 2 个观测点插值得到，精度有限。是否扩到 50 个，须在运行前以精度为理由决定，不得参照已看过的结果。不扩也可以，但须在结论中注明。

## 6. 修复后的 .ok 建议字段（草案；以修复后脚本的解析器为准，尚未创建）

Strategy 修复 P1-1 后，解析器应要求以下字段。Arch 复审时用实测 sha 填入：

```
format=quantlab_run_auth_v1
version=tie_sens_v1
signed_by=arch
signed_et=<用 date 实测的 ET 时间>
allow_full=true
allow_smoke=false
script_sha256=<修复后 research/strategy_tie_sensitivity_prereg_v1.py 的实测 sha>
prereg_sha256=<修订后 docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md 的实测 sha>
dep_ts_sha256=912fb00794ae3a1119633fa9521cd1dae8f7f547c055c13be043a05d752c0e8e
dep_lr_sha256=fed36cf2567190d31b64dd1b28c6cdfc52f757ea4e514a52b2372ed98b8c1960
dep_hx2_sha256=3f7f75c31611de6ab066d1bd2961cae3214aad26cfe144ad1641b305e49532c2
ref_weights_60w_sha256=<b4_leg_review/weights_B4_50_25_25_60w.parquet 实测>
ref_weights_100w_sha256=<b4_leg_review/weights_B4_50_25_25_100w.parquet 实测>
out_dir=output/strategy_hiliq/tie_sens_prereg_v1
```

以下是人读字段，脚本忽略：scope=、basis=docs/v2/ARCH_TIE_SENSITIVITY_PREREG_REVIEW_ZH.md、not_authorized=paper_change,rule_adoption,sealed_window。

---

## rev2 复审（2026-10-18 00:57 ET，box `date` 实测）

- **范围：** 只读审计。没有运行脚本的正式模式或 smoke，没有加载行情，没有回测，没有创建 .ok。
- **跑过的东西：**
  - Strategy 的单测（只用临时文件）；
  - 我自己的负面测试，在 /tmp 临时目录中进行，结束后已删除。
- **输出目录：** output/strategy_hiliq/tie_sens_prereg_v1/ 仍不存在。

### rev2 结论：PASS（可以建 .ok）

上一轮的 P1-1～3 和 P2-1～5 都已在代码中落实。剩下 1 条 P2 和 3 条 P3，都不阻塞。

### 1. sha 核对（全部自己重算）

| 对象 | 实测 | 在 git e7b240d 中 |
|---|---|---|
| 预注册 STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md | 0af0aa1059cbb9a2cb830028a47f5215f2657dbc48d203d3268c95b9215b5224 | 一致 |
| 脚本 strategy_tie_sensitivity_prereg_v1.py | abef35f4d8422b6c4caa1a9551d5b62c36ae0349b843776739d0591c2b89f587 | 一致 |
| 审计文档 STRATEGY_CAPADV_TOPN_TIE_AUDIT_ZH.md | 00b7941b37d1facd003f65d1dfe223bf53dff23511c171d54b1b7fc3c0b81beb | 一致 |
| 依赖 ts / lr / hx2 | 912fb007… / fed36cf2… / 3f7f75c3… | 未变，一致 |
| 审计 CSV | 6f80fb083a60bed98ecf656448d0b8b9f57902b7736f66673510c017ffd782c2 | 一致 |
| 单测 .py / .out.txt | f36f375f… / b309e202… | 一致 |

**git 与 rev1 的 diff：**
- e7b240d（00:55:09 ET）是这些文件**第一次**进入 git，共 11 个文件，全部是新增。
- rev1（e237e919 / 8993e643）从未提交过，也没有副本，**无法用 git diff 对比**。
- 我改为用上一轮审计时打印的 rev1 脚本全文（61 行）逐段人工对照。结果与 Strategy 的描述一致，改动只有以下几处：
  - 新增结构化 .ok 解析和 14 个文件的 sha 钉死；
  - 新增 out_dir 校验；
  - 新增 SPLIT 变体；
  - 新增 VOID 处理；
  - 复现门放在所有 smoke 之前；
  - 指标扩充；
  - 实现了第 5 条 capadv-only 比对；
  - 新增 flags 输出。
- **没有变的部分：**
  - PROD、CODE、ADV、RAND 的定义；
  - 种子固定为 1–20；
  - 判读阈值：p10/p90 区间，5pp。

### 2. 逐条核对（看代码，不只看文档）

| 原问题 | 落实情况 |
|---|---|
| **P1-1 .ok 严格解析** | ✅ parse_run_auth：只解析 `^[a-z0-9_]+=value$` 的行；缺字段、空值、重复字段都拒绝；布尔值只接受小写 true/false，没有默认值；sha 必须是 64 位小写十六进制。enforce_run_auth：必须 allow_full=true、allow_smoke=false、out_dir 精确匹配；对 14 个文件运行时实测 sha，不符或文件缺失即拒。全部用 SystemExit，脚本里 `assert` 为 0 处。 |
| 14 个钉死文件 | 脚本本身、预注册、ts、lr、hx2、参考权重 60w 和 100w、审计 CSV、capadv_only_pos_weights、capadv_x2 BOOK nav（60w、100w）、3 个 N1 腿 parquet。覆盖了要求的全部文件，还多了 capadv 参考 nav 和 3 个腿 ✅ |
| 输出目录 | ✅ OUT_REL 硬编码；.ok 的 out_dir 必须与它相等；check_out_dir 要求目录不存在或为空目录（是文件也拒）。 |
| **P1-2 PROD 复现门** | ✅ 先构建全部权重，再比对。在第一次 smoke 之前，要求两档行集合完全相同（outer merge 且 indicator 全为 both），并且 max\|Δw\| == 0.0（严格等于 0），否则 void。上一轮我做的纯权重比对实测为 0，预期可以通过。 |
| **P1-3 禁止事后选规则、不改纸面** | ✅ 预注册 §4 第 6、7 条已写明。SELECTABLE=() 只是声明，写进 meta，代码里没有可以“采用”的路径（见 P3-r2-1）。 |
| **P2-1 SPLIT** | ✅ select_split：权重严格大于第 N 名的保留原权重；跨越第 N 名的并列组整组保留，每只按 slots/len(组) 缩放。所以 SPLIT 选出的权重合计等于 Top-N 的合计，调用方按腿预算归一后 Top-N 以外的部分不受影响；没有并列跨越时与 Top-N 相同。单测 3 例覆盖了跨越、不跨越、全部等权。 |
| **P2-2 指标** | ✅ 记录 cagr、mdd、calmar、sharpe、win_daily、win_monthly、cost_pct_initial、fill_ratio、年化单边目标换手、平均持股数；按 RAND 分布报告分位，以及 PROD、CODE、ADV、SPLIT 所处的百分位。 |
| **P2-3 审计 CSV** | ✅ CSV 的 sha 已钉死；零效应前提用 if 判断，不满足就 void（并要求 35 行）。 |
| **P2-4 第 5 条 1e-6** | ✅ 对 \|ΔCAGR\| 和 \|ΔMDD\| 分别检查，>1e-6 即 void，参考 nav 的 sha 已钉死。 |
| **P2-5 失败作废与阈值披露** | ✅ smoke 失败、nav 缺失、指标缺失或非有限值、复现门失败、零效应前提不成立，都会写 VOID.md 并退出；summary.json 只在最后才写。5pp 阈值是看过结果后设定的，已在 §4 第 3 条披露。⚠️ 残余问题见 P2-r2-1。 |
| 阈值和种子 | ✅ SEEDS=range(1,21)，VARIANTS 固定 24 个；flags 仍按 [p10, p90] 和 >0.05 判断，没有变化。 |

### 3. 单测与负面测试

- Strategy 单测：**60/60 PASS**，加 `python -O` 运行同样 60/60。
- 我用真实的 14 个文件和临时 .ok 做的负面测试：

| 情形 | 结果 |
|---|---|
| 正确的 .ok | ACCEPTED |
| 文件开头带 BOM | REFUSED（format 字段不被识别） |
| 重复键 | REFUSED |
| 缺 allow_smoke | REFUSED |
| `allow_smoke = false`（等号两侧有空格） | REFUSED（按缺字段处理） |
| 腿文件 sha 错误 | REFUSED |
| `# allow_full=true`（注释行） | REFUSED |
| 行尾带注释 | REFUSED |

### 4. §6 .ok 草案中 Strategy 自填的 sha

我逐一按 PINNED 路径实测了全部 13 个自填值，**全部一致**：script、ts、lr、hx2、ref 60w/100w、audit_csv、capadv_pos（ff27f279…）、capadv_ref_nav 60w/100w（c16638ca… / aba50300…）、3 个腿（3b288c83… / 6bb3b3f3… / c4b93255…）。

prereg_sha256 由 Arch 实测填入：0af0aa10…5224。

### 5. 残余问题（不阻塞）

- **P2-r2-1：** 只有主动调用 void() 的失败点会写 VOID.md。以下情况都不会写：
  - 非 SystemExit 的异常，例如构建或 pandas 报错；
  - kill；
  - 内存超限被人工终止。

  不过 summary.json 只在最后写，部分结果在技术上无法以“完成”状态出现。**操作规则：** 只要没有 summary.json，整次运行一律视为 VOID，由 Strategy 或 Arch 手动补写 VOID.md。建议以后改为 try/except BaseException 统一调用 void()；本轮不要求修改。
- **P3-r2-1：** SELECTABLE=() 只是声明，约束力来自预注册 §4 第 6、7 条和流程，而不是代码。
- **P3-r2-2：** check_out_dir 没有排除符号链接。目前 output/strategy_hiliq/ 下不存在该目录，风险很低。
- **P3-r2-3：** 单测会在 /tmp 留下 tiesens_* 临时目录，不影响结果。

### 6. .ok 文本草案（未创建文件；signed_et 由 Arch 用 date 实测填写）

```
ARCH RUN AUTH tie_sens_v1 — QuantLab Arch
format=quantlab_run_auth_v1
version=tie_sens_v1
signed_by=arch
signed_et=<用 date 实测的 ET 时间>
allow_full=true
allow_smoke=false
live=false
promotion=false
scope=只限 X2 并列敏感性，仅作披露，不改纸面 B4
basis=docs/v2/ARCH_TIE_SENSITIVITY_PREREG_REVIEW_ZH.md
not_authorized=paper_change,rule_adoption,sealed_window
out_dir=output/strategy_hiliq/tie_sens_prereg_v1
script_sha256=abef35f4d8422b6c4caa1a9551d5b62c36ae0349b843776739d0591c2b89f587
prereg_sha256=0af0aa1059cbb9a2cb830028a47f5215f2657dbc48d203d3268c95b9215b5224
dep_ts_sha256=912fb00794ae3a1119633fa9521cd1dae8f7f547c055c13be043a05d752c0e8e
dep_lr_sha256=fed36cf2567190d31b64dd1b28c6cdfc52f757ea4e514a52b2372ed98b8c1960
dep_hx2_sha256=3f7f75c31611de6ab066d1bd2961cae3214aad26cfe144ad1641b305e49532c2
ref_weights_60w_sha256=eeb4804ea350cc059093a4c7a5a9ba4ebc809b9928005bc1e0b2cc5bbd004bd2
ref_weights_100w_sha256=21da88d21262f891662c2611fa5f7249821e0746accf95c0c9db466d6238f19b
audit_csv_sha256=6f80fb083a60bed98ecf656448d0b8b9f57902b7736f66673510c017ffd782c2
capadv_pos_weights_sha256=ff27f279824d528e50d7ed6f03fb7d61b3036561af5a8b5b0d7801dae31d954b
capadv_ref_nav_60w_sha256=c16638ca3cf2c9f14cc9317d2e49dae49c565a9f91ea8c783aea3b42588ab16f
capadv_ref_nav_100w_sha256=aba50300f4e7032fd335503911e3239526bb9475def39eec2b1471d91d4ac1f1
leg_capadv_sha256=3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
leg_ee_sha256=6bb3b3f3160eafce410079ac49203faed609f9d722a55b9ef6f15c82af6d69e0
leg_ii_sha256=c4b93255b694adb9b0484e55413abf80072be1e48d750e25a39dc4e37917b5e2
```

**格式注意：**
- 使用 UTF-8 无 BOM；
- 每行 key=value，等号两侧不留空格，行尾不加注释；
- live、promotion、scope、basis、not_authorized 不在解析器的必填清单里，会被忽略，仅供人读；
- 第一行是标题文字，会被忽略。

建 .ok 前须确认：输出目录仍不存在，且 14 个文件的 sha 没有变化。
