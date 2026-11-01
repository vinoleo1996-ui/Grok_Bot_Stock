# Arch 审核 r2：Data cs_panel 复牌重建 + D-2/D-3/D-4 修复（D-1～D-4）

- 审核人：QuantLab Arch｜写于 2026-10-18 01:34 ET（取证 01:24–01:32 ET，按 `date` 实测）｜只读审核：未改 Data 任何文件，未运行 Data 的任何脚本，未算任何叶收益 / IC。
- 取代：r1（01:10 ET，sha fa75e4ff…，写于恢复未完成时，P0-1「审核对象缺失」已不成立），原件归档在 `docs/v2/_archive/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_ZH.r1_fa75e4ff.md`。
- 独立复算脚本与结果：`docs/v2/audit/arch_cs_panel_resumefix_r2/`（resume_counts.py bec3dd16…、carry60.py da201880…、variants.py f2fd1f1b…、spike2018.py 402e2c05…；结果 resume_counts.json 9700c866…、variants.json 43bbcb87…）。按年分块读掩码，峰值 RSS 794MB（≤1.5GB）。carry60.py 是 Data 脚本 resume_flags() 的逐行拷贝，只用于量化回看窗口影响。

## 0. 结论

**CONDITIONAL —— P0=0，P1=6，P2=8，P3=4。本轮不写 `output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok`。**

不写 .ok 的原因：三个脚本都**没有 .ok 门禁**（不解析、不强制、不复算 sha，只要 `--execute` 就落盘），按要求优先补门禁，不接受「仅授权记录」形式；另外 P1-3/P1-4/P1-5 修完后三个脚本 sha 必然变化，现在钉 8eac523b / 34fd86fe / 0e89e688 没有意义。方向认可：根因、版本化新目录、掩码与旧面板只读、按年分块，这些都对；Data 自报的 2026 年 321 / 183 两个数我用独立代码逐数复现。

## 1. sha 核对（01:24 ET 实测，全部一致）

| 文件 | Data 报 | 实测 | mtime（EDT） |
|---|---|---|---|
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 3a7bb0cd…93b8 | 一致 | 01:23:13 |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | 50aaf043…15a5 | 一致 | 01:23:13 |
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py | 8eac523b…497b | 一致 | 01:22:03 |
| scripts/fix_sd1/build_suspend_flags_v2.py | 34fd86fe…6dfc | 一致 | 01:22:23 |
| scripts/fix_sd1/build_stock_delisted_v2.py | 0e89e688…8fac | 一致 | 01:22:44 |
| docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md（未送钉，仅记录） | — | 02fc06f6…15d9 | 01:23:51 |

输入（只读，供下一版 .ok 钉）：掩码 universe_mask_hiliq_v1.parquet c5433e80…b9af（与 Alpha .ok 一致）；v1 cs_panel 2018–2026：035d1f60…、b843a7bc…、e25a7e59…、bea54e54…、ad188dda…、6acf163e…、6d238ee3…、39568253…、4608d8bc…（2023–2026 与 Alpha .ok 一致）；float_mktcap 346d0dda…；sw_l1 89d4afa3…；stock_delisted v1 90c8934d…（与 SD1 规格所记 manifest 一致）；namechange_all 6b81ee0b…；delisted_daily e0db051e…；research/ai_cs_panel_build.py 66cfcb81…。

方案文档头写「01:3x ET」，但 mtime 是 01:23:13，时间戳是占位符（P3-1）。诊断文档在恢复清单里记的是 cf953ada…，01:23:51 被重写成 02fc06f6…，且仍保留「草稿脚本未验证、未定稿（它依赖的 v1 cs_panel 已丢失）」这句过期表述（P3-1）。

## 2. 代码审核

### 2.1 PIT
- 掩码 suspended = suspend_d 当日 S（盘前可知）| ~bar_prev（T−1 成交额），v1 的 hiliq / fulla 只用 ≤T 盘前信息。
- `is_resume_day` 用到 vol(t)>0，t 16:00 才知道；`hiliq_carry` = is_resume_day ∧「复牌前最后一个有成交日 in_universe」，后半段只用 ≤T−1 信息，前半段同样是 t 收盘信息。两列都**不是** T−1 可知，只能作**记账专用**（booking-only）。这符合裁定，前提是不进入当日选股——见 P1-3：现脚本让 is_resume_day 进入了 fulla，违反这一点。
- `ret`、`ret_on` 用当日 close/open 除以 pre_close（Tushare pre_close 是除权后的停牌前收盘），只用于事后记账，合规。
- 引擎在 t 盘前判「当日不新买」，应当用 suspend_flags_v2.resume_announced（t 09:00 可知）；用面板 is_resume_day 只能在 t+1 以后使用或作披露。另外 v1 掩码在复牌日本来就是 suspended=True、in_universe=False，所以 HI_LIQ 选股侧的「复牌日不新买」已经自动成立，is_resume_day 闸门和它一致，没有冲突。

### 2.2 列定义能否实现裁定
- 叶评价消费方（如 leaf_selfcheck_v3 `_pool_panel`）用 `P = cumprod(1+ret)`，停牌期没有行，P 为 NaN；补回复牌日行之后，跨停牌的前瞻收益会把复牌跳空计入。持仓权重来自叶权重文件，不来自面板，所以「停牌期权重保留、复牌日记账」**可以实现**。
- 但 leaf_selfcheck_v3 用 `fulla(d)`/`hiliq(d)` 作 d 日池掩码。现脚本 fulla_v2 = fulla ∨ (is_resume_day ∧ 非ST ∧ 非次新 ∧ adv20≥3e6)，于是复牌日股票进入 FULLA 池（002445.SZ 2026-03-09 fulla=True），改变了 FULLA_V1 池的定义 → P1-3。
- 面板没法表达「停牌中持有」，引擎要靠「掩码 suspended 且无行」识别停牌日。建议补回行加 `prev_traded_date`（复牌前最后有成交日），便于引擎把复牌收益挂回停牌前持仓（P2-6）。

### 2.3 其他代码问题（详见 P 清单）
- `--fixes none --check-v1` 只把 v1_frame_equals 写进 stats，**不中止**；v1 年文件不存在时静默跳过（`rows_v1=None`）。resume 模式下 v1_rows_missing / v1_value_mismatch 同样只记录不断言。
- OUT 用 `mkdir(exist_ok=True)`，不查空，会覆盖；中途 RSS/MemAvailable 退出时，已写年份留在目录里却没有 manifest。MemAvailable<2GB 写的是「暂停」，实际是 `sys.exit`。
- hiliq_carry 的回看窗口是「年初−60 天」，跨年长停牌会漏标。实测只影响 2020 年 1 行（60d 185 vs 无界 186）。
- is_resume_day 把「盘中 S（有 timing）且前一日有成交」的日子也标成复牌：掩码脚本第 95 行 `_suspend_set` 收所有 S 记录，不区分 timing。

## 3. 计数核对（独立代码，按年分块）

| 年 | 掩码定义 is_resume_day | 其中盘中S标成复牌 | 真复牌∧合格(=2865口径) | 脚本实际补回(合格∪carry) | hiliq_carry |
|---|---|---|---|---|---|
| 2018 | 4677（含 2018-01-02 首个数据日 3252 行伪复牌） | 111 | 632 | 766 | 296 |
| 2019 | 779 | 149 | 402 | 458 | 214 |
| 2020 | 972 | 240 | 328 | 363 | 186（Data 60d 185） |
| 2021 | 1040 | 218 | 331 | 364 | 145 |
| 2022 | 813 | 114 | 278 | 309 | 151 |
| 2023 | 560 | 84 | 160 | 177 | 63 |
| 2024 | 412 | 38 | 156 | 201 | 110 |
| 2025 | 660 | 36 | 330 | 401 | 273 |
| 2026 | 509 | 30 | 248 | **321** | **183** |
| 合计 | 10422 | 1020 | **2865** | ≈3360 | 1621 |
| 2024 起 | 1581 | 104 | **734** | 923 | 566 |

对账结论：
1. **2865 / 734 逐数复现**：口径是「掩码 suspended ∧ 当日有成交 ∧ 非全天S ∧ 当日无 S 记录（排除盘中 S）∧ 非ST ∧ 非次新 ∧ adv20≥3e6」，即「应补进 fulla 的真复牌」。
2. **2026 年 321 / 183 逐数复现**。321 = 248（真复牌且合格）+ 1（盘中S被当复牌且合格）+ 72（不合格、只因 hiliq_carry 保留）。所以 321 与 734 不是同一口径：脚本按自身逻辑会补 2018–2026 年约 3360 行、2024 年起 923 行，不是 2865 / 734。
3. **4971 无法逐数复现**。最接近的是 R 记录口径：掩码复牌行中带 R 记录的有 4962 行，R∧当日有成交 4977–4978。按掩码口径数，真复牌（剔除 2018-01-02 伪复牌）是 6150。4971 和 2865 不在同一基数上，「4971 次中应补 2865」这句表述须更正（P2-3）。
4. 「X2 窗口 702 次」本轮未复核。

**抽查（轻读 raw daily / suspend_d / 掩码 / v1 面板）**

| 事件 | raw | 停牌前最后成交 | 掩码 | v1 行 | 独立复算标志 |
|---|---|---|---|---|---|
| 002445.SZ 2026-03-09 | R；close 3.06 / pre 2.78 → ret 0.10071942（=Data +10.07%） | 2026-02-12（停 10 个交易日） | suspended=T | 无 | resume=T，carry=T |
| 002090.SZ 2025-07-23 | R；ret −7.859% | 2025-07-18（2 日） | suspended=T | 无 | resume=T，carry=T |
| 300658.SZ 2026-01-19 | R；ret +19.973% | 2025-12-31（10 日，跨年） | suspended=T | 无 | resume=T，carry=T |
| 603007.SH 2026-04-21 | R；ret −2.041% | 2026-04-17（1 日；04-17 前 st=T，复牌当日 st=F，即摘帽复牌） | suspended=T | 无 | resume=T，carry=F；现脚本因 t 日合格会让 fulla=T 并补回，P1-3 修正后不再补回 |
| 002445.SZ 2026-08-24 | R（timing 空）；vol 47,973.94；ret +10.131% | 2026-08-14（5 日） | suspended=T | 无 | resume=T，carry=T；与 Data「复牌、可交易」一致 |

suspend_flags_v2 的 485（R 439 / 盘中 S 34 / R|S 12）本轮未逐数复核（没运行 Data 脚本）。我按近似口径数出 2026 年 is_resume_day 576 行（Data 580，差 4 未对齐），其中约 125 行是**新股上市首日**（P1-5）。

## 4. 列裁定（证据未推翻，维持并细化）

- **叶评价收益记账用 `hiliq_carry`**（FULLA 口径用 P1-3 新增的 `fulla_carry`）：停牌期间持仓权重保留、不重新归一，停牌日收益为 0，复牌日按 close/pre_close 记入。这两列是记账专用，含 t 收盘信息，不得用于当日选股或池定义。
- **`is_resume_day` 只用于披露和「当日禁止新买入」闸门**；不进因子、不进选股、不作剔除条件。引擎在 t 盘前判断时用 `suspend_flags_v2.resume_announced`（t 09:00）。
- **`hiliq`、`fulla` 保持 v1 掩码原定义**：补回的行上两列都是 False，选股口径与 v1 逐位相同。
- 补回行只靠 `*_carry` 列进入面板。凡是「以行存在作池」的消费方，必须改为按 hiliq/fulla 过滤（P2-6）。

## 5. P 清单与必须的修改

**P0：无。**

**P1（全部修完、重报 sha，Arch 复核后才发 .ok）**
- **P1-1 三个脚本加 .ok 门禁**（仿 research/strategy_tie_sensitivity_prereg_v1.py 的 parse_run_auth / enforce_run_auth / check_out_dir）：
  - 新增必填参数 `--arch-ok PATH`，**所有模式都要过门禁，包括 dry-run**。
  - 只解析 `^[a-z0-9_]+=value$` 行；字段重复、缺失或为空都 SystemExit。
  - 校验 format=quantlab_run_auth_v1、version=cs_panel_resumefix_v1、signed_by=arch、live=false、promotion=false，以及 allow_full / allow_smoke / allow_dryrun 三个字段都精确为 true 或 false。
  - 开工前复算下列 sha，与 .ok 比对，不一致即拒跑：三个脚本自身、两份方案、掩码、v1 cs_panel 各年、float_mktcap、sw_l1、stock_delisted v1、namechange_all、delisted_daily。
  - 校验 `step` 在 serial_order 中，且前序步骤的回执 / manifest 已存在、sha 与 .ok 一致。
  - 校验 out_dir 与 .ok 完全相同且为空目录（目标文件已存在即拒）。
  - 必填键名见 §6，脚本里的 AUTH_REQUIRED 须与之逐字相同。
- **P1-2 新旧一致性改为运行内断言**：
  - `--fixes none` 强制带 `--check-v1`，跑 2018–2026 **全部年份**。
  - 每年断言 `DataFrame.equals(v1)` 为真，且 `pa.Table.from_pandas(m,preserve_index=False).equals(pq.read_table(v1))`（schema 含 dtype 一致）也为真。
  - v1 年文件不存在、任一年不等，立即非零退出，不写任何文件，后续步骤不得开始。
  - 执行模式写出 fixesnone 文件后，逐年记录两边文件 sha 和 bytes_equal。bytes_equal=false 的年份，须在回执里用 parquet 元数据 diff 证明差异只在 created_by / pandas 元数据。
  - resume 模式逐年断言 v1_rows_missing_in_v2==0 且 v1_value_mismatch==0，否则中止。
- **P1-3 fulla 恢复 v1 定义**：
  - 删掉 `m["fulla"]=m.fulla|(m.is_resume_day&elig)`。
  - 新增 `fulla_carry` = 补回行 ∧ 复牌前最后有成交日 fulla_v1=True（只用 ≤T−1 信息判断「当时在池」）。
  - keep = v1_keep ∨ hiliq_carry ∨ fulla_carry。
  - 新增 `row_origin`（'v1'|'restored'），补回行的 hiliq、fulla 都为 False。
  - 按新口径重报各年补回数（会与 321 不同）。
- **P1-4 退市数据缺来源的 56 只**：
  - 保留 needs_manual_source=True，并新增 `sd1_delist_type_default`：没有公告来源的一律记 UNKNOWN，SD1 按 FORCED 处理，即 delist_forced_recovery 默认 0、敏感性 0.3 / 0.7。
  - 只有补上公告来源（公告编号、日期、URL）后，才可改记 MERGER_SWAP / CASH_OUT，并走规格 §3.5 的对价或 MA_FALLBACK 路径。
  - manifest 和回执逐只列出这 56 只。delist_events_v1 的 type 映射也按此执行。
- **P1-5 suspend_flags_v2.is_resume_day 剔除新股首日并统一定义**：
  - 现 `newres = cur−prev` 会把上市首日（以及前一日零成交）当成复牌，2026 年约 125 行。
  - 剔除 list_date==t 以及此前从无成交的代码。
  - 「前一交易日无 bar」改按 amount>0 判断（与掩码 bar_prev 同口径），并与 cs_panel 的 is_resume_day 共用同一函数、同一定义；文档与代码要一致。
- **P1-6 落盘原子化、不覆盖**：
  - 三个脚本都先写到 `<out>/.staging_<ts>/`，全部年份成功、manifest 写完后才 rename 成正式目录或文件。
  - 中途退出时写 VOID.md，不留下半成品。
  - 目标存在即拒；ind_names.csv 须与 v1 的同名文件 sha 一致，并记入 manifest。

**P2**
- **P2-1（流程）**：三个 dry-run（cs_panel 2026 两次、suspend_flags 2026、stock_delisted 全表）都在没有 Arch .ok 的情况下运行，违反团队规则「无 Arch .ok 不得运行任何形式的任务」。dry-run 也须有 dev .ok（allow_dryrun=true）。记为 Data 的 P2 流程反馈；本次 dry-run 数字只作参考，不作证据，以授权后的正式回执为准。
- **P2-2 串行与回执**：
  - 顺序为 D1a（`--fixes none --check-v1 2018 2026`，写 panel_cache_v2_fixesnone）→ D1b（`--fixes resume 2018 2026`）→ D2（suspend_flags_v2 2018–2026）→ D3D4（stock_delisted_v2）。
  - 每步各写一份 manifest 和回执，前一步回执的 sha 由后一步的门禁检查。
  - 排在 fund_portfolio、broker_recommend 合并之前，并且不得与其他研究任务并行（启动前查 ps）。
- **P2-3 计数口径**：回执逐年列出 §3 表里的各列，写清每个数的定义。更正「4971 次中应补 2865」：2865 / 734 是「真复牌 ∧ 合格」口径，4971 是 R 记录口径（Arch 复算 4962–4978，未逐数对上，须给出定义并闭合）。2018-01-02 首个数据日的 3252 行伪复牌，须置 is_resume_day=False（第一个交易日没有 T−1 可比），并单列披露。
- **P2-4 盘中 S 不算复牌**：is_resume_day 增加条件「前一交易日无成交 ∨ 当日有 R 记录」。盘中 S 且前一日有成交的行，只标 intraday_halt；需要记账时由 carry 列保留，记账原因写 intraday_halt。实测历年 1020 行被误标，其中约 47 行进入补回集（2026 年 1 行）。
- **P2-5 carry 无界回看**：用跨年状态，记录每只股票最后一个有成交、且非复牌日的 in_universe / fulla，替代「年初−60 天」窗口。断言：有历史成交的复牌行，hp 不得为 NaN。
- **P2-6 消费方说明与 prev_traded_date**：补回行新增 prev_traded_date 与 halt_sessions。方案「影响面」一节须写明：消费方必须按 hiliq/fulla 过滤，不得以行存在作池；记账专用列不得进入信号。
- **P2-7 002509 人工覆盖须引来源**：Arch 检索到候选来源，须 Data 亲自打开核对后写进 MANUAL_OVERRIDE 和 manifest：
  - 天广中茂公告 2020-053《关于公司股票终止上市的公告》（深证上【2020】442 号，2020-05-27 决定终止上市；原因是 2020-04-09 至 05-11 连续 20 个交易日收盘低于 1 元；自 2020-06-04 起进入退市整理期），见 http://disc.static.szse.cn/download/disc/disk02/finalpage/2020-05-28/9f3e0d5c-66cd-4ab0-b727-ed74438ea31a.PDF；
  - 摘牌公告 2020-094（整理期 30 个交易日，最后交易日 2020-07-17，07-20 摘牌）。
  - 新增 `delist_period_ann_date=20200527`、`override_source_verified`。
  - 核对之前，002509 的 needs_manual_source 置 True，整理期起点只能用于会计层，不得作 SD1 的 PIT 强卖触发。
  - 已有交叉证据：delisted_daily 中 2020-04-09 至 05-11 收盘全部 <1（0.69–0.99），整理期 30 个成交日，与公告一致。
- **P2-8 manifest 补全**：每份 manifest 记录所有输入 sha（同 P1-1 列表）、raw daily 和 suspend_d 文件清单的哈希，以及逐年 rows / rows_v1 / rows_added / 按 row_origin 和原因分列的补回数 / v1_rows_missing / v1_value_mismatch / v1_frame_equals / bytes_equal / rss_mb / sha256；另记 .ok 文件的 sha。

**P3**
- P3-1 方案文档「01:3x ET」改为实际时间；删掉诊断文档中「草稿脚本未验证、依赖已丢失」的过期句。
- P3-2 MemAvailable<2GB 时实际是退出，把文档里的「暂停」改成「中止」。
- P3-3 face_value_delist_flag 应只用整理期开始前的 20 个成交日计算。现在的算法把整理期收盘也算进去，所以 122 只的命中数偏高；这个标志只作披露，不影响改类结果，但须改正。
- P3-4 回执抽样补上本审的 603007.SH 2026-04-21（摘帽复牌，P1-3 修正后不再补回）和 300658.SZ 2026-01-19（跨年 carry）。

## 6. 下一版 .ok 的键结构（Data 门禁须逐字匹配；本轮未写）

```
format=quantlab_run_auth_v1
version=cs_panel_resumefix_v1
signed_by=arch
signed_et=<ISO8601 ET>
allow_full=true
allow_smoke=false
allow_dryrun=false
live=false
promotion=false
scope=D1_cs_panel_v2_resumefix_2018_2026_and_D2_suspend_flags_v2_and_D3D4_stock_delisted_v2_new_versioned_outputs_only
not_authorized=tier1_materialize_change,paper_mask_change,v1_panel_overwrite,mask_rebuild,leaf_eval,leaf_ic,engine_change,fund_portfolio_merge,broker_recommend_merge
serial_order=D1a_fixesnone_check,D1b_resume_execute,D2_suspend_flags,D3D4_stock_delisted
years=2018-2026
out_dir_d1a=output/ai_factory/panel_cache_v2_fixesnone
out_dir_d1b=output/ai_factory/panel_cache_v2_resumefix
out_dir_d2=data/v2/suspend_flags
out_path_d3d4=data/v2/ref/stock_delisted_v2.parquet
ruling_leaf_eval_booking=hiliq_carry_keep_weight_through_halt_book_resume_day_return
ruling_is_resume_day=disclosure_and_no_new_buy_gate_only
ruling_hiliq_fulla=v1_mask_definition_unchanged
ruling_carry_cols=booking_only_not_selection
plan_cs_panel_sha256=…
plan_sd_fix_sha256=…
script_cs_panel_sha256=…
script_suspend_flags_sha256=…
script_stock_delisted_sha256=…
mask_sha256=c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af
v1_cs_panel_2018_sha256=… （至 2026，共 9 个）
float_mktcap_sha256=346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef
sw_l1_sha256=89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c
stock_delisted_v1_sha256=90c8934dddc698f46075a20fe3d60309094919868c5e3a4bacc4d12c765f0603
namechange_all_sha256=6b81ee0b0d60d6d468910fb606ea8e4d448618c4e67fbd5337ffe0b0523fba5a
delisted_daily_sha256=e0db051eb9e39487076ce2a73f6a03866442660794281ccc25cc502dfcb4f2aa
```

tier1_materialize 本身的修改（第 66–72 行）另需一份 .ok，不在本次范围内；修改前 SD1 一律以 suspend_flags_v2 为准。

## 7. 下一步

Data 修完 P1-1 至 P1-6（P2-4 / P2-5 建议同批修，因为都改同一个函数），重报五个 sha 和逐条修改说明。门禁要附自测：缺 .ok、sha 不一致、out_dir 非空、allow_dryrun=false 时跑 dry-run，这四种情况都必须拒跑。Arch 复核后按 §6 写 .ok。live=false，promotion=false。
