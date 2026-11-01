# STRATEGY 热修：B4 Option A LEG_CHG |= 改为 .update（UnboundLocalError）

- 时刻（America/New_York）：2026-10-26T19:29:23-0400
- live=false；promotion=false；禁 --force
- 状态：HOTFIX_LANDED；B4 重跑已用热修 sha 写出 parquet（见下）；等 Arch 追认热修 DIFF

## 现象

主令 GO 后以 Arch PASS 钉 `625ddcd6` 执行 `--run-legs` →

`UnboundLocalError: cannot access local variable 'LEG_CHG'` @ L254。

根因：选项 A 使用 `LEG_CHG |= set(...)` 增强赋值，使 `main()` 内 LEG_CHG 被视作局部名。S6 的 `leg_chg` 本就在函数内初始化，不受影响（仍 `93b00354`）。

## 热修

同语义：`LEG_CHG.update(change_days(booked_parquet))`（不用 `|=`）。DIFF：`docs/v2/audit/STRATEGY_B4_RHYTHM_OPTION_A_HOTFIX_UPDATE_20261026.diff` sha `458512463451713a5de7eee6c727ccbb67b002c68fbca3daca2b56c11a318bf1`（sha8 `45851246`）。

| 项 | sha8 | 全长 |
|---|---|---|
| Option A 炸钉 | `625ddcd6` | `625ddcd68353605e6e14d0448117bff85ce41053b5f1c0369a6de33d54ab644c` |
| 热修后 B4 | `da62b28a` | `da62b28a43a88bb9e28d725eba84040be7c99ae5b08e93e9960e4a0057aad1c6` |
| S6（不变） | `93b00354` | `93b0035431929ea6fddd955a30673e588606ab8aa97c94c0637dbc0d5a05bd45` |
| 前序 DIFF PASS | `e506dc63` | 语义母本仍有效 |

## B4 重跑结果（热修 sha；已落盘）

| AUM | parquet sha8 | check ok | rhythm_ok | status |
|---|---|---|---|---|
| 60w | `7c99ab58` | true | true | WRITTEN |
| 100w | `48cbb6e2` | true | true | WRITTEN |

- `new_change_days=["2026-10-14"]`；`leg_change_days_forward` 含 10-13/14/15
- check 内 `frozen_script_sha256[b4]=da62b28a…`（热修）

请 Arch **追认**热修 DIFF；S6 本拍继续按已 PASS 的 `93b00354` 开跑。
