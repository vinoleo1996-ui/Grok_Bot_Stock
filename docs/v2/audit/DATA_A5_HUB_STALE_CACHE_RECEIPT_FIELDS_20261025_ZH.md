# DATA A5：hub stale / 空不写长缓存 → 双测·健康回执字段对照（文档 only）

- **角色**：QuantLab Data 执行器
- **计划**：`docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` **A5**（Leo 经主 Agent 批准 · 2026-10-25）
- **对照源**：`docs/v2/refs/alphalens_workbuddy/hub.py`
- **姊妹页（Web 专责）**：`docs/v2/audit/WEB_ALPHALENS_AGE_STALE_READY_GAP_20261025_ZH.md`（看板 age_s/stale/ready；**本页不改 Web**）
- **性质**：规范草案 + 缺口对照；**不改** `probe5_small.py`、不改生产 parquet、不签 `.ok`、不消费补跑包、`live=false`
- **ET**：2026-10-25 ≈11:45 America/New_York（箱内同时区）

---

## 1. hub 对照（表）

对照文件：`docs/v2/refs/alphalens_workbuddy/hub.py`（模块头 L1–13；`Hub` L89–158；空源 L129–131 / L215–217）。  
现盘样例回执：`RELAY_PROBE_RECEIPT_20261025T1056ET.md`、`…T0839ET.md`、`…T0634ET_DUAL_ROUND.md`、`…T0509ET_DUAL_ROUND.md`。  
探针脚本（只读）：`docs/v2/audit/relay_probe_20261025/probe5_small.py`（写盘仅 CSV append：`ts_et,api,params,elapsed_s,http_status,rows,error`；**无** HTTP 响应体长 TTL 缓存）。

| hub 机制 | AlphaLens hub.py 行为（引文件+行意） | QuantLab Data 现盘双测/健康回执现状 | 缺口 |
|---|---|---|---|
| `updated_at` / last-good | 仅成功 `put` 时写 `self.at[key]=now`（L108–112）；`meta` 输出 `updated_at`（L118–120） | 回执有本轮 `时刻` / CSV `ts_et`；**无**「最近一次双 API 均通」指针 | 缺 last-good 锚点字段 |
| `age_s` | `now - at`，从未写入则 `None`（L104–106） | 无；读者只能肉眼比多份回执时间戳 | 缺 `age_s_since_last_good` |
| `stale` | `at is None` 或 `age > ttl`（L114–116）；TTL 随 key（行情≈4s 等） | 有总评 `RELAY_DOWN` / `DUAL_STABLE_FAIL`，**非**相对约定频率的 stale 布尔 | 缺显式 `stale` + 频率阈值 |
| `empty_source_response` | 空容器关键 key：只 `err[key]=…`，**不 `put`**，返回旧值（L129–131）；quotes 无有效价同（L215–217） | CSV/回执有 `error`/`rows`；失败时 http 空、rows 空；**未**区分「本轮 empty」vs「保留 last-good」 | 缺 `this_run_empty` 与 last-good **并列** |
| 空结果是否写长缓存/TTL | 空/异常 **不刷新** `at`/`ttl`，不污染 last-good（L128–136） | 探针本身**不**写响应缓存（仅 append CSV）；健康回执**未**声明 `cache_write=forbidden_long`；后续若加磁盘/内存缓存无硬闸 | 缺回执级 `cache_write` 契约 + 禁令条文 |
| 状态聚合 | `status().keys[k] = meta + ttl + error`（L152–158） | 判定段写通断结论；无结构化字段块 | 缺可机对齐的回执字段块 |

**缺口 Top3（一句各）**

1. **无 last-good**：RELAY_DOWN 轮无法指向「最近双通回执」→ 健康态与空/失败轮混淆。  
2. **无 age_s / stale**：SUSPEND 时长靠人工翻历史 md，无法相对约定频率（建议 >3600s）自动标 stale。  
3. **无 cache_write 声明**：今日探针虽未写长 TTL，回执未把「空结果禁写长缓存」钉成字段；Eng 改脚本时易漏。

---

## 2. 拟改回执字段（规范草案 · **未实施**）

命名可微调，**语义必须齐**。字段落在回执 md 头部 YAML/表格块即可；CSV 可增列，改码另签。

### 2.1 单次探针回执（例：08:30 / 10:50）

| 字段 | 类型/枚举 | 语义 |
|---|---|---|
| `probe_status` | `PASS` \| `RELAY_DOWN` \| `DEGRADED` \| `BLOCKED_NO_KEY` | 本轮总评；主裁已钉：**不接受 degraded 当通** → 实务上 Data 单测失败即 `RELAY_DOWN`（`DEGRADED` 仅预留） |
| `last_good_ts_et` | `YYYY-mm-dd HH:MM:SS` ET 或空 | 最近一次 **trade_cal∧stock_basic 均 HTTP 200 且无 timeout/SSL 且 rows>0** 的回执时刻 |
| `last_good_receipt_sha` | sha256 全长或空 | 上指回执文件内容哈希 |
| `this_run_empty` | bool | 本轮是否空响应（无 HTTP body / JSON 无 rows / 双 API 皆失败导致无可消费行） |
| `cache_write` | `none` \| `short_ttl` \| `forbidden_long` | **空结果必须 `forbidden_long`**；今日探针仅 CSV → 正常写 `none`；若将来短缓存探测结果 → `short_ttl`（须另签 TTL 秒数） |
| `age_s_since_last_good` | float \| null | 本轮时刻 − `last_good_ts_et`；无 last-good 则为 null |
| `stale` | bool | `age_s_since_last_good is null` **或** `age_s_since_last_good > STALE_S`；**建议阈值 `STALE_S=3600`**（1h；与例程 08:30/10:50 间距同量级，可另签调整） |
| `error_trade_cal` / `error_stock_basic` | str \| 空 | 对齐 hub `err[key]`；可继续用现 CSV `error` 列 |

**对照现盘**：T1056 / T0839 皆 `RELAY_DOWN`，应填 `this_run_empty=true`（或至少双 API 无可消费成功体）、`cache_write=forbidden_long`（语义禁令；物理上今日 `none`）、`last_good_*` 指向历史最近双通回执（若有；否则空 + `stale=true`）。

### 2.2 双轮双测回执（例：T0634 / T0509）

继承 §2.1 全部字段，并增：

| 字段 | 语义 |
|---|---|
| `round1.probe_status` / `round2.probe_status` | 各轮是否双通（PASS 仅当该轮两 API 均通） |
| `round1.last_good_ptr` / `round2.last_good_ptr` | 各轮结束时指向的 last-good（通常同全局；若本轮某 round 双通则更新指针） |
| `dual_stable` | `DUAL_STABLE_PASS` \| `DUAL_STABLE_FAIL` | 与现总评一致 |
| `dual_stable_vs_last_good` | 文案枚举：`both_rounds_refresh_last_good` \| `one_round_refresh` \| `no_refresh_keep_prior` | **FAIL 且无刷新时必须 keep_prior**，禁止用失败轮冒充 last-good |
| `interval_s_r1_r2` | 轮间隔秒（现要求 ≥120） | 旁证解冻条件 |

**对照现盘**：T0634 `DUAL_STABLE_FAIL`（R1 双败 / R2 双通）→ `dual_stable_vs_last_good=one_round_refresh`（仅 R2 可更新 last-good）；T0509 双轮皆败 → `no_refresh_keep_prior`。

---

## 3. 空结果禁写长缓存（硬规则 · 条文化 · **本文件不改代码**）

供 Eng/Arch 后续改探针或健康脚本时对照：

1. **空/失败不得 `put` 长 TTL**：HTTP 非 200、ReadTimeout、SSL、JSON 无 rows、或 `rows==0` → **禁止**写入任何 TTL≥探针例程间隔（建议 ≥3600s）的响应体/行集缓存；回执必须标 `cache_write=forbidden_long`（或物理 `none` 且注明禁写）。  
2. **不得用空结果刷新 last-good**：`last_good_ts_et` / `last_good_receipt_sha` **仅**在双 API 均通且 rows>0 时更新；空轮只更新本轮 `probe_status`/`this_run_empty`/`age_s`/`stale`。  
3. **CSV 诊断日志 ≠ 长缓存**：允许 append `probe_log*.csv` / 回执 md（审计）；**禁止**把失败轮的空 body 落成「可被下游当行情/日历消费」的 parquet/json 快照。  
4. **短 TTL 例外须另签**：若 Eng 为降压加进程内短缓存，TTL 须 ≪ `STALE_S`（建议 ≤120s），且空结果仍走规则 1–2；回执标 `cache_write=short_ttl` + `ttl_s=`。  
5. **解冻消费门闩**：补跑 `.ok` / 生产拉取 **不得**仅凭「最近一轮有任一 API 200」；须 `dual_stable=DUAL_STABLE_PASS` **或**（单测路径）连续两例程 `probe_status=PASS`，且 `stale=false` 相对 last-good。

---

## 4. 非目标

- **不改** Web 看板（见 Web A5 姊妹页）。  
- **不移植** AlphaLens hub 常驻服务 / NeoData / 8722。  
- **不消费** 补跑 `.ok`（含旁证 `9e4359f9`）；不签新 `.ok`。  
- **不抬** `live`；本回合 **不改** `probe5_small.py`、不改生产数据、不改 `TEAM_STATE`。  
- 计划「不做」节对齐：不移植全站；不把其 OOS 负超额当候选叶。

---

## 5. 文末确认

- Data **未改生产**代码/数据；**未签** `.ok`；**live=false**。  
- 本文件为 A5 文档交付；字段落地与脚本改动 **另签**。  
- 全长 sha256（写盘后 `sha256sum`）：见下一行。

**整文件 sha256**：
4d616df8b5742c76eb08a907ea255726f4e9ffa64814559eed5d0215743d2975
