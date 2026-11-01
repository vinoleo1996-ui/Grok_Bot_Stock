# Arch 审阅：moneyflow deeper P0 reuse-blended DIFF

- 时刻（America/New_York）：2026-10-25T05:46:33-04:00
- 审阅方：QuantLab Arch
- 依据：主 05:32/05:42 P0；code_change `27d6b462…`；Strategy 修订 DIFF/封面（脚本 `f7a6a775…`）；废签 `42a16384…`；Eng 旁证 dig `c416f43d…`
- live=false；本审后另签 run.ok；**禁**复用废签 `42a16384` / `68c04741`；**禁抬帽**

## 结论

**PASS_WITH_CONDITIONS**

DIFF 相对 baseline `2dae9a91…`（lowmem v1.1）双向干净；reuse 钉路径跳过再读 trunk/sat 与重算混合，对齐 deeper P0 裁定与 Eng「2320≈trunk 整表读」旁证。可签 run.ok（rss_cap=2048；out_dir reuse_blended）。

### 条件（写入 run.ok / 开跑纪律）

1. **外挂 runguard**：`rss_cap_mb=2048`；任一相关 PID VmHWM>2048 → SIGTERM→VOID（脚本内无 watchdog）。
2. **reuse 钉**：run.ok 必须钉 `reuse_blended_path` + `reuse_blended_sha256=3f8a2b33…`；硬链/拷贝后 dst sha 须 MATCH，否则 VOID。
3. 避叶25 `10:00–10:45 ET`；禁 paper/live；禁抬帽 4.5GB；禁复用废签。
4. **WARN（可接受）**：reuse 路径仍对小 blended（≈52KB / 3.1 万行）`pd.read_parquet` 做 turnover/列校验——**不等于**再读 trunk；审阅注明，不挡签。

### 旁证（主/Eng FYI）

- lowmem VOID：VmHWM≈2320 死在主进程读 trunk（≈359 万行），book-smoke 未产出。
- Eng X2 BOOK 单档峰值约 0.65–0.78GB → P0 跳过腿读后，理论峰应落在串行 BOOK 档内、可进 2048 帽（仍须外挂实测）。

## sha 表

| 项 | sha256 | 结果 |
|---|---|---|
| code_change .ok | `27d6b4622296d3d3dfe5e86d5f2c1eaea4be2f102b31dcb20aa65d82f2a35f1f` | MATCH |
| baseline 脚本（逆补丁 / v1.1） | `2dae9a91eb2caf11e3d08d46fa1f025dba4b83a1a497b5c1ab2ad16d70166616` | MATCH |
| DIFF | `a84c6792f874a450d3d9da2d91c8ee566ed3f35eaa587d12f675f3c1f5de0a3c` | MATCH |
| 现盘脚本 | `f7a6a77595eef52120f7619eff9a8b8656b8534d10b76afa4d18ea5d9bd3150c` | MATCH |
| 封面 | `58a32f5054cb058366787a8ce04a523f90556bf075e21a22ebffd6293fb3f1e5` | MATCH |
| reuse blended（recovery） | `3f8a2b33a995f381ee9e7060858a2029c1a8854a31a32b48ab4842281f188103` | MATCH |
| prior VOID run.ok | `42a163840cf4023d2ddb39471acd7368550025e7db49a1519bf68e1c91faa262` | MATCH（不可复用） |
| py_compile | — | PASS |

`/tmp`：`patch -R -p1`→baseline；再 `patch -p1`→现盘；双向干净、无 .rej。

## 清单

| # | 项 | 结果 |
|---|---|---|
| 1 | 仅改 `research/strategy_moneyflow_stack_diag_v1.py` | PASS |
| 2 | reuse 时跳过 trunk/sat DataFrame 重算 | PASS（`install_reused_blended`） |
| 3 | 仍串行 BOOK + aum_* + gc（含 Eng L3 del 大对象） | PASS |
| 4 | DEFAULT_OUT → reuse_blended | PASS |
| 5 | 无 reuse 钉时兼容重算分支 | PASS |
| 6 | 无抬帽 / 无 CMC / 无纸面 | PASS |
| 7 | `prepare_smoke_weights` / book-smoke 兼容 | PASS（见下） |
| 8 | reuse 仍小 parquet read（turnover） | WARN→可接受 |

### prepare_smoke_weights / book-smoke 兼容性

`prepare_smoke_weights` 写出列：`session, instrument, instrument_id, weight, target_weight`。  
recovery 钉死的 `blended_weights_8020.parquet`（sha `3f8a2b33…`）**已是该格式**（实测 31311×5）。reuse 硬链到 `out/blended_weights_8020.parquet` 后，`run_book_smoke_serial(w_path, …)` 以该路径作 `--stock-path`——**无需再跑 prepare_smoke_weights**。重算分支仍调用 prepare，格式一致。

## 将来 run.ok 要点（本轮已签）

- script_sha256=`f7a6a77595eef52120f7619eff9a8b8656b8534d10b76afa4d18ea5d9bd3150c`
- out_dir=`output/strategy_hiliq/moneyflow_stack_8020_reuse_blended_20261025`
- reuse_blended_path + reuse_blended_sha256=`3f8a2b33…`
- rss_cap_mb=2048
- decay_outcome=REJECT
- avoid_windows=叶25
- prior_void=`42a16384…`（及 `68c04741…`）不可复用

给 Strategy/主：**PASS_WITH_CONDITIONS；run.ok 已另签；请按新 .ok 开跑（外挂 2048 帽；钉 reuse；避叶25）。**
