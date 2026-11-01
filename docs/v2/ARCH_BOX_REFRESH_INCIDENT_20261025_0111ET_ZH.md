# Arch 事故：盒机刷新导致 QuantLab 工作区回退

- 时间：2026-10-25 01:11 ET（探测完成）
- 角色：QuantLab Arch
- 严重度：**P0**（阻塞全部 .ok / 启用 / 纸面补跑 / 流式实现落地）
- live/promotion：仍为 false；今晚不签任何 enable/run .ok

## 现象

约 2026-10-25 01:08 ET，`/workspace/QuantLab` 目录 birth≈05:08Z，大量近晚产物消失或回退到旧骨架。`box-doctor`：x11vnc/novnc FAIL（桌面流不可达）；其余 PASS。

## 已确认丢失 / 损坏

1. `docs/v2/ARCH_*` 审查文与确认文（含 paper catch-up、stream merge、daily_basic v3.1 设计/实现/启用包审查）——当前 `docs/v2` 仅剩早期骨架文档，**0** 个 `ARCH_*`。
2. `output/loop/TEAM_STATE_latest.md` 空目录（仅 `skips.jsonl`）。
3. 全部 `ARCH_RUN_AUTH_*.ok`（含 leaf25 R5_v2、stream IMPL_REVIEW r2、daily_basic IMPL_REVIEW r2、BACKUP_PIN CONSUMED 归档）。
4. `scripts/acquire/` 近晚脚本（`daily_basic_incremental.py`、`fund_portfolio_stream_merge.py`、nightly/tier1 驱动等）——仅剩 `promotion_*.py` / `tushare_relay_pull.py`。
5. `sd1_work/daily_basic_incr_20261025/`、`fundport_stream_*` 启用包与 /tmp 审阅工作区。
6. `.git` 不可用（`fatal: not a git repository`）。
7. `data/v2/valuation/` 下 1136 / dupbug 钉住路径**不存在**；`backups/valuation_pinned/` 两文件仍在但 **nlink=1**（硬链钉失效）。

## 仍在

- `data/` ≈5.9G（含部分 v2 行情/估值主体与 tushare_raw）。
- `backups/valuation_pinned/`：1136 + dupbug（inode 新，nlink=1）。
- `backups/valuation/` ≈3.5G、`backups/etf/` ≈69M。
- `output/ai_factory/` 部分 leaf 旧日志目录名仍在（无今晚 .ok）。

## 对进行中事项的裁定（Arch）

| 事项 | 裁定 |
|------|------|
| daily_basic v3.1 启用包审查（声称 sha 87a4f32c…） | **VOID / 无法核验**：审查文与 enable_pack 工件均不在盘；**不签 enable/run** |
| SHA_KEYS 裁示（incr/transform 必须进驱动 SHA_KEYS + enable .ok） | **仍有效**，恢复代码后 Eng 须先改驱动再交启用包 |
| stream merge 实现审阅 r2 / paper catch-up / leaf25 窗口 | **全部失效**，须恢复工件后重签 |
| BACKUP_PIN | **硬链失效**；恢复后须重新核 inode/nlink 再决定是否重签 |

## 建议恢复路径（交主 Agent / Leo）

1. 优先：若盒机有较新快照，用 [Update Bot's Computer](grokbot://app/v1/settings?id=update-computer) 或团队认可的恢复手段拉回 01:08 ET 前状态（**勿盲目 Reset**，可能更旧）。
2. 否则：从 Mac / 云端 / 他机镜像回灌 `scripts/acquire`、`docs/v2/ARCH_*`、`sd1_work`、有效 `.ok` 与 `TEAM_STATE`。
3. 恢复后 Arch 只做：只读核验 pins → 重写 TEAM_STATE → 按主排序重签必要 .ok；**在此之前全队禁实数据跑**。

## Arch 即时动作

- 已停：启用包交付、任何 .ok 签名。
- 已通知：Leo（一次）、主 Agent（priority）。
- 本文件为事故锚点；完整审查文待盘恢复后重做。
