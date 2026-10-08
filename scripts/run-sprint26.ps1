param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReleaseManifest = "",
    [string]$UatRun = "",
    [string]$ProductionUrl = "",
    [string]$ProductionBundle = ""
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-readiness package ==="
Push-Location .\libs\python\smartedu_readiness
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Readiness config tests ==="
python -m pytest -q .\tests\readiness

Write-Host "`n=== Readiness catalog ==="
python .\scripts\validate-readiness-catalog.py

if ($ReleaseManifest -and $UatRun -and $ProductionUrl) {
    Write-Host "`n=== Production-readiness preflight ==="
    python .\scripts\production-readiness-preflight.py `
        $ReleaseManifest `
        --uat-run $UatRun `
        --production-url $ProductionUrl
}

if ($ProductionBundle) {
    Write-Host "`n=== Production bundle ==="
    python .\scripts\verify-production-bundle.py $ProductionBundle
}

Write-Host "`nSprint 26 checks completed."
