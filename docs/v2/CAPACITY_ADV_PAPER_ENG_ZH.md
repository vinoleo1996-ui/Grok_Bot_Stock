# Eng 接线：capacity_adv 纸面轨（不下单）

**日期**：2026-10-13（America/New_York）  
**范围**：Eng 平台入口，供 Strategy / New Bot 接 paper；**不**翻转 live / `strategy_promotion_approved`；**不**启 uvicorn；**不**跑重型 E1 对账；**不** Full D1 OOM 扫池。  
**机制**：`g1g5_ashare_capacity_adv_v1`  
**短包**：`docs/v2/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_ZH.md`  
**已过门 Book-Smoke**：`docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md` · `output/v3/book_smoke_g1g5_capacity_adv_x2/`

| 旗标 | 值 |
|---|---|
| promotion_path | paper（研究级纸面；不下单） |
| live_handoff / strategy_live_orders | **NO / false** |
| promotion_approved（live） | **false**（Eng 本任务未动） |
| strategy_promotion_approved | **false**（Eng 本任务未动） |

---

## 1. 权威权重包

```
output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet
```

- 原始行约 **32732**（含权=0 行）；Eng `validate_weight_path` 只计 **正权** → **15739** 行 / **668** sessions / `2024-01-02`→`2026-10-09`。
- 表内已含 **510300 压舱**（日均≈0.21）→ 消费时 **必须** `sleeves={"core":0,"stock":1,"alpha_event":0}`，**禁止**再叠 `core=1` overlay（否则双计压舱）。
- 覆盖检查：`assert_session_coverage_path(..., target_end="2026-10-09")` → ok（禁止仅前推解读）。

---

## 2. Eng 已确认可用（绿）

| 入口 | 模块 / CLI | 状态 |
|---|---|---|
| strategy_feed | `quantlab.platform.strategy_feed` · `describe_strategy_feed()` | **绿**：merged close/returns、chunk/`float32`、disk cache、D1 `d1_members_at` / `_chunked`、biweekly sessions、510300 returns、日历至 2026-10-09 |
| weight_long_table | `quantlab.platform.weight_long_table` | **绿**：契约 `weight_long_v1_20261012`；本包 validate + coverage ok |
| book-smoke 接线 | `python -m quantlab.cli book-smoke ...`（默认 `--skip-run`） | **绿**：正确 sleeves 时 gaps=[]；`strategy_promotion_approved` 仍 false |
| book-smoke NAV（已有结果） | 同上 + `--run-nav` | **绿（既有）**：X2 @60万∧100万 any_pass / both_aum_pass；见上回执（Eng 本任务**未**重跑 NAV） |
| live-dry-run | `python -m quantlab.cli live-dry-run` / `--gates-only` | **绿接线**：G1–G5→权重→烟；多数门为表面/stub；**不下单** |
| execution | `run_weight_schedule` + `ExecConfig.strategy_v1`（book 默认） | **绿**：冲击 / 10% 参与率帽 / 公司行动等已在引擎 |
| capacity_curve | `quantlab.platform.execution.capacity_curve` | **绿 API**；默认 capitals=(5e5,2e6,1e7) 作**附录档**；主敏感度请显式传 60万/100万（见 §4） |

## 3. Stub / 勿误用

| 项 | 说明 |
|---|---|
| `live-dry-run` 内 trading_loop / factor_evolve | stub 或烟雾数据；**不要**当成 capacity_adv 真权重 |
| book-smoke **默认** sleeves | `core=1,stock=0` → 即使传了 `--stock-path` 也不会吃进个股叶；capacity_adv **必须**改 sleeves |
| Full D1 全池预载 | 用 `iter_merged_close_chunks` / `chunk_size` / `float32`；禁止无界 wide panel |
| E1 / reconcile_zero_cost 全窗 | 本 paper 路径**不要求**；需要时另开轻量任务 |
| uvicorn / 实盘下单 | **禁止** |
| 翻转 live / strategy promotion | **禁止**（本 Eng 任务不动） |

---

## 4. 资金档（Leo AUM）

- **主敏感度（Mandate）**：**60万 ∧ 100万** CNY（`book-smoke --capitals 600000,1000000` 默认即此）。
- **更大 AUM**：仅附录 / 诊断；`capacity_curve(..., capitals=(5e5, 2e6, 1e7))` 的默认档偏附录，**不要**当成主门。
- 主对比请显式：

```python
from quantlab.platform.execution import capacity_curve
capacity_curve(panels, schedule, capitals=(600_000, 1_000_000))
# 附录示例：
# capacity_curve(panels, schedule, capitals=(600_000, 1_000_000, 2_000_000, 10_000_000))
```

参与率：引擎默认 `participation_cap=0.10`；本叶权重生成侧另有 ADV 参与率 k=2%@AUM=100万（见短包 / run_meta）。

---

## 5. Strategy 最小命令清单

工作目录：`/workspace/QuantLab`。`PY='/workspace/qlvenv/bin/python'`，`export PYTHONPATH=.`。

### 5.1 权重契约（轻）

```bash
$PY - <<'PY'
from quantlab.platform.weight_long_table import validate_weight_path, assert_session_coverage_path
p = "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
print(validate_weight_path(p, require_rows=True))
print(assert_session_coverage_path(p, target_end="2026-10-09"))
PY
```

### 5.2 一键接线（推荐；默认不下 NAV）

```bash
$PY -m quantlab.cli capacity-adv-paper
```

等价展开：

```bash
$PY -m quantlab.cli book-smoke \
  --stock-path output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet \
  --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' \
  --capitals 600000,1000000 \
  --windows X2 \
  --out output/v3/book_smoke_g1g5_capacity_adv_paper \
  --receipt docs/v2/BOOK_SMOKE_CAPACITY_ADV_PAPER_WIRE_ZH.md
```

### 5.3 复跑纸面 NAV（可选；较重，非 Full D1）

```bash
$PY -m quantlab.cli capacity-adv-paper --run-nav
# 或：
$PY -m quantlab.cli book-smoke --run-nav \
  --stock-path output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet \
  --sleeves '{"core":0.0,"stock":1.0,"alpha_event":0.0}' \
  --capitals 600000,1000000 \
  --windows X2 \
  --out output/v3/book_smoke_g1g5_capacity_adv_paper
```

既有满窗结果可直接复用：`output/v3/book_smoke_g1g5_capacity_adv_x2/`（无需为接线再跑）。

### 5.4 live-dry-run（研究闭环表面；非本叶专用）

```bash
$PY -m quantlab.cli live-dry-run --gates-only   # 轻
$PY -m quantlab.cli live-dry-run                # G1–G5 + 骨架烟；不下单
```

### 5.5 strategy_feed（自建 paper / 再平衡日历时）

```python
from quantlab.platform.strategy_feed import (
    describe_strategy_feed, trading_sessions, biweekly_rebalance_sessions,
    merged_close_panel, iter_merged_close_chunks, merged_daily_returns,
    d1_members_at, etf_510300_daily_returns,
)
describe_strategy_feed()  # 路径 / 内存旋钮
# Full 窗：优先 iter_merged_close_chunks(..., chunk_size=300, dtype="float32")
```

---

## 6. 引用

- ACCEPT：`docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_ACCEPT_ZH.md`
- who_pays：`docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md`
- 执行成本：`docs/v2/EXECUTION_COSTS_PLATFORM.md`（`capacity_curve`）
- 骨架 / 长表：`docs/v2/SKELETON_ONECLICK_ZH.md`
- live dry-run：`docs/v2/LIVE_DRYRUN_COMMANDS_ZH.md`
