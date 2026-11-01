# 叶25 X2 selfcheck_v2 钉盘证 + 准备回执（非实跑）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T13:35:00-04:00（America/New_York；墙钟 2026-10-26 13:35 ET）
- **状态**：PIN_MATCH · **SELFCHECK_EXECUTED=false** · live=false · promotion_approved=false · ≠X2 ACCEPT
- **主令**：2026-10-26 ~13:31 ET 派单（叶25 全叶 alpha CONSUMED 后 → selfcheck_v2 DRAFT）

## 两件全长 sha256 MATCH

| 件 | 路径 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|---|
| alpha | `output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet` | `8be12024` | `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` | **MATCH** |
| meta | `output/ai_factory/_leaf25_full_factor/20261026_015610/run_meta.json` | `44c27f54` | `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` | **MATCH** |

## alpha schema / 行数 / 窗

| 项 | 值 |
|---|---|
| 列 | `trade_date, ts_code, alpha, cfacc, chunk_id, universe` |
| 行数 | **1633512** |
| 交易日数 | 570 |
| instrument 数 | 4914 |
| 窗 span | **2024-06-03 → 2026-10-09**（meta 一致；x2_end=`20261009`） |
| 缺 eval_weights | **是**（本票任务：由 alpha 生成评价权重） |
| 缺 ind 列 | **是** → 执行路径用 SW L1 asof 挂行业（IND_CAP） |

## meta peak / PIN_GAP

| 项 | 值 |
|---|---|
| peak_kb_final | **751032**（≈733 MB；软/硬帽 1500；禁抬） |
| n_chunks / parts | **29** |
| universe / window | HILIQ / x2 |
| mechanism_tag | `g1g5_ashare_cfacc_desens_cs_v1` |
| residual_covars overall | **PARTIAL** |
| PIN_GAP 字段 | **β120 / mom / logADV20 / vol20** |
| CFACC TTM+desens | **已实装** |
| 勿称 | **全残差齐** |
| live / promotion_approved | false / false |
| 构建脚本（UNCHANGED） | `de7b3647`（本票不改字节） |
| Arch CONSUMED | `fb19ac28` |
| AI RUN_RECEIPT | `b8c0b050` |
| CONSUMED `.ok` | `3c297052` → 归档 `d37a157e`（**禁 RESTORED**） |
| QUIET lift | `a4857568` |

## 硬声明

- **SELFCHECK_EXECUTED=false**：本回合**未**调用 `leaf_selfcheck_common.evaluate`；**未**读真价/收益；**未**写 `eval_weights_*.parquet` 实数。
- 叶25 alpha **CONSUMED_PASS 不解阻 X2**；勿当 X2 ACCEPT。
- **PIN_GAP PARTIAL** 必须写入签文/预注册：β120/mom/logADV20/vol20；CFACC 已实装；勿称全残差齐。
- 下一步：等主交审 → Arch 只审不签 → 主排新签窗 + **新** `.ok` 后，才执行 CMD 中 PRIMARY CLI（`--execute`）。
- forbid RESTORED **十二**票（十一+本票内容）：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**
- 拟 `.ok` 名（**未创建**）：`output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`
- 禁抬帽 / 禁自签 `.ok` / 禁自跑 Book-Smoke / 禁开叶28/29 / 禁改构建脚本 `de7b3647` / 禁 RESTORED `3c297052`
- pgrep（kline/export_static/snapshot/gen）：本回合 **EMPTY**
- 新脚本：`research/leaf25_x2_selfcheck_v2.py` sha8 **`b1db0886`** 全长 `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3`
- Gate：`leaf_selfcheck_common.evaluate` → decay + portfolio A/B/current
- rss 软/硬帽 **1500** + peak_proof REQUIRED；sampler `/tmp/quantlab_leaf25_x2_selfcheck_*`

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false
