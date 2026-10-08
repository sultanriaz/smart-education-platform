\pset pager off

SELECT current_database() AS database_name, now() AT TIME ZONE 'UTC' AS checked_at_utc;

SELECT
    state,
    count(*) AS connections
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state
ORDER BY state;

SELECT
    pid,
    usename,
    state,
    wait_event_type,
    wait_event,
    now() - query_start AS running_for,
    left(query, 200) AS query
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND query_start IS NOT NULL
ORDER BY query_start
LIMIT 20;

SELECT
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC, seq_scan DESC
LIMIT 30;

SELECT
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC
LIMIT 30;

SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 30;

SELECT
    i.relname AS invalid_index
FROM pg_index x
JOIN pg_class i ON i.oid = x.indexrelid
WHERE NOT x.indisvalid;
