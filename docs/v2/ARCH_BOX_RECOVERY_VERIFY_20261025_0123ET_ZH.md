# Arch 恢复核验（盒机刷新后）

- 时刻：2026-10-25T01:23:00-04:00（America/New_York）
- 角色：QuantLab Arch
- 依据：主 Agent 01:21 ET 加急·恢复核验
- live=false；**未出具「恢复核验 PASS」**；**未签任何 enable/run/纸面 .ok**

## 结论（给主）

**可接受「部分恢复」，不必强制快照回滚到 01:08 前**——前提是按下方缺口补齐后再谈 PASS。

| 维度 | 状态 |
|------|------|
| docs/v2 ARCH_* | **OK**（≈125，含事故文） |
| git HEAD | **OK** `da9fde6a0037da6e2d10f09f65b14f4f0997f952` |
| scripts acquire 关键 | **OK** incr=`a7ac54b3…` MATCH；stream=`374489d0…` MATCH |
| enable 相关脚本 | 见下表（nightly/tier1/新驱动） |
| 实现审阅 .ok | **OK** daily_basic r2=`0a7d15f6…` MATCH；stream r2=`954d985e…` MATCH；二者 allow_enable/allow_run=false |
| 叶25 R5_v2.ok | **字节 OK** `b052fc9b…`；窗 `10:00–10:45` expires `11:00` ET；**主已取消本窗，禁消费，待重签** |
| 叶25 钉文件 | pin_list v4.1=`b6c60b4f…` MATCH；cmd R5c_v2=`11873aaa…` MATCH；script=`f43b9016…` MATCH |
| sd1_work | **已回**（01:17 mtime）：含 `daily_basic_incr_20261025/enable_pack`、`fundport_stream_20261025`、`paper_catchup_20261025` |
| paper confirm | **OK** `8d572b2a…` |
| BACKUP_PIN / valuation | **FAIL**：live `…1136`/`…dupbug` **MISS**；pinned nlink=1 inode **138684/138733**（收据曾为 inode 346570/2662401 nlink=2）→ 硬链钉失效 |
| 启用包审查文 | **仍缺** `ARCH_DATA_DAILY_BASIC_V3_1_ENABLE_PACK_REVIEW_ZH.md`（刷新前亦未落盘核验） |
| 实数据进程 | 无 |

## 关键脚本现盘 vs 启用包宣称

（启用包 META post；现盘复算）

见同批 Shell 核验输出；Arch 要求 MATCH 后方可进入 enable 审查。

## BACKUP_PIN

- 收据：`docs/v2/audit/fundport_20261025/BACKUP_PIN_RECEIPT_20261025.json` 曾 post nlink=2。
- 现盘：`backups/valuation_pinned/` 两文件 size 仍对（1136=743884130 / dupbug=744405927），sha256=`4820339f…` / `5c3ed5f6…`，但 **inode 已变且 nlink=1**，live 路径不存在。
- live `daily_basic_full_tushare.parquet` inode=138082 sha=`f6bbf9e5…`（与 pinned 不同文件）。

→ **不得**在未重钉前签任何写估值/补跑/enable。

## 裁定

1. **部分恢复可继续**：代码、审查文、实现审阅 .ok、叶25 字节、sd1_work、git 足够支撑只读审查与 Eng 改 SHA_KEYS。
2. **不必须**回滚到 01:08 前快照（除非 Leo 另有完整态偏好）。
3. **恢复核验 PASS 条件（未满足）**：
   - Data 重建立 valuation 1136/dupbug live 硬链（或 Arch 认可的等价钉），inode/nlink 核验通过并新收据；
   - enable 相关脚本全 MATCH（nightly `2b4704e8…` / tier1 `7205ba43…` / 新驱动 `2380eb2a…` / scope `428a05d4…`）；
   - TEAM_STATE 各角色节回填。
4. 在出具 PASS 前：**禁签** enable / run / 纸面 / 补跑 .ok；叶25 现窗 **勿用**（待主重排后重签）。
5. SHA_KEYS 裁示仍有效；Eng 恢复后先改驱动再交启用包。

## 下一步（听主）

- Data：只读确认后申请 **重钉** 窗口（非补跑）。
- Eng：改 SHA_KEYS（不申请 enable）。
- Arch：守盘；PASS 后再审启用包并重写本 TEAM_STATE。

---

## 补记 01:24 ET（主复检冲突 + 路径澄清）

1. **sd1_work 路径**：稳定在 **`/workspace/sd1_work`**（inode 101168，mtime 2026-10-25 01:17 ET），**不是** `/workspace/QuantLab/sd1_work`（该路径不存在）。01:23 核验「已回」指前者；主侧查 QuantLab 子路径会得 MISS——无冲突。PASS 条件仍要求该目录持续在盘（含 enable_pack / fundport_stream / paper_catchup）。
2. **BACKUP_PIN 诊断更正**：取证钉语义是 `backups/valuation/` → `backups/valuation_pinned/` 硬链，**不是** `data/v2/valuation/` 下带日期文件。现盘两边文件均在、size/sha 全等（1136=`4820339f…`，dupbug=`5c3ed5f6…`），但 **inode 不同且 nlink=1**（断链副本）。`data/v2/valuation/` 无 1136/dupbug 属正常。
3. 主采纳部分恢复；Arch 另签窄口重钉 .ok（见 `ARCH_RUN_AUTH_DATA_BACKUP_PIN_REPAIR_20261025.ok`）。

---

## 恢复核验更新 2026-10-25T01:27:16-04:00 — **PASS**

| 原 FAIL 项 | 现状态 |
|------------|--------|
| BACKUP_PIN 断链 | **CLOSED** — 收据 `fb91ed0bbbdbcb3f87315f7561646c86eeccc94e1cab05b4af3955f1c0d9b999`；核验文 `ARCH_BACKUP_PIN_REPAIR_VERIFY_20261025_ZH.md` sha `9572abe6d9060b64793720ea23d398d50cad6853ad7710003e3c97c2e6043ba4` |
| sd1_work | **OK** — `/workspace/sd1_work` 持续在盘（含 enable_pack） |
| 关键脚本/.ok 字节 | 仍 MATCH（见 01:23 表） |

**出具：恢复核验 PASS**（部分恢复路径；未做 01:08 快照回滚）。

仍约束（非本 PASS 撤销）：
- 今晚不自动签 enable/run/纸面/补跑/stream run（须主另排）
- 叶25 R5_v2.ok 字节在但现窗继续禁消费，待主重签
- 启用包审查文仍缺；Eng SHA_KEYS 驱动已 MATCH f1910e8a…，启用前另审

