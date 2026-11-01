# 侧稿说明：diag 混合阶段降内存（不改生产）

- 目标文件（将来 Arch code_change 后由 Strategy/Eng 落地）：`research/strategy_moneyflow_stack_diag_v1.py`
- 本目录仅：`strategy_moneyflow_stack_diag_v1_SIDE.py.draft`（示意片段）
- **禁**覆盖 `research/*.py`；**禁抬帽**；**不跑**
- await Arch code_change

## DIFF 意图（相对 `2dae9a91…`）

1. **优先**：若 `.ok` / CLI 提供 `reuse_blended_path` + `expected_blended_sha256` MATCH → `os.link` 或 `shutil.copy2` 到 out_dir，**跳过** `_load_weights(trunk/sat)` 与 `blend_weights`。
2. **否则重算**：`_load_weights` 改为  
   - `columns=` 仅 `session|date` / `instrument|instrument_id` / `weight|target_weight`；  
   - 若 pyarrow 可用：`filters=[(weight_col, ">", 0)]`；  
   - 或当 trunk 路径为 dense 全日历表时，改读同目录 `…_pos_weights.parquet`（须 Arch 钉 sha）。
3. 写出 smoke 权重后：`del trunk_w, sat_w, sat_stripped, blended; gc.collect()`，再 `run_book_smoke_serial`。
4. 不改门B/GATE_V3、不改 CMC、不恢复 C0。

## py_compile

对 `*.py.draft` 可本地 `python3 -m py_compile`（语法烟）；**不**申请 Arch `.ok`。
