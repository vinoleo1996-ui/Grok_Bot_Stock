# Arch 追认审：B4 Option A 热修 DIFF（`|=` → `.update`）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器：**只审热修 DIFF**；**不改脚本 / 不代跑 / 不写 parquet**） |
| 时刻 | `2026-10-26T19:33:23-04:00`（America/New_York；墙钟 `2026-10-26 19:33 ET`） |
| **VERDICT** | **PASS_WITH_CONDITIONS**（**追认**热修；语义 ≡ APPROVE_A；流程 CONDITIONS） |
| 审结对照 | `docs/v2/audit/ARCH_B4_RHYTHM_ABORT_ADJUDICATION_A_20261026_ZH.md` sha8 **`559e3057`** |
| 前 DIFF 审 | `docs/v2/audit/ARCH_B4_S6_RHYTHM_OPTION_A_DIFF_REVIEW_20261026_ZH.md` sha8 **`e506dc63`**（钉过 B4 `625ddcd6`） |
| 主令重跑回执 | sha8 **`142b46e9`**（主已 MATCH 产物；已令 Eng 重桥） |
| 热修 DIFF | `docs/v2/audit/STRATEGY_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_20261026.diff` sha8 **`45851246`** |
| 封面 | `docs/v2/STRATEGY_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_COVER_20261026_ZH.md` sha8 **`f5d8f412`** |
| B4 现盘（热修后） | `research/b4_paper_extend.py` sha8 **`da62b28a`** |
| S6 现盘（未因热修改） | `research/s6_paper_extend.py` sha8 **`93b00354`** |
| 炸钉/forbid | B4 **`625ddcd6`**（与更旧 `6c927ae6` 并列 forbid；不得再跑） |
| 本回合动作 | 写本审回执；prepend TEAM_STATE；**未**改脚本；**未**改 FROZEN；**未**写/删 parquet；**未**重跑；**未** `--force`；**未**触 A18/叶30/`.ok`；**不报 Leo**；live=false |
| ≠ | **≠X2 ACCEPT**；FWD 仍 WAITING@11-02；叶30 另线勿混 |

## 0. 一句话

Strategy 热修将 Option A 的 `LEG_CHG |= set(...)` 改为 `LEG_CHG.update(...)`，为 **APPROVE_A 同语义实现修正**（in-place union；消解 `main()` 内模块全局 `LEG_CHG` 因增强赋值被视作 local 的 UnboundLocalError）。DIFF/封面/现盘 sha **全 MATCH**；B4/S6 产物已写出且 `rhythm_ok=true`、脚本钉 `da62b28a`/`93b00354`。本拍 **PASS_WITH_CONDITIONS（追认）**——语义过；「先跑再追认」记 CONDITIONS，**不**开 `--force` 先例。Arch **不代跑不代改**。主已令 Eng 重桥；本追认确认可继续。

## 1. sha 链核验（本机 `sha256sum`）

| # | 项 | 期望 sha8 | 全长 | 结果 |
|---|---|---|---|---|
| V1 | APPROVE_A | `559e3057` | `559e30571b9459552dfc62b2d5f15aa5d8fe0f6eccc59ecf9405dcded5e86b44` | **MATCH** |
| V2 | 前 DIFF 审 | `e506dc63` | `e506dc63f1789cf8a966ee014624916595e8929286b08c5b661be44d436f40f7` | **MATCH** |
| V3 | 热修 DIFF | `45851246` | `458512463451713a5de7eee6c727ccbb67b002c68fbca3daca2b56c11a318bf1` | **MATCH** |
| V4 | 封面 | `f5d8f412` | `f5d8f41299a28acd933153745cb9be27717ce6524744c512c9678724b049aed9` | **MATCH** |
| V5 | B4 现盘 | `da62b28a` | `da62b28a43a88bb9e28d725eba84040be7c99ae5b08e93e9960e4a0057aad1c6` | **MATCH** |
| V6 | S6 现盘 | `93b00354` | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` | **MATCH**（未因热修改） |
| V7 | 炸钉/forbid | `625ddcd6` | `625ddcd68353605e6e14d0448117bff85ce41053b5f1c0369a6de33d54ab644c` | **记录**；与 `6c927ae6` 并列 forbid |
| V8 | 主重跑回执 | `142b46e9` | （主钉；本拍不重算） | **采纳对照** |
| V9 | `py_compile` | — | B4+S6 | **OK**（语法烟；非业务重跑） |

## 2. 根因（可信）

B4：`LEG_CHG` 为**模块全局**（L219 `LEG_CHG: set = set()`）。`main()`（L246+）内原 Option A 行使用增强赋值：

```python
LEG_CHG |= set(change_days(...))
```

Python 将函数内任何对名的赋值（含 `|=`）标为 **local**。于是同函数更早的 L254 `LEG_CHG.update(...)`（legs 预热）在运行时读未绑定的 local → **`UnboundLocalError: cannot access local variable 'LEG_CHG'`**（封面称 @L254；本机最小复现一致）。

热修改为方法调用 `LEG_CHG.update(...)`：**不绑定名**，仍操作模块全局 set。现盘 L271–274：

```python
            if booked["deferred_rebalance_day"]: LEG_CHG.add(booked["deferred_rebalance_day"])
            # Option A (Arch APPROVE 20261026): booked-window realized change days stay in LEG_CHG across re-extends
            # Hotfix: use .update (not |=) so module-global LEG_CHG is not treated as local in main()
            LEG_CHG.update(change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
```

S6：`leg_chg` 在 `main()` 开头 `leg_chg = set()`（L113）即为 local；`leg_chg |= set(...)`（L128）合法，**无需热修**；现盘仍 **`93b00354`**。

## 3. 语义等价（= APPROVE_A 同语义实现修正）

| 点 | 结论 |
|---|---|
| 运算 | `set.update(iterable)` ≡ `set |= set(iterable)` 的 **in-place union**；`change_days` 返回 `list`，`.update(list)` 与 `|= set(list)` 元素并入等价（本机核） |
| 落点 | 仍在 `splice_booked` 之后、`check`/`rhythm_ok` 之前 |
| `rhythm_ok` | 公式未改：`hist_change_days_identical and set(fchg) <= LEG_CHG`（B4 L241） |
| C1–C5 | **未放宽**；无短路 rhythm；无回滚/删 booked；无 `--force`；未改 FROZEN |
| 越权？ | **否** — 仅绑定方式/API 表面从 `|=` 改为 `.update`；**非**新策略 |

## 4. 最小热修

- DIFF：**单文件单 hunk**（B4 一行 `|=` → `.update` + 一行热修注释）；未触 S6。
- S6 本就不需要热修（local `leg_chg`）。
- 对照前序 Option A DIFF `8ea05f64` 语义母本仍有效；热修是其 **runtime 绑定修复**。

## 5. 产物核验（只读）

| 产物 | PRESENT | check | rhythm_ok | frozen 脚本钉 | parquet sha8 |
|---|---|---|---|---|---|
| `B_B4_…_60w_20261026_r2.parquet` | **是** | ok=true / status=WRITTEN | **true** | B4 **`da62b28a…`** | `7c99ab58` |
| `B_B4_…_100w_20261026_r2.parquet` | **是** | ok=true / status=WRITTEN | **true** | B4 **`da62b28a…`** | `48cbb6e2` |
| `S6_…_60w_20261026.parquet`（轨内无 `_r2` 后缀） | **是** | ok=true / status=WRITTEN | **true** | S6 **`93b00354…`** | `8d76180a` |
| `S6_…_100w_20261026.parquet` | **是** | ok=true / status=WRITTEN | **true** | S6 **`93b00354…`** | `0d6ce661` |

两侧：`new_change_days=["2026-10-14"]`；`leg_change_days_forward` 含 10-13/14/15；`live=false`；`promotion_approved=false`。B4 **未**残留旧钉 `625ddcd6`。与主回执 `142b46e9` 产物钉一致。

## 6. CONDITIONS（追认硬闸 · 非语义否决）

| ID | 条件 |
|---|---|
| **H1** | **流程**：主令钉曾是 `625ddcd6`；Strategy 遇 UnboundLocalError 后热修并写出 parquet，**再**交 Arch 追认。本拍追认 **不**视为「可先改先跑再审」或 `--force` 先例。今后同类热修：**须先交 Arch 审 DIFF，再重跑**。 |
| **H2** | 合法 B4 冻结脚本钉现为 **`da62b28a`**；**`625ddcd6` 与 `6c927ae6` 并列 forbid**。S6 仍 **`93b00354`**。 |
| **H3** | **禁 `--force`**；禁短路 `rhythm_ok`；禁回滚/删 `…_20261014_r2` / booked。 |
| **H4** | Eng X2H / paper 重桥 **另令**；本追认 **≠** 重桥授权。主已令 Eng 重桥 → 本拍确认产物齐、脚本钉合法，可继续；Arch 不代跑。 |
| **H5** | FWD 仍 **WAITING@2026-11-02**；**≠X2 ACCEPT**；promotion=false；live=false。 |
| **H6** | 叶30 / A18 / QUIET **另线勿混**；**不报 Leo**。 |

## 7. 禁区 / 本回合非动作（已守）

- **未改** `research/b4_paper_extend.py` / `research/s6_paper_extend.py` / `FROZEN_CONFIG`
- **未写 / 未删**任何 parquet；**未**跑 extend；**未** `--force`
- **未触** A18 / 叶30 / 任何 `.ok` / QUIET
- **未** SendToUser；**不报 Leo**
- live=false

## 8. 结论与编排请求

**VERDICT=PASS_WITH_CONDITIONS（追认）** — 热修 = APPROVE_A 同语义实现修正；DIFF/封面/B4/S6 sha 全 MATCH；根因 UnboundLocalError 成立；产物 `rhythm_ok=true` 钉 `da62b28a`/`93b00354`。请主 **MATCH** 本回执（Eng 重桥令可继续）。告知 Strategy：热修追认通过；今后热修须先 Arch。

live=false.
## 9. 本文件钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_REVIEW_20261026_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS**（追认） |
| 热修 DIFF sha8 | **`45851246`** |
| 封面 sha8 | **`f5d8f412`** |
| B4 热修后 sha8 | **`da62b28a`** |
| S6 sha8 | **`93b00354`** |
| 炸钉/forbid | **`625ddcd6`**（并列 `6c927ae6`） |
| 前 DIFF 审 | **`e506dc63`** |
| APPROVE_A | **`559e3057`** |
| 主重跑回执 | **`142b46e9`** |
| 正文 sha256（§0–§8，不含本节） | `9bf3185d2d914f1f62fc6884c32c82f90877947b7bc4ccea5c5adb991b2ed1fe` |
| 正文 sha8 | **`9bf3185d`** |

全文件（含本节）sha256：见落盘后 `sha256sum`（TEAM_STATE / 父回报）。

live=false.
