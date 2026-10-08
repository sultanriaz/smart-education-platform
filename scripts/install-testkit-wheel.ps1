param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$DistRoot = Join-Path $RepoRoot "dist\testkit"
$Wheel = Get-ChildItem $DistRoot -Filter "smartedu_testkit-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Wheel) {
    throw "No smartedu-testkit wheel found. Run build-testkit-wheel.ps1 first."
}

python -m pip install --force-reinstall $Wheel.FullName
