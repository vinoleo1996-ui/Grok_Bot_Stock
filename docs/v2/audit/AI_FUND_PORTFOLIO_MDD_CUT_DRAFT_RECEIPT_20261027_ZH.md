# RECEIPT · fund who_pays 组合层降 MDD DRAFT/PREREG

- 角色：QuantLab AI（执行器）
- 时点：**2026-10-27 22:56 ET**（America/New_York）
- **结论：DRAFT READY**
- **EXECUTED=`false`**
- **≠ACCEPT**；live=false；leo_notify=false

---

## 摘要

| 项 | 值 |
|---|---|
| DRAFT 路径 | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` |
| DRAFT sha8 | `eeccb25e` |
| 本 RECEIPT 路径 | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_RECEIPT_20261027_ZH.md` |
| 主候选 | **`V_BALLAST_MIX`**（stock=0.50 / core·510300=0.50） |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 对照 | `V_HOLD_GATE` / `V_IND_SIZE` / `V_VOL_SCALE` |
| 目标闸 | 主闸 abs(MDD)≤25% 且 CAGR≥C0；对照报 abs(MDD)≤15% |
| 下一跳 | **交主→Arch 只审**；禁自开 Eng/BS/X2 |

---

## 盘证 MATCH（开写前）

FROZEN `303e0185` · ArchFROZEN `bcbe4b72` · mask `6ab6a305` · Eng `b013a7a8` · Arch PASS_WC `694b9a80` · CONSUMED `3e2a9b9c` · WHO `547b246e` · ALLA `724e1df5` · C2 events `81afda13` · weights `601c5cf6` · summary `0d1ddcb0` · 叶38旁线 `c01c2034` — **全部 MATCH**。

---

## 禁项回执

| 禁项 | 回执 |
|---|---|
| 未 RESTORED `f08ce32c` | **是** |
| 未自开 Eng/BS/X2 | **是** |
| 未改 WHO/ALLA 事件条款 | **是** |
| 未 mid_large 主口径 | **是** |
| 未混叶38 | **是** |
| 未挂 QUIET / 未自签 `.ok` | **是** |
| 未 git commit | **是** |
| 未按未跑收益调阈 | **是**（参数事先写死） |
| 未把 DRAFT 当 ACCEPT | **是** |

---

## 下一跳

**交主 → Arch 只审本 DRAFT**（`eeccb25e`）。过审后再由主令是否 Eng Book-Smoke。旁线叶38 `c01c2034` 维持。
