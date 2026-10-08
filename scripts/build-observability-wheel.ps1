param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$PackageRoot = Join-Path $RepoRoot "libs\python\smartedu_observability"
$DistRoot = Join-Path $RepoRoot "dist\observability"

New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null
python -m pip wheel $PackageRoot --no-deps --no-build-isolation -w $DistRoot
Write-Host "smartedu-observability wheel built in $DistRoot"
