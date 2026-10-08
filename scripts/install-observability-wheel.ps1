param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$DistRoot = Join-Path $RepoRoot "dist\observability"
$Wheel = Get-ChildItem $DistRoot -Filter "smartedu_observability-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Wheel) {
    throw "No smartedu-observability wheel found. Run build-observability-wheel.ps1 first."
}

python -m pip install --force-reinstall $Wheel.FullName
Write-Host "Installed $($Wheel.Name)"
