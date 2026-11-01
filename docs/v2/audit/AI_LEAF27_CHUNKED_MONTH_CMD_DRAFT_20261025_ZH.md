# 叶27 更深分块 · HILIQ×x2×month CMD 草案（**未申 `.ok`**）

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-25T14:20:03-04:00（America/New_York；墙钟 2026-10-25 14:20 ET）
- **状态**：**DRAFT ONLY · READY·HOLD_UNTIL_MAIN_AFTER_R3B** · **ok_requested=false** · **不是 `.ok`** · **不替代 Arch 签发** · **禁自开跑** · **HOLD_UNTIL_MAIN_AFTER_R3B**
- **对照**：ABORT 回执 sha8 **`4e37aacc`**；脚本 UNCHANGED **`262f9bf6`**；VOID `.ok` **`3a6caa4f`→`fc218dd1` 已盘证**；先验审 `282d6ca1`（quarter）；交审排 r3b 后
- **优先级**：次于 r3b@15:00

## 明确声明

> **本文件未申请、未获得、不构成任何 run/probe `.ok`。**  
> 在 Arch **VOID** `3a6caa4f` 且另审 PASS、主排**新窗**并签发**新** `.ok` 之前，**禁止**执行下方 CLI。  
> **禁止**复跑 quarter 票 / RESTORED 任何 VOID `.ok`。

## PRIMARY CLI（待新 `.ok` 钉入；现不可跑）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python   research/leaf27_chunked_members_mktcap_r1.py   --universe HILIQ --window x2 --chunk-mode month
```

## FALLBACK CLI（仅 month 仍 ABORT_RSS 后另签；现不可跑）

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python   research/leaf27_chunked_members_mktcap_r1.py   --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40
```

## 硬钉（未来 `.ok` 必须逐字对齐）

| 项 | 值 |
|---|---|
| script | `research/leaf27_chunked_members_mktcap_r1.py` |
| script sha256 | `262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10`（**UNCHANGED**；CLI-only 侧稿） |
| universe / window | `HILIQ` / `x2`（**禁** `both`；sealed 另签） |
| chunk_mode PRIMARY | `month` |
| chunk_mode FALLBACK | `ndays` + `--chunk-ndays 40`（仅 month ABORT 后） |
| rss_limit | **1500** MB（**禁抬帽**） |
| 采样 | `/tmp/quantlab_leaf27_chunked_month_*` only |
| 禁复用 `.ok` | `8bcd79dc…` · `725be3e0…` · **`3a6caa4f…`（VOID 后仍禁 RESTORED）** 及一切 VOID/CONSUMED |
| 禁同 cmd | 旧 `…_lowmem_v1.py --universe HILIQ --window x2` **不可**再签；quarter 票 **不可**复跑 |

## 与 quarter 已消费票差异（防误复用）

| | quarter 票（ABORT） | 本草案 |
|---|---|---|
| chunk_mode | `quarter` | **`month`**（备 `ndays 40`） |
| 脚本字节 | `262f9bf6…` | **同** UNCHANGED |
| `.ok` | `3a6caa4f` 待 VOID | **无**（未申；须新签） |
| 峰证据 | 1572MB @chunk4_mktcap | **未实跑** |

## Prelaunch 清单（未来主令开跑时；**现不做**）

1. 新 `.ok` 盘证 MATCH（≠ `3a6caa4f` / ≠ `8bcd79dc` / ≠ `725be3e0`）；CLI 逐字 = PRIMARY（或另签 FALLBACK）
2. script sha256 MATCH `262f9bf6…`；`--dry-compile-only` → `live:false` `ok_requested:false` `rss_limit_mb:1500`
3. healthz：`8795`（或既定 SOP）`ok=true` 且 `quiet=true`；若 8787 不通按 SOP，**勿**因短暂宕自改 CLI/抬帽
4. wait≥15s；`pgrep` 无 gen/snapshot/kline/本脚本重影
5. MemAvailable≥2.5GiB；rss 帽=1500 禁抬
6. sampler 仅 `/tmp/quantlab_leaf27_chunked_month_*`；禁 RESTORED/`lowmem_v1` 同 cmd；禁 `--window both`/FULLA
7. 单次；峰证明 REQUIRED；交回执；QUIET 听 Arch 规则，AI 勿擅 lift
8. **勿抢 r3b@15:00**

## 静态自检（本回合可做；非授权）

```bash
sha256sum research/leaf27_chunked_members_mktcap_r1.py
# → 262f9bf6878d5c64956529a680abbf36e45adfe72fc7dedc4c68dc1c40291a10
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python   research/leaf27_chunked_members_mktcap_r1.py --dry-compile-only
# → live:false ok_requested:false rss_limit_mb:1500
```

live=false。
