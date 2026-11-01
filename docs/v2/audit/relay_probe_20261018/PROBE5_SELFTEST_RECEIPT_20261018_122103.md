# PROBE5 SELFTEST RECEIPT 20261018_122103

- start (ET): 2026-10-18 12:18:58 EDT ; end (ET): 2026-10-18 12:20:59 EDT ; selftest exit code: 0 ; ALL_PASS: True
- No relay contact (base-url 127.0.0.1 only), no project data read, no project code imported, real probe_log.csv untouched, real key not read (fake env file). No .ok required (fake-file test).

## Files (sha256)
- /tmp/relay_probe/probe4.py  ea9dff995e2add3f103cf9e632001907eca2c88be1c4e447e1bedfcf7d2940fb
- /tmp/relay_probe/probe5.py  62b7b0be6eed660b74f33d6ee755856492f286b2c6924e6f1f0fa7893c24f048
- /tmp/relay_probe/probe5.diff  d84aeb99f06bb96d80fdd7998d79071c00c217952eb6a95f66d2a1eb28ba2159
- /tmp/relay_probe/selftest_probe5.py  6e9f089a5fb2afcefbc991f9ad14c1ddb8954712c42aa8fb62088719b23f7585
- /tmp/relay_probe/gen_probe5.py  e7cb66dbe65d63e9b74e9eded37b270c7be157b6f5e65fdb0c977d8d01ab2f39
- /tmp/relay_probe/write_receipt5.py  84cf131e9f00e69b3adb9a878f274601de336417eb045ab39b60ca64bf23ab43
- /tmp/relay_probe/selftest5/result.json  c3dad6a1627bfe0340d066d27e02193a24e393972cfc5b1b683319a95a776627

## Command
    nice -n 10 python3 /tmp/relay_probe/selftest_probe5.py </dev/null

## How the fakes were made
- fake key file: /tmp/relay_probe/selftest5/fake.env, written atomically by the selftest, content TSPRO_PROXY_KEY=FAKEKEY_selftest5_not_real
- fake server: stdlib http.server.ThreadingHTTPServer inside the selftest process on 127.0.0.1:35009 (ephemeral), daemon threads; shut down and socket closed at end, then port re-checked closed
  - /fast/: 200 + JSON with 5000 items at once
  - /slowbody/: status + headers (Content-Length 100), then sleep 140 s, no body
  - /slowhead/: accept, send nothing for 140 s
  - /drip/: headers, then 1 byte every 5 s for 200 s (per-read timeout never fires; only the 120 s wall cap can stop it)
- fake logs: /tmp/relay_probe/selftest5/log_<case>.csv via probe5 --log-path
- fast case ran first; slowbody, slowhead, drip ran in parallel (three probe5 parents, each with one child)

## Checks
- fast_rows_5000_big_page_full: PASS
- slowbody_timeout_115_or_wall120_not_15: PASS
- slowhead_timeout_115_or_wall120_not_15: PASS
- drip_wall_cap_120: PASS
- no_read_timeout_15_anywhere: PASS
- server_saw_only_fake_key: PASS
- server_port_closed_after: PASS

## Per-case results
### fast
- cmd: `/usr/bin/python3 /tmp/relay_probe/probe5.py --only stock_basic --base-url http://127.0.0.1:35009/fast/ --env-file /tmp/relay_probe/selftest5/fake.env --log-path /tmp/relay_probe/selftest5/log_fast.csv`
- rc: 0 ; outer elapsed: 0.55 s
- stdout:
    2026-10-18 12:18:58 stock_basic 0.5 200 5000  child_pid=218788 rc=0 big_page_full=True
    RESULT stock_basic big_page_full=True
- log csv:
    ts_et,api,params,elapsed_s,http_status,rows,error
    2026-10-18 12:18:58,stock_basic,"{""list_status"":""L"",""limit"":5000,""offset"":0}",0.5,200,5000,
### slowbody
- cmd: `/usr/bin/python3 /tmp/relay_probe/probe5.py --only stock_basic --base-url http://127.0.0.1:35009/slowbody/ --env-file /tmp/relay_probe/selftest5/fake.env --log-path /tmp/relay_probe/selftest5/log_slowbody.csv`
- rc: 2 ; outer elapsed: 115.61 s
- stdout:
    2026-10-18 12:20:54 stock_basic 115.57   ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=35009): Read timed out. child_pid=218801 rc=0 big_page_full=False
    RESULT stock_basic big_page_full=False
- log csv:
    ts_et,api,params,elapsed_s,http_status,rows,error
    2026-10-18 12:20:54,stock_basic,"{""list_status"":""L"",""limit"":5000,""offset"":0}",115.57,,,"ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=35009): Read timed out."
### slowhead
- cmd: `/usr/bin/python3 /tmp/relay_probe/probe5.py --only stock_basic --base-url http://127.0.0.1:35009/slowhead/ --env-file /tmp/relay_probe/selftest5/fake.env --log-path /tmp/relay_probe/selftest5/log_slowhead.csv`
- rc: 2 ; outer elapsed: 115.61 s
- stdout:
    2026-10-18 12:20:54 stock_basic 115.56   ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=35009): Read timed out. (read timeout=115) child_pid=218802 rc=0 big_page_full=False
    RESULT stock_basic big_page_full=False
- log csv:
    ts_et,api,params,elapsed_s,http_status,rows,error
    2026-10-18 12:20:54,stock_basic,"{""list_status"":""L"",""limit"":5000,""offset"":0}",115.56,,,"ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=35009): Read timed out. (read timeout=115)"
### drip
- cmd: `/usr/bin/python3 /tmp/relay_probe/probe5.py --only stock_basic --base-url http://127.0.0.1:35009/drip/ --env-file /tmp/relay_probe/selftest5/fake.env --log-path /tmp/relay_probe/selftest5/log_drip.csv`
- rc: 2 ; outer elapsed: 120.4 s
- stdout:
    2026-10-18 12:20:59 stock_basic 120.36   wall_timeout_120s (term_sent) child_pid=218800 rc=-15 big_page_full=False
    RESULT stock_basic big_page_full=False
- log csv:
    ts_et,api,params,elapsed_s,http_status,rows,error
    2026-10-18 12:20:59,stock_basic,"{""list_status"":""L"",""limit"":5000,""offset"":0}",120.36,,,wall_timeout_120s (term_sent)

## Server-side requests seen
- /fast/stock_basic key_is_fake=True
- /slowbody/stock_basic key_is_fake=True
- /slowhead/stock_basic key_is_fake=True
- /drip/stock_basic key_is_fake=True
