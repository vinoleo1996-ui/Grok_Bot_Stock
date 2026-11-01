# Arch 叶27 LOWMEM×x2 独立 .ok 开窗预检证据（2026-10-25）

- 角色：QuantLab Arch
- 时刻（America/New_York）：2026-10-25T11:45:53-04:00
- 主裁：开放另窗（采纳审阅 `aefa7faa` PASS_WITH_CONDITIONS）
- live=false；promotion_approved=false

## 结论

**PRE_OK_PASS=yes** → 已签 HI_LIQ **LOWMEM v1 × `--window x2`** 独立 `.ok`（**不含** sealed / FULLA / both）。

## 预检链

| 步 | 结果 |
|---|---|
| 1 设 `output/loop/RESEARCH_QUIET.lock` | 2026-10-25T11:42:51-04:00 |
| 2 healthz quiet=true（≤90s） | 2026-10-25T11:43:19-04:00 quiet=true |
| 3 再等 ≥15s | 至 11:43:34 |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} |
| 5 pgrep 括号逃逸 | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` **空** |
| MemAvailable@签 | 12075564 kB（≥2.5GiB） |

## 钉表重哈希

| 项 | sha8 | 判定 |
|---|---|---|
| 脚本 lowmem_v1 | `05bd81ea` | **MATCH** |
| DIFF 文 | `b1455e93` | **MATCH** |
| 封面 | `1521e1a4` | **MATCH** |
| unified patch | `2154b6fb` | **MATCH** |
| Arch 审阅 | `aefa7faa` | **MATCH** |
| ABORT 旁证 | `37b63b8f` | **MATCH** |
| Data 盘点 | `acb8d3e0` | **MATCH** |
| AI 对照 | `63185c9f` | **MATCH** |

## 签发

| 项 | 值 |
|---|---|
| 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.ok` |
| sha256 | `8bcd79dcc7a0e10640f2b7807a7e632ba2a6b7e20e385dfc1d58d07487fc9078` |
| sha8 | `8bcd79dc` |
| 窗 | 2026-10-25T11:45:00-04:00 → 2026-10-25T12:45:00-04:00（expires 2026-10-25T12:47:00-04:00） |
| CLI | `--universe HILIQ --window x2` |
| rss_limit | 1500MB（禁抬帽） |
| 禁复用 | VOID `725be3e0`；叶25 `1c32ab1e` |
| 禁 CLI | `--window both` / `sealed`（本 ok）；FULLA |

## 非动作

- **未**代跑；签完后撤静默锁（AI 开跑前自设）
- sealed 须另签另进程
- FULLA 仍 GAP
