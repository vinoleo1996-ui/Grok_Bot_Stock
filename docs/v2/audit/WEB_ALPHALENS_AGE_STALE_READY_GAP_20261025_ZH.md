# Web 看板 × AlphaLens hub：age_s / stale / ready 缺口对照（A5）

- **专责**：QuantLab Web
- **日期**：2026-10-25（时间均为 America/New_York / ET）
- **live**=false · **不改生产码** · 本文档优先；改码另签
- **来源计划**：`docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` A5
- **对照 refs**：`docs/v2/refs/alphalens_workbuddy/hub.py`（及 README 中 `/api/health` 说明）
- **现看板**：`/workspace/quantlab-web/`（server.py / apis.py / freshness.py / static/app.js / app.html / API.md）

---

## 1) hub.py 行为摘要（带行号）

### 1.1 核心字段定义

| 概念 | 定义 | 行号 |
|---|---|---|
| `age_s` | 距上次成功 `put` 的秒数；从未写入则为 `None` | `Hub.age` L104–106；`meta` L118–120 |
| `stale` | 从未写入 **或** `now - at > ttl` | `Hub.stale` L114–116 |
| `updated_at` | 上次 `put` 时刻的本地 `%H:%M:%S`；未写入则为 `None` | `meta` L118–120 |
| `ttl` | 每次 `put(key, value, ttl=…)` 单独记录；缺省 60s | `Hub.put` L108–112；`status` L152–158 |
| `ready` | `quant` 快照有 `rows` **且** `quotes` 非空 | `ready()` L598–599 |
| `error` | 刷新异常或空源时写入 `hub.err[key]`，不覆盖 last-good | `refresh` L128–136；`status` L156 |

`meta(key)` 对外统一返回：`{updated_at, age_s, stale}`（L118–120）。  
`status()` 对每个已缓存 key 再附上 `ttl` 与 `error`（L152–158）。  
`snapshot()` 顶层带 `ready`，并对 quotes/bars/quant/etf/sector_flow/allocation 附 `meta`（L602–612）。

### 1.2 空结果与 TTL 规则（「空不写长缓存」）

`Hub.refresh`（L122–138）要点：

1. **`val is None`**：不调用 `put`，保留旧值与旧 `at`/`ttl`（L128、L133）。
2. **指定 key 且空容器**（`bars` / `flow_stock` / `sector_flow` / `quotes` / `etf_flow_map`）：  
   置 `err[key]="empty_source_response"`，**直接返回旧值，不 `put`**（L129–131）。  
   → 空结果**不会**刷新 `at`，也就**不会**把 `age_s` 归零、**不会**把 `stale` 打成 false。  
   这就是「空结果不写长 TTL / 不污染 last-good」。
3. **异常**：记 `err`，返回 `self.data.get(key)`（L134–136），同样不推进 TTL 时钟。
4. **行情特判** `_refresh_quotes`：若本批无有效价，只写 `err["quotes"]="empty_source_response"` 并 `return`，不 `put`（L215–217）。

对比：成功路径才 `put(key, val, ttl)`（L132），TTL 时钟从成功写入起算。

### 1.3 前端契约（refs README）

- 不做假实时：响应带 `updated_at / age_s / stale`，UI 显示「数据 X 秒前」（README「不装实时」）。
- `GET /api/health`（或 `/api/hub`）展示服务状态与各数据集 `age_s` / `stale` / `error`；`ready` 表示首屏量化+行情是否可用。

---

## 2) 现看板缺口对照表

口径说明：

- **已有**：语义接近，可直接映射或轻微改名。
- **部分**：有新鲜度概念，但粒度/单位/契约不同。
- **缺失**：无对应字段或行为。

| AlphaLens hub 能力 | 现看板对应 | 状态 | 说明（文件:行或端点） |
|---|---|---|---|
| 每数据集 `age_s`（秒） | `/api/freshness` 的 `lag_trading_days`；横幅「滞后 N 交易日」 | **部分** | freshness.py L14–18、L34–35、L78–81；app.js `freshBanner` L171–184。单位是**交易日**，不是秒；且是「最新交易日 vs 今日」而非「距上次成功刷新」 |
| 每数据集 `stale`（相对自身 TTL） | `overall` / `level` = ok\|yellow\|red（>1 / >2 交易日） | **部分** | 固定日历阈值，不是 per-key TTL；无 `stale: bool` |
| 全局 `ready`（首屏可服务） | `/healthz` 的 `ok`；snapshot 始终可返回磁盘 JSON | **部分** | healthz=`进程存活`，**不是**「关键数据集已预热」。无 `ready` 布尔 |
| `updated_at` / `generated_et` | snapshot.`generated`；apis.`generated_et`；freshness.`generated_et` / `dashboard_generated_et` | **已有** | snapshot.py L63；apis.py L32；freshness.py L78–80。是生成时刻，不是 per-dataset `at` |
| 顶栏「数据 X 秒前」 | 顶栏「滞后 N 交易日」+ 看板生成/部署时间 | **部分** | app.js L180–182；适合日频纸面轨，不适合秒级内存快照 |
| 空结果不刷新 TTL / 保留 last-good | 文件源模型：读失败多半缺字段或旧 mtime；无统一 empty→keep-last API 层 | **缺失**（Web 侧） | 看板从磁盘/parquet 组装，不是 hub 式内存 put。空/失败时是否写坏中间文件属 **Data/写端**；Web 展示层亦无 `error: empty_source_response` 契约 |
| per-key `ttl` 暴露 | 无 | **缺失** | freshness/API.md 未定义数据集 TTL |
| per-key `error`（含 empty_source） | freshness `sources[].note`（如静默「沿用上次读数」） | **部分** | freshness.py L48–53；不是结构化 `error` 枚举 |
| `status().keys` 聚合 | freshness.`sources[]` + `agents[]` | **部分** | 有多源列表，缺 age_s/stale/ttl/ready |
| 静默期不读真实行情 | `/api/freshness` 静默复用 `_MKT`；kline 只回缓存 | **已有** | freshness.py L48–57；API.md L89–91；与 A5 正交但保留 |

**结论（Web）**：看板已有「日频新鲜度横幅」，**没有** hub 式「秒级 age_s / per-TTL stale / ready」。A5 吸收应做**最小增量**（扩展 freshness 或轻量 `/api/hub_status`），而不是移植 AlphaLens 全站内存 hub。

---

## 3) 最小 UI/API 草案（文档优先；改码另签）

### 3.1 设计原则

1. **不移植** AlphaLens 内存刷新循环 / NeoData / 8722。
2. 复用现有 `/api/freshness` + 顶栏横幅，避免新大页。
3. `age_s` / `stale` / `ready` 的语义对齐 hub，但数据源仍是 QuantLab 文件/快照（日频为主）。
4. **空结果不写长 TTL**：写端（Data）禁把 empty 当 last-good；读端（Web）若检测到空/缺，**不**把 `age_s` 归零、**不**把 `stale=false`。

### 3.2 API 字段草案（建议挂在 `/api/freshness` 增量，另签改码）

在现有 freshness JSON 上增加（向后兼容，旧前端可忽略）：

```json
{
  "ready": false,
  "ready_note": "缺少 market_stock 最新交易日或 snapshot.nav 为空",
  "datasets": [
    {
      "key": "market_stock",
      "label": "行情最新交易日（个股 bars）",
      "updated_at_et": "2026-10-24T16:00:00-04:00",
      "age_s": 72000.0,
      "ttl_s": 172800,
      "stale": false,
      "error": null,
      "last_good_et": "2026-10-24T16:00:00-04:00",
      "empty": false
    }
  ]
}
```

| 字段 | 含义（对齐 hub） | 建议默认 TTL（草案，另签确认） |
|---|---|---|
| `age_s` | 距 `updated_at_et`（或文件 mtime / 交易日收盘锚点）的秒数；未知则 `null` | — |
| `ttl_s` | 超过则 `stale=true` | 日频行情/NAV：约 2 个交易日折合秒（或显式用交易日阈值，见下） |
| `stale` | `updated_at` 缺失或超 TTL | 与现 `level` 可并存：过渡期可用 `stale ≈ (level != ok)` |
| `ready` | 看板首屏关键集齐：建议 `snapshot` 可读且 `paper_nav`+`market_stock` 非空且非 unknown | 对齐 hub「quant.rows ∧ quotes」的精神，映射到纸面轨关键源 |
| `error` / `empty` | 源空或读失败；若 empty=true，则不得刷新 last_good、不得把 age_s 置 0 | 对应 hub L129–131 |

**日频特例（推荐写进实现注释）**：纸面轨/行情以「交易日」为真相时，可用：

- `stale = (lag_trading_days > 1)`（黄）作为默认；
- 同时仍输出 `age_s`（墙上秒），供「X 小时前」展示；
- `ttl_s` 仅作辅助，避免和 SSE 日历双标准打架。

**空结果规则（Web 读侧，必须）**：

1. 构建某 dataset 时若读到空表 / 缺列 / 空文件 → `empty=true`，`error="empty_source_response"`（或等价），**沿用**进程内/磁盘缓存的上一笔 `last_good_et` 与 `age_s` 基准。
2. **禁止**用「本次构建时刻」冒充 `updated_at`。
3. 静态导出 `/api/freshness.json` 同规则：空结果不得把线上 TTL/新鲜度「刷绿」。

`/healthz`：**不**塞完整 datasets（避免无 token 泄露细节）；可选只加 `ready: bool`（另签）。完整列表留在需 token 的 `/api/freshness`。

### 3.3 UI 草案（`static/app.js` 横幅，另签）

在现有 `#freshBanner`（app.js L171–184）上增量：

1. 标题旁增加：`ready` → 「首屏就绪」/「预热中」小徽章。
2. 明细表新增列：`age_s`（格式化为「Xm / Xh / Xd 前」）、`stale`（是/否）、`error`（若有）。
3. 保留现有「滞后交易日」列（纸面门禁仍认交易日）。
4. 文案避免假实时：写「数据更新于 …（X 前）」，不写「实时」。

`app.html`：无需新页；横幅仍插在 `.dash-header` 后。

### 3.4 文档同步（另签改码时）

- `API.md`「GET /api/freshness」节补充 `datasets[]` / `ready` 字段表与空结果规则。
- 不新增 AlphaLens 禁抄项（8 维主 alpha、LLM 辩论下单等）。

---

## 4) 非目标与依赖

### 4.1 非目标（本 Web 吸收不做）

- 不移植 hub 常驻刷新循环、NeoData、8722、内存 quotes/bars。
- 不把 AlphaLens OOS 负超额策略当候选叶。
- 不改研究 parquet、不下单、不抬 live。
- 不在本文档回合改 `server.py` / `freshness.py` / 前端生产文件（**改码另签**）。
- 不解决 Data「双测写空文件污染」本身——只定义 Web 展示契约与消费规则。

### 4.2 归 Data / Eng

| 项 | 归属 | 说明 |
|---|---|---|
| 双测/健康回执带 last-good vs empty 污染禁令 | **Data**（计划 A5） | 写端禁止用 empty 覆盖 last-good；健康回执区分 empty 与 stale |
| 日更 DONE/FAILED、行情 parquet 完整性 | **Data** | Web 只读展示 |
| 纸面 append-only / T+1 结算语义 | **Eng**（计划 A3） | 与 age_s 展示正交 |
| 回测≡实盘、provenance | **Arch**（A1/A2） | 不经 Web |

### 4.3 归 Web（后续另签改码）

1. freshness 增量字段 + 空结果不刷绿。
2. 横幅 UI 展示 age_s / stale / ready。
3. API.md 同步。
4. 与静默守卫兼容：静默期继续「不读行情 parquet、沿用上次读数」，且沿用时标记 `note`/`error`，不得伪装成新鲜 put。

### 4.4 建议验收（实现回合）

- 人为空源或缺失文件：API 中该 key `empty=true`，`age_s` 不归零，`stale` 不因空写而变 false。
- 正常有数：`ready=true` 当关键源齐；横幅可见「X 前」。
- live 始终 false；无 token 打印。

---

## 5) 文档自身 sha256

- **正文哈希**（本节标题及之前全部字节的 SHA256）：`299f697c4398e8a5e9714dd00e27e9cad0b3fe20d37c1c37fe769ed8af41bead`
- **整文件哈希**：见下一行（对「写入整文件哈希行之前」的文件字节计算；校验时可去掉最后一行后再 `sha256sum`）。

**整文件 sha256**：`92d974a8430ccb08645fd8eef5db3ba44c24907a3abca426a38a1356f1b4835a`
