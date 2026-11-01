# 主裁：叶25 mem_probe r2 FAIL → VOID + r3

- 时刻：2026-10-25 12:30 ET（America/New_York）
- live=false · **≠ X2** · **禁同票重跑**

## 事实（已核）

| 项 | 值 |
|---|---|
| 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_RUN_RECEIPT_20261025_ZH.md` sha8 `d01f95c0` |
| 结果 | **FAIL** rc=1；peak≈208MB；C4=PASS；非 RSS |
| 根因 | PIT `end_date` 为 `timestamp[us]`，脚本用字符串 `YYYYMMDD` 滤 → ArrowNotImplementedError |
| `.ok` | `cd230f9c…` single_use **已用完（FAIL）** |

## 令 Arch

1. **VOID/消费** `ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.ok`（禁再消费同票）。
2. 共审 FAIL 回执后 **lift QUIET**（AI 未自 lift）。
3. 等 AI r3 包另审另签；**勿**签复用 r2 `.ok`。

## 令 AI（r3）

1. 修 `_read_pit_projected`：`end_date`（及同类日期列）按 **timestamp** 比较（`pd.Timestamp` / arrow timestamp），禁字符串滤。
2. 落 `leaf25_full_factor_mem_probe_r3.py` + COVER + CMD + DIFF；静态烟测；**禁** `--allow-real-data` 实跑至新 `.ok`。
3. 交 Arch 另审；**ai_no_retry** 本票停。

## 叶27（并行排期）

- Arch 审 `282d6ca1…` PASS_WITH_CONDITIONS 收讫。
- QUIET lift 后另窗：**拟 14:00–14:45 ET** 再令 Arch 签独立叶27 `.ok`（硬钉脚本 `262f9bf6…`；rss=1500 禁抬；禁 RESTORED/同cmd lowmem_v1）。
- 若 r3 实跑窗冲突则叶27 顺延；文档/签票可先，开跑互斥 QUIET。
