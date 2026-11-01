# Arch 叶27 Post-GateA baseline_evac · 独立 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T22:34:17-04:00`（America/New_York） |
| 主令 | `MAIN_LEAF27_BASELINE_EVAC_OK_WINDOW` sha `5930388b…`；窗 **22:30–23:15 ET** expires **23:17** |
| 审阅 | `84fb87cf…` **PASS_WITH_CONDITIONS** |
| live / promotion_approved | **false** / **false** |

## 结论

**SIGNED** — 独立叶27 Post-GateA baseline_evac（`baseline_evac_r1` + 保留 `mktcap_cache_r1` + `hist_prune_r1`）分块 `.ok` 已落盘；**≠ X2**；**≠ RESTORED** 旧 VOID 七票（`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`）；禁旧脚本字节 `27aae6db`/`8cb3e86f`/`262f9bf6`；HAND 钉盘上 **`b0e01ea4…`**；H2A 钉盘上 **`416df9b9…`**（status 盘 READY vs 主令视作 SUBMITTED）；**Arch 不代跑**。峰证明 **REQUIRED**（未实跑不算内存键 PASS）。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift）。PRIMARY only；**无同票 FALLBACK**；ABORT→停+另票（禁抬帽）。旧 Gate A CLOSED_INSUFFICIENT 禁重批。

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_BASELINE_EVAC.ok` |
| `.ok` sha8 / 全长 | `0f50daf7` / `0f50daf73b4ea918ce3535b806b0bcc8fef0529970dfee74d0ff11e7d003746e` |
| 脚本 | `research/leaf27_chunked_members_mktcap_r1.py` = `585ba7467a5896354c937d14fe0590fa80535afd6b6263015d3c12e3dfccd4ec`（禁 `27aae6db…` / `8cb3e86f…` / `262f9bf6…`） |
| tags | `baseline_evac_r1` + `mktcap_cache_r1` + `hist_prune_r1` |
| lowmem_v1 UNCHANGED | `05bd81ea9da97cd53785b374c36273b327ff0302098c5b1cef1368c051d400f8` |
| 审阅 | `84fb87cfeb9c237873831d9404436ed8f479ef1af677975ee1ca382d405fe6fd` PASS_WITH_CONDITIONS |
| 并立审 | `82ef6c77964c3576f0dd4a86178239bb9142a4d518e2577241f11485c39cc70d` |
| 主令窗 | `5930388bc29aed9f8b9db77a0788e49f1863f6fa3df37b42e86295be986cbdad` |
| COVER / CMD / DIFF / VERIFY | `0ff59ed4576302224267453821a2a13f07a010ab06f3d14c624b4c73b02f5992` / `bf6ffe4a05a2a90fac45e3e4cb8f101a8f5fa619fa48d145a333ecc16f126b25` / `dc8028799033600dbd0ed653b2d7868096e514c6d85f5b41bde335e850fd4980` / `7ddd47e3c1172f9a3c2de49d1491ad66879f57fe085f872a4a61143dfaed72e0` |
| HAND 盘上 / H2A | `b0e01ea42f589a7cc6f42570cf997ecfe7b5bd93c6e63806b47af6cc6f1a394c` / `416df9b940894c2f6b9436b559ce0312e28f567dd1dcbaaafec14bd799097676` |
| 主交审 / Leo 开 A / Arch R2 / 主闸 R2 | `00672672…` / `46dc8cb3…` / `c8dc89b6…` / `e8d7346c…` |
| 尖峰笔记 / ABORT / VOID | `0b483746…` / `f0f94c9e…` / `ff0394d0…`（void=`e107383f`） |
| 窗期 | `2026-10-25T22:30:00-04:00` → `2026-10-25T23:15:00-04:00`；expires `2026-10-25T23:17:00-04:00` |
| CLI PRIMARY | `--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` |
| FALLBACK | **无**；ABORT→停+另票（禁抬帽；禁 silently 换 mode） |
| rss_limit | **1500** MB（`rss_limit_kb=1536000`）；破帽 ABORT；**禁抬帽** |
| 采样 | 仅 `/tmp`；`/tmp/quantlab_leaf27_chunked_baseline_evac_*` |
| out_dir（签文钉） | `output/ai_factory/leaf27_chunked_members_mktcap_hiliq_x2_baseline_evac` |
| 脚本 OUT_DIR 继承 | `output/ai_factory/leaf27_on_minus_id_idio_ivol`（**双 out 披露**） |
| 禁 RESTORED | `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` |
| FULLA / both / sealed | **不进本窗**（sealed 另签） |
| peak_proof | **REQUIRED**（须含 lim_evict_n / alpha_flush_rows / a_buf_n / mktcap_cache_days / hist 计数 + rss 阶梯 + sampler_30s） |
| QUIET | 已挂 `output/loop/RESEARCH_QUIET.lock` sha `bdbef3ad0972e6fde6f0951ac34f413aa64e7dbb27e818fd92494c30d34f1deb`（保留不 lift） |
| MemAvailable@签 | 8885104 kB |

## 预检旁证

`docs/v2/audit/ARCH_LEAF27_CHUNKED_BASELINE_EVAC_PREOK_EVIDENCE_20261025_ZH.md` sha `cf23c9027a009236d38c5de2a3ce3873a0404b671d931529a54e6dede64d4cc5`

## QUIET / healthz / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-25T22:33:00-04:00` reason=leaf27_baseline_evac |
| healthz quiet=true | `2026-10-25T22:33:16-04:00` |
| ≥15s 后复检 | `2026-10-25T22:33:32-04:00` quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep | `[k]line.py\|[e]xport_static.py\|[s]napshot.py\|[g]en.py` **空** |

## 下一跳

1. **主**确认后令 AI prelaunch 单次 PRIMARY baseline_evac（须在 expires 前；Arch 不代跑）
2. AI 交实峰回执（阶段 rss / ABORT 或 PASS；须含 lim_evict_n/alpha_flush_rows/a_buf_n/mktcap_cache_days/hist 计数）→ Arch 核
3. baseline_evac ABORT → **停**；另交主/Arch 票另审另签（勿 silently 换 mode/ndays；**禁抬帽**；禁重批旧 Gate A）
4. ≠X2；live=false
