param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReleaseManifest = "",
    [string]$LaunchRecord = "",
    [string]$ProductionUrl = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-stabilization package ==="
Push-Location .\libs\python\smartedu_stabilization
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Stabilization config/tests ==="
python -m pytest -q .\tests\stabilization

Write-Host "`n=== Stabilization catalog ==="
python .\scripts\validate-stabilization-catalog.py

if ($ReleaseManifest -and $LaunchRecord -and $ProductionUrl) {
    Write-Host "`n=== Stabilization preflight ==="
    python .\scripts\stabilization-preflight.py `
        $ReleaseManifest `
        --launch-record $LaunchRecord `
        --production-url $ProductionUrl
}

Write-Host "`nSprint 28 offline checks completed."
