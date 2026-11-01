# daily_basic 增量 v3.1 — Arch 启用包审查（SHA_KEYS 后重交）

live=false；promotion=false；**今晚不签 enable/run/纸面 .ok**；**未改生产**；**未跑实数据**。

- 审查对象：Eng 恢复核验 PASS 后重交启用包（revision=`resubmit_after_recovery_sha_keys`）
- 包目录：`/workspace/sd1_work/daily_basic_incr_20261025/enable_pack/`
- META：`finished_at_et=2026-10-25T01:29:07-04:00`；`prior_driver_dead_const=2380eb2a…`（**历史**）；**现行驱动钉 = f1910e8a…**
- 依据：主「审启用包；默认今晚不签 enable」；Arch SHA_KEYS 裁示（incr/transform 进驱动 SHA_KEYS + OK_KEYS_REQUIRED）
- 审查时刻（America/New_York）：2026-10-25 01:32 ET
- 方式：只读复算 sha / 静态读驱动 `SHA_KEYS`·`OK_KEYS_REQUIRED`·`check_pins`·`check_ok` / 读 SELFTEST_RESULTS + 抽查 selftest 断言 / BEFORE·AFTER valuation inventory；**不重跑自测**；**不签 .ok**

## 结论

**PASS_WITH_CONDITIONS**

- 包内宣称前缀与全长 **一致**；现盘代码钉 **全 MATCH**（驱动 **f1910e8a…**，非 2380eb2a）；transform 复算 **308b5054… MATCH**。
- Arch SHA_KEYS 裁示 **闭合**：`sha_daily_basic_incremental` / `pin_daily_basic_transform` 已入 `SHA_KEYS`；`OK_KEYS_REQUIRED = […基线…] + list(SHA_KEYS)` 故两键为 .ok 必填；`check_pins` 对 transform 调 `compute_transform_sha`；`check_ok` 遍历 `SHA_KEYS` 对照 .ok 钉值。
- 自测回执 **32 PASS / 0 FAIL**；抽查覆盖 CLI `--mode incremental`（rc==0）、全量 `QL_DB_ALLOW_FULL` 闸、原子 manifest、`SHA_KEYS` 两键、驱动 sha=f1910e8a、生产 valuation inventory equal。
- f99 字节未动；例程未切新驱动；生产 `data/v2/valuation/` BEFORE==AFTER（6 文件）；小文件现盘 sha MATCH。
- **条件（挡本晚 enable，不改本审查技术结论）：**
  1. **今晚不签 enable**（主编排默认；Eng 亦未申请）。
  2. 将来启用 .ok 必须含：`sha_daily_basic_incremental=a7ac54b3…`、`pin_daily_basic_transform=308b5054…`、`sha_driver=f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05`（全长），且 `allow_enable`/`promotion` 另裁。
  3. 例程/生产名不得静默切离 f99；切新驱动须另签。
  4. META `post.ENABLE_PACK_META.json` 自指 sha=`713bd7c5…` ≠ 现盘 `3a2910ac…`（写入后自哈希鸡生蛋，**P2**，不挡）。

## 包内材料（全长 sha256）

| 包内件 | Eng 前缀 | Arch 复算全长 | 结果 |
|---|---|---|---|
| `DIFF_ENABLE_PACK_ZH.md` | `258ebeb1…` | `258ebeb168c0d1da8f19a9b2672b14b58e164872ff21a53abeb8adb5f114b2ad` | **OK** |
| `ENABLE_PACK_RECEIPT_ZH.md` | `203cf3ed…` | `203cf3ed5e29786770688fc3de3b1590231bde5261eab69d434ec131e3f88aa4` | **OK** |
| `ENABLE_PACK_META.json` | `3a2910ac…` | `3a2910accd3249d59a8b5d7fc47d3c785b33b1597ff18194a44e6ad37a22db66` | **OK** |
| `selftest_enable_pack.py` | `d0a699ca…` | `d0a699ca9d76e85c5f4dec0a16ba29224bef40a51bf2b76a5651fd8cb10ac06b` | **OK** |
| `SELFTEST_RESULTS.json` | `1b79f62b…` | `1b79f62ba393e972f812217abb581c2e465e580929bfe457e30fbfe6e5146835` | **OK** |
| `PROD_VALUATION_SHA_INVENTORY_AFTER.json`（附） | — | `b40cecf7a6b8b1f9a2c761579cfd4eb5e62d92cfa1f23f1807169214046c2467` | 记录 |

- META.revision = `resubmit_after_recovery_sha_keys`
- META.post.driver_new = `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05`（与现盘 MATCH）
- META.prior_driver_dead_const = `2380eb2ac8fba1978dd47b916c6f43dcb18cb1b8ad30565b12defee7d4acffd1`（仅历史）
- META.self-claim：`SELF_STALE`（claim `713bd7c5de4bc8679b918b569cb41b46ca47f248d22d0c56add104508b77f1b6` / actual `3a2910accd3249d59a8b5d7fc47d3c785b33b1597ff18194a44e6ad37a22db66`）
- `allow_enable=false` / `allow_run=false` / `requested_enable_ok=false` / `created_ok=false` / `live=false`

## 现盘钉对照

| 钉 | 路径 | 期望全长 | 现盘全长 | 结果 |
|---|---|---|---|---|
| `driver_new` | `docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py` | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` | **MATCH** |
| `nightly_update` | `scripts/nightly_update.py` | `2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b` | `2b4704e88a45e8bb173aa8f3375de9d9dc67a13b8c5501292ddf0a0fa3ebfd5b` | **MATCH** |
| `tier1_materialize` | `scripts/acquire/tier1_materialize.py` | `7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c` | `7205ba43b4e4dc50c1ca9f546f6f54c359ad8c78f4707c2d2bb161d46829e65c` | **MATCH** |
| `daily_basic_incremental` | `scripts/acquire/daily_basic_incremental.py` | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` | **MATCH** |
| `scope_dbincr_v3_1` | `docs/v2/audit/nightly_20261019/nightly_sha_scope_dbincr_v3_1.txt` | `428a05d4891ab1c37fb272870b4a1c721d98406748d638a100784a898caca0c5` | `428a05d4891ab1c37fb272870b4a1c721d98406748d638a100784a898caca0c5` | **MATCH** |
| `f99_driver` | `docs/v2/audit/nightly_20261019/run_nightly_v1.py` | `f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a` | `f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a` | **MATCH** |
| `eng_sha_keys_doc` | `docs/v2/audit/nightly_20261019/ENG_SHA_KEYS_INCR_TRANSFORM_20261025_ZH.md` | `246f37ae8a2de5f797f3ca698197ad20ab0bc4fa0cf97da598ed87cc966f490d` | `246f37ae8a2de5f797f3ca698197ad20ab0bc4fa0cf97da598ed87cc966f490d` | **MATCH** |
| `blockers_review` | `docs/v2/ARCH_DATA_DAILY_BASIC_V3_1_ENABLE_BLOCKERS_REVIEW_ZH.md` | `5b05c7c71d5cb5adfd09e4d632051a3c62319b8e86184196ce290ee827f716ac` | `5b05c7c71d5cb5adfd09e4d632051a3c62319b8e86184196ce290ee827f716ac` | **MATCH** |
| `impl_r2_ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_IMPL_REVIEW_r2.ok` | `0a7d15f653d0f3e9d67b597de4625cab3fd62914625cee8bcec7b94ee8f997f2` | `0a7d15f653d0f3e9d67b597de4625cab3fd62914625cee8bcec7b94ee8f997f2` | **MATCH** |
| `transform_sha`（复算） | `__computed__/daily_basic_transform_sha` | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` | **MATCH** |

补充：
- impl r2 `.ok` `allow_enable=false`；其内 `tier1_sha256=2af28a69…` 为 P1 闭合时钉（启用包已将 live tier1 推进至 `7205ba43…`，属预期差分，**不以 impl .ok 的旧 tier1 否定本包**）。
- blockers 审查文 `5b05c7c7…` MATCH；P1 enable_blockers 已 CLOSED（先验）。

## Arch SHA_KEYS 裁示闭合

| 裁示项 | 结果 | 证据 |
|---|---|---|
| incr/transform 进驱动 `SHA_KEYS` | **PASS** | 键 `sha_daily_basic_incremental`→`a7ac54b3…`；`pin_daily_basic_transform`→`308b5054…`（`__computed__/…`） |
| 进 `OK_KEYS_REQUIRED` | **PASS** | L128：`OK_KEYS_REQUIRED = […]+ list(SHA_KEYS)`；两键随字典键进入必填 |
| `check_pins` 对照磁盘/复算 | **PASS** | transform 分支 `compute_transform_sha`；incr 文件 sha；Arch 复算 transform MATCH |
| `check_ok` 对照 .ok | **PASS** | 遍历 `SHA_KEYS`：`kv[k].lower()!=pin`→拒；缺键亦无法通过必填/`ok_known_keys` |
| 不得仅靠模块常量死钉 | **PASS** | 相对 prior `2380eb2a` 死钉版已废；现网以 `SHA_KEYS`+`check_pins` 为准 |
| 启用 .ok 模板含两键 + `sha_driver=f1910e8a…` | **模板就绪** | RECEIPT/DIFF 已写明；**本晚不签** |
| f99 不被例程切去跑新字节 | **PASS** | f99 sha MATCH 未动；新驱动独立文件名 `run_nightly_v1_dbincr_v3_1.py` |
| 生产 valuation 未被写 | **PASS** | BEFORE==AFTER（6）；自测 `prod_valuation_sha_inventory_equal` ok；小文件现盘 sha MATCH |

## 自测可信度（32/0）

| 检查面 | 代表用例 | 结果 |
|---|---|---|
| py_compile | nightly / tier1 / driver_new / incr | PASS |
| nightly CLI 增量接线 | `materialize_daily_basic_cli` + `--mode incremental`；步内无直接 `materialize_daily_basic(` | PASS |
| CLI 解析 | `cli_mode_incremental_parsed` rc==0 end=20261024（/tmp stub） | PASS |
| 全量闸 | 无 env→拒；`QL_DB_ALLOW_FULL=1`→dry_run 可入 | PASS |
| 原子 manifest | final 存在、无 `.tmp` 残留、dest parquet | PASS |
| SHA_KEYS | `driver_sha_keys_has_incr` / `has_transform`；驱动 sha=f1910e8a | PASS |
| f99 / incr 未动 | `f99_bytes_unchanged`；`incr_sha_unchanged` | PASS |
| 生产隔离 | `prod_valuation_sha_inventory_equal` n=6 | PASS |
| tier1 静态 | `QL_DB_ALLOW_FULL` 闸；`os.replace` manifest；无整表 history_diff 回退 | PASS |

说明：自测未直接调用驱动 `check_pins()` 函数入口，但静态断言 + Arch 侧复算 transform / 磁盘 sha 已覆盖同等语义。无生产 `read_schema` 重活。

## P0 / P1

**P0：无。**

**P1（启用前，非本晚）：**
1. 签发 enable .ok 时必须带齐 `sha_daily_basic_incremental` / `pin_daily_basic_transform` / `sha_driver=f1910e8a…`（全长），并另裁窗与 `allow_*`。
2. 例程切换至新驱动须单独授权；禁止改 f99 字节顶替。

**P2：**
1. META `post.ENABLE_PACK_META.json` 自指 sha 过期（`713bd7c5…` vs `3a2910ac…`）。
2. scope 文件注释或仍写「常量」字样（DIFF 已披露）；以驱动 `SHA_KEYS` 为准。
3. impl r2 .ok 内旧 tier1 钉与现网 enable 钉并存——启用签收以本包/现盘为准。

## 启用前条件（清单）

1. 本审查结论保持 PASS_WITH_CONDITIONS（或嗣后 SUPERSEDE）。
2. 现盘钉仍 MATCH 本表（驱动 f1910e8a / nightly 2b4704e8 / tier1 7205ba43 / incr a7ac54b3 / scope 428a05d4 / transform 308b5054 / f99 未动）。
3. 主 Agent **另令** 允许签 enable（**今晚默认否**）。
4. enable .ok 键集含两 SHA_KEYS 新键 + `sha_driver` 全长；`live=false` 除非另裁。
5. 不与叶25/纸面/补跑/stream run 混签。

## 明确裁定

- **今晚不签 enable .ok。**
- **不签 run / 纸面 / 补跑 .ok。**
- 父会话勿将本审查误读为启用授权。

## 给主 / Eng 摘要

> Arch：daily_basic v3.1 启用包（重交，驱动 **f1910e8a…**）审查 **PASS_WITH_CONDITIONS**。包 sha 与现盘钉全 MATCH；SHA_KEYS/OK_KEYS（`+ list(SHA_KEYS)`）裁示闭合；自测 32/0；valuation 未写；f99 未动。**今晚不签 enable。** 条件见审查文启用前清单。live=false。
