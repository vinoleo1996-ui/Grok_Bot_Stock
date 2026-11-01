# 预警接口契约（Eng）——只打 risk_flag，不改权重

## 入口
`PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli alert-ingest [file] [--date YYYYMMDD]`（不带 file 时默认读 output/intel/ALERTS_latest.json，即 schema quantlab.intel.alerts.v1，按下文映射）
校验通过后写入 data/v2/alerts/alerts_<YYYYMMDD>.parquet（按 alert_id 去重，后写覆盖先写）；校验失败输出 REJECTED 与原因，退出码 1，不写文件。

## 字段（全部为字符串，必填）
| 字段 | 说明 |
|---|---|
| alert_id | 全局唯一 |
| ts_et | 生效时间，ISO8601 带时区偏移 |
| scope | stock / industry |
| code | stock 用 sh./sz./bj.XXXXXX；industry 用申万一级 6 位 sw_code（如 801780） |
| severity | info / warn / high |
| kind | 预警类别（由 AI 自定，如 regulatory、earnings_warning） |
| source | 产出方（如 quantlab_ai_intel） |
| expires_et | 失效时间，ISO8601 带时区偏移 |
| note | 说明 |

## 消费
- quantlab.portfolio.research_loop.risk_flags(holdings)：对 ts_et ≤ 当前 < expires_et 的预警，按个股代码或该股当前的申万一级（data/v2/sw_l1_pit/industry_members_sw_l1.parquet，研究级）匹配，在持仓上加 risk_flag 列（severity:kind:alert_id）。
- paper-daily 写出 output/loop/paper_daily_<date>/risk_flags.parquet，覆盖 capacity_adv、b4_600000、b4_1000000 三条。**权重永不自动修改**（recon 中 weights_modified=false）。
- 现状：AI intel 目前没有预警产出（output/intel 只有权重和辩论账本）。本接口等 AI 按上述字段写文件。

## 测试（2026-10-13 ET，合成文件，事后已删除）
- 坏代码（601088 缺前缀）：REJECTED，exit 1。
- 合法两条（个股 sh.601088 warn；行业 801780 info）：入库成功。paper-daily --force 标记 B4 60万 4 名、B4 100万 5 名、capacity_adv 7 名，权重未变。
- 测试用 alerts_19990101.parquet、data/v2/alerts/ 目录和对应的 paper_daily 输出均已删除。

## AI intel 映射（quantlab.intel.alerts.v1 → 本契约，2026-10-13 起为默认源）
- alerts[] 的每一项生成一条 industry 行（申万一级名称经 industry_members_sw_l1 映射为 sw_code；映射不到的列入 unmapped_industries），并为 stocks[] 中每只股票生成一条 stock 行。
- severity：call=偏空 且 strength=强 → high；偏空 → warn；其余（偏多、观察）→ info。kind=intel_<call>_<strength>。
- ts_et = generated_et（按 America/New_York 解释）；源数据没有失效时间，Eng 暂定 expires_et = ts_et + 24h。
- alert_id = intel- 加 sha1(generated_et|industry|code) 的前 12 位，重复入库幂等。source = quantlab_ai_intel:<mode>。

## v1.1（2026-10-14，向后兼容）
- severity 枚举：`info` / `watch` / `high`（旧值 `warn` 按 `watch` 读入；历史文件里的 warn 在合并时同样映射为 watch）。
- **显式优先**：读取 output/intel/ALERTS_latest.json 中顶层 `alerts[]` 每项和 `events[]` 每项的 `severity` 字段；值不在枚举里 → 记为 `info`，并在 stdout 打印 `severity_unknown_mapped_to_info`。
- **缺失才推导**：只有没有 severity 时才用旧规则（偏空+强=high，偏空=watch，其它=info）。
- 新列 `severity_source`：`explicit` / `derived` / `explicit_unknown_mapped_info`（旧文件为 `derived_legacy_v1`；其它来源的文件没有此列时默认 explicit）。
- `events[]`（CPI/FOMC/台积电等宏观事件）→ `scope="market"`，`code="ALL"`，`kind="intel_event"`。只用于展示，不匹配个股/行业的 risk_flag。
- 边界不变：severity 只影响告警展示和 risk_flag，**永不改变权重、不产生订单**。
