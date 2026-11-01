# Arch 复审 R2：叶27 limit_hit 日对齐闭合（对照终审条件5）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T06:59:35-04:00
- 对照终审：`docs/v2/ARCH_AI_LEAF27_DIFF_REVIEW_20261025_ZH.md` sha256 `666fed209731dab958cddf498f16ca879f03ff22d844e8d52aee0f315871bd79`
- 审阅基准：Arch 契约预告 sha256 `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196`
- 范围：静态审新三件套 + 闭合文 + 豁免文；**/tmp 从空应用 DIFF + py_compile**；**不跑实数据**；**不签任何 .ok**；**不挡叶25**
- live=false；promotion_approved=false

## 结论

**PASS_WITH_CONDITIONS**

相对终审 `666fed20…`：**条件5（涨跌停日对齐）CLOSED**——`LimitPanelCache` + `limit_hit` 真接线（非恒返 `None` 桩）；`exclude_hit_or_unknown` 在截面残差与 ivol 两处生效；meta 硬披露 `limit_hit_n` / `limit_unknown_n` / `bj_limit_empty_n`；未知（含 BJ 空）→剔除，**禁**静默当未触板。**条件2** 主裁研究级豁免 **已收讫**（`b39954c3…` → CLOSED-by-waiver）；日历 T−1 仍硬。残差五步 / 暴露 `target_weight` / `α_raw=−ivol` **未回退**。首页/DIFF/impl/脚本均 MATCH 预告 `31462908…` + 豁免 `b39954c3…`。

**签 `.ok` 前仍剩（本轮不签）**：条件3 — 路径/实现 sha 独立 `.ok` 窗重钉（OHLC raw daily、etf_daily_adj、float_mktcap、limit panels、suspend、capadv 权重）。WARN（SW L1 keep=last、β 股票腿 vs 510300 hfq、Jaccard 仅元数据、FULLA 未 assert）续开，不单独否决本复审。

**本轮明确：未签任何 .ok。不挡叶25。**

## 条件状态（对照 `666fed20…`）

| # | 条件 | 本轮状态 |
|---|---|---|
| 1 | Arch 预告钉 `31462908…` | **CLOSED**（DIFF/脚本/impl 首页全长 MATCH；无 `ac853d7f`） |
| 2 | 市值 `available_at` | **CLOSED-by-waiver**（主裁 `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f`）；日历 T−1 / 禁静默用 T 仍 SCRIPT_LANDED |
| 3 | 路径/实现 sha 重钉 | **OPEN（签 .ok 前）** — 另窗核盘面字节；本轮不签 |
| 4 | 不挡叶25 | **PASS**（现盘 `.ok` `7b279d47…`@10:00–10:45 ET；本审不碰） |
| 5 | 涨跌停日对齐 | **CLOSED**（见下节证据） |
| 6 | WARN 项 | **续开**（不单独否决） |

## 条件5 证据（limit_hit 真闭合）

1. **`LimitPanelCache`**：`panel_kind` 按 `ymd<=20260630`→`1c85` else `ext`；1c85 读 `limit_up`/`limit_down` 并以 index=`event_time`（或缺则列）→`%Y-%m-%d`；extend 读 `trade_date`+板价列；按 `(ts_code, kind)` 缓存，禁每 (code,day) 重读整表。
2. **`limit_hit` 返回**：`True`=触板（`close≥lu` 或 `close≤ld`，板价有限且 >0）；`False`=至少一侧板价有效且未触；`None`=panel/行缺或 lu&ld 均无效（含 BJ 空）/ close NaN。AST 见多路 return，**非**恒 `None` 桩。
3. **调用点**：`run_one` 日循环在算 `on_minus_id` 前 `keep_idx` 过滤 — `hit is True` / `hit is None` 均 `continue`（不进当日截面残差五步，故不进当日 `eps_hist`）；ivol 段再次 `if hit is not False: continue`。策略常量 `limit_policy="exclude_hit_or_unknown"`。
4. **meta 硬披露**：写出 `limit_hit_n` / `limit_unknown_n` / `bj_limit_empty_n`（BJ 后缀计入 unknown 时累加 `bj_limit_empty_n`）。
5. **未知语义**：缺文件/读失败/行缺 → `None` → 剔除；**无**把未知映射为 `False` 的路径。

## sha 表（盘面再测）

| 项 | 路径 | sha256 | 结果 |
|---|---|---|---|
| 脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` | **MATCH** |
| DIFF | `docs/v2/AI_LEAF27_ON_MINUS_ID_IDIO_IVOL_DIFF.patch` | `e2ed0fc88bfe38c07892a3a87d03f9b2372cb8cfd568fd7de9548f3113978b71` | **MATCH** |
| impl pin | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` | **MATCH** |
| 闭合文 | `docs/v2/AI_LEAF27_LIMIT_HIT_CLOSURE_20261025_ZH.md` | `f43279177c6fe8c3e6bce5d2aa60457d6cf586ecaecc375b33546141edaffc3e` | **MATCH** |
| 主裁豁免 | `docs/v2/MAIN_LEAF27_MKTCAP_AVAILABLE_AT_RESEARCH_WAIVER_20261025_ZH.md` | `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f` | **MATCH** |
| Arch 预告 | `docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` | `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196` | **MATCH** |
| 前终审 | `docs/v2/ARCH_AI_LEAF27_DIFF_REVIEW_20261025_ZH.md` | `666fed209731dab958cddf498f16ca879f03ff22d844e8d52aee0f315871bd79` | **MATCH** |
| 旧包脚本/DIFF/impl | — | `1da6922c…` / `3d3a901f…` / `2fc801aa…` | **SUPERSEDED（不作准）** |
| `/tmp` patch -p1 from /dev/null → 脚本 sha | — | = `7a5f756c…` | **PASS** |
| `python3 -m py_compile` | — | — | **PASS** |

## 残差 / 暴露未回退（抽检）

| 项 | 结果 |
|---|---|
| α_raw=−ivol；β=60/min40；W=20/min15 | **PASS** |
| 五步：on_minus_id → SW demean → log mktcap T−1 → β510300 → target_weight | **PASS** |
| 暴露列 `target_weight`；miss→0；剔 510300；禁 ADV | **PASS** |
| 日历 T−1 `mktcap_T_minus_1`；缺→无效 | **PASS** |
| `mktcap_available_at=RESEARCH_WAIVER_GRANTED` + 豁免全长钉 meta | **PASS** |

## 非动作

- **未签**叶27 / 叶25 / 补跑 / moneyflow 任何 `.ok`
- 不跑实数；不 git commit；不改 `research/` 逻辑（只审）
- 不挡叶25@10:00–10:45 ET
- live=false

## 下一步（供主裁，非本轮执行）

1. **另窗**签叶27 `.ok`：仅余条件3路径 sha 盘面重钉（+ 收悉 WARN）；**不复用**叶25 钉。  
2. 本复审闭合条件5；条件2 豁免已生效；无需再为 limit_hit 重交（除非另窗发现盘面路径漂移）。
