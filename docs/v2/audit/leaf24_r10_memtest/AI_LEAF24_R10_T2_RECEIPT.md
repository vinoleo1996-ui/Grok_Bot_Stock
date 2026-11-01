# AI_LEAF24_R10_T2_RECEIPT (build_FULLA)

- run: 2026-10-18 08:04:54 -> 08:07:01 ET via bash /tmp/l24r10_T2_wrapper.sh (non-interactive), STOPKB=1484800, SCR=/workspace/QuantLab/output/ai_factory/_memtest/leaf24_r10, uni=FULLA
- wrapper sha256: 99464996d81b29d702239c2dfbb4098a8a92939655f15f985d5366fc5dffc2b2 (T1 wrapper with T1->T2, HILIQ->FULLA, 1331200->1484800; bash -n OK)
- step table sha256: d1cf24d8741175c0d598116b1f761190de69edb3ca6df85971911cbee6d7ed3b (commit 875b8eae9dcc622eb96128725514915ebb85caf3)
- .ok sha256: 8805b823d2e20a3b1026a038735bd765049265ca4e2fd3d4d46c407a8d792b30 (test=build_FULLA, expires 12:00 ET)
- precheck 08:04 ET: lock RESEARCH_QUIET 6afb7c1892a3 OK; ps only system daemons + 94322 Tsl; r10 53d3f8b1 / harness 7dac5761 / fund_resid 2b49b10b; no formal out_dir / g1g5_imax_intraday_*; T1 HILIQ meta+outputs present, no FULLA products; MemAvailable 9375760 kB; niceness 0

## Result
- MEMTEST_END test=build_FULLA vmhwm_kb=1105672 vmhwm_mib=1079.8 vmrss_kb=452868 target_1300mib=within
- WRAPPER_DONE rc=0 stopped=0; exit=0 stopped=0; PGID cleared (no PGID_ALIVE)

## C1-C5
- C1 PASS: exit 0
- C2 PASS: meta stage=build_FULLA, script 53d3f8b1, arch_ok 8805b823, variant primary, uni FULLA, 7 outputs sha verified (sha256sum -c OK); external_outputs absent, _ext_root no files; T1 meta check by harness passed (no STOP)
- C3 PASS: MEMTEST_START x1, peak_check build x6, peak_check memtest end x1, MEMTEST_END x1, no STAMP; C3b PASS: no RSS_GUARD_KILL/RSS_WATCHDOG_ERROR/STOP/refused/Traceback
- C4 PASS: VmHWM 1105672 kB <= 1536000 and < stop 1484800; meta peak_rss_mb 1079.76 < 1500; target_1300mib=within
- C5 PASS: c5watch no hit (T2_c5.txt absent); sampler 118 lines, no STOPLINE/PGID_MISMATCH; ps before/after: only system daemons + 94322 (Tsl)

## sha256
```
f8d2e707394dd78ee117d89080a85e58063697328cd53b6fdebb5c28c81b48ab  output/ai_factory/_memtest/leaf24_r10/alpha_FULLA_2024.parquet
c6ae7046bc50a823e58e5e37e77b6edbc9129e6ce3d2c8773018fc1d9015ed5c  output/ai_factory/_memtest/leaf24_r10/alpha_FULLA_2025.parquet
4c9887daa0d79d2956646f08f4e9a6d2438dafa8a2ca3d9bc137e326f54b4970  output/ai_factory/_memtest/leaf24_r10/alpha_FULLA_2026.parquet
fd5822e029e28d740921330762d56b51e2090d4dc115ea38880fd8b48cc2d9e1  output/ai_factory/_memtest/leaf24_r10/coverage_FULLA.parquet
6ec6f0bcc335466b480cdb669606875c14eeeb4d8083c6708e14a37695c039e0  output/ai_factory/_memtest/leaf24_r10/gate_FULLA_2024.parquet
5c2f4a9370b9457faa5ed0a87173c2abb676076e6820642fdb45992133a562cd  output/ai_factory/_memtest/leaf24_r10/gate_FULLA_2025.parquet
d8448ad6b28c614160af510a84975129486eb16582343e4bdaafb59bb84dd354  output/ai_factory/_memtest/leaf24_r10/gate_FULLA_2026.parquet
2694477cc95ccf5e3bf5597d32e01b4a851c700c159b6dc0b08e4b5c7d000fd9  output/ai_factory/_memtest/leaf24_r10/build_FULLA_meta.json
7343d667836b0d39ece5eafd6c8447327a3fe92bc1c873c29e02a358d9111f96  output/ai_factory/_memtest/leaf24_r10_logs/T2.log
16cfcb4a8ef05d2accdd532fb92b58e1da4c48f27b6550a7fcea76e471794448  output/ai_factory/_memtest/leaf24_r10_logs/T2_sampler.txt
008affb53bb8aa82baf8dbdbbf91a111e609b0db98161b326060e6502614f6ed  output/ai_factory/_memtest/leaf24_r10_logs/T2_exit.txt
8efe155992f49490a714c6df2f1e8091223ff4d5d8a20eb4880b262dc841b768  output/ai_factory/_memtest/leaf24_r10_logs/T2_ps_before.txt
d064d228d670dc72ba1751d3bbc51586758a4b7589a2f2b979a73aa4dba47bce  output/ai_factory/_memtest/leaf24_r10_logs/T2_ps_after.txt
```
T1 HILIQ files untouched (sha prefixes): 0ccc0f96 70a2cc47 5a1fc629 38dc39ab e8278e47 b58f48d3 b7bcc527 d3282894 
