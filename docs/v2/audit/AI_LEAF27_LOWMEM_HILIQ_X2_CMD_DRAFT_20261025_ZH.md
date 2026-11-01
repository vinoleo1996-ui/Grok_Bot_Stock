# 叶27 降内存首跑 · HILIQ×x2 专属 cmd / R5c 草案

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T11:42:00-04:00（America/New_York）
- **状态**：**DRAFT**（**未授权实跑** · **不是 `.ok`** · **不替代 Arch 签发**）
- **live**：false · **promotion_approved**：false
- **窗（主已排）**：**12:30–13:30 ET**；**有 Arch 新 `.ok` 且入窗**才开跑
- **本回合非动作**：不申 `.ok` · 不实跑 · 不读真实行情大表 · 不 git commit · 不 UpdateRoutine（除非主令）

## 1. 钉表（全长）

| 件 | 路径 | sha256 |
|---|---|---|
| 脚本（执行钉） | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| DIFF 文 | `docs/v2/audit/AI_LEAF27_LOWMEM_DIFF_20261025_ZH.md` | `b1455e935c5b18aecd17ab0c9ba5cb3a30d68639760f435d0df377821c2c2d1c` |
| patch | `docs/v2/audit/AI_LEAF27_LOWMEM_V1_20261025.diff` | `2154b6fb60fa448da10e0eba620fa22096051d6d41cad69dbd8e02cc37ec055f` |
| 封面 | `docs/v2/audit/AI_LEAF27_LOWMEM_COVER_20261025_ZH.md` | `1521e1a4eb91aa9954f28c3bbbf7d61333427739b27045f9a55025ec57c443a8` |
| Arch 审阅 | `docs/v2/audit/ARCH_LEAF27_LOWMEM_REVIEW_20261025_ZH.md` | `aefa7faa9974cd891fb097a7491a7f72534c92189c7f478ab58092fca79973fb` |
| 旧基线脚本（禁实跑授权） | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` |
| VOID `.ok`（**禁复用**） | `_consumed/…725be3e0.VOID.20261025T1115ET.ok` | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` |

- Arch 结论：**PASS_WITH_CONDITIONS**（四件 MATCH；本回合 Arch **不签**；另窗另签）
- FULLA 仍 **GAP**；禁 `--universe FULLA|both`；禁 `--window both`（首跑）
- sealed：**另窗另签另进程**（本草案不含）

## 2. 拟 cmd（单进程 · 仅 HILIQ×x2）

占位：`<ET_TS>=$(date +%Y%m%d_%H%M%S)`（开跑瞬间填）；`<ARCH_OK>`=Arch 新签发路径（**不得**填 VOID `725be3e0`）。

```bash
# DRAFT — 有新 .ok 且 12:30–13:30 ET 窗内才执行；本文件不是授权
cd /workspace/QuantLab && \
ET_TS=$(date +%Y%m%d_%H%M%S) && \
OUT=output/ai_factory/leaf27_on_minus_id_idio_ivol && \
LOGDIR=$OUT/_logs && \
SAMPDIR=/tmp/quantlab_leaf27_lowmem_hiliq_x2_${ET_TS} && \
mkdir -p "$LOGDIR" "$SAMPDIR" && \
# 预检：pgrep 空 + .ok 新钉 + 窗内（见 §4）后，再：
env PYTHONDONTWRITEBYTECODE=1 nice -n 10 \
  /workspace/qlvenv/bin/python \
  research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py \
  --universe HILIQ --window x2 \
  >"$LOGDIR/run_${ET_TS}.log" 2>&1
```

**一行摘要（开跑核）**：

```text
/workspace/qlvenv/bin/python research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py --universe HILIQ --window x2
```

| 路径类 | 约定 |
|---|---|
| out_dir | `output/ai_factory/leaf27_on_minus_id_idio_ivol`（脚本 `OUT_DIR` 硬钉；产物 `alpha_HILIQ_x2_*.parquet` / `run_meta_HILIQ_x2_*.json` / `build_summary_*.json`） |
| log | `…/_logs/run_<ET_TS>.log`（+ `.launch` 若有） |
| **sampler** | **必须** `/tmp/quantlab_leaf27_lowmem_hiliq_x2_<ET_TS>/sampler_30s.txt`（禁写 `output*` / `data*`） |
| x2 日历 | `2024-06-03` … `2026-10-09`（脚本 `WINDOWS["x2"]`） |

**明确禁止的 CLI**：`--window both` · `--universe FULLA|both` · 旧脚本 `g1g5_on_minus_id_idio_ivol_alpha.py`（`7a5f756c…`）。

## 3. 帽与中止（禁抬帽）

| 项 | 值 | 说明 |
|---|---|---|
| **rss_limit** | **1500** MB（硬钉） | `.ok` 须同钉；**禁抬帽** |
| 破帽 | **ABORT** | 外监/Arch TERM；对齐 ABORT 回执先例；**不**自重试 |
| 脚本内 C4/stop/hard | **无**内建 abort 帽（仅 `rss_mb()`/`peak_rss_mb` 披露） | 外挂 30s sampler + 破帽杀停；若 Arch 另钉 wrapper 则以其为准，仍 **≤1500** |
| 对照失败 | 旧跑峰≈3557MB ≫1500（`--window both` + 旧脚本） | 本草案改 lowmem + **单窗 x2** |

## 4. 开跑前检查清单（全部 PASS 才启进程）

1. `pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` → **空**（非空则不开跑，报 Arch/Data/Web）
2. 研究进程：`pgrep -f 'g1g5_on_minus_id_idio_ivol'` → **空**（防双开）
3. **新** `.ok` 现盘且 sha ≠ `725be3e0…`；内容钉脚本 `05bd81ea…`、`rss_limit=1500`、CLI=`HILIQ`+`x2`、采样 `/tmp`
4. 时刻 ∈ **12:30–13:30 ET**（America/New_York）；未过 expires（以 `.ok` 为准）
5. QUIET：若 `.ok`/ops 要求设 `RESEARCH_QUIET.lock` → 设后核 healthz `quiet=true` 再跑；结束/ABORT 须 **lift**
6. MemAvailable 充足（参考前回预检量级）；**不**读大表做「试跑」
7. 静态已核（本回合）：`py_compile` → `/tmp/ai_leaf27_lowmem_hiliq_x2_draft.pyc` **PASS**；未写 research `__pycache__`

## 5. 回执须披露（开跑后；模板另文）

- mktcap / capadv **float32** 存储（IO 布局；相对基线可能边际数值差）
- `_prune_hist`（每~40 日）相对基线可能边际差
- **峰 RSS**（ps + 日志 `rss=` + `run_meta.peak_rss_mb`）
- rc / ET_TS / `.ok` sha / 脚本 sha `05bd81ea…` / 禁复用 VOID `725be3e0` / 产物路径

模板：`docs/v2/audit/AI_LEAF27_LOWMEM_HILIQ_X2_RECEIPT_TEMPLATE_20261025_ZH.md`（状态=TEMPLATE）。

## 6. 本文件边界

| 本文件是 | 本文件不是 |
|---|---|
| cmd/R5c **草案** + 开跑核对表 | **不是** `.ok` / 不是授权 |
| 对齐 Arch `aefa7faa…` 开放条件 | **不**替代 Arch 签发 |
| 等主窗 + Arch 新 `.ok` | **不** UpdateRoutine（除非主令） |

对照只读：ABORT `docs/v2/AI_LEAF27_HILIQ_ABORT_RECEIPT_20261025_ZH.md`；RUN FAIL `docs/v2/AI_LEAF27_HILIQ_RUN_RECEIPT_20261025_ZH.md`；DIFF/COVER/Arch 审阅（上表）。

live=false。
