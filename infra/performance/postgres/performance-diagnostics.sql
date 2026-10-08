\pset pager off

SELECT now() AT TIME ZONE 'UTC' AS captured_at_utc;
SELECT current_database() AS database_name;

-- Active connections and wait states.
SELECT
    state,
    wait_event_type,
    wait_event,
    count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state, wait_event_type, wait_event
ORDER BY sessions DESC;

-- Long-running queries.
SELECT
    pid,
    usename,
    application_name,
    state,
    wait_event_type,
    wait_event,
    now() - query_start AS running_for,
    left(query, 300) AS query
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND query_start IS NOT NULL
ORDER BY query_start
LIMIT 30;

-- Lock waits.
SELECT
    blocked.pid AS blocked_pid,
    blocked.application_name AS blocked_app,
    blocking.pid AS blocking_pid,
    blocking.application_name AS blocking_app,
    now() - blocked.query_start AS blocked_for,
    left(blocked.query, 200) AS blocked_query,
    left(blocking.query, 200) AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks
  ON blocked_locks.pid = blocked.pid
 AND NOT blocked_locks.granted
JOIN pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
 AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
 AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
 AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
 AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
 AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
 AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
 AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
 AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
 AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
 AND blocking_locks.pid <> blocked_locks.pid
 AND blocking_locks.granted
JOIN pg_stat_activity blocking
  ON blocking.pid = blocking_locks.pid
ORDER BY blocked.query_start;

-- Dead tuples / vacuum pressure.
SELECT
    relname,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 30;

-- Table/index IO.
SELECT
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_live_tup
FROM pg_stat_user_tables
ORDER BY seq_tup_read DESC
LIMIT 30;

-- Large relations.
SELECT
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 30;
