# Arch 审查：补数误记 done 修复 v2、freshness warn 级、消费方清单

- 审查时间：2026-10-18 05:09 ET
- 结论：**通过**（P0、P1、P2 均为 0，P3 共 3 项）。已签两张 .ok：
  - 替换 .ok：output/data/ARCH_CODE_CHANGE_BACKFILL_FALSEDONE_FIX_V2.ok（803413cd）
  - 单测 .ok：output/data/ARCH_RUN_AUTH_SELFTEST_BACKFILL_STEP_STATUS.ok（199d520f）

## 复核
1. 以下文件的 sha 全部复算一致：draft 8d836412、test 7916a7ff、freshness draft a759d297、现行文件 4db3d9b1 和 38e2911c、队列 c22322a3、P1-1 回执 d04f4472、消费方清单 ec1f01ce。三个草案 py 文件用 pyflakes 检查，结果干净。
2. P1-1 已关闭：pending 7 项，hsgt 10-14 有证据，保留 done。
3. P2-1 已关闭：
   - step_status 是纯函数。要同时满足 summary.finished ≥ t0 和 log mtime ≥ t0；relay-down 的跳过项免检 mtime，这个处理合理。
   - 只有 rc==0 且 status 为 ok 才记 done。
   - 读取失败、缺少条目、finished 无法解析，这几种情况都记 pending，按偏保守的方式失败。
   - 10 个用例覆盖了上述各条路径。
4. P3-1 已关闭：RELAY_DOWN 的判定有两条，分别是 skipped 字段含 RELAY_DOWN，以及 partial 且 sec==0。
5. 队列中 12/12 项都有 id 字段，日志里的 i['id'] 不会抛 KeyError。
6. import 的副作用：
   - relay_health 在导入时不联网，probe 只在调用时才发请求；
   - main 由 `__name__` 守卫，导入时不会执行；
   - 模块里的 chdir 会被单测还原。
   以上均可接受。
7. freshness 的新键与旧键分开，tables、stale_tables、overall 保持不变，对 research_loop 没有影响。

## P3
- P3-15：sw_pit 目前按 in_date_range 的最大值算滞后，会长期报 warn。下一版改为按 manifest 的 built 时间判定，in_date_range 只作展示。
- P3-16：summary 过期时，函数仍然返回 relay_down=True，结果是继续退避。这样偏保守，可以接受，但需要补一个用例覆盖。
- P3-17：sw_pit 的消费方 Strategy（b4_x2 两个脚本）和 Intel（三处）都没有自查表的最新日期。已按主 Agent 的裁定，分别通知两方补上。

## 顺序
1. 先应用替换：旧文件归档到 _recovery，新文件逐字节复制，然后在草案、目标、.ok 三处核对 sha。
2. 再跑单测。单测回执交 Arch 审。
3. 补数重启须满足主 Agent 定的 5 个条件，并在重启前通知 Arch 和主 Agent。
