# 勘误：冻结记录中「__init__ bfdfa63c」的文件归属（Eng，2026-10-18 07:2x ET）

只改记录，不改代码。核对只用了 sha256sum 和 git，没有启动 python。

- bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc 对应 **quantlab/platform/__init__.py**。
  - 现场 sha256sum 与 git HEAD 中该文件的 blob 一致。
  - 纸面 import 链用的就是这个文件：quantlab.platform 先 import execution。
- quantlab/__init__.py 是空文件，sha 为 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855，从未被钉过。
- 以下记录写的是简写「__init__ / __init__.py bfdfa63c」，一律应读作 quantlab/platform/__init__.py：
  - TEAM_STATE 的 Eng 小节（纸面 10-19 行，已改为全路径）；
  - docs/v2/audit/AUDIT_20261018_0225_ET_ZH.md L10；
  - docs/v2/audit/ARCH_SW_L1_GAP_IMPACT_20261018_ZH.md L55（该行已写明 quantlab/platform/ 前缀）；
  - docs/v2/ARCH_AI_LEAF23_24_FIX5_FIX6_REVIEW_ZH.md L28。
- 以下文件早已写明全路径（platform_init / quantlab/platform/__init__.py），无需更正：SD1_SHAS.txt、paper_import_closure.json、各 .ok 的 dep_sha256_platform_init，以及 ARCH_STRATEGY_SW_PIT_ASOF_FIX_R2_REVIEW_ZH.md L210。
- 10-19 纸面例程的 pin 检查对象应为 quantlab/platform/__init__.py = bfdfa63c，以及 quantlab/platform/execution.py = 373fed30。
- 其他 agent 的文档本勘误不动原文，以本文件为准。
