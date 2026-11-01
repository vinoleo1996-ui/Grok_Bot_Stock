# Arch 审查：叶23 r2.9 与叶24 r7（静态审查）

- 审查时间：2026-10-18T05:55:22-04:00
- 审查人：QuantLab Arch
- 方式：只读静态审查。没有运行项目代码，没有 import 项目模块，没有移动文件。复现用 qlvenv 里的 pandas 3.0.6 / numpy 2.5.3 / pyarrow 25.0.1，只读真实数据。
- 前一份：docs/v2/ARCH_AI_LEAF23_R2_8_REVIEW_ZH.md（6bf4e1b5）。
- 结论：**叶23 r2.9 通过**，可以签运行 .ok（草稿见第 5 节）。**叶24 r7 通过**（代码层面；运行 .ok 另签）。没有 P0/P1/P2。

## 1. 文件与 diff 核对

- 两个文件都在工作区、未提交。改前文件在 _recovery/ai/pre_r2_9_r7_0555/：叶23 1d2193ac（= r2.8），叶24 6e46c01c（= r6）。
- 叶23 r2.9：sha d199b778e6a50c345a761c6f1f1f1b699b461b486479c88cbca880e4e02eabf0。diff 6b3fca47cd5369d36e56b257ee3f4f088599e2787ac614cb44463f11f59b6d01。
- 叶24 r7：sha c5b79efa70b6d0eab0ea4d3edf22554357a35fcd98cf515323cc407898525fc1。diff 6794e8d0febac3c4bf7c0930b243f9855c83d063e6c79fc0b1decfc61ce85f46。
- 两个 diff 头都已改成 a/research/... b/research/...，patch -p1 干净打上，结果 sha 分别是 d199b778、c5b79efa。一致。
- git diff HEAD -- research/ 只有这两个文件（+7/−6）。
- 预注册未变：叶23 r2.1 8f5d8ac4；叶24 c289e770。
- pyflakes 4.0.3：两个文件都是 0 条。py_compile（输出到 /tmp，已删）：都通过。

## 2. 叶23 r2.9 精度路径

改动：to_session 的 NaT 数组改用 cal.values.dtype；build 里 merge_asof 前把 ev.eff、evo.eff_o 转成 P.date.dtype；CAPW 写明 format="%Y-%m-%d"。

端到端复现（行内重写 calendar、ymd、to_session，不 import 项目代码）：
- calendar：真实 cs_panel 2023–2026，dtype datetime64[us]，913 个交易日，2023-01-03 到 2026-10-14。与 P.date 精度相同。
- 用真实 forecast 的 available_at 走 day1 → eff（+20）：新版 eff 是 [us]，旧版是 [ns]。非 NaT 值逐个相等；NaT 都是 125 个，位置一致。
- 新 eff 写 parquet 再读回：timestamp[us] → datetime64[us]。所以重跑 fund 会写 us。
- 用 stage 01 真实产物（eff 是 ns，0 个 NaT）和真实 cs_panel_2025（1,204,703 行，[us]）：astype 到 [us] 无损（转回 ns 全等），仍然有序。两次 merge_asof 都成功：eff 匹配 1,204,703 行，eff_o 匹配 1,194,076 行，没有 eff 晚于 date 的情况。之后的 (date − eff).dt.days 正常。
- 所以 r2.9 对旧的 ns 表和新的 us 表都能跑。

eff / eff_o 的产生和使用（全部核过）：
- 产生：L558 formal eff、L574 forecast eff、L573 day1，都来自 to_session → 现在都是 cal 精度 [us]。
- fund 内部比较：peff < day1、f4 <= eff、f1 <= eff，两边都出自 to_session，精度相同。L545 toordinal、L603 searchsorted 与精度无关。
- 落盘：L597 event_table_oldsel、L607 event_table → us。blackout_pairs 的 date 取自 cal → us。
- build：L641–642 读入，L671 转成 P.date.dtype，L672–673 merge_asof，L675、L680 做日期差。一致。
- eval：不读 eff / eff_o。

NaT：
- to_session 先全填 NaT，只在 ok 位置写值，NaT 的位置不变。
- astype 在 ns→us 时保留 NaT（实测）。fund 末尾已 dropna(subset=["eff"])，表里本来就没有 NaT。astype 没有掩盖任何问题。

P3（不阻塞）：
- np.full(..., np.datetime64("NaT"), dtype=...) 在 numpy 2.5.3 下有 DeprecationWarning（通用单位的 NaT），旧版也有。将来 numpy 可能报错。下一轮改成 np.datetime64("NaT", "us") 或 np.full(len(i), np.datetime64("NaT"), dtype=cal.values.dtype) 前先 np.array("NaT", dtype=cal.values.dtype)。
- ev/evo 的 astype 放在年循环里，每年重复一次，无害；放到循环前更清楚。

## 3. 叶24 r7

- 改动：cat、ewf 用默认参数绑定；去掉没用的 U；pool_benchmarks 之后立即 del rr，后面的 del 去掉 rr。del rr 之后再没用到 rr，ewf 用 _r。正确。
- 全文件没有写死 ns，没有 merge_asof，没有 to_session。
- L474：after = idx.values[:, None] > DatetimeIndex(last.values).values[None, :]。
  - numpy 比较不同单位的 datetime64 时，先转成共同的更细单位再比，不是按整数直接比。实测：us 的 2025-03-03 > ns 的 2025-03-02T23:59:59.999999999 结果为 True。
  - 用真实 calendar 和一个模拟 last（含 None→1970-01-01 的填充）对比"全部转 ns 再比"，结果逐元素相同。语义正确，不只是不报错。
  - 实际上 idx 和 last 都是 [us]，没有混用。
- pandas 中不同单位的 Series 比较、Series 与 Timestamp 比较：实测都正常，不会报错。只有 merge_asof 要求同一类型，叶24 没有。
- 与上次（r2.8 审查第 4.2 节）相同，叶24 带过滤读取全部类型匹配。

## 4. 等级汇总

- P0 / P1 / P2：无。
- P3：to_session 的 NaT DeprecationWarning（叶23）；astype 可移到循环外（叶23）。叶24 无。
- 待回执项（沿用）：r0.index 与 rr.index 相同（叶23 N4 披露用）。

## 5. 叶23 r2.9 运行 .ok 草稿（未安装）

- 目录 _review/leaf23_r2_9_ok_draft/：
  - ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok.draft：sha 见报告，54 个键，LF，每行 ^[a-z0-9_]+=\S+$，键顺序同 82d79d23。
  - ARCH_TOOL_CMDS_LEAF23_X2.cmd：只改首行注释（written_at 和 script_sha256=d199b778…），其余与 19db13cc 逐字相同。sha 493cc03c280be625ad96b9c6f26b45f5f78b74f2ccf03e73741e576d79d82578。
- 与 82d79d23 相比只改 3 个键：
  - script_sha256 = d199b778e6a50c345a761c6f1f1f1b699b461b486479c88cbca880e4e02eabf0
  - tool_cmds_sha256 = 493cc03c280be625ad96b9c6f26b45f5f78b74f2ccf03e73741e576d79d82578
  - issued_at = 新时间；expires_et 仍为 2026-10-19T04:30:00-04:00（值未变）。
- 重测后不变：forecast f1e59284、forecast manifest 0bdabc47、TOOLS 22 项、TOOL_CLOSURE 4 项、mask c5433e80、panel manifest 5c44019d、prereg 8f5d8ac4。live=false，promotion=false，promotion_approved=false。
- 安装注意：
  - tool_cmds_path 是固定值 output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd，脚本按这个路径算 sha。安装时要先把旧 .cmd（19db13cc）归档，再把新 .cmd 放到这个路径。否则 tool_cmds_sha256 对不上，脚本会拒绝。
  - 安装前把 issued_at 改成实际签发时间，重测 forecast 和 manifest。
  - stage 01 残留产物要先按上次建议移到 _void 并留 SHA256SUMS，fund 才能在空目录重跑。
