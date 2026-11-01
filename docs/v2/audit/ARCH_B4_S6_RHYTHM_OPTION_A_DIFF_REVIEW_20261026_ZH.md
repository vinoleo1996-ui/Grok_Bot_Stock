# Arch DIFF 审：B4/S6 rhythm Option A 最小补丁

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器：**只审 DIFF**；**不改脚本 / 不代跑 / 不写 parquet**） |
| 时刻 | `2026-10-26T19:25:57-04:00`（America/New_York；墙钟 `2026-10-26 19:25 ET`） |
| **VERDICT** | **PASS_WITH_CONDITIONS** |
| 审结对照 | `docs/v2/audit/ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` sha8 **`559e3057`** |
| 提案对照 | `docs/v2/STRATEGY_B4_RHYTHM_ABORT_PROPOSAL_20261026_ZH.md` sha8 **`5dfbe8d2`** |
| DIFF | `docs/v2/audit/STRATEGY_B4_S6_RHYTHM_OPTION_A_20261026.diff` sha8 **`8ea05f64`** |
| 封面 | `docs/v2/STRATEGY_B4_S6_RHYTHM_OPTION_A_DIFF_COVER_20261026_ZH.md` sha8 **`6e42357e`** |
| B4 新 | `research/b4_paper_extend.py` sha8 **`625ddcd6`** |
| S6 新 | `research/s6_paper_extend.py` sha8 **`93b00354`** |
| 本回合动作 | 写本审回执；prepend TEAM_STATE；**未**改两脚本；**未**改 FROZEN_CONFIG；**未**写/删 parquet；**未**跑 extend；**未** `--force`；**未**触 A18/叶30/`.ok`；**不报 Leo**；live=false |
| ≠ | **≠X2 ACCEPT**；FWD 仍 WAITING@11-02；叶30 另线勿混 |

## 0. 一句话

Strategy 落盘的 Option A 最小补丁 **MATCH** 审结 `559e3057` §3.1：`splice_booked` 之后、`check`/`rhythm_ok` 之前 `LEG_CHG |= set(change_days(booked_parquet))`（S6：`leg_chg |= …` 同语义）。C1–C5 全过；本拍 **PASS_WITH_CONDITIONS**——CONDITIONS 是重跑硬闸，非补丁违规。Arch **不代跑**；请主 MATCH 后令 Strategy/Eng 用**新**脚本 sha 重跑（禁 `--force`）→ 写出 parquet → 再令 Eng 重桥。

## 1. sha 链核验（本机 `sha256sum`）

| # | 项 | 期望 sha8 | 全长 | 结果 |
|---|---|---|---|---|
| V1 | 审结 APPROVE_A | `559e3057` | `559e30571b9459552dfc62b2d5f15aa5d8fe0f6eccc59ecf9405dcded5e86b44` | **MATCH** |
| V2 | 提案 | `5dfbe8d2` | `5dfbe8d2abcca65ad2fe2cc3c569ffea8eef2c352c4bfcf098c635f309bd490c` | **MATCH** |
| V3 | 封面 | `6e42357e` | `6e42357effe0442af61178720c49a7b6dc867799bc49a24f4a1ca44529d5240d` | **MATCH** |
| V4 | DIFF | `8ea05f64` | `8ea05f64e5d8039efc6c748e36f66ebd51cc72ab822a9f3336d034b1146a2cbe` | **MATCH** |
| V5 | B4 现盘（新） | `625ddcd6` | `625ddcd68353605e6e14d0448117bff85ce41053b5f1c0369a6de33d54ab644c` | **MATCH** 封面声称 |
| V6 | S6 现盘（新） | `93b00354` | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` | **MATCH** 封面声称 |
| V7 | B4 旧对照/forbid | `6c927ae6` | `6c927ae692685e4b87054ecccd1a1342be735d8242cbfe82f0b1f84b9a82653c` | **记录于封面**；不得再当合法冻结脚本钉 |
| V8 | S6 旧对照/forbid | `3b258bbe` | `3b258bbe9bd213fefc06f0dfa27d363fdb50e7672157831957d461f44eb92e7a` | **记录于封面**；不得再当合法冻结脚本钉 |
| V9 | 目标 parquet | — | `B_B4_*_20261026_r2.parquet` / S6 对应 | **ABSENT**（仅既有 check.json @19:08 ET；本拍未新写） |
| V10 | `py_compile` | — | 两脚本 | **OK**（语法烟；非业务重跑） |

DIFF 与现盘交叉：DIFF 声称 new sha == 现盘 B4/S6；现盘 L270–273 / L125–128 含 Option A 两行（注释+union）；DIFF 各文件仅 +2 行。

## 2. DIFF 要点摘要

**B4**（`research/b4_paper_extend.py` ≈L269–273）：

```python
        if bp is not None:
            W, booked = splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: LEG_CHG.add(booked["deferred_rebalance_day"])
            # Option A (Arch APPROVE 20261026): booked-window realized change days stay in LEG_CHG across re-extends
            LEG_CHG |= set(change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
```

**S6**（`research/s6_paper_extend.py` ≈L124–128）：

```python
        if bp is not None:
            W, booked = B.splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: leg_chg = leg_chg | {booked["deferred_rebalance_day"]}
            # Option A (Arch APPROVE 20261026): same semantics as b4 — booked realized change days ∪ into leg_chg
            leg_chg |= set(B.change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
```

落点顺序：**splice → deferred add → Option A union → `check`（含 `rhythm_ok`）→ 写盘判定**。`rhythm_ok` 公式未改：仍 `hist_change_days_identical and set(fchg) <= LEG_CHG`（B4 L241 / S6 L98）。

边界：`if bp is not None` 内执行 → 无 booked 不炸；`change_days` 空 → `set()` 并入为 no-op。读全 booked parquet 的 `change_days` 为审结 §3.1 允许的等价/超集并入，**不**放宽 post-booked 子集检验。

## 3. C1–C5（对照 APPROVE_A）

| ID | 条件 | 结果 | 证据 |
|---|---|---|---|
| **C1** | 最小：只加 LEG_CHG 并入 booked change days；禁改 booked-day never rewrite；禁短路 rhythm；禁回滚/删 booked；禁 `--force` 旁路 | **PASS** | DIFF 各 +2 行；`splice_booked` 正文未改；`rhythm_ok` 公式未改；无 argparse `--force`；未触 `20261014_r2` / FROZEN |
| **C2** | 产物 `frozen_script_sha256` 指向新脚本；旧 sha 对照/forbid | **PASS（机制+对照）** | `TRACK_SCRIPTS` 含本脚本；运行时 `script_shas(TRACK_SCRIPTS)` 写入 check；封面钉新旧全长；本拍未 invent `.ok`、未改 FROZEN_CONFIG |
| **C3** | 本拍未重跑；parquet 仍 ABSENT；check 可为 ABORT | **PASS** | 无 `*_20261026_r2.parquet`；既有 check.json mtime 19:08 ET（补丁 19:22 前）；本拍 Arch/Strategy 均未跑 extend |
| **C4** | S6 与 B4 同语义（非仅注释） | **PASS** | S6 `leg_chg |= set(B.change_days(...))` 与 B4 `LEG_CHG |= set(change_days(...))` 字面同构；落点同序 |
| **C5** | 禁区守住 | **PASS** | 未 `--force`；未短路；未回指/删 booked；未改 FROZEN 绕检；未触 A18/叶30/`.ok` |

## 4. CONDITIONS（PASS 后硬闸 · 非补丁违规）

| ID | 条件 |
|---|---|
| **R1** | 主令重跑前须确认现盘脚本 sha 仍为 B4 **`625ddcd6`** / S6 **`93b00354`**；旧 `6c927ae6` / `3b258bbe` **禁止**再跑 |
| **R2** | **禁 `--force`**；禁短路 `rhythm_ok`；禁回滚/删 `…_20261014_r2` |
| **R3** | 重跑后目标：`B_B4_50_25_25_topN_{60,100}w_20261026_r2.parquet` 写出；check `ok=true` 且 `rhythm_ok=true`；`frozen_script_sha256` 反映新脚本 |
| **R4** | S6 shadow 同拍或主令随后顺手；不得长期 B4 单过 S6 永久 ABORT |
| **R5** | Eng X2H / paper 重桥 **另令**；本 DIFF 审结 **≠** 重桥授权 |
| **R6** | FWD 仍 **WAITING@2026-11-02**；**≠X2 ACCEPT**；promotion=false；live=false |
| **R7** | 叶30 / A18 / QUIET **另线勿混**；**不报 Leo** |

## 5. 禁区 / 本回合非动作（已守）

- **未改** `research/b4_paper_extend.py` / `research/s6_paper_extend.py` / `FROZEN_CONFIG`
- **未写 / 未删**任何 `*_20261026_r2.parquet`；**未**跑 extend；**未** `--force`
- **未触** A18 / 叶30 / 任何 `.ok` / QUIET
- **未** SendToUser；**不报 Leo**
- live=false

## 6. 结论与编排请求

**VERDICT=PASS_WITH_CONDITIONS** — sha 链全 MATCH；补丁语义满足 APPROVE_A §3.1；C1–C5 PASS。请主 **MATCH** 本回执 → **令 Strategy（或 Eng）** 用新脚本重跑 B4（及 S6）写出 `*_20261026_r2.parquet`（禁 `--force`）→ check `rhythm_ok=true` → **再令 Eng 重桥**。

live=false.

## 7. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_B4_S6_RHYTHM_OPTION_A_DIFF_REVIEW_20261026_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| DIFF sha8 | **`8ea05f64`** |
| 封面 sha8 | **`6e42357e`** |
| B4 新 sha8 | **`625ddcd6`** |
| S6 新 sha8 | **`93b00354`** |
| 审结对照 sha8 | **`559e3057`** |
| 正文 sha256（§0–§6，不含本节） | `7cdc7601bf8623a4e27b592fdf82a6faa2ab9cb5ba1786c4e3e04e1d2edd6c37` |
| 正文 sha8 | **`7cdc7601`** |

全文件（含本节）sha256：见落盘后 `sha256sum`（TEAM_STATE / 父回报）。

live=false.
