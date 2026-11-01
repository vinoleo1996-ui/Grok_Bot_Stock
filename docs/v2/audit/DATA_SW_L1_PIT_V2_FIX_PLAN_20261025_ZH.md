# 申万 L1 PIT v2 修复方案草案（2026-10-25）——文档 only，交 Arch 审

- 作者：QuantLab Data 执行器；写成 ≈2026-10-25T12:22 ET（America/New_York）
- 性质：**方案草案**。本回合**不实修**；未改任何 parquet / `.ok` / `probe5_small.py` / TEAM_STATE / 生产路径；未消费补跑 `9e4359f9`；中转 SUSPEND 维持。
- live=false；promotion=false。Arch 今日审计钉 **sw_l1 UNCHANGED**（`AUDIT_20261025_1211_ET_ZH.md` / 回执语境 `c8877760`）：CLEAN `89d4afa3` MATCH。
- 证据基线：`ARCH_SW_L1_GAP_IMPACT_20261018_ZH.md`；`data_ro_audit_20261018/`（`SW_IMPACT_INVENTORY_ZH.md`、`EVIDENCE_…`、`B_missing_codes_classified.csv`、`A_12codes_open_records.csv`）；现盘只读复算（pyarrow/pandas，无写）。

## 1. 结论（先行）

| 桶 | n | 根因 | 建议阶段 |
|---|---|---|---|
| 双开未结束 | 12 | 全量分页陈旧 open 与分拉 closed 并存；merge 无 open/closed 优先级 | **P0** 闭合（丢陈旧 open，保 ≤1 open/码） |
| 235 误删 | 235 | 10-14 04:00 `sw_pit_refresh` 截断重拉覆盖修补表；整段历史从 BAD 消失 | **P1** 从 bak `59734014` 恢复 open 行（离线，不需 Tushare） |
| 68 截断 | 68 | 全量分页截断未回填；仅分拉/CLEAN 有 | **P2** 以 CLEAN/`89d4afa3` 血统 +（另窗）分拉 raw 补；SUSPEND 期禁大批补拉 |
| 46「源缺」 | 46 | BAD 仅有 closed 史；其中 33 只 bak 仍有 open（Arch：我方关/删） | **P3** 能从 bak/CLEAN 恢复的并入 P1 口径；真无源的标 `quality_status=source_gap`，不编造 |

- **本回合不实修**；实施须 Arch+主排期，分步签 `.ok`（code-change → selftest → dry-run→/tmp → execute），避开纸面窗与叶并发。
- **首修建议：P0 → P1**（P0 是不变量；P1 用 bak 离线、中转 SUSPEND 下可做；P2 依赖另窗 relay）。
- **叶25 另轨**：`sw_members_asof` PIN_OK_WITH_CONDITIONS `4e4ca0b8` / 脚本 `dec73305` 须**共钉 cal+SW**；**修复生产 PIT 表 ≠ 解阻叶25**，不替代 mem_probe / X2 分 `.ok`。

## 2. 现盘只读核验（相对 10-18：**MATCH，无漂移**）

| 表 | 路径 | sha8（全长见文末） | 行/代码 | open 行/码 | 双开 | 相对 10-18 |
|---|---|---|---|---|---|---|
| BAD | `data/v2/sw_pit/industry_members_sw_l1_pit.parquet` | **0b1d3432** | 7573 / 5600 | 5566 / 5554 | **12** | MATCH |
| BAK | `…/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet` | **59734014** | 7743 / 5759 | 5736 / 5724 | 12 | MATCH；235/235 仍有 open |
| CLEAN | `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | **89d4afa3** | 7920 / 5914 | 5914 / 5914 | 0 | MATCH（纸面/叶钉） |
| VOTE | `…/industry_members_sw_l1.parquet` | **87d769aa** | 7115 / 5847 | — | — | MATCH（风险旗标） |

- 缺当前成分：**349**（CSV 桶 235+68+46）；现盘仍 349 无 BAD open；CLEAN 349/349 有 open；46 中 bak open=**33**（与 Arch §1 一致）。
- 双开 12 码与 `A_12codes_open_records.csv` 名单一致（002420/002481/…/688002）。
- CLEAN/VOTE 纸面映射钉：**只记 sha，本方案不改、不覆盖**。

## 3. 修复步骤（伪步骤；无代码 patch）

输出约定（与旧方案一致）：**新文件** `data/v2/sw_pit/sw_l1_pit_v2.parquet` + manifest；**不覆盖** BAD `0b1d3432`、CLEAN `89d4afa3`。execute 前对 BAD 另打 `*.bak_pre_v2_<YYYYMMDD>.parquet`（可选；v2 路径本身可回滚）。

| 步 | 输入 | 输出 | 回滚 | 验收断言 |
|---|---|---|---|---|
| P0 双开闭合 | BAD + 分拉/CLEAN 同码 closed 优先规则 | v2 中间表（或 /tmp dry-run） | 丢弃 v2；BAD 不动 | 每码 open≤1；12 码无双开未结束；conflicts 明细落盘 |
| P1 235 恢复 | bak open 行（235）∪ P0 表；对照 CLEAN | v2′ | 删 v2′ / 用上一 bak | 235 均有 open；normdiff vs CLEAN open 可解释；纸面仍读 CLEAN（sha 不变） |
| P2 68 补拉 | CLEAN/分拉 raw；**另窗** relay 交叉核验（SUSPEND 禁大批） | v2″ | 同上 | 68 有 open 或显式 defer；每日缺成分仅剩源缺桶 |
| P3 46 标注 | bak 可恢复子集 + 真源缺 | v2 终稿 + manifest | 同上 | 缺当前成分仅 `source_gap`；无编造行业；promotion_approved=false |
| 闸门 | 代码数不缩（相对 bak/CLEAN 下界）；单进程 RSS≤1.5GB；nice 10 | — | — | 断言失败不落盘；非零退出 |

干跑：输出仅 `/tmp`；Arch 审 dry-run（无双开；缺成分仅源缺；vs `89d4afa3` open 一致或差异全解释）后再签 execute `.ok`。

## 4. 风险与门闩

- **纸面 runner**（capacity_adv/B4/S6）经 `g1g5_nontextbook_weights` 读 **CLEAN**，不读 BAD；修复不得污染 CLEAN/VOTE sha。
- **X2/Intel** 读 BAD（`strategy_*_x2`、`intel_common`）：修复后 `_UNK_` 桶与行业帽会变；须另影子对比 + 下游重签，**不在本方案自动触发**。
- **中转 SUSPEND / RELAY_DOWN**（`629921c6`；补跑 `.ok` `9e4359f9` 禁消费）：P0/P1 离线；**禁**对 Tushare 大批 `index_member_all` 补拉，除非主+Arch 另开窗。
- 防再缩表：execute 后禁止无闸 nightly `sw` 覆盖；旧 `sw_pit_refresh` 覆盖路径须先废或改写 v2（另工单，非本回合）。
- 资源：与叶/纸面错峰；MemAvailable&lt;2GB 暂停。

## 5. 非目标

- 不改 Strategy `sw_members_asof` / 叶25 asof 逻辑；不解阻叶25 X2。
- 不抬 live；不自动消费任何 `.ok`（含 `9e4359f9`）。
- 不改 BAD/CLEAN/VOTE 现盘字节；不写 TEAM_STATE；不 SendToAgent / 不报 Leo。
- 不把 46 只无源码编造进行业。

## 6. 确认

- [x] 只读核验完成；相对 10-18 **MATCH、无漂移**
- [x] 本文件为**唯一新建**交付；未改生产数据/脚本/TEAM_STATE
- [x] 建议首修：**P0（双开）→ P1（235 bak 恢复）**；P2/P3 待排期与 relay 窗
- [x] 叶25：`4e4ca0b8`/`dec73305` 共钉 cal+SW 另轨；修 PIT ≠ 解阻叶25
- [x] 实施前置：Arch+主排期 + 分步 `.ok`；本回合**不申请实修**

### 钉住 sha（全长）

| 对象 | sha256 |
|---|---|
| BAD | `0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6` |
| BAK | `597340148480675b09a0560ae7ce23917edf5f35c40e51c25c64f3b701f72c9c` |
| CLEAN | `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` |
| VOTE | `87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3` |


### 本文件 sha
- content sha256（§1–§6 正文，不含本段）: `ffa35e2038bbe960e53f56cfa6c732615b02901345fe86c4bd39457c82740d46`
- 整文件 sha256sum：以盘上 `sha256sum` 本文件为准（回报主 Agent；与 content 不同因含本段）。
