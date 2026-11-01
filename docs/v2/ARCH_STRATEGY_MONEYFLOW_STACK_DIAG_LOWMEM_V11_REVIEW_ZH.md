# Arch 审阅：moneyflow 低内存 v1.1 DIFF

- 时刻（America/New_York）：2026-10-25T05:18:01-04:00
- 审阅方：QuantLab Arch
- 依据：主 05:15 P0；Strategy DIFF/封面；裁定 `ARCH_STRATEGY_MONEYFLOW_VOID_LOWMEM_DECISION_20261025_ZH.md`
- live=false；本审后另签 run.ok；**禁**复用废签 `68c04741`

## 结论

**PASS_WITH_CONDITIONS**

DIFF 相对 baseline 干净；实现分档串行 + BOOK-only + aum_* + gc，对齐裁定。可签 run.ok（rss_cap=2048；新 out_dir）。

### 条件（写入 run.ok / 开跑纪律）

1. **外挂 runguard**：`rss_cap_mb=2048`；任一相关 PID VmHWM>2048 → SIGTERM→VOID（脚本内无 watchdog）。
2. **blended**：脚本仍每次重算混合（无 skip 复用路径）——**允许**；开跑后写出的 `blended_weights_8020.parquet` 须 **sha MATCH** 期望 `3f8a2b33…`，否则 VOID（同 trunk/sat 钉应复现）。参考副本：`output/strategy_hiliq/_recovery/strategy/20261025T0502ET_moneyflow_stack_void/blended_weights_8020.parquet`。
3. 避叶25 `10:00–10:45 ET`；禁 paper/live；禁抬帽 4.5GB；禁复用废签。
4. meta 内 `code_change_ok_sha256_prefix` 仍写旧 `951f3ce2`（cosmetic WARN，不挡）。

## sha 表

| 项 | sha256 | 结果 |
|---|---|---|
| code_change .ok | `b2340c67ab78e526ba65894be2182d0c54885441b8fe7f6e2578ecd196b1c81a` | MATCH |
| baseline 脚本（逆补丁） | `c2ff60451ef1a20b74c287863762a8c78d8b616443e1cfeb188761c106694c63` | MATCH |
| DIFF | `e5e0b6da101f3dc7b7c6c9b6d8d39959f309a146ac0c3909916d1ee3cc2d5739` | MATCH |
| 现盘脚本 | `2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616` | MATCH |
| 封面 | `1cc9be33308a4f08e3490a1ac919232b6e1f13728226b5717d053f225b1209d8` | MATCH |
| 期望 blended（recovery） | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103` | MATCH |
| py_compile | — | PASS |

`/tmp`：`patch -R`→baseline；再 `patch -p1`→现盘；双向干净。

## 清单

| # | 项 | 结果 |
|---|---|---|
| 1 | 仅改 `research/strategy_moneyflow_stack_diag_v1.py` | PASS |
| 2 | 分档串行单 `--capitals` | PASS（`run_book_smoke_serial`） |
| 3 | `--arms BOOK` 去 C0 | PASS |
| 4 | `book_smoke/aum_*` + gc.collect | PASS |
| 5 | 汇总 summary / VOID 路径 | PASS |
| 6 | 无 4.5GB 硬跑 / 无并行双档 / 无 CMC | PASS |
| 7 | blended skip 复用 | WARN→改用写出后 sha 校验 |
| 8 | live/paper 门禁仍在 | PASS |

## 将来 run.ok 要点（本轮已签）

- script_sha256=`2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616`
- out_dir=`output/strategy_hiliq/moneyflow_stack_8020_lowmem_20261025`
- rss_cap_mb=2048
- expected_blended_sha256=`3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103`
- decay_outcome=REJECT
- avoid_windows=叶25
- prior_void=`68c04741…` 不可复用

给 Strategy/主：**PASS_WITH_CONDITIONS；run.ok 已另签；请按新 .ok 开跑（外挂 2048 帽）。**
