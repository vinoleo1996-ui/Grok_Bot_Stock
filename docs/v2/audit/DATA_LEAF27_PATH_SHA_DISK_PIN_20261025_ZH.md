# DATA 叶27 现盘路径/字节盘点 PIN（条件3 · 研究级）

- **角色**：QuantLab Data 执行器
- **ET 时刻**：2026-10-25 07:02–07:05 America/New_York（箱内时钟 CST 等同会话）
- **主令**：主 Agent P1 / Arch 叶27 R2 条件3——路径/实现 sha 另窗重钉用；对照脚本常量盘点现盘字节
- **禁令**：禁签 `.ok`；禁消费补跑 `.ok` `9e4359f9`；禁写生产；不挡叶25；`live=false`
- **本文件性质**：研究级只读核验回执；**Data 不签** `.ok`；仅供 Arch 另窗重钉条件3 的数据侧证据

---

## 1. 输入核验表

| 输入 | 路径 | 全长 sha256 | vs 期望 | 判定 |
|------|------|-------------|---------|------|
| Arch R2 | `docs/v2/ARCH_AI_LEAF27_DIFF_REVIEW_LIMIT_HIT_R2_20261025_ZH.md` | `4c85a169f6822e2d589b9d761672d944cad9ca21941518431aa64fee0f5b13e5` | （本窗只读存在复核） | 存在 |
| IMPL_PIN | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `a532e6db956600ab3e4048edeaabdc653b2e83ed4ef52f2839eeb78e12f87416` | `a532e6db…f87416` | **MATCH** |
| 脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` | `7a5f756c…08f8c6` | **MATCH** |
| 前缺口（引用勿覆写） | `docs/v2/audit/DATA_LEAF27_CONTRACT_GAP_ALIGN_20261025_ZH.md` | `cc85cb34dbaf7dba196e39ec17ce4dfb518302a48ea80769646230305257a745` | `cc85cb34…` | **MATCH** |

脚本常量（现盘再读 L65–L86，与主令一致）：

```
DAILY = data/v2/tushare_raw/daily
MKTCAP = data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet
MKTCAP_SHA = 346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef
ETF = data/v2/etf/etf_daily_adj.parquet
ETF_SHA = 48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
CAPADV_HILIQ = output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet
CAPADV_HILIQ_SHA = 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d
PANEL_1C85 = data/local_market/1c85fd9aceaa03c3c4863bec/panels
PANEL_EXT = data/v2/asof_extend_tushare_202610/panels
MASK HILIQ = output/strategy_hiliq/universe_mask_hiliq_v1.parquet
```

IMPL_PIN 另钉：OHLC 样本 `20180102.parquet` sha `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631`；覆盖 20180102→20261016 n=2130；suspend 辅助 `data/v2/suspend_flags/suspend_flags_v2.parquet` 列 `halted_fullday`。

---

## 2. 结论总表

| # | 项 | 路径 | 全长 sha / 规模 | vs 常量 | 列/内容抽检 | 判定 |
|---|-----|------|-----------------|---------|-------------|------|
| 1 | OHLC raw daily | `data/v2/tushare_raw/daily` | n=**2130**；`20180102.parquet`→`20261016.parquet` | 覆盖+样本 sha | `pre_close,open,close` 齐 | **MATCH** |
| 1a | OHLC 样本 | `…/daily/20180102.parquet` | `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631` | IMPL_PIN | nrows=3282 | **MATCH** |
| 2 | etf_daily_adj | `data/v2/etf/etf_daily_adj.parquet` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | `48b21e84…` | `510300.SH` + `close_hfq` | **MATCH** |
| 3 | float_mktcap_from2015 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` | `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` | `346d0dda…` | 有 `float_mktcap`；**无** `available_at`（与研究豁免一致） | **MATCH** |
| 4a | limit panels 1c85 | `data/local_market/1c85fd9aceaa03c3c4863bec/panels` | n=**6026** | 目录钉 | SH/SZ 有 `limit_up`/`limit_down`；BJ 样例列在但值全空 | **MATCH**（BJ 空值旁记） |
| 4b | limit panels extend | `data/v2/asof_extend_tushare_202610/panels` | n=**5582** | 目录钉 | SH/SZ/BJ 均有 `limit_up`/`limit_down` 且 BJ 非空 | **MATCH** |
| 5a | suspend 掩码 HILIQ | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | （脚本读列，无钉 sha） | 有 `suspended` | **MATCH** |
| 5b | suspend_flags_v2 | `data/v2/suspend_flags/suspend_flags_v2.parquet` | `ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377` | IMPL_PIN 辅助钉 | 有 `halted_fullday` | **MATCH** |
| 6 | capadv 权重 HILIQ | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` | `3b288c83…` | 有 `target_weight` | **MATCH** |

**计数**：钉 sha / 覆盖项 **MATCH = 9**；**MISMATCH = 0**；**PARTIAL = 0**（BJ@1c85 `limit_*` 全空为已知旁记，不改 MATCH——列存在且脚本按 SH/SZ 主路径消费）。

---

## 3. 分节证据

### 3.1 OHLC raw daily

- 目录存在；`*.parquet` 文件数 **2130**；首 `20180102.parquet` / 尾 `20261016.parquet`（与 IMPL_PIN 覆盖一致）。
- 样本全长 sha：
  - `20180102.parquet` → `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631` **MATCH** IMPL_PIN
  - `20260630.parquet` → `013df430120c5aefef7a092361e0c2aefc8aec65e8d0b1098cb9b7d951dfbeac`（路径切点旁证）
  - `20261016.parquet` → `d25ca1c7a55a9785d2c94b2f3072192444a4e419c5813e46019be46987a65212`（尾日旁证）
  - 另抽 `20200102.parquet` → `fed2f8ec886363623651343c653b001188dc1635d27198d655fb54d4cd8f569b`
- schema（四样本一致）：`ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount` —— **含** `pre_close, open, close`。

### 3.2 etf_daily_adj

- 存在；size≈72.1MB；全长 sha **MATCH** `48b21e84…0ffd74c`。
- nrows=1,564,839；`trade_date` 范围 20150105→20261016（n_dates=2862）。
- 含 `close_hfq`（null=0）；投影确认存在 `ts_code==510300.SH`。
- 另含 `available_at` / `available_at_tz`（ETF 侧有；非本条件阻断项）。

### 3.3 float_mktcap_daily_from2015_tushare

- 存在；size≈185.2MB；全长 sha **MATCH** `346d0dda…72a1ef`。
- nrows=11,711,361。
- 列：`instrument_id, trade_date, float_mktcap, total_mv, turnover_rate, source, schema, quality_status, promotion_approved`。
- **有** `float_mktcap`；**无** `available_at` —— 与主令/研究豁免（脚本 `mktcap_available_at=RESEARCH_WAIVER_GRANTED`）一致，不记 MISMATCH。

### 3.4 limit panels

- **1c85**：存在；n=6026（`bj.430017`…`sz.301696`）。
  - `sh.600000` / `sz.000001`：列含 `limit_up`/`limit_down`（各约 5 行 null / ~3000）。
  - `bj.430017`：列在，但 `limit_up`/`limit_down` **568/568 null**（BJ@1c85 值空旁记）。
- **extend**：存在；n=5582（`bj.920000`…`sz.302132`）。
  - `sh.600000` / `sz.000001` / `bj.920000`：均含 `limit_up`/`limit_down`，BJ 样例 null=0/72。
- 与脚本路径切点（ymd≤20260630 → 1c85；否则 → extend）一致；目录级 **MATCH**。

### 3.5 suspend

- **MASK HILIQ** `universe_mask_hiliq_v1.parquet`：存在；sha `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af`；nrows=11,748,583；列含 `date, instrument, in_universe, st, suspended, young, adv_fail, adv20_yuan` —— **有 `suspended`**。
- **suspend_flags_v2**：存在；sha `ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377`；nrows=111,480；**有 `halted_fullday`**（及 `available_at_open/close` 等）。

### 3.6 capadv 权重

- 路径存在；size≈12.3MB；全长 sha **MATCH** `3b288c83…2d31c4d`。
- nrows=3,595,176；列含 `date, instrument, target_weight, …` —— **有 `target_weight`**。

---

## 4. 汇总（交 Arch 另窗）

- **条件3 盘面（数据侧）**：**全 MATCH**（钉 sha 项 0 MISMATCH；目录/列抽检齐）。
- 可交 Arch 另窗用本回执 + 上表全长 sha 重钉路径/实现；**Data 本窗不签 `.ok`**。
- 旁记：1c85 BJ panel `limit_*` 全空（列在值空）；mktcap 无 `available_at`（豁免已钉）。二者均不构成字节 MISMATCH。
- **不挡叶25**；未触生产写；未消费补跑 `9e4359f9`；未签任何 `.ok`。

---

*原子写：tmp→rename；本文件新建，未覆写旧回执。*
