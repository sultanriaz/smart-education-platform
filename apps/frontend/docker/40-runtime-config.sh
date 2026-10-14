#!/bin/sh
set -eu

API_BASE_URL_VALUE="${API_BASE_URL:-http://localhost:8080}"
APP_NAME_VALUE="${APP_NAME:-Smart Education Platform}"

case "$API_BASE_URL_VALUE" in
    http://*|https://*) ;;
    *) echo "API_BASE_URL must be an absolute http(s) URL" >&2; exit 1 ;;
esac
# Restrict to safe JS-string characters. Avoid shell/JS string injection from
# a malformed ConfigMap value; names intentionally permit ordinary spaces.
if ! printf '%s' "$API_BASE_URL_VALUE" | LC_ALL=C grep -Eq '^[A-Za-z0-9:/_.?&=%#~+@-]+$'; then
    echo "Unsafe API_BASE_URL characters" >&2; exit 1
fi
if ! printf '%s' "$APP_NAME_VALUE" | LC_ALL=C grep -Eq '^[A-Za-z0-9 .,()_/-]+$'; then
    echo "Unsafe APP_NAME characters" >&2; exit 1
fi

cat > /tmp/runtime-config.js <<EOF
window.__APP_CONFIG__ = {
  API_BASE_URL: "${API_BASE_URL_VALUE}",
  APP_NAME: "${APP_NAME_VALUE}"
};
EOF
