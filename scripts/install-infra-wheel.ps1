param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$DistRoot = Join-Path $RepoRoot "dist\infra"
$Wheel = Get-ChildItem $DistRoot -Filter "smartedu_infra-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Wheel) {
    throw "No smartedu-infra wheel found. Run scripts\build-infra-wheel.ps1 first."
}

python -m pip install --force-reinstall $Wheel.FullName
Write-Host "Installed $($Wheel.Name)"
