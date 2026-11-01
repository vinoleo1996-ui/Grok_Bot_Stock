# AI 回执：叶31 Amihud 冲击慢 α 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 02:26 ET**（America/New_York；ISO `2026-10-27T02:26:17-0400`） |
| 主令 | ~02:19 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`7a6a1e1a` MATCH**；FROZEN sha8 **`bcbec955` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（写前/后 `pgrep` 重进程空） |

## 0. 一句话

新脚本 sha8 **`08f37fd2`** 已落；钉 FROZEN **`bcbec955`** / Arch **`7a6a1e1a`**；mechanism=`g1g5_ashare_amihud_impact_slow_v1`；W/再平衡=20/20；α=`−rank`；再平衡日懒加载日频 bars（吸取叶30 peak 教训）；overlap vs 19/25/27/30；rss=1500+peak_proof；forbid 四票；`0087c928` 另队。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf31_amihud_impact_slow_alpha_build.py` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **`08f37fd2`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `e736a03349cf6bac7ea8ae726f26cedc43619b8185dbc8d59c25b16758935978` | **`e736a033`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `37443b02ac526ee5a52d9483f40cc90e43318309b4a78d10c937b6f3dd0e0cbc` | **`37443b02`** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `6c47e185272a6749881ae554f36bf06b1672250cc182e2f73d1f9b8dfab03e04` | **`6c47e185`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_20261027_ZH.md` | — | **`bcbec955`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`7a6a1e1a`** |
| 模板（只读未改） | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | — | **`3ee9fed2`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_amihud_impact_slow_v1`
- `alpha_sign` = `neg_rank_impact_resid`；`ic_sign_expected` = **positive**（注释钉；脚本不算 IC）
- `amihud_W`=20 / `rebal_every_td`=20 / `amihud_min_valid`=15
- 残差：SW L1 demean → OLS(logmv T−1, mom20, vol20, logADV20)；style 源=`derived_from_daily_bars_W20`（钉死；禁事后换 capacity_adv）
- amount：tushare daily 千元 ×1000 → 元；adj=`data/v2/adj/adj_factor_2023h2plus.parquet`
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf31_amihud_`
- forbid ok sha8：`aa25e989`,`7e239487`,`5af20222`,`5ae077fa`
- `primary_load`=`rebal_day_lazy_bars`；peak_proof REQUIRED
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf31_amihud_impact_slow_alpha_build.py', cfile='/tmp/leaf31.pyc', doraise=True)"
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）  
`--universe FULLA` dry → STOP PRIMARY（exit 2）

## 3. 对照 Arch CONDITIONS（`7a6a1e1a` §3）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`08f37fd2`**；钉 FROZEN `bcbec955` |
| **C3** 重叠 | **已预留** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30.json`；Jaccard≥0.7 exit 4；ρ>0.5 强度过滤 |
| **C4** 残差清单 | **已写死** | SW L1 + logmv + mom20/vol20/logADV20；缺列 PIN_GAP/硬失败 |
| **C5** 双轨 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research` 可选；`--universe FULLA` STOP |
| **C6** decay KEEP | **仅钉** | 不在本脚本跑闸；注释/FROZEN 引用 |
| **C7** forbid 四票 | **入钉** | `FORBID_OK_SHA8` + 真跑校验 |
| **C8** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` 阶段性 peak_proof |
| **C9** `0087c928` | **另队** | 常量 `LEAF30_KEEP_REPAIR_SHA8_SEPARATE`；未并入 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**并入叶30 KEEP `0087c928`；**未** RESTORED 四票
- `live=false`；`promotion_approved=false`；**不推 Leo**；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 08f37fd2（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED 四票；禁复用叶25/27/30）
          → X2（完整 Amihud α + overlap 重算 + decay KEEP 硬验收）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 正文（§0–§5）sha256 / sha8 | `6cf8868fa715e3d17e1322dcb034275bdc12a36cdacc86d9da1c7242475c24bb` / **`6cf8868f`** |
| 脚本 sha8 | **`08f37fd2`** |
| COVER / CMD / DIFF sha8 | **`e736a033`** / **`37443b02`** / **`6c47e185`** |

**EXECUTED=false** · **leo_notify=false** · **live=false**
