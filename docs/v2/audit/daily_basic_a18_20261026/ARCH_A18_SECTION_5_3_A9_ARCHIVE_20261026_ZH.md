# Arch A9 归档：A18 §5.3 引导基线 EXEC `.ok`（A9_RECONCILE_FAIL）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T18:03:00-04:00`（墙钟 2026-10-26 18:03 ET；归档动作） |
| 回执落盘 | 2026-10-26 18:05 ET |
| **状态** | **A9_ARCHIVED**（single_use 已消费；**勿复用**） |
| 触发 | 主令 A18 §5.3 A9 归档 + §3.1 口径判；Eng D1 sha8 **`09c1b2c8` MATCH**；结论 **A9_RECONCILE_FAIL** |
| archive_by | **Arch only**（Eng 未挪 live） |
| QUIET | **未挂** |
| 代跑 / seed / allow_run / 物化 / 改 parquet·manifest / 写 baseline | **均未** |
| live | false；不报 Leo；≠叶30 |

## 1. 钉核（归档前）

| 钉 | 期望 | 实测 | 结果 |
|---|---|---|---|
| Eng D1 | sha8 `09c1b2c8`；A9_RECONCILE_FAIL；diff=286；rows 差=0；baseline ABSENT | 全长 `09c1b2c8bf6cf7678d727f9a6c39139314806bbd96f21314cc4bed916addc751`；结论 MATCH 主钉 | **MATCH** |
| 审稿 | sha8 `232a2295` | 全长 `232a229583ae602520861e2bcad72c3a08aca3d8ce4f103a8636f561cb486dbb` | **MATCH** |
| live EXEC `.ok` | 路径 `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok`；sha8 `6de02e74`；mtime 仍 15:18 ET | 全长 `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca`；mtime `Oct 26 15:18`；size=2485 | **MATCH** |
| DEST / MAN | `f6bbf9e5` / `8c2c978b` | Eng 钉；本档未改生产 | **采信 Eng MATCH** |
| OUT_TMP | `/tmp/a18_s53_20261026T175303_2902093` | 仍在；`reconcile.json` diff_count=286；`DIFFS.json`；`driver.log` RECONCILE_FAIL；peak_kb=260192 a13_ok | **MATCH** |
| baseline | ABSENT | `daily_basic_full_tushare_build_baseline.json` **ABSENT** | **MATCH** |
| RESTORED | 禁 | 未见 RESTORED 标记；内容钉与 SIGNED 一致 | **OK** |

## 2. 归档动作

1. 复算 live 全长 sha = `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca` → **MATCH** `6de02e74`
2. `mv -n` 移入 `_consumed/`（保留原 mtime 15:18；**未**改文件内容）
3. 确认 live 路径 **ABSENT**
4. **未**挂 QUIET；**未** seed / allow_run / 物化 / 改 parquet·manifest；**未**盲写 baseline；**未**复用 `4377eb59`；**未**另签新 `.ok`；**勿复用本票** `6de02e74`

### 归档路径

`output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.6de02e74.A9_RECONCILE_FAIL.20261026T1803ET.ok`

| 区分 | 值 |
|---|---|
| **内容钉**（文件 bytes sha8 / 全长） | **`6de02e74`** / `6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca` |
| 归档路径文件 | 同上（`mv` 不改内容；路径名含内容钉 + 结果标签 + 墙钟） |
| live 路径 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` → **ABSENT**（`ls` No such file） |

## 3. live 清空证明

```
LIVE_ABSENT=YES
ls: cannot access '.../ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok': No such file or directory
archived sha256 = 6de02e7421fae731be0ee5ab68443ba514b908b34ec03a6ec049b88e42524eca
baseline ABSENT; QUIET ABSENT
```

## 4. 下游指针

- 口径书面结论：`ARCH_A18_SECTION_5_3_HASH_CALIBER_JUDGE_20261026_ZH.md`（同目录；**HASH_CALIBER_BUG**）
- 建议：Eng 先修 §3.1 dest 侧 hash 与 `ref_build_year` 对齐 → Arch 复审命令清单 → **主另签新窗**（**禁**复用 `6de02e74` / `4377eb59`）；禁带病写 baseline

≠X2；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 A9 归档）
