-- Usage:
-- psql -v monitor_password='<strong-secret>' -f create-monitoring-role.sql
--
-- This role can inspect PostgreSQL statistics but is not granted application
-- table DML privileges.

SELECT format(
    'CREATE ROLE smartedu_monitor LOGIN PASSWORD %L',
    :'monitor_password'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = 'smartedu_monitor'
)
\gexec

GRANT pg_monitor TO smartedu_monitor;

GRANT CONNECT ON DATABASE identity_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE academic_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE attendance_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE scheduling_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE notification_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE facility_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE learning_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE assessment_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE reporting_db TO smartedu_monitor;
GRANT CONNECT ON DATABASE platform_db TO smartedu_monitor;
