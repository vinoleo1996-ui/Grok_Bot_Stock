# Arch 审阅：叶27 HI_LIQ 降内存包（lowmem v1）

- **角色**：QuantLab Arch（执行器）
- **时刻**：2026-10-25T11:37:31-04:00（America/New_York）
- **结论**：**PASS_WITH_CONDITIONS**
- **动作本回合**：**不签 `.ok`** · **不实跑**真实数据 · live=false · promotion_approved=false
- **禁复用**：VOID `.ok` `725be3e0…`（已归档 `_consumed/…725be3e0.VOID.20261025T1115ET.ok`）
- **rss 帽**：仍 **≤1500MB**；**禁抬帽**

## 1. 输入 sha256 核对（全长 MATCH）

| 件 | 路径 | 期望 | 盘证 | 结果 |
|---|---|---|---|---|
| DIFF 文 | `docs/v2/audit/AI_LEAF27_LOWMEM_DIFF_20261025_ZH.md` | `b1455e935c5b18aecd17ab0c9ba5cb3a30d68639760f435d0df377821c2c2d1c` | 同左 | **MATCH** |
| 封面 | `docs/v2/audit/AI_LEAF27_LOWMEM_COVER_20261025_ZH.md` | `1521e1a4eb91aa9954f28c3bbbf7d61333427739b27045f9a55025ec57c443a8` | 同左 | **MATCH** |
| 草案脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` | 同左 | **MATCH** |
| unified diff | `docs/v2/audit/AI_LEAF27_LOWMEM_V1_20261025.diff` | `2154b6fb60fa448da10e0eba620fa22096051d6d41cad69dbd8e02cc37ec055f` | 同左 | **MATCH** |
| 旧基线脚本 | `research/g1g5_on_minus_id_idio_ivol_alpha.py` | `7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6` | 同左 | **MATCH**（SUPERSEDED_FOR_LOWMEM_RUN） |
| ABORT 旁证 | `docs/v2/audit/ARCH_LEAF27_HILIQ_ABORT_RSS_20261025_ZH.md` | `37b63b8fb98739e86f3d5a0b2542ca3adc9627fe531566efd7082ef02d2e799d` | 同左 | **MATCH** |

## 2. 静态 / 重建

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/arch_leaf27_lowmem_v1_review.pyc` | **PASS**（未写 research `__pycache__`） |
| `--dry-compile-only` | **PASS**（rc=0；`live:false`；钉出 baseline `7a5f756c…`） |
| `/tmp` 隔离：`baseline.py` + 改写路径后的 unified diff → `lowmem_rebuilt.py` | **sha MATCH** `05bd81ea…`（`cmp` 与草案一致；**禁** live 仓 `git apply`） |
| 旧钉 `e2ed0fc8` / impl `a532e6db` | 按 DIFF 文标注 SUPERSEDED_FOR_LOWMEM / 契约仍对照；本审不重签 |

## 3. 条款表

| # | 要点 | 裁定 | 说明 |
|---|---|---|---|
| 1 | 内存策略真实降峰路径 | **PASS_WITH_CONDITIONS** | `DayFloatMap`（float32 并行数组+按日物化）、`LimitPanelCache(keep_sessions=cal_set)`、mask/capadv 日期跨度过滤、`mktcap.drop_before(T−1)`、列式 α 累积、`del+gc`、腿间清空。**仍**在 `run_one` 开头一次性 `load_mktcap_by_session(cal_set)`（窗内全历再裁），panel 按名整文件读后过滤——方向正确，**未证明**峰≤1500。 |
| 2 | 因子/α/β/W 零改 | **PASS**（附注） | 常量钉 MATCH：`MECHANISM_TAG`、β60/min40、W20/min15、`α_raw=-ivol`、`limit_policy=exclude_hit_or_unknown`、`exposure_col=target_weight`、残差序 SW→logMV T−1→β→capadv→ivol→domain。helper 相对基线仅 `dtype=np.float64` / docstring 裁剪，语义等价。存储侧 mktcap/capadv **float32** 属 IO 布局；另窗回执须披露可能的边际数值差。 |
| 3 | universe 仅 HILIQ | **PASS** | CLI 拒 `--universe FULLA\|both`（`FULLA_GAP`）；默认 HILIQ。FULLA 仍 **GAP**。 |
| 4 | rss≤1500 / 禁抬帽 | **PASS** | DIFF/封面/WARN 文案钉 1500；**无**抬帽申请。`.ok` 须硬钉 rss_limit=1500。 |
| 5 | PIT / 泄漏 | **PASS** | `mktcap_T_minus_1` 仍只用 `sessions[di-1]`；`drop_before` 只丢严格早于 keep_from 的日；`keep_sessions` 不引入日历外未来板价；warm_start 与基线同构。 |
| 6 | 分窗 ops | **PASS（推荐强制）** | `--window both` 保留但 **WARN**+腿间 `gc`；**Arch 推荐另窗申签时强制单窗**：先 `HILIQ --window x2`，`sealed` 另进程/另签。 |
| 7 | 禁复用 VOID `.ok` | **PASS** | `725be3e0` 已 VOID；本包不得消费；另窗须**新** code_change/run `.ok`，脚本钉 `05bd81ea…`。 |
| 8 | `_prune_hist`（每~40 日） | **COND** | 基线无此剪枝；长时间不进日环 `codes` 的标的可能丢 β/ε 历史，回流时与基线路径略异。可接受为降内存，但须在回执披露；若主要求 bit 级对齐则禁用/收紧 prune。 |

## 4. 是否可进入「另窗申签」前置

**可以（带条件）**——静态包合格，**不**等于已验证 RSS≤1500。

开放条件（全部满足后再由主排窗、Arch 另签）：

1. **分窗**：独立进程 `HILIQ --window x2` 与（可选随后）`HILIQ --window sealed`；**禁止**授权 `--window both` 作为首跑。
2. **rss_limit=1500** 硬钉；采样仅 `/tmp`；破帽即 ABORT；**禁抬帽**。
3. **脚本钉** `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` sha `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8`；DIFF/patch 钉 `b1455e93…` / `2154b6fb…`。
4. **禁复用** `725be3e0` 及旧脚本 `7a5f756c` 实跑授权。
5. 回执披露：float32 存储、`_prune_hist`、峰 RSS；无 alpha 选参。
6. FULLA 仍 GAP，不进本窗。

## 5. 建议下一步

| 角色 | 动作 |
|---|---|
| **AI** | 等主排窗；准备 lowmem 专属 cmd/R5c 草案（单窗 x2 优先）；**不自跑**；可另文重钉 impl「执行脚本指针」→ `05bd81ea…`。 |
| **主** | 确认开放条件 → 排 **另窗**（建议先 x2）；勿复用叶25/旧叶27 `.ok`。 |
| **Arch** | 条件齐后另签独立 `.ok`（本回合**不签**）；监控峰 RSS；破帽再迭代（分块/进一步裁 panel），仍禁抬帽。 |
| **Data/Eng** | 无需 CONT；Eng panel mmap 非阻塞。 |

## 6. 总裁定

**PASS_WITH_CONDITIONS** — 四件全长 MATCH；`/tmp` diff 重建 MATCH；因子钉与残差序静态零暗改；HILIQ-only；rss 文案≤1500；PIT 保持。开放项：首跑必须分窗、硬帽 1500、披露 float32/prune，且 **RSS 合规只能由授权实跑证明**。

live=false。
