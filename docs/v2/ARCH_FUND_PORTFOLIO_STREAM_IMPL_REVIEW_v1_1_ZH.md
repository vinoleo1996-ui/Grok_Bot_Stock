# fund_portfolio 流式合并 v1.1 实现审阅（Arch）

live=false；promotion=false。方式：只读静态 + 自测产物核对；未改生产代码/parquet；未签任何 .ok（由父会话签发）。

## 钉住基线（sha256 全长核对）

| 件 | 声称前缀 | 现盘 sha256 | 结果 |
|---|---|---|---|
| 设计 v1.1 `docs/v2/DATA_FUND_PORTFOLIO_STREAM_MERGE_DESIGN_v1_1_ZH.md` | 4a46df7f… | `4a46df7f61a281efd74ec1d0abc126aa681cdd435ee3dfd5a0ab40eed8c1815f` | OK（与 FROZEN 逐字节一致） |
| Arch 设计复审 `docs/v2/ARCH_FUND_PORTFOLIO_STREAM_MERGE_REVIEW_v1_1_ZH.md` | 48f55b79… | `48f55b798dd05a2cae0d8fa9139ca894afe26df8a0570c21ed5d271b39dda1df` | OK |
| 实现 `scripts/acquire/fund_portfolio_stream_merge.py` | 367eb772… | `367eb772e1257955dc643bbf4feb1d850adad4cf351f4b7be28ea275df5a3aa4` | OK |
| 自测回执 `sd1_work/fundport_stream_20261025/SELFTEST_RECEIPT_ZH.md` | ee115177… | `ee115177e1c182e06f4046d1d63b28cfd68307b374f77e4c099ffcf3d69c9d65` | OK |
| 旧 L96 `scripts/acquire/remaining_after_stk_surv.py` | 2d9cf67f… | `2d9cf67f2fd1d2e473e47ce0e8a36207460df693c3ee2ae4bca79c6524f08333` | OK（未改；整表 concat 仍在） |
| 驱动 `SELFTEST_DRIVER.py` | （未钉） | `71bd45bdbc7d4a387055058de8b2a1d2131be38203489911495f7200f2350527` | 记录 |
| 残留披露 `RESIDUAL_DISCLOSURES_ZH.md` | （未钉） | `e39ea6380dbdc09dfb137eb2aaf0cd9d5a7080abf053df42cbac837fc55de113` | 记录 |
| 结果 JSON `selftest_results.json` | （未钉） | `2f2f85b8a6ae387f307795a3da867fb73a4603d4ffbc3dd7ec0c416ec697c4d2` | 记录 |

审查时刻（America/New_York）：2026-10-25 00:29 ET。

## 结论

**PASS_WITH_CONDITIONS**

- §9 自测汇总 13 PASS / 0 FAIL；C1 观测 peak_rss_kb=141844、n_batches=2（130 页）；路径均在 `/tmp/ql_fundport_stream_test_*`；生产 `data/v2/events/fund_portfolio_2018plus.parquet` 与 DONE 均不存在（自测未写生产）。
- C1–C8 / O1–O6 主体已在实现落地（见下表）。
- **条件（P2，挡「无条件 PASS」，不挡带条件签发实现审阅 .ok）：** `precheck_run_ok` 当前把整数 `0` 当作可接受的 `allow_broker_recommend`（与 Eng 自述「0→exit 20」及设计 §10.1「必须 false」不一致）。签发实现审阅 .ok 前须二选一：(a) Eng 改码使 `0`→exit 20 并重交 script sha；或 (b) 实现审阅 .ok 正文显式钉「仅 JSON `false` 或字符串 `"false"`；`0`/`1`/缺省/true 一律 exit 20」，并把修码列为开跑前必做。
- **今晚不授权运行**：本审阅不构成运行 .ok；不写生产；L96 `RuntimeError("disabled")` 仍待启用/运行链，不在本次改旧 runner。

## C1–C8 / O1–O6 实现核对

| ID | 结果 | 证据要点 |
|---|---|---|
| C1 | 落地 | `BATCH_MAX_FILES=128`、`BATCH_MAX_ROWS=400000`；`plan_batches` 双顶同时生效；单文件超行单独成批；批间 `del batch_frame`；manifest 回显常量；超 RSS→exit 21。自测 n_batches=2、peak≪1e6 kB。注：期内仍用 `acc_parts` 列表再 concat（整期 acc 峰值已在设计复审残留披露，可接受）。 |
| C2 | 落地 | CLI/run-ok path+sha 双钉；sha 不符 exit 28；缺 path exit 28；自测合成日历在 `/tmp/.../trade_cal.parquet`；无隐式活路径。自测 4a/4b PASS。 |
| C3 | 落地 | 省略无键 drop；`--c3-fixture` + 模块内 A/B；自测 `3_c3_key_frozenset` PASS（n_a=n_b=3）。 |
| C4 | 部分/按设计 | 新 CLI 已建。旧 L96 未改（sha 2d9cf67f）——符合设计「启用 .ok 再生效 disabled」与 Eng 残留 #1；**不得**在无启用 .ok 时改旧 runner。 |
| C5 | 落地 | `mint_run_id`：已存在则 `_r2`…；`os.mkdir` 无 `exist_ok`；不扫删他 run。自测 7 PASS。 |
| C6 | 落地 | manifest/DONE `.tmp`+`os.replace`；三方 sha 校验后写 DONE。自测 8 PASS。最终表 O_EXCL tmp + ParquetWriter + replace。 |
| C7 | 落地 | `mem_available_min_kb` 只从 run .ok 读；缺字段 exit 20；脚本无硬编码 2621440（默认由 .ok 写入）。启动/每期前读 MemAvailable。 |
| C8 | 基本落地* | 缺省/true/`"true"`/1 → exit 20；接受 JSON `false` 与 `"false"`。*见条件：整数 `0` 当前误放行。不触 Q8。 |
| O1 | 闭合 | 同 C3 |
| O2 | 闭合 | 同 C1 |
| O3 | 闭合（启用后） | 新 CLI 有；L96 disabled 待启用 .ok |
| O4 | 闭合 | 同 C7 |
| O5 | 闭合 | allow_broker_recommend 门闩；无 Q8 调用 |
| O6 | 闭合 | run .ok 必含 `log_path`；缺则 exit 20；每期 log flush |

## 自测范围与生产隔离

- 驱动前缀强制 `/tmp/ql_fundport_stream_test_*`；回执项 `10_no_prod_data` PASS；`--selftest` 路径断言。
- 源分片 sha 清单跑后不变（项 5）。
- SIGTERM：`--term-after-period` 期写完后自杀；rc=31；最终路径不存在；leftover_tmp=[]（项 6）。
- 未申请实现/运行 .ok；live=false。

## Arch 裁示（Eng 四点歧义）

| # | 歧义 | 裁示 | 理由 |
|---|---|---|---|
| A1 | HOLD 路径按 `markers_dir.parent/HOLD_FUNDPORT_MERGE` | **Yes** | markers 默认 `output/markers` 时落点为设计 §8 的 `output/HOLD_FUNDPORT_MERGE`；参数化后与旧 HOLD 对齐，无需另加 events-dir sibling。 |
| A2 | `allow_broker_recommend` 接受 JSON `false` 或字符串 `"false"` | **Yes（仅此二者）** | 夹具便利可接受 `"false"`；缺省/true/`"true"`/1 → exit 20。**整数 `0` 必须 exit 20**（当前实现误放行，见结论条件）。 |
| A3 | C1 自测只造 >128 小页，未造单文件 >400000 行 | **Yes（本轮可接受）** | §9.9 只要求超 BATCH_MAX_FILES 且 n_batches≥2、RSS≤1e6；单文件超行单独成批已在 `plan_batches` 编码。建议开跑前补一条夹具（非挡实现审阅）。 |
| A4 | SIGTERM 用 `--term-after-period` 自测钩子 | **Yes（仅自测）** | 满足 §9.6「中途 TERM、最终未 replace、ledger 清理」语义；生产 CLI 默认关闭；运行 .ok 不得依赖该钩子。 |

## 残留（不升格 P0；进运行 .ok 核对清单）

1. 期内键去重前仍持有整期（acc / acc_parts）；采样点在每批追加后与 `del acc` 后——与设计复审残留一致。
2. `--resume` 默认关；语义弱于设计残留所述 `--resume-from-period-dir`（只读完成期目录）。缺省关闭可接受；若启用 resume，须另送审。
3. 可选树 RSS 1s 采样未实现（设计「可选」）。
4. L96 整表 concat 仍在，直至启用 .ok。
5. A3 单文件 >400k 行夹具待补（建议，非本轮门禁）。

## 实现审阅 .ok 应钉键（父会话签发时）

仅在结论条件满足后签发。**本文件不创建 .ok。**

建议键：

- `kind` / `auth_type`: `impl_review`（或团队惯用等价字段）
- `path_script`: `scripts/acquire/fund_portfolio_stream_merge.py`
- `script_sha256`: `367eb772e1257955dc643bbf4feb1d850adad4cf351f4b7be28ea275df5a3aa4`（若 Eng 修 abr==0 则换成新 sha）
- `receipt_sha256`: `ee115177e1c182e06f4046d1d63b28cfd68307b374f77e4c099ffcf3d69c9d65`
- `design_sha256`: `4a46df7f61a281efd74ec1d0abc126aa681cdd435ee3dfd5a0ab40eed8c1815f`
- `design_review_sha256`: `48f55b798dd05a2cae0d8fa9139ca894afe26df8a0570c21ed5d271b39dda1df`
- `impl_review_sha256`: （签发时填 `sha256sum` 本审查文）
- `l96_runner_sha256`: `2d9cf67f2fd1d2e473e47ce0e8a36207460df693c3ee2ae4bca79c6524f08333`（仍未 disabled）
- `single_use`: true
- `live`: false
- `promotion_approved`: false
- `allow_write_events`: false（实现审阅不授权写生产）
- `allow_run`: false（**今晚不授权运行**；开跑另签运行 .ok）
- `allow_broker_recommend`: false（且实现须拒 `0`）
- `note`: 开跑另签运行 .ok（含 mem_available_min_kb=2621440、trade_cal path+sha、log_path、窗口、allow_write_events）

## P0 / P1

- **P0：** 无
- **P1：** 无（相对实现审阅门禁）
- **P2：** `allow_broker_recommend=0` 误放行（见结论条件）

live=false；promotion=false。

