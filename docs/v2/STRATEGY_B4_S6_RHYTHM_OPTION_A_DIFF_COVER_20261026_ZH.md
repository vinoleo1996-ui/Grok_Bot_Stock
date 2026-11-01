# STRATEGY DIFF 封面：B4/S6 rhythm Option A（Arch APPROVE_A 落地补丁）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Strategy（executor） |
| 时刻 | 2026-10-26（America/New_York） |
| 动作 | **仅写最小补丁 + DIFF + 本封面**；**未重跑** extend；**未写** `*_20261026_r2.parquet`；**未** `--force`；**未**改 FROZEN / 删 booked；**未** invent `.ok`；**未**更新 TEAM_STATE / ql_bus |
| VERDICT 来源 | Arch `APPROVE_OPTION_A` |
| live | false |
| promotion | false |
| 状态 | **WAITING_ARCH_DIFF_PASS** → 再等主令重跑 |

## 0. 一句话

按 Arch 批 A：`splice_booked` 之后在既有 `LEG_CHG.add(deferred)` 外，再 `LEG_CHG |= set(change_days(booked_parquet))`（S6 同语义 `leg_chg`）。闭合 booked 窗已入账换日在二次续写时丢失的洞；**不**放宽 post-booked 新换日；**不**短路 `rhythm_ok`。

## 1. 钉点核验（改前）

| # | 项 | 结果 | sha256 / sha8 |
|---|---|---|---|
| V1 | 审结 `docs/v2/audit/ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` | **MATCH** | `559e30571b9459552dfc62b2d5f15aa5d8fe0f6eccc59ecf9405dcded5e86b44` / `559e3057` |
| V2 | 提案 `docs/v2/STRATEGY_B4_RHYTHM_ABORT_PROPOSAL_20261026_ZH.md` | **MATCH** | `5dfbe8d2abcca65ad2fe2cc3c569ffea8eef2c352c4bfcf098c635f309bd490c` / `5dfbe8d2` |
| V3 | 改前 `research/b4_paper_extend.py` | **MATCH 基线** | `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c` / `6c927ae6` |
| V4 | 改前 `research/s6_paper_extend.py` | **记录基线**（任务未给硬钉；改前实测） | `3b258bbe9bd213fefc06f0dfa27d363fdb50e7672157831957d461f44eb92e7a` / `3b258bbe` |

## 2. 新旧脚本 sha（改后）

| 脚本 | 旧 sha256（对照 / forbid 基线） | 旧 sha8 | 新 sha256 | 新 sha8 |
|---|---|---|---|---|
| `research/b4_paper_extend.py` | `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c` | `6c927ae6` | `625ddcd68353605e6e14d0448117bff85ce41053b5f1c0369a6de33d54ab644c` | `625ddcd6` |
| `research/s6_paper_extend.py` | `3b258bbe9bd213fefc06f0dfa27d363fdb50e7672157831957d461f44eb92e7a` | `3b258bbe` | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` | `93b00354` |

**C2 说明**：产物侧 `frozen_script_sha256` 由运行时 `script_shas(TRACK_SCRIPTS)` 写入 check.json；脚本改后下次合法重跑会自动记新 sha。本拍**不** invent Arch `.ok`、**不**擅改 `FROZEN_CONFIG` / `paper_import_closure.json`（Eng 闸重钉另拍）。旧 `6c927ae6…` / `3b258bbe…` 作对照/forbid 基线，**不得**再当合法冻结脚本钉（重跑后）。

## 3. DIFF

| 项 | 值 |
|---|---|
| path | `docs/v2/audit/STRATEGY_B4_S6_RHYTHM_OPTION_A_20261026.diff` |
| sha256 | `8ea05f64e5d8039efc6c748e36f66ebd51cc72ab822a9f3336d034b1146a2cbe` |
| sha8 | `8ea05f64` |
| 生成 | `diff -u` baseline 副本 → 现盘；header 规范化为 `a/`/`b/research/…` |
| 范围 | **仅** `b4_paper_extend.py` + `s6_paper_extend.py` 各 +2 行（注释 1 + 语句 1） |

## 4. 逐行语义（补丁）

### 4.1 B4 — `research/b4_paper_extend.py`（约 L270–273）

保留：

```python
            W, booked = splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: LEG_CHG.add(booked["deferred_rebalance_day"])
```

新增：

```python
            # Option A (Arch APPROVE 20261026): booked-window realized change days stay in LEG_CHG across re-extends
            LEG_CHG |= set(change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
```

语义：

1. 仍先 `splice_booked`（booked-day never rewrite 不变）。
2. 仍把**当前** `deferred_rebalance_day` 加入 `LEG_CHG`（post-booked 解释路径不变）。
3. **再**把 booked parquet 上 `change_days` 全集并入 `LEG_CHG`，使已入账窗内换日（如 2026-10-14）在二次续写时仍满足 `set(fchg) ⊆ LEG_CHG`。
4. `rhythm_ok` 公式未改：仍 `hist_change_days_identical and set(fchg) <= LEG_CHG`（见既有 L241 一带）。
5. **未**放宽 post-booked 新换日：新 fchg 仍须被腿日历或当前 deferred 解释。

### 4.2 S6 — `research/s6_paper_extend.py`（约 L125–128）

保留：

```python
            W, booked = B.splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: leg_chg = leg_chg | {booked["deferred_rebalance_day"]}
```

新增：

```python
            # Option A (Arch APPROVE 20261026): same semantics as b4 — booked realized change days ∪ into leg_chg
            leg_chg |= set(B.change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
```

结构差异：S6 用局部 `leg_chg` + `B.change_days` / `B.splice_booked`；语义与 B4 **字面同构**（C4）。

## 5. CONDITIONS C1–C5 自检

| ID | 条件 | 本拍 |
|---|---|---|
| C1 | 最小改；禁动 booked-day never rewrite | **PASS**：各脚本 +2 行；`splice_booked` / FROZEN 钉 / booked 行逻辑未改 |
| C2 | 更新产物将记的 `frozen_script_sha256`；旧 sha 对照/forbid | **PASS（机制）**：运行时 `script_shas`；封面钉新旧全长；**未** invent `.ok` |
| C3 | DIFF 交 Arch 只审不代改；PASS 前禁重跑 | **PASS**：本封面 + DIFF；**NO RUN** |
| C4 | S6 shadow 同语义 | **PASS**：已平行补丁 |
| C5 | 禁 `--force` / 短路 rhythm / 回指或删 `*_20261014_r2` | **PASS**：未触 |

## 6. 明确未做

- **未**执行 `b4_paper_extend` / `s6_paper_extend`（任何参数）
- **未**写 `B_B4_*_20261026_r2.parquet` / S6 对应 parquet（盘上仍 ABSENT）
- **未** `--force`；**未**改 `rhythm_ok` 布尔短路
- **未**改/删 `…_20261014_r2`；**未**改 `FROZEN_CONFIG`
- **未**碰 moneyflow / paper-daily Eng / 叶30
- **未** commit；**未**更新 TEAM_STATE / ql_bus
- `py_compile` 两脚本 **OK**（语法烟；非业务重跑）

## 7. 下一步（非本拍）

1. **Arch** 审本 DIFF + 封面 → PASS / 驳回。
2. Arch DIFF **PASS 后等主令**再重跑 `b4_paper_extend`（无 `--force`）写出 `B_B4_*_20261026_r2.parquet`（check `ok=true`）。
3. S6 shadow 同拍或随后由主令顺手。
4. Eng X2H bridge / paper-daily 仍 HOLD 至主令。

FWD 仍 WAITING@11-02。**不报 Leo**。
