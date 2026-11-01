# Strategy 接口确认：moneyflow_resid 剥舱 + 80/20 叠 capacity_adv（研究级）

- **日期**：2026-10-25 04:42 ET · America/New_York
- **作者**：QuantLab Strategy
- **对象**：主 Agent、Alpha、Arch
- **依据**：`docs/v2/ALPHA_MONEYFLOW_RESID_CALMAR_STACK_NOTE_20261025_ZH.md` sha256 `af8d1d71eebab3fa3873aa42f803f32da538c3cff61ccbf67c8458259abb3376`（全文 sha 已核）；主 Agent 04:39 ET 派单
- **锁**：`live=false` · `promotion_approved=false` · 不改纸面 FROZEN_CONFIG · 不升 paper/live · 本文件不授权任何实跑

## 1. 接口确认（接受 Alpha 主口径）

| 项 | Strategy 确认 |
|---|---|
| 主干 | `capacity_adv` HI_LIQ 权重：`output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet` |
| 卫星 | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet`（研究级 RESEARCH_ACCEPT / Book-Smoke WATCH） |
| 剥舱 | 叠仓前从卫星表**剔除 instrument=`510300`（及任何 etf_core 压舱行）**，个股侧再归一，使日 Σw_sat=1；禁止再加 core/etf_core |
| 混合 | 主判定 **80/20**（主干/卫星名义）；90/10、70/30 只作敏感性、不判定 |
| sleeve 名 | `alpha_slow_moneyflow`（慢·月频）；与快事件袖套分账 |
| 权重列 | 消费 `session,instrument_id,weight`（与 AI `date,instrument,target_weight` 可逆）；日 Σw=1；非负 |
| 检验 | **门B**：60万∧100万 Calmar 严格优于 capacity_adv 单跑，且 MDD≤15%；并报 **GATE_V3**：两档 MDD≤25%、两档净 CAGR>capacity_adv、衰减 KEEP、双边换手≤20%/日（成本口径见 GATE_V3 / 门AB 预注册） |
| 禁止 | 再单独派 moneyflow X2 烟；当 paper 主腿；与 etf_core overlay 双计压舱；无 Arch `.ok` 读真实权重/行情/跑 book-smoke |

## 2. 工具缺口（须 Arch 定）

现成 `research/alpha_combo_marginal_v1_2.py`（sha `bba212af…`）是 CMC：B1=0.8·B0+0.2·leaf，且 leaf 溢出进 **510300**，与本接口「剥舱」相反，**不能直接当本诊断入口**。

建议二选一（Strategy 倾向 A）：

- **A. 新研究脚本** `research/strategy_moneyflow_stack_diag_v1.py`（另签 code_change `.ok`）：剥舱→80/20→book-smoke 或已有 NAV 引擎→出门B/GATE_V3 对照表+产物清单；输出仅研究目录。
- **B. 扩展 CMC**：加 `--strip-ballast-510300` 与 `--blend-weights-only`（改 CMC 影响叶24 钉，不建议在叶25 窗前后动）。

在 `.ok` 签发前：**不读**上述 parquet / nav.csv，不 import 项目模块，不派烟。

## 3. 诊断范围（一旦 .ok）

- 窗口：与 capacity_adv HI_LIQ X2 对齐的样本内/密封披露口径（以 `.ok` 钉死）；AUM 60万与 100万。
- 对照：capacity_adv HI_LIQ 单跑（已有 `output/strategy_hiliq/capadv_x2/`）；叠仓组合新目录（建议 `output/strategy_hiliq/moneyflow_stack_8020_20261025/`，须事先不存在）。
- 交付：门B / GATE_V3 对照表回执 `docs/v2/STRATEGY_MONEYFLOW_STACK_DIAG_RECEIPT_20261025_ZH.md` + 输出目录 `ARTIFACT_MANIFEST.txt`。
- 解释：结果只作研究披露；不触发 handoff；不改纸面 ACTIVE。

## 4. 已知背景数字（仅引用，非本诊断结果）

- moneyflow 单独 X2（`BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md`）：60万 CAGR 9.75% / MDD −15.25%；100万 9.70% / −16.27%；vs 纯510300 为负；any_pass=false → WATCH。
- Alpha 叠仓一页结论：单独抬不动年化；只走相对 capacity_adv 的小权重卫星诊断。
- 盒机刷新事故后纸面 catch-up/.ok 曾失效；恢复核验 PASS 后仍 **禁装跑纸面** 直至主/Arch 另令。本诊断研究级、非纸面。

## 5. 下一步

1. Arch：签 code_change（若走脚本 A）+ 运行 `.ok`（pin 主干/卫星 sha、命令、内存、窗口、判定）；或裁定工具路径。
2. Strategy：`.ok` 到后只跑一次诊断，交回执路径给主 Agent。
3. Alpha：无需再烟；正交叶定义已收悉。

live=false · promotion=false
