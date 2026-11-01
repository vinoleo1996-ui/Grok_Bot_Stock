# Arch 叶33 SHARE_UNLOCK_PRESSURE_RESID X2 `.ok` VOID（ABORT_TYPEERROR_TZ）

- **角色**：QuantLab Arch
- **written_et**：2026-10-27T06:42:30-04:00（America/New_York；盘 VOID 动作 2026-10-27T06:41:25-04:00）
- **voided_et**：2026-10-27T06:41:25-04:00
- **live**：false · **promotion_approved**：false · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck** · **≠A18**

## 结论

**VOID.ABORT_TYPEERROR_TZ** — 原票 sha8=`c5ed13df` **禁再消费 / 禁 RESTORED**；QUIET **已 lift**（仅 leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2 这把）；本回合**未新签** `.ok`、**不代跑**、**不抬帽**、**不代改脚本**、**非 CONSUMED_PASS**、**非 RSS**。回执实际 status 字样 = **ABORT_TYPEERROR_TZ**（与叶30 VOID.ABORT_PEAK_HWM / 叶27 VOID.ABORT_RSS 命名惯例对齐）。

## 核验（MATCH）

| 项 | 值 |
|---|---|
| AI 回执 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_RUN_RECEIPT_ABORT_TZ_20261027_ZH.md` |
| AI 回执 sha256 | `481bacda12b3f820134adc0acf7dbb574c52c6f49a3a21303df4f85f1a70e6c1` |
| AI 回执 sha8 | `481bacda` — **MATCH** |
| AI 结论 | **ABORT_TYPEERROR_TZ**；SUCCESS=false；TypeError 早退（**非** Exit 94/95；**非** RSS） |
| 主令 | 主 06:37 ET priority Arch CONSUME/VOID + lift QUIET |
| ET_TS | `20261027_063601` |
| run_pid | **4096856** — 已退出 |
| 根因 | `_load_share_float_window` L818：`available_at`=`datetime64[us, Asia/Shanghai]` vs naive `asof` → TypeError |
| peak_kb | ≈**450768**（after_sw）≪1500硬帽；**非 RSS 失败** |
| alpha / overlap / run_meta | **ABSENT** |
| out | `output/ai_factory/_leaf33_share_unlock/20261027_063601/` **空** |
| 脚本钉 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`05c45917`** MATCH（只读核；**UNCHANGED**） |
| SIGNED / 审 / FROZEN / PIN | `aaaff921` / `2fa37636` / `8ed43721` / `4e17ccfc`（只引用） |
| ≠成功 | **非 CONSUMED_PASS**；无可用 alpha |

## VOID 归档

| 项 | 值 |
|---|---|
| 原 live | `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok`（**已不在 live**） |
| 原内容 sha256 | `c5ed13dff03942644f40443b1db01adc8cdee180fd4ade2b252a69658fe9edb7` |
| 原内容 sha8 | `c5ed13df` |
| 归档路径 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.c5ed13df.VOID.ABORT_TYPEERROR_TZ.20261027T0641ET.ok` |
| 归档文件 sha256 | `c5ed13dff03942644f40443b1db01adc8cdee180fd4ade2b252a69658fe9edb7` |
| 归档文件 sha8 | `c5ed13df`（内容钉不变；mv 不改内容） |
| live `.ok` | **ABSENT** |
| 禁复用 / forbid RESTORED | **`c5ed13df`** + **`5774bb6e`** + 既有二十票习惯集 |

## QUIET

| 项 | 值 |
|---|---|
| 处置前 | `output/loop/RESEARCH_QUIET.lock` 存在；内容 sha8 **`d588a1bd`**；holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；ok_sha8=`c5ed13df` |
| 处置 | **lift**（仅本 holder）→ `output/loop/_lifted/RESEARCH_QUIET_leaf33_share_unlock_pressure_resid_x2_ABORT_TYPEERROR_TZ_LIFTED_20261027T0641ET.lock` |
| 原 QUIET 内容 sha256 | `d588a1bdf7c88f40315ac8a9dacf394356ff50d3eb6b7c910fa720699a26f7f4` |
| 原 QUIET 内容 sha8 | `d588a1bd` |
| lift 文件 sha256 | `53ea26ba327022e37fb6b542dc6be3cf10f2d9367e2d50cab9b2f0fdd5e5e8b1` |
| lift 文件 sha8 | `53ea26ba`（内容追加 lift 块后 ≠ 原 `d588a1bd`） |
| 处置后 | live 锁 **ABSENT** |
| 占用核 | 无其他 leaf33 live 授权窗；live leaf33 `.ok`=0；**未触** `_lifted` 其他；**未触** A18 |

## 禁项（钉）

- **禁抬 rss**（仍 1500）；**禁**代改 `research/leaf33_*` 重跑；**禁** AI 自改复跑
- **禁 RESTORED** `c5ed13df` / `5774bb6e`+二十票；本拍**不新签** `.ok`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **禁触** A18；`0087c928`/叶28/29 另队
- **不报 Leo**；live=false；Arch **不代跑**

## 下一跳（架构口径 · 仅文档建议）

1. 请主令 AI 出 **tz 对齐补丁草案**（建议：`available_at` 与 `asof`/`d` 统一 naive 日历日或统一 `Asia/Shanghai` 后再 `normalize`；覆盖 `_load_share_float_window` + per-day PIT）→ Arch **只审** → **新** `.ok`（新名；**禁 RESTORED** `c5ed13df`）
2. **本拍不代改、不代签、不代跑**；禁 AI 自改复跑
3. ≠X2 ACCEPT；叶28/29 / `0087c928` 另队

## 非动作

- 不新签 `.ok`；不代跑研究脚本；不改主干代码；不抬帽；不 RESTORED；不触 A18；不报 Leo；live=false
