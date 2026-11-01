# Eng：daily_basic 驱动 SHA_KEYS 落地（incr/transform）

- 时刻：2026-10-25T01:25:01-0400（America/New_York）
- 依据：Arch 01:12 VOID 裁示 + 主 01:24「可准备/落地 SHA_KEYS，不申请 enable/run」
- live=false；**未申请 enable/run**；未改生产路径；未臆造启用包目录

## 变更

| 项 | 值 |
|---|---|
| 驱动 | `docs/v2/audit/nightly_20261019/run_nightly_v1_dbincr_v3_1.py` |
| 旧 sha（常量死钉版） | `2380eb2ac8fba1978dd47b916c6f43dcb18cb1b8ad30565b12defee7d4acffd1` |
| **新 sha** | `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05` |
| f99dd11a | **未动** `f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a` |

### SHA_KEYS 新增（进入 OK_KEYS_REQUIRED）

| 键 | 路径/语义 | 钉值 |
|---|---|---|
| `sha_daily_basic_incremental` | `scripts/acquire/daily_basic_incremental.py` | `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8` |
| `pin_daily_basic_transform` | `__computed__/daily_basic_transform_sha`（非文件） | `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974` |

- `check_pins`：incr 对照磁盘文件 sha；transform 调 `compute_transform_sha(tier1)` 对照钉值。
- `check_ok`：.ok 必填上述两键且值==钉（启用 .ok 模板须同步；本晚不签）。

## 核验

- `check_pins()` → None（PASS）
- incr 磁盘 sha MATCH；transform 复算 MATCH
- nightly/tier1 仍为启用包钉：`2b4704e8…` / `7205ba43…`

## 未做

- 不申请 enable/run .ok
- 不改例程、不切驱动
- 不写生产 valuation；不臆造 `sd1_work` 启用包内容
