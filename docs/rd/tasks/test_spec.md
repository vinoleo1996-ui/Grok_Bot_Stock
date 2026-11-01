# 测试 SPEC

算法落地前的失败条件。样例在 `tests/test_rd_contracts.py`。

- 申万成员 `available_at` 的上海日期不早于决策日时，`sw_l1_asof` 不得返回该行业。
- `load_merged_panel` 与 `load_etf_510300` 在文件不存在时抛 `FileNotFoundError`，不返回空行情冒充成功。
- 读取结果的 `promotion_approved` 为 false。
- 复权因子 `bfill` 仍会把未来因子填进缺口。该样例标记为预期失败，不得改成通过来关闭 `architect-002`。
