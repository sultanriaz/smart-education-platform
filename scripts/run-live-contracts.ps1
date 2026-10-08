param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

python -m pytest -q `
    tests\contracts `
    tests\security `
    tests\integration\test_health_contract_live.py `
    tests\integration\test_gateway_security_live.py `
    tests\performance\test_nfr_smoke_live.py `
    -m live
