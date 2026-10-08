param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== Secret scan ==="
$SecretArgs = @(".\scripts\secret_scan.py", ".")
if ($Strict) { $SecretArgs += "--strict" }
python @SecretArgs

Write-Host "`n=== Container static audit ==="
$ContainerArgs = @(".\scripts\container_security_audit.py", ".")
if ($Strict) { $ContainerArgs += "--strict" }
python @ContainerArgs

if (Get-Command bandit -ErrorAction SilentlyContinue) {
    Write-Host "`n=== Bandit ==="
    bandit -q -r .\services .\libs\python -x "*/tests/*"
} elseif ($Strict) {
    throw "bandit is required in strict mode"
} else {
    Write-Warning "bandit is not installed; skipping"
}

if (Get-Command pip-audit -ErrorAction SilentlyContinue) {
    Write-Host "`n=== pip-audit current environment ==="
    pip-audit
} elseif ($Strict) {
    throw "pip-audit is required in strict mode"
} else {
    Write-Warning "pip-audit is not installed; skipping"
}

$Frontend = Join-Path $RepoRoot "apps\frontend"
if (Test-Path (Join-Path $Frontend "package.json")) {
    Push-Location $Frontend
    try {
        if (Test-Path ".\package-lock.json") {
            Write-Host "`n=== npm audit ==="
            npm audit --audit-level=high
        } else {
            Write-Warning "No package-lock.json; npm audit reproducibility is limited"
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "`nSecurity audit completed."
