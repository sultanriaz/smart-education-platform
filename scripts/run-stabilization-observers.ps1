param(
    [ValidateSet("PRODUCTION_READ_ONLY")]
    [string]$Confirm,

    [string]$RepoRoot = (Get-Location).Path,
    [string]$MetricsScript = $env:STABILIZATION_METRICS_CHECK_SCRIPT,
    [string]$MessagingScript = $env:STABILIZATION_MESSAGING_CHECK_SCRIPT,
    [string]$SecurityScript = $env:STABILIZATION_SECURITY_CHECK_SCRIPT,
    [string]$SupportScript = $env:STABILIZATION_SUPPORT_CHECK_SCRIPT
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if ($Confirm -ne "PRODUCTION_READ_ONLY") {
    throw "Explicit -Confirm PRODUCTION_READ_ONLY is required."
}

$Hooks = @(
    @("metrics", $MetricsScript),
    @("messaging", $MessagingScript),
    @("security", $SecurityScript),
    @("support", $SupportScript)
)

foreach ($Hook in $Hooks) {
    $Name = $Hook[0]
    $Script = $Hook[1]

    if (-not $Script) {
        throw "$Name stabilization observer hook is not configured."
    }
    if (-not (Test-Path $Script)) {
        throw "$Name stabilization observer hook does not exist: $Script"
    }

    Write-Host "=== $Name stabilization observer ==="
    & $Script

    if ($LASTEXITCODE -ne 0) {
        throw "$Name stabilization observer failed."
    }
}

Write-Host "PASS all configured production stabilization observer hooks."
