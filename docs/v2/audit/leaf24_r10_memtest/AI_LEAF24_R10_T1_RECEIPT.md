# AI_LEAF24_R10_T1_RECEIPT (build_HILIQ)

- run: 2026-10-18 08:01:40 -> 08:02:50 ET via bash /tmp/l24r10_T1_wrapper.sh (non-interactive), STOPKB=1331200, uni=HILIQ
- wrapper sha256: 77b5d2b515418bd33024def8cf17e40e0f325f6dfd0140cd99ec863c03bc80fa
- step table sha256 (rev3b, L27 narrowed to T1): d1cf24d8741175c0d598116b1f761190de69edb3ca6df85971911cbee6d7ed3b
- commits: 259bdbaad2e0c7efc4036c9564992b0811598194 (content unchanged 5e75f9d3: first sed hit line 28, disclosed, no history rewrite); 875b8eae9dcc622eb96128725514915ebb85caf3 (effective, L27 narrowed)
- .ok sha256: 56bd86ec1b6be390719f630e3b1aa62fab988d69213673424e301fed71ed5fd2

## Result
- MEMTEST_END test=build_HILIQ vmhwm_kb=977440 vmhwm_mib=954.5 vmrss_kb=442784 target_1300mib=within
- WRAPPER_DONE rc=0 stopped=0; exit=0 stopped=0

## C1-C5
- C1 PASS: exit 0
- C2 PASS: meta stage=build_HILIQ, script 53d3f8b1, arch_ok 56bd86ec, variant primary, 7 outputs sha match files; external_outputs absent (build must list none; harness check passed); _ext_root has no files
- C3 PASS: MEMTEST_START x1, peak_check build x6, peak_check memtest end x1, MEMTEST_END x1, no STAMP; C3b PASS: no RSS_GUARD_KILL/RSS_WATCHDOG_ERROR/STOP/refused/Traceback
- C4 PASS: VmHWM 977440 kB <= 1536000; meta peak_rss_mb 954.53 < 1500; target_1300mib=within (no stop)
- C5 PASS: c5watch log empty (no hit); sampler no stop line; ps after: only system daemons + 94322 (Tsl)

## sha256
```
0ccc0f96f6cabd69d34e126ab91249d4b751c8065dd7ca45f272464a7463b096  output/ai_factory/_memtest/leaf24_r10/alpha_HILIQ_2024.parquet
70a2cc479f128a6f34c840c3f4031cf9eb22f243b55fb623f445c8715a06336e  output/ai_factory/_memtest/leaf24_r10/alpha_HILIQ_2025.parquet
5a1fc629278c2cfa6552549417161c506f30a024fe1f368efc5b193da441a5a3  output/ai_factory/_memtest/leaf24_r10/alpha_HILIQ_2026.parquet
e8278e47fe7aba9acf8da929193ecd6c49f59738e88eee14be383b031df7a0c3  output/ai_factory/_memtest/leaf24_r10/coverage_HILIQ.parquet
b58f48d30b83269fe7036810e2192033cb3282cb51f50c504dd9fd861b149742  output/ai_factory/_memtest/leaf24_r10/gate_HILIQ_2024.parquet
b7bcc527e18d5011e0d3209009c07afc4f4ff42861e61de4f09ba2bf3b284497  output/ai_factory/_memtest/leaf24_r10/gate_HILIQ_2025.parquet
d32828940bbafd819de91ec3bb07099d5b2a319c0bdf5271c336828b8d954c0f  output/ai_factory/_memtest/leaf24_r10/gate_HILIQ_2026.parquet
38dc39abed1cbd6eb3dbb234e77eaec2f17f6417117aa2d912f216b3470799ab  output/ai_factory/_memtest/leaf24_r10/build_HILIQ_meta.json
497b03acb34b6ae2e2b3cdae85332c81f2d230b8698d1ed028cb942b7f8df098  output/ai_factory/_memtest/leaf24_r10_logs/T1.log
a80ee855cb93383c674c2adae0502b08ad07d12675a0923619451e1756d5cdbf  output/ai_factory/_memtest/leaf24_r10_logs/T1_sampler.txt
008affb53bb8aa82baf8dbdbbf91a111e609b0db98161b326060e6502614f6ed  output/ai_factory/_memtest/leaf24_r10_logs/T1_exit.txt
7eaa7c70aff44cad3ebf110bdc0b689c67f1ca7d3f7ca29d8ccc36d1509939cd  output/ai_factory/_memtest/leaf24_r10_logs/T1_ps_before.txt
ae8c603664a5514da09568492b06299730e047ab03ac64fb3fff8c17cbd33296  output/ai_factory/_memtest/leaf24_r10_logs/T1_ps_after.txt
```
T1_c5.txt: empty/absent
