# AI_LEAF24_R10_T3_RECEIPT (build_FULLA_win60)

- run: 2026-10-18 08:09:17 -> 08:11:32 ET via bash /tmp/l24r10_T3_wrapper.sh (non-interactive), STOPKB=1484800, SCR=/workspace/QuantLab/output/ai_factory/_memtest/leaf24_r10_win60, uni=FULLA
- wrapper sha256: dd3bb7ffd4f14c55c05a7d822cdf6a5c62bc196f3b451745a9a8847c599597ec (from T2 wrapper: T2->T3, SCR->leaf24_r10_win60, --test build_FULLA_win60, .ok BUILD_FULLA_WIN60; bash -n OK)
- step table sha256: d1cf24d8741175c0d598116b1f761190de69edb3ca6df85971911cbee6d7ed3b (commit 875b8eae9dcc622eb96128725514915ebb85caf3)
- .ok sha256: 95aed3df50e12c57bf75005731414f01c6819cfa0fe8663704d6ff812bf394c0 (44 keys, LF, test=build_FULLA_win60, allow_sensitivity=true, expires 12:00 ET); .ok archival: pending Arch archival (dai Arch gui dang)
- precheck 08:09 ET: lock RESEARCH_QUIET 6afb7c1892a3 OK; ps only system daemons + 94322 Tsl; r10 53d3f8b1 / harness 7dac5761 / fund_resid 2b49b10b; no formal out_dir / g1g5_imax_intraday_*; leaf24_r10_win60 absent; MemAvailable 8842176 kB; niceness 0

## Result
- MEMTEST_END test=build_FULLA_win60 vmhwm_kb=1076764 vmhwm_mib=1051.5 vmrss_kb=474532 target_1300mib=within
- WRAPPER_DONE rc=0 stopped=0; exit=0 stopped=0; PGID cleared
- note: VmHWM 1051.5 MiB is ~28 MiB BELOW T2 (1079.8 MiB), not +150-250 MiB as estimated

## C1-C5
- C1 PASS: exit 0
- C2 PASS: meta stage=build_FULLA, variant=win60, script 53d3f8b1, arch_ok 95aed3df, uni FULLA, 7 outputs sha verified (sha256sum -c OK); external_outputs absent, _ext_root no files
- C3 PASS: MEMTEST_START x1, peak_check build x6, peak_check memtest end x1, MEMTEST_END x1, no STAMP; C3b PASS: none of RSS_GUARD_KILL/RSS_WATCHDOG_ERROR/STOP/refused/Traceback
- C4 PASS: VmHWM 1076764 kB <= 1536000 and < stop 1484800; meta peak_rss_mb 1051.53 < 1500; target_1300mib=within
- C5 PASS: c5watch no hit (T3_c5.txt absent); sampler 133 lines, no STOPLINE/PGID_MISMATCH; ps before/after: only system daemons + 94322 (Tsl)

## sha256
```
456f29628adf96ff7145f28543785c39a1bce5c35fedb3ed3e6810eecbefeb2f  output/ai_factory/_memtest/leaf24_r10_win60/alpha_FULLA_2024.parquet
e935d5501fd5e8717dea421ad920c00fbc2c58a25e0b204630b15e20674b9435  output/ai_factory/_memtest/leaf24_r10_win60/alpha_FULLA_2025.parquet
a36e7d2392ebdb1a989bbe057dfbd27e584e533d482d4067f68f591053c67914  output/ai_factory/_memtest/leaf24_r10_win60/alpha_FULLA_2026.parquet
b8901f1d61d3fd0529c696fc3eda245d4e8e9061af8dddde0dbfbb2ed087bcba  output/ai_factory/_memtest/leaf24_r10_win60/coverage_FULLA.parquet
6ec6f0bcc335466b480cdb669606875c14eeeb4d8083c6708e14a37695c039e0  output/ai_factory/_memtest/leaf24_r10_win60/gate_FULLA_2024.parquet
5c2f4a9370b9457faa5ed0a87173c2abb676076e6820642fdb45992133a562cd  output/ai_factory/_memtest/leaf24_r10_win60/gate_FULLA_2025.parquet
d8448ad6b28c614160af510a84975129486eb16582343e4bdaafb59bb84dd354  output/ai_factory/_memtest/leaf24_r10_win60/gate_FULLA_2026.parquet
a6ccc32a21be248c713a195e58f417d15e8748f58905f65ba3702819feef850c  output/ai_factory/_memtest/leaf24_r10_win60/build_FULLA_meta.json
2d7a43bb806d0afa021e7c9377dfadc389ec8dcc44d53b107d312ed0dd63ec1d  output/ai_factory/_memtest/leaf24_r10_logs/T3.log
22ae17dd78671a5202d46fa71e276c1e4df4aa8bcb5cb18fa89f19a5b941bc52  output/ai_factory/_memtest/leaf24_r10_logs/T3_sampler.txt
008affb53bb8aa82baf8dbdbbf91a111e609b0db98161b326060e6502614f6ed  output/ai_factory/_memtest/leaf24_r10_logs/T3_exit.txt
a8ee19e3f5bc30ec6eac246f0700db94264e147d4ba95ab7207bbd358304a8ec  output/ai_factory/_memtest/leaf24_r10_logs/T3_ps_before.txt
9fc396e6c738f1e8eaf239ebd4a6bd4788874ac0b415dcab6e17220a72843802  output/ai_factory/_memtest/leaf24_r10_logs/T3_ps_after.txt
```
