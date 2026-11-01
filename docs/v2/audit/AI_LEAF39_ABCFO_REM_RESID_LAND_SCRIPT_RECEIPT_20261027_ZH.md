# 【LAND_SCRIPT 回执 2026-10-27】叶39：异常经营现金流 ABCFO / 真实盈余管理残差 α 正式构建脚本

- **时点**：2026-10-28 00:14:23 America/New_York (ET)
- **主裁**：LAND_SCRIPT GO（Arch FROZEN 只审 `b51a59a0` PASS_WC → 主裁 LAND_SCRIPT ~00:06 ET）
- **本拍角色**：AI 执行器落 **正式构建脚本 + 回执**；**未**真跑全窗 X2；**未**自签 `.ok`；**未** Book-Smoke；**未** git commit；**未** SendToUser / 报 Leo；**未**改 FROZEN/DRAFT/COUNT 字节
- **leo_notify**=false；**live**=false；**promotion**=false；**ok_requested**=false；**EXECUTED_full_alpha**=false（本拍仅静态交付）
- **≠** X2 ACCEPT；**KEEP≠ACCEPT**；COUNT `d0d11598` / 脚本 `20313ba3` **不是**本票主脚本

---

## 1. 交付物

| # | 路径 | sha8 | 说明 |
|---|---|---|---|
| 1 | `research/leaf39_abcfo_rem_resid_alpha_build.py` | **`e99376dd`** | 正式构建脚本（ABCFO 残差 α；C2(a)(b)/C3/C4/C5/C8/C9；§压峰；`--help`+`--dry-compile-only` 默认轻路径） |
| 2 | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_LAND_SCRIPT_RECEIPT_20261027_ZH.md` | （本文件；落盘后以磁盘 sha8 为准） | 本回执 |
| 3 | `/tmp/leaf39_abcfo_rem_resid_alpha_build.pyc` | n/a | `py_compile` 产物（size=72512） |
| 4 | 叶34 Jaccard PIN 附录 JSON | **本拍未估 → PIN_GAP** | CLI `--leaf34-jaccard` 已预留；本拍 dry-only 不读大体量；最迟 X2 前补估 |

**脚本全长 sha256**：`e99376dd71ce889ad7c16e5b6e6e87d3f2058f8f3b1f1e93880bd260eea8806b`

**`research/leaf39*` 列表（本拍）**：
- `research/leaf39_abcfo_rem_resid_alpha_build.py`

---

## 2. 钉 MATCH 表（本机 sha256 前8）

| 项 | 路径 | 期望 sha8 | 盘上 sha8 | 结果 |
|---|---|---|---|---|
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `b51a59a0` | `b51a59a0` | **MATCH** |
| FROZEN | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_20261027_ZH.md` | `150d1a28` | `150d1a28` | **MATCH** |
| RECEIPT FROZEN | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `507f09f1` | `507f09f1` | **MATCH** |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `4a1b4dd0` | `4a1b4dd0` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `542138d6` | `542138d6` | **MATCH** |
| DRAFT RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_RECEIPT_20261027_ZH.md` | `691bbc14` | `691bbc14` | **MATCH** |
| COUNT JSON | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json` | `d0d11598` | `d0d11598` | **MATCH** |
| COUNT 脚本 | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_SCRIPT_20261027.py` | `20313ba3` | `20313ba3` | **MATCH** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | `c5433e80` | **MATCH** |
| dig | `output/d1/DIG_FACTOR_20261027_2330ET.md` | `440410de` | `440410de` | **MATCH** |

**汇总**：**ALL MATCH**

备注：
- dig `440410de`（文内自称 `87f65bbe` **勿采**）
- COUNT 脚本 `20313ba3` = audit 目录计数闸；**非正式 α 构建**；本票主脚本为 `research/leaf39*`
- 叶30 模板只读 `3ee9fed2`（RSS/残差工程）；叶38 模板只读工程 `3a44471d`（**禁**混产品 `c01c2034`/`5f694370`）
- 叶34 正式脚本只读 `482009dc`；exclusion mask 路径钉入 CLI

---

## 3. §压峰清单（对齐叶38 §6.1 + 叶30 r3_peakcut；代码路径可见）

| # | 要求 | 落地 | 代码锚点 |
|---|---|---|---|
| 1 | 流式/分块：按年读 HI_LIQ；`del`+`gc` | **是** | `load_hiliq_mask_by_chunks`；fundamentals 分表读后释放 |
| 2 | logmv 懒加载：再平衡日 T-1 | **是** | `_load_logmv_t1` per rebal；`after_logmv_rebal_*` |
| 3 | 单线程：禁并行 worker 叠 RSS | **是** | `OMP/MKL/OPENBLAS/NUMEXPR/VECLIB=1`；`enforce_single_thread()` |
| 4 | 超限硬 ABORT；rss=1500 **禁抬** | **是** | `check_rss` → **Exit 94**（soft/split）/ **Exit 95**（hard）；`--rss-limit-mb` >1500 → STOP |
| 5 | peak_proof≤1500 REQUIRED；无则不得申 `.ok` | **是** | dry payload `peak_proof_required` 标签列表；实跑 `final_peak_proof`；本拍**不**申 `.ok` |
| 6 | 默认轻路径 | **是** | `--dry-compile-only` / `--help`；无授权拒重路径 |

Exit 码对齐叶38/37习惯：**94**=soft/split ABORT；**95**=hard ABORT。

---

## 4. 机制摘要（对照 FROZEN `150d1a28`；未改条款）

- **mechanism**=`g1g5_ashare_abcfo_rem_resid_v1`
- **PRIMARY**=日度**残差 α 向量** parquet（**非** Top-N；**非** exclusion mask 主交付）
- **公式**：YTD→单季后 CFO/A ~ 1/A + S/A + ΔS/A（**再平衡日截面 SW L1 OLS APPROX**；C2(a) **不升**年×行业面板；不重跑 COUNT）→ ABCFO=ε → `α ∝ −ε` → SW L1 demean + vs log 流通市值 OLS
- **掩码**：银行 `801780.SI` / 房地产 `801180.SI` / 非银 `801790.SI` + HI_LIQ（`c5433e80`）
- **PIT**：`available_at ≤ t`；禁偷看
- **硬闸**：vs 叶19/25/30 Jaccard ∨ **正式 ρ_excess** >0.5 拒（C2(b)：Spearman 仅门控；`--skip-rho-excess` 默认 True；X2 前 `--no-skip-rho-excess`）
- **C3**：vs 叶34 exclusion Jaccard **PIN**；CLI `--leaf34-jaccard`；硬拒 0.5；**勿改 PRIMARY**
- 窗意向 2024-06-03→2026-10-09；再平衡 20；成本 30bp（评价；本拍不读收益选阈）
- KEEP≠ACCEPT；decay 近端 252d（脚本不执行衰减门）
- **C5** CRR_MOD2/IO **不升** PRIMARY；**C9** COUNT ≠ X2 ACCEPT

工程骨架仅借鉴叶30 r3 / 叶38 的 RSS/peak_proof/ABORT 路径；**未**拷 CRR 公式；**未**拷 exclusion overlay 主逻辑；**未**触 RESTORED `f08ce32c`/`335635dd`；**未**混 fund `ba7609af`/`fbc1bd9a`；**未**混叶38 `c01c2034`/`5f694370`。

---

## 5. C2 / C3 本拍状态

| 条件 | 本拍 |
|---|---|
| **C2(a)** | 维持截面 SW L1 OLS APPROX；**不升**面板；**不重跑** COUNT `d0d11598` |
| **C2(b)** | 正式 ρ_excess **路径已钉**（`formal_rho_excess_stub` + `--skip-rho-excess`/`--no-skip-rho-excess`）；本拍 dry **未**跑；X2 前须开 |
| **C3** | **PIN_GAP（诚实）**：本拍 dry-only 未估叶34 Jaccard；CLI `--leaf34-jaccard` 已实现；硬拒 0.5；禁事后改 PRIMARY；最迟 X2 前补估 |
| **C4** | 禁自签/自开；不混 fund/叶38；rss≤1500；禁 RESTORED — **已遵守** |
| **C5** | 备选不升 PRIMARY — 入钉 |
| **C8** | PRIMARY=残差 α 向量 — 入钉 |
| **C9** | 计数 ≠ ACCEPT — 入钉 |

---

## 6. 静态门（本拍执行）

| 检查 | 结果 |
|---|---|
| `pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'` | **empty OK** |
| `pyflakes research/leaf39_abcfo_rem_resid_alpha_build.py` | **clean (exit 0; 无告警)**（`/workspace/qlvenv/bin/pyflakes`） |
| `py_compile` → `/tmp/leaf39_abcfo_rem_resid_alpha_build.pyc` | **PASS**（size=72512） |
| `--dry-compile-only` | **exit 0**；打印 pins JSON；**ZERO** 大表加载 |
| `--help` | **PASS**（argparse 骨架完整） |
| 真跑全窗 X2 / 读收益选阈 | **未做**（本拍只写脚本静态；EXECUTED_full_alpha=false） |
| 自签 `.ok` | **未做** |
| 触 fund MDD HOLD / 叶38 产物 | **未做** |
| 改 FROZEN/DRAFT/COUNT/Arch 审文 | **未做**（字节未改） |
| git commit | **未做** |

---

## 7. 禁项再钉（已遵守）

- 禁自签 `.ok` / 禁自开 X2 / Book-Smoke / 禁挂 QUIET
- 禁 RESTORED `f08ce32c` / `335635dd`
- 禁混 fund MDD HOLD `ba7609af`/`fbc1bd9a`；禁混叶38 `c01c2034`/`5f694370`
- 禁抬 rss>1500；无 peak_proof≤1500 不得申 `.ok`（本拍亦不申）
- 禁把 COUNT gate_pass 当 X2 ACCEPT；禁 KEEP 解阻 ACCEPT
- 禁把 CRR_MOD2/IO 升 PRIMARY；禁事后改 PRIMARY 救闸
- 禁改 FROZEN `150d1a28` / DRAFT `542138d6` / COUNT `d0d11598` 字节

---

## 8. 状态机 / 下一跳

```
PREREG_FROZEN 150d1a28
  → Arch FROZEN 只审 b51a59a0 PASS_WC
    → 【本拍】LAND_SCRIPT 正式脚本 research/leaf39* sha8=e99376dd
      → 【下一跳】请主 → Arch **另窗只审脚本**（禁顺带审 X2 / 禁自签 .ok）
        → 通过后独立新窗 .ok + X2
           （须 peak_proof≤1500 + 正式 ρ_excess + 叶34 Jaccard + decay KEEP；KEEP≠ACCEPT）
```

**请主 Agent**：将本回执 + 脚本路径交 **Arch 另窗只审脚本**（script-only review）。本拍 AI **不**自派 Arch、**不**自签、**不**开 X2。

---

## 9. 冻结对照

| 项 | 值 |
|---|---|
| 脚本 | `research/leaf39_abcfo_rem_resid_alpha_build.py` |
| 脚本 sha8 | `e99376dd` |
| FROZEN | `150d1a28` MATCH |
| Arch FROZEN 审 | `b51a59a0` MATCH |
| RECEIPT FROZEN | `507f09f1` MATCH |
| COUNT | `d0d11598` MATCH（未改） |
| mechanism | `g1g5_ashare_abcfo_rem_resid_v1` |
| C3 叶34 Jaccard | **PIN_GAP**（CLI 已预留） |
| §压峰 | 全套可见 |
| live / promotion / ok_requested / EXECUTED_full_alpha | false / false / false / false |
| leo_notify | false |

**本文件状态**：**LAND_SCRIPT_RECEIPT**（≠ `.ok`；≠ X2 ACCEPT；≠ QUIET）。
