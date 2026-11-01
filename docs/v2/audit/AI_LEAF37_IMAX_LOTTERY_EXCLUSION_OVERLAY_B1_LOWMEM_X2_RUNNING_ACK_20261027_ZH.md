# AI · 叶37 B1_LOWMEM X2 RUNNING_ACK · 2026-10-27

- status: **RUNNING**（prelaunch PASS → 真跑已开）
- ET_TS: `20261027_183719`
- OUT: `output/ai_factory/_leaf37_imax_lottery/20261027_183719/`
- set_wall_et: 2026-10-27 18:37:19 EDT
- leo_notify: **false**；live: **false**；≠X2 ACCEPT；book_smoke: false

## MATCH pins（开工复核）

| pin | sha8 | 全长/状态 |
|---|---|---|
| `.ok` | `b5be1164` | `b5be11642107551e241578c41907105763a4a92009fa3a91a0bc810dad453ff0` MATCH |
| SIGNED | `7b3bd298` | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_OK_SIGNED_20261027_ZH.md` MATCH |
| 脚本 B1 | `32605aca` | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` MATCH only |
| 基盘 | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` UNCHANGED **禁跑** |
| 审 PASS_WC | `b403a7e5` | REVIEW MATCH |
| COVER / CMD / DIFF / RECEIPT | `a4bfa39d` / `286e2104` / `6d61fd79` / `46f4192d` | MATCH |
| VOID / FROZEN / PIN | `998171e1` / `c5927f1b` / `e01be34c` | MATCH |
| QUIET lock | `a616211d` | `a616211dd0cdfc06a60f8b40c095c2f543b4f53f886fef6761a8034d6b2d054e` set_by=ai holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2` |
| forbid n=31 首项 | `4096d401` | +`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+… |

## Prelaunch SOP

- pgrep `kline.py|export_static.py|snapshot.py|gen.py`: **空**（二次 wait≥15s 后仍空）
- MemAvailable: `MemAvailable:   12739992 kB`
- dry-compile-only: **rc=0**；`b1_lowmem=true`；`prev_script_sha8=108aba8f`；forbid∋`4096d401`；`rss_limit_mb=1500`；`c3_option=B`；`top_q=0.2`；`primary_delivery=mask_only`
- IN_WINDOW: expires **2026-10-27T19:54:00-04:00**；signed 18:26；现 18:37 ET
- 禁：基盘 `108aba8f` / FULLA / `--no-overlap-report` / 抬 rss / RESTORED 旧票 / 擅 lift QUIET

## CLI

```bash
cd /workspace/QuantLab
export PYTHONDONTWRITEBYTECODE=1
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok --out output/ai_factory/_leaf37_imax_lottery/20261027_183719/ \
  > output/ai_factory/_leaf37_imax_lottery/20261027_183719/run.log 2>&1
```

- sampler_prefix 期望: `/tmp/quantlab_leaf37_imax_lottery_b1_`
- rss_limit_mb=**1500** 禁抬；peak_proof=**REQUIRED**
- PRIMARY=HILIQ×x2；mask-only q=0.20；C3=B；full_residual_e_id=false

## pid

- pid: **795437**
- run.log: `output/ai_factory/_leaf37_imax_lottery/20261027_183719/run.log`

## 硬禁重申

禁跑基盘；禁 RESTORED `4096d401`+；禁抬 rss；禁 `--no-overlap-report`；禁 FULLA；禁 Book-Smoke；禁自签 `.ok`；禁擅 lift QUIET；禁 git commit；≠X2 ACCEPT；leo_notify=false；live=false。
