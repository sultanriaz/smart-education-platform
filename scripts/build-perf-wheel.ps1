param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$PackageRoot = Join-Path $RepoRoot "libs\python\smartedu_perf"
$DistRoot = Join-Path $RepoRoot "dist\perf"
New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null
python -m pip wheel $PackageRoot --no-deps --no-build-isolation -w $DistRoot
