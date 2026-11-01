# Arch 审结：B4 `ABORT_SELFCHECK` / `rhythm_ok` 提案 — 批准选项 A

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器：只核验 + 写审结 + TEAM_STATE；**不改脚本 / 不代跑 / 不写 parquet**） |
| 时刻 | `2026-10-26T19:19:20-04:00`（America/New_York；墙钟 `2026-10-26 19:19 ET`） |
| **VERDICT** | **APPROVE_OPTION_A** |
| 提案 | `docs/v2/STRATEGY_B4_RHYTHM_ABORT_PROPOSAL_20261026_ZH.md` sha8 **`5dfbe8d2`** |
| 提案全长 | `5dfbe8d2abcca65ad2fe2cc3c569ffea8eef2c352c4bfcf098c635f309bd490c` **MATCH** |
| 脚本现钉 | `research/b4_paper_extend.py` sha8 **`6c927ae6`** / 全长 `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c` **MATCH**（= 提案钉；本拍**未改**） |
| 本回合动作 | **批口径 A**；写本审结；prepend TEAM_STATE；**不**改 `b4_paper_extend.py`；**不**改 FROZEN_CONFIG；**不**写/删 parquet；**不**跑 extend；**不** `--force`；**不**触 A18/叶30/`.ok`；**不**报 Leo；live=false |
| ≠ | **≠X2 ACCEPT**；FWD 仍 WAITING@11-02 |

## 0. 一句话

二次续写时 booked 窗保留 deferred 入账日 **10-14**，但 `LEG_CHG` 只加**当前** deferred=**10-15** → 永久 `fchg ⊈ LEG_CHG`。**批准选项 A**：`splice_booked` 之后 `LEG_CHG |= set(change_days(booked_parquet))`（或仅 booked 窗 `FROZEN_END < s ≤ booked_last`）。闭合缺口、不放宽 post-booked 新换日约束。本拍 Arch **只批口径**；落地补丁由 Strategy 写、Arch 另审 DIFF、主令重跑。

## 1. 核验（只读 · 本机）

| # | 项 | 结果 | 证据 |
|---|---|---|---|
| V1 | 提案 sha256 | **MATCH** | `sha256sum` → `5dfbe8d2abcca65ad2fe2cc3c569ffea8eef2c352c4bfcf098c635f309bd490c`（sha8 `5dfbe8d2`） |
| V2 | 脚本现 sha256 | **MATCH 提案钉** | `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c`（sha8 `6c927ae6`）；本拍未改 |
| V3 | `splice_booked` | **在** | `research/b4_paper_extend.py` **L134–150**（booked-day never rewrite；deferred=booked_last 下一交易日） |
| V4 | `rhythm_ok` | **在** | **L238–241**：`fchg` 自 `change_days(W[W.session >= FROZEN_END])`；`rhythm_ok = hist_change_days_identical and set(fchg) <= LEG_CHG` |
| V5 | `LEG_CHG.add(deferred)` | **在** | **L271**：仅 `if booked["deferred_rebalance_day"]: LEG_CHG.add(...)` — **不**并入 booked 窗历史 change days（根因位） |
| V6 | 60w check | **MATCH 提案** | `…/B_B4_50_25_25_topN_60w_20261026_r2.check.json` sha256 `94456b6201bc05bfed41908ed4df66d38c417ff5189bae534ccdce76bf38f555`；`status=ABORT_SELFCHECK`；`check.rhythm_ok=false`；`new_change_days=["2026-10-14"]`；`leg_change_days_forward=["2026-10-13","2026-10-15"]`；`booked_days.booked_file`∋`20261014_r2`；`booked_last=2026-10-14`；`deferred_rebalance_day=2026-10-15`；`hist_ok=true` |
| V7 | 100w check | **同构 MATCH** | `…_100w_20261026_r2.check.json` sha256 `684ecab52adc426f6c0199ac8aa5ba2c52febcdcd046bea9e7be42898640fb25`；字段同 60w |
| V8 | 目标 parquet | **ABSENT** | `B_B4_50_25_25_topN_{60,100}w_20261026_r2.parquet` **未写**（仅 check.json） |

## 2. 根因复述（裁定采信）

1. FROZEN 钉 `…_20261014_r2`：上次续写时 deferred=**10-14** 已入账 booked，混合真实换日锁在 **10-14**。
2. D=20261026 二次续写：`splice_booked` 保留 `FROZEN_END < s ≤ 2026-10-14` → 拼后 `fchg={10-14}`。
3. 脚本只 `LEG_CHG.add(当前 deferred=10-15)`，**不**把 booked 窗内已实现换日（10-14）加回 → `LEG_CHG` forward ≈ `{10-13,10-15}`。
4. `set(fchg) <= LEG_CHG` 永久失败 → `ABORT_SELFCHECK`；非数据坏、非腿 hist 漂、非缺 `.ok`。
5. 冻结规则内无法修好（回指/删 `20261014_r2` / 伪造腿换日 / `--force` / 短路 rhythm **皆禁**）。

## 3. VERDICT：APPROVE_OPTION_A

### 3.1 补丁语义（精确；Strategy 落地时须字面满足）

在 **`splice_booked` 成功返回之后**（约现 L270–271 一带），于现有

```text
if booked["deferred_rebalance_day"]: LEG_CHG.add(booked["deferred_rebalance_day"])
```

之外（或紧随其后）增加等价语义：

```text
LEG_CHG |= set(change_days(booked_parquet))
# 或收窄：仅 booked 窗 FROZEN_END < s ≤ booked_last 上的 change_days
```

- **保留**不变量：`rhythm_ok` 仍要求 `set(fchg) ⊆ LEG_CHG`（及 `hist_change_days_identical`）；**禁止**短路 `rhythm_ok=true`。
- **不放宽** post-booked（`s > booked_last`）新换日约束：新出现的 fchg 日仍须被腿日历或**当前** deferred 解释。
- **禁止**改写 booked 行 / 回滚钉点 / 删 `…_20261014_r2`。
- 改后更新产物内 `frozen_script_sha256`；旧脚本 sha **`6c927ae6…`** 记入 forbid/对照表，**不得**再当合法冻结脚本钉。

### 3.2 理由

1. 根因是 deferred 入账后的二次续写缺口；A 把已入账换日并入 `LEG_CHG`，闭合「booked 窗有换日但 LEG_CHG 不知」的洞。
2. A **不**削弱对 post-booked 新换日的子集检验；审计仍可见全量 `new_change_days`。
3. 选项 B 把 booked 窗整段移出检验，审计面弱于 A → **本拍不批**。
4. 选项 C（累积未落地腿换日重写）过重 → **本拍不批**。

### 3.3 明确拒绝（本拍）

| 选项/动作 | 裁定 |
|---|---|
| 选项 B（rhythm 只检 post-booked fchg） | **REJECT（本拍）** |
| 选项 C（deferred 记账大改） | **REJECT（本拍）** |
| 短路 `rhythm_ok` / 删除检验 | **FORBIDDEN** |
| 回滚/回指/删除 `…_20261014_r2` 或改 FROZEN 钉重写 booked | **FORBIDDEN** |
| `--force` / 跳过 selfcheck | **FORBIDDEN** |

## 4. CONDITIONS（落地前硬闸）

| ID | 条件 |
|---|---|
| **C1** | 补丁**最小**：只改 `LEG_CHG` 并入 booked change days（§3.1）；**禁**改 booked-day never rewrite；**禁**动 hist / 权重合成 / 腿日历语义 |
| **C2** | 改后更新 `frozen_script_sha256`；旧 sha 全长 `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c`（sha8 `6c927ae6`）记入 forbid/对照；新 sha 入审 DIFF |
| **C3** | 本拍 Arch **只批口径、不批改代码本体**。Strategy 出最小 DIFF → **Arch 复审 DIFF PASS** 后，主才令重跑（无 `--force`） |
| **C4** | S6 shadow **同构**须同一语义：Strategy 出平行补丁（`s6_paper_extend` 族）或同脚本族一并对齐；不得 B4 单修留下 S6 永久 ABORT |
| **C5** | **禁** `--force`；**禁**短路 rhythm；**禁**回指/删 `20261014_r2`；**禁**改 FROZEN_CONFIG 仅为绕检 |

## 5. 落地路径（请主编排；Arch 本拍停于审结）

```text
主 MATCH 本审结
  → 令 Strategy：按 §3.1 最小补丁改 b4_paper_extend.py（及 S6 同语义 / 平行提案）
      → Arch 只审 DIFF（PASS 后）
          → 主令重跑 B4（及 S6）：无 --force
              → 目标写出：
                 output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261026_r2.parquet
                 output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261026_r2.parquet
                 + check ok=true / rhythm_ok=true
                  → 再排 Eng X2H bridge / paper 相关段
```

- FWD 仍 **WAITING@2026-11-02**（本拍不推进 forward）。
- **≠X2 ACCEPT**；promotion=false；live=false。

## 6. 禁区 / 本回合非动作（已守）

- **未改** `research/b4_paper_extend.py` / 任何 S6 脚本 / `FROZEN_CONFIG`
- **未写 / 未删**任何 `*_20261026_r2.parquet`；**未**跑 extend；**未** `--force`
- **未触** A18 / 叶30 / 任何 `.ok` / QUIET
- **未** SendToUser；**不报 Leo**
- live=false

## 7. 结论

**VERDICT=APPROVE_OPTION_A** — 提案 `5dfbe8d2` / 脚本 `6c927ae6` / check 60w·100w 关键字段全 MATCH；根因成立；批 A 补丁语义；拒 B/C/短路/回滚/`--force`。请主 MATCH → 令 Strategy 最小补丁 → Arch 审 DIFF → 再令重跑。S6 同语义一并。

live=false.

## 8. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` |
| VERDICT | **APPROVE_OPTION_A** |
| 提案 sha8 | **`5dfbe8d2`** |
| 脚本现 sha8 | **`6c927ae6`**（forbid/对照旧钉） |
| 正文 sha256（§0–§7，不含本节） | `2a1b74eed3f520efbcecbe0d681c9a6c81fd15b8d48978027aba651e774c4f16` |
| 正文 sha8 | **`2a1b74ee`** |

全文件（含本节）sha256：见落盘后 `sha256sum`（TEAM_STATE / 父回报）。

live=false.
