# 叶24 r9 内存估算（AI，2026-10-18 ET；部分待补测）

脚本：research/g1g5_imax_intraday_alpha.py r9 sha256 `b83cb8e65ce942a600a9ce985dd471a78c622f3676759955aa4cdf5f0a4ffa53`（未提交、未运行项目代码）。
基线 r7 `c5b79efa…`；r8 `4135efba…` 已归档 `_recovery/ai/pre_r9_0627/g1g5_imax_intraday_alpha.py`（sha 4135efba…，一致）。
目标（Arch 06:27）：每个进程峰值 + 余量 < 1.3GB。**余量按主 Agent 06:30 转达的 Arch 更正取 180 MiB**（实跑比复刻高约 157 MiB；不再用 122）。

## 1. 方法
- 独立只读估算脚本（只 import numpy/pandas/pyarrow + 标准库，不 import research.* / quantlab.*；读真实 panel / mask / 叶18/18v 文件；只写 stdout；VmRSS 或 VmHWM > 1450000 kB 自杀）：
  - build：`/tmp/l23_r210_est/est24b.py`（sha 5baef5ef…），参数 `<UNI> r8|r9`；r9 模式复刻 r9 的按年读叶18/18v α、Q/ER/Ee/Lu 提前释放、trim。
  - eval：`/tmp/l23_r210_est/est24.py`（sha e0346f06…），按 universe 拆进程的复刻（FE 收益缓存预载并保留、PX 列裁剪、pick_book 只用再平衡日行、pool_benchmarks = r2.10 写法）。
- 都以 `PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python` 运行。
- **06:30 起按主 Agent 指令停止一切估算脚本**（叶23 r2.10 实跑中，单重任务）；06:30 时 HILIQ build r9 复刻被中断（日志只到 2025 imax），之后未再启动任何估算。下表“待补测”项须等叶23 跑完、主 Agent 通知后再跑。

## 2. 各阶段峰值（VmHWM，MiB；+180 = 判定值）
| 阶段 | r8 复刻 | r9 复刻 | r9 + 180 | < 1300？ | 日志 |
|---|---|---|---|---|---|
| build HILIQ | 1063 | ≥921（只测到 2025 imax，被中断） | ≥1101 | 预计是，**待补测** | e24_build_HILIQ.log 389d2d96… / e24_build_HILIQ_r9.log 371492f0… |
| build FULLA | 1320 | **1135**（2025 段 Q/ER/pivot） | **1315** | **否，超 15 MiB** | e24_build_FULLA.log 820a27fa… / e24_build_FULLA_r9.log ca04cb70… |
| eval HILIQ（拆分） | 1384（HILIQ+FULLA 同进程，1450 自杀） | 1013（拆分复刻；叠在 pb 2024 年段） | 1193 | 是 | e24_r8.log / e24_split_HILIQ.log 2e68c22b… |
| eval FULLA（拆分） | 同上 | 1262（峰在叶18 重合段，读全量 α 2,821,833 行）→ r9 改按持仓名读后**预计 ≈1097**（下一峰 = pool_benchmarks 2024 年段） | 1442 → **预计 ≈1277** | 改后预计是，**待补测** | e24_split_FULLA.log 7695db45… |
| merge | — | 只读两份 summary json，预计 < 300 | < 500 | 是 | 未测 |

说明：
- build FULLA r9 复刻**没有**包含 r9 另加的 `P.drop(columns=["logmv","adv20_yuan"])`（峰值时 P 约 2.0M 行，两列 float64 约 32 MiB）。扣掉后预计约 1103 + 180 ≈ 1283，低于 1300，但余量很薄，也没有实测。
  - **【r10 更正，Arch r9 审核 b771b4be P2-1/P3-3】** 上句两处错：logmv / adv20_yuan 在面板里是 **float32**，不是 float64（两列约 15 MiB，不是 32 MiB）；且在 pandas 3.0.6 下 drop 后的新 P 与原 4 列 float32 块共享内存，**drop 不释放任何内存**。「约 1283」作废，build FULLA 仍按 1135 + 180 = 1315 计。r10 已删去 drop，改为 Q 建好后立即做年份过滤并丢掉全量 P，见 docs/v2/AI_LEAF24_R10_MEMORY_ESTIMATE_ZH.md。
- eval FULLA 的 1262 峰在重合段：r8 读叶18 FULLA α 全表。r9 只读叶18/18v 自己权重文件里持有过的名字（实测行数：叶18 FULLA 571,917/2,821,833 = 20.3%，叶18v FULLA 259,912/2,821,833 = 9.2%；HILIQ 25.7% / 12.0%），所以这段应降到 pb 段 1097 以下。这是推算，**待补测**。
- 1.5GB 红线（1536000 kB）与 VmHWM 看门狗不变。

## 3. 未达标项与可选的进一步措施（都要 Arch 先同意，均不改定义）
1. build FULLA（1315 > 1300）：先补测带 P.drop 的 r9 复刻。仍超的话，可选：
   (a) ER→Ee/Lu 改用 `set_index(["date","instrument"]).unstack()` 代替 `pivot_table`。(date, instrument) 唯一，结果值相同，但中间 dtype 会保持 float32（pivot_table 中间结果是 float64）；imax_window 内部本来就 astype(float32)，最终数值相同。这属于中间 dtype 变化，要 Arch 判断是否算“dtype 变化”。
   - **【r10 更正，Arch r9 审核 P3-3】** 括号里的说法错：pandas 3.0.6 下 pivot_table 对 float32 值**本来就返回 float32**（Arch 合成数据实测），所以 unstack 不涉及任何 dtype 变化，也不能靠 float64→float32 省内存。
   (b) 在 Q 构建完成后先取出 year-y 过滤行（Pf），再释放全量 P。注意：之前把 Pf 放在 Q 之前的那版复刻反而升到 1370，因为 P、Pf、Q 三者同时存在，所以顺序要放在 Q 之后，并且必须实测。
2. eval FULLA：补测 r9 复刻（按持仓名过滤的读法）。

## 4. 可能改变数值的点（逐条）
- 按年读叶18/18v α（build）：P 在合并时只含 y 年、日期 ≥ gstart 的行；原来的全区间表（date ≥ X2 起点）里能匹配上的行完全一样 → 不变。
- 重合段按持仓名读 α：左连接以持仓行为键，非持仓名的行本来就匹配不上 → Jaccard、held_alpha_missing_share 不变。**没有按“只读再平衡日”实现**：Wls 覆盖全部持有日，held_alpha_missing_share 是在全部持有日上取均值，只读再平衡日会把非再平衡日的持仓行变成 NaN，从而改变这个披露数。所以用了等价的按名过滤，请 Arch 确认这个偏离。
- pick_book 只用再平衡日 α/gate 行：byd 只在 d ∈ rd 时被读 → 选股相同（与 r2.10 (b) 相同）。
- FE 收益缓存保留：与叶23 r2.10 (c) 相同（同一个 key (2024,2025,2026)、同一份数据）；Arch 在 r2.10 审核中已把它列为重点审查项，叶24 跟随审核结论。
- trim()/del/drop：只释放内存，不影响数值。
- pool_benchmarks：与叶23 r2.10 的函数逐字相同（含 r2.10 的释放顺序和 cat 改写），r2.10 审核结论直接适用。
- eval 拆分：每个 universe 一个进程，stamp 各自生成；merge 重新生成 summary_<stamp>.json 和 eval_meta.json（stage="eval"，满足 verify_leaf23_complete 式下游和敏感性链）。summary 结构变化：res 不变，另加 stamps_by_uni、auth_by_uni，peak_rss_mb_eval 改为按 universe 记录（与 r2.10 相同）。
