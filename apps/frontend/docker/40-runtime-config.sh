#!/bin/sh
set -eu

API_BASE_URL_VALUE="${API_BASE_URL:-http://localhost:8080}"
APP_NAME_VALUE="${APP_NAME:-Smart Education Platform}"

cat > /usr/share/nginx/html/runtime-config.js <<EOF
window.__APP_CONFIG__ = {
  API_BASE_URL: "${API_BASE_URL_VALUE}",
  APP_NAME: "${APP_NAME_VALUE}"
};
EOF
