# AI 回执：叶35 ETF 被动压力 overlay 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 13:26 ET**（America/New_York；ISO `2026-10-27T13:26:18-04:00`） |
| 主令 | 2026-10-27 ~13:15 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`5a082d18` MATCH**；FROZEN sha8 **`be9fc459` MATCH**；PIN **`dd17044a` MATCH**；RECEIPT **`132ba6f1` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；py_compile **PASS**；pyflakes **PASS**；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（本拍只落脚本） |

## 0. 一句话

新脚本 sha8 **`25ae4572`** 已落；钉 FROZEN **`be9fc459`** / RECEIPT **`132ba6f1`** / Arch **`5a082d18`** / PIN **`dd17044a`**；mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**；soft-penalty 非 PRIMARY（默认关）；**C3 方案 A**（次月首个交易日 09:00 Asia/Shanghai + 份额 PIT）；**C11≠叶26**；再平衡日懒加载压力；overlap vs moneyflow/26resid/8a/25/27/30–34；rss=1500+peak_proof；forbid `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票；KEEP 不解阻；C12 入钉；`0087c928`/叶28/29 另队；叶33 **`afbbe7e7` UNCHANGED**。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` | **`25ae4572`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `eee0866bb08af9b2bb8acca9dbc1799005fd2c0e0c8d8fc044b4f1290d4c04a4` | **`eee0866b`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `c6d3b9ede7abef7172479205b7a6252f8556629a211046ccdeeb764b41f5220c` | **`c6d3b9ed`** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `dc50390418a18e373bdde712466c356ef57232b3210b088acd6c190d67b1a60f` | **`dc503904`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | — | **`be9fc459`** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | — | **`132ba6f1`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`5a082d18`** |
| PIN C3（只读） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | — | **`dd17044a`** |
| 计数脚本迁仓（只读） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | — | **`4e964d40`** |
| 叶33 正式（只读未改） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | — | **`afbbe7e7` UNCHANGED** |
| 叶34 模板（只读未改） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | — | **`482009dc`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_etf_passive_flow_pressure_overlay_v1`
- `primary_delivery` = **mask_only**；`top_q`=**0.20**；`alpha_sign`=`high_abs_pressure_mask0_exclusion`
- C3 方案 A：`weight_available_at`=次月首个交易日 09:00 Asia/Shanghai；份额 `available_at≤t_ts`；`percent_div100`；禁静默月末 asof
- soft-penalty：**默认关闭非 PRIMARY**；`--enable-soft-penalty` 须 SW+style
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf35_etf_passive_`
- forbid ok sha8：**26** 项含 `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票
- `primary_load`=`rebal_day_lazy_etf_share_x_weight_scheme_A_pit`；peak_proof REQUIRED
- overlap：`moneyflow_resid` + `leaf26_resid`/`leaf8a`（可选 PIN_GAP）+ `leaf25/27/30/31/32/33/34`；leaf26-like raw 诊断不得硬拒
- `keep_does_not_unblock_x2_accept`=true；`count_approx_not_x2_accept`=true
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py', cfile='/tmp/leaf35_build.pyc', doraise=True)"
pyflakes research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）
`--universe FULLA` dry → STOP PRIMARY（exit 2）

## 3. 对照 Arch CONDITIONS（`5a082d18` / C1–C13）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C1** FROZEN 预注册 | 上游已 FROZEN | `be9fc459` MATCH |
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`25ae4572`**；钉 FROZEN `be9fc459` + PIN `dd17044a` |
| **C3** 权重方案 A / 份额 PIT | **入代码** | `_load_weight_pin_scheme_a` + `_pressure_on_day`；禁静默 APPROX |
| **C4** mask-only / soft-penalty | **明示** | PRIMARY=mask_only；soft-penalty 默认关非 PRIMARY |
| **C5** top_q=0.20 | **写死** | `TOP_Q=0.20`；高 `|pressure|`=剔除；禁事后翻 |
| **C6** 双轨 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research`；`--universe FULLA` STOP |
| **C7** 重叠 | **已预留** | `write_overlap_report` → moneyflow/26resid/8a/25/27/30–34；Jaccard≥0.7 exit 4；leaf26-like raw 不得硬拒 |
| **C8** forbid | **入钉** | `FORBID_OK_SHA8` 26 项含 `178e90e9`+`c1b71e64` |
| **C9** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` |
| **C10** 另队 | **遵守** | `0087c928` 常量另队；叶28/29 不夹带 |
| **C11** overlay≠叶26 | **遵守** | 交付 exclusion mask 叠主干；禁完整残差 α / moneyflow 主输入 |
| **C12** APPROX≠ACCEPT | **入钉** | `count_approx_not_x2_accept=true` |
| **C13** decay KEEP | **仅钉** | 三闸+KEEP 不解阻（叶32/34）；本脚本不跑闸 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**并入叶30 KEEP `0087c928`；**未** RESTORED forbid 集
- **未**改 FROZEN / 叶33 `afbbe7e7` / 叶34 模板 `482009dc` / HOLD `45dd87dc` / `178e90e9`
- research 仅新增 leaf35 **构建**脚本（**无** selfcheck）
- `live=false`；`promotion_approved=false`；**不推 Leo**；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 25ae4572（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED 178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票；禁复用叶25/27/30–34）
          → X2（完整 exclusion mask + overlap 重算含 moneyflow/叶26残差/8a/25/27/30–34 + decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 sha8 | **`25ae4572`** |
| COVER / CMD / DIFF sha8 | **`eee0866b`** / **`c6d3b9ed`** / **`dc503904`** |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false**
