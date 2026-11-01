# 叶27 X2 selfcheck_v2 钉盘证 + 准备回执（非实跑）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T00:35:00-04:00（America/New_York；墙钟 2026-10-26 00:35 ET）
- **状态**：PIN_MATCH · **SELFCHECK_EXECUTED=false** · live=false · promotion_approved=false · ≠X2 ACCEPT
- **主令**：2026-10-26 ~00:27 ET 深挖派单（selfcheck_v2 → X2 另包 DRAFT）

## 三件全长 sha256 MATCH

| 件 | 路径 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|---|
| alpha | `output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet` | `652b8a68` | `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` | **MATCH** |
| meta | `output/ai_factory/leaf27_on_minus_id_idio_ivol/run_meta_HILIQ_x2_20261025_224033.json` | `85c2dc78` | `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` | **MATCH** |
| summary | `output/ai_factory/leaf27_on_minus_id_idio_ivol/build_summary_20261025_224333.json` | `80596bff` | `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` | **MATCH** |

## alpha schema / 行数 / 窗

| 项 | 值 |
|---|---|
| 列 | `date, instrument, alpha, alpha_raw, ivol, size_domain, ind` |
| 行数 | **1271399** |
| 交易日数 | 570 |
| instrument 数 | 4478 |
| 窗 span | **2024-06-03 → 2026-10-09**（meta/summary 一致） |
| 缺 eval_weights | **是**（本票任务：由 alpha 生成评价权重） |

## meta peak / tags

| 项 | 值 |
|---|---|
| peak_rss_mb | **1401.22265625**（软帽 1500；禁抬） |
| n_chunks | **17** |
| universe / window | HILIQ / x2 |
| baseline_evac_tag | `baseline_evac_r1` |
| mktcap_cache_tag | `mktcap_cache_r1` |
| hist_prune_tag | `hist_prune_r1` |
| limit_policy | `exclude_hit_or_unknown` |
| live / promotion_approved | false / false |
| 脚本（构建 alpha） | `585ba746`（**本票不改字节**） |
| Arch 回执 CONSUMED | `78557480` |
| AI RUN_RECEIPT | `1671eec4` |
| CONSUMED `.ok` | `0f50daf7` → 归档 `7e06a5b3`（**禁 RESTORED**） |

## 硬声明

- **SELFCHECK_EXECUTED=false**：本回合**未**调用 `leaf_selfcheck_common.evaluate`；**未**读真价/收益；**未**写 `eval_weights_*.parquet` 实数。
- baseline_evac **CONSUMED_PASS 不解阻 X2**；勿当 X2 ACCEPT。
- 下一步：等主交审 → Arch 只审不签 → 主排新签窗 + **新** `.ok` 后，才执行 CMD 中 PRIMARY CLI（`--execute`）。
- forbid RESTORED 八票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**
- 禁抬帽 / 禁自签 `.ok` / 禁自跑 Book-Smoke / 禁开叶28/29 / 禁改脚本 `585ba746`
- pgrep（kline/export_static/snapshot/gen）：本回合 **EMPTY**
- 新脚本：`research/leaf27_x2_selfcheck_v2.py` sha8 **`a40d7069`** 全长 `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0`

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false
