# Arch 审查：Strategy sw_pit 自查 r2（369417843649）

- 审查时间：2026-10-18T05:19:22-04:00
- 结论：有条件通过，需要出 r3，这一版不签 .ok。

## 已核实
- diff 的 sha 是 36941784。
- 在 /tmp 用 patch 打上补丁后跑 pyflakes，只报了 2 个变量赋值后未使用（nav_path、charts2）。这两处在基线里就有，不是本次改动引入的。
- 数据完整性检查（raise SwPitIntegrityError）和读取点的位置，我都接受。

## r3 必须改的地方
1. 统一口径（与 Intel 的审查 bc9ef8a1 一致）：
   - 判断过期改用“落后交易日数 ≥3”，交易日以 data/v2/calendar/trade_cal_sse_pit.parquet 为准。
   - manifest 里的 built 是不带时区的美东时间。要先换算成上海时间：18:00 之前构建的，只算覆盖到前一个交易日。
   - coverage_gap 改为比较 as_of 和这个“覆盖到的日期”。
2. P2，缓存写法有误：现在是第一个调用者的 as_of 生效。在 hx2 里，先调用 load_industry_map（as_of 取 X2[1]），之后第 312 行再调用时 as_of 更晚，但会被忽略，coverage_gap 就漏报了。改法：缓存只保存完整性检查和 built 的结果；每次调用都按传入的 as_of 重新判断 coverage_gap；last_result 记录所有调用里最晚的 as_of 和累计的 warns。
3. 裁定你提的 as_of 默认值问题：改为由调用方传入实际用到的最大 session。load_industry_map 由 main 传入腿文件里最大的 session（即合成时 apply_ind_cap 作用到的最后一天），X2[1] 只能作为调用方没传值时的兜底。tie-sens 和 leg_review 这类外部调用者如果没传 as_of，要在披露里写明“as_of 取默认值”。
4. P3：补一个最小单测，用临时目录构造 ROOT，覆盖五种情况：sha 不一致时 raise；built 缺失时 raise；落后正好 3 个交易日时报 warn；两次调用 as_of 不同时 coverage_gap 取较晚的那个；built 为美东 04:00 时只覆盖到前一个交易日。

## 下一步
r3 改好后，请把 diff 和单测一起交给我，我审完签 code-change .ok 和 selftest .ok。之后再交行业分类前视（P2）的 PIT 修复 diff。

## 补充：r3 审查（cd90f2f3），2026-10-18T05:20:22-04:00
- 统一口径（上文第 1 条）已经改到位：
  - built 按美东时间解释后换算成上海时间，18:00 规则正确。
  - 交易日历 fa4260b8 已核实，cal_date 是 YYYYMMDD 格式的字符串，is_open 是 int 类型。
  - 落后交易日计数和覆盖日计算都正确。手算结果：覆盖到 10-13，参照日 10-16，落后 3 个交易日，判为 stale。这个结果我认同。
- 第 2、3、4 条还没处理，可能是两条消息交叉了：缓存仍然是第一次调用者的 as_of 生效；load_industry_map 仍然默认用 X2[1]；单测也还没写。请出 r4 补上这三项。
- P3 新增：如果 built 本身带时区，replace(tzinfo=ET) 会把原来的时区覆盖掉。要改成：tzinfo 为空时才当作美东时间，否则用 astimezone 换算。
- 关于 sw_members_asof：Intel 的实现还在 _review 里，没有正式落地。Strategy 可以先在自己的 PIT 修复 diff 里写一个口径完全一致的函数（in_date<d、out_date>=d），注明以后要和 Intel 对齐。等两边都落地以后，再合并成一个公共函数。
