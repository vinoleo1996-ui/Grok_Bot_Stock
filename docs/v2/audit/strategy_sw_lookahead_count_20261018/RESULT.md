# Strategy：SW L1 前视（look-ahead）代码-天统计（只读）
- 作者：QuantLab Strategy；Arch 要求；2026-10-18 ET。
- 只读：pandas 直接读 parquet，没 import 任何项目代码，没跑测试/项目脚本，没写 research/ 或 output/。脚本和输出在 /tmp/swlk，本目录是副本。
- 运行：`cd /tmp/swlk && python3 -B sw_lookahead_count.py --out /tmp/swlk/out`，2026-10-18 07:04:39–07:05:13 EDT，rc=0，30.5 s，pandas 3.0.6。
- 脚本 sha256：f6ed68edeff8c4b6773ded2659e6513ec88c4d55651a52de35c67fb4aa68ea9e（本目录 sw_lookahead_count.py；07:03:37 先跑过一次 aeefc522 版，只少 ref_unknown_* 和 pit 对比代码列表两项，结果已被本次覆盖）。
- 依据：Data 盘点 docs/v2/audit/data_ro_audit_20261018/SW_IMPACT_INVENTORY_ZH.md（sha 415f0783ea19…，已核）：BAD = data/v2/sw_pit/industry_members_sw_l1_pit.parquet，CLEAN = data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet。

## 输入 sha256
| 文件 | sha256 |
|---|---|
| data/v2/sw_pit/industry_members_sw_l1_pit.parquet（BAD） | 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6 |
| data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet（CLEAN） | 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c |
| data/v2/calendar/trade_cal_sse_pit.parquet | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 |
| output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet | 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d |
| output/strategy_hiliq/legs/g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet | 6bb3b3f3160eafce410079ac49203faed609f9d722a55b9ef6f15c82af6d69e0 |
| output/strategy_hiliq/legs/g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet | c4b93255b694adb9b0484e55413abf80072be1e48d750e25a39dc4e37917b5e2 |
| output/strategy_hiliq/b4/B4_50_25_25_topN_60w.parquet | ca77bc8cf05a8cc5665a0532ce5221e05f3d0431cf87ee614c7779064cad627a |
| output/strategy_hiliq/b4/B4_50_25_25_topN_100w.parquet | f75ace33da3e919e799ee1e63fd141ed6d34b3b2a509d7bdf7659ab05849e315 |
| data/v2/valuation/daily_basic_full_tushare.parquet（只读 ts_code, trade_date） | f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948 |

## 口径
- 窗口 X2 = 2024-06-03..2026-10-09（570 个开市日）；全部代码-天都落在开市日（n_keys_not_open_day = 0）。
- 旧口径：照抄 hx2 load_industry_map（`sort_values("in_date").groupby("ts_code").tail(1)`，不看 out_date），在 BAD 上。
- PIT：in_date < d 且（out_date 为空或 >= d）。多于一条有效行时按固定顺序取一条（in_date 最新 -> is_new=Y -> out_date 空 -> 文件靠后），同时记为双开。纯规则，没加改分类空档日沿用 1 天。
- CLEAN 适配：instrument_id `sz.000001` -> `000001.SZ`，sw_name 当 l1_name；7920 行中有 1 行 instrument_id 格式坏（`Tsh.00018`），保留原样，匹配不到任何代码。CLEAN 与 BAD 的 31 个一级行业名、代码完全一致。
- 范围：
  - 合成书 = B4 三条腿（weight>0、非 ETF、三腿共同 session）与 B4 60w/100w 持仓的并集；这是 apply_ind_cap 可能查到的代码-天上界。
  - B4 60w / 100w = 实际持仓（非 ETF），另给权重占比。
  - 当天全部在市 = daily_basic_full_tushare 当天有记录的非 ETF 代码；停牌日没有记录，不计入。
- “含未知的不一致”把未知当 `_UNK_` 比较，就是 apply_ind_cap 实际看到的差异。

## 结果
| 口径 | 代码-天 | 代码 | 对比 | 两边都有行业但不同：代码-天 / 代码 / 占比 | PIT 未知（旧口径有）：代码-天 / 代码 | PIT 未知合计：代码-天 / 代码 / 占比 | 旧口径未知（PIT 有）：代码-天 / 代码 | 含未知的不一致（apply_ind_cap 看到的）：代码-天 / 代码 / 占比 | 权重占比（不同 / 含未知）|
|---|---|---|---|---|---|---|---|---|---|
| 合成书（3 腿 + B4 60w/100w 并集） | 34138 | 881 | 旧(BAD) vs PIT(BAD) | 486 / 18 / 1.42% | 477 / 15 | 2501 / 71 / 7.33% | 0 / 0 | 963 / 33 / 2.82% | — |
| 合成书（3 腿 + B4 60w/100w 并集） | 34138 | 881 | 旧(BAD) vs PIT(CLEAN) | 900 / 29 / 2.64% | 1 / 1 | 1 / 1 / 0.00% | 2024 / 56 | 2925 / 86 / 8.57% | — |
| 合成书（3 腿 + B4 60w/100w 并集） | 34138 | 881 | PIT(BAD) vs PIT(CLEAN) | 31 / 1 / 0.09% | 0 / 0 | 1 / 1 / 0.00% | 2500 / 70 | 2531 / 71 / 7.41% | — |
| B4 60w 实际持仓 | 9854 | 415 | 旧(BAD) vs PIT(BAD) | 129 / 11 / 1.31% | 134 / 10 | 692 / 30 / 7.02% | 0 / 0 | 263 / 21 / 2.67% | 1.00% / 2.11% |
| B4 60w 实际持仓 | 9854 | 415 | 旧(BAD) vs PIT(CLEAN) | 247 / 20 / 2.51% | 1 / 1 | 1 / 1 / 0.01% | 558 / 20 | 806 / 41 / 8.18% | 1.97% / 8.02% |
| B4 60w 实际持仓 | 9854 | 415 | PIT(BAD) vs PIT(CLEAN) | 23 / 1 / 0.23% | 0 / 0 | 1 / 1 / 0.01% | 691 / 29 | 714 / 30 / 7.25% | 0.19% / 7.32% |
| B4 100w 实际持仓 | 16146 | 576 | 旧(BAD) vs PIT(BAD) | 241 / 12 / 1.49% | 224 / 13 | 1237 / 48 / 7.66% | 0 / 0 | 465 / 25 / 2.88% | 1.10% / 2.24% |
| B4 100w 实际持仓 | 16146 | 576 | 旧(BAD) vs PIT(CLEAN) | 440 / 22 / 2.73% | 1 / 1 | 1 / 1 / 0.01% | 1013 / 35 | 1454 / 58 / 9.01% | 2.12% / 9.58% |
| B4 100w 实际持仓 | 16146 | 576 | PIT(BAD) vs PIT(CLEAN) | 29 / 1 / 0.18% | 0 / 0 | 1 / 1 / 0.01% | 1236 / 47 | 1265 / 48 / 7.83% | 0.14% / 8.71% |
| 当天全部在市（daily_basic 有记录） | 3090198 | 5660 | 旧(BAD) vs PIT(BAD) | 56927 / 182 / 1.84% | 27585 / 285 | 204745 / 604 / 6.63% | 0 / 0 | 84512 / 318 / 2.73% | — |
| 当天全部在市（daily_basic 有记录） | 3090198 | 5660 | 旧(BAD) vs PIT(CLEAN) | 75466 / 215 / 2.44% | 1656 / 249 | 1829 / 251 / 0.06% | 176987 / 318 | 254109 / 627 / 8.22% | — |
| 当天全部在市（daily_basic 有记录） | 3090198 | 5660 | PIT(BAD) vs PIT(CLEAN) | 2843 / 5 / 0.09% | 10 / 9 | 1829 / 251 / 0.06% | 202926 / 364 | 205779 / 378 / 6.66% | — |

| 口径 | BAD 双开：代码-天 / 代码 / 跨行业代码 | CLEAN 双开 |
|---|---|---|
| 合成书（3 腿 + B4 60w/100w 并集） | 98 / 3 / 2（002597.SZ, 300777.SZ, 688002.SH） | 0 / 0 |
| B4 60w 实际持仓 | 33 / 2 / 2（002597.SZ, 300777.SZ） | 0 / 0 |
| B4 100w 实际持仓 | 66 / 3 / 2（002597.SZ, 300777.SZ, 688002.SH） | 0 / 0 |
| 当天全部在市（daily_basic 有记录） | 8522 / 18 / 14（000016.SZ, 000408.SZ, 000639.SZ, 002420.SZ, 002481.SZ, 002597.SZ, 002719.SZ, 003030.SZ, 300699.SZ, 300741.SZ, 300777.SZ, 300858.SZ, 300972.SZ, 301087.SZ, 302132.SZ, 603020.SH, 605077.SH, 688002.SH） | 0 / 0 |

要点：
- 合成书口径：旧口径与 PIT(BAD) 行业不同 486 代码-天 / 18 代码（1.42%）；PIT(BAD) 查不到而旧口径有 477 / 15；PIT(BAD) 未知合计 2501 / 71（7.33%）。换 CLEAN 后 PIT 未知只剩 1 个代码-天（601127.SH 2024-07-30，疑为改分类空档日，纯规则不沿用）。旧口径与 PIT(CLEAN) 不同 900 / 29（2.64%）。
- 旧口径在 BAD 上本身就有 2024 个代码-天 / 56 个代码查不到（这些代码不在 BAD 里，CLEAN 有），所以含未知的不一致是 2925 / 86（8.57%）。
- 典型前视：688002.SH 2025-03-20..2026-03-31 旧口径用了 2026-08-21 才生效的“电子”，PIT 是“国防军工”；600346.SH、000703.SZ 旧口径用“基础化工”，PIT 是“石油石化”。逐行明细见 synth_mismatch_rows.csv。
- PIT(BAD) 与 PIT(CLEAN) 都有行业但不同的只有 002597.SZ（31 代码-天）：BAD 的“食品饮料”行没有 out_date，双开取了“食品饮料”；CLEAN 是 2021-07-30 起“基础化工”。
- CLEAN 在所有范围内都没有双开。

## 双开 18 个 vs 12 个（BAD）
- 18 = X2（2024-06-03..2026-10-09）内任意一天、BAD 全部代码里出现过 >1 条有效行的代码；在当天在市（daily_basic）的限制下也是 18；其中跨行业 14 个。
- 12 = 2026-09-24..10-16 每个开市日都双开的代码，与“两条 out_date 均为空”的 12 个、Data A_12codes_open_records.csv 完全一致：002420, 002481, 002597, 003030, 300699, 300741, 300777, 300858, 300972, 603020, 605077, 688002。
- 多出的 6 个在 09-24 之前已经结束双开：000016.SZ（至 2024-07-29，同行业）、000408.SZ（至 2026-06-30，跨行业）、000639.SZ（至 2024-07-29，跨行业）、002719.SZ（至 2024-07-29，同行业）、301087.SZ（至 2026-08-20，同行业）、302132.SZ（至 2026-08-20，同行业）。
- 结论：两个数口径不同，并不矛盾。12 指“表尾（09-24 至 10-16）双开”，18 指“X2 内曾双开”。X2 每天双开的代码数在 11–18 之间。真正落在 hx2 合成书代码-天上的只有 3 个（002597、300777、688002；98 代码-天）。

## 文件
RESULT.md、sw_lookahead_count.py（脚本副本）、result.json（全部数字和双开清单）、synth_mismatch_rows.csv（合成书口径逐行不一致）、run.log、SHA256SUMS。
