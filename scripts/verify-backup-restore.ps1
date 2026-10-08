param(
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [string]$ContainerName = "smartedu-infra-postgres"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

$TempDb = "restore_verify_$((Get-Date).ToString('yyyyMMddHHmmss'))"
$ContainerPath = "/tmp/restore-verify.dump"

docker exec $ContainerName createdb -U postgres $TempDb
docker cp $BackupFile "${ContainerName}:$ContainerPath"

try {
    docker exec $ContainerName `
        pg_restore -U postgres -d $TempDb --no-owner --no-acl $ContainerPath

    docker exec $ContainerName `
        psql -U postgres -d $TempDb -v ON_ERROR_STOP=1 -c `
        "SELECT current_database(), now();"

    Write-Host "Restore drill passed for $BackupFile"
}
finally {
    docker exec $ContainerName rm -f $ContainerPath
    docker exec $ContainerName dropdb -U postgres --if-exists $TempDb
}
