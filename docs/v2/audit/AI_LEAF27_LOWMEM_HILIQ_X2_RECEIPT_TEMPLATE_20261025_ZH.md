# 叶27 降内存 HILIQ×x2 回执模板（TEMPLATE · 非实跑回执）

- **角色**：QuantLab AI
- **时刻**：2026-10-25T11:42:00-04:00（America/New_York）— 模板落盘时刻
- **状态**：**TEMPLATE**（字段待实跑后填；**不是**实跑回执）
- **live**：false · **promotion_approved**：false
- **关联草案**：`docs/v2/audit/AI_LEAF27_LOWMEM_HILIQ_X2_CMD_DRAFT_20261025_ZH.md`
- **窗**：12:30–13:30 ET（有 Arch 新 `.ok` 且入窗再跑）

> 开跑完成后复制本模板为正式回执（建议改名去掉 `_TEMPLATE_` / 或另写 `…_RUN_RECEIPT_…`），填齐后 `sha256sum` 盘证。

## 钉核验（实跑后填）

| 项 | 期望 / 预留 | 实填 |
|---|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_…`（新签） | _TBD_ |
| `.ok` sha256 | （新签全长；**≠** VOID） | _TBD_ |
| 禁复用 VOID | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` | **未消费 / 未复用** |
| 脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | _盘证_ |
| 脚本 sha256 | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | _MATCH?_ |
| CLI | `--universe HILIQ --window x2`（禁 both） | _TBD_ |
| rss_limit | **1500** MB（禁抬帽） | _TBD_ |
| 窗 / expires | 12:30–13:30 ET / （以 `.ok`） | _TBD_ |
| Arch 审阅 | `aefa7faa9974cd891fb097a7491a7f72534c92189c7f478ab58092fca79973fb` | 引用 |

## 执行（实跑后填）

| 项 | 实填 |
|---|---|
| ET_TS | _TBD_（`YYYYMMDD_HHMMSS`） |
| started_et / ended_et | _TBD_ |
| run_pid / sampler_pid | _TBD_ |
| rc | _TBD_ |
| result | _PASS / FAIL / ABORT_RSS_OVER_LIMIT / …_ |
| interpreter | `/workspace/qlvenv/bin/python` |
| env | `PYTHONDONTWRITEBYTECODE=1`；nice -n 10（若用） |
| log | `output/ai_factory/leaf27_on_minus_id_idio_ivol/_logs/run_<ET_TS>.log` sha=_TBD_ |
| sampler | `/tmp/quantlab_leaf27_lowmem_hiliq_x2_<ET_TS>/sampler_30s.txt` sha=_TBD_（禁 output*） |

## 强制披露（Arch 条件）

| 披露项 | 实填 |
|---|---|
| **峰 RSS**（MB） | ps 峰值=_TBD_；日志末/最大 `rss=`=_TBD_；`run_meta.peak_rss_mb`=_TBD_ |
| 是否破帽（>1500） | _YES→ABORT / NO_ |
| **float32 存储** | mktcap/capadv（及 LimitPanel 板价）以 float32 数组存；相对基线 float64 嵌套 dict **可能边际数值差** — 披露：_已注明 / 观测差=_TBD_ |
| **`_prune_hist`** | 每~40 日剪不在 alive 的 β/ε 历史；相对基线可能边际差 — 披露：_已注明 / 观测=_TBD_ |
| 无 α 选参 | _确认未改 α/β/W/门控_ |

## 产物路径（实跑后填）

| 产物 | 路径 | sha256 / 状态 |
|---|---|---|
| alpha | `output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_<stamp>.parquet` | _TBD 或 无_ |
| run_meta | `…/run_meta_HILIQ_x2_<stamp>.json` | _TBD 或 无_ |
| build_summary | `…/build_summary_<stamp>.json` | _TBD 或 无_ |

## QUIET / 让出

| 项 | 实填 |
|---|---|
| QUIET 设/lift | _TBD_ |
| healthz quiet 终态 | _TBD_ |
| 是否挡其他窗 | _TBD_ |

## `.ok` 处置（实跑后）

- 消费/归档：**待 Arch**（AI 不自 VOID；破帽则禁再消费本 `.ok`）
- AI：**不自重试**；不申抬帽；sealed 另窗另签

## 请 Arch / 主（占位）

1. Arch：核回执 MATCH；裁定 PASS 或破帽归档
2. 主：是否排 sealed 另窗
3. Data：无 CONT（除非回执另述）

live=false。
