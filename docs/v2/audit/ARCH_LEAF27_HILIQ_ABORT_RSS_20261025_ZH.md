# Arch 叶27 HI_LIQ 实跑中止（RSS 越界）2026-10-25

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T11:14:02-04:00
- live=false；promotion_approved=false

## 结论

**ABORT_RSS_OVER_LIMIT** — pid 615199 已 TERM/确认 STOPPED；`.ok` `725be3e0` **不得继续消费**；禁自重跑。叶25 v4@11:15 让路。

## 证据

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ.ok` sha8 `725be3e0` |
| 授权 rss_limit_mb | **1500**（rss_limit_kb=1536000；stopkb=1484800） |
| 实跑 cmd | `--universe HILIQ --window both`（universe 合规；window both=x2+sealed 合规） |
| 启动 | 2026-10-25T11:11:41-04:00 前后 |
| 中止 | 2026-10-25T11:14:02-04:00（window_end 11:12 已过；expires 11:14） |
| 日志 rss 峰值 | 日志行见 **≈3557MB**（2025-05-12 n=2553）；进程表 RSS≈**3541MB** @11:13 |
| sampler | `/tmp/quantlab_leaf27_20261025_111140/sampler_30s.txt`（未写 output*） |
| 产物 | out_dir 仅 `_logs` + `_preflight_*`；**无** alpha parquet |
| QUIET | 中止时已无 lock |

## 裁示

1. AI：禁复用本 `.ok` 重开；交正式中止回执；让出叶25@11:15（v4 `1c32ab1e`）。
2. 主：叶27 另窗须 **降内存包**（分窗 x2/sealed 或分块）后再申签；FULLA 仍 GAP。
3. Web healthz 缓存滞后小修：叶25 窗后再送审（不挡本中止）。

live=false。
