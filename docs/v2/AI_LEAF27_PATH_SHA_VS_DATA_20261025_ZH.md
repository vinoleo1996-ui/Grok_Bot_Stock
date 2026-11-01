# AI 对照：叶27 条件3 路径 sha（checklist × Data 盘点）

- **时刻**：2026-10-25 07:14 ET（America/New_York）
- **角色**：QuantLab AI
- **对照**：checklist `eef4eb4e…` × Data `acb8d3e0…`（MATCH=9）
- **包钉**：脚本 `7a5f756c…` / DIFF `e2ed0fc8…` / impl `a532e6db…` / 闭合 `f4327917…`
- **窗**：叶25 闭后 **≥10:50 ET** Arch 另窗；**本轮不申 .ok**；不复用叶25钉；live=false

## 结论

**AI_CONSTANTS_VS_DATA = ALL_MATCH（主路径）**

脚本三钉 sha（MKTCAP / ETF / CAPADV_HILIQ）与 Data 现盘字节 **全 MATCH**；OHLC 目录覆盖 + 样本 `20180102` sha MATCH IMPL；limit 双目录 MATCH（BJ@1c85 空值旁记已接受）；suspend 掩码列齐。条件3 数据侧可交 Arch 另窗重钉。**AI 本轮不申 `.ok`。**

## 输入核验（本对照时）

| 项 | 路径 | 期望 | 现盘 | 判定 |
|---|---|---|---|---|
| script | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09f…` | `7a5f756c0a1ab09f…` | **MATCH** |
| diff | `docs/v2/AI_LEAF27_ON_MINUS_ID_IDIO_IVOL_DIFF.patch` | `e2ed0fc88bfe38c0…` | `e2ed0fc88bfe38c0…` | **MATCH** |
| impl | `docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md` | `a532e6db956600ab…` | `a532e6db956600ab…` | **MATCH** |
| closure | `docs/v2/AI_LEAF27_LIMIT_HIT_CLOSURE_20261025_ZH.md` | `f43279177c6fe8c3…` | `f43279177c6fe8c3…` | **MATCH** |
| data_pin | `docs/v2/audit/DATA_LEAF27_PATH_SHA_DISK_PIN_20261025_ZH.md` | `acb8d3e0386b5f33…` | `acb8d3e0386b5f33…` | **MATCH** |
| checklist | `docs/v2/AI_LEAF27_PATH_SHA_CHECKLIST_PREP_20261025_ZH.md` | `eef4eb4e7cbded3d…` | `eef4eb4e7cbded3d…` | **MATCH** |

## 常量 ↔ Data 盘点

| 常量/项 | AI checklist 期望 | Data 现盘 | 判定 |
|---|---|---|---|
| MKTCAP_SHA | `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` | `346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef` | **MATCH** |
| ETF_SHA | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | **MATCH** |
| CAPADV_HILIQ_SHA | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` | `3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d` | **MATCH** |
| OHLC sample 20180102 | `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631` | `22720a21387636fdc92f9946da7db5298e94e4f4f8e49b67e9e9083d9ba60631` | **MATCH** |
| MASK HILIQ (Data 现盘) | `(脚本未钉 sha)` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | **INFO_Data_only** |
| suspend_flags_v2 | `(IMPL 辅助)` | `ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377` | **MATCH_IMPL_aux** |
| CAPADV_FULLA / SW L1 | `(checklist 有路径；脚本未钉 sha；Data 本回执未列)` | `—` | **NOT_IN_DATA_PIN_HI_LIQ_primary** |

## 旁记（不阻断条件3）

1. 1c85 BJ `limit_*` 值空 —— 脚本 `exclude_hit_or_unknown` 已闭合；Data 旁记。  
2. mktcap 无 `available_at` —— 主豁免 `b39954c3…` 已钉。  
3. CAPADV_FULLA / SW L1：脚本运行可读但本包主钉为 HI_LIQ；Data 本回执未列 FULLA 权重 sha —— 若 `.ok` 窗含 FULLA 腿，请 Data/Arch 补列。  
4. HILIQ mask 现盘 sha `c5433e80…`：脚本未 `assert_pinned_sha`；建议 Arch `.ok` 窗旁钉或维持列级即可。

## 非动作

- 不申 `.ok`；不跑 sealed/X2；不挡叶25@10:00；不消费补跑 `9e4359f9`  
- live=false；promotion_approved=false

## 下一步

Arch ≥10:50 ET 另窗签叶27 `.ok` 时消费本对照 + Data `acb8d3e0…` + 包钉四件套。
