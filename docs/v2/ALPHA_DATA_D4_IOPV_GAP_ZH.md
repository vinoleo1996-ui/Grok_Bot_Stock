# Alpha 验收 · D4 ETF IOPV（拒收缺口 ACCEPT）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab Alpha  
**对应需求**：`docs/v2/ALPHA_DATA_REQUESTS_QUANTMIND_20261012_ZH.md` §D4  
**门锁**：`promotion_approved=false` · **Alpha 不自建 / 不伪造 IOPV**

---

## 裁决

**GAP ACCEPT（拒收可接）** — 同意 Data **拒**；记为文档化硬缺口，非交付失败甩锅。

无历史 IOPV 源时，**禁止**用 NAV/收盘价伪造 IOPV。A2/折溢价臂继续按「无 IOPV」降级（收盘价/单位净值仅作弱代理且须显式标注）。

---

## 证据（盘内 + Data 状态单）

| 来源 | 结论 |
|---|---|
| `docs/v2/ALPHA_DATA_REQUESTS_STATUS_20261012.md` | `etf_iopv`/`fund_iopv`/`rt_fund_daily` → unknown_api；仅实时 `rt_etf_sz_iopv`（深市、无 start/end 史） |
| `output/d1/alpha_qm_d4_d5_d6_audit.json` | 早先探针：无历史；`fund_daily_has_iopv=false` |
| 仓内 `fund_daily` 样例（510300） | 列仅 OHLC/额量，**无 iopv** |
| 份额/NAV PIT | 已有；**不能替代 IOPV** |

---

## 残留与后续（非本拍强阻塞）

- 若日后有付费/交易所历史 IOPV 或可审计替代源，Data 另开单；Alpha 再验。
- D5（调样公告日）/ D6（配股 PIT）仍排队 — 本单不展开。

---

## 明确未做

- 未虚构 IOPV 文件  
- 未跑 GP / 未晋级
