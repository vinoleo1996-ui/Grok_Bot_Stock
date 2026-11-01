# Eng 回执：A18 §5.3 dest hash 同构修补（侧草稿）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻（America/New_York） | `2026-10-26 18:13 ET` |
| 状态 | **DONE**（侧草稿 + 2014 钉测；**未**写 baseline；**未**全量重跑） |
| 判稿 | **`6466c490`** HASH_CALIBER_BUG |
| 归档 | **`f28183e0`**（`.ok` `6de02e74` ABSENT） |
| 前序 A9 D1 | **`09c1b2c8`** |
| DIFF sha8 | **`dbff641d`** |
| live | false |

## 1. 交付钉

| 产物 | 路径（相对 `docs/v2/audit/daily_basic_a18_20261026/`） | sha8 | 全长 |
|---|---|---|---|
| helper 侧草稿 | `a18_s53_year_sorted_content_col_hashes_helper.py` | **`3094f0b6`** | `3094f0b60fa721922489b5ea21b1e7c4ca29b1b7d2bb8b65288b80b22fa9ab02` |
| v2 驱动侧草稿 | `a18_s53_driver_v2_dest_monthly.py` | **`af15b52d`** | `af15b52dbd54ed52216b41891f29a833cd13084f9c21512ca1fe01389e622deb` |
| 2014 钉测证明 | `ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_PIN_2014_PROOF.json` | **`2cc3e356`** | `2cc3e3568a33c7e6283561942fef66b96f4e0ae95a237ce43e3c0f05494a4b5f` |
| DIFF | `ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_DIFF_20261026_ZH.md` | **`dbff641d`** | `dbff641dfee72b9f4b7a473fbaf13a3795147d04caf123182b47018c6d884e83` |
| 本回执 | `ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_RECEIPT_20261026_ZH.md` | （SHA256SUMS） | （SHA256SUMS） |

## 2. 钉测结果（必须）

| 检查 | 结果 |
|---|---|
| 2014 col_hashes | **22 / 22 MATCH** |
| 2014 stub | **MATCH** `02bb7e2122743075e1f615aa6798ee3b1fd945f99f4d081fff3ed87451b88c9d` |
| 2014 rows | **570677** = ref |
| OUT_TMP（A9 只读） | `/tmp/a18_s53_20261026T175303_2902093` |
| 钉测工作目录 | `/tmp/a18_s53_isomorph_20261026/`（含 `pin_2014_proof.json`） |
| `py_compile` helper+driver | **PASS**（无需 `.ok`；侧草稿） |

## 3. 生产钉（未动）

| 文件 | sha8 | 状态 |
|---|---|---|
| `scripts/acquire/daily_basic_incremental.py` | **`a7ac54b3`** | **UNTOUCHED** |
| transform pin | `308b5054` | 未改（驱动仍校验） |
| dest parquet | `f6bbf9e5` | 只读 |
| manifest | `8c2c978b` | 只读；无 `build` |
| baseline | — | **ABSENT**（本票未写） |
| live EXEC `.ok` | — | **ABSENT**（Arch 已归档） |

## 4. 禁区复述（本票遵守）

禁复用 `6de02e74` / `4377eb59`；禁盲 seed / allow_run / 物化 / 带病 baseline；禁改生产 parquet·manifest；禁第二全量驱动；禁候选3 enable；禁 git commit；纸面 HOLD。live=false。

## 5. Bonus：纸面 SW 披露（非阻塞）

纸面 ABORT 留下的 `output/loop/paper_daily_20261026/SW_SHA_DISCLOSURE.md` 曾与 `READINESS_ABORT` 字节相同（sha8 `665232a5`）。本票覆写为**真实短披露**（路径+sha256 前缀 `89d4afa3` / `87d769aa` 已核）。**未**跑 paper-daily。

## 6. 下一跳

交 Arch 复审清单（本 DIFF + v2 驱动）→ 主另签新窗 → 新 `.ok` 下用 v2 重跑 §5.3。Eng 停等。不报 Leo。

---
文档结束（Eng A18 §5.3 DEST_HASH_ISOMORPH_RECEIPT）
