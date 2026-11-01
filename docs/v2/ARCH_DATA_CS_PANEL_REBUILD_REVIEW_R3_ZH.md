# Arch 审核 r3：Data cs_panel 复牌重建 + D-2/D-3/D-4 修复复核

- 审核人：QuantLab Arch｜写于 2026-10-18 01:50 ET（取证 01:44–01:48 ET，按 `date` 实测）。
- 承接 r2：docs/v2/ARCH_DATA_CS_PANEL_REBUILD_REVIEW_ZH.md（530f53cd…2a62，本轮复算一致）。
- 只读审核：没有运行 Data 的三个构建脚本，没有改 Data 的任何文件。只跑了两样东西：Data 的纯合成单测 `scripts/fix_sd1/test_sd1_common.py`（先确认它不读真实数据，只在 /tmp 写临时文件）；以及 Arch 自己的探针 `docs/v2/audit/arch_cs_panel_resumefix_r3/carry_none_probe.py`（c963cd6d…）。探针逐行照搬 D1b 的补回循环、调用经 sha 校验的 ResumeState，只读 2018–2019 两年，峰值 RSS 399MB；结果在 carry_none_probe.json（17d9c0d8…）。

## 0. 结论

**WITHHELD —— P0=0，P1=1，P2=4，P3=6。本轮不写 `output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok`。**

r2 的 P1-1～P1-6 在代码里都已落实，门禁、断言、原子落盘的写法认可。但新增的 P2-5 断言范围写得过宽：D1b 在 2018-01-03 就会必然触发 VOID（见 P1-1），所以现在发 .ok 只会换来一次 VOID。修完之后 cs_panel 脚本的 sha 必变，.ok 也得重签。这一处修改很小，修完重报 sha，Arch 当轮就签。

## 1. sha 核对（01:44 ET 实测，全部一致）

| 键 | 文件 | 实测 | mtime（EDT）|
|---|---|---|---|
| plan_cs_panel | docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 5d0a0fb2…f0ac ✅ | 01:41:23 |
| plan_sd_fix | docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md | d0319476…9625 ✅ | 01:41:23 |
| script_cs_panel | scripts/fix_sd1/build_cs_panel_v2_resumefix.py | 29f66d98…a0e2 ✅ | 01:39 |
| script_suspend_flags | scripts/fix_sd1/build_suspend_flags_v2.py | 1b62bba1…6f0a ✅ | 01:39 |
| script_stock_delisted | scripts/fix_sd1/build_stock_delisted_v2.py | 1504209b…2a16 ✅ | 01:40 |
| （传递钉定）| scripts/fix_sd1/sd1_common.py | 91eb61b4…16ca ✅ | 01:39 |
| （不钉，仅记）| scripts/fix_sd1/test_sd1_common.py | fd497582…f1 | 01:40 |

**sd1_common 传递钉定属实**：三个脚本第 19–23 行、第 24–28 行、第 25–29 行都硬编码了 COMMON_SHA256=91eb61b4…，读字节、算全长 sha 之后才执行 `import sd1_common`，不一致即 SystemExit。脚本自身由 enforce_code 复算。

**数据输入**（01:44 实测，与 r2 §1 和 Data 清单一致）：
- 掩码 c5433e80…b9af；
- v1 cs_panel 2018–2026：035d1f60 / b843a7bc / e25a7e59 / bea54e54 / ad188dda / 6acf163e / 6d238ee3 / 39568253 / 4608d8bc，全长见附录；ind_names.csv 1ce86712…；
- float_mktcap 346d0dda…；sw_l1 89d4afa3…；stock_delisted v1 90c8934d…；namechange_all 6b81ee0b…；delisted_daily e0db051e…。

## 2. 门禁（P1-1 复核：通过）

`sd1_common.gate()` 的顺序：parse_run_auth → check_mode → enforce_code（5 个代码和方案文件）→ check_out → check_order → enforce_inputs（数据），与 Data 的说法一致；在 enforce_inputs 之前不读任何数据文件。
- 缺少 `--arch-ok`、或文件不存在：block。只解析 `^[a-z0-9_]+=` 行，键重复就拒；必填键缺失或为空就拒；FIXED 里的值逐字比对；not_authorized 必须是 9 项的超集；三个 allow_* 只接受 true 或 false；钉定 sha 必须是 64 位小写十六进制，用 file_sha256 分块复算全文。带 BOM 的首行匹配不上，会被当成缺 format 而拒跑；行内注释会让布尔值不合法而拒跑。
- check_mode：allow_smoke 必须为 false；--execute 要求 allow_full=true；dry-run 要求 allow_dryrun=true。**没有发现绕过开关**：没有环境变量、没有 force 参数，三个脚本都无条件调用 gate。
- check_out：目录型输出要么不存在、要么为空；D3D4 的三个目标文件只要有一个存在就拒；残留 `*.staging_*` 也拒。
- check_order：后序步骤已有产出，算乱序；前一步 RECEIPT 必须 step 匹配、status=PASS、ok_sha256 等于本次 .ok 的 sha，且 5 个 PIN_CODE 值逐一相同。
- 我用 Data 自己的 parse_run_auth / check_mode / enforce_code / check_out / check_order，以非运行方式校验了附录的 .ok 草稿：解析通过（47 键），dry 和 exec 两种模式都通过，代码 sha 一致，D1a 输出位置为空，D1a 无前序要求。草稿写在 /tmp，校验完已删除，没有落成 .ok。

**自测**（output/diag/arch_gate_selftest_20261018.txt）：5 种情况 × 3 个脚本共 15 条，全部 exit=1，审计钩子统计 data_files_opened=0。我读了 /tmp/sd1_selftest/harness.py：它用 sys.addaudithook 监听 open 事件，匹配 data/v2、panel_cache、universe_mask、.parquet，方法可信。case2 的消息结尾是「!= 」后面为空，原因是 harness 把消息截到 160 字符，不是授权值为空。合成单测我在本轮重跑过，ALL SYNTHETIC TESTS PASS，exit 0。

## 3. 一致性断言（P1-2：通过）

- D1a（--fixes none）：逐年要求 v1 文件存在，否则 void；`m.equals(v1)` 和 `pa.Table.from_pandas(...).equals(pq.read_table(v1))` 必须同时为真，否则 void。执行模式下逐年记录 sha、v1_sha、bytes_equal；不相等时记录 parquet 元数据差异（created_by、schema、kv）。
- D1b：逐年断言 v1 行缺失为 0、值改动为 0（V1COLS 八列，NaN 视为相等）、补回行的 hiliq 和 fulla 不得为真、rows = rows_v1 + restored，任何一条不满足都 void。

## 4. 列口径与 PIT（P1-3、P1-5、P2-4、P2-6：通过；P2-5 见 P1-1）

- `fulla |=` 已删除，fulla 按 v1 掩码定义重算。新增 fulla_carry、row_origin、restore_reason、prev_traded_date、halt_sessions。补回条件是 `~keep_v1 & (hiliq_carry | fulla_carry)`。
- carry 状态由 update_pool 只用「有成交且掩码未判停牌」的日子更新；当天的 carry 在当天 update_pool **之前**读取，所以只用 ≤T−1 的信息，合规。
- 603007.SH 2026-04-21：复牌前最后一个正常成交日 st=T，所以 in_universe=F、fulla_v1=F，carry 都是 F，不会被补回。**这一条只做了静态推导**：全年份探针被中断，没有用数据跑到 2026，以 D1b 回执的抽样为准。
- `resume_announced` 等于当日 suspend_d 的 R 记录，available_at_open 为 t 09:00（上海时间）。suspend_d 是盘前发布的停复牌公告，所以 PIT 成立。is_resume_day 和两个 carry 列的 available_at 都是 t 16:00，列表和文档都写明了只能用于记账或披露。
- ResumeState（sd1_common 第 190–224 行）逐条核对：
  - 候选是 `(vol>0) − 全天S`，再与 has_traded 取交集，所以新股首日和从未成交的代码被排除；种子是首日掩码 young=False 的代码。
  - first_done 保证首个数据日一律记 False。
  - 前一日判断用 prev_amt，即上一处理日 amount>0 的集合。
  - 盘中 S 的条件是 `c not in prev_amt or c in R`，所以前一日有成交且当天没有 R 的不算复牌。
  - state 是模块级全局对象，跨年延续，没有回看窗口。
  - info 在更新 has_traded 之前计算，给出 prev_traded_date 和 halt_sessions。
  - cs_panel 和 suspend_flags 都调用同一个类。

## 5. 落盘（P1-6：通过，残余风险见 P2-2）

Staging 写到 `<out>.staging_<ts>`，mkdir 用 exist_ok=False；commit 时目录做 rename，D3D4 逐个 rename 三个文件，rename 前再检查目标是否已存在。void 会删掉 staging、写 `<out>.VOID_<ts>.md` 再中止；dry-run 只中止、不写 VOID。guard 检查 MemAvailable<2GB 和 ru_maxrss>1500MB，触发就 void。ind_names.csv 必须与 v1 的 sha 相同，否则 void。

## 6. D-3/D-4 与 002509（P1-4、P2-7：通过）

- v1 的「疑似主动/吸收合并/私有化退市」类共 60 只（轻读 stock_delisted v1）。脚本先把命中面值规则的改成面值退市，其余记 UNKNOWN(缺公告来源)，needs_manual_source=True，sd1_delist_type_default=UNKNOWN，回收默认 0.0、敏感性 '0.0,0.3,0.7'。60 − 4 = 56，与 Data 的「4 只改类、56 只 UNKNOWN」相符；具体名单以回执为准。**提醒 Eng**：「UNKNOWN 按 FORCED 处理」只写在数据侧文档里，SD1 代码必须照此实现。
- 002509.SZ 轻读核对：
  - v1 记录：类别是合并/私有化类，delisting_period_start 为空、整理期天数为 0，last_trade_date=2020-07-17，delist_date=2020-07-20；namechange 只有天广消防和天广中茂两条，没有带「退」的名称。
  - delisted_daily 中 vol>0 的日子：2020-06-04 到 07-17 共 **30 个交易日**；06-04 之前最后 20 个成交日是 2020-04-09 到 05-11，收盘最高 0.99，全部低于 1 元；05-12 到 06-03 没有成交。
  - 这与公告 2020-053（深证上【2020】442 号：05-27 决定终止上市，06-04 起进入整理期）和摘牌日 07-20 完全吻合。按新规则，face_value_delist_flag=True，所以 002509 会从合并类改记为面值退市。MANUAL_OVERRIDE 只在 namechange 没有起点时生效，source_url 已写入，override_source_verified=True，needs_manual_source=False，delist_period_pit_usable=True，口径成立。PDF 原文本轮未重新打开，采信 Data 的核对，加上上述数据交叉证据。

## 7. 范围与冻结件（通过）

- 旧 cs_panel 9 个文件和 ind_names.csv 的 sha 与 Data 清单（2018 035d1f60 … 2026 4608d8bc）和 r2 记录一致；mtime 都是 01:14（恢复回写），之后没有被改过。
- 掩码 c5433e80 没动（mtime 01:07）。
- scripts/acquire/tier1_materialize.py 是 e9c89a6c，与清单一致（mtime 01:12，恢复回写）。两份方案都写明它不在本次范围，三个脚本都不 import 它，也不写它。
- 输出位置 panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、stock_delisted_v2.parquet（以及它的 .manifest/.receipt），还有对应的 staging 和 VOID 文件**都不存在**，自测 ③ 放的标记文件没有残留。/tmp/sd1_selftest/ 里还留着 harness.py 和 mkok.py，假 .ok 文件已删除（见 P3-4）。

## 8. 进程冲突（01:45–01:48 ET 实测）

- tie-sens PID 90241 已经退出。Alpha v4.1 regen（PID 133587，research/alpha_s8_errata_fullsleeve_b_v41.py，nice 19，RSS 约 1.19GB）01:45 还在跑，01:47 已经不在了。01:47:57 的 ps 里没有任何 research/ 进程。
- Data 的抓数进程：PID 94322（remaining_after_stk_surv.py）只写 data/v2/events/ 下的 report_rc 映射、fund_portfolio、broker_recommend，以及 tushare_raw/fund_portfolio_dh 和 tushare_raw/broker_recommend；PID 94403（relay_outage_backfill.py）是补拉守护，待办里还有 hsgt、sw、cyq、tier3 四个步骤，它的子进程 94466/94467（nightly tier3）只写 data/v2/tier3_daily。sw 步骤写的是 data/v2/sw_pit/，**不是**钉定的 sw_l1_pit/industry_members_sw_l1_tushare.parquet。**结论：这些进程不写任何重建输入**，可以并存；不过它们占用内存，重建时 guard 的 MemAvailable 检查照常生效。
- 提醒：raw daily 和 suspend_d 只登记了文件名清单的哈希，没有钉内容（P2-1）。nightly 的 daily_pull 和 tier1_pull 会往 tushare_raw/daily 写文件，所以重建期间不得运行 nightly 的 daily_pull、adj_factor、bars 这类步骤。

## 9. P 清单

**P0：无。**

**P1（修完重报 sha，Arch 当轮签 .ok）**
- **P1-1（r3 新增）P2-5 断言范围过宽，D1b 必然 VOID。** build_cs_panel 第 81 行写的是 `if isr and lh is None: ST.void(...)`。可 seed_listed 把首日 young=False、当天停牌的代码也算作「有过成交」，这些代码在数据里从来没有过「有成交且未停牌」的日子，复牌时 carry 状态必然为空。Arch 探针（照搬 D1b 循环）实测：**2018 年 217 行、2019 年 2 行会触发**，第一行是 000032.SZ 2018-01-03（同日还有 000790、002442、002697、600671、600859、601005）。真跑 D1b 会在 2018 年第二个交易日就 VOID。r2 的 P2-5 原文是「**有历史成交**的复牌行，hp 不得为 NaN」，不包括种子代码。修改要求：
  1. 断言只针对「数据内出现过正常成交日」的代码，即 last_h 存在。
  2. 种子代码首次复牌、且没有 carry 状态的，hiliq_carry=fulla_carry=False，不补回，按 v1 处理（不知道当时是否在池，从保守），另加 `carry_state='unknown_pre_data'`，或者用 restore_reason 区分。
  3. manifest 逐年记录这类行数（预期 2018 年约 217、2019 年约 2），回执单列披露，并抽样 3 只。
  4. test_sd1_common.py 补一个用例：种子代码停牌跨过首日后复牌，carry=(None,None) 时不中止。
  5. 方案 P2-5 一段同步改写。
  
  另外：探针显示 2018 年 fulla_carry 的补回数（990）远多于 hiliq_carry（296），这是 FULLA 口径更宽导致的，回执里要说明。

**P2**
- **P2-1 raw daily 和 suspend_d 没有内容钉定**：manifest 里只有文件名清单的哈希。D1a 的逐年 equals 能间接守住 v1 行的 ret/close，但补回行、suspend_flags 和 resume 判定直接读 raw 文件。要求 manifest 增加 `raw_content_sha256`（逐个文件 sha 排序拼接后再取 sha），三步共用一份并互相比对；重建期间不得运行 nightly 的写 raw 步骤。
- **P2-2 staging 泄漏面**：Staging 创建之后、try 之前的代码（cs 第 43–51 行，ind_names 和 sw；sf 第 36–40 行），以及 try 之后的写盘和 commit，一旦出异常，或者进程被 SIGKILL/OOM 杀掉，都不会写 VOID，staging 会留下来。下一次运行会因为残留 staging 被拒，所以不会产生坏产物，但没有 VOID 记录。要求把这些代码包进 try；回执里说明「残留 staging = 中断」，一律人工 VOID。
- **P2-3 D2 的日期范围比 D1 宽**：build_suspend_flags 的 days 用的是 glob 全部 daily 文件（现在到 20261016），掩码和 D1b 都只到 2026-10-14。要求截到掩码最后一天，或者在 manifest 里写明，并在回执单列 10-15 和 10-16。
- **P2-4 运行条件不在代码门禁里**：nice、串行、「没有其他研究进程」只能写成 .ok 里的建议键，parser 会忽略未知键。要求回执记录启动时的 `os.nice(0)` 和 `ps` 中 research/ 进程快照；niceness 不是 10、或者有其他研究进程，就写 FAIL。下一版门禁可以把 run_niceness 改成强制键。

**P3**
- P3-1 方案文档头写的是「01:45 EDT」，mtime 却是 01:41:23，时间戳又写在了未来（r2 P3-1 复发），请改成实际时间。诊断文档已经改成 55ff3593…，过期句已删除，不在钉定范围内。
- P3-2 方案 P1-2 写「写 VOID、非零退出」，但 dry-run 下 void 不写 VOID 文件，只中止，文档要说明。
- P3-3 RSS 守卫用的是 ru_maxrss（峰值），只在年边界检查（D2 每 100 日查一次），超限是事后发现。预计峰值 0.85GB，余量够，接受；建议在年内循环里也查一次。
- P3-4（流程）Data 自报：读了 namechange_all 和 stock_delisted v1 的 schema（不读数据行）；自测 ③ 在三个输出位置临时放了标记文件，测完已删除，本轮复核无残留。/tmp/sd1_selftest/mkok.py 生成的是 .ok 格式的假授权文件（头部标注 SELFTEST FAKE，已删除），harness.py 还在，请 Data 自行清理。三件都轻微，记 P3。**下次做任何自测，包括只读 schema、往输出位置放标记、生成假 .ok，都要先拿到带 `allow_selftest=true` 的 Arch .ok。**上一轮无 .ok 跑 dry-run 已在 r2 P2-1 记账，不重复计。
- P3-5 parse_run_auth 不校验 signed_et 的格式，草稿里写 `DRAFT_NOT_SIGNED` 也能通过。建议校验 ISO8601 格式。
- P3-6 已确认：tie-sens 和 Alpha regen 都已退出；Data 的抓数进程不写任何重建输入（§8）。

## 10. 下一版 .ok（P1-1 修完后签；键结构已用 Data 的 parse_run_auth 校验通过）

路径 `output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v1.ok`（门禁只认 `--arch-ok PATH`，路径不固定，用这个名字）。届时把三个 script/plan sha 换成新值，其余照下：

```
format=quantlab_run_auth_v1
version=cs_panel_resumefix_v1
signed_by=arch
signed_et=<ISO8601 ET>
allow_full=true
allow_smoke=false
allow_dryrun=true
live=false
promotion=false
scope=D1_cs_panel_v2_resumefix_2018_2026_and_D2_suspend_flags_v2_and_D3D4_stock_delisted_v2_new_versioned_outputs_only
not_authorized=tier1_materialize_change,paper_mask_change,old_cs_panel_overwrite,v1_panel_overwrite,mask_rebuild,leaf_eval,leaf_ic,engine_change,fund_portfolio_merge,broker_recommend_merge
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
plan_cs_panel_sha256=<新>
plan_sd_fix_sha256=<新或 d0319476…>
script_cs_panel_sha256=<新>
script_suspend_flags_sha256=<新或 1b62bba1…>
script_stock_delisted_sha256=<新或 1504209b…>
common_sha256=<新 sd1_common sha，若改>
mask_sha256=c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af
v1_cs_panel_2018_sha256=035d1f60d90911d8c8988b386eb8b845cb3cc0fbe9826af4f2ca7cd19222d8a9
v1_cs_panel_2019_sha256=b843a7bc00fc383d016f407a10d910131eeaadf0345acd5c373b67da7cc3f857
v1_cs_panel_2020_sha256=e25a7e59fe587b921760da751c2fb330b771847fab9dd56a2fdfa0887eee8904
v1_cs_panel_2021_sha256=bea54e540332248165239a3407f85da248d38f0b75aaade25f041302835dead8
v1_cs_panel_2022_sha256=ad188ddaf9807ae343bda6db8d53aa20737e4778f66bda7810faa042d699fc5e
v1_cs_panel_2023_sha256=6acf163e12fac1aacfe2188ebe9e0f2df4f2abff5ad95d5907c88296bc302ab5
v1_cs_panel_2024_sha256=6d238ee3b2429edc1a5f70d36c1aea48bda70a9031fef54e987a255b11b7fc7b
v1_cs_panel_2025_sha256=39568253199713f28305409b512d380340d0d0c915464ee8a1c0020611db331f
v1_cs_panel_2026_sha256=4608d8bc1eec7109a85f7b8018ab9a2f4d0fdcd1f36b4d1faefdc9714ecb2868
float_mktcap_sha256=346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef
sw_l1_sha256=89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c
stock_delisted_v1_sha256=90c8934dddc698f46075a20fe3d60309094919868c5e3a4bacc4d12c765f0603
namechange_all_sha256=6b81ee0b0d60d6d468910fb606ea8e4d448618c4e67fbd5337ffe0b0523fba5a
delisted_daily_sha256=e0db051eb9e39487076ce2a73f6a03866442660794281ccc25cc502dfcb4f2aa
run_niceness=10
run_serial=true
run_after=alpha_v41_regen_finished_and_no_other_research_process_in_ps
run_forbid_concurrent=nightly_daily_pull,tier1_pull,adj_factor,bars_materialize
```

运行条件（写进 .ok 建议键，由回执自证）：
- 每一步都用 `nice -n 10`，严格按 D1a → D1b → D2 → D3D4 串行，一次只跑一个进程。
- 开跑前先看 ps：Alpha v4.1 regen 必须已结束，没有其他 research/ 进程，也没有在写 raw 的 nightly 步骤。
- 每步写 manifest 和 RECEIPT，下一步的门禁检查上一步的 RECEIPT。

## 附录：全长 sha

- plan_cs_panel 5d0a0fb20ab14d4f7263db8429f094850afdf501cffdc47be284b27ceccaf0ac
- plan_sd_fix d0319476e1ea16148917cbd0984054897f904c21c164788096d6c39f5ad59625
- script_cs_panel 29f66d984a389f0fbc2139cbfd7dc5dc0aaa14b3f5bfcf8720fc44a4549fa0e2
- script_suspend_flags 1b62bba147b878b2ee2ab8735d627a7a06bae0124d2929c24ee51519ebed6f0a
- script_stock_delisted 1504209b696500a7940d6cb2eab28618d880b600049fd53ea63038ebd9082a16
- sd1_common 91eb61b433ea835f8174670a2a1c6a583b7a4e78c29d85884a319ad13f7516ca
- test_sd1_common fd497582b364ecfe40d15e9f38b94eb3e80c48b2e881323e5eecce4aca7c93f1
- ind_names.csv（v1）1ce867127690040bf04b6c8ad5bc16a6d99a396d2ac431893a21eef7892a902a
- tier1_materialize.py e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb
- 诊断文档 docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md 55ff3593891d8a1928fcd1e73be49603c4c0384ca1f8fb44ac6964b0f557d584
- 探针 carry_none_probe.py c963cd6d3be7ff8f7947765754554c8687aca074566deddc3cbda3877863e777；carry_none_probe.json 17d9c0d8717a3f22fc06e77a97330eb2056b3248bfe5ca2d906c36f559cbd9a3

live=false，promotion=false。
