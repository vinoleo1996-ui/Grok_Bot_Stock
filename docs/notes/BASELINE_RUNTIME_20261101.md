# 基线运行（接线前）

环境：`/tmp/qlvenv`，依赖 `requirements-research.lock`，pytest 9.2.0。分支 `cursor/wire-core-runtime-5dc3`。未加 `--book-nav`。

- `tests/test_data_os.py` 与 `tests/test_ai_factor_factory_smoke.py` 在合计里通过。整次 pytest：15 passed，5 failed。
- `tests/test_skeleton_oneclick.py` 四项失败于 `quantlab/platform/strategy_feed.py` 导入 `quantlab.data.v2_readers`：`ModuleNotFoundError: No module named 'quantlab.data'`。
- `tests/test_skeleton_oneclick.py::test_live_dryrun_gates_only` 失败于 `FileNotFoundError: /workspace/data/v2/tushare_raw/trade_cal.parquet`。该文件不在检出里。不造日历去把这项跑绿。
- `python -m quantlab.cli skeleton-smoke` 退出码 1，同一 `ModuleNotFoundError`。`--skip-run` 还没执行到，因为导入 `quantlab.platform` 时就会加载 `strategy_feed`。

## 接线之后（同一环境）

- 原因是 `.gitignore` 的 `data/` 匹配了 `quantlab/data/`。已改成只忽略仓库根 `/data/`。
- `skeleton-smoke` 退出码 0，`strategy_promotion_approved=false`。
- `book-smoke --skip-run --stock-path <因子演化冒烟长表>`：`consumable.stock.status=book_consumable`，`nav_ran=false`。
- `book-smoke --run-nav` 退出码 1，`FileNotFoundError: data/v2/etf/etf_daily_adj.parquet`。没有写替代净值。
- `test_live_dryrun_gates_only` 仍然缺少 `trade_cal.parquet`，保持失败。
