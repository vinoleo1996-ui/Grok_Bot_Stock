# probe5_small 重建落盘说明（2026-10-25）

- 时刻：2026-10-25 ~04:50 ET
- 原因：盒刷丢失 `/tmp/relay_probe/probe5_small.py`（原钉 sha256 `601a092fef871e917098cddddeb7c65c17627b804d7e4c2f35f413ef1b5bd77f`）；Eng/Mac 均无副本
- 锚点回执：`docs/v2/audit/relay_probe_20261018/PROBE5_SELFTEST_RECEIPT_20261018_122103.md`、`PROBE_1250_RECEIPT_20261018_125839.md`；今日 `RELAY_PROBE_RECEIPT_20261025T0024ET.md`
- **仓库路径**：`docs/v2/audit/relay_probe_20261025/probe5_small.py`
- **新 sha256**：`1c3999c7b73bcb7c74b9efdfcc568366e148cbac44e1299b11c2e5e06e59ad21`（sha8 `1c3999c7`）→ **请 Arch 重钉**（PIN_MISMATCH vs 601a092f）
- 口径：connect 15s / read 115s / wall 120s；`--only trade_cal|stock_basic`；stock_basic limit=100；BIG_PAGE=5000
- 恢复副本：`_recovery/data/relay_probe_20261025/probe5_small_1c3999c7b73bcb7c.py`
- 已用此脚本跑过一轮（回执 `RELAY_PROBE_RECEIPT_20261025T0448ET.md` sha8 `5d208af6`）：**不通**（SSL EOF）。Arch 重钉后再跑官方只读轮。
- live=false；不写生产。
