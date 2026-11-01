# D1b dry-run 回执 v2（r5 代码，v2.ok，--fixes resume）
- 时间：2026-10-18 02:10:50–02:12:08 EDT；执行人：QuantLab Data；单进程，live=false，promotion=false
- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v2.ok --fixes resume`
  - 没有加 --execute。
  - 峰值 RSS 由外层 subprocess 测量，跑完读 getrusage(RUSAGE_CHILDREN)。
- 运行前自查（02:10:48）：
  - .ok sha 为 cc04d83d…，未过期（expires 2026-10-19 02:07 ET）。
  - 7 个文件的 sha 与 _recovery/data/sd1_r5_20261018/SHA256SUMS 逐一比对，全部 OK。
  - MemAvailable 约 11.5 GB。
  - ps 里没有 research/、tier1、adj_factor、bars_materialize、daily_pull 进程。
  - 本轮没有改代码。
- stdout：d1b_dryrun_stdout_20261018_v2.txt。
  - GATE_PASS step=D1b_resume_execute mode=dryrun ok_sha256=cc04d83d…
  - 末行为 "DRY-RUN PASS: nothing written"，exit 0。
- 没有出现 VOID，也没有触发不变式；2021 年起 unknown_pre_data 均为 0。

## 1. unknown：事件 × 标签
| 年 | 复牌·pre_data | 复牌·no_normal | 盘中·first_trade | 盘中·no_normal | 合计 |
|---|---|---|---|---|---|
| 2018 | 212 | 5 | 76 | 0 | 293 |
| 2019 | 2 | 0 | 136 | 5 | 143 |
| 2020 | 2 | 0 | 204 | 21 | 227 |
| 2021 | 0 | 0 | 178 | 27 | 205 |
| 2022 | 0 | 0 | 92 | 7 | 99 |
| 2023 | 0 | 0 | 59 | 12 | 71 |
| 2024 | 0 | 0 | 15 | 10 | 25 |
| 2025 | 0 | 0 | 20 | 4 | 24 |
| 2026 | 0 | 0 | 13 | 2 | 15 |

样本：
- 2018：000032.SZ、000790.SZ、002442.SZ、002697.SZ、600671.SH，日期均为 2018-01-03，标签均为 pre_data。
- 2019：000540.SZ 2019-01-02 pre_data；601860.SH 2019-01-03 first_trade；300757.SZ 2019-01-08 first_trade。
- 2022：301158.SZ 2022-01-18 no_normal；688062.SH 2022-01-19 no_normal。
- 其余年份的样本见 stdout。

### 对账
- **r3 探针（复牌类 221 行）**：本次复牌类为 2018 年 217（212+5）、2019 年 2、2020 年 2，合计 221，一致。
- **r4 预期，2018 年**：
  - 总数 293 = 复牌 217 + 盘中 76，一致。
  - 标签口径有差异。Arch 预期"种子 288 + 无正常日 5"，实际为 pre_data 212 + first_trade_in_data 76 + no_normal_session 5。
  - 原因：r4 探针把"t 之前没有任何成交"的行统一归为一类（288）。r5 按 P2-1 再拆了一层：属于种子集的记 pre_data（212，都是复牌）；不属于种子集、数据内首次成交就是盘中停牌日的记 first_trade_in_data（76，都是新股首日临时停牌）。212+76=288，与预期一致。5 行无正常日一致，都属于复牌事件。
- **r4 预期，2019 年**：
  - 总数 143 = 复牌 2 + 盘中 141，一致。
  - 138 = pre_data 2 + first_trade 136，与预期一致。无正常日 5 也一致，这 5 行都属于盘中事件，不是复牌。
- **2020 年**：复牌·pre_data 2，与 r3 一致。盘中·first_trade 204 和盘中·no_normal 21 没有先验预期，属于新增披露。
- **2021 年起**：pre_data 为 0，满足不变式。unknown 只剩盘中类，即新股首日停牌和"之前的成交日都被掩码判停牌"两类，这两类都不补回。

## 2. 补回行数（rows_added = restored）
| 年 | 补回 | 其中复牌 | 其中盘中 | fulla_carry=True | hiliq_carry=True | hiliq/fulla 置 True |
|---|---|---|---|---|---|---|
| 2018 | 990 | 959 | 31 | 990 | 296 | 0 |
| 2019 | 472 | 466 | 6 | 472 | 214 | 0 |
| 2020 | 423 | 419 | 4 | 423 | 186 | 0 |
| 2021 | 316 | 315 | 1 | 316 | 145 | 0 |
| 2022 | 280 | 278 | 2 | 280 | 151 | 0 |
| 2023 | 187 | 186 | 1 | 187 | 63 | 0 |
| 2024 | 214 | 214 | 0 | 214 | 110 | 0 |
| 2025 | 408 | 408 | 0 | 408 | 273 | 0 |
| 2026 | 289 | 288 | 1 | 289 | 183 | 0 |
| 合计 | 3579 | 3533 | 46 | 3579 | 1621 | 0 |

- 对照 Arch：2018 年 990、2019 年 472，一致。
- 9 年 v1_rows_missing_in_v2=0、v1_value_mismatch=0，v1 原有的行一行没少、数值一个没变。
- 补回行的 hiliq/fulla 一律保持 False，符合 v1 口径不变的裁定。
- 每个补回行 fulla_carry 都为 True，说明补回的前提就是 carry 已知且属于 FULLA。

## 3. sessions_walked 与 days_walked
- 代码第 179 行会算 man["sessions_walked"]，但 manifest 只在 execute 模式下写出，dry-run 的 stdout 不打印。所以这次拿不到具体值，D2 也还没跑。
- 这项核对只能留到 execute 回执里，用两份 manifest 对照。要在 dry-run 阶段核对，需要改代码让 dry-run 也打印该值，属于 Arch 决策范围；本轮没有改。

## 4. 资源与零写入
- 峰值 RSS：子进程 maxrss 为 1,373,740 KB（约 1341 MB），不超过 1.5 GB。逐年 rss_mb 最高 1342，出现在 2025、2026 年。
- 零写入确认：
  - output/ai_factory/panel_cache_v2_fixesnone、panel_cache_v2_resumefix、data/v2/suspend_flags、data/v2/ref/stock_delisted_v2.parquet 都不存在（ls 报 No such file）。
  - output/、data/ 在 .ok 之后没有新增 staging 或 VOID 文件。
  - scripts/fix_sd1 下没有 __pycache__。
- 未跑 D2、D3D4。
