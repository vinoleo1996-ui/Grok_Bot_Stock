# 叶33 限售解禁压力残差慢 α · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 05:56 ET（America/New_York；ISO `2026-10-27T05:56:15-04:00`）
- 动作：按主令 05:52 ET + Arch **PASS_WITH_CONDITIONS** `55531e12` 落 **PREREG_FROZEN**
- **未实跑** / **未申 `.ok`** / **未落** `research/leaf33*` / **未挂 QUIET** / **未** RESTORED forbid / **未**并入 `0087c928` / **未** git commit / **未** SendToUser / **未** SendToAgent
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | **`8ed43721`** | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `55531e12` | MATCH |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `1032477d` | MATCH |
| COVER DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` | `61d9f656` | MATCH |
| PIN 决议 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | MATCH（选径 a；FROZEN 升级 (a)+加价） |

## C1–C10 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | 完整预注册（符号/H/H_back/W/再平衡/失效写死） | **本文件**：α=−rank(pressure_resid)；H=20；H_back=5；W=20；最少有效日≥15；再平衡 20d；PIT available_at≤t |
| C2 | 正式脚本另窗 | `research/leaf33*` **ABSENT**（本拍禁落） |
| C3 | PIN_GAP=`float_ratio` 选 (a)+加价 | **写死**：unlock_mv=Σ float_share×close_T−1；unlock_raw=unlock_mv/float_mktcap_T−1（元/元 无量纲）；表内 float_ratio **PRIMARY 禁用**；**不是**改用 (b) |
| C4 | X2 前重算重叠 vs 19/25/27/30/31/32；另披露 vs margin_delta/hk_hold/moneyflow；Jaccard≥0.7 硬拒 + ρ 强度 | 口径写死；正式重叠待完整 α |
| C5 | 残差清单写死 | pressure_raw→SW L1 + log 流通市值 + mom20/vol20/logADV20（或钉死 capacity_adv）；缺→PIN_GAP；禁 两融/Amihud/on_minus_id/CRR/hk_hold/float_ratio |
| C6 | FULLA 双钉 | HI_LIQ PRIMARY（mask hiliq_v1，median≥300）+ FULLA 研究（mask fulla_v1，median≥800）；PRIMARY 不得静默改 FULLA |
| C7 | decay KEEP | 近端=252d（gate v1.1）；`latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`） |
| C8 | forbid `5774bb6e`+二十票 | 完整列出；禁复用叶25/27/30/31/32 `.ok`；禁 `--arch-ok-path` |
| C9 | rss=1500 + peak_proof | 写死 REQUIRED；未来执行硬 ABORT；禁抬 |
| C10 | `0087c928` 另队；叶28/29 不夹带 | **不并入**；本拍未审 |

## C3 加价公式（摘要）

```
unlock_mv_{i,t} = Σ_j float_share_{i,j} × close_{i,T−1}
unlock_raw_{i,t} = unlock_mv_{i,t} / float_mktcap_{i,T−1}
pressure_raw = mean_W(unlock_raw)  # W=20
```

- float_share：股；close：元/股（脚本钉价列）；float_mktcap：元 → unlock_raw **无量纲**
- 表内 float_ratio：PRIMARY 禁用；对照默认 OFF
- 由 PIN `4e17ccfc` 选径 (a) 升级加价；**不是** (b)

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_share_unlock_pressure_resid_v1` |
| 公式 | (a)+加价 → pressure_raw=mean_W(unlock_raw)；α=−rank(pressure_resid) |
| H / H_back / W / 再平衡 / 最少有效日 | 20 / 5 / 20 / 20 / ≥15 |
| X2 窗 | 2024-06-03 → 2026-10-09 |
| 成本 | 30bp |
| 边界 | ≠hk_hold/northbound/moneyflow；≠叶32 两融；≠Amihud/on_minus_id/CRR/应计；≠float_ratio PRIMARY |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再谈脚本窗。≠X2 ACCEPT。勿报 Leo。

live=false · EXECUTED=false.
