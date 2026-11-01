# 侧稿 DIFF 笔记（相对生产；未应用）

- 生产脚本 **未改**（`research/strategy_moneyflow_stack_diag_v1.py` 仍 `2dae9a91…`）
- 侧稿：`strategy_moneyflow_stack_diag_v1_SIDE.py.draft` — 仅示意 `reuse_blended_or_none` / `load_weights_lean` / `release_mix_frames`
- 引擎窗口化：**仅** `SIDE_engine_windowed_merged_panel_NOTES_ZH.md`，无 py 补丁
- `py_compile`：对 draft 执行语法检查（见下）；**不**要 Arch `.ok`
- await Arch code_change 后由主路径合入；live=false；禁抬帽

## py_compile（本轮）

- `python3 -m py_compile strategy_moneyflow_stack_diag_v1_SIDE.py.draft` → **OK**
- 无市场数据自检：`SIDE draft selftest OK`
- 生产 `research/*.py` 未动；无需 Arch `.ok`
