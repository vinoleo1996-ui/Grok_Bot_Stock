# 叶27 HI_LIQ 中止回执（ABORT_RSS_OVER_LIMIT）

- written_et: 2026-10-25 11:15:08 ET
- by: QuantLab AI
- live: false
- promotion_approved: false
- result: **ABORT_RSS_OVER_LIMIT**
- retry: **none**（`.ok` `725be3e0…` 禁再消费 / 禁自重跑）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ.ok` |
| `.ok` sha256 | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` |
| script | `research/g1g5_on_minus_id_idio_ivol_alpha.py` sha `7a5f756c…` |
| 窗 | 10:50–11:12 ET / expires 11:14 |
| 启动 | **11:11:41 ET**（window_end 前） |
| 命令 | `--universe HILIQ --window both` |
| pid | 615199（Arch TERM → STOPPED） |

## 中止原因

- 授权 `rss_limit=1500MB`；日志/进程峰值约 **3557MB**（超限）
- Arch 旁证：`docs/v2/audit/ARCH_LEAF27_HILIQ_ABORT_RSS_20261025_ZH.md` sha `37b63b8fb98739e86f3d5a0b2542ca3adc9627fe531566efd7082ef02d2e799d`
- **无** alpha parquet / 无完整 build_summary 产物

## 采样与 QUIET

- sampler：`/tmp/quantlab_leaf27_20261025_111140/sampler_30s.txt`（未写 output*）
- QUIET：已 lift（`_lifted/RESEARCH_QUIET_leaf27_DONE_LIFTED_20261025_111335ET.lock`）；healthz quiet=false @回执时
- AI 采样器与 yield_watch 已停

## 让出叶25

- 叶25 钉仍在：R5_v4 `.ok` `1c32ab1e…` + R5c_v4 `8231cf2d…`；例程 `25-1-11-15` @11:15
- **注意（开跑前须再核）**：回执时 `pgrep` 见 `export_static.py` 与 `kline.py` 进程——叶25 静默门禁要求为空；若仍在则**不开跑**，报 Arch/Data/Web

## 后续

- 叶27 另窗须 **降内存包** 后再向 Arch 申签；本 `.ok` 作废不重用
- live=false
