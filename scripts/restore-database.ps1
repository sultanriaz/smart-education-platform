param(
    [Parameter(Mandatory=$true)][string]$Database,
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [string]$ContainerName = "smartedu-infra-postgres",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$Allowed = @(
    "identity_db",
    "academic_db",
    "attendance_db",
    "scheduling_db",
    "notification_db",
    "facility_db",
    "learning_db",
    "assessment_db",
    "reporting_db",
    "platform_db"
)

if ($Database -notin $Allowed) {
    throw "Unsupported database: $Database"
}
if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}
if (-not $Force) {
    throw "Restore is destructive. Re-run with -Force after verifying the target."
}

$ContainerPath = "/tmp/$Database.restore.dump"
docker cp $BackupFile "${ContainerName}:$ContainerPath"

try {
    docker exec $ContainerName `
        pg_restore -U postgres -d $Database `
        --clean --if-exists --no-owner --no-acl $ContainerPath
}
finally {
    docker exec $ContainerName rm -f $ContainerPath
}

Write-Host "Restore completed for $Database"
