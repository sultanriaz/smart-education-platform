param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$PackageRoot = Join-Path $RepoRoot "libs\python\smartedu_infra"
$DistRoot = Join-Path $RepoRoot "dist\infra"

if (-not (Test-Path $PackageRoot)) {
    throw "smartedu_infra package not found at $PackageRoot"
}

New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null

python -m pip wheel $PackageRoot --no-deps --no-build-isolation -w $DistRoot

Write-Host "smartedu-infra wheel built in $DistRoot"
