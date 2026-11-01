# Arch 叶27 mktcap 尖峰缓解方案草案 R2（Gate A 后 · 只提案 · 不签不跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器） |
| written_et | `2026-10-25T20:49:00-04:00`（America/New_York；墙钟 2026-10-25 20:49 ET） |
| 性质 | **DRAFT ONLY** · **非 `.ok`** · **不签** · **不代跑** · **不改主干** · live=false · ≠X2 |
| 主令 | TEAM FYI — 并入 AI Gate A 后短笔记 `0b483746`；对照原草案 `a2307c8b` 后落盘；仍 ≤3 候选、禁抬帽、RECOMMENDED 一票 |
| 触发 | Gate A mktcap_cache ABORT_RSS 峰 **1507MB**@`chunk6_mktcap` / lim **1500**（禁抬帽） |
| 原草案（冻结） | `docs/v2/audit/ARCH_LEAF27_MKTCAP_SPIKE_MITIGATION_DRAFT_20261025_ZH.md` sha8 **`a2307c8b`**（RECOMMENDED 旧 A = 免全表重扫 → 已开闸实跑） |
| AI Gate A 短笔记 | `docs/v2/audit/AI_LEAF27_CHUNKED_MKTCAP_CACHE_ABORT_SPIKE_NOTE_20261025_ZH.md` sha8 **`0b483746`** |
| AI 回执 | `f0f94c9e` · VOID Arch `ff0394d0` · VOID `.ok` **`e107383f`** · 脚本 **`27aae6db`** · ET_TS=`20261025_204028` |
| prev 尖峰笔记 | `dd193511`（hist-prune；对照峰 1518） |
| 峰对照 | ndays40 **1514** → hist-prune **1518** → Gate A **1507**（同 stage=`chunk6_mktcap`；Gate A 仅降 ~11MB，**不够过帽**） |

## 0. 一句话

原草案 `a2307c8b` 的 **RECOMMENDED=A（免全表重扫）已落地为 Gate A** 并实跑：全表 RG 扫尖峰从 +33MB 收到 +10MB，但块末 `drop_before` 把跨块 store 压到 `cache_days=2` → 每块仍 **miss≈40 物化**；叠在 **HWM 不回落** 基线 chunk5=**1497**/1500（余量仅 **3MB**）上，chunk6 **+10** 即破帽（1507）。对齐 AI 笔记 `0b483746` 五标签。本 R2 给主闸 **≤3 主候选**（全票**不抬帽**）；**RECOMMENDED=A（跨块基线疏散）**；旧 A 标 **CLOSED_INSUFFICIENT**（非本闸候选）；Arch **不自签** `.ok`、不代跑、不抬帽、不解阻 X2。

## 1. 盘证钉（MATCH）

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT（Gate A） | `f0f94c9e` | MATCH |
| Arch VOID 回执 | `ff0394d0` | MATCH |
| VOID `.ok` | `e107383f` → `_consumed/…VOID.ABORT_RSS…` | 禁 RESTORED |
| 脚本 | `27aae6db`（mktcap_cache_r1 + hist_prune_r1；禁 `8cb3e86f`/`262f9bf6`） | MATCH |
| AI Gate A 短笔记 | `0b483746` | MATCH |
| 原缓解草案 | `a2307c8b`（冻结；本 R2 对照用，**不覆写**） | MATCH |
| prev 尖峰笔记 | `dd193511` | MATCH |
| rss_limit | **1500**（禁抬） | 硬钉 |
| QUIET | 已 lift（`1d423cc6`）；quiet=false | MATCH |
| live `.ok` | 0 | MATCH |
| forbid RESTORED **七**票 | `e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0` | 禁复用 |

### 1.1 破帽路径（Gate A 日志准 · 摘 `0b483746`/`f0f94c9e`）

```
chunk[5] mktcap=1497 → hist_pruned+freed=1497 (Δ0; cache_days=2; hit=1 miss=40)
chunk[6] members=1497 / capadv=1497
ABORT stage=chunk6_mktcap rss=1507 limit=1500   # +10
```

sampler_30s：peak_kb=`898968`≈878MB（EXIT；未先杀进程）≪ 日志 HWM 1507 → 计量层仍是 **生涯高峰**（续 `a2307c8b` §2.1）。

### 1.2 对照原 `a2307c8b` 预测 vs Gate A 实测

| `a2307c8b` 主张 | Gate A 实测（`0b483746`） | 判定 |
|---|---|---|
| 免 12×RG 全表重扫可压 +33MB 尖峰 | 尖峰幅度 **+33→+10**；峰 **1518→1507** | **部分兑现**（装载路径已换） |
| 估峰带 1400–1490 | 实峰 **1507** 仍破 1500 | **估失败 / 过帽不足** |
| 风险「filters 仍可能扫底表」 | miss-only filters **仍每块物化 ~40 日**（`MISS40_FILTER_STILL_MATERIALIZES`） | **风险坐实** |
| 风险「缓存持有过宽→基线升」 | 块末 `drop_before` 反把 store 压到 **2 日** → hit≈1（`CACHE_HIT_BOUND_BY_DROP_BEFORE`）；基线升主因仍是 hist/lim/α + HWM | **机制与预想不同**：非「缓存过宽」，而是「命中被 T-1 drop 钉死」 |
| 附录 D 基线疏散 | chunk5 已 **1497**/1500，余量 **3MB** < 装载 **+10**（`CHUNK6_PLUS10_OVER_3MB_SLACK`） | **升格为主因候选** |

**CLOSED_INSUFFICIENT（非本闸候选）**：原 A「mktcap 免全表重扫 / mktcap_cache_r1」——路径生效、峰仅降 ~11MB、**不够过帽**；禁把本 R2 再批成「重跑同一 Gate A」。

## 2. 根因假设（须有盘证 · 对齐 `0b483746` + 续 `dd193511`）

### 2.1 `CACHE_HIT_BOUND_BY_DROP_BEFORE`（新 · 非 bug）

| 证据 | 说明 |
|---|---|
| 块末日志固定 `mktcap_cache_days=2` | Gate A **故意**跨块保留 store，但日循环 `drop_before`（T-1 语义不变）持续丢掉过期日 |
| 下一块 want≈40 日 ∩ 残留 2 日 → 通常 hit=1 | 冷启动后几乎每块 `hit=1 miss=40 load_n=40` |
| 「跨块缓存」避免的是全表 RG 扫描 | **不是**「40 日 miss 的 pandas 物化」 |

### 2.2 `MISS40_FILTER_STILL_MATERIALIZES`（新 · 破帽瞬时）

| 证据 | 说明 |
|---|---|
| ABORT stage 仍为 `chunk6_mktcap` | 装载瞬时，非日循环中段 |
| chunk6：`pq.read_table(filters=40日)→to_pandas→put_day×40` | +**10MB**（1497→1507） |
| 对照 hist-prune 全表扫 +33@chunk6 | Gate A 尖峰变小，但**起点更高/余量更窄** |

### 2.3 `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE`（续）

| 证据 | 说明 |
|---|---|
| chunk0..5 凡 `hist_pruned+freed` 皆 Δ=0 | 与 `dd193511`/`a2307c8b` §2.1 同构；Gate A 下更贴帽 |
| `rss_mb()` = `ru_maxrss/1024`（HWM） | 日志峰与软门永不下降 |
| sampler VmRSS peak≈878MB ≪ 1507 | 当前 RSS 有余量；软门按 HWM |

### 2.4 `GATE_A_PEAK_RELIEF_INSUFFICIENT` + `CHUNK6_PLUS10_OVER_3MB_SLACK`（新）

| 证据 | 说明 |
|---|---|
| 1518→1507（Δ≈−11）仍 ≫ 1500 | Gate A **未**过闸 |
| chunk5 末 1497 → 余量 3MB；chunk6 mktcap +10 | 算术上必然破帽，除非压基线或削装载峰或改计量 |

### 2.5 `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD`（续 · 基线主力）

`ret_hist`/`eps_hist`（prune 后仍数千键）、`lim_cache`、`mkt_hist`、`a_*` α 行列表跨块增长；另 mktcap store 按设计跨块保留（虽被 drop 到 2 日，持有量小）。

## 3. 候选票（≤3；主闸；Arch 不自签）

硬约束（全票共用）：**rss=1500 禁抬**；禁复用七票；禁 silent fallback；禁自开跑；禁解阻 X2；另审另签；peak_proof REQUIRED；**禁**再批「重跑 Gate A / 复用 `e107383f`/`27aae6db` 同语义票」充数。

### A · **RECOMMENDED** · 跨块基线疏散（lim_cache 旧会话驱逐 + α 中段落盘）

| 项 | 内容 |
|---|---|
| 机制 | 块末/每 N 日：驱逐 `LimitPanelCache` 中早于因子窗的 panel；`a_*` 定期 flush parquet 再清空列表；保留 `ret_hist`/`eps_hist` 因子语义与 T-1；**保留** Gate A miss-only filters（不回退全表扫）；**不改** CLI ndays40 |
| 改动面 | 优先仅 `research/leaf27_chunked_members_mktcap_r1.py`（或薄封装）；**不**改 lowmem 因子路径；**不**抬帽 |
| 对准标签 | `CHUNK6_PLUS10_OVER_3MB_SLACK`（主）+ `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE` + `CROSS_CHUNK_HIST_LIM_ALPHA_HOLD` |
| 预估 RSS | 新跑压低 HWM 爬升曲线，目标 chunk5 末余量 ≫10MB；估峰带 **1400–1490**（须实峰证明；非保证） |
| 取舍 | 工程量中；须新脚本 sha + 独立 COVER/CMD/DIFF；对「已锁死的 HWM」无回魔法——靠**新进程**全程少堆 |
| 风险 | 限价面板重复读 IO；α 拼接一致性；若疏散不足仍可能在 chunk6 +10 破帽 |
| 抬帽 | **否** |
| 对照原草案 | = `a2307c8b` 附录 **D** 升格；因 Gate A 证明破帽已从「全表扫」转为「基线余量不足」 |

### B · miss 装载削峰（按日/小批 filters→to_pandas，避免一次物化 ~40 日）

| 项 | 内容 |
|---|---|
| 机制 | 在 **保留** Gate A miss-only + `drop_before` T-1 前提下，将 `missing` 按日或小批（如 5 日）循环 `read_table(filters=…)→to_pandas→put_day`，降低单次分配尖峰；**不**为提高 hit 而放宽 `drop_before`（禁改 T-1） |
| 对准 | `MISS40_FILTER_STILL_MATERIALIZES` + `CACHE_HIT_BOUND_BY_DROP_BEFORE`（承认 hit≈1，改削峰） |
| 预估 | 把 chunk6 级 +10MB 压到数 MB 内；**若** chunk5 HWM 仍 1497，仍可能差 1–3MB 破帽 → 常须与 A 同跑或后继 |
| 取舍 | 改动面小于 A；单独票可能不够；与 A 叠加时归因变难（故本闸不把「A+B 包」列为第三票） |
| 风险 | pyarrow 批读仍触底表；IO 次数升；因子语义回归 |
| 抬帽 | **否** |
| 对照原草案 | 原 A 的**下一刀**（装载策略深化）；**≠** 重开 Gate A |

### C · 软门改读 `/proc/self/status` VmRSS（当前）+ 日志双报 HWM

| 项 | 内容 |
|---|---|
| 机制 | `_check_rss` 用 **当前 VmRSS**；另打印 `ru_maxrss` 作 peak_hwm；块末 freed 才可见降 |
| 对准 | `BASELINE_NO_RSS_DROP_AFTER_CHUNK_FREE`（计量层）；Gate A sampler 878MB ≪ 1507 强化「门控口径」议题 |
| 预估 | 理论头寸大；**但**单改计量 ≠ 降真实尖峰；若政策仍要压 HWM，本票不够 |
| 取舍 | 改动小；属 **计量/门控政策**，须主**明文**批准 |
| 风险 | 被视作「放宽门」；短暂尖峰可能冲 cgroup；与既有 peak_proof 口径要重钉 |
| 抬帽 | **否**（限值仍 1500；改的是测什么） |
| 对照原草案 | = `a2307c8b` 候选 **B** 原样保留（证据更强） |

### 附录（非本闸必选 · 不占 ≤3 席）

| 标 | 说明 |
|---|---|
| 旧 A | 免全表重扫 / Gate A — **CLOSED_INSUFFICIENT**（1507 仍破；禁重批） |
| 旧 C | ndays=20 更细切 — 历史四跳 ABORT 提示切细不够；本闸不占席 |
| E | A+B 组合包 — 最可能一次过帽，但包体大、归因难；主若改批可另开 |

## 4. 禁项（本草案 + 任一下一票）

- **禁抬** `rss_limit=1500`
- **禁复用/RESTORED** 七票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- **禁** 把本 R2 批成「重跑 Gate A / 复用脚本 `27aae6db` 同语义」充下一票
- **禁** silent fallback / 静默换 mode / 静默改 ndays / 静默放宽 `drop_before`（T-1）
- **禁** Arch/AI 自开跑、自申 `.ok`、自排签窗
- **禁** 解阻 X2 / 把本草案当 X2 或开跑授权
- **禁** 改因子钉（β60/W20/残差序/HI_LIQ/α 方向）借「省内存」偷改
- 本文件 **≠** `.ok`；**不**改 `research/` 主干字节（本回合）；**不覆写** `a2307c8b`

## 5. 推荐默认（主闸）

**RECOMMENDED = A**（跨块基线疏散：lim_cache 驱逐 + α 中段落盘）。

理由（一句话）：Gate A 已证 `GATE_A_PEAK_RELIEF_INSUFFICIENT`——破帽算术现为 **余量 3MB vs 装载 +10MB**（`CHUNK6_PLUS10_OVER_3MB_SLACK`）；在禁抬帽且保留 T-1 `drop_before` 下，优先把 HWM 爬升曲线压出余量，比再磨 miss 命中率或改计量更对准盘证。

主可改批 B/C；Arch **不自签**。

## 5.1 主令对齐（≤3 票 + 放宽帽）

主正式令要求 **≤3 候选工程票** + **RECOMMENDED 一票**。本 R2 闸口只呈 **A / B / C**：

| 序 | 票 | 一句话 |
|---|---|---|
| 1 | **A（RECOMMENDED）** | 基线疏散（lim/α）；估峰 1400–1490（须实峰） |
| 2 | B | miss 按日/小批物化削峰（保留 Gate A filters + T-1） |
| 3 | C | 软门改 VmRSS 计量（政策票；限值仍 1500） |

**放宽帽**：A/B/C **本回合均不申请放宽**。若主批后实峰仍破帽且无其他不抬帽路径，须 **明文请示 Leo 是否放宽帽**——Arch/主/AI **均勿自决放宽**。

## 6. 验收 / 另审另签流程

1. 主批默认票（或改批）→ AI 出 COVER/CMD/DIFF/HAND（若代码变更）→ **Arch 只审不签** → 主排签窗 → Arch 新签 `.ok`（新 sha；禁 RESTORED）+ 挂 QUIET → 主令 AI prelaunch **单次**。
2. **peak_proof REQUIRED**：日志 `rss=` 阶梯 + sampler_30s +（若批 C）VmRSS/HWM 双报；破帽 → **停** + 回执；**禁抬帽**；禁自重跑。
3. 对照键：是否仍 ABORT@`*_mktcap`；chunk5 末余量是否 ≫10；`hit/miss/load_n`；`mktcap_cache_days`；`ret_hist_n`/`eps_hist_n`；脚本新 sha（≠`27aae6db` 同语义复跑）。
4. ≠X2；live=false 直至主另令。

## 7. 非动作（本回合）

- 未新签 `.ok`；未代跑；未改 `research/leaf27_chunked_members_mktcap_r1.py`；未抬帽；未挂/未动 QUIET；未申 X2；未覆写 `a2307c8b`。
- 下一跳：**等主闸** RECOMMENDED 或改批。

live=false · promotion_approved=false · ≠X2
