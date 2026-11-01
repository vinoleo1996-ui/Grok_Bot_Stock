# 叶33 tz 对齐补丁封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T06:51:37-04:00（America/New_York；墙钟 2026-10-27 06:51 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · **EXECUTED=false**
- **优先级**：主令 ~06:44 ET；Arch VOID **`8a3b25ba` MATCH** → 出 tz 对齐补丁草案（只审路径）

## 一句话

对齐策略写死 **`naive_calendar_day`**：新增 `_as_naive_norm_ts` / `_as_naive_norm_series`，覆盖 `_load_share_float_window`（原 L818）+ per-day PIT（原 L1073）+ SW 路径（防下一拍再炸）。候选 sha8 **`afbbe7e7`**；DIFF sha8 **`bf9ee97a`**；正式脚本 **`05c45917` UNCHANGED**。dry-compile **PASS**（含 tz pins）。**未实跑** / **未申 `.ok`** / **未挂 QUIET**。交主→Arch **只审补丁**。≠X2 ACCEPT。forbid 声明∋ RESTORED **`c5ed13df`**+**`5774bb6e`**+二十票；`0087c928`/叶28/29 另队。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| **对照正式脚本（UNCHANGED）** | **`05c45917`** · `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` |
| **候选（/tmp only）** | **`afbbe7e7`** · `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` |
| Arch VOID | **`8a3b25ba`** |
| RUN ABORT | **`481bacda`** |
| QUIET lift（只引用） | **`53ea26ba`**；live QUIET ABSENT |
| FROZEN / PIN | **`8ed43721`** / **`4e17ccfc`**（机制未动） |
| tz_align_mode | **`naive_calendar_day`** |
| rss | **1500** 禁抬 |
| forbid 声明 | RESTORED **`c5ed13df`** + **`5774bb6e`**+二十票（脚本元组未改 21 项） |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | 仅 tz 对齐助手 + PIT/SW 调用点 + dry-compile tz pins；**不**改 C3/α/H/W/rebal/FROZEN/PIN/rss/overlap |
| **落地方式** | 本拍只 DIFF/候选；正式 `research/` **等 Arch 审过 + 主令** 再覆盖 |
| **真跑门** | 另窗新 `.ok`（禁 RESTORED `c5ed13df`）；本拍**未开** |
| **不改** | `05c45917` 正式字节；FROZEN；叶32/31 模板；任一 live `.ok`/QUIET |

## 禁止清单

- 本拍实跑 / `--allow-real-data` / 申 `.ok` / 挂 QUIET / 抬 rss / git commit / 覆盖正式脚本
- RESTORED **`c5ed13df`** / **`5774bb6e`+二十票**
- 事后翻 α 符号 / W / H / H_back / 再平衡；改 C3 加价公式
- 并入 `0087c928`；夹带叶28/29；报 Leo；声称 X2 ACCEPT

## 请 Arch / 主

1. **主**：收本 COVER+DRAFT+DIFF+RECEIPT → hand Arch **只审补丁**。
2. **Arch**：只审不签；PASS 后主排落地窗（新脚本 sha8 + **新** `.ok`；禁 RESTORED）。
3. 实跑另窗；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 | sha8 |
|---|---|---|
| DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DRAFT_20261027_ZH.md` | （见 RECEIPT） |
| COVER | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_COVER_DRAFT_20261027_ZH.md` | （见 RECEIPT） |
| DIFF | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_DIFF_DRAFT_20261027.diff` | **`bf9ee97a`** |
| RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_TZ_ALIGN_PATCH_RECEIPT_20261027_ZH.md` | （见 RECEIPT） |
| 候选 | `/tmp/leaf33_tz_patch_candidate.py` | **`afbbe7e7`** |

live=false · ≠X2 · ok_requested=false · EXECUTED=false · leo_notify=false
