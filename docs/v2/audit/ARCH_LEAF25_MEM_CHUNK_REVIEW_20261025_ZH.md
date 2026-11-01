# Arch 审阅：叶25 全叶 MEM 分块估算

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器） |
| 时刻 | `2026-10-25T11:51:13-04:00`（America/New_York；墙钟 `2026-10-25 11:51:13 ET`） |
| **结论** | **NEED_MEM_PROBE** |
| 动作本回合 | **不签 `.ok`** · **不实跑**真数据 · live=false · promotion_approved=false |
| 审对象 | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` |
| 禁复用 | step_m1 `.ok` `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0`（CONSUMED） |
| rss | C4/stop/hard **1331200 / 1484800 / 1536000** kB；**禁抬帽** |
| 叶27 | 本审不碰叶27 `.ok` / 不改其窗 |

## 0. 一句话结论

MEM 分块**策略方向合格**（example 标注清晰、C4 对齐、禁抬帽、强制分块、wrapper v5/`/tmp`、对照叶27 ABORT），**但不足以单独支撑「X2 实跑独立 `.ok`」的内存键签发**：全叶峰值外推未标定，且 build/分块脚本仍 stub。**必须先**另签 **mem_probe 小窗**（dry/单块小样本）校准峰后再签 X2 实跑 `.ok`。

## 1. 输入 sha256 核对（全长）

| 件 | 路径 | 期望 / 报称 | 盘证 | 结果 |
|---|---|---|---|---|
| MEM | `docs/v2/audit/leaf25_step_m1/AI_LEAF25_FULL_FACTOR_MEM_ESTIMATE_CHUNK_20261025_ZH.md` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | 同左 | **MATCH** |
| r6 FROZEN 戳记 | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_FROZEN_20261025_ZH.md` | （以盘为准） | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **盘证** |
| r6 基盘 DRAFT | `docs/v2/AI_LEAF25_FULL_FACTOR_PREREG_r6_DRAFT_20261025_ZH.md` | `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` | 同左 | **MATCH** |
| 全叶窗草案 | `docs/v2/AI_LEAF25_FULL_FACTOR_WINDOW_DRAFT_20261025_ZH.md` | 报称 `994324c9…` | `994324c9ad0c4cc10d2f24426ed9375ca6ec79bf3ca191aa9d53409d00eab002` | **MATCH** |
| step_m1 回执 | `…/AI_LEAF25_STEP_M1_R5_V4_RUN_RECEIPT_20261025_ZH.md` | `2bf4745d…` | `2bf4745d9f01a192738362aa8ccaa30957ea2d3a83b1348d612894f7df7457a4` | **MATCH** |
| Arch consume | `…/ARCH_LEAF25_STEP_M1_R5_V4_CONSUMED_20261025_ZH.md` | `9c96bf35…` | `9c96bf351ef6e6e69b127ef9e308569e01f574dd5840588866239a842473c838` | **MATCH** |
| wrapper P2 审 | `…/ARCH_LEAF25_WRAPPER_SAMPLER_TMP_ONLY_REVIEW_20261025_ZH.md` | `964cf57b…` | `964cf57be56e8723fcff79ba620c5034e18b6e0fe083f59bef939e5db4705f78` | **MATCH** |
| wrapper v5 | `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` | `4240ce82…` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | **MATCH** |

## 2. 审阅要点裁定

| # | 要点 | 裁定 | 说明 |
|---|---|---|---|
| 1 | MEM 是否足以支撑「X2 独立 `.ok`」内存键 | **不足（挡签实跑）** | 策略键（C4 三帽、禁抬、强制分块、wrapper v5、`/tmp`、0.85×C4 再拆）**可抄进 `.ok` 模板**；但 **k_row/k_cs 未标定**、块粒度 20–60 日为 example、build/chunk/merge/eval **均 stub 未实现**（`research/leaf25_cfacc*` / `leaf25_full_factor*` **不存在**）。无实测单块峰 → **不得**签 X2 实跑 `.ok`。 |
| 2 | **是否必须先**另签 mem_probe 小窗 | **YES** | 见 §3。 |
| 3 | example 误写成实测？与叶27 ABORT 教训 | **PASS（披露合格）** | 文首+§2+§4 反复标 **example/估**；唯一实测锚 `peak_kb=675792`（step_m1）。§3.4 明示对照叶27 峰≈3557MB>1500 → **禁整窗 densify**；与 Arch 叶27 教训一致。 |
| 4 | 采样仅 `/tmp`、wrapper v5 是否写入方案 | **PASS** | §3.1#4、§5 `.cmd` stub、§6 清单均钉 v5 `4240ce82…` 与 `/tmp`；对齐 P2 Arch PASS `964cf57b…`。 |
| 5 | FROZEN r6 钉表与 MEM 冲突？ | **无冲突** | MEM 不改 `X2_END`；FROZEN/DRAFT 钉 `X2_END_TRADE_DATE=20261009`、Data `adb219a0…` / float `346d0dda…`；C4 三帽同文；密封/X2 分签同义。**勿**经 daily_basic/adv20 上移结束日 — MEM 未主张上移。 |
| 6 | 若够签 / 不够：缺口 | **不够签实跑**；缺口见 §4；探针通过后应硬钉键见 §5 |

## 3. mem_probe：YES + 理由

**裁定：YES — 必须先另签 mem_probe 小窗（dry / 单块小样本），再签 X2 实跑 `.ok`。**

理由（硬）：

1. **锚点异构**：唯一实测峰来自 step_m1 TTM recon 金标样本（三码×多 as-of），**不是**全 A×多日宽面板 α build；MEM §2.1 自己承认「整窗 densify **必破**」。
2. **外推未标定**：`k_row`/`k_cs`「未在全叶标定」；期望峰 900000 kB 明文 **example**；到 C4=1331200 的余量不可当作已证安全裕度。
3. **叶27 实证教训**：HI_LIQ 整窗路径 ABORT（峰≈3557MB）；叶25 不得在「仅估」上直接实跑全 X2。
4. **实现空缺**：分块策略尚无法静态证明「无 densify 路径」（脚本未写）；探针同时校准块粒度与峰。

探针最小要求（供主排窗 / AI 实现；**本回合不签不跑**）：

- 独立小 `.ok`（禁与密封/X2 实跑同张；禁复用 `1c32ab1e`）
- wrapper v5 `4240ce82…`；C4/stop/hard **同** 1331200/1484800/1536000；**禁抬帽**
- 采样仅 `/tmp`
- 覆盖 **至少一块** 拟生产粒度（建议先 1 个自然月再平衡日，或 MEM P0 下限 ~20 日），宇宙优先 **HI_LIQ**（FULLA 可后）
- dry/小样本允许：可不写最终评价簿，但必须走「读 PIT→截面 α→落盘分区→gc」主峰路径
- 通过线（建议硬钉进 probe `.ok`）：单块 `peak_kb ≤ 0.85×C4`（≤1131520）；否则 **再拆**后重探针，**不**抬帽
- 探针回执披露：`peak_kb`、块边界、`N_days`/`N_names`、是否 densify、float32 等存储口径

## 4. 缺口清单（挡 X2 实跑 `.ok`）

| # | 缺口 | 责任 | 挡签？ |
|---|---|---|---|
| G1 | **无 mem_probe 实测峰**（本文结论核心） | AI 实现 stub → 主排小窗 → Arch 另签 probe `.ok` → AI 跑 → Arch 消费 | **是** |
| G2 | build / chunk_plan / merge / eval / mem_probe 脚本 **均未实现**（MEM §5 stub） | AI 另任务；新文件名 + 全长 sha 钉进冻结补丁/回执 | **是**（与 G1 串联） |
| G3 | FROZEN §5 §8 财务 + leaf19 **PENDING_REVERIFY** | AI/Arch 现盘重验写入回执（签 X2 前） | **是**（FROZEN 已列；本 MEM 审不替代） |
| G4 | 期望峰 900MB 仍为 example；须由探针改写为 **校准后报告线** | Arch 在 X2 `.ok` 用探针峰×安全系数钉死 | 随 G1 |
| G5 | X2 `.cmd` 草案占位 `<BUILD_SCRIPT>` | AI 在脚本落盘后更新草案 | 随 G2 |

**非缺口（本 MEM 已合格）**：example/实测分界；C4 对齐与禁抬帽文案；强制分块优先级表；wrapper v5 + `/tmp`；叶27 警示；与 `X2_END=20261009` 无冲突。

## 5. 探针通过后，X2 `.ok` 应硬钉的内存键（预列；本回合不签）

| 键意图 | 值 / 约束 |
|---|---|
| `c4_limit_kb` | **1331200** |
| `stopkb` / wrapper STOP | **1484800** |
| `rss_limit_kb` / hard | **1536000** |
| `ban_raise_rss_cap` | **true**（破帽 ABORT；不够就拆） |
| `wrapper_sha256` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` |
| `sampler_root` | **仅** `/tmp/quantlab_*`（禁 `output*`/`data*`） |
| `mem_estimate_sha256` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` |
| `arch_mem_review_sha256` | （本文件落盘后全长） |
| `mem_probe_receipt_sha256` | （探针回执全长；**必填**） |
| `chunk_force` | true；禁整窗 densify；块结束 `del+gc` |
| `chunk_max_rebaldays` / `chunk_max_l1` | **以探针校准值为准**（不得松于探针通过时的粒度） |
| `peak_split_threshold_kb` | **1131520**（0.85×C4）；任一实跑块 ≥ 此值 → 停并拆，`ai_no_retry` |
| `expected_peak_report_kb` | 探针峰 × 约定系数（替换 MEM example 900000） |
| `window` | **仅 X2**；`X2_END_TRADE_DATE=20261009`；start `2024-06-03`；**禁** `--window both`；密封另张 |
| `prereg` | FROZEN 戳记 `4bb1ff2b…` + 正文 `e8ca2bcc…` |
| `ban_reuse_ok` | 显式禁 `1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0` |
| `ai_no_retry` | true |
| `live` | false |

## 6. 给主 / AI 的下一跳（本回合 Arch **不签 `.ok`**）

| 角色 | 动作 |
|---|---|
| **AI** | ① 实现 `leaf25_full_factor_mem_probe_r1.py`（或等价新名）+ 最小 chunk_plan；静态 `py_compile`→`/tmp`；**勿**写 research `__pycache__`。② 交 probe cmd 草案（wrapper v5 / C4 三帽 / `/tmp` / 单块 HI_LIQ）。③ **勿**申 X2 实跑 `.ok`；等 Arch 审探针实现包。④ 并行可推进 build stub，但 **不得**抢在探针前实跑全 X2。⑤ FROZEN §5 重验另排，可与探针实现并行准备清单。 |
| **主** | ① 采纳本审 **NEED_MEM_PROBE**。② 在叶27 **12:30–13:30 ET** 之后（或书面让出后），排 **mem_probe 小窗**（建议短窗，勿占用拟 X2 **14:30–16:00** 全段除非探针极短）。③ 探针 PASS 且脚本 sha 齐 + §8 重验齐 → 再令 Arch 签 **独立 X2 `.ok`**（禁与密封同张；禁复用 `1c32ab1e`）。 |
| **Arch** | ① 本文件即 MEM 审结。② **本回合不签**任何 `.ok`。③ 待 AI 交探针实现包后再静态审；通过后另签 **probe `.ok`**；消费探针回执后，再备 X2 `.ok`（硬钉 §5）。 |

## 7. 总裁定

**NEED_MEM_PROBE** — MEM `103717df…` 全长 MATCH；example/实测分界合格；C4 对齐禁抬帽合格；强制分块与叶27 教训一致；wrapper v5/`/tmp` 已写入；与 FROZEN `X2_END=20261009` 无冲突。**挡签**：无全叶/单块实测峰 + build 脚本 stub → **必须先 mem_probe**，不得直接签 X2 实跑 `.ok`。

live=false。
