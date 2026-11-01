# 【LAND_SCRIPT 回执 2026-10-27】叶38：非标审计意见剔除 overlay 正式构建脚本

- **时点**：2026-10-27 21:07:32 America/New_York (ET)
- **主裁**：LAND_SCRIPT GO（Arch FROZEN 只审 `01753ff4` PASS_WC → 主裁 LAND_SCRIPT）
- **本拍角色**：AI 执行器落 **正式构建脚本 DRAFT + 回执**；**未**真跑 X2；**未**自签 `.ok`；**未**挂 QUIET；**未** Book-Smoke；**未** git commit；**未** SendToUser / 报 Leo
- **leo_notify**=false；**live**=false；**promotion**=false；**ok_requested**=false；**EXECUTED**=false（本拍仅静态交付）
- **≠** X2 ACCEPT；**KEEP≠ACCEPT**；COUNT `ba34da2a` **不是**本票主脚本

---

## 1. 交付物

| # | 路径 | sha8 | 说明 |
|---|---|---|---|
| 1 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` | **`d5cf50bb`** | 正式构建脚本（含 §6.1 全套 / mask pipeline / pins / `--help`+`--dry-compile-only` 默认轻路径） |
| 2 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_LAND_SCRIPT_RECEIPT_20261027_ZH.md` | （本文件；落盘后以磁盘 sha8 为准） | 本回执 |
| 3 | `/tmp/leaf38_audit_nonstd_exclusion_overlay_alpha_build.pyc` | n/a | `py_compile` 产物（size=65994） |

**脚本全长 sha256**：`d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263`

**`research/leaf38*` 列表（本拍）**：
- `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py`

---

## 2. 钉 MATCH 表（本机 sha256 前8）

| 项 | 路径 | 期望 sha8 | 盘上 sha8 | 结果 |
|---|---|---|---|---|
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `01753ff4` | `01753ff4` | **MATCH** |
| FROZEN | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `ce0eb2ce` | `ce0eb2ce` | **MATCH** |
| RECEIPT FROZEN | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `bb8051bd` | `bb8051bd` | **MATCH** |
| who | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `16c1f70b` | `16c1f70b` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `7c3b8691` | `7c3b8691` | **MATCH** |
| COUNT 盘上 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `e82aefa2` | `e82aefa2` | **MATCH** |
| COUNT 脚本 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `ba34da2a` | `ba34da2a` | **MATCH** |
| JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` | `2b3babb5` | `2b3babb5` | **MATCH** |
| dig | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | `fa973826` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `acba0865` | `acba0865` | **MATCH** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | `c5433e80` | **MATCH** |
| 叶37 B1 模板只读 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` | `32605aca` | `32605aca` | **MATCH** |

**汇总**：**ALL MATCH**

备注：
- COUNT 盘上 `e82aefa2`（文内自称 `7cc317d9` **勿采**）
- dig `fa973826`（文内自称 `a6ddc4ef` **勿采**）
- COUNT 脚本 `ba34da2a` = audit 目录计数闸；**非正式 α 构建**；本票主脚本为 `research/leaf38*`

---

## 3. §6.1 压峰清单（C9 首要；代码路径可见）

| # | 要求 | 落地 | 代码锚点 |
|---|---|---|---|
| 1 | 分进程：overlay mask vs negevent/叶36 Jaccard | **是** | `--jaccard-worker-only` + `_run_jaccard_subprocess`；预落 `excl_pairs.npy`/`mask_pairs.npy` 后父进程 `del excl/mask_by` 再 spawn |
| 2 | 流式/分块：按年/日块读 parquet；`del`+`gc` | **是** | `_load_hiliq_mask_by_chunks(year_chunk=True)`；审计表建 excl 后释放 |
| 3 | 降表示：categorical / int id；紧凑 Jaccard | **是** | `_instrument_vocab`；磁盘 `(YYYYMMDD,inst_id) int32` npy |
| 4 | 单线程：禁并行 worker 叠 RSS | **是** | `OMP/MKL/OPENBLAS/NUMEXPR/VECLIB=1`；`enforce_single_thread()` |
| 5 | 超限硬 ABORT；rss=1500 **禁抬** | **是** | `check_rss` → **Exit 94**（soft/split）/ **Exit 95**（hard）；`--rss-limit-mb` >1500 → STOP |
| 6 | peak_proof≤1500 REQUIRED；无则不得申 `.ok` | **是** | dry payload `peak_proof_required` 标签列表；实跑 `final_peak_proof`；本拍**不**申 `.ok` |

Exit 码对齐叶37习惯：**94**=soft/split ABORT；**95**=hard ABORT。

---

## 4. 机制摘要（对照 FROZEN `ce0eb2ce`；未改条款）

- **mechanism**=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`
- **PRIMARY**=mask-only 负向 exclusion overlay：HI_LIQ 内最新审计意见 `is_non_standard=True` → mask=0；可算其余 mask=1；不可算不进有效集
- **PIT**：`available_at→T1`（严格次一交易日）；键=`ts_code`；禁偷看
- 叠主干 / capacity_adv；**≠**完整多空审计 α 主叶；≠叶36/37/negevent 换皮
- 厚度（运行时披露，不改阈）：median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50
- Jaccard>0.5 vs negevent **或** 叶36 → 硬拒；vs 34/35/37 披露
- 窗意向 2024-06-03→2026-10-09；成本 30bp；HI_LIQ PRIMARY
- KEEP≠ACCEPT；decay 近端 252d（脚本不执行衰减门）

工程骨架仅借鉴叶37 B1 `32605aca` 的 RSS/peak_proof/ABORT 路径；**未**复用 IMAX 逻辑；**未**触 RESTORED `57ab9096`+`b5be1164`+`4096d401`+…

---

## 5. 静态门（本拍执行）

| 检查 | 结果 |
|---|---|
| `pyflakes research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` | **clean (exit 0; 无告警)** |
| `py_compile` → `/tmp/leaf38_audit_nonstd_exclusion_overlay_alpha_build.pyc` | **PASS**（size=65994） |
| `--dry-compile-only` | **exit 0**；打印 pins JSON；**ZERO** 大表加载 |
| `--help` | **PASS**（argparse 骨架完整） |
| 真跑 X2 / 读大盘 | **未做**（本拍只写脚本静态） |
| 自签 `.ok` | **未做** |
| 触 fund_portfolio / `/tmp/fund_count_rerun*` | **未做**（产物不混） |
| 改 FROZEN/RECEIPT/WHO/COVER/COUNT/Arch 审文 | **未做** |
| git commit | **未做** |

---

## 6. 禁项再钉（已遵守）

- 禁自签 `.ok` / 禁挂 QUIET / 禁自跑 X2 / Book-Smoke / 禁自派 X2
- 禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+…
- 禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`；叶37/36/35 HOLD CLOSED 不回撤
- 禁混 fund_portfolio（WHO/ALLA 附录、`/tmp/fund_count_rerun*` 未动）
- 禁把 COUNT gate_pass 当 X2 ACCEPT；禁 KEEP 解阻 ACCEPT
- 禁抬 rss；无 peak_proof≤1500 不得申 `.ok`（本拍亦不申）

---

## 7. 状态机 / 下一跳

```
PREREG_FROZEN ce0eb2ce
  → Arch FROZEN 只审 01753ff4 PASS_WC
    → 【本拍】LAND_SCRIPT 正式脚本 research/leaf38* sha8=d5cf50bb
      → 【下一跳】请主 → Arch **另窗只审脚本**（禁顺带审 X2 / 禁自签 .ok）
        → 通过后独立新窗 .ok + X2（须 peak_proof≤1500 + 完整重叠 + decay KEEP；KEEP≠ACCEPT）
```

**请主 Agent**：将本回执 + 脚本路径交 **Arch 另窗只审脚本**（script-only review）。本拍 AI **不**自派 Arch、**不**自签、**不**开 X2。

---

## 8. 冻结对照

| 项 | 值 |
|---|---|
| 脚本 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` |
| 脚本 sha8 | `d5cf50bb` |
| FROZEN | `ce0eb2ce` MATCH |
| Arch FROZEN 审 | `01753ff4` MATCH |
| RECEIPT FROZEN | `bb8051bd` MATCH |
| mechanism | `g1g5_ashare_audit_nonstd_exclusion_overlay_v1` |
| §6.1 | 全套可见 |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**本文件状态**：**LAND_SCRIPT_RECEIPT**（≠ `.ok`；≠ X2 ACCEPT；≠ QUIET）。
