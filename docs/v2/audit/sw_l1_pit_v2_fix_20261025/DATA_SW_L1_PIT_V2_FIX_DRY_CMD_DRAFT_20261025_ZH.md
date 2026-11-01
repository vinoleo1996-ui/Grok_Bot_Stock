# 申万 L1 PIT v2 修复 —— dry-run 命令草案（2026-10-25）

- 角色：QuantLab Data；live=false
- **本回合不执行**下列命令中的生产 dry（合成自检已在 COVER §5）；待 Arch 静态审通过并签 `<ARCH_DRY_OK>` 后，于**周一双通两轮齐后**再申跑
- **禁**在无签时运行 `--execute`
- 修 PIT ≠ 解阻叶25 / X2

## 环境

```bash
export PYTHONDONTWRITEBYTECODE=1
cd /workspace/QuantLab
SCRIPT=docs/v2/audit/sw_l1_pit_v2_fix_20261025/sw_l1_pit_v2_fix.py
# 期望脚本 sha256：见 COVER 交付表（落盘后钉）
```

## P0 dry（out 仅 /tmp）

```bash
nice -n 10 python3 "$SCRIPT" \
  --mode p0 \
  --dry-run \
  --out-dir /tmp/sw_l1_pit_v2_fix_dry_p0_$(date +%Y%m%dT%H%M%S) \
  --bad data/v2/sw_pit/industry_members_sw_l1_pit.parquet \
  --bak data/v2/sw_pit/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet \
  --clean data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
# 可选：若 Arch dry .ok 要求挂票（字段 allow_dry=true / scope=sw_l1_pit_v2）：
#   --ok <ARCH_DRY_OK>
```

验收：`P0_OK.txt`；`conflicts_p0.csv`；每码 open≤1；BAD/BAK/CLEAN 启动 sha MATCH。

## P1 dry（接 P0 mid；out 仅 /tmp）

```bash
OUT=/tmp/sw_l1_pit_v2_fix_dry_p1_$(date +%Y%m%dT%H%M%S)
# 先 P0 写入 $OUT，或 --p0-mid 指向已审 P0 mid
nice -n 10 python3 "$SCRIPT" \
  --mode p1 \
  --dry-run \
  --out-dir "$OUT" \
  --p0-mid /tmp/sw_l1_pit_v2_fix_dry_p0_XXXX/sw_l1_pit_v2_p0_mid.parquet \
  --bad data/v2/sw_pit/industry_members_sw_l1_pit.parquet \
  --bak data/v2/sw_pit/industry_members_sw_l1_pit.bak_pre_fix_20261014.parquet \
  --clean data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet \
  --codes-235 docs/v2/audit/data_ro_audit_20261018/B_missing_codes_classified.csv
#   --ok <ARCH_DRY_OK>
```

验收：`P1_OK.txt`；235 均有 open；`normdiff_vs_clean_open_p1.txt` 差异可解释；禁 `--allow-shrink`。

## Execute（占位；**无签禁止运行**）

```bash
# STOP：无 Arch execute .ok（allow_run/allow_execute=true；scope 钉 sw_l1_pit_v2；
# live=false；promotion_approved=false；明文不解阻叶25）前禁止：
# nice -n 10 python3 "$SCRIPT" --mode p0 --execute --ok <ARCH_EXEC_OK> \
#   --out-dir data/v2/sw_pit/_staging_sw_l1_pit_v2_XXXX
# 最终产物约定见方案：新文件 sw_l1_pit_v2.parquet（不覆盖 BAD/CLEAN/VOTE）
```

## 硬禁

- 禁消费 `9e4359f9…`；禁 `--allow-shrink`；禁 dry 写 `data/` / `output/`
- 禁改 `scripts/acquire/sw_pit_refresh.py`（另工单）
- 禁声称本 dry/execute 解阻叶25 / X2
