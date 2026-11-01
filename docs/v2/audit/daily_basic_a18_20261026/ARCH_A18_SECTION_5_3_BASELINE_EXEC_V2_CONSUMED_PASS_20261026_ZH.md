# Arch A18 §5.3 EXEC_V2 CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T18:38:56-04:00`（归档+lift 动作） |
| 回执落盘 | `2026-10-26T18:39:23-04:00` |
| **结论** | **CONSUMED_PASS** |
| archive_by | **Arch only**（Eng 未挪 live；禁 Eng 自 lift） |
| live / promotion / ≠X2 ACCEPT / ≠叶30 签 | **false** / **false** / **true** / **true** |
| 代跑 / seed / allow_run / 物化 / 改 parquet·manifest·incr / 候选3 enable / 签叶30 / 报 Leo | **均未** |

## 1. 钉核（CONSUME 前）

| 钉 | 期望 | 实测 | 结果 |
|---|---|---|---|
| Eng D1 MD | sha8 `0ddeb1b7` | 全长 `0ddeb1b7e4340d0e87625fc27b3431bbdc02d1cc63a81a7aae81285853bed2e2` | **MATCH** |
| Eng D1 JSON | sha8 `1a50b8a5`；status=DONE；reconcile_ok=true；diff_count=0；years 13/13；end=`20261016`；a13_ok；pid 2950358；peak VmHWM 263040 | 全长 `1a50b8a5c1d2d1981c642669c738849ec53bc7aa8edc66ac55da26def18efd9c`；字段 MATCH | **MATCH** |
| baseline | PRESENT sha8 `273163cc` | 全长 `273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486`；路径 `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` | **MATCH** |
| live EXEC_V2 `.ok` | sha8 `a62881b9`；driver `af15b52d`；helper `3094f0b6`；审 `0815e13f`；SIGNED `b49544ed` | 全长 `a62881b9f9078cf3df8b3fc992be999701ff562cfacc29a76e98fdb789c06ec6`；钉齐 | **MATCH** |
| live QUIET | sha8 `bf4548d4`；holder=`a18_s53_v2`；do_not_lift_until_arch_or_consumed | 全长 `bf4548d48a8eb16c1cfc45d6f7d5245b45ed4cd60808faf0d8f8bcd8f34a57dd` | **MATCH** |
| pid 2950358 | gone | `ps` 无该 pid；无 a18_s53 重进程 | **MATCH** |
| RESTORED / 旧票 | 禁 `6de02e74`/`4377eb59`/`a158f17a`/`5ae077fa` | 未见 RESTORED；内容钉与 SIGNED 一致 | **OK** |

## 2. 归档 `.ok`

1. 复算 live 全长 sha = `a62881b9f9078cf3df8b3fc992be999701ff562cfacc29a76e98fdb789c06ec6` → **MATCH** `a62881b9`
2. `mv -n` 移入 `_consumed/`（保留原 mtime 18:25；**未**改文件内容）
3. 确认 live 路径 **ABSENT**

### 归档路径

`output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.a62881b9.CONSUMED_PASS.20261026T1838ET.ok`

| 区分 | 值 |
|---|---|
| **内容钉**（文件 bytes sha8 / 全长） | **`a62881b9`** / `a62881b9f9078cf3df8b3fc992be999701ff562cfacc29a76e98fdb789c06ec6` |
| 归档路径文件 | 同上（`mv` 不改内容；路径名含内容钉 + CONSUMED_PASS + 墙钟） |
| live 路径 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.ok` → **ABSENT** |

## 3. 合法 lift QUIET（Arch）

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；内容 sha8 **`bf4548d4`**；holder=`a18_s53_v2`；8795 quiet=true |
| 处置 | **lift** → `output/loop/_lifted/RESEARCH_QUIET_a18_s53_v2_CONSUMED_PASS_LIFTED_20261026T1838ET.lock`（原内容 + `# ARCH_QUIET_LIFTED` 注记） |
| 原 QUIET 内容 sha256 | `bf4548d48a8eb16c1cfc45d6f7d5245b45ed4cd60808faf0d8f8bcd8f34a57dd` |
| 原 QUIET 内容 sha8 | **`bf4548d4`** |
| lift 文件 sha256 | `961ac5d1d5133d584f048b5741a12e0a9b367eca1559356e34d0eba710c2b426` |
| lift 文件 sha8 | **`961ac5d1`** |
| 处置后 | live 锁**无**；healthz `quiet=false`（`quiet_reason=""`）；研究 a18 pid 空 |
| 关系 | lift 文件 = 原 `bf4548d4` 字节 + Arch lift 注记；原内容钉关系保留于注记字段 `quiet_content_sha8=bf4548d4` |

## 4. live 清空证明

```
LIVE_OK_ABSENT=YES
LIVE_QUIET_ABSENT=YES
archived_ok_sha256 = a62881b9f9078cf3df8b3fc992be999701ff562cfacc29a76e98fdb789c06ec6
baseline PRESENT sha8=273163cc（本拍未改）
8795 healthz quiet=false @ 2026-10-26T18:38:56-04:00
```

## 5. 下游指针

- Eng D1：`docs/v2/audit/daily_basic_a18_20261026/ENG_A18_SECTION_5_3_BASELINE_EXEC_V2_RECEIPT_20261026_ZH.md`（`0ddeb1b7`）+ JSON（`1a50b8a5`）
- SIGNED：`ARCH_A18_SECTION_5_3_BASELINE_EXEC_V2_SIGNED_20261026_ZH.md`（`b49544ed`）
- baseline：`data/v2/valuation/daily_basic_full_tushare_build_baseline.json`（`273163cc`）
- 建议主令：**Data 写 DONE marker** → 再排纸面；叶30 独立 X2 签窗可按主排（QUIET 已 ABSENT；仍听主窗 ≥23:05 或另令）
- **禁**复用本票 `a62881b9` RESTORED；**禁**复用 `6de02e74`/`4377eb59`/`a158f17a`/`5ae077fa`

≠X2 ACCEPT；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 EXEC_V2 CONSUMED_PASS）
