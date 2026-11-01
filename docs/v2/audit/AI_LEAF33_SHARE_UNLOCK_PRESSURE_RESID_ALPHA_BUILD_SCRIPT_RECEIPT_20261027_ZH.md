# AI 回执：叶33 限售解禁压力残差慢 α 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 06:13 ET**（America/New_York；ISO `2026-10-27T06:13:30-04:00`） |
| 主令 | ~06:04 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`bf5234a9` MATCH**；FROZEN sha8 **`8ed43721` MATCH**；PIN **`4e17ccfc` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（本拍只落脚本） |

## 0. 一句话

新脚本 sha8 **`05c45917`** 已落；钉 FROZEN **`8ed43721`** / RECEIPT **`8f43e2f8`** / Arch **`bf5234a9`** / PIN **`4e17ccfc`**；mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；C3=(a)+加价；H/H_back/W/rebal=20/5/20/20；α=`−rank(pressure_resid)`；再平衡日懒加载 share_float+close+mktcap+bars；overlap vs 19/25/27/30/31/32+margin_delta/hk_hold/moneyflow；rss=1500+peak_proof；forbid `5774bb6e`+二十票；KEEP 不解阻；`0087c928`/叶28/29 另队。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` | **`05c45917`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `8f7504a2dce4b92027e330300ac92fce56d5175a84d18bba5ab3c18de506ee68` | **`8f7504a2`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `ccdb18d7a316b884b4b1f6403d36b9435e076757a10ed791c46e2257793735b2` | **`ccdb18d7`** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `78878272e1f0c393a174f8cf7da4386fc39c9ba17bc0d4880c87b37d5dbc538d` | **`78878272`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | — | **`8ed43721`** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | — | **`8f43e2f8`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`bf5234a9`** |
| PIN（只读） | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | — | **`4e17ccfc`** |
| 模板（只读未改） | `research/leaf32_margin_net_flow_resid_alpha_build.py` | — | **`4e0f3c00`** |
| 模板2（只读未改） | `research/leaf31_amihud_impact_slow_alpha_build.py` | — | **`08f37fd2`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_share_unlock_pressure_resid_v1`
- `alpha_sign` = `neg_rank_pressure_resid`；`ic_sign_expected` = **positive**（注释钉；脚本不算 IC）
- `pressure_H/H_back/W`=20/5/20；`rebal_every_td`=20；`pressure_min_valid`=15
- C3 公式钉：`unlock_mv=sum(float_share*close_T-1); unlock_raw=unlock_mv/float_mktcap_T-1; pressure_raw=mean_W(unlock_raw)`；`ban_float_ratio_primary=true`
- `close_col_pinned`=`close`（`unadjusted_close_cny_per_share`）；禁事后改 adj
- 残差：SW L1 demean → OLS(logmv T−1, mom20, vol20, logADV20)；style 源=`derived_from_daily_bars_W20`
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf33_share_unlock_`
- forbid ok sha8：**21** 项含 `5774bb6e`+二十票
- `primary_load`=`rebal_day_lazy_share_float_close_mktcap_bars`；peak_proof REQUIRED
- overlap：`leaf19/25/27/30/31/32` + `margin_delta` + `hk_hold` + `moneyflow`
- `keep_does_not_unblock_x2_accept`=true
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf33_share_unlock_pressure_resid_alpha_build.py', cfile='/tmp/leaf33_build.pyc', doraise=True)"
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）  
`--universe FULLA` dry → STOP PRIMARY（exit 2）

## 3. 对照 Arch CONDITIONS（`bf5234a9` / C1–C10）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C1** FROZEN 预注册 | 上游已 FROZEN | `8ed43721` MATCH |
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`05c45917`**；钉 FROZEN `8ed43721` + PIN `4e17ccfc` |
| **C3** float_ratio PIN | **(a)+加价入代码** | `C3_FORMULA_PIN` + close=`close`；禁 float_ratio 主路径 |
| **C4** 重叠 | **已预留** | `write_overlap_report` → vs 19/25/27/30/31/32+margin_delta/hk_hold/moneyflow；Jaccard≥0.7 exit 4；ρ>0.5 强度；缺→PIN_GAP |
| **C5** 残差清单 | **已写死** | SW L1 + logmv + mom20/vol20/logADV20；缺列 PIN_GAP |
| **C6** 双轨 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research` 可选；`--universe FULLA` STOP |
| **C7** decay KEEP | **仅钉** | 三闸+KEEP 不解阻注释/meta；本脚本不跑闸 |
| **C8** forbid | **入钉** | `FORBID_OK_SHA8` 21 项含 `5774bb6e`；真跑校验 |
| **C9** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` 阶段性 peak_proof |
| **C10** 另队 | **遵守** | `0087c928` 常量另队；叶28/29 不夹带 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载；仅 schema 列名只读）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**并入叶30 KEEP `0087c928`；**未** RESTORED `5774bb6e`+二十票
- **未**改 FROZEN / 叶32 `4e0f3c00` / 叶31 `08f37fd2` / `3ee9fed2` / `dcf6b559`
- `live=false`；`promotion_approved=false`；**不推 Leo**；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 05c45917（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED 5774bb6e+二十票；禁复用叶25/27/30/31/32）
          → X2（完整 share-unlock α + overlap 重算含 vs leaf32/margin_delta/hk_hold/moneyflow + decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 sha8 | **`05c45917`** |
| COVER / CMD / DIFF sha8 | **`8f7504a2`** / **`ccdb18d7`** / **`78878272`** |

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false**
