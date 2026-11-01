# Arch 终审：叶27 脚本 DIFF（on_minus_id idio ivol）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T06:46:43-04:00
- 审阅基准：Arch 契约预告 sha256 `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196`
- 范围：静态审 DIFF + 脚本全文 + impl pin；**/tmp 应用 DIFF + py_compile**；**不跑实数据**；**不签任何 .ok**；**不挡叶25**
- live=false；promotion_approved=false

## 结论

**PASS_WITH_CONDITIONS**

新包（DIFF `3d3a901f…` / 脚本 `1da6922c…` / impl `2fc801aa…`）首页与正文均钉现盘预告 `31462908…`（旧包 `e3cd4bf1`/`1cb516bb`/`0c4bbcc7` 及预告 `ac853d7f` **SUPERSEDED，不作准**）。主规格方向、β/W、OHLC 主路径、510300 单路径、capacity_adv 暴露钉静态对齐；市值 **禁静默用 T** 已硬落地。签 `.ok` 前仍须闭合涨跌停日对齐闸与路径 sha 重钉等条件。

**本轮明确：未签任何 .ok。**

## 条件（签叶27 `.ok` 前须闭合或明示研究级豁免）

1. **Arch 预告钉 → `31462908…`**：本包 **已 MATCH（CLOSED）**。DIFF 首页、脚本 docstring、impl pin §对齐均引全长 `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196`；旧 `ac853d7f…` 仅作 SUPERSEDED 旁注。**STALE_PREVIEW_PIN = false（本包）**。
2. **市值 T−1 断言评判**：
   - **禁静默用 T：够硬**——`mktcap_T_minus_1` 仅取 `sessions[di-1]`；缺/≤0 → `e3` 置 NaN 且 ivol 截面跳过该票；加载表后 `assert_pinned_sha(MKTCAP)`。
   - **`available_at` 列级：仍软**——未读表内 `available_at`、未与 `decision_cutoff(T)` 比对；仅 docstring 约定「T−1 会话 18:00 Asia/Shanghai 代理」。签 `.ok` 前须：**硬化列断言**，或 Arch/主裁明示研究级豁免「日历 T−1 + reader 代理可接受」。
3. **签 `.ok` 前路径/实现 sha 重钉**：OHLC raw daily（逐日或样本集）、`etf_daily_adj`、`float_mktcap_from2015`、limit panels、suspend 掩码、capadv 权重——本包常量已写研究推荐 sha，**独立 `.ok` 窗须再核盘面字节 MATCH**（禁私换路径）。
4. **不挡叶25**：现盘 `.ok` sha8 `7b279d47`（全长 `7b279d4731760de3c6b194b1d5d93e47acfc5607fa5d05f1defbd5dce07e31a7`）；窗 **10:00–10:45 ET**；本审不碰叶25 钉/例程。
5. **涨跌停闸（签 `.ok` 阻断级）**：`limit_hit` **桩实现恒返 `None`，且 `run_one` 未调用**——触板日未剔出截面/ivol。列名 `limit_up`/`limit_down` 与路径常量对齐预告，但**行为未闭合**。签前须日对齐接线（未知→无效或硬披露，禁静默当未触板；BJ 值空须披露）。
6. **WARN（不单独否决本轮研究 DIFF）**：SW L1 用 `drop_duplicates(keep=last)` 非完整 `out_date` PIT；β 股票腿用 `close/pre_close−1` vs 510300 hfq（脚本已 DRAFT 披露）；Jaccard 仅文案/元数据、无独立计算（OLS 用连续 `target_weight`，与 Alpha 暴露钉一致）；FULLA 权重未 `assert_pinned_sha`。

## sha 表（盘面再测）

| 项 | 路径 | sha256 | 结果 |
|---|---|---|---|
| DIFF | `docs/v2/AI_LEAF27_ON_MINUS_ID_IDIO_IVOL_DIFF.patch` | `3d3a901f1989c2a84bfb43c71ef3dc2f775a6a6e636521fc7018db3800e4d9f2` | **MATCH** |
| 脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `1da6922cb859cb9028b7399bce3abab0a2d48233e9c3e21f34807565000322c6` | **MATCH** |
| impl pin | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `2fc801aaa8c46b38a18dfb767e0319500f637c973f820b7195b9e7d64714eea8` | **MATCH** |
| Arch 预告（审阅基准） | `docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` | `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196` | **MATCH** |
| 预注册 r1 FROZEN | `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` | `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf` | MATCH |
| Alpha 暴露钉 | `docs/v2/ALPHA_LEAF27_CAPACITY_ADV_EXPOSURE_PIN_20261025_ZH.md` | `5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7` | MATCH |
| Data 缺口对齐 | `docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md` | `cc85cb34dbaf7dba196e39ec17ce4dfb518302a48ea80769646230305257a745` | MATCH |
| Alpha 残差短审（旁证） | `docs/v2/ALPHA_LEAF27_DIFF_RESID_CONTRACT_REVIEW_20261025_ZH.md` | `d321ffe697c5a1b5d173d63d8985a5dc5dde176c322fe7d5f4fbccbd7be048d0` | MATCH（**短审物为旧包 sha**；暴露逻辑与新包一致；本终审以新包为准） |
| 权重表（常量钉） | capadv HI_LIQ weights | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` | 脚本常量+运行时 assert |
| 旧包 DIFF/脚本/impl | — | `e3cd4bf1…` / `0c4bbcc7…` / `1cb516bb…` | **SUPERSEDED（不作准）** |
| `/tmp` patch -p1 from /dev/null → 脚本 sha | — | = `1da6922c…` | PASS |
| `python3 -m py_compile` | — | — | **PASS** |

## 清单（对照预告 §1/§2 + impl A–E）

| # | 项 | 结果 |
|---|---|---|
| 1 | α_raw=−ivol；β=510300 60/min40；W=20/min15 | **PASS**（常量+`alpha_raw=-ivols_a`） |
| 2 | OHLC 主路径 raw daily + `pre_close` 校验（`pc>0`） | **PASS** |
| 3 | 禁 `reference_price` 作 pre_close | **PASS**（文案+未引用） |
| 4 | 510300=`etf_daily_adj` hfq c2c + sha assert `48b21e84…` | **PASS** |
| 5 | capacity_adv：`target_weight`；路径+sha `3b288c83…`；缺失→0；剔 510300；禁 ADV | **PASS**（与 Alpha `5e720335` / 短审 RESID_CONTRACT_PASS 一致） |
| 6 | 活跃仅 Jaccard（OLS 不用 0-1） | **PASS**（文案；无误用 ADV） |
| 7 | 停牌：宇宙掩码 `suspended` | **PASS** |
| 8 | 涨跌停：列名 `limit_up`/`limit_down` 常量 | **PASS（列名）** / **FAIL→条件5（行为未接）** |
| 9 | 市值 T−1：prev session；缺则无效 | **PASS（禁静默用 T）** |
| 10 | `available_at` ≤ decision_cutoff 运行时断言 | **WARN/软** → 条件2 |
| 11 | 封面/DIFF/impl 引预告 `31462908` 非 `ac853d7f` | **PASS** |
| 12 | live/paper | **PASS**（`live=False`；无 paper 入口；`--dry-compile-only`） |
| 13 | 不挡叶25 / 本轮不签 .ok | **PASS** |

### 回答 AI 问 B（市值 T−1 断言是否够硬）

**对「缺 T−1 / 禁静默用 T」够硬；对 impl §B 要求的 `available_at` 列级断言不够硬（仍文档代理）。** 故 B 维持 **GAP_PENDING_SCRIPT 的 available_at 子项**，日历 T−1 子项可标 **SCRIPT_LANDED**。

## 非动作

- **未签**叶27 / 叶25 / 补跑 / moneyflow 任何 `.ok`
- 不改 `research/` 逻辑（只审）；不跑实数；不 git commit
- 不挡叶25@10:00–10:45 ET
- live=false

## 下一步（供主裁，非本轮执行）

1. AI：接线 `limit_hit` 日对齐（未知/BJ 空→无效或硬披露）→ 重交 DIFF；可选硬化 `available_at` 断言。  
2. Arch：**另窗**签叶27 `.ok`（条件 2–5 闭合后；**不复用**叶25 钉）。  
3. Alpha 暴露侧已短审通过；全脚本以本终审为准。
