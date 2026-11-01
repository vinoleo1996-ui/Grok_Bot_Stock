# Arch 审查：叶23 r2.8（静态审查）

- 审查时间：2026-10-18T05:52:55-04:00
- 审查人：QuantLab Arch
- 方式：只读静态审查。没有运行项目代码，没有 import 项目模块。真实数据只用 pyarrow/pandas 读 schema 和少量行。合成小样本只在 qlvenv 里测 pandas 行为。
- 结论：**r2.8 的 3 处改动本身正确，但不能签运行 .ok。** 发现 1 个 P0：build 阶段 L671 的 merge_asof 两侧日期精度不同，会直接报错停下。要先出 r2.9。

## 1. 提交与 diff 核对

- commit 263be3281d03ad16975ca5aaee5b8a22ee950436，parent fc49e8097ac6fb723e2c4496322fef0cc6f6c844。对。
- fc49e809..263be328 只改了 research/g1g5_sue_desens_cs_alpha.py 一个文件（+9/−8）。
- 62000993..263be328 之间，这个脚本只有 263be328 这一次提交改过。
- 工作区脚本 sha256 = 1d2193acf67281a67a379411c1a43dd4947eadb0e6ab890dbc5b577dd3e09d47。
- git blob c56ed8238fe8729b1f7be77465576e7406a58aab，工作区 hash-object 一致，工作区无未提交改动。
- diff 文件 sha256 = e174b77771f94aeb3cda5a83a9040aade4455d81fc33b80d5088a580e0c1b229。对。
- 从 62000993 git archive 取出脚本（sha 3d094e22，与 _recovery/ai/pre_r2_8_0550/ 归档一致），打上 diff 后 sha = 1d2193ac。一致。
- 小瑕疵（P3）：diff 头写的是 _recovery/... 和 research/... 两个不同路径，patch -p1 找不到文件，要手动指定目标。以后 diff 头请用 a/research/... b/research/...。

## 2. 三处改动

### 2.1 CAPW（修 stage 02 的崩溃）
- 腿文件 date 列真实类型是 large_string，格式 'YYYY-MM-DD'（全部 10 位），范围 2024-01-02 到 2026-10-09。session 列也是 large_string。
- pd.to_datetime 不带 format 也能解析对：与 format="%Y-%m-%d" 结果逐行相同，0 个 NaT。
- 建议（P3）：写明 format="%Y-%m-%d"，以后格式变了会直接报错，不会悄悄猜。
- 时区：字符串无时区，转出来是无时区 datetime64[us]，与 cs_panel 的 date 一致。没有时区问题。
- 行集：按 datetime 截取 ≥ 2024-05-14 得 3,143,088 行；按原意图（字符串 ≥ '2024-05-14'）也是 3,143,088 行。一致。
- shift(1) 保留：先截到 X2S−20 天，去掉 510300 平衡行，按 instrument、date 排序，再 groupby shift(1)，最后才截到 X2S。顺序与 r2.7 相同。X2S 首日的 t−1 值取自 20 天缓冲区，没有丢。

### 2.2 P3-7：cat、ewf 用默认参数绑定
- 正确。行为不变。r2.8 跑 pyflakes 结果为 0 条。

### 2.3 P3-8：pool_benchmarks 后立即 del rr，IX 改用 r0.index
- del rr 之后到函数结尾，没有任何地方再用 rr。后面的 del 也去掉了 rr。正确。
- r0 来自 pool_benchmarks(…, rr, …)，AI 说 r0.index 与 rr.index 相同。这一点我没跑代码验证；IX 后面还会 reindex 到 U，并对首行用 seed 填，再 ffill。即便 index 有差别，也只影响披露用的 N4 排除计数，不进主结果。记为待回执核对项。

## 3. pyflakes

- 命令：PYTHONPATH=/tmp/pf python3 -m pyflakes（pyflakes 4.0.3）。
- 叶23 r2.8：0 条。
- AI 说的 'parts'、'r0' undefined 警告，实际出在**叶24**（research/g1g5_imax_intraday_alpha.py），不在叶23 r2.8：
  - L448 parts：cat 在 L449–451 被调用，都在 L451 的 del parts 之前。之后没有任何地方再调 cat。运行时不会触发。误报。
  - L710 r0（两处）：ewf 只在 L711 调用，在 L718 del r0 之前。之后不再调 ewf。运行时不会触发。误报。
  - L709 U 赋值未用：无害。
- 叶24 这三条都是 P3。建议照叶23 r2.8 的写法改成默认参数绑定，让 pyflakes 归零。

## 4. 带过滤的读取和日期 merge 全面核对

类型都取自真实 parquet 元数据。

### 4.1 叶23 r2.8

| 位置 | 文件 | 列 | arrow 类型 | 字面量/对侧类型 | 结论 |
|---|---|---|---|---|---|
| L349 read_panel | cs_panel_2018–2026 | date | timestamp[us] | datetime | 对 |
| L431–432 | universe_mask_hiliq_v1 | date | timestamp[us] | datetime | 对 |
| L506–507 | cs_panel_* | row_origin / restore_reason | large_string | str | 对 |
| L630 bench_ret | etf_daily_adj | ts_code | large_string | str | 对；trade_date 是 'YYYYMMDD' 字符串，用 format="%Y%m%d" 解析，对 |
| L646–647 | leaf19 / leaf20 alpha | date | timestamp[us] | datetime | 对 |
| L652 | capacity_adv 腿 | date | large_string 'YYYY-MM-DD' | 已无下推过滤，先转再截 | 对（r2.8 修好） |
| L567 | forecast_2024plus | ann_date / end_date | large_string 'YYYYMMDD' | 经 ymd() 去 '-' 取 8 位，format="%Y%m%d" | 对 |
| L567 | forecast_2024plus | available_at | timestamp[us, tz=Asia/Shanghai] | ymd() 取字符串前 8 位 = 上海当地日期 | 对，无时区错位 |
| L554 | financials_pit_tushare | end_date / available_at | timestamp[us] / timestamp[us, tz=Asia/Shanghai] | first_version 取字符串前 10 位 = 当地日期 | 对 |
| L422 | delisted_master | delist_date 等 | timestamp[us] | — | 对 |
| L833 | capadv BOOK target_weights | session | timestamp[us] | astype(str)[:10] 再 to_datetime | 对 |
| L832 | capadv nav.csv | _et | 'YYYY-MM-DD' | parse_dates | 对 |
| **L671 merge_asof** | event_table（fund 产物）vs cs_panel | eff vs date | **eff = timestamp[ns]；P.date = datetime64[us]** | — | **P0：报错停下** |
| L672 merge_asof | event_table_oldsel vs cs_panel | eff_o vs date | timestamp[ns] vs [us] | — | 同上，P0 |
| L680–681 merge | leaf19/20、blackout_pairs、CAPW | date | 全部 [us] | — | 对 |
| L864–865 | leaf20 weights/alpha | date | [us] / [us] | — | 对 |

**P0 的证据：**
- to_session()（L357–360）把结果写成 dtype="datetime64[ns]"。所以 event_table.eff 和 event_table_oldsel.eff 落盘是 timestamp[ns]（已读 stage 01 真实产物的 schema 确认）。
- 当前环境 pandas 3.0.6 / pyarrow 25.0.1。读 timestamp[us] 会保留 us，pd.to_datetime 也不改精度，所以 P.date 是 datetime64[us]。
- 我在 qlvenv 里只用 pandas，取真实 cs_panel_2024 的 1000 行和真实 event_table 做 merge_asof，报 MergeError："incompatible merge keys [1] dtype('<M8[us]') and dtype('<M8[ns]'), must be the same type"。
- 所以 r2.8 的 build HILIQ 会在 CAPW 之后、L671 处停下。是崩溃，不是悄悄出错，但一样会再用掉一张 .ok。
- 普通 merge 和 reindex 在 us/ns 之间能对上（实测），只有 merge_asof 严格要求同类型。
- 修法（r2.9）：to_session 用 cal 的精度（例如 dtype=cal.values.dtype，或返回前 .as_unit("us")）。同时在 build 里读 ev、evo 后显式 astype(P.date.dtype)，两边各一道。因 to_session 也在 fund 里用，fund 必须重跑。

### 4.2 叶24（research/g1g5_imax_intraday_alpha.py，当前 sha 6e46c01cd7268aa549a8d900d78c434b017b25d3cea62c3340754264c4d85c05，与送审一致）

| 位置 | 文件 | 列 | arrow 类型 | 字面量/对侧 | 结论 |
|---|---|---|---|---|---|
| L332 read_panel | cs_panel_* | date | timestamp[us] | datetime | 对 |
| L402–403 | universe_mask | date | timestamp[us] | datetime | 对 |
| L477–478 | cs_panel_* | row_origin / restore_reason | large_string | str | 对 |
| L568 | etf_daily_adj | ts_code | large_string | str | 对 |
| L580–581 | leaf18 / leaf18v alpha（HILIQ、FULLA） | date | timestamp[us] | datetime | 对 |
| L699–700 | cs_panel_* | date | timestamp[us] | datetime | 对 |
| L615、L645、L733–734、L791 merge | leaf18/18v alpha、weights、PX、自身产物 | date | 全部 [us] | — | 对 |
| L756 | capadv target_weights | session | timestamp[us] | 转字符串再解析 | 对 |

- 叶24 没有 merge_asof，没有 to_session，没有任何写死 ns 的地方。
- 叶24 在这一类上**没有 P0/P1/P2**。只有第 3 节的 3 条 P3。
- 提醒：叶24 若以后引入任何 merge_asof 或 ns 精度的中间表，按本节同样核对。

### 4.3 共用模块 g1g5_fund_resid_alpha（2b49b10b）
- rets()、bench 读 etf 用 format="%Y%m%d"，结果 [us]，reindex 到 panel 的 [us] 实测全部对上（2025 年 243/243）。
- 其中的 merge_asof 在 build() 里，叶23/24 都不调 build()。

## 5. stage 01 的残留产物

- 目录 output/ai_factory/leaf23_sue_desens_cs/ 现有 4 个文件：event_table.parquet、event_table_oldsel.parquet、blackout_pairs.parquet、fund_meta.json。
- 脚本 L917–919：目录存在且非空才拒绝；空目录可以通过，之后 mkdir(exist_ok=True)。所以清空后的已存在空目录可以复用。
- .ok 的 out_dir 必须等于 OUT_ROOT（L247），换新目录要改脚本，不划算。
- 而且这些产物是用 r2.7 脚本、ns 精度的 eff 生成的，r2.9 必须重跑 fund，不能复用。
- 建议：由 AI 在下一张 .ok 之前，把这 4 个文件移到 output/ai_factory/_void/leaf23_r2_7_stage02_stop_20261018/，附 SHA256SUMS（移动前后各算一次），留下空的原目录。我不动它们。

## 6. 下一张叶23 .ok 要改的字段

- script_sha256：改为 r2.9 的 sha（r2.8 的 1d2193ac 不签，因为 P0）。
- issued_at / expires_et：新签。避开 10-19 05:55 nightly，若跨过 nightly 必须在 nightly 之后重新实测 forecast。
- data_forecast_sha256：开签前重测。现值 f1e59284…，未变。
- 条件附件里 forecast manifest：重测。现值 0bdabc4760e22e516b24089b339596d30e739b927126d605d245834c3c7f90f3，未变。
- tool_cmds_sha256：.cmd 内容只有首行注释里记了旧 script_sha256=3d094e22，脚本不校验这一行（只校验整个文件 sha 和 CMC 行）。建议重写首行为新 sha，再按新文件 sha 签；不重写也能用，但留档不准。
- 其他字段本次实测全部与 82d79d23 一致，可原样沿用：
  - TOOLS 22 项：dep_fe 2b49b10b、selfcheck ecaa30d8、combo 5658f612、combo_legacy bee23019、adg a877cec5、lc 218b61cf、l19 hiliq 16202b2e / fulla c761dc36、l20 hiliq 4ad2984e / fulla c572d56b、l20w hiliq a812b550 / fulla acf9e9c3、capadv600 tw b010839d / nav c16638ca、capadv1000 tw b010839d / nav aba50300、forecast f1e59284、financials bc0f4c3d、etf 48b21e84、mask c5433e80、delisted 63590f23、capadv_leg 3b288c83。
  - TOOL_CLOSURE 4 项：adj_price 93b54ae7、panel_stitch 043fa68d、moneyflow ca045076、nontextbook 8a56d136。
  - cs_panel_manifest_sha256 5c44019d、prereg 8f5d8ac4、out_dir 不变。
- 白名单：OK_FIXED 19 + OK_REQUIRED 9 + TOOLS 22 + TOOL_CLOSURE 4 = 54 个键，互不重叠。r2.8 与 r2.7 相同。82d79d23 正好 54 个键，没有多也没有少。r2.9 若不改这些表，仍应是 54，签前再数一次。

## 漏审复盘

- FIX5/FIX6 审查（9907169a）漏了 stage 02 的 CAPW 过滤。原因：
  - 我只看了代码里的字面量是 datetime，默认被读的列也是时间类型，没有去读腿文件的真实 schema。
  - 叶19/20、cs_panel、mask 都是 timestamp，我把这个印象套到了 capacity_adv 腿上。它其实是字符串。
  - 我也没核 merge_asof 两边的精度。这次又发现了一处同类问题（L671）。
- 新增检查项（以后每次审查必做）：
  1. 每个带 filters= 的读取，用 pyarrow.parquet.read_schema 读真实元数据，列出列类型和字面量类型，逐个对照。字符串列还要对格式（'YYYY-MM-DD' 还是 'YYYYMMDD'）。
  2. 每个 merge / merge_asof / join / isin 的日期键，列出两侧的 dtype 和精度（us / ns）和时区。merge_asof 必须完全相同。
  3. 有写死 dtype 的地方（如 datetime64[ns]）要单独标出，追踪它流向哪里。
  4. 核对时用当前环境的 pandas / pyarrow 版本，因为精度行为随版本变。
