param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$DistRoot = Join-Path $RepoRoot "dist\security"
$Wheel = Get-ChildItem $DistRoot -Filter "smartedu_security-*.whl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Wheel) {
    throw "No smartedu-security wheel found. Run scripts\build-security-wheel.ps1 first."
}

python -m pip install --force-reinstall $Wheel.FullName
Write-Host "Installed $($Wheel.Name)"
