param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$DistRoot = Join-Path $RepoRoot "dist\contracts"
$Wheel = Get-ChildItem $DistRoot -Filter "smartedu_contracts-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Wheel) {
    throw "No smartedu-contracts wheel found. Run scripts\build-contract-wheel.ps1 first."
}

python -m pip install --force-reinstall $Wheel.FullName
Write-Host "Installed $($Wheel.Name)"
