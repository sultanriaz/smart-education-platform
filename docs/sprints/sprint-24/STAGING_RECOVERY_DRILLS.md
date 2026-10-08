# Staging Recovery Drills

Recovery must be demonstrated in staging before production launch.

## PostgreSQL recovery

Required drill:

1. create/identify a staging QA marker record
2. execute the approved backup/PITR mechanism
3. restore to an isolated restore target
4. verify schema versions
5. verify the QA marker record and related integrity
6. record elapsed time
7. destroy the isolated restore target after evidence is preserved

Do not overwrite the active staging database as the first restore test.

Use:

```powershell
.\scripts\staging-backup-restore-drill.ps1 `
    -Mode DATABASE `
    -Confirm STAGING_ONLY
```

after setting:

```text
STAGING_DB_BACKUP_SCRIPT
STAGING_DB_RESTORE_SCRIPT
STAGING_DB_VERIFY_RESTORE_SCRIPT
```

## Object-storage recovery

Required drill:

1. upload a marked staging test object
2. create version/delete scenario
3. execute backup/version restore path
4. verify checksum/content
5. verify authorization remains private
6. clean up test object

Use:

```powershell
.\scripts\staging-backup-restore-drill.ps1 `
    -Mode OBJECT_STORAGE `
    -Confirm STAGING_ONLY
```

with the corresponding provider-specific script variables.

## Release redeploy

Redeploy the exact current `release-manifest.json`.

Confirm:

```text
same image digests
same migrations not rerun unnecessarily
same public behavior
```

## Secret recovery

Recreate one staging service Secret from the real secret source.

Confirm the service can restart and recover without any secret being recovered
from Git.

## Credential rotation

Rotate one staging credential, for example:

```text
RabbitMQ user password
database password
internal service token
```

Prefer overlap/dual-key rotation where the service supports it.

## Evidence

Record:

```text
date/time UTC
operator
release tag
provider/product
backup identifier
restore target
elapsed time
integrity checks
problems encountered
cleanup completion
```
