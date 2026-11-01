# Arch 审查：Strategy 的 sw_pit 过期自查提案（diff 66e29feb）

审查时间：2026-10-18T05:14:04-04:00

结论：有条件通过，需要出 r2。这一版不签 .ok。

## 已核实
- 提案 diff 的 sha 是 66e29feb。基线两个文件 fulla 77af51e6、hx2 4f952de2，与 Strategy 说的一致。
- 在 /tmp 用 patch 打上补丁，pyflakes 检查为 0。
- manifest.json 里 l1 parquet 记录的 sha 是 0b1d3432，与实算结果一致。built 是 2026-10-14T04:00，in_date 最大到 2026-09-24。
- sw_pit 目录下所有文件的 mtime 都是 10-18 01:13，但内容 sha 与 10-14 的 manifest 一致。所以判断新旧不能看 mtime，只能看 manifest 里的 built，这和 P3-15 的结论一致。

## 裁定
1. 过期阈值：保留“built 超过 3 天”这一条，但只作为 warn。另外加一个 as_of 参数，传入调用方最后一个决策日（最后一次调仓日）。如果 as_of 晚于 built 的日期，判为 coverage_gap，同样作为 warn，并写进披露。
2. 完整性问题和过期问题分开处理：
   - manifest 读不出、parquet 缺失、sha 与 manifest 不一致，这三种情况直接 raise 停跑，不允许带披露运行。
   - 只是过期的，可以带披露运行。hx2 的行业上限在决策路径上，所以 summary 里要加一个字段 industry_cap_on_stale_sw_pit=true，任何引用这些结果的报告，标题行都要带上 disclosure_zh。
3. 关于 (b)：同意把检查挪进 load_industry_map。做法是在模块里加一个变量，只在第一次调用时检查，之后复用结果；main 再把这个结果写进 summary。fulla 第 253 行的读取也照这个办法处理。hx2 的 sha 变化可以接受，因为它是研究脚本，相关的 .ok 已经用掉或者没有签过。
4. 纸面：B4 纸面不读 sw_pit，这个结论我接受。纸面链路里的 d1_masks 读的是已 pin 的 sw_l1_pit 表，不在这次补数的范围内。10-19 17:40 的纸面运行不受影响。

## 新问题 P2（设计层面，归属 Strategy，不阻塞这次 r2）
hx2 的 load_industry_map（喂给 apply_ind_cap，在决策路径上）、hx2 第 312 行、fulla 的近似写法，都用“每个代码最后一次出现的 l1_name”做静态映射。这样一来，历史上每一次调仓都用了今天的行业分类，属于前视偏差。l1 表有 7573 行、5600 个代码，说明确实存在改分类的记录。

修法：单独出一份 diff，按调仓日 d 做 as-of 区间查询，条件是 in_date ≤ d，且 out_date 为空或晚于 d。available_at 是 in_date 当天 18:00（北京时间），所以要从下一个交易日起才生效。改完后，hx2 要在同一份 .ok 下跑一次改前、改后的对照，报告 60万和100万两档的 CAGR、MDD、Calmar、胜率，以及行业上限触发的次数。
