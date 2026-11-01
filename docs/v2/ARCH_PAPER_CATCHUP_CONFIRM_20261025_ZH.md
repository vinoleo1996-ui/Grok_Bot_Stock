# 纸面 catch-up 三点书面确认（Arch）

live=false；promotion=false。
- 对象：Eng 预案 `/workspace/sd1_work/paper_catchup_20261025/PAPER_CATCHUP_PLAN_ZH.md` sha256 `c4acc464b7c26325d4853fbd4b70cc06056b59659c8d679d40239ed7ec8b7db0`
- 主 Agent 裁定：2026-10-25 00:22 / **00:23** ET
- Arch 备案确认：2026-10-25T00:23:38-04:00
- 性质：装载 + 计划集 + 门禁形状已闭合；开跑集仍空；今晚不签补跑/纸面运行 .ok

## 1. 装哪一版 — **已确认**

**默认装 r4.5-strict**（`NEW_PROMPT_R4_5_STRICT.txt` sha256 `ca0f873555d1016baa7f47160b3c0e4efe646cae3379df33449a9a6e0ebaef7f`）。

仅当同时满足时才改装 r4.5（`222c10c966bfc5ed5dc01dbe81ce3a6f3f003e546dd7a404854433254f6b1d5c`）：
1. catch-up 日更链 .ok 明确签署 v3.1（或后继）marker 契约；且
2. Arch 在该 .ok **书面点名** `load_routine=r4.5`。

点名之前两版都不装。今晚不装、不跑纸面。

## 2. 新门禁时刻 — **主 00:23 形状已确认**

写入未来「纸面 catch-up 门禁 .ok」的固定形状：

| 键 | 值 |
|---|---|
| 禁止 | 复用 10-19 17:40；用常态 cron `40 17 * * 1-5` 当补跑窗 |
| 单次窗 | 签发当日 **11:00–15:00 America/New_York** |
| not_before | 签发日 `T11:00:00-04:00`（或当时夏令偏移） |
| expires | 签发日 `T15:00:00-04:00` |
| 未开跑 | .ok 作废；次日同钟点由 Arch **重签** |
| 签发前提 | Data 已报 DONE 日集合 + 新 freshness 文件，且主 Agent 已确认 `<D>_open` **非空** |

今晚**不签**补跑 .ok、不签纸面门禁/运行 .ok。中转探活通 + Data 新申请后，Arch 再签补跑 .ok；纸面门禁 .ok 另签并套用上表。

## 3. `<D>` — **计划集已裁；开跑集仍空**

| 集合 | 值 | 状态 |
|---|---|---|
| `<D>_plan` | **20261019, 20261020, 20261021, 20261022, 20261023** | 主已裁，不变 |
| `<D>_open` | **空** | 等 Data 报 `DONE ∩ plan` + freshness 覆盖 → 主发确认句 → Arch 写入纸面 catch-up .ok |

并入（非单独目录）：
- **20261015、20261016** 只进首个成功 catch-up 日的 `NOTE_STALL_MERGE.md`。

开跑前置（缺一不可）：`<D>_open` 非空且写入 .ok；Eng 已装 r4.5-strict（或点名的 r4.5）并回报 sha；两组 pgrep 空；execution `373fed30…`、trade_cal `141078fa…` 未变。

**当前仍不得开跑。**

## 并行

- fund_portfolio 流式 v1.1 PASS：Eng `/tmp` 自测绿前 Arch **不签**实现审阅 .ok；今晚不签运行 .ok。

live=false；promotion=false。
