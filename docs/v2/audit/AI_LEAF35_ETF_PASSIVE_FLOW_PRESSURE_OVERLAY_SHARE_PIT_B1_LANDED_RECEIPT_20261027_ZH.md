# AI 回执：叶35 份额 PIT B1 已落地正式脚本（禁 execute / 禁 X2）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 15:11 ET**（America/New_York；`2026-10-27T15:11:15-04:00`） |
| 主令 | Arch PASS_WC **`31a08790` MATCH**；endorse B1 → 落地 B1 |
| **结论** | **SCRIPT_LANDED**；正式脚本 **`434ff42c`**（≠`25ae4572`）；dry-compile **PASS**；pyflakes **PASS**；**EXECUTED_X2=false** |
| ≠X2 ACCEPT | **true** |
| live / leo_notify | **false** / **false** |

## 0. 一句话

DRAFT **`bdfd3c56`** / DIFF **`2d3abebd`** B1 语义已手工原子写入 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py`；落地 sha8 **`434ff42c`**；叶33 **`afbbe7e7` UNCHANGED**。交主→Arch **另票只审新脚本**。未申 `.ok` / 未挂 QUIET / 未跑 X2。

## 1. 产出钉

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| 正式脚本 AFTER | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | **`434ff42c`** | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` |
| 正式 BEFORE 备份 | `/tmp/leaf35_formal_25ae4572_BEFORE.py` | **`25ae4572`** | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` |
| LANDED DIFF | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_DIFF_20261027.diff` | **`06a202c3`** | `06a202c3edcda56a687063a0ac6374f41761587681418ed8b5245d93b38e7347` |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_COVER_20261027_ZH.md` | **`fb514f52`** | `fb514f526255072d1929d3a5bc72b24c1d7409fae735783d357a4a25672017d5` |
| CMD | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_B1_LANDED_CMD_20261027_ZH.md` | **`e2773c12`** | `e2773c12395f110b6293d4230d7d6848010ee63c13c457872f95f83c8d41b66a` |
| RECEIPT | 本文件 | **见落盘后重算** | — |
| Arch 补丁审 | `…_SHARE_PIT_PATCH_REVIEW_…` | **`31a08790`** | `31a08790967f49fb25443e81d93c0dcb68dab46a7abaa378f89d6c2ede9b3eac` |
| DRAFT / COVER DRAFT / DIFF DRAFT | | `bdfd3c56` / `8ea77257` / `2d3abebd` | 落盘前 MATCH |
| PIN / FROZEN / COUNT JSON | | `dd17044a` / `be9fc459` / `a17b75fb` | MATCH |
| 叶33 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | **`afbbe7e7`** | UNCHANGED |

## 2. 验证

- 落盘前钉 MATCH：formal BEFORE=`25ae4572`；DRAFT=`bdfd3c56`；COVER DRAFT=`8ea77257`；DIFF=`2d3abebd`；Arch=`31a08790`；PIN=`dd17044a`；FROZEN=`be9fc459`；COUNT JSON=`a17b75fb`；叶33=`afbbe7e7`
- 方法：备份 → `/tmp` 手工改 → `diff -u` 仅 3 hunk（`_load_etf_flows_window`×2 + `_pressure_on_day`×1）→ `install` 原子覆写；**禁止**对 research/ 盲 `patch -p` DRAFT ONLY
- `py_compile` → `/tmp/leaf35_b1_land.pyc` **PASS**
- `/tmp/ql_pyflakes_venv/bin/pyflakes` exit **0**
- `pq.read_table` 保持；目标函数内无 `trade_date.isin(rebal)` / 无 `trade_date == d` 硬过滤残留（他处日历 isin 未动）
- pgrep `kline|export_static|snapshot|gen` **空**；live `.ok` 未申；QUIET 未挂；**未** git commit

## 3. Arch CONDITIONS（`31a08790`）对照

| Cond | 本拍 |
|---|---|
| 落地 research/ 新 sha8≠`25ae4572` | **DONE** `434ff42c` |
| 对齐 PIN §1.3（取消 trade_date==rebal；asof avail≤t_ts） | **DONE** |
| C3A / mask-only / top_q / C11 / 不降门不变 | **保持** |
| 禁 RESTORED 旧票；禁本拍跑 X2 | **钉**（未申任何 `.ok`；EXECUTED_X2=false） |
| 交主→Arch 另票只审新脚本 | **本拍交回** |

## 4. 禁令自检

未跑 X2；未申 `.ok`；未挂 QUIET；未 `--allow-real-data`；未读真数压力；未 RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票；未碰叶33；未 git commit；≠叶36。

## 5. 下一跳

主→Arch **另票只审新脚本 `434ff42c`** → 再裁新 X2 签窗（**新** `.ok`；禁 RESTORED）。

**EXECUTED_X2=false** · ok_requested=false · live=false · leo_notify=false · ≠X2 ACCEPT · ≠叶36

---
RECEIPT_SHA8=`d81e40f2` FULL=`d81e40f20f91a46784d4f81b68fb5e6aaf0676fce5d5073a2471e14f5af5f0a4`
