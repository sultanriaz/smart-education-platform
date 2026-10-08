param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Live,
    [switch]$E2E
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

$Results = Join-Path $RepoRoot "test-results\sprint19"
New-Item -ItemType Directory -Force -Path $Results | Out-Null

Write-Host "=== smartedu-testkit ==="
Push-Location .\libs\python\smartedu_testkit
try {
    python -m pytest -q --junitxml="$Results\testkit.xml"
}
finally {
    Pop-Location
}

Write-Host "`n=== Architecture tests ==="
python -m pytest -q tests\integration -m architecture `
    --junitxml="$Results\architecture.xml"

Write-Host "`n=== Service tests ==="
.\scripts\test-all-services.ps1 -RepoRoot $RepoRoot `
    -ReportsRoot "$Results\services"

Write-Host "`n=== Migration checks ==="
.\scripts\test-migrations.ps1 -RepoRoot $RepoRoot

Write-Host "`n=== Gateway ==="
Push-Location .\infra\gateway
try {
    python -m pytest -q --junitxml="$Results\gateway.xml"
}
finally {
    Pop-Location
}

Write-Host "`n=== Frontend ==="
Push-Location .\apps\frontend
try {
    npm run typecheck
    npm run lint
    npm run test
    npm run build
}
finally {
    Pop-Location
}

if ($Live) {
    Write-Host "`n=== Live integration/contract/security tests ==="
    python -m pytest -q tests\contracts tests\integration tests\security -m live `
        --junitxml="$Results\live.xml"
}

if ($E2E) {
    Write-Host "`n=== Browser E2E ==="
    Push-Location .\tests\e2e
    try {
        npm test
    }
    finally {
        Pop-Location
    }
}

Write-Host "`nSprint 19 test run completed."
