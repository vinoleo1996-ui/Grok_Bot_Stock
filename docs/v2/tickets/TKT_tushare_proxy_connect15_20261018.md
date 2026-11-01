# TKT_tushare_proxy_connect15_20261018 — tushare_proxy / tier1_pull 网络超时加固（10-19 之后执行）

- 编号：TKT_tushare_proxy_connect15_20261018
- 提出：QuantLab Data（2026-10-18 ET），依据 Arch 12:24 / 12:36 / 12:38、Eng 12:34 / 12:40
- 负责人（建议）：QuantLab Eng（两份文件都归 Eng；Data 不改）
- 执行窗口：10-19 日更结束之后（Eng 12:40：10-19 05:25–18:40 不动 tier1_pull；tushare_proxy 同样冻结到 10-19 之后）
- 状态：OPEN；live=false；promotion_approved=false
- 涉及文件（当前钉 sha）：
  - quantlab/data_sources/tushare_proxy.py  ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772
  - scripts/acquire/tier1_pull.py  5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf

## 1 现状（只读核对，行号对应上面两个 sha）

| 位置 | 现状 | 问题 |
|---|---|---|
| tushare_proxy.py L26 `_get(..., retries=5, timeout=60)` | requests 标量 timeout：connect 与 read 同值；read 是“每次 recv 之间”的空闲上限，没有总时长 | 慢速滴流（每 114 秒来一点字节）可无限拖长单次请求 |
| tushare_proxy.py L38–39 | 429 时 `time.sleep(Retry-After)`，**没有上限**，且占用一次重试 | 对端给大 Retry-After 时单次 `_get` 可远超预期 |
| tushare_proxy.py L44–46 | 异常后退避 `min(30, 2*(i+1))` | 5 次合计 2+4+6+8+10=30 秒 |
| tushare_proxy.py L57–60 `relay()` | `TSPRO_RELAY_TIMEOUT` 默认 180（标量） | Arch 要求 connect 15、read ≤115、总 120；现在做不到“connect 15”与“总 120” |
| tushare_proxy.py L62–80 `datahub()` | 直连 4 组（https/http × 两种 api 名）每组 90 秒；设了 `DATAHUB_HTTP_PROXY` 再加代理 4 组每组 60 秒；每组 `_get(retries=2)`（L71 / L75 / L78） | 单次 `datahub()` 最坏约 20 分钟（见第 2 节） |
| tier1_pull.py L15 | `SLEEP` 默认 0.25 | — |
| tier1_pull.py L17–31 `_call` | `SOURCE=auto` 先 datahub 再 relay（L18）；`SOURCE=relay` 单源（L19–20）；失败间隔 1.5 秒（L30） | auto 时最坏 = datahub 最坏 + relay 最坏 |
| tier1_pull.py L33–51 `pull` | limit 5000（L35）；每页最多 8 次 `_call`，退避 `2*(a+1)`（L38–45，合计 72 秒）；行数 < limit 才停（L47） | 10-16 daily 5567 行、daily_basic 5567、adj_factor 5577、stk_limit 5655 → 每个接口都要两页，第一页是满 5000 行大页 |
| tier1_pull.py L53–56 `dates` | 读 `data/v2/tushare_raw/trade_cal.parquet` | 10-19 由驱动钉住 PIN 141078fa 并核 D 为开市日 |
| tier1_pull.py L64–70 `cached_day` | 文件存在且 size>0 即跳过 | 半截文件不会出现（save 是 tmp + replace，L58–62），但“存在即跳过”意味着坏数据不会被重拉 |

另：已安装 urllib3 2.8.0 / requests 2.34.2。urllib3 2.8.0 把 TLS 握手计入 connect 阶段，但握手超时报错文案是 `Read timed out. (read timeout=<connect 值>)`，看日志时不要误判成 read 超时（Arch 12:24）。

## 2 最坏情形算术（单页、单接口；“一次卡满”= 每次尝试只在一个阶段卡到上限）

10-19 驱动给子进程恒设 `TSPRO_RELAY_TIMEOUT=115`（Arch 12:36 / 12:38）。

- relay 单次 `_call`：5 × 115 + 退避 30 = **605 秒**（connect 与 read 各卡一次满：5 × 230 + 30 = 1180 秒；滴流：无上限）
- datahub 单次 `_call`（设了代理）：直连 4 × 2 × 90 + 退避 4 × (2+4) = 744；代理 4 × 2 × 60 + 24 = 504；合计 **1248 秒**（不设代理 744 秒）
- `SOURCE=auto`：1248 + 605 + 1.5 × 2 ≈ **1856 秒 / 次 `_call`**
- 每页 8 次 `_call` + 72 秒退避：
  - `SOURCE=relay`：8 × 605 + 72 = **4912 秒 ≈ 82 分钟**
  - `SOURCE=auto`：8 × 1856 + 72 ≈ **14920 秒 ≈ 4.1 小时**（若 relay 仍用默认 180：8 × (1248 + 930 + 3) + 72 ≈ 4.9 小时，与 Arch 估的约 4.7 小时同量级）
- 再叠加 429 的 Retry-After（L38–39）无上限。

结论：单页最坏远超 10-19 daily_pull 的 30 分钟时间盒。10-19 不改代码，靠驱动的 30 分钟硬停兜底（run_nightly_v1.py 的时间盒与按确切 PID 停树），超时即 MAX_RUN → 停树 → 恢复并双核日历 → FAILED。

## 3 建议改法（10-19 之后，由 Eng 实施）

1. `_get` 改为元组超时 `timeout=(connect, read)`，并加整次请求总时限（例如 `stream=True` + 逐块读 + 单调时钟 deadline，超过即关闭连接抛错）。
2. `relay()`：connect 15、read 115、单次请求总时限 120（Arch 12:24）；环境变量拆为 `TSPRO_RELAY_CONNECT_TIMEOUT` / `TSPRO_RELAY_READ_TIMEOUT` / `TSPRO_RELAY_TOTAL_TIMEOUT`，旧 `TSPRO_RELAY_TIMEOUT` 只作 read 的兼容别名。
3. `datahub()`：直连 `(15, 90)`、代理 `(15, 60)`；同样加总时限；整个 `datahub()` 加总预算参数。
4. 429：`Retry-After` 设上限（例如 30 秒），并计入总预算。
5. `tier1_pull.pull`：加“每页总预算 / 每次调用总预算”参数（环境变量），超出直接抛错，让上层更早失败。
6. 日志：超时异常里写明阶段（connect / TLS / read / total），避免 urllib3 2.8.0 的误导文案。

## 4 验收

- 单元测试：本地假 HTTP 服务分别模拟 connect 挂起、TLS 握手挂起、首字节前挂起、滴流、429 大 Retry-After；断言每种情况在 connect 15 / read 115 / total 120 内抛错。
- 第 2 节算术按新参数重算并写入回执；新 sha 由 Arch 重新钉住后才可用于日更。
- 不改变成功路径的返回值与行数（拿 10-16 已有原始文件做对照）。

## 5 引用

- docs/v2/ARCH_DATA_NIGHTLY_V1_DESIGN_REVIEW_ZH.md（2dada5ed）
- docs/v2/audit/nightly_20261019/ 下本次驱动差异说明（Known gaps 一节引用本票）
