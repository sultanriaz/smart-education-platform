param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$OutputRoot = "",
    [string]$ContainerName = "smartedu-infra-postgres"
)

$ErrorActionPreference = "Stop"

if (-not $OutputRoot) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputRoot = Join-Path $RepoRoot "backups\postgres\$Stamp"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

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

foreach ($Db in $Databases) {
    $ContainerPath = "/tmp/$Db.dump"
    $LocalPath = Join-Path $OutputRoot "$Db.dump"

    Write-Host "Backing up $Db..."
    docker exec $ContainerName `
        pg_dump -U postgres -Fc --no-owner --no-acl -d $Db -f $ContainerPath

    docker cp "${ContainerName}:$ContainerPath" $LocalPath
    docker exec $ContainerName rm -f $ContainerPath

    if (-not (Test-Path $LocalPath)) {
        throw "Backup file missing: $LocalPath"
    }
}

$Manifest = @{
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    format = "pg_dump custom"
    databases = $Databases
} | ConvertTo-Json -Depth 4

$Manifest | Set-Content -Encoding utf8 (Join-Path $OutputRoot "manifest.json")
Write-Host "Backups written to $OutputRoot"
