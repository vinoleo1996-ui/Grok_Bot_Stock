# 叶37 B1 / LOW_MEM · CMD DRAFT（只 dry；禁真跑）

- **角色**：QuantLab AI
- **时刻**：2026-10-27T18:09:50-04:00（America/New_York；墙钟 2026-10-27 18:09 ET）
- **状态**：DRAFT ONLY · EXECUTED=false · live=false · leo_notify=false · ≠X2 ACCEPT
- **脚本**：`research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` sha8 **`32605aca`**
- **基盘**：`…_alpha_build.py` sha8 **`108aba8f` UNCHANGED**

## 本拍已执行（验证 only）

```bash
pgrep -f 'kline.py|export_static.py|snapshot.py|gen.py'   # empty
sha256sum research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py
# -> 108aba8f… UNCHANGED

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python -c \
  'import py_compile; py_compile.compile(
     "research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py",
     cfile="/tmp/leaf37_b1_lowmem.pyc", doraise=True)'

/workspace/qlvenv/bin/python -m pyflakes \
  research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py
# CLEAN

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py \
  --dry-compile-only
# exit 0；pins: b1_lowmem=true; prev_script_sha8=108aba8f; forbid∋4096d401;
#         rss=1500; c3=B; mask_only; top_q=0.20

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py \
  --universe HILIQ --window x2 --x2-end 20261009
# exit 2：missing authorization flags

PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py \
  --dry-compile-only --universe FULLA
# exit 2：FULLA forbidden as PRIMARY
```

## 真跑意图（本拍禁执行；待新 `.ok` + 主窗）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python \
  research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py \
  --universe HILIQ --window x2 --x2-end 20261009 \
  --allow-real-data \
  --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok \
  --out output/ai_factory/_leaf37_imax_lottery/<ET_TS>/
```

硬钉：rss=**1500 禁抬**；peak_proof REQUIRED（含 year/instr 分块标签）；**禁** `--no-overlap-report`；C3=B；mask-only q=0.20；C11≠叶24；禁 RESTORED `4096d401`+旧票。

## 禁

真跑 / `--allow-real-data`（本拍）/ 自签 `.ok` / 挂 QUIET / RESTORED `4096d401` / 抬 rss / 改基盘 `108aba8f` / Book-Smoke / 声称 X2 ACCEPT。
