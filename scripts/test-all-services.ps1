param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$ReportsRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $ReportsRoot) {
    $ReportsRoot = Join-Path $RepoRoot "test-results\services"
}
New-Item -ItemType Directory -Force -Path $ReportsRoot | Out-Null

$Services = Get-ChildItem (Join-Path $RepoRoot "services") -Directory |
    Where-Object { $_.Name -like "*-service" } |
    Sort-Object Name

$Failures = @()

foreach ($Service in $Services) {
    $Tests = Join-Path $Service.FullName "tests"
    if (-not (Test-Path $Tests)) {
        Write-Warning "$($Service.Name): no tests directory"
        $Failures += "$($Service.Name):missing-tests"
        continue
    }

    Write-Host "`n=== $($Service.Name) ==="
    $Report = Join-Path $ReportsRoot "$($Service.Name).xml"

    Push-Location $Service.FullName
    try {
        python -m pytest -q --junitxml="$Report"
        if ($LASTEXITCODE -ne 0) {
            $Failures += $Service.Name
        }
    }
    finally {
        Pop-Location
    }
}

if ($Failures.Count -gt 0) {
    throw "Service test failures: $($Failures -join ', ')"
}

Write-Host "`nAll service suites passed."
