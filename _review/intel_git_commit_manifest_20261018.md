# research/intel git 提交清单（给 Arch，仅准备）
生成时间：2026-10-18 05:48 ET｜仓库 /workspace/QuantLab，HEAD b172f48｜research/intel/ 目前整个目录未跟踪（`?? research/intel/`）。
**这份清单只是准备材料。我没有执行 git add、commit 或 push，也没有改 .gitignore。**

## A. 建议纳入（18 个文件）
### A1. research/intel/*.py
其中 5 个是本次 r3 落地的文件（有 * 标记），sha 与 Arch .ok 49ac45a9 的 new 一致，回执见 docs/v2/audit/intel_sw_pit_r3_selftest/RECEIPT.md（3bef754d）。
| 文件 | sha256 | 字节 |
|---|---|---|
| research/intel/build_ai_earnings_surprise.py | 5102c289e9707d9c0668b45357ba7f8d6b4180159ab72bef72f7c7186550fd15 | 4592 |
| research/intel/build_cpi_consensus.py | acf96477b190ef04bb3a6c123867ac615493cae63031a79604df92a146a47223 | 2803 |
| research/intel/build_tsmc_guidance.py | 42ad5ba589ffc39299677b47fa6a6534b75407153d5ac7e552390b8bb109e8ee | 3528 |
| research/intel/collect_ai_earnings_cnbc.py | fa31af5cd4873bc145a0f820908d2b2367926a0191c43753dc61d7fc6e4d6cda | 2519 |
| research/intel/intel_ai_earnings_event_study.py | b0784e2d48155b840d5285c3615868408536bca8808aae4676d5582efdf86c81 | 4518 |
| research/intel/intel_c1_gap_split.py * | a5edf0feed0cb56331b7a0915780ce281f51b6f2771468be6ca746f78466c8a6 | 6927 |
| research/intel/intel_common.py * | 25f23dff40e09c1724011bc1bfeb3eefa0bb1a924af67e2ccf27664f65dce74a | 22019 |
| research/intel/intel_cpi_tsmc_event_study.py | 8cc4142bedd74afef2aba1ea9651a6b60eea61cec05b90cd605a12a710b22ff7 | 5922 |
| research/intel/intel_event_study.py * | b211b21120e5f2eca77e283674b87e2bddefd28d990fe2467dfae8cf84d5cb4d | 6541 |
| research/intel/intel_pit_candidates_study.py | af374e736a0299bf2978409f79234792afd4dab41efa704c8868c3692e61d0f1 | 5145 |
| research/intel/intel_run.py * | ecebb10b79790e46e7c645ce75fd4453cf9d79a5c6ef0d5a947bd9cde0fa99d6 | 15693 |
| research/intel/parse_ai_earnings_cnbc.py | 42fda2646e243b341d976abaf4ebb00ad78fa813c8039bf67e9a173db26316a1 | 3426 |
| research/intel/test_intel_run_merge.py | 0c56eab412c137996506eaea8f91bf00b7175b97148dab32144082104739f374 | 2859 |
| research/intel/test_news_classifier.py | cc41a3b1974ea0c8ec580ea0e5c5f3f7e5f94bed41c7ec1514984318c876cbf7 | 4187 |
| research/intel/test_sw_freshness.py * | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33 | 13090 |

### A2. research/intel/weekly/*.py（3 个都建议纳入）
weekly 是周报和 ALERTS 后处理的复现脚本，已有产出（WEEKLY_20261017_2359、ALERTS events）依赖它们。
| 文件 | sha256 | 字节 |
|---|---|---|
| research/intel/weekly/alerts_postprocess_20261018.py | f8fed85a07b4db2c795ca37f295cb311c2a508740a18177992f498ae28beb627 | 11114 |
| research/intel/weekly/paper_exposure.py | 82d0ee6b914b0f7e7b3aca09972513e147f5b847abafdcd61c257bf230c8323c | 2041 |
| research/intel/weekly/weekly_charts_20261017.py | 5c05d22345aae4f2fb492f24db57080f8e1c4dd14a46c4c91b9407e7a6452f0a | 12702 |
提请 Arch 注意以下几点：
- weekly/paper_exposure.py 用 `out_date.isna()` 取的是当前成分，不是团队现行的 as-of PIT 口径（in_date<d、out_date 为空或 out_date>=d）。它只用来对 10-14 纸面持仓做暴露快照，属于只读用途，但不符合 PIT 标准。建议两种处理之一：纳入时在提交信息里写明是"非 PIT 快照"；或者先排除，等改成 PIT 口径后再纳入。改代码需要另签 .ok。
- weekly 下的脚本写死了 /workspace/QuantLab 的绝对路径，周报脚本还依赖 weekly_data/ 下的 Yahoo json，这些数据不在仓库里。
- 全部 .py 中都没有 token、密钥或密码字面量（rg 检查过）。

## B. 建议排除
| 文件 | sha256 | 字节 | 理由 |
|---|---|---|---|
| research/intel/intel_common.py.bak_0526 | 7c568b04894aeac3a20bfc06238c71aa79f68f75f31a2cc4bc89d78e55d52090 | 8690 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/intel_common.py.bak_20261018_0040_prefix | 7d8716a9ffb44e28797ba618f293c680f6eb8b4136ee0b084503002a2f36f2a8 | 10536 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/intel_common.py.bak_20261018_0120_hormuz | 0c60fb5480b6a4077eb513aa534ada1db4c7384092b8abbbe1cf6f53a8cadd11 | 11798 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/intel_common.py.bak_20261018_newsclf | 83969948a42d0011d40601e77e07cc32b49fd9f85bd6fb98870ace19ffd1882f | 9204 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/intel_run.py.bak_0526 | 57ef4ffafb6591f43adf25636aca4576747fab5afff4e567f4ae03c715971d83 | 9991 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/intel_run.py.bak_20261018_0125_merge | 805aa008e0d60587e31525d65d33a2462b2976cb8504bcc21a0101450ae95f0a | 10059 | 手工备份，旧版已有 sha 留证，或已归档在 _recovery/ |
| research/intel/__pycache__/intel_common.cpython-312.pyc | db0317f324cd14addbe7e9d442da6f1a5ffb45285b3cf039b42ad55a485cad6b | 15808 | 字节码 |
| research/intel/__pycache__/intel_common.cpython-313.pyc | 7ec76a9fd8d595cf2db46905abc3aece1f2a2173d27645bd432d8fc56f7f4ab2 | 15935 | 字节码 |
| research/intel/__pycache__/intel_run.cpython-312.pyc | 4857680271570f398dbfb5ca6d6a3629c08e3f100c2272016797b35e6a4bf39f | 24564 | 字节码 |
| research/intel/__pycache__/intel_run.cpython-313.pyc | c04f091b310ff885bbff4c25b28188ae2943e44408036597b704b8558426ca47 | 24927 | 字节码 |
| research/intel/__pycache__/test_news_classifier.cpython-312-pytest-9.1.1.pyc | 31a03a50965e98bf86dd19ad2f086f1beb54edb82b213e67a5254dc5cbe67828 | 5708 | 字节码 |

## C. .gitignore
- `__pycache__/` 和 `*.pyc` 已经被现有 .gitignore 第 4、6 行（`**/__pycache__/`、`*.pyc`）忽略，`git check-ignore` 已确认，不需要改。
- `*.bak_*` 目前没有被忽略。如果直接 `git add research/intel/`，会把 6 个 .bak 文件一起加进去。两种做法：
  1. **推荐**：只按 A 节列出的路径逐个 add，不改 .gitignore。
  2. 如果想一劳永逸，在 .gitignore 加一行 `research/intel/*.bak_*`（或全局的 `*.bak_*`）。这一步需要 Arch 批准，而且要先确认仓库里其他地方没有需要跟踪的 .bak 文件。

## D. 拟用命令（等 Arch 批准，我不执行）
```
cd /workspace/QuantLab && git add research/intel/build_ai_earnings_surprise.py research/intel/build_cpi_consensus.py research/intel/build_tsmc_guidance.py research/intel/collect_ai_earnings_cnbc.py research/intel/intel_ai_earnings_event_study.py research/intel/intel_c1_gap_split.py research/intel/intel_common.py research/intel/intel_cpi_tsmc_event_study.py research/intel/intel_event_study.py research/intel/intel_pit_candidates_study.py research/intel/intel_run.py research/intel/parse_ai_earnings_cnbc.py research/intel/test_intel_run_merge.py research/intel/test_news_classifier.py research/intel/test_sw_freshness.py research/intel/weekly/alerts_postprocess_20261018.py research/intel/weekly/paper_exposure.py research/intel/weekly/weekly_charts_20261017.py  && git status --short research/intel
```

## E. 拟用提交信息
```
Intel: track research/intel (incl. sw_pit freshness r3; Arch code-change .ok 49ac45a9)

- r3: intel_common/intel_run/intel_event_study/intel_c1_gap_split + test_sw_freshness.py
  (sha = .ok new; review 3406b576; selftest .ok a907c614 → 59/29/11 passed,
  receipt docs/v2/audit/intel_sw_pit_r3_selftest/RECEIPT.md 3bef754d)
- plus previously approved intel modules, tests and weekly/ reproduction scripts
- excluded: *.bak_* backups, __pycache__ (already ignored)
Research-only, live=false.
```
