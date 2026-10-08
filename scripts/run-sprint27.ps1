param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReleaseManifest = "",
    [string]$ReadinessRun = "",
    [string]$ProductionUrl = "",
    [string]$ProductionBundle = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-launch package ==="
Push-Location .\libs\python\smartedu_launch
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Sprint 27 config/workflow tests ==="
python -m pytest -q .\tests\launch

if ($ReleaseManifest -and $ReadinessRun -and $ProductionUrl) {
    Write-Host "`n=== Production launch preflight ==="
    python .\scripts\production-launch-preflight.py `
        $ReleaseManifest `
        --readiness-run $ReadinessRun `
        --production-url $ProductionUrl
}

if ($ReleaseManifest) {
    $MigrationBundle = ".\deploy\kubernetes\production-launch\migrations.yaml"
    Write-Host "`n=== Render migration Jobs ==="
    python .\scripts\render-production-migrations.py `
        $ReleaseManifest `
        --output $MigrationBundle

    python .\scripts\verify-production-migrations.py `
        $ReleaseManifest `
        $MigrationBundle
}

if ($ProductionBundle) {
    Write-Host "`n=== Verify production bundle ==="
    python .\scripts\verify-production-bundle.py $ProductionBundle
}

Write-Host "`nSprint 27 offline checks completed."
