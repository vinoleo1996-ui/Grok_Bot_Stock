# 叶25 mem_probe r3 · 滤子类型修补封面（交 Arch 审）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI（执行器） |
| 起草 | `2026-10-25T12:35:23-0400`（America/New_York；墙钟 `2026-10-25 12:35:23 ET`） |
| 状态 | **r3 滤子修补包已落地** · **未申 `.ok`** · **本回合未 `--allow-real-data`** · **未 git commit** |
| live | **false** · promotion_approved **false** |
| 对齐主令 | `docs/v2/audit/MAIN_LEAF25_MEM_PROBE_R2_FAIL_R3_ORDER_20261025_ZH.md` sha **`52aa42c239b6b785a4c01345b7773776cb0a705ffa86a5ef6b4c70938456f6d4`**（sha8 `52aa42c2`） |
| 对齐 Arch 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_FAIL_VOID_R3_RULE_20261025_ZH.md` sha **`6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f`**（sha8 `6ef34f99`） |
| r2 FAIL 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_RUN_RECEIPT_20261025_ZH.md` sha **`d01f95c0b2f5ffa59c56787bfeb09c30c980de6a0f0ce10f10998c4fe3050454`**（sha8 `d01f95c0`） |
| r2 `.ok` | **`cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`** → 已 VOID：`output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.cd230f9c.VOID.FAIL_TYPE.20261025T1232ET.ok` · **禁再消费同票** |
| QUIET | Arch **已 lift**；本包编码 **不需 QUIET**；**勿再挂** |
| 动作本回合 | 新脚本 + DIFF + 本封面 + CMD 草案 + `py_compile`→`/tmp` + pyflakes + schema/dry 静态烟测；**禁自开跑** · **禁申 `.ok`/X2.ok** · **禁抬帽** · **禁 git commit** |

## 0. 目的

落实主令 `52aa42c2…` + Arch 裁定 `6ef34f99…`：r2 实峰因 PIT `end_date` 滤子类型不匹配 FAIL（非破帽）。交付 **r3** 最小类型对齐修（`pd.Timestamp` / schema-aware；禁对 `timestamp[us]` 喂 YYYYMMDD string），交 Arch **另审另签新实峰 probe `.ok`**。本包**不等于**授权开跑；**不解阻 X2**。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | sha256 | 结果 |
|---|---|---|---|
| 主令 r2 FAIL→r3 | `docs/v2/audit/MAIN_LEAF25_MEM_PROBE_R2_FAIL_R3_ORDER_20261025_ZH.md` | `52aa42c239b6b785a4c01345b7773776cb0a705ffa86a5ef6b4c70938456f6d4` | **MATCH** |
| Arch VOID+r3 裁定 | `docs/v2/audit/ARCH_LEAF25_MEM_PROBE_R2_FAIL_VOID_R3_RULE_20261025_ZH.md` | `6ef34f99c78c341bd1c8308100507856b7b7990ffae462abc859cb47f7ddfe3f` | **MATCH** |
| r2 FAIL 回执 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R2_RUN_RECEIPT_20261025_ZH.md` | `d01f95c0b2f5ffa59c56787bfeb09c30c980de6a0f0ce10f10998c4fe3050454` | **MATCH** |
| r2 脚本（对照） | `research/leaf25_full_factor_mem_probe_r2.py` | `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` | 保留；**不**再申 r2 `.ok` |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |
| VOID 原 `.ok` | （已迁 `_consumed/`） | `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279` | **VOID · 禁再消费** |

## 2. 交付物 sha256（全长）

| 件 | 路径 | sha256 | 注 |
|---|---|---|---|
| **mem_probe r3** | `research/leaf25_full_factor_mem_probe_r3.py` | **`8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea`** | **NEW**；滤子+`_norm_pit` 复核 |
| unified DIFF | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_20261025.diff` | **`caec5bde93b17144fdf0faabec4fcb927d9c7681cd1bae4e16803738bbdd2f4f`** | r2→r3 |
| 本封面 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_FILTER_FIX_COVER_20261025_ZH.md` | 以盘 `sha256sum` 为准（落盘后自钉） |
| probe cmd 草案 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_MEM_PROBE_R3_CMD_DRAFT_20261025_ZH.md` | `440930e8ac2cc3ef61e2891cad1683271c8b6ceab10ebd92d4c0035b197b84f7` |
| chunk_plan | `research/leaf25_full_factor_chunk_plan_r1.py` | `e858b32d314b9161a366ffef6661605943061162d707f7b86d01439d35dcdb12` | **UNCHANGED** |
| build stub | `research/leaf25_cfacc_desens_build_r1.py` | `45537fb9294202f10293b8c0c7b57d9ebf95b835f8af23e3ef63a6dc25c47ee3` | **UNCHANGED** |

## 3. 根因与修补（四行摘要）

1. **根因**：`_read_pit_projected` 以 YYYYMMDD **string** 做 `end_date >=`；盘上三表均为 **`timestamp[us]`** → `ArrowNotImplementedError: greater_equal (timestamp[us], string)`（回执 `d01f95c0…`）。
2. **滤子修**：新增 `_end_date_filter_value`——timestamp/date → `pd.Timestamp(end_lo)`（与 `_load_hiliq_chunk_members` 同型）；**仅**当 schema 为 string/large_string 才用 YYYYMMDD；**禁止**对 timestamp 列喂 string 进 pyarrow filters。
3. **注释**：删除「end_date stored as YYYYMMDD string」误导注释；改为 schema-aware 说明并钉 FAIL/Arch sha8。
4. **`_norm_pit` / asof us↔ns**：见 §3.1；门闩另禁复用 VOID `cd230f9c…` 与 step_m1 `1c32ab1e…`。

### 3.1 `_norm_pit` / asof · us vs ns 复核（Arch 清单）

| 位点 | 盘类型 | r3 处理 | 比较侧 | 结论 |
|---|---|---|---|---|
| parquet filter `end_date` | `timestamp[us]` | RHS=`pd.Timestamp`（禁 string） | Arrow 内核 | **对齐**（同 HI_LIQ mask 路径） |
| `_norm_pit` → `end_s` | `timestamp[us]` | `pd.to_datetime` 原生解析 → `dt.normalize()`（本机烟测 dtype=**datetime64[us]**；若环境提升为 ns 亦可）；string 圆径仅 fallback | asof `sort_values(end_s)` | **日粒度一致**；与 `d` 比较在日界，us/ns 午夜无歧义 |
| `_norm_pit` → `avail_sh_date` | `timestamp[us, tz=Asia/Shanghai]` | `to_datetime(..., utc=True)` → `tz_convert(SH)` → naive `normalize()`（烟测 dtype=**datetime64[us]**） | `_asof_value`: `avail_sh_date < d` | **两侧均为 naive 日归一 Timestamp**；`d` 来自 HI_LIQ `pd.Timestamp(...).normalize()`；日比较足够 |
| `_asof_value` | n/a（内存） | 无 merge_asof；布尔掩码 + sort | `d` vs `avail_sh_date`；`end_s` 仅排序 | **无需 us/ns 显式 cast**；日比较足够 |

**未改** asof 语义 / report_type=1 / densify=false / claims_full_cfacc=false / C4 三帽。

## 4. 仍钉（未变）

| 项 | 值 |
|---|---|
| C4 / stop / hard | **1331200 / 1484800 / 1536000** kB；禁抬；≥0.85×C4 → exit 94 |
| 采样 | **仅** `/tmp/quantlab_*` |
| 宇宙/块 | **HI_LIQ** 单块；month 或 rebal_days≤20；禁 `--window both`；FULLA 非本轮实路径 |
| wrapper | v5 sha `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| 禁复用 `.ok` | `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`（step_m1）· `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`（r2 VOID） |
| α 口径 | `crude_accrual_cs_zscore_probe_only`；`claims_full_cfacc=false`；`densify=false`；float32 part |

## 5. 禁项

- **禁**再消费 VOID `.ok` `cd230f9c…` / 任何 CONSUMED footer 变体
- **禁**复用 step_m1 `.ok` `1c32ab1e…`；**禁**申 X2 `.ok`；**禁**本回合申 probe `.ok`
- **禁**自开跑 `--allow-real-data`（至 Arch 新签 + 主另排窗）
- **禁**抬 C4/stop/hard；**禁** `--window both`；**禁**整窗 densify
- **禁**采样写入 `output*`/`data*`；**禁** git commit；**禁** research `__pycache__`
- **禁**再挂 RESEARCH_QUIET（Arch 已 lift；编码不需 QUIET）
- **禁**动叶27 开跑 / RESTORED `8bcd79dc`/`725be3e0`

## 6. 静态检查（本回合）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf25_mem_probe_r3.pyc` | **PASS** |
| pyflakes `leaf25_full_factor_mem_probe_r3.py`（`/tmp/ql_pyflakes_venv`） | **PASS**（rc=0） |
| chunk_plan / stub sha | **UNCHANGED** `e858b32d…` / `45537fb9…` |
| schema-only：三表 `end_date=timestamp[us]` + `_end_date_filter_value` → `pd.Timestamp`（禁 string RHS） | **PASS** |
| `_norm_pit` us 烟测（synthetic timestamp[us] → day-normalize；asof `< d`） | **PASS**（dtype datetime64[us]） |
| dry-run 结构烟测（synthetic cal，HI_LIQ month 2024-06，`/tmp/quantlab_*`，无 `--allow-real-data`） | **PASS** rc=0 |
| `--allow-real-data` 无 `--arch-ok-path` | **STOP** rc=2 |
| research `__pycache__` 新增 r3 | **无** |
| `--allow-real-data` 实读大表 / git commit / 申 `.ok` | **未做** |

## 7. 给 Arch / 主的下一跳

1. **Arch**：审本 r3 包（脚本 `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` + 本封面 + CMD + DIFF）；通过后**另签独立实峰 probe `.ok`**（钉 wrapper v5 / C4 / `/tmp` / HI_LIQ 单块 / 禁 `cd230f9c`/`1c32ab1e` / `ai_no_retry`）。**勿**复活 VOID 票。
2. **主**：另排实峰短窗；与叶27 拟窗互斥 QUIET。
3. **AI**：等新 `.ok` + 入窗后再 `--allow-real-data`；回执披露 float32 / densify=false / peak_kb / `claims_full_cfacc=false`；**勿**申 X2 `.ok`。

live=false；promotion_approved=false。
