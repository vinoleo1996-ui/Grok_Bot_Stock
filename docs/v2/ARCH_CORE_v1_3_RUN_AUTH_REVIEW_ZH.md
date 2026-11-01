# Core v1.3 重跑授权审查（Arch，2026-10-18 00:15 ET）

**结论：发现 1 个 P1，本次不写 `core_x2/ARCH_RUN_AUTH_v1_3.ok`。** 修掉 P1 后，Arch 只需复核这一处 diff 即可写授权文件（其余 8 项已核通过）。
只读审查：没有改策略代码，没有计算任何收益，没有写 core_x2/ 正式路径，live=false，纸面轨没动。没有创建 ARCH_RESIGN_A_v1_3.ok。

审查对象（sha256）：
- `research/optimizer_core_v1_1.py` = `b500c21bca955ea8c8667808f412e734a5c70dae9b20823e5b890d6a5938067e`
- `research/optimizer_core_x2_run.py` = `29b38cf880ebb7c3c648b1f5a7936bedd14468d2ad472f9da96f087099bfc40a`
- `docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_v1_3_ZH.md` = `174601a4791e066c2fb419c5966daa5f991a27ac2048cac13848bff2be4f2b0e`
- `research/optimizer_lambda_calib_sealed.py`（常量）= `875daca9cfbb861cdf685a9f7ff836f1dc18fa80eccf2cf238baccaaf40d3b9c`
- 改动对照：`/workspace/scratch_v13val/*.pre_indpool`（10-15 恢复版，即 pre-ruling 代码）。代码不在 git 中（仓库最后提交 10-12），以此副本 diff。

## 逐条核对
| # | 项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 求解器、整手两处都用全池 wb 行业权重；与 Size/β 同源 | ✅ | 求解器 `IND_POOL=True` 时 `wb_ind = pool_ind_bench(D)`（`D["wb"]` 在全池归一后按申万一级 `data/v2/sw_l1_pit` 分组）。整手由运行器传 `D["wb"].reindex(pool)`、`wb_raw=False`，在 `lot_round_greedy` 中归一后乘股票预算。`prepare_day` 已把 wb 重索引到求解池并归一（sealed.py L926–927），Size/MidCap/β 的 `style_ctx` 与 v1.2 求解器 `POOL_STD` 用的是同一个 `D["wb"]`，同源。 |
| 2 | 覆盖基准有、组合零持仓的行业 | ✅ | 求解器：支撑集外行业若 wb_g > 8%+slack → 该支撑集判不可行（`infeasible_pool_industry_uncovered`）；wb_g ≤ 8%+slack 的零持仓行业自动满足。整手终检 `ind_bad` 对 `wbi.index`（全池所有行业）检查下界。smoke 实测：零持仓行业中 wb 最大的是 801730（7.94%），未破 8%。 |
| 3 | 整手补手检查完整 | ✅ | 修复步：上界（min(20%, wb_g+box)×预算）、**新增下界**（被减行业 ≥ wb_g−box，或不恶化）、风格 + β 超界量须严格下降、现金 ≥0、持仓 ≥20。现金补手：上界 + 风格/β 不增。终检：风格/β 超界、行业上下界、<20 只 → LOT_HARD_FAIL；现金 >2% 只标 LOT_CASH_GT2（K2）。 |
| 4 | 只对 v1.3 生效 | ✅ | `IND_POOL` 默认 False，运行器只在 `v13` 下置 True；v1.1/v1.2 的 smoke 路径、ckpt 目录、门禁不变；整手 wb 实参由 `D["wb"]` 改为 `D["wb"].reindex(pool)`，因 `D["wb"]` 本来就以求解池为索引，属恒等变换。**复现**：临时目录用现代码以 v1.2 设置重解 2026-07-31（上期取 `_ckpt_v1_2/20260630`），100万：求解权重与 `_ckpt_v1_2` 最大差 0.0，两口径整手权重最大差 0.0；60万状态同为 INFEASIBLE。 |
| 5 | λ 与常量不变 | ✅ | `frozen_lambdas()` 断言 λ_risk=117.21317483995702、λ_turn=0.6/0.6；calib_*.json 未动（mtime 10-15 恢复）。NAME_CAP 6%/5%、Neff 20–30、IND 0.08/0.20、SIZE_BOX 0.35、β 0.10、slack 上限 0.05σ/1pp、ETF 20%、W_FLOOR 2%、CASH_MAX 2% 均不变。 |
| 6 | 放行门禁 | ✅（但见 P1） | v13 分支不读 `--arch-cosigned`，只认非空且含 "arch" 的 `ARCH_RUN_AUTH_v1_3.ok`，全量和 smoke 都被拦；sha256 写入 meta。当前 core_x2/ 下无 v1.3 正式权重、无 `_ckpt_v1_3_poolind/`、无授权文件。 |
| 7 | 沿用日新增两列 | ✅ | `_carry()` 计算 `carry_n_out_of_pool` / `carry_out_of_pool_names`，`write_v11_outputs` 写入 disclosure。 |
| 8 | AMEND | ✅ | 页眉时间改为 10-14 ≈09:24 ET，引巡检第 8 行；另有**独立佐证**：看板 fs-watch 事件 `docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_v1_3_ZH.md` 10-14 09:24:58 ET 落盘（Stage2 草稿 09:24:51）。两次先跑后签（10-14 09:24、10-17 23:59）均如实写在 §0 和修订记录。§1.1、§1.2 已加。全文无收益数字（仅 §4 非收益披露）。 |
| 9 | 临时目录 smoke | ✅ | `docs/v2/audit/arch_core_v1_3_runauth_smoke.py` → `..._result.json`（只在内存求解，未写 core_x2/）。2026-06-30、2025-11-28 两档两口径：全部可行，行业约束确实绑定（求解相对偏离最大 = 8%/8.5%，正好等于 box+slack），整手后行业相对/绝对、Size/MidCap、β、20–30 只、单票上限**越界 0**。2026-06-30 电子（801080）全池 wb 21.4% > 20% 绝对上限，可行区间被压到 [13.4%, 20%]，求解正确处理。 |

## 问题
| 级别 | 内容 | 修法 | 负责人 |
|---|---|---|---|
| **P1** | **v1.3 smoke 会污染正式 checkpoint。** 运行器 L212–214：`smoke_days and not v13` 才切到 `_smoke_v1_1/`；v1.3 带 `--smoke-days` 时 `ck_dir` 仍是正式的 `_ckpt_v1_3_poolind/`，smoke 日以 `prev=None`（w0=wb、无上期整手持仓）求解并 `pickle.dump` 进正式目录，`smoke_feasibility.json` 也写在那里。之后全量运行遇到已存在的 ckpt 直接加载（L231），这些日子的权重就带着错误的 w0（换手惩罚基准错）和缺失的沿用漂移进入正式权重，且无任何提示。授权文件同时开放 smoke 和全量，这个风险是现实的。 | v1.3 smoke 改写独立目录（如 `_smoke_v1_3_poolind/`），或在 v1.3 下禁止 `--smoke-days`；另建议 ckpt 内写 `smoke: True` 和代码 sha256，全量加载时遇到 smoke 标记或代码 sha 不符即报错。 | Strategy |
| P2 | 整手修复的目标函数只降风格/β 超界，不主动修行业下界缺口；取整清零造成的行业缺口只能靠补手顺带修，否则判 LOT_HARD_FAIL。方向保守（不越界），但会降低可行率。`lot_fail_reason` 只分 `style` / `names_or_industry`，风格与行业同时坏时只记 style。 | 重跑后按 style / industry / names 三类分别披露 LOT_HARD_FAIL。不改算法。 | Strategy |
| P2 | 支撑集筛选仍是按 |w¹| 截前 K（冻结规格），不会为覆盖 wb > 8%+slack 的行业主动纳入股票；若某日这类行业未进前 K，所有 K 都会判 INFEASIBLE。 | 重跑后单列 `infeasible_pool_industry_uncovered` 日数。冻结规格，不改。 | Strategy |
| P2 | C1 复核（`exposure_drift`）行业按"股票部分归一"计，代码约束按"NAV×预算"计。K2 下现金常 >2%，两种口径会让复核误标。 | disclosure 同时给两种口径，判定以代码口径为准。 | Strategy / Eng |
| P2 | `_UNK`（无申万映射）作为一个"行业"受约束（smoke 中 wb 0.01–0.77%）。 | 披露 `_UNK` 只数和权重。 | Strategy |

## 授权文件（P1 修掉后写入；本次未写）
预定格式为单行：`Arch run-auth v1_3 | <ET 时间> | optimizer_core_v1_1.py sha256=<…> | optimizer_core_x2_run.py sha256=<…> | AMEND_v1_3 sha256=<…> | 只授权生成权重与非收益披露，不授权计算收益 | ref docs/v2/ARCH_CORE_v1_3_RUN_AUTH_REVIEW_ZH.md`。
sha 以修复后的文件为准；之后代码或 AMEND 再有改动，授权自动失效，须重审。

## 并发情况（00:18 ET 补）
- 本审查进行期间，Arch 增量审计例程（agent 98437113）于 **00:17:10 ET 写入了 `ARCH_RUN_AUTH_v1_3.ok`**（只授权权重生成，依据 `docs/v2/audit/AUDIT_20261018_0016_ET_ZH.md` §3）。本审查**没有写**该文件，也**没有删除**它。
- 例程的审查没有覆盖本文 P1（v1.3 smoke 写进正式 ckpt）。在 P1 修好前：**v1.3 只准跑全量命令 `--version v1_3`，禁止带 `--smoke-days`**；若已带 smoke 跑过，须清空 `_ckpt_v1_3_poolind/` 后重跑全量。是否撤回授权文件，由主 Agent 裁定。
- 截至 00:18 ET：`_ckpt_v1_3_poolind/` 不存在，无 v1.3 运行进程，无 v1.3 正式权重。
