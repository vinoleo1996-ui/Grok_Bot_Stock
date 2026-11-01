# gs-quant 参考快照（QuantLab refs）

- **上游**：https://github.com/goldmansachs/gs-quant
- **许可**：Apache-2.0（见 `LICENSE`）
- **钉住提交**：见 `REF_COMMIT.txt`（浅克隆 master；本回合 `bbe7071` / 2026-10-13 release 2.2.1）
- **用途**：架构/API 形态对照，**不是** QuantLab 生产数据源
- **硬禁**：不接 Marquee client_id/secret 作 A 股行情/基本面生产源；不声称 gs-quant 可做 QuantLab 实盘；不把利率/衍生品定价栈当主线

## 包顶层（节选）

见 `PACKAGE_LAYOUT.txt`。主模块：`analytics` · `api/gs`（Marquee）· `backtests` · `data` · `datetime` · `entities` · `instrument` · `markets` · `models` · `risk` · `timeseries` · `tracing` · `workflow`。

吸收计划：`docs/v2/audit/MAIN_GS_QUANT_ABSORB_PLAN_20261025_ZH.md`
