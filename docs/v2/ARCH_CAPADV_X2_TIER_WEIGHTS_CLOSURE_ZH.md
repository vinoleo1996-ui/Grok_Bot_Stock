# capadv X2 两档 target_weights 相同：结案

- 签署：QuantLab Arch，2026-10-18T10:20:27-04:00
- 结论：按设计如此，不是缺陷。CLOSED。

## 事实（Arch 已复核行号）
1. 权重层只按约束更紧的一档（100万）截断一次：research/g1g5_capacity_adv_weights_hiliq.py（d7fe76b9）L79 AUM_BINDING=1_000_000，L80 ADV_PARTICIPATION_K=0.006，L291-294 单票上限=min(NAME_CAP, k*ADV/AUM_BINDING)。与预注册 STRATEGY_HI_LIQ_SUBSET_PREREG_ZH.md L14/L17 一致。
2. 60万名义金额更小，满足100万的约束必然满足60万，所以两档共用同一份信号层权重（target_weights 都是 b010839d）。
3. 执行层分档：quantlab/portfolio/v2_multisleeve_book.py（6adefbeb）L533 把输入目标原样写出，所以字节相同；L534 的 actual_weights 按档不同（0f8bee14 / 84bd0249）。整手、参与率0.10、sqrt冲击都随 initial_cash 变化，nav c16638ca / aba50300，成本 2.54% / 2.89%。

## 影响与披露
- 100万档：无影响（它就是约束档）。
- 60万档：用的是按100万算的更严单票上限，偏保守，属于预注册口径。报告里须写明。
- 报告必须注明：两档共用 AUM 无关的目标权重，只在成本/容量/执行层分档。

## 对 CMC 的要求
- 表示信号层：base_60w/base_100w 都钉 target_weights b010839d，这样是对的。
- 表示各档实际持仓：改钉各档自己的 actual_weights。后续 CMC 的 .ok 必须写明用哪一种。
- 文件 mtime 01:14 是恢复时留下的，生成时间以 run.log 的 10-14 20:03 ET 为准。
