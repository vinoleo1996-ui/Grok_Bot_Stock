# QuantLab 系统架构总图（研究级）

更新日期：2026-10-11。权威细节见 `SYSTEM_ARCH_V3_ZH.md`、`SYSTEM_ARCH_V3_AI_NATIVE_ZH.md`。

## 端到端总览

```mermaid
flowchart TB
  Leo["Leo / New Bot<br/>拍板·密封窗·总闸门"]

  subgraph Data["Data 数据层"]
    MKT["行情/市值/财务 PIT"]
    EVT["公告/龙虎榜/两融/可转债事件"]
    TXT["文本语料 → Embedding"]
    ALT["雪球情绪试点 · 东财替代"]
    PING["ENG_PING_PATHS<br/>验收与路径表"]
  end

  subgraph Eng["Eng 平台层"]
    RD["Readers / Masks / Feed"]
    EX["执行引擎<br/>成本·复权·期货·保证金"]
    E1["双引擎对账 E1"]
    INTEL["intel 契约<br/>消息/嵌入读取"]
  end

  subgraph Alpha["Alpha 研究层"]
    WB["WorkBuddy 四角色<br/>分析师·采集·风控·复盘"]
    AF["AI 因子工厂 L1<br/>结构/文本叶子 · 禁教科书主结果"]
    VAL["多重检验 · 成本/容量闸门"]
    HO["Top-K → 残差分数交接"]
  end

  subgraph Beta["Beta 组合层"]
    CIB["结构性袖套<br/>CIB2-EW 等"]
    BUD["风险预算 · L≤1.5"]
    NEXT["下一臂队列<br/>CB3/TCarry/S1"]
  end

  subgraph Strat["Strategy 策略层"]
    BOOK["多袖套账本"]
    RB["再平衡 / 权重日程"]
    PAPER["前向模拟盘 2026-11+"]
  end

  OUT["产出 NAV/parquet/台账<br/>promotion_approved=false"]

  Leo --> Alpha
  Leo --> Beta
  Leo --> Strat
  Leo --> PING

  MKT --> RD
  EVT --> RD
  TXT --> INTEL
  ALT --> INTEL
  PING --> RD

  RD --> WB
  INTEL --> AF
  RD --> AF
  WB --> AF
  AF --> VAL
  VAL --> HO

  HO --> BOOK
  CIB --> BUD
  BUD --> BOOK
  NEXT -.-> BUD
  RD --> BOOK
  EX --> BOOK
  BOOK --> RB
  RB --> E1
  RB --> PAPER
  E1 --> OUT
  PAPER --> OUT
```

## AI 挖因子特写

```mermaid
flowchart LR
  A["制度/结构/文本算子库<br/>非教科书主线"] --> B["假设 → 代码 → 回测<br/>RD-Agent 式闭环"]
  B --> C["探索窗筛选"]
  C --> D{"过闸门?"}
  D -->|否| E["账本计次 · 复盘写回"]
  D -->|是| F["预注册 · Leo 批准密封"]
  F --> G["密封窗单次"]
  G --> H["Strategy 组合"]
  E --> A
```

## 角色边界

| 角色 | 负责 | 不负责 |
|---|---|---|
| Data | 落盘、PIT、消息源 | 策略结论 |
| Eng | 读取器、掩码、引擎、对账、接口 | 因子是否有效 |
| Alpha | 挖因子、检验、WorkBuddy 流水线 | 改引擎默认 |
| Beta | 袖套、风险预算、结构性收益 | 改 D1 掩码 |
| Strategy | 组合账本、再平衡、模拟盘 | 伪造数据验收 |
| Leo | 密封/晋级拍板 | — |
