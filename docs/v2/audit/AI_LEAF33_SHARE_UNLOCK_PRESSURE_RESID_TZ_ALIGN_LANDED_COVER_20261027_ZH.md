# AI COVER：叶33 tz 对齐补丁已落地正式脚本（禁实跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 07:03 ET**（`2026-10-27T07:03:00-04:00`） |
| 主令 | ~07:00 ET；Arch 只审 **PASS_WITH_CONDITIONS** **`19cc790f` MATCH** → 落地正式脚本 |
| **结论** | **SCRIPT_LANDED**；正式路径 sha8 **`afbbe7e7`**（≠`05c45917`）；基线钉 `tz_patch_base_script_sha8=05c45917`；**EXECUTED=false** |
| live / leo_notify | **false** / **false** |

## 一句话

已用 candidate **`afbbe7e7`** 覆盖 `research/leaf33_share_unlock_pressure_resid_alpha_build.py`；落地后脚本 sha8 **`afbbe7e7`**（与 candidate 字节相同）；`tz_align_mode=naive_calendar_day`；dry-compile **PASS**；C3/α/H/W/rebal/FROZEN **`8ed43721`**/PIN **`4e17ccfc`**/rss=1500/forbid21 **未改**。**未申 `.ok` / 未挂 QUIET / 未实跑**。交主→Arch **审新脚本**。

## 钉点

| 件 | sha8 |
|---|---|
| 正式脚本 | **`afbbe7e7`** / `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` |
| candidate（源） | **`afbbe7e7`** |
| 基线对照 | **`05c45917`**（`tz_patch_base_script_sha8`） |
| Arch 补丁审 | **`19cc790f`** PASS_WITH_CONDITIONS |
| 补丁 DRAFT/COVER/DIFF/RECEIPT | `30844702` / `54e38493` / `bf9ee97a` / `ca603494` |
| VOID / RUN ABORT | `8a3b25ba` / `481bacda` |
| FROZEN / PIN | `8ed43721` / `4e17ccfc` |
| 落地 DIFF | 见同批 DIFF 文件 |

## 不变钉

- C3=(a)+加价；α=`−rank(pressure_resid)`；H/H_back/W/rebal=20/5/20/20
- FROZEN `8ed43721` / PIN `4e17ccfc`；rss=1500；forbid21（文档另禁 RESTORED `c5ed13df`）
- PRIMARY=HILIQ；禁 `--no-overlap-report`

## 禁令

未实跑；未申 `.ok`；未挂 QUIET；禁 RESTORED `c5ed13df`+`5774bb6e`+二十票；`0087c928`/叶28/29 另队；≠X2 ACCEPT。
