# Arch 叶27 独立 .ok 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch（执行器）
- 时刻（America/New_York）：2026-10-25T11:02:19-04:00
- 例程：`27-ok-10-50`
- live=false；promotion_approved=false

## 结论

**PRE_OK_PASS=yes** → 已签 HI_LIQ 主路径独立 `.ok`（**不含 FULLA**）。

## 时间 / 叶25

| 项 | 值 |
|---|---|
| 开窗判定 | ≥10:50 ET **且** 叶25 现窗未开（旧 `7b279d47` VOID；新 v4 `1c32ab1e` 窗 **11:15–12:00** 相对当时为 FUTURE） |
| 叶25 实数进程 | **无**（pgrep leaf25/R5c_v4/ttm_recon/g1g5_on_minus 空） |
| 禁复用 | **不**复用 `7b279d47` |

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | 2026-10-25T11:00:03-04:00 |
| 2 healthz quiet=true（≤90s） | 2026-10-25T11:00:11-04:00 quiet=true |
| 3 再等 ≥15s | 至 11:00:44+ |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空** |
| MemAvailable@签 | 13153300 kB（≥2.5GiB） |

## 条件3 重哈希

| 项 | 期望 | 现盘 | 判定 |
|---|---|---|---|
| Data 盘点 | `acb8d3e0…825e9` | 同 | **MATCH** |
| AI 对照 | `63185c9f…7200f` | 同 | **MATCH** |
| 脚本 | `7a5f756c…08f8c6` | 同 | **MATCH** |
| DIFF | `e2ed0fc8…978b71` | 同 | **MATCH** |
| impl | `a532e6db…f87416` | 同 | **MATCH** |
| 闭合 | `f4327917…affc3e` | 同 | **MATCH** |

## 现盘字节复测

MATCH=9 / MISMATCH=0（MKTCAP / ETF / CAPADV_HILIQ / OHLC样本 / MASK / suspend_flags / 目录覆盖 n=2130/6026/5582）。

## FULLA

**gap** — Data 盘点未列 FULLA 权重 sha → 本 `.ok` **仅 HI_LIQ**；`allow_fulla=false`。

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ.ok` |
| sha256 | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` |
| sha8 | `725be3e0` |
| 窗 | 2026-10-25T10:50:00-04:00 → 2026-10-25T11:12:00-04:00（expires 2026-10-25T11:14:00-04:00） |
| 禁窗 | 叶25 2026-10-25T11:15:00-04:00/2026-10-25T12:15:00-04:00 |

## 非动作

- **未**启动研究实跑；签完后可撤静默锁（由 AI 开跑前自设）
- 不删例程；不 WakeParent；不报 Leo（由父/主裁）
