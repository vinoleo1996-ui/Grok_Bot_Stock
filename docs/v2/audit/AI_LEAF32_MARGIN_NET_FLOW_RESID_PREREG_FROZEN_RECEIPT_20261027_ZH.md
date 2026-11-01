# 叶32 净融资流入强度残差慢 α · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 03:50 ET（America/New_York；ISO `2026-10-27T03:50:46-04:00`）
- 动作：按主令 03:47 ET + Arch **PASS_WITH_CONDITIONS** `84df02b5` 落 **PREREG_FROZEN**
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf32*` / **未挂 QUIET** / **未** RESTORED forbid / **未**并入 `0087c928` / **未** git commit
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` | **`6b8de5e9`** | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `84df02b5` | MATCH |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `fad5911e` | MATCH |
| COVER DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` | `ebda2603` | MATCH |

## C1–C9 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 另窗冻结预注册（相对 DRAFT 升格） | **本文件** |
| C2 | 正式脚本尚未写 | `research/leaf32*` **ABSENT**（本拍禁落） |
| C3 | X2 前重算重叠 vs 19/25/27/30/31；**另须披露 vs margin_delta**；Jaccard≥0.7 硬拒 + ρ 强度 | 口径写死；正式重叠待完整 α |
| C4 | 残差清单写死 | flow_raw→SW L1 + log 流通市值 + mom20/vol20/logADV20（或钉死 capacity_adv）；缺→PIN_GAP；禁 Amihud/on_minus_id/CRR/hk_hold |
| C5 | FULLA 双钉 | HI_LIQ PRIMARY（mask hiliq_v1，median≥300）+ FULLA 研究（mask fulla_v1，median≥800）；PRIMARY 不得静默改 FULLA |
| C6 | decay KEEP | 近端=252d（gate v1.1）；`latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；失败→最多 WATCH/HOLD |
| C7 | forbid 六票 | `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30/31 `.ok`；禁 `--arch-ok-path` |
| C8 | rss=1500 + peak_proof | 写死 REQUIRED；未来执行硬 ABORT |
| C9 | 叶30 KEEP 另队 | `0087c928` **不并入** |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_margin_net_flow_resid_v1` |
| 公式 | net_rz=rzmre−rzche；flow_raw=mean_W(net_rz/float_mktcap_T−1)；α=−rank(flow_resid) |
| W / 再平衡 / 最少有效日 | 20 / 20 / ≥15 |
| X2 窗 | 2024-06-03 → 2026-10-09 |
| 成本 | 30bp |
| 边界 | ≠hk_hold/northbound；≠Δrzye margin_delta 复刻；≠Amihud/on_minus_id/CRR/应计 |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗。≠X2 ACCEPT。勿报 Leo。

live=false.
