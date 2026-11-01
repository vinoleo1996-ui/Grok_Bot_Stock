# AI 回执：叶30 CRR 正式 α 构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-26 17:50 ET**（America/New_York；墙钟 `2026-10-26 17:50:15 EDT`） |
| 主令 | ~17:45 ET 另窗只写正式构建脚本；Arch 预注册 **PASS_WITH_CONDITIONS** sha8 **`f61ffb05` MATCH**；FROZEN sha8 **`93cad965` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**触 A18 |
| HOLD | **否**（写前 `pgrep` 重进程空；MemAvailable≈7.0Gi >3Gi） |

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r1.py` | `b903756fddf152814e617358c242a3e991dc955217dba62eaa704a7b30f3830b` | **`b903756f`** |
| 本回执 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_SCRIPT_RECEIPT_20261026_ZH.md` | （见 §6） | （见 §6） |
| FROZEN（只读） | `docs/v2/AI_LEAF30_CRR_CFOOE_VOLPEN_WHO_PAYS_FROZEN_20261026_ZH.md` | — | **`93cad965`** |
| Arch 预注册审（只读） | `docs/v2/audit/ARCH_LEAF30_CRR_WHO_PAYS_PREREG_REVIEW_20261026_ZH.md` | — | **`f61ffb05`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_crr_cfooe_volpen_v1`
- `lambda_frozen` = **1.0**；`ic_sign_expected` = **positive**（注释钉；脚本不算收益）
- `approx` = **false**（主交付禁 ocf_to_profit；计数 APPROX 仅 GAP 提及）
- `crr_L`=16 / `crr_min_q`=12；`vol_win`=8 / `vol_min`=6
- 行业硬排除：`801780.SI` / `801180.SI` / `801790.SI`（`801230` 不掩）
- 窗：`2024-06-03 → 2026-10-09`；再平衡每 20 交易日；PRIMARY HILIQ×x2；FULLA → STOP
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf30_crr_`
- forbid ok sha8 含：`3c297052`,`e107383f`,`2be59acd`,`1c32ab1e`,`ebc673bf`,`6de02e74` 等
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute; wait Arch script review → new X2 .ok`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf30_crr_cfooe_volpen_alpha_build_r1.py', cfile='/tmp/leaf30_crr_build.pyc', doraise=True)"
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_cfooe_volpen_alpha_build_r1.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`

## 3. 对照 Arch C1–C5

| Cond | 本拍 | 证据 |
|---|---|---|
| **C1** 正式构建脚本 | **已写** | 上表脚本 sha8 **`b903756f`** |
| **C2** 禁 ocf 主源 | **遵守** | 主读 `financials_pit_tushare.operate_profit` + `cashflow_pit_tushare.n_cashflow_act`；`claims.ocf_to_profit_main=false`；读路径硬拒 `ocf_to_profit*` |
| **C3** 重叠预留 | **已预留** | `write_overlap_report` + CLI `--overlap-report` / 真跑默认写 `overlap_vs_leaf19_25.json`；注释钉计数抽样≠正式重叠；Jaccard≥0.7 硬拒 / ρ>0.5 强度过滤 |
| **C4** mom/vol/ADV 不强制 | **未静默加** | 残差最低集 = SW L1 demean + logmv OLS（对齐 FROZEN §3） |
| **C5** 错开 A18 | **遵守** | 写脚本时**零**大表加载；未触 A18 EXEC `.ok` sha8 **`6de02e74`**；无重进程；forbid 含 `6de02e74` |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大财务表探索；仅 `pq.read_schema` 核列名 + dry-compile
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**动 A18；叶26 **不交审**；叶28/29 **仍 FROZEN**
- `live=false`；`promotion_approved=false`；**不推 Leo**

## 5. 下一跳（请主）

```
脚本 b903756f（本回执）
  → 主令 Arch 审脚本
      → 另窗独立 X2 .ok（禁复用叶25；避 A18；≠APPROX）
          → X2（完整 16 季 OP CRR + vol_pen）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF30_CRR_ALPHA_BUILD_SCRIPT_RECEIPT_20261026_ZH.md` |
| 正文（§1–§5）sha256 / sha8 | `04dfd0f9a4bdb27939d78a43a1c20351516e694ed78265a91474811b258e9069` / **`04dfd0f9`** |
| 脚本 sha8 | **`b903756f`** |

live=false.
