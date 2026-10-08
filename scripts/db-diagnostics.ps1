param(
    [string]$ContainerName = "smartedu-infra-postgres",
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$SqlFile = Join-Path $RepoRoot "infra\postgres\diagnostics.sql"
if (-not (Test-Path $SqlFile)) {
    throw "Diagnostics SQL not found: $SqlFile"
}

$Databases = @(
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

$ContainerSql = "/tmp/smartedu-diagnostics.sql"
docker cp $SqlFile "${ContainerName}:$ContainerSql"

try {
    foreach ($Db in $Databases) {
        Write-Host "`n================ $Db ================"
        docker exec $ContainerName `
            psql -U postgres -d $Db -f $ContainerSql
    }
}
finally {
    docker exec $ContainerName rm -f $ContainerSql
}
