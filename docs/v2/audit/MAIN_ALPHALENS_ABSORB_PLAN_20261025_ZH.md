# AlphaLens / WorkBuddy 吸收计划（主裁 · Leo 2026-10-25 11:42 ET 批准）

- **来源**：Leo Mac `/Users/agiuser/WorkBuddy/2026-10-23-17-45-52`（`cnus-info-expert-v2` AlphaLens）
- **箱内 refs**：`docs/v2/refs/alphalens_workbuddy/`（provenance / paper / evidence_* / crowding / hub / exits / quant_audit / README / v1_architecture / news_evidence_policy）
- **禁抄**：8 维技术打分当主 alpha；LLM 多空辩论下单；当日股票池回测（幸存者偏差）
- **live**=false · **promotion_approved**=false

## 吸收项与责任

| # | 项 | 落点 | 专责 | 交付物（本回合） |
|---|---|---|---|---|
| A1 | 回测≡实盘同源 | ARCH 检查单 + Book-Smoke/Gate 预检 | Arch | `docs/v2/ARCH_CHECKLIST_BACKTEST_EQ_LIVE_ZH.md`：凡宣称数字须证明 scoring/universe/gate/cost 与纸面轨同一模块路径；禁止平行简化因子 |
| A2 | 策略 provenance 防漂移 | 运行时 sha 清单 | Arch(+Eng 接线) | 设计：对叶脚本+wrapper+关键 reader 算 manifest sha；进程内变码拒跑；VERSION 复用不同码报错。对照 `refs/.../provenance.py`。先出设计+最小自检脚本草案，**不**改生产轨 |
| A3 | 纸面 append-only + T+1 开盘结算 | Eng paper 轨对照 | Eng | 对照现有 capacity_adv/B4 paper：是否可改日、是否次日开盘、是否满 N 日才计、基准对照。缺口 DIFF 草案（只文档/对照表，不擅改 live） |
| A4 | 证据政策 | Intel 事件特征 | Intel | 吸收 `evidence_policy`：来源分权、转载去重、充分度、**资料缺口≠反证** → `docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md` + 映射到 PIT 事件特征字段 |
| A5 | hub stale / age_s / 空不写长缓存 | Web 看板 + Data 健康 | Web + Data | Web：看板展示数据集 age_s/stale/ready；Data：双测/健康回执带 last-good vs empty 污染禁令。对照 `hub.py` |
| A6 | 拥挤闸门 + 状态平滑 | Beta 袖套参考 | Beta | 只读对照 crowding/exits；提案是否进 β 预算/降仓（**非**选股主 alpha）；出 1 页对照，不擅自改 Mandate |
| A7 | 审计反面教材 | 全队 | Arch | 把 `quant_audit_20261024.md` 的 P0（回测≠实盘、池污染）钉进检查单「禁止复发」节 |

## 不做

- 不移植 AlphaLens 全站 / NeoData / 8722 服务
- 不把其 OOS 负超额策略当候选叶
- 不抬 QuantLab live；不消费无关 `.ok`

## 排期

1. 本小时：refs 齐 + 本计划落盘 + 各专责开工
2. 今日内：A1/A4/A7 文档；A3/A5 对照表；A2 设计草案
3. 叶27 12:30–13:30 ET 窗与叶25 r6 **优先于**吸收实现代码；吸收以文档/检查单为主，代码变更另签

## 主裁状态

- 【OPEN】吸收进行中
- 叶27 LOWMEM 另窗 12:30–13:30 ET 并行（Arch 另签.ok）


## 修订（Leo 2026-10-25 ~11:44 ET）

**纠正**：原「禁抄」中的两点改为 **开放因子研究**：
1. 技术/拥挤/状态复合分 → 残差候选叶（须 WF + Gate；禁页面 TOP 当超额）。
2. LLM 多空辩论 → PIT 事件/情绪特征（禁 LLM 直接下单权重）。
仍禁：未经门控把 AlphaLens 纸面当主策略；live=false。
