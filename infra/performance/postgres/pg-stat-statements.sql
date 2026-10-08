-- Run only if pg_stat_statements is enabled by the PostgreSQL deployment.
-- In managed production, enable it using the provider-supported mechanism.

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
    queryid,
    calls,
    round(total_exec_time::numeric, 2) AS total_exec_ms,
    round(mean_exec_time::numeric, 2) AS mean_exec_ms,
    round(stddev_exec_time::numeric, 2) AS stddev_exec_ms,
    rows,
    shared_blks_hit,
    shared_blks_read,
    temp_blks_read,
    temp_blks_written,
    left(query, 500) AS query
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT 50;
