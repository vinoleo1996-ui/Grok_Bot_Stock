# Arch 重钉：probe5_small 重建脚本（2026-10-25）

- 时刻：2026-10-25T04:49:18-04:00（America/New_York）
- 结论：**ACCEPT / 已重钉**（PIN_MISMATCH 预期；原钉不可恢复）
- live=false；勿与叶25 / 补跑 runner / enable / 纸面混签

## 背景

- 原钉 sha256 `601a092fef871e917098cddddeb7c65c17627b804d7e4c2f35f413ef1b5bd77f`（10-18 12:50 回执）经盒刷丢失于 `/tmp/relay_probe/`；Eng/仓库/Mac offline **无字节副本**。
- Data 按 10-18 自测+回执规格重建；主令要求落盘仓库路径后由 Arch 重钉。

## 核验

| 项 | 结果 |
|---|---|
| 重建 sha256 | `1c3999c7b73bcb7c74b9efdfcc568366e148cbac44e1299b11c2e5e06e59ad21` MATCH Data 宣称 |
| 仓库落盘 | `docs/v2/audit/relay_probe_20261025/probe5_small.py` 同字节 |
| 运行时路径 | `/tmp/relay_probe/probe5_small.py` 同字节（可作执行副本） |
| 超时 | connect=15 / read=115 / wall=120 MATCH |
| stock_basic | limit=100；BIG_PAGE=5000 仅判 big_page_full |
| 范围 | 仅 trade_cal / stock_basic；无重试；不写生产 parquet；不导入 QuantLab 项目代码 |
| 密钥 | 自 `.env.datasources` / env；不打印 |

## 已签授权

- `.ok`：`output/data/ARCH_RUN_AUTH_PROBE5_SMALL_REPIN_20261025.ok`
- sha256：`1f0d7f30e98eb989d598c6a34d41523b036d0033e50104b35f7ae7de19567051`
- 旁证钉：`docs/v2/audit/relay_probe_20261025/PROBE5_SMALL_PIN.txt` sha `8d27c5a6707699b709a38c0b42ff283aff0a08cf2a0682a5cd765d5f84a5c1a9`

## 与 0448 回执关系

- Data 已交 `RELAY_PROBE_RECEIPT_20261025T0448ET.md`：**两 API 均 SSL EOF → 不通**。
- 该回执作中转现状证据；**本重钉不把 0448 判为 PASS**。
- 后续探针须用本钉 sha `1c3999c7…`（仓库或 /tmp 同字节均可）；通后再谈补跑实跑。

## 补跑边界（澄清）

- 窗口授权 `ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok` sha `9e4359f9…` **仍有效**（授权专用执行器，非 nightly）。
- **实跑**仍挡：①中转探针 PASS；②Eng 交齐 runner 包并由 Arch 审签。不堵 Eng 准备包。

## 给 Data 的用法

```bash
# 推荐：从仓库副本同步到 /tmp 后再跑（防再丢）
install -m 755 docs/v2/audit/relay_probe_20261025/probe5_small.py /tmp/relay_probe/probe5_small.py
nice -n 10 timeout 130 python3 /tmp/relay_probe/probe5_small.py --only trade_cal </dev/null
nice -n 10 timeout 130 python3 /tmp/relay_probe/probe5_small.py --only stock_basic </dev/null
```

跑完交回执路径 + 是否可补 1019–23。live=false。
