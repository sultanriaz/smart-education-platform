#!/bin/sh
set -eu

escape_literal() {
  printf "%s" "$1" | sed "s/'/''/g"
}

ensure_role_and_db() {
  role="$1"
  db="$2"
  password="$3"
  escaped_password="$(escape_literal "$password")"

  role_exists="$(psql -U "$POSTGRES_USER" -d postgres -tAc \
    "SELECT 1 FROM pg_roles WHERE rolname='${role}'")"
  if [ "$role_exists" != "1" ]; then
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c \
      "CREATE ROLE ${role} LOGIN PASSWORD '${escaped_password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;"
  fi

  db_exists="$(psql -U "$POSTGRES_USER" -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${db}'")"
  if [ "$db_exists" != "1" ]; then
    createdb -U "$POSTGRES_USER" -O "$role" "$db"
  fi

  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$db" -c \
    "REVOKE CREATE ON SCHEMA public FROM PUBLIC; GRANT USAGE, CREATE ON SCHEMA public TO ${role};"
}

ensure_role_and_db identity_svc identity_db "$IDENTITY_DB_PASSWORD"
ensure_role_and_db academic_svc academic_db "$ACADEMIC_DB_PASSWORD"
ensure_role_and_db attendance_svc attendance_db "$ATTENDANCE_DB_PASSWORD"
ensure_role_and_db scheduling_svc scheduling_db "$SCHEDULING_DB_PASSWORD"
ensure_role_and_db notification_svc notification_db "$NOTIFICATION_DB_PASSWORD"
ensure_role_and_db facility_svc facility_db "$FACILITY_DB_PASSWORD"
ensure_role_and_db learning_svc learning_db "$LEARNING_DB_PASSWORD"
ensure_role_and_db assessment_svc assessment_db "$ASSESSMENT_DB_PASSWORD"
ensure_role_and_db reporting_svc reporting_db "$REPORTING_DB_PASSWORD"
ensure_role_and_db platform_svc platform_db "$PLATFORM_DB_PASSWORD"

echo "Created/verified Smart Education logical service databases."
