# 合成小样自检说明（/tmp only）

- 时刻：2026-10-25 ≈12:38 ET（America/New_York）
- 目的：证明 P0 双开闭合逻辑；**未**读生产大表做 execute；**未**签 `.ok`
- 输入：`/tmp/sw_l1_pit_v2_fix_synth/{bad,bak,clean}.parquet`（迷你；`--skip-input-sha`）
- 命令：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  docs/v2/audit/sw_l1_pit_v2_fix_20261025/sw_l1_pit_v2_fix.py \
  --mode p0 --dry-run \
  --out-dir /tmp/sw_l1_pit_v2_fix_dry_p0 \
  --bad /tmp/sw_l1_pit_v2_fix_synth/bad.parquet \
  --bak /tmp/sw_l1_pit_v2_fix_synth/bak.parquet \
  --clean /tmp/sw_l1_pit_v2_fix_synth/clean.parquet \
  --skip-input-sha
```

- 结果：**PASS**
  - Case A（closed 优先）：`sz.002420` 丢陈旧 open `801110`，保留 `801230` open
  - Case B（无 closed 双开）：`sz.999001` 保留较新 `in_date` 的 `801020`
  - 每码 open≤1；`conflicts_p0.csv` 2 行；`P0_OK.txt` 已落
- 修 PIT ≠ 解阻叶25
