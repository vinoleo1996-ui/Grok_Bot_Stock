# STRATEGY 提案：B4 `ABORT_SELFCHECK` / `rhythm_ok=false`（D=20261026）

- 日期：2026-10-26（America/New_York）
- 作者：QuantLab Strategy（executor）
- live=false；promotion=false；**未改代码**；**未写 parquet**；未碰 moneyflow；未 `--force`
- 状态：**WAITING_ARCH**（节奏/booked 口径变更须 Arch 审）

## 1. 现象（盘上已核）

`python3 research/b4_paper_extend.py --run-legs` → exit **2** `ABORT_SELFCHECK`。

| 产物 | 状态 |
|---|---|
| `output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261026_r2.check.json` | `status=ABORT_SELFCHECK`；**parquet 未写**；sha256 `94456b6201bc05bfed41908ed4df66d38c417ff5189bae534ccdce76bf38f555` |
| `output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261026_r2.check.json` | 同上；sha256 `684ecab52adc426f6c0199ac8aa5ba2c52febcdcd046bea9e7be42898640fb25` |

关键字段（60w/100w 同构）：

- `hist_ok=true`；腿 end 均 `2026-10-26`（cap/ee/ii）；`leg_hist_check.*.ok=true`
- `new_change_days=["2026-10-14"]`
- `leg_change_days_forward=["2026-10-13","2026-10-15"]`
- `rhythm_ok=false`（`set(fchg) <= LEG_CHG` 失败：`{10-14} ⊈ {10-13,10-15}`）
- `booked_days.booked_file=…/B_B4_*_20261014_r2.parquet`；`booked_last=2026-10-14`；`deferred_rebalance_day=2026-10-15`
- `booked_days.diff` 全在 **2026-10-13**（booked≠recomputed；booked-day 规则保留）
- `FROZEN_END=2026-10-09`；`REV=r2`；`STATUS=PAPER_TRACK_2_BACKFILL_READY_FORWARD_PENDING`
- FWD 仍 WAITING（自 11-02）；脚本内**无** Arch `run.ok` 硬门（本拍未缺 `.ok`）

## 2. 根因（为何是 10-14 vs 10-13/15）

### 2.1 腿日历（当前盘）

| 腿 | forward change days（> FROZEN_END） |
|---|---|
| capacity_adv（paper `…_20261026_r2`） | **无** |
| earnings_event | **仅 2026-10-13** |
| insider_increase | **仅 2026-10-13** |

→ 原始混合重算（无 splice）的 `new_change_days` = `["2026-10-13"]`，本可过节奏门。

### 2.2 booked 链与 deferred 的「二次续写」陷阱

1. **2026-10-13** 腿换仓；当日 B4 已被 booked（`…_20261013_r2`），按规则 **不改写**。
2. 续到 **2026-10-14** 时：`deferred_rebalance_day=2026-10-14` 写入 `LEG_CHG`，混合在 **10-14** 落地换仓；`…_20261014_r2` 通过（`rhythm_ok=true`，当时 `leg_change_days_forward=["2026-10-13","2026-10-14"]`）。
3. 钉点 `FROZEN_CONFIG.weights` 现指向 **`…_20261014_r2`**（60w sha `efcef7c4…` / 100w sha `4736c030…`）。
4. 今日 D=20261026 续写（10-15/16 停摆后的并日 catch-up，**非根因**，只是首次二次续写暴露点）：
   - `splice_booked` 保留 `FROZEN_END < s ≤ 2026-10-14` 的 booked 行 → 拼后组合的真实换日仍是 **10-14**（来自已入账的上次 deferred）。
   - 因 booked 窗内仍有 10-13 diff，脚本把 **当前** `deferred_rebalance_day` 标为 booked_last 的下一交易日 **10-15**，并 `LEG_CHG.add("2026-10-15")`。
   - **不会**把已锁在 booked 窗内的历史 deferred 日（10-14）加回 `LEG_CHG`。
   - 于是：`fchg={10-14}`，`LEG_CHG={10-13,10-15}` → `rhythm_ok=false`。

### 2.3 卡死性质

只要钉点 ≥ `20261014_r2`，任何后续 extend 都会把 **10-14** 拼进 `W`，而腿日历永远不会再产出 10-14，当前 deferred 又总是「booked_last+1 交易日」。**在现行 `rhythm_ok` 语义下会永久 ABORT**——不是数据坏、不是腿 hist 漂，是 **booked-day × rhythm 子集检验** 在「deferred 已入账之后的第二次续写」上未闭合。

模拟（只读，未落盘）：

- `change_days` 在 `booked_last` **之后**为空（10-15…10-26 权重相对 10-14 booked 无新换仓）——组合实质已对齐腿后仓位，仅自检口径拒写。

## 3. 冻结规则内可否修好？（结论：否）

| 尝试 | 结论 |
|---|---|
| 改腿权重 / 重跑腿让腿在 10-14 换仓 | 否：腿真实换日是 10-13；伪造换日违规 |
| 回指 `FROZEN_CONFIG` → `…_20261013_r2` 以重算 10-14 | 否：等于解开已 booked 的 10-14，违反「booked days never rewritten」 |
| 改写 / 删除 `…_20261014_r2` | 否：同上 |
| `--force` / 跳过 selfcheck | 禁 |
| 改 `research/b4_paper_extend.py` 蒙混跳检 | 禁（本提案正是为此） |

→ **FIXED_IN_RULES 不可行**；须 Arch 裁定节奏/booked 口径后改冻结脚本（或等价批准的补丁）。

## 4. 选项（请 Arch 择一）

### 选项 A（推荐）：`LEG_CHG` 并入 booked 窗内已实现的 change days

在 `splice_booked` 之后：

```text
LEG_CHG |= set(change_days(booked_parquet))   # 或仅 booked 窗 FROZEN_END < s ≤ booked_last
```

- 语义：已入账换日视为「已由历史 deferred/腿解释」，可继续满足 `fchg ⊆ LEG_CHG`。
- 本拍模拟：`rhythm` → **True**（60w/100w）。
- 风险：低；不放宽 post-booked 新换日的约束。

### 选项 B：`rhythm_ok` 只约束 **post-booked** 换日

```text
fchg_out = [d for d in fchg if d > booked_last]
rhythm_ok = hist_change_days_identical and set(fchg_out) <= LEG_CHG
```

- 语义：booked 窗内换日不再参与子集检验（因不可改写）。
- 本拍模拟：`fchg_out=[]` → **True**。
- 风险：中低；须在 check.json 保留 `new_change_days` 全量以便审计。

### 选项 C：deferred 记账改为「累积未落地腿换日」而非「booked_last+1」

更重的口径重写；本拍不必要（A/B 已够用）。不推荐作为本拍最小修复。

### 明确不推荐

- 把 `rhythm_ok` 直接短路为 true / 删除检验。
- 回拨钉点重写 10-14 booked 行。

## 5. 建议 Arch 决策

1. **批准选项 A**（或 B）作为 `research/b4_paper_extend.py` 的 r2 节奏补丁（须记 `frozen_script_sha256` 变更）。
2. 补丁落地后由 Strategy/Eng 重跑一次（**无 `--force`**）：写出  
   `B_B4_50_25_25_topN_{60,100}w_20261026_r2.parquet` + check `ok=true`。
3. 同步审 S6 shadow（同构：`new_chg=[10-14]` / `leg_fwd=[10-13,10-15]` / `ABORT_SELFCHECK`）——同一补丁语义应一并适用或出平行提案。
4. 通过后主 Agent 再令 Eng 重跑 X2H bridge / paper-daily 相关段；FWD 仍自 11-02。

## 6. 脚本锚点（现行）

- 文件：`research/b4_paper_extend.py`（盘上 sha256 `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c`）
- `rhythm_ok`：`set(fchg) <= LEG_CHG`（约 L238–241）
- `LEG_CHG.add(deferred_rebalance_day)`：仅当前 splice（约 L271）
- `splice_booked` / booked-day 规则（约 L134–150）
- 钉点：`output/strategy_paper_b4/FROZEN_CONFIG.json` → `…_20261014_r2.parquet`

## 7. Strategy 本拍动作边界

- 已做：只读诊断 + 本提案。
- **未做**：改脚本、写 parquet、改 `FROZEN_CONFIG`、更新 TEAM/ql_bus、触达 Leo、开 moneyflow。
- 待命：Arch 批 A 或 B 后的最小补丁与一次授权重跑。
