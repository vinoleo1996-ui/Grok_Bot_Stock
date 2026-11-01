# daily_basic 增量设计 v3.1 — Arch 审查（C1–C12 闭合）

live=false；promotion=false。
- 审查对象：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_1_ZH.md
- 设计 sha256：**5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc**（**460** 行；Data 自称 461 行 → 差 1，不挡确认，记 P3）
- 审查源（含复审 C1–C12）：docs/v2/ARCH_DAILY_BASIC_INCREMENTAL_REVIEW_ZH.md，sha256 **48a64380682e593adb1d3386ae92126df4173e31c61b7699ff6ce8f7b06fe18a**（524 行，已核）
- 基线 v3（未动）：docs/v2/DATA_DAILY_BASIC_INCREMENTAL_DESIGN_v3_ZH.md，sha256 **13fd86b67ba6c8d074aba08d8a3ad3cac93fd7ebbae9acbe41547e80c15d0aab**（336 行，已核）
- BACKUP_PIN 回执：docs/v2/audit/fundport_20261025/BACKUP_PIN_RECEIPT_20261025.json，sha256 **15905d602e0df9041f50248dccfdea513d43284dde48fc23a630bcd3fac48cf1**（已核；文首/§2.10/§7.1 均不再列为待办）
- 审查时刻：2026-10-25T00:30:16-0400（America/New_York）
- 方式：只读静态；未改仓库代码、未读真实 parquet 行、未发信号、**未签任何 .ok**（含补跑/启用/实现/运行）

## 结论

**PASS**（设计确认）。C1–C12 均已在 v3.1 正文按复审要求闭合；相对 v3 的差异限于声明范围（C 项补丁 + A12–A18 + D1–D4 + 启用条件改写），未见回退为旧全量/旧码表/「或已由 Arch 裁定」等危险路径。

- **可向 Data 宣布「设计确认」**（本审查即确认；设计文件冻结为上述 sha，勿覆盖）。
- **今晚不签**补跑 .ok、启用 .ok、实现审阅 .ok、运行 .ok。
- 启用仍须：**Eng 代码 diff 逐条对应 C1–C12** + selftest/盘点/基线等门禁 + **另签启用 .ok**（10-20 窗已过期，条件见设计 §6.1）。
- §7.2 三项（AST 规范化具体代码、`raw_touched` 路径与清除权属、新驱动文件名）**不挡本设计确认**，但**挡启用 .ok**。

## 材料核验

| 项 | 结果 |
|---|---|
| 设计 sha | 与 Data 声称一致：`5c6a3a1dcc0fdcba…` |
| 设计行数 | 实测 460；声称 461 → **P3 差 1** |
| 审查源 sha | 与文首一致：`48a64380682e593a…` |
| v3 sha | 与文首一致且文件未动：`13fd86b67ba6c8d0…` |
| BACKUP_PIN | 回执 sha 与文首一致；决定 (a) 已完成 |
| 对照表行号 | Data 给出的 C1–C12 行号与正文落点一致（已抽读） |

## C1–C12 状态表

| ID | 状态 | 证据（行号 + 要点） |
|---|---|---|
| C1 | **CLOSED** | L112–120 / §2.3：完整文件名 `^\d{8}\.parquet$`；废止 v3 错位 `$`；*.tmp.parquet→27 |
| C2 | **CLOSED** | L197–205、L217–240、§8 L345–414：SIGHUP=**32** DB_INCR_SIGNAL_HUP；码表删 -1；SIGTERM 回滚后重发→-15；草图 HUP 不重发直接 return 32 |
| C3 | **CLOSED** | L137–143：transform_sha=规范化 AST dump（去 docstring）+常量表；废止 inspect.getsource；runtime_versions（python/pandas/pyarrow/numpy）变亦退 28 |
| C4 | **CLOSED** | L144–148：_one 外提模块级；A14 合成文件 22 列 hash 与旧闭包逐文件相等；Eng diff 单独成段 |
| C5 | **CLOSED** | L197–205 + 草图 L382–385：except 入口先 SIGTERM/SIGHUP→SIG_IGN，清理完再按 C2 退出 |
| C6 | **CLOSED** | L206–209 + 草图 L369–372：O_CREAT\|O_EXCL 创建后立刻 fstat 记 (st_dev,st_ino)，再交 ParquetWriter |
| C7 | **CLOSED** | L324–328：S5 五阶段（拷贝/构建/回读/diff/提交）各随机 TERM；TERM→退出 ≤5 s；A15 回滚完整 |
| C8 | **CLOSED** | L286–300 / §5.2–5.3：废止「或已由 Arch 裁定」；新表+过时 manifest 两边都不信；基线仅 ref_build；盘点空档+命令清单先交 Arch+只读元数据；A18→退出 20 |
| C9 | **CLOSED** | L261–264：ref_build 最大年（1,313,182 行）VmHWM ≤ 1,000,000 kB = A13 |
| C10 | **CLOSED** | L102–111：快筛含 st_ctime_ns；raw_touched 或 .ok 注 raw_full_sha_required=true 强制全量内容 sha；A17 |
| C11 | **CLOSED** | L181–191 + 草图：pending 恢复 → STALE_TMP → 前置；成品未变时本次自移 pending 至 _quarantine |
| C12 | **CLOSED** | L166–179：硬链接失败撤回（核同 inode）；成品只许 os.replace；备份名 `%Y%m%d_%H%M%S` 精确到秒 |

**汇总：CLOSED 12 / PARTIAL 0 / OPEN 0。**

## 相对 v3 / 审查源的差异与回退风险

1. **差异范围**：v3.1 为 v3 复制改写，专为闭合复审 C1–C12 与决定 (a)–(g)，并纳入 A12–A18、D1–D4；启用条件由「10-20 05:00 ET 窗」改为「Arch 确认 + Eng diff 对 C1–C12 + 另签 .ok」。
2. **废止引用（非回退）**：正文中仍出现的 `^\d{8}$\.parquet`、`inspect.getsource`、「或已由 Arch 裁定」、`-1 / SIGNAL_HUP`、NO_PRUNE 等字样，均为**标明废止/已完成**的对照句，码表与草图已切到新语义。
3. **回退风险**：**低**。未见恢复旧全量默认、恢复 -1 作 HUP 码、恢复「Arch 裁定可用过时 manifest」、或把 BACKUP_PIN 再列为待办。v3 文件字节未动，可溯源。
4. **适应性改写（合理）**：C8 原「10-19 18:40 之后盘点」因窗过期，改为「Arch 指定空档 + 无其他真实数据进程」——符合现状，不降低只读边界。

## 残留 / 不挡设计确认（挡启用）

见设计 §7.2：
1. AST 规范化具体代码（函数集、dump 选项）——Eng 提案，Arch 审定后钉进代码/本节补丁。
2. `raw_touched` 标记路径与清除权属——须进恢复/回补工具的 .ok 模板。
3. 新版驱动文件名与冻结清单——Arch 签启用 .ok 时一并钉。

另 **P3**：Data 自称 461 行，实测 460 行（末行「（完）」+ 换行）；对照表行号仍正确，不要求改文重交。

## 下一步（PASS 后）

1. **Data**：接受本审查为 v3.1 **设计确认**；冻结 `5c6a3a1dcc0fdcba279cafbbacf64c829fc50ee9ed3faf0d8095b6dc4b8c17fc`，勿再改字节除非 Arch 开 v3.2。今晚无补跑 .ok；叶25 窗 10:00–10:45 ET 仍不写生产。
2. **Eng**：按 v3.1 实现；代码 diff **逐条标注 C1–C12**；改码前归档 tier1_materialize.py（e9c89a6c…）与 nightly_update.py（ec079d56…）至 `_recovery/data/daily_basic_incr_<stamp>/`；selftest 全 /tmp，覆盖 A12–A18。
3. **Arch（后续，非今晚）**：审 Eng diff → 签实现/selftest 相关 .ok → 盘点/基线 .ok → **另签启用 .ok**（注释：增量模式、自检阈值、首晚 VmHWM、SIGHUP=32）。**今晚不签补跑/enable/实现/运行 .ok。**
4. **主 Agent**：本设计确认与纸面 catch-up / 叶25 并行不冲突；增量启用仍走完整门禁链。

（完）
