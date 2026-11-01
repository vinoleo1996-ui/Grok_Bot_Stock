# fund_portfolio 计数附录回执（C2 ALLA 池复滤 · gate_pass=true）

- 角色：QuantLab AI（执行器）
- 时刻：2026-10-27 ~21:35 ET（America/New_York）
- 触发：主裁 HOLD who_pays→X2；Arch RERUN 审 **`b410680b`** PASS_WC → 旁线 **C1+C2**
- dig：sha8 **`fa973826`**（文内自称 `a6ddc4ef` 勿采）
- 旧 FAIL 回执保留：`…RECEIPT_20261027_ZH.md` **`f36d0a04`**；RERUN 回执保留：`…RERUN_ZH.md` **`e3cc0143`**
- 叶37 HOLD CLOSED 维持；**未**混叶38；`live=false`；`promotion=false`；`leo_notify=false`
- **未**申 `.ok`；**未** Book-Smoke；**未**自派 X2；**未**读价格/收益；**未** git commit

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 主变体候选 | **`dark_horse_add`**（冻结优先级先 DH 后 crowd） |
| crowd_add | gate_pass=`true`（备选） |
| 池 | **ALLA**（`research/all_a_universe_mask.py`）；**非** mid_large 主口径 |
| 基线 | RERUN events **`6c8e6613`** / JSON **`9f214237`**（无池滤） |
| peak_rss_mb | **249.2**（≤1500；未抬） |
| pgrep | 空 → 开；web_exempt=true |

## C1 前缀闭环

| 件 | 路径 | sha8 | 全长 |
|---|---|---|---|
| WHO 前缀快照 | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | **`05346562`** | `053465623702bc176cfc6e192c03cc9bb81a20435d732715b1bc3d734732858c` |
| ALLA 前缀快照 | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | **`9a90c4eb`** | `9a90c4eb6c3448af3b9ceaa9ba1e83f88f5c641ce70d679bfd5c04626165f337` |
| 说明 | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | **`956588eb`** | — |
| 历史 WHO `a7add118` | sidecar 文面钉 | — | **ABSENT**（未伪造 HIST） |
| 历史 ALLA `ee7bfc79` | Arch/RECEIPT 文内钉 | — | **ABSENT**（盘上 ALLA `.sha256` 现为 `09eff235…`≠该钉；未伪造） |

写附录后前缀复算：WHO **`05346562`** / ALLA **`9a90c4eb`** → **MATCH**。

## 计数摘要（C2）

### dark_horse_add
- 全窗 **12763**（RERUN 13035，剔 272）；X2 事件 **5348**；X2 不同股票 **2835**
- 年 2024/2025/2026：**1727** / **2007** / **1614**
- 全压舱日 **1.65%**（11/668）；稀疏风险=否

### crowd_add
- 全窗 **21557**（RERUN 21751，剔 194）；X2 **9476**；X2 股 **2063**
- 年 2024/2025/2026：**3302** / **3518** / **2656**
- 全压舱日 **1.65%**；稀疏风险=否

## 文件钉（C2 后）

| 文件 | 对照 | 新 sha8 | 全长 |
|---|---|---|---|
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | 前 `604d777d`；前缀 `05346562` | **`547b246e`** | `547b246e64de4a3c358e78bd4a95a187849da22e3cb8947e238633b498716f36` |
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | 前 `0cbfacd9`；前缀 `9a90c4eb` | **`724e1df5`** | `724e1df52c1e69a21dc6e9ae725000266845e77b44aff9604662fab663d35e06` |
| `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | — | **`d6024472`** | `d60244728d9c87630373dc0ede7e6548acb579bf0506c6493e49d7ecbcfad292` |
| `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | — | **`81afda13`** | `81afda134adcf63af0b36d540c73a0aa71f0859682c45cda1a9647d32451be62` |

## Data / 输入钉 MATCH

| 钉 | expect | 状态 |
|---|---|---|
| Arch RERUN 审 | `b410680b` | **MATCH** |
| DATA / AE / O / E / DIG | `e2f1ccbc` / `d96b83e1` / `50b32700` / `07e01516` / `fa973826` | **MATCH**（E 未动） |
| RERUN JSON/events/RECEIPT | `9f214237` / `6c8e6613` / `e3cc0143` | **MATCH**（基线保留） |
| 旧 FAIL | `f36d0a04` | **MATCH**（保留） |

## 禁项回执

- 未改「计数附录」以上任何冻结条款（前缀 MATCH `05346562`/`9a90c4eb`）
- 未读收益/股价序列；浮筹沿用基线持仓字段结果
- 未用 mid_large 作 C2 主口径；未用 ETF/E 冒充 AE；E 未动
- 未混叶38；未自签 `.ok`；未挂 QUIET；未 Book-Smoke；未自派 who_pays/X2；未 git commit
- 未报 Leo；live=false；promotion=false

## 下一跳

交主 → **Arch 再只审**（C1 快照 + C2 ALLA 附录）。禁自派 X2。
