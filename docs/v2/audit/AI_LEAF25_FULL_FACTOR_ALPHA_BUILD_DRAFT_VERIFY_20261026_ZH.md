# 叶25 全叶/HILIQ×x2 alpha 构建 DRAFT 盘证 · 2026-10-26 01:20 ET

| 件 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|
| COVER | `07b0a1b8` | `07b0a1b869c15367cd0711a565327a6cdefdcc9712b6028720e2477c9d5cbd21` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| CMD | `8ab8831c` | `8ab8831cb203ea42f998966d92e32231a038ef30bacbd4f260300253d918ce4e` | **MATCH** · HOLD_UNTIL_MAIN_SUBMIT |
| DIFF | `03d50f3f` | `03d50f3f500d82fc453dd992a2e179a822f2969005114b5e4f2006d0c5269c17` | **MATCH**（空→新文件 `research/leaf25_full_factor_alpha_build_r1.py`） |
| HAND | `21bf0d41` | `21bf0d418cc76427e91eb50d767b95d01b5682245d9774709ec7488d5dfc64fd` | **MATCH** · **DRAFT_READY_FOR_ARCH_HOLD** · **未 SUBMITTED** |
| 脚本（新） | `de7b3647` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` | **MATCH NEW**（≠ stub / ≠ mem_probe） |
| 旧 CMD | `035e5818` | `035e5818954e0f08798a860ad870312f278784b0291bcc424e602f8cf1be1c78` | 继承修订源；不覆盖 |
| r6 令 | `53331667` | `53331667295488e334121d0fdcb4db7867417358dc8736e481eb00b0d27a844e` | **MATCH** |
| FROZEN 戳记 | `4bb1ff2b` | `4bb1ff2b805f441499607ada5f871044e72e6176a66052c73b64816130d199e2` | **MATCH** |
| 基盘 DRAFT | `e8ca2bcc` | `e8ca2bcc1136b473bdc77f3f655e77f35404990068e9e30ac0c1cd9ed721292c` | **MATCH** |
| MEM | `103717df` | `103717df1f9e5d63f8c681f16da091f44801e1b69b219ae1a18b2159446145d1` | **MATCH** |
| wrapper v5 | `4240ce82` | `4240ce82f0929085ab4bcb37e2400a3414e70e162c9e697cf02d97103342f882` | 可钉 |
| stub | （保留） | `research/leaf25_cfacc_desens_build_r1.py` | **UNCHANGED**（未覆盖） |

## 静态自检（本回合）

| 检 | 结果 |
|---|---|
| `--dry-compile-only` | **PASS**：`live:false` `ok_requested:false` `rss_limit_mb:1500` `universe:HILIQ` `window:x2` `mechanism_tag:g1g5_ashare_cfacc_desens_cs_v1`；forbid 含 `1c32ab1e`/`6054b3bf`/八票/`3c19dd7d`；**无实数加载** |
| `py_compile` → `/tmp/leaf25_full_alpha_build_r1.pyc` | **PASS** |
| pyflakes（`/tmp/ql_pyflakes_venv`） | **PASS**（exit 0） |
| `pgrep` 本构建/相关实跑 | **PGREP_EMPTY_OK**（**未**开跑） |
| 新脚本 ≠ mem_probe / stub | **PASS**（新路径 `research/leaf25_full_factor_alpha_build_r1.py`） |
| git commit | **未做** |
| 申 `.ok` / 交 Arch | **未做**（HOLD；等主交审；Arch 只审不签） |
| Book-Smoke / selfcheck | **否**（本票不做） |

## forbid_restored（明文）

`1c32ab1e / e107383f / 2be59acd / a7d98ac9 / 8e51de63 / 3a6caa4f / 8bcd79dc / 725be3e0 / 0f50daf7 / 3c19dd7d / 6054b3bf`

## 残差协变量缺件（披露）

| 协变量 | 状态 |
|---|---|
| SW L1 | PINNED_PATH（`sw_members_asof`；实跑尽力） |
| logmv | PINNED_PATH_PARTIAL（float_mktcap 钉；列 MATCH 时可用） |
| leaf19 α | PINNED_PATH（缺→0） |
| β120 / mom / logADV20 / vol20 | **PIN_GAP**（本票未钉 reader；meta 披露；α_raw 仍产出） |

## 状态

- **HOLD_UNTIL_MAIN_SUBMIT**；HAND=**DRAFT_READY_FOR_ARCH_HOLD**（**未**自称 SUBMITTED）
- 等主交审 / 新窗 / 新 `.ok`（脚本钉 `de7b3647`）
- 禁自开跑 / 禁抬帽 / 禁申 `.ok` / 禁自签 / 禁申 X2 ACCEPT
- PRIMARY：HILIQ×x2×month；mechanism `g1g5_ashare_cfacc_desens_cs_v1`
- sampler 前缀钉：`/tmp/quantlab_leaf25_full_alpha_*`
- live=false · ≠X2 ACCEPT · ≠selfcheck · ok_requested=false
