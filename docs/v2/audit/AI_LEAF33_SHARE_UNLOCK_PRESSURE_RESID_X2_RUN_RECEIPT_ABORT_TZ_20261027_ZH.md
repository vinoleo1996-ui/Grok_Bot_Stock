# AI 回执：叶33 X2 PRIMARY ABORT（tz 比较 TypeError；禁自改复跑）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 06:36 ET**（America/New_York；ISO `2026-10-27T06:36:48-04:00`） |
| 主令 | ~06:33 ET SIGNED MATCH→GO；`.ok` **`c5ed13df`** / QUIET **`d588a1bd`** / SIGNED **`aaaff921`** / 审 **`2fa37636`** / 脚本 **`05c45917`** / FROZEN **`8ed43721`** / PIN **`4e17ccfc`** |
| **结论** | **ABORT_TYPEERROR_TZ**；rc≠0；**未**产出 alpha；**未**擅改脚本；**未** lift QUIET；**未**复用他叶 `.ok`；**未**申新 `.ok` |
| ≠X2 ACCEPT | **true** |
| ≠Book-Smoke / ≠selfcheck | **true** |
| live / leo_notify | **false** / **false** |

## 0. 一句话

PRIMARY 按钉开跑后约 2s 于 `_load_share_float_window` PIT 比较崩溃：`available_at` 为 **tz-aware**（`datetime64[us, Asia/Shanghai]`）而 `asof` 为 **tz-naive Timestamp** → `TypeError`。peak_kb≈**450768**≪1500。脚本 **`05c45917` UNCHANGED**；`.ok` **`c5ed13df`** / QUIET **`d588a1bd`** 仍在（do_not_lift）。**交主→Arch CONSUME**；等主令是否出 tz 对齐补丁（禁 AI 自改复跑）。

## 1. 运行钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_063601` |
| pid | `4096856` |
| nice | 10 |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/20261027_063601/ --sample-dir /tmp/quantlab_leaf33_share_unlock_20261027_063601` |
| `--no-overlap-report` | **未加**（禁） |
| rss 帽 | 1500；**未抬** |
| out | `output/ai_factory/_leaf33_share_unlock/20261027_063601`（空目录；无 alpha / 无 run_meta / 无 overlap） |
| sample-dir | `/tmp/quantlab_leaf33_share_unlock_20261027_063601`（空） |
| log | `/tmp/leaf33_x2_run/20261027_063601.log` sha8 **`5b667ce7`** |
| rc | TypeError 未捕获 → 进程早退（非 Exit 94/95） |

## 2. 产物 / 峰

| 项 | 值 |
|---|---|
| alpha parquet | **ABSENT** |
| overlap JSON | **ABSENT** |
| run_meta.json | **ABSENT** |
| peak_kb（RSS_CHECK after_sw） | **450768** ≪ 1536000 |
| after_mask peak_kb | 449684 |
| build_start peak_kb | 107312 |
| ABORT 类 | **TYPEERROR_TZ**（非 RSS / 非 Jaccard） |

## 3. 错误摘录（log）

```
TypeError: Cannot compare tz-naive and tz-aware datetime-like objects
...
File ".../leaf33_share_unlock_pressure_resid_alpha_build.py", line 818, in _load_share_float_window
    pit_ok = df["available_at"].isna() | (df["available_at"].dt.normalize() <= asof)
TypeError: Invalid comparison between dtype=datetime64[us, Asia/Shanghai] and Timestamp
```

根因候选（只报不改）：`share_float_pit.available_at` 带 `Asia/Shanghai`；`asof = pd.Timestamp(asof_max).normalize()` 无 tz。同函数后续 per-day PIT（~L1073）同类风险。叶32 margin 路径 `available_at` 多为 naive，故模板未暴露。

## 4. 钉点 MATCH（跑后）

| 项 | sha8 | 状态 |
|---|---|---|
| 脚本 | `05c45917` / `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` | **UNCHANGED** |
| `.ok` | `c5ed13df` / `c5ed13dff03942644f40443b1db01adc8cdee180fd4ade2b252a69658fe9edb7` | **仍在；未复用他叶** |
| QUIET | `d588a1bd` / `d588a1bdf7c88f40315ac8a9dacf394356ff50d3eb6b7c910fa720699a26f7f4` | **仍在；未擅 lift**；holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2`；expires 07:55 ET |
| SIGNED | `aaaff921` | 上游 |
| 审 | `2fa37636` | 上游 |
| FROZEN / PIN | `8ed43721` / `4e17ccfc` | 上游 |
| forbid `5774bb6e`+二十 | `.ok`∉forbid | MATCH |
| pgrep kline/export_static/snapshot/gen | 空 | MATCH |
| C3 / KEEP / 0087c928 | 未改定义；另队不夹带 | MATCH |

## 5. 禁令自检

- **未**改 `05c45917` / 未改叶32 `4e0f3c00` / 叶31 `08f37fd2`
- **未**申新 `.ok` / **未** lift QUIET
- **未**盲复跑 / **未** `--no-overlap-report` / **未**抬 rss
- **未**报 Leo / **未**派 Eng / **未**宣称 X2 ACCEPT
- `0087c928` / 叶28/29 **另队**

## 6. 下一跳（请主排）

1. **Arch CONSUME** 本回执（ABORT_TYPEERROR_TZ）
2. 是否开 **tz 对齐补丁**（建议：`available_at` 与 `asof`/`d` 统一 naive 日历日或统一 `Asia/Shanghai` 后再 `normalize`；覆盖 `_load_share_float_window` + per-day PIT）→ Arch 只审补丁 → **新** `.ok`（禁 RESTORED `c5ed13df` 作他用亦禁复用已消耗窗，听 Arch）
3. 当前 QUIET **保留**至 Arch/主令 lift；expires **07:55 ET**

**EXECUTED_ATTEMPTED=true** · **SUCCESS=false** · **X2_ACCEPT=false** · live=false · leo_notify=false
