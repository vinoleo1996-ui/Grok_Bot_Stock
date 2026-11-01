# Data：叶26 GAP×4 + PARTIAL×3 推进回执（研究级；**不签 .ok**）

- 角色：QuantLab Data 执行器
- 时刻（America/New_York）：**2026-10-26 01:17 ET (America/New_York)**（`2026-10-26T01:17:49-0400`）
- 主令：主 Agent — 叶26 GAP 推进；对照 `DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` / 盘点 / AI r2
- 禁令：只读复测 + 审计目录/ `/tmp` 草案；**禁写生产** `data/`/`data/v2/`；**禁外网/中转拉取**；**禁消费**补跑 `.ok` `9e4359f9`；SUSPEND 维持；不申请本叶 `.ok`；不改 `TEAM_STATE`；修 PIT ≠ 解阻叶25
- live=false；`promotion_approved=false`；research_only=true

---

## 0. 对照输入 sha MATCH

| 文件 | 期望 | 实测全长 sha256 | 结果 |
|---|---|---|---|
| `docs/v2/audit/DATA_LEAF26_ETF_FLOW_GAP_RECEIPT_20261025_ZH.md` | `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` | `aaf84d66ececa313a371020cd0ae0f4ce5092902849b89b5b6dea79867b4e859` | **MATCH** |
| `docs/v2/audit/leaf26_20261025/DATA_LEAF26_GAP_INVENTORY_ZH.md` | 前缀 `c03a9f0e` | `c03a9f0e4c9c7622cd0dc0be36de2aaada70f9dacc48921156c89f640125b305` | **MATCH** |
| `docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` | 前缀 `0b55bfeb` | `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5` | **MATCH** |
| `output/intel/ETF_FLOW_PIT_CANDIDATES_latest.md` | （aaf84d66 钉 `ca035159…`） | `ca0351595f7a2ae4bd0c2367a510cd2012626a1d76613db517df7108937d886c` | **MATCH** |

---

## 1. 现盘复测 vs aaf84d66（关键路径）

| 路径 | 复测 sha256 | 行数 / 日期极值 | vs aaf84d66 |
|---|---|---|---|
| `index_weight_csi300_500_1000.parquet` | `d543a485959d6b579a2c5a26e18c3f7afea7a1047e308367588729c1f69bbd39` | 189000；trade_date 20180131→20260930；无 available_at | **无 DELTA** |
| `000300/905/852_SH_202610.parquet` | 占位 `e5feded3…` | 各 **0** 行 | **无 DELTA** |
| `fund_basic_E.parquet` | `07e0151624b02eefd11c88c0a1de31e6a70db8736c5dd019a73aaab902b66d8f` | 2931 | **无 DELTA** |
| `etf_share_flow_pit_major.parquet` | `a3eac35b91ae78a9cd152a7e68fb75a9274c6a32a1bfa7550f6ada88c45232bf` | 14258；→20261009；有 unit_nav/available_at | **无 DELTA** |
| `hk_hold_ashare_daily_2018plus.parquet` | `edf3f438a5b079263eca4e8b9005a27c0f602bf393641db3daa76caf0099ee69` | 3715734；trade_date→20250630；密止 **20240816**；后稀疏 4 季末点 | **无 DELTA** |
| `etf_daily_adj.parquet` | `48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c` | 1564839；→20261016；无 unit_nav/premium | **无 DELTA** |
| `hsgt_top10_daily_2018plus.parquet` | `c54935e82c8372bb5ac37023a4319ea16eff7f9fbc0aa03ef3106937f59a42f1` | 38364；→20261016 | **无 DELTA** |
| `hsgt_top10_manifest.json` | `4d5e6f5d3c55f4b133be2416d1978f71beef6ff632c30103aeaa1f8cedc354a7` | rows=38304 止 20261013；内嵌 sha≠文件 | **无 DELTA**（漂移仍在） |
| `northbound_summary.json` | `85e87ac551d80722352308f4e54aa288f6ab996777dd398f6dd5275db62e2b06` | hsgt_top10 与文件对齐 | **无 DELTA** |
| `moneyflow_hsgt_daily_2014plus.parquet` | `ee1fca152f580b906628b4be5bc67e153e9f48aed3a2d31ffbde72e963b7d369` | 2800；→20261009 | **无 DELTA** |

### DELTA 备注（非生产表）

| 项 | 说明 |
|---|---|
| `output/intel/ALERTS_latest.{md,json}` | 旁路已刷新至 ~2026-10-26 01:01 ET（sha 见美 ETF 盘点文）；aaf84d66 未钉 ALERTS sha → **不记为生产 DELTA** |
| 生产 `data/v2` 关键路径 | 全长 sha / 行数 / 日期与 aaf84d66 **一致** |

---

## 2. 七项状态表（旧→新 + 本回合推进）

| # | 项 | 旧 (aaf84d66) | 新 | 本回合推进 |
|---|---|---|---|---|
| 1 | index_weight PIT / available_at / asof | **GAP** | **GAP**（规则草案已交） | 规则草案（默认推荐下一自然月 1 日 09:00 SH）；schema；D5 关系；绕行 `pit_basis=month_end_snapshot_no_available_at`；`/tmp` 3 月末点合成样例 sha `c596e938…` |
| 2 | 000852 权重 | **PARTIAL** | **PARTIAL** | 复测 105000 行 / 105 月末点至 **20260930**；202610 空片 0 行；**确认 r2 剔除**；续补排队（等中转+`.ok`） |
| 3 | 宽基 ETF↔指数映射 + 联接去重 | **PARTIAL** | **PARTIAL**（DRAFT 非 Arch 钉） | 硬编码 510300→000300、510500→000905；审计目录 DRAFT CSV + 联接候选（fund_basic 名含「联接」24；宽基相关摘录） |
| 4 | hk_hold 密窗 | **GAP** | **GAP** | 密止 20240816 确认；稀疏点完整列表 20240930/1231/20250331/20250630；续密/替代源排队（Tushare `hk_hold`；**未拉取**） |
| 5 | premium PIT 视图 | **GAP** | **GAP**（配方+样例） | Join 配方 asof=max(两表 available_at)；`/tmp` 510300/510500 样例 **4250** 行 sha `60a8420f…`；审计目录 head20 CSV |
| 6 | 美 ETF PIT | **GAP** | **GAP** | 盒上仍 0 条美 ETF PIT parquet；ALERTS 旁路路径+sha；时区规则草案（US close+缓冲→下一 SSE 09:00） |
| 7 | hsgt_top10 catalog vs 文件 | **PARTIAL** | **PARTIAL**（DRAFT JSON） | 按文件重算 rows=38364/days=2033/止 20261016/sha `c54935e8…`；`hsgt_top10_manifest.DRAFT.json` 仅审计目录；**未**覆盖生产 manifest |

---

## 3. 交付物清单（路径 + 全长 sha256）

### 3.1 审计目录 `docs/v2/audit/leaf26_20261026/`

| 文件 | sha256 |
|---|---|
| `DATA_LEAF26_INDEX_WEIGHT_PIT_RULE_DRAFT_ZH.md` | `479d7c6f404ed8ff4946a2b4b36032c81299607dadc82e9881e6851383054cb0` |
| `DATA_LEAF26_HK_HOLD_DENSE_GAP_ADVANCE_ZH.md` | `58648c7dabd0a013c10b50ee81289f55e3aa94d538880e14b531339d716a1849` |
| `DATA_LEAF26_PREMIUM_PIT_JOIN_RECIPE_ZH.md` | `89ee0d3a8fd7f525a70410eb77c005ea7a13042fe06c32d23a316ef98106804b` |
| `DATA_LEAF26_US_ETF_PIT_INVENTORY_ZH.md` | `8dc3d9f68d62e26785097bc4f41d1d7489b642ee26c484927f8eeeed4dc86ce3` |
| `DATA_LEAF26_BROAD_ETF_INDEX_MAP_DRAFT_ZH.md` | `d1728922e423ca997fc63fb7e51bd8c0baa14488b6091aacf42cf55937a8b4c3` |
| `DATA_LEAF26_BROAD_ETF_INDEX_MAP_DRAFT.csv` | `21bd9d26a497566b2e126d77b2e9db4ffdd552acc0369ace901536ea77d6631a` |
| `DATA_LEAF26_HSGT_TOP10_MANIFEST_RECAL_DRAFT_ZH.md` | `0f62e2fcd521d3c52cc4058f07198c677a6f4392b879d9c6d433b252f2f4ff36` |
| `hsgt_top10_manifest.DRAFT.json` | `14de2821f1b3c76842e3fd8b9f311a49e6c50428c0a16c18c2cbbae8b0aae949` |
| `premium_pit_sample_510300_510500_head20.csv` | `0a1205edf75e771637dc15ce62d91209a317fbd9078821f0c718d3f2223dc67d` |

### 3.2 `/tmp` 研究样例（非生产）

| 文件 | sha256 |
|---|---|
| `/tmp/leaf26_20261026_samples/index_weight_available_at_sample_3months.parquet` | `c596e938595b8a49ab3d91796b6435e4cc056ea0bdf8bcc527fdda5b43d52c7d` |
| `/tmp/leaf26_20261026_samples/premium_pit_sample_510300_510500.parquet` | `60a8420f32d52ec08c914f84c3ab9b70d5fd88dda29bb23da2ef1ebd4e07831f` |
| `/tmp/leaf26_20261026_samples/hsgt_top10_manifest.DRAFT.json` | `14de2821f1b3c76842e3fd8b9f311a49e6c50428c0a16c18c2cbbae8b0aae949`（与审计目录同内容） |

### 3.3 本总回执

- 路径：`docs/v2/audit/DATA_LEAF26_GAP_ADVANCE_RECEIPT_20261026_ZH.md`  
- 全长 sha256：见落盘后 `sha256sum`（写于文末自我钉或由父代理核）。

---

## 4. 仍硬依赖中转 / Arch `.ok`（本回合不可闭合）

| 项 | 依赖 |
|---|---|
| index_weight 落 `available_at` 列 / 新 PIT 表 | Arch 共签规则 A/B + 生产写 `.ok` |
| 202610 权重月片续补（含 000852） | 中转拉取 + `.ok`（**禁**消费 `9e4359f9`） |
| hk_hold 续密窗 | 中转 / Tushare + `.ok`；或稀疏契约另签 |
| premium PIT 生产表 | Eng/Data 共签落地路径 + `.ok` |
| 美 ETF PIT 主库 | 新源接入 + 时区规则 Arch 钉 + `.ok` |
| 宽基映射 Arch FROZEN | Arch 钉路径/sha（本 DRAFT 不足） |
| hsgt_top10 生产 manifest 覆盖 | Arch `.ok`；本回合仅 DRAFT |

---

## 5. 叶26 r2 主规格是否仍可研究级推进（对齐 aaf84d66 §6）

**是 — 维持 aaf84d66 §6 结论，无收紧：**

| # | 阻塞 r2 主规格？ | 说明 |
|---|---|---|
| 1 index_weight 无 available_at | 软阻塞严格 PIT；研究级可绕 | 已披露路径 `pit_basis=month_end_snapshot_no_available_at`；规则草案待 Arch |
| 2 000852 / 202610 空 | **否** | r2 剔除 |
| 3 映射无 Arch 钉 | **否**（研究级） | 两对硬编码 + DRAFT CSV |
| 4–7 Intel 生态 | **否** | 非 r2 主轴 |

主输入仍本地可读：`etf_share_flow_pit_major`（510300/510500）+ 权重表 000300/000905。  
正式预注册 / 严格 PIT / 本叶 `.ok` **仍不申请**。

---

## 6. 生产未触碰证明（mtime）

本回合开始前快照 vs 结束后（只读 `stat`）：

```
data/v2/index_members/index_weight_csi300_500_1000.parquet before_mtime=1792905116 after_mtime=1792905116 size=488959 SAME=True
data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet before_mtime=1792905190 after_mtime=1792905190 size=35555406 SAME=True
data/v2/northbound/hsgt_top10_manifest.json before_mtime=1792905345 after_mtime=1792905345 size=987 SAME=True
data/v2/northbound/hsgt_top10_daily_2018plus.parquet before_mtime=1792905190 after_mtime=1792905190 size=1587790 SAME=True
data/v2/etf/etf_daily_adj.parquet before_mtime=1792904939 after_mtime=1792904939 size=72103162 SAME=True
data/v2/etf/share_pit/etf_share_flow_pit_major.parquet before_mtime=1792905245 after_mtime=1792905245 size=661410 SAME=True
data/v2/etf/raw/fund_basic_E.parquet before_mtime=1792905196 after_mtime=1792905196 size=205404 SAME=True
```

结论：上列关键生产文件 **mtime/size 未变**（`SAME=True` 全过）。本回合写入仅限 `docs/v2/audit/leaf26_20261026/*`、`docs/v2/audit/DATA_LEAF26_GAP_ADVANCE_RECEIPT_20261026_ZH.md` 与 `/tmp/leaf26_20261026_samples/*`。

---

## 7. 明确声明

- **未写**生产 `data/` / `data/v2/` 任何现有 parquet/manifest（含 `hsgt_top10_manifest.json`）。  
- **未拉**外网/中转；**未消费**补跑 `.ok` `9e4359f9`；SUSPEND 维持。  
- **不申请**本叶 `.ok`；不改 `TEAM_STATE`（父代理负责）。  
- 修 PIT ≠ 解阻叶25；live=false；promotion_approved=false。

---

## 8. 交付

- 本回执：`docs/v2/audit/DATA_LEAF26_GAP_ADVANCE_RECEIPT_20261026_ZH.md`  
- 原子写：tmp → `mv` 就位。  
- 子目录：`docs/v2/audit/leaf26_20261026/`（新建）。
