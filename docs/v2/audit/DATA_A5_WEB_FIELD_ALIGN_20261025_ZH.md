# DATA A5 × Web A5：拟增字段对齐回执（文档 only）

- **角色**：QuantLab Data 执行器
- **ET**：2026-10-25 ≈12:20 America/New_York
- **live**=false · **不改**两源 A5、探针、生产、`.ok`
- **对照源**（只读）：
  - Data A5 `DATA_A5_HUB_STALE_CACHE_RECEIPT_FIELDS_20261025_ZH.md` 全长 sha256=`7f02367eed9d0542f6d73a67dbabe1d32c656704c2e4b0cf5013a5c3a1f7f268`
  - Web A5 `WEB_ALPHALENS_AGE_STALE_READY_GAP_20261025_ZH.md` 全长 sha256=`708364351bfe0e6b47069324b779ae5091d6641fe9f4b81b3f4a410d405a5a17`（前缀 `70836435` MATCH）

---

## 结论（先行）

**字段语义已对齐，可排实现**；改码须另签 Eng/Arch `.ok`；本回合未改探针/生产。

---

## 1. 字段对照表

| 概念 | Data A5 字段名 | Web A5 字段名 | 判定 | 备注 |
|---|---|---|---|---|
| last-good 时刻 | `last_good_ts_et` | `last_good_et` | RENAME_OK | 语义同；实现可双向接受或统一 `last_good_et` |
| age_s | `age_s_since_last_good` | `age_s` | RENAME_OK | 语义同；Data 回执可兼出短名 `age_s` |
| stale | `stale` | `stale` | ALIGN | 同：无 last-good 或超阈值 → true |
| empty | `this_run_empty` | `empty` | RENAME_OK | 语义同；空轮不刷 last-good |
| error | `error_trade_cal` / `error_stock_basic` | `error` | ALIGN | 同 hub `err[key]`；Data 按 API 拆键，Web 按 dataset |
| cache_write | `cache_write` | — | DATA_ONLY | 写端专属；Web 不需同名，读侧须守「empty 不刷绿」 |
| ready | — | `ready` | WEB_ONLY | 看板首屏就绪；探针回执不强制 |
| updated_at | —（本轮 `时刻`/CSV `ts_et`；锚点见 last-good） | `updated_at_et` | WEB_ONLY | Web per-dataset 展示；Data 以 last-good 为成功锚 |
| ttl / 阈值 | `STALE_S`（建议 3600） | `ttl_s` | ALIGN | **概念同、域不同**——见 §3；不得混用同一数值 |
| probe_status | `probe_status` | — | DATA_ONLY | 探针总评；看板不强制 |
| dual_stable | `dual_stable`（+ `dual_stable_vs_last_good`） | — | DATA_ONLY | 双轮双测专属 |

**计数**：ALIGN=3 · RENAME_OK=3 · DATA_ONLY=3 · WEB_ONLY=2

---

## 2. 命名差异建议（不改两源文）

1. Data `last_good_ts_et` ↔ Web `last_good_et`：语义同；实现时可双向接受或统一 `last_good_et`。
2. Data `age_s_since_last_good` ↔ Web `age_s`：语义同；实现时 Data 回执可同时输出短名 `age_s`。
3. Data `this_run_empty` ↔ Web `empty`：语义同。
4. Data `cache_write`：写端专属；Web 不需同名字段，但读侧须遵守「empty 不刷绿」。
5. Web `ready`：看板专属；探针回执不强制。

---

## 3. TTL 域差异（钉死）

| 侧 | 阈值 | 用途 |
|---|---|---|
| **Data 探针** | 建议 `STALE_S=3600`（1h） | 相对中转例程频率（08:30/10:50 量级）标 `stale` |
| **Web 日频看板** | 交易日阈值 / `ttl_s≈2交易日`（或 `lag_trading_days>1`） | 纸面轨/行情新鲜度；可并存墙上秒 `age_s` |

**不得**把 `3600` 与「≈2 交易日秒数」混作同一阈值；实现时分域配置，另签确认。

---

## 4. 文末确认

- 未改 `probe5_small.py`、未改生产、未签 `.ok`、未消费 `9e4359f9`、live=false。
- 未改两源 A5 文；本文件为唯一新建对齐回执。

- 下行「整文件 sha256」= 不含该哈希值行（含本列表与标签）的 content sha；对完整落盘文件再跑 `sha256sum` 会因含哈希值行而不同，验收以 content sha 为准。

**整文件 sha256**：
e4b5090689fb3265c86489c693e79be72ba4ec0a51dd2e3df023f6df63d23aa6
