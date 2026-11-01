# AI CMD DRAFT：叶33 tz 落地脚本（现不可跑；须新 `.ok`）

| 项 | 值 |
|---|---|
| 时刻 | **2026-10-27 07:03 ET** |
| 正式脚本 | **`afbbe7e7`** |
| 基线 | `05c45917` |
| Arch 补丁审 | `19cc790f` |

## approved_cmd_dry（可静校）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --dry-compile-only
```

## 拟 approved_cmd（**现不可跑**；须新 `.ok` + 主签窗；禁 RESTORED `c5ed13df`）

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/<ET_TS>/ --sample-dir /tmp/quantlab_leaf33_share_unlock_<ET_TS>
```

- **禁** `--no-overlap-report`
- rss=1500 禁抬；peak_proof REQUIRED
- `.ok` 路径为拟名；内容须为**新**签发且 sha8∉forbid21 且 ≠`c5ed13df`
