# Arch 复核：AI 的 N8 修复（leaf_selfcheck_v3）

- 写于 2026-10-18 01:01 ET（Arch，按 `date` 实测）。只读复核，没有运行 leaf_selfcheck_v3，也没算任何收益。
- 复核对象：
  - `output/ai_factory/leaf_selfcheck_v3_N8.diff`（mtime 00:41）
  - `output/ai_factory/leaf_selfcheck_v3_N8_smoke.log`（mtime 00:42）
  - 当前 `research/leaf_selfcheck_v3.py`（sha256 c28eab58a119…e756，mtime 00:41）
- 一致性：把 diff 反向应用到当前文件，能干净还原出改前版本（还原后含 4 处 MIDLARGE），说明 diff 与现行文件一致。

## 结论：PASS，附 2 条 P3 建议，不阻塞

| 检查项 | 结果 | 证据 |
|---|---|---|
| top300 分支已删除 | ✓ | `factor_report` 里 `MIDLARGE_TOP300_LEGACY` 和 `select_mid_large_topn_light(top_n=300)` 两个分支都已删除；全文件不再出现 top300、TOP300、mid_large 代码路径（只剩 L86 的说明注释）。输出后缀一律为 `_pool-{universe}`（L177） |
| UNIVERSES 只剩两个 | ✓ | L87：`UNIVERSES = ("HI_LIQ_V1.1", "FULLA_V1")`，默认 HI_LIQ_V1.1 |
| HAC lag = max(h−1, 1) | ✓ | L96：`lag = max(h - 1, 1)`，删掉了原来 `int(4(n/100)^(2/9))` 的下限，与 Alpha 的 `alpha_combo_marginal.ic_tstats` 一致。smoke 日志显示 lag 为 1/4/9/19/59，对应 h = 1/5/10/20/60 |
| 新增字段 ic_t_naive、ic_hac_lag | ✓ | L138：`ic_t_naive = mean/std·√n`，`ic_hac_lag = max(h−1,1)`。原有的 ic_t（n_eff = n/h）和 ic_t_hac 都保留。smoke 日志三种 t 并列打印 |
| 旧池参数会报错 | ✓（带条件） | L116 `assert universe in UNIVERSES`。smoke 日志末行「legacy pool rejected: MIDLARGE_TOP300_LEGACY」，EXIT 0，峰值 RSS 723MB（≤1.5GB） |
| 两份文档的时间戳改为 00:13 | ✓ | `AI_EQINC_SEC8_RECONCILE_ZH.md` 第 2 行改为 00:13 ET（原写 00:25）；`AI_HILIQ_V1_SEC8_SUPPLEMENT_ZH.md` 第 1 行改为 00:13 ET（原写 00:30）。**独立旁证**：Arch 活动表 `docs/v2/audit/arch_activity_since_20261015.csv` 第 1664–1665 行记录的首次落盘时间分别是 00:13:14 和 00:13:38，与更正值一致。两份文件现在的 mtime 是 00:42:32 和 00:42:39，这是更正时的修改时间 |

## P3 建议（交 AI，不阻塞）

1. **P3-1：assert 在 `python -O` 下会失效，而且检查位置太晚。**
   - L116 的 assert 在 `python -O` 下会被跳过。即便如此，`_pool_panel` 的 `{...}[universe]` 字典查找（L103）仍会抛 KeyError，所以 -O 下旧池也**跑不出结果**。
   - 但这样报错信息不明确，而且报错发生在 `run()` 已经跑完 `LC.evaluate` 和 `marginal` 之后（L172-173），白耗算力。
   - 建议：在 `__main__` 解析参数后、以及 `run()` 入口处，改为显式 `if universe not in UNIVERSES: raise SystemExit(...)`。这与 Arch 对 Strategy runner 的 P2-2 是同一要求。
2. **P3-2：输出字段 `pool` 名不副实。**
   - L125 的 `"pool": len(cols)` 记的是列数，即掩码的全部代码加上持仓代码，所以 HI_LIQ 和 FULLA 都是 5258。它不是池子的实际成员数，容易误读。
   - 建议改名为 `n_cols`，另报日均池成员数。

## 附带发现（不属 N8，转入引擎规格）

- `_pool_panel`（L101-113）的价格指数用 cs_panel 的 ret 累乘得到。而 cs_panel **系统性缺复牌首日这一行**：X2 内 702 次复牌中有 701 次缺失（见 `docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md` §1.4 D-1）。
- 后果：前瞻收益会丢掉复牌跳空。IC 受影响的程度，等 cs_panel_v2 重建后按该规格 §4 的规则重算。
- 这不是 N8 引入的问题，不影响本次 PASS。
