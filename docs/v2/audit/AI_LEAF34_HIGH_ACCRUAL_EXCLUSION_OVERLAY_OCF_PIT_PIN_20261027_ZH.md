# 叶34 PIN（C3）— ocf_to_profit PIT / NP≤0 / period_basis 冻结前钉

- 角色：QuantLab AI
- 时点：2026-10-27 10:03 ET（ISO `2026-10-27T10:03:09-04:00`）
- 触发：主令 2026-10-27 09:56 ET 择 FROZEN（不 HOLD）；Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`9d8a2f9e`** → C3 须写死 ocf/PIT/NP/period_basis
- 状态：**PIN 决议**；并入 PREREG_FROZEN 正文后 PIN_GAP（C3）关闭条件 = 本钉全文入 FROZEN
- EXECUTED=false；ok_requested=false；live=false；leo_notify=false；≠X2 ACCEPT
- **本拍未**签 `.ok` / **未**挂 QUIET / **未**实跑 α / **未**落 `research/leaf34*`

## 0. 日表只读核（本机实测；未联 α / 未读收益）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet` |
| 行数 | **9,754,991** |
| 列（实测） | `trade_date, instrument_id, ts_code, e_end_date, n_cashflow_act, net_profit, n_income_attr_p, e_available_at, denom_small, np_negative, ocf_to_profit, ocf_to_profit_attr, period_basis, source, schema` |
| sha256 全长 | `f9faf7e7a719e7163c9aba3b43511887b52f622088cd7243f96262bfc4407a95` |
| sha8 | **`f9faf7e7`** |
| `period_basis` 取值 | `YTD_cumulative` 与 null（n_unique=2） |
| `denom_small` | False≈9,658,952；True≈93,670；null≈2,369 |
| `np_negative` | False≈7,910,381；True≈1,842,241；null≈2,369 |
| `ocf_to_profit` 有限 | ≈9,658,875（nan≈96,116） |

结论：日表列齐；可作 PRIMARY CF-accrual 代理源；**非** BS `WC_ACC/TA`。

## 1. 冻结写死（PRIMARY — C3）

1. **日表路径唯一（PRIMARY）**：`data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（只读；与 COUNT APPROX `806e1758` / JSON `9730d432` **同口径**）。
2. **PIT**：再平衡日 \(t\) 仅用 `e_available_at ≤ t` 的 as-of 行；**严禁**偷看 `e_available_at > t`。
3. **有效行**（合取；与 COUNT 一致）：
   - `ocf_to_profit` **有限**（非 NaN/Inf）
   - `denom_small = false`
   - `net_profit > 0`
   - `np_negative = false`
   - **NP≤0 一律剔除**（含 `net_profit≤0` 或 `np_negative=true`；不进 overlay 有效集，**不填假 0**）
4. **`period_basis`（PRIMARY 接受）**：
   - 日表现有口径 = **`YTD_cumulative` / YTD-ish**（列值以表为准；null 行不进有效集除非脚本另钉并补丁）
   - **接受理由**：与 COUNT APPROX（`accrual_cf_proxy=1−ocf_to_profit` from 本日本表；COUNT 文钉 YTD-ish OCF/NP）**同口径**，避免静默改季表/TTM 造成计数—冻结分叉
   - **若日后改季表 / TTM / 非 YTD**：须另补丁文件 + 重计数闸；**不得静默改**本钉
5. **主定义**：
   ```
   accrual_cf = 1 − ocf_to_profit   # 仅 NP>0 有效行
   ```
   （等价于 (NP−OCF)/NP 当 NP>0）
6. **PRIMARY 不用** BS `WC_ACC/TA`（Sloan / accrual_quality 分子）：
   - BS 路径 = **可选对照默认 OFF**
   - 启用须另补丁 + 重计数 + 重验 vs 叶19/25 Jaccard；不得静默升 PRIMARY

## 2. 与 COUNT / Arch 对齐

| 钉 | sha8 | 本 PIN |
|---|---|---|
| Arch who_pays 审 C3 | `9d8a2f9e` | 写死 (a)(b)(c)(d) |
| COUNT RECEIPT | `806e1758` | 同 valid 行 + YTD-ish；NP≤0 已剔 |
| COUNT JSON | `9730d432` | 同 APPROX 代理 |
| WHO DRAFT §2/§4 | `fa6aa2e3` | 同公式意向 |

## 3. 禁

- 本拍不签 `.ok`；不挂 QUIET；不实跑；不联表读收益选 q/方向
- 禁静默改 period_basis / 改季表/TTM / 改用 BS WC 当 PRIMARY
- 禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票 + `81521fb5`；`0087c928` 另队
- 禁改叶33 正式 `afbbe7e7`；叶32 HOLD `45dd87dc` 不回撤

## 4. 下一跳

本决议并入 `AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_*.md` → 主交 Arch **只审 FROZEN** → 另窗脚本（C2）。
