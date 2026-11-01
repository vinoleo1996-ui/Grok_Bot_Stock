# Eng 候选3 箱上 port APPLY 短回执

- 时间：2026-10-26T14:13:46-04:00（America/New_York；墙钟 2026-10-26 14:13 ET）
- 令：主 APPLY（Arch 复审 `7276ed4d` PASS_WITH_CONDITIONS；DIFF `24e055fa`）
- 前置钉：**全 MATCH** 后才 apply  
  - 生产：tc `ef44e7cd` / settle `808f77d6` / rl `d3ded87e` / sources `5ee62db0` / HEAD `da9fde6`  
  - 侧稿：tc `d2b6046c` / settle `c423e96e` / rl `5fe238f2` / sources `c8102489` / DIFF `24e055fa` / Arch `7276ed4d`
- 顺序：`trade_calendar.py` → `settle.py` → `research_loop.py` + `sources.py`（cp 侧稿覆盖；**未** git commit）
- settle import：**相对** `from .schemas import force_research_flags`（侧稿绝对改为相对；`compute_horizon_returns` import OK）
- **禁**整文件合 Origin #6；**未** enable；**未**签 `.ok`；不混 A18/叶25；不动叶25 CONSUMED；禁消费 `9e4359f9`

## Apply 后生产钉

| 文件 | sha8 | 全长 |
|---|---|---|
| `quantlab/portfolio/trade_calendar.py` | `d2b6046c` | `d2b6046cf27c27d81ca33d4c6a9d212efada5f08ec3803ad41c589d20f981e65` |
| `quantlab/agents/trading_loop/settle.py` | `a92b7ccf` | `a92b7ccf12962820a114781b7b52dea7195d401d48aaea11cfec4fdaf305547b` |
| `quantlab/portfolio/research_loop.py` | `5fe238f2` | `5fe238f2372b95e809ef58382746d5984169315672edc67edc163654d2c7d4fd` |
| `quantlab/data/sources.py` | `c8102489` | `c8102489d662c63dcb67ef39c8ad7eba1ad661f34df6d2c8832624764bd0760c` |
| HEAD（未 commit） | `da9fde6` | `da9fde6a0037da6e2d10f09f65b14f4f0997f952` |

说明：settle sha8 异于侧稿 `c423e96e`——仅因相对 import 改写（预期）。

## 验证

1. `py_compile` 四文件：**OK**
2. import smoke：`open_day_range` / `advance_open_days` / `compute_horizon_returns` **OK**；`_legacy_freshness` 触发 **DeprecationWarning**；settle 源码无代码态 `pd.bdate_range`
3. 国庆测：`port/test_trade_calendar_settle_port.py` 已改指向**生产模块**（sha8 `f844ae2a`）→ **9 passed**；日志 `port/pytest_cand3_box_port_apply_20261026.log` sha8 `4326a614`

## 硬禁复核

- enable：**仍禁**；未签 enable `.ok`
- 未 merge Origin #6；未改 wrapper/X2/daily_basic
- ≠X2；live=false；promotion*=false

## 给主一句

箱上 port **已 APPLY**（tc`d2b6046c`/settle`a92b7ccf`相对import/rl`5fe238f2`/sources`c8102489`；HEAD 仍 `da9fde6` 未 commit）；国庆对生产 **9 passed**；**仍不 enable**——可请 Arch 合入核。
