param(
    [Parameter(Mandatory=$true)][string]$Service,
    [Parameter(Mandatory=$true)][string]$Module,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$DatabaseUrl = ""
)

$ErrorActionPreference = "Stop"

$ServiceRoot = Join-Path $RepoRoot "services\$Service"
if (-not (Test-Path $ServiceRoot)) {
    throw "Service not found: $ServiceRoot"
}

$PreviousUrl = $env:DATABASE_URL
try {
    if ($DatabaseUrl) {
        $env:DATABASE_URL = $DatabaseUrl
    }

    Push-Location $ServiceRoot
    try {
        python -m $Module
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:DATABASE_URL = $PreviousUrl
}
