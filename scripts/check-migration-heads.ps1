param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$Services = Get-ChildItem (Join-Path $RepoRoot "services") -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "alembic.ini") }

foreach ($Service in $Services) {
    Write-Host "`n=== $($Service.Name) ==="
    Push-Location $Service.FullName
    try {
        python -m alembic -c .\alembic.ini heads
    }
    finally {
        Pop-Location
    }
}
