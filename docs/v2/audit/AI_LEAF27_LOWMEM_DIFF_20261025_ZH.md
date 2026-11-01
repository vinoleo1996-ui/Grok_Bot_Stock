# 叶27 HI_LIQ 降内存 DIFF 包（lowmem v1 · 交 Arch 审）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T11:30:20-04:00（America/New_York）
- **状态**：**DIFF_DRAFT** · 研究级 · **不申 `.ok`** · **不实跑读盘** · **不 git commit**
- **live**=false · **promotion_approved**=false
- **对照失败**：ABORT_RSS_OVER_LIMIT 峰≈**3557MB** ≫ rss_limit **1500**（禁抬帽）

## 0. 钉与旁证（全长 MATCH）

| 项 | 路径 / 值 | sha256 |
|---|---|---|
| 预注册 r1 FROZEN | `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` | `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` |
| Arch 契约预告 | `docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` | `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196` |
| impl pin（旧包） | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` |
| 旧 DIFF patch | `docs/v2/AI_LEAF27_ON_MINUS_ID_IDIO_IVOL_DIFF.patch` | `e2ed0fc88bfe38c07892a3a87d03f9b2372cb8cfd568fd7de9548f3113978b71` |
| 基线脚本（ABORT 实跑） | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` |
| Arch ABORT 旁证 | `docs/v2/audit/ARCH_LEAF27_HILIQ_ABORT_RSS_20261025_ZH.md` | `37b63b8fb98739e86f3d5a0b2542ca3adc9627fe531566efd7082ef02d2e799d` |
| AI 跑回执 FAIL | `docs/v2/AI_LEAF27_HILIQ_RUN_RECEIPT_20261025_ZH.md` | `788a496ca04d12a749f5be8cad5f2a9364c9bbc217fe61a2ed8fdb12769f48df` |
| AI 中止回执 | `docs/v2/AI_LEAF27_HILIQ_ABORT_RECEIPT_20261025_ZH.md` | `5923350ad8519a6593102b621826bb05a5e509808103a6e367ba997879b005ba` |
| 已 VOID `.ok` | `725be3e0…`（禁再消费） | — |
| 叶25 PASS 回执（权威） | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_STEP_M1_R5_V4_RUN_RECEIPT_20261025_ZH.md` | `2bf4745d…` |

## 1. 根因（只读）

实跑日志（`--universe HILIQ --window both`）：

| 日进度 | n | rss |
|---|---|---|
| 2024-08-07 | 1332 | **3030MB**（已≫1500） |
| 2024-11-08 | 2348 | 3295MB |
| 2025-02-11 | 2290 | 3472MB |
| 2025-05-12 | 2553 | **3557MB**（中止） |

判定：**峰值在预载/日环早期已破帽**，LimitPanelCache 全历史 + 嵌套 Python `dict[date][inst]→float`（mktcap≈11.7M 行、capadv≈3.6M 行、mask≈11.7M 行）为主因；日环缓增≈0.5GB。非因子公式问题。

## 2. 本包产物

| 件 | 路径 | sha256 |
|---|---|---|
| **本 DIFF 文** | `docs/v2/audit/AI_LEAF27_LOWMEM_DIFF_20261025_ZH.md` | （以 sha256sum 盘证为准） |
| **封面/闭合** | `docs/v2/audit/AI_LEAF27_LOWMEM_COVER_20261025_ZH.md` | （以 sha256sum 盘证为准） |
| **草案脚本** | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| **unified diff**（相对基线 `7a5f756c…`） | `docs/v2/audit/AI_LEAF27_LOWMEM_V1_20261025.diff` | `2154b6fb60fa448da10e0eba620fa22096051d6d41cad69dbd8e02cc37ec055f` |

静态：`py_compile` PASS（`/tmp`）；`/tmp/leaf27_lowmem_venv` **pyflakes** PASS；`--dry-compile-only` OK；**未**写 `__pycache__` 进 repo（已清理误生成）。

## 3. 改动要点（因子定义 / α 符号 / 门控 **零改**）

| # | 方向 | 做法 | 预期 |
|---|---|---|---|
| 1 | 紧凑日表 | 新 `DayFloatMap`：每会话存 `codes[]`+`float32 vals[]`，按需物化单日 `dict`；替代嵌套 Python float | mktcap/capadv 常驻由 ~GB 级对象堆降到数组级 |
| 2 | 市值滑动 | 日环仅保留 ≥T−1 的 mktcap 日；`drop_before` | 长窗不堆全历史 mktcap |
| 3 | 宇宙掩码 | 先按 cal 日期跨度过滤再 groupby | 少持无用年 |
| 4 | LimitPanelCache | `keep_sessions=cal_set`；板价 `float32`；只缓存日历内行 | 砍掉 panel 全历史（主缓增源） |
| 5 | dtype / 增量 α | 日环数组明确 dtype；α 用列 list 而非 `list[DataFrame]` | 降碎片与峰值 |
| 6 | del+gc | 大表加载后 / 每~40 日 prune hist / `run_one` 结束清空 | 窗间释放 |
| 7 | 分窗（ops） | **推荐** `--window x2` 与 `--window sealed` **分进程**；`both` 保留但 WARN+腿间 gc | 对齐 Arch「分窗或分块」 |
| 8 | FULLA | CLI **拒绝** `FULLA|both`（FULLA 仍 GAP） | 与 VOID 授权一致 |
| 9 | rss_limit | **仍 ≤1500**；本包**不**申请抬帽 | 禁抬帽 |

**未改**：`α_raw=−ivol`；β=60/40；W=20/15；残差五步顺序；`limit_policy=exclude_hit_or_unknown`；`target_weight` 暴露；路径/sha 常量钉；HI_LIQ 主路径。

## 4. 旧包 SUPERSEDED（仅 lowmem 路径；因子钉仍有效对照）

| 旧件 | sha256 | 状态 |
|---|---|---|
| 基线脚本 `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` | **SUPERSEDED_FOR_LOWMEM_RUN**（保留只读对照；另窗以 lowmem 草案为准） |
| 旧 DIFF patch | `e2ed0fc88bfe38c07892a3a87d03f9b2372cb8cfd568fd7de9548f3113978b71` | **SUPERSEDED_FOR_LOWMEM**（limit_hit 包仍作历史） |
| impl pin | `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` | 契约钉仍 MATCH；**执行脚本指针**待 Arch 审本包后另文重钉 |
| `.ok` `725be3e0…` | — | **VOID**（已归档；禁复用） |

## 5. MATCH 对照预注册 / Arch 预告

| 检查 | 结果 |
|---|---|
| mechanism_tag `g1g5_ashare_on_minus_id_idio_ivol_v1` | MATCH |
| `α_raw=−ivol` / β60·40 / W20·15 | MATCH（未改常量） |
| 残差顺序 SW→logMV T−1→β→capadv→ivol | MATCH |
| HI_LIQ 主 / FULLA GAP | MATCH（脚本拒 FULLA） |
| Arch 裁：另窗须降内存（分窗/分块）；禁抬帽 | MATCH（本包） |
| 预注册 `f12965da…` / 预告 `31462908…` | MATCH 引用 |

## 6. 非动作 / 请 Arch·主

1. **禁止**本回合申 `.ok` / 实跑 sealed·X2 / 读收益选参 / git commit  
2. 请 **Arch** 审本 DIFF + 草案脚本；通过后 **另窗** 签独立 code_change/run `.ok`（rss≤1500；建议先 `HILIQ --window x2`，sealed 另签或另进程）  
3. 请 **Eng**（可选）：若 Arch 要进一步压 LimitPanel I/O，可协助 panel 列裁/mmap——**非本包阻塞**  
4. Data：无新写；无需 CONT  

live=false。
