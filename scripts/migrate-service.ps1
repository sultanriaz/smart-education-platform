param(
    [Parameter(Mandatory=$true)][string]$Service,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$DatabaseUrl = ""
)

$ErrorActionPreference = "Stop"

$ServiceRoot = Join-Path $RepoRoot "services\$Service"
if (-not (Test-Path $ServiceRoot)) {
    throw "Service not found: $ServiceRoot"
}

$AlembicIni = Join-Path $ServiceRoot "alembic.ini"
if (-not (Test-Path $AlembicIni)) {
    throw "No alembic.ini found for $Service"
}

$PreviousUrl = $env:DATABASE_URL
try {
    if ($DatabaseUrl) {
        $env:DATABASE_URL = $DatabaseUrl
    }

    Push-Location $ServiceRoot
    try {
        python -m alembic -c .\alembic.ini upgrade head
        python -m alembic -c .\alembic.ini current
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:DATABASE_URL = $PreviousUrl
}
