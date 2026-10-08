# Backup, Restore, and Recovery

Sprint 17 supplies local/test scripts for proving recoverability. Production
should use managed PostgreSQL/object-storage backup capabilities where available.

## PostgreSQL

Local backup:

```powershell
.\scripts\backup-databases.ps1
```

This creates one PostgreSQL custom-format dump per service database.

Restore one database:

```powershell
.\scripts\restore-database.ps1 `
  -Database academic_db `
  -BackupFile .\backups\postgres\<stamp>\academic_db.dump `
  -Force
```

Non-destructive restore drill:

```powershell
.\scripts\verify-backup-restore.ps1 `
  -BackupFile .\backups\postgres\<stamp>\academic_db.dump
```

A backup is not considered valid until a restore drill has succeeded.

## Production PostgreSQL

For production use:

- encrypted backups
- off-host backup storage
- automated retention
- point-in-time recovery / WAL archiving where supported
- periodic restore drills
- alerting on failed backups
- separate credentials for backup operations

The application DB login should not be the backup superuser.

## Object storage

Backup:

```powershell
python .\scripts\object_storage_backup.py `
  --output .\backups\objects\<stamp>
```

Restore:

```powershell
python .\scripts\object_storage_restore.py `
  --input .\backups\objects\<stamp> `
  --force
```

The object backup manifest stores SHA-256 checksums.

## RPO/RTO

The original SRS requires strong availability/recovery behavior. A production
deployment should define concrete RPO/RTO per data class and demonstrate them in
the deployment runbook.

Local `pg_dump` alone is not a zero-data-loss production strategy.
