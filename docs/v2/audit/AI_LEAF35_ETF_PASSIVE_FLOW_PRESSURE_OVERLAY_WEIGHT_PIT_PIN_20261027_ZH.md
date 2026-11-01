# 叶35 PIN（C3）— 指数权重 synthetic available_at / 份额 PIT 冻结前钉

- 角色：QuantLab AI
- 时点：2026-10-27 13:03 ET（ISO `2026-10-27T13:03:36-04:00`）
- 触发：主令 2026-10-27 ~12:57 ET 择 **FROZEN**（不 HOLD）；Arch who_pays 只审 **PASS_WITH_CONDITIONS** 回执 **`ee7ec307`** → C3 须写死权重 asof 升级（方案 A）+ 份额 `available_at≤t`
- 状态：**PIN 决议**；并入 PREREG_FROZEN 正文后 PIN_GAP（C3）关闭条件 = 本钉全文入 FROZEN
- EXECUTED=false；ok_requested=false；live=false；leo_notify=false；≠X2 ACCEPT
- **本拍未**签 `.ok` / **未**挂 QUIET / **未**实跑 α / **未**落 `research/leaf35*`

## 0. 只读核（本机实测；未联 α / 未读收益）

### 0.1 指数权重表（无 `available_at` → 须方案 A）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/index_members/index_weight_csi300_500_1000.parquet` |
| 行数 | **189,000** |
| 列（实测） | `index_code, con_code, trade_date, weight` |
| sha256 全长 | `d543a485959d6b579a2c5a26e18c3f7afea7a1047e308367588729c1f69bbd39` |
| sha8 | **`d543a485`** |
| `index_code` 取值 | `000300.SH` / `000905.SH` / `000852.SH`（仅此三） |
| `trade_date` 形态 | **月末点**（n=105；首 `20180131` → 末 `20260930`；多为月末/月末附近交易日） |
| `available_at` | **ABSENT**（列不存在） |
| 权重单位 | COUNT/JSON 检测 = **percent_div100**（`weight_month_sum_median_000300=100.0`） |

结论：权重表 **无 PIT `available_at`**；COUNT 用「月末 `trade_date` 向后 asof」= **APPROX**。**禁**静默沿用该 APPROX 当 PIT 完备。

### 0.2 宽基份额流主表（有 `available_at`）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet` |
| 行数 | **14,258** |
| 列（实测） | `ts_code, trade_date, fd_share, nav_ann_date, unit_nav, adj_nav, share_wan, d_share_wan, flow_est_wan_yuan, share_available_at, nav_available_at, available_at` |
| sha256 全长 | `a3eac35b91ae78a9cd152a7e68fb75a9274c6a32a1bfa7550f6ada88c45232bf` |
| sha8 | **`a3eac35b`** |
| 宽基三件套在表 | `510300.SH` / `510500.SH` / `512100.SH` **PRESENT** |
| `available_at` | **PRESENT**（`timestamp[us]`） |

校验表（非 PRIMARY 强制）：`data/v2/etf/share_pit/etf_share_flow_pit_all.parquet` sha8 `c6279f56`（1,581,727 行）。

### 0.3 交易日历（方案 A 合成 `available_at` 用）

| 项 | 值 |
|---|---|
| 路径 | `data/v2/calendar/trade_cal_sse_pit.parquet` |
| 列 | `cal_date, is_open, pretrade_date, available_at` |
| 行数 | 8,035 |
| sha8 | **`fa4260b8`** |
| sha 全长 | `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` |

## 1. 冻结写死（PRIMARY — C3 方案 A）

### 1.1 宽基 ETF↔指数映射（钉死）

| ETF | 指数 |
|---|---|
| `510300.SH` | `000300.SH` |
| `510500.SH` | `000905.SH` |
| `512100.SH` | `000852.SH` |

**禁**行业/主题 ETF 作主轴（仅上表三件套）。

### 1.2 权重 synthetic `available_at` — **方案 A（共签）**

对权重表每一月末点行，其 `trade_date = YYYYMMDD`（点值日）：

1. 取该 `trade_date` 所在自然月的 **下一自然月**。
2. 在 `trade_cal_sse_pit` 中找该下一自然月内 **首个 `is_open=1` 的交易日** `D*`（**用交易日历，不用纯日历日**）。
3. 合成：
   ```
   weight_available_at := D* 当日 09:00:00 Asia/Shanghai
   ```
   （实现可用 timezone-aware timestamp；与日历表 `available_at` 惯例对齐「开市前 09:00」）。
4. 再平衡日 \(t\)（交易日；比较时将 \(t\) 视为该日会话时点，**约定 \(t\) 日可用 = `weight_available_at ≤ t日 15:00 Asia/Shanghai` 或实现上 `date(weight_available_at) ≤ t` 且若同日则须 `weight_available_at` 的时钟 ≤ 决策时点；**PRIMARY 实现钉**：`weight_available_at ≤ timestamp(t, 15:00 Asia/Shanghai)`，与份额合取前先各自满足）。
5. asof 选取：在满足 `weight_available_at ≤ t_ts` 的月末权重点中，取 **最新** `trade_date` 点的 `weight`（向后 asof **仅**在已合成 PIT 约束下允许）。

**明确禁止**：
- **禁**静默沿用「月末 `trade_date` 向后 asof、无视合成 `available_at`」当 PIT 完备（COUNT APPROX 仅历史对照）。
- **禁**用纯自然月「次月 1 日」而跳过交易日历（本钉 = **次月首个交易日**）。
- **禁**在 `weight_available_at > t_ts` 时偷看该月末点。

### 1.3 份额表 PIT（写死）

- 路径 PRIMARY：`etf_share_flow_pit_major.parquet`
- 再平衡日 \(t\)：**仅**用 `available_at ≤ t_ts` 的行（`t_ts` = `timestamp(t, 15:00 Asia/Shanghai)` 同 §1.2）。
- 流量代理：优先 `flow_est_wan_yuan`（有限）；缺则回退 `d_share_wan`（与 COUNT/JSON 同口径）。
- **严禁**偷看 `available_at > t_ts`。

### 1.4 合取（权重 × 份额 → pressure）

对 ETF \(e\)、成分 \(i\)、再平衡日 \(t\)：

```
pressure_raw(i,t) = Σ_{e ∈ {510300,510500,512100}}
    w(i, index(e), asof_PIT(t)) × flow_est_proxy(e, t)
```

其中：
- `w(...)` 仅来自满足 §1.2 的权重 asof；
- `flow_est_proxy` 仅来自满足 §1.3 的份额行；
- 权重单位按 COUNT：`percent_div100`（表内多为百分数，入算前 `/100` 使权重和≈1；与 JSON `weight_unit_detected` 对齐）；
- 任一 ETF 当日份额不可得 → 该 ETF 项为 0（不填假流量）；三件套皆不可得或权重不可映射 → 名 \(i\) **不进** overlay 有效集（不填假 0 pressure）。

### 1.5 与 COUNT APPROX 的关系

| 项 | COUNT（APPROX） | 本 PIN / FROZEN |
|---|---|---|
| 权重 asof | 月末 `trade_date` 向后 asof（无 `available_at`） | **方案 A 合成 `weight_available_at`** |
| 份额 | `available_at≤t` | **同**（写死） |
| 映射 / top_q / 公式核 | 三件套；q=0.20；Σ w×flow | **同** |
| gate_pass | true（APPROX） | **≠** X2 ACCEPT（C12） |

正式构建须按本 PIN 重算覆盖/重叠；**不得**声称 COUNT APPROX 已等于方案 A PIT。

## 2. 与 COUNT / Arch 对齐

| 钉 | sha8 | 本 PIN |
|---|---|---|
| Arch who_pays 审 C3 | `ee7ec307` | 共签方案 A；禁静默 APPROX |
| COUNT RECEIPT | `cbca88e7` | 同三件套/公式核；升级权重 PIT |
| COUNT JSON | `a17b75fb` | 同 `etf_index_map` / `pressure_raw` 口径 |
| WHO DRAFT §2/§4 | `05942769` | 同机制意向；本钉落实方案 A |
| 计数脚本（迁仓） | `4e964d40` | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` |

## 3. 禁

- 本拍不签 `.ok`；不挂 QUIET；不实跑完整 α；不联表读收益选 q/方向
- 禁静默沿用月末向后 asof 当 PIT 完备；禁改映射；禁行业 ETF 主轴
- 禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票
- 禁改叶33 正式 `afbbe7e7`；叶32 HOLD `45dd87dc` / 叶34 HOLD CLOSED `178e90e9` 不回撤
- 禁落 `research/leaf35*`（C2 另窗）

## 4. 下一跳

本决议并入 `AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_*.md` → 主交 Arch **只审 FROZEN** → 另窗正式构建脚本（C2）。
