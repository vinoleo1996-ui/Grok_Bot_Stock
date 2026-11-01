# 驱动差异说明：run_nightly_v1.py predraft2（a7292a61）→ v3（63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16）

- 作者：QuantLab Data；2026-10-18 13:02 ET。行号均指新驱动 docs/v2/audit/nightly_20261019/run_nightly_v1.py（63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16，1423 行）。
- 旧版归档：_recovery/data/nightly_20261019/predraft2_20261018T114300/run_nightly_v1.py（a7292a61…，SHA256SUMS 同目录）；另一份 predraft3_20261018T125243/。
- 统一 diff：DRIVER_DIFF_vs_predraft2_20261018T130216.diff（12727b8fa591c0705f25439a416a3bc5503a655e9b199c0ae6a55e3780fcba87）。新增兜底 routine_fallback_v1.py（f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f）。
- 测试：DRIVER_TEST_RECEIPT2_20261018T130216_ZH.md（全部 /tmp 假文件、假进程）。
- 依据：Arch 设计审查 docs/v2/ARCH_DATA_NIGHTLY_V1_DESIGN_REVIEW_ZH.md（2dada5ed）§5 第 1–17 项与 §6；Arch 12:16 / 12:24 / 12:36 / 12:38；主 Agent 12:32（1）–（4）；Eng 12:34 / 12:40。
- 未改动：tushare_proxy.py（ae91f230）、tier1_pull.py（5b70dfed）、nightly_update.py 及全部步骤脚本（Eng 所有）。

## 1. Arch §5 十七项逐条对照（驱动行号）
| # | Arch 要求（摘） | 实现位置 | 说明 / 测试 |
|---|---|---|---|
| A1 | 两档 30 分钟 daily_pull 硬停；call B 在 min(起跑 + 预算, 16:00) 硬停判 FAILED；不跨 16:40；无 06:20 / 06:30 | L86、L87、L1228（call A 时间盒）；L1278（闸门）；L1288–L1289（硬停 CALLB_TIMEOUT）；L495（16:40 BLACKOUT）；L1292（被停即 fail） | CLI 已删 cutoff / latest 参数；预算来自 .ok call_b_budget_min（1..120，L685）。T15、T17 |
| A2 | 停止顺序：SIGSTOP 父 → 重新枚举 → 冻结后代 → 最深 TERM + CONT → 限时等 → KILL → 父 → 孤儿扫描；确切 PID + cmdline + PPID；call A 认 scripts/acquire/，call B 认完整相对路径 | stop_tree L315：SIGSTOP_PARENT L322，重新枚举 L323，冻结 L326，最深 TERM+CONT L327，KILL 父 L339；wait 限时 L502；孤儿扫描 L346；signal_exact L297；标记 L103 / L104 | 拒发 / 杀不掉记 residual → 不重试、不起 call B（L1247）。T11–T14 |
| A3 | 所有子进程 / wait 带超时；顶层 try/except BaseException + 信号处理；统一收尾（停树、恢复日历、双核、回执、单一 FAILED） | run_tool L442（超时 = min(工具默认, 阶段剩余, 距 16:40)，L450）；pgrep timeout L383；信号 L1369–L1376；统一收尾 L1391–L1419；finish L1083 | 退出码：统一异常收尾 = 11（L1080），只读预检通过 = 10（L1079）。**与 Arch 原文“exit 10”冲突，见第 9 节 Q-1。** T10、T16 |
| A4 | 结构化 reason_code；只有 MAX_RUN 可重试 | RETRYABLE L111；reason_code 产生于 stop_tree（L342）、HANG（L506）、ATTEMPT_FAILED（L1242）、CALLB_GATE、P0、SIGNAL / TOOL_TIMEOUT / EXCEPTION（L1393）；重试判定 L1249 | marker 写 reason_codes（L1019）。T18 |
| A5 | 超时一节：connect / read / overall、页大小、file:line | 本文第 2 节 | 子进程环境 L100、L101 |
| A6 | /tmp 自测：hang、SIGTERM、call B 超时、孙进程、RSS 不重试、旧 summary、两种 last_date、.ok 四类拒绝 | tdrv5.py / thang2.py | 见测试回执（T01–T19） |
| B7 | 恢复前确认树已不在；compare → restore → 30 秒双核；每次尝试后、call B 后、收尾、异常路径；rc=2 复跑一次 | tree_gone L522；compare_restore L864（rc=2 复跑 L891；失败 / 超时走自带原子恢复 L898；双核 L899）；调用点：每次尝试后 L1232，call B 后 L1298，异常路径 L1409；收尾 L1320 + finish 内 cal_sha_post（L1094） | 收尾处是 sha 复核（每个调用之后都已做过完整恢复链），不再额外跑一轮 compare。T15、T16、T19 |
| B8 | 备份两份 sha + chmod 444 | L1190–L1198 | 独立 PIN 备份对比为可选，未做 |
| B9 | 例程 20 分钟兜底 | routine_fallback_v1.py（新）；例程草稿第五节 | pgrep 空 + 备份 sha == PIN + .ok allow_routine_fallback_restore 才原子恢复；无 marker 代写 FAILED driver_killed；sha 仍不符退出 5（P1）。驱动钉其 sha（SHA_KEYS sha_routine_fallback）。T19 |
| C10 | .ok key=value、ASCII、LF、无行内注释；拒重复 / 未知键 | parse_ok L618 | T01 |
| C11 | 必填键与值 | OK_KEYS_REQUIRED L112；check_ok L660（等值表 L673；issued / expires L688；sha 键 L695） | T02 |
| C12 | 拒 /_consumed/ 与 DRAFT；不移动不删除 .ok；记全长 sha | L662、L628、L667 | 全文件无 .ok 的 rename / unlink。T01、T02 |
| D13 | 按 §3 实测；只认本次写入；日期统一 YYYYMMDD == D；hsgt rc=2 = partial | post_checks L1327；norm_date L529；summary 窗口 L546；hsgt L601；原始文件 trade_date 实测 L959 | T05、T06、T07 |
| E14 | 两条锚定 pgrep 为空；94322 检查；例程删 SIGCONT | L94、L95；pgrep_gates L790；guarded_check L399；GUARDED L98；signal_exact 拒发 GUARDED L299 | 例程草稿第一节已删 SIGCONT。T09 |
| E15 | 全部钉 sha；解释器 /usr/bin/python3；ET 日期 == D 且 ≥ 05:25 | check_pins L713；SHA_KEYS L50；start_window_check L725；PIN 日历 D 开市 L1204 | 当前仓库文件 sha 与 Arch §6 逐个一致（第 8 节） |
| E16 | RSS 树合计 1484800 停、单进程 > 1536000；保留 rss 日志 | L79、L80、L493、rss 日志 L477 | T18 |
| E17 | 无 sw / trade_cal 步骤、无 --force、无删除 | L72；.ok 禁止键 L677 | 驱动唯一的“移动”是凭 .ok 的同盘隔离与 supersede，无 unlink（自建临时文件除外） |
| 另 | P3 锁内容；重试前完整 quiet；Q-A3 (a)–(f)；Q-A4 | lock_content_check L744；重试前 quiet L1266；条件 L1257；锁 sha A→B L1283 | — |
| 主 Agent 12:32 | （1）预算 75；（2）call B 超时停树 FAILED；（3）SIGKILL 兜底；（4）94322 只能 T / 已退出、驱动永不发信号 | 见 A1、A2、B9、E14 | — |
| Eng 12:40 | 只钉 5b70dfed；call A 恒设 TIER1_SKIP_CAL_REFRESH=1 并查日志 | SHA_KEYS sha_tier1_pull；L101；check_cal_skip_log L591 | 缺日志行记 P1，恢复链照做。T15 |

## 2. 超时一节（Arch 第 5 项；Arch 12:24 / 12:38）
| 层 | 参数 | 位置 |
|---|---|---|
| tushare_proxy `_get` | retries=5，timeout=60（requests 标量：connect 与 read 同值；read 为两次 recv 间的空闲上限，**无总时长**） | tushare_proxy.py L26、L34 |
| 429 | sleep(Retry-After，默认 5，**无上限**)，占一次重试 | L38–39 |
| 异常退避 | min(30, 2(i+1))：5 次合计 30 秒 | L44–46 |
| relay | timeout = TSPRO_RELAY_TIMEOUT（默认 180）；10-19 驱动恒设 115 | L57–60；驱动 L100 |
| datahub | 直连 https/http × 两种 api 名 = 4 组，每组 timeout 90；设了 DATAHUB_HTTP_PROXY 再加 4 组 timeout 60；每组 `_get(retries=2)` | L62–80（L71、L75、L78） |
| tier1_pull `_call` | auto：datahub 后 relay；SOURCE=relay 单源；失败间隔 1.5 秒 | tier1_pull.py L17–31（L19–20、L30） |
| tier1_pull `pull` | limit 5000（L35）；每页 8 次 `_call`，退避 2(a+1)（合计 72 秒，L38–45）；行数 < limit 才停（L47） | L33–51 |
| tier1_pull 其他 | SLEEP 0.25（L15）；dates 读 trade_cal（L53–56）；cached_day size>0 即跳过（L64–70） | — |
| 页大小 | 10-16 实测 daily 5567、daily_basic 5567、adj_factor 5577、stk_limit 5655、suspend_d 11 → 前四个接口第一页都是满 5000 行大页 | — |
| 驱动外层 | daily_pull 30 分钟硬停；call B min(起跑 + 75, 16:00)；16:40；审计工具 snap 900 / compare 300 / restore 300 且 ≤ 阶段剩余与距 16:40；wait 60；pgrep 20 | L85、L83 |

urllib3 2.8.0（已安装；requests 2.34.2）：TLS 握手计入 connect 阶段，超时报错文案却是 `Read timed out. (read timeout=<connect 值>)`，看日志时不要据此判断为 read 超时。

### 2.1 Known gaps（10-19 不改代码，靠 30 分钟硬停兜底）
单页最坏情形（“一次卡满”= 每次尝试只在一个阶段卡到上限；connect 与 read 都卡满则翻倍；滴流与 429 无上限）：
- relay 单次 `_call`（TSPRO_RELAY_TIMEOUT=115）：5 × 115 + 30 = **605 秒**（tushare_proxy L26、L44–46、L57–60）。
- datahub 单次 `_call`：直连 4 × 2 × 90 + 4 × 6 = 744；代理 4 × 2 × 60 + 24 = 504；合计 **1248 秒**（L62–80）；无代理 744 秒。
- SOURCE=auto 单次 `_call`：1248 + 605 + 3 ≈ **1856 秒**（tier1_pull L17–31）。
- 每页 8 次 `_call` + 72 秒（tier1_pull L38–45）：SOURCE=relay **4912 秒 ≈ 82 分钟**；auto **≈ 14920 秒 ≈ 4.1 小时**（relay 用默认 180 时约 4.9 小时，与 Arch 估算 ≈ 4.7 小时同量级）。
- 叠加：429 Retry-After 无上限（L38–39）；read 是空闲上限，慢速滴流可无限延长（L34）。
- 实测延迟（docs/v2/audit/relay_probe_20261018/PROBE_1250_RECEIPT_20261018_125839.md，99f3dc9ed969fee94cacabc0db7c8b1e634e841a093d6ce3935c2ceca9ba814d）：12:57 ET relay stock_basic limit=100 HTTP 200、100 行、25.51 秒；trade_cal HTTP 200、7 行、13.51 秒；12:15 ET 一次 limit=5000 请求卡在 connect / TLS 阶段。即小页也要 10–25 秒，满 5000 行大页有实际卡死记录；按 10-19 每接口两页、5 个接口估算，正常情况已接近数分钟级，一旦卡住只能由 30 分钟硬停兜底。

为什么 30 分钟硬停能兜住：驱动不依赖子进程自己的超时。run_nightly 每 5 秒轮询（L499），到 box_end（L497）即按第 1 节 A2 顺序停整棵树；停树最坏耗时 ≈ 5 秒轮询 + 每层 10 秒 TERM + 5 秒 KILL 等待 + 60 秒 wait，随后恢复并双核日历、判 FAILED（strict；relaxed 仅 MAX_RUN 且满足 (a)–(f) 才重试）。因此单页无论卡多久，墙钟都被限制在 30 分钟 + 停树耗时之内；call B 同理被限制在 min(起跑 + 75, 16:00)。代价：网络慢时 10-19 会 FAILED 而不是拖到中午。

后续修复票：docs/v2/tickets/TKT_tushare_proxy_connect15_20261018.md（d19e47f690c070dd75c0ef4fd4bab213e001af99cb4abd51eeac145a992a27a8；建议 connect 15 / read 115 / 总 120、429 上限、每页总预算，Eng 于 10-19 之后实施）。

### 2.2 call B 是否读 trade_cal
会读（只读）：cyq_perf_monthly.py L16、fill_hsgt_top10_extend.py L33 / L39、_light_event_windows_pull.py L292 读 data/v2/tushare_raw/trade_cal.parquet；data_freshness_status.py L10 读 PIT 日历 data/v2/calendar/trade_cal_sse_pit.parquet。因此 call B 期间日历必须是 PIN：驱动在 call B 起跑闸门核 sha（L1280），call B 后再走恢复链并在“恢复前 sha 不是 PIN”时判 FAILED（L1299）。call B 中没有任何步骤联网拉 trade_cal 或 stock_basic（tier1_materialize.materialize_stock_basic 只读本地且 nightly 不调用）。

## 3. 大页行为
10-19 daily_pull 每个接口约 5600 行 → 两页（5000 + 约 600）。cached_day 在文件存在且 size>0 时跳过（tier1_pull L64–70），save 为 tmp + os.replace（L58–62），被停时可能残留 `<D>.tmp.parquet`：驱动 raw_check 把任何 .tmp.parquet 判为不合格（L943），凭 .ok 同盘隔离（L972）。

## 4. FAILED 覆盖与残留缺口
| 情形 | 结果 |
|---|---|
| daily_pull 超 30 分钟 / call B 超预算 / 16:40 / RSS | 停树 → 恢复双核 → FAILED（MAX_RUN / CALLB_TIMEOUT / BLACKOUT / RSS）（T15、T17、T18） |
| nightly 停后 wait 超时 | HANG → 不重试 → FAILED（T14） |
| 例程 / 人发 TERM / INT / HUP | DriverSignal → 统一收尾 → FAILED，退出 11（T16） |
| 未捕获异常 / 审计工具超时 | EXCEPTION / TOOL_TIMEOUT → 统一收尾 → FAILED，退出 11（T10） |
| 驱动被 SIGKILL | 无法捕获 → 例程 20 分钟兜底：恢复日历 + 代写 FAILED driver_killed（T19） |
| 残留缺口 | （1）OOM / SIGKILL 发生在写 marker 中途：marker 由 write_new（O_EXCL + link）原子发布，不会半截；兜底只在无 marker 时代写。（2）marker 写入失败退出 3：兜底照常检查日历但不会再写 marker（已存在时）。（3）兜底需要 .ok allow_routine_fallback_restore_20261019=true 才恢复日历，否则退出 5（P1）。 |

## 5. 写路径清单（Arch 12:37）：证明不碰 fund_portfolio_dh 及其临时文件
94322（remaining_after_stk_surv.py fund_portfolio，L79–120）写：data/v2/tushare_raw/fund_portfolio_dh/<period>/<offset 9 位>.parquet 与 _DONE（L83、L90–91，to_parquet 直接写，无单独临时名）；合并后 data/v2/events/fund_portfolio_2018plus.parquet（L104）+ manifest；output/markers/fund_portfolio_2018plus.DONE（L119）；docs/v2/DATA_FUND_PORTFOLIO_FULLWINDOW_RECEIPT_ZH.md（L109）。
`rg -i fund_portfolio` 在 nightly_update.py、tier1_pull.py、tushare_proxy.py 与 11 个步骤脚本中**零命中**（只有 etf_daily_adj_incr / eng_daily_panels 出现 fund_daily / fund_adj，是 ETF 日线接口名，路径见下表）。
| 写入方 | 路径（相对 /workspace/QuantLab） | 方式 / 临时文件 | 依据 |
|---|---|---|---|
| nightly_update.py | logs/nightly/20261019_<step>.log（追加）；logs/nightly/20261019_summary.json | open a；write_text 整份重写 | L14、L116、L137 |
| nightly_update.py（bundle 步） | output/data_v2_bundle/{northbound,index_members,corporate_actions,sw_pit,index,cyq,tier3_daily/<kind>}/… | shutil.copy2（源见 BUNDLE_MAP；无 fund_portfolio） | L46–83 |
| nightly_update.py（仅中转快速失败时） | output/relay_outage_backfill_queue.json | write_text | L86–95、L112 |
| tier1_pull.py extend（call A） | data/v2/tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261019.parquet；临时 <同目录>/20261019.tmp.parquet | to_parquet tmp → os.replace | L58–62、L102 |
| tier1_pull.py | data/_acquire_logs/tier1_progress.json（及该目录） | write_text | L12–13、L78 |
| tier1_pull.py（TIER1_SKIP_CAL_REFRESH≠1 时才会） | data/v2/tushare_raw/trade_cal.parquet；临时 trade_cal.parquet.tmp.<pid> | 原子 replace；10-19 call A 恒设跳过，驱动仍每次恢复双核 | L83–98 |
| tier1_pull.py index（index_pull 步） | data/v2/tushare_raw/index_daily/… | to_parquet | L139 |
| adj_factor_incr.py | data/v2/adj/adj_factor_2023h2plus.parquet（临时 .tmp.parquet）；adj_factor_2023h2plus_manifest.json | tmp → replace | L6、L21、L25 |
| tier1_materialize materialize_bars | data/v2/bars/daily_ohlcv_raw_pit.parquet（临时 .tmp.parquet）+ manifest；data/v2/asof_extend_tushare_202610/panels/… + manifest | tmp → replace；面板直写 | L87–160 |
| tier1_materialize materialize_daily_basic | data/v2/valuation/daily_basic_full_tushare.parquet（临时 .tmp.parquet）；data/v2/valuation/_daily_basic_parts_<stamp>/（建后 rmtree）；backups/valuation/daily_basic_full_tushare.<stamp>.parquet（保留 5 份，旧的 unlink）；output/daily_update_status.json（临时 .tmp）；manifest | 见行号 | L168–175、L249–282、L293–416 |
| tier1_materialize materialize_index | data/v2/index/index_daily_pit.parquet、index_daily_<code>.parquet、manifest | to_parquet | L440–456 |
| etf_daily_adj_incr.py | data/v2/etf/raw/{fund_daily,fund_adj}/<D>.parquet（临时 +.tmp）；data/v2/etf/etf_daily_adj.parquet（+.tmp）；output/daily_update_status.json（.tmp） | tmp → replace | L5、L13–14、L33、L50、L62 |
| eng_daily_panels.py | data/v2/etf_510300/panels/sh.510300.parquet、manifest.json；data/v2/asof_extend_202610/…；data/v2/asof_extend_tushare_202610/manifest.json；data/v2/tushare_raw/dividend_by_exdate/…；data/v2/corporate_actions/dividend_by_exdate_tushare.parquet、manifest_dividend_by_exdate.json；output/daily_update_status.json（.tmp） | tmp → replace / write_text | L24、L32、L61–179 |
| mid_large_universe_incr.py | data/v2/universe/mid_large_members_pit.parquet（.tmp）、备份 copy2、manifest；output/daily_update_status.json（.tmp） | tmp → replace | L12–14、L58–77 |
| _light_event_windows_pull.py（events） | output/data_v2_bundle/windows/ 与 data/v2/events/ 下 <name>.parquet（.tmp.parquet）、<name>_manifest.json、<name>_MISSING.json、light_event_windows_summary.json；data/v2/tushare_raw/{pledge_stat,stk_holdertrade,forecast_by_period,forecast,express}/… | tmp → replace / 直写；缓存空文件 unlink 重拉 | L21–23、L150–180、L219–221、L258–259、L316–337、L378–412、L471–472、L517–518 |
| forecast_manifest_declare.py（events） | data/v2/events/{forecast_1y,forecast_2024h2_2025,forecast_2024plus}_manifest.json；docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md | write_text | L7、L59–67、L83 |
| fill_hsgt_top10_extend.py | data/v2/tushare_raw/hsgt_top10/<d>.parquet（.tmp.parquet；<700 字节旧文件 unlink 重拉）；data/v2/northbound/hsgt_top10_daily_2018plus.parquet、northbound_summary.json；output/d1/hsgt_top10_extend_progress.json；logs/event_hsgt_top10_extend.log | tmp → replace | L20–24、L51–62、L104–155、L163、L187–189 |
| cyq_perf_monthly.py | data/v2/tushare_raw/cyq_perf/<d>.parquet；data/v2/cyq/cyq_perf_<YYYYMM>.parquet、manifest.json | 直写 | L11、L43–66 |
| tier3_daily_snapshot.py | data/v2/tier3_daily/<kind>/<D>.parquet；data/v2/tier3_daily/manifests/<D>.json | 直写 | L8、L27–30、L60 |
| data_freshness_status.py | output/data_freshness_status.json（.tmp） | tmp → replace | L9、L85 |
| 驱动 run_nightly_v1.py | _recovery/data/nightly_20261019/run_<STAMP>/（trade_cal 备份 .141078fa 444、post 副本、cal_compare / cal_restore / snap 日志与输出、rss_<tag>.log、quarantine/a<k>/<api>/）；logs/nightly/nightly_20261019_<tag>_<HHMMSS>.out；docs/v2/audit/nightly_20261019/driver_receipt_<STAMP>.json；output/nightly_markers/nightly_20261019.{DONE,FAILED}.json（唯一）与 _superseded/（仅凭 supersede 键）；output/loop/RESEARCH_QUIET.lock（仅 05:28 后不存在且 .ok 授权时新建）；data/v2/tushare_raw/trade_cal.parquet（自带恢复，临时 .trade_cal.parquet.restore.<pid>.<hex>） | write_new：同目录 .<name>.tmp.<pid>.<hex> + O_EXCL + os.link（绝不覆盖） | 驱动 L180、L842、L972、L1000 |
| cal_restore_v2.py（驱动调用） | data/v2/tushare_raw/trade_cal.parquet；被改写版本保存到 --keep-rewritten-dir（run 目录） | 原子 replace | cal_restore_v2.py |
| routine_fallback_v1.py | data/v2/tushare_raw/trade_cal.parquet（临时 .trade_cal.parquet.fallback.<pid>.<hex>）；output/nightly_markers/nightly_20261019.FAILED.json（仅无 marker 时）；docs/v2/audit/nightly_20261019/routine_fallback_receipt_<ts>.json | O_EXCL + replace / link | routine_fallback_v1.py |

以上没有任何路径落在 data/v2/tushare_raw/fund_portfolio_dh/、data/v2/events/fund_portfolio_2018plus*、output/markers/fund_portfolio_2018plus.DONE 之下，临时文件名都在各自目标的同一目录内；data/v2/events/ 下 events 步只写上表列出的名字（forecast / express / pledge / holdertrade 等 light_event 名单与 forecast manifest），不含 fund_portfolio_2018plus。


## 6. 94322 / 94403 与 relay_outage_backfill（只读代码证据）
- 94322：2026-10-18 12:50 ET 实测 /proc/94322/status State: S。按主 Agent 12:32 第 4 条，10-19 开跑时须为 T 或已退出，否则驱动前置失败（不发任何信号）。
- 94403 = scripts/acquire/relay_outage_backfill.py（当前 8d836412…）。事实：已于 2026-10-18 04:59:31 ET 打印 all done 后退出（docs/v2/audit/data_cs_panel_v3_dryrun/cont_94403_20261018.md；queue_falsedone_20261018.md）；12:50 ET 复核：/proc/94403 不存在，锚定 pgrep relay_outage_backfill 为空，output/relay_outage_backfill.pid 不存在。
- 它做什么（代码只读）：
  - L9 / L79：每轮 relay_health.probe() 探中转；中转不通 sleep 900。
  - L12 / L80：HEAVY 含 nightly_update、tier1_materialize、remaining_after_stk_surv；只在每轮开头等待它们退出，**步骤运行中不再检查**。
  - L84：跑 _light_event_windows_pull.py（events，走 datahub / relay）。
  - L89–91：对队列 extra 中有 retry_cmd 的项执行 `python3 scripts/nightly_update.py --date d --steps k`（retry_cmd 由 nightly_update.py register_backfill L86–95 写入 output/relay_outage_backfill_queue.json），其 cmdline 会命中驱动的 PGREP_DATA（nightly_update）。
  - L103：跑 fill_hsgt_top10_extend.py（中转），最多 20 块。
  - L71–73：pidfile + os.kill(pid, 0) 判重；L107：未完成则 sleep 900 循环。
- 结论：它会与 daily_pull / call B 抢同一中转，并可能在 10-19 白天起一个新的 nightly_update 子进程（与驱动的 nightly 并行写同一产物与 summary）。因此驱动按 cmdline 查全部 relay_outage_backfill 进程，只允许 T 或不存在（L412），且永不发信号。
- 旧 05:00 的 94403 CONT 例程若仍在，会对一个已退出、可能已被复用的 PID 发 CONT——已由主 Agent 删除；例程 diff 已记录。
- 放宽申请的依据（供 Arch 判断，Data 不主张）：若有人重启它，只有在其队列为空（无 pending 项）时它才只做探测 + sleep；当前队列状态见 queue_falsedone_20261018.md。

## 7. 子进程环境
CHILD_ENV（L100）：PYTHONDONTWRITEBYTECODE=1、TSPRO_RELAY_TIMEOUT=115，所有 nightly 调用与审计工具都带；CALL_A_ENV（L101）：TIER1_SKIP_CAL_REFRESH=1 只给 call A；SOURCE=relay 仅当 .ok source_relay_only=true（L706），默认不设。驱动记录继承到的 SOURCE / SLEEP / TSPRO_RELAY_TIMEOUT / 是否设 DATAHUB_HTTP_PROXY（L1147；只记是否设，不记值）。

## 8. 钉 sha 现值（2026-10-18 13:02 ET 重算，与 Arch §6 一致）
| 键 / 文件 | sha256（磁盘重算） |
|---|---|
| sha_driver：docs/v2/audit/nightly_20261019/run_nightly_v1.py | 63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16 |
| sha_cal_restore：docs/v2/audit/nightly_20261019/cal_restore_v2.py | 6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4 |
| sha_cal_compare：docs/v2/audit/nightly_20261019/cal_compare_v1.py | 74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc |
| sha_snapshot_tool：docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a |
| sha_scope：docs/v2/audit/nightly_20261019/nightly_sha_scope_20261019.txt | 04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807 |
| sha_nightly_update：scripts/nightly_update.py | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| sha_tier1_pull：scripts/acquire/tier1_pull.py | 5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf |
| sha_tushare_proxy：quantlab/data_sources/tushare_proxy.py | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 |
| sha_relay_health：scripts/acquire/relay_health.py | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f |
| sha_adj_factor_incr：scripts/acquire/adj_factor_incr.py | 723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad |
| sha_tier1_materialize：scripts/acquire/tier1_materialize.py | e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb |
| sha_etf_daily_adj_incr：scripts/acquire/etf_daily_adj_incr.py | ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4 |
| sha_eng_daily_panels：scripts/acquire/eng_daily_panels.py | a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be |
| sha_mid_large_universe_incr：scripts/acquire/mid_large_universe_incr.py | fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b |
| sha_light_event_windows_pull：scripts/acquire/_light_event_windows_pull.py | f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71 |
| sha_forecast_manifest_declare：scripts/acquire/forecast_manifest_declare.py | f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731 |
| sha_fill_hsgt_top10_extend：scripts/acquire/fill_hsgt_top10_extend.py | 36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918 |
| sha_cyq_perf_monthly：scripts/acquire/cyq_perf_monthly.py | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f |
| sha_tier3_daily_snapshot：scripts/acquire/tier3_daily_snapshot.py | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 |
| sha_data_freshness_status：scripts/acquire/data_freshness_status.py | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 |
| sha_routine_fallback：docs/v2/audit/nightly_20261019/routine_fallback_v1.py | f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f |
| pin_trade_cal：data/v2/tushare_raw/trade_cal.parquet | 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086（磁盘 一致） |
| data/v2/calendar/trade_cal_sse_pit.parquet | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41（磁盘 一致） |
| data/v2/calendar/manifest.json | 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4（磁盘 一致） |
| docs/v2/eng_sd1/paper_import_closure.json | 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20（磁盘 一致） |

## 9. 待确认问题
- Q-1（退出码冲突）：主 Agent 11:42 定只读预检通过 = 退出 10；Arch 第 3 项统一失败收尾写的是 “exit 10”。现实现：预检通过 10、统一异常收尾 11、普通 FAILED 1。请 Arch 指定。
- Q-2：“只有 MAX_RUN 可重试”已严格实现（ATTEMPT_FAILED 如 rc≠0、原始文件不合格、summary 不符也不重试）。
- Q-3：hsgt 只认 remaining=0；源端空日会判 FAILED（10-14 remaining=3；10-15、10-16 remaining=0）。
- Q-4（两个选择）：（a）PPID=1 可疑孤儿只记录 P1、不发信号；（b）summary 路径 logs/nightly/<D>_summary.json（nightly_update.py L137）。
- Q-5：收尾处只做 sha 复核而非再跑一轮 compare→restore（每次调用后已做），是否满足 B7 “at finish”？
- Q-6：独立 PIN 备份对比（B8 可选）未做；如需要请指定 PIN 备份路径。
- Q-7：94322 当前为 S，开跑前由谁暂停 / 确认退出？
