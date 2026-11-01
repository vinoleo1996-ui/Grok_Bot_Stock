# 叶37 PIN（C3=B）— IMAX_proxy 交付定义冻结钉

- 角色：QuantLab AI
- 时点：2026-10-27 17:00 ET（America/New_York；ISO `2026-10-27T17:00:00-04:00`）
- 触发：主裁 **叶37 出 FROZEN GO**；Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`4a074f0a`** → C3 二选一择 **(B)**：冻结 `IMAX_proxy` 为交付定义并持续 APPROX 披露
- 状态：**PIN 决议**；并入 PREREG_FROZEN 正文后 C3 关闭条件 = 本钉全文入 FROZEN
- EXECUTED=false；ok_requested=false；live=false；leo_notify=false；≠X2 ACCEPT
- **本拍未**签 `.ok` / **未**挂 QUIET / **未**实跑 α / **未**落 `research/leaf37*` / **未**改叶33/35 正式脚本

## 0. 只读核（本机；未联 α / 未读收益）

### 0.1 面板（PRIMARY 价格源）

| 项 | 值 |
|---|---|
| 路径族 | `output/ai_factory/panel_cache_v2_resumefix/cs_panel_YYYY.parquet`（build_version=`cs_panel_v2_resumefix`） |
| COUNT 已用年 | 2023–2026（预热+X2） |
| 实测列（2024） | `date, instrument, hiliq, fulla, adv20_yuan, ret, ret_on, close, ind, logmv, is_resume_day, …` |
| **PRIMARY 用列** | `date, instrument, hiliq, ret, ret_on`（及与 HI_LIQ 掩码合取） |
| `open` / `pre_close` | **ABSENT**于 panel 列；`ret`/`ret_on` 已为叶24 预注册定义之等价物 |
| 定义对齐叶24 | `ret = close/pre_close − 1`；`ret_on = open/pre_close − 1`（面板预计算；本 PIN **不**另从 ohlcv 重算，除非另窗升级） |
| COUNT 年 sha8 | 2023=`6588573a`；2024=`bbbfe95a`；2025=`164cde98`；2026=`8df4afec` |

### 0.2 HI_LIQ 掩码

| 项 | 值 |
|---|---|
| 路径 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` |
| sha8 | **`c5433e80`** |
| 用法 | `in_universe=True` ∩（实现可再合 panel `hiliq=True`）→ 可算池 |

### 0.3 对照（非交付输入）

| 项 | 路径 / sha8 |
|---|---|
| 叶18 α | `…/leaf18_overnight_idio_ivol/alpha_HILIQ_x2_20261014_205327.parquet` / `1a42f9e8` |
| 叶18v α | `…/leaf18v_…/alpha_HILIQ_x2_20261014_212630.parquet` / `237e760c` |
| 叶27 α | `…/leaf27_…/alpha_HILIQ_x2_20261025_224033.parquet` / `652b8a68` |
| 叶24 α | `…/leaf24_imax_intraday/alpha_HILIQ_{YYYY}.parquet` |

**禁**把上表 α 当本叶主输入（仅 Jaccard/ρ）。

## 1. C3=(B) 冻结写死：`IMAX_proxy` = 交付定义

### 1.1 公式（FROZEN）

```
r_id(i,t)      = (1 + ret(i,t)) / (1 + ret_on(i,t)) − 1
IMAX_proxy(i,t)= mean( largest 5 finite r_id(i,·) in trading days [t−19, t] )
                 要求窗口内有效（有限 r_id 且名∈当日 HI_LIQ 可算集）日数 ≥ 15
                 否则 IMAX_proxy 缺失（该名该日不可算）
```

| 项 | **FROZEN（C3=B）** |
|---|---|
| 窗口 | 20 交易日（含 t）；对齐叶24 IMAX 窗长 |
| K | 最大 **5** 日均值 |
| min_valid | **≥15** |
| **full_residual_e_id** | **`false`** |
| 残差路径 | **本拍不采用**叶24 全路径：`e_id = CS OLS(r_id ~ SW L1 + logmv_{t−1})` |
| APPROX | **持续披露**：交付 IMAX = `IMAX_proxy`（raw `r_id`），**不是**全残差 `e_id` IMAX |
| 剔除 | `H_t = {i ∈ HI_LIQ_t ∩ computable_t : IMAX_proxy(i,t) ≥ Q_{1−0.20}(·)}` |

### 1.2 明确禁止

- **禁**静默把 `IMAX_proxy` 当作叶24 全残差 `e_id` IMAX 对外宣称
- **禁**本 FROZEN 窗内「悄悄」改用全 `e_id` 而不改文件/不重跑计数闸
- **禁**从收益反选窗长 / K / min_valid / q
- **禁**用 `inquiry_reply` / 精神叙事 / 情绪因子替换本定义

### 1.3 升级纪律（另窗）

若日后升为叶24 全路径 `e_id` IMAX：

1. **须另窗**修订 PIN + PREREG（新文件或补丁），明示 `full_residual_e_id=true`
2. **须重跑** HI_LIQ 计数闸（覆盖 + vs 叶18/18v/27 Jaccard 硬拒 + 披露叶24/34/35/36）
3. **须** Arch 再审；**不得**沿用本拍 COUNT `2217f580` 当升级后已证
4. 本 PIN（C3=B）在升级生效前保持为交付定义

### 1.4 与 COUNT APPROX 的关系

| 项 | COUNT（已跑） | 本 PIN / FROZEN |
|---|---|---|
| IMAX | `IMAX_proxy` raw r_id 20d top-5 | **同 = 交付定义（C3=B）** |
| full_residual_e_id | false | **false** |
| gate_pass | true（APPROX） | **≠** X2 ACCEPT（C12） |
| 正式构建 | — | 按本 PIN 实现 mask-only；可复用计数脚本口径但**非正式 α 构建** |

## 2. 与 Arch / 上游对齐

| 钉 | sha8 | 本 PIN |
|---|---|---|
| Arch who_pays 审 C3 | `4a074f0a` | 择 **(B)** proxy 冻结；持续 APPROX；不升级全 e_id |
| WHO / COVER / COUNT / SCRIPT / JSON | `0ed8e9d8` / `847245f8` / `154bc157` / `c10b735f` / `2217f580` | 口径对齐 |
| dig | `74234fca` | 上下文 |

## 3. 本拍非动作

- 未签 `.ok`；未挂 QUIET；未落 `research/leaf37*`；未跑 X2/Book-Smoke/完整 α
- 未改叶33 `afbbe7e7` / 叶35 `434ff42c`；未放宽叶36 覆盖阈；未开备选 B

live=false · EXECUTED=false · ok_requested=false · leo_notify=false.
