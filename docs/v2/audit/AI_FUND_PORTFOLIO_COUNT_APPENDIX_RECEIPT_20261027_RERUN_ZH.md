# fund_portfolio 计数附录回执（RERUN · gate_pass=true）

- 角色：QuantLab AI（执行器）
- 时刻：2026-10-27 21:10 ET（America/New_York）
- dig：sha8 **`fa973826`** / 全长 `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`（文内自称 `a6ddc4ef` 勿采）
- 旧 FAIL 回执保留：`docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_ZH.md` **`f36d0a04`**（史）
- 叶37 HOLD CLOSED 维持；**未**混叶38；`live=false`；`promotion=false`；`leo_notify=false`
- **未**申 `.ok`；**未** Book-Smoke；**未**自派 X2；**未**读价格/收益；**未** git commit

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`true`** |
| 主变体候选 | **`dark_horse_add`**（优先级先 DH 后 crowd；两变体均过闸） |
| crowd_add | 亦 gate_pass=true（备选） |
| fund_portfolio_dh | **34** 季 MATCH（20180331→20260630） |
| 过滤 | AE 14241 ∩ 前十大；股票 `.SH`/`.SZ`；**未施** mid_large/ALLA 池滤 |
| peak_rss_mb | **676.3**（≤1500） |
| web_exempt | 是（仅 export_static/kline） |

## 计数摘要

### dark_horse_add
- 全窗 **13035**；X2 事件 **5386**；X2 不同股票 **2847**
- 年 2024/2025/2026：**1739** / **2019** / **1628**
- 全压舱日 **1.65%**（11/668）；稀疏风险=否
- 浮筹缺口剔除 4343（持仓字段无法可靠估算；未读股价）

### crowd_add
- 全窗 **21751**；X2 **9511**；X2 股 **2068**
- 年 2024/2025/2026：**3316** / **3529** / **2666**
- 全压舱日 **1.65%**；稀疏风险=否

## 文件钉（本拍追加后）

| 文件 | 追加前/对照 sha8 | 追加后 sha8 | 全长 |
|---|---|---|---|
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | 冻结正文 `a7add118`；旧附录版 `5393a769` | **`604d777d`** | `604d777d2ecb2954b3a35e442aed77f041fe9df53ee6e946b527033b2719a5f0` |
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | 旧附录版 `8ef304f5`；条款前 `ee7bfc79` | **`0cbfacd9`** | `0cbfacd9f0495df30abd8d041747788916f89984524c6dc9de27c2685746bee9` |
| `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun.json` | — | **`9f214237`** | `9f214237fe8a86a0c870eeed1d094e37af688098f786a2ffa36ccda07b42c75f` |
| `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | — | **`6c8e6613`** | `6c8e661325e7571140bc68c227f4f878921d6c3d196ccf64eea196d57340cafa` |

## Data / 输入钉 MATCH

| 钉 | 路径 | expect | got | 状态 |
|---|---|---|---|---|
| DATA_RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc` | **MATCH** |
| AE | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| O | `data/v2/etf/raw/fund_basic_O.parquet` | `50b32700` | `50b32700` | **MATCH** |
| E | `data/v2/etf/raw/fund_basic_E.parquet` | `07e01516` | `07e01516` | **MATCH** |
| DIG | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | `fa973826` | **MATCH** |
| OLD_RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_ZH.md` | `f36d0a04` | `f36d0a04` | **MATCH** |

## 禁项回执

- 未改「计数附录」以上任何冻结条款（WHO/ALLA 前缀字节与冻结快照一致）
- 未读收益/价格序列；trade_cal 只读日历
- 未动 fund_basic_E；未用 ETF-only 冒充主动权益
- 未混叶38；未自签 `.ok`；未挂 QUIET；未 Book-Smoke；未自派 X2；未 git commit
- 未报 Leo；live=false；promotion=false

## 下一跳

过闸 → **等主排**（禁自派 X2）。FAIL 史文件保留勿删。
