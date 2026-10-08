param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$PackageRoot = Join-Path $RepoRoot "libs\python\smartedu_contracts"
$DistRoot = Join-Path $RepoRoot "dist\contracts"

if (-not (Test-Path $PackageRoot)) {
    throw "smartedu_contracts package not found at $PackageRoot"
}

New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null

python -m pip wheel $PackageRoot --no-deps --no-build-isolation -w $DistRoot

Write-Host "Contract wheel built in $DistRoot"
