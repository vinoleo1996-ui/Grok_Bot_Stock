# 复权因子向过去回填

证据：`quantlab/smallcap/panel.py` 第 94 行 `factor.ffill().bfill()`。

`tests/test_rd_contracts.py` 里对应样例是预期失败。状态 open。这轮不改选股公式，所以不在这里改行为。
