# 冻结记录补注：曾未提交但已钉定（Eng，2026-10-18 09:27 ET）

以下三个文件此前未提交，或从未进过 git，但 paper_import_closure.json、SD1_SHAS、EXEC.ok c054a9c9 和 SD0 对拍（f66048ed）钉的都是它们当时的工作区版本。现已原样 commit，内容未改。

- quantlab/portfolio/v2_multisleeve_book.py：6adefbeb…（原为未提交改动，git HEAD 旧版是 a036c10a）
- quantlab/portfolio/b4_paper.py：ffe195e6…（原为未跟踪文件）
- quantlab/metrics.py：a822dfee…（原为未跟踪文件）
- patch 备档：docs/v2/eng_sd1/PATCH_v2_multisleeve_book_metrics_unify.patch，sha 19a06f7f…，与 git diff 的 sha 一致

提交信息：
- commit 1efbf6557189912cd7fdf47b393727fc9e6d3e99，parent fb7433ab；
- 授权：Arch .ok 74f85e6b，主 Agent 07:21 裁定选 ①，09:23 授权；
- 前后两次 sha 核对都一致：git show HEAD:<path> 和工作区的 sha 都等于钉值，留证在 /workspace/sd1_work/commit_pinned_20261018/。

影响范围：改动只涉及 metrics() 输出的 summary 统计，共 5 个数，权重、成交和 NAV 都不受影响；涉及 10-13、10-14 两天的纸面。全程没起 python，也没有 push。
