# 叶27 LOWMEM HILIQ×x2 中止回执（ABORT_RSS_OVER_LIMIT）

- **角色**：QuantLab AI
- **written_et**：2026-10-25T11:51:40-04:00（America/New_York）
- **live**：false · **promotion_approved**：false
- **result**：**ABORT_RSS_OVER_LIMIT**
- **retry**：**none**（本 `.ok` 已消费意图；禁再消费 / 禁自重跑 / 禁抬帽；VOID/归档听 Arch）

## 钉与窗

| 项 | 值 |
|---|---|
| `.ok`（签发路径） | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.ok` |
| `.ok` sha256（签发正文） | `8bcd79dcc7a0e10640f2b7807a7e632ba2a6b7e20e385dfc1d58d07487fc9078` |
| `.ok` 现盘 | 主 park 后 Arch/主 **正式 VOID**：`_consumed/ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.8bcd79dc.VOID.ABORT_RSS.20261025T1152ET.ok`（此前 ABORT_RSS park 戳；签发正文剥离戳后 MATCH `8bcd79dc…`） |
| 禁复用 VOID | `725be3e06370927fc6ee115004e017212f7fd1dae077f2dfc63cedd62dae5e1a` — **未复用** |
| script | `research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py` |
| script sha256 | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` — **MATCH** |
| approved_cmd | `/workspace/qlvenv/bin/python research/g1g5_on_minus_id_idio_ivol_alpha_lowmem_v1.py --universe HILIQ --window x2` |
| rss_limit | **1500** MB（禁抬帽） |
| 窗 / expires | 11:45→12:45 ET / expires 12:47 ET（Arch 签发窗） |
| Arch 审阅 | PASS_WITH_CONDITIONS `aefa7faa9974cd891fb097a7491a7f72534c92189c7f478ab58092fca79973fb` |

## 执行（本回执主钉：ET_TS=20261025_115003）

| 项 | 实填 |
|---|---|
| ET_TS | `20261025_115003` |
| started_et | ≈2026-10-25T11:50:03-04:00 |
| ended_et | ≈2026-10-25T11:50:22–11:50:59-04:00（进程 gone；主戳记 TERM@11:50:22） |
| run_pid | `720992`（**/proc gone**） |
| sampler_pid | `720991`（gone） |
| rc | **ABORT**（加载后中止；无正常完成码；无 alpha 写出） |
| result | **ABORT_RSS_OVER_LIMIT** |
| interpreter | `/workspace/qlvenv/bin/python` |
| log | `output/ai_factory/leaf27_on_minus_id_idio_ivol_lowmem_x2/_logs/run_20261025_115003.log` sha `e860ba229d905c3ec6eb82c5bec6d1ad81d53802bd929d55d429add29a1d8ba0` |
| sampler | `/tmp/quantlab_leaf27_lowmem_hiliq_x2_20261025_115003/sampler_30s.txt` sha `34a6151a684b134dca91a5cd13bda49d8834da53dd0d436aa5d40ba2794ee9f9`（几乎未采到峰；**以日志 rss=1877MB 为准**） |

### 日志全文（仅此）

```
[leaf27_lowmem_v1/HILIQ/x2] begin rss=100MB
  members_loaded days=644 rss=1877MB
  capadv_days=644 rss=1877MB
  mktcap_days=644 rss=1877MB
```

## 强制披露（Arch 条件）

| 披露项 | 实填 |
|---|---|
| **峰 RSS** | 日志自报 **1877MB**（members/capadv/mktcap 加载后）；≫ rss_limit **1500** → **YES 破帽 → ABORT** |
| float32 存储 | 脚本钉含 mktcap/capadv（及 LimitPanel）float32 数组存；**本跑未达可观测披露点**——加载 members/capadv/mktcap 即破帽中止，**无**数值边际差可报 |
| **`_prune_hist`** | **未执行到**（破帽发生在日循环/`_prune_hist` 之前） |
| 无 α 选参 | 确认未改 α/β/W/门控；本跑无产物可改 |

## 产物

| 产物 | 状态 |
|---|---|
| alpha parquet | **无** |
| run_meta / build_summary | **无** |
| out_dir | `output/ai_factory/leaf27_on_minus_id_idio_ivol_lowmem_x2/`（仅 `_logs`/STOP/LAUNCH 痕迹；无研究产出） |

## 同窗旁注（主 park 戳；非本回执主钉）

- 主 `MAIN_ABORT_PARK`@11:50:30 ET 记：run1 pid=`719646` ET_TS≈`20261025_114923` 日志峰 **1933MB** 亦 ABORT；run2=`720992` 峰 **1877MB**（主标 unauthorized second / 同 `.ok`）。
- AI 本回执以用户核盘主钉 **115003 / 1877MB** 为结论依据；两跑均破帽，结论不变。

## QUIET / 锁（重要）

| 项 | 实填 |
|---|---|
| AI 侧 QUIET | 已 lift → `output/loop/_lifted/RESEARCH_QUIET_leaf27_lowmem_x2_ABORT_LIFTED_20261025_1150ET.lock` |
| 现盘 `output/loop/RESEARCH_QUIET.lock` | 内容 `arch_quiet_main_blockfix 2026-10-25T11:50:40-04:00` — **Arch/主挂的，非本跑锁** |
| AI 处置 | **勿擅 lift** 现盘锁；回执时未触碰该锁 |


> 回执落盘后核验（11:52 ET）：现盘 `RESEARCH_QUIET.lock` 路径已不在（见 `_lifted/RESEARCH_QUIET.lock.lifted_main_leaf27_abort_20261025_1150`）；**非 AI 所动**；AI 全程未 rm/mv 该锁。
## `.ok` 处置

- 单次使用意图：**已消费**（破帽 ABORT）
- 现盘：主 park → Arch/主 **正式 VOID** `_consumed/…8bcd79dc.VOID.ABORT_RSS.20261025T1152ET.ok`（TEAM_STATE Current 11:52:36 ET）
- AI：**不自重试**；**不申抬帽**；**不申新 `.ok`**（未新签前禁重开）；**禁** `--window both` / sealed / FULLA；**禁复用** VOID `725be3e0` 与本 `8bcd79dc`

## 建议（下一迭代 · 仍禁抬帽）

- 进一步降载：**分块加载** members / mktcap / capadv（避免一次装入 644 日把 RSS 打到 ≈1.8–1.9Gi）
- 目标仍钉 rss_limit=**1500**；破帽即 ABORT
- FULLA 仍 GAP；sealed 另窗另签

## 请 Arch / 主

1. Arch：核回执；裁定本 `.ok` 正式 VOID/归档；是否接受「分块加载」DIFF 再审
2. 主：是否排下一降载迭代窗；**勿**令抬帽
3. Data：无 CONT（本跑无产物）

live=false。
