# 预注册：B4@HI_LIQ / capadv-only 并列打破敏感性 v1（rev2，未运行，等 Arch .ok）

- 负责人：QuantLab Strategy；受主 Agent 委派。rev1 写于 2026-10-18 ET（sha e237e919…）。rev2 按 Arch 审核 `docs/v2/ARCH_TIE_SENSITIVITY_PREREG_REVIEW_ZH.md`（结论为有条件通过）修订，修复了 P1-1/2/3、P2-1~5，并记录了 P3。
- 状态：**DRAFT_FOR_ARCH_RECHECK**。**未运行。**rev2 期间只做了静态检查：py_compile、读文件、sha256，以及对临时文件做的纯函数单元测试 60/60（`research/tests_tie_sens/`）。没有加载行情数据，没有计算收益。
- 运行门控：结构化 `output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok`，**只能由 Arch 写**，格式见 §6。文件缺失或任一字段不符，脚本就拒跑。
- **披露（看过结果之后才写）**：本预注册写于**已看过中止批次部分结果之后**（`docs/v2/STRATEGY_CAPADV_TOPN_TIE_AUDIT_ZH.md` §4：v0 已丢弃；v1 部分结果 60万 n=15、100万 n=15 含 RAND15_100w；未经 .ok；主 Agent 裁定结果不作废、仅作描述）。种子数 20 在中止批次开跑时已经定下。**§4 第 3 条的 5pp 阈值是在看过 60万档 p90−p10≈6.8pp 之后才设的**，可以预见会触发，因此只作为加注阈值，不作为证据。
- 横幅：研究级；live=false；promotion=false；不动纸面轨、FROZEN_CONFIG、纸面产物；不改 B4 权重或 λ；不跑密封窗。

## 1. 对象
| 臂 | 定义 |
|---|---|
| B4@HI_LIQ | N1 腿：capacity_adv 195620 / earnings_event 202822 / insider_increase 202928；诊断版 50/25/25；逐腿取前 N（60万 N=6，100万 N=10），先按腿股票预算归一，再做组合单票 6% 截顶（溢出转 510300），再做申万一级 ≤25%（股票袖套）迭代截顶。流程和 `strategy_b4_hiliq_leg_review.py::build` 完全相同，只替换 selector。**参考权重**（b4_leg_review/weights_B4_50_25_25_{60w,100w}.parquet）由 **PROD** 规则生成，Arch 实测 PROD 逐行复现（max\|Δw\|=0）。CODE 不能复现（60万 max\|Δw\|=0.142，10804 行）。 |
| capadv-only@HI_LIQ_V1.1 | 整条腿 195620（25 只 + 20% 510300），**不做 Top-N**。零效应前提依据**钉死 sha 的**审计 CSV（35/35 调仓日重复分数为 0，并与生产腿一致），所以只跑一次 PROD。结果须与现有 capadv_x2 一致（第 5 条）。 |
- 窗口：X2 2024-06-03→2026-10-09（样本内，只作诊断）。资金档：600000、1000000。引擎：book-smoke ExecConfig.strategy_v1（BOOK，sleeves stock=1，`--windows X2`），串行运行。

## 2. 并列打破变体（固定 24 个；**事后不得增减**；种子数**不扩**）
所有变体的主键都是腿权重降序，只有次级键不同。
| 变体 | 精确定义 | 身份 |
|---|---|---|
| **PROD** | **现行 N1 规则**：`pandas.Series.sort_values(ascending=False).head(N)`，默认 quicksort（numpy introsort，不稳定），不取整；Series 索引是腿 parquet 当日行序。N1 事件腿的行序来自构建器 `all_insts = set(...)` 的迭代顺序（依赖 PYTHONHASHSEED，已固化在文件中，跨日不变）。**= 参考权重 = 头条 21.43%/13.77%** | 现行 |
| **CODE** | `np.lexsort((code_rank, -round(w,12)))`，并列时按代码升序。≈ 字母序 = **已隔离旧腿和纸面 B4（事件腿文件按代码排序）的实际效果**；**不是** N1 现行规则 | 历史对照 |
| **ADV** | 并列时按 20 日均 ADV（float_mktcap×turnover_rate/100，rolling(20, min_periods=10).mean() 后 shift(1)）降序。缺失记 0；ADV 也相同时，lexsort 稳定，退回文件行序（P3-2） | 备选披露 |
| **SPLIT** | 权重严格大于第 N 名的保留原权重。若第 N 名处的并列组跨过截断，**整组全部保留**，每只的权重 × (剩余名额 / 组大小)，即剩余名额的预算在组内等分，持股数可以多于 N。之后照常按腿预算归一（`select_split`）。这是唯一不做任意选择的无偏基准。持股数和成交率单独披露 | **只作基准披露，永不可选** |
| **RAND1–RAND20** | 并列时按持久随机优先级 `int(md5(f"{seed}|{leg}|{instrument}").hexdigest()[:12],16)` 升序，seed = 1,2,…,20（整数）。同一名字跨日优先级不变 | 分布 |
- 种子数固定为 20（中止批次开跑时定下，理由是 p10/p90 各约有 2 个观测点）。**本预注册不扩种子。**如果以后要扩到 50，只能在运行前以精度为理由决定，不得参照已看过的结果。结论须注明 n=20 下 p10/p90 的插值精度有限（P3-3）。
- P3-1：keyed 变体对权重取整 12 位，PROD 不取整，差异 <1e-12，可以忽略。
- 共 24 个变体 × 2 档 = 48 次 B4 smoke，另加 1 次 capadv-only（两档同跑）。

## 3. 指标（全部落盘到 summary.json）
CAGR（244 日，nav 首末）、MDD、Calmar = CAGR/|MDD|、Sharpe、日胜率、月胜率（`nav_metrics`），成本占初始资金、成交率（book_smoke_summary BOOK），年化单边换手（由目标权重文件计算：0.5×Σ|Δw| 日均 ×244，限 X2），平均股票持股数。每档对 RAND1–20 报告以上每个指标的 n、中位数、p10、p25、p75、p90、最小、最大（numpy 线性插值），以及 PROD、CODE、ADV、SPLIT 在其中的百分位（严格小于该值的比例）。

## 4. 解读规则（事先固定）
1. 某档 **PROD（现行规则）或 CODE** 的 CAGR 落在 RAND 的 [p10, p90] 之外，就把该档 B4 头条标注为「**对选择规则敏感**」。PROD 的百分位作为「现行规则所处位置」报告。
2. 不论第 1 条结果如何，Leo 的 B4 A–D 选项材料一律引用 **RAND 中位数 [p10, p90]**。PROD、CODE、ADV、SPLIT 只作为分布中的点披露，不作为头条。
3. 某档 RAND 的 p90−p10 > 5pp CAGR，就标注为「头条不稳定」，结论表述降级。**（此阈值设于看过 60万档约 6.8pp 之后，见开头披露。）**
4. ADV 和 SPLIT 只作披露。
5. capadv-only 与现有 capadv_x2 BOOK（`output/strategy_hiliq/capadv_x2/aum_{600000,1000000}/X2/BOOK/nav.csv`，sha 见 §6）比较，|ΔCAGR| 和 |ΔMDD| 都须 ≤1e-6，否则整次作废（脚本内实现）。
6. **禁止事后选规则**：任何变体，包括 SPLIT、ADV、CODE 以及**表现最好的 RAND 种子**，都**不得**因为本次结果被选为新的选名规则（脚本 `SELECTABLE=()`）。
7. **纸面 B4 永不因本次结果改变**：无论结果如何，纸面 B4 和诊断版规则都不改。如果要修改，必须同时满足：主 Agent 裁定、Leo 决定、走冻结流程、新的预注册，并用 X2 之外的前瞻数据检验。
8. 本次运行只提供不确定性区间；B4 如何定义由 Leo 决定。

## 5. 运行与失败处理
- 脚本：`research/strategy_tie_sensitivity_prereg_v1.py`，sha256 **abef35f4d8422b6c4caa1a9551d5b62c36ae0349b843776739d0591c2b89f587**
- 静态测试：`research/tests_tie_sens/test_guards_tie_sens_v1.py`（sha256 f36f375f…），结果 60/60 PASS，输出见 `.out.txt`。只用临时文件，不调用 main()。
- 执行顺序（任何一步失败都 `raise SystemExit`，不用 assert）：
  1. 解析 .ok
  2. 实测 14 个钉死文件的 sha，与 .ok 比对
  3. 校验 out_dir（必须是新目录或空目录）
  4. 检查审计 CSV 的零效应前提
  5. 构建全部 48 份权重（不算收益）
  6. **复现门**：PROD 两档权重与参考权重的行集合必须相同，且 max\|Δw\| == 0，否则整次中止，**在任何 smoke 之前**
  7. 串行 smoke
  8. capadv-only 第 5 条比对
  9. 写 summary.json
- **作废规则**：任何一次 smoke 失败、nav 缺失或指标缺失，**整次运行作废**：写 `VOID.md`，不写 summary.json，**不报告部分结果**。
- 命令：`cd /workspace/QuantLab && /workspace/qlvenv/bin/python research/strategy_tie_sensitivity_prereg_v1.py`
- 输出目录：`output/strategy_hiliq/tie_sens_prereg_v1/`（当前不存在）。
- 预计：构建约 2 秒/变体；49 次 smoke，每次 14–32 秒；合计约 13–27 分钟。RSS：主进程 <1 GB（Arch 实测构建约 0.64 GB，另加 ADV 透视表）；book-smoke 子进程约 0.43–0.7 GB。任何进程超过 1.5 GB 时人工终止，并按作废处理。
- 中止批次的产物（`output/strategy_hiliq/topn_tie_audit/`，含 `_discarded/`）保留不动，**不得**并入本次结果。

## 6. .ok 字段规格（与 Arch §6 草案一致，并按 P1-1 补全；解析器 = `parse_run_auth`/`enforce_run_auth`）
规则：只解析 `^[a-z0-9_]+=value$` 的行，其余文字忽略。缺字段、空值、重复字段都拒跑。`format`、`version`、`out_dir` 精确匹配。`signed_by` 不区分大小写，必须为 arch。布尔值只接受小写 `true`/`false`，没有默认值。必须 `allow_full=true` 且 `allow_smoke=false`（本脚本没有 smoke 或部分运行模式）。sha 必须是 64 位小写十六进制，并与运行时实测值相等。
```
format=quantlab_run_auth_v1
version=tie_sens_v1
signed_by=arch
signed_et=<用 date 实测的 ET 时间>
allow_full=true
allow_smoke=false
out_dir=output/strategy_hiliq/tie_sens_prereg_v1
script_sha256=abef35f4d8422b6c4caa1a9551d5b62c36ae0349b843776739d0591c2b89f587
prereg_sha256=<本文件 rev2 的实测 sha，由 Arch 填>
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
- 钉死文件路径（key → 路径）见脚本 `PINNED`：审计 CSV = `output/strategy_hiliq/topn_tie_audit/capadv_leg_score_tie_by_rebalance.csv`（中止批次之前由只读重建打分脚本生成，现在钉死 sha，不重算）；capadv 参考 nav = capadv_x2 BOOK nav.csv。
- 人读字段（脚本忽略）：scope=、basis=docs/v2/ARCH_TIE_SENSITIVITY_PREREG_REVIEW_ZH.md、not_authorized=paper_change,rule_adoption,sealed_window。
- 脚本、本文件或任一钉死文件的 sha 有变化，授权即自动失效，需要 Arch 重签。不允许追加变体或种子。
