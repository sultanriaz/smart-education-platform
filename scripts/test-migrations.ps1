param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$Services = Get-ChildItem (Join-Path $RepoRoot "services") -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "alembic.ini") } |
    Sort-Object Name

foreach ($Service in $Services) {
    Write-Host "`n=== Migration check: $($Service.Name) ==="
    Push-Location $Service.FullName
    try {
        $Heads = python -m alembic -c .\alembic.ini heads
        if ($LASTEXITCODE -ne 0) { throw "$($Service.Name): alembic heads failed" }

        $HeadLines = @($Heads | Where-Object { $_.Trim() })
        if ($HeadLines.Count -ne 1) {
            throw "$($Service.Name): expected exactly one Alembic head, got $($HeadLines.Count)"
        }

        python -m alembic -c .\alembic.ini upgrade head
        if ($LASTEXITCODE -ne 0) { throw "$($Service.Name): upgrade head failed" }

        python -m alembic -c .\alembic.ini current
        if ($LASTEXITCODE -ne 0) { throw "$($Service.Name): current failed" }

        # Alembic check is available on modern Alembic and catches schema drift.
        python -m alembic -c .\alembic.ini check
        if ($LASTEXITCODE -ne 0) { throw "$($Service.Name): alembic check failed" }
    }
    finally {
        Pop-Location
    }
}

Write-Host "`nAll service migration checks passed."
