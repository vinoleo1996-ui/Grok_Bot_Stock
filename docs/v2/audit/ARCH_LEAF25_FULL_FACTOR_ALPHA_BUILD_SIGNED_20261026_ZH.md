# Arch 叶25 全叶 HILIQ×x2 alpha 构建 · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-26T01:50:19-04:00`（America/New_York） |
| 主令窗 | `MAIN_LEAF25_FULL_FACTOR_ALPHA_BUILD_OK_WINDOW` sha8 **`12dc8e6d`**；窗 **01:45–02:30 ET** expires **02:32** |
| 审阅 | `dd68765e…` **PASS_WITH_CONDITIONS** |
| 催签 | 主 URGENT @01:46（例程 `25-alpha-build-ok-01-45` 截至签时未见落签→Arch 入窗补签） |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶25 全叶 HILIQ×x2 alpha 构建（PRIMARY：新脚本 `leaf25_full_factor_alpha_build_r1.py` → CFACC TTM+desensitize(−CFACC)+部分截面残差 → `_leaf25_full_factor/<ET_TS>/`）`.ok` 已落盘；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠ mem_probe**；**≠ RESTORED** 十一票（`1c32ab1e`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`6054b3bf`）；脚本全长 **`de7b3647…`**；COVER `07b0a1b8` · CMD `8ab8831c` · DIFF `03d50f3f` · HAND 钉盘上 **`21bf0d41…`** · VERIFY `d6750c94` · H2A 钉盘上 **`2ac86676…`**（HAND=`DRAFT_READY_FOR_ARCH_HOLD` / H2A=`READY_FOR_MAIN_SUBMIT`）；**PIN_GAP** 入签（β120/mom/logADV20/vol20 未齐；勿称全残差；CFACC TTM+desens 已实装；overall=PARTIAL）；rss 软/硬帽 **1500** 禁抬（脚本硬 ABORT）；peak_proof **REQUIRED**；sampler `/tmp/quantlab_leaf25_full_alpha_*`；**Arch 不代跑**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；峰＞1500→停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 窗令 | `12dc8e6d` | `12dc8e6d8c0dbb38d5e5a97a167e545758fabe107e5c5b5c86f1decdcf656f35` | **MATCH** |
| 审阅 | `dd68765e` PASS_WITH_CONDITIONS | `dd68765ee41c91583200e238f7b6623b9fde3daba630f213fccc15a00e1f8dae` | **MATCH** |
| 脚本 | `de7b3647…` | `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` | **MATCH** |
| COVER | `07b0a1b8` | `07b0a1b869c15367cd0711a565327a6cdefdcc9712b6028720e2477c9d5cbd21` | **MATCH** |
| CMD | `8ab8831c` | `8ab8831cb203ea42f998966d92e32231a038ef30bacbd4f260300253d918ce4e` | **MATCH** |
| DIFF | `03d50f3f` | `03d50f3f500d82fc453dd992a2e179a822f2969005114b5e4f2006d0c5269c17` | **MATCH** |
| HAND | `21bf0d41` | `21bf0d418cc76427e91eb50d767b95d01b5682245d9774709ec7488d5dfc64fd` | **MATCH** |
| VERIFY | `d6750c94` | `d6750c94ee32f98fd5437b0ca65f623427b5d5a291b266e32f059aa1110f8452` | **MATCH** |
| H2A | `2ac86676` | `2ac866767fdbcd2847801c0abe5ae26f56737cca16a5211cc3e4d545c4590224` | **MATCH** |
| 交审令 | `504b6a9d` | `504b6a9da3cee23c942c4de5c2afebe412cb294d9e506717c558dffb1ea2147b` | **MATCH** |
| 拟 .ok 签前 | 不存在 | 不存在 | **MATCH** |
| QUIET 签前 | 不存在 | 不存在 | **MATCH** |
| live .ok | 0 | 0 | **MATCH** |
| 窗期 | 01:45–02:30 / expires 02:32 | 签时 `01:50:19` ET | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_FULL_FACTOR_ALPHA_BUILD_HILIQ_X2.ok` |
| `.ok` sha8 / 全长 | `3c297052` / `3c297052af27c24a3344c85c578199abc53d10c84cf3373b5046b9a3d3c2d0f3` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `073fe7a4` / `073fe7a45e062ed4d27bb59b1ae0ea8c43938ca7e294ad4352c5bf64bb409630` |
| 脚本 | `research/leaf25_full_factor_alpha_build_r1.py` = `de7b36477908ee522c73e71db64ac904356d7a65c420ea897332925c36427856` |
| 审阅 | `dd68765ee41c91583200e238f7b6623b9fde3daba630f213fccc15a00e1f8dae` PASS_WITH_CONDITIONS |
| 主令窗 | `12dc8e6d8c0dbb38d5e5a97a167e545758fabe107e5c5b5c86f1decdcf656f35` |
| 交审令 | `504b6a9da3cee23c942c4de5c2afebe412cb294d9e506717c558dffb1ea2147b` |
| COVER / CMD / DIFF / VERIFY | `07b0a1b8…` / `8ab8831c…` / `03d50f3f…` / `d6750c94…` |
| HAND 盘上全长 | `21bf0d418cc76427e91eb50d767b95d01b5682245d9774709ec7488d5dfc64fd` |
| H2A 盘上全长 | `2ac866767fdbcd2847801c0abe5ae26f56737cca16a5211cc3e4d545c4590224` |
| 窗期 | `2026-10-26T01:45:00-04:00` → `2026-10-26T02:30:00-04:00`；expires `2026-10-26T02:32:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --x2-end 20261009 --chunk-mode month --out output/ai_factory/_leaf25_full_factor/<ET_TS>/` + `--allow-real-data --arch-ok-path <OK>` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；脚本 `check_rss` soft/hard **硬 ABORT** |
| 采样 | 仅 `/tmp/quantlab_leaf25_full_alpha_*` |
| 产物 | `_leaf25_full_factor/<ET_TS>/` + `alpha_parts/HI_LIQ/part_*.parquet` + `alpha_HILIQ_x2_<ET_TS>.parquet` + `run_meta.json` |
| PIN_GAP | **已入签**：β120/mom/logADV20/vol20=PIN_GAP；overall=PARTIAL；CFACC TTM+desens 已实装；勿称全残差齐 |
| 禁 RESTORED | 十一票：`1c32ab1e`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`6054b3bf` |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 4625832 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-26T01:50:19-04:00` reason=leaf25_full_factor_alpha_build_HILIQ_x2 holder=leaf25_FULL_FACTOR_ALPHA_BUILD |
| pgrep kline/export_static/snapshot/gen | 空 |
| pgrep leaf25_full_factor | 空 |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（alpha sha + run_meta sha + peak rss + PIN_GAP 披露复述；峰＞1500→停）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻叶27/全量 X2；live=false

live=false。
