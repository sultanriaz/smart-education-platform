param(
    [string]$RepoRoot = (Get-Location).Path,
    [ValidateSet("smoke","baseline","srs-500","stress-750","stress-1000","soak-250")]
    [string]$Profile = "smoke",
    [switch]$Load,
    [switch]$Infrastructure
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== smartedu-perf unit tests ==="
Push-Location .\libs\python\smartedu_perf
try {
    python -m pytest -q
}
finally {
    Pop-Location
}

Write-Host "`n=== Performance config tests ==="
python -m pytest -q .\tests\performance\test_config.py

Write-Host "`n=== Connection budget ==="
python .\scripts\check-connection-budget.py

if ($Infrastructure) {
    .\scripts\benchmark-infrastructure.ps1
}

if ($Load) {
    .\scripts\run-load.ps1 -Profile $Profile
}
