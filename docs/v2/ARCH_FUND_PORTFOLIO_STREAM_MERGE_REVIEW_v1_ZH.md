# fund_portfolio 流式合并设计 v1 — Arch 复审（预备）

live=false；promotion=false。
- 审查对象：docs/v2/DATA_FUND_PORTFOLIO_STREAM_MERGE_DESIGN_v1_ZH.md
- 设计 sha256：b78cc9e1db381f9fef43e32d3b83d83b6053d6b80aa0ecf783353b733c5c14c7（160 行）
- 审查时刻：2026-10-25T00:14:19-04:00 ET
- 性质：**预备复审**（Leo 尚未确认启用路径；本文件不构成改码或运行授权）
- 方式：只读静态；未读真实 parquet 行、未改代码、未发信号

## 结论（预备）

**PASS_WITH_CONDITIONS**（条件见下）。方向正确，可消旧 L96 整表 concat 的内存与半截写风险；Eng 落地须等：Leo 放行 + 本文条件闭合 + 另签实现审阅 .ok 与单次运行 .ok。

## 已对齐的优点

1. 按期持有、禁止跨期 concat；最终 ParquetWriter 按期流式拼。
2. O_EXCL + os.replace；inode ledger 清理；退出码从 20 起；TERM→31、HUP→32。
3. available_at 逐步对齐 L97–102；自测强制 /tmp；源分片只读 sha 清单。
4. 峰值目标严于 1.5GiB 红线（单进程 1e6 kB）。
5. 启用顺序明确：审 → 进程已退出/TERM → Eng → 双 .ok → 回执。

## 条件（须进 v1.1 或实现前闭合）

| ID | 级别 | 内容 |
|---|---|---|
| C1 | P1 | **期内** concat 若一期页数仍大，须在 v1 正文写清「按文件批」上限（O2 默认允许不够）：每批文件数或行数硬顶，批间 del；否则单期仍可能顶穿 1e6 kB。 |
| C2 | P1 | `deadline`/`tdays` 依赖 trade_cal：实现须钉 trade_cal 路径与 sha（或只读 pin），自测注入合成日历；禁止隐式读活路径未声明。 |
| C3 | P2 | 省略无键 drop_duplicates（O1）：须有合成夹具证明「仅键去重」与「先无键再键去重」在 keep=first 键集合上一致，否则保留无键步但只在期内。 |
| C4 | P2 | 最终拼接触发：必须新 CLI；旧 L96 在启用 .ok 生效后改为 `raise RuntimeError("disabled")`（删除整函数风险更大，优先硬失败）。O3 采纳「新 CLI + 旧函数改调用」。 |
| C5 | P2 | run_id 目录若上次崩溃残留：启动时只清理**本进程将创建**的路径；发现同名 run_id 已存在则换新 run_id，禁止复用半截。 |
| C6 | P2 | manifest/DONE 原子写细节：先写 `.tmp` 再 `os.replace`；DONE 内容=最终表 sha256 与 manifest.sha256 一致。 |
| C7 | P3 | MemAvailable 阈值 2621440 kB（O4）写入运行 .ok，驱动/脚本不硬编码魔法数。 |
| C8 | P3 | Q8 broker_recommend（O5）明确不在本启用窗口；运行 .ok `allow_broker_recommend=false`。 |

## 开放项裁定（Arch 预备）

| ID | 裁定 |
|---|---|
| O1 | 采纳 Data：默认不保留无键 drop；C3 夹具必过。 |
| O2 | 允许期内按文件批；C1 须写硬顶。 |
| O3 | 新 CLI + 旧路径硬失败。 |
| O4 | 2621440 kB，写入运行 .ok。 |
| O5 | fundport DONE 后再谈 Q8；本 .ok 禁 Q8。 |
| O6 | 新 log 路径写入运行 .ok。 |

## 与 94322 / BACKUP_PIN 的关系

- 2026-10-25 00:11 起 94322 已不存在；TERM .ok 当前无签发对象。
- 流式合并不依赖 TERM，只要「无最终产物」且另签运行 .ok。
- BACKUP_PIN 与本文无关；另窗另签。

## 下一步（阻塞在 Leo）

1. Leo 确认是否重签 BACKUP_PIN、是否放行流式合并路径。
2. Data 交 v1.1（闭合 C1–C8）或 Eng 在实现 PR 中逐条回应。
3. Arch 正式复审（去掉「预备」）→ 签实现审阅 .ok → 自测绿 → 签单次运行 .ok。

live=false；promotion=false。
