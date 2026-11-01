# 主 · 叶27 LOWMEM×x2 ABORT_RSS + 停第二跑

- 时刻：2026-10-25T11:50:30-04:00（America/New_York）
- `.ok` sha8=`8bcd79dc`（原 path `ARCH_RUN_AUTH_LEAF27_ON_MINUS_ID_IDIO_IVOL_HILIQ_LOWMEM_X2.ok`）
- 脚本 `05bd81ea` / rss_limit=1500 / HILIQ×x2 / live=false

## 事实

| 跑 | ET_TS | pid | 峰（log） | 结果 |
|---|---|---|---|---|
| 1 | 20261025_114923 | 719646 | **1933MB** | ABORT_RSS_OVER_LIMIT @11:49:53（members_loaded days=644） |
| 2 | 20261025_115003 | 720992 | **1877MB** | 未授权第二跑（同 `.ok`）；主 TERM @11:50:22 |

- 采样旁证：`/tmp/quantlab_leaf27_lowmem_hiliq_x2_20261025_114923/{ABORT.txt,sampler_30s.txt,sampler_summary.txt}`
- 结论：**LOWMEM v1 未把成员/市值装载峰压到 ≤1500**；抬帽仍禁；禁再消费 `8bcd79dc`。
- 处置：`.ok` 已 park → `_consumed/…8bcd79dc.ABORT_RSS.20261025T1150ET.ok`；`STOP_NO_RELAUNCH.txt` 已落 out_dir；Arch 须正式 VOID；AI 禁重跑。
- Eng A3 / Intel A4 吸收文档本回合另收（与叶27无关）。

