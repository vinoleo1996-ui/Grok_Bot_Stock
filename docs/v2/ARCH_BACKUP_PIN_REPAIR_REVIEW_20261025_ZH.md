# Arch 窄口审阅：BACKUP_PIN 断链重钉（盒机刷新后）

- 时刻：2026-10-25T01:25:05-04:00
- 依据：主 Agent 01:24 ET 编排步骤 1；核验文 `ARCH_BOX_RECOVERY_VERIFY_20261025_0123ET_ZH.md`
- 结论：**PASS — 准予签发单次重钉 .ok**
- live=false；非补跑、非 enable、非纸面、非 stream run

## 现盘（只读复算）

| 文件 | 角色 | inode | nlink | size | sha256 前缀 |
|------|------|-------|-------|------|-------------|
| backups/valuation/…1136.parquet | src_1 | 138101 | 1 | 743884130 | 4820339f… |
| backups/valuation_pinned/…1136.parquet | dst_1 | 138684 | 1 | 743884130 | 4820339f…（=src） |
| backups/valuation/…1137_dupbug.parquet | src_2 | 138117 | 1 | 744405927 | 5c3ed5f6… |
| backups/valuation_pinned/…1137_dupbug.parquet | dst_2 | 138733 | 1 | 744405927 | 5c3ed5f6…（=src） |

旧收据（nlink=2 / inode 346570·2662401）已失效；CONSUMED `.ok` aeb86f8d 不得复用。

## 重钉步骤（Data 唯一允许动作）

对每一对 (src, dst)：

1. `stat` 确认 size 与上表一致、src≠dst inode、二者 nlink=1。
2. **允许**对 src/dst 做 sha256 预检（须相等；已由 Arch 复算，Data 应再验一次）。
3. `os.unlink(dst)` —— **仅**当 sha 全等；禁止 unlink src。
4. `os.link(src, dst)`（禁止 copy/move/overwrite 其它路径）。
5. `stat`：src 与 dst **同 inode**，**nlink=2**，size 不变。

收据：`docs/v2/audit/fundport_20261025/BACKUP_PIN_REPAIR_RECEIPT_20261025.json`（字段同前次 + `repair=true` + 双方 sha256）。

## 明确禁止

- 写 `data/v2/valuation/*`（含 full / valuation_tushare）
- prune / 删除 src / 改代码 / 开增量或 nightly
- 复用旧 .ok 或旧收据充当 PASS

## sd1_work 澄清

工作区在 `/workspace/sd1_work`（非 QuantLab 子目录）。恢复核验 PASS 仍要求该树稳定在盘。

## 签发

见 `output/data/ARCH_RUN_AUTH_DATA_BACKUP_PIN_REPAIR_20261025.ok`。
