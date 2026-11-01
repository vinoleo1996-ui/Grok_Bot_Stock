# 叶27 实现前契约闭合钉（研究级 · IMPL_PIN）

- **角色**：QuantLab AI（后台执行器）
- **时刻**：2026-10-25 06:51:30 ET（America/New_York）
- **状态**：**IMPL_PIN** · 研究级 · **不申 `.ok`** · `live=false` · `promotion_approved=false`
- **对齐（全长 MATCH）**：
  - Arch 预告：`docs/v2/ARCH_AI_LEAF27_CONTRACT_PREVIEW_20261025_ZH.md` sha256 `31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196`（取代 `ac853d7f…` SUPERSEDED）
  - 预注册 r1 FROZEN：`docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` sha256 `f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf`
  - Alpha 暴露钉：`docs/v2/ALPHA_LEAF27_CAPACITY_ADV_EXPOSURE_PIN_20261025_ZH.md` sha256 `5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7`
  - Data 缺口对齐：`docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md` sha256 `cc85cb34dbaf7dba196e39ec17ce4dfb518302a48ea80769646230305257a745`
  - 主裁 available_at 研究级豁免：`docs/v2/MAIN_LEAF27_MKTCAP_AVAILABLE_AT_RESEARCH_WAIVER_20261025_ZH.md` sha256 `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f`
- **脚本**：`research/g1g5_on_minus_id_idio_ivol_alpha.py` sha256 `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6`
- **锁**：不改 FROZEN 预注册正文（方向 `α_raw=−ivol` / β=60 / W=20）；不读收益/IC；不挡叶25；不 git commit；**豁免 ≠ 签 `.ok`**
- **范围**：闭合 Arch 终审 `666fed20…` 阻断项（`limit_hit` 日对齐）；重交 DIFF

---

## 总表（A–E）· 并入 Data `cc85cb34…` + 主豁免 `b39954c3…`

| 节 | 主题 | 状态（本钉） | 说明 |
|---|---|---|---|
| A | OHLC / `pre_close` | **CLOSED** | 主路径 raw daily |
| B | 市值 T−1 | **拆开** | 日历 T−1 = **SCRIPT_LANDED**；`available_at` 列级 = **RESEARCH_WAIVER_GRANTED** |
| C | 510300 单路径 | **CLOSED** | `etf_daily_adj` hfq c2c |
| D | capacity_adv 暴露 | **CLOSED（MATCH Alpha）** | `target_weight` |
| E | 涨跌停 / 停牌 | **CLOSED（行为）** | `limit_hit` 日对齐已接；未知/BJ→无效 |

---

## A. OHLC / pre_close · CLOSED

| 项 | 写死值（对齐 Data §1） |
|---|---|
| **主路径** | `data/v2/tushare_raw/daily/{YYYYMMDD}.parquet` |
| **列** | `open, close, pre_close`（另有 `ts_code,trade_date,high,low,…`） |
| **样本 sha** | `20180102.parquet` = `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631` |
| **覆盖** | `20180102`→`20261016`（Data：n=2130） |
| **无效** | 缺 `open`/`pre_close` 或 `pre_close≤0` → 无效 |
| **公式现算** | `r_on=open/pre_close−1`；`r_id=close/open−1`；`on_minus_id=r_on−r_id` |
| **禁** | 1c85 / asof_extend* panel 作主规格 OHLC（**无** `pre_close`）；**禁**把 `reference_price` 静默当 `pre_close` |
| **复权** | 信号层默认 raw；评价/自检跟 `AI_ADJ_PRICE_RECEIPT_ZH` |

**状态：CLOSED**

---

## B. 市值 T−1 · 拆开（SCRIPT_LANDED + RESEARCH_WAIVER）

> Data §2：长表 **无** `available_at` 列（schema：`instrument_id,trade_date,float_mktcap,…`）。**禁止伪造列**。

| 子项 | 状态 | 写死值 |
|---|---|---|
| **日历 T−1** | **SCRIPT_LANDED** | 会话 T 取 `sessions[di-1]` 的 `float_mktcap`；缺/≤0 → 无效；**禁静默用 T**（`mktcap_T_minus_1`） |
| **`available_at` 列级** | **RESEARCH_WAIVER_GRANTED** | 主裁文 sha256 `b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f`：接受日历 T−1 + reader 文档代理（T−1 会话 18:00 Asia/Shanghai）；**不要求**表内列运行时断言 |
| **推荐主表** | 路径 CLOSED | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` sha256 `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` |
| **asof 禁混** | — | `float_mktcap_asof.parquet` 仅单日快照，不得当历史序列 |

**状态：日历 T−1 = SCRIPT_LANDED；available_at = RESEARCH_WAIVER_GRANTED（≠ `.ok`）**

---

## C. 510300 单路径 · CLOSED

| 项 | 写死值 |
|---|---|
| **唯一主路径** | `data/v2/etf/etf_daily_adj.parquet` |
| **文件 sha256** | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` |
| **过滤** | `ts_code == "510300.SH"` |
| **收益** | hfq close-to-close |
| **β** | 60 / 最少 40 |
| **禁混** | `etf_510300/panels`；`data/bench/510300_daily.parquet` |

**状态：CLOSED**

---

## D. capacity_adv 暴露 · CLOSED（MATCH Alpha）

| 项 | 写死值 |
|---|---|
| **暴露列** | **`target_weight`** |
| **路径** | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` |
| **表 sha256** | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` |
| **规则** | left-join；缺失→0；剔 `510300.SH`；不得跳过第 5 步 |
| **活跃** | `active_capadv=1{target_weight>0}` **仅 Jaccard** |
| **禁止** | `adv20_yuan` / `adv_fail` 作第 5 步回归量 |

**状态：CLOSED（MATCH Alpha `5e720335…`）**

---

## E. 涨跌停 / 停牌 · CLOSED（行为）

### E.1 涨跌停 · 行为 CLOSED（相对 Arch `666fed20…` 条件5）

| 项 | 写死值 |
|---|---|
| **列名** | **`limit_up` / `limit_down`**（价格档；触板：`close>=limit_up` 或 `close<=limit_down`，板价有限且 >0） |
| **panel ≤2026-06-30** | `data/local_market/1c85fd9aceaa03c3c4863bec/panels/{ex}.{code}.parquet`；index=`event_time` → `%Y-%m-%d` |
| **panel ≥2026-07-01** | `data/v2/asof_extend_tushare_202610/panels/`；列 `trade_date` → `%Y-%m-%d` |
| **缓存** | `LimitPanelCache`：按 `(ts_code, panel_kind)` 一次读表；禁每 (code,day) 重读 |
| **`limit_hit` 返回** | `True`=触板；`False`=板价有效且未触板；`None`=panel/行缺或 lu&ld 均无效（含 BJ 值空） |
| **日循环策略** | **`limit_policy=exclude_hit_or_unknown`**：触板或未知 → **不进**当日截面残差五步 / `eps_hist` / ivol；仅 `False` 参与 |
| **BJ** | lu/ld 空 → `None` → 剔除；meta 硬披露 `bj_limit_empty_n` / `limit_unknown_n` / `limit_hit_n` |
| **禁** | 恒返 `None` 的桩；静默把未知当未触板 |

### E.2 停牌

| 优先 | 路径 | 列 |
|---|---|---|
| ① | universe_mask_* | `suspended` |
| ② | `suspend_flags_v2.parquet` | `halted_fullday` |

**状态：CLOSED（日对齐+未知/BJ→无效）**

---

## 非动作 / 下一步

- **不申 `.ok`**；不跑 sealed/X2 实数；不挡叶25@10:00；不 git commit  
- 路径 sha 另窗再核（Arch 条件3）  
- **下一步**：交 Arch 复审 `limit_hit` 闭合 + 知悉 `available_at` 豁免 → 独立 `.ok` 另窗

## 钉摘要

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` |
| 脚本 sha | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` |
| A/C/D/E | CLOSED（E 行为已接） |
| B 日历 T−1 | **SCRIPT_LANDED** |
| B available_at | **RESEARCH_WAIVER_GRANTED**（`b39954c3…`） |
| Arch 预告 | `31462908…` MATCH |
| live | false |
