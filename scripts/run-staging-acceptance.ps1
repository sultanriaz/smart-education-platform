param(
    [Parameter(Mandatory=$true)]
    [string]$ReleaseManifest,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$BaseUrl = $env:SMARTEDU_STAGING_URL,
    [string]$KubeContext = $env:STAGING_KUBE_CONTEXT,
    [switch]$E2E,
    [switch]$PerformanceSmoke,
    [switch]$Observability
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not $BaseUrl) {
    throw "SMARTEDU_STAGING_URL or -BaseUrl is required."
}
if (-not $KubeContext) {
    throw "STAGING_KUBE_CONTEXT or -KubeContext is required."
}

$CurrentContext = (kubectl config current-context).Trim()
if ($CurrentContext -ne $KubeContext) {
    throw "Current kubectl context '$CurrentContext' is not expected staging context '$KubeContext'."
}

Write-Host "=== Staging preflight ==="
python .\scripts\staging-preflight.py `
    --release-manifest $ReleaseManifest

Write-Host "`n=== Required secrets ==="
python .\scripts\staging-secret-check.py

Write-Host "`n=== Deployment rollouts ==="
.\scripts\staging-rollout-status.ps1 `
    -KubeContext $KubeContext

Write-Host "`n=== Public smoke ==="
python .\scripts\staging-public-smoke.py `
    --base-url $BaseUrl

$env:SMARTEDU_GATEWAY_URL = $BaseUrl.TrimEnd("/")

if (Test-Path .\scripts\run-live-contracts.ps1) {
    Write-Host "`n=== Sprint 19 live contracts/security ==="
    .\scripts\run-live-contracts.ps1 -RepoRoot $RepoRoot
}

if ($E2E) {
    if (-not (Test-Path .\tests\e2e\package.json)) {
        throw "Sprint 19 Playwright project not found."
    }

    Write-Host "`n=== Student / Teacher / Admin E2E ==="
    Push-Location .\tests\e2e
    try {
        npm ci
        npx playwright install --with-deps chromium
        npx playwright test
    }
    finally {
        Pop-Location
    }
}

if ($PerformanceSmoke) {
    if (-not (Test-Path .\scripts\run-load.ps1)) {
        throw "Sprint 20 load runner not found."
    }
    Write-Host "`n=== Sprint 20 smoke performance ==="
    .\scripts\run-load.ps1 `
        -Profile smoke `
        -HostUrl $env:SMARTEDU_GATEWAY_URL `
        -RepoRoot $RepoRoot
}

if ($Observability) {
    if (-not (Test-Path .\scripts\observability-smoke.ps1)) {
        throw "Sprint 21 observability smoke runner not found."
    }
    Write-Host "`n=== Sprint 21 observability ==="
    .\scripts\observability-smoke.ps1 -RequireServices
}

Write-Host "`nPASS staging acceptance command completed."
