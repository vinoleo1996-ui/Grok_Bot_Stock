# AI 叶32 Margin Net Flow Resid X2 RUNNING_ACK

- ET: 2026-10-27 04:28:29 EDT
- status: **RUNNING**
- ET_TS: `20261027_042805`
- pid: `3952200` alive=True nice=10
- script: `research/leaf32_margin_net_flow_resid_alpha_build.py` sha8 **`4e0f3c00`** / 全长 `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187`
- `.ok`: `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok` sha8 **`02426b73`** / 全长 `02426b73d253237127772bd0023c52938ad58bdb76204feeddac87ceb385d736`
- QUIET: `output/loop/RESEARCH_QUIET.lock` sha8 **`6d62911f`** holder=`leaf32_MARGIN_NET_FLOW_RESID_X2`（do_not_lift）
- SIGNED回执: `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_X2_OK_SIGNED_20261027_ZH.md` sha8 **`39baa28e`**
- 脚本审: `814939b8` / COVER `b269aec5` / CMD `53002ae3` / DIFF `264d0159` / RECEIPT `0937a882` / FROZEN `6b8de5e9` / ArchFROZEN `7c0d864f`
- out: `output/ai_factory/_leaf32_margin_flow/20261027_042805/`
- log: `output/ai_factory/_leaf32_margin_flow/20261027_042805_logs/run_20261027_042805.log`
- samp: `/tmp/quantlab_leaf32_margin_flow_20261027_042805`
- approved_cmd: **exact**（含 `--allow-real-data --arch-ok-path`；**无** `--no-overlap-report`；另加推荐 `--sample-dir`）
- cmdline: `/workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf32_margin_flow/20261027_042805/ --sample-dir /tmp/quantlab_leaf32_margin_flow_20261027_042805`
- prelaunch: QUIET MATCH；healthz quiet=true gen/snapshot/kline=false child_pids={}；wait≥15s 复检；pgrep data readers empty；MemAvailable≈12.9Gi≥soft；dry-compile-only PASS（mechanism/W20/−rank/rss=1500/forbid∋4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa；primary_load=rebal_day_lazy_margin_float_bars）；`.ok` sha8∉forbid
- rss_limit_mb: **1500 禁抬**；硬 Exit 94/95；PRIMARY=HILIQ 按日懒加载；peak_proof REQUIRED
- ≠X2 ACCEPT / ≠selfcheck / ≠Book-Smoke；live=false；禁触 A18；禁 RESTORED `4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`；`0087c928` 另队
- 完后写 RUN_RECEIPT → 交 Arch CONSUME；**勿报 Leo**；**勿擅 lift QUIET**
