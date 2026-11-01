# DataHub 经本机 Clash 出口（云端）

## 现象
- 云端 DNS：`datahubco.com` → `198.18.0.1`（fake-ip），直连超时
- 本机 DNS：`datahubco.com` → `47.76.174.222`，`NO_PROXY=*` 直连可用

## 已验证可用出口
- 本机 Clash Verge mixed-port：`127.0.0.1:7897`
- 云端经 Tailscale 访问：`http://100.102.49.98:7897`（机器 `dxcc2cvxyp`）
- 验证：`GET https://datahubco.com/app-api/openapi/v1/tushare/stock-basic?limit=3` → HTTP 200，`code=0`，3 条

## 调用约定（云端）
```bash
export HTTPS_PROXY=http://100.102.49.98:7897
export HTTP_PROXY=http://100.102.49.98:7897
# 仅对 datahub 使用；勿全局污染其他源
curl -x "$HTTP_PROXY" -L -H "X-API-Key: $DATAHUB_API_KEY" \
  "https://datahubco.com/app-api/openapi/v1/tushare/stock-basic?limit=3"
```

## 注意
- Clash 配置里 `allow-lan: false`；当前 Tailscale 路径可用，但若你改 Clash/断 Tailscale 会失效
- 更稳：Clash 开「允许局域网」或做 SSH 反向隧道把 7897 映到云端 localhost
- 密钥仅存 `/workspace/QuantLab/.env.datasources` 的 `DATAHUB_API_KEY`
