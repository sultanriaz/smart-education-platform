#!/bin/sh
set -eu

attempt=0
until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "Object storage was unavailable after 30 attempts." >&2
    exit 1
  fi
  sleep 2
done

for bucket in learning-resources platform-imports platform-exports report-exports; do
  mc mb --ignore-existing "local/$bucket"
  mc anonymous set none "local/$bucket"
done

mc version enable local/learning-resources

ensure_user() {
  user="$1"
  password="$2"
  policy="$3"
  policy_file="$4"

  mc admin policy create local "$policy" "$policy_file" >/dev/null 2>&1 || \
    mc admin policy info local "$policy" >/dev/null

  mc admin user add local "$user" "$password" >/dev/null
  mc admin policy attach local "$policy" --user "$user" >/dev/null
}

ensure_user learning_svc "$LEARNING_S3_SECRET" learning-policy /policies/learning-policy.json
ensure_user platform_svc "$PLATFORM_S3_SECRET" platform-policy /policies/platform-policy.json
ensure_user reporting_svc "$REPORTING_S3_SECRET" reporting-policy /policies/reporting-policy.json

echo "Private buckets and least-privilege application users are ready."
