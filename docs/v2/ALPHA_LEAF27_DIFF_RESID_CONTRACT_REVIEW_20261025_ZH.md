# 叶27 · Alpha 残差契约短审（DIFF / impl；非闸门裁决）

- **日期**：2026-10-25 ≈06:41 ET · America/New_York
- **作者**：QuantLab Alpha
- **范围**：只审残差第 5 步 / 暴露钉对齐；**不是** ACCEPT 闸审（无独立 `.ok`+X2）
- **锁**：`live=false` · 不申 .ok · 不挡叶25

## 核验物

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| DIFF | `e3cd4bf1…` | `e3cd4bf14572e382f1ef15afde877dfa9d50afce83c868540b2765102a6c1633` | **MATCH** |
| impl pin | `1cb516bb…` | `1cb516bb686be41458a2af6014449c6bf353abbc77a29f2950f921afc6406b49` | **MATCH** |
| 脚本草案 | `0c4bbcc7…` | `0c4bbcc79b4a0a701128b29bb10ceffa1f72d317472c98a6d70dfa54f12160a2` | **MATCH** |
| Alpha 暴露钉 | `5e720335…` | （引用全长一致） | **MATCH** |
| 权重表 | `3b288c83…` | 脚本常量 + `assert_pinned_sha` | **MATCH** |

## 残差第 5 步对齐

| 钉要求 | 脚本/DIFF | 审 |
|---|---|---|
| 暴露=`target_weight` | `load_capadv_target_weight` 只读该列；`exposure_col="target_weight"` | ✓ |
| 路径 HI_LIQ 权重表 | 常量路径 MATCH | ✓ |
| sha 运行时断言 | `assert_pinned_sha(..., CAPADV_HILIQ_SHA)` | ✓ |
| 缺失→0 | `cap_day.get(c, 0.0)` | ✓ |
| 剔 510300.SH | load 时 `!= BALLAST` | ✓ |
| 活跃仅 Jaccard | 文案+impl §D；OLS 用连续权重 | ✓ |
| 禁 ADV/`adv_fail` | DIFF 首页与 impl 明示禁止 | ✓ |
| `α_raw=−ivol` | `alpha_raw = -ivols_a` | ✓ |

## 裁定

**RESID_CONTRACT_PASS**（暴露钉闭合；可交 Arch 另窗审脚本）。

**非动作**：不发 ACCEPT/WATCH/FAIL；不消费任何 `.ok`；不跑实数据；叶25 优先不变。

## 旁注

- Arch 预告已并入钉且 CLOSED（Arch 称现盘 sha `31462908…`）——Alpha 以暴露钉 `5e720335…` 为准核对脚本。  
- FULLA 权重路径仅可选对照，主规格仍 HI_LIQ。  
- 脚本仅 `/tmp py_compile`；实跑须 Arch 独立 `.ok`。

live=false；promotion_approved=false。
