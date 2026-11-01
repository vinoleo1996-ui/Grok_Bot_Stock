# Eng 接线：B4 集中化三腿 纸面轨 2（不下单）

- 冻结依据：docs/v2/STRATEGY_COMBO_CONCLUSION_20261013_ZH.md（PAPER_TRACK_2_CONFIRMED）。live=false，strategy_promotion=false，promotion_approved=false，handoff_live_mainbook=NO；密封窗不动；capacity_adv 纸面轨（output/strategy_paper_capacity_adv、capacity-adv-paper CLI）未改动。
- 权重（各档只用自己的文件，sha256 记录在 output/strategy_paper_b4/FROZEN_CONFIG.json，每次运行都会校验，变更即拒绝运行）：
  - 60万：output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w.parquet
  - 100万：output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w.parquet
- 口径与 capacity_adv 纸面轨一致：sleeves core=0/stock=1/alpha_event=0，ExecConfig.strategy_v1（book_smoke 默认），臂 BOOK/C0。

## 入口
```
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli b4-paper --mode all        # backfill + forward + monitor
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli b4-paper --mode backfill   # X2 历史回填
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli b4-paper --mode forward    # 前向（自 2026-11-02 起）
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli b4-paper --mode monitor    # 监控
```
代码：quantlab/portfolio/b4_paper.py；cli.py 只新增了 b4-paper 子命令。单进程，峰值 RSS 约 0.9GB。

## 输出
- 回填 NAV（X2）：output/strategy_paper_b4/backfill_x2/aum_600000_run/aum_600000/X2/BOOK/nav.csv、…/aum_1000000_run/aum_1000000/X2/BOOK/nav.csv（C0 在同目录 X2/C0/），另有 target_weights / actual_weights.parquet。
- 前向 NAV（2026-11 起，独立于回填）：output/strategy_paper_b4/forward/aum_{600000,1000000}_run/aum_*/FWD/BOOK/nav.csv。前向窗起点为 2026-11-02；当前权重只到 2026-10-09，所以状态为 WAITING。需要 AI 按冻结规则续出权重（同路径或经 Strategy 确认的新冻结文件）后才会生成。
- 监控：output/strategy_paper_b4/monitor.json，内容包括 CAGR/MDD/Sharpe、成本、fill_ratio、买不进占比、单名欠配（scripts_eng/conc_fill_diag.py）、6% 上限（目标与实际）、单边年化换手、相对 capacity_adv 主干与 C0 的对比、分段（年度及前后半）。
- 状态：output/strategy_paper_b4/STATUS.json（PAPER_TRACK_2_BACKFILL_READY_FORWARD_PENDING）。

## 换哈希闸门（rehash，Strategy 裁定 2026-10-13）
```
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli b4-paper --mode rehash --new-60w <新60w.parquet> --new-100w <新100w.parquet> [--dry-run] [--receipt <路径>]
```
- 检查 (a)：新文件中 ≤2026-10-09 的行与当前冻结文件逐行一致，session×instrument 集合相同，|Δw|≤1e-8。
- 检查 (b)：新增行（>2026-10-09）单名目标 ≤6%（容差 1e-6）、逐日 Σw=1（容差 1e-6）、无负权。
- 两项都通过才更新 FROZEN_CONFIG.json 的 path/sha256（旧值记入 rehash_history），并写 docs/v2/B4_PAPER_REHASH_<ET 时间>_ZH.md（新旧 sha256 与检查结果）。任一项失败：打印报告、退出码 1、配置不变。--dry-run 只做检查。
- 测试（2026-10-13 ET，测试文件放在 /tmp，事后已删除）：
  - 当前文件对自身 dry-run：通过，exit 0。
  - 对自身 apply：通过，exit 0，回执写到 /tmp，配置随后从备份恢复。
  - 历史行扰动 +1e-4：拒绝，exit 1（max_abs_diff=1e-4）。
  - 新增日单名 8.5%：拒绝，exit 1（sessions_over_cap=1）。
  - 合规扩展：通过，exit 0。
  - 测试结束后 FROZEN_CONFIG.json 与测试前逐字节一致。

## 分段展示（monitor.json）
- segment_finding：X2 前半段（至 2025-08-01）两档都跑输 C0 和主干。60万：vs C0 −3.65pp、vs 主干 −7.81pp；100万：vs C0 −3.46pp、vs 主干 −4.56pp。
- paper_segments：backfill_X2_H1、backfill_X2_H2、forward_from_2026-11-02 三段分别给出 CAGR/MDD/Sharpe 与相对 C0、主干的超额，不合并。前向段的主干对比在 capacity_adv 有前向 NAV 之前为 null。
