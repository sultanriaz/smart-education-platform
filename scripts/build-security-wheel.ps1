param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$PackageRoot = Join-Path $RepoRoot "libs\python\smartedu_security"
$DistRoot = Join-Path $RepoRoot "dist\security"

if (-not (Test-Path $PackageRoot)) {
    throw "smartedu_security package not found at $PackageRoot"
}

New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null
python -m pip wheel $PackageRoot --no-deps --no-build-isolation -w $DistRoot
Write-Host "smartedu-security wheel built in $DistRoot"
