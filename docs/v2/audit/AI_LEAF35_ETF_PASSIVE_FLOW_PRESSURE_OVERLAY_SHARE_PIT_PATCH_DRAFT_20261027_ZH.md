# 叶35 Option B · 份额 PIT 口径补丁 DRAFT（推荐 B1）

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:59:25 ET（America/New_York）；ISO `2026-10-27T14:59:25-04:00`
- **状态**：**DRAFT ONLY** · EXECUTED=**false** · **未**改正式脚本 · **未** `patch -p` · **未**复跑 X2 · **未**申 `.ok` · **未**挂 QUIET · live=false · ≠X2 ACCEPT · ≠叶36 · leo_notify=false

## 0. 上游钉（落盘实测）

| 项 | sha8 | 全长 / 路径 | 状态 |
|---|---|---|---|
| Arch VTRUE CONSUMED_PASS | **现算 `0471f4f8`**（主钉曾报 `bc8f53d7`；**双记勿瞒**；以本表现算为准） | `0471f4f85c0b62eb69a64a88ef01c2e33a4acc56eb65e2bbc7562ec17f5b42e7` · `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_CONSUMED_PASS_20261027_ZH.md` | 文件存在；文内未自嵌 sha8 |
| consumed `.ok` | `00eec671` | `00eec671fc904ac745752070fd4b84b8939715d350d5b089dd5de09b6c19b291` · `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.00eec671.CONSUMED_PASS.20261027T1449ET.ok` | CONSUMED_PASS 归档 |
| QUIET lift | `9306ceff` | `9306ceffba28eca00ac9f61b7a393e43a9f3b989b3105004e6898d2c34b30ea5` · `output/loop/_lifted/RESEARCH_QUIET_leaf35_mapping_recon_vtrue_probe_CONSUMED_PASS_LIFTED_20261027T1449ET.lock` | live QUIET **ABSENT** |
| live `.ok` | — | `output/ai_factory/*.ok` 计数=**0** | ABSENT |
| VTRUE RUN RECEIPT | `107a72b1` | `107a72b1987d912d45bd490cf4d483711d49cd3e25e06723bc35c42379588c81` | DONE |
| VTRUE per-rebal JSON | `446b60d1` | `446b60d1ccba05bfd3837843b6d4712ca2e5aa3a56eff830092197bf55a3306a` · `output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/mapping_recon_vtrue_per_rebal.json` | 30/30 `share_avail_late` |
| VTRUE 探针 py | `2c2226e0` | `2c2226e00a232ad1caf61f9d456990e5b7abe2c0040976371d0036f5480cca67` | 只读 |
| PIN C3 | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` · `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | §1.3 份额**仅** `available_at≤t_ts`；**未**要求 `trade_date==rebal` |
| FROZEN | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | 份额 PIT=`available_at≤t_ts` |
| ArchFROZEN | `5a082d18` | `5a082d181f469ec49bab2efb73f6fb14976fc6d01a4a548de23eabe098cfd660` | PASS_WITH_CONDITIONS 入钉 |
| 正式脚本 | **`25ae4572`** | `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0` · `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | **本拍 UNCHANGED（禁改）** |
| 叶33 正式 | **`afbbe7e7`** | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` · `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | **不触** |
| VOID X2 / 旧 `.ok` | `dfafff28` / `10927bd9` | `_consumed/…X2_HILIQ.10927bd9.VOID…` | 禁 RESTORED |

> **CONSUMED 哈希双记**：主令钉现算 **`bc8f53d7`**；本拍实测 **`0471f4f8`** / 全长 `0471f4f85c0b62eb69a64a88ef01c2e33a4acc56eb65e2bbc7562ec17f5b42e7`。二者不一致 → **以现算为准**并双记；不臆改主文。

## 1. 根因（对照正式 `25ae4572` 只读）

正式实现比 PIN §1.3 **更严**，额外硬约束 `trade_date == rebal`，与「同日份额行 `available_at` 常晚于当日 15:00」合取 → 空压。

1. **`_load_etf_flows_window`（约 L812–851）**  
   - L843–844：`want = rebal_days` → `df = df[trade_date.isin(want)]`  
   - 预滤后窗口内**只剩再平衡当日**份额行。  
   - 读取仍为 `pq.read_table`（本 DIFF **不改**读取 API）。

2. **`_pressure_on_day`（约 L854–901）**  
   - L861：`day_etf = etf_df[etf_df["trade_date"] == d]`  
   - L865–868：再滤 `available_at_clock ≤ t_ts`  
   - 空 → `return None` → 主循环记 `pressure_empty_or_unmappable` → X2 `STOP_ZERO_MASK_ROWS`。

3. **VTRUE 证据（JSON `446b60d1`）**  
   - `n_rebal=30`；`empty_reason=share_avail_late` **30/30**  
   - 同日：`n_share_rows=3` 且 `n_share_rows_avail_le_tts=0`  
   - `n_share_rows_pin13_avail_only`≈4695–6405  
   - B 权重 schemeA=`n_weight_rows_schemeA=1800` **非主因**  
   - 只读样例（rebal=`2024-06-03`）：同日三只 ETF `available_at=2024-06-04 23:59`（>15:00）；PIN§1.3 可选 `trade_date=2024-05-31` 且 `available_at=2024-06-03 09:00`（≤15:00）。

## 2. 选项与推荐

| 选项 | 含义 | 本票态度 |
|---|---|---|
| **B1** | 对齐 PIN §1.3：取消 `trade_date==rebal` 硬过滤；在 `available_at≤t_ts`（且 `trade_date≤d`）中按 ETF 取**最新** `available_at` 行 | **推荐** |
| B2 | 保留 `trade_date==rebal`，放宽时钟 | **不推荐**（易踩 PIT 前视） |
| B3 | 修订 PIN/FROZEN 追认同日硬过滤 | 近 Option C；须主裁；本票不推 |

**本票推荐：B1。**

## 3. 拟改点（函数 / 行意图；仅提案）

### 3.1 `_load_etf_flows_window`

- **现状**：只保留 `trade_date ∈ rebal_days`。
- **B1 拟改**：`trade_date ∈ [min(rebal)−40d, max(rebal)]`；**不再** `isin(rebal_days)`。
- **不变**：`pq.read_table`；宽基三只；`flow_proxy` 口径；日侧 PIT。

### 3.2 `_pressure_on_day`

- **现状**：`trade_date==d` ∧ `available_at_clock≤t_ts`。
- **B1 拟改**：`available_at_clock≤t_ts` ∧ `trade_date≤d` → 按 ETF 最新 `available_at_clock`。
- **不变**：权重方案 A；空则 None；不填假流量。

### 3.3 明确不改

C4 mask-only；C5 top_q=0.20；C6 HI_LIQ；C8 forbid；C9 rss=1500+peak_proof；C11≠叶26；C12≠ACCEPT；C13 KEEP；叶33 `afbbe7e7`。

DIFF：`docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_SHARE_PIT_PATCH_DIFF_DRAFT_20261027.diff`（**DRAFT ONLY — DO NOT APPLY**）。

## 4. PIT 不前视论证（B1）

1. 决策时点仍 `t_ts=timestamp(rebal, 15:00 Asia/Shanghai)`。  
2. 只用 `available_at_clock ≤ t_ts`；严禁偷看更晚行。  
3. 附加 `trade_date ≤ d`，禁止未来交易日份额点。  
4. 合法行内最新 `available_at` = 标准 asof（非静默月末权重 asof）。  
5. 放宽的是非 PIN 的「必须同日 trade_date」；时钟约束不放松。  
6. 样例：`2024-05-31` 行在 `2024-06-03 15:00` 已公告，不前视。

## 5. 与 PIN `dd17044a` / FROZEN `be9fc459` 对齐表

| 条款 | PIN / FROZEN | 正式 `25ae4572` | B1 | B3 |
|---|---|---|---|---|
| 份额 PIT | 仅 `available_at≤t_ts`；未要求同日 trade_date | 额外 `trade_date==rebal` | **对齐 PIN** | 修订 PIN 追认同日 |
| 权重方案 A | 次月首个交易日 09:00 | 已实现 | 不变 | 不变 |
| 禁偷看 / 禁静默月末 asof | 写死 | 有 | 保持 | — |
| mask / top_q / C11 | 已钉 | 已钉 | 不降门 | — |

B1=对齐既有钉文；B3 才须主裁改钉。

## 6. 不降门

top_q=0.20；Jaccard≥0.7 硬拒；rss=1500 禁抬；peak_proof；C11 overlay≠叶26；≠X2 ACCEPT；KEEP 不解阻。

## 7. 落地门禁（本拍不执行）

Arch 只审本票 → 主令落新脚本（sha8≠`25ae4572`）→ Arch 审新脚本 → 主签**新** X2 `.ok`（禁 RESTORED `00eec671`+`10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票）→ 新窗执行。

本拍禁写 alpha/mask；禁改正式；禁自签；禁 QUIET；禁 Book-Smoke；禁复跑 X2；禁叶36。

## 8. 红线回执

正式仍 **`25ae4572`** / `25ae45723454423a31d4b0c6987c5eb0a2e8bb733c2506c2db67d628e91b4ad0`；叶33 **`afbbe7e7`**；DIFF 未应用；EXECUTED=false；≠X2 ACCEPT；≠叶36；leo_notify=false；live=false。
