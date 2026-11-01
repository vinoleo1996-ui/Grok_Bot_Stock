# Arch 叶27 mktcap 尖峰缓解方案草案（只提案 · 不签不跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器） |
| written_et | `2026-10-25T17:11:40-04:00`（America/New_York；墙钟 2026-10-25 17:11 ET） |
| 性质 | **DRAFT ONLY** · **非 `.ok`** · **不签** · **不代跑** · **不改主干** · live=false · ≠X2 |
| 主令 | TEAM 17:07 ET — hist-prune VOID 齐；出 mktcap 尖峰方案草案（主闸后再报 Leo） |
| 触发 | hist-prune ABORT_RSS 峰 **1518MB**@`chunk6_mktcap` / lim **1500**（禁抬帽） |
| AI 回执 | `d8be85cb` · VOID 权威 `fd159322` · 脚本 `8cb3e86f` · ET_TS=`20261025_165654` |
| AI 尖峰笔记 | `docs/v2/audit/AI_LEAF27_CHUNKED_HIST_PRUNE_CHUNK56_SPIKE_NOTE_20261025_ZH.md` sha8 **`dd193511`** |
| 对照 ndays40 | 1514@chunk6（无 hist_prune）→ 本跳 1518@chunk6（prune **未压尖峰**） |

## 0. 一句话

hist_prune_r1 **已执行**但日志 freed Δ=0；破帽仍落在 **`load_mktcap_chunk` 瞬时 +33MB** 叠在 **跨块基线≈1485** 上。根因对齐 AI 笔记 `dd193511` 四标签。本草案给主闸 **≤3 主候选**（A/B/C；D/E 附录；**全票不抬帽**）；**RECOMMENDED=A**（mktcap 免全表重扫）；Arch **不自签** `.ok`、不代跑、不抬帽、不解阻 X2。

## 1. 盘证钉（MATCH）

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `d8be85cb` | MATCH |
| Arch VOID 回执 | `fd159322` | MATCH |
| VOID `.ok` | `2be59acd` → `_consumed/…VOID.ABORT_RSS…` | 禁 RESTORED |
| 脚本 | `8cb3e86f`（hist_prune_r1；禁 `262f9bf6`） | MATCH |
| AI 尖峰笔记 | `dd193511` | MATCH |
| rss_limit | **1500**（禁抬） | 硬钉 |
| QUIET | 已 lift（`b0c85e42`）；8795 quiet=false | MATCH |
| live `.ok` | 0 | MATCH |
| forbid RESTORED 六票 | `2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0` | 禁复用 |

### 1.1 破帽路径（hist-prune 日志准）

```
chunk[5] mktcap=1485 → hist_pruned+freed=1485 (Δ0; ret_hist_n=3875 eps_hist_n=3124)
chunk[6] members=1485 / capadv=1485
ABORT stage=chunk6_mktcap rss=1518 limit=1500   # +33
```

sampler_30s：peak_kb=`1392852`≈1360MB；中段 VmRSS 曾降到 **865MB**（`16:58:26`），证明 **当前 RSS 可回落**，与日志「freed 不降」口径不一致（见 §2.1）。

## 2. 根因假设（须有盘证 · 对齐 `dd193511`）

### 2.1 `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE`

| 证据 | 说明 |
|---|---|
| 日志 chunk0..5 凡 `hist_pruned+freed` 皆与前一 stage **同值（Δ=0）** | AI 笔记 §B；回执 `d8be85cb` 摘要同 |
| `rss_mb()` = `resource.getrusage(...).ru_maxrss/1024`（`g1g5_…lowmem_v1.py:106-107`） | **生涯高峰 HWM**，永不下降 → 日志「freed」无法反映归还 |
| sampler VmRSS 865MB ≪ 日志 HWM 1485/1518 | 当前 RSS 有余量；软门却按 HWM 计量 |

**推论**：块末 `clear+del+gc` 即使归还页，**日志峰与软门仍锁在 HWM**；基线在计量上「贴帽」，下一块只剩 ~15MB HWM 余量。

### 2.2 `MKTCAP_FULLSCAN_TRANSIENT_SPIKE`（破帽点）

| 证据 | 说明 |
|---|---|
| ABORT stage **恰为** `chunk6_mktcap`（+33MB） | 装载瞬时，非日循环中段 |
| `load_mktcap_by_session`：对 **全部** RG `read_row_group→to_pandas` 再 `isin(want)` | 脚本/lowmem helper；每 chunk 重扫 |
| 盘证 parquet：177MB · **12 RG** · **11.7M 行**；各 RG `trade_date` stats 均为 **2015-01-05..2026-10-09** | **RG 日期 prune 无效**（与 members 可 prune 不同） |
| 每 chunk `dates_needed≈41` 日却全表扫描 | 17 chunk × 12 RG 重复物化 |

### 2.3 `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD`

| 对象 | 盘证 |
|---|---|
| `ret_hist`/`eps_hist` | prune 后仍 3875/3124 键（因子窗不可砍） |
| `LimitPanelCache` | 块末未清；`keep_sessions=全 cal` |
| `a_date/a_inst/…` | α 行跨块增长；块末未清 |
| `mkt_hist`/`swm`/`r_mkt` | 进程级常驻 |

### 2.4 `HIST_PRUNE_R1_NO_PEAK_RELIEF`

对照 ndays40（无 prune）1514@chunk6 → hist_prune 1518@chunk6；**同阶段、同量级、略高**。Arch 审 `6543726a` 已预告「不保证单块 mktcap 尖峰消失」——实峰证实。

## 3. 候选票（3–5；主闸；Arch 不自签）

硬约束（全票共用）：**rss=1500 禁抬**；禁复用六票；禁 silent fallback；禁自开跑；禁解阻 X2；另审另签；peak_proof REQUIRED。

### A · **RECOMMENDED** · mktcap 免全表重扫（跨块缓存 / 仅补缺失日 + batch 过滤）

| 项 | 内容 |
|---|---|
| 机制 | 进程内保留 `DayFloatMap` 跨 chunk；每块只加载 **缺失** `trade_date`；读取改 pyarrow batch/`filters`（避免整 RG→大 pandas）；块内继续 `drop_before`；**不改**因子钉 / CLI ndays40 |
| 改动面 | 优先仅 `research/leaf27_chunked_members_mktcap_r1.py`（或薄封装）；**不**改 lowmem 因子路径；**不**抬帽 |
| 对准标签 | `MKTCAP_FULLSCAN_TRANSIENT_SPIKE`（主）+ 降低重复分配对 HWM 的推高 |
| 预估 RSS | 去掉每块 12×RG 重扫瞬时；目标把 chunk6 级 +33MB HWM 尖峰压到帽下；**预估峰值带 1400–1490**（须实峰证明；非保证） |
| 取舍 | 工程量中；须新脚本 sha + 独立 COVER/CMD/DIFF；RG 无日期分区故「跳 RG」不可用，必须改读取策略 |
| 风险 | 缓存持有过宽→基线升；filters 仍可能扫底表；因子/T-1 语义回归 |
| 抬帽 | **否** |

### B · 软门改读 `/proc/self/status` VmRSS（当前）+ 日志双报 HWM

| 项 | 内容 |
|---|---|
| 机制 | `_check_rss` 用 **当前 VmRSS**；另打印 `ru_maxrss` 作 peak_hwm；块末 freed 才可见降 |
| 对准 | `BASELINE_NO_RSS_DROP`（计量层） |
| 预估 | sampler 曾现 865MB 当前值 → 理论头寸大；**但**若政策仍要压 HWM，单改计量≠降真实尖峰 |
| 取舍 | 改动小；属 **计量/门控政策**，须主明文批准 |
| 风险 | 被视作「放宽门」；短暂尖峰可能冲 cgroup；与既有 peak_proof 口径要重钉 |
| 抬帽 | **否**（限值仍 1500；改的是测什么） |

### C · 更细切 ndays=20（mode 票 · 非代码修复）

| 项 | 内容 |
|---|---|
| 机制 | CLI `--chunk-ndays 20`；脚本字节可 UNCHANGED |
| 对准 | 降低单块 members/capadv 并发；**不**消除 mktcap 全表扫描 |
| 预估 | 早期块或降；chunk 中后段 HWM 仍可能贴帽（月/季/40 史） |
| 风险 | 又一轮 mode 票；历史四跳 ABORT 提示切细不够 |
| 抬帽 | **否** |

### D · 跨块基线疏散（lim_cache 旧会话驱逐 + α 中段落盘）

| 项 | 内容 |
|---|---|
| 机制 | 块末/每 N 日：驱逐 `LimitPanelCache` 中早于窗口的 panel；`a_*` 定期 flush parquet 再清空列表；保留 hist 因子语义 |
| 对准 | `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD` |
| 预估 | 基线 −50–150MB 量级（估）；**不单独保证** mktcap +33 尖峰消失 |
| 风险 | 限价面板重复读 IO；α 拼接一致性 |
| 抬帽 | **否** |

### E · 组合包（A+D，可选加 B 作观测）

| 项 | 内容 |
|---|---|
| 机制 | 先 A（破帽点）+ D（基线）；B 仅作双轨日志/门控（若主批） |
| 预估 | 最可能一次过帽；包体更大、审更重 |
| 风险 | 归因困难；一轮票塞过多 |
| 抬帽 | **否** |

## 4. 禁项（本草案 + 任一下一票）

- **禁抬** `rss_limit=1500`
- **禁复用/RESTORED** 六票：`2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- **禁** silent fallback / 静默换 mode / 静默改 ndays
- **禁** Arch/AI 自开跑、自申 `.ok`、自排签窗
- **禁** 解阻 X2 / 把本草案当 X2 或开跑授权
- **禁** 改因子钉（β60/W20/残差序/HI_LIQ/α 方向）借「省内存」偷改
- 本文件 **≠** `.ok`；**不**改 `research/` 主干字节（本回合）

## 5. 推荐默认（主闸）

**RECOMMENDED = A**（mktcap 免全表重扫 / 跨块按需补日）。

理由（一句话）：破帽 stage 钉死在 `chunk6_mktcap`，且盘证 mktcap parquet **RG 日期不可 prune** + 每块全表重扫——只有改装载策略才能对准 `MKTCAP_FULLSCAN_TRANSIENT_SPIKE`；hist_prune 已证 `HIST_PRUNE_R1_NO_PEAK_RELIEF`。

主可改批 B/C/D/E；Arch **不自签**。


## 5.1 主令对齐（≤3 票 + 放宽帽）

主正式令要求 **≤3 候选工程票**。本草案闸口默认只呈 **A / B / C**（D/E 为附录备选，非本闸必选）：

| 序 | 票 | 一句话 |
|---|---|---|
| 1 | **A（RECOMMENDED）** | mktcap 免全表重扫；估峰 1400–1490（须实峰） |
| 2 | B | 软门改 VmRSS 计量（政策票；限值仍 1500） |
| 3 | C | ndays=20 更细切（mode；不消除全表扫） |

**放宽帽**：A 若按估可靠压到 ≤1500，**本回合不申请放宽**。若主批 A（或 B/C）后实峰仍破帽且无其他不抬帽路径，须 **明文请示 Leo 是否放宽帽**——Arch/主/AI **均勿自决放宽**。

## 6. 验收 / 另审另签流程

1. 主批默认票（或改批）→ AI 出 COVER/CMD/DIFF/HAND（若代码变更）→ **Arch 只审不签** → 主排签窗 → Arch 新签 `.ok`（新 sha；禁 RESTORED）+ 挂 QUIET → 主令 AI prelaunch **单次**。
2. **peak_proof REQUIRED**：日志 `rss=` 阶梯 + sampler_30s +（若批 B）VmRSS/HWM 双报；破帽 → **停** + 回执；**禁抬帽**；禁自重跑。
3. 对照键：是否仍 ABORT@`*_mktcap`；chunk 末 freed 是否仍 Δ0（若仍用 HWM）；`ret_hist_n`/`eps_hist_n`；脚本新 sha。
4. ≠X2；live=false 直至主另令。

## 7. 非动作（本回合）

- 未新签 `.ok`；未代跑；未改 `research/leaf27_chunked_members_mktcap_r1.py`；未抬帽；未挂/未动 QUIET；未申 X2。
- 下一跳：**等主闸** RECOMMENDED 或改批。

live=false · promotion_approved=false · ≠X2
