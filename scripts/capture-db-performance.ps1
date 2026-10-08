param(
    [string]$ContainerName = "smartedu-infra-postgres",
    [string]$RepoRoot = (Get-Location).Path,
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutputRoot) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputRoot = Join-Path $RepoRoot "tests\performance\results\db-$Stamp"
}
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$Sql = Join-Path $RepoRoot "infra\performance\postgres\performance-diagnostics.sql"
$ContainerSql = "/tmp/smartedu-performance.sql"
docker cp $Sql "${ContainerName}:$ContainerSql"

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

try {
    foreach ($Db in $Databases) {
        Write-Host "Capturing $Db"
        $File = Join-Path $OutputRoot "$Db.txt"
        docker exec $ContainerName `
            psql -U postgres -d $Db -f $ContainerSql |
            Set-Content -Encoding utf8 $File
    }
}
finally {
    docker exec $ContainerName rm -f $ContainerSql
}

Write-Host "Database performance diagnostics: $OutputRoot"
