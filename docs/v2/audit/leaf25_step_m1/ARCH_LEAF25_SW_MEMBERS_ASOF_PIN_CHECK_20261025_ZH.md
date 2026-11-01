# Arch 叶25 全叶钉核：`sw_members_asof` / `dec73305`

- 角色：QuantLab Arch 执行器（只读核验 + 落结论；**不签 `.ok`**；**不实跑**生产大表内容）
- 时戳：2026-10-25 11:30:34 ET（America/New_York）
- live=false
- 结论：**PIN_OK_WITH_CONDITIONS**

## 1. 现盘 sha（本核自算）

| 路径 | sha256 |
| --- | --- |
| `research/sw_members_asof.py` | `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7` |
| `research/tests_sw_pit/test_sw_members_asof.py` | `e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc` |
| `docs/v2/AI_LEAF25_FULL_FACTOR_WINDOW_DRAFT_20261025_ZH.md` | `994324c9ad0c4cc10d2f24426ed9375ca6ec79bf3ca191aa9d53409d00eab002` |

- 脚本前缀 **MATCH** 主裁 / 草案所引 `dec73305…`（全长见上表）。
- 草案 sha 前缀 **MATCH** `994324c9…`。

## 2. 草案钉表表述（`994324c9…`）

- §2.2「拟读输入」：共享 as-of = `research/sw_members_asof.py::sw_l1_asof_with_gap_carry`，现盘 sha 写为 `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7`，标注 **待 Arch 确认可钉入全叶 `.ok`**；旁注「r5 曾阻塞于 DIFF C」。
- §8 #8：同路径 / 同 sha 前缀，状态 **待 Arch 确认可钉**。
- §9：预注册冻结选项含「先出 r6（钉 `sw_members_asof` `dec73305…` …）」。

本核回答：该脚本 **可以** 作为全叶钉表中的 `sw_members_asof` 钉值；历史「DIFF C」阻塞已被 r3e 落地 + 自测消解（见 §3），不再构成 PIN_BLOCK。

## 3. 既有 Arch / Strategy MATCH 证据

| 证据 | sha256（本核） | MATCH 要点 |
| --- | --- | --- |
| r3e 落地回执 `docs/v2/audit/STRATEGY_SW_PIT_R3E_LANDING_RECEIPT_20261018.md` | `cd379089cb3902064501b16a8dec0a8706dbc68da5cb4546dd58eb75fbf98611` | 落地后 `research/sw_members_asof.py` = **`dec73305…`**；测试 = `e80f98ed…` |
| r3e 自测回执 `docs/v2/audit/strategy_r3e/SELFTEST_R3E_RECEIPT_20261018.md` | `ec10c0569813b16c2d9a7fb6317856afb8a182cfd00a371e5558e5691037ce91` | **85 passed / 0 failed**，EXIT=0；跑前=跑后 pin 含 `dec73305…` / `e80f98ed…` |
| 叶25 步骤−1 pin 表 v4_1 `LEAF25_STEP_M1_R5_PIN_LIST_v4_1.md` | `b6c60b4f49367da32d56c9ca2e4c66520dbb2006981365eceec0636809813cb1` | 将 `dec73305…` / `e80f98ed…` 列为叶25 冻结链前置；写明 **Arch 12:58 ET 受理** 自测回执 `ec10c056…`；并注明步骤−1 本身不调用该脚本 |

补充：Strategy r3e commit 回执亦钉同一对文件 sha；DIFF C / C-r* 系列是 r3e 前演进，**不得**再以「DIFF C 未落地」拦 `dec73305`。

## 4. PIT / asof 语义（只读脚本头与规则，不读大表行）

- 交易日 `d` 成员规则：`in_date < d` 且（`out_date` 空 **或** `out_date >= d`）→ **禁未来函数**（`in_date == d` 排除；`out_date == d` 仍算成员）。
- 换类缺口：仅在 SSE 开市日、上一开市日 `prev_open(d)` 口径下 **至多携带 1 个交易日**；无日历 / 超日历 / 解析失败 → `SwPitIntegrityError`（fail-closed）。
- `gap_carry` **必须**显式传入 `TradeCal`（无模块默认）；日历字节一次读取并对齐 `TRADE_CAL_SHA_PIN`。
- 文档声明比较路径 **无 `merge_asof`**；重叠默认 `on_overlap="raise"`。
- 默认表：`data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`（CLEAN）；legacy `data/v2/sw_pit/...` 仅 pitfix。

判定：**PIT/asof 语义可接受**，未见可钉入全叶的前视口径。

## 5. 依赖路径存在性（最小只读：存在 + sha，不解析表体）

| 依赖 | 现盘 sha256 | 与脚本/草案钉 |
| --- | --- | --- |
| `data/v2/calendar/trade_cal_sse_pit.parquet` | `fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` | = 脚本 `TRADE_CAL_SHA_PIN` / 草案 r5 日历钉 `fa4260b8…` |
| `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet` | `89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c` | = 草案 SW L1 钉 `89d4afa3…` |
| `data/v2/sw_l1_pit/manifest.json` | `0493991cd34f72a85d8cb1139b1f3b947b0754fa38029f54ad06a45b2a26446b` | 存在（CLEAN manifest check 用） |
| `data/v2/sw_pit/industry_members_sw_l1_pit.parquet` | `0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6` | = legacy 钉 `0b1d3432…`（pitfix only） |

**无未落地路径缺口**（默认 CLEAN + 日历均在盘）。

## 6. 结论与全叶钉入条件

### 结论：`PIN_OK_WITH_CONDITIONS`

- **可钉**：全叶 `.ok` / 预注册 r6 冻结表可将  
  `research/sw_members_asof.py` = `dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7`  
  （入口 `sw_l1_asof_with_gap_carry`）列为正式钉；测试建议同钉  
  `research/tests_sw_pit/test_sw_members_asof.py` = `e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc`。
- **非 PIN_OK（无条件）原因**：全叶签发仍须与其它钉/流程同包，见下；本文件 **只裁定该脚本钉**，不授权发 `.ok`、不实跑。

### 全叶钉入条件（须同时满足）

1. **共钉输入**：同一张 `.ok` / 冻结表须共钉日历 `fa4260b8…` 与 SW L1 CLEAN `89d4afa3…`（现盘已 MATCH；冻结瞬间再 `sha256sum` 一次）。
2. **调用约定**：全叶 build 使用 `sw_l1_asof_with_gap_carry` 时 **显式传 `TradeCal`**；禁止 `sha_pin=None` 的生产路径。
3. **预注册**：r5 仍 DRAFT 时，须经 **r6**（或主裁等价冻结）写入本 sha 后再 FROZEN；不得只在运行 cmd 里「口头」引用。
4. **日历续期耦合**（既有 Arch P2）：`trade_cal` 延期导致 sha 变 → 必须同步改 `TRADE_CAL_SHA_PIN`（脚本 sha 会变）并 **重签** 一切钉了旧 `dec73305` 的 `.ok`。
5. **不替代其它全叶闸**：P2 wrapper 采样尽 `/tmp`、全叶 build/X2 脚本 sha、密封与 X2 **分两张 `.ok`**、禁复用 `1c32ab1e`、禁抬帽——仍按主裁另裁；本钉通过 **不解除** 那些阻塞。
6. **Intel 副本**：Intel 侧若仍用自有 `sw_members_asof`，不得默认与本钉字节等价；全叶若只走 Strategy 共享函数则无此风险。

## 7. 本核边界

- 未签任何 `.ok`；未改 `TEAM_STATE`；未实跑 pytest / 未加载生产表行内容。
- 未 SendToUser / SendToAgent。
