#!/bin/sh
set -eu

until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
  sleep 2
done

for bucket in learning-resources platform-imports platform-exports report-exports; do
  mc mb --ignore-existing "local/$bucket"
  mc anonymous set none "local/$bucket"
done

mc version enable local/learning-resources || true

echo "MinIO buckets are ready and private."
