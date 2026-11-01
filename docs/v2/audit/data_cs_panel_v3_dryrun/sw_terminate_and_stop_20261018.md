# sw nightly 终止 + 94403 STOP 回执（2026-10-18，ET）

授权：主 Agent 例外授权，只针对 PID 212763/212762（SIGTERM，不用 kill -9）；94403 STOP/CONT 已由主 Agent 批准。本步没跑 D1a 或任何 dry-run，没碰 moneyflow，没启动 8787，没碰 94322（fund_portfolio 继续跑）。

## 时间线（ET）
- 04:14:41 首次快照：94403 S；212762 S（nightly_update.py --date 20261016 --steps sw，lstart 02:28:20）；212763 Sl（sw_pit_refresh.py）。日志 logs/nightly/20261016_sw.log 里一直是 index_member_all 504/503 upstream_pool_exhausted。
- 04:15:14–04:29:44 每 30 秒轮询一次，212762 一直没自己结束 → 走路径 B。
- 04:30:14.501 到 04:30，212762 还活着（etime 02:01:53）。
- 04:30:14.550 钉住表 sha/mtime（前）：89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c，mtime 2026-10-18 01:08:43.180683904
- **04:30:14.551 SIGSTOP 94403**；04:30:15.556 /proc/94403/stat state=T
- 04:30:15.557 SIGTERM 212763 → 04:30:16.561 已退出
- 04:30:21.571 SIGTERM 212762（等 5 秒它没自己退出）
- 04:30:51.626 脚本报 "212762 STILL ALIVE after 30s … state=Z" → 脚本按规则 ABORT。**异常说明：** 212762 已经终止，现在是 zombie/defunct（RSS 0，[python3] <defunct>，PPid 94403）。kill -0 对 zombie 仍然成功，所以脚本当成"活着"。因为父进程 94403 处于 T，没法回收它；94403 CONT 后会回收。zombie 不能再执行或写文件，我判断它已退出，于是继续做了第 4、5 步（隔离用的是可逆的 mv）。如果你按字面规则认为当时应该停下，请知悉这一偏离。
- 04:31:35 隔离 2 个 sw 候选文件（见下）
- 04:31:50 终态快照和三项检查

## 隔离清单（data/v2/_quarantine/sw_pit_INCOMPLETE_20261018/，保留相对路径）
| 原路径 | sha256 | 大小 | mtime |
|---|---|---|---|
| data/v2/sw_pit/sw2021_classify_l1.parquet | 471c2b0f628406b86c378504d5ef69d42afae76bf194cf6f4b896832c9e8a01b | 4957 | 02:28:25.42 |
| data/v2/sw_pit/sw2021_classify_l2.parquet | 125831fd7d07c149711cfcbdc53949ee98cb3a5e1e3756708aaf13df8a6f9f63 | 7729 | 02:28:27.00 |

INCOMPLETE.md sha256 9b0eff6a8b5296dcc57064ca8dd6cbfd87fe836dd5edef4d8bcc6820df7dc55b

备注：
- 这两个文件和 output/data_v2_bundle/sw_pit/ 下 01:13 的副本逐字节相同，内容实际没变。
- 它们与 data/v2/sw_pit/manifest.json 记录的 sha（193aa546…、96ce98e5…）不一致；bundle 副本同样不一致，所以这个不一致在本次运行之前就已存在。
- 隔离后 data/v2/sw_pit/ 缺 classify_l1/l2，manifest.json 仍然引用它们。sw_pit 本来就是 research 候选（promotion_approved=false）。
- members 表和 raw（01:13）没有被本次运行改写，没移动。

## 自 212762 启动（02:28:20）以来 data/v2 下的写入（列出，没移动）
- data/v2/tushare_raw/fund_portfolio_dh/：3430 个文件，属于 94322 fund_portfolio，正常写入，排除。
- data/v2/northbound/hsgt_top10_daily_2018plus.parquet 和 northbound_summary.json（02:28:21）：前一个 hsgt 步骤的收尾（tushare_raw/hsgt_top10/20261016.parquet 02:28:16），不是 sw，没移动。
- data/v2/alerts/alerts_20261018.parquet（04:04:58）：不是 sw，写入者不明，没移动。
- 已存在的零字节文件 data/v2/asof_extend_tushare_202610/panels_backup_prefactor/bj.920415.parquet（01:05，早于本次运行），不相关，没动。

## 三项强制检查
1. **PASS**：钉住表 data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet，04:31:50 时 sha256 仍为 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c，mtime 仍为 01:08:43.18（前后一致）。
2. **PASS**：隔离区以外的 data/v2 里没有 212762 留下的临时文件或半写文件。检查范围：整个 data/v2（prune _quarantine）里的 *.tmp、*.part、*.partial、隐藏文件、*~；自 02:28:20 起的零字节文件；data/v2/sw* 下自 02:28:20 起的写入。唯一命中的是 data/v2/sw_pit 目录本身，因为 mv 改了它的 mtime。另外，sw_pit_refresh.py 只会写 data/v2/sw_pit/ 下的 classify、members、*_pit 和 manifest。
3. **PASS（附说明）**：212763 已经不在进程表里；212762 已终止，只剩 zombie（Z、<defunct>、RSS 0），等 94403 CONT 后回收；94403 为 T（/proc state T），子进程只有这个 zombie，94403 下没有活的 nightly、tier3 或 backfill 子进程。

## 受保护路径的写入检查（自 02:28:20 起写入数）
bars 0（最新 01:12:24）、adj 0（01:14:22）、tier3_daily 0（02:28:02，早于启动）、index 0、float_mktcap 0、valuation 0、universe 0、calendar 0、etf 0（01:15:40）、cb 0（01:11:48）、futures 0（01:12:09）、etf_510300 0（01:08:43）、financials_pit 0（01:15:41）、ep 0（01:15:40）、tushare_raw/trade_cal.parquet mtime 01:08:43、st_events 0（01:09:44）、tushare_raw/daily、daily_basic、adj_factor 0（01:14:21）、index_daily 0、fund_daily 0。全部没有写入。

## 后续注意
- 94403 CONT 后会回收 212762，看到 sw 失败后可能马上重试 sw。sw 要等中转恢复后再重跑，不能落在对拍窗口或 dry-run/execute 期间。CONT 前可能需要先确认 94403 的重试队列。
- 10-19 05:30 ET 前必须 CONT 94403。

## ps 快照
### 04:14:41 首次（摘录）
```
  94322   94319 Ssl     02:52:17 140924 python3 scripts/acquire/remaining_after_stk_surv.py
  94403   94401 Ss      02:52:15 35780 python3 scripts/acquire/relay_outage_backfill.py
 212762   94403 S       01:46:20 14228 python3 scripts/nightly_update.py --date 20261016 --steps sw
 212763  212762 Sl      01:46:20 153040 /usr/bin/python3 scripts/acquire/sw_pit_refresh.py
```
### 原始执行日志（含 04:30:14 和 04:30:51 的完整 ps）
```
PATH_B: 04:30 reached 2026-10-18 04:30:14.501 EDT, 212762 alive
### ps snapshot 2026-10-18 04:30:14.503 EDT
    PID    PPID STAT     ELAPSED   RSS CMD
      1       0 Ss      03:24:31   752 /tini -- /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
      7       1 Sl      03:24:31  7640 /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
     53       7 Ss      03:24:31 14736 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
    204      53 S       03:24:31 32564 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    209     204 S       03:24:31  2028 bash /usr/local/bin/box-bounded-log --run /tmp/novnc-forks.log -- /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    210     209 S       03:24:31  1780 flock -n /tmp/novnc-forks.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    211     210 Sl      03:24:31 34020 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    227      53 Ssl     03:24:31 48524 /exec-daemon/node /usr/local/bin/sand-window-router.mjs 1339 1337 14000
    247      53 Ssl     03:24:31 48652 /exec-daemon/node /usr/local/bin/sand-session-sync.mjs
    248      53 Sl      03:24:31 99416 /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    257     248 S       03:24:31  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-web-bot-auth.log -- /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    258     257 S       03:24:31  1896 flock -n /tmp/sand-web-bot-auth.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    259     258 Sl      03:24:31 32612 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    277      53 Sl      03:24:31 71384 /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    284     277 S       03:24:31  2016 bash /usr/local/bin/box-bounded-log --run /tmp/sand-ua-governor.log -- /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    286     284 S       03:24:31  1884 flock -n /tmp/sand-ua-governor.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    290     286 Sl      03:24:31 32988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    322      53 Ssl     03:24:31 49900 /exec-daemon/node /usr/local/bin/sand-cookie-persist.mjs
    323      53 S       03:24:31  4276 bash /usr/local/bin/supervise-exec-daemon 1337 /usr/local/bin/start-exec-daemon
    324      53 S       03:24:31  4084 bash /usr/local/bin/supervise-egress-tunnel 8790 /usr/local/bin/start-egress-tunnel
    369     323 Ss      03:24:31  3424 bash /usr/local/bin/start-exec-daemon
    372     324 Ssl     03:24:31  2508 /usr/local/bin/sand-egress-tunnel server
    376     369 Sl      03:24:31 91660 /exec-daemon/node /exec-daemon/index.js serve --port 1337 --pty-websocket-port 1338 --auth-token local --rg-path /exec-daemon/rg --pty-auth-token local-pty --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
    720       1 Ss      03:24:21  4316 bash /usr/local/bin/start-desktop.sh
    724     720 S       03:24:21  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-2/start-desktop.log -- /usr/local/bin/start-desktop.sh
    725     724 S       03:24:21  1792 flock -n /tmp/sand-window-2/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    726     725 Sl      03:24:21 34316 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    766       1 Ss      03:24:21  2036 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
    771     720 S       03:24:21 64044 Xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    776     771 S       03:24:21  1904 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:2.log -- /usr/local/bin/box-xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    778     776 S       03:24:21  1864 flock -n /tmp/xvfb:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
    779     778 Sl      03:24:21 33344 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
   1153     771 Z       03:24:20     0 [bash] <defunct>
   1201       1 Ssl     03:24:20 68900 /exec-daemon/node /exec-daemon/index.js serve --port 14002 --pty-websocket-port 13602 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   1277     720 Sl      03:24:20 26088 xfwm4 --compositor=off
   1282    1277 S       03:24:20  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:2.log -- /usr/local/bin/box-xfwm4 --compositor=off
   1283    1282 S       03:24:20  1784 flock -n /tmp/xfwm4:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1285    1283 Sl      03:24:20 33180 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1316     720 S       03:24:20  4080 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1325    1316 S       03:24:20  1984 bash /usr/local/bin/box-bounded-log --run /tmp/picom:2.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1326    1325 S       03:24:20  1792 flock -n /tmp/picom:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1329    1326 Sl      03:24:20 33040 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1380       1 Sl      03:24:20  3476 /usr/libexec/dconf-service
   1536       1 Ssl     03:24:20 21152 plank --name dock1
   1543    1536 S       03:24:20  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:2-dock1.log -- /usr/local/bin/box-plank --name dock1
   1544    1543 S       03:24:20  1828 flock -n /tmp/plank:2-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1546    1544 Sl      03:24:20 33052 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1559     720 S       03:24:20  1872 tail -f /dev/null
   1618       1 S       03:24:20  3364 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   1619    1618 Sl      03:24:20  7168 /usr/libexec/bamf/bamfdaemon
   5268       1 Ss      03:21:47  4308 bash /usr/local/bin/start-desktop.sh
   5271    5268 S       03:21:47  1928 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-12/start-desktop.log -- /usr/local/bin/start-desktop.sh
   5273    5271 S       03:21:47  1844 flock -n /tmp/sand-window-12/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5274    5273 Sl      03:21:47 34184 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5313       1 Ss      03:21:47  2100 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   5318    5268 S       03:21:47 60404 Xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5323    5318 S       03:21:47  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:12.log -- /usr/local/bin/box-xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5324    5323 S       03:21:47  1904 flock -n /tmp/xvfb:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   5326    5324 Sl      03:21:47 33956 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   6227    5318 Z       03:21:47     0 [bash] <defunct>
   6247       1 Ssl     03:21:47 96196 /exec-daemon/node /exec-daemon/index.js serve --port 14012 --pty-websocket-port 13612 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   6295    5268 S       03:21:46 28912 x11vnc -skip_lockkeys -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6300    6295 S       03:21:46  2012 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:12.log -- /usr/local/bin/box-x11vnc -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6301    6300 S       03:21:46  1848 flock -n /tmp/x11vnc:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6302    6301 Sl      03:21:46 33832 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6325    5268 Sl      03:21:46 57632 xfwm4 --compositor=off
   6333    6325 S       03:21:46  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:12.log -- /usr/local/bin/box-xfwm4 --compositor=off
   6335    6333 S       03:21:46  1928 flock -n /tmp/xfwm4:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6336    6335 Sl      03:21:46 33988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6368    5268 S       03:21:46  4776 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6375    6368 S       03:21:46  2036 bash /usr/local/bin/box-bounded-log --run /tmp/picom:12.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6376    6375 S       03:21:46  1796 flock -n /tmp/picom:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6380    6376 Sl      03:21:46 33908 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6450       1 Sl      03:21:46  3432 /usr/libexec/dconf-service
   6654       1 Ssl     03:21:46 59200 plank --name dock1
   6662    6654 S       03:21:46  2056 bash /usr/local/bin/box-bounded-log --run /tmp/plank:12-dock1.log -- /usr/local/bin/box-plank --name dock1
   6665    6662 S       03:21:46  1876 flock -n /tmp/plank:12-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6668    6665 Sl      03:21:46 33984 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6697    5268 S       03:21:46  1896 tail -f /dev/null
   6834       1 S       03:21:46  3468 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   6835    6834 Sl      03:21:46  8616 /usr/libexec/bamf/bamfdaemon
   8307       1 Ss      03:20:25  4300 bash /usr/local/bin/start-desktop.sh
   8311    8307 S       03:20:25  2072 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-6/start-desktop.log -- /usr/local/bin/start-desktop.sh
   8312    8311 S       03:20:25  1896 flock -n /tmp/sand-window-6/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8313    8312 Sl      03:20:25 34012 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8352       1 Ss      03:20:25  2148 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   8357    8307 S       03:20:25 60424 Xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8363    8357 S       03:20:25  1992 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:6.log -- /usr/local/bin/box-xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8364    8363 S       03:20:25  1860 flock -n /tmp/xvfb:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   8366    8364 Sl      03:20:25 34252 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   9579    8357 Z       03:20:24     0 [bash] <defunct>
   9604       1 Ssl     03:20:24 125944 /exec-daemon/node /exec-daemon/index.js serve --port 14006 --pty-websocket-port 13606 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   9653    8307 S       03:20:24 28992 x11vnc -skip_lockkeys -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9658    9653 S       03:20:24  2076 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:6.log -- /usr/local/bin/box-x11vnc -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9659    9658 S       03:20:24  1796 flock -n /tmp/x11vnc:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9661    9659 Sl      03:20:24 33932 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9679    8307 Sl      03:20:24 11392 xfwm4 --compositor=off
   9684    9679 S       03:20:24  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:6.log -- /usr/local/bin/box-xfwm4 --compositor=off
   9685    9684 S       03:20:24  1860 flock -n /tmp/xfwm4:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9692    9685 Sl      03:20:24 34276 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9730    8307 S       03:20:24  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9738    9730 S       03:20:24  2072 bash /usr/local/bin/box-bounded-log --run /tmp/picom:6.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9741    9738 S       03:20:24  1904 flock -n /tmp/picom:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9743    9741 Sl      03:20:24 34180 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9795       1 Sl      03:20:24  3336 /usr/libexec/dconf-service
  10084       1 Ssl     03:20:24 59472 plank --name dock1
  10095   10084 S       03:20:24  2020 bash /usr/local/bin/box-bounded-log --run /tmp/plank:6-dock1.log -- /usr/local/bin/box-plank --name dock1
  10096   10095 S       03:20:24  1848 flock -n /tmp/plank:6-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10100   10096 Sl      03:20:24 33960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10125    8307 S       03:20:24  1888 tail -f /dev/null
  10284       1 S       03:20:23  3436 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  10287   10284 Sl      03:20:23  8556 /usr/libexec/bamf/bamfdaemon
  11187       1 Ss      03:19:54  4368 bash /usr/local/bin/start-desktop.sh
  11191   11187 S       03:19:54  2056 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-8/start-desktop.log -- /usr/local/bin/start-desktop.sh
  11192   11191 S       03:19:54  1832 flock -n /tmp/sand-window-8/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11193   11192 Sl      03:19:54 34096 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11232       1 Ss      03:19:54  2160 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  11237   11187 S       03:19:54 61208 Xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11242   11237 S       03:19:54  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:8.log -- /usr/local/bin/box-xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11243   11242 S       03:19:54  1868 flock -n /tmp/xvfb:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  11245   11243 Sl      03:19:54 33972 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  12725   11237 Z       03:19:53     0 [bash] <defunct>
  12735       1 Ssl     03:19:53 89316 /exec-daemon/node /exec-daemon/index.js serve --port 14008 --pty-websocket-port 13608 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  12790   11187 S       03:19:53 29100 x11vnc -skip_lockkeys -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12797   12790 S       03:19:53  1972 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:8.log -- /usr/local/bin/box-x11vnc -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12798   12797 S       03:19:53  1944 flock -n /tmp/x11vnc:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12800   12798 Sl      03:19:53 34032 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12819   11187 Sl      03:19:53 11396 xfwm4 --compositor=off
  12824   12819 S       03:19:53  2044 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:8.log -- /usr/local/bin/box-xfwm4 --compositor=off
  12825   12824 S       03:19:53  1828 flock -n /tmp/xfwm4:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12826   12825 Sl      03:19:53 34084 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12882   11187 S       03:19:53  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12891   12882 S       03:19:53  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:8.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12892   12891 S       03:19:53  1824 flock -n /tmp/picom:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12896   12892 Sl      03:19:53 33904 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12929       1 Sl      03:19:53  3616 /usr/libexec/dconf-service
  13167       1 Ssl     03:19:53 59724 plank --name dock1
  13178   13167 S       03:19:53  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:8-dock1.log -- /usr/local/bin/box-plank --name dock1
  13179   13178 S       03:19:53  1868 flock -n /tmp/plank:8-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13180   13179 Sl      03:19:53 33988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13209   11187 S       03:19:52  1968 tail -f /dev/null
  13486       1 S       03:19:52  3444 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  13489   13486 Sl      03:19:52  8748 /usr/libexec/bamf/bamfdaemon
  14353       1 Ss      03:19:36  4228 bash /usr/local/bin/start-desktop.sh
  14356   14353 S       03:19:36  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-5/start-desktop.log -- /usr/local/bin/start-desktop.sh
  14358   14356 S       03:19:36  1824 flock -n /tmp/sand-window-5/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14359   14358 Sl      03:19:36 33876 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14398       1 Ss      03:19:36  2192 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  14403   14353 S       03:19:36 61084 Xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14408   14403 S       03:19:36  1928 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:5.log -- /usr/local/bin/box-xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14409   14408 S       03:19:36  1924 flock -n /tmp/xvfb:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  14411   14409 Sl      03:19:36 33972 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  16166   14403 Z       03:19:35     0 [bash] <defunct>
  16176       1 Ssl     03:19:34 96040 /exec-daemon/node /exec-daemon/index.js serve --port 14005 --pty-websocket-port 13605 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  16236   14353 S       03:19:34 29000 x11vnc -skip_lockkeys -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16242   16236 S       03:19:34  2040 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:5.log -- /usr/local/bin/box-x11vnc -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16243   16242 S       03:19:34  1932 flock -n /tmp/x11vnc:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16246   16243 Sl      03:19:34 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16263   14353 Sl      03:19:34 11432 xfwm4 --compositor=off
  16268   16263 S       03:19:34  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:5.log -- /usr/local/bin/box-xfwm4 --compositor=off
  16269   16268 S       03:19:34  1848 flock -n /tmp/xfwm4:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16271   16269 Sl      03:19:34 34296 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16311   14353 S       03:19:34  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16316   16311 S       03:19:34  2048 bash /usr/local/bin/box-bounded-log --run /tmp/picom:5.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16318   16316 S       03:19:34  1944 flock -n /tmp/picom:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16321   16318 Sl      03:19:34 34252 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16362       1 Sl      03:19:34  3336 /usr/libexec/dconf-service
  16645       1 Ssl     03:19:34 59744 plank --name dock1
  16656   16645 S       03:19:34  2012 bash /usr/local/bin/box-bounded-log --run /tmp/plank:5-dock1.log -- /usr/local/bin/box-plank --name dock1
  16657   16656 S       03:19:34  1900 flock -n /tmp/plank:5-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16661   16657 Sl      03:19:34 33932 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16690   14353 S       03:19:34  1916 tail -f /dev/null
  16944       1 S       03:19:34  3384 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  16947   16944 Sl      03:19:34  8804 /usr/libexec/bamf/bamfdaemon
  18167       1 Ss      03:18:57  4288 bash /usr/local/bin/start-desktop.sh
  18171   18167 S       03:18:57  2004 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-4/start-desktop.log -- /usr/local/bin/start-desktop.sh
  18172   18171 S       03:18:57  1868 flock -n /tmp/sand-window-4/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18173   18172 Sl      03:18:57 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18212       1 Ss      03:18:57  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  18217   18167 S       03:18:57 61228 Xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18222   18217 S       03:18:57  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:4.log -- /usr/local/bin/box-xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18224   18222 S       03:18:57  1840 flock -n /tmp/xvfb:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  18225   18224 Sl      03:18:57 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  20160   18217 Z       03:18:56     0 [bash] <defunct>
  20188       1 Ssl     03:18:56 92100 /exec-daemon/node /exec-daemon/index.js serve --port 14004 --pty-websocket-port 13604 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  20233   18167 S       03:18:56 29044 x11vnc -skip_lockkeys -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20238   20233 S       03:18:56  2056 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:4.log -- /usr/local/bin/box-x11vnc -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20241   20238 S       03:18:56  1876 flock -n /tmp/x11vnc:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20242   20241 Sl      03:18:56 34372 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20261   18167 Sl      03:18:56 11764 xfwm4 --compositor=off
  20266   20261 S       03:18:56  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:4.log -- /usr/local/bin/box-xfwm4 --compositor=off
  20267   20266 S       03:18:56  1924 flock -n /tmp/xfwm4:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20269   20267 Sl      03:18:56 34280 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20316   18167 S       03:18:56  4916 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20323   20316 S       03:18:56  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:4.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20324   20323 S       03:18:56  1828 flock -n /tmp/picom:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20328   20324 Sl      03:18:56 33960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20372       1 Sl      03:18:56  3488 /usr/libexec/dconf-service
  20653       1 Ssl     03:18:55 60444 plank --name dock1
  20665   20653 S       03:18:55  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:4-dock1.log -- /usr/local/bin/box-plank --name dock1
  20667   20665 S       03:18:55  1932 flock -n /tmp/plank:4-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20671   20667 Sl      03:18:55 33996 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20713   18167 S       03:18:55  1964 tail -f /dev/null
  20976       1 S       03:18:55  3456 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  20979   20976 Sl      03:18:55  8696 /usr/libexec/bamf/bamfdaemon
  26442       1 Ss      03:15:50  3524 /bin/bash ./supervise.sh
  26447       1 Ss      03:15:50  3404 /bin/bash ./deploy_supervise.sh
  26450   26447 S       03:15:50  3468 /bin/bash ./deploy_loop.sh
  26454       1 Ss      03:15:50  3432 ql_keepalive_loop -c while true; do sleep 600; /workspace/quantlab-web/start_all.sh --from-keepalive; done
  26581       1 Ssl     03:15:49 40084 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/cli/index.js serve --port 6768 --pairing-address grok-bot
  26627   26581 Sl      03:15:49 150448 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --user-data-dir=/home/box/.config/orca --serve --serve-port 6768 --serve-pairing-address grok-bot
  26630   26627 S       03:15:49 18112 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote --no-zygote-sandbox
  26631   26627 S       03:15:49 18084 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26633   26631 S       03:15:49 10788 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26702       1 Sl      03:15:48  3572 /home/box/.orca/app-1.4.224-20261018051422/chrome_crashpad_handler --monitor-self-annotation=ptype=crashpad-handler --no-rate-limit --no-upload-gzip --database=/home/box/.config/orca/Crashpad --annotation=_productName=orca --annotation=_version=1.4.224 --annotation=lsb-release=Debian GNU/Linux 13 (trixie) --annotation=plat=Linux --annotation=prod=Electron --annotation=ver=43.7.5 --initial-client-fd=41 --shared-client-connection
  26752   26630 Sl      03:15:48 23232 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=gpu-process --disable-dev-shm-usage --ozone-platform=x11 --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --gpu-preferences=WAAAAAAAAAAgAQAEAAAAAAAAAAAAAGAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAABAAAAAAAAAAgAAAAAAAAACAAAAAAAAAAIAAAAAAAAAA== --use-gl=disabled --shared-files --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708988185955192
  26756   26752 S       03:15:48 12136 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=broker
  26762   26627 Sl      03:15:48 24784 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=utility --utility-sub-type=network.mojom.NetworkService --lang=en-US --service-sandbox-type=none --disable-dev-shm-usage --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --standard-schemes=orca-preview,orca-media --secure-schemes=orca-preview,orca-media --cors-schemes=orca-preview --fetch-schemes=orca-preview --streaming-schemes=orca-preview,orca-media --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708989122997041
  26800   26627 Ssl     03:15:47 41724 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --socket /home/box/.config/orca/daemon/daemon-v43.sock --token /home/box/.config/orca/daemon/daemon-v43.token --pid-record /home/box/.config/orca/daemon/daemon-v43.pid --launch-nonce 9f1cf877-a9c1-4595-b95d-e8ac301fed85 --entry-path /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --app-version 1.4.224 --spawner-exec-path /home/box/.orca/app-1.4.224-20261018051422/orca-ide --log-file /home/box/.config/orca/logs/daemon.log
  27167      53 Ss      03:15:45  3748 bash /usr/local/bin/supervise-sand-supervisor /tmp/sand-supervisor/status.json /tmp/sand-supervisor.log /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27182   27167 Ssl     03:15:45 65800 /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27183   27167 Ss      03:15:45  3428 bash -c while sleep "$1"; do kill -USR1 "$2" 2>/dev/null || exit 0; done ticker 5 27167
  27186      53 S       03:15:45  4328 bash /usr/local/bin/start-desktop.sh
  27191   27186 S       03:15:45  1992 bash /usr/local/bin/box-bounded-log --run /tmp/start-desktop.log -- /usr/local/bin/start-desktop.sh
  27192   27191 S       03:15:45  1824 flock -n /tmp/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27194   27192 Sl      03:15:45 34156 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27245       1 Ss      03:15:45  2232 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  27250   27186 S       03:15:45 61116 Xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27255   27250 S       03:15:45  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:1.log -- /usr/local/bin/box-xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27256   27255 S       03:15:45  1864 flock -n /tmp/xvfb:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27258   27256 Sl      03:15:45 34500 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27263   27250 Z       03:15:45     0 [bash] <defunct>
  27313   27182 Ssl     03:15:45 599800 /exec-daemon/node --disable-warning=ExperimentalWarning /opt/sand/sand-host/host-main.cjs
  27366      53 Ss      03:15:45 24188 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
  27383      53 S       03:15:45  2592 /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27385   27383 S       03:15:45  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-orbitd.log -- env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27386   27385 S       03:15:45  1944 flock -n /tmp/sand-orbitd.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27389   27386 Sl      03:15:45 34396 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27390   27383 S       03:15:45  8104 /usr/local/libexec/sand/sand-daemon-supervisor __supervise orbitd
  27398   27186 S       03:15:45 20080 x11vnc -skip_lockkeys -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27403   27398 S       03:15:45  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:1.log -- /usr/local/bin/box-x11vnc -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27404   27403 S       03:15:45  1832 flock -n /tmp/x11vnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27405   27404 Sl      03:15:45 34220 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27427   27186 S       03:15:45 35112 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27432   27427 S       03:15:45  2020 bash /usr/local/bin/box-bounded-log --run /tmp/novnc:1.log -- websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27433   27432 S       03:15:45  1836 flock -n /tmp/novnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27434   27433 Sl      03:15:45 34484 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27453   27186 Sl      03:15:45 11748 xfwm4 --compositor=off
  27458   27453 S       03:15:45  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:1.log -- /usr/local/bin/box-xfwm4 --compositor=off
  27462   27458 S       03:15:45  1880 flock -n /tmp/xfwm4:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27466   27462 Sl      03:15:45 34148 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27505   27186 S       03:15:45  4860 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27510   27505 S       03:15:45  1992 bash /usr/local/bin/box-bounded-log --run /tmp/picom:1.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27512   27510 S       03:15:45  1880 flock -n /tmp/picom:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27513   27512 Sl      03:15:45 34128 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27574       1 Sl      03:15:45  3560 /usr/libexec/dconf-service
  27953      53 Ssl     03:15:45 60176 plank --name dock1
  27967   27953 S       03:15:45  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:1-dock1.log -- /usr/local/bin/box-plank --name dock1
  27969   27967 S       03:15:45  1820 flock -n /tmp/plank:1-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  27974   27969 Sl      03:15:45 33916 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  28014   27186 S       03:15:45  1948 tail -f /dev/null
  28485       1 S       03:15:44  3376 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  28490   28485 Sl      03:15:44  8700 /usr/libexec/bamf/bamfdaemon
  29120   27390 Sl      03:15:44  5244 /var/lib/sand-daemon-supervisor/orbitd/releases/28b0833c5707e1c919cee4d4ab5a8ad0eeac9c46/orbitd
  29240   27313 Sl      03:15:44 200612 /opt/sand/sand-host/extensions/codebase-telemetry/csnaps
  29910      53 Ss      03:15:40  4428 bash /usr/local/bin/start-desktop.sh
  29915   29910 S       03:15:40  1980 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-3/start-desktop.log -- /usr/local/bin/start-desktop.sh
  29916   29915 S       03:15:40  1824 flock -n /tmp/sand-window-3/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  29917   29916 Sl      03:15:40 34200 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  30000      53 Ss      03:15:40  2272 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  30031   29910 S       03:15:40 52252 Xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30036   30031 S       03:15:40  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:3.log -- /usr/local/bin/box-xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30037   30036 S       03:15:40  1824 flock -n /tmp/xvfb:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30039   30037 Sl      03:15:40 34084 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30381   27182 Ss      03:15:40 20056 x11vnc -skip_lockkeys -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30384   30381 S       03:15:40  2028 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:2.log -- /usr/local/bin/box-x11vnc -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30385   30384 S       03:15:40  1932 flock -n /tmp/x11vnc:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  30386   30385 Sl      03:15:40 35400 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  33709   30031 Z       03:15:38     0 [bash] <defunct>
  33760      53 Ssl     03:15:37 96228 /exec-daemon/node /exec-daemon/index.js serve --port 14003 --pty-websocket-port 13603 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  33788   29910 S       03:15:37 29036 x11vnc -skip_lockkeys -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33790   33788 S       03:15:37  2024 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:3.log -- /usr/local/bin/box-x11vnc -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33791   33790 S       03:15:37  1840 flock -n /tmp/x11vnc:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33792   33791 Sl      03:15:37 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33824   29910 Sl      03:15:37 11788 xfwm4 --compositor=off
  33827   33824 S       03:15:37  2076 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:3.log -- /usr/local/bin/box-xfwm4 --compositor=off
  33832   33827 S       03:15:37  1824 flock -n /tmp/xfwm4:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33834   33832 Sl      03:15:37 34284 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33861   29910 S       03:15:37  4876 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33871   33861 S       03:15:37  2024 bash /usr/local/bin/box-bounded-log --run /tmp/picom:3.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33872   33871 S       03:15:37  1896 flock -n /tmp/picom:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33877   33872 Sl      03:15:37 34140 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33940      53 Sl      03:15:37  3492 /usr/libexec/dconf-service
  34299      53 Ssl     03:15:37 60100 plank --name dock1
  34308   34299 S       03:15:37  2052 bash /usr/local/bin/box-bounded-log --run /tmp/plank:3-dock1.log -- /usr/local/bin/box-plank --name dock1
  34317   34308 S       03:15:37  1824 flock -n /tmp/plank:3-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34330   34317 Sl      03:15:37 34072 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34358   29910 S       03:15:37  1900 tail -f /dev/null
  34507      53 S       03:15:37  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  34509   34507 Sl      03:15:37  8908 /usr/libexec/bamf/bamfdaemon
  35700      53 Ss      03:15:32  4332 bash /usr/local/bin/start-desktop.sh
  35703   35700 S       03:15:32  1996 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-7/start-desktop.log -- /usr/local/bin/start-desktop.sh
  35704   35703 S       03:15:32  1924 flock -n /tmp/sand-window-7/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35705   35704 Sl      03:15:32 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35755      53 Ss      03:15:32  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  35760   35700 S       03:15:32 52176 Xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35765   35760 S       03:15:32  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:7.log -- /usr/local/bin/box-xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35766   35765 S       03:15:32  1868 flock -n /tmp/xvfb:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  35767   35766 Sl      03:15:32 34044 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  38646   35760 Z       03:15:30     0 [bash] <defunct>
  38695      53 Ssl     03:15:30 92264 /exec-daemon/node /exec-daemon/index.js serve --port 14007 --pty-websocket-port 13607 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  38714   35700 S       03:15:30 29116 x11vnc -skip_lockkeys -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38716   38714 S       03:15:30  1976 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:7.log -- /usr/local/bin/box-x11vnc -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38720   38716 S       03:15:30  1916 flock -n /tmp/x11vnc:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38723   38720 Sl      03:15:30 34164 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38739   35700 Sl      03:15:30 11844 xfwm4 --compositor=off
  38741   38739 S       03:15:30  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:7.log -- /usr/local/bin/box-xfwm4 --compositor=off
  38745   38741 S       03:15:30  1896 flock -n /tmp/xfwm4:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38754   38745 Sl      03:15:30 34308 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38783   35700 S       03:15:30  4868 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38786   38783 S       03:15:30  1952 bash /usr/local/bin/box-bounded-log --run /tmp/picom:7.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38787   38786 S       03:15:30  1836 flock -n /tmp/picom:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38792   38787 Sl      03:15:30 34184 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38862      53 Sl      03:15:30  3564 /usr/libexec/dconf-service
  39132      53 Ssl     03:15:30 60244 plank --name dock1
  39135   39132 S       03:15:30  2004 bash /usr/local/bin/box-bounded-log --run /tmp/plank:7-dock1.log -- /usr/local/bin/box-plank --name dock1
  39139   39135 S       03:15:30  1940 flock -n /tmp/plank:7-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39143   39139 Sl      03:15:30 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39194   35700 S       03:15:30  1940 tail -f /dev/null
  39490      53 S       03:15:29  3460 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  39496   39490 Sl      03:15:29  8724 /usr/libexec/bamf/bamfdaemon
  40253      53 Ss      03:15:27  4240 bash /usr/local/bin/start-desktop.sh
  40257   40253 S       03:15:27  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-10/start-desktop.log -- /usr/local/bin/start-desktop.sh
  40258   40257 S       03:15:27  1820 flock -n /tmp/sand-window-10/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40259   40258 Sl      03:15:27 34244 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40298      53 Ss      03:15:27  2168 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  40303   40253 S       03:15:27 52220 Xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40309   40303 S       03:15:27  2088 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:10.log -- /usr/local/bin/box-xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40310   40309 S       03:15:27  1932 flock -n /tmp/xvfb:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  40313   40310 Sl      03:15:27 34096 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  43282   40303 Z       03:15:24     0 [bash] <defunct>
  43326      53 Ssl     03:15:24 92156 /exec-daemon/node /exec-daemon/index.js serve --port 14010 --pty-websocket-port 13610 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  43338   40253 S       03:15:24 28984 x11vnc -skip_lockkeys -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43339   43338 S       03:15:24  2008 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:10.log -- /usr/local/bin/box-x11vnc -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43340   43339 S       03:15:24  1944 flock -n /tmp/x11vnc:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43345   43340 Sl      03:15:24 33948 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43363   40253 Sl      03:15:24 11860 xfwm4 --compositor=off
  43368   43363 S       03:15:24  2000 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:10.log -- /usr/local/bin/box-xfwm4 --compositor=off
  43370   43368 S       03:15:24  1932 flock -n /tmp/xfwm4:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43379   43370 Sl      03:15:24 34188 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43406   40253 S       03:15:24  4892 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43417   43406 S       03:15:24  2004 bash /usr/local/bin/box-bounded-log --run /tmp/picom:10.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43420   43417 S       03:15:24  1828 flock -n /tmp/picom:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43421   43420 Sl      03:15:24 34240 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43451      53 Sl      03:15:24  3488 /usr/libexec/dconf-service
  43842   40253 S       03:15:24  1880 tail -f /dev/null
  43954   27182 Ssl     03:15:24 60260 plank --name dock1
  43957   43954 S       03:15:24  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:10-dock1.log -- /usr/local/bin/box-plank --name dock1
  43962   43957 S       03:15:24  1900 cat
  44192      53 S       03:15:24  3428 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  44194   44192 Sl      03:15:24  8760 /usr/libexec/bamf/bamfdaemon
  45490      53 Ss      03:15:14  4312 bash /usr/local/bin/start-desktop.sh
  45496   45490 S       03:15:14  2044 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-11/start-desktop.log -- /usr/local/bin/start-desktop.sh
  45497   45496 S       03:15:14  1924 flock -n /tmp/sand-window-11/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45499   45497 Sl      03:15:14 34092 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45547      53 Ss      03:15:14  2164 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  45552   45490 S       03:15:14 52280 Xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45557   45552 S       03:15:14  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:11.log -- /usr/local/bin/box-xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45558   45557 S       03:15:14  1936 flock -n /tmp/xvfb:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  45559   45558 Sl      03:15:14 34128 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  49144   45552 Z       03:15:12     0 [bash] <defunct>
  49154      53 Ssl     03:15:12 92184 /exec-daemon/node /exec-daemon/index.js serve --port 14011 --pty-websocket-port 13611 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  49212   45490 S       03:15:11 28972 x11vnc -skip_lockkeys -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49217   49212 S       03:15:11  2052 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:11.log -- /usr/local/bin/box-x11vnc -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49219   49217 S       03:15:11  1916 flock -n /tmp/x11vnc:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49220   49219 Sl      03:15:11 34172 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49246   45490 Sl      03:15:11 11744 xfwm4 --compositor=off
  49251   49246 S       03:15:11  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:11.log -- /usr/local/bin/box-xfwm4 --compositor=off
  49252   49251 S       03:15:11  1824 flock -n /tmp/xfwm4:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49254   49252 Sl      03:15:11 34268 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49294   45490 S       03:15:11  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49301   49294 S       03:15:11  1872 bash /usr/local/bin/box-bounded-log --run /tmp/picom:11.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49302   49301 S       03:15:11  1832 flock -n /tmp/picom:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49309   49302 Sl      03:15:11 34212 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49348      53 Sl      03:15:11  3604 /usr/libexec/dconf-service
  49610      53 Ssl     03:15:11 60448 plank --name dock1
  49625   49610 S       03:15:11  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:11-dock1.log -- /usr/local/bin/box-plank --name dock1
  49628   49625 S       03:15:11  1832 flock -n /tmp/plank:11-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49632   49628 Sl      03:15:11 34044 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49668   45490 S       03:15:11  1884 tail -f /dev/null
  50219      53 S       03:15:11  3548 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  50221   50219 Sl      03:15:11  8816 /usr/libexec/bamf/bamfdaemon
  68159      53 Ss      03:14:42  4344 bash /usr/local/bin/start-desktop.sh
  68162   68159 S       03:14:42  2032 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-13/start-desktop.log -- /usr/local/bin/start-desktop.sh
  68164   68162 S       03:14:42  1948 flock -n /tmp/sand-window-13/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68165   68164 Sl      03:14:42 34764 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68204      53 Ss      03:14:42  2236 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  68209   68159 S       03:14:42 52280 Xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68214   68209 S       03:14:42  1956 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:13.log -- /usr/local/bin/box-xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68215   68214 S       03:14:42  1876 flock -n /tmp/xvfb:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  68217   68215 Sl      03:14:42 34884 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  71849   68209 Z       03:14:40     0 [bash] <defunct>
  71893      53 Ssl     03:14:39 102152 /exec-daemon/node /exec-daemon/index.js serve --port 14013 --pty-websocket-port 13613 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  71905   68159 S       03:14:39 29012 x11vnc -skip_lockkeys -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71910   71905 S       03:14:39  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:13.log -- /usr/local/bin/box-x11vnc -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71912   71910 S       03:14:39  1864 flock -n /tmp/x11vnc:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71913   71912 Sl      03:14:39 34920 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71930   68159 Sl      03:14:39 13248 xfwm4 --compositor=off
  71935   71930 S       03:14:39  1876 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:13.log -- /usr/local/bin/box-xfwm4 --compositor=off
  71936   71935 S       03:14:39  1888 flock -n /tmp/xfwm4:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71938   71936 Sl      03:14:39 34828 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71971   68159 S       03:14:39  4880 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71982   71971 S       03:14:39  1940 bash /usr/local/bin/box-bounded-log --run /tmp/picom:13.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71983   71982 S       03:14:39  1864 flock -n /tmp/picom:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  71985   71983 Sl      03:14:39 34868 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  72033      53 Sl      03:14:39  3528 /usr/libexec/dconf-service
  72327      53 Ssl     03:14:39 61140 plank --name dock1
  72341   72327 S       03:14:39  1872 bash /usr/local/bin/box-bounded-log --run /tmp/plank:13-dock1.log -- /usr/local/bin/box-plank --name dock1
  72345   72341 S       03:14:39  1940 flock -n /tmp/plank:13-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72349   72345 Sl      03:14:39 34960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72391   68159 S       03:14:39  1944 tail -f /dev/null
  72844      53 S       03:14:39  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  72847   72844 Sl      03:14:39  9460 /usr/libexec/bamf/bamfdaemon
  80415   26442 Sl      03:13:00 170492 python3 -X utf8 server.py
  94319       1 S       03:07:51  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94322   94319 Ssl     03:07:51 140992 python3 scripts/acquire/remaining_after_stk_surv.py
  94401       1 S       03:07:49  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94403   94401 Ss      03:07:49 35780 python3 scripts/acquire/relay_outage_backfill.py
 212762   94403 S       02:01:53 14224 python3 scripts/nightly_update.py --date 20261016 --steps sw
 212763  212762 Sl      02:01:53 154516 /usr/bin/python3 scripts/acquire/sw_pit_refresh.py
 337724    9604 Ss      01:04:48  4068 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1" < /dev/null; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
 337733  337724 S       01:04:48 19444 python3 -
 437040       1 S          15:00  3520 /bin/bash /tmp/swterm/run.sh
 440937   80415 ZN         10:28     0 [python3] <defunct>
 443569   26454 S          05:50  1960 sleep 600
 445709   26450 S          02:00  2016 sleep 300
 446533   27183 S          00:01  1896 sleep 5
 446542     324 S          00:00  2004 sleep 2
 446545     323 S          00:00  2008 sleep 2
 446549  437040 R          00:00  4744 ps -eo pid,ppid,stat,etime,rss,cmd
212762 etime=   02:01:53 lstart=Sun Oct 18 02:28:20 2026
pinned before: 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c  data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet mtime=2026-10-18 01:08:43.180683904 -0400 2026-10-18 04:30:14.550 EDT
SIGSTOP 94403 sent 2026-10-18 04:30:14.551 EDT
94403 state=T 2026-10-18 04:30:15.556 EDT
SIGTERM 212763 sent 2026-10-18 04:30:15.557 EDT
212763 exited 2026-10-18 04:30:16.561 EDT
SIGTERM 212762 sent 2026-10-18 04:30:21.571 EDT
212762 STILL ALIVE after 30s 2026-10-18 04:30:51.626 EDT state=Z
### ps snapshot 2026-10-18 04:30:51.630 EDT
    PID    PPID STAT     ELAPSED   RSS CMD
      1       0 Ss      03:25:08   752 /tini -- /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
      7       1 Sl      03:25:08  7640 /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
     53       7 Ss      03:25:08 14736 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
    204      53 S       03:25:08 32564 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    209     204 S       03:25:08  2028 bash /usr/local/bin/box-bounded-log --run /tmp/novnc-forks.log -- /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    210     209 S       03:25:08  1780 flock -n /tmp/novnc-forks.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    211     210 Sl      03:25:08 34020 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    227      53 Ssl     03:25:08 48524 /exec-daemon/node /usr/local/bin/sand-window-router.mjs 1339 1337 14000
    247      53 Ssl     03:25:08 48836 /exec-daemon/node /usr/local/bin/sand-session-sync.mjs
    248      53 Sl      03:25:08 99392 /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    257     248 S       03:25:08  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-web-bot-auth.log -- /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    258     257 S       03:25:08  1896 flock -n /tmp/sand-web-bot-auth.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    259     258 Sl      03:25:08 32612 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    277      53 Sl      03:25:08 71676 /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    284     277 S       03:25:08  2016 bash /usr/local/bin/box-bounded-log --run /tmp/sand-ua-governor.log -- /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    286     284 S       03:25:08  1884 flock -n /tmp/sand-ua-governor.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    290     286 Sl      03:25:08 32988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    322      53 Ssl     03:25:08 49900 /exec-daemon/node /usr/local/bin/sand-cookie-persist.mjs
    323      53 S       03:25:08  4276 bash /usr/local/bin/supervise-exec-daemon 1337 /usr/local/bin/start-exec-daemon
    324      53 S       03:25:08  4084 bash /usr/local/bin/supervise-egress-tunnel 8790 /usr/local/bin/start-egress-tunnel
    369     323 Ss      03:25:08  3424 bash /usr/local/bin/start-exec-daemon
    372     324 Ssl     03:25:08  2508 /usr/local/bin/sand-egress-tunnel server
    376     369 Sl      03:25:08 91660 /exec-daemon/node /exec-daemon/index.js serve --port 1337 --pty-websocket-port 1338 --auth-token local --rg-path /exec-daemon/rg --pty-auth-token local-pty --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
    720       1 Ss      03:24:58  4316 bash /usr/local/bin/start-desktop.sh
    724     720 S       03:24:58  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-2/start-desktop.log -- /usr/local/bin/start-desktop.sh
    725     724 S       03:24:58  1792 flock -n /tmp/sand-window-2/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    726     725 Sl      03:24:58 34316 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    766       1 Ss      03:24:58  2036 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
    771     720 S       03:24:58 64044 Xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    776     771 S       03:24:58  1904 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:2.log -- /usr/local/bin/box-xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    778     776 S       03:24:58  1864 flock -n /tmp/xvfb:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
    779     778 Sl      03:24:58 33344 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
   1153     771 Z       03:24:58     0 [bash] <defunct>
   1201       1 Ssl     03:24:57 68900 /exec-daemon/node /exec-daemon/index.js serve --port 14002 --pty-websocket-port 13602 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   1277     720 Sl      03:24:57 26088 xfwm4 --compositor=off
   1282    1277 S       03:24:57  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:2.log -- /usr/local/bin/box-xfwm4 --compositor=off
   1283    1282 S       03:24:57  1784 flock -n /tmp/xfwm4:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1285    1283 Sl      03:24:57 33180 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1316     720 S       03:24:57  4080 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1325    1316 S       03:24:57  1984 bash /usr/local/bin/box-bounded-log --run /tmp/picom:2.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1326    1325 S       03:24:57  1792 flock -n /tmp/picom:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1329    1326 Sl      03:24:57 33040 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1380       1 Sl      03:24:57  3476 /usr/libexec/dconf-service
   1536       1 Ssl     03:24:57 21152 plank --name dock1
   1543    1536 S       03:24:57  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:2-dock1.log -- /usr/local/bin/box-plank --name dock1
   1544    1543 S       03:24:57  1828 flock -n /tmp/plank:2-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1546    1544 Sl      03:24:57 33052 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1559     720 S       03:24:57  1872 tail -f /dev/null
   1618       1 S       03:24:57  3364 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   1619    1618 Sl      03:24:57  7168 /usr/libexec/bamf/bamfdaemon
   5268       1 Ss      03:22:25  4308 bash /usr/local/bin/start-desktop.sh
   5271    5268 S       03:22:25  1928 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-12/start-desktop.log -- /usr/local/bin/start-desktop.sh
   5273    5271 S       03:22:25  1844 flock -n /tmp/sand-window-12/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5274    5273 Sl      03:22:25 34184 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5313       1 Ss      03:22:25  2100 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   5318    5268 S       03:22:25 60404 Xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5323    5318 S       03:22:25  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:12.log -- /usr/local/bin/box-xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5324    5323 S       03:22:25  1904 flock -n /tmp/xvfb:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   5326    5324 Sl      03:22:25 33956 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   6227    5318 Z       03:22:24     0 [bash] <defunct>
   6247       1 Ssl     03:22:24 96196 /exec-daemon/node /exec-daemon/index.js serve --port 14012 --pty-websocket-port 13612 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   6295    5268 S       03:22:23 28912 x11vnc -skip_lockkeys -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6300    6295 S       03:22:23  2012 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:12.log -- /usr/local/bin/box-x11vnc -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6301    6300 S       03:22:23  1848 flock -n /tmp/x11vnc:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6302    6301 Sl      03:22:23 33832 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6325    5268 Sl      03:22:23 57632 xfwm4 --compositor=off
   6333    6325 S       03:22:23  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:12.log -- /usr/local/bin/box-xfwm4 --compositor=off
   6335    6333 S       03:22:23  1928 flock -n /tmp/xfwm4:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6336    6335 Sl      03:22:23 33988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6368    5268 S       03:22:23  4776 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6375    6368 S       03:22:23  2036 bash /usr/local/bin/box-bounded-log --run /tmp/picom:12.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6376    6375 S       03:22:23  1796 flock -n /tmp/picom:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6380    6376 Sl      03:22:23 33908 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6450       1 Sl      03:22:23  3432 /usr/libexec/dconf-service
   6654       1 Ssl     03:22:23 59200 plank --name dock1
   6662    6654 S       03:22:23  2056 bash /usr/local/bin/box-bounded-log --run /tmp/plank:12-dock1.log -- /usr/local/bin/box-plank --name dock1
   6665    6662 S       03:22:23  1876 flock -n /tmp/plank:12-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6668    6665 Sl      03:22:23 33984 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6697    5268 S       03:22:23  1896 tail -f /dev/null
   6834       1 S       03:22:23  3468 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   6835    6834 Sl      03:22:23  8616 /usr/libexec/bamf/bamfdaemon
   8307       1 Ss      03:21:02  4300 bash /usr/local/bin/start-desktop.sh
   8311    8307 S       03:21:02  2072 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-6/start-desktop.log -- /usr/local/bin/start-desktop.sh
   8312    8311 S       03:21:02  1896 flock -n /tmp/sand-window-6/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8313    8312 Sl      03:21:02 34012 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8352       1 Ss      03:21:02  2148 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   8357    8307 S       03:21:02 60424 Xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8363    8357 S       03:21:02  1992 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:6.log -- /usr/local/bin/box-xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8364    8363 S       03:21:02  1860 flock -n /tmp/xvfb:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   8366    8364 Sl      03:21:02 34252 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   9579    8357 Z       03:21:01     0 [bash] <defunct>
   9604       1 Ssl     03:21:01 125944 /exec-daemon/node /exec-daemon/index.js serve --port 14006 --pty-websocket-port 13606 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   9653    8307 S       03:21:01 28992 x11vnc -skip_lockkeys -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9658    9653 S       03:21:01  2076 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:6.log -- /usr/local/bin/box-x11vnc -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9659    9658 S       03:21:01  1796 flock -n /tmp/x11vnc:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9661    9659 Sl      03:21:01 33932 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9679    8307 Sl      03:21:01 11392 xfwm4 --compositor=off
   9684    9679 S       03:21:01  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:6.log -- /usr/local/bin/box-xfwm4 --compositor=off
   9685    9684 S       03:21:01  1860 flock -n /tmp/xfwm4:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9692    9685 Sl      03:21:01 34276 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9730    8307 S       03:21:01  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9738    9730 S       03:21:01  2072 bash /usr/local/bin/box-bounded-log --run /tmp/picom:6.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9741    9738 S       03:21:01  1904 flock -n /tmp/picom:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9743    9741 Sl      03:21:01 34180 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9795       1 Sl      03:21:01  3336 /usr/libexec/dconf-service
  10084       1 Ssl     03:21:01 59472 plank --name dock1
  10095   10084 S       03:21:01  2020 bash /usr/local/bin/box-bounded-log --run /tmp/plank:6-dock1.log -- /usr/local/bin/box-plank --name dock1
  10096   10095 S       03:21:01  1848 flock -n /tmp/plank:6-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10100   10096 Sl      03:21:01 33960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10125    8307 S       03:21:01  1888 tail -f /dev/null
  10284       1 S       03:21:01  3436 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  10287   10284 Sl      03:21:01  8556 /usr/libexec/bamf/bamfdaemon
  11187       1 Ss      03:20:31  4368 bash /usr/local/bin/start-desktop.sh
  11191   11187 S       03:20:31  2056 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-8/start-desktop.log -- /usr/local/bin/start-desktop.sh
  11192   11191 S       03:20:31  1832 flock -n /tmp/sand-window-8/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11193   11192 Sl      03:20:31 34096 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11232       1 Ss      03:20:31  2160 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  11237   11187 S       03:20:31 61208 Xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11242   11237 S       03:20:31  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:8.log -- /usr/local/bin/box-xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11243   11242 S       03:20:31  1868 flock -n /tmp/xvfb:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  11245   11243 Sl      03:20:31 33972 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  12725   11237 Z       03:20:30     0 [bash] <defunct>
  12735       1 Ssl     03:20:30 89316 /exec-daemon/node /exec-daemon/index.js serve --port 14008 --pty-websocket-port 13608 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  12790   11187 S       03:20:30 29100 x11vnc -skip_lockkeys -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12797   12790 S       03:20:30  1972 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:8.log -- /usr/local/bin/box-x11vnc -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12798   12797 S       03:20:30  1944 flock -n /tmp/x11vnc:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12800   12798 Sl      03:20:30 34032 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12819   11187 Sl      03:20:30 11396 xfwm4 --compositor=off
  12824   12819 S       03:20:30  2044 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:8.log -- /usr/local/bin/box-xfwm4 --compositor=off
  12825   12824 S       03:20:30  1828 flock -n /tmp/xfwm4:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12826   12825 Sl      03:20:30 34084 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12882   11187 S       03:20:30  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12891   12882 S       03:20:30  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:8.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12892   12891 S       03:20:30  1824 flock -n /tmp/picom:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12896   12892 Sl      03:20:30 33904 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12929       1 Sl      03:20:30  3616 /usr/libexec/dconf-service
  13167       1 Ssl     03:20:30 59724 plank --name dock1
  13178   13167 S       03:20:30  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:8-dock1.log -- /usr/local/bin/box-plank --name dock1
  13179   13178 S       03:20:30  1868 flock -n /tmp/plank:8-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13180   13179 Sl      03:20:30 33988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13209   11187 S       03:20:30  1968 tail -f /dev/null
  13486       1 S       03:20:29  3444 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  13489   13486 Sl      03:20:29  8748 /usr/libexec/bamf/bamfdaemon
  14353       1 Ss      03:20:13  4228 bash /usr/local/bin/start-desktop.sh
  14356   14353 S       03:20:13  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-5/start-desktop.log -- /usr/local/bin/start-desktop.sh
  14358   14356 S       03:20:13  1824 flock -n /tmp/sand-window-5/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14359   14358 Sl      03:20:13 33876 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14398       1 Ss      03:20:13  2192 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  14403   14353 S       03:20:13 61084 Xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14408   14403 S       03:20:13  1928 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:5.log -- /usr/local/bin/box-xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14409   14408 S       03:20:13  1924 flock -n /tmp/xvfb:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  14411   14409 Sl      03:20:13 33972 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  16166   14403 Z       03:20:12     0 [bash] <defunct>
  16176       1 Ssl     03:20:12 96040 /exec-daemon/node /exec-daemon/index.js serve --port 14005 --pty-websocket-port 13605 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  16236   14353 S       03:20:11 29000 x11vnc -skip_lockkeys -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16242   16236 S       03:20:11  2040 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:5.log -- /usr/local/bin/box-x11vnc -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16243   16242 S       03:20:11  1932 flock -n /tmp/x11vnc:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16246   16243 Sl      03:20:11 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16263   14353 Sl      03:20:11 11432 xfwm4 --compositor=off
  16268   16263 S       03:20:11  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:5.log -- /usr/local/bin/box-xfwm4 --compositor=off
  16269   16268 S       03:20:11  1848 flock -n /tmp/xfwm4:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16271   16269 Sl      03:20:11 34296 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16311   14353 S       03:20:11  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16316   16311 S       03:20:11  2048 bash /usr/local/bin/box-bounded-log --run /tmp/picom:5.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16318   16316 S       03:20:11  1944 flock -n /tmp/picom:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16321   16318 Sl      03:20:11 34252 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16362       1 Sl      03:20:11  3336 /usr/libexec/dconf-service
  16645       1 Ssl     03:20:11 59744 plank --name dock1
  16656   16645 S       03:20:11  2012 bash /usr/local/bin/box-bounded-log --run /tmp/plank:5-dock1.log -- /usr/local/bin/box-plank --name dock1
  16657   16656 S       03:20:11  1900 flock -n /tmp/plank:5-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16661   16657 Sl      03:20:11 33932 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16690   14353 S       03:20:11  1916 tail -f /dev/null
  16944       1 S       03:20:11  3384 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  16947   16944 Sl      03:20:11  8804 /usr/libexec/bamf/bamfdaemon
  18167       1 Ss      03:19:34  4288 bash /usr/local/bin/start-desktop.sh
  18171   18167 S       03:19:34  2004 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-4/start-desktop.log -- /usr/local/bin/start-desktop.sh
  18172   18171 S       03:19:34  1868 flock -n /tmp/sand-window-4/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18173   18172 Sl      03:19:34 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18212       1 Ss      03:19:34  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  18217   18167 S       03:19:34 61228 Xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18222   18217 S       03:19:34  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:4.log -- /usr/local/bin/box-xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18224   18222 S       03:19:34  1840 flock -n /tmp/xvfb:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  18225   18224 Sl      03:19:34 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  20160   18217 Z       03:19:33     0 [bash] <defunct>
  20188       1 Ssl     03:19:33 92100 /exec-daemon/node /exec-daemon/index.js serve --port 14004 --pty-websocket-port 13604 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  20233   18167 S       03:19:33 29044 x11vnc -skip_lockkeys -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20238   20233 S       03:19:33  2056 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:4.log -- /usr/local/bin/box-x11vnc -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20241   20238 S       03:19:33  1876 flock -n /tmp/x11vnc:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20242   20241 Sl      03:19:33 34372 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20261   18167 Sl      03:19:33 11764 xfwm4 --compositor=off
  20266   20261 S       03:19:33  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:4.log -- /usr/local/bin/box-xfwm4 --compositor=off
  20267   20266 S       03:19:33  1924 flock -n /tmp/xfwm4:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20269   20267 Sl      03:19:33 34280 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20316   18167 S       03:19:33  4916 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20323   20316 S       03:19:33  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:4.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20324   20323 S       03:19:33  1828 flock -n /tmp/picom:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20328   20324 Sl      03:19:33 33960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20372       1 Sl      03:19:33  3488 /usr/libexec/dconf-service
  20653       1 Ssl     03:19:33 60444 plank --name dock1
  20665   20653 S       03:19:33  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:4-dock1.log -- /usr/local/bin/box-plank --name dock1
  20667   20665 S       03:19:33  1932 flock -n /tmp/plank:4-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20671   20667 Sl      03:19:33 33996 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20713   18167 S       03:19:33  1964 tail -f /dev/null
  20976       1 S       03:19:32  3456 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  20979   20976 Sl      03:19:32  8696 /usr/libexec/bamf/bamfdaemon
  26442       1 Ss      03:16:27  3524 /bin/bash ./supervise.sh
  26447       1 Ss      03:16:27  3404 /bin/bash ./deploy_supervise.sh
  26450   26447 S       03:16:27  3468 /bin/bash ./deploy_loop.sh
  26454       1 Ss      03:16:27  3432 ql_keepalive_loop -c while true; do sleep 600; /workspace/quantlab-web/start_all.sh --from-keepalive; done
  26581       1 Ssl     03:16:26 40084 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/cli/index.js serve --port 6768 --pairing-address grok-bot
  26627   26581 Sl      03:16:26 150484 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --user-data-dir=/home/box/.config/orca --serve --serve-port 6768 --serve-pairing-address grok-bot
  26630   26627 S       03:16:26 18112 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote --no-zygote-sandbox
  26631   26627 S       03:16:26 18084 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26633   26631 S       03:16:26 10788 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26702       1 Sl      03:16:25  3572 /home/box/.orca/app-1.4.224-20261018051422/chrome_crashpad_handler --monitor-self-annotation=ptype=crashpad-handler --no-rate-limit --no-upload-gzip --database=/home/box/.config/orca/Crashpad --annotation=_productName=orca --annotation=_version=1.4.224 --annotation=lsb-release=Debian GNU/Linux 13 (trixie) --annotation=plat=Linux --annotation=prod=Electron --annotation=ver=43.7.5 --initial-client-fd=41 --shared-client-connection
  26752   26630 Sl      03:16:25 23232 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=gpu-process --disable-dev-shm-usage --ozone-platform=x11 --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --gpu-preferences=WAAAAAAAAAAgAQAEAAAAAAAAAAAAAGAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAABAAAAAAAAAAgAAAAAAAAACAAAAAAAAAAIAAAAAAAAAA== --use-gl=disabled --shared-files --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708988185955192
  26756   26752 S       03:16:25 12136 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=broker
  26762   26627 Sl      03:16:25 24784 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=utility --utility-sub-type=network.mojom.NetworkService --lang=en-US --service-sandbox-type=none --disable-dev-shm-usage --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --standard-schemes=orca-preview,orca-media --secure-schemes=orca-preview,orca-media --cors-schemes=orca-preview --fetch-schemes=orca-preview --streaming-schemes=orca-preview,orca-media --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708989122997041
  26800   26627 Ssl     03:16:25 41724 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --socket /home/box/.config/orca/daemon/daemon-v43.sock --token /home/box/.config/orca/daemon/daemon-v43.token --pid-record /home/box/.config/orca/daemon/daemon-v43.pid --launch-nonce 9f1cf877-a9c1-4595-b95d-e8ac301fed85 --entry-path /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --app-version 1.4.224 --spawner-exec-path /home/box/.orca/app-1.4.224-20261018051422/orca-ide --log-file /home/box/.config/orca/logs/daemon.log
  27167      53 Ss      03:16:22  3748 bash /usr/local/bin/supervise-sand-supervisor /tmp/sand-supervisor/status.json /tmp/sand-supervisor.log /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27182   27167 Ssl     03:16:22 65800 /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27183   27167 Ss      03:16:22  3428 bash -c while sleep "$1"; do kill -USR1 "$2" 2>/dev/null || exit 0; done ticker 5 27167
  27186      53 S       03:16:22  4328 bash /usr/local/bin/start-desktop.sh
  27191   27186 S       03:16:22  1992 bash /usr/local/bin/box-bounded-log --run /tmp/start-desktop.log -- /usr/local/bin/start-desktop.sh
  27192   27191 S       03:16:22  1824 flock -n /tmp/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27194   27192 Sl      03:16:22 34156 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27245       1 Ss      03:16:22  2232 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  27250   27186 S       03:16:22 61116 Xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27255   27250 S       03:16:22  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:1.log -- /usr/local/bin/box-xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27256   27255 S       03:16:22  1864 flock -n /tmp/xvfb:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27258   27256 Sl      03:16:22 34500 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27263   27250 Z       03:16:22     0 [bash] <defunct>
  27313   27182 Ssl     03:16:22 600068 /exec-daemon/node --disable-warning=ExperimentalWarning /opt/sand/sand-host/host-main.cjs
  27366      53 Ss      03:16:22 24188 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
  27383      53 S       03:16:22  2592 /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27385   27383 S       03:16:22  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-orbitd.log -- env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27386   27385 S       03:16:22  1944 flock -n /tmp/sand-orbitd.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27389   27386 Sl      03:16:22 34396 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27390   27383 S       03:16:22  8104 /usr/local/libexec/sand/sand-daemon-supervisor __supervise orbitd
  27398   27186 S       03:16:22 20080 x11vnc -skip_lockkeys -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27403   27398 S       03:16:22  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:1.log -- /usr/local/bin/box-x11vnc -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27404   27403 S       03:16:22  1832 flock -n /tmp/x11vnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27405   27404 Sl      03:16:22 34220 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27427   27186 S       03:16:22 35112 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27432   27427 S       03:16:22  2020 bash /usr/local/bin/box-bounded-log --run /tmp/novnc:1.log -- websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27433   27432 S       03:16:22  1836 flock -n /tmp/novnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27434   27433 Sl      03:16:22 34484 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27453   27186 Sl      03:16:22 11748 xfwm4 --compositor=off
  27458   27453 S       03:16:22  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:1.log -- /usr/local/bin/box-xfwm4 --compositor=off
  27462   27458 S       03:16:22  1880 flock -n /tmp/xfwm4:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27466   27462 Sl      03:16:22 34148 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27505   27186 S       03:16:22  4860 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27510   27505 S       03:16:22  1992 bash /usr/local/bin/box-bounded-log --run /tmp/picom:1.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27512   27510 S       03:16:22  1880 flock -n /tmp/picom:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27513   27512 Sl      03:16:22 34128 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27574       1 Sl      03:16:22  3560 /usr/libexec/dconf-service
  27953      53 Ssl     03:16:22 60176 plank --name dock1
  27967   27953 S       03:16:22  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:1-dock1.log -- /usr/local/bin/box-plank --name dock1
  27969   27967 S       03:16:22  1820 flock -n /tmp/plank:1-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  27974   27969 Sl      03:16:22 33916 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  28014   27186 S       03:16:22  1948 tail -f /dev/null
  28485       1 S       03:16:22  3376 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  28490   28485 Sl      03:16:22  8700 /usr/libexec/bamf/bamfdaemon
  29120   27390 Sl      03:16:21  5244 /var/lib/sand-daemon-supervisor/orbitd/releases/28b0833c5707e1c919cee4d4ab5a8ad0eeac9c46/orbitd
  29240   27313 Sl      03:16:21 200620 /opt/sand/sand-host/extensions/codebase-telemetry/csnaps
  29910      53 Ss      03:16:17  4428 bash /usr/local/bin/start-desktop.sh
  29915   29910 S       03:16:17  1980 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-3/start-desktop.log -- /usr/local/bin/start-desktop.sh
  29916   29915 S       03:16:17  1824 flock -n /tmp/sand-window-3/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  29917   29916 Sl      03:16:17 34200 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  30000      53 Ss      03:16:17  2272 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  30031   29910 S       03:16:17 52252 Xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30036   30031 S       03:16:17  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:3.log -- /usr/local/bin/box-xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30037   30036 S       03:16:17  1824 flock -n /tmp/xvfb:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30039   30037 Sl      03:16:17 34084 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30381   27182 Ss      03:16:17 20056 x11vnc -skip_lockkeys -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30384   30381 S       03:16:17  2028 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:2.log -- /usr/local/bin/box-x11vnc -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30385   30384 S       03:16:17  1932 flock -n /tmp/x11vnc:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  30386   30385 Sl      03:16:17 35400 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  33709   30031 Z       03:16:15     0 [bash] <defunct>
  33760      53 Ssl     03:16:14 96228 /exec-daemon/node /exec-daemon/index.js serve --port 14003 --pty-websocket-port 13603 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  33788   29910 S       03:16:14 29036 x11vnc -skip_lockkeys -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33790   33788 S       03:16:14  2024 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:3.log -- /usr/local/bin/box-x11vnc -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33791   33790 S       03:16:14  1840 flock -n /tmp/x11vnc:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33792   33791 Sl      03:16:14 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33824   29910 Sl      03:16:14 11788 xfwm4 --compositor=off
  33827   33824 S       03:16:14  2076 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:3.log -- /usr/local/bin/box-xfwm4 --compositor=off
  33832   33827 S       03:16:14  1824 flock -n /tmp/xfwm4:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33834   33832 Sl      03:16:14 34284 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33861   29910 S       03:16:14  4876 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33871   33861 S       03:16:14  2024 bash /usr/local/bin/box-bounded-log --run /tmp/picom:3.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33872   33871 S       03:16:14  1896 flock -n /tmp/picom:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33877   33872 Sl      03:16:14 34140 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33940      53 Sl      03:16:14  3492 /usr/libexec/dconf-service
  34299      53 Ssl     03:16:14 60100 plank --name dock1
  34308   34299 S       03:16:14  2052 bash /usr/local/bin/box-bounded-log --run /tmp/plank:3-dock1.log -- /usr/local/bin/box-plank --name dock1
  34317   34308 S       03:16:14  1824 flock -n /tmp/plank:3-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34330   34317 Sl      03:16:14 34072 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34358   29910 S       03:16:14  1900 tail -f /dev/null
  34507      53 S       03:16:14  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  34509   34507 Sl      03:16:14  8908 /usr/libexec/bamf/bamfdaemon
  35700      53 Ss      03:16:09  4332 bash /usr/local/bin/start-desktop.sh
  35703   35700 S       03:16:09  1996 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-7/start-desktop.log -- /usr/local/bin/start-desktop.sh
  35704   35703 S       03:16:09  1924 flock -n /tmp/sand-window-7/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35705   35704 Sl      03:16:09 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35755      53 Ss      03:16:09  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  35760   35700 S       03:16:09 52176 Xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35765   35760 S       03:16:09  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:7.log -- /usr/local/bin/box-xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35766   35765 S       03:16:09  1868 flock -n /tmp/xvfb:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  35767   35766 Sl      03:16:09 34044 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  38646   35760 Z       03:16:07     0 [bash] <defunct>
  38695      53 Ssl     03:16:07 92264 /exec-daemon/node /exec-daemon/index.js serve --port 14007 --pty-websocket-port 13607 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  38714   35700 S       03:16:07 29116 x11vnc -skip_lockkeys -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38716   38714 S       03:16:07  1976 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:7.log -- /usr/local/bin/box-x11vnc -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38720   38716 S       03:16:07  1916 flock -n /tmp/x11vnc:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38723   38720 Sl      03:16:07 34164 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38739   35700 Sl      03:16:07 11844 xfwm4 --compositor=off
  38741   38739 S       03:16:07  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:7.log -- /usr/local/bin/box-xfwm4 --compositor=off
  38745   38741 S       03:16:07  1896 flock -n /tmp/xfwm4:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38754   38745 Sl      03:16:07 34308 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38783   35700 S       03:16:07  4868 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38786   38783 S       03:16:07  1952 bash /usr/local/bin/box-bounded-log --run /tmp/picom:7.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38787   38786 S       03:16:07  1836 flock -n /tmp/picom:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38792   38787 Sl      03:16:07 34184 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38862      53 Sl      03:16:07  3564 /usr/libexec/dconf-service
  39132      53 Ssl     03:16:07 60244 plank --name dock1
  39135   39132 S       03:16:07  2004 bash /usr/local/bin/box-bounded-log --run /tmp/plank:7-dock1.log -- /usr/local/bin/box-plank --name dock1
  39139   39135 S       03:16:07  1940 flock -n /tmp/plank:7-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39143   39139 Sl      03:16:07 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39194   35700 S       03:16:07  1940 tail -f /dev/null
  39490      53 S       03:16:06  3460 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  39496   39490 Sl      03:16:06  8724 /usr/libexec/bamf/bamfdaemon
  40253      53 Ss      03:16:04  4240 bash /usr/local/bin/start-desktop.sh
  40257   40253 S       03:16:04  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-10/start-desktop.log -- /usr/local/bin/start-desktop.sh
  40258   40257 S       03:16:04  1820 flock -n /tmp/sand-window-10/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40259   40258 Sl      03:16:04 34244 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40298      53 Ss      03:16:04  2168 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  40303   40253 S       03:16:04 52220 Xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40309   40303 S       03:16:04  2088 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:10.log -- /usr/local/bin/box-xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40310   40309 S       03:16:04  1932 flock -n /tmp/xvfb:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  40313   40310 Sl      03:16:04 34096 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  43282   40303 Z       03:16:02     0 [bash] <defunct>
  43326      53 Ssl     03:16:01 92156 /exec-daemon/node /exec-daemon/index.js serve --port 14010 --pty-websocket-port 13610 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  43338   40253 S       03:16:01 28984 x11vnc -skip_lockkeys -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43339   43338 S       03:16:01  2008 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:10.log -- /usr/local/bin/box-x11vnc -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43340   43339 S       03:16:01  1944 flock -n /tmp/x11vnc:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43345   43340 Sl      03:16:01 33948 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43363   40253 Sl      03:16:01 11860 xfwm4 --compositor=off
  43368   43363 S       03:16:01  2000 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:10.log -- /usr/local/bin/box-xfwm4 --compositor=off
  43370   43368 S       03:16:01  1932 flock -n /tmp/xfwm4:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43379   43370 Sl      03:16:01 34188 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43406   40253 S       03:16:01  4892 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43417   43406 S       03:16:01  2004 bash /usr/local/bin/box-bounded-log --run /tmp/picom:10.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43420   43417 S       03:16:01  1828 flock -n /tmp/picom:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43421   43420 Sl      03:16:01 34240 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43451      53 Sl      03:16:01  3488 /usr/libexec/dconf-service
  43842   40253 S       03:16:01  1880 tail -f /dev/null
  43954   27182 Ssl     03:16:01 60260 plank --name dock1
  43957   43954 S       03:16:01  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:10-dock1.log -- /usr/local/bin/box-plank --name dock1
  43962   43957 S       03:16:01  1900 cat
  44192      53 S       03:16:01  3428 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  44194   44192 Sl      03:16:01  8760 /usr/libexec/bamf/bamfdaemon
  45490      53 Ss      03:15:51  4312 bash /usr/local/bin/start-desktop.sh
  45496   45490 S       03:15:51  2044 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-11/start-desktop.log -- /usr/local/bin/start-desktop.sh
  45497   45496 S       03:15:51  1924 flock -n /tmp/sand-window-11/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45499   45497 Sl      03:15:51 34092 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45547      53 Ss      03:15:51  2164 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  45552   45490 S       03:15:51 52280 Xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45557   45552 S       03:15:51  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:11.log -- /usr/local/bin/box-xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45558   45557 S       03:15:51  1936 flock -n /tmp/xvfb:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  45559   45558 Sl      03:15:51 34128 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  49144   45552 Z       03:15:49     0 [bash] <defunct>
  49154      53 Ssl     03:15:49 92184 /exec-daemon/node /exec-daemon/index.js serve --port 14011 --pty-websocket-port 13611 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  49212   45490 S       03:15:48 28972 x11vnc -skip_lockkeys -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49217   49212 S       03:15:48  2052 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:11.log -- /usr/local/bin/box-x11vnc -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49219   49217 S       03:15:48  1916 flock -n /tmp/x11vnc:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49220   49219 Sl      03:15:48 34172 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49246   45490 Sl      03:15:48 11744 xfwm4 --compositor=off
  49251   49246 S       03:15:48  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:11.log -- /usr/local/bin/box-xfwm4 --compositor=off
  49252   49251 S       03:15:48  1824 flock -n /tmp/xfwm4:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49254   49252 Sl      03:15:48 34268 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49294   45490 S       03:15:48  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49301   49294 S       03:15:48  1872 bash /usr/local/bin/box-bounded-log --run /tmp/picom:11.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49302   49301 S       03:15:48  1832 flock -n /tmp/picom:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49309   49302 Sl      03:15:48 34212 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49348      53 Sl      03:15:48  3604 /usr/libexec/dconf-service
  49610      53 Ssl     03:15:48 60448 plank --name dock1
  49625   49610 S       03:15:48  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:11-dock1.log -- /usr/local/bin/box-plank --name dock1
  49628   49625 S       03:15:48  1832 flock -n /tmp/plank:11-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49632   49628 Sl      03:15:48 34044 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49668   45490 S       03:15:48  1884 tail -f /dev/null
  50219      53 S       03:15:48  3548 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  50221   50219 Sl      03:15:48  8816 /usr/libexec/bamf/bamfdaemon
  68159      53 Ss      03:15:19  4344 bash /usr/local/bin/start-desktop.sh
  68162   68159 S       03:15:19  2032 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-13/start-desktop.log -- /usr/local/bin/start-desktop.sh
  68164   68162 S       03:15:19  1948 flock -n /tmp/sand-window-13/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68165   68164 Sl      03:15:19 34764 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68204      53 Ss      03:15:19  2236 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  68209   68159 S       03:15:19 52280 Xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68214   68209 S       03:15:19  1956 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:13.log -- /usr/local/bin/box-xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68215   68214 S       03:15:19  1876 flock -n /tmp/xvfb:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  68217   68215 Sl      03:15:19 34884 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  71849   68209 Z       03:15:17     0 [bash] <defunct>
  71893      53 Ssl     03:15:17 102152 /exec-daemon/node /exec-daemon/index.js serve --port 14013 --pty-websocket-port 13613 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  71905   68159 S       03:15:16 29012 x11vnc -skip_lockkeys -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71910   71905 S       03:15:16  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:13.log -- /usr/local/bin/box-x11vnc -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71912   71910 S       03:15:16  1864 flock -n /tmp/x11vnc:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71913   71912 Sl      03:15:16 34920 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71930   68159 Sl      03:15:16 13248 xfwm4 --compositor=off
  71935   71930 S       03:15:16  1876 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:13.log -- /usr/local/bin/box-xfwm4 --compositor=off
  71936   71935 S       03:15:16  1888 flock -n /tmp/xfwm4:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71938   71936 Sl      03:15:16 34828 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71971   68159 S       03:15:16  4880 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71982   71971 S       03:15:16  1940 bash /usr/local/bin/box-bounded-log --run /tmp/picom:13.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71983   71982 S       03:15:16  1864 flock -n /tmp/picom:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  71985   71983 Sl      03:15:16 34868 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  72033      53 Sl      03:15:16  3528 /usr/libexec/dconf-service
  72327      53 Ssl     03:15:16 61140 plank --name dock1
  72341   72327 S       03:15:16  1872 bash /usr/local/bin/box-bounded-log --run /tmp/plank:13-dock1.log -- /usr/local/bin/box-plank --name dock1
  72345   72341 S       03:15:16  1940 flock -n /tmp/plank:13-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72349   72345 Sl      03:15:16 34960 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72391   68159 S       03:15:16  1944 tail -f /dev/null
  72844      53 S       03:15:16  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  72847   72844 Sl      03:15:16  9460 /usr/libexec/bamf/bamfdaemon
  80415   26442 Sl      03:13:37 170492 python3 -X utf8 server.py
  94319       1 S       03:08:28  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94322   94319 Ssl     03:08:28 140996 python3 scripts/acquire/remaining_after_stk_surv.py
  94401       1 S       03:08:26  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94403   94401 Ts      03:08:26 35780 python3 scripts/acquire/relay_outage_backfill.py
 212762   94403 Z       02:02:30     0 [python3] <defunct>
 337724    9604 Ss      01:05:25  4068 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1" < /dev/null; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
 337733  337724 S       01:05:25 19512 python3 -
 437040       1 S          15:37  3580 /bin/bash /tmp/swterm/run.sh
 440937   80415 ZN         11:06     0 [python3] <defunct>
 443569   26454 S          06:27  1960 sleep 600
 445709   26450 S          02:37  2016 sleep 300
 446768   27183 S          00:03  2024 sleep 5
 446789     324 S          00:01  2016 sleep 2
 446792     323 S          00:01  1972 sleep 2
 446877  437040 R          00:00  4728 ps -eo pid,ppid,stat,etime,rss,cmd
ABORT
```
### 04:31:50 终态完整 ps
```
    PID    PPID STAT     ELAPSED   RSS CMD
      1       0 Ss      03:26:07   752 /tini -- /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
      7       1 Sl      03:26:07  7640 /pod-daemon --ssh-auth-sock-path /run/host-services/ssh-auth.sock --ssh-auth-vsock-port 52
     53       7 Ss      03:26:07 14736 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
    204      53 S       03:26:07 32564 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    209     204 S       03:26:07  2028 bash /usr/local/bin/box-bounded-log --run /tmp/novnc-forks.log -- /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
    210     209 S       03:26:07  1780 flock -n /tmp/novnc-forks.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    211     210 Sl      03:26:07 34012 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc-forks.log 204
    227      53 Ssl     03:26:07 48516 /exec-daemon/node /usr/local/bin/sand-window-router.mjs 1339 1337 14000
    247      53 Ssl     03:26:07 48840 /exec-daemon/node /usr/local/bin/sand-session-sync.mjs
    248      53 Sl      03:26:07 99384 /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    257     248 S       03:26:07  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-web-bot-auth.log -- /exec-daemon/node /usr/local/bin/sand-web-bot-auth.mjs
    258     257 S       03:26:07  1896 flock -n /tmp/sand-web-bot-auth.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    259     258 Sl      03:26:07 32604 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-web-bot-auth.log 248
    277      53 Sl      03:26:06 71512 /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    284     277 S       03:26:06  2016 bash /usr/local/bin/box-bounded-log --run /tmp/sand-ua-governor.log -- /exec-daemon/node /usr/local/bin/sand-ua-governor.mjs
    286     284 S       03:26:06  1884 flock -n /tmp/sand-ua-governor.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    290     286 Sl      03:26:06 32980 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-ua-governor.log 277
    322      53 Ssl     03:26:06 49892 /exec-daemon/node /usr/local/bin/sand-cookie-persist.mjs
    323      53 S       03:26:06  4276 bash /usr/local/bin/supervise-exec-daemon 1337 /usr/local/bin/start-exec-daemon
    324      53 S       03:26:06  4084 bash /usr/local/bin/supervise-egress-tunnel 8790 /usr/local/bin/start-egress-tunnel
    369     323 Ss      03:26:06  3424 bash /usr/local/bin/start-exec-daemon
    372     324 Ssl     03:26:06  2508 /usr/local/bin/sand-egress-tunnel server
    376     369 Sl      03:26:06 91652 /exec-daemon/node /exec-daemon/index.js serve --port 1337 --pty-websocket-port 1338 --auth-token local --rg-path /exec-daemon/rg --pty-auth-token local-pty --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
    720       1 Ss      03:25:57  4316 bash /usr/local/bin/start-desktop.sh
    724     720 S       03:25:57  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-2/start-desktop.log -- /usr/local/bin/start-desktop.sh
    725     724 S       03:25:57  1792 flock -n /tmp/sand-window-2/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    726     725 Sl      03:25:57 34308 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-2/start-desktop.log 720
    766       1 Ss      03:25:57  2036 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
    771     720 S       03:25:57 64044 Xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    776     771 S       03:25:57  1904 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:2.log -- /usr/local/bin/box-xvfb :2 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
    778     776 S       03:25:57  1864 flock -n /tmp/xvfb:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
    779     778 Sl      03:25:57 33336 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:2.log 771
   1153     771 Z       03:25:56     0 [bash] <defunct>
   1201       1 Ssl     03:25:56 68900 /exec-daemon/node /exec-daemon/index.js serve --port 14002 --pty-websocket-port 13602 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   1277     720 Sl      03:25:56 26088 xfwm4 --compositor=off
   1282    1277 S       03:25:56  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:2.log -- /usr/local/bin/box-xfwm4 --compositor=off
   1283    1282 S       03:25:56  1784 flock -n /tmp/xfwm4:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1285    1283 Sl      03:25:56 33172 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:2.log 1277
   1316     720 S       03:25:56  4080 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1325    1316 S       03:25:56  1984 bash /usr/local/bin/box-bounded-log --run /tmp/picom:2.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   1326    1325 S       03:25:56  1792 flock -n /tmp/picom:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1329    1326 Sl      03:25:56 33032 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:2.log 1316
   1380       1 Sl      03:25:56  3476 /usr/libexec/dconf-service
   1536       1 Ssl     03:25:56 21152 plank --name dock1
   1543    1536 S       03:25:56  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:2-dock1.log -- /usr/local/bin/box-plank --name dock1
   1544    1543 S       03:25:56  1828 flock -n /tmp/plank:2-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1546    1544 Sl      03:25:56 33044 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:2-dock1.log 1536
   1559     720 S       03:25:56  1872 tail -f /dev/null
   1618       1 S       03:25:56  3364 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   1619    1618 Sl      03:25:56  7168 /usr/libexec/bamf/bamfdaemon
   5268       1 Ss      03:23:23  4308 bash /usr/local/bin/start-desktop.sh
   5271    5268 S       03:23:23  1928 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-12/start-desktop.log -- /usr/local/bin/start-desktop.sh
   5273    5271 S       03:23:23  1844 flock -n /tmp/sand-window-12/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5274    5273 Sl      03:23:23 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-12/start-desktop.log 5268
   5313       1 Ss      03:23:23  2100 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   5318    5268 S       03:23:23 60404 Xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5323    5318 S       03:23:23  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:12.log -- /usr/local/bin/box-xvfb :12 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   5324    5323 S       03:23:23  1904 flock -n /tmp/xvfb:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   5326    5324 Sl      03:23:23 33948 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:12.log 5318
   6227    5318 Z       03:23:23     0 [bash] <defunct>
   6247       1 Ssl     03:23:23 96188 /exec-daemon/node /exec-daemon/index.js serve --port 14012 --pty-websocket-port 13612 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   6295    5268 S       03:23:22 28912 x11vnc -skip_lockkeys -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6300    6295 S       03:23:22  2012 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:12.log -- /usr/local/bin/box-x11vnc -display :12 -localhost -nopw -shared -forever -noxdamage -rfbport 5912 -quiet
   6301    6300 S       03:23:22  1848 flock -n /tmp/x11vnc:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6302    6301 Sl      03:23:22 33824 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:12.log 6295
   6325    5268 Sl      03:23:22 57632 xfwm4 --compositor=off
   6333    6325 S       03:23:22  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:12.log -- /usr/local/bin/box-xfwm4 --compositor=off
   6335    6333 S       03:23:22  1928 flock -n /tmp/xfwm4:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6336    6335 Sl      03:23:22 33980 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:12.log 6325
   6368    5268 S       03:23:22  4776 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6375    6368 S       03:23:22  2036 bash /usr/local/bin/box-bounded-log --run /tmp/picom:12.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   6376    6375 S       03:23:22  1796 flock -n /tmp/picom:12.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6380    6376 Sl      03:23:22 33900 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:12.log 6368
   6450       1 Sl      03:23:22  3432 /usr/libexec/dconf-service
   6654       1 Ssl     03:23:22 59200 plank --name dock1
   6662    6654 S       03:23:22  2056 bash /usr/local/bin/box-bounded-log --run /tmp/plank:12-dock1.log -- /usr/local/bin/box-plank --name dock1
   6665    6662 S       03:23:22  1876 flock -n /tmp/plank:12-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6668    6665 Sl      03:23:22 33976 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:12-dock1.log 6654
   6697    5268 S       03:23:22  1896 tail -f /dev/null
   6834       1 S       03:23:22  3468 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
   6835    6834 Sl      03:23:22  8616 /usr/libexec/bamf/bamfdaemon
   8307       1 Ss      03:22:01  4300 bash /usr/local/bin/start-desktop.sh
   8311    8307 S       03:22:01  2072 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-6/start-desktop.log -- /usr/local/bin/start-desktop.sh
   8312    8311 S       03:22:01  1896 flock -n /tmp/sand-window-6/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8313    8312 Sl      03:22:01 34004 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-6/start-desktop.log 8307
   8352       1 Ss      03:22:01  2148 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
   8357    8307 S       03:22:01 60424 Xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8363    8357 S       03:22:01  1992 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:6.log -- /usr/local/bin/box-xvfb :6 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
   8364    8363 S       03:22:01  1860 flock -n /tmp/xvfb:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   8366    8364 Sl      03:22:01 34244 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:6.log 8357
   9579    8357 Z       03:22:00     0 [bash] <defunct>
   9604       1 Ssl     03:22:00 125944 /exec-daemon/node /exec-daemon/index.js serve --port 14006 --pty-websocket-port 13606 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
   9653    8307 S       03:22:00 28992 x11vnc -skip_lockkeys -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9658    9653 S       03:22:00  2076 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:6.log -- /usr/local/bin/box-x11vnc -display :6 -localhost -nopw -shared -forever -noxdamage -rfbport 5906 -quiet
   9659    9658 S       03:22:00  1796 flock -n /tmp/x11vnc:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9661    9659 Sl      03:22:00 33924 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:6.log 9653
   9679    8307 Sl      03:22:00 11392 xfwm4 --compositor=off
   9684    9679 S       03:22:00  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:6.log -- /usr/local/bin/box-xfwm4 --compositor=off
   9685    9684 S       03:22:00  1860 flock -n /tmp/xfwm4:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9692    9685 Sl      03:22:00 34268 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:6.log 9679
   9730    8307 S       03:22:00  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9738    9730 S       03:22:00  2072 bash /usr/local/bin/box-bounded-log --run /tmp/picom:6.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
   9741    9738 S       03:22:00  1904 flock -n /tmp/picom:6.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9743    9741 Sl      03:22:00 34172 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:6.log 9730
   9795       1 Sl      03:22:00  3336 /usr/libexec/dconf-service
  10084       1 Ssl     03:22:00 59472 plank --name dock1
  10095   10084 S       03:22:00  2020 bash /usr/local/bin/box-bounded-log --run /tmp/plank:6-dock1.log -- /usr/local/bin/box-plank --name dock1
  10096   10095 S       03:22:00  1848 flock -n /tmp/plank:6-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10100   10096 Sl      03:22:00 33952 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:6-dock1.log 10084
  10125    8307 S       03:22:00  1888 tail -f /dev/null
  10284       1 S       03:21:59  3436 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  10287   10284 Sl      03:21:59  8556 /usr/libexec/bamf/bamfdaemon
  11187       1 Ss      03:21:30  4368 bash /usr/local/bin/start-desktop.sh
  11191   11187 S       03:21:30  2056 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-8/start-desktop.log -- /usr/local/bin/start-desktop.sh
  11192   11191 S       03:21:30  1832 flock -n /tmp/sand-window-8/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11193   11192 Sl      03:21:30 34088 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-8/start-desktop.log 11187
  11232       1 Ss      03:21:30  2160 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  11237   11187 S       03:21:30 61208 Xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11242   11237 S       03:21:30  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:8.log -- /usr/local/bin/box-xvfb :8 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  11243   11242 S       03:21:30  1868 flock -n /tmp/xvfb:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  11245   11243 Sl      03:21:30 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:8.log 11237
  12725   11237 Z       03:21:29     0 [bash] <defunct>
  12735       1 Ssl     03:21:29 89308 /exec-daemon/node /exec-daemon/index.js serve --port 14008 --pty-websocket-port 13608 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  12790   11187 S       03:21:29 29100 x11vnc -skip_lockkeys -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12797   12790 S       03:21:29  1972 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:8.log -- /usr/local/bin/box-x11vnc -display :8 -localhost -nopw -shared -forever -noxdamage -rfbport 5908 -quiet
  12798   12797 S       03:21:29  1944 flock -n /tmp/x11vnc:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12800   12798 Sl      03:21:29 34024 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:8.log 12790
  12819   11187 Sl      03:21:29 11396 xfwm4 --compositor=off
  12824   12819 S       03:21:29  2044 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:8.log -- /usr/local/bin/box-xfwm4 --compositor=off
  12825   12824 S       03:21:29  1828 flock -n /tmp/xfwm4:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12826   12825 Sl      03:21:29 34076 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:8.log 12819
  12882   11187 S       03:21:29  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12891   12882 S       03:21:29  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:8.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  12892   12891 S       03:21:29  1824 flock -n /tmp/picom:8.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12896   12892 Sl      03:21:29 33896 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:8.log 12882
  12929       1 Sl      03:21:29  3616 /usr/libexec/dconf-service
  13167       1 Ssl     03:21:28 59724 plank --name dock1
  13178   13167 S       03:21:28  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:8-dock1.log -- /usr/local/bin/box-plank --name dock1
  13179   13178 S       03:21:28  1868 flock -n /tmp/plank:8-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13180   13179 Sl      03:21:28 33980 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:8-dock1.log 13167
  13209   11187 S       03:21:28  1968 tail -f /dev/null
  13486       1 S       03:21:28  3444 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  13489   13486 Sl      03:21:28  8748 /usr/libexec/bamf/bamfdaemon
  14353       1 Ss      03:21:12  4228 bash /usr/local/bin/start-desktop.sh
  14356   14353 S       03:21:12  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-5/start-desktop.log -- /usr/local/bin/start-desktop.sh
  14358   14356 S       03:21:12  1824 flock -n /tmp/sand-window-5/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14359   14358 Sl      03:21:12 33868 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-5/start-desktop.log 14353
  14398       1 Ss      03:21:12  2192 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  14403   14353 S       03:21:12 61084 Xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14408   14403 S       03:21:12  1928 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:5.log -- /usr/local/bin/box-xvfb :5 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  14409   14408 S       03:21:12  1924 flock -n /tmp/xvfb:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  14411   14409 Sl      03:21:12 33964 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:5.log 14403
  16166   14403 Z       03:21:11     0 [bash] <defunct>
  16176       1 Ssl     03:21:10 96032 /exec-daemon/node /exec-daemon/index.js serve --port 14005 --pty-websocket-port 13605 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  16236   14353 S       03:21:10 29000 x11vnc -skip_lockkeys -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16242   16236 S       03:21:10  2040 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:5.log -- /usr/local/bin/box-x11vnc -display :5 -localhost -nopw -shared -forever -noxdamage -rfbport 5905 -quiet
  16243   16242 S       03:21:10  1932 flock -n /tmp/x11vnc:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16246   16243 Sl      03:21:10 34160 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:5.log 16236
  16263   14353 Sl      03:21:10 11432 xfwm4 --compositor=off
  16268   16263 S       03:21:10  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:5.log -- /usr/local/bin/box-xfwm4 --compositor=off
  16269   16268 S       03:21:10  1848 flock -n /tmp/xfwm4:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16271   16269 Sl      03:21:10 34288 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:5.log 16263
  16311   14353 S       03:21:10  4852 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16316   16311 S       03:21:10  2048 bash /usr/local/bin/box-bounded-log --run /tmp/picom:5.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  16318   16316 S       03:21:10  1944 flock -n /tmp/picom:5.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16321   16318 Sl      03:21:10 34244 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:5.log 16311
  16362       1 Sl      03:21:10  3336 /usr/libexec/dconf-service
  16645       1 Ssl     03:21:10 59744 plank --name dock1
  16656   16645 S       03:21:10  2012 bash /usr/local/bin/box-bounded-log --run /tmp/plank:5-dock1.log -- /usr/local/bin/box-plank --name dock1
  16657   16656 S       03:21:10  1900 flock -n /tmp/plank:5-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16661   16657 Sl      03:21:10 33924 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:5-dock1.log 16645
  16690   14353 S       03:21:10  1916 tail -f /dev/null
  16944       1 S       03:21:10  3384 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  16947   16944 Sl      03:21:10  8804 /usr/libexec/bamf/bamfdaemon
  18167       1 Ss      03:20:33  4288 bash /usr/local/bin/start-desktop.sh
  18171   18167 S       03:20:33  2004 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-4/start-desktop.log -- /usr/local/bin/start-desktop.sh
  18172   18171 S       03:20:33  1868 flock -n /tmp/sand-window-4/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18173   18172 Sl      03:20:33 33956 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-4/start-desktop.log 18167
  18212       1 Ss      03:20:33  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  18217   18167 S       03:20:33 61228 Xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18222   18217 S       03:20:33  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:4.log -- /usr/local/bin/box-xvfb :4 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  18224   18222 S       03:20:33  1840 flock -n /tmp/xvfb:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  18225   18224 Sl      03:20:33 33956 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:4.log 18217
  20160   18217 Z       03:20:32     0 [bash] <defunct>
  20188       1 Ssl     03:20:32 92104 /exec-daemon/node /exec-daemon/index.js serve --port 14004 --pty-websocket-port 13604 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  20233   18167 S       03:20:32 29044 x11vnc -skip_lockkeys -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20238   20233 S       03:20:32  2056 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:4.log -- /usr/local/bin/box-x11vnc -display :4 -localhost -nopw -shared -forever -noxdamage -rfbport 5904 -quiet
  20241   20238 S       03:20:32  1876 flock -n /tmp/x11vnc:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20242   20241 Sl      03:20:32 34364 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:4.log 20233
  20261   18167 Sl      03:20:32 11764 xfwm4 --compositor=off
  20266   20261 S       03:20:32  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:4.log -- /usr/local/bin/box-xfwm4 --compositor=off
  20267   20266 S       03:20:32  1924 flock -n /tmp/xfwm4:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20269   20267 Sl      03:20:32 34272 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:4.log 20261
  20316   18167 S       03:20:32  4916 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20323   20316 S       03:20:32  2028 bash /usr/local/bin/box-bounded-log --run /tmp/picom:4.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  20324   20323 S       03:20:32  1828 flock -n /tmp/picom:4.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20328   20324 Sl      03:20:32 33952 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:4.log 20316
  20372       1 Sl      03:20:32  3488 /usr/libexec/dconf-service
  20653       1 Ssl     03:20:31 60444 plank --name dock1
  20665   20653 S       03:20:31  1996 bash /usr/local/bin/box-bounded-log --run /tmp/plank:4-dock1.log -- /usr/local/bin/box-plank --name dock1
  20667   20665 S       03:20:31  1932 flock -n /tmp/plank:4-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20671   20667 Sl      03:20:31 33988 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:4-dock1.log 20653
  20713   18167 S       03:20:31  1964 tail -f /dev/null
  20976       1 S       03:20:31  3456 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  20979   20976 Sl      03:20:31  8696 /usr/libexec/bamf/bamfdaemon
  26442       1 Ss      03:17:26  3524 /bin/bash ./supervise.sh
  26447       1 Ss      03:17:26  3404 /bin/bash ./deploy_supervise.sh
  26450   26447 S       03:17:26  3468 /bin/bash ./deploy_loop.sh
  26454       1 Ss      03:17:26  3432 ql_keepalive_loop -c while true; do sleep 600; /workspace/quantlab-web/start_all.sh --from-keepalive; done
  26581       1 Ssl     03:17:25 40088 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/cli/index.js serve --port 6768 --pairing-address grok-bot
  26627   26581 Sl      03:17:25 150432 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --user-data-dir=/home/box/.config/orca --serve --serve-port 6768 --serve-pairing-address grok-bot
  26630   26627 S       03:17:25 18112 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote --no-zygote-sandbox
  26631   26627 S       03:17:25 18084 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26633   26631 S       03:17:25 10788 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=zygote
  26702       1 Sl      03:17:24  3572 /home/box/.orca/app-1.4.224-20261018051422/chrome_crashpad_handler --monitor-self-annotation=ptype=crashpad-handler --no-rate-limit --no-upload-gzip --database=/home/box/.config/orca/Crashpad --annotation=_productName=orca --annotation=_version=1.4.224 --annotation=lsb-release=Debian GNU/Linux 13 (trixie) --annotation=plat=Linux --annotation=prod=Electron --annotation=ver=43.7.5 --initial-client-fd=41 --shared-client-connection
  26752   26630 Sl      03:17:24 23232 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=gpu-process --disable-dev-shm-usage --ozone-platform=x11 --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --gpu-preferences=WAAAAAAAAAAgAQAEAAAAAAAAAAAAAGAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAABAAAAAAAAAAgAAAAAAAAACAAAAAAAAAAIAAAAAAAAAA== --use-gl=disabled --shared-files --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708988185955192
  26756   26752 S       03:17:24 12136 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=broker
  26762   26627 Sl      03:17:24 24784 /home/box/.orca/app-1.4.224-20261018051422/orca-ide --type=utility --utility-sub-type=network.mojom.NetworkService --lang=en-US --service-sandbox-type=none --disable-dev-shm-usage --crashpad-handler-pid=0 --enable-crash-reporter=593e2e5f-6b43-4a86-bb64-a8a4bc69fbbe,no_channel --user-data-dir=/home/box/.config/orca --standard-schemes=orca-preview,orca-media --secure-schemes=orca-preview,orca-media --cors-schemes=orca-preview --fetch-schemes=orca-preview --streaming-schemes=orca-preview,orca-media --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,4798019459902702605,6824676083144334604,262144 --enable-features=EarlyEstablishGpuChannel,EstablishGpuChannelAsync,GlobalShortcutsPortalPreferredTrigger,PdfUseShowSaveFilePicker --disable-features=DirectSockets,DirectSocketsInServiceWorkers,DirectSocketsInSharedWorkers,DropInputEventsWhilePaintHolding,FedCm,IntensiveWakeUpThrottling,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,1093890293600097732,3130111451012626359,4 --trace-process-track-uuid=3190708989122997041
  26800   26627 Ssl     03:17:23 41728 /home/box/.orca/app-1.4.224-20261018051422/orca-ide /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --socket /home/box/.config/orca/daemon/daemon-v43.sock --token /home/box/.config/orca/daemon/daemon-v43.token --pid-record /home/box/.config/orca/daemon/daemon-v43.pid --launch-nonce 9f1cf877-a9c1-4595-b95d-e8ac301fed85 --entry-path /home/box/.orca/app-1.4.224-20261018051422/resources/app.asar.unpacked/out/main/daemon-entry.js --app-version 1.4.224 --spawner-exec-path /home/box/.orca/app-1.4.224-20261018051422/orca-ide --log-file /home/box/.config/orca/logs/daemon.log
  27167      53 Ss      03:17:21  3748 bash /usr/local/bin/supervise-sand-supervisor /tmp/sand-supervisor/status.json /tmp/sand-supervisor.log /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27182   27167 Ssl     03:17:21 65792 /exec-daemon/node /usr/local/bin/sand-supervisor.mjs
  27183   27167 Ss      03:17:21  3428 bash -c while sleep "$1"; do kill -USR1 "$2" 2>/dev/null || exit 0; done ticker 5 27167
  27186      53 S       03:17:21  4328 bash /usr/local/bin/start-desktop.sh
  27191   27186 S       03:17:21  1992 bash /usr/local/bin/box-bounded-log --run /tmp/start-desktop.log -- /usr/local/bin/start-desktop.sh
  27192   27191 S       03:17:21  1824 flock -n /tmp/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27194   27192 Sl      03:17:21 34148 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/start-desktop.log 27186
  27245       1 Ss      03:17:21  2232 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  27250   27186 S       03:17:21 61116 Xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27255   27250 S       03:17:21  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:1.log -- /usr/local/bin/box-xvfb :1 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  27256   27255 S       03:17:21  1864 flock -n /tmp/xvfb:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27258   27256 Sl      03:17:21 34492 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:1.log 27250
  27263   27250 Z       03:17:21     0 [bash] <defunct>
  27313   27182 Rsl     03:17:21 1140908 /exec-daemon/node --disable-warning=ExperimentalWarning /opt/sand/sand-host/host-main.cjs
  27366      53 Ss      03:17:21 24188 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
  27383      53 S       03:17:21  2592 /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27385   27383 S       03:17:21  2028 bash /usr/local/bin/box-bounded-log --run /tmp/sand-orbitd.log -- env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/local/libexec/sand/sand-daemon-supervisor run orbitd
  27386   27385 S       03:17:21  1944 flock -n /tmp/sand-orbitd.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27389   27386 Sl      03:17:21 34388 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-orbitd.log 27383
  27390   27383 S       03:17:21  8104 /usr/local/libexec/sand/sand-daemon-supervisor __supervise orbitd
  27398   27186 S       03:17:21 20080 x11vnc -skip_lockkeys -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27403   27398 S       03:17:21  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:1.log -- /usr/local/bin/box-x11vnc -display :1 -localhost -nopw -shared -forever -noxdamage -rfbport 5900 -quiet
  27404   27403 S       03:17:21  1832 flock -n /tmp/x11vnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27405   27404 Sl      03:17:21 34212 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:1.log 27398
  27427   27186 S       03:17:21 35112 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27432   27427 S       03:17:21  2020 bash /usr/local/bin/box-bounded-log --run /tmp/novnc:1.log -- websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  27433   27432 S       03:17:21  1836 flock -n /tmp/novnc:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27434   27433 Sl      03:17:21 34476 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/novnc:1.log 27427
  27453   27186 Sl      03:17:21 11748 xfwm4 --compositor=off
  27458   27453 S       03:17:21  2020 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:1.log -- /usr/local/bin/box-xfwm4 --compositor=off
  27462   27458 S       03:17:21  1880 flock -n /tmp/xfwm4:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27466   27462 Sl      03:17:21 34140 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:1.log 27453
  27505   27186 S       03:17:21  4860 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27510   27505 S       03:17:21  1992 bash /usr/local/bin/box-bounded-log --run /tmp/picom:1.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  27512   27510 S       03:17:21  1880 flock -n /tmp/picom:1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27513   27512 Sl      03:17:21 34120 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:1.log 27505
  27574       1 Sl      03:17:21  3560 /usr/libexec/dconf-service
  27953      53 Ssl     03:17:21 60176 plank --name dock1
  27967   27953 S       03:17:21  2024 bash /usr/local/bin/box-bounded-log --run /tmp/plank:1-dock1.log -- /usr/local/bin/box-plank --name dock1
  27969   27967 S       03:17:21  1820 flock -n /tmp/plank:1-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  27974   27969 Sl      03:17:21 33908 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:1-dock1.log 27953
  28014   27186 S       03:17:21  1948 tail -f /dev/null
  28485       1 S       03:17:20  3376 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  28490   28485 Sl      03:17:20  8700 /usr/libexec/bamf/bamfdaemon
  29120   27390 Sl      03:17:20  5244 /var/lib/sand-daemon-supervisor/orbitd/releases/28b0833c5707e1c919cee4d4ab5a8ad0eeac9c46/orbitd
  29240   27313 Sl      03:17:20 200684 /opt/sand/sand-host/extensions/codebase-telemetry/csnaps
  29910      53 Ss      03:17:16  4428 bash /usr/local/bin/start-desktop.sh
  29915   29910 S       03:17:16  1980 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-3/start-desktop.log -- /usr/local/bin/start-desktop.sh
  29916   29915 S       03:17:16  1824 flock -n /tmp/sand-window-3/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  29917   29916 Sl      03:17:16 34192 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-3/start-desktop.log 29910
  30000      53 Ss      03:17:16  2272 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  30031   29910 S       03:17:16 52252 Xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30036   30031 S       03:17:16  2080 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:3.log -- /usr/local/bin/box-xvfb :3 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  30037   30036 S       03:17:16  1824 flock -n /tmp/xvfb:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30039   30037 Sl      03:17:16 34076 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:3.log 30031
  30381   27182 Ss      03:17:16 20056 x11vnc -skip_lockkeys -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30384   30381 S       03:17:16  2028 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:2.log -- /usr/local/bin/box-x11vnc -display :2 -localhost -nopw -shared -forever -noxdamage -rfbport 5902 -quiet
  30385   30384 S       03:17:16  1932 flock -n /tmp/x11vnc:2.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  30386   30385 Sl      03:17:16 35392 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:2.log 30381
  33709   30031 Z       03:17:13     0 [bash] <defunct>
  33760      53 Ssl     03:17:13 96220 /exec-daemon/node /exec-daemon/index.js serve --port 14003 --pty-websocket-port 13603 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  33788   29910 S       03:17:13 29036 x11vnc -skip_lockkeys -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33790   33788 S       03:17:13  2024 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:3.log -- /usr/local/bin/box-x11vnc -display :3 -localhost -nopw -shared -forever -noxdamage -rfbport 5903 -quiet
  33791   33790 S       03:17:13  1840 flock -n /tmp/x11vnc:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33792   33791 Sl      03:17:13 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:3.log 33788
  33824   29910 Sl      03:17:13 11788 xfwm4 --compositor=off
  33827   33824 S       03:17:13  2076 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:3.log -- /usr/local/bin/box-xfwm4 --compositor=off
  33832   33827 S       03:17:13  1824 flock -n /tmp/xfwm4:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33834   33832 Sl      03:17:13 34276 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:3.log 33824
  33861   29910 S       03:17:13  4876 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33871   33861 S       03:17:13  2024 bash /usr/local/bin/box-bounded-log --run /tmp/picom:3.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  33872   33871 S       03:17:13  1896 flock -n /tmp/picom:3.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33877   33872 Sl      03:17:13 34132 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:3.log 33861
  33940      53 Sl      03:17:13  3492 /usr/libexec/dconf-service
  34299      53 Ssl     03:17:13 60100 plank --name dock1
  34308   34299 S       03:17:13  2052 bash /usr/local/bin/box-bounded-log --run /tmp/plank:3-dock1.log -- /usr/local/bin/box-plank --name dock1
  34317   34308 S       03:17:13  1824 flock -n /tmp/plank:3-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34330   34317 Sl      03:17:13 34064 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:3-dock1.log 34299
  34358   29910 S       03:17:13  1900 tail -f /dev/null
  34507      53 S       03:17:13  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  34509   34507 Sl      03:17:13  8908 /usr/libexec/bamf/bamfdaemon
  35700      53 Ss      03:17:08  4332 bash /usr/local/bin/start-desktop.sh
  35703   35700 S       03:17:08  1996 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-7/start-desktop.log -- /usr/local/bin/start-desktop.sh
  35704   35703 S       03:17:08  1924 flock -n /tmp/sand-window-7/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35705   35704 Sl      03:17:08 34160 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-7/start-desktop.log 35700
  35755      53 Ss      03:17:08  2224 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  35760   35700 S       03:17:08 52176 Xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35765   35760 S       03:17:08  2056 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:7.log -- /usr/local/bin/box-xvfb :7 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  35766   35765 S       03:17:08  1868 flock -n /tmp/xvfb:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  35767   35766 Sl      03:17:08 34036 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:7.log 35760
  38646   35760 Z       03:17:06     0 [bash] <defunct>
  38695      53 Ssl     03:17:06 92256 /exec-daemon/node /exec-daemon/index.js serve --port 14007 --pty-websocket-port 13607 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  38714   35700 S       03:17:06 29116 x11vnc -skip_lockkeys -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38716   38714 S       03:17:06  1976 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:7.log -- /usr/local/bin/box-x11vnc -display :7 -localhost -nopw -shared -forever -noxdamage -rfbport 5907 -quiet
  38720   38716 S       03:17:06  1916 flock -n /tmp/x11vnc:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38723   38720 Sl      03:17:06 34156 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:7.log 38714
  38739   35700 Sl      03:17:06 11844 xfwm4 --compositor=off
  38741   38739 S       03:17:06  2028 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:7.log -- /usr/local/bin/box-xfwm4 --compositor=off
  38745   38741 S       03:17:06  1896 flock -n /tmp/xfwm4:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38754   38745 Sl      03:17:06 34300 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:7.log 38739
  38783   35700 S       03:17:06  4868 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38786   38783 S       03:17:06  1952 bash /usr/local/bin/box-bounded-log --run /tmp/picom:7.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  38787   38786 S       03:17:06  1836 flock -n /tmp/picom:7.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38792   38787 Sl      03:17:06 34176 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:7.log 38783
  38862      53 Sl      03:17:06  3564 /usr/libexec/dconf-service
  39132      53 Ssl     03:17:06 60244 plank --name dock1
  39135   39132 S       03:17:06  2004 bash /usr/local/bin/box-bounded-log --run /tmp/plank:7-dock1.log -- /usr/local/bin/box-plank --name dock1
  39139   39135 S       03:17:06  1940 flock -n /tmp/plank:7-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39143   39139 Sl      03:17:06 34168 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:7-dock1.log 39132
  39194   35700 S       03:17:05  1940 tail -f /dev/null
  39490      53 S       03:17:05  3460 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  39496   39490 Sl      03:17:05  8724 /usr/libexec/bamf/bamfdaemon
  40253      53 Ss      03:17:03  4240 bash /usr/local/bin/start-desktop.sh
  40257   40253 S       03:17:03  2024 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-10/start-desktop.log -- /usr/local/bin/start-desktop.sh
  40258   40257 S       03:17:03  1820 flock -n /tmp/sand-window-10/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40259   40258 Sl      03:17:03 34236 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-10/start-desktop.log 40253
  40298      53 Ss      03:17:03  2168 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  40303   40253 S       03:17:03 52220 Xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40309   40303 S       03:17:03  2088 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:10.log -- /usr/local/bin/box-xvfb :10 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  40310   40309 S       03:17:03  1932 flock -n /tmp/xvfb:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  40313   40310 Sl      03:17:03 34088 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:10.log 40303
  43282   40303 Z       03:17:00     0 [bash] <defunct>
  43326      53 Ssl     03:17:00 92148 /exec-daemon/node /exec-daemon/index.js serve --port 14010 --pty-websocket-port 13610 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  43338   40253 S       03:17:00 28984 x11vnc -skip_lockkeys -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43339   43338 S       03:17:00  2008 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:10.log -- /usr/local/bin/box-x11vnc -display :10 -localhost -nopw -shared -forever -noxdamage -rfbport 5910 -quiet
  43340   43339 S       03:17:00  1944 flock -n /tmp/x11vnc:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43345   43340 Sl      03:17:00 33940 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:10.log 43338
  43363   40253 Sl      03:17:00 11860 xfwm4 --compositor=off
  43368   43363 S       03:17:00  2000 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:10.log -- /usr/local/bin/box-xfwm4 --compositor=off
  43370   43368 S       03:17:00  1932 flock -n /tmp/xfwm4:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43379   43370 Sl      03:17:00 34180 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:10.log 43363
  43406   40253 S       03:17:00  4892 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43417   43406 S       03:17:00  2004 bash /usr/local/bin/box-bounded-log --run /tmp/picom:10.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  43420   43417 S       03:17:00  1828 flock -n /tmp/picom:10.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43421   43420 Sl      03:17:00 34232 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:10.log 43406
  43451      53 Sl      03:17:00  3488 /usr/libexec/dconf-service
  43842   40253 S       03:17:00  1880 tail -f /dev/null
  43954   27182 Ssl     03:17:00 60260 plank --name dock1
  43957   43954 S       03:17:00  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:10-dock1.log -- /usr/local/bin/box-plank --name dock1
  43962   43957 S       03:17:00  1900 cat
  44192      53 S       03:17:00  3428 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  44194   44192 Sl      03:17:00  8760 /usr/libexec/bamf/bamfdaemon
  45490      53 Ss      03:16:50  4312 bash /usr/local/bin/start-desktop.sh
  45496   45490 S       03:16:50  2044 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-11/start-desktop.log -- /usr/local/bin/start-desktop.sh
  45497   45496 S       03:16:50  1924 flock -n /tmp/sand-window-11/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45499   45497 Sl      03:16:50 34084 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-11/start-desktop.log 45490
  45547      53 Ss      03:16:50  2164 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  45552   45490 S       03:16:50 52280 Xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45557   45552 S       03:16:50  2032 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:11.log -- /usr/local/bin/box-xvfb :11 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  45558   45557 S       03:16:50  1936 flock -n /tmp/xvfb:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  45559   45558 Sl      03:16:50 34120 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:11.log 45552
  49144   45552 Z       03:16:48     0 [bash] <defunct>
  49154      53 Ssl     03:16:48 92176 /exec-daemon/node /exec-daemon/index.js serve --port 14011 --pty-websocket-port 13611 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  49212   45490 S       03:16:47 28972 x11vnc -skip_lockkeys -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49217   49212 S       03:16:47  2052 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:11.log -- /usr/local/bin/box-x11vnc -display :11 -localhost -nopw -shared -forever -noxdamage -rfbport 5911 -quiet
  49219   49217 S       03:16:47  1916 flock -n /tmp/x11vnc:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49220   49219 Sl      03:16:47 34164 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:11.log 49212
  49246   45490 Sl      03:16:47 11744 xfwm4 --compositor=off
  49251   49246 S       03:16:47  2052 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:11.log -- /usr/local/bin/box-xfwm4 --compositor=off
  49252   49251 S       03:16:47  1824 flock -n /tmp/xfwm4:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49254   49252 Sl      03:16:47 34260 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:11.log 49246
  49294   45490 S       03:16:47  4864 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49301   49294 S       03:16:47  1872 bash /usr/local/bin/box-bounded-log --run /tmp/picom:11.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  49302   49301 S       03:16:47  1832 flock -n /tmp/picom:11.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49309   49302 Sl      03:16:47 34204 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:11.log 49294
  49348      53 Sl      03:16:47  3604 /usr/libexec/dconf-service
  49610      53 Ssl     03:16:47 60448 plank --name dock1
  49625   49610 S       03:16:47  2044 bash /usr/local/bin/box-bounded-log --run /tmp/plank:11-dock1.log -- /usr/local/bin/box-plank --name dock1
  49628   49625 S       03:16:47  1832 flock -n /tmp/plank:11-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49632   49628 Sl      03:16:47 34036 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:11-dock1.log 49610
  49668   45490 S       03:16:47  1884 tail -f /dev/null
  50219      53 S       03:16:47  3548 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  50221   50219 Sl      03:16:47  8816 /usr/libexec/bamf/bamfdaemon
  68159      53 Ss      03:16:18  4344 bash /usr/local/bin/start-desktop.sh
  68162   68159 S       03:16:18  2032 bash /usr/local/bin/box-bounded-log --run /tmp/sand-window-13/start-desktop.log -- /usr/local/bin/start-desktop.sh
  68164   68162 S       03:16:18  1948 flock -n /tmp/sand-window-13/start-desktop.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68165   68164 Sl      03:16:18 34756 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/sand-window-13/start-desktop.log 68159
  68204      53 Ss      03:16:18  2236 /usr/bin/dbus-daemon --syslog --fork --print-pid 4 --print-address 6 --session
  68209   68159 S       03:16:18 52280 Xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68214   68209 S       03:16:18  1956 bash /usr/local/bin/box-bounded-log --run /tmp/xvfb:13.log -- /usr/local/bin/box-xvfb :13 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
  68215   68214 S       03:16:18  1876 flock -n /tmp/xvfb:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  68217   68215 Sl      03:16:18 34876 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xvfb:13.log 68209
  71849   68209 Z       03:16:16     0 [bash] <defunct>
  71893      53 Ssl     03:16:15 102144 /exec-daemon/node /exec-daemon/index.js serve --port 14013 --pty-websocket-port 13613 --auth-token local --rg-path /exec-daemon/rg --computer-use-enabled --computer-use-lazy-init --computer-use-api-width 1280 --computer-use-api-height 800 --mcp-meta-tool-enabled --origin-cli-enabled --orbitd-proxy-socket /run/orbitd-proxy/rpc.sock
  71905   68159 S       03:16:15 29012 x11vnc -skip_lockkeys -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71910   71905 S       03:16:15  2048 bash /usr/local/bin/box-bounded-log --run /tmp/x11vnc:13.log -- /usr/local/bin/box-x11vnc -display :13 -localhost -nopw -shared -forever -noxdamage -rfbport 5913 -quiet
  71912   71910 S       03:16:15  1864 flock -n /tmp/x11vnc:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71913   71912 Sl      03:16:15 34912 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/x11vnc:13.log 71905
  71930   68159 Sl      03:16:15 13248 xfwm4 --compositor=off
  71935   71930 S       03:16:15  1876 bash /usr/local/bin/box-bounded-log --run /tmp/xfwm4:13.log -- /usr/local/bin/box-xfwm4 --compositor=off
  71936   71935 S       03:16:15  1888 flock -n /tmp/xfwm4:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71938   71936 Sl      03:16:15 34820 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/xfwm4:13.log 71930
  71971   68159 S       03:16:15  4880 picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71982   71971 S       03:16:15  1940 bash /usr/local/bin/box-bounded-log --run /tmp/picom:13.log -- /usr/local/bin/box-picom --backend xrender --no-vsync --no-frame-pacing --no-use-damage
  71983   71982 S       03:16:15  1864 flock -n /tmp/picom:13.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  71985   71983 Sl      03:16:15 34860 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/picom:13.log 71971
  72033      53 Sl      03:16:15  3528 /usr/libexec/dconf-service
  72327      53 Ssl     03:16:15 61140 plank --name dock1
  72341   72327 S       03:16:15  1872 bash /usr/local/bin/box-bounded-log --run /tmp/plank:13-dock1.log -- /usr/local/bin/box-plank --name dock1
  72345   72341 S       03:16:15  1940 flock -n /tmp/plank:13-dock1.log.lock /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72349   72345 Sl      03:16:15 34952 /exec-daemon/node /usr/local/bin/box-bounded-log.mjs /tmp/plank:13-dock1.log 72327
  72391   68159 S       03:16:15  1944 tail -f /dev/null
  72844      53 S       03:16:15  3512 /bin/bash /usr/libexec/bamf/bamfdaemon-dbus-runner
  72847   72844 Sl      03:16:15  9460 /usr/libexec/bamf/bamfdaemon
  80415   26442 Sl      03:14:36 170492 python3 -X utf8 server.py
  94319       1 S       03:09:26  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94322   94319 Ssl     03:09:26 141012 python3 scripts/acquire/remaining_after_stk_surv.py
  94401       1 S       03:09:24  2156 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
  94403   94401 Ts      03:09:24 35780 python3 scripts/acquire/relay_outage_backfill.py
 212762   94403 Z       02:03:29     0 [python3] <defunct>
 443569   26454 S          07:26  1960 sleep 600
 445709   26450 S          03:36  2016 sleep 300
 447995   80415 ZN         00:02     0 [python3] <defunct>
 448004   27183 S          00:02  1936 sleep 5
 448018     323 S          00:01  2008 sleep 2
 448024     324 S          00:00  1968 sleep 2
 448029    9604 Ss         00:00  3836 /usr/bin/bash -O extglob -c IFS= builtin read -r -d '' __cursor_command <&5 2>/dev/null || { builtin printf '%s\n' 'The command did not run: a shell startup file ($BASH_ENV or .zshenv) closed or replaced file descriptor 5, which carries the command. Run it again; this shell now passes commands as arguments.' >&2; builtin exit 126; }; exec 5<&-; builtin set -- "$__cursor_command"; builtin unset __cursor_command; snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap"; { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin eval "${__CURSOR_SANDBOX_TEMP_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE --
 448038  448029 R          00:00  4744 ps -eo pid,ppid,stat,etime,rss,cmd
```
### 执行脚本 /tmp/swterm/run.sh
```bash
#!/bin/bash
cd /workspace/QuantLab
L=/tmp/swterm/log.txt
P=data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
ts(){ date '+%F %T.%3N %Z'; }
snap(){ echo "### ps snapshot $(ts)" >>$L; ps -eo pid,ppid,stat,etime,rss,cmd >>$L; }
st(){ awk '{print $3}' /proc/$1/stat 2>/dev/null || echo GONE; }
kids(){ pgrep -P 94403 | tr '\n' ' '; }
DEAD=$(date -d '2026-10-18 04:30:00' +%s)
echo "start poll $(ts)" >>$L
while :; do
  now=$(date +%s)
  if ! kill -0 212762 2>/dev/null; then
    echo "PATH_A: 212762 exited on its own, observed $(ts); 94403 kids=[$(kids)]" >>$L
    if [ -z "$(kids)" ]; then
      snap; kill -STOP 94403; echo "SIGSTOP 94403 sent $(ts)" >>$L; sleep 1
      echo "94403 state=$(st 94403) kids=[$(kids)] $(ts)" >>$L
      if [ -n "$(kids)" ]; then kill -CONT 94403; echo "new child spawned; CONT 94403 $(ts) state=$(st 94403)" >>$L;
      else echo DONE_A >>$L; exit 0; fi
    fi
    # wait for 04:30 with child present
    while [ $(date +%s) -lt $DEAD ]; do sleep 30; done
    echo "PATH_A fallback reached 04:30 $(ts) kids=[$(kids)]; NOT signalling (task B applies to 212762 only)" >>$L; snap; echo STOP_A_UNRESOLVED >>$L; exit 2
  fi
  [ $now -ge $DEAD ] && break
  echo "poll $(ts) 212762=$(st 212762) 212763=$(st 212763) 94403=$(st 94403)" >>$L
  sleep 30
done
echo "PATH_B: 04:30 reached $(ts), 212762 alive" >>$L
snap
echo "212762 etime=$(ps -o etime= -p 212762) lstart=$(ps -o lstart= -p 212762)" >>$L
echo "pinned before: $(sha256sum $P) mtime=$(stat -c %y $P) $(ts)" >>$L
kill -STOP 94403; echo "SIGSTOP 94403 sent $(ts)" >>$L; sleep 1
echo "94403 state=$(st 94403) $(ts)" >>$L
kill -TERM 212763; echo "SIGTERM 212763 sent $(ts)" >>$L
for i in $(seq 1 30); do kill -0 212763 2>/dev/null || break; sleep 1; done
if kill -0 212763 2>/dev/null; then echo "212763 STILL ALIVE after 30s $(ts) state=$(st 212763)" >>$L; snap; echo ABORT >>$L; exit 3; fi
echo "212763 exited $(ts)" >>$L
for i in $(seq 1 5); do kill -0 212762 2>/dev/null || break; sleep 1; done
if kill -0 212762 2>/dev/null; then
  kill -TERM 212762; echo "SIGTERM 212762 sent $(ts)" >>$L
  for i in $(seq 1 30); do kill -0 212762 2>/dev/null || break; sleep 1; done
  if kill -0 212762 2>/dev/null; then echo "212762 STILL ALIVE after 30s $(ts) state=$(st 212762)" >>$L; snap; echo ABORT >>$L; exit 3; fi
  echo "212762 exited $(ts)" >>$L
else echo "212762 exited by itself after child TERM (no SIGTERM needed) $(ts)" >>$L; fi
echo "94403 state=$(st 94403) kids=[$(kids)] $(ts)" >>$L
snap
echo "pinned after: $(sha256sum $P) mtime=$(stat -c %y $P) $(ts)" >>$L
echo DONE_B >>$L
```
