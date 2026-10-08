#!/bin/sh
set -eu

API_BASE_URL_VALUE="${API_BASE_URL:-http://localhost:8080}"
ENABLE_HSTS_VALUE="${ENABLE_HSTS:-false}"

case "$API_BASE_URL_VALUE" in
  http://*|https://*) ;;
  *)
    echo "API_BASE_URL must begin with http:// or https://" >&2
    exit 1
    ;;
esac

case "$API_BASE_URL_VALUE" in
  *" "*|*";"*|*'"'*)
    echo "API_BASE_URL contains unsafe characters for CSP generation" >&2
    exit 1
    ;;
esac

mkdir -p /etc/nginx/security

cat > /etc/nginx/security/security-headers.conf <<EOF
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header X-Permitted-Cross-Domain-Policies "none" always;
add_header X-DNS-Prefetch-Control "off" always;
add_header Content-Security-Policy "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' ${API_BASE_URL_VALUE}; worker-src 'self' blob:; manifest-src 'self'" always;
EOF

if [ "$ENABLE_HSTS_VALUE" = "true" ]; then
  cat >> /etc/nginx/security/security-headers.conf <<EOF
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
EOF
fi
