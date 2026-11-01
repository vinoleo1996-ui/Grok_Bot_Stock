# 94403 队列误标 done 更正（2026-10-18 ET）
- 依据：主 Agent 裁定。脚本把 status!="done" 的项视为待办，extra 项只要带 retry_cmd 就会重跑，所以用 pending 即可；另加 false_done_reason 字段。
- 归档：_recovery/data/backfill_queue_pre_falsedone_20261018/（SHA256SUMS 内 queue sha a0818008…）
- output/relay_outage_backfill_queue.json：a0818008db4d2e091bb1fa089141adba1fbdb884661837e6975b0332e2352fc7 → be8a78959e2a4294fd30fa28d6799b3691259147b6b7a7ef713a2eee70525f63
- 改动：sw/cyq/tier3 20261016 从 done 改为 pending，并写明原因；顶层 status 改为 pending_false_done_reverted（脚本下次启动时会覆盖这个值）。hsgt_top10 window 保持 done。
- 没有重启 backfill。94403 已于 04:59:31 退出，pidfile 不存在。
```diff
--- _recovery/data/backfill_queue_pre_falsedone_20261018/relay_outage_backfill_queue.json	2026-10-18 04:59:31.717122197 -0400
+++ output/relay_outage_backfill_queue.json	2026-10-18 05:03:11.121122197 -0400
@@ -121,9 +121,11 @@
     "step": "sw",
     "date": "20261016"
    },
-   "status": "done",
+   "status": "pending",
    "retry_cmd": "python3 scripts/nightly_update.py --date 20261016 --steps sw",
-   "last_rc": 0
+   "last_rc": 0,
+   "false_done_reason": "fail rc=-15 (terminated 04:30 ET per 主 Agent)",
+   "false_done_note": "2026-10-18 05:0x ET QuantLab Data: 04:59 被 backfill 误标 done (nightly_update exit 0 但步骤非 ok); 改回 pending, 未重启 backfill"
   },
   {
    "id": "nightly_step|cyq|20261016",
@@ -133,9 +135,11 @@
     "step": "cyq",
     "date": "20261016"
    },
-   "status": "done",
+   "status": "pending",
    "retry_cmd": "python3 scripts/nightly_update.py --date 20261016 --steps cyq",
-   "last_rc": 0
+   "last_rc": 0,
+   "false_done_reason": "partial: RELAY_DOWN fast-fail, sec=0",
+   "false_done_note": "2026-10-18 05:0x ET QuantLab Data: 04:59 被 backfill 误标 done (nightly_update exit 0 但步骤非 ok); 改回 pending, 未重启 backfill"
   },
   {
    "id": "nightly_step|tier3|20261016",
@@ -145,9 +149,11 @@
     "step": "tier3",
     "date": "20261016"
    },
-   "status": "done",
+   "status": "pending",
    "retry_cmd": "python3 scripts/nightly_update.py --date 20261016 --steps tier3",
-   "last_rc": 0
+   "last_rc": 0,
+   "false_done_reason": "partial: RELAY_DOWN fast-fail, sec=0",
+   "false_done_note": "2026-10-18 05:0x ET QuantLab Data: 04:59 被 backfill 误标 done (nightly_update exit 0 但步骤非 ok); 改回 pending, 未重启 backfill"
   }
  ],
  "items": [
@@ -455,7 +461,7 @@
   "err": null,
   "checked_at": "2026-10-18T01:22:26-0400"
  },
- "status": "done",
+ "status": "pending_false_done_reverted",
  "events_last": {
   "rc": 0,
   "n_fails": 0
```
