param(
    [Parameter(Mandatory=$true)]
    [string]$ReleaseManifest,
    [Parameter(Mandatory=$true)]
    [string]$StagingUrl,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$StagingReleaseManifest = "",
    [switch]$E2E,
    [switch]$AccessibilitySmoke
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

Write-Host "=== UAT catalog ==="
python .\scripts\validate-uat-catalog.py

Write-Host "`n=== UAT release/environment preflight ==="
$PreflightArgs = @(
    ".\scripts\uat-preflight.py",
    $ReleaseManifest,
    "--staging-url", $StagingUrl
)
if ($StagingReleaseManifest) {
    $PreflightArgs += @(
        "--staging-release-manifest",
        $StagingReleaseManifest
    )
}
python @PreflightArgs

$env:SMARTEDU_GATEWAY_URL = $StagingUrl.TrimEnd("/")

if ($E2E) {
    if (-not (Test-Path .\tests\e2e\package.json)) {
        throw "Sprint 19 Playwright project not found at tests/e2e."
    }

    Write-Host "`n=== Sprint 19 E2E regression ==="
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

if ($AccessibilitySmoke) {
    Write-Host "`n=== Accessibility smoke handoff ==="
    Write-Host (
        "Run the integrated accessibility checks for UAT-X-007 and UAT-X-008. " +
        "Sprint 25 does not invent an accessibility runner until Codex reconciles " +
        "the actual frontend test stack."
    )
}

Write-Host "`nAutomated UAT prechecks completed."
