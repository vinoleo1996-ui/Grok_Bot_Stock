# Alpha 验收 · D3 中大盘宇宙成员 PIT

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab Alpha  
**对应需求**：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md` §D3  
**门锁**：`promotion_approved=false` · **未跑 GP** · **未晋级密封**

---

## 裁决

**ACCEPT**（研究级可接）

满足：session / instrument_id / universe_id / available_at；可复现规则；默认剔微盘/北交所；**显式 ≠ CSI300**。进因子短清单 / 冲击闸 / 密封仍须另审。

---

## 核验路径

| 资产 | 路径 | 结果 |
|---|---|---|
| 成员 PIT | `data/v2/universe/mid_large_members_pit.parquet` | schema + 统计对齐 |
| 规则 | `data/v2/universe/MID_LARGE_RULE.md` | SSE+SZSE、剔 ST、前一日流通市值 top 50% |
| manifest | `data/v2/universe/mid_large_members_pit_manifest.json` | `explicit_not_csi300=true`；5 session 验收表 |

---

## Schema / PIT

列：`session`, `instrument_id`, `universe_id`, `available_at`, `float_mktcap_basis`, `basis_trade_date`

| 项 | 值 |
|---|---|
| rows | **5,552,904** |
| sessions | **2,856**（2015-01-06→2026-10-09） |
| instruments_union | **4,410** |
| universe_id | 仅 `mid_large` |
| available_at | 全部 session **09:00 Asia/Shanghai**；null=0 |
| 北交所/BJ | **0** |
| 显式 in_out 列 | **无**（成员表=在池；进出可由 session 差分派生 — 软注，不挡 ACCEPT） |

`basis_trade_date` = 前一开市日 → 开盘决策无同日市值泄漏（抽检 5 日均满足）。

---

## 抽样成员数（与 manifest 一致）

| session | n_members | min float_mktcap_basis | median |
|---|---:|---:|---:|
| 2018-06-29 | 1624 | 3.38e9 | 7.32e9 |
| 2020-06-30 | 1825 | 4.16e9 | 9.47e9 |
| 2022-06-30 | 2281 | 4.26e9 | 1.04e10 |
| 2024-06-28 | 2481 | 3.45e9 | 8.38e9 |
| 2026-06-30 | 2490 | 5.85e9 | 1.44e10 |

微盘抽检：上述会话 **below 1e9 / 3e9 = 0**（无微盘灌入）。

---

## ≠ CSI300

- 规则与 manifest 均写明 `universe_id=mid_large` **≠ CSI300**。
- 对照 `index_weight_csi300_500_1000` @2024-06-28：CSI300=300，mid_large=2481；重叠≈299；规模远大于成分指数 → **非 CSI300 贴标**。

---

## 明确未做

- 未跑 GP / 未晋级 / `promotion_approved=false`
- 未要求 Data 改规则为 CSI300
