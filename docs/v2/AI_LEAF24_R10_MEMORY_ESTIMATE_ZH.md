# 叶24 r10 内存估算（AI，静态推算；2026-10-18 ET）

- 脚本 r10：research/g1g5_imax_intraday_alpha.py sha256 53d3f8b1fe0c9906bb7a5b855af09e979f5bfa2075be65132a1878268fff707f（未提交、未运行）。
- **本版没有跑任何复刻脚本或 schema 检查，没有读任何真实数据**（主 Agent 06:45 裁定：读真实数据的脚本都算运行，须 Arch .ok）。下面数字全部来自已有记录（r8/r9 复刻日志、叶23 r2.10 实跑日志）加上按 dtype × 行数的静态推算。
- 判定标准（Arch 07:02 更新，取代原「复刻峰值 + 180 ≤ 1300」）：复测只做 build HILIQ 和 build FULLA，用外壳跑 r10 自己的 build()；指标只看 MEMTEST_END 的 VmHWM，不加 180 MiB；> 1300 MiB 不算失败，但须停下报 Arch；硬线 VmHWM 1536000 kB。eval 不复测，以正式 eval 的看门狗加五条判定为准，exit 137 → 停、报 Arch、不重试、部分产物移 _void。
- 下面第 2–3 节的「+ 180」列是旧口径下的推算，保留作历史记录，已不是判定标准。复刻口径的数比真代码低约 157 MiB（Arch 06:30 转达），所以复刻口径的推算只作参考。
- 已更正的 dtype（Arch r9 审核 P3-3）：面板 logmv / adv20_yuan 是 float32（r9 文档误写 float64）；pandas 3.0.6 下 pivot_table 对 float32 输入返回 float32（r9 文档误写中间为 float64）。r9 文档已就地加更正注记。

## 1. 依据（已有记录）
| 记录 | 内容 |
|---|---|
| /tmp/l23_r210_est/e24_build_FULLA_r9.log（ca04cb70…） | r9 写法复刻 build FULLA：VmHWM 1135 MiB，出现在 2025 年段 Q / e_id / pivot；该复刻中全量 P 一直活到年份过滤 |
| /tmp/l23_r210_est/e24_build_HILIQ_r9.log（371492f0…） | r9 复刻 build HILIQ 只测到 2025 imax，≥ 921 MiB（06:30 停止估算时中断） |
| /tmp/l23_r210_est/e24_build_HILIQ.log（389d2d96…） | r8 写法复刻 build HILIQ：1063 MiB |
| /tmp/l23_r210_est/e24_split_HILIQ.log / e24_split_FULLA.log（2e68c22b… / 7695db45…） | 拆分 eval 复刻：HILIQ 1013 MiB；FULLA 1262 MiB（峰在叶18 重合段，全量 2,821,833 行），其次 pool_benchmarks 2024 年段 1097、PX + rr 1076 |
| docs/v2/audit/leaf23_r2_10_run/logs/A01.log、A02.log | 叶23 r2.10 实跑（pool_benchmarks 与叶24 r9 逐字相同）：HILIQ 峰 1,109,996 kB（pb 2026 年段）；FULLA pb 前 1,158,664 kB、pb 2025 年段 1,161,840 kB |

## 2. r10 相对 r9 的内存变化（静态）
1. **build：年份过滤提前到 Q 之后、e_id 循环之前，并立即丢掉全量 P（P2-1）。**
   - 全量 P（FULLA 2025：2,015,162 行；列 date(us) 8 B + instrument 字符串约 8 B 偏移 + 9 B + ret/ret_on/logmv/adv20_yuan 各 4 B(float32) + ind + col）约 45–55 B/行 → 约 85–105 MiB。
   - 过滤后的 P（FULLA 2025 过滤并 dropna 后 1,187,338 行，过滤后未 dropna 的行数没有记录，按约 1.2M 计）约 55–65 MiB。
   - e_id / pivot / imax 段净省约 30–45 MiB；但过滤那一刻 P、Q、过滤结果三者同时存在，瞬时多出约 55–65 MiB。r9 复刻的 1135 峰具体落在 Q 构建还是 ER pivot，日志不能区分（检查点只在段末）。
   - 推算 build FULLA 复刻峰值约 1095–1160 MiB，加 180 后约 **1275–1340 MiB**，**不能静态判定 ≤ 1300**，须复测。
2. **pool_benchmarks 的 B3 修复（与叶23 r2.11 逐字相同）**：每年多读 row_origin（字符串，约 1.2M 行/年，约 12–19 MiB，转成 float64 标志约 9.6 MiB 后立即丢弃字符串列）、多一个 rst pivot（约 243 × 5,467 × 8 B ≈ 10.6 MiB，加 pivot_table 临时开销）、bad_rs（bool）、sus 留到年末（+10.6 MiB）。每个 pb 年段峰值约 **+20–60 MiB**。
3. 显式空持仓 / NaN 检查：只在已读入的小权重帧上做，可忽略。

## 3. 各阶段推算
| 阶段 | 已有最佳记录 | r10 推算（复刻口径） | + 180（旧口径，仅作历史） | 处理（Arch 07:02） |
|---|---|---|---|---|
| build HILIQ | r8 1063；r9 至 2025 imax ≥ 921 | ≤ 约 1063（r9/r10 只减不增；2026 段没测） | ≤ 约 1243 | **复测 T1**（外壳，VmHWM） |
| build FULLA | r9 1135 | 约 1095–1160 | 约 1275–1340 | **复测 T2**（外壳，VmHWM） |
| eval HILIQ | 拆分复刻 1013（峰在 pb 2024 段） | 约 1033–1073 | 约 1213–1253 | 不复测；以正式 eval 看门狗加五条判定为准 |
| eval FULLA | 拆分复刻 1262；按名过滤后下一峰 pb 2024 段 1097 | pb 段约 1117–1157；重合段降到 pb 段以下（推算） | 约 1297–1337 | 不复测；以正式 eval 看门狗加五条判定为准（exit 137 → 停、报 Arch、不重试、部分产物移 _void） |
| merge | 未测，只读两份 json | < 300 | < 500 | 不复测 |

- 旁证：叶23 r2.10 实跑 FULLA pool_benchmarks 段 VmHWM 约 1135 MiB（真实进程，不需要再加复刻余量）。叶24 eval FULLA 的 pb 段代码与之逐字相同，PX 读法相同；叶24 A（2,698,355 行）与叶23 A 的大小差异没有静态记录，所以只能作参考：1135 + 20–60 ≈ 1155–1195 MiB（真实口径）。
- 结论（Arch 07:02 更新）：在叶23 A04–A27 之后、叶24 正式运行之前，只复测 build HILIQ（T1）和 build FULLA（T2）。用外壳 research/ai_memtest_l24_r10.py（87e16d71）调用 r10 自己的 build()，在草稿目录 output/ai_factory/_memtest/leaf24_r10 里跑，每项单独 .ok；步骤表 docs/v2/AI_LEAF24_R10_RETEST_PROPOSED_CMD.txt（ab688533）。复测的 build 产物不复用，正式运行重新 build，草稿目录事后整体移 _void。不再使用复刻脚本，也不写代理 α 复刻；旧复刻脚本 est24b.py、est24.py 是 r9 写法，作废不用。eval HILIQ / eval FULLA 不复测。

## 4. 备选方案（只写成文档，没有应用；超标时才由 Arch 决定是否用）
- (a) ER → Ee / Lu 用 unstack 代替 pivot_table：
  ```
  if ER.duplicated(["date", "instrument"]).any(): raise SystemExit("STOP: duplicate (date, instrument) in e_id frame — report to Arch")
  Ee = ER.set_index(["date", "instrument"])["e"].unstack().reindex(index=RW.index, columns=RW.columns)
  Lu = ER.set_index(["date", "instrument"])["lu"].unstack().reindex(index=RW.index, columns=RW.columns)
  ```
  pandas 3.0.6 下 pivot_table 对 float32 返回 float32，unstack 也是 float32，**没有 dtype 变化**，数值逐元素相同（Arch 合成数据实测）。重复键要显式报错（pivot_table 会静默取均值，unstack 会抛 ValueError，这里改成带说明的 STOP）。只能省 groupby 的中间开销，省多少要实测。
- (b) 已在 r10 实施（年份过滤提前），不再是备选。
- 仍超时上报主 Agent，不自行改口径或参数。
