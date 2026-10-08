param(
    [ValidateSet("DATABASE","OBJECT_STORAGE")]
    [string]$Mode = "DATABASE",
    [ValidateSet("STAGING_ONLY")]
    [string]$Confirm,
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if ($Confirm -ne "STAGING_ONLY") {
    throw "Explicit -Confirm STAGING_ONLY is required."
}

if ($Mode -eq "DATABASE") {
    $Backup = $env:STAGING_DB_BACKUP_SCRIPT
    $Restore = $env:STAGING_DB_RESTORE_SCRIPT
    $Verify = $env:STAGING_DB_VERIFY_RESTORE_SCRIPT
}
else {
    $Backup = $env:STAGING_OBJECT_BACKUP_SCRIPT
    $Restore = $env:STAGING_OBJECT_RESTORE_SCRIPT
    $Verify = $env:STAGING_OBJECT_VERIFY_RESTORE_SCRIPT
}

foreach ($Script in @($Backup, $Restore, $Verify)) {
    if (-not $Script) {
        throw "$Mode recovery drill scripts are not fully configured."
    }
    if (-not (Test-Path $Script)) {
        throw "Configured recovery script does not exist: $Script"
    }
}

$Started = Get-Date
Write-Host "=== $Mode backup ==="
& $Backup
if ($LASTEXITCODE -ne 0) { throw "$Mode backup step failed." }

Write-Host "=== $Mode isolated restore ==="
& $Restore
if ($LASTEXITCODE -ne 0) { throw "$Mode restore step failed." }

Write-Host "=== $Mode restored-data verification ==="
& $Verify
if ($LASTEXITCODE -ne 0) { throw "$Mode verification step failed." }

$Elapsed = (Get-Date) - $Started
Write-Host ("PASS {0} recovery drill completed in {1:n1} seconds." -f `
    $Mode, $Elapsed.TotalSeconds)
