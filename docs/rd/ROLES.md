# 研发岗位

只通过 `docs/rd/messages.jsonl` 互通。一条意见没有 `evidence` 不能离开 `open`。子任务不能互相调用；算法总监把上一轮原文贴进下一轮。

| 岗位 | 这一阶段交付 | 不做什么 |
| --- | --- | --- |
| 产品 | 把记分卡里的采用结论写成意见 | 不新开收益目标 |
| 算法 / 股票池 | `experiments/universe.md` 三组对照 | 不改选股代码 |
| 算法 / 因子 | `experiments/factors.md` 三组对照 | 不用没有 `available_at` 的财务 |
| 算法 / 组合 | `experiments/portfolio.md` 三组对照 | 不在名单冻结前配权 |
| 算法总监 | 书面审核三份设计 | 设计未通过不批准落地 |
| 测试 | `tasks/test_spec.md` 与失败即红的样例 | 不改断言去迎合实现 |
| 系统架构 | 接线清单；`v2_readers` 缺文件失败 | 不在读取器里算收益 |
| 软件工程 / 数据 | `tasks/data_request.md` | 不生成替代行情 |
