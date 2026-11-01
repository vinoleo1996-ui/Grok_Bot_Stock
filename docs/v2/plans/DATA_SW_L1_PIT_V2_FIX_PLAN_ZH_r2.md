# Data 申万一级 PIT 修复方案 r2（sw_l1_pit_v2）——仅方案，待 Arch 审

- 作者：QuantLab Data；起草 2026-10-18 07:1x ET。
- **本文件是 r2，新文件**。r1 = docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH.md（sha 2d9f5b8e9981a9d75366622779c6d2c57422154a2c29fe8f1736e9efc62f2ee8，已冻结，未改动）。
- 回应：Arch 静态审 docs/v2/ARCH_DATA_SW_L1_PIT_V2_PLAN_REVIEW_ZH.md（sha f17f477120a8b19adcdffcc79ccf9edc48255503cf0aa65b7f528f09b4b38b32），有条件通过；3 个 P1、11 个 P2、10 个 P3 逐条回应见 §15。
- 状态：**仅方案**。下文代码与 diff 只是文本：没有在 repo 创建任何 .py，没有 git apply，没有运行。起草时叶23 r2.11 / 叶24 正在用真实数据运行，因此本轮**只读了源码与文档文本**（rg/Read .py/.md，以及审计 CSV 493f3621），没有读任何 parquet/数据文件，没有 import 项目代码。代码文本在 /tmp 做了 py_compile 与 pyflakes 静态检查（均通过、无告警），未执行。
- 定性：235 / 68 / 46 三类都是我方合并丢失，整个问题记 sw_pit 路径 P1（Arch 06:51）。
- live=false，promotion_approved=false。

## 0. 硬约束
- 不覆盖、不改动：0b1d3432（data/v2/sw_pit/industry_members_sw_l1_pit.parquet）与 89d4afa3（data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet）。所有产出都是新的版本文件，原子写、不覆盖（§6.4）。
- 新输出：data/v2/sw_pit/sw_l1_pit_v2.0.parquet（+ .manifest.json），之后 sw_l1_pit_v2.1.parquet …；“当前已审版本”由指针 data/v2/sw_pit/sw_l1_pit_APPROVED.json 指定，**只由 Arch 在审完回执后更新**，Data 代码只读（§6.7）。
- 不碰 94322、8787、moneyflow、data/v2/events。
- 资源：单进程 RSS ≤ 1.5GB（预估 <300MB，P3-10）；MemAvailable 低于 2GB 即暂停；一次只一个重任务；nice -n 10，PYTHONDONTWRITEBYTECODE=1，/usr/bin/python3。

## 1. 排期
1. 实施推迟到叶23 r2.11、叶24、10-19 纸面跟踪全部结束之后；与交易日历 2027 延长包同批交付（含 20130424 pretrade_date 本地由 is_open 推导 = 20130423）。
2. **截止 2026-12-15**（P3-8）。
3. 避开 10-19 16:40–18:40 ET（及 17:40 前后一小时）；每次运行前通知主 Agent 与 Arch（开始时间、预计时长）。
4. .ok 重签范围（P3-8，更正 r1 L18）：叶23/叶24 钉的是 89d4afa3，本方案**不改 89d4afa3**，所以它们的 .ok **不因本方案重签**；只有消费方迁移到 v2 时，迁移方的 .ok 才由 Arch 重签（Strategy 两个脚本读 0b1d3432，迁移时重签）。
5. 通知 Strategy/Intel 由主 Agent 负责。

## 2. 问题复述（只读审计结论）
- 坏表 0b1d3432：7573 行 / 5600 个代码，由 `scripts/acquire/sw_pit_refresh.py`（sha a18684fe…）生成。流程是：全量 Y/N 分页 + 按 L1×Y/N 分拉 → concat → 只去掉完全相同的行 → groupby(instrument_id, l1_code, out_date 为空记为 2099)。没有来源优先级，同一成分的 open 和 closed 版本两条都留下。
- 12 只双开（P2）：002420 002481 002597 003030 300699 300741 300777 300858 300972 603020 605077 688002（完整代码见 A_12codes_open_records.csv）。分拉数据里每只只有 1 条 open，另一条是 closed；多出来的 open 来自全量分页返回的陈旧或矛盾版本。
- 349 只在市股票在 2026-09-24..10-16 的每个交易日（11 天，3839 个 code-day）都没有 open 的 L1：
  - 235 只：10-14 04:00 那次“修复”误删（P1）；
  - 68 只：全量分页截断后没补（分拉里有）；
  - 46 只：原判“源缺”，§3.2 复核推翻（89d4afa3 里全部有 open 行）。**Arch 06:51 裁定：与 235、68 同类，都是我方合并丢失，统一记 sw_pit 路径 P1。**
- 10-14 缩表根因（inventory 415f0783）：queue_chain_20261014.py:139-142 在 03:50–04:00 跑了 nightly_update --steps hsgt,sw，sw_pit_refresh 用一次被 relay 截断的拉取覆盖了表；脚本唯一的保护是“代码数 >5000”。修复见 §6 的防缩表闸门和取消覆盖旧表。
- 文档 ALPHA_DATA_D5D6_FIX_ZH.md 写的是 7735 行并带 is_primary 列，和实际文件（7573 行、没有 is_primary）不符，回执里一并更正。

## 3. bak_pre_fix 核验（主 Agent 要求，只读）
命令（2026-10-18 06:5x ET；pgrep 确认没有 leaf 进程；只用 pyarrow 读 ts_code、instrument_id、out_date 列，不 import 项目代码；峰值 maxrss 169MB）：
`sha256sum …；stat -c "%n | birth %w | mod %y" …；nice -n 10 /usr/bin/python3 -c "<pyarrow 读列 + 集合比较>"`

| 项 | 结果 |
|---|---|
| bak sha | 597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c ✔ |
| 当前表 sha | 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6 ✔ |
| 89d4afa3 sha | 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c ✔ |
| bak 行数 / 代码数 | **7743 / 5759** ✔ |
| 当前表 行数 / 代码数 | 7573 / 5600 |
| 代码集：bak 有、当前表没有 | **254**（和“10-14 修复删了 254 只”一致）✔ |
| 代码集：当前表有、bak 没有 | **95**（修复时还新增了 95 只，审计原文没提，回执里要说明来源） |
| 235 只误删代码是否都在 bak 里 | 235/235 ✔；235 只都在被删的 254 只里 ✔；被删但不在 235 里的 19 只是已退市或未上市等，不属于在市口径 |

### 3.1 时间戳
- bak：birth 和 mod 都是 2026-10-18 01:13:14.40 ET；当前表：birth 和 mod 都是 01:13:13.24 ET。
- 两个文件都是 10-18 01:13 工作区整体恢复时重写出来的新 inode（落在 RECOVERY_MANIFEST 记录的 01:13:24–01:14:51 区间附近；logs/nightly/20261014_* 也都是 01:13:3x）。**原始 mtime 已经丢了，没法用文件时间直接证明 bak 早于 10-14 04:00。**
- 不过内容证据足够：bak 比当前表多出的代码正好是修复删除的 254 只，而且包含全部 235 只误删代码，据此判定 bak 就是误删之前的版本。建议 Arch 接受用内容证据代替时间证据。

### 3.2 三类代码在 89d4afa3 里的情况（按 instrument_id 口径）
- 235 只全部有 open 行；68 只全部有 open 行；**46 只也全部有 open 行**。
- 结论：以 89d4afa3 为主来源（§5）重建后，预计 09-24..10-16 每天缺成分为 **0**（口径见 §6.6：out_date 含当天）。source_gap 预计 0 只；source_gap 的代码本来就没有 open 行可打标，所以只列入 source_gap.csv 和 manifest，不加行（P3-1）。

## 4. 规则（r2 修订）
1. **主来源**：89d4afa3，accepted（condition_a_met，Arch 94e91ffa）。62 个 raw（10-18 01:08）来源未知，只作佐证（出全键 normdiff，不拦截）。
2. **不用 FULL 全量文件**（P1-3 二选一的选择，理由见 §5.3）；sw_pit_refresh 也停用全量 Y/N 分页。
3. **冲突处理不删键**（P2-4）：完全重复行去重；同键既有 open 又有 closed → 保留 closed，open 版本并入（键保留）；同一代码多条 open → 较旧的补 out_date = 新 open 的 in_date 前一交易日（键保留）。全部写入 conflicts.csv，含逐行说明。
4. **每代码 open ≤ 1**：违反即显式 raise，不落盘。
5. **不编造**：在市但无 open 行的代码不加行，只列入 source_gap.csv 和 manifest（所有行 quality_status=ok；改正 r1 L54/L61 的说法，P3-1）。非 A 股代码（如 T00018）剔除，列入 non_a_share_excluded.csv 和 manifest（P1-2）。
6. **只写新版本文件**，原子写，不覆盖；两步版本 v2.0 / v2.1（§5）。
7. **交易日历**：20130424 pretrade_date 本地推导，随 2027 包交付（不在本 diff 内）。

## 5. 数据来源与两步设计（P1-3）
### 5.0 主来源
- 89d4afa3 为 v2 主来源，状态 accepted（condition_a_met，Arch 94e91ffa）：manifest.json 记 7920 行 / 5914 代码 / 31 行业；7115 属于 87d769aa；62 raw 经 tushare_relay_pull.py:200-230 重建，7920 行中 7919 行一致，唯一差异是非 A 股代码 T00018 的写法。
- 限制：10-10 的 sha 未记录，无法证明与 10-10 原文件逐字节一致；可证的是与 output/data_v2_bundle 及 data_v2_bundle.tar 副本一致。v2 manifest 写明（代码 manifest.primary.note）。

### 5.1 第一步：v2.0 = 89d4afa3 清洗版
- as_of = **2026-10-10**（89d4afa3 的 fetch 日），写入 manifest。
- 内容 = 89d4afa3 经 §4 规则 3–5 清洗、代码与日期规范化、按 §6.6 契约输出。**只用 89d4afa3**，不用 FULL、不用 raw、不用重拉。
- 闸门：以 89d4afa3 为基线的硬闸门（§6.0），不接受 --allow-shrink。
- 与 0b1d3432 的比较只写 info；与 62 raw 的全键 normdiff 只披露。

### 5.2 第二步：v2.1 = 实施日重拉增量（v2 的下一版本）
- 实施日用 `sw_pit_refresh.py --pull-only` 重拉到**新建目录** data/v2/tushare_raw/index_member_all_<YYYYMMDD_HHMMSS>/（目录名统一为这个格式，P3-5）。目录必须是该次运行新建、日期部分等于实施日、所有文件 mtime 晚于 run .ok 的 signed_et、COMPLETE.json 存在且 INCOMPLETE.json 不存在、不等于 RAW_0108（P2-7）。
- 合并规则：只追加新键、只给 v2.0 中 open 的键补 out_date；**不删键、不重新打开、不改已有 out_date**（代码 increment_check 拒绝这三类）。重拉中与此冲突的差异不采纳，但逐条列入 increment_diff.csv，在回执披露。
- 基线：已审指针指向的 v2.0；软闸门（§6.0）。
- **取代 r1“normdiff 必须为空”的硬条件**：r2 不再要求重拉与 89d4afa3 的 normdiff 为空；v2.0 → v2.1 的每一条差异都分类（key_added / out_date_filled / repull_reopen_ignored / out_date_conflict_ignored / in_base_not_in_repull）并披露，由 Arch 审回执决定是否采纳 v2.1（更新指针）。
- 回退（原 6b）：若重拉与 v2.0 出现大面积 in_base_not_in_repull 或 out_date 冲突且无法解释，则不更新指针，停在 v2.0，报 Arch 重新评估叶23/24 与主来源。

### 5.3 FULL 全量文件：不用（P1-3 二选一）
- 选择：**不用**，而不是钉 sha。
- 理由：(1) FULL（sw2021_members_l1l2l3_raw.parquet）来自 10-14 那次被截断的拉取，也是 12 只双开陈旧 open 的来源；(2) 89d4afa3 有 5914 个代码，覆盖 349 只缺失代码（§3.2），v2.0 不需要补缺；(3) 10-10 之后的新代码和新变化由 v2.1 的实施日重拉进入，有独立性校验与差异披露，比一个没有来源保障的旧全量文件可靠；(4) 不用它就少一个需要钉住和解释的输入。sw_pit_refresh 同时停用全量 Y/N 分页（§6.2）。

### 5.4 09-24..10-09 增量（gap2）：Data 开放项（P3-2 更正归属）
- 归属：**Data 的开放项**（r1 L67/L568/L628 写成“待 Arch”，改正）。
- 入口：经第二步进入。代码 gap2_report 比较 89d4afa3 与重拉中 in_date 或 out_date 落在 2026-09-24..10-09 的键，输出 gap2_delta.csv。
- 交付：**实施前交**。做法：叶23/24 结束后、实施日之前，单独签一个 pull .ok 跑一次 `--pull-only`，再用 `--step v2.0` dry-run（带 --repull_dir）只出 gap2_delta 报告交 Arch；实施日再按 §5.2 重拉一次做 v2.1。
- 不阻塞本次方案审。

### 5.5 队列、时间证据、来源记录
- 队列 `nightly_step|sw|20261014/15/16` 三项并入 v2；Arch 审过 v2.0 回执后标 done，reason=`superseded_by sw_l1_pit_v2.0 (<sha>)`，改前归档到 _recovery/data/。nightly 的 sw 步骤在同一份代码变更中停用（§6.3），SW 只改一次。
- 时间证据：bak 与 0b1d3432 的原始时间戳被 10-18 01:13 ET 工作区恢复覆盖；Arch 接受内容证据（sha + 行级 diff）；v2 manifest 写 time_evidence=lost。
- 来源记录：89d4afa3 与 output/data_v2_bundle、data_v2_bundle.tar（10-10 14:42）副本逐字节一致；manifest fetch_time 2026-10-10T10:01:23-04:00；由 tushare_relay_pull.py:140-151、223-230 写出；10-18 01:08 的文件是恢复。62 个 raw 不在 tar 里，没有来源记录。

## 6. 代码（文本，未应用、未运行）
落代码前把旧脚本归档到 _recovery/data/sw_l1_pit_v2_pre_<date>/。涉及 4 个文件：新建 scripts/acquire/sw_l1_pit_v2_build.py、新建 tests/test_sw_l1_pit_v2_build.py、修改 scripts/acquire/sw_pit_refresh.py、修改 scripts/nightly_update.py。

### 6.0 闸门
| 场景 | 基线 | 规则 | 覆盖 |
|---|---|---|---|
| v2.0 首次写入 | 89d4afa3（同主来源） | 89d4afa3 每个 (code, industry, in_date) 键都在 v2 中；唯一键数、代码数不降；补 out_date 键不变，不算缩表；删行逐行写 conflicts.csv（reason=deleted_vs_89d4afa3_baseline）且仍拒绝 | **无**（v2.0 遇 --allow-shrink 直接拒绝；hard_gate 没有覆盖参数） |
| v2.1 及之后刷新 | 指针指向的已审版本 | 唯一键数、代码数阈值 0；旧键子集；当前成员扣除同期退市后降幅 ≤ 0.3%（退市取 stock_basic 与 stock_delisted_v2 的较早日期，区间为 (指针 built_et 日期, 今天]） | `--allow-shrink` → enforce 追加 mode allow_shrink，.ok 须 `allow_allow_shrink=true`；预期不需要 |
| sw_pit_refresh 的 l2 | sw_l2_pit_APPROVED.json 指向的已审 l2 版本 | 同上 | 仅在没有已审基线（baseline=none）时需要 allow_allow_shrink=true |
| 与 0b1d3432 比较 | — | 只写 shrink_gate.json 的 info 段（0b1d3432 有而 v2 无的键），不拦截 | — |
- 键比较一律用 规范化代码 + 行业代码 + in_date.strftime("%Y%m%d")（P2-2）；行数闸门按去重后的唯一键计（P2-4）。
- 取代 sw_pit_refresh 原来的绝对断言 `nunique()>5000`。r1 L97“首次构建需 allow_shrink、baseline=none”限定为“sw_pit_refresh 的 l2 没有已审基线”这一种情形（P3-1）。

### 6.1 运行门禁（P1-1）
- 真实签名（已读 scripts_eng/ok_runner_pin.py 源码，sha c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485，L78）：`enforce(script, ok_paths, modes=(), deps=None)`。它校验 live=false、promotion=false、runner_sha256_<stem> 钉住本脚本、每个 mode 都有 allow_<mode>=true、每个 dep 都有 dep_sha256_<key>。r1 selftest 写的 `enforce(modes=["selftest"])` 会 TypeError，已改为 `enforce(__file__, [OK_PATH], modes=["selftest"], deps={...})`。
- 各入口第一件事调用 enforce，mode 各自独立：

| 入口 | modes | deps |
|---|---|---|
| sw_l1_pit_v2_build.py --step v2.0（dry-run / execute） | dry_run / execute | primary、prev_0b1d、stock_basic、delisted、cal、raw0108_list |
| sw_l1_pit_v2_build.py --step v2.1（dry-run / execute） | dry_run_increment / execute_increment（可加 allow_shrink） | 同上 |
| sw_pit_refresh.py --pull-only | pull | sw_l1_pit_v2_build |
| sw_pit_refresh.py（l2 刷新） | refresh（可加 allow_shrink） | sw_l1_pit_v2_build |
| tests/test_sw_l1_pit_v2_build.py | selftest | sw_l1_pit_v2_build |

- .ok 解析一律用 ok_runner_pin.parse_ok/enforce，删除 r1 自造的 check_ok（P2-8）；mode 精确匹配 allow_<mode>，不做子串匹配。r2 不再有 normdiff 硬条件，所以不需要 allow_normdiff / normdiff_allow（§5.2）。
- 单次使用：execute、execute_increment、pull、refresh 的 .ok 用一次即在旁边写 `<ok>.consumed.json`（O_EXCL 创建）；开始时若已存在则拒绝。dry-run .ok 在有效期内可重复用。
- **前置条件（不归 Data）**：scripts_eng/ok_runner_pin.py 目前**不在 git 中**（git ls-files 报未跟踪），须由 **Arch 或 Eng** 先提交入库；本方案所有入口都依赖它。

### 6.2 diff：scripts/acquire/sw_pit_refresh.py（基于 a18684fe 重新生成，P2-6）
- 已核对当前文件 sha = a18684feb3a0816881a81ff1e6d3fe3d60a927e6ff9655c99ca36c50fa2196e9，**与 r1 所基于的版本一致，没有差异**。diff 由 `diff -u` 对 /tmp 中的提议文本生成，hunk 头由工具计算（修 P2-6 的 hunk 行数错误）；提议全文在 /tmp 做过 py_compile 与 pyflakes。
- 变化：入口先 enforce；新增 --ok / --pull-only / --allow-shrink；重拉目录必须新建（exist_ok=False）；classify_l1/l2 版本化、原子写；停用全量 Y/N 分页；每个分拉**先原子落盘成功，再进内存**；任何分拉失败 → 写 INCOMPLETE.json 并**非零退出**；成功则写 COMPLETE.json（含每个文件 sha）；--pull-only 到此结束；取消 >5000 绝对断言；不再写 l1 PIT 表；l2 用指针基线的软闸门；manifest 版本化，键名统一为 built_et（tz-aware）。
```diff
--- a/scripts/acquire/sw_pit_refresh.py
+++ b/scripts/acquire/sw_pit_refresh.py
@@ -1,8 +1,17 @@
 """SW2021 L1/L2(/L3) PIT 成分刷新: tushare index_member_all (按 L1 × is_new Y/N). 写候选表, 不覆盖已 promotion 的 industry_members_sw_l1.parquet."""
-import sys, json, time, pathlib, pandas as pd
+import sys, json, time, pathlib, argparse, pandas as pd
 ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT))
+sys.path.insert(0,str(ROOT/"scripts_eng")); from ok_runner_pin import enforce
+ap=argparse.ArgumentParser(); ap.add_argument("--ok",action="append",required=True)
+ap.add_argument("--pull-only",action="store_true"); ap.add_argument("--allow-shrink",action="store_true"); ARGS=ap.parse_args()
+_MODES=["pull"] if ARGS.pull_only else ["refresh"]+(["allow_shrink"] if ARGS.allow_shrink else [])
+_G=enforce(__file__,ARGS.ok,modes=_MODES,deps={"sw_l1_pit_v2_build":ROOT/"scripts/acquire/sw_l1_pit_v2_build.py"})  # 先于任何联网/读写
+sys.path.insert(0,str(ROOT/"scripts/acquire")); import sw_l1_pit_v2_build as V
+V.check_unconsumed(ARGS.ok)                                    # 单次使用
 from quantlab.data_sources.tushare_proxy import relay,_to_df
 OUTD=ROOT/"data/v2/sw_pit"; OUTD.mkdir(parents=True,exist_ok=True)
+STAMP=pd.Timestamp.now(tz="America/New_York").strftime("%Y%m%d_%H%M%S")
+RAWD=ROOT/"data/v2/tushare_raw"/("index_member_all_"+STAMP); RAWD.mkdir(parents=True,exist_ok=False)  # 必须新建
 def call(api,**kw):
     out,off=[],0
     for a in range(6):
@@ -17,36 +26,42 @@
             print("retry",api,kw,e,flush=True); time.sleep(5*2**a); out,off=[],0
     raise RuntimeError(f"fail {api} {kw}")
 cls=call("index_classify",level="L1",src="SW2021")
-cls.to_parquet(OUTD/"sw2021_classify_l1.parquet",index=False)
-call("index_classify",level="L2",src="SW2021").to_parquet(OUTD/"sw2021_classify_l2.parquet",index=False)
-parts=[]
-# relay 的 l1_code 过滤在负载下不稳定(观测到忽略过滤/截断), 改为全量 Y/N 分页后本地去重
-for isn in "YN":
-    df=call("index_member_all",is_new=isn); df["is_new"]=isn; parts.append(df); print("members",isn,len(df),flush=True); time.sleep(0.5)
-# 再按 L1 × Y/N 分拉补齐 (全量分页在 relay 端存在截断), 合并去重
+V.atomic_write_parquet(cls,V.versioned(OUTD/"sw2021_classify_l1.parquet",STAMP),len(cls))   # 版本化, 不覆盖
+cls2=call("index_classify",level="L2",src="SW2021")
+V.atomic_write_parquet(cls2,V.versioned(OUTD/"sw2021_classify_l2.parquet",STAMP),len(cls2))
+parts,failed,shas=[],[],{}
+# 只用按 L1 x Y/N 分拉; 全量 Y/N 分页返回陈旧/矛盾版本(12 只双开的来源), 停用
 for c in cls.index_code:
     for isn in "YN":
         try:
-            df=call("index_member_all",l1_code=c,is_new=isn); df["is_new"]=isn; parts.append(df[df.l1_code==c])
-        except Exception as e: print("l1 fail",c,isn,e,flush=True)
+            df=call("index_member_all",l1_code=c,is_new=isn); df=df[df.l1_code==c].copy(); df["is_new"]=isn
+            f=RAWD/f"{c}_{isn}.parquet"; shas[f.name]=V.atomic_write_parquet(df,f,len(df))   # 先落盘成功, 再进内存
+            parts.append(df)
+        except Exception as e: print("l1 fail",c,isn,e,flush=True); failed.append(f"{c}_{isn}: {e!r}")
         time.sleep(0.3)
+if failed or len(shas)!=2*len(cls):
+    V.atomic_write_json({"incomplete":failed,"n_ok":len(shas),"expected":2*len(cls),"stamp":STAMP},RAWD/"INCOMPLETE.json")
+    raise SystemExit(f"REFUSED (sw_pit_refresh): 分拉不完整 {len(failed)} 失败, 见 {RAWD}/INCOMPLETE.json")   # 非零退出
+V.atomic_write_json({"files":shas,"stamp":STAMP,"runner_sha256":_G["runner_sha256"],"oks":_G["oks"]},RAWD/"COMPLETE.json")
+if ARGS.pull_only:
+    V.consume_ok(ARGS.ok,{"pulled":str(RAWD)}); print("PULL-ONLY done",RAWD,flush=True); raise SystemExit(0)
 m=pd.concat(parts,ignore_index=True).drop_duplicates()
-print("union rows",len(m),"instruments",m.ts_code.nunique(),flush=True)
-assert m.ts_code.nunique()>5000, f"too few instruments {m.ts_code.nunique()} -> relay 截断, 不落盘"
-m["in_date"]=pd.to_datetime(m.in_date,errors="coerce"); m["out_date"]=pd.to_datetime(m.out_date,errors="coerce")
-m["instrument_id"]=m.ts_code.str.split(".").str[1].str.lower()+"."+m.ts_code.str.split(".").str[0]
+print("union rows",len(m),"instruments",m.ts_code.nunique(),flush=True)   # 绝对断言 >5000 取消, 改为对已审版本的闸门
+m["in_date"]=V.parse_dates(m.in_date,"in_date"); m["out_date"]=V.parse_dates(m.out_date,"out_date")
+m["instrument_id"]=m.ts_code.map(V.norm_code)
+nonA=sorted(m[m.instrument_id.isna()].ts_code.unique()); m=m[m.instrument_id.notna()].copy()
 m["available_at"]=m.in_date+pd.Timedelta(hours=18)
-m["source"]="tushare.index_member_all(SW2021)"; m["promotion_approved"]=False
-m.to_parquet(OUTD/"sw2021_members_l1l2l3_raw.parquet",index=False)
-asof=pd.Timestamp.now(tz="Asia/Shanghai").tz_localize(None).normalize()
-man={}
-for lv in ["l1","l2"]:
-    t=m[["instrument_id","ts_code","name",f"{lv}_code",f"{lv}_name","in_date","out_date","is_new","available_at","source","promotion_approved"]].copy()
-    t["out_key"]=t.out_date.fillna(pd.Timestamp("2099-12-31"))
-    t=t.sort_values("in_date").groupby(["instrument_id",f"{lv}_code","out_key"],as_index=False).first().drop(columns="out_key")
-    f=OUTD/f"industry_members_sw_{lv}_pit.parquet"; t.to_parquet(f,index=False)
-    man[lv]=dict(path=str(f),rows=len(t),instruments=int(t.instrument_id.nunique()),n_codes=int(t[f"{lv}_code"].nunique()),
-                 in_date_range=[str(t.in_date.min().date()),str(t.in_date.max().date())],current_members=int(t.out_date.isna().sum()))
-man.update(source="tushare relay index_member_all + index_classify SW2021",available_at="in_date 18:00 Asia/Shanghai (Tushare 未提供公告时间, 近似)",
-  note="不覆盖已 promotion 的 data/v2/sw_l1_pit/industry_members_sw_l1.parquet; 本表为 research 候选",promotion_approved=False,built=pd.Timestamp.now().isoformat())
-json.dump(man,open(OUTD/"manifest.json","w"),ensure_ascii=False,indent=2); print(json.dumps(man,ensure_ascii=False))
+m["source"]="tushare.index_member_all(SW2021) perL1"; m["promotion_approved"]=False
+V.atomic_write_parquet(m,V.versioned(OUTD/"sw2021_members_l1l2l3_raw.parquet",STAMP),len(m))   # 不覆盖
+man={"stamp":STAMP,"raw_dir":str(RAWD),"non_a_share_excluded":nonA}
+# l1 PIT 改由 sw_l1_pit_v2_build.py (v2.x) 生成; 此处只建 l2
+lv="l2"
+t=m[["instrument_id","ts_code","name",f"{lv}_code",f"{lv}_name","in_date","out_date","is_new","available_at","source","promotion_approved"]].drop_duplicates()
+base=V.read_pointer(OUTD/"sw_l2_pit_APPROVED.json")
+gate=V.soft_gate(t,base["df"] if base else None,kcol=f"{lv}_code",delisted=set(),shrink_granted=ARGS.allow_shrink)
+f=V.versioned(OUTD/f"industry_members_sw_{lv}_pit.parquet",STAMP); s=V.atomic_write_parquet(t,f,len(t))
+man[lv]=dict(path=str(f),sha256=s,rows=len(t),instruments=int(t.instrument_id.nunique()),gate=gate,current_members=int(t.out_date.isna().sum()),
+             in_date_range=[str(t.in_date.min().date()),str(t.in_date.max().date())],out_date_semantics="inclusive (最后在任日)")
+man.update(source="tushare relay index_member_all(perL1) + index_classify SW2021",available_at="in_date 18:00 Asia/Shanghai (Tushare 未提供公告时间, 近似)",
+  note="不覆盖任何已有文件; l2 新版本待 Arch 审后由 Arch 更新 sw_l2_pit_APPROVED.json",promotion_approved=False,built_et=V.now_et())
+V.atomic_write_json(man,V.versioned(OUTD/"manifest.json",STAMP)); V.consume_ok(ARGS.ok,{"refresh":STAMP}); print(json.dumps(man,ensure_ascii=False,default=str))
```

### 6.3 diff：scripts/nightly_update.py（同一份代码变更，P2-6）
- 读前 sha ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636。
- 变化：停用 sw 步骤（--steps 带 sw 时只打印提示，不记入 res，不影响 overall）；RELAY_STEPS 去掉 sw；BUNDLE_MAP 去掉 5 个固定文件名的 sw_pit 条目，bundle 改为按 Arch 更新的已审指针复制（指针不存在时不复制；bundle 里的旧副本保持原样，不删除）。
- 注意：nightly_update.py 也是工作日 05:55 日更所用的脚本，所以这份 diff 只能在 §1 窗口内与其它变更同批落地，并由 Arch 在同一个 code-change .ok 中签。
```diff
--- a/scripts/nightly_update.py
+++ b/scripts/nightly_update.py
@@ -36,7 +36,7 @@
      "mid_large_universe":[[PY,"scripts/acquire/mid_large_universe_incr.py","--date",ymd]],  # D3 data/v2/universe/mid_large_members_pit.parquet 只追加, 写 status.tables.mid_large_universe (纳入 ok 判定)
      "events":       [[PY,"scripts/acquire/_light_event_windows_pull.py"],[PY,"scripts/acquire/forecast_manifest_declare.py"]],  # 2026-10-18: forecast manifest 声明(Arch P1-5)
      "hsgt":         [[PY,"scripts/acquire/fill_hsgt_top10_extend.py"]],
-     "sw":           [[PY,"scripts/acquire/sw_pit_refresh.py"]],
+     # "sw" 步骤停用 (SW L1 PIT v2 plan r2): 改为手动 scripts/acquire/sw_pit_refresh.py --ok <Arch .ok>, 防止再次覆盖/截断
      "cyq":          [[PY,"scripts/acquire/cyq_perf_monthly.py",ym,ym]],
      "tier3":        [[PY,"scripts/acquire/tier3_daily_snapshot.py","--date",ymd]],
      "bundle":       "bundle",
@@ -51,11 +51,6 @@
  ("data/v2/index_members/manifest_d5.json","index_members"),
  ("data/v2/corporate_actions/rights_issue_em.parquet","corporate_actions"),
  ("data/v2/corporate_actions/manifest_d6_rights_issue.json","corporate_actions"),
- ("data/v2/sw_pit/industry_members_sw_l1_pit.parquet","sw_pit"),
- ("data/v2/sw_pit/industry_members_sw_l2_pit.parquet","sw_pit"),
- ("data/v2/sw_pit/sw2021_classify_l1.parquet","sw_pit"),
- ("data/v2/sw_pit/sw2021_classify_l2.parquet","sw_pit"),
- ("data/v2/sw_pit/manifest.json","sw_pit"),
  ("data/v2/index/index_daily_pit.parquet","index"),
  ("data/v2/index/index_daily_pit_manifest.json","index"),
  ("data/v2/cyq/manifest.json","cyq"),
@@ -72,6 +67,15 @@
         dst=BUNDLE/sub; dst.mkdir(parents=True,exist_ok=True)
         if p.stat().st_size<8e6: _cp(p,dst); out.append(f"{sub}/{p.name}")
         else: out.append(f"SKIP>8MB {src}")
+    for ptr in ("sw_l1_pit_APPROVED.json","sw_l2_pit_APPROVED.json"):  # sw_pit 版本化后: 只按 Arch 更新的已审指针复制
+        pp=ROOT/"data/v2/sw_pit"/ptr
+        if not pp.exists(): continue
+        j=json.loads(pp.read_text()); dst=BUNDLE/"sw_pit"; dst.mkdir(parents=True,exist_ok=True)
+        for k in ("path","manifest"):
+            p=ROOT/j[k]
+            if p.stat().st_size<8e6: _cp(p,dst); out.append(f"sw_pit/{p.name}")
+            else: out.append(f"SKIP>8MB {j[k]}")
+        _cp(pp,dst); out.append(f"sw_pit/{ptr}")
     for p in sorted((ROOT/"data/v2/cyq").glob("cyq_perf_*.parquet")):  # 按月, 每月约 3-6MB
         dst=BUNDLE/"cyq"; dst.mkdir(parents=True,exist_ok=True)
         if p.stat().st_size<8e6: _cp(p,dst); out.append(f"cyq/{p.name}")
@@ -82,7 +86,7 @@
             dst=BUNDLE/"tier3_daily"/kind; dst.mkdir(parents=True,exist_ok=True); _cp(p,dst); out.append(f"tier3_daily/{kind}/{p.name}")
     return out
 
-RELAY_STEPS={"hsgt","cyq","tier3","sw"}  # 只能走 Tushare 中转的步骤: 中转不通时跳过记 partial
+RELAY_STEPS={"hsgt","cyq","tier3"}  # 只能走 Tushare 中转的步骤: 中转不通时跳过记 partial
 def register_backfill(k,d):
     f=ROOT/"output/relay_outage_backfill_queue.json"
     try: q=json.loads(f.read_text())
@@ -100,6 +104,8 @@
     S,env_extra=steps_for(d); order=list(S)
     sel=a.steps.split(",") if a.steps else order
     env=dict(os.environ,**env_extra); res={}
+    if "sw" in sel:  # 不记入 res, 不影响 overall
+        print("sw step disabled (SW L1 PIT v2 plan r2): 改用 sw_pit_refresh.py --ok",flush=True); sel=[k for k in sel if k!="sw"]
     print(f"NIGHTLY date={d} steps={sel}",flush=True)
     for k in sel:
         t0=time.time()
```

### 6.4 scripts/acquire/sw_l1_pit_v2_build.py 全文
```python
# scripts/acquire/sw_l1_pit_v2_build.py  (plan r2; 文本, 未落 repo, 未运行)
# SW2021 L1 PIT v2, 两步:
#   step v2.0 = 89d4afa3 清洗版, as_of=2026-10-10 (89d4afa3 的 fetch 日); 不用 FULL 全量文件.
#   step v2.1 = 实施日重拉(新目录)作为 v2 的下一版本: 只加键 / 只补 out_date, 不删键, 差异逐条披露.
# 不联网. 不覆盖任何已存在文件. 所有输入钉 sha (代码常量 + .ok dep_sha256_*). 入口第一件事是 ok_runner_pin.enforce.
import sys, os, re, json, argparse, pathlib, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd

ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT / "scripts_eng"))
from ok_runner_pin import enforce, parse_ok, sha256_file as sha     # 复用, 不自造 .ok 校验

ET = ZoneInfo("America/New_York")
SWD = ROOT / "data/v2/sw_pit"
POINTER = SWD / "sw_l1_pit_APPROVED.json"     # 已审版本指针: 只由 Arch 审完回执后更新; 本脚本只读
RAW_0108 = ROOT / "data/v2/tushare_raw/index_member_all"     # 62 文件, 来源未知, 只作佐证
INPUTS = {  # key -> (path, sha256); 同名 dep 由 .ok 的 dep_sha256_<key> 再钉一次
    "primary":     (ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet",
                    "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"),
    "prev_0b1d":   (SWD / "industry_members_sw_l1_pit.parquet",
                    "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6"),
    "stock_basic": (ROOT / "data/v2/meta/stock_basic_incl_delisted.parquet",
                    "2ef2d71d28957b0d8d7b8a599d4fcafbecc969f121e5ee072719ad202508eca8"),
    "delisted":    (ROOT / "data/v2/ref/stock_delisted_v2.parquet",
                    "9d757b96bb27540ea02ca0af323aacfb3880797604830a3984eb6fa4fdff3750"),
    "cal":         (ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet",
                    "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"),
    "raw0108_list": (ROOT / "docs/v2/audit/sw_l1_pit_v2/raw0108_sha256.txt", None),  # 62 行 "<sha>  <file>", 只由 .ok 钉
}
PROTECT = {INPUTS["primary"][1], INPUTS["prev_0b1d"][1]}
PROTECT_PATHS = {INPUTS["primary"][0].resolve(), INPUTS["prev_0b1d"][0].resolve()}
PRIMARY_AS_OF = "2026-10-10"
WIN = ("20260924", "20261016")
GAP2 = ("20260924", "20261009")
OPEN_THRESH = 0.003
TWELVE = ["sz.002420", "sz.002481", "sz.002597", "sz.003030", "sz.300699", "sz.300741",
          "sz.300777", "sz.300858", "sz.300972", "sh.603020", "sh.605077", "sh.688002"]
A_DOT = re.compile(r"^(\d{6})\.(SH|SZ|BJ)$", re.I)
A_PFX = re.compile(r"^(SH|SZ|BJ)\.(\d{6})$", re.I)
P_D8 = r"\d{8}"
P_ISO = r"\d{4}-\d{2}-\d{2}"
CONTRACT = [  # v2 schema 契约 (见方案 §6.5)
    ("instrument_id", "string"), ("ts_code", "string"), ("name", "string"),
    ("l1_code", "string"), ("l1_name", "string"),
    ("in_date", "datetime64[us]"), ("out_date", "datetime64[us]"), ("is_new", "string"),
    ("available_at", "datetime64[us]"), ("source", "string"), ("src", "string"),
    ("revision", "string"), ("quality_status", "string"), ("promotion_approved", "bool"),
]


class Refuse(SystemExit):
    pass


def fail(msg):
    raise Refuse(f"REFUSED (sw_l1_pit_v2_build): {msg}")


def now_et():
    return dt.datetime.now(ET).isoformat(timespec="seconds")


def parse_tz(s, what):
    t = dt.datetime.fromisoformat(str(s))
    if t.tzinfo is None:
        fail(f"{what}: 时间必须带时区 (got {s!r})")
    return t


# ---------- 代码规范化 (唯一入口) ----------
def norm_code(x):
    # 返回 "sh.600000"; 接受 600000.SH / 600000.sh / sh.600000 / SH.600000; 非 A 股 (如 T00018, 无点) 返回 None
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    m = A_DOT.fullmatch(s)
    if m:
        return m.group(2).lower() + "." + m.group(1)
    m = A_PFX.fullmatch(s)
    if m:
        return m.group(1).lower() + "." + m.group(2)
    return None


def to_ts(iid):
    a, b = iid.split(".")
    return b + "." + a.upper()


# ---------- 日期 ----------
def parse_dates(s, name):
    # 显式格式; 统一 datetime64[us] 零点无时区; 解析前空值数必须等于解析后 NaT 数 (非法日期 -> 拒绝, 不得变成 open)
    s = pd.Series(s)
    if pd.api.types.is_datetime64_any_dtype(s):
        if getattr(s.dt, "tz", None) is not None:
            fail(f"{name}: tz-aware 日期不接受")
        n_null = int(s.isna().sum())
        out = s.astype("datetime64[us]")
    elif pd.api.types.is_integer_dtype(s) or pd.api.types.is_float_dtype(s):
        n_null = int(s.isna().sum())
        t = s.astype("Int64").astype("string")
        if not t.dropna().str.fullmatch(P_D8).all():
            fail(f"{name}: 整数日期不是 YYYYMMDD")
        out = pd.to_datetime(t, format="%Y%m%d", errors="coerce").astype("datetime64[us]")
    else:
        t = s.astype("string").str.strip().replace("", pd.NA)
        n_null = int(t.isna().sum())
        v = t.dropna()
        if v.str.fullmatch(P_D8).all():
            fmt = "%Y%m%d"
        elif v.str.fullmatch(P_ISO).all():
            fmt = "%Y-%m-%d"
        else:
            bad = v[~(v.str.fullmatch(P_D8) | v.str.fullmatch(P_ISO))].head(3).tolist()
            fail(f"{name}: 日期格式混合或未知, 样例 {bad}")
        out = pd.to_datetime(t, format=fmt, errors="coerce").astype("datetime64[us]")
    if int(out.isna().sum()) != n_null:
        fail(f"{name}: 解析前空值 {n_null} != 解析后 NaT {int(out.isna().sum())} (存在非法日期)")
    nn = out.dropna()
    if (nn != nn.dt.normalize()).any():
        fail(f"{name}: 含非零点时间")
    return out


def dkey(s):
    return s.dt.strftime("%Y%m%d").fillna("")


def keys(df, kcol="l1_code"):
    return set(zip(df["instrument_id"], df[kcol], dkey(df["in_date"])))


def is_member(df, d):
    # out_date 口径: 含当天 (最后在任日). 成员 <=> in_date <= d <= out_date (out_date 为空 = 在任)
    return (df.in_date <= d) & (df.out_date.isna() | (d <= df.out_date))


# ---------- 读入与规范化 ----------
def _std(d, code_col, src):
    d = d.copy()
    d["instrument_id"] = d[code_col].map(norm_code)
    non_a = sorted(d.loc[d.instrument_id.isna(), code_col].astype(str).unique())
    d = d[d.instrument_id.notna()].copy()
    d["in_date"] = parse_dates(d["in_date"], f"{src}.in_date")
    d["out_date"] = parse_dates(d["out_date"], f"{src}.out_date")
    d["src"] = src
    cols = ["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new", "src"]
    return d[cols].drop_duplicates(), non_a


def verify_inputs():
    for k, (p, want) in INPUTS.items():
        if want is not None and sha(p) != want:
            fail(f"输入 {k} sha 不符: {p}")


def load_primary():
    p, want = INPUTS["primary"]
    if sha(p) != want:
        fail("主来源 89d4afa3 sha 不符")
    d = pd.read_parquet(p, columns=["instrument_id", "sw_code", "sw_name", "in_date", "out_date", "is_new"])
    d = d.rename(columns={"sw_code": "l1_code", "sw_name": "l1_name"})
    return _std(d, "instrument_id", "89d4afa3")


def load_raw_dir(raw_dir, n_files=62):
    fs = sorted(pathlib.Path(raw_dir).glob("801*.SI_[YN].parquet"))
    if len(fs) != n_files:
        fail(f"{raw_dir}: 文件数 {len(fs)} != {n_files}")
    parts = []
    for f in fs:
        l1, isn = f.stem.split("_")
        d = pd.read_parquet(f, columns=["ts_code", "l1_code", "l1_name", "in_date", "out_date"])
        d = d[d.l1_code == l1].copy()
        d["is_new"] = isn
        parts.append(d)
    return _std(pd.concat(parts, ignore_index=True), "ts_code", pathlib.Path(raw_dir).name)


def verify_raw_list(raw_dir, list_path):
    want = {}
    for line in pathlib.Path(list_path).read_text().splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            want[name.strip()] = h
    got = {f.name: sha(f) for f in sorted(pathlib.Path(raw_dir).glob("801*.SI_[YN].parquet"))}
    if got != want:
        fail(f"{raw_dir}: 文件 sha 与钉住清单不符 ({len(set(got.items()) ^ set(want.items()))} 处)")
    return got


# ---------- 冲突处理: 不删键 ----------
def resolve(m, tdays):
    # 1) 完全重复行去重 (行数闸门按去重后的唯一键计)
    # 2) 同键既有 open 又有 closed: 保留 closed, open 那行并入 (键不丢)
    # 3) 同一代码多条 open: 较旧的补 out_date = 新 open in_date 的前一交易日 (键不丢)
    m = m.drop_duplicates().reset_index(drop=True)
    conf = []
    m["_k"] = list(zip(m.instrument_id, m.l1_code, dkey(m.in_date)))
    g = m.groupby("_k")
    drop_idx = []
    for k, grp in g:
        if len(grp) == 1:
            continue
        closed = grp[grp.out_date.notna()]
        if closed.out_date.nunique() > 1:
            fail(f"同键多个不同 out_date: {k}")
        if len(closed):
            for i in grp.index[grp.out_date.isna()]:
                drop_idx.append(i)
                conf.append(dict(instrument_id=k[0], l1_code=k[1], in_key=k[2], reason="same_key_open_merged_into_closed",
                                 explain="同键已有 closed 版本; open 版本并入, 键保留"))
            for i in closed.index[1:]:
                drop_idx.append(i)
        else:
            drop_idx.extend(grp.index[1:])
    m = m.drop(index=drop_idx)
    tset = sorted(tdays)
    o = m[m.out_date.isna()].sort_values(["instrument_id", "in_date"])
    for iid, grp in o.groupby("instrument_id"):
        if len(grp) < 2:
            continue
        idx = list(grp.index)
        for a, b in zip(idx[:-1], idx[1:]):
            nxt = m.at[b, "in_date"]
            prev_td = max((t for t in tset if t < nxt), default=None)
            if prev_td is None or prev_td < m.at[a, "in_date"]:
                fail(f"{iid}: 无法为较旧 open 找到合法 out_date")
            m.at[a, "out_date"] = prev_td
            conf.append(dict(instrument_id=iid, l1_code=m.at[a, "l1_code"], in_key=m.at[a, "in_date"].strftime("%Y%m%d"),
                             reason="older_open_closed", explain=f"补 out_date={prev_td:%Y%m%d} (新 open {nxt:%Y%m%d} 前一交易日)"))
    return m.drop(columns="_k"), pd.DataFrame(conf)


def check_one_open(m):
    n = m[m.out_date.isna()].groupby("instrument_id").size()
    bad = n[n > 1]
    if len(bad):
        fail(f"open>1: {bad.index.tolist()[:20]}")


# ---------- 在市口径 (沪深 A 股, 不含 .BJ) ----------
def load_universe_frames():
    sb = pd.read_parquet(INPUTS["stock_basic"][0], columns=["ts_code", "name", "list_date", "delist_date"])
    dl = pd.read_parquet(INPUTS["delisted"][0], columns=["ts_code", "delist_date"])   # 列名在 dry-run 前以 schema 只读确认
    return sb, dl


def delist_map(sb, dl):
    a = sb[["ts_code", "delist_date"]].assign(delist_date=lambda x: parse_dates(x.delist_date, "stock_basic.delist_date"))
    b = dl.assign(delist_date=lambda x: parse_dates(x.delist_date, "delisted_v2.delist_date"))
    u = pd.concat([a, b]).dropna(subset=["delist_date"])
    return u.groupby("ts_code").delist_date.min()          # 两个来源取较早退市日


def listed_on(d, sb, dmap):
    s = sb[sb.ts_code.str.fullmatch(r"\d{6}\.(SH|SZ)")].copy()        # 明确不含 .BJ
    s["list_date"] = parse_dates(s.list_date, "stock_basic.list_date")
    s["dd"] = s.ts_code.map(dmap)
    ok = (s.list_date <= d) & (s.dd.isna() | (d < s.dd))           # 退市日当天不在市
    return set(s[ok].ts_code.map(norm_code))


def delisted_between(t0, t1, dmap):
    x = dmap[(dmap > pd.Timestamp(t0)) & (dmap <= pd.Timestamp(t1))]
    return set(x.index.map(norm_code)) - {None}


def daily_missing(t, days, sb, dmap):
    rows = []
    for d in days:
        rows.append({"date": d.strftime("%Y%m%d"), "missing": len(listed_on(d, sb, dmap) - set(t[is_member(t, d)].instrument_id))})
    return pd.DataFrame(rows)


def trading_days(lo, hi):
    cal = pd.read_parquet(INPUTS["cal"][0], columns=["cal_date", "is_open"])
    d = parse_dates(cal.loc[cal.is_open == 1, "cal_date"].astype("string"), "cal_date")
    return sorted(x for x in d if pd.Timestamp(lo) <= x <= pd.Timestamp(hi))


# ---------- 闸门 ----------
def hard_gate(new, base, kcol="l1_code"):
    # v2.0 首次写入: 基线 89d4afa3; 每个键必须保留; 唯一键数/代码数不降; 不接受任何覆盖
    kb, kn = keys(base, kcol), keys(new, kcol)
    lost = sorted(kb - kn)
    r = {"baseline": "89d4afa3", "keys": (len(kb), len(kn)),
         "codes": (base.instrument_id.nunique(), new.instrument_id.nunique()), "missing_keys": lost, "hard": True}
    r["ok"] = not lost and len(kn) >= len(kb) and r["codes"][1] >= r["codes"][0]
    return r


def soft_gate(new, base, kcol="l1_code", delisted=frozenset(), shrink_granted=False):
    # 后续刷新: 唯一键数/代码数阈值 0; 旧键子集; 当前成员扣除同期退市后降幅 <= 0.3%.
    # shrink_granted 只能来自 enforce(modes=[..., "allow_shrink"]) 通过 (即 .ok 中 allow_allow_shrink=true)
    if base is None:
        if not shrink_granted:
            fail("无已审基线; 需 allow_allow_shrink=true 的 .ok (baseline=none)")
        return {"baseline": None, "ok": True, "override": True}
    kb, kn = keys(base, kcol), keys(new, kcol)
    lost = sorted(kb - kn)
    po = set(base[base.out_date.isna()].instrument_id) - set(delisted)
    no = set(new[new.out_date.isna()].instrument_id) - set(delisted)
    bad = {}
    if len(kn) < len(kb):
        bad["keys"] = (len(kb), len(kn))
    if new.instrument_id.nunique() < base.instrument_id.nunique():
        bad["codes"] = (base.instrument_id.nunique(), new.instrument_id.nunique())
    if lost:
        bad["subset"] = {"n": len(lost), "sample": lost[:20]}
    if po and (len(po) - len(no)) / len(po) > OPEN_THRESH:
        bad["open_ex_delist"] = (len(po), len(no))
    if bad and not shrink_granted:
        fail(f"SHRINK_GATE: {bad}")
    return {"ok": True, "tripped": bad, "override": bool(bad), "delisted_between": len(delisted), "missing_keys": lost}


def info_missing_keys(new, other, kcol="l1_code"):
    # 只作报告 (0b1d3432), 不拦截
    miss = sorted(keys(other, kcol) - keys(new, kcol))
    return {"n_keys_in_other_not_in_new": len(miss), "keys": miss}


# ---------- step v2.1 增量规则 ----------
def merge_increment(base, rep):
    # 只加新键; base open 而 rep closed -> 补 out_date; 其余差异只报告不采纳
    b = base.copy()
    b["_k"] = list(zip(b.instrument_id, b.l1_code, dkey(b.in_date)))
    r = rep.copy()
    r["_k"] = list(zip(r.instrument_id, r.l1_code, dkey(r.in_date)))
    rb = r.drop_duplicates("_k").set_index("_k")
    diff = []
    for i, row in b.iterrows():
        if row["_k"] not in rb.index:
            diff.append(dict(key=row["_k"], kind="in_base_not_in_repull", adopted=False))
            continue
        ro = rb.loc[[row["_k"]]].iloc[0].out_date
        if pd.isna(row.out_date) and pd.notna(ro):
            b.at[i, "out_date"] = ro
            diff.append(dict(key=row["_k"], kind="out_date_filled", adopted=True, value=ro.strftime("%Y%m%d")))
        elif pd.notna(row.out_date) and pd.isna(ro):
            diff.append(dict(key=row["_k"], kind="repull_reopen_ignored", adopted=False))
        elif pd.notna(row.out_date) and pd.notna(ro) and ro != row.out_date:
            diff.append(dict(key=row["_k"], kind="out_date_conflict_ignored", adopted=False,
                             value=f"{row.out_date:%Y%m%d}->{ro:%Y%m%d}"))
    add = r[~r["_k"].isin(set(b["_k"]))].drop_duplicates("_k")
    for k in add["_k"]:
        diff.append(dict(key=k, kind="key_added", adopted=True))
    out = pd.concat([b, add.assign(src="repull")], ignore_index=True).drop(columns="_k")
    return out, pd.DataFrame(diff)


def increment_check(base, new):
    # v2.1 只许加键或补 out_date; 删键 / 重新打开 / 改已有 out_date 一律拒绝
    nb = new.assign(_k=list(zip(new.instrument_id, new.l1_code, dkey(new.in_date)))).set_index("_k")
    bad = []
    for _, row in base.iterrows():
        k = (row.instrument_id, row.l1_code, row.in_date.strftime("%Y%m%d"))
        if k not in nb.index:
            bad.append((k, "deleted"))
            continue
        no = nb.loc[[k]].out_date.iloc[0]
        if pd.notna(row.out_date) and pd.isna(no):
            bad.append((k, "reopened"))
        elif pd.notna(row.out_date) and no != row.out_date:
            bad.append((k, "out_date_changed"))
    return bad


def gap2_report(primary, rep):
    # 09-24..10-09 增量: rep 中 in_date 或 out_date 落在 GAP2 且与 89d4afa3 不同的键
    lo, hi = pd.Timestamp(GAP2[0]), pd.Timestamp(GAP2[1])
    hit = rep[((rep.in_date >= lo) & (rep.in_date <= hi)) | ((rep.out_date >= lo) & (rep.out_date <= hi))]
    nd = normdiff_all(primary, hit)
    return hit, nd[nd.kind != "only_a"]


def normdiff_all(a, b, kcol="l1_code"):
    # 全键比较 (含 closed 历史): only_a / only_b / out_date_diff
    x = a.assign(in_key=dkey(a.in_date), out_key=dkey(a.out_date))[["instrument_id", kcol, "in_key", "out_key"]].drop_duplicates()
    y = b.assign(in_key=dkey(b.in_date), out_key=dkey(b.out_date))[["instrument_id", kcol, "in_key", "out_key"]].drop_duplicates()
    j = x.merge(y, on=["instrument_id", kcol, "in_key"], how="outer", suffixes=("_a", "_b"), indicator=True)
    j["kind"] = j["_merge"].map({"left_only": "only_a", "right_only": "only_b", "both": "same"})
    j.loc[(j.kind == "same") & (j.out_key_a != j.out_key_b), "kind"] = "out_date_diff"
    return j[j.kind != "same"].drop(columns="_merge")


# ---------- 重拉目录独立性 ----------
def validate_repull_dir(p, signed_et, impl_date, raw0108=RAW_0108, n_files=62):
    p = pathlib.Path(p).resolve()
    if p == pathlib.Path(raw0108).resolve():
        fail("repull_dir 不能是 RAW_0108")
    m = re.fullmatch(r"index_member_all_(\d{8})_(\d{6})", p.name)
    if not m or m.group(1) != impl_date:
        fail(f"repull_dir 名称须为 index_member_all_<实施日 {impl_date}>_<HHMMSS>: {p.name}")
    if (p / "INCOMPLETE.json").exists() or not (p / "COMPLETE.json").exists():
        fail("repull_dir 不完整 (INCOMPLETE 存在或 COMPLETE 缺失)")
    fs = sorted(p.glob("801*.SI_[YN].parquet"))
    if len(fs) != n_files:
        fail(f"repull_dir 文件数 {len(fs)} != {n_files}")
    t0 = parse_tz(signed_et, "run .ok signed_et").timestamp()
    old = [f.name for f in fs if f.stat().st_mtime <= t0]
    if old:
        fail(f"repull_dir 有文件早于 run .ok 签发时间: {old[:5]}")
    want = json.loads((p / "COMPLETE.json").read_text())["files"]
    got = {f.name: sha(f) for f in fs}
    if got != want:
        fail("repull_dir 文件 sha 与 COMPLETE.json 不符")
    return got


# ---------- 已审版本指针 ----------
def read_pointer(path=POINTER):
    path = pathlib.Path(path)
    if not path.exists():
        return None
    j = json.loads(path.read_text())
    for k in ("version", "path", "sha256", "manifest", "manifest_sha256", "as_of", "built_et", "approved_by", "approved_et"):
        if k not in j:
            fail(f"指针缺字段 {k}")
    parse_tz(j["built_et"], "pointer.built_et")
    parse_tz(j["approved_et"], "pointer.approved_et")
    p = ROOT / j["path"]
    if sha(p) != j["sha256"] or sha(ROOT / j["manifest"]) != j["manifest_sha256"]:
        fail("指针指向的文件 sha 不符")
    j["df"] = pd.read_parquet(p)
    for c in ("in_date", "out_date"):
        j["df"][c] = parse_dates(j["df"][c], f"pointer.{c}")
    return j


# ---------- 原子写 ----------
def versioned(p, tag):
    p = pathlib.Path(p)
    q = p.with_name(f"{p.stem}.{tag}{p.suffix}")
    if q.exists():
        fail(f"已存在, 不覆盖: {q}")
    return q


def _pre_write(final):
    final = pathlib.Path(final)
    if final.exists() or final.resolve() in PROTECT_PATHS:
        fail(f"目标已存在或受保护: {final}")
    return final, final.with_name(f".{final.name}.tmp.{os.getpid()}")


def _link(tmp, final):
    try:
        os.link(tmp, final)                     # 不覆盖: 目标存在则 FileExistsError
    except FileExistsError:
        os.unlink(tmp)
        fail(f"竞争: 目标已出现 {final}")
    os.unlink(tmp)


def atomic_write_parquet(df, final, expect_rows, protect=None):
    final, tmp = _pre_write(final)              # sha/路径保护检查在写之前
    df.to_parquet(tmp, index=False)
    s = sha(tmp)
    if s in (protect if protect is not None else PROTECT):
        os.unlink(tmp)
        fail("产出 sha 与受保护文件相同")
    n = len(pd.read_parquet(tmp, columns=[df.columns[0]]))
    if n != expect_rows:
        os.unlink(tmp)
        fail(f"回读行数 {n} != {expect_rows}")
    _link(tmp, final)
    return s


def atomic_write_json(obj, final):
    final, tmp = _pre_write(final)
    with open(tmp, "x", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    json.loads(pathlib.Path(tmp).read_text(encoding="utf-8"))     # 回读校验
    _link(tmp, final)
    return sha(final)


# ---------- .ok 单次使用 ----------
def _marker(p):
    p = pathlib.Path(p)
    return p.with_name(p.name + ".consumed.json")


def check_unconsumed(ok_paths):
    for p in ok_paths:
        if _marker(p).exists():
            fail(f".ok 已被消费: {p}")


def consume_ok(ok_paths, info):
    for p in ok_paths:
        fd = os.open(_marker(p), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
        with os.fdopen(fd, "w") as f:
            json.dump({"consumed_et": now_et(), "ok_sha256": sha(p), **info}, f, ensure_ascii=False, default=str)


# ---------- 契约 ----------
def to_contract(m, sb, revision):
    names = sb.assign(iid=sb.ts_code.map(norm_code)).dropna(subset=["iid"]).drop_duplicates("iid").set_index("iid")["name"]
    out = m.copy()
    out["ts_code"] = out.instrument_id.map(to_ts)
    out["name"] = out.instrument_id.map(names)
    out["available_at"] = out.in_date + pd.Timedelta(hours=18)
    out["source"] = "tushare.index_member_all(SW2021)"
    out["revision"] = revision
    out["quality_status"] = "ok"
    out["promotion_approved"] = False
    out = out[[c for c, _ in CONTRACT]]
    for c, t in CONTRACT:
        out[c] = out[c].astype(t)
    return out.sort_values(["instrument_id", "in_date", "l1_code"]).reset_index(drop=True)


def validate_contract(df):
    got = [(c, str(df[c].dtype)) for c in df.columns]
    want = [(c, t if t != "string" else "string") for c, t in CONTRACT]
    if got != want:
        fail(f"schema 契约不符: {got}")


# ---------- 报告 ----------
def write_reports(od, **frames):
    od = pathlib.Path(od)
    od.mkdir(parents=True, exist_ok=False)          # dry-run 证据目录必须新建, 不覆盖旧证据
    summary = {}
    for name, obj in frames.items():
        if isinstance(obj, pd.DataFrame):
            obj.to_csv(od / f"{name}.csv", index=False)
            summary[name] = len(obj)
        else:
            (od / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
            summary[name] = "json"
    (od / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ok", action="append", required=True)
    ap.add_argument("--step", choices=["v2.0", "v2.1"], required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--repull_dir")
    ap.add_argument("--allow-shrink", dest="allow_shrink", action="store_true")
    ap.add_argument("--out_dir", default=None)
    a = ap.parse_args(argv)
    mode = ("execute" if a.execute else "dry_run") + ("_increment" if a.step == "v2.1" else "")
    modes = [mode]
    if a.allow_shrink:
        if a.step == "v2.0":
            fail("v2.0 首次写入为硬闸门, 不接受 --allow-shrink")
        modes.append("allow_shrink")                 # .ok 须 allow_allow_shrink=true
    G = enforce(__file__, a.ok, modes=modes, deps={k: p for k, (p, _) in INPUTS.items()})   # 第一件事
    if a.execute:
        check_unconsumed(a.ok)
    verify_inputs()
    kv = {o: parse_ok(pathlib.Path(o)) for o in a.ok}
    signed = max(parse_tz(v["signed_et"], f"{o}.signed_et") for o, v in kv.items())
    stamp = dt.datetime.now(ET).strftime("%Y%m%d_%H%M%S")
    od = pathlib.Path(a.out_dir or f"/tmp/sw_l1_pit_v2_{a.step}_{mode}_{stamp}")
    sb, dl = load_universe_frames()
    dmap = delist_map(sb, dl)
    tdays_all = trading_days("19900101", "20271231")
    days = trading_days(*WIN)
    prev = pd.read_parquet(INPUTS["prev_0b1d"][0], columns=["instrument_id", "l1_code", "in_date", "out_date"])
    prev = prev.assign(instrument_id=prev.instrument_id.map(norm_code),
                       in_date=parse_dates(prev.in_date, "0b1d.in_date"), out_date=parse_dates(prev.out_date, "0b1d.out_date"))
    prim, non_a = load_primary()
    raw_sha = verify_raw_list(RAW_0108, INPUTS["raw0108_list"][0])
    raw, _ = load_raw_dir(RAW_0108)
    checks_ok = True
    if a.step == "v2.0":
        if read_pointer() is not None:
            fail("已有已审版本, v2.0 不能重复写")
        m, conf = resolve(prim, tdays_all)
        check_one_open(m)
        gate = hard_gate(m, prim)
        checks_ok &= gate["ok"]
        deleted = sorted(keys(prim) - keys(m))
        conf = pd.concat([conf, pd.DataFrame([dict(instrument_id=k[0], l1_code=k[1], in_key=k[2], reason="deleted_vs_89d4afa3_baseline",
                                                   explain="v2 无此键; 须逐行说明, 闸门仍拒绝") for k in deleted])])
        base_built, rep_sha, inc_diff, g2 = None, None, pd.DataFrame(), None
        nds = {"normdiff_vs_raw0108": normdiff_all(m, raw)}       # 披露, 不拦截 (raw 只作佐证)
        if a.repull_dir:                                          # gap2 预交付: 实施前的 pull-only 重拉, 只出报告
            rep_g = validate_repull_dir(a.repull_dir, signed.isoformat(), dt.datetime.now(ET).strftime("%Y%m%d"))
            rep, _ = load_raw_dir(a.repull_dir)
            _, nds["gap2_delta"] = gap2_report(prim, rep)
            nds["normdiff_v20_vs_repull"] = normdiff_all(m, rep)
            rep_sha = rep_g
        as_of, tag = PRIMARY_AS_OF, "v2.0"
    else:
        ptr = read_pointer()
        if ptr is None or ptr["version"] != "v2.0":
            fail("v2.1 需要已审 v2.0 指针")
        if not a.repull_dir:
            fail("v2.1 需要 --repull_dir")
        impl = dt.datetime.now(ET).strftime("%Y%m%d")
        rep_sha = validate_repull_dir(a.repull_dir, signed.isoformat(), impl)
        rep, non_a_rep = load_raw_dir(a.repull_dir)
        non_a = sorted(set(non_a) | set(non_a_rep))
        base = ptr["df"][["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new", "src"]]
        merged, inc_diff = merge_increment(base, rep)
        m, conf = resolve(merged, tdays_all)
        check_one_open(m)
        bad = increment_check(base, m)
        checks_ok &= not bad
        if bad:
            conf = pd.concat([conf, pd.DataFrame([dict(key=k, reason=r) for k, r in bad])])
        base_built = parse_tz(ptr["built_et"], "pointer.built_et")
        gate = soft_gate(m, base, delisted=delisted_between(base_built.date(), dt.date.today(), dmap),
                         shrink_granted="allow_shrink" in G["modes"])
        g2_hit, g2 = gap2_report(prim, rep)
        nds = {"normdiff_v21_vs_repull": normdiff_all(m, rep), "normdiff_v20_vs_repull": normdiff_all(base, rep),
               "normdiff_v21_vs_raw0108": normdiff_all(m, raw), "gap2_delta": g2}
        as_of, tag = impl[:4] + "-" + impl[4:6] + "-" + impl[6:], "v2.1"
    out = to_contract(m, sb, tag)
    validate_contract(out)
    gap = sorted(listed_on(pd.Timestamp(WIN[1]), sb, dmap) - set(out[out.out_date.isna()].instrument_id))
    before, after = daily_missing(prev, days, sb, dmap), daily_missing(out, days, sb, dmap)
    info = {"vs_0b1d3432": info_missing_keys(out, prev)}            # 只作报告
    summary = write_reports(od, conflicts=conf, increment_diff=inc_diff,
                            daily_missing_before_after=before.merge(after, on="date", suffixes=("_before", "_after")),
                            twelve_codes_resolution=out[out.instrument_id.isin(TWELVE)],
                            source_gap=pd.DataFrame({"instrument_id": gap}),
                            non_a_share_excluded=pd.DataFrame({"code": non_a}),
                            shrink_gate={**{k: v for k, v in gate.items() if k != "missing_keys"},
                                         "missing_keys": gate.get("missing_keys", []), "info": info},
                            **nds)
    print(json.dumps({"step": tag, "mode": mode, "checks_ok": checks_ok, "out_dir": str(od), "summary": summary}, ensure_ascii=False))
    if not checks_ok:
        fail(f"检查未通过, 证据在 {od}")
    if not a.execute:
        return 0
    final = SWD / f"sw_l1_pit_{tag}.parquet"
    s = atomic_write_parquet(out, final, len(out))
    man = dict(table="sw_l1_pit", version=tag, path=str(final.relative_to(ROOT)), sha256=s, rows=len(out),
               instruments=int(out.instrument_id.nunique()), open_rows=int(out.out_date.isna().sum()),
               as_of=as_of, built_et=now_et(), out_date_semantics="inclusive: member iff in_date <= d <= out_date",
               schema=CONTRACT, dates="datetime64[us], naive, 00:00 = Asia/Shanghai 日历日",
               inputs={k: {"path": str(p), "sha256": (want or sha(p))} for k, (p, want) in INPUTS.items()},
               raw0108=dict(sha256=raw_sha, status="source_unknown (supporting evidence only)"),
               repull=dict(dir=a.repull_dir, sha256=rep_sha) if rep_sha else None,
               primary=dict(sha256=INPUTS["primary"][1], status="accepted (condition_a_met, Arch 94e91ffa)",
                            note="10-10 sha 未记录, 无法证明与 10-10 文件逐字节一致; 与 data_v2_bundle(.tar) 副本一致; 62 raw 重建 7919/7920 一致 (差 T00018 写法)"),
               time_evidence="lost: bak/0b1d3432 原始时间戳被 2026-10-18 01:13 ET 工作区恢复覆盖; 以 sha + 行级 diff 内容证据代替",
               non_a_share_excluded=non_a, source_gap=gap, n_conflicts=len(conf), gate=summary.get("shrink_gate"),
               ok_gate=G, promotion_approved=False)
    atomic_write_json(man, final.with_suffix(".manifest.json"))
    consume_ok(a.ok, {"step": tag, "out": str(final), "sha256": s})
    print("WROTE", final, s, "-> 待 Arch 审回执后由 Arch 更新指针", POINTER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
- 唯一规范化函数 norm_code 用正则白名单（P1-2）；89d4afa3、raw、重拉都先走同一函数，再求差集；T00018 之类返回 None → 剔除并记录。
- 所有安全检查用显式 raise（fail → Refuse(SystemExit)），python -O 下仍有效（P2-9）。
- 原子写：先检查目标不存在且不是受保护路径 → 写同目录 tmp → 算 sha，与 PROTECT 比较 → 回读行数 → os.link（目标存在即失败，不覆盖）→ 删除 tmp；manifest 与 COMPLETE/INCOMPLETE 同样原子写（P2-9）。
- dry-run 证据目录必须新建（exist_ok=False），不覆盖旧证据；检查不通过时**先写全部报告，再非零退出**；成功与否看退出码和 summary.json 中各项计数（P3-7）。
- 在市口径（P3-6）：沪深 6 位 A 股，**不含 .BJ**（明确写出）；list_date ≤ d 且 d < 退市日；退市日取 stock_basic 与 stock_delisted_v2 两者的较早日期；delisted_between 用同一份合并退市表。r1 中“stock_delisted_v2 的代码全部剔除、不看日期”的写法已改。
- stock_delisted_v2 的列名（ts_code、delist_date）与 89d4afa3 的 dtype 本轮未读（叶在跑，禁读数据），列入 §14 的 dry-run 前只读探查。

### 6.5 tests/test_sw_l1_pit_v2_build.py 全文（只用合成数据）
```python
# tests/test_sw_l1_pit_v2_build.py  (plan r2; 文本, 未落 repo, 未运行)
# selftest: 只用合成数据; allow_real_data=false; out_dir 在 /tmp. 先 enforce(真实签名) 再 import 被测模块.
# 运行 (仅在 selftest .ok 签发后): PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 tests/test_sw_l1_pit_v2_build.py
import sys, os, json, pathlib, tempfile
REPO = pathlib.Path("/workspace/QuantLab")
OK_PATH = REPO / "output/data/ARCH_RUN_AUTH_SELFTEST_SW_L1_PIT_V2.ok"
sys.path.insert(0, str(REPO / "scripts_eng"))
from ok_runner_pin import enforce, parse_ok
_G = enforce(__file__, [OK_PATH], modes=["selftest"],
             deps={"sw_l1_pit_v2_build": REPO / "scripts/acquire/sw_l1_pit_v2_build.py"})
_KV = parse_ok(OK_PATH)
if _KV.get("scope") != "selftest":
    raise SystemExit("selftest gate: scope must be selftest")
if _KV.get("allow_real_data", "").strip().lower() != "false":
    raise SystemExit("selftest gate: allow_real_data must be false")
_OUT = _KV.get("out_dir", "")
if not (_OUT == "mkdtemp" or _OUT.startswith("/tmp/")):
    raise SystemExit(f"selftest gate: out_dir {_OUT!r} must be mkdtemp or /tmp/<tag>")
sys.path.insert(0, str(REPO / "scripts/acquire"))
import pandas as pd
import sw_l1_pit_v2_build as B          # 只在门禁之后 import; 不调用 B.main()

COLS = ["instrument_id", "l1_code", "l1_name", "in_date", "out_date", "is_new", "src"]
TD = [pd.Timestamp(x) for x in pd.bdate_range("2019-01-01", "2026-12-31")]   # 合成交易日


def _tmp():
    return pathlib.Path(tempfile.mkdtemp(dir=None if _OUT == "mkdtemp" else _OUT))


def _df(rows):
    d = pd.DataFrame(rows, columns=COLS[:6])
    d["src"] = "t"
    d["in_date"] = B.parse_dates(d.in_date, "in")
    d["out_date"] = B.parse_dates(d.out_date, "out")
    return d


def _base(n):
    return _df([[f"sz.{i:06d}", "801010.SI", "x", "20200102", None, "Y"] for i in range(n)])


def _raises(fn, needle=""):
    try:
        fn()
    except SystemExit as e:
        if needle not in str(e):
            raise AssertionError(f"wrong refusal: {e}")
        return
    raise AssertionError("should refuse")


# --- P1-2 代码规范化 ---
def test_norm_code_variants_and_non_a():
    for v in ["600000.SH", "600000.sh", "sh.600000", "SH.600000", " 600000.SH "]:
        assert B.norm_code(v) == "sh.600000", v
    assert B.norm_code("830799.BJ") == "bj.830799"
    assert B.norm_code("T00018") is None and B.norm_code("801010.SI") is None and B.norm_code(None) is None


def test_suffix_variants_never_two_ids():
    d = pd.DataFrame([["600000.SH", "801780.SI", "银行", "20140101", None, "Y"],
                      ["sh.600000", "801780.SI", "银行", "20140101", None, "Y"],
                      ["T00018", "801780.SI", "x", "20140101", None, "Y"]],
                     columns=["code", "l1_code", "l1_name", "in_date", "out_date", "is_new"])
    m, non_a = B._std(d, "code", "t")
    assert m.instrument_id.nunique() == 1 and len(m) == 1 and non_a == ["T00018"]


# --- P2-1 / P2-2 日期 ---
def test_dates_us_vs_ns_same_keys():
    ns = pd.Series(pd.to_datetime(["2020-01-02", None]).astype("datetime64[ns]"))
    us = pd.Series(pd.to_datetime(["2020-01-02", None]).astype("datetime64[us]"))
    a, b = B.parse_dates(ns, "ns"), B.parse_dates(us, "us")
    assert str(a.dtype) == "datetime64[us]" and B.dkey(a).tolist() == B.dkey(b).tolist() == ["20200102", ""]


def test_dates_string_int_datetime_equal():
    s = B.parse_dates(pd.Series(["20200102", ""]), "s")
    i = B.parse_dates(pd.Series([20200102, None], dtype="Int64"), "i")
    iso = B.parse_dates(pd.Series(["2020-01-02", None]), "iso")
    assert B.dkey(s).tolist() == B.dkey(i).tolist() == B.dkey(iso).tolist() == ["20200102", ""]


def test_illegal_out_date_refused_not_open():
    _raises(lambda: B.parse_dates(pd.Series(["20200102", "20201399"]), "out"), "NaT")
    _raises(lambda: B.parse_dates(pd.Series(["20200102", "2020-01-03"]), "out"), "混合")


def test_tz_and_non_midnight_refused():
    _raises(lambda: B.parse_dates(pd.Series(pd.to_datetime(["2020-01-02"]).tz_localize("Asia/Shanghai")), "x"), "tz")
    _raises(lambda: B.parse_dates(pd.Series(pd.to_datetime(["2020-01-02 09:30"])), "x"), "零点")


# --- P2-3 out_date 含当天 ---
def test_out_date_inclusive():
    d = _df([["sz.000030", "801230.SI", "", "20100104", "20130628", "N"],
             ["sz.000030", "801880.SI", "", "20130701", None, "Y"]])
    assert B.is_member(d, pd.Timestamp("2013-06-28")).sum() == 1      # 出表当天仍是成员
    assert B.is_member(d, pd.Timestamp("2013-06-29")).sum() == 0
    assert B.is_member(d, pd.Timestamp("2013-07-01")).sum() == 1


# --- P2-4 冲突处理不删键 ---
def test_multi_open_closes_older_keeps_key():
    d = _df([["sz.002481", "801120.SI", "", "20111010", None, "Y"],
             ["sz.002481", "801010.SI", "", "20210730", None, "Y"]])
    m, conf = B.resolve(d, TD)
    B.check_one_open(m)
    assert B.keys(m) == B.keys(d)
    old = m[m.l1_code == "801120.SI"].iloc[0]
    assert old.out_date == pd.Timestamp("2021-07-29") and "older_open_closed" in set(conf.reason)


def test_same_key_open_and_closed_keeps_closed():
    d = _df([["sz.002420", "801110.SI", "", "20210730", "20260630", "N"],
             ["sz.002420", "801110.SI", "", "20210730", None, "Y"],
             ["sz.002420", "801230.SI", "", "20260701", None, "Y"]])
    m, conf = B.resolve(d, TD)
    B.check_one_open(m)
    assert B.keys(m) == B.keys(d) and len(m) == 2
    assert m[m.l1_code == "801110.SI"].out_date.iloc[0] == pd.Timestamp("2026-06-30")


# --- 闸门 ---
def test_first_write_hard_gate_blocks_deleted_row():
    base = _base(10)
    g = B.hard_gate(base.drop(index=3), base)
    assert not g["ok"] and len(g["missing_keys"]) == 1


def test_closed_record_is_not_shrink():
    base = _base(10)
    new = base.copy()
    new.loc[0, "out_date"] = pd.Timestamp("2026-10-01")
    assert B.hard_gate(new, base)["ok"]


def test_hard_gate_has_no_override_path():
    import inspect
    assert "shrink" not in inspect.signature(B.hard_gate).parameters


def test_info_vs_0b1d3432_does_not_block():
    base = _base(10)
    other = pd.concat([base, _df([["sz.002420", "801110.SI", "", "20100601", None, "Y"]])])
    assert B.info_missing_keys(base, other)["n_keys_in_other_not_in_new"] == 1
    assert B.hard_gate(base, base)["ok"]


def test_soft_gate_zero_threshold_and_subset():
    base = _base(1000)
    _raises(lambda: B.soft_gate(base.iloc[:999], base), "SHRINK_GATE")
    moved = base.copy()
    moved.loc[0, "in_date"] = pd.Timestamp("2021-01-04")
    _raises(lambda: B.soft_gate(moved, base), "subset")


def test_soft_gate_open_net_of_delist():
    base = _base(1000)
    new = base.copy()
    new.loc[new.index[:5], "out_date"] = pd.Timestamp("2026-10-01")
    _raises(lambda: B.soft_gate(new, base), "open_ex_delist")
    g = B.soft_gate(new, base, delisted={f"sz.{i:06d}" for i in range(5)})
    assert g["tripped"] == {}


def test_soft_gate_override_only_via_granted_mode():
    base = _base(100)
    _raises(lambda: B.soft_gate(base.iloc[:50], base, shrink_granted=False), "SHRINK_GATE")
    assert B.soft_gate(base.iloc[:50], base, shrink_granted=True)["override"]


# --- P1-3 step v2.1 增量规则 ---
def test_increment_adds_keys_and_fills_out_date_only():
    base = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"],
                ["sz.000002", "801180.SI", "", "20140101", "20200101", "N"]])
    rep = _df([["sz.000001", "801780.SI", "", "20140101", "20261020", "N"],
               ["sz.000002", "801180.SI", "", "20140101", None, "Y"],
               ["sz.000003", "801010.SI", "", "20261015", None, "Y"]])
    new, diff = B.merge_increment(base, rep)
    assert set(diff.kind) == {"out_date_filled", "repull_reopen_ignored", "key_added"}
    assert B.increment_check(base, new) == []
    assert new[new.instrument_id == "sz.000002"].out_date.iloc[0] == pd.Timestamp("2020-01-01")


def test_increment_check_refuses_delete_reopen_change():
    base = _df([["sz.000001", "801780.SI", "", "20140101", "20200101", "N"],
                ["sz.000002", "801180.SI", "", "20140101", "20200101", "N"],
                ["sz.000003", "801180.SI", "", "20140101", None, "Y"]])
    new = _df([["sz.000001", "801780.SI", "", "20140101", None, "Y"],
               ["sz.000002", "801180.SI", "", "20140101", "20210101", "N"]])
    kinds = {r for _, r in B.increment_check(base, new)}
    assert kinds == {"reopened", "out_date_changed", "deleted"}


# --- P2-10 全键 normdiff ---
def test_normdiff_all_includes_closed_history():
    a = _df([["sz.000001", "a", "", "20100101", "20150101", "N"]])
    b = _df([["sz.000001", "a", "", "20100101", "20160101", "N"]])
    assert B.normdiff_all(a, a.copy()).empty
    assert list(B.normdiff_all(a, b).kind) == ["out_date_diff"]


# --- P2-9 原子写 ---
def test_atomic_write_no_overwrite_and_protect_before_link():
    d = _tmp()
    df = pd.DataFrame({"instrument_id": ["sz.000001"]})
    f = d / "x.parquet"
    s = B.atomic_write_parquet(df, f, 1, protect=set())
    _raises(lambda: B.atomic_write_parquet(df, f, 1, protect=set()), "已存在")
    g = d / "y.parquet"
    _raises(lambda: B.atomic_write_parquet(df, g, 1, protect={s}), "受保护")
    assert not g.exists() and not list(d.glob(".y.parquet.tmp.*"))
    _raises(lambda: B.atomic_write_parquet(df, d / "z.parquet", 2, protect=set()), "回读行数")


# --- P2-7 重拉目录独立性 ---
def test_repull_dir_validation():
    root = _tmp()
    raw = root / "index_member_all"
    raw.mkdir()
    _raises(lambda: B.validate_repull_dir(raw, "2026-01-01T00:00:00-05:00", "20261020", raw0108=raw, n_files=1), "RAW_0108")
    rp = root / "index_member_all_20261020_101500"
    rp.mkdir()
    f = rp / "801010.SI_Y.parquet"
    pd.DataFrame({"a": [1]}).to_parquet(f)
    (rp / "INCOMPLETE.json").write_text("{}")
    _raises(lambda: B.validate_repull_dir(rp, "2026-01-01T00:00:00-05:00", "20261020", raw0108=raw, n_files=1), "不完整")
    os.unlink(rp / "INCOMPLETE.json")
    (rp / "COMPLETE.json").write_text(json.dumps({"files": {f.name: B.sha(f)}}))
    assert B.validate_repull_dir(rp, "2026-01-01T00:00:00-05:00", "20261020", raw0108=raw, n_files=1)
    _raises(lambda: B.validate_repull_dir(rp, "2099-01-01T00:00:00-05:00", "20261020", raw0108=raw, n_files=1), "早于")
    _raises(lambda: B.validate_repull_dir(rp, "2026-01-01T00:00:00", "20261020", raw0108=raw, n_files=1), "时区")
    _raises(lambda: B.validate_repull_dir(rp, "2026-01-01T00:00:00-05:00", "20261021", raw0108=raw, n_files=1), "实施日")


# --- P2-8 单次使用 ---
def test_ok_single_use_marker():
    d = _tmp()
    ok = d / "x.ok"
    ok.write_text("live=false\npromotion=false\n")
    B.check_unconsumed([ok])
    B.consume_ok([ok], {"t": 1})
    _raises(lambda: B.check_unconsumed([ok]), "已被消费")


# --- P2-11 契约 ---
def test_contract_columns_and_dtypes():
    sb = pd.DataFrame({"ts_code": ["000001.SZ"], "name": ["平安银行"]})
    out = B.to_contract(_df([["sz.000001", "801780.SI", "银行", "20140101", None, "Y"]]), sb, "v2.0")
    B.validate_contract(out)
    assert out.ts_code.iloc[0] == "000001.SZ" and out.name.iloc[0] == "平安银行"


if __name__ == "__main__":
    n = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
            n += 1
            print("ok", k)
    print("ALL", n, "PASS")
```
- 用例覆盖：代码后缀变体与 T00018（P1-2）；同一证券两种写法不会变成两个 id（P1-2）；us 对 ns、YYYYMMDD 字符串对 datetime、整数日期、非法 out_date、tz-aware、非零点时间（P2-1/P2-2）；out_date 含当天（P2-3）；多 open 补 out_date、同键 open/closed（P2-4）；首次写入硬闸门、补 out_date 不算缩表、删行被拦、0b1d3432 只作 info（Arch 06:57）；软闸门阈值 0、子集、扣退市、覆盖只能来自 mode（P2-8）；v2.1 只加键只补 out_date，拒绝删除/重开/改 out_date（P1-3）；全键 normdiff（P2-10）；原子写不覆盖、保护检查在 link 之前（P2-9）；重拉目录独立性（P2-7）；.ok 单次使用（P2-8）；schema 契约（P2-11）。

### 6.6 v2 schema 契约与列映射（P2-11、P2-3）
| 列 | dtype | 说明 | 0b1d3432 对应 | 89d4afa3 对应 |
|---|---|---|---|---|
| instrument_id | string | `sh.600000` 形式，唯一规范化 | instrument_id | instrument_id |
| ts_code | string | `600000.SH`，由 instrument_id 推出 | ts_code | （无，推出） |
| name | string | 取 stock_basic（2ef2d71d）的**当前**名称，不是 PIT 名称 | name | （无） |
| l1_code | string | 申万一级代码，如 801780.SI | l1_code | sw_code |
| l1_name | string | 申万一级名称 | l1_name | sw_name |
| in_date | datetime64[us] | 无时区、零点，表示 Asia/Shanghai 日历日 | in_date | in_date |
| out_date | datetime64[us] | 同上；**含当天（最后在任日）**；空 = 在任 | out_date | out_date |
| is_new | string | Y/N（来源原样） | is_new | is_new |
| available_at | datetime64[us] | in_date 18:00，无时区，表示 Asia/Shanghai 墙钟时间（近似） | available_at | available_at（不沿用，重算） |
| source | string | tushare.index_member_all(SW2021) | source | source |
| src | string | 行来源：89d4afa3 / 重拉目录名 | （新增） | — |
| revision | string | v2.0 / v2.1 | （新增） | revision |
| quality_status | string | 全部 ok（source_gap 只在清单中） | （新增） | quality_status |
| promotion_approved | bool | 恒为 False | promotion_approved | — |

- 成员判定口径：**in_date ≤ d ≤ out_date**（out_date 为空视为在任），写进 manifest 的 out_date_semantics、本契约和 daily_missing。依据：RECON CSV 显示 out_date 是最后在任日（例：000030 的 801230 止于 2013-06-28 周五，801880 自 2013-07-01 周一起）。r1 的 daily_missing 用 out_date > d，会把换行业当天算成缺失，已改；新口径与 Intel 单测“出表当天仍是成员”一致。**须通知 cs_panel 与 Intel**（由主 Agent 发）。
- 0b1d3432 的实际 dtype 本轮未读（叶在跑）；列映射按列名给出，dtype 对照在 §14 的只读探查中补齐。
- manifest 关键字段：version、as_of、built_et（tz-aware ISO，读写同名，P2-5）、out_date_semantics、schema、inputs（全部 sha）、raw0108（sha 清单，source_unknown）、repull（目录与文件 sha）、primary.note（10-10 sha 未记录）、time_evidence=lost、non_a_share_excluded、source_gap、gate、ok_gate。

### 6.7 已审版本指针（P2-5）
- 文件 data/v2/sw_pit/sw_l1_pit_APPROVED.json（l2 为 sw_l2_pit_APPROVED.json），字段：version、path、sha256、manifest、manifest_sha256、as_of、built_et、approved_by、approved_et、review_doc。时间字段一律 tz-aware ISO，读到不带时区的值即拒绝。
- **只由 Arch 在审完回执后更新**；Data 代码只读（read_pointer 校验 sha）。v2.0 写入时要求指针不存在；v2.1 要求指针指向已审的 v2.0；之后的刷新都以指针为基线。这样“之后以 v2 为基线”就有了实现路径，r1 中 OUT 固定文件名只能写一次的问题也随之消除。
- bundle 只复制指针指向的文件（§6.3）。

## 7. 执行步骤（全部在 §1 窗口内）
1. 前置（不归 Data）：Arch/Eng 把 scripts_eng/ok_runner_pin.py 提交入库。
2. 前置（Data）：叶23/24 结束后，生成 docs/v2/audit/sw_l1_pit_v2/raw0108_sha256.txt（62 行 sha，只用 sha256sum）；在一个只读 .ok 下探查 89d4afa3 / 0b1d3432 / stock_delisted_v2 / stock_basic 的 schema 与 dtype，以及 89d4afa3 中多 open、同键 open/closed 的计数（P2-4 的备选证明），结果交 Arch。
3. Arch 审本 r2，签 code-change .ok（4 个文件）。归档旧脚本到 _recovery/data/sw_l1_pit_v2_pre_<date>/，再落代码。
4. selftest .ok → 跑 selftest。
5. gap2 预交付（§5.4）：pull .ok → `sw_pit_refresh.py --pull-only --ok <pull.ok>`；dry_run .ok → `sw_l1_pit_v2_build.py --step v2.0 --repull_dir <该目录> --ok <dry.ok>`，交 gap2_delta.csv 与各 normdiff 报告。
6. v2.0：dry_run → Arch 审报告 → execute .ok → `--step v2.0 --execute` → 回执 → Arch 审过后把指针更新为 v2.0。
7. v2.1（实施日）：pull .ok → 重拉到新目录 → `--step v2.1 --repull_dir <新目录>` dry_run_increment → Arch 审 increment_diff 与各 normdiff → execute_increment .ok → 写 v2.1 → 回执 → Arch 决定是否把指针更新到 v2.1。回退见 §5.2。
8. 队列三项 sw 标 superseded；下游迁移（§13）；迁移方 .ok 重签。
- 每次运行前：pgrep 无冲突进程、MemAvailable ≥ 2GB、自查 .ok 的 expires_et 未过、signed_et 不在未来；运行中通过 /proc 看 RSS。

### 7.1 .ok 清单（P3-8）
| .ok | mode | 次数 |
|---|---|---|
| code-change（4 个文件） | — | 一次 |
| selftest | selftest（scope=selftest、allow_real_data=false、out_dir 在 /tmp） | 有效期内可重复 |
| 只读探查（§7 第 2 步） | 只读，不写 | 一次 |
| pull（gap2 预交付） | pull | 单次 |
| v2.0 dry_run | dry_run | 有效期内可重复 |
| v2.0 execute | execute | 单次 |
| 实施日 relay 重拉 | pull | 单次（重拉读真实数据，算一次运行） |
| v2.1 dry_run_increment / execute_increment | dry_run_increment / execute_increment | dry-run 可重复；execute 单次 |

- 消费归档：单次 .ok 用后在旁边生成 `<ok>.consumed.json`（含 ok 的 sha、时间、产物 sha），回执引用它；回执完成后，Data 把 .ok 连同 consumed 标记移到 output/data/ok_consumed/ 归档，不删除。

## 8. 修前修后对比（预期，执行后以实测替换）
| 交易日 | 修前缺 open L1（0b1d3432） | 修后预期（v2.0，口径 in_date ≤ d ≤ out_date） |
|---|---|---|
| 2026-09-24 | 349 | 0 |
| 2026-09-28 | 349 | 0 |
| 2026-09-29 | 349 | 0 |
| 2026-09-30 | 349 | 0 |
| 2026-10-08 | 349 | 0 |
| 2026-10-09 | 349 | 0 |
| 2026-10-12 | 349 | 0 |
| 2026-10-13 | 349 | 0 |
| 2026-10-14 | 349 | 0 |
| 2026-10-15 | 349 | 0 |
| 2026-10-16 | 349 | 0 |

- 修前的 349 是按 r1 口径（out_date > d）算的；修后按含当天口径。回执会给出两种口径下的修前数，便于对照（窗口内没有换行业时两者相同）。
- 丢失时间：235、68 以及 46 中的 33 只，是 10-14 那次覆盖丢的；46 中另外 13 只也是我方合并丢失，但发生在 10-14 之前（大约 2022-07 SW2021 调整期之后的构建），丢失机制只是推测（§12.2）。
- 12 只双开：v2.0 来自 89d4afa3，每只 1 条 open；0b1d3432 里的陈旧 open 键只出现在 info 段。
- 行数 / 代码数：修前 7573 / 5600；v2.0 预期约 7920 / 5914，再减去非 A 股（至少 T00018）。
- source_gap 预期 0 只。

## 9. 回执内容
- 两种口径下修前、修后每日缺成分（09-24..10-16）；规则原文；新文件 sha、行数、代码数、open 行数；12 只的处理明细；source_gap 与 non_a_share_excluded 清单；conflicts.csv 的计数与分类；全键 normdiff（vs raw0108；v2.1 时另有 vs 重拉）；increment_diff（v2.1）；gap2_delta（预交付）；62 个 raw 与重拉目录的文件 sha；95 与 117 对账；ALPHA_DATA_D5D6_FIX_ZH.md 中 7735 行 / is_primary 的更正；命令、时间（ET）、峰值 RSS、所用 .ok 及其 consumed 标记。

## 10. 回滚
- 所有产出都是新版本文件；回滚 = 不更新或回退指针（由 Arch 操作），下游 .ok 继续钉旧 sha；v2 文件归档到 _recovery/data/（删除需另行授权）。
- 代码回滚：从 _recovery/data/sw_l1_pit_v2_pre_<date>/ 恢复 sw_pit_refresh.py 与 nightly_update.py。恢复 nightly 的 sw 步骤须 Arch 另行同意，否则会重新引入 10-14 的失效方式。
- 队列三项只在 Arch 审过回执后改为 done；回滚时按归档恢复。

## 11. 裁定记录
- Arch 2026-10-18 06:51 ET：46 只与 235、68 同类，整个问题记 sw_pit 路径 P1；时间证据接受内容证据；队列三项并入 v2；dry-run .ok 前须交 helper 与 selftest 全文；95 只逐只追溯。
- Arch 06:53：62 raw 只作佐证；防缩表闸门原则接受。
- Arch 06:55：条件 (a) 成立，89d4afa3 为主来源；行数/代码数阈值 0 + 旧键子集 + 当前成员扣退市后 ≤0.3%；10-10 sha 未记录要写进 manifest；95/117 对账；33/13。
- Arch 06:57：首次写 v2 基线 = 89d4afa3，硬闸门，不接受 --allow-shrink；0b1d3432 只作 info；13 只丢失时间早于 10-14。
- Arch 07:04（静态审 f17f4771）：方案层面有条件通过；代码文本不通过，3 个 P1、11 个 P2 须在 r2 修订，P3 一并修订；gap2 为 Data 开放项。本 r2 即为回应。

## 12. 95 只“修复新增”代码逐只追溯（沿用 r1 只读结果，r2 未重读数据）（只读，2026-10-18 06:52:41 ET）
- 定义：当前表 0b1d3432 有、bak 59734014 没有的代码，共 95 只。
- 输出：docs/v2/audit/data_ro_audit_20261018/SW_95_NEW_CODES_TRACE.csv（sha 7f0f4f0672d8bf153aec0bc8e7e012d6e3e3f59ee8cf41206412af8da3a5cc6e）。列：ts_code, category, list_date, delist_date, list_status, in_namechange, cur_rows, cur_open_rows, cur_min_in_date, in_89d4, open_in_89d4。
- 读取文件 sha：0b1d3432…89f6、59734014…2c9c、data/v2/meta/stock_basic_incl_delisted.parquet 2ef2d71d28957b0d8d7b8a599d4fcafbecc969f121e5ee072719ad202508eca8、data/v2/st_events/namechange_all.parquet 6b81ee0b0d60d6d468910fb606ea8e4d448618c4e67fbd5337ffe0b0523fba5a、89d4afa3…f66c。
- 命令：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 -c "<pyarrow 只读 ts_code/in_date/out_date、list_date/delist_date/list_status、namechange ts_code、89d4afa3 instrument_id/out_date；集合差 + 分类，写 CSV>"`；不 import 项目代码；峰值 maxrss 164MB。

| 类别 | 数量 |
|---|---|
| 备份之后上市（list_date ≥ 20261014） | 0 |
| 代码变更 | 0（95 只都在 namechange_all 里出现，但那只是改名记录，没有代码映射；本地没有 code-mapping 数据，无法判为代码变更） |
| 来源未知 | **95** |

- 特征：95 只全部 list_status=L，上市日期 1992–2025（2022 年 20 只最多），没有新股；在当前表各 1 行且为 open；**在 89d4afa3 中全部存在且有 open 行**。
- **推测（hypothesis，非结论）**：这些是早已上市、在 89d4afa3 中有正常成分的股票，推测 **bak 自身那次拉取也被截断**，10-14 那次拉取恰好拿到了它们。若推测成立，则 0b1d3432 和 bak 都是不完整的截断拉取结果，进一步支持以 89d4afa3 / 重拉为主来源，并加防缩表闸门。v2 重建后这 95 只预计都在（normdiff 覆盖）。

- 佐证（只读核验，2026-10-18 06:56:12 ET）：按 §2 同一在市口径（stock_basic_incl_delisted + stock_delisted_v2 9d757b96，交易日取 trade_cal_sse_pit fa4260b8），**bak 59734014 自身在 09-24..10-16 每个交易日都缺 192 只**（11 天均为 192，与 Arch 的 192 一致）；同口径当前表每日缺 349。峰值 maxrss 160MB。

### 12.1 95 与 Arch 117 的对账（只读，2026-10-18 06:55:38 ET）
- 口径：**我方 95** = 当前表 0b1d3432 有、bak 59734014 没有的代码（任何记录）；**Arch 117** = 当前表有 open 记录、bak 没有 open 记录的代码。
- 重算：95 口径得 95，117 口径得 117；95 ⊂ 117（95−117 = 0），差 117−95 = **22**。
- 22 只的情况：**全部在 bak 里出现过，但只有已结束（closed）记录，bak 中 open 行数为 0**；当前表里它们的 open 记录与 bak 的 closed 记录不是同一条（行业或 in_date 不同，22/22），即当前表多出一条新的 open 成分。所以它们不是“新增代码”，但是“新增 open 成分”。
- 明细：docs/v2/audit/data_ro_audit_20261018/SW_95_vs_117_RECON.csv（sha 493f3621537133b3fb7ebaa0c30c0e5b02b027eb7f1cbaeced8747df77c6ebab），列 ts_code, category, bak_rows, bak_open, bak_records, cur_open_records。
- 22 只：000030 000059 000506 000586 000698 000839 000889 000969 001319 002017 002192 002247 002756 002796 002965 300328 300745 **300893**（.SZ，18 只）；600198 601112 603266 688102（.SH，4 只）。r1（2d9f5b8e）L653 漏列 300893.SZ（P3-4）。已用 rg 对照 CSV 493f3621 核实 CSV 里有 300893.SZ（rg -c 300893 结果为 1），CSV 无需重生成，只是正文漏抄。
- 读取 sha：0b1d3432…89f6、59734014…2c9c、ARCH_SW_L1_GAP_IMPACT_20261018_ZH.md 94e91ffa28297afd495fc519bb736b0782fc8f00707ba84a5a46d9a90adca059。命令：`PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 -c "<pyarrow 只读 ts_code/l1_code/in_date/out_date，集合比较，写 CSV>"`；峰值 maxrss 157MB。

### 12.2 46 只的 bak 核验（Arch：33 只在 bak 有 open 行）
- 核验结果：**46 只中 33 只在 bak 59734014 里有 open 行**（与 Arch 一致）；当前表里这 33 只只剩 closed 历史，说明 10-14 那次覆盖丢了它们的 open 行。这是“我方合并丢失”的佐证。
- 其余 **13 只**在 bak 里也只有 closed 记录（没有 open 行）：000537 000567 000728 000875 002200 002647 300986（.SZ）；600226 600502 600517 600674 600821 605178（.SH）。它们的 open 行在 10-14 之前的构建里就已丢失，不是 10-14 那次造成的。丢失机制**推测（hypothesis）**为全量分页截断或陈旧版本 + 无来源优先级的合并，未证实（P3-3）。89d4afa3 里 13 只都有 open 行（§3.2），所以仍属我方合并丢失，只是丢失时间更早。
- 13 只在 bak 里的记录举例：000537 为 801180，1993-12-10→2022-08-25；600226 为 801010 1999→2019-07-23、801760 2019-07-24→2022-07-28；600674 最后一条止于 2011-01-07。多数止于 2022-07 前后，和 SW2021 调整期吻合，说明 bak 缺的是 2022 年之后的新 open 成分。


## 13. 下游迁移（坏表 0b1d3432 的消费方）
v2 经 Arch 审过、指针更新后，由各 owner 自行改读 v2（建议通过指针读），迁移方 .ok 由 Arch 重签；**Data 不改他们的代码**；通知由主 Agent 负责。

| 消费方 | 位置 | Owner |
|---|---|---|
| strategy_hiliq_capadv_b4_x2.py | L72-76（load_industry_map）、L316 | Strategy |
| fulla_b4_x2 | L255 | Strategy |
| research/intel/intel_common.py | L169-172（FRESHNESS_TABLES.sw_pit：读 sw_pit/manifest.json 的 l1 键与 0b1d3432）；L309（sw_members_asof，须按 in_date ≤ d ≤ out_date 口径核对） | Intel |
| intel_event_study.py | — | Intel |
| intel_c1_gap_split.py | — | Intel |
| output/v3/beta_risk_budget_prereg/measure_baseline.py | L47-48（读 0b1d3432） | 待定：Arch 已报主 Agent 指派 |
| scripts/nightly_update.py BUNDLE_MAP | L54-58 | Data（本方案 §6.3 已改为按指针复制） |
| scripts/acquire/queue_chain_20261014.py | L130（g0 读 sw_pit/manifest.json） | Data：一次性历史脚本，不再运行，不改；版本化后原 manifest.json 保持原样 |

- **measure_baseline.py:48 以本节为准**：Arch 影响文档 94e91ffa 漏列此项（Arch 审 P3-9 已核实它在 L47-48 读 0b1d3432）。
- 不在本次迁移范围：读 89d4afa3 的消费方（g1g5、cs_panel、纸面跟踪），因为 89d4afa3 不变。
- out_date 口径（含当天）须告知 cs_panel 与 Intel（由主 Agent 发）。
- 迁移完成前 0b1d3432 原样保留，不删除、不覆盖。

## 14. 本轮未能解决的问题 / 开放项
1. **ok_runner_pin.py 未入 git**：前置条件，归 Arch 或 Eng。
2. **实际 dtype 与列名未读**：89d4afa3、0b1d3432、stock_delisted_v2（ts_code、delist_date 是否存在）、stock_basic 日期列的格式。叶23/24 运行期间禁止读数据，放到 §7 第 2 步做只读探查（需 .ok）。若与代码假设不符，代码会显式拒绝，不会静默出错；届时按探查结果修改代码，重交 Arch。
3. **89d4afa3 中多 open、同键 open/closed 的计数**（P2-4 的备选证明）：同上，探查后交。代码已经按“不删键”处理这两类情况；计数为 0 只是多一层确认。
4. **gap2（09-24..10-09）增量**：Data 开放项，实施前按 §5.4 交付。
5. **name 列**取 stock_basic 的当前名称，不是 PIT 名称；消费方如需 PIT 名称，需另议。
6. **nightly_update.py 的改动影响日更**：须在 §1 窗口内与其它变更同批落地，由 Arch 在同一 code-change .ok 中签。

## 15. 审查回应表（Arch f17f4771 → r2 章节）
| Arch 条目 | 要求要点 | r2 处理位置 |
|---|---|---|
| P1-1 运行门禁 / enforce 签名 | 各入口先 enforce(script, ok_paths, modes, deps)；改正 selftest 调用；ok_runner_pin 先入库 | §6.1（签名核对、入口与 mode 表）；§6.2、§6.4 main()、§6.5 开头；前置条件见 §6.1、§7 第 1 步、§14-1 |
| P1-2 代码规范化 | 唯一正则白名单；T00018 政策；同格式后求差集 | §4 规则 5；§6.4 norm_code/_std；§6.5 test_norm_code_variants_and_non_a、test_suffix_variants_never_two_ids |
| P1-3 10-10 之后的变化 | 两步：v2.0 as_of 10-10 / v2.1 只加键只补 out_date；FULL 钉 sha 或不用；gap2 接入 | §5.1–§5.4；§6.4 merge_increment/increment_check/gap2_report；§6.5 增量用例；§7 第 5–7 步 |
| P2-1 日期解析 | 显式 format；NaT 前后一致；datetime64[us] 零点 | §6.4 parse_dates；§6.5 日期用例 |
| P2-2 键比较 | strftime("%Y%m%d") + 规范化代码 | §6.0；§6.4 dkey/keys；§6.5 test_dates_us_vs_ns_same_keys |
| P2-3 out_date 口径 | 写死含当天；manifest/契约/daily_missing 统一；通知 cs_panel 与 Intel | §6.6；§6.4 is_member/daily_missing；§8；§13；§6.5 test_out_date_inclusive |
| P2-4 删行与硬闸门冲突 | 较旧 open 补 out_date；同键去重；行数按去重后计；或只读计数证明 | §4 规则 3；§6.4 resolve；§6.5 两个用例；§14-3 |
| P2-5 上一版本指针 / built 键 | 指针文件由 Arch 更新；tz-aware；读写同名 | §0；§6.7；§6.4 read_pointer、manifest.built_et；§6.2 l2 |
| P2-6 refresh diff | 基于 a18684fe 重生成且 hunk 正确；classify 版本化；失败非零 + INCOMPLETE；--pull-only；停用 nightly sw；修 BUNDLE_MAP | §6.2（sha 已核对，一致）；§6.3 |
| P2-7 输入钉 sha / 重拉独立 | 全部输入钉 sha（常量 + manifest）；repull_dir ≠ RAW_0108、日期 = 实施日、mtime > signed_et；sha 进回执 | §6.4 INPUTS/verify_inputs/verify_raw_list/validate_repull_dir；§5.2；§6.5 test_repull_dir_validation |
| P2-8 自造 .ok 校验 | 复用 parse_ok/enforce；精确匹配 allow_*；单次使用 | §6.1；§6.4 check_unconsumed/consume_ok；§6.5 test_ok_single_use_marker、test_soft_gate_override_only_via_granted_mode |
| P2-9 assert / 原子写 | 显式 raise；tmp → 校验 sha、PROTECT、行数 → os.link；manifest 同样原子写 | §6.4 fail/atomic_write_parquet/atomic_write_json；§6.5 test_atomic_write_no_overwrite_and_protect_before_link |
| P2-10 normdiff 只比 open | 全键 normdiff | §6.4 normdiff_all；§6.5 test_normdiff_all_includes_closed_history |
| P2-11 schema 契约 | 列、dtype、精度、时区、out_date 口径；与 0b1d3432 的列映射 | §6.6；§6.4 CONTRACT/to_contract/validate_contract；§6.5 test_contract_columns_and_dtypes |
| P3-1 陈旧文本 | L97 限定；L165、L408 删除；conditionally_accepted → accepted；source_gap 说法 | §6.0（L97 限定）；§6.4（没有“0b1d3432 闸门基线”注释和“只会增长”一句，primary.status=accepted）；§3.2 结论与 §4 规则 5 |
| P3-2 gap2 归属 | Data 开放项，实施前交 | §5.4；§14-4 |
| P3-3 推测标注 | 关闭 L629 待决项；L658 标为推测 | §12（95 只的“bak 截断”作为 hypothesis 保留，不再列为待决）；§12.2；§8 |
| P3-4 22 只少 1 只 | 补 300893.SZ | §12.1（已对照 CSV 493f3621 核实 CSV 含 300893.SZ，无需重生成） |
| P3-5 参数与目录名 | 统一 --raw_dir 与目录名 | §5.2、§7（--step v2.1 --repull_dir；目录 index_member_all_<YYYYMMDD_HHMMSS>） |
| P3-6 在市口径 | 退市按日期判断；delisted_between 用两个来源；写明不含 .BJ | §6.4 delist_map/listed_on/delisted_between 及说明 |
| P3-7 dry-run 产出与判定 | 证据目录不覆盖；不能只看退出码 | §6.4 write_reports(exist_ok=False)、先写报告再非零退出、summary.json |
| P3-8 排期与 .ok 清单 | 12-15 截止；补重拉 .ok 与消费归档规则；收窄重签范围 | §1 第 2、4 条；§7.1 |
| P3-9 §13 对比 | 补 BUNDLE_MAP、queue_chain L130、intel_common L309；Strategy 行号；89d4afa3 消费方不在范围；measure_baseline 以 §13 为准 | §13 |
| P3-10 内存 | 预估合理 | §0（保留 <300MB 预估） |
| 开放项（审查第 14 条） | gap2 实施前交 | §5.4、§14-4 |
