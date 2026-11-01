# SW L1 PIT v2 修复方案 r3.2（只含对 r3.1 的增量：Arch 新 P2-A）

- 作者：QuantLab Data；生成时间 2026-10-18T11:02:38-04:00（ET，date 生成）。新文件，不改 r3.1（docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r3_1.md，daa19d26）。
- 依据：Arch 审查 docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）§1.1「新 P2-A」与 §6 第 1 条。
- 本文只是代码文本，未落 repo、未运行任何测试；落地仍在 10-19 纸面跑完之后，另签 code-change .ok（签确切文本）。
- 除本节替换的测试函数外，r3.1 其余内容（含 validate_repull_dir，r3.1 L284-312）一字不改。

## 1. 问题（Arch P2-A）
r3.1 L365-385 的 test_repull_dir_validation_r3_1：L369 先取 done=now，L373 才写 801010.SI_Y.parquet，所以文件 mtime 晚于 done；validate_repull_dir 的 L307（`done.timestamp() < max(mtime)` → 「completed_et 早于目录内文件 mtime」）会让 L376 的正例直接抛错。另外 L385 期望的子串「早于」同时匹配 L306 与 L308 两条消息，区分不了。

## 2. 改法
- 先写文件，再取 done；并用 os.utime 把文件 mtime 明确设到 done 之前 1 秒（不依赖文件系统时间戳粒度与时钟精度）。
- 「未来」「早于签发」两例按新顺序复核（见 §3 注释），期望消息改为各自的完整短语。
- 新增一例专测 L307：文件 mtime 设到 done 之后 60 秒、签发时间很早，应只触发「completed_et 早于目录内文件 mtime」。

## 3. 替换文本（替换 r3.1 L365-385 整个函数）
```python
# ===== r3.2: 替换 r3.1 test_repull_dir_validation_r3_1 (r3.1 L365-385); Arch 11cb0690 P2-A =====
def test_repull_dir_validation_r3_2():
    root = _tmp()
    raw = root / "index_member_all"
    raw.mkdir()
    stamp = pd.Timestamp.now(tz="America/New_York")
    rp = root / f"index_member_all_{stamp:%Y%m%d}_213000"
    rp.mkdir()
    f = rp / "801010.SI_Y.parquet"
    pd.DataFrame({"a": [1]}).to_parquet(f)                       # 先写文件
    done = pd.Timestamp.now(tz="America/New_York")                # 再取 done (P2-A)
    t_file = (done - pd.Timedelta(seconds=1)).timestamp()
    os.utime(f, (t_file, t_file))                                  # mtime 明确早于 done, 不靠时钟粒度
    cj = {"files": {f.name: B.sha(f)}, "completed_et": done.isoformat(), "pull_ok_sha256": "x"}
    (rp / "COMPLETE.json").write_text(json.dumps(cj))
    SIGN_OK = "2026-01-01T00:00:00-05:00"                          # 早于文件 mtime 与 done
    # 正例: L297 signed<=done, L299 done<=now, L304 mtime>signed, L307 done>=mtime, L310 sha 一致
    got, t = B.validate_repull_dir(rp, SIGN_OK, "x", raw0108=raw, n_files=1)
    assert t == pd.Timestamp(done.isoformat())
    assert got == {f.name: B.sha(f)}
    _raises(lambda: B.validate_repull_dir(rp, SIGN_OK, "y", raw0108=raw, n_files=1), "pull_ok_sha256")
    _raises(lambda: B.validate_repull_dir(rp, "2099-01-01T00:00:00-05:00", "x", raw0108=raw, n_files=1), "晚于 completed_et")
    _raises(lambda: B.validate_repull_dir(rp, "2026-01-01T00:00:00", "x", raw0108=raw, n_files=1), "时区")
    _raises(lambda: B.validate_repull_dir(raw, SIGN_OK, "x", raw0108=raw, n_files=1), "RAW_0108")
    # 未来: now 注入为 done 前一天 -> L299 先于 mtime 检查触发
    past = done - pd.Timedelta(days=1)
    _raises(lambda: B.validate_repull_dir(rp, SIGN_OK, "x", raw0108=raw, n_files=1, now=past), "completed_et 在未来")
    # L307: 文件 mtime 晚于 done 60 秒 (签发很早, L304 不触发; done 仍不在未来)
    t_late = (done + pd.Timedelta(seconds=60)).timestamp()
    os.utime(f, (t_late, t_late))
    _raises(lambda: B.validate_repull_dir(rp, SIGN_OK, "x", raw0108=raw, n_files=1, now=done + pd.Timedelta(minutes=5)), "completed_et 早于目录内文件 mtime")
    # L304: 文件 mtime 早于签发时间 (签发 2026-06-01 仍早于 done, L297 不触发)
    t_old = pd.Timestamp("2026-01-01T00:00:00-05:00").timestamp()
    os.utime(f, (t_old, t_old))
    _raises(lambda: B.validate_repull_dir(rp, "2026-06-01T00:00:00-04:00", "x", raw0108=raw, n_files=1), "早于 pull .ok 签发时间")
```
- 第 4 例（L307）注入 now = done + 5 分钟，是为了让「未来」检查与真实时钟无关；validate_repull_dir 已支持 now 参数（r3.1 L299）。
- 消息子串均取自 r3.1 L295、L298、L300、L306、L308 的原文。

## 4. selftest 与 .ok
- selftest 仍按 r3.1 §6 的 scope=selftest、allow_real_data=false、out_dir 在 /tmp 下；本函数只用 _tmp() 下的临时目录，不读真实数据。
- code-change .ok 签 r3.1 全文 + 本文 §3 替换文本；本文 sha 写进 .ok。
