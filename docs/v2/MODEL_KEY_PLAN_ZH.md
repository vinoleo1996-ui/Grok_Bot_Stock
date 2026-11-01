# 模型/数据源密钥管理方案（一页，只写方案，不存密钥）

## 现状
- 数据源密钥在 `/workspace/QuantLab/.env.datasources`（DATAHUB_API_KEY、TSPRO_PROXY_KEY、DATAHUB_HTTP_PROXY），不进 git，由脚本 `source`/逐行读入。
- 第三档文本流水线（公告/新闻/研报摘要、嵌入）以后会用到 LLM / Embedding 密钥，目前还没有统一位置。

## 方案
1. **单一来源**：所有密钥放在 box 上的 `~/.config/quantlab/secrets.env`（权限 600，属主 box），按用途分组：`DS_*`（数据源）、`LLM_*`（对话模型）、`EMB_*`（向量）。`.env.datasources` 保留成兼容软链接或过渡文件。
2. **不入库**：`.gitignore` 覆盖 `*.env*`、`secrets*`；pre-commit 加 gitleaks（或 `rg -e 'sk-|api[_-]?key'`）扫描；manifest、日志、parquet 里一律不写密钥，日志打印时脱敏（只留后 4 位）。
3. **加载方式**：统一用 `quantlab/config/secrets.py` 的 `get_secret(name)`，读取顺序是 环境变量 → secrets.env，缺失直接报错，不留默认值；夜间脚本也只走这个入口。
4. **最小权限**：每个用途一把 key（数据拉取、研究 LLM、线上 live 分开），live/策略层的 key 不放在研究 box 上；能设额度/限流的平台都设月度上限。
5. **轮换**：每 90 天轮换一次，或怀疑泄露时立即轮换。轮换步骤：生成新 key → 更新 secrets.env → 跑 `scripts/nightly_update.py --dry-run` 验证 → 吊销旧 key。轮换日期记在 `docs/v2/KEY_ROTATION_LOG.md`（只记日期和用途，不记值）。
6. **Mac 侧**：Mac 端 8787 接口只读 parquet，不需要任何上游密钥；如果以后要用，走 macOS Keychain，不同步 box 的 secrets 文件。
7. **审计**：每月用 `rg` 扫描 output/、logs/、data_v2_bundle/，确认没有密钥落盘。

## 未决
- LLM 供应商和预算由 Leo 定；定了之后只按本方案新增 `LLM_*` 变量名，不改架构。
