# AI 回执：叶32 净融资流入强度残差慢 α 正式构建脚本已写（禁 execute）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 04:09 ET**（America/New_York；ISO `2026-10-27T04:09:08-0400`） |
| 主令 | ~03:57 ET；Arch FROZEN 只审 **PASS_WITH_CONDITIONS** sha8 **`7c0d864f` MATCH**；FROZEN sha8 **`6b8de5e9` MATCH** |
| **结论** | **SCRIPT_WRITTEN**；`--dry-compile-only` **PASS**（exit 0）；**未** `--allow-real-data` / **未** `--execute` / **未**加载大表 / **未**申 `.ok` / **未**挂 QUIET |
| HOLD | **否**（写前/后 `pgrep` 重进程空） |

## 0. 一句话

新脚本 sha8 **`4e0f3c00`** 已落；钉 FROZEN **`6b8de5e9`** / RECEIPT **`7623ce8c`** / Arch **`7c0d864f`**；mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；W/再平衡=20/20；α=`−rank(flow_resid)`；再平衡日懒加载 margin+float+bars（吸取叶30/31 peak 教训）；overlap vs 19/25/27/30/31+margin_delta；rss=1500+peak_proof；forbid 六票；`0087c928` 另队。**交主→Arch 只审脚本**。EXECUTED=false。

## 1. 产出钉

| 件 | 路径 | sha256（全长） | sha8 |
|---|---|---|---|
| 正式构建脚本 | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **`4e0f3c00`** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `b269aec512b826f74384106d3313f85c4e2f69b18f1fac370171b2244201818a` | **`b269aec5`** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `53002ae3860b64e79f52455f13fc046ae5baa5302ec079d46ef0410e78e7067f` | **`53002ae3`** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `264d01596154c71923f17fa4b0106db661daf29f95f19e9ccddbf1e91256b294` | **`264d0159`** |
| FROZEN（只读） | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` | — | **`6b8de5e9`** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | — | **`7623ce8c`** |
| Arch FROZEN 审（只读） | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | — | **`7c0d864f`** |
| 模板（只读未改） | `research/leaf31_amihud_impact_slow_alpha_build.py` | — | **`08f37fd2`** |

## 2. dry-compile 关键 pins

- `mechanism_tag` = `g1g5_ashare_margin_net_flow_resid_v1`
- `alpha_sign` = `neg_rank_flow_resid`；`ic_sign_expected` = **positive**（注释钉；脚本不算 IC）
- `flow_W`=20 / `rebal_every_td`=20 / `flow_min_valid`=15
- 残差：SW L1 demean → OLS(logmv T−1, mom20, vol20, logADV20)；style 源=`derived_from_daily_bars_W20`（钉死；禁事后换 capacity_adv）
- 主输入：`net_rz=rzmre−rzche`；`flow_raw=mean_W(net_rz/float_mktcap_T−1)`；PIT=`available_at`
- 窗：`2024-06-03 → 2026-10-09`；PRIMARY HILIQ×x2；FULLA 仅 `--also-fulla-research`
- `rss_limit_mb`=1500；`sampler_prefix`=`/tmp/quantlab_leaf32_margin_flow_`
- forbid ok sha8：`4bb141c9`,`fdbaa512`,`aa25e989`,`7e239487`,`5af20222`,`5ae077fa`
- `primary_load`=`rebal_day_lazy_margin_float_bars`；peak_proof REQUIRED
- overlap：`leaf19/25/27/30/31` + `margin_delta`（weight 口径）
- dry 声明：`dry-compile-only; ZERO big-table load; NOT authorized to execute`

验证命令（已跑）：

```
python3 -c "import py_compile; py_compile.compile('research/leaf32_margin_net_flow_resid_alpha_build.py', cfile='/tmp/leaf32.pyc', doraise=True)"
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --dry-compile-only
```

无授权 flag 时 STOP（已抽检）：`STOP: missing authorization flags ...`（exit 2）  
`--universe FULLA` dry → STOP PRIMARY（exit 2）

## 3. 对照 Arch CONDITIONS（`7c0d864f` §3 / C1–C9）

| Cond | 本拍 | 证据 |
|---|---|---|
| **C2** 正式构建脚本 | **已写** | 脚本 sha8 **`4e0f3c00`**；钉 FROZEN `6b8de5e9` |
| **C3** 重叠 | **已预留** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30_31_margin_delta.json`；Jaccard≥0.7 exit 4；ρ>0.5 强度过滤；margin_delta 缺→PIN_GAP exit 3 |
| **C4** 残差清单 | **已写死** | SW L1 + logmv + mom20/vol20/logADV20；缺列 PIN_GAP/硬失败 |
| **C5** 双轨 | **遵守** | PRIMARY=HILIQ；`--also-fulla-research` 可选；`--universe FULLA` STOP |
| **C6** decay KEEP | **仅钉** | 三闸注释/meta；本脚本不跑闸 |
| **C7** forbid 六票 | **入钉** | `FORBID_OK_SHA8` + 真跑校验 |
| **C8** rss/peak | **入钉** | 1500 硬 ABORT + `check_rss` 阶段性 peak_proof |
| **C9** `0087c928` | **另队** | 常量 `LEAF30_KEEP_REPAIR_SHA8_SEPARATE`；未并入 |

## 4. 未执行声明（硬）

- **未**带 `--allow-real-data` / `--arch-ok-path` / `--execute` 跑真构建
- **未** `pd.read_parquet` 大表探索（dry 零加载；仅 schema 列名只读）
- **未** X2 / selfcheck / Book-Smoke
- **未**自申任何 `.ok`；**未**挂/抬 QUIET
- **未**并入叶30 KEEP `0087c928`；**未** RESTORED 六票
- **未**改 FROZEN / 叶31 脚本 / 叶30 构建
- `live=false`；`promotion_approved=false`；**不推 Leo**；**≠X2 ACCEPT**

## 5. 下一跳（请主）

```
脚本 4e0f3c00（本回执）
  → 主令 Arch 只审脚本
      → 另窗独立 X2 .ok（禁 RESTORED 六票；禁复用叶25/27/30/31）
          → X2（完整 margin-flow α + overlap 重算含 vs margin_delta + decay KEEP 硬验收）
```

live=false.

## 6. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` |
| 正文（§0–§5）sha256 / sha8 | `75f7a5f3209a59077fabfeef7bdbdff62e19e2f8c55942ea698257d69844f3c1` / **`75f7a5f3`** |
| 脚本 sha8 | **`4e0f3c00`** |
| COVER / CMD / DIFF sha8 | **`b269aec5`** / **`53002ae3`** / **`264d0159`** |

**EXECUTED=false** · **leo_notify=false** · **live=false**
