# AI COVER：叶35 份额 PIT B1 已落地正式脚本（禁实跑 / 禁 X2）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 15:11 ET**（America/New_York；`2026-10-27T15:11:15-04:00`） |
| 主令 | Arch 补丁只审 **PASS_WITH_CONDITIONS `31a08790` MATCH**；endorse B1；主裁落地 B1 |
| **结论** | **SCRIPT_LANDED**；正式路径 sha8 **`434ff42c`**（≠`25ae4572`）；**EXECUTED_X2=false** |
| live / leo_notify | **false** / **false** |

## 一句话

已按 DRAFT **`bdfd3c56`** / DIFF **`2d3abebd`** 手工等价写入 `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py`（/tmp 改拷贝→`diff -u` 仅目标 hunk→atomic `install`；**未**盲 `patch -p` DRAFT ONLY）。落地后脚本 sha8 **`434ff42c`**；dry-compile **PASS**；pyflakes **PASS**；C3 方案 A / mask-only / top_q=0.20 / C11≠叶26 / 不降门 **不变**；`pq.read_table` **保持**。**未申 `.ok` / 未挂 QUIET / 未跑 X2 / 未读真 parquet 压力**。交主→Arch **另票只审新脚本**。

## 钉点 MATCH

| 件 | sha8 | 全长 / 路径 |
|---|---|---|
| 正式脚本 AFTER | **`434ff42c`** | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` · `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` |
| 正式 BEFORE（VOID/对照钉） | **`25ae4572`** | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` · `/tmp/leaf35_formal_25ae4572_BEFORE.py` |
| DRAFT | **`bdfd3c56`** | `bdfd3c56ca38591db842e3167176e683f7ed45d7564fb0672dbde98e5f701043` |
| COVER DRAFT | **`8ea77257`** | `8ea772576fdf6add2a7054ec2cec891b05fd0b9800057c324db1e14183810a84` |
| DIFF DRAFT | **`2d3abebd`** | `2d3abebd4032adacc6905b0db935305e1e9c767391a30540470341f217acf8c7`（DRAFT ONLY—DO NOT APPLY；本拍手写等价） |
| Arch 补丁审 | **`31a08790`** | `31a08790967f49fb25443e81d93c0dcb68dab46a7abaa378f89d6c2ede9b3eac` PASS_WC |
| PIN / FROZEN / COUNT JSON | **`dd17044a`** / **`be9fc459`** / **`a17b75fb`** | PIN §1.3；FROZEN；`output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` |
| 叶33 正式 | **`afbbe7e7`** | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` · **UNCHANGED 未碰** |
| 本拍 LANDED DIFF | **`06a202c3`** | `06a202c3edcda56a687063a0ac6374f41761587681418ed8b5245d93b38e7347` |

## B1 语义（已写入）

1. `_load_etf_flows_window`：取消 `trade_date.isin(rebal_days)`；改为 buffered window `[first_rebal−40d, last_rebal]`；docstring 标明 B1/PIN§1.3。
2. `_pressure_on_day`：取消 `trade_date==d`；改为 `available_at_clock≤t_ts ∧ trade_date≤d`，再 per-ETF 最新 `available_at_clock`。
3. 未改其他函数 / 门控 / CLI；保持 `pq.read_table`。

## 禁令自检

- 本拍禁跑 X2；禁申 `.ok`；禁挂 QUIET；禁 `--allow-real-data`；禁读真 parquet 跑压力
- 禁 RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`81521fb5`+旧票
- 禁碰叶33 `afbbe7e7`；禁 git commit；pgrep 空
- ≠X2 ACCEPT；≠叶36；**leo_notify=false**；live=false；**EXECUTED_X2=false**
