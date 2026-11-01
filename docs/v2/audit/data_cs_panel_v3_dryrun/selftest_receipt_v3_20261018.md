# 单测回执 · test_sd1_common.py（SD1 r6b / v3 dry-run 前置）

- 时间：开始 2026-10-18 02:36:25 EDT；结束 2026-10-18 02:36:25 EDT（America/New_York）；执行人：QuantLab Data；live=false，promotion=false
- 命令：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/QuantLab/.venv_opt/bin/python3 scripts/fix_sd1/test_sd1_common.py`
  - 说明：本文件是 Arch 钉死的独立合成单测脚本（非 pytest 用例）；docstring 要求 `python3 scripts/fix_sd1/test_sd1_common.py`。环境无 `/usr/bin/time`，峰值 RSS 用外层 `python3` + subprocess 读 `resource.getrusage(RUSAGE_CHILDREN).ru_maxrss`（外层不 import 任何项目模块）。
- 授权核对（运行前）：
  - `output/data/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok` sha256=a7159eca51dcf65a769b420039ff194aab6d48520dfda3e04a9c71ab46276959（与 Arch 签发一致）
  - scope=selftest；allow_selftest=true；allow_real_data=false；其余 allow_*=false；out_dir=mkdtemp；expires_et=2026-10-19T02:31:43-04:00（未过期）
  - 旁证：v3 dry-run `.ok` `ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_v3.ok` sha256=dac5f6dd7ee6e011101a6201db7a1b113d8fb1f12f8824711da86787ba2b2124（本次未使用，仅核对存在）
- 钉死文件：
  - runner `scripts/fix_sd1/test_sd1_common.py` sha256=892401e5ec99e6471f5aa3a18ab68bf9adcd2c28cd1b9cc868f95cbb8cbed32f
  - dep `scripts/fix_sd1/sd1_common.py` sha256=c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa
- 结果：exit 0；stdout 含 `ALL SYNTHETIC TESTS PASS`。单测为单个 `run()`，遇错即停；失败 0。
- 峰值 RSS：105,864 KB（约 103 MB），远低于 1.5GB 上限。
- 内存：运行前 MemAvailable ≈ 11,490,456 KB（约 11.0 GB）≥ 2GB。
- 未读真实数据：门禁 allow_real_data=false；测试仅构造内存 Synthetic DataFrame / ResumeState，写入 mkdtemp 后 rmtree；未触碰 parquet/面板路径。
- 未做：未跑 D1a/D1b/D2/D3D4；未对 94403/212762 发 STOP/CONT；未触 moneyflow；未启 8787。
- stdout 落盘：`docs/v2/audit/data_cs_panel_v3_dryrun/selftest_stdout_20261018.txt`
