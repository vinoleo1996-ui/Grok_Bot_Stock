# fund_portfolio 计数附录回执（口径未齐 FAIL）

- 角色：QuantLab AI（执行器）
- 时刻：2026-10-27 20:33 ET（America/New_York）
- dig：sha8 **`fa973826`** / 全长 `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101`（文内自称 `a6ddc4ef` 勿采）
- 叶37 HOLD CLOSED 维持（Alpha `384fb9db` / Arch `4afd5ae1`）；**禁**复跑 `015e6f06`/`32605aca`/`108aba8f`/`57ab9096`
- `live=false`；`promotion=false`；`leo_notify=false`；**未**申 `.ok`；**未** Book-Smoke；**未**自派 X2；**未**读价格/收益

## 结论

| 项 | 值 |
|---|---|
| **gate_pass** | **`false`** |
| 原因 | **口径未齐**：缺主动权益 `fund_basic`（盘上仅 `fund_basic_E` market=E） |
| fund_portfolio_dh | **34** 季 MATCH（20180331→20260630） |
| dark_horse_add / crowd_add | **未计数**（过滤不可信） |
| 冻结条款 | **未改**（仅替换「计数附录」段） |

## 文件钉（追加后）

| 文件 | 追加前 sha8 | 追加后 sha8 | 追加后全长 |
|---|---|---|---|
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `a7add118` | **`5393a769`** | `5393a7696139275184d55394a21d9462447e73c2ae4b88761c51a311316e3593` |
| `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `ee7bfc79` | **`8ef304f5`** | `8ef304f51ed66439105c03bd6b11adfe76681d3854779826d37521220a40bbf5` |

## Data 待办（再跑计数前置）

1. 补 `fund_basic` 场外/主动权益满窗（market=O 等；覆盖 2018→2026）
2. 类型过滤回执：主动权益集合；剔除指数/ETF/联接口径写死
3. 回执到位后，方可对两份 FROZEN 文末「计数附录」重跑 PIT 计数（仍禁读收益）

## 禁项回执

- 未用 ETF-only 表冒充主动权益过滤
- 未改附录以上任何冻结条款
- 未 git commit
- 未申 `.ok` / 未挂 QUIET / 未开 X2

下一跳：转 **叶38 非标审计意见剔除 overlay** who_pays + HI_LIQ 计数；请主裁 Data 补 fund_basic / Arch 审叶38 / HOLD。
