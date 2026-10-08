\pset pager off

-- Candidate heavily scanned tables. This is evidence for review, not an
-- automatic instruction to add an index.
SELECT
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    n_live_tup,
    CASE
        WHEN seq_scan = 0 THEN 0
        ELSE seq_tup_read / seq_scan
    END AS avg_rows_per_seq_scan
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY seq_tup_read DESC
LIMIT 50;

-- Existing indexes with little/no observed use. Do not drop without checking
-- uniqueness/constraint purpose and a representative observation window.
SELECT
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC
LIMIT 50;
