#!/usr/bin/env bash
# Usage: datahub_curl.sh <api-path> [curl query args...]
# Example: datahub_curl.sh /app-api/openapi/v1/tushare/stock-basic --data-urlencode limit=3
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
set -a; source "$ROOT/.env.datasources"; set +a
PROXY="${DATAHUB_HTTP_PROXY:-http://100.102.49.98:7897}"
PATH_API="${1:?api path}"; shift || true
exec curl -sS -L --connect-timeout 20 --max-time 120 \
  -x "$PROXY" \
  -H "X-API-Key: ${DATAHUB_API_KEY}" \
  -G "https://datahubco.com${PATH_API}" \
  "$@"
