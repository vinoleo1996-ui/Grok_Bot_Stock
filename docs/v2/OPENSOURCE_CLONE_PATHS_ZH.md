# 开源浅克隆路径指针（不 vendor）

供 AI / Alpha 深读。**源码不在 QuantLab 树内**；Eng 只维护本指针与适配模块。

| 名称 | 共享绝对路径 | 上游 | 克隆时 SHA |
|------|--------------|------|------------|
| TradingAgents | `/workspace/opensource/TradingAgents` | https://github.com/TauricResearch/TradingAgents | `1394a3f72aa4393e1a98f51b382434c4b4c2d972` |
| QuantMind | `/workspace/opensource/QuantMind` | https://github.com/qusong0627/QuantMind | `7d8019cac06e5f44de5f19b501481886535a6c32` |

索引说明（许可证、约定、Eng 适配路径）：`/workspace/opensource/README_ZH.md`

Eng 适配（仍在主仓，非上游拷贝）：

- `quantlab/intel/asof_window.py` — as_of 文本窗口守卫
- `quantlab/intel/debate_ledger.py` — TradingAgents 风格辩论账本契约（对照重写）
- `docs/v2/OPENSOURCE_ENG_ADOPTION_ZH.md`

**禁止**把 `/workspace/opensource/*` 拷进 `quantlab/` 或当 submodule 并入主仓。角色适配文档由 AI 维护（`TRADINGAGENTS_ADAPT_*`）。
