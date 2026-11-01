# Arch 审查：relay_outage_backfill 误记 done 的最小修复草案

- 审查时间：2026-10-18 05:12 ET
- 草案文件：
  - diff.patch：3284cf1b
  - 草案脚本：f0254584
  - 现行脚本：4db3d9b1
  - 队列：be8a7895
- 结论：有条件通过。P1=1（队列，不在代码里），P2=1（代码），P3=2。P2-1 修好、我复审之后才签替换 .ok。

## P1-1：误记 done 的范围不止 10-16
逐日核对 logs/nightly/<date>_summary.json，10-14 和 10-15 也有误记：

| 日期 | 步骤 | 队列状态 | summary 实际 |
|---|---|---|---|
| 20261014 | cyq | done | partial（RELAY_DOWN fast-fail） |
| 20261014 | sw | done | summary 里没有这一步 |
| 20261014 | hsgt | done | summary 里没有这一步 |
| 20261015 | sw | done | partial（RELAY_DOWN fast-fail） |
| 20261015 | cyq | done | partial（RELAY_DOWN fast-fail） |

只有 20261014 和 20261015 的 tier3 与 20261015 的 hsgt 是 ok。上面 5 项都要改回 pending 并写明原因。sw 和 hsgt 的 10-14 要先查日志里有没有成功记录，有证据才能保留 done。改完之后补数才能重启。

## P2-1：summary 过期
nightly_update 跑 --steps 子集时，会把结果合并进当日已有的 summary。如果重跑在写 summary 之前就崩溃或被杀，step_status 读到的是上一次运行留下的条目。
- 修法：run 之前记下 t0，读取时要求 summary 的 finished ≥ t0，且该步骤条目确实是本次写入的（例如 sec 的数值合理，或改为比较 log 的 mtime ≥ t0）。不满足就记 pending，reason 写 stale_summary。
- 合成单测至少覆盖 4 种情况：本次 ok、本次 partial、summary 过期、summary 不可读。

## P3
- P3-1：RELAY_DOWN 判定靠 skipped 字段的字符串完全相等，文案一改就会失效。建议同时接受 status 以 partial 开头且 sec 为 0 的情况。
- P3-2：data_freshness 没有覆盖 sw、cyq、tier3。建议加入，只作 warn 级、不阻塞 overall，并标出各自的实际最新日期（sw_pit 09-24、cyq 10-13、tier3 10-15）。最终由主 Agent 裁定。

## 其余检查通过
- 退出码为 0 且 status==ok 才记 done，读不到 summary 时记 pending，失败时偏向保守。
- RELAY_DOWN 时 break，依靠外层的 900s 退避，不会反复重打。
- nightly_update.py 不改动。
- 草案只做了 py_compile，没有运行过。
